#!/usr/bin/env python3
"""Validate the explicit research question and retrieval plan (Python 3.9+)."""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

TYPES = {"event_pricing", "asset", "theme", "actor"}


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def validate_plan(plan):
    errors = []
    if not isinstance(plan, dict):
        return ["plan must be an object"]
    if type(plan.get("schema_version")) is not int or plan.get("schema_version") != 2:
        errors.append("schema_version must be 2")
    for field in ("question", "task", "entity", "decision_needed", "prior_judgment", "stop_condition"):
        if not _text(plan.get(field)):
            errors.append(field + " must be nonempty text")
    if not isinstance(plan.get("type"), str) or plan.get("type") not in TYPES:
        errors.append("type must be event_pricing/asset/theme/actor")
    if not isinstance(plan.get("historical"), bool):
        errors.append("historical must be boolean")
    try:
        value = plan.get("as_of")
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None or "T" not in value:
            raise ValueError()
    except (ValueError, TypeError, AttributeError):
        errors.append("as_of must be a timezone-aware ISO instant")
    comparison = plan.get("comparison")
    if not isinstance(comparison, dict):
        errors.append("comparison must name period, unit and scope")
    else:
        for field in ("period", "unit", "scope"):
            if not _text(comparison.get(field)):
                errors.append("comparison." + field + " must be nonempty text")
    for field, keys in (("hypotheses", ("explanation", "discriminating_observation")),
                        ("queries", ("question", "query", "source", "purpose"))):
        rows = plan.get(field)
        if not isinstance(rows, list) or not rows:
            errors.append(field + " must be a nonempty list")
            continue
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                errors.append("%s[%d] must be an object" % (field, index))
                continue
            for key in keys:
                if not _text(row.get(key)):
                    errors.append("%s[%d].%s must be nonempty text" % (field, index, key))
    budget = plan.get("budget")
    if not isinstance(budget, dict):
        errors.append("budget must be an object")
    else:
        value = budget.get("max_queries")
        if type(value) is not int or value < 1:
            errors.append("budget.max_queries must be a positive integer")
        value = budget.get("max_followups")
        if type(value) is not int or not 0 <= value <= 2:
            errors.append("budget.max_followups must be an integer from 0 to 2")
    if "parent_run_id" in plan and not _text(plan["parent_run_id"]):
        errors.append("parent_run_id must be nonempty text when present")
    from analysis_contract import validate_design
    errors.extend(validate_design(plan))
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan")
    args = parser.parse_args()
    try:
        plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    errors = validate_plan(plan)
    print(json.dumps({"passed": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
