#!/usr/bin/env python3
"""Read-only MBS catalog lookup. Resolves one group file per component; no network."""
import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
INDEX = ROOT / "references" / "index.json"


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
        if not 1 <= args.limit <= 50:
            parser.error("--limit must be between 1 and 50")
        needle = args.query.casefold()
        matches = []
        seen = set()
        for component, summary in index["components"].items():
            path = ROOT / summary["file"]
            if path in seen:
                continue
            seen.add(path)
            group = json.loads(path.read_text(encoding="utf-8"))
            for block in group["components"].values():
                for entry in block["functions"]:
                    haystack = " ".join([entry["name"], entry["signature"], entry["status"],
                                         block["component"]]).casefold()
                    if needle in haystack:
                        matches.append({"name": entry["name"], "component": block["component"],
                                        "signature": entry["signature"], "status": entry["status"]})
                        if len(matches) >= args.limit:
                            return emit({"query": args.query, "matches": matches})
        return emit({"query": args.query, "matches": matches})
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
