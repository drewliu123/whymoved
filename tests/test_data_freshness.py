"""Every example must appear in the data-freshness table."""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DataFreshnessTests(unittest.TestCase):
    def test_every_example_is_listed(self):
        page = (ROOT / "docs" / "data-freshness.md").read_text(encoding="utf-8")
        for report_path in sorted((ROOT / "examples").glob("*/research/work/report.json")):
            name = report_path.parents[2].name
            self.assertIn(name, page, "%s is missing from data-freshness.md" % name)


if __name__ == "__main__":
    unittest.main()
