#!/usr/bin/env python3
"""Install reviewed skills or the plugin into local Codex marketplace paths.

Skills are copied to the documented ``.agents/skills`` discovery directory. The
plugin is copied to a plugin folder and, optionally, registered in a personal or
repo marketplace. The installer never downloads, deletes or overwrites an
existing installation.
"""
import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

import build


def safe_base(base):
    base = Path(base).expanduser().absolute()
    for parent in (base, *base.parents):
        if parent.is_symlink():
            raise ValueError(f"Refusing symlink destination ancestor: {parent}")
    return base


def install(base, name="filemaker-pro", source=None):
    """Install one skill. The default preserves the original single-skill call."""
    source = Path(source) if source else build.ROOT / name
    if name not in build.SKILLS:
        raise ValueError(f"Unknown skill: {name}")
    base = safe_base(base)
    target = base / name
    if target.exists() or target.is_symlink():
        raise ValueError(f"Destination already exists; review/backup it before manual replacement: {target}")
    files = build.prepare_skill(name, source)
    base.mkdir(parents=True, exist_ok=True)
    lock = base.parent / f".{name}-install.lock"
    descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    os.close(descriptor)
    try:
        with tempfile.TemporaryDirectory(prefix=f".{name}-stage-", dir=base.parent) as temporary:
            staged = Path(temporary) / name
            for relative, data in files.items():
                destination = staged / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(data)
            if target.exists() or target.is_symlink():
                raise ValueError(f"Destination appeared during installation; refusing replacement: {target}")
            staged.rename(target)
    finally:
        lock.unlink()
    return target


def install_many(base, names):
    base = safe_base(base)
    names = list(names)
    for name in names:
        if name not in build.SKILLS:
            raise ValueError(f"Unknown skill: {name}")
        if (base / name).exists() or (base / name).is_symlink():
            raise ValueError(f"Destination already exists: {base / name}")
    return [install(base, name) for name in names]


def plugin_payload():
    """Return the plugin tree as archive-style relative paths."""
    return build.plugin_payload()


def install_plugin(base, name=build.PLUGIN_NAME):
    base = safe_base(base)
    target = base / name
    if target.exists() or target.is_symlink():
        raise ValueError(f"Plugin destination already exists; review/backup it before replacement: {target}")
    files = plugin_payload()
    base.mkdir(parents=True, exist_ok=True)
    lock = base.parent / f".{name}-plugin-install.lock"
    descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    os.close(descriptor)
    try:
        with tempfile.TemporaryDirectory(prefix=f".{name}-stage-", dir=base.parent) as temporary:
            staged = Path(temporary) / name
            for relative, data in files.items():
                destination = staged / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(data)
            if target.exists() or target.is_symlink():
                raise ValueError(f"Plugin destination appeared during installation: {target}")
            staged.rename(target)
    finally:
        lock.unlink()
    return target


def register_marketplace(marketplace, plugin_path, plugin_name=build.PLUGIN_NAME):
    from pathlib import PurePosixPath
    if (not plugin_path.startswith("./") or "\\" in plugin_path or
            ".." in PurePosixPath(plugin_path).parts):
        raise ValueError("Marketplace plugin path must stay inside its root and start with ./")
    marketplace = Path(marketplace).expanduser().absolute()
    for parent in (marketplace, *marketplace.parents):
        if parent.is_symlink():
            raise ValueError(f"Refusing symlink marketplace ancestor: {parent}")
    marketplace.parent.mkdir(parents=True, exist_ok=True)
    if marketplace.exists():
        data = json.loads(marketplace.read_text(encoding="utf-8"))
    else:
        data = {"name": "filemaker-pro-agent-skills", "interface": {"displayName": "FileMaker Pro Agent Skills"}, "plugins": []}
    plugins = data.setdefault("plugins", [])
    if any(entry.get("name") == plugin_name for entry in plugins):
        raise ValueError(f"Marketplace already lists {plugin_name}")
    plugins.append({
        "name": plugin_name,
        "source": {"source": "local", "path": plugin_path},
        "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
        "category": "Developer Tools",
        "interface": {"displayName": "FileMaker Pro Agent Skills"},
    })
    # Unique temporary file, not a predictable writable/symlink target.
    descriptor, temporary_name = tempfile.mkstemp(prefix=".marketplace-", suffix=".json", dir=marketplace.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write((json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
        temporary.replace(marketplace)
    finally:
        temporary.unlink(missing_ok=True)
    return marketplace


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", choices=("user", "project"), required=True)
    parser.add_argument("--project", type=Path, help="Existing target project directory; required for project scope")
    parser.add_argument("--skill", action="append", choices=build.SKILLS, help="Install one skill; repeatable")
    parser.add_argument("--all", action="store_true", help="Install every individual skill")
    parser.add_argument("--plugin", action="store_true", help="Install the multi-skill plugin instead of individual skills")
    parser.add_argument("--register-marketplace", action="store_true", help="Register the installed plugin in a local marketplace")
    args = parser.parse_args()
    if args.register_marketplace and not args.plugin:
        parser.error("--register-marketplace requires --plugin")
    if args.scope == "project":
        if args.project is None or not args.project.is_dir():
            parser.error("--scope project requires an existing --project directory")
        project = args.project.resolve()
    else:
        if args.project:
            parser.error("--project is only valid for project scope")
        project = None
    try:
        if args.plugin:
            if args.skill or args.all:
                parser.error("--plugin cannot be combined with --skill/--all")
            if project:
                plugin_base = project / "plugins"
                marketplace = project / ".agents/plugins/marketplace.json"
                relative = f"./plugins/{build.PLUGIN_NAME}"
            else:
                plugin_base = Path.home() / ".codex/plugins"
                marketplace = Path.home() / ".agents/plugins/marketplace.json"
                relative = f"./.codex/plugins/{build.PLUGIN_NAME}"
            target = install_plugin(plugin_base)
            print(target)
            if args.register_marketplace:
                print(register_marketplace(marketplace, relative))
            else:
                print(f"Marketplace entry path: {relative}")
            return 0
        base = (project / ".agents/skills") if project else (Path.home() / ".agents/skills")
        names = list(build.SKILLS) if args.all else (args.skill or ["filemaker-pro"])
        for target in install_many(base, names):
            print(target)
    except (ValueError, OSError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
