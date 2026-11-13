"""Cross-run research memory: pointer index, point-in-time query, archive safety."""

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
import research_memory as memory


def write_run(home, run_id, *, as_of, title="标题", question="问题", judgment="判断", entity="",
              plan_entity=None, metric_entity=None, parent=None, judgment_changed=None,
              trigger_due="2026-12-09", broken=False):
    run = Path(home) / "journal" / "runs" / run_id
    run.mkdir(parents=True)
    if broken:
        (run / "report.json").write_text("{", encoding="utf-8")
        return run
    report = {
        "schema_version": 2, "title": title, "question": question, "type": "asset", "task": "观察",
        "as_of": as_of, "answer": {"text": judgment, "claim_ids": ["C1"]},
        "findings": [{"title": "发现一", "text": "细节", "claim_ids": ["C1"]}],
        "alternatives": [], "watch": [], "limitations": [], "tables": [],
        "opportunity": {"version": 1, "applicability": "trading",
                        "assessment": {"status": "watch", "text": "说明", "claim_ids": ["C1"]},
                        "triggers": [{"id": "T1", "signal": "信号", "by": "窗口",
                                      "due": trigger_due, "claim_ids": ["C1"],
                                      "supports_if": "支持", "weakens_if": "削弱", "invalidates_if": "失效"}]},
        "analysis": {"version": 1, "models": [{"id": "M1", "spec": {"kind": "dcf"}}]},
    }
    if judgment_changed is not None:
        report["update"] = {"judgment_changed": judgment_changed, "reason": "更新",
                            "comparability": {"status": "comparable", "reason": "同口径"}}
    (run / "report.json").write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")
    plan = {"entity": plan_entity if plan_entity is not None else entity}
    (run / "plan.json").write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
    claims = {"claims": [{"id": "C1", "text": "事实", "type": "fact"},
                         {"id": "C2", "text": "事实二", "type": "fact",
                          "metric": {"name": "revenue", "entity": metric_entity}}]}
    (run / "claims.json").write_text(json.dumps(claims, ensure_ascii=False), encoding="utf-8")
    manifest = {"run_id": run_id, "as_of": as_of, "parent_run": parent}
    (run / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    return run


def snapshot(home):
    hashes = {}
    for path in sorted((Path(home) / "journal" / "runs").rglob("*")):
        if path.is_file():
            hashes[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


class IndexTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name).resolve()
        write_run(self.home, "R20261001T000000Z-aaaaaaaaaaaa", as_of="2026-10-01T00:00:00Z",
                  title="比特币下行", question="BTC 怎么看", entity="Bitcoin (BTC-USDT-SWAP)",
                  judgment="偏空但等信号", parent="R20260901T000000Z-ffffffffffff")
        write_run(self.home, "R20261101T000000Z-bbbbbbbbbbbb", as_of="2026-11-01T00:00:00Z",
                  title="英伟达估值", question="NVDA 贵吗", entity="NVDA", plan_entity="NVDA",
                  metric_entity="MSFT", judgment_changed=True)
        write_run(self.home, "R20261102T000000Z-cccccccccccc", as_of="2026-11-02T00:00:00Z", broken=True)

    def tearDown(self):
        self.tmp.cleanup()

    def index(self):
        return memory.build_index(self.home)

    def test_records_skips_and_entities(self):
        index = self.index()
        self.assertEqual(index["schema_version"], 1)
        self.assertEqual([run["run_id"] for run in index["runs"]],
                         ["R20261001T000000Z-aaaaaaaaaaaa", "R20261101T000000Z-bbbbbbbbbbbb"])
        self.assertEqual(index["skipped"][0]["run"], "R20261102T000000Z-cccccccccccc")
        self.assertIn("invalid report.json", index["skipped"][0]["reason"])
        self.assertEqual(index["entities"]["NVDA"], ["R20261101T000000Z-bbbbbbbbbbbb"])
        self.assertIn("Bitcoin (BTC-USDT-SWAP)", index["entities"])
        self.assertIn("MSFT", index["entities"])
        record = index["runs"][1]
        self.assertEqual(record["parent_run"], "")
        self.assertTrue(record["judgment_changed"])
        self.assertEqual(record["claim_count"], 2)
        self.assertEqual(record["model_kinds"], ["dcf"])
        self.assertEqual(record["triggers"], [{"id": "T1", "due": "2026-12-09"}])
        self.assertEqual(record["metric_names"], ["revenue"])
        self.assertEqual(len(record["report_sha256"]), 64)

    def test_index_is_rebuildable_and_archives_untouched(self):
        before = snapshot(self.home)
        first = self.index()
        second = self.index()
        self.assertEqual(first, second)
        self.assertEqual(first["index_hash"], second["index_hash"])
        self.assertEqual(before, snapshot(self.home))
        with tempfile.TemporaryDirectory() as out:
            path = Path(out) / "index.json"
            memory._write_index(first, path)
            bytes_once = path.read_bytes()
            memory._write_index(second, path)
            self.assertEqual(bytes_once, path.read_bytes())

    def test_missing_runs_directory(self):
        with tempfile.TemporaryDirectory() as empty:
            with self.assertRaises(FileNotFoundError):
                memory.build_index(empty)


class QueryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name).resolve()
        write_run(self.home, "R20261001T000000Z-aaaaaaaaaaaa", as_of="2026-10-01T00:00:00Z",
                  title="比特币下行", question="BTC 怎么看", entity="Bitcoin (BTC-USDT-SWAP)",
                  judgment="偏空但等信号")
        write_run(self.home, "R20261101T000000Z-bbbbbbbbbbbb", as_of="2026-11-01T00:00:00Z",
                  title="英伟达估值", question="NVDA 贵吗", entity="NVDA", plan_entity="NVDA")
        self.index = memory.build_index(self.home)

    def tearDown(self):
        self.tmp.cleanup()

    def test_term_matching_is_case_insensitive(self):
        for term in ("btc", "BTC", "bitcoin"):
            result = memory.query_index(self.index, term)
            self.assertEqual(result["count"], 1, term)
            self.assertEqual(result["matches"][0]["run_id"], "R20261001T000000Z-aaaaaaaaaaaa")

    def test_as_of_and_limit(self):
        result = memory.query_index(self.index, "e", as_of="2026-10-15T00:00:00Z")
        self.assertEqual([item["run_id"] for item in result["matches"]],
                         ["R20261001T000000Z-aaaaaaaaaaaa"])
        limited = memory.query_index(self.index, "e", limit=1)
        self.assertEqual(len(limited["matches"]), 1)
        self.assertEqual(limited["matches"][0]["run_id"], "R20261101T000000Z-bbbbbbbbbbbb")

    def test_empty_and_invalid_terms(self):
        with self.assertRaises(ValueError):
            memory.query_index(self.index, "   ")
        with self.assertRaises(ValueError):
            memory.query_index(self.index, "btc", as_of="not-a-date")

    def test_no_match(self):
        result = memory.query_index(self.index, "不存在的标的")
        self.assertEqual(result["count"], 0)
        self.assertEqual(result["matches"], [])


