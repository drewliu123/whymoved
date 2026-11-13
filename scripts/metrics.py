#!/usr/bin/env python3
"""Structured numeric facts on claims (Python 3.9+).

A claim's `text` remains the evidence record; `metric` adds a machine-checkable
number with its unit, period and scope so that YTD-vs-quarter, currency-scale
and segment-vs-consolidated mistakes stop being invisible prose problems.

The block is optional and additive: ledgers without `metric` keep their current
behaviour. Validation here checks the shape of the block and the consistency of
declared comparisons; it does not prove the number equals the original filing.

Block fields:

    name         nonempty text, the metric being measured
    value        finite number
    unit         nonempty text, the unit the value is expressed in
    period_type  fy | quarter | ytd | ltm | instant
    period_end   ISO date/datetime the period ends (or the instant)
    period_start ISO date/datetime; required except for instant
    entity       optional nonempty text (ticker, company or instrument)
    scope        optional: consolidated (default) or segment:<name>
    currency     optional nonempty text
    scale        optional nonempty text ("million", "billion", ...)
    basis        optional: gaap | adjusted
    locator      optional pointer into the source document
    comparison_with  optional claim ids this number is explicitly compared with
"""

import argparse
import json
import math
import sys
from pathlib import Path

PERIOD_TYPES = ("fy", "quarter", "ytd", "ltm", "instant")
BASES = ("gaap", "adjusted")
REQUIRED = ("name", "value", "unit", "period_type", "period_end")
OPTIONAL = ("period_start", "entity", "scope", "currency", "scale", "basis", "locator", "comparison_with")


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    try:
        return value if math.isfinite(value) else None
    except OverflowError:
        return None


def _date(value):
    from common import parse_date
    return parse_date(value) if isinstance(value, str) else None


def _norm(value):
    return value.strip().casefold() if isinstance(value, str) else ""


def metric_key(metric):
    """Grouping key: entity + name + scope + period_type, normalised."""
    scope = _norm(metric.get("scope")) or "consolidated"
    return (_norm(metric.get("entity")), _norm(metric.get("name")), scope, metric.get("period_type"))


def describe(metric):
    """Human-readable period/scope line used by reports and CLI output."""
    period = str(metric.get("period_end", ""))
    if _text(metric.get("period_start")):
        period = str(metric["period_start"]) + " → " + period
    parts = [metric.get("period_type", ""), period]
    if _text(metric.get("scope")):
        parts.append(metric["scope"])
    if _text(metric.get("basis")):
        parts.append(metric["basis"])
    return "；".join(part for part in parts if part)


def validate_metric(metric):
    """Validate one metric block; returns a list of M-prefixed errors."""
    if not isinstance(metric, dict):
        return ["M1 metric must be an object"]
    errors = []
    unknown = set(metric) - set(REQUIRED) - set(OPTIONAL)
    if unknown:
        errors.append("M1 metric has unknown fields: " + ", ".join(sorted(map(str, unknown))))
    missing = [field for field in REQUIRED if field not in metric]
    if missing:
        errors.append("M1 metric missing fields: " + ", ".join(missing))
        return errors
    if not _text(metric["name"]):
        errors.append("M1 metric.name must be nonempty text")
    if _number(metric["value"]) is None:
        errors.append("M1 metric.value must be a finite number")
    if not _text(metric["unit"]):
        errors.append("M1 metric.unit must be nonempty text")
    period_type = metric["period_type"]
    if not isinstance(period_type, str) or period_type not in PERIOD_TYPES:
        errors.append("M1 metric.period_type must be one of " + ", ".join(PERIOD_TYPES))
    end = _date(metric["period_end"])
    if end is None:
        errors.append("M2 metric.period_end must be an ISO date/datetime")
    if period_type == "instant":
        if "period_start" in metric and _text(metric["period_start"]):
            start = _date(metric["period_start"])
            if start is None or (end is not None and start != end):
                errors.append("M2 instant metric.period_start must equal period_end")
    elif "period_start" not in metric or not _text(metric["period_start"]):
        errors.append("M2 " + str(period_type) + " metrics require metric.period_start")
    else:
        start = _date(metric["period_start"])
        if start is None:
            errors.append("M2 metric.period_start must be an ISO date/datetime")
        elif end is not None and start > end:
            errors.append("M2 metric.period_start must not be after period_end")
    if "entity" in metric and not _text(metric["entity"]):
        errors.append("M1 metric.entity must be nonempty text when present")
    if "scope" in metric:
        scope = metric["scope"]
        if not _text(scope):
            errors.append("M1 metric.scope must be nonempty text when present")
        elif _norm(scope) != "consolidated" and (not _norm(scope).startswith("segment:") or len(_norm(scope)) == len("segment:")):
            errors.append("M1 metric.scope must be consolidated or segment:<name>")
    for field in ("currency", "scale", "locator"):
        if field in metric and not _text(metric[field]):
            errors.append("M1 metric." + field + " must be nonempty text when present")
    if "basis" in metric and (not isinstance(metric["basis"], str) or metric["basis"] not in BASES):
        errors.append("M1 metric.basis must be gaap or adjusted")
    comparisons = metric.get("comparison_with")
    if comparisons is not None:
        if not isinstance(comparisons, list) or not comparisons:
            errors.append("M1 metric.comparison_with must be a nonempty claim id list")
        elif any(not _text(item) for item in comparisons):
            errors.append("M1 metric.comparison_with must contain nonempty claim ids")
        elif len(set(comparisons)) != len(comparisons):
            errors.append("M1 metric.comparison_with contains duplicates")
    return errors


