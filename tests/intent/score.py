#!/usr/bin/env python3
"""Score offline intent decisions; does not run a model or validate reasoning."""

import argparse
import json
from pathlib import Path


MODES = {"fact_lookup", "forecast", "market_decision", "other", "unresolved"}
ACTIONS = {
    "search_market", "verify_rules", "forecast_outcomes", "assess_costs",
    "official_lookup", "build_forecast", "replan", "clarify_contract",
    "report_gap", "compare_benchmark", "final_release_only",
    "choose_contract_final", "invent_probabilities", "fabricate_market", "downgrade_fact",
}


def score(actual, inputs, expected):
    rows = actual.get("cases") if isinstance(actual, dict) else None
    if not isinstance(rows, list):
        return {"passed": False, "errors": ["actual.cases must be a list"], "cases": []}
    by_id, errors = {}, []
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str):
            errors.append("each result must be an object with a string id")
        elif row["id"] in by_id:
            errors.append("duplicate result: " + row["id"])
        else:
            by_id[row["id"]] = row
    stages = {row["id"]: row["stage"] for row in inputs["cases"]}
    if set(stages) != set(expected):
        errors.append("input and expected case ids differ")
    if set(by_id) != set(stages):
        errors.append("missing or unexpected result ids: " + repr(sorted(set(by_id) ^ set(stages))))
    results = []
    for case_id, rule in expected.items():
        row = by_id.get(case_id)
        failures = []
        if row is None:
            failures.append("missing result")
        else:
            mode = row.get("task_mode")
            if not isinstance(mode, str) or mode not in MODES:
                failures.append("invalid task_mode")
            actions = row.get("actions")
            if not isinstance(actions, list) or any(not isinstance(a, str) or a not in ACTIONS for a in actions):
                failures.append("invalid actions")
                actions = []
            if not isinstance(row.get("reason"), str) or not row["reason"].strip():
                failures.append("reason is required")
            if "task_modes" in rule and row.get("task_mode") not in rule["task_modes"]:
                failures.append("unexpected task_mode")
            for action in rule.get("required_actions", []):
                if action not in actions:
                    failures.append("missing action: " + action)
            for action in rule.get("forbidden_actions", []):
                if action in actions:
                    failures.append("forbidden action: " + action)
            for field in ("answer_fit", "blocking"):
                value = row.get(field)
                if stages[case_id] == "review":
                    if type(value) is not bool or value != rule[field]:
                        failures.append("incorrect " + field)
                elif field not in row or value is not None:
                    failures.append(field + " must be null for triage")
        results.append({"id": case_id, "passed": not failures, "errors": failures})
    return {"passed": not errors and all(row["passed"] for row in results), "errors": errors, "cases": results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("actual", type=Path)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    try:
        result = score(json.loads(args.actual.read_text(encoding="utf-8")),
                       json.loads((here / "inputs.json").read_text(encoding="utf-8")),
                       json.loads((here / "expected.json").read_text(encoding="utf-8")))
    except (OSError, ValueError) as exc:
        parser.exit(2, str(exc) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
