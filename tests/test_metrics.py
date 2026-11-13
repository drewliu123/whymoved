"""Structured numeric facts: shape, period discipline, comparison consistency."""

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import check_claims
import metrics
import render_report
from test_reports import documents


def metric(**overrides):
    data = {"name": "revenue", "value": 12, "unit": "USD million", "period_type": "quarter",
            "period_start": "2026-07-01", "period_end": "2026-09-30",
            "entity": "EXAMPLE", "scope": "consolidated", "currency": "USD", "scale": "million", "basis": "gaap"}
    data.update(overrides)
    return data


def ledger_with(*blocks, claim_type="fact"):
    _, ledger, sources = documents()
    ledger["claims"][0]["type"] = claim_type
    ledger["claims"][0]["metric"] = blocks[0]
    for index, block in enumerate(blocks[1:], start=2):
        claim = copy.deepcopy(ledger["claims"][0])
        claim.update(id="C%d" % index, text="fictional metric %d" % index, metric=block)
        ledger["claims"].append(claim)
    return ledger, sources


def failures(ledger, sources):
    result = check_claims.validate_ledger(ledger, sources)
    return result, [message for messages in result["failures"].values() for message in messages]


class MetricShapeTests(unittest.TestCase):
    def test_valid_metric_passes(self):
        ledger, sources = ledger_with(metric())
        result, messages = failures(ledger, sources)
        self.assertTrue(result["passed"], messages)

    def test_metric_is_optional(self):
        _, ledger, sources = documents()
        result, messages = failures(ledger, sources)
        self.assertTrue(result["passed"], messages)

    def test_shape_failures(self):
        cases = [
            {"name": ""}, {"value": True}, {"value": float("nan")}, {"value": "12"},
            {"unit": ""}, {"period_type": "half"}, {"period_end": "not-a-date"},
            {"period_type": "fy", "period_start": None},
            {"period_start": "2026-12-31", "period_end": "2026-09-30"},
            {"period_type": "instant", "period_start": "2026-07-01"},
            {"scope": "segments"}, {"scope": "segment:"}, {"basis": "non-gaap"},
            {"currency": ""}, {"scale": ""}, {"entity": ""}, {"locator": ""},
            {"comparison_with": []}, {"comparison_with": "C2"}, {"comparison_with": [1]},
            {"comparison_with": ["C1"]}, {"unknown_field": 1},
        ]
        for overrides in cases:
            ledger, sources = ledger_with(metric(**overrides))
            result, messages = failures(ledger, sources)
            self.assertFalse(result["passed"], overrides)
            self.assertTrue(any("metric:" in message for message in messages), overrides)

    def test_required_fields(self):
        for field in metrics.REQUIRED:
            block = metric()
            del block[field]
            ledger, sources = ledger_with(block)
            result, messages = failures(ledger, sources)
            self.assertFalse(result["passed"], field)
            self.assertTrue(any("metric:" in message for message in messages), field)

    def test_metric_only_on_evidence_claims(self):
        for claim_type in ("view", "inference"):
            ledger, sources = ledger_with(metric(), claim_type=claim_type)
            result, messages = failures(ledger, sources)
            self.assertFalse(result["passed"], claim_type)
            self.assertTrue(any("metric:" in message for message in messages), claim_type)

    def test_scope_and_instant_are_accepted(self):
        ledger, sources = ledger_with(metric(scope="segment:cloud"),
                                      metric(name="shares", value=10, unit="million shares",
                                             period_type="instant", period_end="2026-09-30"))
        ledger["claims"][1]["metric"].pop("period_start")
        result, messages = failures(ledger, sources)
        self.assertTrue(result["passed"], messages)
        bad = copy.deepcopy(ledger)
        bad["claims"][1]["metric"]["period_start"] = "2026-07-01"
        result, messages = failures(bad, sources)
        self.assertFalse(result["passed"])


