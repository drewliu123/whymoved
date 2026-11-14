"""Report v2 contract, literal rendering, reference and accessibility regressions.

Run: python3 -m unittest discover -s tests -p 'test_reports.py'
"""

import copy
import html
import json
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))
import render_report
from test_event_study import document as event_document, sample as event_sample

AS_OF = "2026-10-31T12:00:00Z"


def documents():
    source = {"id": "S1", "url": "https://example.com/official", "publisher": "Example Official", "tier": "T0",
              "published_at": "2026-10-30T12:00:00Z", "retrieved_at": AS_OF, "quote": "Revenue increased to 12.",
              "locator": "paragraph 1", "origin_id": "O1", "origin_basis": "Direct official publication",
              "supports": ["fact"], "evidence_kind": "document", "access_status": "ok",
              "selection": {"selected": True, "reason": "direct evidence", "relevance": "direct", "purpose": "reported revenue", "priority": "decisive"}}
    sources = {"schema_version": 2, "as_of": AS_OF, "historical": False, "candidates": [source], "source_status": {"official": {"status": "ok"}}}
    ledger = {"schema_version": 2, "as_of": AS_OF, "claims": [{"id": "C1", "text": "Revenue increased to 12.", "type": "fact", "as_of": AS_OF, "sources": [{"source_id": "S1"}], "basis": []}]}
    report = {"schema_version": 2, "title": "收入变化", "question": "收入发生了什么变化？", "type": "asset", "task": "财报观察", "as_of": AS_OF,
              "answer": {"text": "本期收入增加。", "claim_ids": ["C1"]},
              "findings": [{"title": "收入增加", "text": "披露收入为 12。", "claim_ids": ["C1"], "why_it_matters": "更新收入判断。",
                            "increment": {"kind": "new_fact", "baseline": "上一截点未披露", "detail": "补充本期披露值"}}],
              "alternatives": [], "watch": [{"signal": "下一次披露", "meaning": "验证趋势是否持续", "claim_ids": ["C1"]}],
              "limitations": [{"text": "只有单期数据", "material": True, "claim_ids": ["C1"]}],
              "tables": [{"title": "披露值", "columns": ["项目", "收入"], "rows": [["本期", 12]], "claim_ids": ["C1"], "note": "披露口径"}]}
    return report, ledger, sources


class BlockRenderTests(unittest.TestCase):
    def document(self):
        report, ledger, sources = documents()
        report["tables"] = [
            {"id": "T1", "title": "分部收入", "columns": ["分部", "收入"], "units": ["", "百万美元"],
             "rows": [["云", 120], ["设备", 80]], "claim_ids": ["C1"]},
            {"id": "T2", "title": "附注表", "columns": ["项目"], "rows": [["其他"]], "claim_ids": ["C1"]},
        ]
        report["findings"][0]["table_ids"] = ["T1"]
        return report, ledger, sources

    def test_validation_of_inline_tables_and_units(self):
        report, ledger, sources = self.document()
        self.assertEqual(render_report.validate_report(report, ledger, sources), [])
        cases = [
            lambda r: r["findings"][0].update(table_ids=["T404"]),
            lambda r: r["findings"][0].update(table_ids=[]),
            lambda r: r["findings"][0].update(table_ids=["T1", "T1"]),
            lambda r: r["findings"][0].update(table_ids=[1]),
            lambda r: r["tables"][0].update(id="1bad"),
            lambda r: r["tables"][1].update(id="T1"),
            lambda r: r["tables"][0].update(units=["百万美元"]),
            lambda r: r["tables"][0].update(units=[1, 2]),
            lambda r: r["tables"][0].update(id=None),
        ]
        for mutate in cases:
            report, ledger, sources = self.document()
            mutate(report)
            self.assertTrue(render_report.validate_report(report, ledger, sources), mutate)

    def test_inline_table_renders_once_and_units_in_headers(self):
        report, ledger, sources = self.document()
        for render in (render_report.render_markdown, render_report.render_html):
            text = render(report, ledger, sources).replace("\\", "")
            self.assertEqual(text.count("分部收入"), 1)
            self.assertIn("收入（百万美元）", text)
            self.assertIn("附注表", text)
            self.assertLess(text.index("为什么重要"), text.index("分部收入"))
            self.assertLess(text.index("分部收入"), text.index("附注表"))

    def test_unreferenced_tables_keep_previous_order_and_output(self):
        report, ledger, sources = documents()
        report["tables"][0]["units"] = ["", "百万美元"]
        markdown = render_report.render_markdown(report, ledger, sources)
        self.assertIn("收入（百万美元）", markdown)
        plain, ledger2, sources2 = documents()
        before = render_report.render_markdown(plain, ledger2, sources2)
        self.assertNotIn("（百万美元）", before)


