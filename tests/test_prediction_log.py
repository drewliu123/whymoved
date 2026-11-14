"""Scoring rules for the falsifiable prediction log."""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("prediction_log", ROOT / "scripts" / "prediction_log.py")
prediction_log = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prediction_log)


def entry(direction="below", threshold=33.0, horizon="2027-07-31"):
    return {"id": "P1", "example": "demo", "metric": "capex/revenue", "threshold": threshold,
            "direction": direction, "unit": "%", "consensus": "c", "forecast": "f",
            "horizon_end": horizon, "benchmark": "b", "invalidation": "i", "status": "open"}


class PredictionScoringTests(unittest.TestCase):
    def test_below_hit_and_miss(self):
        data = {"schema_version": 1, "entries": [entry()]}
        self.assertEqual(prediction_log.score(data, "P1", 32.0, "2027-08-01")["status"], "hit")
        data = {"schema_version": 1, "entries": [entry()]}
        self.assertEqual(prediction_log.score(data, "P1", 33.0, "2027-08-01")["status"], "miss")

    def test_above_hit(self):
        data = {"schema_version": 1, "entries": [entry(direction="above", threshold=18.0)]}
        self.assertEqual(prediction_log.score(data, "P1", 19.0, "2027-08-01")["status"], "hit")

    def test_cannot_score_before_horizon(self):
        data = {"schema_version": 1, "entries": [entry()]}
        with self.assertRaises(ValueError):
            prediction_log.score(data, "P1", 32.0, "2027-01-01")

    def test_unknown_id(self):
        data = {"schema_version": 1, "entries": [entry()]}
        with self.assertRaises(KeyError):
            prediction_log.score(data, "P9", 32.0, "2027-08-01")

    def test_no_double_scoring(self):
        data = {"schema_version": 1, "entries": [entry()]}
        prediction_log.score(data, "P1", 32.0, "2027-08-01")
        with self.assertRaises(ValueError):
            prediction_log.score(data, "P1", 31.0, "2027-08-02")


if __name__ == "__main__":
    unittest.main()
