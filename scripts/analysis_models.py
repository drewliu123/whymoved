#!/usr/bin/env python3
"""Compute fixed, deterministic economic models using Python 3.9+ only.

Units are canonical labels: currency, ratio, year, shares, currency/share.
All currency and share quantities in one spec must use consistent scaling.
Evidence semantics of role and claim_ids are validated by the caller.
"""

import argparse
import json
import math
import sys
from pathlib import Path


MODEL_UNITS = {
    "operating_bridge": {
        "base_revenue": "currency", "revenue_growth": "ratio",
        "base_margin": "ratio", "scenario_margin": "ratio",
    },
    "free_cash_flow": {
        "operating_profit": "currency", "tax_rate": "ratio",
        "depreciation": "currency", "capex": "currency",
        "change_working_capital": "currency",
    },
    "dcf": {
        "free_cash_flow": "currency", "growth": "ratio",
        "discount_rate": "ratio", "terminal_growth": "ratio",
        "years": "year", "net_debt": "currency", "shares": "shares",
    },
    "reverse_dcf": {
        "free_cash_flow": "currency", "discount_rate": "ratio",
        "terminal_growth": "ratio", "years": "year",
        "net_debt": "currency", "shares": "shares", "price": "currency/share",
        "growth_low": "ratio", "growth_high": "ratio",
    },
}


def _fields(value, required, optional, label):
    if not isinstance(value, dict):
        raise ValueError(label + " must be an object")
    missing = set(required) - value.keys()
    unknown = value.keys() - set(required) - set(optional)
    if missing:
        raise ValueError(label + " missing fields: " + ", ".join(sorted(missing)))
    if unknown:
        raise ValueError(label + " unknown fields: " + ", ".join(sorted(map(str, unknown))))


def _number(value, label):
    if type(value) not in (int, float):
        raise ValueError(label + " must be a finite number, not bool")
    try:
        finite = math.isfinite(value)
    except OverflowError:
        finite = False
    if not finite:
        raise ValueError(label + " must be finite and representable")
    return value


def _ranges(kind, values):
    for name, value in values.items():
        _number(value, name)
        if name == "tax_rate" and not 0 <= value <= 1:
            raise ValueError(name + " must be between 0 and 1")
        if name in ("revenue_growth", "growth", "growth_low", "growth_high", "terminal_growth") and value <= -1:
            raise ValueError(name + " must be greater than -1")
        if name in ("base_revenue", "depreciation", "capex") and value < 0:
            raise ValueError(name + " must be nonnegative")
        if name in ("shares", "price", "discount_rate") and value <= 0:
            raise ValueError(name + " must be positive")
        if name == "free_cash_flow" and value <= 0:
            raise ValueError("free_cash_flow must be positive for valuation")
        if name == "years" and (value != int(value) or not 1 <= value <= 50):
            raise ValueError("years must be an integer from 1 to 50")
    if kind in ("dcf", "reverse_dcf"):
        if values["terminal_growth"] >= values["discount_rate"]:
            raise ValueError("terminal_growth must be less than discount_rate")
    if kind == "reverse_dcf" and values["growth_high"] <= values["growth_low"]:
        raise ValueError("growth_high must be greater than growth_low")


def _output(value, unit):
    return {"value": _number(value, "model output"), "unit": unit}


def _dcf(values, growth):
    """Return enterprise value and discounted terminal value using FCF0."""
    cash_flow = values["free_cash_flow"]
    discount = 1.0
    cash_flows = []
    for _ in range(int(values["years"])):
        cash_flow = _number(cash_flow * (1 + growth), "projected free cash flow")
        discount = _number(discount * (1 + values["discount_rate"]), "discount factor")
        cash_flows.append(_number(cash_flow / discount, "discounted free cash flow"))
    terminal = _number(cash_flow * (1 + values["terminal_growth"]) /
                       (values["discount_rate"] - values["terminal_growth"]), "terminal value")
    discounted_terminal = _number(terminal / discount, "discounted terminal value")
    enterprise = _number(math.fsum(cash_flows + [discounted_terminal]), "enterprise value")
    if enterprise <= 0:
        raise ValueError("enterprise value underflowed to zero")
    return enterprise, discounted_terminal


