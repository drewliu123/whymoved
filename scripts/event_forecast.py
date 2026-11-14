#!/usr/bin/env python3
"""List and score directional event forecasts."""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

DIRECTIONS = {"up", "down"}


def load(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or not isinstance(data.get("entries"), list):
        raise ValueError("event forecast file must have schema_version 1 and entries")
    return data


def save(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def score(data, forecast_id, close_price, scored_at=None):
    scored_at = scored_at or date.today().isoformat()
    entry = next((item for item in data["entries"] if item.get("id") == forecast_id), None)
    if entry is None:
        raise KeyError("unknown forecast: " + forecast_id)
    if entry.get("status") != "open":
        raise ValueError("forecast is already " + str(entry.get("status")))
    if scored_at < entry.get("horizon_end", ""):
        raise ValueError("cannot score before horizon_end " + str(entry.get("horizon_end")))
    if entry.get("direction") not in DIRECTIONS:
        raise ValueError("direction must be up or down")
    close_price = float(close_price)
    baseline = float(entry["baseline_price"])
    hit = close_price > baseline if entry["direction"] == "up" else close_price < baseline
    entry.update({"status": "hit" if hit else "miss", "close_price": close_price,
                  "return_pct": round((close_price / baseline - 1) * 100, 2), "scored_at": scored_at})
    return entry


def summary(data):
    counts = {"open": 0, "hit": 0, "miss": 0}
    for entry in data["entries"]:
        counts[entry.get("status", "open")] = counts.get(entry.get("status", "open"), 0) + 1
    return counts


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", default="predictions/events-2026.json")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    score_parser = sub.add_parser("score")
    score_parser.add_argument("--id", required=True)
    score_parser.add_argument("--close", type=float, required=True)
    score_parser.add_argument("--date", default=date.today().isoformat())
    args = parser.parse_args(argv)
    path = Path(args.file)
    data = load(path)
    if args.command == "list":
        for entry in data["entries"]:
            print("%s  %-5s  %-28s  %s  %s  baseline %s" % (entry["id"], entry.get("status", "open"),
                  entry.get("event", ""), entry.get("direction"), entry.get("confidence"), entry.get("baseline_price")))
        print("counts:", summary(data))
        return 0
    entry = score(data, args.id, args.close, args.date)
    save(path, data)
    print("%s: %s, return %.2f%% (close %s vs baseline %s)" % (entry["id"], entry["status"], entry["return_pct"], entry["close_price"], entry["baseline_price"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
