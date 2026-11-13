"""SEC retrieval entry point: configuration checks without network calls."""

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def invoke(*args, env=None):
    return subprocess.run([sys.executable, str(SCRIPTS / "sec_data.py"), *args],
                          capture_output=True, text=True, env=env, timeout=120)


def clean_env():
    env = dict(os.environ)
    env.pop("EDGAR_IDENTITY", None)
    return env


class SecCliTests(unittest.TestCase):
    def test_doctor_reports_provider_or_skips(self):
        process = invoke("doctor")
        if process.returncode != 0:
            self.skipTest("optional SEC runtime is not configured in this environment")
        payload = json.loads(process.stdout)
        self.assertEqual(payload["provider"], "edgartools")
        self.assertEqual(payload["status"], "ok")
        self.assertFalse(payload["data"]["sec_network_requested"])
        self.assertIn("Retrieval package, not sources/claims", " ".join(payload["notes"]))

    def test_filings_without_identity_makes_no_request(self):
        process = invoke("filings", "AAPL", "--limit", "1", env=clean_env())
        self.assertEqual(process.returncode, 2, process.stdout + process.stderr)
        payload = json.loads(process.stdout)
        self.assertEqual(payload["status"], "not_run")
        self.assertIn("EDGAR_IDENTITY", payload["reason"])
        self.assertIsNone(payload["data"])

    def test_unknown_subcommand_is_rejected(self):
        process = invoke("lookup", "AAPL")
        self.assertEqual(process.returncode, 2)
        self.assertNotIn("Traceback", process.stdout + process.stderr)


if __name__ == "__main__":
    unittest.main()
