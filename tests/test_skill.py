import ast
import hashlib
import importlib.util
import json
import re
import socket
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("filemaker-pro", "goya-be-plugin", "monkeybread-mbs-plugin",
          "beezwax-bbox-plugin", "fmp-dev-orchestrator")


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


sys.path.insert(0, str(ROOT / "scripts"))
import build
import install_codex
import validate
catalog = module("catalog", ROOT / "filemaker-pro/scripts/catalog.py")
route = module("route", ROOT / "fmp-dev-orchestrator/scripts/route.py")


class StructureTests(unittest.TestCase):
    def test_python_310_grammar(self):
        paths = list((ROOT / "scripts").glob("*.py")) + list((ROOT / "tests").glob("*.py"))
        for name in SKILLS:
            paths += list((ROOT / name / "scripts").glob("*.py"))
        for path in paths:
            with self.subTest(path=str(path.relative_to(ROOT))):
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path), feature_version=(3, 10))

    def test_frontmatter_profile(self):
        for name in SKILLS:
            with self.subTest(name=name):
                meta = validate.frontmatter(ROOT / name / "SKILL.md")
                self.assertEqual(meta["name"], name)
                self.assertEqual(set(meta), {"name", "description"})
                self.assertNotIn("allowed-tools", meta)

    def test_invalid_frontmatter_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "SKILL.md"
            path.write_text('---\nname: Bad_Name\ndescription: "test"\n---\nBody')
            with self.assertRaises(ValueError):
                validate.frontmatter(path)

    def test_version_body(self):
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        for name in SKILLS:
            self.assertIn(f"Release {version}.", (ROOT / name / "SKILL.md").read_text(encoding="utf-8"))

    def test_openai_metadata(self):
        for name in SKILLS:
            with self.subTest(name=name):
                text = (ROOT / name / "agents/openai.yaml").read_text(encoding="utf-8")
                self.assertIn("display_name:", text)
                self.assertIn(f"${name}", text)
                self.assertNotIn("allow_implicit_invocation: false", text)
                self.assertNotIn("dependencies:", text)
                for line in text.splitlines():
                    if not line.strip():
                        continue
                    key, value = line.strip().split(":", 1)
                    self.assertRegex(key, r"^[a-z_]+$")
                    if value.strip():
                        self.assertIsInstance(json.loads(value.strip()), str)

    def test_all_json(self):
        for name in SKILLS:
            for path in (ROOT / name / "references").glob("*.json"):
                with self.subTest(path=str(path.relative_to(ROOT))):
                    self.assertIsInstance(json.loads(path.read_text(encoding="utf-8")), dict)

    def test_plugin_manifest(self):
        manifest = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["$schema"], "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json")
        self.assertEqual(manifest["name"], "filemaker-pro-agent-skills")
        self.assertEqual(manifest["version"], (ROOT / "VERSION").read_text(encoding="utf-8").strip())
        self.assertEqual(manifest["license"], "CC-BY-4.0")
        interface = manifest["extensions"]["com.openai"]["interface"]
        self.assertTrue(interface["displayName"])
        self.assertTrue(interface["defaultPrompt"])

    def test_notice_copies(self):
        for notice in ("LICENSE", "ATTRIBUTION.md", "THIRD-PARTY.md"):
            expected = (ROOT / notice).read_bytes()
            for name in SKILLS:
                with self.subTest(name=name, notice=notice):
                    self.assertEqual((ROOT / name / notice).read_bytes(), expected)

    def test_readme_parity_and_sections(self):
        english = (ROOT / "README.md").read_text(encoding="utf-8")
        spanish = (ROOT / "README.es.md").read_text(encoding="utf-8")
        for heading in ("ChatGPT", "Codex", "Architecture", "Attribution", "Licenses"):
            self.assertIn(heading, english)
        for heading in ("ChatGPT", "Codex", "Arquitectura", "Atribución", "Licencias"):
            self.assertIn(heading, spanish)
        for text in (english, spanish):
            for forbidden in ("owner authorization", "authorization pending", "this session", "audit report", "autorización pendiente"):
                self.assertNotIn(forbidden, text.lower())

    def test_no_symlinks(self):
        for name in SKILLS:
            for path in (ROOT / name).rglob("*"):
                self.assertFalse(path.is_symlink(), str(path))

    def test_attribution_covers_all_sources(self):
        text = (ROOT / "ATTRIBUTION.md").read_text(encoding="utf-8")
        for repo in ("claris-filemaker-pro-skill", "fmp-dev-design-patterns",
                     "goya-be-plugin-skill", "monkeybread-mbs-plugin-skill",
                     "beezwax-bbox-plugin-skill", "fmp-dev-orchestrator-skill"):
            self.assertIn(repo, text)
        third_party = (ROOT / "THIRD-PARTY.md").read_text(encoding="utf-8")
        for vendor in ("Goya", "Monkeybread", "Beezwax", "Claris"):
            self.assertIn(vendor, third_party)

    def test_no_duplicate_references(self):
        seen = {}
        for name in SKILLS:
            for path in (ROOT / name / "references").rglob("*"):
                if path.is_file():
                    digest = hashlib.sha256(path.read_bytes()).hexdigest()
                    self.assertNotIn(digest, seen, f"Duplicate reference: {path} and {seen.get(digest)}")
                    seen[digest] = str(path)

    def test_descriptions_have_boundaries(self):
        for name in SKILLS:
            text = (ROOT / name / "SKILL.md").read_text(encoding="utf-8")
            description = text.split("description: ", 1)[1].split("\n", 1)[0]
            self.assertIn("Do not use", description)
            self.assertGreater(len(description), 80)
        triggers = {
            "filemaker-pro": "FileMaker",
            "goya-be-plugin": "BE_",
            "monkeybread-mbs-plugin": "MBS",
            "beezwax-bbox-plugin": "bBox_",
            "fmp-dev-orchestrator": "Route",
        }
        for name, trigger in triggers.items():
            text = (ROOT / name / "SKILL.md").read_text(encoding="utf-8")
            description = text.split("description: ", 1)[1].split("\n", 1)[0]
            self.assertIn(trigger, description)

    def test_links_all_skills(self):
        for name in SKILLS:
            folder = (ROOT / name).resolve()
            for path in folder.rglob("*.md"):
                for link in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
                    if re.match(r"[a-z]+:", link) or link.startswith("#"):
                        continue
                    destination = (path.parent / link.split("#")[0]).resolve()
                    self.assertTrue(destination.is_relative_to(folder), f"Escaping link {path}: {link}")
                    self.assertTrue(destination.exists(), f"Broken link {path}: {link}")


