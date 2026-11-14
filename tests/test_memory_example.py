"""The committed memory-workflow example must replay thread and digest exactly."""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "memory-workflow"
SCRIPTS = ROOT / "scripts"
CHILD = "R20261114T062832Z-83a837b1bc84"
PARENT = "R20261114T062832Z-c67a8ff09ba8"


class MemoryWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name).resolve() / "home"
        shutil.copytree(EXAMPLE / "home", self.home)

    def tearDown(self):
        self.tmp.cleanup()

    def test_archives_carry_parent_link(self):
        manifest = json.loads((self.home / "journal" / "runs" / CHILD / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["parent_run"], PARENT)
        self.assertEqual(manifest["run_id"], CHILD)

    def test_thread_matches_frozen_output(self):
        process = subprocess.run([sys.executable, str(SCRIPTS / "research_memory.py"), "index", "--home", str(self.home)],
                                 capture_output=True, text=True)
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        process = subprocess.run([sys.executable, str(SCRIPTS / "research_memory.py"), "thread", "--home", str(self.home), CHILD],
                                 capture_output=True, text=True)
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        self.assertEqual(json.loads(process.stdout), json.loads((EXAMPLE / "thread.json").read_text(encoding="utf-8")))

    def test_digest_matches_frozen_output(self):
        process = subprocess.run([sys.executable, str(SCRIPTS / "digest.py"), "--home", str(self.home),
                                  "--as-of", "2026-11-14", "--days", "30"], capture_output=True, text=True)
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        self.assertEqual(process.stdout, (EXAMPLE / "digest.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
