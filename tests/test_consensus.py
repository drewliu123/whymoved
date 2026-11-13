"""Consensus snapshots, revisions, dispersion and guidance separation."""

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
import consensus
import render_report
from test_reports import AS_OF, documents
from test_sources import candidate


def block(**overrides):
    data = {"series_id": "NVDA_FY2027_EPS", "metric": "EPS", "target_period": "FY2027",
            "provider": "LSEG", "sample_size": 24, "median": 9.0, "low": 8.2, "high": 9.8}
    data.update(overrides)
    return data


def claim(cid="C1", ctype="consensus", as_of=AS_OF, **overrides):
    data = {"id": cid, "text": "EPS estimate snapshot", "type": ctype, "as_of": as_of,
            "sources": [{"source_id": "S1"}]}
    data.update(overrides)
    return data


def survey(cid="S1", tier="T1", fieldwork_end="2026-10-30", population="24 surveyed analysts"):
    return candidate(cid, tier=tier, supports=["consensus"], evidence_kind="survey",
                     published_at=fieldwork_end,
                     survey={"population": population, "sample_size": 24, "method": "poll",
                             "fieldwork_start": "2026-09-01", "fieldwork_end": fieldwork_end})


def survey_doc(*sources):
    return {"schema_version": 2, "as_of": AS_OF, "historical": False,
            "candidates": list(sources), "source_status": {"web": {"status": "ok"}}}


class BlockValidationTests(unittest.TestCase):
    def errors(self, data, ctype="consensus"):
        return consensus.validate_claim_blocks(claim(ctype=ctype, **data))

    def test_valid_blocks(self):
        self.assertEqual(self.errors({"consensus": block()}), [])
        self.assertEqual(self.errors({"guidance": {"metric": "revenue", "target_period": "FY2027",
                                                  "midpoint": 100, "low": 98, "high": 102}}, ctype="fact"), [])
        self.assertEqual(self.errors({"guidance": {"metric": "revenue", "target_period": "FY2027",
                                                  "midpoint": 100}}, ctype="fact"), [])

    def test_type_rules(self):
        self.assertTrue(self.errors({"consensus": block()}, ctype="fact"))
        self.assertTrue(self.errors({"guidance": {"metric": "m", "target_period": "p", "midpoint": 1}},
                                    ctype="price"))
        self.assertTrue(self.errors({"guidance": {"metric": "m", "target_period": "p", "midpoint": 1}},
                                    ctype="consensus"))
        message = self.errors({"guidance": {"metric": "m", "target_period": "p", "midpoint": 1}},
                              ctype="consensus")[0]
        self.assertIn("cannot stand in for analyst consensus", message)

    def test_consensus_shape_failures(self):
        cases = [
            {"consensus": None},
            {"consensus": block(series_id="1bad")},
            {"consensus": {key: value for key, value in block().items() if key != "provider"}},
            {"consensus": block(provider="")},
            {"consensus": block(sample_size=1)},
            {"consensus": block(sample_size=2.0)},
            {"consensus": block(median=10.0)},
            {"consensus": block(low=9.5, median=9.0)},
            {"consensus": block(high=float("nan"))},
            {"consensus": dict(block(), extra=1)},
        ]
        for data in cases:
            self.assertTrue(self.errors(data), data)

    def test_guidance_shape_failures(self):
        cases = [{"guidance": None}, {"guidance": {}},
                 {"guidance": {"metric": "", "target_period": "p", "midpoint": 1}},
                 {"guidance": {"metric": "m", "target_period": "p", "midpoint": 1, "low": 2, "high": 3}},
                 {"guidance": {"metric": "m", "target_period": "p", "midpoint": 1, "low": 5, "high": 3}},
                 {"guidance": {"metric": "m", "target_period": "p", "midpoint": 1, "extra": 2}}]
        for data in cases:
            self.assertTrue(self.errors(data, ctype="fact"), data)

    def test_ledger_wiring(self):
        ledger = {"schema_version": 2, "as_of": AS_OF,
                  "claims": [claim(consensus_scope="24 surveyed analysts", consensus=block())]}
        result = check_claims.validate_ledger(ledger, survey_doc(survey()))
        self.assertTrue(result["passed"], result["failures"])
        bad = copy.deepcopy(ledger)
        bad["claims"][0]["consensus"]["sample_size"] = 1
        result = check_claims.validate_ledger(bad, survey_doc(survey()))
        self.assertFalse(result["passed"])
        self.assertIn("consensus:", json.dumps(result["failures"], ensure_ascii=False))

    def test_guidance_on_consensus_is_rejected_by_ledger(self):
        ledger = {"schema_version": 2, "as_of": AS_OF,
                  "claims": [claim(consensus_scope="24 surveyed analysts", consensus=block(),
                                   guidance={"metric": "revenue", "target_period": "FY2027", "midpoint": 1})]}
        result = check_claims.validate_ledger(ledger, survey_doc(survey()))
        self.assertFalse(result["passed"])
        self.assertIn("guidance", json.dumps(result["failures"], ensure_ascii=False))