class NativeCatalogTests(unittest.TestCase):
    def test_function_count_unique(self):
        data = catalog.load("function-catalog.json")
        self.assertEqual(len(data["functions"]), 368)
        self.assertEqual(len({x["name"] for x in data["functions"]}), 368)
        self.assertEqual(data["meta"]["function_count"], 368)

    def test_step_count_unique(self):
        data = catalog.load("script-steps-catalog.json")
        self.assertEqual(len(data["categories"]), 16)
        self.assertEqual(len(catalog.entries("step")), 216)
        self.assertEqual(len({x["name"] for x in catalog.entries("step")}), 216)

    def test_function_schema(self):
        for entry in catalog.entries("function"):
            with self.subTest(name=entry["name"]):
                for key in ("name", "format", "return_type", "originated_in_version", "slug", "doc_url"):
                    self.assertIsInstance(entry[key], str)
                    self.assertTrue(entry[key])
                self.assertRegex(entry["doc_url"], r"^https://help\.claris\.com/")

    def test_step_schema(self):
        for entry in catalog.entries("step"):
            for key in ("name", "syntax", "originated_in_version", "slug", "doc_url"):
                self.assertTrue(entry[key])
            for platform, value in entry.get("platform_exceptions", {}).items():
                self.assertIn(platform, catalog.PLATFORMS)
                self.assertIn(value, ("Partial", "No"))

    def test_function_signature(self):
        entry = catalog.find("function", "JSONSetElement")
        self.assertEqual(entry["format"], "JSONSetElement ( json ; keyOrIndexOrPath ; value ; type )")
        self.assertEqual(entry["return_type"], "text")

    def test_errors_full_roster(self):
        entries = catalog.entries("error")
        self.assertEqual(len(entries), 292)
        self.assertEqual(len({x["code"] for x in entries}), 292)

    def test_version_and_platform_checks(self):
        self.assertEqual(catalog.lookup("step", "Open Transaction", "19.6")["version_check"]["status"], "unavailable")
        self.assertEqual(catalog.lookup("step", "Open Transaction", "19.6.1")["version_check"]["status"], "minimum-met")
        self.assertEqual(catalog.lookup("step", "Go to Layout", platform="WebDirect")["platform_check"]["snapshot_support"], "Partial")
        with self.assertRaises(ValueError):
            catalog.lookup("step", "Open Transaction", platform="OData")

    def test_offline_lookup(self):
        with patch.object(socket, "socket", side_effect=AssertionError("Network forbidden")):
            self.assertEqual(catalog.lookup("function", "Abs")["status"], "found")
            self.assertEqual(catalog.lookup("error", "401")["status"], "found")


