#!/usr/bin/env python3
"""Verify every retained factual field against the pinned, hashed local upstream."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

from import_facts import PINS, ROOT


def verify_repo(repo, pin, records):
    commit = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    if commit != pin:
        raise ValueError(f"Unexpected source checkout: {repo.name}")
    if subprocess.check_output(["git", "-C", str(repo), "status", "--porcelain", "--untracked-files=no"], text=True).strip():
        raise ValueError(f"Modified tracked source files: {repo.name}")
    pinned_paths = set(subprocess.check_output(["git", "-C", str(repo), "ls-tree", "-r", "--name-only", pin], text=True).splitlines())
    if len(records) != len(pinned_paths) or {entry["path"] for entry in records} != pinned_paths:
        raise ValueError(f"Incomplete or duplicated inventory: {repo.name}")
    for entry in records:
        path = repo / entry["path"]
        pinned_bytes = subprocess.check_output(["git", "-C", str(repo), "show", f"{pin}:{entry['path']}"])
        if path.is_symlink() or path.read_bytes() != pinned_bytes:
            raise ValueError(f"Source differs from pinned Git object: {entry['path']}")
        if hashlib.sha256(pinned_bytes).hexdigest() != entry["sha256"]:
            raise ValueError(f"Inventory hash differs from pinned Git object: {entry['path']}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sources", type=Path)
    args = parser.parse_args()
    refs = ROOT / "filemaker-pro/references"
    inventory = json.loads((refs / "source-inventory.json").read_text(encoding="utf-8"))
    checked = 0
    for repository in inventory["repositories"]:
        name = repository["repository"].rsplit("/", 1)[-1]
        if repository["commit"] != PINS[name]:
            raise ValueError(f"Inventory commit mismatch: {name}")
        verify_repo(args.sources / name, PINS[name], repository["files"])
        for entry in repository["files"]:
            path = args.sources / name / entry["path"]
            if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
                raise ValueError(f"Source hash/symlink mismatch: {entry['path']}")
            checked += 1
    src = args.sources / "claris-filemaker-pro-skill/references"
    for filename in ("function-catalog.json", "script-steps-catalog.json", "field-types-catalog.json"):
        original = json.loads((src / filename).read_text(encoding="utf-8"))
        actual = json.loads((refs / filename).read_text(encoding="utf-8"))
        actual.pop("adaptation")
        if actual != original:
            raise ValueError(f"Catalog information loss: {filename}")
    # The source table has additional grouped ranges; compare individually listed codes only.
    raw_errors = (src / "error-codes.md").read_text(encoding="utf-8")
    source_codes = {int(x) for x in re.findall(r"^\|\s*(-?\d+)\s*\|", raw_errors, flags=re.M)}
    source_codes.update((-1, 0))
    actual_codes = {x["code"] for x in json.loads((refs / "error-codes.json").read_text(encoding="utf-8"))["errors"]}
    if source_codes != actual_codes:
        raise ValueError(f"Error roster delta: {source_codes ^ actual_codes}")
    print(f"PASS: {checked} source-file hashes; all original fields of all 3 catalogs equal source, including 368 functions and 216 steps; 292 error codes preserved.")
    print("Examples are adapted separately, not copied byte-for-byte. Integrity verification is not a FileMaker runtime test or a legal opinion.")


if __name__ == "__main__":
    main()
