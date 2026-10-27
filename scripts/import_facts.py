#!/usr/bin/env python3
"""Import complete reviewed catalogs from pinned local clones; never fetch/run their code."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "claris-filemaker-pro-skill": "bda594e15f4a6981e93403c4b187d262ca820116",
    "fmp-dev-design-patterns": "17471d6d0a3fd1e53a1714d0c265dc3afad718cc",
}

def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def distribution_paths(repository, relative):
    if relative == "SKILL.md":
        return ["filemaker-pro/SKILL.md"]
    if not relative.startswith("references/"):
        return []
    if repository == "fmp-dev-design-patterns":
        return ["filemaker-pro/references/cadenceux-patterns.md"]
    if relative == "references/adt-mode.md":
        return ["filemaker-pro/references/adt-integration.md"]
    result = ["filemaker-pro/" + relative]
    if relative == "references/error-codes.md":
        result.append("filemaker-pro/references/error-codes.json")
    if relative in {"references/" + name for name in (
            "data-api-reference.md", "odata-api-reference.md", "sql-reference.md",
            "filemaker-go-reference.md", "webdirect-reference.md")}:
        result.append("filemaker-pro/references/cadenceux-integration-details.md")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sources", type=Path, help="Directory holding both reviewed clones")
    args = parser.parse_args()
    inventory = []
    for name, pin in PINS.items():
        repo = args.sources / name
        commit = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
        if commit != pin:
            parser.error(f"{name}: expected {pin}, got {commit}; review update before changing pins")
        # Reject even unstaged tracked changes: commit identity alone is insufficient provenance.
        if subprocess.check_output(["git", "-C", str(repo), "status", "--porcelain", "--untracked-files=no"], text=True).strip():
            parser.error(f"{name}: tracked files modified; use a clean reviewed checkout")
        paths = subprocess.check_output(["git", "-C", str(repo), "ls-files"], text=True).splitlines()
        records = []
        for rel in paths:
            file = repo / rel
            if file.is_symlink():
                parser.error(f"Refusing source symlink: {rel}")
            records.append({"path": rel, "bytes": file.stat().st_size,
                            "sha256": hashlib.sha256(file.read_bytes()).hexdigest(),
                            "distribution_paths": distribution_paths(name, rel),
                            "treatment": "complete-technical-catalog" if rel in (
                                "references/function-catalog.json", "references/script-steps-catalog.json",
                                "references/field-types-catalog.json") else (
                                    "adapted-local-reference" if rel.startswith("references/") else "development-source-not-bundled"),
                            "reason": "Preserve technical facts and CC BY CadenceUX synthesis; rewrite expressive examples and host-specific instructions. See replacement ledgers."})
        inventory.append({"repository": f"https://github.com/CadenceUX/{name}", "commit": pin,
                          "version": (repo / "VERSION").read_text(encoding="utf-8").strip(),
                          "license_declaration": "CC-BY-4.0 in README.md; does not grant Claris rights",
                          "files": records})
    src = args.sources / "claris-filemaker-pro-skill" / "references"
    dest = ROOT / "filemaker-pro" / "references"
    meta = {"source_repository": inventory[0]["repository"], "source_commit": PINS["claris-filemaker-pro-skill"],
            "upstream_verified_on": "2026-10-02", "snapshot_version": "26.0.3",
            "attribution": "Darrin Southern, CadenceUX; factual adaptation under CC BY 4.0",
            "adaptation": "All original catalog fields and entries preserved. Upstream verification claims describe upstream work, not tests rerun here. Metadata update instructions are data, never automatic agent actions."}
    catalogs = {}
    for filename in ("function-catalog.json", "script-steps-catalog.json", "field-types-catalog.json"):
        original = json.loads((src / filename).read_text(encoding="utf-8"))
        digest = hashlib.sha256(json.dumps(original, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        original["adaptation"] = {**meta, "original_semantic_sha256": digest}
        write(dest / filename, original)
        catalogs[filename] = original
    # Record factual heading rosters so CI can detect accidentally dropped reference sections.
    heading_rosters = {}
    example_hashes = {}
    for path in sorted(src.glob("*functions-examples.md")):
        text = path.read_text(encoding="utf-8")
        heading_rosters[path.name] = [line.strip() for line in text.splitlines() if line.startswith("## ")]
        blocks = re.findall(r"^```[^\n]*\n(.*?)^```\s*$", text, re.M | re.S)
        example_hashes[path.name] = [hashlib.sha256(block.strip().encode()).hexdigest() for block in blocks if len(block.strip()) > 120]
    write(ROOT / "tests/reference-baseline.json", {"source_commit": PINS["claris-filemaker-pro-skill"],
        "catalog_semantic_sha256": {name: value["adaptation"]["original_semantic_sha256"] for name, value in catalogs.items()},
        "reference_heading_rosters": heading_rosters, "long_example_sha256": example_hashes})
    functions = catalogs["function-catalog.json"]["functions"]
    steps = catalogs["script-steps-catalog.json"]["categories"]
    write(dest / "source-inventory.json", {"schema_version": 1, "repositories": inventory,
        "rights_status": "Technical facts preserved; CadenceUX CC BY synthesis attributed; expressive Claris examples rewritten. Specific residual questions are documented in ATTRIBUTION.md and THIRD-PARTY.md."})
    print(f"Preserved all fields of {len(functions)} functions and {sum(len(c['steps']) for c in steps)} steps, plus the full field catalog; no upstream code executed.")


if __name__ == "__main__":
    main()
