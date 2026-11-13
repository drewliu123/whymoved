"""Reference-class event study: window returns, skipped samples, boundaries."""

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import event_study

START = date(2025, 5, 1)


def series(closes):
    return [{"date": (START + timedelta(days=index)).isoformat(), "close": float(value)}
            for index, value in enumerate(closes)]


def sample(cid, closes, event_index, label="同类事件"):
    return {"id": cid, "date": (START + timedelta(days=event_index)).isoformat(),
            "label": label, "claim_ids": ["C1"], "prices": series(closes)}


def document(samples, before=2, after=2):
    return {"schema_version": 1, "event": "虚构事件类型", "window": {"before": before, "after": after},
            "samples": samples}


class ValidationTests(unittest.TestCase):
    def test_valid_document(self):
        self.assertEqual(event_study.validate_document(document([sample("E1", [100, 110, 120, 132, 144], 2),
                                                                sample("E2", [100, 100, 100, 90, 99], 2)])), [])

    def test_window_failures(self):
        for window in ({"before": 2, "after": 0}, {"before": -1, "after": 2},
                       {"before": 2, "after": 251}, {"before": 2.0, "after": 2},
                       {"before": 2}, {"before": 2, "after": 2, "extra": 1}, "nope"):
            doc = document([sample("E1", [1, 2, 3], 1), sample("E2", [1, 2, 3], 1)])
            doc["window"] = window if isinstance(window, dict) else window
            self.assertTrue(event_study.validate_document(doc), window)

    def test_sample_failures(self):
        base = [sample("E1", [1, 2, 3, 4, 5], 2), sample("E2", [1, 2, 3, 4, 5], 2)]
        cases = [
            lambda s: s.pop("id"),
            lambda s: s.update(id=""),
            lambda s: s.update(date=""),
            lambda s: s.update(extra=1),
            lambda s: s.update(claim_ids=[1]),
            lambda s: s.update(prices=[]),
            lambda s: s.update(prices=[{"date": "2025-05-01", "close": 100}]),
            lambda s: s.update(prices=[{"date": "2025-05-02", "close": 2},
                                       {"date": "2025-05-01", "close": 1},
                                       {"date": "2025-05-03", "close": 3}]),
            lambda s: s.update(prices=[{"date": "2025-05-01", "close": 0},
                                       {"date": "2025-05-02", "close": 1},
                                       {"date": "2025-05-03", "close": 2}]),
            lambda s: s.update(prices=[{"date": "2025-05-01", "close": 1},
                                       {"date": "2025-05-01", "close": 2},
                                       {"date": "2025-05-03", "close": 3}]),
            lambda s: s.update(prices=[{"date": "2025-05-01", "close": float("nan")},
                                       {"date": "2025-05-02", "close": 1},
                                       {"date": "2025-05-03", "close": 2}]),
        ]
        for mutate in cases:
            samples = json.loads(json.dumps(base))
            mutate(samples[0])
            self.assertTrue(event_study.validate_document(document(samples)), mutate)

    def test_duplicate_ids_and_too_few_samples(self):
        self.assertTrue(event_study.validate_document(document([sample("E1", [1, 2, 3], 1),
                                                                 sample("E1", [1, 2, 3], 1)])))
        self.assertTrue(event_study.validate_document(document([sample("E1", [1, 2, 3], 1)])))
        self.assertTrue(event_study.validate_document({"schema_version": 1, "event": "x", "window": {"before": 1, "after": 1},
                                                       "samples": "nope"}))


