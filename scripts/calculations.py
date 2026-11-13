#!/usr/bin/env python3
"""Deterministic, whitelisted arithmetic for report.calculations (Python 3.9+).

Report calculations were previously recorded but never recomputed: a row could
claim any result as long as the shape looked right. This module adds an
optional `op` to a calculation row. When `op` is present the arithmetic is
recomputed from the listed inputs (or from earlier calculation ids) and compared
with the frozen result; when it is absent the row stays a transparent record and
is not executed.

The whitelist is deliberately small and positional. It is not a formula
language: no free expressions, no source text evaluation, no functions. It
recomputes arithmetic, not economic meaning, and does not prove that an input
equals what the original source says (that is the evidence ledger's job).

Operators (input order is significant):

    ratio       a / b                     inputs: a, b (same unit)   -> ratio
    growth      a / b - 1                 inputs: a, b (same unit)   -> ratio
    cagr        (a / b) ** (1 / years) - 1 inputs: end, begin, years -> ratio
    difference  a - b                     inputs: a, b (same unit)   -> that unit
    sum         a + b + ...               inputs: all same unit      -> that unit
    product     a * b * ...               exactly one non-ratio input -> its unit
"""

import math

OPS = ("ratio", "growth", "cagr", "difference", "sum", "product")
MAX_REF_DEPTH = 2
RATIO_OPS = {"ratio", "growth", "cagr"}
IDENTIFIER = None  # Safe-id validation lives in the caller; see validate_calculations.


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _safe_id(value):
    return (isinstance(value, str) and bool(value) and value[0].isalpha()
            and all(char.isalnum() or char in "_.-" for char in value))


def _number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    try:
        return value if math.isfinite(value) else None
    except OverflowError:
        return None


def _finite(value, label):
    if value is None or not math.isfinite(value):
        raise ValueError(label + " is not a finite number")
    return value


def _resolve_values(row, previous):
    """Return (values, units, refs) for one row; refs resolve from earlier rows."""
    values, units, refs = [], [], []
    for n, item in enumerate(row.get("inputs", [])):
        location = row.get("id", "calculation") + ".inputs[%d]" % n
        if not isinstance(item, dict):
            raise ValueError(location + " must be an object")
        if not _text(item.get("name")):
            raise ValueError(location + ".name must be nonempty text")
        if not _text(item.get("unit")):
            raise ValueError(location + ".unit must be nonempty text")
        if "ref" in item:
            target = item["ref"]
            if not isinstance(target, str) or target not in previous:
                raise ValueError(location + ".ref must name an earlier computed calculation")
            if previous[target]["depth"] >= MAX_REF_DEPTH:
                raise ValueError(location + ".ref exceeds the maximum reference depth")
            if item["unit"] != previous[target]["unit"]:
                raise ValueError(location + ".unit differs from the referenced result")
            values.append(previous[target]["value"])
            units.append(previous[target]["unit"])
            refs.append(target)
            continue
        if "claim_ids" in item and "ref" in item:
            raise ValueError(location + " cannot use both ref and claim_ids")
        value = _number(item.get("value"))
        if value is None:
            raise ValueError(location + " requires a finite value or an earlier ref")
        values.append(value)
        units.append(item["unit"])
    return values, units, refs


def _check_units(op, values, units, result_unit):
    """Validate the unit contract of an operator and return the canonical unit."""
    if len(values) < 2:
        raise ValueError(op + " needs at least two inputs")
    if op in RATIO_OPS:
        if len(units) != (3 if op == "cagr" else 2):
            raise ValueError(op + " takes exactly " + ("three" if op == "cagr" else "two") + " inputs")
        if op == "cagr":
            if units[0] != units[1]:
                raise ValueError("cagr needs end and begin in the same unit")
            if units[2] != "year":
                raise ValueError("cagr years input must use the year unit")
        elif units[0] != units[1]:
            raise ValueError(op + " needs both inputs in the same unit")
        if result_unit != "ratio":
            raise ValueError(op + " result unit must be ratio")
        return "ratio"
    if op in ("difference", "sum"):
        if op == "difference" and len(units) != 2:
            raise ValueError("difference takes exactly two inputs")
        if len(set(units)) != 1:
            raise ValueError(op + " needs every input in the same unit")
        if result_unit != units[0]:
            raise ValueError(op + " result unit must match the input unit")
        return units[0]
    if op == "product":
        others = [unit for unit in units if unit != "ratio"]
        if len(others) != 1:
            raise ValueError("product needs exactly one non-ratio input")
        if len(units) - len(others) < 1:
            raise ValueError("product needs at least one ratio input")
        if result_unit != others[0]:
            raise ValueError("product result unit must match its non-ratio input")
        return others[0]
    raise ValueError("unknown op")


