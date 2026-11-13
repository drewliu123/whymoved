"""Earnings quality metrics and red-flag screening from standardized statements."""

import copy
import json
import math
import subprocess
from datetime import date
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import financial_quality as fq


def document(**overrides):
    data = {
        "schema_version": 1, "entity": "EXAMPLE", "currency": "USD", "scale": "million", "as_of": "2026-11-14",
        "periods": [
            {"id": "FY2024", "period_type": "fy", "period_start": "2024-01-01", "period_end": "2024-12-31",
             "revenue": 1000, "gross_profit": 500, "operating_profit": 200, "net_income": 150,
             "cfo": 180, "capex": 60, "depreciation_amortization": 80,
             "receivables": 120, "inventory": 80, "payables": 60,
             "total_assets": 900, "equity": 500, "debt": 200, "cash": 100,
             "share_based_comp": 40, "shares_diluted": 100, "tax_rate": 0.2},
            {"id": "FY2025", "period_type": "fy", "period_start": "2025-01-01", "period_end": "2025-12-31",
             "revenue": {"value": 1200, "claim_ids": ["C1"]}, "gross_profit": 570, "operating_profit": 210,
             "net_income": 120, "cfo": {"value": 100, "claim_ids": ["C2"]}, "capex": 50,
             "depreciation_amortization": 90, "receivables": 210, "inventory": 130, "payables": 65,
             "total_assets": 1100, "equity": 520, "debt": 260, "cash": 90,
             "share_based_comp": 90, "shares_diluted": 104, "tax_rate": 0.2},
        ],
    }
    data.update(overrides)
    return data


def period(index, identifier, **overrides):
    item = copy.deepcopy(document()["periods"][index])
    item["id"] = identifier
    item.update(overrides)
    return item


class ValidationTests(unittest.TestCase):
    def test_valid_document(self):
        self.assertEqual(fq.validate_document(document()), [])

    def test_structural_failures(self):
        cases = []
        cases.append(document(periods=[]))
        cases.append(document(periods=[period(0, "A")]))
        cases.append(document(periods=[period(0, "A"), period(1, "A")]))
        cases.append(document(periods=[period(0, "A"), period(1, "B", period_type="quarter")]))
        cases.append(document(periods=[period(0, "A"), period(1, "B", revenue=0)]))
        cases.append(document(periods=[period(0, "A"), period(1, "B", capex=-1)]))
        cases.append(document(periods=[period(0, "A"), period(1, "B", tax_rate=1.5)]))
        cases.append(document(periods=[period(0, "A"), period(1, "B", surprise=1)]))
        cases.append(document(periods=[period(0, "A", period_end="not-a-date"), period(1, "B")]))
        cases.append(document(periods=[period(0, "A", period_start="2024-12-31"), period(1, "B")]))
        cases.append(document(periods=[period(0, "A", revenue="1000"), period(1, "B")]))
        cases.append(document(periods=[period(0, "A", revenue={"value": 1000, "claim_ids": []}), period(1, "B")]))
        cases.append(document(periods=[period(0, "A", revenue={"value": 1000, "claim_ids": [""]}), period(1, "B")]))
        cases.append(document(entity=""))
        cases.append(document(schema_version=2))
        cases.append("not a document")
        for index, item in enumerate(cases):
            self.assertTrue(fq.validate_document(item), index)

    def test_claim_objects_are_accepted(self):
        data = document()
        data["periods"][0]["cfo"] = {"value": 180, "claim_ids": ["C1", "C2"]}
        self.assertEqual(fq.validate_document(data), [])