class AnalyseTests(unittest.TestCase):
    def doc(self):
        return document([sample("E1", [100, 110, 120, 132, 144, 158], 2),
                         sample("E2", [100, 100, 100, 90, 99, 108.9], 2)], before=2, after=2)

    def test_returns_and_summary(self):
        result = event_study.analyse(self.doc())
        first = result["samples"][0]
        self.assertAlmostEqual(first["pre_return"], 0.2)
        self.assertAlmostEqual(first["post_return"], 0.2)
        self.assertAlmostEqual(first["total_return"], 0.44)
        self.assertEqual((first["start_close"], first["event_close"], first["end_close"]), (100.0, 120.0, 144.0))
        post = result["summary"]["post_return"]
        self.assertEqual(post["n"], 2)
        self.assertAlmostEqual(post["mean"], (0.2 - 0.01) / 2)
        self.assertAlmostEqual(post["median"], 0.095)
        self.assertAlmostEqual(post["positive_rate"], 0.5)
        self.assertAlmostEqual(post["q1"], 0.0425)
        self.assertAlmostEqual(post["q3"], 0.1475)
        self.assertNotIn("p_value", json.dumps(result))
        self.assertTrue(any("不给p值" in note for note in result["notes"]))

    def test_window_edges_are_observations_not_calendar_days(self):
        result = event_study.analyse(document([sample("E1", [100, 120, 144], 1),
                                               sample("E2", [100, 120, 144], 1)], before=1, after=1))
        self.assertAlmostEqual(result["samples"][0]["post_return"], 144 / 120 - 1)
        result = event_study.analyse(document([sample("E1", [100, 120, 144], 1),
                                               sample("E2", [100, 120, 144], 1)], before=0, after=1))
        self.assertEqual(result["samples"][0]["pre_return"], 0)
        self.assertEqual(result["samples"][0]["start_close"], 120)

    def test_skipped_samples(self):
        samples = [sample("E1", [100, 110, 120, 132, 144], 2),
                   sample("E2", [100, 110, 120, 132, 144], 2),
                   sample("E3", [100, 110, 120, 132, 144], 0),
                   sample("E4", [100, 110, 120, 132, 144], 4),
                   sample("E5", [100, 110, 120, 132, 144], 2)]
        samples[4]["date"] = "2025-04-01"
        result = event_study.analyse(document(samples, before=2, after=2))
        reasons = {row["id"]: row["reason"] for row in result["skipped"]}
        self.assertEqual(len(result["samples"]), 2)
        self.assertIn("not enough observations before", reasons["E3"])
        self.assertIn("not enough observations after", reasons["E4"])
        self.assertIn("event date is not in the price series", reasons["E5"])
        self.assertEqual(len(reasons), 3)

    def test_fewer_than_two_usable_samples(self):
        samples = [sample("E1", [100, 110, 120, 132, 144], 2),
                   sample("E2", [100, 110, 120, 132, 144], 0)]
        with self.assertRaisesRegex(ValueError, "fewer than two usable samples"):
            event_study.analyse(document(samples, before=2, after=2))

    def test_non_finite_close_is_skipped_or_rejected(self):
        doc = self.doc()
        doc["samples"][0]["prices"][2]["close"] = float("nan")
        self.assertTrue(event_study.validate_document(doc))


class CliTests(unittest.TestCase):
    def run_cli(self, payload, *extra):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp).resolve() / "events.json"
            path.write_text(json.dumps(payload) if not isinstance(payload, str) else payload, encoding="utf-8")
            return subprocess.run([sys.executable, str(SCRIPTS / "event_study.py"), str(path), *extra],
                                  capture_output=True, text=True)

    def test_valid_cli_and_out(self):
        doc = document([sample("E1", [100, 110, 120, 132, 144], 2),
                        sample("E2", [100, 100, 100, 90, 99], 2)])
        process = self.run_cli(doc)
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        self.assertTrue(json.loads(process.stdout)["passed"])
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp).resolve() / "result.json"
            source = Path(tmp).resolve() / "events.json"
            source.write_text(json.dumps(doc), encoding="utf-8")
            process = subprocess.run([sys.executable, str(SCRIPTS / "event_study.py"), str(source),
                                      "--out", str(target)], capture_output=True, text=True)
            self.assertEqual(process.returncode, 0, process.stdout)
            self.assertTrue(target.exists())

    def test_failures(self):
        self.assertEqual(self.run_cli(document([sample("E1", [1, 2, 3], 1)])).returncode, 1)
        self.assertEqual(self.run_cli("{").returncode, 2)


if __name__ == "__main__":
    unittest.main()
