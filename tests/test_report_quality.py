"""Readability guards for the example reports: scenario count and chart units."""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MONEY = ("百万美元", "美元", "倍", "天", "指数")


class ExampleReportQualityTests(unittest.TestCase):
    def reports(self):
        for path in sorted((ROOT / "examples").glob("*/research/work/report.json")):
            yield path.parents[2].name, json.loads(path.read_text(encoding="utf-8"))

    def test_scenarios_are_focused(self):
        for name, report in self.reports():
            scenarios = report.get("scenarios", [])
            self.assertLessEqual(len(scenarios), 4, "%s has %d scenarios; keep at most four" % (name, len(scenarios)))

    def test_implications_are_not_finding_copies(self):
        def grams(value):
            value = "".join(value.split())
            return {value[index:index + 2] for index in range(len(value) - 1)}

        for name, report in self.reports():
            findings = [item.get("title", "") + item.get("text", "") for item in report.get("findings", [])]
            for implication in report.get("implications", []):
                left = grams(implication.get("title", "") + implication.get("text", ""))
                best = 0.0
                for finding in findings:
                    right = grams(finding)
                    if left and right:
                        best = max(best, len(left & right) / len(left | right))
                self.assertLess(best, 0.35, "%s implication repeats a finding: %s" % (name, implication.get("title")))

    def test_charts_do_not_mix_units(self):
        for name, report in self.reports():
            for index, chart in enumerate(report.get("charts", [])):
                names = [series.get("name", "") for series in chart.get("series", [])]
                if not names:
                    continue
                has_percent = any("%" in item for item in names)
                has_other = any(any(token in item for token in MONEY) for item in names)
                self.assertFalse(has_percent and has_other,
                                 "%s chart[%d] mixes percent with another unit: %r" % (name, index, names))


if __name__ == "__main__":
    unittest.main()
