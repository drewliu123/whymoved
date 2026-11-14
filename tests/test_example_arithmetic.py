"""Recompute P/E tables from their own price and EPS columns."""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def number(value):
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        text = value.strip().replace(",", "").replace("%", "").replace("x", "")
        try:
            return float(text)
        except ValueError:
            return None
    return None


class ExampleArithmeticTests(unittest.TestCase):
    def test_pe_tables_recompute(self):
        checked = 0
        for report_path in sorted((ROOT / "examples").glob("*/research/work/report.json")):
            report = json.loads(report_path.read_text(encoding="utf-8"))
            for table in report.get("tables", []):
                columns = table.get("columns", [])
                if not {"收盘价", "EPS", "P/E"}.issubset(set(columns)):
                    continue
                price_index = columns.index("收盘价")
                eps_index = columns.index("EPS")
                pe_index = columns.index("P/E")
                for row in table.get("rows", []):
                    price = number(row[price_index]) if len(row) > price_index else None
                    eps = number(row[eps_index]) if len(row) > eps_index else None
                    pe = number(row[pe_index]) if len(row) > pe_index else None
                    if not price or not eps or not pe:
                        continue
                    expected = price / eps
                    tolerance = max(1.0, expected * 0.05)
                    self.assertLessEqual(abs(expected - pe), tolerance,
                                         "%s %s P/E %.1f but price/EPS is %.1f" % (report_path.parents[2].name, row[0], pe, expected))
                    checked += 1
        self.assertGreaterEqual(checked, 20, "expected to check the valuation tables")


if __name__ == "__main__":
    unittest.main()
