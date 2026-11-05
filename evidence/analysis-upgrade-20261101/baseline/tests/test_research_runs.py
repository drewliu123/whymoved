"""Run archive/update safety regressions; every write uses a temporary home.

Run: python3 -m unittest discover -s tests -p 'test_research_runs.py'
"""

import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from test_reports import AS_OF, SCRIPTS, documents
sys.path.insert(0, str(SCRIPTS))
import research_run


class ResearchRunsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()
        self.home = self.root / "home"
        self.report, self.ledger, self.sources = documents()
        self.plan = {"schema_version": 2, "question": self.report["question"], "type": "asset", "task": self.report["task"],
                     "as_of": AS_OF, "entity": "Example", "historical": False, "decision_needed": "Assess revenue", "prior_judgment": "Await disclosure",
                     "comparison": {"period": "Q3", "unit": "USD", "scope": "company"},
                     "hypotheses": [{"explanation": "Revenue increased", "discriminating_observation": "Official revenue"}],
                     "queries": [{"question": "What changed?", "query": "revenue", "source": "official", "purpose": "Check revenue"}],
                     "budget": {"max_queries": 1, "max_followups": 0}, "stop_condition": "Official disclosure read"}
        self.write()

    def tearDown(self):
        self.tmp.cleanup()

    def write(self):
        self.paths = []
        for name, value in (("report", self.report), ("claims", self.ledger), ("sources", self.sources), ("plan", self.plan)):
            path = self.root / (name + ".json")
            path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
            self.paths.append(path)

    def archive(self, **kw):
        self.write()
        return research_run.archive_run(*self.paths, home=self.home, **kw)

    def update(self, reason="新披露没有改变判断", changed=False, status="comparable"):
        self.report["update"] = {"judgment_changed": changed, "reason": reason, "comparability": {"status": status, "reason": "作者核对口径"}}

    def test_archive_without_forecast_does_not_touch_legacy_ledgers(self):
        (self.home / "data").mkdir(parents=True)
        (self.home / "journal").mkdir()
        authors = self.home / "data/authors.json"; authors.write_text("sentinel authors")
        memos = self.home / "journal/memos.jsonl"; memos.write_text("sentinel memos")
        result = self.archive()
        directory = Path(result["path"])
        self.assertEqual(set(p.name for p in directory.iterdir()), {"manifest.json", "report.json", "claims.json", "sources.json", "plan.json", "report.md", "report.html"})
        run = research_run.load_run(result["run_id"], self.home)
        self.assertEqual(run["report"], self.report)
        self.assertEqual(len(research_run.list_runs(self.home)), 1)
        self.assertEqual(authors.read_text(), "sentinel authors")
        self.assertEqual(memos.read_text(), "sentinel memos")
        self.report["title"] = "later edit"
        self.write()
        self.assertNotIn("later edit", (directory / "report.html").read_text())

    def test_new_archive_rejects_legacy_ledger_before_writes(self):
        self.ledger["schema_version"] = 1
        self.ledger["claims"][0]["sources"] = [copy.deepcopy(self.sources["candidates"][0])]
        self.assertEqual(research_run.validate_report(self.report, self.ledger, self.sources), [])
        with self.assertRaisesRegex(ValueError, "require claims schema_version 2"):
            self.archive()
        self.assertFalse((self.home / "journal/runs").exists())

    def test_list_ignores_normal_active_reservations(self):
        result = self.archive()
        reservation = self.home / "journal/runs" / (".reserve-" + result["run_id"])
        reservation.write_text("")
        self.assertEqual(len(research_run.list_runs(self.home)), 1)
        reservation.unlink()
        reservation.symlink_to(Path(result["path"]) / "report.json")
        with self.assertRaisesRegex(ValueError, "unexpected entry"):
            research_run.list_runs(self.home)

    def test_evidence_identity_fields_trigger_diff(self):
        parent = research_run.load_run(self.archive()["run_id"], self.home)
        self.update()
        for field, value in (("url", "https://example.com/replaced"), ("canonical_url", "https://example.com/canonical"), ("publisher", "Replacement Official"), ("tier", "T1")):
            with self.subTest(field=field):
                changed = copy.deepcopy(self.sources)
                changed["candidates"][0][field] = value
                if field == "tier":
                    extra = copy.deepcopy(changed["candidates"][0])
                    extra.update(id="S2", publisher="Independent", origin_id="O2", url="https://other.example.com/report", tier="T2")
                    changed["candidates"].append(extra)
                    ledger = copy.deepcopy(self.ledger)
                    ledger["claims"][0]["sources"].append({"source_id": "S2"})
                else:
                    ledger = self.ledger
                difference = research_run.compare_run(parent, self.report, ledger, changed)
                self.assertIn("S1", difference["evidence"]["changed"])

    def test_audit_is_frozen_hashed_metadata_and_safe_input(self):
        audit = {"queries": [{"query": "revenue"}], "review": {"findings": ["unverified user text"], "dispositions": []}, "execution": []}
        path = self.root / "audit.json"
        path.write_text(json.dumps(audit))
        result = self.archive(audit_path=path)
        self.assertEqual(research_run.load_run(result["run_id"], self.home)["audit"], audit)
        self.assertIn("audit.json", result["manifest"]["files"])
        self.assertEqual(result["manifest"]["audit_role"], "untrusted_metadata")
        path.write_text("[]")
        with self.assertRaisesRegex(ValueError, "audit must be a JSON object"):
            self.archive(audit_path=path)
        path.unlink(); path.symlink_to(self.paths[0])
        with self.assertRaisesRegex(ValueError, "symlink input"):
            self.archive(audit_path=path)
        (Path(result["path"]) / "audit.json").write_text("{}")
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            research_run.load_run(result["run_id"], self.home)

    def test_invalid_archive_has_no_success_directory(self):
        self.report["answer"]["claim_ids"] = ["missing"]
        with self.assertRaises(ValueError):
            self.archive()
        self.assertFalse((self.home / "journal/runs").exists())

    def test_duplicate_run_and_input_paths_refused(self):
        result = self.archive()
        before = (Path(result["path"]) / "manifest.json").read_bytes()
        with self.assertRaises(ValueError):
            self.archive(run_id=result["run_id"])
        self.assertEqual(before, (Path(result["path"]) / "manifest.json").read_bytes())
        with self.assertRaises(ValueError):
            research_run.archive_run(self.paths[0], self.paths[0], *self.paths[2:], home=self.home)
        with self.assertRaises(ValueError):
            research_run.load_run("../../outside", self.home)

    def test_source_and_output_symlinks_and_traversal_refused(self):
        linked = self.root / "linked.json"; linked.symlink_to(self.paths[0])
        with self.assertRaises(ValueError):
            research_run.archive_run(linked, *self.paths[1:], home=self.home)
        with self.assertRaises(ValueError):
            research_run.archive_run(self.root / "x/../report.json", *self.paths[1:], home=self.home)
        self.home.mkdir()
        (self.home / "journal").symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.archive()

    def test_failed_staging_is_cleaned(self):
        with patch.object(research_run.os, "rename", side_effect=OSError("simulated publication failure")):
            with self.assertRaises(OSError):
                self.archive()
        self.assertEqual(list((self.home / "journal/runs").iterdir()), [])

    def test_update_requires_parent_and_author_change_explanation(self):
        parent = self.archive()
        with self.assertRaises(ValueError):
            self.archive(parent_run=parent["run_id"])
        self.update()
        with self.assertRaises(ValueError):
            self.archive()
        before = (Path(parent["path"]) / "manifest.json").read_bytes()
        self.sources["candidates"][0]["quote"] = "New revenue quotation."
        self.ledger["claims"][0]["text"] = "Updated revenue statement."
        result = self.archive(parent_run=parent["run_id"])
        diff = result["diff"]
        self.assertEqual(diff["sources"]["changed"], ["S1"])
        self.assertEqual(diff["evidence"]["changed"], ["S1"])
        self.assertEqual(diff["claims"]["changed"], ["C1"])
        self.assertFalse(diff["judgment"]["judgment_changed"])
        self.assertEqual(before, (Path(parent["path"]) / "manifest.json").read_bytes())
        loaded = research_run.load_run(result["run_id"], self.home)
        self.assertEqual(loaded["manifest"]["parent_run"], parent["run_id"])
        self.assertEqual(loaded["diff"], diff)

    def test_changed_period_unit_scope_are_flagged(self):
        self.report["scope"] = "company"
        self.report["tables"][0]["unit"] = "USD"
        parent = self.archive()
        self.update()
        self.report["scope"] = "segment"
        self.report["tables"][0]["unit"] = "CNY"
        with self.assertRaisesRegex(ValueError, "period/unit/scope"):
            self.archive(parent_run=parent["run_id"])
        self.update(status="mixed")
        result = self.archive(parent_run=parent["run_id"])
        self.assertEqual(len(result["diff"]["comparability_issues"]), 2)

    def test_plan_comparison_differences_are_checked_on_update(self):
        parent = self.archive()
        self.update()
        self.plan["comparison"]["period"] = "Q4"
        with self.assertRaisesRegex(ValueError, "period/unit/scope"):
            self.archive(parent_run=parent["run_id"])
        self.update(status="mixed")
        child = self.archive(parent_run=parent["run_id"])
        self.assertEqual(child["diff"]["comparability_issues"][0]["path"], "plan.comparison.period")

    def test_added_removed_and_ranking_only_evidence_difference(self):
        parent = research_run.load_run(self.archive()["run_id"], self.home)
        self.update()
        self.sources["candidates"][0]["selection"]["reason"] = "reconsidered ranking"
        difference = research_run.compare_run(parent, self.report, self.ledger, self.sources)
        self.assertEqual(difference["sources"]["changed"], ["S1"])
        self.assertEqual(difference["evidence"]["changed"], [])
        self.assertEqual(research_run._changes([{"id": "A"}], [{"id": "B"}]), {"added": ["B"], "removed": ["A"], "changed": []})

    def test_tamper_and_manifest_path_escape_detected(self):
        result = self.archive()
        directory = Path(result["path"])
        (directory / "report.md").write_text("changed")
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            research_run.load_run(result["run_id"], self.home)
        manifest_path = directory / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["files"]["../outside"] = "0" * 64
        manifest_path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "inventory"):
            research_run.load_run(result["run_id"], self.home)

    def test_update_detects_parent_tamper(self):
        parent = self.archive()
        self.update()
        child = self.archive(parent_run=parent["run_id"])
        (Path(parent["path"]) / "sources.json").write_text("{}")
        with self.assertRaisesRegex(ValueError, "parent file changed"):
            research_run.load_run(child["run_id"], self.home)

    def test_cli_renderer_archive_show_list_and_diff(self):
        env = dict(os.environ, TOUYAN_HOME=str(self.home))
        def run(script, *args):
            result = subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)], env=env, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            return result
        output = self.root / "rendered"
        run("render_report.py", self.paths[0], "--claims", self.paths[1], "--sources", self.paths[2], "--out-dir", output)
        audit = self.root / "audit.json"
        audit.write_text('{"queries":[],"review":{"findings":[],"dispositions":[]},"execution":[]}')
        result = run("research_run.py", "archive", "--report", self.paths[0], "--claims", self.paths[1], "--sources", self.paths[2], "--plan", self.paths[3], "--audit", audit)
        archived = json.loads(result.stdout)
        self.assertIn("audit.json", archived["manifest"]["files"])
        self.assertEqual((output / "report.html").read_text(), (Path(archived["path"]) / "report.html").read_text())
        self.assertEqual(json.loads(run("research_run.py", "show", archived["run_id"]).stdout)["report"], self.report)
        self.assertEqual(len(json.loads(run("research_run.py", "list").stdout)), 1)
        self.update(); self.write()
        diff = json.loads(run("research_run.py", "diff", archived["run_id"], "--report", self.paths[0], "--claims", self.paths[1], "--sources", self.paths[2], "--plan", self.paths[3]).stdout)
        self.assertEqual(diff["claims"]["changed"], [])
        self.assertFalse((self.home / "journal/memos.jsonl").exists())
        self.assertFalse((self.home / "data/authors.json").exists())

    def test_optional_calculations_must_match_frozen_report(self):
        calc = self.root / "calculations.json"
        calc.write_text(json.dumps({"schema_version": 2, "as_of": AS_OF, "calculations": []}))
        result = self.archive(calculations_path=calc)
        self.assertIn("calculations.json", result["manifest"]["files"])
        calc.write_text(json.dumps({"schema_version": 2, "as_of": "wrong", "calculations": []}))
        with self.assertRaises(ValueError):
            self.archive(calculations_path=calc)


if __name__ == "__main__":
    unittest.main()