class MultiSeriesChartTests(unittest.TestCase):
    def chart_document(self):
        report, ledger, sources = documents()
        report["chart"] = {
            "title": "收入与利润", "x_label": "期间", "y_label": "数值", "unit": "亿元",
            "claim_ids": ["C1"], "note": "同一口径",
            "series": [
                {"name": "收入", "rows": [{"label": "Q1", "value": 12}, {"label": "Q2", "value": 15}]},
                {"name": "利润", "rows": [{"label": "Q1", "value": 2}, {"label": "Q2", "value": 3}]},
            ]}
        return report, ledger, sources

    def test_validates_and_renders_both_formats(self):
        report, ledger, sources = self.chart_document()
        self.assertEqual(render_report.validate_report(report, ledger, sources), [])
        page = render_report.render_html(report, ledger, sources)
        self.assertEqual(page.count("<polyline"), 2)
        self.assertIn("收入", page)
        self.assertIn("利润", page)
        self.assertIn("2个序列", page)
        self.assertIn("系列：", page)
        self.assertEqual(page.count("<script"), 1, "no inline script is added")
        markdown = render_report.render_markdown(report, ledger, sources)
        self.assertIn("期间", markdown)
        self.assertIn("收入（亿元）", markdown)
        self.assertIn("利润（亿元）", markdown)
        self.assertIn("| Q1 | 12 | 2 |", markdown)
        self.assertIn("| Q2 | 15 | 3 |", markdown)

    def test_benchmark_excess_columns(self):
        report, ledger, sources = documents()
        prices = [{"date": "2024-01-30", "close": 100}, {"date": "2024-01-31", "close": 110},
                  {"date": "2024-02-01", "close": 121}]
        bench = [{"date": "2024-01-30", "close": 50}, {"date": "2024-01-31", "close": 50},
                 {"date": "2024-02-01", "close": 52}]
        report["event_study"] = {"schema_version": 1, "event": "虚构事件", "window": {"before": 1, "after": 1},
                                 "samples": [{"id": "E1", "date": "2024-01-31", "prices": prices,
                                              "benchmark_prices": bench},
                                             {"id": "E2", "date": "2024-01-31", "prices": prices,
                                              "benchmark_prices": bench}]}
        self.assertEqual(render_report.validate_report(report, ledger, sources), [])
        page = render_report.render_html(report, ledger, sources)
        for token in ("后窗超额", "全窗超额", "标的收益减基准收益"):
            self.assertIn(token, page)
        text = render_report.render_markdown(report, ledger, sources).replace("\\", "")
        self.assertIn("后窗超额", text)

    def test_negative_cases(self):
        cases = [
            lambda c: c.update(rows=[{"label": "Q1", "value": 1}]),
            lambda c: c.update(series=[]),
            lambda c: c["series"][0].pop("name"),
            lambda c: c["series"][1]["rows"][0].update(label="Q3"),
            lambda c: c["series"][0]["rows"][0].update(value=float("nan")),
            lambda c: c["series"][0].update(extra=1),
            lambda c: c["series"][0].update(rows=[{"label": "Q1", "value": 1}]),
        ]
        for mutate in cases:
            report, ledger, sources = self.chart_document()
            mutate(report["chart"])
            self.assertTrue(render_report.validate_report(report, ledger, sources), mutate)

    def test_single_series_chart_still_uses_interactive_renderer(self):
        report, ledger, sources = documents()
        report["chart"] = {"title": "收入序列", "x_label": "期间", "y_label": "收入", "unit": "亿元",
                           "rows": [{"label": "Q1", "value": 12}, {"label": "Q2", "value": 12}],
                           "claim_ids": ["C1"]}
        page = render_report.render_html(report, ledger, sources)
        for token in ('id="chart-crosshair"', 'r="14" fill="transparent"', "data-x=", 'aria-live="polite"'):
            self.assertIn(token, page)
        self.assertNotIn("系列：", page)


class ChartListTests(unittest.TestCase):
    def chart(self, title, series=False):
        if series:
            return {"title": title, "x_label": "期间", "y_label": "值", "unit": "亿元", "claim_ids": ["C1"],
                    "series": [{"name": "A", "rows": [{"label": "Q1", "value": 1}, {"label": "Q2", "value": 2}]},
                               {"name": "B", "rows": [{"label": "Q1", "value": 2}, {"label": "Q2", "value": 1}]}]}
        return {"title": title, "x_label": "期间", "y_label": "值", "unit": "亿元", "claim_ids": ["C1"],
                "rows": [{"label": "Q1", "value": 1}, {"label": "Q2", "value": 2}]}

    def document(self):
        report, ledger, sources = documents()
        report["charts"] = [self.chart("单序列"), self.chart("双序列", series=True)]
        return report, ledger, sources

    def test_validates_and_renders_each_chart(self):
        report, ledger, sources = self.document()
        self.assertEqual(render_report.validate_report(report, ledger, sources), [])
        page = render_report.render_html(report, ledger, sources)
        self.assertEqual(page.count('<section class="chart">'), 2)
        self.assertEqual(page.count("<polyline"), 3)
        self.assertLess(page.index("单序列"), page.index("双序列"))
        markdown = render_report.render_markdown(report, ledger, sources)
        self.assertLess(markdown.index("单序列"), markdown.index("双序列"))
        self.assertIn("| 期间 | 值（亿元） |", markdown)
        self.assertIn("| 期间 | A（亿元） | B（亿元） |", markdown)

    def test_benchmark_excess_columns(self):
        report, ledger, sources = documents()
        prices = [{"date": "2024-01-30", "close": 100}, {"date": "2024-01-31", "close": 110},
                  {"date": "2024-02-01", "close": 121}]
        bench = [{"date": "2024-01-30", "close": 50}, {"date": "2024-01-31", "close": 50},
                 {"date": "2024-02-01", "close": 52}]
        report["event_study"] = {"schema_version": 1, "event": "虚构事件", "window": {"before": 1, "after": 1},
                                 "samples": [{"id": "E1", "date": "2024-01-31", "prices": prices,
                                              "benchmark_prices": bench},
                                             {"id": "E2", "date": "2024-01-31", "prices": prices,
                                              "benchmark_prices": bench}]}
        self.assertEqual(render_report.validate_report(report, ledger, sources), [])
        page = render_report.render_html(report, ledger, sources)
        for token in ("后窗超额", "全窗超额", "标的收益减基准收益"):
            self.assertIn(token, page)
        text = render_report.render_markdown(report, ledger, sources).replace("\\", "")
        self.assertIn("后窗超额", text)

    def test_negative_cases(self):
        report, ledger, sources = self.document()
        report["chart"] = self.chart("重复")
        self.assertTrue(any("either chart or charts" in error
                            for error in render_report.validate_report(report, ledger, sources)))
        for patch in ({"charts": []}, {"charts": "nope"}, {"charts": [None]},
                      {"charts": [{"title": "x"}]}, {"charts": [self.chart("x", series=True)]}):
            report, ledger, sources = self.document()
            report.update(patch)
            if patch.get("charts") == [self.chart("x", series=True)]:
                report["charts"][0]["series"][1]["rows"][0]["label"] = "Q9"
            self.assertTrue(render_report.validate_report(report, ledger, sources), patch)

    def test_single_chart_reports_still_valid(self):
        report, ledger, sources = documents()
        report["chart"] = self.chart("唯一")
        self.assertEqual(render_report.validate_report(report, ledger, sources), [])
        page = render_report.render_html(report, ledger, sources)
        self.assertEqual(page.count('<section class="chart">'), 1)


