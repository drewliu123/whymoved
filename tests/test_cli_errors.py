"""Failure paths must stay short, path-bearing and traceback-free, with stable exit codes."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from test_analysis_contract import bundle


def invoke(name, *args):
    return subprocess.run([sys.executable, str(SCRIPTS / name), *args], capture_output=True, text=True)


def write_documents(root, report, ledger, sources, plan):
    paths = {}
    for name, document in (("report", report), ("claims", ledger), ("sources", sources), ("plan", plan)):
        path = root / (name + ".json")
        path.write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")
        paths[name] = path
    return paths


class ReaderErrorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()
        self.bad = self.root / "bad.json"
        self.bad.write_text("{", encoding="utf-8")
        self.missing = self.root / "missing.json"

    def tearDown(self):
        self.tmp.cleanup()

    def assert_reader_failure(self, process, path):
        self.assertEqual(process.returncode, 2, process.stdout + process.stderr)
        output = process.stdout + process.stderr
        self.assertIn(str(path), output)
        self.assertNotIn("Traceback", output)

    def test_unreadable_json_reports_the_path(self):
        cases = [
            ("research_plan.py", [str(self.bad)]),
            ("sources.py", ["validate", str(self.bad)]),
            ("analysis_contract.py", ["check", "--plan", str(self.bad), "--report", str(self.bad),
                                      "--claims", str(self.bad), "--sources", str(self.bad)]),
            ("render_report.py", [str(self.bad), "--claims", str(self.bad), "--sources", str(self.bad),
                                  "--out-dir", str(self.root / "out")]),
            ("catalyst_calendar.py", [str(self.bad)]),
        ]
        for name, args in cases:
            with self.subTest(cli=name):
                self.assert_reader_failure(invoke(name, *args), self.bad)

    def test_missing_file_reports_the_path(self):
        cases = [
            ("research_plan.py", [str(self.missing)]),
            ("analysis_contract.py", ["check", "--plan", str(self.missing), "--report", str(self.missing),
                                      "--claims", str(self.missing), "--sources", str(self.missing)]),
            ("render_report.py", [str(self.missing), "--claims", str(self.missing), "--sources", str(self.missing),
                                  "--out-dir", str(self.root / "out")]),
        ]
        for name, args in cases:
            with self.subTest(cli=name):
                self.assert_reader_failure(invoke(name, *args), self.missing)

    def test_contract_failure_exits_one(self):
        report, ledger, sources, plan = bundle("change_explanation")
        report["answer"]["claim_ids"] = ["missing"]
        paths = write_documents(self.root, report, ledger, sources, plan)
        process = invoke("analysis_contract.py", "check", "--plan", str(paths["plan"]), "--report", str(paths["report"]),
                         "--claims", str(paths["claims"]), "--sources", str(paths["sources"]))
        self.assertEqual(process.returncode, 1, process.stdout + process.stderr)
        self.assertNotIn("Traceback", process.stdout + process.stderr)
        self.assertIn("answer.claim_ids", process.stdout + process.stderr)

    def test_render_validation_failure_exits_one(self):
        report, ledger, sources, plan = bundle("change_explanation")
        report["answer"]["claim_ids"] = ["missing"]
        paths = write_documents(self.root, report, ledger, sources, plan)
        process = invoke("render_report.py", str(paths["report"]), "--claims", str(paths["claims"]),
                         "--sources", str(paths["sources"]), "--out-dir", str(self.root / "out"))
        self.assertEqual(process.returncode, 1, process.stdout + process.stderr)
        self.assertNotIn("Traceback", process.stdout + process.stderr)

    def test_library_has_no_silent_standalone_run(self):
        process = invoke("calculations.py")
        self.assertEqual(process.returncode, 2, process.stdout + process.stderr)
        self.assertIn("library", process.stderr)


if __name__ == "__main__":
    unittest.main()