class RevisionTests(unittest.TestCase):
    def snapshot(self, cid, as_of, median, provider="LSEG", metric="EPS", low=None, high=None):
        return {"id": cid, "type": "consensus", "as_of": as_of,
                "consensus": block(median=median, low=median - 1 if low is None else low,
                                   high=median + 1 if high is None else high,
                                   provider=provider, metric=metric)}

    def analyse(self, claims):
        return consensus.analyse(claims)

    def test_revision_direction_and_percent(self):
        result = self.analyse([self.snapshot("C1", "2026-10-01T00:00:00Z", 9.0),
                               self.snapshot("C2", "2026-10-20T00:00:00Z", 9.45),
                               self.snapshot("C3", "2026-10-31T00:00:00Z", 9.0)])
        self.assertEqual(len(result["series"]), 1)
        revisions = result["series"][0]["revisions"]
        self.assertEqual([row["direction"] for row in revisions], ["up", "down"])
        self.assertAlmostEqual(revisions[0]["pct"], 0.05)
        self.assertAlmostEqual(revisions[1]["delta"], -0.45)
        self.assertAlmostEqual(result["series"][0]["snapshots"][0]["dispersion"], 2 / 9.0)

    def test_snapshots_are_ordered_by_as_of_not_input_order(self):
        result = self.analyse([self.snapshot("C2", "2026-10-20T00:00:00Z", 9.45),
                               self.snapshot("C1", "2026-10-01T00:00:00Z", 9.0)])
        snapshots = result["series"][0]["snapshots"]
        self.assertEqual([row["claim_id"] for row in snapshots], ["C1", "C2"])
        self.assertEqual(result["series"][0]["revisions"][0]["direction"], "up")

    def test_single_snapshot_warns_and_separates_target_periods(self):
        result = self.analyse([self.snapshot("C1", "2026-10-01T00:00:00Z", 9.0)])
        self.assertEqual(len(result["series"]), 1)
        self.assertTrue(any("single snapshot" in warning for warning in result["warnings"]))
        self.assertEqual(result["series"][0]["revisions"], [])
        other = self.snapshot("C3", "2026-10-02T00:00:00Z", 12.0)
        other["consensus"]["target_period"] = "FY2028"
        result = self.analyse([self.snapshot("C1", "2026-10-01T00:00:00Z", 9.0), other])
        self.assertEqual(len(result["series"]), 2)

    def test_provider_and_metric_mixing_warns(self):
        result = self.analyse([self.snapshot("C1", "2026-10-01T00:00:00Z", 9.0, provider="LSEG"),
                               self.snapshot("C2", "2026-10-20T00:00:00Z", 9.4, provider="FactSet"),
                               self.snapshot("C3", "2026-10-21T00:00:00Z", 9.4, metric="EPS (adj)")])
        warnings = " ".join(result["warnings"])
        self.assertIn("mixes providers", warnings)
        self.assertIn("mixes metric labels", warnings)

    def test_zero_median_has_no_percent(self):
        result = self.analyse([self.snapshot("C1", "2026-10-01T00:00:00Z", 0.0),
                               self.snapshot("C2", "2026-10-20T00:00:00Z", 1.0)])
        revision = result["series"][0]["revisions"][0]
        self.assertIsNone(revision["pct"])
        self.assertEqual(revision["direction"], "up")

    def test_guidance_is_listed_separately(self):
        result = self.analyse([{"id": "G1", "type": "fact", "as_of": AS_OF,
                                "guidance": {"metric": "revenue", "target_period": "FY2027",
                                             "midpoint": 100, "low": 98, "high": 102}}])
        self.assertEqual(result["series"], [])
        self.assertEqual(result["guidance"][0]["claim_id"], "G1")
        self.assertEqual(result["guidance"][0]["midpoint"], 100)

    def test_invalid_blocks_are_ignored_by_extraction(self):
        result = self.analyse([{"id": "C1", "type": "consensus", "as_of": AS_OF,
                                "consensus": block(sample_size=1)},
                               {"id": "G1", "type": "fact", "as_of": AS_OF,
                                "guidance": {"metric": "", "target_period": "p", "midpoint": 1}}])
        self.assertEqual(result["series"], [])
        self.assertEqual(result["guidance"], [])


