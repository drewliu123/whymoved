"""Expectation comparison: price-implied growth beside consensus growth, never merged."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import expectation_compare
from test_analysis_contract import priced_bundle
from test_reports import documents


def consensus_claim(cid, period, median):
    return {"id": cid, "text": "共识快照", "type": "consensus", "as_of": "2026-10-31T12:00:00Z",
            "sources": [{"source_id": "S1"}], "consensus_scope": "analysts",
            "consensus": {"series_id": "EPS", "metric": "EPS", "target_period": period,
                          "provider": "LSEG", "sample_size": 20, "median": median,
                          "low": median - 1, "high": median + 1}}


class BuildTests(unittest.TestCase):
    def test_both_sides(self):
        report, ledger, sources, plan = priced_bundle()
        claims = ledger["claims"] + [consensus_claim("K1", "FY2026", 10), consensus_claim("K2", "FY2027", 12)]
        result = expectation_compare.build(report, claims)
        self.assertEqual(len(result["price_implied_growth"]), 1)
        price = result["price_implied_growth"][0]
        self.assertEqual(price["model_id"], "M1")
        self.assertEqual(price["years"], 5)
        self.assertIn("未来 5 年", price["horizon"])
        self.assertEqual(len(result["consensus_growth"]), 1)
        self.assertAlmostEqual(result["consensus_growth"][0]["implied_growth"], 0.2)
        self.assertEqual(result["gaps"], [])
        self.assertTrue(any("相减" in note for note in result["notes"]))

    def test_missing_sides_are_reported(self):
        report, ledger, sources = documents()
        result = expectation_compare.build(report, [consensus_claim("K1", "FY2026", 10),
                                                    consensus_claim("K2", "FY2027", 12)])
        self.assertEqual(result["price_implied_growth"], [])
        self.assertTrue(any("reverse_dcf" in gap for gap in result["gaps"]))
        report, ledger, sources, plan = priced_bundle()
        result = expectation_compare.build(report, ledger["claims"])
        self.assertEqual(result["consensus_growth"], [])
        self.assertTrue(any("相邻财年" in gap for gap in result["gaps"]))

    def test_markdown_output(self):
        report, ledger, sources, plan = priced_bundle()
        claims = ledger["claims"] + [consensus_claim("K1", "FY2026", 10), consensus_claim("K2", "FY2027", 12)]
        text = expectation_compare.render_markdown(expectation_compare.build(report, claims))
        for token in ("预期对照（口径不同，不可相减）", "价格隐含增长（反向 DCF）", "共识相邻财年增长",
                      "未来 5 年的恒定增长", "FY2026", "0.2000", "## 边界"):
            self.assertIn(token, text)


class CliTests(unittest.TestCase):
    def invoke(self, report_text, claims_payload, *extra):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            report = root / "report.json"
            report.write_text(report_text, encoding="utf-8")
            claims = root / "claims.json"
            claims.write_text(json.dumps(claims_payload, ensure_ascii=False), encoding="utf-8")
            return subprocess.run([sys.executable, str(SCRIPTS / "expectation_compare.py"),
                                   str(report), "--claims", str(claims), *extra],
                                  capture_output=True, text=True)

    def test_cli_json_and_markdown(self):
        report, ledger, sources, plan = priced_bundle()
        claims = ledger["claims"] + [consensus_claim("K1", "FY2026", 10), consensus_claim("K2", "FY2027", 12)]
        process = self.invoke(json.dumps(report), {"claims": claims})
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        payload = json.loads(process.stdout)
        self.assertTrue(payload["passed"])
        self.assertEqual(len(payload["consensus_growth"]), 1)
        process = self.invoke(json.dumps(report), {"claims": claims}, "--markdown")
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        self.assertIn("# 预期对照", process.stdout)

    def test_cli_failures(self):
        process = self.invoke("[]", {"claims": []})
        self.assertEqual(process.returncode, 1)
        process = self.invoke("{}", {"claims": "nope"})
        self.assertEqual(process.returncode, 1)
        process = self.invoke("{", {"claims": []})
        self.assertEqual(process.returncode, 2)


if __name__ == "__main__":
    unittest.main()