class PluginCatalogTests(unittest.TestCase):
    @staticmethod
    def be():
        return json.loads((ROOT / "goya-be-plugin/references/function-catalog.json").read_text(encoding="utf-8"))

    @staticmethod
    def bbox():
        return json.loads((ROOT / "beezwax-bbox-plugin/references/function-catalog.json").read_text(encoding="utf-8"))

    @staticmethod
    def mbs_index():
        return json.loads((ROOT / "monkeybread-mbs-plugin/references/index.json").read_text(encoding="utf-8"))

    def test_baseelements_counts(self):
        data = self.be()
        entries = [entry for category in data["categories"].values() for entry in category["functions"]]
        self.assertEqual(len(entries), 133)
        self.assertEqual(len({entry["name"] for entry in entries}), 129)
        self.assertEqual(len(data["deprecated"]), 11)
        self.assertEqual(len(data["constants"]["groups"]), 4)
        self.assertEqual(sum(len(x["constants"]) for x in data["constants"]["groups"]), 10)

    def test_bbox_counts(self):
        data = self.bbox()
        entries = [entry for category in data["categories"].values() for entry in category["functions"].values()]
        self.assertEqual(len(entries), 87)
        self.assertEqual(data["meta"]["doc_status_counts"], {"full": 39, "full_demo_confirmed": 48})
        for key in ("mode_flags", "error_reference", "container_field_references", "native_fm_bridge",
                    "thread_and_session_safety", "psos_and_calculation_field_limits"):
            self.assertIn(key, data["shared_reference"])

    def test_mbs_counts_and_groups(self):
        index = self.mbs_index()
        self.assertEqual(index["catalog_function_count"], 7859)
        self.assertEqual(len(index["components"]), 245)
        total = 0
        for component, summary in index["components"].items():
            group = json.loads((ROOT / "monkeybread-mbs-plugin" / summary["file"]).read_text(encoding="utf-8"))
            block = group["components"][component]
            self.assertEqual(block["function_count"], len(block["functions"]))
            total += len(block["functions"])
        self.assertEqual(total, 7859)

    def test_factual_catalog_policy(self):
        for entry in [x for c in self.be()["categories"].values() for x in c["functions"]]:
            self.assertNotIn("description", entry)
            self.assertNotIn("example_code", entry)
            for parameter in entry["parameters"]:
                self.assertNotIn("description", parameter)
        for entry in [x for c in self.bbox()["categories"].values() for x in c["functions"].values()]:
            self.assertNotIn("description", entry)
            self.assertNotIn("example_code", entry)
            self.assertNotIn("notes", entry)
            for parameter in entry["parameters"]:
                self.assertNotIn("description", parameter)
        index = self.mbs_index()
        group = json.loads((ROOT / "monkeybread-mbs-plugin" / index["components"]["Dialog"]["file"]).read_text(encoding="utf-8"))
        for entry in group["components"]["Dialog"]["functions"]:
            self.assertNotIn("description", entry)
            self.assertNotIn("examples", entry)
            for parameter in entry["parameters"]:
                self.assertNotIn("description", parameter)
                self.assertNotIn("example", parameter)

    def test_urls_are_https(self):
        for data in (self.be(), self.bbox()):
            for category in data["categories"].values():
                entries = category["functions"].values() if isinstance(category["functions"], dict) else category["functions"]
                for entry in entries:
                    self.assertRegex(entry["url"], r"^https://")
        index = self.mbs_index()
        for summary in index["components"].values():
            group = json.loads((ROOT / "monkeybread-mbs-plugin" / summary["file"]).read_text(encoding="utf-8"))
            for block in group["components"].values():
                for entry in block["functions"]:
                    self.assertRegex(entry["url"], r"^https://")

    def test_baseelements_queries(self):
        data = self.be()
        entries = {entry["name"]: entry for category in data["categories"].values() for entry in category["functions"]}
        post = entries["BE_HTTP_POST"]
        self.assertIn("BE_HTTP_POST", post["signature"])
        self.assertTrue(any(x["name"] == "url" for x in post["parameters"]))
        self.assertIn("BE_MessageDigest", entries)
        self.assertEqual(next(x for x in data["deprecated"] if x["name"] == "BE_HMAC")["replaced_by"], "CryptAuthCode (native FM 19.3+)")

    def test_bbox_queries(self):
        data = self.bbox()
        entries = {entry["name"]: entry for category in data["categories"].values() for entry in category["functions"].values()}
        shell = entries["bBox_Shell"]
        self.assertEqual(shell["signature"], "bBox_Shell ( mode ; script )")
        self.assertEqual(shell["error_reference"], "bBox_LastError (\"posix\")")
        self.assertIn("bBox_JavaScript", entries)
        self.assertEqual(entries["bBox_Shell"]["doc_status"], "full")

    def test_mbs_queries(self):
        index = self.mbs_index()
        group = json.loads((ROOT / "monkeybread-mbs-plugin" / index["components"]["Dialog"]["file"]).read_text(encoding="utf-8"))
        entries = {entry["name"]: entry for entry in group["components"]["Dialog"]["functions"]}
        self.assertEqual(entries["Dialog.SetMessage"]["signature"], "MBS( \"Dialog.SetMessage\"; Text )")
        self.assertIn("licensed", {entry["status"] for entry in group["components"]["Dialog"]["functions"]})
        self.assertIn("DynaPDF", index["addon_components"])
        self.assertIn("Saxon", index["addon_components"])

    def test_provenance_pins(self):
        expected = {
            "goya-be-plugin": "29579288cba843286b5c15275cd5d23e7bb37f40",
            "beezwax-bbox-plugin": "0c4179ddfd5428f514f85f75f2a68d1001ec4483",
            "monkeybread-mbs-plugin": "946bdca12c2117defb4dc2b8959ee00f04c74086",
            "fmp-dev-orchestrator": "1fe0b8f8682a0bf569a8c4df3ab9aaeab94f405e",
        }
        for name, commit in expected.items():
            data = json.loads((ROOT / name / "references/provenance.json").read_text(encoding="utf-8"))
            self.assertEqual(data["commit"], commit)
            self.assertTrue(data["source_files"])


