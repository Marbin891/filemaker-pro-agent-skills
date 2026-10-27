#!/usr/bin/env python3
"""Scan FileMaker-marked example fences for unknown call names, not engine syntax.

Native and plug-in calls are checked against their owning local catalogs.
Bounded BE/MBS argument counts are checked where metadata is explicit.
This is a lexical inventory only, not a FileMaker parser.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FUNCTION_CATALOG = ROOT / "filemaker-pro/references/function-catalog.json"
# Explicitly defined optional custom functions, not built-ins.
DECLARED_CUSTOM = {"cadenceux-patterns.md": {"haserror_cf", "hasoptionbit_cf", "portalnext", "portalprev"}}
PLUGIN_PREFIXES = ("be_", "mbs", "bbox_")


def plugin_entries():
    result = {}
    for skill in ("goya-be-plugin", "beezwax-bbox-plugin"):
        data = json.loads((ROOT / skill / "references/function-catalog.json").read_text(encoding="utf-8"))
        for category in data["categories"].values():
            functions = category["functions"]
            for entry in (functions.values() if isinstance(functions, dict) else functions):
                result[entry["name"].casefold()] = entry
    for path in (ROOT / "monkeybread-mbs-plugin/references").glob("group-*.json"):
        for block in json.loads(path.read_text(encoding="utf-8"))["components"].values():
            for entry in block["functions"]:
                result["mbs:" + entry["name"].casefold()] = entry
    return result


def arguments(masked, raw, start):
    stack, values, beginning = [], [], start
    for position in range(start, len(masked)):
        char = masked[position]
        if char == ")" and not stack:
            value = raw[beginning:position].strip()
            return values + ([value] if value else [])
        if char in "([":
            stack.append(char)
        elif char in ")]":
            if stack:
                stack.pop()
        elif char == ";" and not stack:
            values.append(raw[beginning:position].strip())
            beginning = position + 1
    return None


def example_paths():
    paths = []
    for skill in ("filemaker-pro", "goya-be-plugin", "monkeybread-mbs-plugin",
                  "beezwax-bbox-plugin", "fmp-dev-orchestrator"):
        paths.append(ROOT / skill / "SKILL.md")
        paths.extend(sorted((ROOT / skill / "references").glob("*.md")))
    return [path for path in paths if path.is_file()]


def scan():
    functions = json.loads(FUNCTION_CATALOG.read_text(encoding="utf-8"))["functions"]
    normalize = lambda text: re.sub(r"\s+", "", text).casefold()
    known = {normalize(x["name"]) for x in functions}
    ordinary = {name for name in known if not name.startswith("get(")}
    plugins = plugin_entries()
    unknown = []
    fences = 0
    calls = 0
    arity_issues = []
    for path in example_paths():
        text = path.read_text(encoding="utf-8")
        for match in re.finditer(r"^```filemaker[^\n]*\n(.*?)^```\s*$", text, re.M | re.S):
            fences += 1
            code = re.sub(r'"(?:\\.|[^"\\])*"|/\*.*?\*/|//[^\n]*', lambda m: " " * len(m[0]), match[1], flags=re.S)
            for call in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*)[ \t]*\(", code):
                name = call[1].casefold()
                if name in {"and", "or", "not", "xor"}:
                    continue
                calls += 1
                if name == "get":
                    parameter = re.match(r"\s*([A-Za-z][A-Za-z0-9]*)\s*\)", code[call.end():])
                    valid = parameter and normalize(f"Get({parameter[1]})") in known
                elif name.startswith(PLUGIN_PREFIXES):
                    args = arguments(code, match[1], call.end())
                    key = name
                    if name == "mbs" and args:
                        try:
                            key = "mbs:" + json.loads(args[0]).casefold()
                        except (ValueError, AttributeError):
                            key = "unknown-dynamic-mbs-name"
                    entry = plugins.get(key)
                    valid = entry is not None
                    if entry and args is not None and name != "bbox_":
                        parameters = entry.get("parameters", [])
                        if all("optional" in item for item in parameters) and "..." not in entry.get("signature", ""):
                            count = len(args) - (1 if name == "mbs" else 0)
                            required = sum(not item["optional"] for item in parameters)
                            if not required <= count <= len(parameters):
                                arity_issues.append({"file": str(path.relative_to(ROOT)), "call": call[1],
                                                     "arguments": count, "required": required, "maximum": len(parameters)})
                else:
                    valid = name in ordinary or name in DECLARED_CUSTOM.get(path.name, set())
                if not valid:
                    line = text.count("\n", 0, match.start(1) + call.start()) + 1
                    unknown.append({"file": str(path.relative_to(ROOT)), "line": line, "call": call[1]})
    return {"status": "PASS" if not unknown and not arity_issues else "REVIEW", "filemaker_fences_scanned": fences,
            "call_names_checked": calls, "unknown_calls": unknown,
            "argument_count_issues": arity_issues,
            "limitation": "Lexical call inventory only: not FileMaker parsing, argument validation, type checking, evaluation or engine execution."}


if __name__ == "__main__":
    result = scan()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