class GrowthTests(unittest.TestCase):
    def claim(self, cid, period, median, provider="LSEG", metric="EPS", as_of="2026-10-01T00:00:00Z"):
        return {"id": cid, "type": "consensus", "as_of": as_of,
                "consensus": {"series_id": "NVDA_EPS", "metric": metric, "target_period": period,
                              "provider": provider, "sample_size": 20, "median": median,
                              "low": median - 1, "high": median + 1}}

    def growth(self, claims):
        return consensus.analyse(claims)

    def test_consecutive_fiscal_years_produce_growth(self):
        result = self.growth([self.claim("C1", "FY2026", 10), self.claim("C2", "FY2027", 12)])
        self.assertEqual(len(result["period_growth"]), 1)
        row = result["period_growth"][0]
        self.assertAlmostEqual(row["implied_growth"], 0.2)
        self.assertEqual((row["from_period"], row["to_period"]), ("FY2026", "FY2027"))
        self.assertEqual((row["from_claim"], row["to_claim"]), ("C1", "C2"))

    def test_non_consecutive_years_are_skipped(self):
        result = self.growth([self.claim("C1", "FY2025", 10), self.claim("C2", "FY2027", 12)])
        self.assertEqual(result["period_growth"], [])

    def test_provider_mismatch_is_skipped_with_warning(self):
        result = self.growth([self.claim("C1", "FY2026", 10),
                              self.claim("C2", "FY2027", 12, provider="FactSet")])
        self.assertEqual(result["period_growth"], [])
        self.assertTrue(any("providers differ" in warning for warning in result["warnings"]))

    def test_metric_mismatch_and_zero_base(self):
        result = self.growth([self.claim("C1", "FY2026", 10, metric="EPS"),
                              self.claim("C2", "FY2027", 12, metric="EPS (adj)")])
        self.assertEqual(result["period_growth"], [])
        self.assertTrue(any("metric labels differ" in warning for warning in result["warnings"]))
        result = self.growth([self.claim("C1", "FY2026", 0), self.claim("C2", "FY2027", 12)])
        self.assertEqual(result["period_growth"], [])
        self.assertTrue(any("base median is zero" in warning for warning in result["warnings"]))

    def test_non_fiscal_labels_are_ignored(self):
        result = self.growth([self.claim("C1", "next quarter", 10), self.claim("C2", "2027Q1", 12)])
        self.assertEqual(result["period_growth"], [])

    def test_latest_snapshot_of_each_period_is_used(self):
        result = self.growth([self.claim("C1", "FY2026", 9, as_of="2026-09-01T00:00:00Z"),
                              self.claim("C2", "FY2026", 10, as_of="2026-10-01T00:00:00Z"),
                              self.claim("C3", "FY2027", 12)])
        row = result["period_growth"][0]
        self.assertAlmostEqual(row["implied_growth"], 0.2)
        self.assertEqual(row["from_claim"], "C2")