def _calculate(kind, values):
    _ranges(kind, values)
    if kind == "operating_bridge":
        base_profit = values["base_revenue"] * values["base_margin"]
        revenue = values["base_revenue"] * (1 + values["revenue_growth"])
        profit = revenue * values["scenario_margin"]
        result = {name: _output(value, "currency") for name, value in (
            ("base_profit", base_profit), ("revenue", revenue), ("profit", profit),
            ("profit_change", profit - base_profit),
            ("revenue_growth_effect", values["base_revenue"] * values["revenue_growth"] * values["base_margin"]),
            ("margin_effect", revenue * (values["scenario_margin"] - values["base_margin"])),
        )}
        if base_profit > 0:
            result["profit_growth"] = _output((profit - base_profit) / base_profit, "ratio")
        return result
    if kind == "free_cash_flow":
        fcf = (values["operating_profit"] * (1 - values["tax_rate"]) +
               values["depreciation"] - values["capex"] - values["change_working_capital"])
        return {"free_cash_flow": _output(fcf, "currency")}
    if kind == "dcf":
        enterprise, terminal = _dcf(values, values["growth"])
        equity = enterprise - values["net_debt"]
        return {
            "enterprise_value": _output(enterprise, "currency"),
            "equity_value": _output(equity, "currency"),
            "per_share": _output(equity / values["shares"], "currency/share"),
            "terminal_value_share": _output(terminal / enterprise, "ratio"),
        }
    target = _number(values["price"] * values["shares"] + values["net_debt"], "target enterprise value")
    if target <= 0:
        raise ValueError("target enterprise value must be positive")
    low, high = values["growth_low"], values["growth_high"]
    low_ev, _ = _dcf(values, low)
    high_ev, _ = _dcf(values, high)
    if not low_ev <= target <= high_ev:
        raise ValueError("no solution: growth bounds do not bracket target enterprise value")
    # Retain the best representable result, including an exact endpoint solution.
    growth, solved = min(((low, low_ev), (high, high_ev)), key=lambda pair: abs(pair[1] - target))
    tolerance = max(1e-10 * abs(target), 1e-300)
    for _ in range(256):
        if abs(solved - target) <= tolerance:
            break
        midpoint = low + (high - low) / 2
        if midpoint == low or midpoint == high:
            break
        enterprise, _ = _dcf(values, midpoint)
        if abs(enterprise - target) < abs(solved - target):
            growth, solved = midpoint, enterprise
        if enterprise < target:
            low = midpoint
        else:
            high = midpoint
    if abs(solved - target) > tolerance:
        raise ValueError("no numerically reliable solution within growth bounds")
    solved, _ = _dcf(values, growth)
    return {
        "implied_growth": _output(growth, "ratio"),
        "target_enterprise_value": _output(target, "currency"),
        "solved_enterprise_value": _output(solved, "currency"),
        "residual": _output(solved - target, "currency"),
    }


def compute_model(spec):
    """Validate and compute a model and ordered, one-input-at-a-time scenarios.

    Raises ValueError for malformed specs, invalid ranges, overflow, or an
    unbracketed reverse valuation. Does not mutate the supplied spec.
    """
    _fields(spec, ("kind", "inputs"), ("sensitivity",), "spec")
    kind = spec["kind"]
    if not isinstance(kind, str) or kind not in MODEL_UNITS:
        raise ValueError("unknown model kind")
    units = MODEL_UNITS[kind]
    _fields(spec["inputs"], units, (), "inputs")
    values = {}
    for name, unit in units.items():
        row = spec["inputs"][name]
        _fields(row, ("value", "unit", "role", "claim_ids"), (), "inputs." + name)
        if row["unit"] != unit:
            raise ValueError(name + " unit must be " + unit)
        if not isinstance(row["role"], str) or row["role"] not in ("observed", "assumption"):
            raise ValueError(name + " role must be observed or assumption")
        if not isinstance(row["claim_ids"], list) or any(
                not isinstance(item, str) or not item.strip() for item in row["claim_ids"]):
            raise ValueError(name + " claim_ids must be a list of nonempty strings")
        values[name] = _number(row["value"], name)
    scenarios = spec.get("sensitivity", [])
    if not isinstance(scenarios, list):
        raise ValueError("sensitivity must be a list")
    seen = set()
    for row in scenarios:
        _fields(row, ("input", "values"), (), "sensitivity entry")
        name = row["input"]
        if not isinstance(name, str) or name not in units:
            raise ValueError("sensitivity input must name a model input")
        if name in seen:
            raise ValueError("duplicate sensitivity input: " + name)
        seen.add(name)
        if kind == "reverse_dcf" and name in ("growth_low", "growth_high", "years"):
            raise ValueError("reverse_dcf sensitivity cannot change " + name)
        if not isinstance(row["values"], list) or not row["values"]:
            raise ValueError("sensitivity values must be a nonempty list")
        for value in row["values"]:
            _number(value, "sensitivity " + name)
    try:
        outputs = _calculate(kind, values)
        sensitivity = []
        for row in scenarios:
            name = row["input"]
            for value in row["values"]:
                changed = dict(values, **{name: value})
                sensitivity.append({"input": name, "value": value, "unit": units[name],
                                    "outputs": _calculate(kind, changed)})
    except (OverflowError, ZeroDivisionError) as exc:
        raise ValueError("model arithmetic overflow or singular denominator") from exc
    return {"outputs": outputs, "sensitivity": sensitivity}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="JSON model spec")
    args = parser.parse_args()
    try:
        spec = json.loads(Path(args.input).read_text(encoding="utf-8"))
        result = compute_model(spec)
    except (OSError, ValueError) as exc:
        print(json.dumps({"passed": False, "errors": [str(exc)]}, ensure_ascii=False))
        return 1
    print(json.dumps({"passed": True, "result": result}, ensure_ascii=False, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