def compute(op, values, units, result_unit):
    """Recompute one whitelisted operation; returns (value, unit)."""
    if op not in OPS:
        raise ValueError("unknown op: " + str(op))
    unit = _check_units(op, values, units, result_unit)
    try:
        if op == "ratio":
            if values[1] == 0:
                raise ValueError("ratio divisor is zero")
            return _finite(values[0] / values[1], "ratio"), unit
        if op == "growth":
            if values[1] == 0:
                raise ValueError("growth base is zero")
            return _finite(values[0] / values[1] - 1, "growth"), unit
        if op == "cagr":
            if values[1] <= 0 or values[0] <= 0:
                raise ValueError("cagr end and begin must be positive")
            if values[2] <= 0:
                raise ValueError("cagr years must be positive")
            return _finite((values[0] / values[1]) ** (1.0 / values[2]) - 1, "cagr"), unit
        if op == "difference":
            return _finite(values[0] - values[1], "difference"), unit
        if op == "sum":
            return _finite(math.fsum(values), "sum"), unit
        total = 1.0
        for value in values:
            total = _finite(total * value, "product")
        return total, unit
    except (OverflowError, ZeroDivisionError) as exc:
        raise ValueError("calculation arithmetic overflow or singular denominator") from exc


def _matches(recorded, computed, precision):
    if precision is None:
        expected = computed
    else:
        if type(precision) is not int or not 0 <= precision <= 12:
            raise ValueError("result.precision must be an integer from 0 to 12")
        expected = round(computed, precision)
    scale = max(abs(expected), abs(computed))
    return abs(recorded - expected) <= max(1e-12, 1e-9 * scale)


def validate_calculations(rows, claim_ids):
    """Validate shape, evidence links and, for rows with `op`, recompute arithmetic.

    Rows without `op` keep the legacy behaviour: structure, units and unresolvable
    references are rejected, but the arithmetic is only recorded, never executed.
    """
    if not isinstance(rows, list):
        return ["calculations must be a list"]
    errors, seen, previous = [], set(), {}
    for n, row in enumerate(rows):
        path = "calculations[%d]" % n
        if not isinstance(row, dict):
            errors.append(path + " must be an object")
            continue
        cid = row.get("id")
        if not isinstance(cid, str) or not _safe_id(cid) or cid in seen:
            errors.append(path + ".id must be a unique safe identifier")
            continue
        seen.add(cid)
        for field in ("description", "formula"):
            if not _text(row.get(field)):
                errors.append(path + "." + field + " must be nonempty text")
        row_refs = row.get("claim_ids")
        if not isinstance(row_refs, list) or not row_refs or any(
                not isinstance(c, str) or c not in claim_ids for c in row_refs):
            errors.append(path + ".claim_ids must resolve")
            row_refs = []
        inputs = row.get("inputs")
        if not isinstance(inputs, list) or not inputs:
            errors.append(path + ".inputs must be nonempty list")
            continue
        resolved = True
        for i, item in enumerate(inputs):
            location = path + ".inputs[%d]" % i
            if not isinstance(item, dict) or not _text(item.get("name")) or not _text(item.get("unit")):
                errors.append(location + " requires name, finite value and unit")
                resolved = False
                continue
            if "ref" in item:
                if "value" in item or "claim_ids" in item:
                    errors.append(location + " cannot mix ref with value or claim_ids")
                    resolved = False
                elif not isinstance(item["ref"], str) or item["ref"] not in previous:
                    errors.append(location + ".ref must name an earlier computed calculation")
                    resolved = False
                else:
                    target = previous[item["ref"]]
                    if item["unit"] != target["unit"]:
                        errors.append(location + ".unit differs from the referenced result")
                        resolved = False
                    if target["depth"] >= MAX_REF_DEPTH:
                        errors.append(location + ".ref exceeds the maximum reference depth")
                        resolved = False
                continue
            if _number(item.get("value")) is None:
                errors.append(location + " requires name, finite value and unit")
                resolved = False
            item_refs = item.get("claim_ids")
            if not isinstance(item_refs, list) or not item_refs or any(
                    not isinstance(c, str) or c not in claim_ids for c in item_refs):
                errors.append(location + ".claim_ids must resolve")
                resolved = False
        result = row.get("result")
        if not isinstance(result, dict) or _number(result.get("value")) is None or not _text(result.get("unit")):
            errors.append(path + ".result requires finite value and unit")
            continue
        op = row.get("op")
        if op is None:
            continue
        if not isinstance(op, str) or op not in OPS:
            errors.append(path + ".op must be one of " + ", ".join(OPS))
            continue
        if not resolved:
            continue
        try:
            values, units, refs = _resolve_values(row, previous)
            computed, unit = compute(op, values, units, result["unit"])
            if not _matches(result["value"], computed, result.get("precision")):
                errors.append(path + ".result differs from deterministic recomputation")
                continue
        except ValueError as exc:
            errors.append(path + ": " + str(exc))
            continue
        depth = 1 + max((previous[ref]["depth"] for ref in refs), default=0)
        # Downstream rows reference the recorded result, not the internal float:
        # the document must stay reproducible from the numbers a reader can see.
        previous[cid] = {"value": result["value"], "unit": unit, "depth": depth}
    return errors
