"""Independent stdlib oracles for the adapted text/date examples.

These reproduce the 374 equality assertions run during the adaptation. They
model selected expectations in Python, not FileMaker parsing, evaluation,
coercion, locale, rendering, field storage, or engine behavior. Catalog checks
and the separately inspected RGB/weekday/ordinal printouts are not counted.

Run directly to see both unittest results and the actual equality-assertion
count: python3 tests/test_text_date_oracles.py
"""

import datetime
import re
import unittest


def normalized_date(month, day, year):
    """Gregorian component-overflow model; not a FileMaker Date evaluator."""
    year += (month - 1) // 12
    month = (month - 1) % 12 + 1
    return datetime.date(year, month, 1) + datetime.timedelta(days=day - 1)


def fiscal_week_model(day, starting_day):
    """Generalize ISO's four-day-first-week rule to another week start.

    This assumption is a mathematical model, not evidence about FileMaker's
    custom-start fiscal-week engine behavior. starting_day uses Sunday=1.
    """
    python_start = (starting_day + 5) % 7

    def first_week_start(year):
        january_fourth = datetime.date(year, 1, 4)
        return january_fourth - datetime.timedelta(
            days=(january_fourth.weekday() - python_start) % 7
        )

    year = day.year
    if day < first_week_start(year):
        year -= 1
    elif day >= first_week_start(year + 1):
        year += 1
    return (day - first_week_start(year)).days // 7 + 1


def daily_business_days(start, stop):
    """Independent enumeration of weekdays in [start, stop), without holidays."""
    return sum(
        (start + datetime.timedelta(days=offset)).weekday() < 5
        for offset in range((stop - start).days)
    )


def final_business_day_model(window_start, window_stop):
    """Model the final reference expression's full-week/tail structure.

    Preconditions: date inputs, stop >= start, Monday-Friday workweek, no
    holidays. Each full seven-day block contributes five days. The remaining
    dates are exactly [window_stop - tail, window_stop), including its first
    date and excluding window_stop. Decreasing `remaining` visits these dates
    in ascending order; it does not walk the calendar backward. At most six
    dates are inspected. This models semantics, not the FileMaker While API.
    """
    span = (window_stop - window_start).days
    if span < 0:
        raise ValueError("window_stop must not precede window_start")
    blocks, tail = divmod(span, 7)
    remaining = tail
    count = 0
    while remaining > 0:
        day = window_stop - datetime.timedelta(days=remaining)
        weekday = (day.weekday() + 1) % 7 + 1  # Sunday=1, Saturday=7
        count += weekday > 1 and weekday < 7
        remaining -= 1
    return blocks * 5 + count


