"""Tests for the evidence checker, journal and author library.

Run: python3 -m unittest discover -s tests
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"


def run(script: str, *args, home: str, stdin: str | None = None):
    env = {**os.environ, "TOUYAN_HOME": home}
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        capture_output=True, text=True, env=env, input=stdin,
    )


def src(tier="T0", publisher="BLS", published_at="2026-10-14", url="https://example.com/a"):
    return {"url": url, "publisher": publisher, "tier": tier, "published_at": published_at}


def claim(cid="C1", ctype="fact", text="CPI 同比 3.7%", sources=None, **extra):
    return {"id": cid, "text": text, "type": ctype, "as_of": "2026-10-26T03:00:00Z",
            "sources": [src()] if sources is None else sources, **extra}


class CheckClaimsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def check(self, claims):
        path = Path(self.home) / "claims.json"
        path.write_text(json.dumps({"claims": claims}, ensure_ascii=False), encoding="utf-8")
        result = run("check_claims.py", str(path), "--json", home=self.home)
        return result.returncode, json.loads(result.stdout)

    def test_valid_ledger_passes(self):
        code, out = self.check([
            claim(),
            claim("C2", "price", "按兵不动 93.5%", [src("T0", "Polymarket")]),
            claim("C3", "view", "有交易者认为定价偏高", [src("T4", "@fort1kkk")]),
            claim("C4", "inference", "分歧在 12 月", [], basis=["C1", "C2"]),
        ])
        self.assertEqual(code, 0, out)

    def test_fact_needs_official_or_two_publishers(self):
        code, out = self.check([claim(sources=[src("T2", "Reuters")])])
        self.assertEqual(code, 1)
        self.assertIn("R2", out["failures"]["C1"][0])
        code, _ = self.check([claim(sources=[src("T2", "Reuters"), src("T2", "Bloomberg", url="https://b")])])
        self.assertEqual(code, 0)

    def test_same_publisher_twice_is_one_source(self):
        code, _ = self.check([claim(sources=[src("T2", "Reuters"), src("T2", "reuters", url="https://b")])])
        self.assertEqual(code, 1)

    def test_price_from_media_rejected(self):
        code, out = self.check([claim(ctype="price", sources=[src("T2", "CNBC")])])
        self.assertEqual(code, 1)
        self.assertTrue(any("R3" in e for e in out["failures"]["C1"]))

    def test_community_only_must_be_view(self):
        code, out = self.check([claim(ctype="consensus", sources=[src("T4", "@someone")])])
        self.assertEqual(code, 1)
        self.assertTrue(any("R5" in e for e in out["failures"]["C1"]))

    def test_generalizing_word_needs_three_publishers(self):
        code, out = self.check([claim(ctype="view", text="拿历史先例对照价格是常见思路",
                                      sources=[src("T4", "@fort1kkk")])])
        self.assertEqual(code, 1)
        self.assertTrue(any("R6" in e for e in out["failures"]["C1"]))

    def test_inference_requires_existing_basis(self):
        code, out = self.check([claim(ctype="inference", sources=[], basis=["C9"])])
        self.assertEqual(code, 1)
        self.assertTrue(any("R7" in e for e in out["failures"]["C1"]))

    def test_look_ahead_source_rejected(self):
        code, out = self.check([claim(sources=[src(published_at="2026-10-29")])])
        self.assertEqual(code, 1)
        self.assertTrue(any("R8" in e for e in out["failures"]["C1"]))

    def test_unknown_publish_date_is_allowed(self):
        code, _ = self.check([claim(sources=[src(published_at="unknown")])])
        self.assertEqual(code, 0)


class JournalAndAuthorsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = self.tmp.name
        memo = {
            "question": "10 月议息会加息吗？", "type": "event_pricing", "as_of": "2026-10-26T03:00:00Z",
            "hypotheses": [{
                "id": "H1", "text": "10 月维持不变", "verify_by": "2026-10-28", "falsify_if": "宣布加息",
                "my_prob": 0.95, "market_prob": 0.935,
                "authors": [{"handle": "fort1kkk", "platform": "x", "stance": "oppose"},
                            {"handle": "bull", "platform": "x", "stance": "support"}],
            }],
        }
        self.memo_path = Path(self.home) / "memo.json"
        self.memo_path.write_text(json.dumps(memo, ensure_ascii=False), encoding="utf-8")
        self.claims_path = Path(self.home) / "claims.json"
        self.write_claims([claim(), claim("C2", "price", "按兵不动 93.5%", [src("T0", "Polymarket")])])
        self.report_path = Path(self.home) / "memo.md"
        self.report_path.write_text("一句话：10 月不动已被定价 [C2]", encoding="utf-8")
        self.plan_path = Path(self.home) / "plan.json"
        self.plan_path.write_text('{"angles": []}', encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def write_claims(self, claims):
        self.claims_path.write_text(json.dumps({"claims": claims}, ensure_ascii=False), encoding="utf-8")

    def add(self, *extra):
        return run("journal.py", "add", str(self.memo_path), "--claims", str(self.claims_path),
                   "--report", str(self.report_path), *extra, home=self.home)

    def memo_id(self):
        rows = (Path(self.home) / "journal" / "memos.jsonl").read_text(encoding="utf-8").splitlines()
        return json.loads(rows[-1])["memo_id"]

    def authors(self):
        return json.loads((Path(self.home) / "data" / "authors.json").read_text(encoding="utf-8"))["authors"]

    def test_add_archives_memo_ledger_and_plan(self):
        r = self.add("--plan", str(self.plan_path))
        self.assertEqual(r.returncode, 0, r.stderr)
        archive = Path(self.home) / "journal" / self.memo_id()
        self.assertEqual(sorted(p.name for p in archive.iterdir()),
                         ["claims.json", "memo.json", "memo.md", "plan.json"])
        self.assertEqual((archive / "memo.md").read_text(encoding="utf-8"), self.report_path.read_text(encoding="utf-8"))
        # The archive survives the next run overwriting the tmp files.
        self.report_path.write_text("下一次研究", encoding="utf-8")
        self.assertIn("10 月不动", (archive / "memo.md").read_text(encoding="utf-8"))
        self.assertIn("memo.md", run("journal.py", "show", self.memo_id(), home=self.home).stdout)

    def test_add_rejects_failing_ledger(self):
        self.write_claims([claim(ctype="price", sources=[src("T2", "CNBC")])])
        r = self.add()
        self.assertEqual(r.returncode, 1)
        self.assertIn("没通过校验", r.stderr)
        self.assertFalse((Path(self.home) / "journal" / "memos.jsonl").exists())

    def test_add_requires_ledger_and_report(self):
        missing = run("journal.py", "add", str(self.memo_path), home=self.home)
        self.assertNotEqual(missing.returncode, 0)
        self.report_path.unlink()
        self.assertEqual(self.add().returncode, 1)

    def test_add_due_grade_stats(self):
        self.assertEqual(self.add().returncode, 0)
        mid = self.memo_id()
        self.assertIn("没有到期", run("journal.py", "due", "--today", "2026-10-27", home=self.home).stdout)
        self.assertIn("H1", run("journal.py", "due", "--today", "2026-10-28", home=self.home).stdout)

        r = run("journal.py", "grade", mid, "H1", "hit", "--note", "维持不变", home=self.home)
        self.assertEqual(r.returncode, 0, r.stderr)
        a = self.authors()
        self.assertEqual((a["x:fort1kkk"]["hits"], a["x:fort1kkk"]["misses"]), (0, 1))
        self.assertEqual((a["x:bull"]["hits"], a["x:bull"]["misses"]), (1, 0))

        stats = run("journal.py", "stats", home=self.home).stdout
        self.assertIn("比市场更准", stats)

    def test_grade_is_append_only(self):
        self.add()
        mid = self.memo_id()
        run("journal.py", "grade", mid, "H1", "hit", home=self.home)
        again = run("journal.py", "grade", mid, "H1", "miss", home=self.home)
        self.assertEqual(again.returncode, 1)
        self.assertIn("只追加", again.stderr)

    def test_void_skips_author_grading(self):
        self.add()
        run("journal.py", "grade", self.memo_id(), "H1", "void", home=self.home)
        self.assertFalse((Path(self.home) / "data" / "authors.json").exists())

    def test_author_promotion_and_demotion(self):
        for i, outcome in enumerate(["hit", "hit", "miss"]):
            run("authors.py", "grade", "good", "--memo", f"M{i}", outcome, home=self.home)
        for i in range(3):
            run("authors.py", "grade", "bad", "--memo", f"M{i}", "miss", home=self.home)
        a = self.authors()
        self.assertEqual(a["x:good"]["status"], "core")
        self.assertEqual(a["x:bad"]["status"], "demoted")

    def test_author_grade_once_per_memo(self):
        run("authors.py", "grade", "dup", "--memo", "M1", "hit", home=self.home)
        run("authors.py", "grade", "dup", "--memo", "M1", "hit", home=self.home)
        self.assertEqual(self.authors()["x:dup"]["hits"], 1)


class ForecastTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = self.tmp.name
        self.claims_path = Path(self.home) / "claims.json"
        self.claims_path.write_text(json.dumps({"claims": [claim(), claim("C2", "price", "按兵不动 93.5%", [src("T0", "Polymarket")])]},
                                               ensure_ascii=False), encoding="utf-8")
        self.fc_path = Path(self.home) / "forecast.json"

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, **overrides):
        fc = {"hypothesis_id": "H1", "mode": "market", "question": "10 月 28 日维持利率不变？",
              "yes_means": "FOMC 声明维持 3.75–4.00%", "window_start": "2026-10-26", "window_end": "2026-10-28",
              "resolution_source": "federalreserve.gov", "trials": [0.95, 0.96, 0.94],
              "market_prob": 0.935, "market_source": "Polymarket", "evidence_ids": ["C1", "C2"], **overrides}
        self.fc_path.write_text(json.dumps({"as_of": "2026-10-26T03:00:00Z", "forecasts": [fc]}, ensure_ascii=False),
                                encoding="utf-8")

    def forecast(self, cmd):
        return run("forecast.py", cmd, str(self.fc_path), "--claims", str(self.claims_path), home=self.home)

    def final(self):
        return json.loads(self.fc_path.read_text(encoding="utf-8"))["forecasts"][0]

    def test_market_mode_uses_the_price(self):
        self.write()
        r = self.forecast("finalize")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.final()["final_prob"], 0.935)  # model trials do not move it
        self.assertEqual(self.forecast("check").returncode, 0)

    def test_independent_mode_averages_and_clips(self):
        self.write(mode="independent", trials=[0.8, 0.7, 0.9], market_prob=None, market_source=None)
        self.assertEqual(self.forecast("finalize").returncode, 0)
        self.assertEqual(self.final()["final_prob"], 0.8)
        self.write(mode="independent", trials=[1.0, 1.0, 0.99], market_prob=None, market_source=None)
        self.forecast("finalize")
        self.assertEqual(self.final()["final_prob"], 0.97)

    def test_independent_mode_needs_three_trials(self):
        self.write(mode="independent", trials=[0.5], market_prob=None, market_source=None)
        self.assertIn("至少 3", self.forecast("finalize").stderr)

    def test_market_mode_requires_price(self):
        self.write(market_prob=None)
        r = self.forecast("finalize")
        self.assertEqual(r.returncode, 1)
        self.assertIn("market_prob", r.stderr)

    def test_rejects_bad_trials_and_unknown_evidence(self):
        self.write(mode="independent", trials=[1.2, 0.5, 0.5], evidence_ids=["C9"])
        r = self.forecast("finalize")
        self.assertEqual(r.returncode, 1)
        self.assertIn("trials", r.stderr)
        self.assertIn("C9", r.stderr)

    def test_window_already_closed_is_not_a_forecast(self):
        self.write(window_start="2026-09-01", window_end="2026-09-30")
        self.assertIn("已结束", self.forecast("finalize").stderr)

    def test_check_detects_hand_edited_probability_and_ledger_change(self):
        self.write()
        self.forecast("finalize")
        doc = json.loads(self.fc_path.read_text(encoding="utf-8"))
        doc["forecasts"][0]["final_prob"] = 0.99
        self.fc_path.write_text(json.dumps(doc), encoding="utf-8")
        self.assertIn("重算", self.forecast("check").stderr)
        self.forecast("finalize")
        ledger = json.loads(self.claims_path.read_text(encoding="utf-8"))
        ledger["claims"][0]["text"] = "CPI 同比 4.1%"
        self.claims_path.write_text(json.dumps(ledger, ensure_ascii=False), encoding="utf-8")
        self.assertIn("改动", self.forecast("check").stderr)


class JournalForecastTest(JournalAndAuthorsTest):
    def write_forecast(self, trials=(0.95, 0.95, 0.95)):
        # The memo fixture registers my_prob 0.95, so an independent forecast averaging 0.95 matches it.
        fc = {"hypothesis_id": "H1", "mode": "independent", "question": "10 月维持不变", "yes_means": "维持",
              "window_start": "2026-10-26", "window_end": "2026-10-28", "resolution_source": "Fed",
              "trials": list(trials), "evidence_ids": ["C1"]}
        path = Path(self.home) / "forecast.json"
        path.write_text(json.dumps({"as_of": "2026-10-26T03:00:00Z", "forecasts": [fc]}), encoding="utf-8")
        run("forecast.py", "finalize", str(path), "--claims", str(self.claims_path), home=self.home)
        return path

    def test_add_archives_matching_forecast(self):
        path = self.write_forecast()
        r = self.add("--forecast", str(path))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((Path(self.home) / "journal" / self.memo_id() / "forecast.json").exists())
        run("journal.py", "grade", self.memo_id(), "H1", "hit", home=self.home)
        self.assertIn("独立判断 1 条", run("journal.py", "stats", home=self.home).stdout)

    def test_add_rejects_memo_prob_that_differs_from_forecast(self):
        path = self.write_forecast((0.9, 0.9, 0.9))
        r = self.add("--forecast", str(path))
        self.assertEqual(r.returncode, 1)
        self.assertIn("不一致", r.stderr)


if __name__ == "__main__":
    unittest.main()
