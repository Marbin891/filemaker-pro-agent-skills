#!/usr/bin/env python3
"""Build deterministic individual-skill ZIPs and one portable plugin ZIP.

The two package formats are kept separate on purpose:

* ``dist/skills/<name>.zip`` contains exactly one top-level skill folder.
* ``dist/plugin.zip`` contains ``plugin.json`` at the root and ``skills/<name>/``.

No network access, upstream code execution or executable binary payload is involved.
"""
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
NOTICES = ("LICENSE", "ATTRIBUTION.md", "THIRD-PARTY.md")
PLUGIN_NAME = "filemaker-pro-agent-skills"
PLUGIN_VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
PLUGIN_ASSETS = ("assets/logo-512.png", "assets/icon-128.png")

FILEMAKER_FILES = (
    "SKILL.md", "agents/openai.yaml", "LICENSE", "ATTRIBUTION.md", "THIRD-PARTY.md",
    "scripts/catalog.py", "references/function-catalog.json",
    "references/script-steps-catalog.json", "references/field-types-catalog.json",
    "references/error-codes.json", "references/error-codes.md",
    "references/compatibility.md", "references/architecture.md",
    "references/professional-patterns.md", "references/integrations.md",
    "references/adt-integration.md", "references/worked-examples.md",
    "references/source-inventory.json",
    "references/data-api-reference.md", "references/odata-api-reference.md",
    "references/sql-reference.md", "references/filemaker-go-reference.md",
    "references/webdirect-reference.md", "references/get-functions-examples.md",
    "references/text-functions-examples.md", "references/date-time-functions-examples.md",
    "references/numeric-functions-examples.md", "references/specialty-functions-examples.md",
    "references/logical-json-ai-functions-examples.md", "references/design-container-functions-examples.md",
    "references/cadenceux-integration-details.md", "references/cadenceux-patterns.md",
    "references/help-sitemap.md", "references/replacement-ledger.json",
    "references/errata.json",
)

SKILLS = {
    "filemaker-pro": FILEMAKER_FILES,
    "goya-be-plugin": (
        "SKILL.md", "agents/openai.yaml", "LICENSE", "ATTRIBUTION.md", "THIRD-PARTY.md",
        "scripts/catalog.py", "references/function-catalog.json",
        "references/patterns.md", "references/provenance.json",
    ),
    "beezwax-bbox-plugin": (
        "SKILL.md", "agents/openai.yaml", "LICENSE", "ATTRIBUTION.md", "THIRD-PARTY.md",
        "scripts/catalog.py", "references/function-catalog.json",
        "references/patterns.md", "references/provenance.json",
    ),
    "monkeybread-mbs-plugin": (
        "SKILL.md", "agents/openai.yaml", "LICENSE", "ATTRIBUTION.md", "THIRD-PARTY.md",
        "scripts/catalog.py", "references/index.json", "references/provenance.json",
        "references/component-guide.md",
    ) + tuple(f"references/group-{number:02}.json" for number in range(1, 21)),
    "fmp-dev-orchestrator": (
        "SKILL.md", "agents/openai.yaml", "LICENSE", "ATTRIBUTION.md", "THIRD-PARTY.md",
        "scripts/route.py", "references/routing.md", "references/provenance.json",
    ),
}

FORBIDDEN_PARTS = {".git", ".claude", "__pycache__", ".DS_Store", "tests", "dist", "maintainer"}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def check_destination(path):
    for candidate in (path, *path.parents):
        if candidate.is_symlink():
            raise ValueError(f"Refusing symlink destination or ancestor: {candidate}")


def validate_payload(name, relative, data):
    parts = Path(relative).parts
    if ".." in parts or Path(relative).is_absolute() or "\\" in relative:
        raise ValueError(f"Unsafe payload path: {name}/{relative}")
    if FORBIDDEN_PARTS.intersection(parts):
        raise ValueError(f"Forbidden payload path: {name}/{relative}")
    if len(data) > 25_000_000:
        raise ValueError(f"Payload file exceeds 25 MB: {name}/{relative}")
    if relative.endswith(".json"):
        json.loads(data.decode("utf-8"))


