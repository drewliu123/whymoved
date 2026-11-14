#!/usr/bin/env python3
"""List and score falsifiable predictions stored as JSON.$"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

DIRECTIONS = {"below", "above"}


def load(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or not isinstance(data.get("entries"), list):
        raise ValueError("prediction file must have schema_version 1 and entries")
    return data


def save(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def score(data, prediction_id, observed, scored_at=None):
    scored_at = scored_at or date.today().isoformat()
    entry = next((item for item in data["entries"] if item.get("id") == prediction_id), None)
    if entry is None:
        raise KeyError("unknown prediction: " + prediction_id)
    if entry.get("status") != "open":
        raise ValueError("prediction is already " + str(entry.get("status")))
    if scored_at < entry.get("horizon_end", ""):
        raise ValueError("cannot score before horizon_end " + str(entry.get("horizon_end")))
    direction = entry.get("direction")
    if direction not in DIRECTIONS:
        raise ValueError("direction must be below or above")
    threshold = float(entry["threshold"])
    observed = float(observed)
    hit = observed < threshold if direction == "below" else observed > threshold
    entry.update({"status": "hit" if hit else "miss", "observed": observed, "scored_at": scored_at})
    return entry


def summary(data):
    counts = {"open": 0, "hit": 0, "miss": 0}
    for entry in data["entries"]:
        counts[entry.get("status", "open")] = counts.get(entry.get("status", "open"), 0) + 1
    return counts


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", default="predictions/2026-11.json")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    score_parser = sub.add_parser("score")
    score_parser.add_argument("--id", required=True)
    score_parser.add_argument("--observed", type=float, required=True)
    score_parser.add_argument("--date", default=date.today().isoformat())
    args = parser.parse_args(argv)

    path = Path(args.file)
    data = load(path)
    if args.command == "list":
        for entry in data["entries"]:
            print("%s  %-8s  %-28s  %s %s %s  %s" % (
                entry["id"], entry.get("status", "open"), entry.get("example", ""),
                entry.get("direction"), entry.get("threshold"), entry.get("unit", ""),
                entry.get("forecast", "")))
        print("counts:", summary(data))
        return 0
    entry = score(data, args.id, args.observed, args.date)
    save(path, data)
    print("%s: %s (observed %s, threshold %s %s)" % (entry["id"], entry["status"], entry["observed"], entry["threshold"], entry.get("unit", "")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
