"""Assemble financial-quality statements from claim.metric blocks."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import financial_quality
import quality_inputs

AS_OF = "2026-11-14T00:00:00Z"


def mclaim(cid, name, value, start, end, entity="EXAMPLE", period_type="fy", **metric):
    block = {"name": name, "value": value, "unit": "USD million", "period_type": period_type,
             "period_start": start, "period_end": end, "entity": entity,
             "currency": "USD", "scale": "million", "scope": "consolidated"}
    block.update(metric)
    return {"id": cid, "text": "fictional metric", "type": "fact", "as_of": AS_OF,
            "sources": [{"source_id": "S1"}], "metric": block}


def ledger(*claims):
    return {"claims": list(claims)}


def fiscal_year(year, values):
    start, end = "%d-01-01" % year, "%d-12-31" % year
    claims = []
    for index, (name, value) in enumerate(values.items(), start=1):
        claims.append(mclaim("C%s%d" % (year, index), name, value, start, end))
    return claims


class AssembleTests(unittest.TestCase):
    def two_periods(self, **overrides):
        claims = fiscal_year(2024, {"revenue": 1000, "gross_profit": 500, "operating_profit": 200,
                                    "net_income": 150, "cfo": 180, "capex": 60,
                                    "depreciation_amortization": 80, "shares_diluted": 100})
        claims += fiscal_year(2025, {"revenue": 1100, "gross_profit": 550, "operating_profit": 220,
                                     "net_income": 165, "cfo": 200, "capex": 70,
                                     "depreciation_amortization": 90, "shares_diluted": 102})
        return claims

    def test_assemble_and_feed_the_quality_screener(self):
        statements, error = quality_inputs.assemble(self.two_periods())
        self.assertIsNone(error)
        self.assertEqual(statements["entity"], "EXAMPLE")
        self.assertEqual(statements["currency"], "USD")
        self.assertEqual(statements["scale"], "million")
        self.assertEqual([period["period_end"] for period in statements["periods"]],
                         ["2024-12-31", "2025-12-31"])
        latest = statements["periods"][-1]
        self.assertEqual(latest["id"], "FY@2025-12-31")
        self.assertEqual(latest["revenue"]["value"], 1100)
        self.assertEqual(len(latest["revenue"]["claim_ids"]), 1)
        self.assertEqual(financial_quality.validate_document(statements), [])
        result = financial_quality.analyse(statements)
        self.assertAlmostEqual(result["periods"][-1]["metrics"]["gross_margin"], 0.5)

    def test_aliases_and_ratio_conversion(self):
        claims = fiscal_year(2024, {"营业收入": 100})
        claims.append(mclaim("T2024", "有效税率", 21, "2024-01-01", "2024-12-31",
                             unit="percent", currency="USD", scale="million"))
        claims += fiscal_year(2025, {"revenue": 120})
        statements, _ = quality_inputs.assemble(claims)
        self.assertEqual(statements["periods"][0]["revenue"]["value"], 100)
        self.assertAlmostEqual(statements["periods"][0]["tax_rate"]["value"], 0.21)

    def test_ignored_rows_are_reported(self):
        claims = self.two_periods()
        claims += [
            mclaim("X1", "mystery", 1, "2024-01-01", "2024-12-31"),
            mclaim("X2", "revenue", 1, "2024-01-01", "2024-12-31", period_type="instant"),
            mclaim("X3", "revenue", 1, None, "2024-12-31"),
            mclaim("X4", "revenue", 1, "2024-01-01", "2024-12-31", scope="segment:cloud"),
            mclaim("X5", "revenue", 1, "2024-01-01", "2024-12-31", entity="OTHER"),
            mclaim("X6", "revenue", 2, "2025-01-01", "2025-12-31", entity="OTHER"),
        ]
        statements, _ = quality_inputs.assemble(claims, entity="EXAMPLE")
        reasons = [row["reason"] for row in statements["ignored"]]
        self.assertTrue(any("not a statement field" in reason for reason in reasons))
        self.assertTrue(any("period_type" in reason for reason in reasons))
        self.assertTrue(any("period_start" in reason for reason in reasons))
        self.assertTrue(any("consolidated scope" in reason for reason in reasons))
        self.assertTrue(any("entity does not match" in reason for reason in reasons))
        selected, _ = quality_inputs.assemble(claims, entity="OTHER")
        self.assertEqual(len(selected["periods"]), 2)

    def test_conflicts_are_rejected(self):
        claims = self.two_periods()
        claims.append(mclaim("Z1", "revenue", 999, "2025-01-01", "2025-12-31"))
        with self.assertRaisesRegex(ValueError, "conflicting values"):
            quality_inputs.assemble(claims)

    def test_duplicate_identical_values_merge_claim_ids(self):
        claims = self.two_periods()
        claims.append(mclaim("Z2", "revenue", 1100, "2025-01-01", "2025-12-31"))
        statements, _ = quality_inputs.assemble(claims)
        self.assertIn("Z2", statements["periods"][-1]["revenue"]["claim_ids"])

    def test_structural_failures(self):
        with self.assertRaisesRegex(ValueError, "no usable"):
            quality_inputs.assemble(ledger())
        single = fiscal_year(2024, {"revenue": 100})
        with self.assertRaisesRegex(ValueError, "two comparable periods"):
            quality_inputs.assemble(single)
        mixed = self.two_periods() + [mclaim("K1", "revenue", 1, "2026-01-01", "2026-12-31", entity="OTHER")]
        with self.assertRaisesRegex(ValueError, "multiple entities"):
            quality_inputs.assemble(mixed)

    def test_currency_and_scale_must_be_resolvable(self):
        claims = self.two_periods()
        for claim in claims:
            claim["metric"].pop("currency", None)
        with self.assertRaisesRegex(ValueError, "currency and scale"):
            quality_inputs.assemble(claims)
        statements, _ = quality_inputs.assemble(claims, currency="USD", scale="million")
        self.assertEqual(statements["currency"], "USD")


class TaxAliasTests(unittest.TestCase):
    def test_pretax_income_and_income_tax_are_mapped(self):
        rows = []
        for index, (period_start, period_end) in enumerate((("2023-07-01", "2024-06-30"),
                                                            ("2024-07-01", "2025-06-30"))):
            for name, value in (("revenue", 1000 + index), ("pretax_income", 260 + index), ("income_tax", 10 + index)):
                rows.append({"id": "C%d" % len(rows), "text": name, "type": "fact", "as_of": "2026-11-14",
                             "sources": [{"source_id": "S1"}],
                             "metric": {"name": name, "value": value, "unit": "USD million", "period_type": "fy",
                                        "period_start": period_start, "period_end": period_end, "entity": "X",
                                        "scope": "consolidated", "currency": "USD", "scale": "million", "basis": "gaap"}})
        result, _ = quality_inputs.assemble(rows)
        period = result["periods"][-1]
        self.assertEqual(period["pretax_income"]["value"], 261)
        self.assertEqual(period["income_tax"]["value"], 11)
        self.assertEqual(period["income_tax"]["claim_ids"], ["C5"])


class CliTests(unittest.TestCase):
    def run_cli(self, payload, *extra):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp).resolve() / "claims.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            return subprocess.run([sys.executable, str(SCRIPTS / "quality_inputs.py"), str(path), *extra],
                                  capture_output=True, text=True)

    def test_cli_writes_statements(self):
        parallel = AssembleTests().two_periods()
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp).resolve() / "claims.json"
            source.write_text(json.dumps(ledger(*parallel)), encoding="utf-8")
            target = Path(tmp).resolve() / "statements.json"
            process = subprocess.run([sys.executable, str(SCRIPTS / "quality_inputs.py"), str(source),
                                      "--out", str(target)], capture_output=True, text=True)
            self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
            payload = json.loads(process.stdout)
            self.assertTrue(payload["passed"])
            statements = json.loads(target.read_text(encoding="utf-8"))
            self.assertEqual(financial_quality.validate_document(statements), [])
            process = subprocess.run([sys.executable, str(SCRIPTS / "financial_quality.py"), str(target)],
                                     capture_output=True, text=True)
            self.assertEqual(process.returncode, 0, process.stdout + process.stderr)

    def test_cli_failures(self):
        self.assertEqual(self.run_cli(ledger()).returncode, 1)
        with tempfile.TemporaryDirectory() as tmp:
            broken = Path(tmp) / "broken.json"
            broken.write_text("{", encoding="utf-8")
            process = subprocess.run([sys.executable, str(SCRIPTS / "quality_inputs.py"), str(broken)],
                                     capture_output=True, text=True)
            self.assertEqual(process.returncode, 2)


if __name__ == "__main__":
    unittest.main()