class BarWaterfallTests(unittest.TestCase):
    def bar_document(self):
        report, ledger, sources = documents()
        report["chart"] = {"kind": "bar", "title": "分部收入", "x_label": "分部", "y_label": "收入",
                           "unit": "亿元", "claim_ids": ["C1"],
                           "rows": [{"label": "云", "value": 12}, {"label": "设备", "value": -3}]}
        return report, ledger, sources

    def waterfall_document(self, final=71.5):
        report, ledger, sources = documents()
        report["chart"] = {"kind": "waterfall", "title": "现金流桥", "x_label": "项目", "y_label": "金额",
                           "unit": "十亿美元", "claim_ids": ["C1"],
                           "rows": [{"label": "经营现金流", "value": 136, "role": "total"},
                                    {"label": "资本开支", "value": -64.5, "role": "delta"},
                                    {"label": "自由现金流", "value": final, "role": "total"}]}
        return report, ledger, sources

    def test_bar_chart(self):
        report, ledger, sources = self.bar_document()
        self.assertEqual(render_report.validate_report(report, ledger, sources), [])
        page = render_report.render_html(report, ledger, sources)
        self.assertEqual(page.count("<rect"), 2)
        self.assertNotIn("<polyline", page)
        for token in ("柱状", "云 12 亿元", "设备 -3 亿元", 'id="chart-readout"'):
            self.assertIn(token, page)
        markdown = render_report.render_markdown(report, ledger, sources)
        self.assertIn("| 分部 | 收入（亿元） |", markdown)
        self.assertIn("| 云 | 12 |", markdown)

    def test_waterfall_chart_and_self_check(self):
        report, ledger, sources = self.waterfall_document()
        self.assertEqual(render_report.validate_report(report, ledger, sources), [])
        page = render_report.render_html(report, ledger, sources)
        self.assertEqual(page.count("<rect"), 3)
        self.assertIn("瀑布", page)
        self.assertIn("经营现金流 136 十亿美元", page)
        markdown = render_report.render_markdown(report, ledger, sources)
        self.assertIn("经营现金流（合计）", markdown)
        self.assertIn("资本开支（变动）", markdown)
        self.assertIn("自由现金流（合计）", markdown)

    def test_waterfall_checkpoint_mismatch(self):
        report, ledger, sources = self.waterfall_document(final=72)
        errors = render_report.validate_report(report, ledger, sources)
        self.assertTrue(any("does not match the accumulated" in error for error in errors), errors)

    def test_kind_validation(self):
        report, ledger, sources = self.bar_document()
        report["chart"]["kind"] = "pie"
        self.assertTrue(any("kind must be" in error for error in render_report.validate_report(report, ledger, sources)))
        report, ledger, sources = self.waterfall_document()
        report["chart"]["series"] = [{"name": "A", "rows": [{"label": "Q1", "value": 1},
                                                            {"label": "Q2", "value": 2}]}]
        report["chart"].pop("rows")
        self.assertTrue(any("waterfall cannot use series" in error
                            for error in render_report.validate_report(report, ledger, sources)))
        report, ledger, sources = self.waterfall_document()
        report["chart"]["rows"][0].pop("role")
        self.assertTrue(any("role must be" in error for error in render_report.validate_report(report, ledger, sources)))
        report, ledger, sources = self.waterfall_document()
        report["chart"]["rows"] = [{"label": "变动", "value": 1, "role": "delta"},
                                   {"label": "合计", "value": 1, "role": "total"}]
        self.assertTrue(any("start with a total" in error for error in render_report.validate_report(report, ledger, sources)))

    def test_grouped_bar_chart(self):
        report, ledger, sources = documents()
        report["chart"] = {"kind": "bar", "title": "分部对比", "x_label": "分部", "y_label": "收入",
                           "unit": "亿元", "claim_ids": ["C1"],
                           "series": [
                               {"name": "FY2024", "rows": [{"label": "云", "value": 10}, {"label": "设备", "value": 4}]},
                               {"name": "FY2025", "rows": [{"label": "云", "value": 12}, {"label": "设备", "value": 3}]}]}
        self.assertEqual(render_report.validate_report(report, ledger, sources), [])
        page = render_report.render_html(report, ledger, sources)
        self.assertEqual(page.count("<rect"), 4)
        self.assertNotIn("<polyline", page)
        for token in ("分组柱状", "FY2024 · 云 10 亿元", "FY2025 · 云 12 亿元", "系列顺序", "同源数据表"):
            self.assertIn(token, page)
        markdown = render_report.render_markdown(report, ledger, sources)
        self.assertIn("| 分部 | FY2024（亿元） | FY2025（亿元） |", markdown)
        self.assertIn("| 云 | 10 | 12 |", markdown)

    def test_stacked_bar_chart(self):
        report, ledger, sources = documents()
        report["chart"] = {"kind": "bar", "bar_mode": "stacked", "title": "收入结构", "x_label": "期间",
                           "y_label": "收入", "unit": "亿元", "claim_ids": ["C1"],
                           "series": [
                               {"name": "云", "rows": [{"label": "FY2024", "value": 6}, {"label": "FY2025", "value": 8}]},
                               {"name": "设备", "rows": [{"label": "FY2024", "value": 4}, {"label": "FY2025", "value": 3}]}]}
        self.assertEqual(render_report.validate_report(report, ledger, sources), [])
        page = render_report.render_html(report, ledger, sources)
        self.assertEqual(page.count("<rect"), 4)
        for token in ("堆叠柱状", "堆叠顺序（自下而上）", "云 · FY2025 8 亿元", "设备 · FY2025 3 亿元"):
            self.assertIn(token, page)
        markdown = render_report.render_markdown(report, ledger, sources)
        self.assertIn("| 期间 | 云（亿元） | 设备（亿元） |", markdown)
        self.assertIn("| FY2025 | 8 | 3 |", markdown)

    def test_stacked_bar_validation(self):
        report, ledger, sources = self.bar_document()
        report["chart"]["bar_mode"] = "stacked"
        self.assertTrue(any("requires series" in error for error in render_report.validate_report(report, ledger, sources)))
        report, ledger, sources = self.bar_document()
        report["chart"]["bar_mode"] = "stacked"
        report["chart"].pop("rows")
        report["chart"]["series"] = [
            {"name": "A", "rows": [{"label": "Q1", "value": 2}, {"label": "Q2", "value": -1}]},
            {"name": "B", "rows": [{"label": "Q1", "value": 1}, {"label": "Q2", "value": 3}]}]
        self.assertTrue(any("negative" in error for error in render_report.validate_report(report, ledger, sources)))
        report, ledger, sources = documents()
        report["chart"] = {"title": "折线", "x_label": "x", "y_label": "y", "unit": "元",
                           "rows": [{"label": "A", "value": 1}, {"label": "B", "value": 2}],
                           "claim_ids": ["C1"], "bar_mode": "stacked"}
        self.assertTrue(any("only valid for bar" in error for error in render_report.validate_report(report, ledger, sources)))

    def test_line_charts_unchanged(self):
        report, ledger, sources = documents()
        report["chart"] = {"title": "收入", "x_label": "期间", "y_label": "收入", "unit": "亿元",
                           "rows": [{"label": "Q1", "value": 1}, {"label": "Q2", "value": 2}],
                           "claim_ids": ["C1"]}
        page = render_report.render_html(report, ledger, sources)
        self.assertIn("<polyline", page)
        self.assertNotIn("<rect", page)
        self.assertNotIn("柱状", page)