class MetricTests(unittest.TestCase):
    def setUp(self):
        self.result = fq.analyse(document())
        self.latest = self.result["periods"][-1]["metrics"]

    def test_level_metrics(self):
        latest = self.latest
        days = (date(2025, 12, 31) - date(2025, 1, 1)).days
        for name, expected in {
            "gross_margin": 0.475, "operating_margin": 0.175, "net_margin": 0.1,
            "cash_conversion": 100 / 120, "accrual_ratio": 20 / 1100,
            "capex_intensity": 50 / 1200, "capex_to_da": 50 / 90,
            "sbc_ratio": 90 / 1200, "invested_capital": 690, "roic": 210 * 0.8 / 690,
        }.items():
            self.assertAlmostEqual(latest[name], expected, places=9, msg=name)
        self.assertAlmostEqual(latest["dso"], 210 * days / 1200)
        self.assertAlmostEqual(latest["dio"], 130 * days / 630)
        self.assertAlmostEqual(latest["dpo"], 65 * days / 630)
        self.assertAlmostEqual(latest["cash_cycle"], latest["dso"] + latest["dio"] - latest["dpo"])

    def test_missing_inputs_yield_none_not_guesses(self):
        data = document()
        for field in ("receivables", "inventory", "payables", "total_assets", "tax_rate", "cash"):
            for item in data["periods"]:
                item.pop(field, None)
        result = fq.analyse(data)
        latest = result["periods"][-1]["metrics"]
        for name in ("dso", "dio", "dpo", "cash_cycle", "accrual_ratio", "invested_capital", "roic"):
            self.assertIsNone(latest[name], name)
        self.assertIsNotNone(latest["gross_margin"])

    def test_changes(self):
        changes = self.result["changes"][0]
        days = (date(2025, 12, 31) - date(2025, 1, 1)).days
        days_prev = (date(2024, 12, 31) - date(2024, 1, 1)).days
        self.assertAlmostEqual(changes["revenue_growth"], 0.2)
        self.assertAlmostEqual(changes["gross_margin_change"], -0.025)
        self.assertAlmostEqual(changes["operating_margin_change"], -0.025)
        self.assertAlmostEqual(changes["share_growth"], 0.04)
        self.assertAlmostEqual(changes["incremental_margin"], (210 - 200) / 200)
        self.assertAlmostEqual(changes["dso_change"], (210 * days / 1200) / (120 * days_prev / 1000) - 1)
        self.assertAlmostEqual(changes["dio_change"], (130 * days / 630) / (80 * days_prev / 500) - 1)

    def test_periods_are_sorted_by_end(self):
        data = document()
        data["periods"].reverse()
        result = fq.analyse(data)
        self.assertEqual([row["id"] for row in result["periods"]], ["FY2024", "FY2025"])
        self.assertEqual(result["changes"][0]["from"], "FY2024")

    def test_unattributed_fields(self):
        data = document()
        result = fq.analyse(data)
        self.assertNotIn("revenue", result["unattributed"]["FY2025"])
        self.assertNotIn("cfo", result["unattributed"]["FY2025"])
        self.assertIn("revenue", result["unattributed"]["FY2024"])
        self.assertIn("capex", result["unattributed"]["FY2025"])


