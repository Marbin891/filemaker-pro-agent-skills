#!/usr/bin/env python3
"""Build redistributable plugin catalogs from pinned CadenceUX clones.

The importer keeps factual API metadata (names, signatures, parameter names,
versions, platform support, licensing status and links) and the CadenceUX
synthesis that is licensed CC BY 4.0.  Vendor documentation prose and vendor
example code are deliberately not copied, because the three vendor docsets do
not grant redistribution rights.  See ATTRIBUTION.md and THIRD-PARTY.md.

Run from the repository root with the reviewed clones in ../sources:

    python3 scripts/import_plugin_catalogs.py ../sources
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "goya-be-plugin-skill": ("goya-be-plugin", "29579288cba843286b5c15275cd5d23e7bb37f40"),
    "beezwax-bbox-plugin-skill": ("beezwax-bbox-plugin", "0c4179ddfd5428f514f85f75f2a68d1001ec4483"),
    "monkeybread-mbs-plugin-skill": ("monkeybread-mbs-plugin", "946bdca12c2117defb4dc2b8959ee00f04c74086"),
    "fmp-dev-orchestrator-skill": ("fmp-dev-orchestrator", "1fe0b8f8682a0bf569a8c4df3ab9aaeab94f405e"),
}

POLICY = {
    "retained": "Factual API metadata and CadenceUX CC BY 4.0 synthesis",
    "omitted": "Vendor documentation prose, vendor parameter descriptions, vendor notes and vendor example code",
    "reason": "The vendor documentation sites do not declare a redistribution licence. Consult the linked vendor page for full prose and examples.",
}


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parameter_names(parameters):
    result = []
    for parameter in parameters or []:
        item = {"name": parameter.get("name", "")}
        if "optional" in parameter:
            item["optional"] = bool(parameter["optional"])
        if "default" in parameter:
            item["default"] = parameter["default"]
        result.append(item)
    return result


def version_history(history):
    result = []
    for item in history or []:
        entry = {"version": item.get("version", "")}
        if item.get("change"):
            entry["change"] = item["change"]
        result.append(entry)
    return result


def be_catalog(source):
    data = json.loads(source.read_text(encoding="utf-8"))
    categories = {}
    for name, category in data["categories"].items():
        functions = []
        for entry in category["functions"]:
            reduced = {
                "name": entry["name"],
                "signature": entry.get("signature", ""),
                "parameters": parameter_names(entry.get("parameters")),
                "keywords": entry.get("keywords", []),
                "version_history": version_history(entry.get("version_history")),
                "compatibility": entry.get("compatibility", {}),
                "url": entry.get("url", ""),
            }
            # These are CadenceUX's correction notices, not vendor prose.
            if "doc_bug_note" in entry:
                reduced["doc_bug_note"] = entry["doc_bug_note"]
            functions.append(reduced)
        categories[name] = {"notes": category.get("notes", ""), "functions": functions}
    deprecated = []
    for entry in data.get("deprecated", []):
        deprecated.append({
            "name": entry["name"],
            "status": entry.get("status", ""),
            "reason": entry.get("reason", ""),
            "replaced_by": entry.get("replaced_by", ""),
            "signature": entry.get("signature", ""),
            "parameters": parameter_names(entry.get("parameters")),
            "keywords": entry.get("keywords", []),
            "version_history": version_history(entry.get("version_history")),
            "url": entry.get("url", ""),
        })
    active = sum(len(value["functions"]) for value in categories.values())
    unique = len({entry["name"] for category in categories.values() for entry in category["functions"]})
    result = {
        "meta": {
            "adapted_from": "CadenceUX goya-be-plugin 1.4.1",
            "source_commit": PINS["goya-be-plugin-skill"][1],
            "vendor": data["meta"].get("vendor", "Goya Pty Ltd"),
            "source_repo": data["meta"].get("source_repo", ""),
            "plugin_version_at_build": data["meta"].get("plugin_version_at_build", ""),
            "active_function_count": unique,
            "unique_function_count": unique,
            "catalog_entry_count": active,
            "deprecated_count": len(deprecated),
            "category_count": len(categories),
            "content_policy": POLICY,
            "field_note": "Each entry retains signature, parameter names/flags/defaults, keywords, version history, platform support and the vendor URL. Prose and examples are not copied; see the URL.",
        },
        "categories": categories,
        "deprecated": deprecated,
        "constants": data.get("constants", {}),
    }
    return result


def bbox_catalog(source):
    data = json.loads(source.read_text(encoding="utf-8"))
    categories = {}
    statuses = {}
    for name, category in data["categories"].items():
        functions = {}
        for key, entry in category["functions"].items():
            status = entry.get("doc_status", "")
            statuses[status] = statuses.get(status, 0) + 1
            reduced = {
                "name": entry.get("name", key),
                "signature": entry.get("signature", ""),
                "doc_status": status,
                "url": entry.get("url", ""),
                "parameters": parameter_names(entry.get("parameters")),
                "result": entry.get("result", ""),
                "error_reference": entry.get("error_reference", ""),
                "script_step_equivalent": entry.get("script_step_equivalent", ""),
            }
            for field in ("since", "compatibility", "deprecated", "doc_bug_note"):
                if field in entry:
                    reduced[field] = entry[field]
            functions[key] = reduced
        categories[name] = {"notes": category.get("notes", ""), "functions": functions}
    result = {
        "meta": {
            "adapted_from": "CadenceUX beezwax-bbox-plugin 1.1.1",
            "source_commit": PINS["beezwax-bbox-plugin-skill"][1],
            "vendor": data["meta"].get("vendor", "Beezwax Datatools, Inc."),
            "product_url": data["meta"].get("product_url", ""),
            "source_repo": data["meta"].get("source_repo", ""),
            "plugin_version_at_build": data["meta"].get("plugin_version_at_build", ""),
            "plugin_build_at_build": data["meta"].get("plugin_build_at_build", ""),
            "plugin_version_documented_date": data["meta"].get("plugin_version_documented_date", ""),
            "function_count": sum(len(c["functions"]) for c in categories.values()),
            "category_count": len(categories),
            "doc_status_counts": statuses,
            "content_policy": POLICY,
            "field_note": "Each entry retains signature, parameter names/flags, result, error reference, script-step equivalent, version, platform support and the vendor URL. Prose and examples are not copied; see the URL.",
        },
        "categories": categories,
        "shared_reference": data.get("shared_reference", {}),
    }
    return result


def mbs_catalog(source_dir, dest):
    index = json.loads((source_dir / "references/index.json").read_text(encoding="utf-8"))
    (dest / "references").mkdir(parents=True, exist_ok=True)
    for stale in (dest / "references").glob("group-*.json"):
        stale.unlink()
    reduced_index = {key: value for key, value in index.items() if key != "components"}
    reduced_index["upstream_skill_version"] = reduced_index.get("version", "")
    reduced_index["version"] = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    reduced_index["adapted_from"] = "CadenceUX monkeybread-mbs-plugin 2.0.1"
    reduced_index["source_commit"] = PINS["monkeybread-mbs-plugin-skill"][1]
    reduced_index["content_policy"] = POLICY
    reduced_index["field_note"] = (
        "Each entry retains signature, parameter names/flags, result, version introduced, "
        "platform support, licensing status, deprecation flag, see-also links and the vendor URL. "
        "Descriptions and examples are not copied; see the URL."
    )
    components = {}
    total = 0
    for name, summary in index["components"].items():
        group_name = Path(summary["file"]).name
        group = json.loads((source_dir / "references" / group_name).read_text(encoding="utf-8"))
        component = group["components"][name]
        functions = []
        for entry in component["functions"]:
            functions.append({
                "name": entry["name"],
                "signature": entry.get("signature", ""),
                "parameters": parameter_names(entry.get("parameters")),
                "result": entry.get("result", ""),
                "version_introduced": entry.get("version_introduced", ""),
                "prerelease": bool(entry.get("prerelease", False)),
                "deprecated": bool(entry.get("deprecated", False)),
                "compatibility": entry.get("compatibility", {}),
                "see_also": entry.get("see_also", []),
                "status": entry.get("status", ""),
                "url": entry.get("url", ""),
            })
        total += len(functions)
        target = dest / "references" / group_name
        if target.exists():
            group = json.loads(target.read_text(encoding="utf-8"))
        else:
            group = {"components": {}}
        group["components"][name] = {
            "component": name,
            "function_count": len(functions),
            "status_counts": component.get("status_counts", {}),
            "prerelease_count": component.get("prerelease_count", 0),
            "deprecated_count": component.get("deprecated_count", 0),
            "requires_addon": component.get("requires_addon", ""),
            "functions": functions,
        }
        write(target, group)
        components[name] = {
            "file": "references/" + group_name,
            "function_count": len(functions),
            "status_counts": component.get("status_counts", {}),
            "prerelease_count": component.get("prerelease_count", 0),
            "deprecated_count": component.get("deprecated_count", 0),
        }
    reduced_index["components"] = components
    reduced_index["catalog_function_count"] = total
    write(dest / "references/index.json", reduced_index)
    return total, len(components)


def provenance(name, source_dir, files):
    records = []
    for relative in files:
        path = source_dir / relative
        records.append({"path": relative, "bytes": path.stat().st_size, "sha256": sha(path)})
    return {
        "repository": "https://github.com/CadenceUX/" + name,
        "commit": PINS[name][1],
        "version": (source_dir / "VERSION").read_text(encoding="utf-8").strip(),
        "license_declaration": "CC-BY-4.0 declared in README.md; vendor documentation rights remain with each vendor",
        "treatment": "Adapted factual catalog plus CadenceUX CC BY synthesis; vendor prose and examples omitted",
        "source_files": records,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sources", type=Path, help="Directory containing the four reviewed clones")
    args = parser.parse_args()
    sources = args.sources.resolve()
    for repo, (_, pin) in PINS.items():
        path = sources / repo
        commit = subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()
        if commit != pin:
            parser.error(f"{repo}: expected {pin}, got {commit}; review before changing pins")
        if subprocess.check_output(["git", "-C", str(path), "status", "--porcelain", "--untracked-files=no"], text=True).strip():
            parser.error(f"{repo}: tracked files modified; use a clean checkout")

    be_dir = sources / "goya-be-plugin-skill"
    be = be_catalog(be_dir / "references/function-catalog.json")
    write(ROOT / "goya-be-plugin/references/function-catalog.json", be)
    write(ROOT / "goya-be-plugin/references/provenance.json", provenance(
        "goya-be-plugin-skill", be_dir, ["SKILL.md", "VERSION", "README.md", "references/function-catalog.json"]))

    bbox_dir = sources / "beezwax-bbox-plugin-skill"
    bbox = bbox_catalog(bbox_dir / "references/function-catalog.json")
    write(ROOT / "beezwax-bbox-plugin/references/function-catalog.json", bbox)
    write(ROOT / "beezwax-bbox-plugin/references/provenance.json", provenance(
        "beezwax-bbox-plugin-skill", bbox_dir, ["SKILL.md", "VERSION", "README.md", "references/function-catalog.json"]))

    mbs_dir = sources / "monkeybread-mbs-plugin-skill"
    mbs_total, mbs_components = mbs_catalog(mbs_dir, ROOT / "monkeybread-mbs-plugin")
    mbs_files = ["SKILL.md", "VERSION", "README.md", "references/index.json"] + [
        "references/" + path.name for path in sorted((mbs_dir / "references").glob("group-*.json"))]
    write(ROOT / "monkeybread-mbs-plugin/references/provenance.json", provenance(
        "monkeybread-mbs-plugin-skill", mbs_dir, mbs_files))

    orch_dir = sources / "fmp-dev-orchestrator-skill"
    write(ROOT / "fmp-dev-orchestrator/references/provenance.json", provenance(
        "fmp-dev-orchestrator-skill", orch_dir, ["SKILL.md", "VERSION", "README.md", "references/stack-check.md"]))

    print(json.dumps({
        "be_functions": be["meta"]["active_function_count"],
        "be_deprecated": be["meta"]["deprecated_count"],
        "bbox_functions": bbox["meta"]["function_count"],
        "mbs_functions": mbs_total,
        "mbs_components": mbs_components,
    }, indent=2))


if __name__ == "__main__":
    main()
