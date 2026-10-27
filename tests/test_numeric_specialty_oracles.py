"""Reproduce the numeric/specialty replacement review with stdlib unittest.

Run from the project root (without writing bytecode)::

    python3 -B -m unittest discover -s tests -p test_numeric_specialty_oracles.py -v

Counts are deliberately distinct from unittest's number of test methods:
* 134 mathematical/calendar/Unicode oracle subcases reproduce the successful
  review command. The length assertion is bookkeeping, not a 135th oracle.
* 417 source-dependent static assertions reproduce that command, followed by
  three bookkeeping assertions for 417 checks, 104 blocks and 139 mappings.
* Additional tests compare 72 catalog signatures and check the local coverage
  contract. Catalog comparison is NEW executable evidence: the earlier command
  checked headings but did not check the catalog. It is not part of the 417.

The source-dependent test needs the sibling sources/claris-filemaker-pro-skill
checkout, or FILEMAKER_SKILL_SOURCE_REFERENCES pointing at its references folder.
It explicitly skips when unavailable; the other tests still run. No network,
FileMaker expression interpreter, engine, device, IME, database, or renderer is
used. Python models validate mathematical expectations, not FileMaker behavior.
In particular the Unicode checks do not execute RomanHankaku or KanaZenkaku.
"""

import datetime
import json
import math
import os
from pathlib import Path
import re
import statistics
import unicodedata
import unittest
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP, localcontext


PROJECT = Path(__file__).resolve().parents[1]
REFERENCES = PROJECT / "filemaker-pro" / "references"
MANIFEST = PROJECT / "docs" / "replacements-numeric-specialty.json"
SOURCE_REFERENCES = Path(
    os.environ.get(
        "FILEMAKER_SKILL_SOURCE_REFERENCES",
        str(PROJECT.parent / "sources" / "claris-filemaker-pro-skill" / "references"),
    )
)
FILES = ("numeric-functions-examples.md", "specialty-functions-examples.md")
D = Decimal


def read_manifest():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def markdown_headings(text):
    return [line for line in text.splitlines() if line.startswith("#")]


def fenced_blocks(text):
    return re.findall(r"```[^\n]*\n(.*?)```", text, re.S)


def heading_degrees(east, north):
    """Independent Python model of the documented guarded heading branches."""
    if east == 0:
        return 90 if north > 0 else -90 if north < 0 else None
    acute = math.degrees(math.atan(north / east))
    return acute if east > 0 else acute - 180 if north < 0 else acute + 180