class TextDateOracleTests(unittest.TestCase):
    equality_assertions_executed = 0

    def eq(self, actual, expected):
        """Count actual unittest equality calls, not examples or loop iterations."""
        type(self).equality_assertions_executed += 1
        self.assertEqual(actual, expected)

    @classmethod
    def setUpClass(cls):
        cls.equality_assertions_executed = 0

    @classmethod
    def tearDownClass(cls):
        print(
            "Independent Python oracle equality assertions executed: "
            f"{cls.equality_assertions_executed}; no FileMaker engine invoked."
        )

    def test_unicode_and_text_models(self):
        for code, character in [(937, "Ω"), (8594, "→")]:
            self.eq(chr(code), character)
            self.eq(ord(character), code)
        self.eq(sum(ord(c) * 100000**i for i, c in enumerate("R7")), 5500082)
        self.eq("".join(c for c in "zone:R/slot:S/level:T" if c in "RST"), "RST")
        self.eq("".join(c for c in "crate 48 / bay 206" if c.isdigit()), "48206")
        for text, length, expected in [
            ("LAB-842", 3, "LAB"),
            ("Dispatch ready", 8, "Dispatch"),
        ]:
            self.eq(text[:length], expected)
        for text, expected in [("R7-42", 5), ("Bay 12 ready", 12)]:
            self.eq(len(text), expected)
        self.eq("BOX-739-Q"[4:7], "739")
        self.eq("Gate opens noon"[5:10], "opens")
        self.eq("QA ok; qa hold".lower().count("qa"), 2)
        self.eq("bay-bay-bay".count("bay"), 3)
        self.eq("rack/slot/bin".index("/") + 1, 5)
        self.eq("rack/slot/bin".rindex("/") + 1, 10)
        self.eq("QA ok; qa hold".lower().rindex("qa") + 1, 8)
        self.eq("Dock closed"[:5] + "available" + "Dock closed"[11:], "Dock available")
        self.eq("R7:084"[:2] + "-" + "R7:084"[3:], "R7-084")
        self.eq("R7084"[:2] + "-" + "R7084"[2:], "R7-084")
        self.eq(sorted([80, 7, 120, 4]), [4, 7, 80, 120])
        self.eq(sorted([95, 420, 26, 61], reverse=True), [420, 95, 61, 26])
        self.eq(
            "raw parcel".replace("raw", "checked").replace("checked", "sealed"),
            "sealed parcel",
        )
        self.eq(" ".join("North    loading   bay".split()), "North loading bay")
        self.eq("".join("  LOT  83 Z ".split()), "LOT83Z")
        self.eq(len("Keep all chilled samples upright".split()), 5)
        for text, increment, expected in [
            ("CRATE-047", 2, "CRATE-049"),
            ("CRATE-099", 1, "CRATE-100"),
            ("SHELF280", 15, "SHELF295"),
        ]:
            match = re.search(r"(\d+)$", text)
            self.eq(
                text[: match.start()]
                + str(int(match[0]) + increment).zfill(len(match[0])),
                expected,
            )

    def test_date_overflow_and_clamped_months(self):
        for components, expected in [
            ((8, 18, 2032), datetime.date(2032, 8, 18)),
            ((14, 1, 2031), datetime.date(2032, 2, 1)),
            ((9, 0, 2032), datetime.date(2032, 8, 31)),
            ((9, -3, 2032), datetime.date(2032, 8, 28)),
        ]:
            self.eq(normalized_date(*components), expected)
        self.eq(
            (normalized_date(4, 24, 2032) - normalized_date(4, 6, 2032)).days,
            18,
        )
        for year, expected in [
            (2031, datetime.date(2032, 2, 29)),
            (2030, datetime.date(2031, 2, 28)),
        ]:
            source = datetime.date(year, 11, 30)
            first = normalized_date(14, 1, year)
            last = normalized_date(first.month + 1, 0, first.year)
            self.eq(min(last, first + datetime.timedelta(days=source.day - 1)), expected)
        self.eq(datetime.date(2032, 3, 1).timetuple().tm_yday, 61)

    def test_fiscal_week_assumptions(self):
        for day, start, expected in [
            (datetime.date(2032, 1, 11), 1, 2),
            (datetime.date(2032, 1, 1), 5, 1),
            (datetime.date(2032, 1, 2), 1, 53),
            (datetime.date(2027, 1, 1), 2, 53),
            (datetime.date(2030, 12, 30), 2, 1),
        ]:
            self.eq(fiscal_week_model(day, start), expected)

    def test_calendar_and_july_fiscal_quarters(self):
        for month in range(1, 13):
            self.eq((month - 1) // 3 + 1, (month + 2) // 3)
            self.eq(((month + 5) % 12) // 3 + 1, ((month - 7) % 12) // 3 + 1)

    def test_weekday_numbering_and_next_business_day(self):
        base = datetime.date(2032, 3, 1)
        for offset in range(7):
            day = base + datetime.timedelta(days=offset)
            weekday = (day.weekday() + 1) % 7 + 1
            self.eq((weekday + 5) % 7 + 1, day.isoweekday())
            monday = day + datetime.timedelta(days=(2 - weekday) % 7)
            self.eq(monday.weekday(), 0)
            candidate = day + datetime.timedelta(days=1)
            candidate_weekday = (candidate.weekday() + 1) % 7 + 1
            next_day = candidate + datetime.timedelta(
                days=2 if candidate_weekday == 7 else 1 if candidate_weekday == 1 else 0
            )
            self.eq(next_day.weekday() < 5, True)

    def test_initial_business_day_model_140_intervals(self):
        """Reproduce the initial full-week/remainder versus daily-count checks."""
        base = datetime.date(2032, 3, 1)
        for offset in range(7):
            start = base + datetime.timedelta(days=offset)
            for length in range(20):
                stop = start + datetime.timedelta(days=length)
                full, remaining = divmod(length, 7)
                independent = full * 5 + sum(
                    (start + datetime.timedelta(days=i)).weekday() < 5
                    for i in range(remaining)
                )
                with self.subTest(start=start, length=length):
                    self.eq(daily_business_days(start, stop), independent)

    def test_final_business_day_expression_140_intervals(self):
        """Check the final tail endpoint semantics against daily enumeration.

        Seven starting weekdays times lengths 0..19 cover empty and one-day
        windows, complete weeks, and all tail lengths, including weekend
        endpoints. Reusing these 140 intervals is intentional: these are the
        additional 140 assertions actually run on the final expression.
        """
        base = datetime.date(2032, 3, 1)
        for offset in range(7):
            start = base + datetime.timedelta(days=offset)
            for length in range(20):
                stop = start + datetime.timedelta(days=length)
                with self.subTest(start=start, length=length):
                    self.eq(
                        final_business_day_model(start, stop),
                        daily_business_days(start, stop),
                    )

    def test_time_overflow_and_duration_arithmetic(self):
        for hours, minutes, seconds, expected in [
            (6, 42, 17, (6, 42, 17)),
            (6.25, 8, 12, (6, 23, 12)),
            (6, 42, 95, (6, 43, 35)),
        ]:
            total = int(hours * 3600 + minutes * 60 + seconds)
            self.eq((total // 3600, total // 60 % 60, total % 60), expected)
        self.eq(3.4 * 3600, 12240)
        self.eq(97680 // 3600, 27)
        self.eq((97680 % 3600) // 60, 8)


if __name__ == "__main__":
    unittest.main(verbosity=2)
