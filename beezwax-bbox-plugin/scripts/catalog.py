#!/usr/bin/env python3
"""Read-only bBox catalog lookup. Standard library only; no network."""
import argparse
import json
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOG = HERE.parent / "references" / "function-catalog.json"

# Curated EN/ES retrieval hints; never evaluate a shell/runtime call here.
INTENTS = (
    (r"(?=.*\b(run|execute|ejecutar)\b)(?=.*\b(python)\b)", ("bBox_Python3Run", "bBox_PythonExecute", "bBox_PythonEval")),
    (r"(?=.*\b(run|execute|ejecutar)\b)(?=.*\b(shell|command|comando|zsh|bash)\b)", ("bBox_Zsh", "bBox_Bash", "bBox_Shell")),
    (r"\b(duckdb)\b", ("bBox_DuckDBOpen", "bBox_DuckDBExec", "bBox_DuckDBClose")),
    (r"(?=.*\b(write|save|escribir|guardar)\b)(?=.*\b(file|archivo|csv)\b)", ("bBox_FileWrite",)),
    (r"(?=.*\b(read|leer)\b)(?=.*\b(file|archivo)\b)", ("bBox_FileRead",)),
    (r"\b(http|request|peticion|solicitud)\b", ("bBox_HTTP_GET", "bBox_HTTP_POST", "bBox_Curl")),
    (r"(?=.*\b(resize|convert|redimensionar|convertir)\b)(?=.*\b(image|imagen)\b)", ("bBox_GraphicsMagick", "bBox_Sips")),
    (r"\b(web viewer|webview|visor web)\b", ("bBox_WebViewLoadHTML", "bBox_WebViewEvaluateJavaScript")),
    (r"\b(javascript|js)\b", ("bBox_JavaScript", "bBox_JavaScriptNode")),
    (r"\b(regex|regexp|regular expression|expresion regular)\b", ("bBox_Grep",)),
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


def search(data, query, limit):
    needle = normalize(query)
    matches = []
    for category, entry in entries(data):
        haystack = normalize(" ".join([entry["name"], entry.get("signature", ""), category]))
        score = search_score(needle, entry["name"], haystack)
        if score:
            matches.append((score, {"name": entry["name"], "category": category,
                                    "signature": entry.get("signature", ""),
                                    "doc_status": entry.get("doc_status", "")}))
    return [entry for _, entry in sorted(matches, key=lambda item: (-item[0], item[1]["name"]))[:limit]]


def load():
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def entries(data):
    for category, block in data["categories"].items():
        for entry in block["functions"].values():
            yield category, entry


def find(data, name):
    wanted = " ".join(name.split()).casefold()
    for category, entry in entries(data):
        if entry["name"].casefold() == wanted:
            return category, entry
    return None, None


def emit(value, code=0):
    print(json.dumps(value, ensure_ascii=False, indent=2))
    return code


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("function")
    p.add_argument("name")
    p = sub.add_parser("search")
    p.add_argument("query")
    p.add_argument("--limit", type=int, default=8)
    p = sub.add_parser("list")
    p.add_argument("--category")
    p = sub.add_parser("shared")
    p.add_argument("key", nargs="?")
    sub.add_parser("stats")
    args = parser.parse_args()
    data = load()
    if args.command == "function":
        if not args.name.strip():
            parser.error("function name must not be blank")
        category, entry = find(data, args.name)
        if entry is None:
            return emit({"status": "not-found-in-snapshot", "name": args.name}, 1)
        return emit({"status": "found", "category": category, "entry": entry})
    if args.command == "search":
        if not args.query.strip():
            parser.error("search query must not be blank")
        if not 1 <= args.limit <= 50:
            parser.error("--limit must be between 1 and 50")
        return emit({"query": args.query, "matches": search(data, args.query, args.limit)})
    if args.command == "list":
        if args.category and args.category not in data["categories"]:
            return emit({"status": "unknown-category", "category": args.category,
                         "categories": sorted(data["categories"])}, 2)
        categories = [args.category] if args.category else sorted(data["categories"])
        return emit({"categories": {
            name: [{"name": entry["name"], "signature": entry.get("signature", ""),
                    "doc_status": entry.get("doc_status", "")}
                   for entry in data["categories"][name]["functions"].values()]
            for name in categories}})
    if args.command == "shared":
        shared = data.get("shared_reference", {})
        if args.key:
            if args.key not in shared:
                return emit({"status": "not-found", "key": args.key,
                             "keys": sorted(shared)}, 1)
            return emit({"key": args.key, "value": shared[args.key]})
        return emit({"keys": sorted(shared)})
    return emit({"meta": data["meta"]})


if __name__ == "__main__":
    raise SystemExit(main())