def oracle_cases(manifest):
    """Return (label, actual, expected, approximate) for the original 134 checks.

    Financial expectations come from the named ledger entries rather than JSON
    insertion order. They are compared exactly at Decimal precision 60. The
    approximate comparisons reproduce the original 1e-12 relative/absolute
    tolerance. Repeated related facts (e.g. two degree-conversion routes) are
    retained because they were separate checks in the original command.
    """
    cases = []

    def equal(label, actual, expected):
        cases.append((label, actual, expected, False))

    def near(label, actual, expected):
        cases.append((label, actual, expected, True))

    elementary = [
        ("abs", abs, [(-18.75, 18.75), (18.75, 18.75)]),
        ("ceiling", math.ceil, [(6.25, 7), (-6.25, -6), (8, 8)]),
        ("floor", math.floor, [(7.8, 7), (-7.2, -8), (12, 12)]),
        ("int", math.trunc, [(6.8, 6), (-6.8, -6), (21.999, 21)]),
        ("lg", math.log2, [(32, 5), (1, 0), (4096, 12)]),
        ("ln", math.log, [(1, 0), (math.exp(3), 3), (25, 3.218875824868201)]),
        ("log", math.log10, [(10000, 4), (1000000, 6), (1, 0)]),
        ("exp", math.exp, [(-2, .1353352832366127), (0, 1), (3, 20.08553692318767)]),
        ("sqrt", math.sqrt, [(144, 12), (7, 2.645751311064591), (0, 0)]),
    ]
    for name, operation, pairs in elementary:
        for value, expected in pairs:
            near(f"{name}({value})", operation(value), expected)
    equal("reviewer combinations", math.comb(9, 3), 84)
    near("balanced sample probability", math.comb(5, 2) ** 2 / math.comb(10, 4), .476190476190476)
    for value, divisor, expected in [(17.5, 4, 4), (-17.5, 4, -5), (29, 6, 4)]:
        equal(f"div({value},{divisor})", math.floor(value / divisor), expected)
    for value, divisor, expected in [(347, 8, 3), (53, 7, 4), (-17, 5, 3), (21, 12, 9)]:
        equal(f"mod({value},{divisor})", value % divisor, expected)
    equal("contract years and months", (53 // 12, 53 % 12), (4, 5))
    for value, expected in [(4, 24), (7, 5040)]:
        equal(f"factorial({value})", math.factorial(value), expected)
    equal("four descending factors from nine", math.prod(range(6, 10)), 3024)

    round_cases = [
        ("86.375", 2, "86.38"), ("8.5", 0, "9"), ("-8.5", 0, "-9"),
        ("7.65", 1, "7.7"), ("48762.12", -3, "49000"),
        ("86.375", -1, "90"), ("4.7", 0, "5"),
    ]
    for value, precision, expected in round_cases:
        equal(
            f"decimal half-up({value},{precision})",
            D(value).quantize(D(1).scaleb(-precision), rounding=ROUND_HALF_UP),
            D(expected),
        )
    for value, precision, expected in [
        ("48.987", 2, "48.98"), ("6.999", 0, "6"),
        ("-6.999", 1, "-6.9"), ("4.7", 0, "4"),
    ]:
        equal(
            f"decimal truncate({value},{precision})",
            D(value).quantize(D(1).scaleb(-precision), rounding=ROUND_DOWN),
            D(expected),
        )
    equal("int in three-way comparison", int(4.7), 4)
    for value, expected in [(-3.2, -1), (0, 0), (.08, 1)]:
        equal(f"sign({value})", (value > 0) - (value < 0), expected)
    for precision, numerator, denominator, expected in [
        (30, 2, 7, "0.285714285714285714285714285714"),
        (50, 4, 11, "0.36363636363636363636363636363636363636363636363636"),
    ]:
        with localcontext() as context:
            context.prec = precision
            equal(f"precision {precision} fraction", D(numerator) / denominator, D(expected))

    with localcontext() as context:
        context.prec = 60
        near("extended decimal exponential", D(-2).exp(), ".1353352832366126918939995")
        near("extended decimal average", (D(2) / 7 + D(4) / 11 + D(3) / 13) / 3,
             ".2933732933732933732933733")

        def fv(payment, rate, periods):
            return D(payment) * ((1 + rate) ** periods - 1) / rate

        def pv(payment, rate, periods):
            return D(payment) * (1 - (1 + rate) ** (-periods)) / rate

        def pmt(principal, rate, periods):
            return D(principal) * rate / (1 - (1 + rate) ** (-periods))

        flows = [-3600, 1200, 1400, 1700, 900]
        payment = pmt(68000, D(".004"), 84)
        finance = {
            "FV_monthly": fv(125, D(".005"), 36),
            "FV_with_opening_balance": fv(850, D(".07"), 12) + D(3200) * D("1.07") ** 12,
            "FV_four_periods_per_year": fv(300, D(".02"), 20),
            "FV_gallery_fund": fv(450, D(".012"), 24),
            "NPV_all_repetitions_discounted": sum(D(x) / D("1.08") ** i for i, x in enumerate(flows, 1)),
            "NPV_initial_at_time_zero_comparison": sum(D(x) / D("1.08") ** i for i, x in enumerate(flows)),
            "PMT_workshop_basic": pmt(18500, D(".0045"), 36),
            "PMT_total_interest": pmt(42000, D(".006"), 60) * 60 - 42000,
            "PV_basic": pv(720, D(".045"), 8),
            "PV_withdrawal_reserve": pv(1600, D(".003"), 180),
            "summary_payment": payment,
            "summary_total": payment * 84,
            "summary_interest": payment * 84 - 68000,
        }
        for name, actual in finance.items():
            equal(name, actual, D(manifest["verification"]["finance_expected_from_decimal_oracle"][name]))
        for name, expected in [
            ("summary_payment", "954.73"), ("summary_total", "80197.18"),
            ("summary_interest", "12197.18"),
        ]:
            equal(f"{name} cents", finance[name].quantize(D(".01"), rounding=ROUND_HALF_UP), D(expected))
        equal("withdrawal reserve funded", D(280000) >= finance["PV_withdrawal_reserve"], True)

    trig = [
        ("pi rounded", round(math.pi, 6), 3.141593),
        ("three half turns", math.radians(540) / math.pi, 3),
        ("third turn degrees", math.degrees(math.pi / 3), 60),
        ("30 degrees", math.radians(30), math.pi / 6),
        ("120 degrees", math.radians(120), 2 * math.pi / 3),
        ("two turns", math.radians(720), 4 * math.pi),
        ("dish area", round(math.pi * 36, 3), 113.097),
        ("atan sqrt three degrees", math.degrees(math.atan(math.sqrt(3))), 60),
        ("direct radians to degrees", math.degrees(.7), 40.10704565915762),
        ("ramp angle", math.degrees(math.atan(.4)), 21.80140948635181),
        ("obtuse radians", math.radians(135), 2.356194490192345),
        ("sine degrees", math.sin(math.radians(30)), .5),
        ("sine radians", math.sin(.4), .3894183423086505),
        ("vertical displacement", 18 * math.sin(math.radians(30)), 9),
        ("cosine radians", math.cos(.4), .9210609940028851),
        ("cosine obtuse", math.cos(math.radians(120)), -.5),
        ("horizontal displacement", 18 * math.cos(math.radians(30)), 15.5884572681199),
        ("tangent radians", math.tan(.25), .2553419212210363),
        ("tangent degrees", math.tan(math.radians(22)), .4040262258351568),
        ("mast height", 1.4 + 35 * math.tan(math.radians(22)), 15.54091790423049),
        ("acos radians", math.acos(.25), 1.318116071652818),
        ("acos manual degrees", 180 * math.acos(.25) / math.pi, 75.52248781407008),
        ("acos degrees", math.degrees(math.acos(.25)), 75.52248781407008),
        ("asin radians", math.asin(-.8), -.9272952180016123),
        ("asin degrees", math.degrees(math.asin(-.8)), -53.13010235415598),
        ("atan radians", math.atan(2), 1.10714871779409),
        ("atan degrees", math.degrees(math.atan(2)), 63.43494882292201),
    ]
    for name, actual, expected in trig:
        near(name, actual, expected)
    for east, north in [(-4, 3), (4, 3), (4, -3), (-4, -3), (0, 4), (0, -4), (-4, 0), (4, 0)]:
        near(f"heading({east},{north})", heading_degrees(east, north), math.degrees(math.atan2(north, east)))
    equal("coincident heading undefined", heading_degrees(0, 0), None)
    haversine = (
        math.sin(math.radians(.5) / 2) ** 2
        + math.cos(math.radians(10)) * math.cos(math.radians(10.5))
        * math.sin(math.radians(.75) / 2) ** 2
    )
    equal("ferry leg km", round(6371 * 2 * math.atan(math.sqrt(haversine / (1 - haversine))), 2), 99.12)
    equal("ring marker", (round(160 + 75 * math.cos(-math.pi / 4)),
                          round(120 + 75 * math.sin(-math.pi / 4))), (213, 67))

    fixtures = [
        ("reading sum", sum([14, 0, 22]), 36),
        ("reading maximum", max([14, 0, 22]), 22),
        ("reading count", len([14, 0, 22]), 3),
        ("duration average", statistics.mean([2, 6, 10]), 6),
        ("sample variance", statistics.variance([2, 6, 10]), 16),
        ("population variance", statistics.pvariance([2, 6, 10]), 10.66666666666667),
        ("sample stdev", statistics.stdev([2, 6, 10]), 4),
        ("population stdev", statistics.pstdev([2, 6, 10]), 3.265986323710904),
        ("duration sum", sum([2, 6, 10]), 18),
        ("invoice tax", 65 * .08, 5.2),
        ("invoice total", 140 + 5.2, 145.2),
        ("loss repetition 1", 2 * 1.5 * .04, .12),
        ("loss repetition 2", 4 * .75 * .04, .12),
        ("loss repetition 3", 3 * 2.2 * .04, .264),
        ("discount repetition 1", 8 * .85, 6.8),
        ("discount repetition 2", 12 * .85, 10.2),
        ("discount repetition 3", 20 * .85, 17),
    ]
    for name, actual, expected in fixtures:
        near(name, actual, expected)
    equal("inspection Tuesday (Monday=0)", datetime.date(2027, 3, 9).weekday(), 1)
    equal("November date month", datetime.date(2027, 11, 18).month, 11)
    equal("Roman width Unicode model", unicodedata.normalize("NFKC", "Ｒａｃｋ－７"), "Rack-7")
    equal("kana width Unicode model", unicodedata.normalize("NFKC", "ﾍﾟﾝ"), "ペン")
    return cases


class NumericSpecialtyOracles(unittest.TestCase):
    def test_original_134_oracle_subcases(self):
        cases = oracle_cases(read_manifest())
        self.assertEqual(len(cases), 134, "Bookkeeping: actual oracle count changed")
        for label, actual, expected, approximate in cases:
            with self.subTest(oracle=label):
                if approximate:
                    self.assertTrue(
                        math.isclose(float(actual), float(expected), rel_tol=1e-12, abs_tol=1e-12),
                        f"{actual!r} != {expected!r} within 1e-12",
                    )
                else:
                    self.assertEqual(actual, expected)

    def test_local_coverage_contract(self):
        manifest = read_manifest()
        self.assertEqual(tuple(file["file"] for file in manifest["files"]), FILES)
        for file, functions, sections, categories in zip(manifest["files"], (34, 38), (37, 40), (4, 5)):
            with self.subTest(file=file["file"]):
                text = (REFERENCES / file["file"]).read_text(encoding="utf-8")
                headings = markdown_headings(text)
                self.assertEqual(sum(h.startswith("## ") and h != "## Contents" for h in headings), sections)
                self.assertEqual(sum(h.startswith("# ") for h in headings) - 1, categories)
                self.assertEqual(file["coverage"]["retained_functions"], functions)
                self.assertEqual(text.count("```") % 2, 0)
                self.assertIn("## Contents", headings)
                self.assertIn(manifest["attribution"]["commit"], text)
                self.assertIn("CC BY 4.0", text)

    def test_additional_catalog_signature_comparison_72_functions(self):
        """New catalog check, separate from the original 417 static assertions."""
        catalog = json.loads((REFERENCES / "function-catalog.json").read_text(encoding="utf-8"))
        by_name = {entry["name"]: entry for entry in catalog["functions"]}
        category_sets = [
            {"Number functions", "Financial functions", "Trigonometric functions", "Repeating functions"},
            {"Aggregate functions", "Japanese functions", "Mobile functions", "Miscellaneous functions", "Persistent data functions"},
        ]
        compared = 0
        for filename, categories, expected_count in zip(FILES, category_sets, (34, 38)):
            expected = {name: entry["format"] for name, entry in by_name.items() if entry["category"] in categories}
            actual = {}
            text = (REFERENCES / filename).read_text(encoding="utf-8")
            for heading in markdown_headings(text):
                if not heading.startswith("## "):
                    continue
                signature = heading[3:]
                name = signature.split(" (")[0]
                if name in by_name:
                    actual[name] = signature
            with self.subTest(file=filename):
                self.assertEqual(len(expected), expected_count)
                self.assertEqual(set(actual), set(expected))
            for name, signature in actual.items():
                with self.subTest(file=filename, function=name):
                    self.assertEqual(re.sub(r"\s+", "", signature), re.sub(r"\s+", "", expected[name]))
                compared += 1
        self.assertEqual(compared, 72, "Bookkeeping: compared catalog signature count")

    def test_original_417_source_dependent_static_assertions(self):
        missing = [str(SOURCE_REFERENCES / name) for name in FILES if not (SOURCE_REFERENCES / name).is_file()]
        if missing:
            self.skipTest("Upstream sources unavailable; set FILEMAKER_SKILL_SOURCE_REFERENCES: " + ", ".join(missing))
        manifest = read_manifest()
        count = blocks = entries = 0

        def verify(condition, message):
            nonlocal count
            count += 1
            self.assertTrue(condition, message)

        for file in manifest["files"]:
            name = file["file"]
            source = (SOURCE_REFERENCES / name).read_text(encoding="utf-8")
            target = (REFERENCES / name).read_text(encoding="utf-8")
            with self.subTest(file=name):
                verify(markdown_headings(source) == markdown_headings(target), "Full ordered heading sequence differs")
                verify(target.count("```") % 2 == 0, "Unbalanced target fences")
                verify("CC BY 4.0" in target and manifest["attribution"]["commit"] in target, "Missing attribution/license")
                verify("## Contents" in target, "Missing contents")
                ranges = []
                for replacement in file["replacements"]:
                    section = replacement["section"]
                    verify(
                        "\n# " + section + "\n" in "\n" + target
                        or "\n## " + section + "\n" in "\n" + target,
                        f"Replacement section missing: {section}",
                    )
                    verify(replacement["review"] in manifest["review_status_definitions"], f"Unknown review status: {section}")
                    for example in replacement["examples"]:
                        lower, upper = example["source_lines"]
                        verify(1 <= lower <= upper <= len(source.splitlines()), f"Invalid source range: {section}")
                        ranges.append((lower, upper))
                        entries += 1
                start = None
                for line_number, line in enumerate(source.splitlines(), 1):
                    if not line.startswith("```"):
                        continue
                    if start is None:
                        start = line_number
                    else:
                        verify(
                            any(lower <= start and upper >= line_number for lower, upper in ranges),
                            f"Unmapped original block: {name}:{start}-{line_number}",
                        )
                        blocks += 1
                        start = None
                originals = {block.strip() for block in fenced_blocks(source)}
                targets = {block.strip() for block in fenced_blocks(target)}
                verify(not originals.intersection(targets), "Unchanged complete original example block")
        self.assertEqual(count, 417, "Bookkeeping: original static assertion count")
        self.assertEqual(blocks, 104, "Bookkeeping: source fenced blocks covered")
        self.assertEqual(entries, 139, "Bookkeeping: manifest example mappings")


if __name__ == "__main__":
    unittest.main(verbosity=2)