def notice_bytes():
    result = {}
    for name in NOTICES:
        path = ROOT / name
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"Missing regular notice: {name}")
        result[name] = path.read_bytes()
    return result


def prepare_skill(name, source=None):
    folder = Path(source) if source is not None else ROOT / name
    if not folder.is_dir() or folder.is_symlink():
        raise ValueError(f"Missing skill folder: {name}")
    files = {}
    for relative in SKILLS[name]:
        path = folder / relative
        if relative in NOTICES and not path.exists():
            continue
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"Missing regular payload file: {name}/{relative}")
        if any(parent.is_symlink() for parent in path.parents if parent != ROOT):
            raise ValueError(f"Symlinked payload parent: {name}/{relative}")
        files[relative] = path.read_bytes()
    frontmatter_name = files["SKILL.md"].decode("utf-8").split("\n", 3)
    if len(frontmatter_name) < 3 or f"name: {name}" not in frontmatter_name[1]:
        raise ValueError(f"SKILL.md name does not match folder: {name}")
    for relative, data in files.items():
        validate_payload(name, relative, data)
    # Generated notice copies are never independently maintained variants.
    notices = notice_bytes()
    for notice, data in notices.items():
        files[notice] = data
    return files


def zip_bytes(items, top_level=None):
    """Return deterministic ZIP bytes. ``items`` maps archive path to bytes."""
    import io
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for archive_path in sorted(items):
            data = items[archive_path]
            info = zipfile.ZipInfo(archive_path, (2026, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data, compresslevel=9)
    return buffer.getvalue()


def build_skill_archive(name, files):
    if len(files) + 2 > 500:
        raise ValueError(f"Skill file count exceeds 500: {name}")
    items = {f"{name}/{relative}": data for relative, data in files.items()}
    archive = zip_bytes(items)
    if len(archive) > 50_000_000:
        raise ValueError(f"Skill ZIP exceeds 50 MB: {name}")
    return archive, items


def plugin_payload(skill_payloads=None):
    from validate import validate_plugin
    validate_plugin()
    if skill_payloads is None:
        skill_payloads = {name: prepare_skill(name) for name in SKILLS}
    items = {}
    for name, files in skill_payloads.items():
        for relative, data in files.items():
            items[f"skills/{name}/{relative}"] = data
    for notice in NOTICES:
        items[notice] = (ROOT / notice).read_bytes()
    items["plugin.json"] = (ROOT / "plugin.json").read_bytes()
    items["README.md"] = (ROOT / "docs/PLUGIN-README.md").read_bytes()
    for relative in PLUGIN_ASSETS:
        path = ROOT / relative
        check_destination(path)
        items[relative] = path.read_bytes()
    return items


def build_plugin_archive(skill_payloads):
    items = plugin_payload(skill_payloads)
    if len(items) > 500:
        raise ValueError("Plugin file count exceeds 500")
    archive = zip_bytes(items)
    if len(archive) > 100_000_000:
        raise ValueError("Plugin ZIP exceeds 100 MB")
    return archive, items


def write_file(path, data):
    check_destination(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def sync_derived():
    """Regenerate the bundled replacement ledger from the four reviewed ledgers."""
    ledgers = sorted((ROOT / "docs").glob("replacements-*.json"))
    if len(ledgers) != 4:
        raise ValueError("Expected all four reviewed example replacement ledgers")
    ledger = {
        "source_commits": ["bda594e15f4a6981e93403c4b187d262ca820116",
                           "17471d6d0a3fd1e53a1714d0c265dc3afad718cc"],
        "scope": "Technical facts and CadenceUX synthesis retained; expressive worked examples replaced. No FileMaker engine test is implied.",
        "ledgers": [{"file": path.name, "details": json.loads(path.read_text(encoding="utf-8"))}
                    for path in ledgers],
    }
    write_file(ROOT / "filemaker-pro/references/replacement-ledger.json",
               (json.dumps(ledger, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def build(verbose=True):
    # Validate all write paths before touching generated notices or artifacts.
    check_destination(DIST)
    for name in SKILLS:
        for notice in NOTICES:
            check_destination(ROOT / name / notice)
        check_destination(DIST / "skills" / f"{name}.zip")
    for relative in ("plugin.zip", "manifest.json", "SHA256SUMS"):
        check_destination(DIST / relative)
    check_destination(ROOT / "filemaker-pro/references/replacement-ledger.json")
    # Do not recursively delete dist: preserve unrelated local work.
    DIST.mkdir(exist_ok=True)
    notices = notice_bytes()
    for name in SKILLS:
        for notice, data in notices.items():
            write_file(ROOT / name / notice, data)
    sync_derived()
    payloads = {name: prepare_skill(name) for name in SKILLS}
    manifest = {
        "release": PLUGIN_VERSION,
        "plugin": {"name": PLUGIN_NAME, "format": "portable-agent-plugin"},
        "skills": {},
        "coverage": {
            "filemaker_functions": 368,
            "filemaker_script_steps": 216,
            "filemaker_error_codes": 292,
            "baseelements_catalog_entries": 133,
            "baseelements_unique_functions": 129,
            "mbs_functions": 7859,
            "mbs_components": 245,
            "bbox_functions": 87,
        },
        "limitations": [
            "No FileMaker engine execution is performed by this build.",
            "No live ChatGPT or Codex host acceptance is performed by this build.",
            "Vendor plug-in binaries, installers and licence keys are not bundled.",
        ],
    }
    for name, files in payloads.items():
        archive, items = build_skill_archive(name, files)
        relative = f"skills/{name}.zip"
        write_file(DIST / relative, archive)
        manifest["skills"][name] = {
            "path": relative,
            "format": "single-skill",
            "top_level_folder": name,
            "version": PLUGIN_VERSION,
            "sha256": sha256(archive),
            "bytes": len(archive),
            "file_count": len(items),
            "uncompressed_bytes": sum(len(data) for data in items.values()),
            "files": [{"path": path, "sha256": sha256(data), "bytes": len(data)}
                      for path, data in sorted(items.items())],
        }
    plugin_archive, plugin_items = build_plugin_archive(payloads)
    write_file(DIST / "plugin.zip", plugin_archive)
    manifest["plugin"].update({
        "path": "plugin.zip",
        "version": PLUGIN_VERSION,
        "skills": list(payloads),
        "sha256": sha256(plugin_archive),
        "bytes": len(plugin_archive),
        "file_count": len(plugin_items),
        "uncompressed_bytes": sum(len(data) for data in plugin_items.values()),
        "layout": ["plugin.json", "README.md", *NOTICES, *PLUGIN_ASSETS, "skills/<skill>/..."],
        "files": [{"path": path, "sha256": sha256(data), "bytes": len(data)}
                  for path, data in sorted(plugin_items.items())],
    })
    lines = [f"{sha256(plugin_archive)}  plugin.zip"]
    for name in sorted(payloads):
        info = manifest["skills"][name]
        lines.append(f"{info['sha256']}  {info['path']}")
    write_file(DIST / "SHA256SUMS", ("\n".join(lines) + "\n").encode("utf-8"))
    write_file(DIST / "manifest.json", (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    if verbose:
        print(json.dumps({
            "release": PLUGIN_VERSION,
            "plugin": {key: manifest["plugin"][key] for key in ("path", "sha256", "bytes", "file_count")},
            "skills": {name: {"bytes": value["bytes"], "file_count": value["file_count"]}
                       for name, value in manifest["skills"].items()},
        }, indent=2))
    return manifest


if __name__ == "__main__":
    build()
