"""The walkthrough tutorial must stay executable; run its bash blocks verbatim."""

import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TUTORIAL = ROOT / "docs" / "tutorial.md"


def blocks():
    text = TUTORIAL.read_text(encoding="utf-8")
    return re.findall(r"```bash\n(.*?)```", text, re.S)


class TutorialTests(unittest.TestCase):
    def test_tutorial_has_expected_steps(self):
        found = blocks()
        self.assertGreaterEqual(len(found), 6)
        joined = "\n".join(found)
        for token in ("analysis_contract.py", "research_run.py", "doctor.py", "--renders",
                      "quality_inputs.py", "financial_quality.py", "memo_pack.py"):
            self.assertIn(token, joined)

    @unittest.skipUnless(shutil.which("bash"), "bash is required to execute the tutorial")
    def test_tutorial_commands_run(self):
        script = "\n".join(blocks()[1:])
        self.assertNotIn("sudo", script)
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, TY_DIR=str(ROOT), TOUYAN_HOME=str(Path(tmp).resolve() / "home"))
            process = subprocess.run(["bash", "-e", "-c", script], capture_output=True, text=True,
                                     env=env, cwd=str(ROOT), timeout=180)
            output = process.stdout + process.stderr
            self.assertEqual(process.returncode, 0, output[-3000:])
            for token in ("passed", "run_id", "renders_checked", "roic", "FY2025"):
                self.assertIn(token, output)


if __name__ == "__main__":
    unittest.main()
