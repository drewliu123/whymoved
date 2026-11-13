"""Release consistency: one version across manifests and a changelog entry for it."""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PackagingTests(unittest.TestCase):
    def manifests(self):
        plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        market = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        return plugin, market

    def test_manifest_versions_agree(self):
        plugin, market = self.manifests()
        versions = {plugin["version"]} | {entry["version"] for entry in market["plugins"]}
        self.assertEqual(len(versions), 1, versions)

    def test_changelog_documents_the_released_version(self):
        plugin, _ = self.manifests()
        text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        headings = re.findall(r"^## (\S+)", text, re.MULTILINE)
        self.assertIn(plugin["version"], headings)
        self.assertEqual(headings[0], plugin["version"], "newest changelog entry must match the release")

    def test_documented_entry_points_exist(self):
        architecture = (ROOT / "docs/architecture.md").read_text(encoding="utf-8")
        links = re.findall(r"\]\(\.\./(scripts/[^)]+)\)", architecture)
        self.assertTrue(links)
        for link in links:
            self.assertTrue((ROOT / link).exists(), link)

    def test_readme_links_resolve(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        for target in re.findall(r"\]\((?!#)([^)h][^)]*)\)", text):
            path = target.split("#")[0]
            if not path:
                continue
            self.assertTrue((ROOT / path).exists(), target)


if __name__ == "__main__":
    unittest.main()
