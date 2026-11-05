#!/usr/bin/env python3
"""Read frozen opportunity records; no fetching, background jobs or trading.

  opportunities.py list [--home PATH] [--history]
"""

import argparse
import json
import sys

from opportunity_contract import STATUSES
from research_run import list_runs, load_run


def list_opportunities(home=None, history=False):
    runs = [load_run(row["run_id"], home) for row in list_runs(home)]
    superseded = {run["manifest"].get("parent_run") for run in runs}
    rows = []
    for run in runs:
        manifest, report = run["manifest"], run["report"]
        if not history and manifest["run_id"] in superseded:
            continue
        opportunity = report.get("opportunity", {})
        if opportunity.get("applicability") != "trading":
            continue
        assessment = opportunity["assessment"]
        rows.append({"run_id": manifest["run_id"], "parent_run": manifest.get("parent_run"),
                     "title": report["title"], "as_of": report["as_of"],
                     "status": assessment["status"], "label": STATUSES[assessment["status"]],
                     "judgment": report["answer"]["text"], "reason": assessment["text"],
                     "catalyst": opportunity["catalyst"], "triggers": opportunity["triggers"],
                     "last_update": report.get("update", {}).get("opportunity")})
    priority = {status: index for index, status in enumerate(STATUSES)}
    return sorted(rows, key=lambda row: (priority[row["status"]], row["as_of"], row["run_id"]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["list"])
    parser.add_argument("--home")
    parser.add_argument("--history", action="store_true")
    args = parser.parse_args()
    try:
        print(json.dumps({"mode": "frozen_records", "note": "按归档截点读取；未刷新行情或检查触发。分支更新分别保留。", "opportunities": list_opportunities(args.home, args.history)}, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, TypeError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
