#!/usr/bin/env python3
"""Compute fixed, deterministic economic models using Python 3.9+ only.

Units are canonical labels: currency, ratio, year, shares, currency/share, count.
All currency and share quantities in one spec must use consistent scaling.
Evidence semantics of role and claim_ids are validated by the caller.

A spec may carry a `tornado` block instead of (or alongside) `sensitivity`:
{"output": "<output name>", "inputs": [{"input": "<input>", "low": 0.08,
"high": 0.10}, ...]}. Each input is moved to its low and high value and the
selected output swing is ranked, making clear which assumption moves the
answer most. Tornado rows are arithmetic, not a joint scenario.

driver_build additionally accepts a `segments` list (name, base_revenue,
volume_growth, price_growth, margin, claim_ids) and decomposes revenue into
base, volume, price and interaction effects. It is arithmetic on stated
segment assumptions, not proof that segments behave independently.

relative_valuation additionally accepts a `peers` list (name, multiple,
optional note and claim_ids) and reports the peer multiple distribution, the
implied value range applied to the target metric, and the multiple that the
observed price implies. It is arithmetic on a selected peer set, not proof
that those peers are comparable.
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
    "relative_valuation": {
        "metric": "currency", "net_debt": "currency",
        "shares": "shares", "price": "currency/share",
    },
    "driver_build": {"margin_delta": "ratio"},
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
        if name in ("shares", "price", "discount_rate", "metric") and value <= 0:
            raise ValueError(name + " must be positive")
        if name == "free_cash_flow" and value <= 0:
            raise ValueError("free_cash_flow must be positive for valuation")
        if name == "years" and (value != int(value) or not 1 <= value <= 50):
            raise ValueError("years must be an integer from 1 to 50")
    if kind == "driver_build" and not -1 <= values["margin_delta"] <= 1:
        raise ValueError("margin_delta must be between -1 and 1")
    if kind in ("dcf", "reverse_dcf"):
        if values["terminal_growth"] >= values["discount_rate"]:
            raise ValueError("terminal_growth must be less than discount_rate")
    if kind == "reverse_dcf" and values["growth_high"] <= values["growth_low"]:
        raise ValueError("growth_high must be greater than growth_low")


def _output(value, unit):
    return {"value": _number(value, "model output"), "unit": unit}


def _peer_rows(spec):
    """Validate the peer set used by relative valuation; order is preserved."""
    peers = spec.get("peers")
    if not isinstance(peers, list) or not peers:
        raise ValueError("relative_valuation requires a nonempty peers list")
    seen, rows = set(), []
    for n, peer in enumerate(peers):
        label = "peers[%d]" % n
        _fields(peer, ("name", "multiple"), ("note", "claim_ids"), label)
        name = peer["name"]
        if not isinstance(name, str) or not name.strip():
            raise ValueError(label + ".name must be nonempty text")
        key = name.strip().casefold()
        if key in seen:
            raise ValueError(label + ".name duplicates another peer")
        seen.add(key)
        multiple = _number(peer["multiple"], label + ".multiple")
        if multiple <= 0:
            raise ValueError(label + ".multiple must be positive")
        if "note" in peer and not isinstance(peer["note"], str):
            raise ValueError(label + ".note must be text")
        claim_ids = peer.get("claim_ids")
        if "claim_ids" in peer and (not isinstance(claim_ids, list) or any(
                not isinstance(item, str) or not item.strip() for item in claim_ids)):
            raise ValueError(label + ".claim_ids must be a list of nonempty strings")
        row = {"name": name.strip(), "multiple": multiple}
        if "note" in peer:
            row["note"] = peer["note"]
        if "claim_ids" in peer:
            row["claim_ids"] = list(claim_ids)
        rows.append(row)
    return rows


def _segment_rows(spec):
    """Validate driver-build segments; order is preserved."""
    segments = spec.get("segments")
    if not isinstance(segments, list) or not segments:
        raise ValueError("driver_build requires a nonempty segments list")
    seen, rows = set(), []
    for n, segment in enumerate(segments):
        label = "segments[%d]" % n
        _fields(segment, ("name", "base_revenue", "volume_growth", "price_growth", "margin"),
                ("claim_ids", "base_margin"), label)
        name = segment["name"]
        if not isinstance(name, str) or not name.strip():
            raise ValueError(label + ".name must be nonempty text")
        key = name.strip().casefold()
        if key in seen:
            raise ValueError(label + ".name duplicates another segment")
        seen.add(key)
        base = _number(segment["base_revenue"], label + ".base_revenue")
        if base < 0:
            raise ValueError(label + ".base_revenue must be nonnegative")
        volume = _number(segment["volume_growth"], label + ".volume_growth")
        price = _number(segment["price_growth"], label + ".price_growth")
        if volume <= -1:
            raise ValueError(label + ".volume_growth must be greater than -1")
        if price <= -1:
            raise ValueError(label + ".price_growth must be greater than -1")
        margin = _number(segment["margin"], label + ".margin")
        base_margin = _number(segment["base_margin"], label + ".base_margin") if "base_margin" in segment else None
        claim_ids = segment.get("claim_ids")
        if claim_ids is not None and (not isinstance(claim_ids, list) or any(
                not isinstance(item, str) or not item.strip() for item in claim_ids)):
            raise ValueError(label + ".claim_ids must be a list of nonempty strings")
        row = {"name": name.strip(), "base_revenue": base, "volume_growth": volume,
               "price_growth": price, "margin": margin}
        if base_margin is not None:
            row["base_margin"] = base_margin
        if claim_ids is not None:
            row["claim_ids"] = list(claim_ids)
        rows.append(row)
    return rows


def _percentile(sorted_values, fraction):
    """Linear-interpolated percentile of an ascending nonempty list."""
    if len(sorted_values) == 1:
        return sorted_values[0]
    position = (len(sorted_values) - 1) * fraction
    lower, upper = math.floor(position), math.ceil(position)
    if lower == upper:
        return sorted_values[lower]
    return _number(sorted_values[lower] + (sorted_values[upper] - sorted_values[lower]) * (position - lower),
                   "percentile")



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


def _calculate(kind, values, peers=None, segments=None):
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
    if kind == "driver_build":
        if not segments:
            raise ValueError("driver_build requires a nonempty segments list")
        delta = values["margin_delta"]
        base_revenue = math.fsum(segment["base_revenue"] for segment in segments)
        revenue = math.fsum(segment["base_revenue"] * (1 + segment["volume_growth"]) *
                            (1 + segment["price_growth"]) for segment in segments)
        volume_effect = math.fsum(segment["base_revenue"] * segment["volume_growth"] for segment in segments)
        price_effect = math.fsum(segment["base_revenue"] * segment["price_growth"] for segment in segments)
        interaction_effect = math.fsum(segment["base_revenue"] * segment["volume_growth"] * segment["price_growth"]
                                       for segment in segments)
        base_profit = math.fsum(segment["base_revenue"] * segment.get("base_margin", segment["margin"])
                               for segment in segments)
        profit = math.fsum(segment["base_revenue"] * (1 + segment["volume_growth"]) *
                           (1 + segment["price_growth"]) * (segment["margin"] + delta) for segment in segments)
        revenue_change = revenue - base_revenue
        result = {
            "segment_count": _output(len(segments), "count"),
            "base_revenue": _output(base_revenue, "currency"),
            "revenue": _output(revenue, "currency"),
            "revenue_change": _output(revenue_change, "currency"),
            "volume_effect": _output(volume_effect, "currency"),
            "price_effect": _output(price_effect, "currency"),
            "interaction_effect": _output(interaction_effect, "currency"),
            "base_profit": _output(base_profit, "currency"),
            "profit": _output(profit, "currency"),
            "profit_change": _output(profit - base_profit, "currency"),
        }
        if base_revenue > 0:
            result["revenue_growth"] = _output(revenue / base_revenue - 1, "ratio")
        if revenue_change != 0:
            result["incremental_margin"] = _output((profit - base_profit) / revenue_change, "ratio")
        return result
    if kind == "relative_valuation":
        if not peers:
            raise ValueError("relative_valuation requires a nonempty peers list")
        multiples = sorted(peer["multiple"] for peer in peers)
        low, median, high = (_percentile(multiples, fraction) for fraction in (.25, .5, .75))
        metric, net_debt, shares = values["metric"], values["net_debt"], values["shares"]

        def per_share(multiple):
            return (multiple * metric - net_debt) / shares

        result = {
            "peer_count": _output(len(multiples), "count"),
            "peer_multiple_min": _output(multiples[0], "ratio"),
            "peer_multiple_q1": _output(low, "ratio"),
            "peer_multiple_median": _output(median, "ratio"),
            "peer_multiple_q3": _output(high, "ratio"),
            "peer_multiple_max": _output(multiples[-1], "ratio"),
            "peer_multiple_mean": _output(math.fsum(multiples) / len(multiples), "ratio"),
            "implied_ev_median": _output(median * metric, "currency"),
            "implied_equity_median": _output(median * metric - net_debt, "currency"),
            "per_share_median": _output(per_share(median), "currency/share"),
            "per_share_low": _output(per_share(low), "currency/share"),
            "per_share_high": _output(per_share(high), "currency/share"),
            "implied_multiple_at_price": _output((values["price"] * shares + net_debt) / metric, "ratio"),
        }
        if result["per_share_median"]["value"] > 0:
            result["price_vs_peer_median"] = _output(values["price"] / result["per_share_median"]["value"] - 1, "ratio")
        implied = result["implied_multiple_at_price"]["value"]
        below = sum(1 for multiple in multiples if multiple < implied)
        result["implied_multiple_percentile"] = _output(below / len(multiples), "ratio")
        return result
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
    _fields(spec, ("kind", "inputs"), ("sensitivity", "peers", "segments", "tornado"), "spec")
    kind = spec["kind"]
    if not isinstance(kind, str) or kind not in MODEL_UNITS:
        raise ValueError("unknown model kind")
    if kind == "relative_valuation":
        peers = _peer_rows(spec)
    elif "peers" in spec:
        raise ValueError("peers is only supported by relative_valuation")
    else:
        peers = None
    if kind == "driver_build":
        segments = _segment_rows(spec)
    elif "segments" in spec:
        raise ValueError("segments is only supported by driver_build")
    else:
        segments = None
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
    tornado_rows = []
    tornado = spec.get("tornado")
    if tornado is not None:
        if not isinstance(tornado, dict):
            raise ValueError("tornado must be an object")
        _fields(tornado, ("output", "inputs"), (), "tornado")
        if not isinstance(tornado["output"], str) or not tornado["output"].strip():
            raise ValueError("tornado.output must name an existing model output")
        entries = tornado["inputs"]
        if not isinstance(entries, list) or not entries:
            raise ValueError("tornado.inputs must be a nonempty list")
        seen_tornado = set()
        for row in entries:
            _fields(row, ("input", "low", "high"), (), "tornado entry")
            name = row["input"]
            if not isinstance(name, str) or name not in units:
                raise ValueError("tornado input must name a model input")
            if name in seen_tornado:
                raise ValueError("duplicate tornado input: " + name)
            seen_tornado.add(name)
            if kind == "reverse_dcf" and name in ("growth_low", "growth_high", "years"):
                raise ValueError("reverse_dcf tornado cannot change " + name)
            low, high = _number(row["low"], "tornado " + name + " low"), _number(row["high"], "tornado " + name + " high")
            if low == high:
                raise ValueError("tornado " + name + " requires two different values")
    try:
        outputs = _calculate(kind, values, peers, segments)
        sensitivity = []
        for row in scenarios:
            name = row["input"]
            for value in row["values"]:
                changed = dict(values, **{name: value})
                sensitivity.append({"input": name, "value": value, "unit": units[name],
                                    "outputs": _calculate(kind, changed, peers, segments)})
        if tornado is not None:
            target = tornado["output"]
            if target not in outputs:
                raise ValueError("tornado.output is not defined for this model")
            for row in tornado["inputs"]:
                name, low, high = row["input"], row["low"], row["high"]
                low_outputs = _calculate(kind, dict(values, **{name: low}), peers, segments)
                high_outputs = _calculate(kind, dict(values, **{name: high}), peers, segments)
                if target not in low_outputs or target not in high_outputs:
                    raise ValueError("tornado.output is not defined at the swept values of " + name)
                low_value, high_value = low_outputs[target]["value"], high_outputs[target]["value"]
                tornado_rows.append({"input": name, "output": target,
                                     "low": low, "high": high,
                                     "low_output": low_outputs[target], "high_output": high_outputs[target],
                                     "swing": _number(abs(high_value - low_value), "tornado swing")})
            tornado_rows.sort(key=lambda item: (-item["swing"], item["input"]))
    except (OverflowError, ZeroDivisionError) as exc:
        raise ValueError("model arithmetic overflow or singular denominator") from exc
    result = {"outputs": outputs, "sensitivity": sensitivity}
    if tornado is not None:
        result["tornado"] = tornado_rows
    return result


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
