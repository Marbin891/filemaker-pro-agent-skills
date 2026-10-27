#!/usr/bin/env python3
"""Bounded static checks on project-owned code and built packages; no network or execution."""
import ast
import hashlib
import json
import re
import zipfile
from pathlib import Path

import build

ROOT = build.ROOT
NETWORK_MODULES = {"requests", "urllib", "http", "socket", "httpx", "aiohttp", "ftplib", "telnetlib"}
SECRETS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{32,}\b"),
    re.compile(r"\bAKIA[A-Z0-9]{16}\b"),
)
FORBIDDEN = (".git/", ".claude", ".DS_Store", "__pycache__", ".fmp12", "tests/", "README", "dist/", "maintainer/")


def audit():
    findings = []
    scanned = []
    for folder in [ROOT / "scripts"] + [ROOT / name / "scripts" for name in build.SKILLS]:
        for path in sorted(folder.glob("*.py")):
            text = path.read_text(encoding="utf-8")
            tree = ast.parse(text, filename=str(path))
            scanned.append(str(path.relative_to(ROOT)))
            for node in ast.walk(tree):
                names = []
                if isinstance(node, ast.Import):
                    names = [x.name.split(".")[0] for x in node.names]
                elif isinstance(node, ast.ImportFrom):
                    names = [(node.module or "").split(".")[0]]
                if NETWORK_MODULES.intersection(names):
                    findings.append(f"Network module in production/helper code: {path.name}:{node.lineno}")
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ("eval", "exec", "__import__"):
                    findings.append(f"Dynamic execution: {path.name}:{node.lineno}")
                if isinstance(node, ast.Call):
                    for keyword in node.keywords:
                        if keyword.arg == "shell" and isinstance(keyword.value, ast.Constant) and keyword.value.value is True:
                            findings.append(f"shell=True: {path.name}:{node.lineno}")

    text_count = 0
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in (".git", "__pycache__", "dist") or part.startswith(".venv")
                                    for part in path.relative_to(ROOT).parts):
            continue
        if path.suffix not in (".md", ".py", ".json", ".yaml", ".yml", ".txt") and path.name not in ("LICENSE", "VERSION"):
            continue
        text = path.read_text(encoding="utf-8")
        text_count += 1
        for pattern in SECRETS:
            if pattern.search(text):
                findings.append(f"Credential-like content: {path.relative_to(ROOT)} (value redacted)")

    manifest = json.loads((ROOT / "dist/manifest.json").read_text(encoding="utf-8"))
    expected_payloads = {name: build.prepare_skill(name) for name in build.SKILLS}
    def check_integrity(archive, info, expected):
        names = archive.namelist()
        if len(names) != len(set(names)):
            findings.append(f"Duplicate entries: {info['path']}")
        if set(names) != set(expected):
            findings.append(f"Payload allowlist mismatch: {info['path']}")
        for name in set(names).intersection(expected):
            if archive.read(name) != expected[name]:
                findings.append(f"Payload drift: {info['path']}:{name}")
        raw = (ROOT / "dist" / info["path"]).read_bytes()
        if hashlib.sha256(raw).hexdigest() != info["sha256"]:
            findings.append(f"Archive SHA-256 mismatch: {info['path']}")
        records = {entry['path']: entry for entry in info['files']}
        if set(records) != set(names):
            findings.append(f"Manifest entries differ: {info['path']}")
        for name in set(names).intersection(records):
            data = archive.read(name)
            if records[name]['sha256'] != hashlib.sha256(data).hexdigest() or records[name]['bytes'] != len(data):
                findings.append(f"Manifest hash/size mismatch: {info['path']}:{name}")
    for name, info in manifest["skills"].items():
        path = ROOT / "dist" / info["path"]
        with zipfile.ZipFile(path) as archive:
            check_integrity(archive, info, {f"{name}/{p}": data for p, data in expected_payloads[name].items()})
            names = archive.namelist()
            if archive.testzip() is not None:
                findings.append(f"CRC failure: {path.name}")
            if {x.split("/", 1)[0] for x in names} != {name}:
                findings.append(f"Skill ZIP has more than one top-level folder: {path.name}")
            if sum(x.lower().endswith("/skill.md") for x in names) != 1:
                findings.append(f"Skill ZIP does not contain exactly one SKILL.md: {path.name}")
            for entry in names:
                if any(token in entry for token in FORBIDDEN):
                    findings.append(f"Forbidden package member {entry} in {path.name}")
            for entry in archive.infolist():
                if ".." in Path(entry.filename).parts or entry.filename.startswith(("/", "\\")) or "\\" in entry.filename:
                    findings.append(f"Unsafe archive path in {path.name}: {entry.filename}")
                if entry.external_attr >> 16 != 0o100644:
                    findings.append(f"Non-regular archive entry in {path.name}: {entry.filename}")

    plugin = ROOT / "dist/plugin.zip"
    with zipfile.ZipFile(plugin) as archive:
        check_integrity(archive, manifest["plugin"], build.plugin_payload(expected_payloads))
        names = archive.namelist()
        if "plugin.json" not in names:
            findings.append("Plugin ZIP has no root plugin.json")
        if archive.testzip() is not None:
            findings.append("Plugin ZIP CRC failure")
        skill_manifests = [x for x in names if x.startswith("skills/") and x.endswith("/SKILL.md")]
        if len(skill_manifests) != len(build.SKILLS):
            findings.append("Plugin ZIP does not contain every skill")
        for entry in archive.infolist():
            if ".." in Path(entry.filename).parts or entry.filename.startswith(("/", "\\")) or "\\" in entry.filename:
                findings.append(f"Unsafe plugin archive path: {entry.filename}")
            if entry.external_attr >> 16 != 0o100644:
                findings.append(f"Non-regular plugin archive entry: {entry.filename}")

    result = {
        "review_date": "2026-10-27",
        "automated_status": "PASS" if not findings else "FAIL",
        "python_files_checked": scanned,
        "text_files_scanned": text_count,
        "artifacts": {
            "plugin": {"sha256": hashlib.sha256(plugin.read_bytes()).hexdigest(), "bytes": plugin.stat().st_size},
            "skills": {name: {"sha256": hashlib.sha256((ROOT / "dist" / info["path"]).read_bytes()).hexdigest(),
                              "bytes": (ROOT / "dist" / info["path"]).stat().st_size}
                       for name, info in manifest["skills"].items()},
        },
        "findings": findings,
        "limits": [
            "Pattern/AST checks cannot prove absence of malware, prompt injection or credentials.",
            "No runtime sandbox, dependency-binary, Git history or legal audit.",
            "Human review must inspect prompts, tool contracts and authorization behavior.",
            "No ChatGPT/Codex host or FileMaker engine acceptance is performed.",
        ],
    }
    (ROOT / "docs/STATIC-AUDIT.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(audit())
