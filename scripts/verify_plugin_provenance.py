#!/usr/bin/env python3
"""Verify pinned plugin catalogs against their reviewed local clones.

Reads only JSON, Markdown and Git metadata. It does not fetch, install or execute
upstream code. A PASS proves catalog reproducibility from the pinned sources, not
vendor-documentation completeness, FileMaker behaviour or legal clearance.
"""
import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import import_plugin_catalogs as importer

ROOT = Path(__file__).resolve().parents[1]
CHECKS = {
    "goya-be-plugin": ("goya-be-plugin-skill", importer.be_catalog, ["references/function-catalog.json"]),
    "beezwax-bbox-plugin": ("beezwax-bbox-plugin-skill", importer.bbox_catalog, ["references/function-catalog.json"]),
}


def check_provenance(skill, source_dir):
    path = ROOT / skill / "references/provenance.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    commit = subprocess.check_output(["git", "-C", str(source_dir), "rev-parse", "HEAD"], text=True).strip()
    if commit != data["commit"]:
        raise ValueError(f"{skill}: commit mismatch")
    for record in data["source_files"]:
        source = source_dir / record["path"]
        if not source.is_file() or source.is_symlink():
            raise ValueError(f"{skill}: missing source {record['path']}")
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        if digest != record["sha256"] or source.stat().st_size != record["bytes"]:
            raise ValueError(f"{skill}: source hash mismatch {record['path']}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sources", type=Path, help="Directory containing the six reviewed clones")
    args = parser.parse_args()
    sources = args.sources.resolve()
    for skill, (repo, transform, outputs) in CHECKS.items():
        source_dir = sources / repo
        check_provenance(skill, source_dir)
        generated = transform(source_dir / "references/function-catalog.json")
        for relative in outputs:
            current = json.loads((ROOT / skill / relative).read_text(encoding="utf-8"))
            if current != generated:
                raise ValueError(f"{skill}: {relative} differs from a fresh transformation")
    mbs_dir = sources / "monkeybread-mbs-plugin-skill"
    check_provenance("monkeybread-mbs-plugin", mbs_dir)
    with tempfile.TemporaryDirectory() as temporary:
        destination = Path(temporary)
        total, components = importer.mbs_catalog(mbs_dir, destination)
        current_index = json.loads((ROOT / "monkeybread-mbs-plugin/references/index.json").read_text(encoding="utf-8"))
        generated_index = json.loads((destination / "references/index.json").read_text(encoding="utf-8"))
        if current_index != generated_index:
            raise ValueError("monkeybread-mbs-plugin: index differs from a fresh transformation")
        for source in sorted((ROOT / "monkeybread-mbs-plugin/references").glob("group-*.json")):
            generated = destination / "references" / source.name
            if not generated.is_file() or source.read_bytes() != generated.read_bytes():
                raise ValueError(f"monkeybread-mbs-plugin: {source.name} differs from a fresh transformation")
        if (total, components) != (7859, 245):
            raise ValueError("monkeybread-mbs-plugin: unexpected counts")
    print("PASS: plugin provenance hashes and catalog transformations match the pinned sources; "
          "no upstream code was executed. This is not a vendor-completeness or legal review.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)