class TransmissionReportTests(unittest.TestCase):
    def document(self):
        report, ledger, sources = documents()
        report["transmission"] = {
            "schema_version": 1, "theme": "测试传导", "as_of": AS_OF,
            "nodes": [{"id": "A", "label": "需求", "kind": "demand",
                       "observables": ["新签订单"], "claim_ids": ["C1"]},
                      {"id": "B", "label": "瓶颈", "kind": "capacity",
                       "observables": ["排队时长"], "claim_ids": ["C1"]}],
            "edges": [{"from": "A", "to": "B", "mechanism": "排队", "lag": "1个季度", "claim_ids": ["C1"]}],
            "bottleneck": {"node": "B", "reason": "审批节奏", "claim_ids": ["C1"]}}
        return report, ledger, sources

    def test_validates_and_renders_appendix(self):
        report, ledger, sources = self.document()
        self.assertEqual(render_report.validate_report(report, ledger, sources), [])
        for render in (render_report.render_markdown, render_report.render_html):
            text = render(report, ledger, sources).replace("\\", "")
            for word in ("行业传导", "瓶颈", "审批节奏", "传导节点", "瓶颈上游", "需求", "排队时长",
                         "传导路径", "A", "B"):
                self.assertIn(word, text)

    def test_negative_transmission(self):
        report, ledger, sources = self.document()
        report["transmission"]["nodes"][0]["claim_ids"] = ["C404"]
        errors = render_report.validate_report(report, ledger, sources)
        self.assertTrue(any("transmission:" in error for error in errors), errors)
        report, ledger, sources = self.document()
        report["transmission"]["edges"][0]["to"] = "NOPE"
        self.assertTrue(any("transmission:" in error for error in render_report.validate_report(report, ledger, sources)))
        report, ledger, sources = documents()
        report["transmission"] = "nope"
        self.assertTrue(any("transmission:" in error for error in render_report.validate_report(report, ledger, sources)))

    def test_reports_without_transmission_unchanged(self):
        report, ledger, sources = documents()
        self.assertNotIn("行业传导", render_report.render_markdown(report, ledger, sources))


