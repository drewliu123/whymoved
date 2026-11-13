"""One-page IC memo derived from frozen report fields."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import memo_pack
import render_report
from test_analysis_contract import add_model, bundle, summary_bundle
from test_event_study import document as event_document, sample as event_sample
from test_reports import QualityReportTests, documents


def memo(data, max_findings=3):
    report, ledger, sources = data
    errors = render_report.validate_report(report, ledger, sources)
    if errors:
        raise AssertionError(errors)
    return memo_pack.build_memo(report, ledger, max_findings)


class MemoContentTests(unittest.TestCase):
    def test_core_sections(self):
        text = memo(documents())
        for heading in ("# 收入变化", "## 判断", "## 关键发现", "## 什么会改变判断", "## 主要风险", "## 溯源"):
            self.assertIn(heading, text)
        for token in ("本期收入增加。", "收入增加", "更新收入判断。", "只有单期数据", "观察 下一次披露", "主张数：1"):
            self.assertIn(token, text)
        self.assertNotIn("## 方法区间", text)

    def test_finding_limit(self):
        report, ledger, sources = documents()
        report["findings"].append({"title": "第二条发现", "text": "x", "claim_ids": ["C1"],
                                   "why_it_matters": "y",
                                   "increment": {"kind": "new_fact", "baseline": "a", "detail": "b"}})
        report["findings"].append({"title": "第三条发现", "text": "x", "claim_ids": ["C1"],
                                   "why_it_matters": "y",
                                   "increment": {"kind": "new_fact", "baseline": "a", "detail": "b"}})
        text = memo((report, ledger, sources), max_findings=2)
        self.assertIn("第二条发现", text)
        self.assertNotIn("第三条发现", text)

    def test_valuation_section_reads_frozen_models(self):
        data = summary_bundle()
        text = memo(data[:3])
        self.assertIn("## 方法区间（来自冻结模型输出）", text)
        for token in ("DCF 基准情形", "可比公司倍数", "反向DCF隐含增长", "隐含增长率",
                      "不跨方法加权", "不是目标价"):
            self.assertIn(token, text)
        dcf = next(model for model in data[0]["analysis"]["models"]
                   if model["spec"]["kind"] == "dcf")
        self.assertIn(str(dcf["result"]["outputs"]["per_share"]["value"]), text)
        reverse = next(model for model in data[0]["analysis"]["models"]
                       if model["spec"]["kind"] == "reverse_dcf")
        self.assertIn(str(reverse["result"]["outputs"]["implied_growth"]["value"]), text)

    def test_dated_catalysts_only(self):
        report, ledger, sources = documents()
        self.assertNotIn("## 接下来看什么", memo((report, ledger, sources)))
        report["watch"][0]["due"] = "2026-12-15"
        report["watch"][0]["type"] = "earnings"
        text = memo((report, ledger, sources))
        self.assertIn("## 接下来看什么", text)
        self.assertIn("2026-12-15", text)
        self.assertIn("下一次披露", text)

    def test_escapes_structure_without_bloating_text(self):
        report, ledger, sources = documents()
        report["title"] = "*加粗尝试* 与标题"
        text = memo((report, ledger, sources))
        self.assertIn("\\*加粗尝试\\*", text)
        self.assertTrue(text.startswith("# \\*加粗尝试\\*"))
        report["findings"][0]["title"] = "CFO-capex（同口径）"
        text = memo((report, ledger, sources))
        self.assertIn("CFO-capex（同口径）", text, "plain hyphens and full-width parens stay readable")

    def test_table_cells_escape_pipes(self):
        data = summary_bundle()
        data[0]["valuation_summary"]["rows"][0]["label"] = "DCF|基准"
        text = memo(data[:3])
        self.assertIn("DCF\\|基准", text)


class MemoLinkedSectionsTests(unittest.TestCase):
    def transmission(self):
        return {"schema_version": 1, "theme": "测试传导", "as_of": "2026-10-31T12:00:00Z",
                "nodes": [{"id": "A", "label": "需求", "kind": "demand",
                           "observables": ["订单"], "claim_ids": ["C1"]},
                          {"id": "B", "label": "并网容量", "kind": "capacity",
                           "observables": ["排队时长"], "claim_ids": ["C1"]}],
                "edges": [{"from": "A", "to": "B", "mechanism": "排队", "lag": "1个季度",
                           "claim_ids": ["C1"]}],
                "bottleneck": {"node": "B", "reason": "审批节奏", "claim_ids": ["C1"]}}

    def test_bottleneck_section(self):
        report, ledger, sources = documents()
        report["transmission"] = self.transmission()
        text = memo((report, ledger, sources))
        self.assertIn("## 传导瓶颈", text)
        self.assertIn("并网容量", text)
        self.assertIn("审批节奏", text)
        self.assertIn("路径：", text)
        self.assertIn("A → B", text)

    def test_quality_flags_section(self):
        report, ledger, sources = documents()
        report["quality"] = {"statements": QualityReportTests().statements()}
        text = memo((report, ledger, sources)).replace("\\", "")
        self.assertIn("## 质量红旗", text)
        self.assertIn("growth_without_cash", text)
        self.assertIn("其余 3 条见完整报告", text)
        report["quality"]["thresholds"] = {"conversion_drop": 1.0}
        text = memo((report, ledger, sources)).replace("\\", "")
        self.assertNotIn("growth_without_cash", text)
        self.assertIn("low_capex_vs_da", text)

    def test_event_study_section(self):
        report, ledger, sources = documents()
        report["event_study"] = event_document(
            [event_sample("E1", [100, 110, 120, 132, 144, 158], 2),
             event_sample("E2", [100, 100, 100, 90, 99, 108.9], 2)], before=2, after=2)
        text = memo((report, ledger, sources))
        self.assertIn("## 参考类事件", text)
        self.assertIn("后窗", text)
        self.assertIn("中位", text)
        self.assertIn("为正", text)
        self.assertIn("不是预测", text)

    def test_quality_unattributed_is_listed(self):
        report, ledger, sources = documents()
        report["quality"] = {"statements": QualityReportTests().statements()}
        report["quality"]["statements"]["periods"][1]["capex"] = 50
        text = memo((report, ledger, sources)).replace("\\", "")
        self.assertIn("未挂 claim 的字段", text)
        self.assertIn("capex", text)

    def test_projection_section_copies_frozen_years(self):
        report, ledger, sources, plan = bundle("operating_outlook")
        add_model(report, ledger, "driver_build")
        model = report["analysis"]["models"][0]
        model["spec"]["projection"] = [{"label": "FY2026E", "revenue_growth": 0.08, "margin": 0.21},
                                       {"label": "FY2027E", "revenue_growth": 0.06, "margin": 0.22},
                                       {"label": "FY2028E", "revenue_growth": 0.05, "margin": 0.23},
                                       {"label": "FY2029E", "revenue_growth": 0.04, "margin": 0.23}]
        import analysis_models
        model["result"] = analysis_models.compute_model(model["spec"])
        text = memo((report, ledger, sources))
        self.assertIn("## 多年路径", text)
        self.assertIn("FY2026E", text)
        self.assertIn("等 4 年", text)
        self.assertIn("不是预测", text)
        self.assertIn("收入/营业利润", text)

    def test_chart_inventory(self):
        report, ledger, sources = documents()
        report["chart"] = {"title": "收入趋势", "x_label": "期间", "y_label": "收入", "unit": "亿元",
                           "rows": [{"label": "Q1", "value": 1}, {"label": "Q2", "value": 2}],
                           "claim_ids": ["C1"]}
        text = memo((report, ledger, sources))
        self.assertIn("图表 1 张", text)
        self.assertIn("收入趋势", text)
        self.assertIn("完整报告或 HTML 版", text)
        report.pop("chart")
        report["charts"] = [{"title": "第二张", "x_label": "x", "y_label": "y", "unit": "元",
                             "rows": [{"label": "A", "value": 1}, {"label": "B", "value": 2}],
                             "claim_ids": ["C1"]},
                            {"title": "第三张", "x_label": "x", "y_label": "y", "unit": "元",
                             "rows": [{"label": "A", "value": 1}, {"label": "B", "value": 2}],
                             "claim_ids": ["C1"]}]
        text = memo((report, ledger, sources))
        self.assertIn("图表 2 张", text)
        self.assertIn("第二张", text)

    def test_sections_absent_by_default(self):
        text = memo(documents())
        self.assertNotIn("## 传导瓶颈", text)
        self.assertNotIn("## 质量红旗", text)
        self.assertNotIn("## 参考类事件", text)
        self.assertNotIn("图表", text)


class MemoCliTests(unittest.TestCase):
    def files(self, data):
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name).resolve()
        paths = []
        for name, document in zip(("report", "claims", "sources"), data[:3]):
            path = root / (name + ".json")
            path.write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")
            paths.append(str(path))
        return tmp, root, paths

    def invoke(self, *args):
        return subprocess.run([sys.executable, str(SCRIPTS / "memo_pack.py"), *args],
                              capture_output=True, text=True)

    def test_writes_memo(self):
        tmp, root, (report, claims, sources) = self.files(documents())
        with tmp:
            target = root / "memo.md"
            process = self.invoke(report, "--claims", claims, "--sources", sources, "--out", str(target))
            self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
            payload = json.loads(process.stdout)
            self.assertTrue(payload["passed"])
            self.assertTrue(target.exists())
            self.assertIn("## 判断", target.read_text(encoding="utf-8"))

    def test_cli_failures(self):
        tmp, root, (report, claims, sources) = self.files(documents())
        with tmp:
            self.assertEqual(self.invoke(report, "--sources", sources).returncode, 1, "claims required")
            self.assertEqual(self.invoke(report, "--claims", claims, "--sources", sources,
                                      "--max-findings", "0").returncode, 1)
            broken = root / "broken.json"
            broken.write_text("{", encoding="utf-8")
            self.assertEqual(self.invoke(str(broken), "--claims", claims).returncode, 2)
            invalid = json.loads(Path(report).read_text(encoding="utf-8"))
            invalid.pop("answer")
            Path(report).write_text(json.dumps(invalid), encoding="utf-8")
            process = self.invoke(report, "--claims", claims, "--sources", sources)
            self.assertEqual(process.returncode, 1)
            self.assertFalse(json.loads(process.stdout)["passed"])


if __name__ == "__main__":
    unittest.main()