class MetricComparisonTests(unittest.TestCase):
    def test_consistent_comparison_passes(self):
        ledger, sources = ledger_with(metric(comparison_with=["C2"]),
                                      metric(period_start="2025-07-01", period_end="2025-09-30"))
        result, messages = failures(ledger, sources)
        self.assertTrue(result["passed"], messages)

    def test_comparison_mismatches(self):
        cases = [
            dict(unit="USD thousand"),
            dict(period_type="ytd", period_start="2026-01-01"),
            dict(currency="EUR"),
            dict(scale="billion"),
            dict(basis="adjusted", unit="USD million"),
        ]
        for overrides in cases:
            values = dict(period_start="2025-07-01", period_end="2025-09-30")
            values.update(overrides)
            other = metric(**values)
            ledger, sources = ledger_with(metric(comparison_with=["C2"]), other)
            result, messages = failures(ledger, sources)
            self.assertFalse(result["passed"], overrides)
            self.assertTrue(any("M3" in message for message in messages), (overrides, messages))

    def test_comparison_reference_problems(self):
        for block in (metric(comparison_with=["C404"]), metric(comparison_with=["C1"])):
            ledger, sources = ledger_with(block)
            result, messages = failures(ledger, sources)
            self.assertFalse(result["passed"])
            self.assertTrue(any("M3" in message for message in messages))

    def test_comparison_requires_target_metric(self):
        ledger, sources = ledger_with(metric(comparison_with=["C2"]))
        ledger["claims"].append({"id": "C2", "text": "无metric的主张", "type": "fact",
                                 "as_of": ledger["as_of"], "sources": [{"source_id": "S1"}], "basis": []})
        result, messages = failures(ledger, sources)
        self.assertFalse(result["passed"])
        self.assertTrue(any("declare metric" in message for message in messages))

    def test_same_group_requires_one_unit(self):
        ledger, sources = ledger_with(metric(), metric(period_start="2026-01-01", period_end="2026-03-31", unit="USD thousand"))
        result, messages = failures(ledger, sources)
        self.assertFalse(result["passed"])
        self.assertTrue(any("M4" in message for message in messages))
        self.assertEqual(len(result["failures"]), 2)

    def test_different_entities_may_differ(self):
        ledger, sources = ledger_with(metric(), metric(entity="PEER", currency="EUR", unit="EUR million"))
        result, messages = failures(ledger, sources)
        self.assertTrue(result["passed"], messages)

    def test_yoy_with_different_period_end_is_fine(self):
        ledger, sources = ledger_with(metric(comparison_with=["C2"]),
                                      metric(period_start="2025-07-01", period_end="2025-09-30"))
        result, messages = failures(ledger, sources)
        self.assertTrue(result["passed"], messages)


class MetricToolingTests(unittest.TestCase):
    def test_extract_metrics(self):
        ledger, _ = ledger_with(metric(), metric(name="margin", value=0.4, unit="ratio",
                                                 period_start="2026-01-01", period_end="2026-03-31"))
        ledger["claims"][1]["metric"].pop("basis")
        rows = metrics.extract_metrics(ledger["claims"])
        self.assertEqual([row["claim_id"] for row in rows], ["C1", "C2"])
        self.assertEqual(rows[0]["entity"], "EXAMPLE")
        self.assertEqual(rows[1]["name"], "margin")
        self.assertIn("2026-09-30", metrics.describe(rows[0]))

    def test_cli(self):
        ledger, _ = ledger_with(metric())
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp).resolve() / "claims.json"
            path.write_text(json.dumps(ledger), encoding="utf-8")
            process = subprocess.run([sys.executable, str(SCRIPTS / "metrics.py"), str(path)],
                                     capture_output=True, text=True)
            payload = json.loads(process.stdout)
            self.assertEqual(process.returncode, 0, payload)
            self.assertTrue(payload["passed"])
            self.assertEqual(len(payload["metrics"]), 1)
            bad = copy.deepcopy(ledger)
            bad["claims"][0]["metric"]["unit"] = ""
            path.write_text(json.dumps(bad), encoding="utf-8")
            process = subprocess.run([sys.executable, str(SCRIPTS / "metrics.py"), str(path)],
                                     capture_output=True, text=True)
            self.assertEqual(process.returncode, 0)
            self.assertEqual(json.loads(process.stdout)["metrics"], [])


class MetricRenderTests(unittest.TestCase):
    def test_metrics_appear_in_both_formats(self):
        report, ledger, sources = documents()
        ledger["claims"][0]["metric"] = metric()
        self.assertEqual(render_report.validate_report(report, ledger, sources), [])
        for render in (render_report.render_markdown, render_report.render_html):
            text = render(report, ledger, sources).replace("\\", "")
            for word in ("数值事实", "EXAMPLE", "2026-09-30", "USD million", "consolidated"):
                self.assertIn(word, text)

    def test_ledgers_without_metrics_render_unchanged(self):
        report, ledger, sources = documents()
        text = render_report.render_markdown(report, ledger, sources)
        self.assertNotIn("数值事实", text)


if __name__ == "__main__":
    unittest.main()
