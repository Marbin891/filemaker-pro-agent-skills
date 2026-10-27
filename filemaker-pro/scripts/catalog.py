#!/usr/bin/env python3
"""Read-only, offline catalog lookup. Does not parse or execute FileMaker calculations."""
import argparse
import json
import re
from pathlib import Path

REFERENCES = Path(__file__).resolve().parents[1] / "references"
PLATFORMS = ("Pro", "Go", "WebDirect", "Server", "Cloud", "DataAPI", "CWP")
SNAPSHOT = (26, 0, 3)


def load(name):
    return json.loads((REFERENCES / name).read_text(encoding="utf-8"))


def normalize(name):
    """Ignore whitespace only; retain punctuation that distinguishes API names."""
    return re.sub(r"\s+", "", name).casefold()


def entries(kind):
    if kind == "function":
        return load("function-catalog.json")["functions"]
    if kind == "step":
        return [dict(step, category=category["name"])
                for category in load("script-steps-catalog.json")["categories"]
                for step in category["steps"]]
    if kind == "error":
        return load("error-codes.json")["errors"]
    if kind == "field":
        return load("field-types-catalog.json")["data_types"]
    raise ValueError(f"Unknown kind: {kind}")


def find(kind, name):
    if kind == "error":
        try:
            code = int(name)
        except ValueError:
            raise ValueError("Error code must be an integer") from None
        return next((x for x in entries(kind) if x["code"] == code), None)
    key = normalize(name)
    if not key:
        raise ValueError("Lookup name must not be empty or whitespace")
    return next((x for x in entries(kind)
                 if key == normalize(x["name"]) or (x.get("slug") and key == normalize(x["slug"]))), None)


def version_tuple(text):
    if not re.fullmatch(r"\d+(?:\.\d+){0,3}", text):
        raise ValueError("Use an engine version such as 19.6.1, not a marketing year")
    parts = tuple(int(x) for x in text.split("."))
    if parts[0] >= 100:
        raise ValueError("Use an engine version: FileMaker 2025 = 22; 2026 = 26")
    return (parts + (0, 0, 0))[:4]


def version_status(origin, target):
    current = version_tuple(target)
    match = re.fullmatch(r"(\d+(?:\.\d+){0,3})( or earlier)?", origin or "")
    if not match:
        return {"status": "unknown", "target": target, "introduced": origin}
    minimum = version_tuple(match[1])
    if current < minimum:
        status = "unknown" if match[2] else "unavailable"
    else:
        status = "minimum-met"
    return {"status": status, "target": target, "introduced": origin,
            "snapshot_scope": "beyond-snapshot" if current > version_tuple("26.0.3") else "within-snapshot",
            "caveat": "Introduction check only. Later options, removals and platform behavior are not version-validated."}


def lookup(kind, name, version=None, platform=None):
    if version is not None:
        version_tuple(version)
    if platform is not None and platform not in PLATFORMS:
        raise ValueError(f"Platform must be one of {', '.join(PLATFORMS)}")
    record = find(kind, name)
    if record is None:
        result = {"status": "not-found-in-snapshot", "kind": kind, "query": name}
        if kind == "error" and 1552 <= int(name) <= 1559:
            result = {"status": "vendor-error-range", "code": int(name),
                      "summary": "Plug-in-defined error; consult the relevant vendor's documentation."}
        if kind == "error" and 5000 <= int(name) <= 5499:
            result = {"status": "custom-error-range", "code": int(name),
                      "summary": "Application-defined error; inspect this solution's conventions."}
        return result
    result = {"status": "found", "kind": kind, "entry": record,
              "evidence": "local-catalog-only; no FileMaker engine execution"}
    corrections = [item for item in load("errata.json")["corrections"]
                   if item["kind"] == kind and normalize(item["name"]) == normalize(record.get("name", ""))]
    if corrections:
        result["documented_corrections"] = corrections
    if version:
        result["version_check"] = version_status(record.get("originated_in_version"), version)
    if platform:
        if platform not in PLATFORMS:
            raise ValueError(f"Platform must be one of {', '.join(PLATFORMS)}")
        result["platform_check"] = {"product": platform,
            "snapshot_support": record.get("platform_exceptions", {}).get(platform, "Yes") if kind == "step" else "unknown",
            "os_restriction": record.get("os_restriction", "not-specified"),
            "caveat": "Snapshot support only; Partial needs option-specific evidence. OData is not DataAPI."}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for kind in ("function", "step", "field", "error"):
        cmd = sub.add_parser(kind)
        cmd.add_argument("name")
        cmd.add_argument("--version")
        cmd.add_argument("--platform", choices=PLATFORMS)
    search = sub.add_parser("search", help="Search names, categories and syntax without loading all entries into context")
    search.add_argument("kind", choices=("function", "step", "field"))
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()
    try:
        if args.command == "search":
            if not 1 <= args.limit <= 50:
                parser.error("--limit must be between 1 and 50")
            needle = args.query.casefold()
            matches = [x for x in entries(args.kind) if needle in json.dumps(x, ensure_ascii=False).casefold()]
            result = {"status": "search", "total": len(matches), "matches": matches[:args.limit]}
        else:
            if args.version:
                version_tuple(args.version)  # reject malformed versions even for missing names
            result = lookup(args.command, args.name, args.version, args.platform)
    except (ValueError, OSError, KeyError) as error:
        parser.error(str(error))
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 1 if result["status"] == "not-found-in-snapshot" else 0


if __name__ == "__main__":
    raise SystemExit(main())
