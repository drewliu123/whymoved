"""Price freshness in market verdicts and recorded source conflicts."""

import copy
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import analysis_contract
import render_report
import research_run
from test_analysis_contract import priced_bundle
from test_reports import AS_OF, documents

DAY = timedelta(hours=24)


def quote_source(data):
    return data[2]["candidates"][-1]


def set_quote_age(data, hours):
    as_of = datetime.fromisoformat(AS_OF.replace("Z", "+00:00"))
    quote = quote_source(data)["market_quote"]
    quote["quoted_at"] = (as_of - timedelta(hours=hours)).isoformat().replace("+00:00", "Z")


def conflict_report():
    report, ledger, sources = documents()
    second = copy.deepcopy(sources["candidates"][0])
    second.update(id="S2", url="https://example.com/second", publisher="Second Publisher", origin_id="O2")
    sources["candidates"].append(second)
    report["conflicts"] = [{
        "metric": "披露收入", "unit": "million USD",
        "candidates": [{"source_id": "S1", "value": 12}, {"source_id": "S2", "value": 10}],
        "adopted_claim_id": "C1", "rule": "以公司原始披露为准",
        "reason": "第二来源为转引且与原始披露不一致"}]
    return report, ledger, sources


class PriceFreshnessTests(unittest.TestCase):
    def check(self, data):
        research_run._validate_bundle(*data, require_analysis=True)

    def test_fresh_quote_passes(self):
        data = priced_bundle()
        self.check(data)

    def test_stale_quote_is_rejected(self):
        data = priced_bundle()
        set_quote_age(data, 200)
        with self.assertRaisesRegex(ValueError, "hour old price; max is 96"):
            self.check(data)

    def test_boundary_and_custom_threshold(self):
        data = priced_bundle()
        set_quote_age(data, 96)
        self.check(data)
        data = priced_bundle()
        set_quote_age(data, 96.5)
        with self.assertRaises(ValueError):
            self.check(data)
        data = priced_bundle()
        set_quote_age(data, 200)
        data[0]["analysis"]["market"]["price_max_age_hours"] = 1000
        self.check(data)

    def test_invalid_threshold_values(self):
        for value in (0, -5, 10000, True, "24", None):
            data = priced_bundle()
            data[0]["analysis"]["market"]["price_max_age_hours"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.check(data)

    def test_without_sources_the_age_rule_cannot_run(self):
        data = priced_bundle()
        set_quote_age(data, 500)
        self.assertEqual(analysis_contract.validate_analysis(data[0]["analysis"], data[1]["claims"]), [])

    def test_direct_unit_errors_are_reported_not_raised(self):
        data = priced_bundle()
        set_quote_age(data, 200)
        errors = analysis_contract.validate_analysis(data[0]["analysis"], data[1]["claims"], sources=data[2])
        self.assertTrue(any("hour old price" in error for error in errors), errors)


class ConflictTests(unittest.TestCase):
    def check(self, data):
        errors = render_report.validate_report(*data)
        if errors:
            raise ValueError("\n".join(errors))

    def test_valid_conflict_passes_and_renders(self):
        data = conflict_report()
        self.check(data)
        for render in (render_report.render_markdown, render_report.render_html):
            text = render(*data).replace("\\", "")
            for word in ("来源冲突与取舍", "披露收入", "S1=12", "S2=10", "以公司原始披露为准",
                         "第二来源为转引", "C1"):
                self.assertIn(word, text)

    def test_conflict_shape_failures(self):
        cases = [
            {"conflicts": []},
            {"conflicts": "nope"},
            {"conflicts": [None]},
        ]
        for patch in cases:
            report, ledger, sources = conflict_report()
            report.update(patch)
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                self.check((report, ledger, sources))
        mutations = [
            lambda entry: entry.update(candidates=[{"source_id": "S1", "value": 12}]),
            lambda entry: entry.update(candidates=[{"source_id": "S1", "value": 12},
                                                   {"source_id": "S2", "value": 12}]),
            lambda entry: entry["candidates"][1].update(source_id="S404"),
            lambda entry: entry.update(adopted_claim_id="C404"),
            lambda entry: entry.update(unit=""),
            lambda entry: entry.update(rule=""),
            lambda entry: entry.update(reason=""),
            lambda entry: entry.update(metric=""),
            lambda entry: entry.update(extra=1),
            lambda entry: entry["candidates"][0].update(note="x"),
            lambda entry: entry["candidates"][0].update(value="12"),
        ]
        for mutate in mutations:
            report, ledger, sources = conflict_report()
            mutate(report["conflicts"][0])
            with self.subTest(mutate=mutate), self.assertRaises(ValueError):
                self.check((report, ledger, sources))

    def test_adopted_claim_must_be_evidence(self):
        report, ledger, sources = conflict_report()
        ledger["claims"].append({"id": "I1", "text": "推断", "type": "inference",
                                 "as_of": AS_OF, "sources": [], "basis": ["C1"]})
        report["conflicts"][0]["adopted_claim_id"] = "I1"
        with self.assertRaises(ValueError):
            self.check((report, ledger, sources))

    def test_adopted_metric_must_match_a_candidate(self):
        report, ledger, sources = conflict_report()
        ledger["claims"][0]["metric"] = {
            "name": "revenue", "value": 12, "unit": "million USD", "period_type": "fy",
            "period_start": "2025-01-01", "period_end": "2025-12-31", "entity": "EXAMPLE"}
        self.check((report, ledger, sources))
        report["conflicts"][0]["candidates"][0]["value"] = 11
        with self.assertRaisesRegex(ValueError, "must match one candidate"):
            self.check((report, ledger, sources))
        report, ledger, sources = conflict_report()
        ledger["claims"][0]["metric"] = {
            "name": "revenue", "value": 12, "unit": "percent", "period_type": "fy",
            "period_start": "2025-01-01", "period_end": "2025-12-31", "entity": "EXAMPLE"}
        with self.assertRaisesRegex(ValueError, "metric unit"):
            self.check((report, ledger, sources))

    def test_reports_without_conflicts_render_unchanged(self):
        report, ledger, sources = documents()
        text = render_report.render_markdown(report, ledger, sources)
        self.assertNotIn("来源冲突与取舍", text)


if __name__ == "__main__":
    unittest.main()
