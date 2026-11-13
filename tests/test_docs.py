"""Relative links and script references in shipped docs must resolve."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [ROOT / "README.md"] + sorted((ROOT / "docs").rglob("*.md")) + sorted((ROOT / "skills").rglob("*.md"))
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
SCRIPT = re.compile(r"scripts/[A-Za-z0-9_]+\.py")
# The iteration log records history, including files that were later renamed.
HISTORICAL = {ROOT / "docs" / "iteration" / "log.md"}


class DocumentationTests(unittest.TestCase):
    def test_relative_links_resolve(self):
        broken = []
        for path in FILES:
            text = path.read_text(encoding="utf-8")
            for target in LINK.findall(text):
                target = target.strip().strip("<>")
                if target.startswith(("http://", "https://", "#", "mailto:")):
                    continue
                relative = target.split("#")[0]
                if not relative:
                    continue
                if not (path.parent / relative).resolve().exists():
                    broken.append((str(path.relative_to(ROOT)), target))
        self.assertEqual(broken, [], "broken relative links: %r" % (broken,))

    def test_script_references_exist(self):
        missing = []
        for path in FILES:
            if path in HISTORICAL:
                continue
            for script in sorted(set(SCRIPT.findall(path.read_text(encoding="utf-8")))):
                if not (ROOT / script).exists():
                    missing.append((str(path.relative_to(ROOT)), script))
        self.assertEqual(missing, [], "missing script references: %r" % (missing,))

    def test_documents_are_linked_from_an_index(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("docs/tutorial.md", readme)
        for name in ("architecture.md", "installation.md", "tutorial.md", "development.md"):
            self.assertIn(name, (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
                          if (ROOT / "docs" / "README.md").exists() else readme)


if __name__ == "__main__":
    unittest.main()
