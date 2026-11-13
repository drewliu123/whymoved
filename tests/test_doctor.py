"""Data-root health check: loadable archives, catalyst audit, read-only behaviour."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import doctor
import research_run
from unittest.mock import patch
from test_analysis_contract import bundle


def archive(home, watch_due=None, entity=None):
    """Create one real archive through the public archiving path."""
    report, ledger, sources, plan = bundle("change_explanation")
    if entity:
        plan["entity"] = entity
    if watch_due:
        report["watch"].append({"signal": "验证毛利率", "meaning": "核对下一期披露",
                                "claim_ids": ["C1"], "due": watch_due, "type": "earnings"})
    with tempfile.TemporaryDirectory() as tmp:
        paths = []
        for name, document in zip(("report", "claims", "sources", "plan"), (report, ledger, sources, plan)):
            path = Path(tmp).resolve() / (name + ".json")
            path.write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")
            paths.append(path)
        return research_run.archive_run(*paths, home=home)["run_id"]


class DoctorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name).resolve()

    def tearDown(self):
        self.tmp.cleanup()

    def test_healthy_root(self):
        archive(self.home, watch_due="2026-12-15", entity="BTC")
        archive(self.home, watch_due="2026-12-20", entity="NVDA")
        passed, summary, errors, warnings = doctor.run_checks(self.home, "2026-11-14")
        self.assertTrue(passed)
        self.assertEqual(errors, [])
        self.assertEqual(summary["runs"], 2)
        self.assertEqual(summary["loaded"], 2)
        self.assertEqual(summary["failed"], 0)
        self.assertEqual(summary["entities"], 2)
        self.assertEqual(summary["dated_catalysts"], 2)
        self.assertEqual(summary["overdue"], 0)

    def test_overdue_catalyst_warns_but_does_not_fail(self):
        archive(self.home, watch_due="2026-11-12")
        passed, summary, errors, warnings = doctor.run_checks(self.home, "2026-11-14")
        self.assertTrue(passed)
        self.assertEqual(summary["overdue"], 1)
        self.assertTrue(any("overdue" in warning for warning in warnings))

    def test_broken_archive_fails_the_check(self):
        archive(self.home, entity="BTC")
        broken = self.home / "journal" / "runs" / "R20261102T000000Z-cccccccccccc"
        broken.mkdir(parents=True)
        (broken / "report.json").write_text("{", encoding="utf-8")
        passed, summary, errors, warnings = doctor.run_checks(self.home, "2026-11-14")
        self.assertFalse(passed)
        self.assertEqual(summary["failed"], 0, "broken runs are reported as errors, not loaded")
        self.assertEqual(summary["loaded"], 1)
        self.assertTrue(any("R20261102T000000Z" in error for error in errors))

    def test_empty_runs_directory_is_healthy_with_warning(self):
        (self.home / "journal" / "runs").mkdir(parents=True)
        passed, summary, errors, warnings = doctor.run_checks(self.home, "2026-11-14")
        self.assertTrue(passed)
        self.assertEqual(summary["runs"], 0)
        self.assertTrue(any("no archived runs" in warning for warning in warnings))

    def test_renders_check_matches_frozen_output(self):
        archive(self.home, entity="BTC")
        passed, summary, errors, warnings = doctor.run_checks(self.home, "2026-11-14", renders=True)
        self.assertTrue(passed, errors)
        self.assertEqual(summary["renders_checked"], 1)
        with patch("render_report.render_markdown", return_value="changed by a future renderer"):
            passed, summary, errors, warnings = doctor.run_checks(self.home, "2026-11-14", renders=True)
        self.assertFalse(passed)
        self.assertTrue(any("report.md differs from the current renderer" in error for error in errors), errors)

    def test_read_only(self):
        archive(self.home, entity="BTC")

        def snapshot():
            return {str(path.relative_to(self.home)): path.read_bytes()
                    for path in sorted(self.home.rglob("*")) if path.is_file()}

        before = snapshot()
        doctor.run_checks(self.home, "2026-11-14")
        self.assertEqual(before, snapshot())


class DoctorCliTests(unittest.TestCase):
    def invoke(self, *args, env=None):
        return subprocess.run([sys.executable, str(SCRIPTS / "doctor.py"), *args],
                              capture_output=True, text=True, env=env)

    def test_missing_root_exits_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            process = self.invoke("--home", tmp)
            self.assertEqual(process.returncode, 2)
            self.assertFalse(json.loads(process.stdout)["passed"])

    def test_invalid_as_of_exits_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            process = self.invoke("--home", tmp, "--as-of", "nope")
            self.assertEqual(process.returncode, 1)

    def test_healthy_root_exits_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp).resolve()
            archive(home, entity="BTC")
            process = self.invoke("--home", str(home), "--as-of", "2026-11-14")
            self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
            payload = json.loads(process.stdout)
            self.assertTrue(payload["passed"])
            self.assertEqual(payload["summary"]["loaded"], 1)

    def test_renders_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp).resolve()
            archive(home, entity="BTC")
            process = self.invoke("--home", str(home), "--as-of", "2026-11-14", "--renders")
            self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
            self.assertEqual(json.loads(process.stdout)["summary"]["renders_checked"], 1)

    def test_default_home_comes_from_environment(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp).resolve()
            archive(home, entity="BTC")
            env = dict(os.environ, TOUYAN_HOME=str(home))
            process = self.invoke("--as-of", "2026-11-14", env=env)
            self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
            self.assertEqual(json.loads(process.stdout)["summary"]["runs"], 1)


if __name__ == "__main__":
    unittest.main()