class QualityReportTests(unittest.TestCase):
    def statements(self):
        def period(identifier, start, end, values):
            data = {"id": identifier, "period_type": "fy", "period_start": start, "period_end": end}
            for name, value in values.items():
                data[name] = {"value": value, "claim_ids": ["C1"]}
            return data
        return {"schema_version": 1, "entity": "EXAMPLE", "currency": "USD", "scale": "million",
                "as_of": AS_OF,
                "periods": [
                    period("FY2024", "2024-01-01", "2024-12-31",
                           {"revenue": 1000, "gross_profit": 500, "operating_profit": 200, "net_income": 150,
                            "cfo": 180, "capex": 60, "depreciation_amortization": 80,
                            "receivables": 120, "inventory": 80, "payables": 60, "total_assets": 900,
                            "equity": 500, "debt": 200, "cash": 100, "share_based_comp": 40,
                            "shares_diluted": 100, "tax_rate": 0.2}),
                    period("FY2025", "2025-01-01", "2025-12-31",
                           {"revenue": 1200, "gross_profit": 570, "operating_profit": 210, "net_income": 120,
                            "cfo": 100, "capex": 50, "depreciation_amortization": 90,
                            "receivables": 210, "inventory": 130, "payables": 65, "total_assets": 1100,
                            "equity": 520, "debt": 260, "cash": 90, "share_based_comp": 90,
                            "shares_diluted": 104, "tax_rate": 0.2})]}

    def document(self):
        report, ledger, sources = documents()
        report["quality"] = {"statements": self.statements()}
        return report, ledger, sources

    def test_validates_and_renders(self):
        report, ledger, sources = self.document()
        self.assertEqual(render_report.validate_report(report, ledger, sources), [])
        for render in (render_report.render_markdown, render_report.render_html):
            text = render(report, ledger, sources).replace("\\", "")
            for word in ("盈利质量", "关键指标", "毛利率", "现金转化", "ROIC", "环比变化", "增量利润率",
                         "红旗", "growth_without_cash", "确定性计算"):
                self.assertIn(word, text)
        markdown = render_report.render_markdown(report, ledger, sources).replace("\\", "")
        self.assertIn("0.475", markdown)
        self.assertIn("0.2", markdown)

    def test_thresholds_override(self):
        report, ledger, sources = self.document()
        report["quality"]["thresholds"] = {"sbc_ratio": 0.05, "margin_drop": 1.0}
        self.assertEqual(render_report.validate_report(report, ledger, sources), [])
        text = render_report.render_markdown(report, ledger, sources).replace("\\", "")
        self.assertIn("high_sbc", text)
        self.assertNotIn("gross_margin_pressure", text)

    def test_benchmark_excess_columns(self):
        report, ledger, sources = documents()
        prices = [{"date": "2024-01-30", "close": 100}, {"date": "2024-01-31", "close": 110},
                  {"date": "2024-02-01", "close": 121}]
        bench = [{"date": "2024-01-30", "close": 50}, {"date": "2024-01-31", "close": 50},
                 {"date": "2024-02-01", "close": 52}]
        report["event_study"] = {"schema_version": 1, "event": "虚构事件", "window": {"before": 1, "after": 1},
                                 "samples": [{"id": "E1", "date": "2024-01-31", "prices": prices,
                                              "benchmark_prices": bench},
                                             {"id": "E2", "date": "2024-01-31", "prices": prices,
                                              "benchmark_prices": bench}]}
        self.assertEqual(render_report.validate_report(report, ledger, sources), [])
        page = render_report.render_html(report, ledger, sources)
        for token in ("后窗超额", "全窗超额", "标的收益减基准收益"):
            self.assertIn(token, page)
        text = render_report.render_markdown(report, ledger, sources).replace("\\", "")
        self.assertIn("后窗超额", text)

    def test_negative_cases(self):
        report, ledger, sources = self.document()
        report["quality"] = "nope"
        self.assertTrue(any("quality must be" in error for error in render_report.validate_report(report, ledger, sources)))
        report, ledger, sources = self.document()
        report["quality"] = {"statements": {}}
        self.assertTrue(any("quality.statements:" in error for error in render_report.validate_report(report, ledger, sources)))
        report, ledger, sources = self.document()
        report["quality"]["thresholds"] = {"unknown": 0.1}
        self.assertTrue(any("not a known threshold" in error for error in render_report.validate_report(report, ledger, sources)))
        report, ledger, sources = self.document()
        report["quality"]["thresholds"] = {"sbc_ratio": 2}
        self.assertTrue(any("in (0, 1]" in error for error in render_report.validate_report(report, ledger, sources)))
        report, ledger, sources = self.document()
        report["quality"]["statements"]["periods"][0]["revenue"]["claim_ids"] = ["C404"]
        self.assertTrue(any("unknown claims" in error for error in render_report.validate_report(report, ledger, sources)))
        report, ledger, sources = self.document()
        report["quality"]["extra"] = 1
        self.assertTrue(any("unknown fields" in error for error in render_report.validate_report(report, ledger, sources)))

    def test_unattributed_fields_are_listed(self):
        report, ledger, sources = self.document()
        report["quality"]["statements"]["periods"][1]["capex"] = 50
        self.assertEqual(render_report.validate_report(report, ledger, sources), [])
        text = render_report.render_markdown(report, ledger, sources).replace("\\", "")
        self.assertIn("未挂 claim 的字段", text)
        self.assertIn("FY2025", text)
        self.assertIn("capex", text)

    def test_reports_without_quality_unchanged(self):
        report, ledger, sources = documents()
        self.assertNotIn("盈利质量", render_report.render_markdown(report, ledger, sources))


