"""Scoring rules for directional event forecasts."""

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("event_forecast", ROOT / "scripts" / "event_forecast.py")
event_forecast = importlib.util.module_from_spec(spec)
spec.loader.exec_module(event_forecast)


def entry(direction="up", baseline=100.0, horizon="2026-11-20"):
    return {"id": "E1", "event": "demo", "date": "2026-11-17", "ticker": "DEMO",
            "consensus": "c", "direction": direction, "confidence": "medium",
            "horizon_end": horizon, "baseline_price": baseline, "benchmark": "b",
            "variant_view": "v", "invalidation": "i", "status": "open"}


class EventForecastTests(unittest.TestCase):
    def test_up_hit_and_miss(self):
        data = {"schema_version": 1, "entries": [entry()]}
        self.assertEqual(event_forecast.score(data, "E1", 101.0, "2026-11-20")["status"], "hit")
        data = {"schema_version": 1, "entries": [entry()]}
        self.assertEqual(event_forecast.score(data, "E1", 100.0, "2026-11-20")["status"], "miss")

    def test_down_hit(self):
        data = {"schema_version": 1, "entries": [entry(direction="down")]}
        self.assertEqual(event_forecast.score(data, "E1", 99.0, "2026-11-20")["status"], "hit")

    def test_cannot_score_before_horizon(self):
        data = {"schema_version": 1, "entries": [entry()]}
        with self.assertRaises(ValueError):
            event_forecast.score(data, "E1", 101.0, "2026-11-18")

    def test_no_double_scoring(self):
        data = {"schema_version": 1, "entries": [entry()]}
        event_forecast.score(data, "E1", 101.0, "2026-11-20")
        with self.assertRaises(ValueError):
            event_forecast.score(data, "E1", 102.0, "2026-11-21")


if __name__ == "__main__":
    unittest.main()
