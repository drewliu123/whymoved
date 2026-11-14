"""Beta estimation from aligned series: arithmetic, alignment and CLI behaviour."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import beta

BENCH = [100, 102, 101, 104, 103, 106]


def exact_asset(bench_values, multiplier=2.0):
    values = [100.0]
    for previous, current in zip(bench_values, bench_values[1:]):
        values.append(values[-1] * (1 + multiplier * (current / previous - 1)))
    return values


def series(name, values):
    return {"name": name, "points": [{"date": "2024-01-%02d" % (index + 2), "value": value}
                                     for index, value in enumerate(values)]}


class EstimateTests(unittest.TestCase):
    def test_exact_beta_two(self):
        asset = exact_asset(BENCH)
        result = beta.estimate(series("asset", asset), series("bench", BENCH), min_observations=3)
        self.assertAlmostEqual(result["beta"], 2, places=9)
        self.assertAlmostEqual(result["r_squared"], 1, places=9)
        self.assertEqual(result["observations"], len(BENCH) - 1)

    def test_alignment_uses_intersection(self):
        asset = series("asset", [1, 2, 3, 4, 5, 6])
        asset["points"][0]["date"] = "2023-12-31"
        result = beta.estimate(asset, series("bench", BENCH), min_observations=3)
        self.assertEqual(result["start"], "2024-01-03")

    def test_rejects_short_or_bad_series(self):
        with self.assertRaisesRegex(ValueError, "common observations"):
            beta.estimate(series("a", BENCH), series("b", BENCH), min_observations=10)
        broken = series("a", BENCH)
        broken["points"][2]["value"] = 0
        with self.assertRaisesRegex(ValueError, "positive"):
            beta.estimate(broken, series("b", BENCH), min_observations=3)
        duplicated = series("a", BENCH)
        duplicated["points"][1]["date"] = duplicated["points"][0]["date"]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            beta.estimate(duplicated, series("b", BENCH), min_observations=3)

    def test_flat_benchmark_is_undefined(self):
        with self.assertRaisesRegex(ValueError, "zero variance"):
            beta.estimate(series("a", [1, 1.1, 1.2, 1.3]), series("b", [5, 5, 5, 5]), min_observations=2)


class CliTests(unittest.TestCase):
    def invoke(self, asset, benchmark, *extra):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            for name, document in (("asset", asset), ("bench", benchmark)):
                path = root / (name + ".json")
                path.write_text(json.dumps(document), encoding="utf-8")
            return subprocess.run([sys.executable, str(SCRIPTS / "beta.py"),
                                   str(root / "asset.json"), str(root / "bench.json"), *extra],
                                  capture_output=True, text=True)

    def test_json_cli(self):
        process = self.invoke(series("asset", exact_asset(BENCH)), series("bench", BENCH),
                              "--min-observations", "3")
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        payload = json.loads(process.stdout)
        self.assertAlmostEqual(payload["beta"], 2, places=9)

    def test_csv_cli_skips_blank_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "asset.csv").write_text("date,value\n2024-01-02,100\n2024-01-03,102\n2024-01-04,101\n2024-01-05,\n2024-01-08,104\n", encoding="utf-8")
            (root / "bench.csv").write_text("date,value\n2024-01-02,200\n2024-01-03,202\n2024-01-04,201\n2024-01-05,203\n2024-01-08,204\n", encoding="utf-8")
            process = subprocess.run([sys.executable, str(SCRIPTS / "beta.py"), str(root / "asset.csv"),
                                      str(root / "bench.csv"), "--csv", "--min-observations", "2"],
                                     capture_output=True, text=True)
            self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
            self.assertIn("beta", json.loads(process.stdout))

    def test_failures(self):
        process = self.invoke(series("a", [1, 2]), series("b", [1, 2]))
        self.assertEqual(process.returncode, 1)
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp).resolve() / "missing.json"
            process = subprocess.run([sys.executable, str(SCRIPTS / "beta.py"), str(missing), str(missing)],
                                     capture_output=True, text=True)
            self.assertEqual(process.returncode, 2)


if __name__ == "__main__":
    unittest.main()
