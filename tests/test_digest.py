"""Multi-run digest: recent judgments, changes, upcoming and overdue catalysts."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import digest
from test_research_memory import write_run


class DigestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name).resolve()
        write_run(self.home, "R20261101T000000Z-aaaaaaaaaaaa", as_of="2026-11-01T00:00:00Z",
                  title="首轮BTC", question="BTC 怎么看", entity="BTC", judgment="中性偏多")
        write_run(self.home, "R20261110T000000Z-bbbbbbbbbbbb", as_of="2026-11-10T00:00:00Z",
                  title="BTC 更新", entity="BTC", judgment="转为偏空", judgment_changed=True,
                  parent="R20261101T000000Z-aaaaaaaaaaaa", trigger_due="2026-11-25")
        write_run(self.home, "R20260901T000000Z-cccccccccccc", as_of="2026-09-01T00:00:00Z",
                  title="旧研究", entity="GOLD", judgment="黄金中性", trigger_due="2026-09-20")

    def tearDown(self):
        self.tmp.cleanup()

    def digest(self, **overrides):
        return digest.build_digest(self.home, overrides.get("as_of", "2026-11-14T00:00:00Z"),
                                   overrides.get("days", 30))

    def test_sections_and_window(self):
        text = self.digest()
        self.assertIn("# 研究摘要（2026-11-14 起 30 天）", text)
        self.assertIn("归档 3 轮；本窗口 2 轮", text)
        self.assertIn("## 判断变化", text)
        self.assertIn("BTC 更新", text)
        self.assertIn("## 本窗口研究", text)
        self.assertLess(text.index("BTC 更新"), text.index("首轮BTC"))
        self.assertNotIn("旧研究", text.split("## 未来 30 天的催化")[0])

    def test_recent_window_is_configurable(self):
        text = self.digest(days=5)
        self.assertIn("本窗口 1 轮", text)
        self.assertNotIn("首轮BTC", text.split("## 未来 30 天的催化")[0])

    def test_same_question_runs_are_grouped(self):
        write_run(self.home, "R20261111T000000Z-eeeeeeeeeeee", as_of="2026-11-11T00:00:00Z",
                  title="BTC 重跑一", question="BTC 怎么看", entity="BTC", judgment="偏多")
        write_run(self.home, "R20261112T000000Z-ffffffffffff", as_of="2026-11-12T00:00:00Z",
                  title="BTC 重跑二", question="BTC 怎么看", entity="BTC", judgment="偏空")
        text = self.digest()
        self.assertIn("同题 3 轮", text)
        self.assertIn("结论版本 3 个", text)
        self.assertIn("BTC 重跑二", text)
        self.assertIn("判断：偏空", text)
        self.assertNotIn("判断：偏多", text, "older runs of the same question collapse into the newest line")
        self.assertIn("重复实验不等于多次独立验证", text)

    def test_thesis_status_change_is_reported_even_without_judgment_change(self):
        run_id = "R20261110T000000Z-bbbbbbbbbbbb"
        report_path = self.home / "journal" / "runs" / run_id / "report.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        report["update"] = {"judgment_changed": False, "reason": "指引下修且 CEO 继任未落地",
                            "opportunity": {"previous_status": "watch", "current_status": "no_edge",
                                            "thesis_change": "weakened"}}
        report["opportunity"] = {"applicability": "trading", "assessment": {"status": "no_edge"}}
        report["question"] = "BTC 怎么看"
        report_path.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")
        text = self.digest()
        self.assertIn("更新：指引下修", text)
        self.assertIn("论点：等待触发 → 未见优势（削弱）", text)
        self.assertIn("论点状态：", text)
        report["update"]["opportunity"] = {"previous_status": "watch", "current_status": "watch",
                                          "thesis_change": "strengthened",
                                          "trigger_results": [{"trigger_id": "TR1", "status": "hit"},
                                                              {"trigger_id": "TR2", "status": "not_checked"}]}
        report_path.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")
        text = self.digest()
        self.assertIn("论点：等待触发（增强）", text)
        self.assertNotIn("等待触发 → 等待触发", text)
        self.assertIn("触发：已触发 1、未检查 1", text)

    def test_upcoming_and_overdue_catalysts(self):
        write_run(self.home, "R20261112T000000Z-dddddddddddd", as_of="2026-11-12T00:00:00Z",
                  entity="BTC", judgment="等待信号", trigger_due="2026-11-13")
        text = self.digest()
        self.assertIn("## 未来 30 天的催化", text)
        self.assertIn("2026-11-25", text)
        self.assertIn("+11.0 天", text)
        self.assertIn("## 过期未核对", text)
        self.assertIn("2026-11-13", text)
        self.assertIn("过期不等于未触发", text)

    def test_no_catalysts_message(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp).resolve()
            write_run(home, "R20261110T000000Z-bbbbbbbbbbbb", as_of="2026-11-10T00:00:00Z",
                      entity="BTC", trigger_due="")
            text = digest.build_digest(home, "2026-11-14T00:00:00Z", 30)
            self.assertIn("没有", text)
            self.assertIn("没有过期未核对", text)

    def test_invalid_arguments(self):
        with self.assertRaisesRegex(ValueError, "as-of"):
            digest.build_digest(self.home, "not-a-date", 30)
        with self.assertRaisesRegex(ValueError, "at least 1"):
            digest.build_digest(self.home, "2026-11-14T00:00:00Z", 0)
        with tempfile.TemporaryDirectory() as empty:
            with self.assertRaises(FileNotFoundError):
                digest.build_digest(empty)


class CliTests(unittest.TestCase):
    def test_cli_and_out(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp).resolve()
            write_run(home, "R20261110T000000Z-bbbbbbbbbbbb", as_of="2026-11-10T00:00:00Z",
                      entity="BTC", judgment="偏空", trigger_due="2026-11-25")
            process = subprocess.run([sys.executable, str(SCRIPTS / "digest.py"), "--home", str(home),
                                      "--as-of", "2026-11-14T00:00:00Z"], capture_output=True, text=True)
            self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
            self.assertIn("# 研究摘要", process.stdout)
            target = home / "digest.md"
            process = subprocess.run([sys.executable, str(SCRIPTS / "digest.py"), "--home", str(home),
                                      "--as-of", "2026-11-14T00:00:00Z", "--out", str(target)],
                                     capture_output=True, text=True)
            self.assertEqual(process.returncode, 0, process.stdout)
            self.assertTrue(target.exists())
            self.assertIn("2026-11-25", target.read_text(encoding="utf-8"))

    def test_cli_failures(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp).resolve()
            write_run(home, "R20261110T000000Z-bbbbbbbbbbbb", as_of="2026-11-10T00:00:00Z", entity="BTC")
            process = subprocess.run([sys.executable, str(SCRIPTS / "digest.py"), "--home", str(home),
                                      "--as-of", "nope"], capture_output=True, text=True)
            self.assertEqual(process.returncode, 1)
            empty = Path(tmp).resolve() / "empty"
            empty.mkdir()
            process = subprocess.run([sys.executable, str(SCRIPTS / "digest.py"), "--home", str(empty)],
                                     capture_output=True, text=True)
            self.assertEqual(process.returncode, 2)


if __name__ == "__main__":
    unittest.main()
