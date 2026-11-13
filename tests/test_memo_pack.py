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
from test_analysis_contract import summary_bundle
from test_reports import documents


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
