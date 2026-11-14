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


class ExampleCashFlowTests(unittest.TestCase):
    def test_pb_tables_recompute(self):
        checked = 0
        for report_path in sorted((ROOT / "examples").glob("*/research/work/report.json")):
            report = json.loads(report_path.read_text(encoding="utf-8"))
            for table in report.get("tables", []):
                columns = table.get("columns", [])
                if not {"收盘价", "普通股（百万）", "权益（十亿美元）", "P/B"}.issubset(set(columns)):
                    continue
                price_i = columns.index("收盘价")
                shares_i = columns.index("普通股（百万）")
                equity_i = columns.index("权益（十亿美元）")
                pb_i = columns.index("P/B")
                for row in table.get("rows", []):
                    price = number(row[price_i]) if len(row) > price_i else None
                    shares = number(row[shares_i]) if len(row) > shares_i else None
                    equity = number(row[equity_i]) if len(row) > equity_i else None
                    pb = number(row[pb_i]) if len(row) > pb_i else None
                    if not price or not shares or not equity or not pb:
                        continue
                    expected = (price * shares / 1000) / equity
                    self.assertLessEqual(abs(expected - pb), max(0.02, expected * 0.03),
                                         "%s %s P/B %.2f but computed %.2f" % (report_path.parents[2].name, row[0], pb, expected))
                    checked += 1
        self.assertGreater(checked, 5, "expected to check JPM's P/B history")

    def test_fcf_tables_recompute(self):
        checked = 0
        for report_path in sorted((ROOT / "examples").glob("*/research/work/report.json")):
            report = json.loads(report_path.read_text(encoding="utf-8"))
            for table in report.get("tables", []):
                columns = table.get("columns", [])
                if not columns or columns[0] != "指标":
                    continue
                rows = {str(row[0]): row for row in table.get("rows", []) if row}
                cfo = rows.get("经营现金流")
                capex = rows.get("资本开支") or rows.get("现金资本开支")
                fcf = rows.get("自由现金流")
                if not (cfo and capex and fcf):
                    continue
                for index in range(1, len(columns)):
                    cfo_v = number(cfo[index]) if len(cfo) > index else None
                    capex_v = number(capex[index]) if len(capex) > index else None
                    fcf_v = number(fcf[index]) if len(fcf) > index else None
                    if cfo_v is None or capex_v is None or fcf_v is None:
                        continue
                    self.assertLessEqual(abs((cfo_v - capex_v) - fcf_v), max(0.05, abs(fcf_v) * 0.01),
                                         "%s %s FCF %.3f but CFO-capex is %.3f" % (report_path.parents[2].name, columns[index], fcf_v, cfo_v - capex_v))
                    checked += 1
        self.assertGreaterEqual(checked, 8, "expected to check the cash-flow tables")


if __name__ == "__main__":
    unittest.main()
