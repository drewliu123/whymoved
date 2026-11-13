"""Relative links and script references in shipped docs must resolve."""

import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [ROOT / "README.md"] + sorted((ROOT / "docs").rglob("*.md")) + sorted((ROOT / "skills").rglob("*.md"))
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
SCRIPT = re.compile(r"scripts/[A-Za-z0-9_]+\.py")
# The iteration log records history, including files that were later renamed.
HISTORICAL = {ROOT / "docs" / "iteration" / "log.md"}


COMMAND = re.compile(r"scripts/([a-z_]+)\.py")
SUBCOMMAND = re.compile(r"[\"']?\s*([A-Za-z][A-Za-z0-9_-]*)")


def subcommands(script):
    """Top-level argparse subcommands, read from the usage block's last choice group."""
    process = subprocess.run([sys.executable, str(ROOT / "scripts" / script), "--help"],
                             capture_output=True, text=True)
    if process.returncode != 0:
        return set()
    usage = process.stdout.split("\n\n")[0]
    groups = re.findall(r"\{([a-zA-Z0-9_,\-]+)\}", usage)
    return set(groups[-1].split(",")) if groups else set()


class CommandReferenceTests(unittest.TestCase):
    def test_subcommand_parser_reads_positional_choices(self):
        names = subcommands("financial_data.py")
        self.assertIn("income", names, "positional subcommands must win over option choices")
        self.assertNotIn("annual", names)

    def test_documented_subcommands_exist(self):
        excluded = {ROOT / "docs" / "iteration" / name
                    for name in ("log.md", "backlog.md", "review-2026-11.md")}
        cache, problems = {}, []
        for path in FILES:
            if path in excluded or path in HISTORICAL:
                continue
            text = path.read_text(encoding="utf-8")
            for match in COMMAND.finditer(text):
                script = match.group(1) + ".py"
                if not (ROOT / "scripts" / script).exists():
                    continue
                token = SUBCOMMAND.match(text[match.end():match.end() + 120])
                if not token:
                    continue
                name = token.group(1)
                if script not in cache:
                    cache[script] = subcommands(script)
                allowed = cache[script]
                if allowed and name not in allowed:
                    problems.append((str(path.relative_to(ROOT)), script, name, sorted(allowed)))
        self.assertEqual(problems, [], "documented subcommands do not exist: %r" % (problems,))


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

    def test_architecture_lists_every_script(self):
        architecture = (ROOT / "docs" / "architecture.md").read_text(encoding="utf-8")
        missing = sorted(path.name for path in (ROOT / "scripts").glob("*.py")
                         if path.name not in architecture)
        self.assertEqual(missing, [], "scripts missing from docs/architecture.md: %r" % (missing,))

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
