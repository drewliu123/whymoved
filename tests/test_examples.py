"""Committed examples must validate, render byte-identically and match their manifests."""

import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import render_report


def examples():
    base = ROOT / "examples"
    return sorted(path for path in base.iterdir()
                  if path.is_dir() and (path / "research/work/report.json").is_file())


def load(example, name):
    return json.loads((example / "research/work" / (name + ".json")).read_text(encoding="utf-8"))


class ExampleTests(unittest.TestCase):
    def test_examples_validate_and_render_frozen_output(self):
        cases = examples()
        self.assertGreaterEqual(len(cases), 2)
        for example in cases:
            with self.subTest(example=example.name):
                report, claims, sources = load(example, "report"), load(example, "claims"), load(example, "sources")
                self.assertEqual(render_report.validate_report(report, claims, sources), [])
                work = example / "research/work"
                self.assertEqual(render_report.render_markdown(report, claims, sources),
                                 (work / "report.md").read_text(encoding="utf-8"))
                self.assertEqual(render_report.render_html(report, claims, sources),
                                 (work / "report.html").read_text(encoding="utf-8"))
                plan = load(example, "plan")
                self.assertEqual(plan["analysis_version"], 1)

    def test_example_manifests_match_files(self):
        for example in examples():
            manifest_path = example / "SHA256.json"
            if not manifest_path.is_file():
                continue
            with self.subTest(example=example.name):
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                self.assertTrue(manifest)
                for relative, expected in manifest.items():
                    path = (example / relative).resolve()
                    self.assertTrue(str(path).startswith(str(example.resolve())), relative)
                    self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected, relative)


if __name__ == "__main__":
    unittest.main()
