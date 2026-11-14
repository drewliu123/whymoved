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


class ExampleRatioTests(unittest.TestCase):
    PERCENT_RULES = [
        ("净利率", "净利润", "收入", 100.0),
        ("研发费用率", "研发费用", "收入", 100.0),
        ("毛利率", "毛利", "收入", 100.0),
        ("营业利润率", "营业利润", "收入", 100.0),
        ("capex/收入", "资本开支", "收入", 100.0),
        ("资本开支/收入", "资本开支", "收入", 100.0),
        ("分配/CFO", "分红+回购", "经营现金流", 100.0),
        ("NII/总资产", "净利息收入", "总资产", 100.0),
        ("ROE", "净利润", "股东权益", 100.0),
        ("ROE", "净利润", "权益", 100.0),
    ]
    RATIO_RULES = [
        ("CFO/净利润", "经营现金流", "净利润"),
        ("FCF/分配", "自由现金流", "分红+回购"),
    ]
    DAY_RULES = [
        ("DSO", "应收", "收入", 365.0),
        ("应收天数", "应收", "收入", 365.0),
        ("存货天数", "存货", "营业成本", 365.0),
        ("DIO", "存货", "营业成本", 365.0),
        ("应付天数", "应付", "营业成本", 365.0),
        ("DPO", "应付", "营业成本", 365.0),
    ]

    @staticmethod
    def normalize(label):
        import re
        return re.sub(r"（.*?）|\(.*?\)", "", str(label)).strip()

    def test_ratio_rows_recompute(self):
        checked = 0
        for report_path in sorted((ROOT / "examples").glob("*/research/work/report.json")):
            report = json.loads(report_path.read_text(encoding="utf-8"))
            for table in report.get("tables", []):
                columns = table.get("columns", [])
                if not columns or columns[0] != "指标":
                    continue
                rows = {self.normalize(row[0]): row for row in table.get("rows", []) if row}
                for index in range(1, len(columns)):
                    for out_label, numerator, denominator, factor in self.PERCENT_RULES:
                        checked += self.check(rows, out_label, numerator, denominator, factor, index,
                                              report_path.parents[2].name, columns[index], "percent")
                    for out_label, numerator, denominator in self.RATIO_RULES:
                        checked += self.check(rows, out_label, numerator, denominator, 1.0, index,
                                              report_path.parents[2].name, columns[index], "ratio")
                    for out_label, numerator, denominator, factor in self.DAY_RULES:
                        checked += self.check(rows, out_label, numerator, denominator, factor, index,
                                              report_path.parents[2].name, columns[index], "days")
        self.assertGreaterEqual(checked, 15, "expected to check ratio rows")

    def check(self, rows, out_label, numerator, denominator, factor, index, name, column, kind):
        out_row = rows.get(out_label)
        num_row = rows.get(numerator)
        den_row = rows.get(denominator)
        if not (out_row and num_row and den_row):
            return 0
        if max(len(out_row), len(num_row), len(den_row)) <= index:
            return 0
        out = number(out_row[index])
        num = number(num_row[index])
        den = number(den_row[index])
        if out is None or num is None or den in (None, 0):
            return 0
        expected = num / den * factor
        if kind == "percent":
            tolerance = max(0.5, abs(expected) * 0.02)
        elif kind == "days":
            tolerance = max(1.5, abs(expected) * 0.02)
        else:
            tolerance = max(0.05, abs(expected) * 0.03)
        self.assertLessEqual(abs(expected - out), tolerance,
                             "%s %s %s %.2f but computed %.2f" % (name, column, out_label, out, expected))
        return 1


if __name__ == "__main__":
    unittest.main()