class CliTests(unittest.TestCase):
    def run_cli(self, skill, *args):
        return subprocess.run([sys.executable, str(ROOT / skill / "scripts" / ("route.py" if skill == "fmp-dev-orchestrator" else "catalog.py")), *args],
                              capture_output=True, text=True, timeout=30)

    def test_baseelements_cli(self):
        result = self.run_cli("goya-be-plugin", "function", "BE_HTTP_POST")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["entry"]["name"], "BE_HTTP_POST")
        self.assertEqual(self.run_cli("goya-be-plugin", "function", "BE_Nope").returncode, 1)
        self.assertEqual(self.run_cli("goya-be-plugin", "constants").returncode, 0)

    def test_bbox_cli(self):
        result = self.run_cli("beezwax-bbox-plugin", "function", "bBox_Shell")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["entry"]["name"], "bBox_Shell")
        self.assertEqual(self.run_cli("beezwax-bbox-plugin", "shared", "mode_flags").returncode, 0)
        self.assertEqual(self.run_cli("beezwax-bbox-plugin", "function", "bBox_Nope").returncode, 1)

    def test_mbs_cli(self):
        result = self.run_cli("monkeybread-mbs-plugin", "function", "Dialog.SetMessage")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["entry"]["name"], "Dialog.SetMessage")
        self.assertEqual(self.run_cli("monkeybread-mbs-plugin", "component", "Dialog").returncode, 0)
        self.assertEqual(self.run_cli("monkeybread-mbs-plugin", "function", "Dialog.Nope").returncode, 1)

    def test_search_limits(self):
        result = self.run_cli("monkeybread-mbs-plugin", "search", "PDF", "--limit", "3")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertLessEqual(len(json.loads(result.stdout)["matches"]), 3)

    def test_route_cli(self):
        result = self.run_cli("fmp-dev-orchestrator", "route", "What does BE_HTTP_POST return?")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["skills"], ["goya-be-plugin"])
        self.assertEqual(self.run_cli("fmp-dev-orchestrator", "route", "Optimize PostgreSQL").returncode, 1)


