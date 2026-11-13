"""Optional adapters must fail closed when unconfigured and reject bad usage."""

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def invoke(name, *args, env=None):
    return subprocess.run([sys.executable, str(SCRIPTS / name), *args],
                          capture_output=True, text=True, env=env, timeout=120)


def without(*names):
    env = dict(os.environ)
    for name in names:
        env.pop(name, None)
    return env


class FinancialDataTests(unittest.TestCase):
    def test_missing_api_key_fails_closed(self):
        process = invoke("financial_data.py", "snapshot", "AAPL",
                         env=without("FINANCIAL_DATASETS_API_KEY"))
        self.assertEqual(process.returncode, 2, process.stdout + process.stderr)
        payload = json.loads(process.stdout)
        self.assertEqual(payload["status"], "not_run")
        self.assertEqual(payload["access_mode"], "unconfigured")
        self.assertIn("FINANCIAL_DATASETS_API_KEY", payload["reason"])
        self.assertIsNone(payload["data"])
        self.assertNotIn("Traceback", process.stdout + process.stderr)


class PolymarketTests(unittest.TestCase):
    def test_unknown_subcommand_is_rejected(self):
        process = invoke("polymarket.py", "lookup", "fed")
        self.assertEqual(process.returncode, 2)
        self.assertNotIn("Traceback", process.stdout + process.stderr)

    def test_help_lists_both_commands(self):
        process = invoke("polymarket.py", "--help")
        self.assertEqual(process.returncode, 0)
        self.assertIn("search", process.stdout)
        self.assertIn("event", process.stdout)


if __name__ == "__main__":
    unittest.main()
