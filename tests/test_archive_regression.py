"""Every archived research run must still load under the current validators.

This is the compatibility guard for a growing contract: new optional fields and
stricter rules must never make an existing `journal/runs/<run_id>` unreadable.
It reads the archives in place and never writes to them.
"""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import render_report
import research_run


class ArchiveRegressionTests(unittest.TestCase):
    def test_all_archived_runs_load(self):
        runs_dir = ROOT / "journal" / "runs"
        if not runs_dir.is_dir():
            self.skipTest("no research archives in this checkout")
        run_ids = sorted(path.name for path in runs_dir.iterdir()
                         if path.is_dir() and path.name.startswith("R"))
        self.assertGreaterEqual(len(run_ids), 1, "expected at least one archived run")
        failures = []
        for run_id in run_ids:
            try:
                loaded = research_run.load_run(run_id, ROOT)
            except Exception as exc:  # noqa: BLE001 - report every incompatibility
                failures.append((run_id, str(exc)[:200]))
                continue
            self.assertEqual(loaded["manifest"]["run_id"], run_id)
        self.assertEqual(failures, [], "archived runs must remain loadable: %r" % (failures,))

    def test_archives_are_not_modified_by_loading(self):
        runs_dir = ROOT / "journal" / "runs"
        if not runs_dir.is_dir():
            self.skipTest("no research archives in this checkout")
        run_ids = sorted(path.name for path in runs_dir.iterdir()
                         if path.is_dir() and path.name.startswith("R"))
        def snapshot():
            return {str(path.relative_to(runs_dir)): path.read_bytes()
                    for path in sorted(runs_dir.rglob("*")) if path.is_file()}

        before = snapshot()
        for run_id in run_ids:
            research_run.load_run(run_id, ROOT)
        after = snapshot()
        self.assertEqual(before, after)


    def test_archived_reports_render_exactly_as_frozen(self):
        """The current renderer must reproduce every frozen report.md / report.html."""
        runs_dir = ROOT / "journal" / "runs"
        if not runs_dir.is_dir():
            self.skipTest("no research archives in this checkout")
        failures = []
        for run_dir in sorted(path for path in runs_dir.iterdir() if path.is_dir() and path.name.startswith("R")):
            try:
                report = json.loads((run_dir / "report.json").read_text(encoding="utf-8"))
                claims = json.loads((run_dir / "claims.json").read_text(encoding="utf-8"))
                sources = json.loads((run_dir / "sources.json").read_text(encoding="utf-8"))
                markdown = render_report.render_markdown(report, claims, sources)
                page = render_report.render_html(report, claims, sources)
            except Exception as exc:  # noqa: BLE001 - report all render regressions
                failures.append((run_dir.name, "render error: " + str(exc)[:160]))
                continue
            for name, rendered in (("report.md", markdown), ("report.html", page)):
                frozen = run_dir / name
                if frozen.is_file() and frozen.read_text(encoding="utf-8") != rendered:
                    failures.append((run_dir.name, name + " differs from the frozen output"))
        self.assertEqual(failures, [], "frozen renders changed: %r" % (failures,))


if __name__ == "__main__":
    unittest.main()
