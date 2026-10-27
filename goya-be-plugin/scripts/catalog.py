#!/usr/bin/env python3
"""Read-only BaseElements catalog lookup. Standard library only; no network."""
import argparse
import json
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOG = HERE.parent / "references" / "function-catalog.json"

# Small, curated EN/ES intent hints, not a semantic model or an execution plan.
INTENTS = (
    (r"(?=.*\b(send|enviar|mandar)\b)(?=.*\b(email|mail|correo)\b)", ("BE_SMTPSend", "BE_SMTPServer")),
    (r"(?=.*\b(write|save|escribir|guardar)\b)(?=.*\b(file|archivo|csv)\b)", ("BE_FileWriteText",)),
    (r"(?=.*\b(read|leer)\b)(?=.*\b(file|archivo)\b)", ("BE_FileReadText",)),
    (r"(?=.*\b(list|listar)\b)(?=.*\b(folder|directory|carpeta|directorio)\b)", ("BE_FileListFolder",)),
    (r"\b(http|request|peticion|solicitud)\b", ("BE_HTTP_GET", "BE_HTTP_POST", "BE_HTTP_ResponseCode")),
    (r"\b(regex|regexp|regular expression|expresion regular)\b", ("BE_RegularExpression",)),
    (r"\b(javascript|js)\b", ("BE_EvaluateJavaScript",)),
    (r"\b(xslt|transformar xml|transform xml)\b", ("BE_XSLTApply", "BE_XSLT_ApplyInMemory")),
    (r"(?=.*\b(merge|append|unir|combinar)\b)(?=.*\b(pdf)\b)", ("BE_PDFAppend",)),
    (r"\b(hash|digest|huella)\b", ("BE_MessageDigest",)),
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


def load():
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def entries(data):
    for category, block in data["categories"].items():
        for entry in block["functions"]:
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


def search(data, query, limit):
    needle = normalize(query)
    matches = []
    seen = set()
    for category, entry in entries(data):
        haystack = " ".join([
            entry["name"], entry.get("signature", ""), category,
            " ".join(entry.get("keywords", [])),
        ])
        score = search_score(needle, entry["name"], normalize(haystack))
        if score and entry["name"] not in seen:
            seen.add(entry["name"])
            matches.append((score, {
                "name": entry["name"],
                "category": category,
                "signature": entry.get("signature", ""),
            }))
    return [entry for _, entry in sorted(matches, key=lambda item: (-item[0], item[1]["name"]))[:limit]]


def constants(data):
    result = []
    for group in data.get("constants", {}).get("groups", []):
        for item in group.get("constants", []):
            result.append({**item, "used_with": group.get("used_with", "")})
    return result


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
    sub.add_parser("deprecated")
    sub.add_parser("constants")
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
            name: [{"name": x["name"], "signature": x.get("signature", "")}
                   for x in data["categories"][name]["functions"]]
            for name in categories}})
    if args.command == "deprecated":
        return emit({"deprecated": data.get("deprecated", [])})
    if args.command == "constants":
        return emit({"constants": constants(data)})
    return emit({"meta": data["meta"], "deprecated_count": len(data.get("deprecated", []))})


if __name__ == "__main__":
    raise SystemExit(main())
