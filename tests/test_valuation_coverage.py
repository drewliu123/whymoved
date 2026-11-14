"""Valuation-coverage page must list every example that carries price claims."""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ValuationCoverageTests(unittest.TestCase):
    def test_every_priced_example_is_listed(self):
        page = (ROOT / "docs" / "valuation-coverage.md").read_text(encoding="utf-8")
        for report_path in sorted((ROOT / "examples").glob("*/research/work/report.json")):
            claims = json.loads((report_path.parent / "claims.json").read_text(encoding="utf-8"))
            if not any(claim.get("type") == "price" for claim in claims["claims"]):
                continue
            name = report_path.parents[2].name
            self.assertIn(name, page, "%s has price claims but is missing from valuation-coverage.md" % name)


if __name__ == "__main__":
    unittest.main()
