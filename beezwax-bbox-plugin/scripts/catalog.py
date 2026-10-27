#!/usr/bin/env python3
"""Read-only bBox catalog lookup. Standard library only; no network."""
import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOG = HERE.parent / "references" / "function-catalog.json"


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
        if not 1 <= args.limit <= 50:
            parser.error("--limit must be between 1 and 50")
        needle = " ".join(args.query.split()).casefold()
        matches = []
        for category, entry in entries(data):
            haystack = " ".join([entry["name"], entry.get("signature", ""), category]).casefold()
            if needle in haystack:
                matches.append({"name": entry["name"], "category": category,
                                "signature": entry.get("signature", ""),
                                "doc_status": entry.get("doc_status", "")})
                if len(matches) >= args.limit:
                    break
        return emit({"query": args.query, "matches": matches})
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