class FlagTests(unittest.TestCase):
    def codes(self, result):
        return {flag["code"] for flag in result["flags"]}

    def test_expected_flags(self):
        result = fq.analyse(document())
        found = self.codes(result)
        for code in ("low_capex_vs_da", "growth_without_cash", "receivables_outpacing_revenue",
                     "inventory_build", "dilution", "operating_deleverage", "gross_margin_pressure"):
            self.assertIn(code, found)
        self.assertNotIn("high_accruals", found)
        self.assertNotIn("high_sbc", found)
        for flag in result["flags"]:
            self.assertIn(flag["severity"], ("high", "medium"))
            self.assertTrue(flag["message"])
            self.assertIn(flag["period"], ("FY2024", "FY2025"))

    def test_threshold_override(self):
        result = fq.analyse(document(), thresholds={"sbc_ratio": 0.05, "margin_drop": 1.0})
        found = self.codes(result)
        self.assertIn("high_sbc", found)
        self.assertNotIn("gross_margin_pressure", found)

    def test_clean_company_has_no_flags(self):
        data = document()
        for index, item in enumerate(data["periods"]):
            revenue = 1000 if index == 0 else 1100
            item.clear()
            item.update({"id": "FY2024" if index == 0 else "FY2025", "period_type": "fy",
                         "period_start": "2024-01-01" if index == 0 else "2025-01-01",
                         "period_end": "2024-12-31" if index == 0 else "2025-12-31",
                         "revenue": revenue, "gross_profit": revenue * 0.5,
                         "operating_profit": revenue * 0.2, "net_income": revenue * 0.1,
                         "cfo": revenue * 0.11, "capex": revenue * 0.06,
                         "depreciation_amortization": revenue * 0.05,
                         "receivables": revenue * 0.1, "inventory": revenue * 0.05,
                         "payables": revenue * 0.05, "total_assets": revenue * 0.9,
                         "equity": revenue * 0.5, "debt": revenue * 0.2, "cash": revenue * 0.1,
                         "share_based_comp": revenue * 0.02, "shares_diluted": 100, "tax_rate": 0.2})
        result = fq.analyse(data)
        self.assertEqual(self.codes(result), set(), result["flags"])

    def test_negative_incremental_margin(self):
        data = document()
        data["periods"][1].update(revenue=1200, operating_profit=180)
        result = fq.analyse(data)
        self.assertIn("negative_incremental_margin", self.codes(result))


class ExampleTests(unittest.TestCase):
    def test_msft_quality_example(self):
        root = Path(__file__).resolve().parents[1]
        data = json.loads((root / "examples/msft-quality/statements.json").read_text(encoding="utf-8"))
        self.assertEqual(fq.validate_document(data), [])
        result = fq.analyse(data)
        latest = result["periods"][-1]["metrics"]
        self.assertAlmostEqual(latest["gross_margin"], 0.6882, places=4)
        self.assertAlmostEqual(latest["operating_margin"], 0.4562, places=4)
        self.assertAlmostEqual(latest["cash_conversion"], 136162 / 101832, places=9)
        self.assertAlmostEqual(latest["capex_to_da"], 64551 / 34153, places=9)
        self.assertEqual(result["flags"], [])
        self.assertIn("revenue", result["unattributed"]["FY2025"])
        for name in ("dso", "dio", "dpo", "roic", "accrual_ratio", "invested_capital"):
            self.assertIsNone(latest[name], name)


class CliTests(unittest.TestCase):
    def run_cli(self, payload, name="statements.json"):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp).resolve() / name
            path.write_text(json.dumps(payload) if not isinstance(payload, str) else payload, encoding="utf-8")
            process = subprocess.run([sys.executable, str(SCRIPTS / "financial_quality.py"), str(path)],
                                     capture_output=True, text=True)
            return process

    def test_valid_cli(self):
        process = self.run_cli(document())
        self.assertEqual(process.returncode, 0, process.stdout)
        payload = json.loads(process.stdout)
        self.assertTrue(payload["passed"])
        self.assertEqual(len(payload["periods"]), 2)
        self.assertTrue(payload["flags"])

    def test_invalid_cli(self):
        process = self.run_cli(document(periods=[]))
        self.assertEqual(process.returncode, 1)
        payload = json.loads(process.stdout)
        self.assertFalse(payload["passed"])
        self.assertTrue(payload["errors"])

    def test_unreadable_cli(self):
        process = self.run_cli("{", name="broken.json")
        self.assertEqual(process.returncode, 2)

    def test_out_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            source = root / "statements.json"
            source.write_text(json.dumps(document()), encoding="utf-8")
            target = root / "quality.json"
            process = subprocess.run([sys.executable, str(SCRIPTS / "financial_quality.py"), str(source), "--out", str(target)],
                                     capture_output=True, text=True)
            self.assertEqual(process.returncode, 0, process.stdout)
            self.assertTrue(target.exists())
            self.assertTrue(json.loads(target.read_text(encoding="utf-8"))["passed"])


if __name__ == "__main__":
    unittest.main()
