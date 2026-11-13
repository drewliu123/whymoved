"""Dated catalysts: optional due/type fields, calendar extraction and CLI."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import catalyst_calendar as cal


def report(as_of="2026-11-14T00:00:00Z", triggers=None, watch=None):
    data = {"as_of": as_of, "watch": watch or []}
    if triggers is not None:
        data["opportunity"] = {"version": 1, "applicability": "trading", "triggers": triggers}
    return data


def trigger(identifier="T1", **overrides):
    data = {"id": identifier, "signal": "FOMC 决议", "by": "12/9 附近",
            "supports_if": "鸽派", "weakens_if": "鹰派", "invalidates_if": "50bp",
            "claim_ids": ["C1"]}
    data.update(overrides)
    return data


def watch(signal="财报", **overrides):
    data = {"signal": signal, "meaning": "验证毛利", "claim_ids": ["C1"]}
    data.update(overrides)
    return data


class CatalystValidationTests(unittest.TestCase):
    def test_due_and_type_are_optional(self):
        self.assertEqual(cal.validate_report_catalysts(report(triggers=[trigger()], watch=[watch()])), [])

    def test_valid_due_and_type_pass(self):
        self.assertEqual(cal.validate_report_catalysts(report(
            triggers=[trigger(due="2026-12-09T19:00:00Z", type="macro")],
            watch=[watch(due="2026-12-15", type="earnings")])), [])

    def test_invalid_due_type_and_past_date(self):
        cases = [
            [trigger(due="12/09/2026")],
            [trigger(due="2026-11-01")],
            [trigger(type="misc")],
            [trigger(type=1)],
        ]
        for triggers in cases:
            self.assertTrue(cal.validate_report_catalysts(report(triggers=triggers)), triggers)
        self.assertTrue(cal.validate_report_catalysts(report(watch=[watch(due="tomorrow")])))
        self.assertTrue(cal.validate_report_catalysts(report(watch=[watch(type="earnings", due="2026-11-13")])))
        # report.as_of itself is validated by render_report; without a usable as_of the
        # ordering rule simply cannot run, so the calendar does not invent a failure.
        self.assertEqual(cal.validate_report_catalysts(report(as_of="not-a-date", triggers=[trigger(due="2026-12-09")])), [])

    def test_malformed_entries_are_ignored_not_crashed(self):
        for bad in ({"watch": "nope"}, {"watch": [None, 1]},
                    {"opportunity": {"triggers": "nope"}}, {"opportunity": {"triggers": [None]}}):
            data = {"as_of": "2026-11-14T00:00:00Z", **bad}
            self.assertEqual(cal.validate_report_catalysts(data), [])


class ExtractionTests(unittest.TestCase):
    def test_entries_keep_the_existing_id_space(self):
        entries = cal.extract_entries(report(
            triggers=[trigger(due="2026-12-09", type="macro")],
            watch=[watch(due="2026-12-15", type="earnings"), watch("指标更新")]), "r.json", "R1")
        self.assertEqual([(entry["kind"], entry["id"]) for entry in entries],
                         [("trigger", "T1"), ("watch", "W1"), ("watch", "W2")])
        self.assertEqual(entries[0]["due"], "2026-12-09")
        self.assertEqual(entries[0]["type"], "macro")
        self.assertIsNone(entries[2]["due"])
        self.assertEqual(entries[1]["claim_ids"], ["C1"])
        self.assertEqual(entries[0]["run_id"], "R1")

    def test_calendar_states_and_sorting(self):
        documents = [("r.json", "R1", report(
            triggers=[trigger("T2", due="2026-11-20"), trigger("T1", due="2026-12-09")],
            watch=[watch(due="2026-12-01", type="earnings"), watch("无日期")]))]
        origin = cal._date("2026-11-14T00:00:00Z")
        result = cal.build_calendar(documents, origin)
        self.assertEqual([entry["id"] for entry in result["upcoming"]],
                         ["T2", "W1", "T1"], "upcoming sorted by due date")
        self.assertEqual([entry["id"] for entry in result["undated"]], ["W2"])
        self.assertEqual(result["overdue"], [])
        w1 = next(entry for entry in result["upcoming"] if entry["id"] == "W1")
        self.assertAlmostEqual(w1["days_from_as_of"],
                               (cal._date("2026-12-01") - origin).total_seconds() / 86400, places=3)
        later = cal.build_calendar(documents, cal._date("2026-12-10"))
        self.assertEqual([entry["id"] for entry in later["overdue"]], ["T2", "W1", "T1"])

    def test_horizon_filters_upcoming_only(self):
        documents = [("r.json", "R1", report(triggers=[trigger("T1", due="2026-12-09"),
                                                      trigger("T2", due="2026-11-20")]))]
        result = cal.build_calendar(documents, cal._date("2026-11-14"), horizon_days=10)
        self.assertEqual([entry["id"] for entry in result["upcoming"]], ["T2"])

    def test_no_as_of_marks_everything_undated(self):
        result = cal.build_calendar([("r.json", None, report(triggers=[trigger(due="2026-12-09")]))], None)
        self.assertEqual(result["undated"][0]["days_from_as_of"], None)
        self.assertTrue(result["notes"])


class ShadowingTests(unittest.TestCase):
    def test_stdlib_calendar_preloaded_does_not_break_imports(self):
        """A stdlib `calendar` already in sys.modules must not shadow our module."""
        process = subprocess.run(
            [sys.executable, "-c",
             "import calendar, sys; sys.path.insert(0, 'scripts'); import render_report; "
             "print('ok')"],
            cwd=str(SCRIPTS.parent), capture_output=True, text=True)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertIn("ok", process.stdout)

    def test_cli_shim_still_works(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp).resolve() / "report.json"
            path.write_text(json.dumps(report(watch=[watch(due="2026-12-15")])), encoding="utf-8")
            process = subprocess.run([sys.executable, str(SCRIPTS / "catalyst_calendar.py"), str(path)],
                                     capture_output=True, text=True)
            self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
            self.assertEqual(json.loads(process.stdout)["upcoming"][0]["id"], "W1")


class CliTests(unittest.TestCase):
    def write_report(self, root, report_data, name="report.json"):
        path = Path(root) / name
        path.write_text(json.dumps(report_data), encoding="utf-8")
        return path

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPTS / "catalyst_calendar.py"), *args],
                              capture_output=True, text=True)

    def test_single_report_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_report(tmp, report(watch=[watch(due="2026-12-15", type="earnings")]))
            process = self.run_cli(str(path))
            self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
            payload = json.loads(process.stdout)
            self.assertTrue(payload["passed"])
            self.assertEqual(payload["upcoming"][0]["id"], "W1")
            self.assertEqual(payload["as_of_text"], "2026-11-14T00:00:00Z")

    def test_due_filter_and_as_of_override(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_report(tmp, report(
                triggers=[trigger("T1", due="2026-11-20"), trigger("T2", due="2026-12-09")]))
            process = self.run_cli(str(path), "--as-of", "2026-11-14", "--due", "10")
            payload = json.loads(process.stdout)
            self.assertEqual([entry["id"] for entry in payload["upcoming"]], ["T1"])
            process = self.run_cli(str(path), "--as-of", "2026-12-01")
            payload = json.loads(process.stdout)
            self.assertEqual([entry["id"] for entry in payload["overdue"]], ["T1"])
            self.assertEqual([entry["id"] for entry in payload["upcoming"]], ["T2"])

    def test_home_scan_reads_archived_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp).resolve() / "journal/runs/R20261114T000000Z-abcdef123456"
            run.mkdir(parents=True)
            self.write_report(run, report(triggers=[trigger(due="2026-12-09", type="macro")]))
            (run / "manifest.json").write_text(json.dumps({"run_id": run.name}), encoding="utf-8")
            process = self.run_cli("--home", tmp)
            payload = json.loads(process.stdout)
            self.assertEqual(payload["upcoming"][0]["run_id"], run.name)
            self.assertTrue(payload["upcoming"][0]["source"].endswith("report.json"))

    def test_run_directory_reads_the_manifest_run_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp).resolve() / "R20261114T000000Z-abcdef123456"
            run.mkdir()
            self.write_report(run, report(triggers=[trigger(due="2026-12-09")]))
            (run / "manifest.json").write_text(json.dumps({"run_id": run.name}), encoding="utf-8")
            process = self.run_cli(str(run))
            payload = json.loads(process.stdout)
            self.assertEqual(payload["upcoming"][0]["run_id"], run.name)

    def test_failures(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = self.write_report(tmp, report(watch=[watch(due="nope")]), name="bad.json")
            self.assertEqual(self.run_cli(str(bad)).returncode, 1)
            broken = Path(tmp) / "broken.json"
            broken.write_text("{", encoding="utf-8")
            self.assertEqual(self.run_cli(str(broken)).returncode, 1)
            self.assertEqual(self.run_cli(str(Path(tmp) / "missing.json")).returncode, 2)
            self.assertEqual(self.run_cli().returncode, 2)


if __name__ == "__main__":
    unittest.main()
