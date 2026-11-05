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