class EventStudyReportTests(unittest.TestCase):
    def test_layout_is_optional_and_known(self):
        report, ledger, sources = documents()
        report["layout"] = "brief"
        self.assertEqual(render_report.validate_report(report, ledger, sources), [])
        report["layout"] = "compact"
        self.assertTrue(any("layout must be classic or brief" in error
                            for error in render_report.validate_report(report, ledger, sources)))

    def test_scenarios_section(self):
        report, ledger, sources = documents()
        report["scenarios"] = [
            {"name": "情景甲", "thesis": "如果 A 发生", "triggers": ["指标一", "指标二"], "implication": "则判断下调"},
            {"name": "情景乙", "thesis": "如果 B 发生", "triggers": ["指标三"], "implication": "则判断维持"}]
        self.assertEqual(render_report.validate_report(report, ledger, sources), [])
        html = render_report.render_html(report, ledger, sources)
        for token in ("情景与触发条件", "情景甲", "触发：指标一；指标二", "则判断下调"):
            self.assertIn(token, html)
        bad = documents()
        bad[0]["scenarios"] = [{"name": "x", "thesis": "y", "triggers": [], "implication": "z"}]
        self.assertTrue(any("triggers must be" in error for error in render_report.validate_report(*bad)))

    def test_executive_summary(self):
        report, ledger, sources = documents()
        report["summary"] = {"conclusion": "结论一句", "surprise": "反直觉一句", "next_check": "验证一句"}
        self.assertEqual(render_report.validate_report(report, ledger, sources), [])
        html = render_report.render_html(report, ledger, sources)
        self.assertIn("执行摘要", html)
        self.assertIn("最反直觉：反直觉一句", html)
        self.assertLess(html.index("执行摘要"), html.index("<h2>判断</h2>"))
        bad = documents()
        bad[0]["summary"] = {"conclusion": "x", "surprise": "y"}
        self.assertTrue(any("summary must contain exactly" in error
                            for error in render_report.validate_report(*bad)))

    def test_implications_section(self):
        report, ledger, sources = documents()
        report["implications"] = [
            {"title": "这对判断意味着什么", "text": "资本开支不是均匀的行业 beta。", "claim_ids": ["C1"]},
            {"title": "下一步看什么", "text": "看订单与验收节奏。", "horizon": "未来 2-4 个季度"}]
        self.assertEqual(render_report.validate_report(report, ledger, sources), [])
        html = render_report.render_html(report, ledger, sources)
        for token in ("这意味着什么", "这对判断意味着什么", "未来 2-4 个季度"):
            self.assertIn(token, html)
        markdown = render_report.render_markdown(report, ledger, sources).replace("\\", "")
        self.assertIn("这意味着什么", markdown)
        bad = documents()
        bad[0]["implications"] = [{"title": "x", "text": "", "claim_ids": ["C1"]}]
        self.assertTrue(any(".text must be nonempty" in error
                            for error in render_report.validate_report(*bad)))

    def test_beta_adjusted_footnote(self):
        report, ledger, sources = documents()
        prices = [{"date": "2024-01-30", "close": 100}, {"date": "2024-01-31", "close": 110},
                  {"date": "2024-02-01", "close": 121}]
        bench = [{"date": "2024-01-30", "close": 50}, {"date": "2024-01-31", "close": 50},
                 {"date": "2024-02-01", "close": 55}]
        report["event_study"] = {"schema_version": 1, "event": "虚构事件", "window": {"before": 1, "after": 1},
                                 "samples": [{"id": "E1", "date": "2024-01-31", "prices": prices,
                                              "benchmark_prices": bench, "benchmark_beta": 2},
                                             {"id": "E2", "date": "2024-01-31", "prices": prices,
                                              "benchmark_prices": bench, "benchmark_beta": 2}]}
        self.assertEqual(render_report.validate_report(report, ledger, sources), [])
        text = render_report.render_html(report, ledger, sources)
        self.assertIn("beta×基准", text)

    def test_returns_only_samples_render(self):
        report, ledger, sources = documents()
        report["event_study"] = {"schema_version": 1, "event": "虚构事件", "window": {"before": 2, "after": 2},
                                 "samples": [
                                     {"id": "E1", "date": "2025-05-03",
                                      "returns": {"pre": 0.2, "post": 0.2, "total": 0.44}},
                                     {"id": "E2", "date": "2025-06-03",
                                      "returns": {"pre": 0.0, "post": -0.01, "total": -0.01}}]}
        self.assertEqual(render_report.validate_report(report, ledger, sources), [])
        text = render_report.render_markdown(report, ledger, sources).replace("\\", "")
        self.assertIn("参考类收益分布", text)
        self.assertIn("9.50%", text)
        self.assertIn("E1", text)

    def test_returns_only_samples_render(self):
        report, ledger, sources = documents()
        report["event_study"] = {"schema_version": 1, "event": "虚构事件", "window": {"before": 2, "after": 2},
                                 "samples": [
                                     {"id": "E1", "date": "2025-05-03",
                                      "returns": {"pre": 0.2, "post": 0.2, "total": 0.44}},
                                     {"id": "E2", "date": "2025-06-03",
                                      "returns": {"pre": 0.0, "post": -0.01, "total": -0.01}}]}
        self.assertEqual(render_report.validate_report(report, ledger, sources), [])
        text = render_report.render_markdown(report, ledger, sources).replace("\\", "")
        self.assertIn("参考类收益分布", text)
        self.assertIn("9.50%", text)
        self.assertIn("E1", text)

    def test_returns_only_samples_render(self):
        report, ledger, sources = documents()
        report["event_study"] = {"schema_version": 1, "event": "虚构事件", "window": {"before": 2, "after": 2},
                                 "samples": [
                                     {"id": "E1", "date": "2025-05-03",
                                      "returns": {"pre": 0.2, "post": 0.2, "total": 0.44}},
                                     {"id": "E2", "date": "2025-06-03",
                                      "returns": {"pre": 0.0, "post": -0.01, "total": -0.01}}]}
        self.assertEqual(render_report.validate_report(report, ledger, sources), [])
        text = render_report.render_markdown(report, ledger, sources).replace("\\", "")
        self.assertIn("参考类收益分布", text)
        self.assertIn("9.50%", text)
        self.assertIn("E1", text)

    def test_returns_only_samples_render(self):
        report, ledger, sources = documents()
        report["event_study"] = {"schema_version": 1, "event": "虚构事件", "window": {"before": 2, "after": 2},
                                 "samples": [
                                     {"id": "E1", "date": "2025-05-03",
                                      "returns": {"pre": 0.2, "post": 0.2, "total": 0.44}},
                                     {"id": "E2", "date": "2025-06-03",
                                      "returns": {"pre": 0.0, "post": -0.01, "total": -0.01}}]}
        self.assertEqual(render_report.validate_report(report, ledger, sources), [])
        text = render_report.render_markdown(report, ledger, sources).replace("\\", "")
        self.assertIn("参考类收益分布", text)
        self.assertIn("9.50%", text)
        self.assertIn("E1", text)


    def test_named_benchmarks_render(self):
        report, ledger, sources = documents()
        prices = [{"date": "2024-01-30", "close": 100}, {"date": "2024-01-31", "close": 110},
                  {"date": "2024-02-01", "close": 121}]
        flat = [{"date": point["date"], "close": 50} for point in prices]
        report["event_study"] = {"schema_version": 1, "event": "虚构事件", "window": {"before": 1, "after": 1},
                                 "samples": [{"id": "E1", "date": "2024-01-31", "prices": prices,
                                              "benchmark_prices": {"FLAT": flat, "UP": flat}},
                                             {"id": "E2", "date": "2024-01-31", "prices": prices,
                                              "benchmark_prices": {"FLAT": flat, "UP": flat}}]}
        self.assertEqual(render_report.validate_report(report, ledger, sources), [])
        text = render_report.render_html(report, ledger, sources)
        self.assertIn("后窗超额·FLAT", text)
        self.assertIn("全窗超额·UP", text)
        self.assertIn("多基准时各基准的分布", text)

    def test_overlap_warnings_render(self):
        report, ledger, sources = documents()
        prices = [{"date": "2024-01-%02d" % day, "close": 100 + day} for day in range(1, 31)]
        report["event_study"] = {"schema_version": 1, "event": "虚构事件", "window": {"before": 1, "after": 1},
                                 "samples": [{"id": "E1", "date": "2024-01-10", "prices": prices},
                                             {"id": "E2", "date": "2024-01-11", "prices": prices}]}
        self.assertEqual(render_report.validate_report(report, ledger, sources), [])
        text = render_report.render_html(report, ledger, sources)
        self.assertIn("样本警告", text)
        self.assertIn("share observations", text)

    def document(self):
        report, ledger, sources = documents()
        report["event_study"] = event_document(
            [event_sample("E1", [100, 110, 120, 132, 144, 158], 2),
             event_sample("E2", [100, 100, 100, 90, 99, 108.9], 2)], before=2, after=2)
        return report, ledger, sources

    def test_validates_and_renders(self):
        report, ledger, sources = self.document()
        self.assertEqual(render_report.validate_report(report, ledger, sources), [])
        for render in (render_report.render_markdown, render_report.render_html):
            text = render(report, ledger, sources).replace("\\", "")
            for word in ("事件研究", "参考类收益分布", "样本明细", "E1", "E2", "后窗",
                         "绝对收益", "不给p值", "不是预测"):
                self.assertIn(word, text)
        markdown = render_report.render_markdown(report, ledger, sources).replace("\\", "")
        self.assertIn("9.50%", markdown)

    def test_benchmark_excess_columns(self):
        report, ledger, sources = documents()
        prices = [{"date": "2024-01-30", "close": 100}, {"date": "2024-01-31", "close": 110},
                  {"date": "2024-02-01", "close": 121}]
        bench = [{"date": "2024-01-30", "close": 50}, {"date": "2024-01-31", "close": 50},
                 {"date": "2024-02-01", "close": 52}]
        report["event_study"] = {"schema_version": 1, "event": "虚构事件", "window": {"before": 1, "after": 1},
                                 "samples": [{"id": "E1", "date": "2024-01-31", "prices": prices,
                                              "benchmark_prices": bench},
                                             {"id": "E2", "date": "2024-01-31", "prices": prices,
                                              "benchmark_prices": bench}]}
        self.assertEqual(render_report.validate_report(report, ledger, sources), [])
        page = render_report.render_html(report, ledger, sources)
        for token in ("后窗超额", "全窗超额", "标的收益减基准收益"):
            self.assertIn(token, page)
        text = render_report.render_markdown(report, ledger, sources).replace("\\", "")
        self.assertIn("后窗超额", text)

    def test_negative_cases(self):
        report, ledger, sources = self.document()
        report["event_study"]["window"]["after"] = 0
        self.assertTrue(any("event_study:" in error for error in render_report.validate_report(report, ledger, sources)))
        report, ledger, sources = self.document()
        report["event_study"]["samples"][0]["claim_ids"] = ["C404"]
        self.assertTrue(any("unknown claims" in error for error in render_report.validate_report(report, ledger, sources)))
        report, ledger, sources = self.document()
        report["event_study"] = "nope"
        self.assertTrue(any("event_study:" in error for error in render_report.validate_report(report, ledger, sources)))
        report, ledger, sources = self.document()
        report["event_study"]["samples"] = [report["event_study"]["samples"][0],
                                            event_sample("E3", [100, 110, 120], 0)]
        self.assertTrue(any("fewer than two usable" in error
                            for error in render_report.validate_report(report, ledger, sources)))

    def test_reports_without_event_study_unchanged(self):
        report, ledger, sources = documents()
        self.assertNotIn("事件研究", render_report.render_markdown(report, ledger, sources))


