"""Offline regressions for execution hosts, intent retrieval and coverage evidence.

These tests inspect local metadata and helpers, not FileMaker or plug-in runtimes.
"""
import hashlib
import importlib.util
import json
import socket
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("goya-be-plugin", "monkeybread-mbs-plugin", "beezwax-bbox-plugin")


def helper(skill):
    spec = importlib.util.spec_from_file_location(skill, ROOT / skill / "scripts/catalog.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class IntentLookupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.helpers = {skill: helper(skill) for skill in SKILLS}
        cls.data = {skill: (module.load_index() if skill == SKILLS[1] else module.load())
                    for skill, module in cls.helpers.items()}
        cls.entries = {}
        for skill, module in cls.helpers.items():
            if skill == SKILLS[1]:
                cls.entries[skill] = {e["name"]: e for p in (ROOT / skill / "references").glob("group-*.json")
                                      for b in json.loads(p.read_text(encoding="utf-8"))["components"].values()
                                      for e in b["functions"]}
            else:
                cls.entries[skill] = {e["name"]: e for _, e in module.entries(cls.data[skill])}

    def assert_intent(self, skill, query, expected):
        module, data = self.helpers[skill], self.data[skill]
        with patch.object(socket, "socket", side_effect=AssertionError("Lookup must stay offline")):
            matches = module.search(data, query, 3)
        self.assertTrue(matches, query)
        self.assertEqual(matches[0]["name"], expected)
        self.assertEqual(len({e["name"] for e in matches}), len(matches))
        for match in matches:
            self.assertEqual(match["signature"], self.entries[skill][match["name"]]["signature"])

    def test_all_intent_targets_exist(self):
        for skill, module in self.helpers.items():
            for _, targets in module.INTENTS:
                for name in targets:
                    with self.subTest(skill=skill, name=name):
                        self.assertIn(name, self.entries[skill])

    def test_exact_names_rank_first_and_normalize_whitespace(self):
        for skill, name in zip(SKILLS, ("BE_HTTP_POST", "Dialog.SetMessage", "bBox_Python3Run")):
            self.assert_intent(skill, "  " + name.swapcase() + "  ", name)

    def test_empty_unknown_and_stopword_queries_do_not_dump_catalogs(self):
        for skill, module in self.helpers.items():
            for query in ("", "   ", "with the", "unobtainium xyzzy"):
                with self.subTest(skill=skill, query=query):
                    self.assertEqual(module.search(self.data[skill], query, 8), [])

    def test_ranked_limits_are_stable_and_be_results_are_unique(self):
        for skill, module in self.helpers.items():
            first = module.search(self.data[skill], "file", 3)
            self.assertEqual(first, module.search(self.data[skill], "file", 50)[:3])
            self.assertEqual(len({e["name"] for e in first}), len(first))

    def test_mbs_search_reads_each_group_once(self):
        original = Path.read_text
        reads = []

        def read(path, *args, **kwargs):
            reads.append(path)
            return original(path, *args, **kwargs)

        with patch.object(Path, "read_text", read):
            self.helpers[SKILLS[1]].search(self.data[SKILLS[1]], "crear pdf", 3)
        self.assertEqual(len(reads), 20)
        self.assertEqual(len(set(reads)), 20)

    def test_representative_metadata_not_just_search_hits(self):
        be = self.entries[SKILLS[0]]["BE_SMTPSend"]
        self.assertEqual([p["name"] for p in be["parameters"]][:4], ["from", "to", "subject", "text"])
        self.assertTrue(be["compatibility"]["fms"])
        pdf = self.entries[SKILLS[1]]["DynaPDF.New"]
        self.assertEqual(pdf["status"], "licensed")
        self.assertTrue(pdf["compatibility"]["server"])
        self.assertIn("DynaPDF", self.data[SKILLS[1]]["addon_components"])
        python = self.entries[SKILLS[2]]["bBox_Python3Run"]
        self.assertEqual(python["doc_status"], "full")
        self.assertIn("mode", python["signature"])
        self.assertTrue(python["error_reference"])


# Separate tests keep the representative bilingual cases visible in CI output.
INTENT_CASES = (
    (0, "send email", "BE_SMTPSend"),
    (0, "enviar correo", "BE_SMTPSend"),
    (0, "write a text file", "BE_FileWriteText"),
    (0, "guardar archivo CSV", "BE_FileWriteText"),
    (0, "leer archivo", "BE_FileReadText"),
    (0, "listar carpeta", "BE_FileListFolder"),
    (0, "HTTP request", "BE_HTTP_GET"),
    (0, "expresión regular", "BE_RegularExpression"),
    (0, "execute javascript", "BE_EvaluateJavaScript"),
    (0, "transformar XML", "BE_XSLTApply"),
    (0, "combinar PDF", "BE_PDFAppend"),
    (1, "create PDF", "DynaPDF.New"),
    (1, "crear PDF", "DynaPDF.New"),
    (1, "extract text from PDF", "DynaPDF.ExtractText"),
    (1, "extraer texto PDF", "DynaPDF.ExtractText"),
    (1, "read Excel spreadsheet", "XL.LoadBook"),
    (1, "leer Excel", "XL.LoadBook"),
    (1, "guardar archivo", "Files.WriteFile"),
    (1, "petición HTTP", "CURL.New"),
    (1, "enviar correo", "SendMail.CreateEmail"),
    (1, "regex replace", "RegEx.ReplaceAll"),
    (1, "analizar JSON", "JSON.Parse"),
    (2, "run Python", "bBox_Python3Run"),
    (2, "ejecutar Python", "bBox_Python3Run"),
    (2, "ejecutar comando shell", "bBox_Zsh"),
    (2, "consultar DuckDB", "bBox_DuckDBOpen"),
    (2, "guardar archivo", "bBox_FileWrite"),
    (2, "leer archivo", "bBox_FileRead"),
    (2, "HTTP request", "bBox_HTTP_GET"),
    (2, "redimensionar imagen", "bBox_GraphicsMagick"),
    (2, "cargar visor web", "bBox_WebViewLoadHTML"),
    (2, "ejecutar javascript", "bBox_JavaScript"),
)


def intent_test(skill, query, expected):
    def test(self):
        self.assert_intent(skill, query, expected)
    return test


for number, (skill_index, query, expected) in enumerate(INTENT_CASES):
    setattr(IntentLookupTests, f"test_intent_{number:02}_{expected.replace('.', '_')}",
            intent_test(SKILLS[skill_index], query, expected))


class CompatibilityAndEvidenceTests(unittest.TestCase):
    def test_go_sdk_webdirect_and_psos_are_distinct(self):
        skill = (ROOT / SKILLS[0] / "SKILL.md").read_text(encoding="utf-8")
        self.assertNotIn("supports current FileMaker Pro, Go", skill)
        self.assertIn("does\n  not support external plug-ins", skill)
        for marker in ("iOS App SDK", "not FileMaker Go", "WPE", "FMSE", "PSoS", "server;", "`ios`", "`fms`"):
            self.assertIn(marker, skill)
        patterns = " ".join((ROOT / SKILLS[0] / "references/patterns.md").read_text(encoding="utf-8").split())
        for marker in ("not in the browser", "Do not interpret", "as Go support", "No server plug-in is available while Go is disconnected",
                       "go-pro-differences.html", "add-files-to-project.html", "plugins-manage.html"):
            self.assertIn(marker, patterns)

    def test_catalog_warns_about_inherited_platform_flags(self):
        data = helper(SKILLS[0]).load()
        interpretation = data["meta"]["compatibility_interpretation"]
        self.assertIn("not FileMaker Go support", interpretation["ios"])
        self.assertIn("does not certify WPE", interpretation["fms"])
        self.assertIn("not in the browser", interpretation["webdirect"])
        # Raw upstream flags remain intact, not silently rewritten as Go support.
        self.assertTrue(any(e["compatibility"].get("ios") for _, e in helper(SKILLS[0]).entries(data)))

    def test_mbs_review_binds_observed_set_to_catalog(self):
        folder = ROOT / SKILLS[1] / "references"
        report = json.loads((folder / "coverage-review.json").read_text(encoding="utf-8"))
        names = {e["name"] for p in folder.glob("group-*.json")
                 for b in json.loads(p.read_text(encoding="utf-8"))["components"].values() for e in b["functions"]}
        digest = hashlib.sha256(("\n".join(sorted(names)) + "\n").encode()).hexdigest()
        self.assertEqual(report["name_set_sha256"], digest)
        self.assertEqual(report["enumerated_unique_function_count"], len(names))
        self.assertEqual(report["component_table_unique_function_count"] + report["deprecated_table_unique_function_count"]
                         - report["component_and_deprecated_overlap"], len(names))
        self.assertEqual(report["advertised_function_count"], 7971)
        self.assertEqual(report["headline_minus_enumerated"], 112)
        self.assertEqual(report["missing_from_catalog"], [])
        self.assertEqual(report["catalog_names_absent_from_primary_tables"], [])
        self.assertEqual(len(report["pages"]), 170)
        self.assertEqual(len({r["path"] for r in report["pages"]}), 170)
        for page in report["pages"]:
            self.assertRegex(page["sha256"], r"^[a-f0-9]{64}$")
            self.assertGreater(page["primary_table_unique_names"], 0)
        self.assertIn("unresolved", report["conclusion"])

    def test_mbs_index_does_not_claim_unproved_residual_cause(self):
        index = helper(SKILLS[1]).load_index()
        self.assertNotIn("not linked from any listing page", index["count_note"])
        self.assertIn("unresolved", index["count_note"])
        entry = next(e for e in helper(SKILLS[1]).load_component(index, "Plugin")["functions"]
                     if e["name"] == "Plugin.LibXSLTVersion")
        self.assertEqual(entry["version_introduced"], "16.4")

    def test_logo_provenance_and_claris_warning_survive(self):
        for relative in ("assets/README.md", "ATTRIBUTION.md", "LICENSE", "SECURITY.md"):
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("ChatGPT", text)
            self.assertIn("exclusive", text)
        self.assertIn("Claris FileMaker documentation", (ROOT / "LICENSE").read_text(encoding="utf-8"))
        self.assertIn("Claris", (ROOT / "THIRD-PARTY.md").read_text(encoding="utf-8"))


class IntentCliAndPackageTests(unittest.TestCase):
    def test_cli_rejects_blank_search_and_invalid_limits(self):
        for skill in SKILLS:
            for args in (("search", " "), ("search", "file", "--limit", "0"), ("search", "file", "--limit", "51")):
                result = subprocess.run([sys.executable, str(ROOT / skill / "scripts/catalog.py"), *args],
                                        capture_output=True, text=True, timeout=30)
                self.assertEqual(result.returncode, 2, result.stdout)

    def test_distributed_helpers_resolve_intents_outside_repository(self):
        for skill, query, expected in zip(SKILLS, ("enviar correo", "crear PDF", "ejecutar Python"),
                                         ("BE_SMTPSend", "DynaPDF.New", "bBox_Python3Run")):
            with tempfile.TemporaryDirectory() as temporary:
                with zipfile.ZipFile(ROOT / "dist/skills" / (skill + ".zip")) as archive:
                    archive.extractall(temporary)
                result = subprocess.run([sys.executable, str(Path(temporary) / skill / "scripts/catalog.py"),
                                         "search", query, "--limit", "1"], cwd=temporary,
                                        capture_output=True, text=True, timeout=30)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout)["matches"][0]["name"], expected)


if __name__ == "__main__":
    unittest.main()