def _compare(left, right):
    """Consistency errors when two claims declare an explicit comparison."""
    errors = []
    if _norm(left.get("unit")) != _norm(right.get("unit")):
        errors.append("M3 comparison requires the same unit: " + str(left.get("unit")) + " vs " + str(right.get("unit")))
    for field in ("currency", "scale"):
        one, other = left.get(field), right.get(field)
        if _text(one) and _text(other) and _norm(one) != _norm(other):
            errors.append("M3 comparison requires the same " + field + ": " + str(one) + " vs " + str(other))
    if left.get("period_type") != right.get("period_type"):
        errors.append("M3 comparison requires the same period_type: " + str(left.get("period_type")) + " vs " + str(right.get("period_type")))
    if _norm(left.get("basis")) and _norm(right.get("basis")) and _norm(left.get("basis")) != _norm(right.get("basis")):
        errors.append("M3 comparison mixes gaap and adjusted basis")
    return errors


def cross_claim_metric_errors(claims):
    """Return {claim_id: [errors]} for metric consistency across a ledger."""
    if not isinstance(claims, list):
        return {}
    by_id = {claim["id"]: claim for claim in claims
             if isinstance(claim, dict) and _text(claim.get("id"))}
    failures = {}

    def fail(cid, message):
        failures.setdefault(cid, []).append(message)

    for cid, claim in by_id.items():
        metric = claim.get("metric")
        if not isinstance(metric, dict):
            continue
        comparisons = metric.get("comparison_with")
        if not isinstance(comparisons, list):
            continue
        for other_id in comparisons:
            if not isinstance(other_id, str) or not other_id:
                continue
            if other_id == cid:
                fail(cid, "M3 metric.comparison_with cannot reference the claim itself")
                continue
            other = by_id.get(other_id)
            if other is None:
                fail(cid, "M3 metric.comparison_with references a missing claim: " + other_id)
                continue
            other_metric = other.get("metric")
            if not isinstance(other_metric, dict):
                fail(cid, "M3 comparison requires " + other_id + " to declare metric")
                continue
            for message in _compare(metric, other_metric):
                fail(cid, message)

    groups = {}
    for cid, claim in by_id.items():
        metric = claim.get("metric")
        if not isinstance(metric, dict) or not _text(metric.get("name")):
            continue
        if validate_metric(metric):
            continue
        groups.setdefault(metric_key(metric), []).append((cid, metric))
    for members in groups.values():
        units = {_norm(metric.get("unit")) for _, metric in members}
        if len(units) > 1:
            for cid, _ in members:
                fail(cid, "M4 same metric, entity, scope and period_type must use one unit: " + ", ".join(sorted(units)))
            continue
        for field in ("currency", "scale"):
            declared = {_norm(metric.get(field)) for _, metric in members if _text(metric.get(field))}
            if len(declared) > 1:
                for cid, _ in members:
                    fail(cid, "M4 same metric, entity, scope and period_type must use one " + field + ": " + ", ".join(sorted(declared)))
        bases = {_norm(metric.get("basis")) for _, metric in members if _text(metric.get("basis"))}
        if len(bases) > 1:
            for cid, _ in members:
                fail(cid, "M4 same metric group mixes gaap and adjusted basis: " + ", ".join(sorted(bases)))
    return failures


def extract_metrics(claims):
    """Return ordered metric rows for downstream tools and reports."""
    rows = []
    for claim in claims if isinstance(claims, list) else []:
        if not isinstance(claim, dict):
            continue
        metric = claim.get("metric")
        if not isinstance(metric, dict) or validate_metric(metric):
            continue
        rows.append({
            "claim_id": claim.get("id"), "entity": metric.get("entity", ""),
            "name": metric["name"], "value": metric["value"], "unit": metric["unit"],
            "period_type": metric["period_type"], "period_start": metric.get("period_start", ""),
            "period_end": metric["period_end"], "scope": metric.get("scope", "consolidated"),
            "currency": metric.get("currency", ""), "scale": metric.get("scale", ""),
            "basis": metric.get("basis", ""), "locator": metric.get("locator", ""),
        })
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path, help="claims.json ledger")
    args = parser.parse_args()
    try:
        ledger = json.loads(args.ledger.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(json.dumps({"passed": False, "errors": [str(exc)]}, ensure_ascii=False))
        return 2
    claims = ledger.get("claims") if isinstance(ledger, dict) else None
    if not isinstance(claims, list):
        print(json.dumps({"passed": False, "errors": ["ledger.claims must be a list"]}, ensure_ascii=False))
        return 1
    rows = extract_metrics(claims)
    mismatches = cross_claim_metric_errors(claims)
    print(json.dumps({"passed": not mismatches, "metrics": rows, "failures": mismatches},
                     ensure_ascii=False, indent=2, allow_nan=False))
    return 0 if not mismatches else 1


if __name__ == "__main__":
    raise SystemExit(main())
