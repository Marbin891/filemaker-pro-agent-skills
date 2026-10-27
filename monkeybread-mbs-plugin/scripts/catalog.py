#!/usr/bin/env python3
"""Read-only MBS catalog lookup. Resolves one group file per component; no network."""
import argparse
import json
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
INDEX = ROOT / "references" / "index.json"

# Curated EN/ES retrieval hints. Results still need function/platform/licence lookup.
INTENTS = (
    (r"(?=.*\b(create|generate|crear|generar)\b)(?=.*\b(pdf)\b)", ("DynaPDF.New", "DynaPDF.AppendPage", "DynaPDF.Save")),
    (r"(?=.*\b(extract|extraer)\b)(?=.*\b(text|texto)\b)(?=.*\b(pdf)\b)", ("DynaPDF.ExtractText", "DynaPDF.ExtractDocumentText")),
    (r"(?=.*\b(read|open|leer|abrir)\b)(?=.*\b(excel|xlsx|spreadsheet)\b)", ("XL.LoadBook", "XL.Sheet.CellReadText")),
    (r"(?=.*\b(write|save|escribir|guardar)\b)(?=.*\b(file|archivo)\b)", ("Files.WriteFile",)),
    (r"(?=.*\b(read|leer)\b)(?=.*\b(file|archivo)\b)", ("Files.ReadFile",)),
    (r"\b(http|request|peticion|solicitud)\b", ("CURL.New", "CURL.SetOptionURL", "CURL.Perform")),
    (r"(?=.*\b(send|enviar|mandar)\b)(?=.*\b(email|mail|correo)\b)", ("SendMail.CreateEmail", "SendMail.PrepareCURL", "CURL.Perform")),
    (r"\b(regex|regexp|regular expression|expresion regular)\b", ("RegEx.ReplaceAll", "RegEx.Replace", "RegEx.Execute")),
    (r"(?=.*\b(parse|analizar)\b)(?=.*\b(json)\b)", ("JSON.Parse",)),
)


def normalize(text):
    return " ".join("".join(c for c in unicodedata.normalize("NFKD", text.casefold())
                            if not unicodedata.combining(c)).split())


def search_score(query, name, haystack):
    if not query:
        return 0
    if query == name.casefold():
        return 1000
    if query in haystack:
        return 900
    hints = [names.index(name) for pattern, names in INTENTS
             if name in names and re.search(pattern, query)]
    if hints:
        return 800 - min(hints)
    tokens = [t for t in re.findall(r"\w+", query)
              if t not in {"a", "an", "the", "to", "with", "using", "in", "de", "un", "una", "con", "en", "el", "la"}]
    return 100 if tokens and all(t in haystack for t in tokens) else 0


def search(index, query, limit):
    needle = normalize(query)
    matches = []
    for relative in sorted({summary["file"] for summary in index["components"].values()}):
        group = json.loads((ROOT / relative).read_text(encoding="utf-8"))
        for block in group["components"].values():
            for entry in block["functions"]:
                haystack = normalize(" ".join([entry["name"], entry["signature"], entry["status"], block["component"]]))
                score = search_score(needle, entry["name"], haystack)
                if score:
                    matches.append((score, {"name": entry["name"], "component": block["component"],
                                            "signature": entry["signature"], "status": entry["status"]}))
    return [entry for _, entry in sorted(matches, key=lambda item: (-item[0], item[1]["name"]))[:limit]]


def load_index():
    return json.loads(INDEX.read_text(encoding="utf-8"))


def load_component(index, component):
    canonical = next((key for key in index["components"] if key.casefold() == component.strip().casefold()), None)
    summary = index["components"].get(canonical)
    if summary is None:
        return None
    return json.loads((ROOT / summary["file"]).read_text(encoding="utf-8"))["components"][canonical]


def component_of(name):
    return name.split(".", 1)[0] if "." in name else name


def emit(value, code=0):
    print(json.dumps(value, ensure_ascii=False, indent=2))
    return code


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("function")
    p.add_argument("name")
    p = sub.add_parser("component")
    p.add_argument("name")
    p = sub.add_parser("search")
    p.add_argument("query")
    p.add_argument("--limit", type=int, default=8)
    sub.add_parser("components")
    sub.add_parser("stats")
    args = parser.parse_args()
    index = load_index()
    if args.command == "function":
        if not args.name.strip():
            parser.error("function name must not be blank")
        component = component_of(args.name)
        block = load_component(index, component)
        if block is None:
            return emit({"status": "not-found-in-snapshot", "name": args.name,
                         "component": component}, 1)
        wanted = args.name.strip().casefold()
        for entry in block["functions"]:
            if entry["name"].casefold() == wanted:
                return emit({"status": "found", "component": component, "entry": entry})
        return emit({"status": "not-found-in-snapshot", "name": args.name,
                     "component": component}, 1)
    if args.command == "component":
        block = load_component(index, args.name)
        if block is None:
            return emit({"status": "not-found-in-snapshot", "component": args.name,
                         "components": sorted(index["components"])}, 1)
        return emit({"status": "found", "component": block["component"],
                     "function_count": block["function_count"],
                     "requires_addon": block.get("requires_addon", ""),
                     "functions": [{"name": x["name"], "signature": x["signature"],
                                    "status": x["status"]} for x in block["functions"]]})
    if args.command == "search":
        if not args.query.strip():
            parser.error("search query must not be blank")
        if not 1 <= args.limit <= 50:
            parser.error("--limit must be between 1 and 50")
        return emit({"query": args.query, "matches": search(index, args.query, args.limit)})
    if args.command == "components":
        return emit({"components": {
            name: {"function_count": value["function_count"],
                   "status_counts": value.get("status_counts", {}),
                   "file": value["file"]}
            for name, value in sorted(index["components"].items())}})
    return emit({"meta": {key: value for key, value in index.items() if key != "components"},
                 "component_count": len(index["components"])})


if __name__ == "__main__":
    raise SystemExit(main())
