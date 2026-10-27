#!/usr/bin/env python3
"""Dependency-free validation of the skill set, catalogs and plugin manifest.

This checks this project's restricted frontmatter profile and structural
invariants. It is not an official Agent Skills validator and does not run a
model, a FileMaker engine or a live host.
"""
import json
import re
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_NAMES = (
    "filemaker-pro", "goya-be-plugin", "monkeybread-mbs-plugin",
    "beezwax-bbox-plugin", "fmp-dev-orchestrator",
)


def frontmatter(path):
    """Parse our flat YAML plus a string-only metadata map; reject other syntax."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise ValueError("Missing YAML frontmatter delimiters")
    header, body = text[4:].split("\n---\n", 1)
    values = {}
    metadata = False
    for line in header.splitlines():
        if line == "metadata:":
            if "metadata" in values:
                raise ValueError("Duplicate metadata")
            values["metadata"] = {}
            metadata = True
            continue
        match = re.fullmatch(r"(  )?([a-z][a-z0-9-]*): (.+)", line)
        if not match:
            raise ValueError(f"Unsupported frontmatter syntax: {line}")
        indent, key, raw = match.groups()
        if indent and not metadata:
            raise ValueError("Unexpected nesting")
        if not indent:
            metadata = False
        target = values["metadata"] if indent else values
        if key in target:
            raise ValueError(f"Duplicate key: {key}")
        if raw.startswith('"'):
            value = json.loads(raw)
        elif re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", raw) and raw not in ("true", "false", "null"):
            value = raw
        else:
            raise ValueError(f"Use quoted strings: {key}")
        if not isinstance(value, str):
            raise ValueError("Metadata must be strings")
        target[key] = value
    allowed = {"name", "description", "license", "compatibility", "metadata"}
    if set(values) - allowed:
        raise ValueError("Unexpected metadata field")
    name = values.get("name", "")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64 or name != path.parent.name:
        raise ValueError("Invalid name or mismatched parent folder")
    if not 1 <= len(values.get("description", "")) <= 1024:
        raise ValueError("Invalid description length")
    if "compatibility" in values and not 1 <= len(values["compatibility"]) <= 500:
        raise ValueError("Invalid compatibility length")
    if not body.strip() or len(text.splitlines()) >= 500:
        raise ValueError("Empty body or excessive main-file length")
    return values


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate_catalogs():
    fm = ROOT / "filemaker-pro/references"
    functions = load_json(fm / "function-catalog.json")["functions"]
    steps = [step for category in load_json(fm / "script-steps-catalog.json")["categories"]
             for step in category["steps"]]
    errors = load_json(fm / "error-codes.json")["errors"]
    if (len(functions), len(steps), len(errors)) != (368, 216, 292):
        raise ValueError("Native FileMaker coverage changed")

    be = load_json(ROOT / "goya-be-plugin/references/function-catalog.json")
    be_entries = [entry for category in be["categories"].values() for entry in category["functions"]]
    if len(be_entries) != 133 or len({entry["name"] for entry in be_entries}) != 129:
        raise ValueError("BaseElements catalog counts changed")
    if len(be["deprecated"]) != 11:
        raise ValueError("BaseElements deprecated roster changed")

    bbox = load_json(ROOT / "beezwax-bbox-plugin/references/function-catalog.json")
    bbox_entries = [entry for category in bbox["categories"].values()
                    for entry in category["functions"].values()]
    if len(bbox_entries) != 87:
        raise ValueError("bBox catalog count changed")
    if bbox["meta"]["doc_status_counts"] != {"full": 39, "full_demo_confirmed": 48}:
        raise ValueError("bBox documentation status counts changed")

    index = load_json(ROOT / "monkeybread-mbs-plugin/references/index.json")
    if index["catalog_function_count"] != 7859 or len(index["components"]) != 245:
        raise ValueError("MBS catalog counts changed")
    total = 0
    for name, summary in index["components"].items():
        group = load_json(ROOT / "monkeybread-mbs-plugin" / summary["file"])
        block = group["components"][name]
        if block["function_count"] != len(block["functions"]):
            raise ValueError(f"MBS component count mismatch: {name}")
        total += len(block["functions"])
    if total != index["catalog_function_count"]:
        raise ValueError("MBS group total does not match the index")


def validate_plugin():
    manifest = load_json(ROOT / "plugin.json")
    if set(manifest) - {"$schema", "name", "version", "description", "author", "homepage",
                        "repository", "license", "keywords", "extensions"}:
        raise ValueError("Unknown portable plugin manifest fields")
    if manifest.get("$schema") != "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json":
        raise ValueError("Unexpected plugin schema")
    if manifest.get("name") != "filemaker-pro-agent-skills":
        raise ValueError("Unexpected plugin name")
    if manifest.get("version") != (ROOT / "VERSION").read_text(encoding="utf-8").strip():
        raise ValueError("Plugin version differs from VERSION")
    if not manifest.get("description") or not manifest.get("license"):
        raise ValueError("Plugin manifest is missing description or licence")
    extensions = manifest.get("extensions", {}).get("com.openai", {})
    interface = extensions.get("interface", {})
    for key in ("displayName", "shortDescription", "longDescription", "developerName", "category"):
        if not isinstance(interface.get(key), str) or not interface[key].strip():
            raise ValueError(f"Plugin interface is missing {key}")
    # Use final directory limits, not the more permissive draft-upload limits.
    for key, limit in (("displayName", 30), ("shortDescription", 30),
                       ("longDescription", 4000), ("developerName", 80)):
        if len(interface[key]) > limit:
            raise ValueError(f"Plugin interface {key} exceeds the public listing limit")
    if any(c in interface["shortDescription"] for c in "\r\n"):
        raise ValueError("Plugin short description must fit on one line")
    if not isinstance(interface.get("defaultPrompt"), list) or not interface["defaultPrompt"]:
        raise ValueError("Plugin needs default prompts")
    if len(interface["defaultPrompt"]) > 3 or any(not isinstance(p, str) or not 1 <= len(p) <= 128
                                               or "\n" in p or "\r" in p for p in interface["defaultPrompt"]):
        raise ValueError("Invalid starter prompts")
    if len(interface.get("capabilities", [])) > 20 or any(not isinstance(c, str) or not 1 <= len(c) <= 120
                                                       for c in interface.get("capabilities", [])):
        raise ValueError("Invalid capability labels")
    for field, relative, size in (("logo", "./assets/logo-512.png", 512),
                                  ("composerIcon", "./assets/icon-128.png", 128)):
        if interface.get(field) != relative:
            raise ValueError(f"Unexpected {field} path; use the reviewed project identity")
        path = ROOT / relative
        for candidate in (path, *path.parents):
            if candidate.is_symlink():
                raise ValueError(f"Symlinked visual resource: {path}")
        validate_png(path.read_bytes(), size)


def validate_png(data, size):
    """Check PNG structure, CRCs, exact RGBA dimensions and decoded scanline size.

    Pixel equality and full image decoding are additionally tested with Pillow.
    Limits follow OpenAI's branding rules; exact target dimensions are local policy.
    """
    if not data.startswith(b"\x89PNG\r\n\x1a\n") or len(data) > 5 * 1024 * 1024:
        raise ValueError("Invalid or oversized PNG")
    offset, chunks, compressed = 8, [], bytearray()
    while offset < len(data):
        if len(data) - offset < 12:
            raise ValueError("Truncated PNG chunk")
        length, = struct.unpack(">I", data[offset:offset + 4])
        kind = data[offset + 4:offset + 8]
        payload = data[offset + 8:offset + 8 + length]
        end = offset + length + 12
        if end > len(data):
            raise ValueError("Truncated PNG payload")
        crc, = struct.unpack(">I", data[end - 4:end])
        if zlib.crc32(kind + payload) & 0xffffffff != crc:
            raise ValueError("PNG CRC mismatch")
        if kind == b"IHDR":
            if chunks or length != 13:
                raise ValueError("Invalid PNG header")
            width, height, depth, color, compression, filtering, interlace = struct.unpack(">IIBBBBB", payload)
            if (width, height, depth, color, compression, filtering, interlace) != (size, size, 8, 6, 0, 0, 0):
                raise ValueError("Expected exact-size non-interlaced RGBA PNG")
        elif kind == b"IDAT":
            compressed.extend(payload)
        elif kind != b"IEND":
            raise ValueError("Unexpected PNG metadata/chunk")
        chunks.append(kind)
        offset = end
    if not chunks or chunks[0] != b"IHDR" or chunks[-1] != b"IEND" or chunks.count(b"IEND") != 1:
        raise ValueError("Invalid PNG chunk order")
    expected = size * (1 + 4 * size)
    decoder = zlib.decompressobj()
    pixels = decoder.decompress(compressed, expected + 1)
    if len(pixels) != expected or not decoder.eof or decoder.unused_data:
        raise ValueError("Invalid PNG image data")


def validate_links(folder):
    for path in folder.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for link in re.findall(r"\]\(([^)]+)\)", text):
            if re.match(r"[a-z]+:", link) or link.startswith("#"):
                continue
            destination = (path.parent / link.split("#")[0]).resolve()
            if not destination.is_relative_to(folder.resolve()):
                raise ValueError(f"Escaping link {path}: {link}")
            if not destination.exists():
                raise ValueError(f"Broken link {path}: {link}")


def main():
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    for name in SKILL_NAMES:
        path = ROOT / name / "SKILL.md"
        metadata = frontmatter(path)
        if set(metadata) != {"name", "description"}:
            raise ValueError(f"Use only name/description in {name} frontmatter")
        if f"Release {version}." not in path.read_text(encoding="utf-8"):
            raise ValueError(f"Skill body version differs from VERSION: {name}")
        validate_links(ROOT / name)
        for path in (ROOT / name / "references").glob("*.json"):
            load_json(path)
    validate_catalogs()
    validate_plugin()
    if not (ROOT / "plugin.json").is_file():
        raise ValueError("Missing plugin.json")
    for notice in ("LICENSE", "ATTRIBUTION.md", "THIRD-PARTY.md"):
        if not (ROOT / notice).is_file():
            raise ValueError(f"Missing {notice}")
    print("PASS: skill frontmatter, links, catalogs, plugin manifest and notices")


if __name__ == "__main__":
    main()
