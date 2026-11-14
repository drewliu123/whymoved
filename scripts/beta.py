#!/usr/bin/env python3
"""Estimate a market beta from two aligned daily series (Python 3.9+).

A benchmark-adjusted event study needs a beta, and a beta needs a stated
estimation window. This script takes two series of observations and returns the
OLS slope of the asset's simple returns on the benchmark's simple returns,
plus R², sample size and dates. It is arithmetic on the supplied data, not a
prediction or a risk model: it does not annualize, adjust for thin trading, or
choose the window for you.

Input (one file per series):

    {"name": "S&P 500", "points": [{"date": "2024-01-02", "value": 4742.83}, ...]}

    python3 "$TY_DIR/scripts/beta.py" asset.json benchmark.json [--min-observations 30]

Exit codes: 0 success, 1 insufficient or invalid observations, 2 unreadable input.
"""

import argparse
import csv
import json
import math
import sys
from pathlib import Path


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    try:
        return value if math.isfinite(value) else None
    except OverflowError:
        return None


def _series(document):
    """Return (name, {date: value}) or raise ValueError."""
    if not isinstance(document, dict):
        raise ValueError("series must be an object")
    points = document.get("points")
    if not isinstance(points, list) or len(points) < 2:
        raise ValueError("series.points must contain at least two observations")
    name = document.get("name")
    name = name.strip() if _text(name) else ""
    values = {}
    for point in points:
        if not isinstance(point, dict) or not _text(point.get("date")):
            raise ValueError("each point needs a date")
        date = point["date"].strip()
        if date in values:
            raise ValueError("duplicate observation date: " + date)
        value = _number(point.get("value"))
        if value is None or value <= 0:
            raise ValueError("values must be positive finite numbers")
        values[date] = value
    return name, values


def _series_from_csv(path):
    """Read a two-column CSV (date, value); a header row is skipped."""
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.reader(handle))
    except OSError as exc:
        raise ValueError(str(exc)) from exc
    points = []
    for index, row in enumerate(rows):
        if len(row) < 2:
            continue
        date, raw = row[0].strip(), row[1].strip()
        if not date or raw in ("", "."):
            continue
        try:
            value = float(raw)
        except ValueError:
            if index == 0:
                continue  # header row
            raise ValueError("non-numeric value in row: " + ",".join(row))
        points.append({"date": date, "value": value})
    return {"name": path.stem, "points": points}


def estimate(asset_document, benchmark_document, min_observations=30):
    """Return beta, R² and sample metadata; raises ValueError for unusable input."""
    asset_name, asset = _series(asset_document)
    benchmark_name, benchmark = _series(benchmark_document)
    common = sorted(set(asset) & set(benchmark))
    if len(common) < min_observations + 1:
        raise ValueError("only %d common observations; need at least %d" % (len(common), min_observations + 1))
    asset_returns, benchmark_returns = [], []
    for previous, current in zip(common, common[1:]):
        asset_returns.append(asset[current] / asset[previous] - 1)
        benchmark_returns.append(benchmark[current] / benchmark[previous] - 1)
    count = len(benchmark_returns)
    mean_asset = sum(asset_returns) / count
    mean_benchmark = sum(benchmark_returns) / count
    covariance = sum((a - mean_asset) * (b - mean_benchmark) for a, b in zip(asset_returns, benchmark_returns))
    variance = sum((b - mean_benchmark) ** 2 for b in benchmark_returns)
    if variance == 0:
        raise ValueError("benchmark returns have zero variance; beta is undefined")
    beta = covariance / variance
    asset_variance = sum((a - mean_asset) ** 2 for a in asset_returns)
    r_squared = (covariance ** 2) / (variance * asset_variance) if asset_variance else 0.0
    return {"passed": True,
            "asset": asset_name or "asset", "benchmark": benchmark_name or "benchmark",
            "beta": beta, "r_squared": r_squared, "observations": count,
            "start": common[0], "end": common[-1],
            "notes": ["OLS slope of simple daily returns; no annualization, thin-trading or regime adjustment.",
                      "The estimation window is the intersection of the two supplied series; it is not chosen here."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("asset", type=Path)
    parser.add_argument("benchmark", type=Path)
    parser.add_argument("--min-observations", dest="min_observations", type=int, default=30)
    parser.add_argument("--csv", action="store_true", help="read two-column CSV files instead of JSON")
    args = parser.parse_args()
    if args.min_observations < 2:
        print(json.dumps({"passed": False, "errors": ["--min-observations must be at least 2"]}, ensure_ascii=False))
        return 1
    documents = []
    for path in (args.asset, args.benchmark):
        try:
            documents.append(_series_from_csv(path) if args.csv else json.loads(path.read_text(encoding="utf-8")))
        except (OSError, ValueError) as exc:
            print(json.dumps({"passed": False, "errors": [str(exc)], "path": str(path)}, ensure_ascii=False))
            return 2
    try:
        result = estimate(documents[0], documents[1], args.min_observations)
    except (ValueError, TypeError) as exc:
        print(json.dumps({"passed": False, "errors": [str(exc)]}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