class RoutingTests(unittest.TestCase):
    def test_routing_cases(self):
        cases = json.loads((ROOT / "tests/routing-cases.json").read_text(encoding="utf-8"))["cases"]
        for case in cases:
            with self.subTest(prompt=case["prompt"]):
                self.assertEqual(route.route(case["prompt"])["skills"], case["expected"])

    def test_orchestrator_contract(self):
        text = (ROOT / "fmp-dev-orchestrator/SKILL.md").read_text(encoding="utf-8")
        for marker in ("goya-be-plugin", "monkeybread-mbs-plugin", "beezwax-bbox-plugin", "filemaker-pro", "answer catalog questions directly"):
            self.assertIn(marker, text)

    def test_native_boundary(self):
        text = (ROOT / "filemaker-pro/SKILL.md").read_text(encoding="utf-8")
        for marker in ("BE_", "MBS(", "bBox_", "fmp-dev-orchestrator"):
            self.assertIn(marker, text)


class DistributionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = build.build(verbose=False)

    def test_deterministic_build(self):
        first = {name: (ROOT / "dist" / info["path"]).read_bytes() for name, info in self.manifest["skills"].items()}
        first["plugin"] = (ROOT / "dist/plugin.zip").read_bytes()
        second_manifest = build.build(verbose=False)
        second = {name: (ROOT / "dist" / info["path"]).read_bytes() for name, info in second_manifest["skills"].items()}
        second["plugin"] = (ROOT / "dist/plugin.zip").read_bytes()
        self.assertEqual(first, second)
        self.assertEqual(self.manifest, second_manifest)

    def test_skill_zips_are_single_skill(self):
        for name, info in self.manifest["skills"].items():
            with self.subTest(name=name):
                path = ROOT / "dist" / info["path"]
                with zipfile.ZipFile(path) as archive:
                    self.assertIsNone(archive.testzip())
                    names = archive.namelist()
                    self.assertEqual({x.split("/", 1)[0] for x in names}, {name})
                    self.assertEqual(sum(x.lower().endswith("/skill.md") for x in names), 1)
                    self.assertNotIn("plugin.json", names)
                    self.assertLessEqual(len(names), 500)
                    self.assertLessEqual(path.stat().st_size, 50_000_000)
                    for entry in archive.infolist():
                        self.assertLessEqual(entry.file_size, 25_000_000)
                        self.assertNotIn("..", Path(entry.filename).parts)
                        self.assertEqual(entry.external_attr >> 16, 0o100644)

    def test_plugin_zip_is_multi_skill(self):
        with zipfile.ZipFile(ROOT / "dist/plugin.zip") as archive:
            names = archive.namelist()
            self.assertIn("plugin.json", names)
            self.assertIn("README.md", names)
            self.assertNotIn("SKILL.md", names)
            self.assertEqual({x.split("/")[1] for x in names if x.startswith("skills/")}, set(SKILLS))
            self.assertEqual(sum(x.endswith("/SKILL.md") for x in names), len(SKILLS))
            self.assertIsNone(archive.testzip())
            self.assertLessEqual(len(names), 500)
            manifest = json.loads(archive.read("plugin.json"))
            self.assertEqual(manifest["name"], "filemaker-pro-agent-skills")

    def test_manifest_hashes(self):
        manifest = json.loads((ROOT / "dist/manifest.json").read_text(encoding="utf-8"))
        for info in [manifest["plugin"]] + list(manifest["skills"].values()):
            path = ROOT / "dist" / info["path"]
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), info["sha256"])
            self.assertIn(info["sha256"], (ROOT / "dist/SHA256SUMS").read_text(encoding="utf-8"))

    def test_extracted_skill_works_without_repo(self):
        for name in SKILLS:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temporary:
                with zipfile.ZipFile(ROOT / "dist" / self.manifest["skills"][name]["path"]) as archive:
                    archive.extractall(temporary)
                root = Path(temporary) / name
                validate.frontmatter(root / "SKILL.md")
                self.assertTrue((root / "LICENSE").is_file())
                self.assertTrue((root / "THIRD-PARTY.md").is_file())
                if name == "fmp-dev-orchestrator":
                    result = subprocess.run([sys.executable, str(root / "scripts/route.py"), "route", "BE_HTTP_POST"],
                                            cwd=temporary, capture_output=True, text=True, timeout=30)
                else:
                    command = "error" if name == "filemaker-pro" else "stats"
                    args = ["401"] if name == "filemaker-pro" else []
                    result = subprocess.run([sys.executable, str(root / "scripts/catalog.py"), command, *args],
                                            cwd=temporary, capture_output=True, text=True, timeout=30)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_plugin_package_works_without_repo(self):
        with tempfile.TemporaryDirectory() as temporary:
            with zipfile.ZipFile(ROOT / "dist/plugin.zip") as archive:
                archive.extractall(temporary)
            root = Path(temporary)
            self.assertTrue((root / "plugin.json").is_file())
            for name in SKILLS:
                validate.frontmatter(root / "skills" / name / "SKILL.md")
            result = subprocess.run(
                [sys.executable, str(root / "skills/goya-be-plugin/scripts/catalog.py"), "function", "BE_HTTP_POST"],
                cwd=temporary, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            result = subprocess.run(
                [sys.executable, str(root / "skills/fmp-dev-orchestrator/scripts/route.py"), "route", "MBS Dialog"],
                cwd=temporary, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_install_each_skill(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).resolve() / ".agents/skills"
            for target in install_codex.install_many(base, SKILLS):
                self.assertTrue((target / "SKILL.md").is_file())
                self.assertTrue((target / "LICENSE").is_file())
            with self.assertRaises(ValueError):
                install_codex.install(base, "goya-be-plugin")

    def test_install_plugin_and_marketplace(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).resolve() / "plugins"
            target = install_codex.install_plugin(base)
            self.assertTrue((target / "plugin.json").is_file())
            self.assertEqual(len([x for x in (target / "skills").iterdir() if x.is_dir()]), len(SKILLS))
            marketplace = Path(temporary).resolve() / ".agents/plugins/marketplace.json"
            install_codex.register_marketplace(marketplace, "./plugins/filemaker-pro-agent-skills")
            data = json.loads(marketplace.read_text(encoding="utf-8"))
            self.assertEqual(data["plugins"][0]["name"], "filemaker-pro-agent-skills")

    def test_install_refuses_symlink(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            (base / "actual").mkdir()
            try:
                (base / "link").symlink_to(base / "actual", target_is_directory=True)
            except OSError:
                self.skipTest("Symlinks unavailable on this host")
            with self.assertRaises(ValueError):
                install_codex.install(base / "link")

    def test_failed_install_leaves_no_discoverable_skill(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).resolve() / ".agents/skills"
            with patch.object(build, "prepare_skill", side_effect=OSError("Injected copy failure")):
                with self.assertRaises(OSError):
                    install_codex.install(base)
            self.assertFalse((base / "filemaker-pro").exists())
            self.assertFalse((base.parent / ".filemaker-pro-install.lock").exists())
            self.assertFalse(list(base.parent.glob(".filemaker-pro-stage-*")))

    def test_competing_lock(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).resolve() / ".agents/skills"
            base.parent.mkdir(parents=True)
            lock = base.parent / ".filemaker-pro-install.lock"
            lock.write_text("other installer owns this lock")
            with self.assertRaises(FileExistsError):
                install_codex.install(base)
            self.assertTrue(lock.exists())


class SecurityTests(unittest.TestCase):
    def test_untrusted_lookup_text_is_not_executed(self):
        with tempfile.TemporaryDirectory() as temporary:
            marker = Path(temporary) / "must-not-exist"
            query = f"__import__('pathlib').Path({str(marker)!r}).write_text('injected')"
            result = subprocess.run([sys.executable, str(ROOT / "goya-be-plugin/scripts/catalog.py"), "function", query],
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 1)
            self.assertFalse(marker.exists())

    def test_no_network_imports(self):
        forbidden = {"requests", "urllib", "http", "socket", "httpx", "aiohttp"}
        for folder in [ROOT / "scripts"] + [ROOT / name / "scripts" for name in SKILLS]:
            for path in folder.glob("*.py"):
                tree = ast.parse(path.read_text(encoding="utf-8"))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        self.assertFalse(forbidden.intersection(x.name.split(".")[0] for x in node.names), path)
                    if isinstance(node, ast.ImportFrom):
                        self.assertNotIn((node.module or "").split(".")[0], forbidden, path)

    def test_skill_safety_contract(self):
        markers = ("untrusted", "authoriz", "Never invent", "no network")
        for name in SKILLS:
            text = (ROOT / name / "SKILL.md").read_text(encoding="utf-8")
            for marker in markers:
                with self.subTest(name=name, marker=marker):
                    self.assertIn(marker.lower(), text.lower())

    def test_no_binaries_in_packages(self):
        suffix = {".fmplugin", ".dylib", ".dll", ".so", ".exe", ".pkg", ".dmg", ".fmp12"}
        for path in (ROOT / "dist").rglob("*.zip"):
            with zipfile.ZipFile(path) as archive:
                for name in archive.namelist():
                    self.assertNotIn(Path(name).suffix.lower(), suffix, name)


if __name__ == "__main__":
    unittest.main()