class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text, self.tags, self.hrefs = [], [], []
    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))
        self.hrefs.extend(v for k, v in attrs if k == "href")
    def handle_data(self, data):
        self.text.append(data)


class ReportsTest(unittest.TestCase):
    def test_valid_document_and_shared_content(self):
        report, ledger, sources = documents()
        self.assertEqual(render_report.validate_report(report, ledger, sources), [])
        page = render_report.render_html(report, ledger, sources)
        markdown = render_report.render_markdown(report, ledger, sources)
        parser = Text(); parser.feed(page)
        text = "".join(parser.text)
        for value in (report["answer"]["text"], report["findings"][0]["why_it_matters"], report["findings"][0]["increment"]["baseline"], report["limitations"][0]["text"], "C1", "S1", "paragraph 1"):
            self.assertIn(value, text)
            self.assertIn(value, markdown)
        self.assertLess(text.index("只有单期数据"), text.index("收入增加更新") if "收入增加更新" in text else text.index("为什么重要"))
        self.assertIn(("details", {"id": "audit"}), parser.tags)
        self.assertIn("#claim-C1", parser.hrefs)

    def test_gfm_table_rows_stay_in_one_block(self):
        r, l, s = documents()
        r["tables"][0]["rows"].append(["上期", 10])
        markdown = render_report.render_markdown(r, l, s)
        self.assertIn("| 项目 | 收入 |\n| --- | --- |\n| 本期 | 12 |\n| 上期 | 10 |", markdown)
        self.assertNotIn("| 收入 |\n\n| ---", markdown)

    def test_embedded_sources_and_legacy_inline_evidence_are_visible(self):
        r, l, s = documents()
        l["sources"] = s
        for render in (render_report.render_html, render_report.render_markdown):
            output = render(r, l)
            self.assertIn("paragraph 1", output)
            self.assertIn("https://example.com/official", output)
        l.pop("sources")
        l["schema_version"] = 1
        l["claims"][0]["sources"] = [copy.deepcopy(s["candidates"][0])]
        for render in (render_report.render_html, render_report.render_markdown):
            output = render(r, l)
            self.assertIn("旧版 schema 1", output)
            self.assertIn("paragraph 1", output)
            self.assertIn("https://example.com/official", output)

    def test_malformed_legacy_basis_is_rejected_before_render(self):
        r, l, s = documents()
        l["schema_version"] = 1
        l["claims"][0]["sources"] = [copy.deepcopy(s["candidates"][0])]
        l["claims"][0]["basis"] = [{}]
        self.assertTrue(any("basis must be" in error for error in render_report.validate_report(r, l)))
        for render in (render_report.render_html, render_report.render_markdown):
            with self.assertRaises(ValueError):
                render(r, l)

    def test_missing_refs_shapes_duplicate_and_future_dates(self):
        for change in (lambda r, l: r["answer"].update(claim_ids=["C404"]),
                       lambda r, l: l["claims"].append(copy.deepcopy(l["claims"][0])),
                       lambda r, l: r.update(as_of="not-a-date"),
                       lambda r, l: r["tables"][0].update(rows=[["wrong width"]]),
                       lambda r, l: l["claims"][0].update(as_of="2026-11-01T00:00:00Z")):
            r, l, s = documents(); change(r, l)
            self.assertTrue(render_report.validate_report(r, l, s))
            with self.assertRaises(ValueError):
                render_report.render_html(r, l, s)

    def test_no_change_requires_explicit_reason(self):
        r, l, s = documents(); r["findings"] = []
        self.assertTrue(render_report.validate_report(r, l, s))
        r["no_change_reason"] = "新增来源没有改变既有判断。"
        self.assertEqual(render_report.validate_report(r, l, s), [])
        self.assertIn(r["no_change_reason"], render_report.render_markdown(r, l, s))

    def test_literal_payload_never_enters_script_or_markdown_link(self):
        r, l, s = documents()
        payload = '</script><img src=x onerror="alert(1)">[click](javascript:alert(1))'
        r["title"] = r["answer"]["text"] = r["findings"][0]["text"] = payload
        s["candidates"][0]["quote"] = payload
        page = render_report.render_html(r, l, s)
        parser = Text(); parser.feed(page)
        self.assertNotIn("img", [tag for tag, _ in parser.tags])
        self.assertEqual([tag for tag, _ in parser.tags].count("script"), 1)
        self.assertIn(payload, "".join(parser.text))
        markdown = render_report.render_markdown(r, l, s)
        self.assertNotIn("[click](javascript:", markdown)
        self.assertNotIn("<img", markdown)
        for url in ("javascript:alert(1)", "data:text/html,x", "file:///tmp/x", "//example.com", "https://user:secret@example.com", "https://example.com/\nfoo"):
            self.assertIsNone(render_report.safe_link(url), url)
        self.assertEqual(render_report.safe_link("https://example.com/(x)"), "https://example.com/%28x%29")

    def test_optional_chart_has_keyboard_points_table_units_and_theme(self):
        r, l, s = documents()
        r["chart"] = {"title": "收入序列", "x_label": "期间", "y_label": "收入", "unit": "亿元", "rows": [{"label": "Q1", "value": 12}, {"label": "Q2", "value": 12}], "claim_ids": ["C1"], "note": "同一口径"}
        page = render_report.render_html(r, l, s)
        for token in ('tabindex="0"', 'aria-live="polite"', 'role="tooltip"', 'id="chart-crosshair"', 'r="14" fill="transparent"', 'data-x=', "ArrowLeft", "ArrowRight", "prefers-color-scheme:dark", "<table>", "亿元", "Q2"):
            self.assertIn(token, page)
        self.assertNotIn("nan", page.lower())
        self.assertIn("Q2", render_report.render_markdown(r, l, s))
        r["chart"]["rows"][0]["value"] = float("nan")
        self.assertTrue(render_report.validate_report(r, l, s))

    def test_huge_json_integers_fail_chart_and_calculations_normally(self):
        huge = json.loads('1' + '0' * 1000)
        r, l, s = documents()
        r["chart"] = {"title": "收入", "x_label": "期间", "y_label": "收入", "unit": "亿元", "rows": [{"label": "Q1", "value": huge}, {"label": "Q2", "value": 12}], "claim_ids": ["C1"]}
        self.assertTrue(any("chart.rows" in e for e in render_report.validate_report(r, l, s)))
        with self.assertRaises(ValueError):
            render_report.render_html(r, l, s)
        r.pop("chart")
        calculation = {"id": "K1", "description": "收入", "formula": "value", "inputs": [{"name": "value", "value": 12, "unit": "亿元", "claim_ids": ["C1"]}], "result": {"value": 12, "unit": "亿元"}, "claim_ids": ["C1"]}
        for field in ("input", "result"):
            with self.subTest(field=field):
                r["calculations"] = [copy.deepcopy(calculation)]
                target = r["calculations"][0]["inputs"][0] if field == "input" else r["calculations"][0]["result"]
                target["value"] = huge
                self.assertTrue(render_report.validate_report(r, l, s))
                with self.assertRaises(ValueError):
                    render_report.render_markdown(r, l, s)

    def test_transparent_calculations_resolve_but_do_not_evaluate(self):
        r, l, s = documents()
        r["calculations"] = [{"id": "K1", "description": "收入变化", "formula": "current - prior", "inputs": [{"name": "current", "value": 12, "unit": "亿元", "claim_ids": ["C1"]}], "result": {"value": 2, "unit": "亿元"}, "claim_ids": ["C1"]}]
        l["claims"][0]["calculation_id"] = "K1"
        self.assertEqual(render_report.validate_report(r, l, s), [])
        for result in (render_report.render_markdown(r, l, s), render_report.render_html(r, l, s)):
            self.assertIn("current", result)
            self.assertIn("亿元", result)
        r["calculations"][0]["inputs"][0]["claim_ids"] = ["missing"]
        self.assertTrue(render_report.validate_report(r, l, s))

    def test_symlinked_ancestor_is_allowed_for_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            real = root / "real"
            real.mkdir()
            alias = root / "alias"
            alias.symlink_to(real, target_is_directory=True)
            render_report.write_outputs(alias / "out", "md", "html")
            self.assertEqual((real / "out/report.md").read_text(), "md")

    def test_output_refuses_overwrite_and_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            render_report.write_outputs(root / "out", "md", "html")
            with self.assertRaises(ValueError):
                render_report.write_outputs(root / "out", "changed", "changed")
            self.assertEqual((root / "out/report.md").read_text(), "md")
            render_report.write_outputs(root / "out", "new", "new", overwrite=True)
            (root / "link").symlink_to(root / "out", target_is_directory=True)
            with self.assertRaises(ValueError):
                render_report.write_outputs(root / "link", "x", "x", True)
            with self.assertRaises(ValueError):
                render_report.read_document(root / "link/report.md")


if __name__ == "__main__":
    unittest.main()