class ExampleChartConsistencyTests(unittest.TestCase):
    @staticmethod
    def key(label):
        text = str(label)
        if "当前" in text:
            return "current"
        digits = "".join(ch for ch in text if ch.isdigit())
        return digits[-4:] if len(digits) >= 4 else text

    def test_pe_charts_match_tables(self):
        checked = 0
        for report_path in sorted((ROOT / "examples").glob("*/research/work/report.json")):
            report = json.loads(report_path.read_text(encoding="utf-8"))
            for chart in report.get("charts", []):
                if "P/E" not in chart.get("title", ""):
                    continue
                table = next((item for item in report.get("tables", []) if "P/E" in item.get("columns", [])), None)
                if not table:
                    continue
                pe_index = table["columns"].index("P/E")
                table_values = {self.key(row[0]): number(row[pe_index]) for row in table["rows"] if len(row) > pe_index}
                for row in chart.get("rows", []):
                    value = number(row.get("value"))
                    expected = table_values.get(self.key(row.get("label")))
                    if value is None or expected is None:
                        continue
                    self.assertLessEqual(abs(value - expected), max(1.0, abs(expected) * 0.05),
                                         "%s chart %s P/E %.1f but table says %.1f" % (report_path.parents[2].name, row.get("label"), value, expected))
                    checked += 1
        self.assertGreaterEqual(checked, 20, "expected to match valuation charts to tables")

    def test_pb_charts_match_tables(self):
        checked = 0
        for report_path in sorted((ROOT / "examples").glob("*/research/work/report.json")):
            report = json.loads(report_path.read_text(encoding="utf-8"))
            for chart in report.get("charts", []):
                if "P/B" not in chart.get("title", ""):
                    continue
                table = next((item for item in report.get("tables", []) if "P/B" in item.get("columns", [])), None)
                if not table:
                    continue
                pb_index = table["columns"].index("P/B")
                table_values = {self.key(row[0]): number(row[pb_index]) for row in table["rows"] if len(row) > pb_index}
                for row in chart.get("rows", []):
                    value = number(row.get("value"))
                    expected = table_values.get(self.key(row.get("label")))
                    if value is None or expected is None:
                        continue
                    self.assertLessEqual(abs(value - expected), max(0.05, abs(expected) * 0.05),
                                         "%s chart %s P/B %.2f but table says %.2f" % (report_path.parents[2].name, row.get("label"), value, expected))
                    checked += 1
        self.assertGreater(checked, 5, "expected to match the JPM P/B chart to its table")


if __name__ == "__main__":
    unittest.main()


class ExampleSeriesConsistencyTests(unittest.TestCase):
    ALIASES = {
        "现金资本开支": ("资本开支", "现金资本开支"),
        "分红+回购": ("分红+回购", "分红与回购"),
        "自由现金流": ("自由现金流",),
        "经营现金流": ("经营现金流",),
        "净利润": ("净利润",),
        "收入": ("收入",),
        "毛利": ("毛利",),
    }

    @staticmethod
    def key(label):
        text = str(label)
        digits = "".join(ch for ch in text if ch.isdigit())
        return digits[-4:] if len(digits) >= 4 else text

    def test_chart_series_match_table_rows(self):
        checked = 0
        for report_path in sorted((ROOT / "examples").glob("*/research/work/report.json")):
            report = json.loads(report_path.read_text(encoding="utf-8"))
            tables = report.get("tables", [])
            for chart in report.get("charts", []):
                series_list = chart.get("series") or [{"name": chart.get("title", ""), "rows": chart.get("rows", [])}]
                for series in series_list:
                    name = str(series.get("name", ""))
                    candidates = self.ALIASES.get(name, (name,))
                    table = None
                    row = None
                    for candidate_table in tables:
                        columns = candidate_table.get("columns", [])
                        if not columns or columns[0] != "指标":
                            continue
                        mapping = {str(item[0]): item for item in candidate_table.get("rows", []) if item}
                        for candidate in candidates:
                            if candidate in mapping:
                                table = candidate_table
                                row = mapping[candidate]
                                break
                        if row:
                            break
                    if not row:
                        continue
                    year_columns = {self.key(column): index for index, column in enumerate(table["columns"]) if self.key(column).isdigit()}
                    for point in series.get("rows", []):
                        key = self.key(point.get("label"))
                        index = year_columns.get(key)
                        value = number(point.get("value"))
                        if index is None or value is None or len(row) <= index:
                            continue
                        expected = number(row[index])
                        if expected is None:
                            continue
                        self.assertLessEqual(abs(value - expected), max(0.05, abs(expected) * 0.02),
                                             "%s chart '%s' %s is %.2f but table says %.2f" % (report_path.parents[2].name, series.get("name"), point.get("label"), value, expected))
                        checked += 1
        self.assertGreaterEqual(checked, 15, "expected to match chart series to table rows")


if __name__ == "__main__":
    unittest.main()
