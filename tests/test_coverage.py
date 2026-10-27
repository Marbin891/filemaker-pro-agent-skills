"""Lossless technical metadata checks and explicitly non-engine calculation checks."""
import datetime
import hashlib
import json
import math
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFS = ROOT / "filemaker-pro/references"
sys.path.insert(0, str(ROOT / "scripts"))
import lint_examples


def strip_literals_and_comments(formula):
    # FileMaker escapes literal quotes with backslashes. This is a lexical check only.
    return re.sub(r'"(?:\\.|[^"\\])*"|//[^\n]*', lambda m: " " * len(m[0]), formula)


class CoverageTests(unittest.TestCase):
    def test_complete_catalogs_semantic_hashes(self):
        baseline = json.loads((ROOT / "tests/reference-baseline.json").read_text(encoding="utf-8"))
        for filename, expected in baseline["catalog_semantic_sha256"].items():
            with self.subTest(filename=filename):
                actual = json.loads((REFS / filename).read_text(encoding="utf-8"))
                adaptation = actual.pop("adaptation")
                digest = hashlib.sha256(json.dumps(actual, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
                self.assertEqual(digest, expected, "An upstream field, note, entry or metadata value was lost/changed")
                self.assertEqual(digest, adaptation["original_semantic_sha256"])

    def test_purposes_notes_and_variants_retained(self):
        functions = json.loads((REFS / "function-catalog.json").read_text(encoding="utf-8"))["functions"]
        steps = [s for c in json.loads((REFS / "script-steps-catalog.json").read_text(encoding="utf-8"))["categories"] for s in c["steps"]]
        self.assertEqual(sum("purpose" in x for x in functions), 368)
        self.assertEqual(sum("purpose" in x for x in steps), 216)
        self.assertEqual(sum("notes" in x for x in steps), 63)
        self.assertEqual(sum("notes" in x for x in functions), 4)
        self.assertEqual(sum("format_vision" in x for x in functions), 1)
        self.assertEqual(sum("os_restriction" in x for x in steps), 3)

    def test_full_field_capability_sections(self):
        data = json.loads((REFS / "field-types-catalog.json").read_text(encoding="utf-8"))
        for key in ("data_types", "field_types", "summary_types", "indexing", "storage", "advanced_options"):
            self.assertTrue(data[key])

    def test_original_calculation_catalog_and_lexical_checks(self):
        functions = json.loads((REFS / "function-catalog.json").read_text(encoding="utf-8"))["functions"]
        known = {x["name"].casefold() for x in functions}
        cases = json.loads((ROOT / "tests/calculation-cases.json").read_text(encoding="utf-8"))["cases"]
        for case in cases:
            with self.subTest(case=case["id"]):
                text = strip_literals_and_comments(case["formula"])
                stack = []
                for char in text:
                    if char in "([":
                        stack.append(char)
                    elif char in ")]":
                        self.assertTrue(stack)
                        self.assertEqual(stack.pop(), {')': '(', ']': '['}[char])
                self.assertEqual(stack, [])
                called = re.findall(r"\b([A-Za-z][A-Za-z0-9]*)\s*\(", text)
                self.assertEqual(set(called), set(case["functions"]))
                self.assertTrue(all(name.casefold() in known for name in called))
                # This only checks vocabulary/balancing, not FileMaker parsing or behavior.

    def test_independent_expected_value_oracles_not_engine(self):
        expected = {c["id"]: c for c in json.loads((ROOT / "tests/calculation-cases.json").read_text(encoding="utf-8"))["cases"]}
        oracles = {
            "packing-json": {"unitCount": 7 * 6, "batchKey": "DEMO-042"},
            "normalize-key": "  queue-k9  ".strip().upper(),
            "exact-secret-comparison": int("Case7" == "case7"),
            "bounded-suffix": "DISPATCH-082"[-3:],
            "case-classification": "bulk" if 7 > 10 else "standard",
            "modulo-bucket": 47 % 6,
            "absolute-delta": abs(13 - 31),
            "binomial-selection": math.comb(8, 3),
            "date-component": datetime.date(2041, 11, 23).year,
            "safe-character-filter": "".join(c for c in "Q9-R2" if c in "0123456789"),
            "json-typed-read": json.loads('{"attempt":3}')["attempt"],
        }
        for key, result in oracles.items():
            self.assertEqual(expected[key]["expected"], result)
        self.assertEqual(expected["elapsed-seconds"]["expected_seconds"], 2 * 3600 + 17 * 60 + 9)

    def test_source_coverage_refs_present(self):
        baseline = json.loads((ROOT / "tests/reference-baseline.json").read_text(encoding="utf-8"))
        for name in baseline["reference_heading_rosters"]:
            self.assertTrue((REFS / name).is_file(), name)
            text = (REFS / name).read_text(encoding="utf-8")
            self.assertIn("CadenceUX", text)
            self.assertTrue("Contents" in text or "contents" in text)

    def test_every_original_native_function_section_retained(self):
        baseline = json.loads((ROOT / "tests/reference-baseline.json").read_text(encoding="utf-8"))
        functions = json.loads((REFS / "function-catalog.json").read_text(encoding="utf-8"))["functions"]
        names = {x["name"] for x in functions}
        for filename, headings in baseline["reference_heading_rosters"].items():
            expected = {line[3:].split("(")[0].strip() for line in headings}
            expected &= names
            actual = set(re.findall(r"^#{2,4}\s+([A-Za-z][A-Za-z0-9]*)\b", (REFS / filename).read_text(encoding="utf-8"), re.M))
            with self.subTest(filename=filename):
                self.assertEqual(expected - actual, set(), "Missing original function section")

    def test_all_138_get_functions_locally_documented(self):
        functions = json.loads((REFS / "function-catalog.json").read_text(encoding="utf-8"))["functions"]
        normalize = lambda value: re.sub(r"\s+", "", value).casefold()
        expected = {normalize(x["name"]) for x in functions if x["name"].startswith("Get(")}
        actual = {normalize(value) for value in re.findall(r"Get\s*\(\s*\w+\s*\)", (REFS / "get-functions-examples.md").read_text(encoding="utf-8"))}
        self.assertEqual(len(expected), 138)
        self.assertEqual(expected - actual, set())

    def test_replacement_ledger_complete_and_no_engine_claim(self):
        ledger = json.loads((REFS / "replacement-ledger.json").read_text(encoding="utf-8"))
        self.assertEqual(len(ledger["ledgers"]), 4)
        self.assertIn("No FileMaker engine test", ledger["scope"])

    def test_example_native_call_inventory(self):
        result = lint_examples.scan()
        self.assertEqual(result["unknown_calls"], [])
        self.assertGreater(result["call_names_checked"], 1000)

    def test_json_example_fixtures_parse(self):
        count = 0
        for path in REFS.glob("*.md"):
            for block in re.findall(r"^```json[^\n]*\n(.*?)^```\s*$", path.read_text(encoding="utf-8"), re.M | re.S):
                with self.subTest(path=path.name, example=count):
                    json.loads(block)
                count += 1
        self.assertGreaterEqual(count, 4)

    def test_long_original_fenced_examples_not_copied_unchanged(self):
        baseline = json.loads((ROOT / "tests/reference-baseline.json").read_text(encoding="utf-8"))
        for filename, hashes in baseline["long_example_sha256"].items():
            actual = re.findall(r"^```[^\n]*\n(.*?)^```\s*$", (REFS / filename).read_text(encoding="utf-8"), re.M | re.S)
            current = {hashlib.sha256(block.strip().encode()).hexdigest() for block in actual if len(block.strip()) > 120}
            with self.subTest(filename=filename):
                self.assertEqual(set(hashes) & current, set(), "Long original worked block still unchanged; review individually")


if __name__ == "__main__":
    unittest.main()