class CliTests(unittest.TestCase):
    def test_index_and_query_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp).resolve()
            write_run(home, "R20261101T000000Z-bbbbbbbbbbbb", as_of="2026-11-01T00:00:00Z",
                      title="比特币", question="BTC 怎么看", entity="BTC")
            process = subprocess.run([sys.executable, str(SCRIPTS / "research_memory.py"), "index", "--home", str(home)],
                                     capture_output=True, text=True)
            self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
            payload = json.loads(process.stdout)
            self.assertTrue(payload["passed"])
            self.assertTrue(Path(payload["written"]).exists())
            process = subprocess.run([sys.executable, str(SCRIPTS / "research_memory.py"), "query",
                                      "--home", str(home), "BTC"], capture_output=True, text=True)
            self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
            payload = json.loads(process.stdout)
            self.assertEqual(payload["count"], 1)
            self.assertTrue(payload["passed"])

    def test_cli_failures(self):
        with tempfile.TemporaryDirectory() as tmp:
            process = subprocess.run([sys.executable, str(SCRIPTS / "research_memory.py"), "index", "--home", tmp],
                                     capture_output=True, text=True)
            self.assertEqual(process.returncode, 2)
            home = Path(tmp).resolve()
            write_run(home, "R20261101T000000Z-bbbbbbbbbbbb", as_of="2026-11-01T00:00:00Z", entity="BTC")
            process = subprocess.run([sys.executable, str(SCRIPTS / "research_memory.py"), "query",
                                      "--home", str(home), "BTC", "--as-of", "nope"], capture_output=True, text=True)
            self.assertEqual(process.returncode, 1)


class RepositoryArchiveTests(unittest.TestCase):
    def test_committed_archives_index_readonly(self):
        index = memory.build_index(ROOT)
        self.assertGreaterEqual(len(index["runs"]), 1)
        for record in index["runs"]:
            self.assertTrue(record["run_id"])
            self.assertTrue(record["as_of"])
            self.assertEqual(len(record["report_sha256"]), 64)
        found = memory.query_index(index, "btc")
        self.assertGreaterEqual(found["count"], 1)


if __name__ == "__main__":
    unittest.main()