class CliAndRenderTests(unittest.TestCase):
    def run_cli(self, claims):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp).resolve() / "claims.json"
            path.write_text(json.dumps({"claims": claims}), encoding="utf-8")
            return subprocess.run([sys.executable, str(SCRIPTS / "consensus.py"), str(path)],
                                  capture_output=True, text=True)

    def test_cli(self):
        process = self.run_cli([RevisionTests().snapshot("C1", "2026-10-01T00:00:00Z", 9.0),
                                RevisionTests().snapshot("C2", "2026-10-20T00:00:00Z", 9.4)])
        self.assertEqual(process.returncode, 0, process.stdout)
        payload = json.loads(process.stdout)
        self.assertTrue(payload["passed"])
        self.assertEqual(len(payload["series"][0]["revisions"]), 1)

    def test_cli_failures(self):
        process = self.run_cli([{"id": "C1", "type": "consensus", "as_of": AS_OF,
                                 "consensus": block(sample_size=1)}])
        self.assertEqual(process.returncode, 1)
        self.assertFalse(json.loads(process.stdout)["passed"])
        with tempfile.TemporaryDirectory() as tmp:
            broken = Path(tmp) / "broken.json"
            broken.write_text("{", encoding="utf-8")
            process = subprocess.run([sys.executable, str(SCRIPTS / "consensus.py"), str(broken)],
                                     capture_output=True, text=True)
            self.assertEqual(process.returncode, 2)

    def test_render_series_and_guidance(self):
        report, ledger, sources = documents()
        sources["candidates"].append(survey("S2"))
        ledger["claims"].append({"id": "C2", "text": "EPS estimate snapshot", "type": "consensus",
                                 "as_of": AS_OF, "sources": [{"source_id": "S2"}],
                                 "consensus_scope": "24 surveyed analysts", "consensus": block()})
        ledger["claims"][0]["guidance"] = {"metric": "revenue", "target_period": "FY2027",
                                           "midpoint": 12, "low": 11, "high": 13}
        self.assertEqual(render_report.validate_report(report, ledger, sources), [])
        for render in (render_report.render_markdown, render_report.render_html):
            text = render(report, ledger, sources).replace("\\", "")
            for word in ("一致预期序列", "共识快照", "NVDA_FY2027_EPS", "24", "公司指引", "管理层指引",
                         "FY2027", "跨提供方不可直接比较"):
                self.assertIn(word, text)

    def test_render_period_growth_table(self):
        report, ledger, sources = documents()
        sources["candidates"].append(survey("S2"))
        sources["candidates"].append(survey("S3"))
        ledger["claims"].append({"id": "C2", "text": "FY2026 EPS estimate snapshot", "type": "consensus",
                                 "as_of": AS_OF, "sources": [{"source_id": "S2"}],
                                 "consensus_scope": "24 surveyed analysts",
                                 "consensus": block(target_period="FY2026", median=10.0, low=9.0, high=11.0)})
        ledger["claims"].append({"id": "C3", "text": "FY2027 EPS estimate snapshot", "type": "consensus",
                                 "as_of": AS_OF, "sources": [{"source_id": "S3"}],
                                 "consensus_scope": "24 surveyed analysts",
                                 "consensus": block(target_period="FY2027", median=12.0, low=11.0, high=13.0)})
        self.assertEqual(render_report.validate_report(report, ledger, sources), [])
        for render in (render_report.render_markdown, render_report.render_html):
            text = render(report, ledger, sources).replace("\\", "")
            for word in ("相邻财年的隐含增长", "共识隐含增长", "FY2026", "FY2027", "0.2", "共识自己的算术"):
                self.assertIn(word, text)

    def test_reports_without_blocks_render_unchanged(self):
        report, ledger, sources = documents()
        text = render_report.render_markdown(report, ledger, sources)
        self.assertNotIn("一致预期序列", text)
        self.assertNotIn("管理层指引", text)


if __name__ == "__main__":
    unittest.main()
