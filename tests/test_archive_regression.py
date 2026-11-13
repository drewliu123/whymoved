"""Every archived research run must still load under the current validators.

This is the compatibility guard for a growing contract: new optional fields and
stricter rules must never make an existing `journal/runs/<run_id>` unreadable.
It reads the archives in place and never writes to them.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
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


if __name__ == "__main__":
    unittest.main()
