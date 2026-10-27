#!/usr/bin/env python3
"""Deterministic routing helper for the FileMaker skill set. No network or model call."""
import argparse
import json
import re

SKILLS = ("filemaker-pro", "goya-be-plugin", "monkeybread-mbs-plugin", "beezwax-bbox-plugin")

MARKERS = {
    "goya-be-plugin": [r"\bBE_[A-Za-z0-9_]*", r"\bBaseElements\b"],
    "monkeybread-mbs-plugin": [r"\bMBS\b", r"\bMonkeybread\b", r"\bDynaPDF\b", r"\bLibXL\b", r"\bSaxon\b"],
    "beezwax-bbox-plugin": [r"\bbBox_[A-Za-z0-9_]+", r"\bbBox\b", r"\bBeezwax\b"],
}
NATIVE = [
    r"\bFileMaker\b", r"\bClaris\b", r"\bcalculation\b", r"\bscript step\b",
    r"\bSet Variable\b", r"\bIf\s*\[", r"\bExecuteSQL\b", r"\bData API\b",
    r"\bOData\b", r"\bWebDirect\b", r"\bFileMaker Go\b", r"\berror code\b",
    r"\bfield type\b", r"\bschema\b", r"\blayout\b", r"\brelationship\b",
    r"\btransaction\b", r"\bOpen Transaction\b", r"\bPSoS\b",
    r"\bPerform Script on Server\b", r"\bServer\b",
    r"\biOS App SDK\b", r"\bcalculo\b", r"\bcálculo\b", r"\bguion\b", r"\bguión\b",
]
STRONG_NATIVE = [
    r"\bscript step\b", r"\bSet Variable\b", r"\bIf\s*\[", r"\bExecuteSQL\b",
    r"\bData API\b", r"\bOData\b", r"\bWebDirect\b", r"\bOpen Transaction\b",
    r"\bPSoS\b", r"\bPerform Script on Server\b", r"\bfield type\b",
    r"\bcalculation\b", r"\blayout\b", r"\brelationship\b", r"\berror code\b",
    r"\bscript\b", r"\bnative\b",
    r"\bFileMaker Go\b", r"\biOS App SDK\b", r"\bServer\b",
    r"\bcalculo\b", r"\bcálculo\b", r"\bguion\b", r"\bguión\b", r"\bnativo\b",
]
NEGATIVE = [r"\bPostgreSQL\b", r"\bExcel\b", r"\bgeneric JSON\b", r"\bPower BI\b"]


def matches(patterns, text):
    found = []
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.I):
            found.append(match.group(0))
    return found


def route(prompt):
    text = prompt or ""
    if not text.strip():
        raise ValueError("prompt must not be blank")
    negative = matches(NEGATIVE, text)
    has_plugin = any(matches(patterns, text) for patterns in MARKERS.values())
    if negative and not has_plugin and not matches([r"\bFileMaker\b", r"\bClaris\b"], text):
        return {
            "status": "no-filemaker-context",
            "skills": [],
            "matched": sorted(set(negative)),
            "reason": "The prompt names a non-FileMaker tool or task and no FileMaker context.",
        }
    scores = {}
    matched = {}
    for skill, patterns in MARKERS.items():
        hits = matches(patterns, text)
        if hits:
            scores[skill] = 10 + len(hits)
            matched[skill] = sorted(set(hits))
    native_hits = matches(NATIVE, text)
    strong_native = matches(STRONG_NATIVE, text)
    if native_hits or (has_plugin and strong_native):
        scores["filemaker-pro"] = 2 * max(1, len(native_hits))
        matched["filemaker-pro"] = sorted(set(native_hits + strong_native))
    # A plug-in marker alone should not pull in the native catalog.
    if "filemaker-pro" in scores and scores["filemaker-pro"] < 2:
        scores.pop("filemaker-pro")
    # For a plug-in-only task, add the native skill only if a native script/API
    # signal is present, not merely the word FileMaker.
    plugin_selected = [x for x in scores if x != "filemaker-pro"]
    if plugin_selected and not strong_native:
        scores.pop("filemaker-pro", None)
        matched.pop("filemaker-pro", None)
    ordered = sorted(scores.items(), key=lambda item: (-item[1], SKILLS.index(item[0])))
    skills = [name for name, _ in ordered]
    if not skills:
        return {
            "status": "no-match",
            "skills": [],
            "matched": [],
            "reason": "No FileMaker product or function marker was found. Ask for clarification rather than loading a skill.",
        }
    primary = skills[0]
    return {
        "status": "routed",
        "primary": primary,
        "supporting": skills[1:],
        "skills": skills,
        "matched": {name: matched[name] for name in skills},
        "evidence": "routing-contract-only",
        "reason": "Selected from explicit plug-in markers and native FileMaker signals.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("route")
    p.add_argument("prompt")
    sub.add_parser("list")
    args = parser.parse_args()
    if args.command == "list":
        print(json.dumps({"skills": list(SKILLS)}, indent=2))
        return 0
    try:
        result = route(args.prompt)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["skills"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
