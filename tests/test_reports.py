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
        report, ledger, sources = self.bar_document()
        report["chart"]["series"] = [{"name": "A", "rows": [{"label": "Q1", "value": 1},
                                                            {"label": "Q2", "value": 2}]}]
        report["chart"].pop("rows")
        self.assertTrue(any("cannot use series" in error for error in render_report.validate_report(report, ledger, sources)))
        report, ledger, sources = self.waterfall_document()
        report["chart"]["rows"][0].pop("role")
        self.assertTrue(any("role must be" in error for error in render_report.validate_report(report, ledger, sources)))
        report, ledger, sources = self.waterfall_document()
        report["chart"]["rows"] = [{"label": "变动", "value": 1, "role": "delta"},
                                   {"label": "合计", "value": 1, "role": "total"}]
        self.assertTrue(any("start with a total" in error for error in render_report.validate_report(report, ledger, sources)))

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
