#!/usr/bin/env python3
"""Assemble financial_quality statements from claim.metric blocks (Python 3.9+).

`financial_quality.py` reads a standardized statements document. Writing that
document by hand re-introduces the transcription risk the ledger exists to
remove. This adapter reads a claims ledger, maps metric names to statement
fields, groups them into comparable periods and emits the statements document
with each value still pointing back at its claim ids.

It does not validate the ledger (check_claims does), does not create claims and
does not compute quality metrics. Unmapped or unusable metrics are reported in
`ignored` rather than silently dropped.
"""

import argparse
import json
import sys
from pathlib import Path

FIELD_ALIASES = {
    "revenue": ("revenue", "revenues", "sales", "收入", "营业收入"),
    "gross_profit": ("gross_profit", "gross profit", "毛利", "毛利润"),
    "operating_profit": ("operating_profit", "operating income", "营业利润", "经营利润"),
    "net_income": ("net_income", "net income", "净利润"),
    "cfo": ("cfo", "operating cash flow", "cash from operations", "经营现金流", "经营活动现金流"),
    "capex": ("capex", "capital expenditure", "capital expenditures", "资本开支", "资本支出"),
    "depreciation_amortization": ("d&a", "depreciation", "depreciation and amortization", "折旧摊销", "折旧与摊销"),
    "receivables": ("receivables", "accounts receivable", "应收账款"),
    "inventory": ("inventory", "inventories", "存货"),
    "payables": ("payables", "accounts payable", "应付账款"),
    "total_assets": ("total_assets", "total assets", "总资产"),
    "equity": ("equity", "shareholders equity", "shareholders' equity", "股东权益", "所有者权益"),
    "debt": ("debt", "total debt", "有息负债", "债务"),
    "cash": ("cash", "cash and equivalents", "现金", "现金及等价物"),
    "share_based_comp": ("sbc", "share based compensation", "stock based compensation", "股权激励", "股份支付"),
    "shares_diluted": ("diluted shares", "shares_diluted", "摊薄股本", "稀释股数"),
    "tax_rate": ("tax_rate", "effective tax rate", "有效税率"),
    "pretax_income": ("pretax_income", "income before tax", "pre-tax income", "税前利润", "税前收入"),
    "income_tax": ("income_tax", "income tax expense", "provision for income tax", "所得税费用"),
}
PERIOD_TYPES = ("fy", "quarter", "ltm")
RATIO_FIELDS = {"tax_rate"}


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _normalise(value):
    if not _text(value):
        return ""
    return " ".join(value.strip().casefold().replace("_", " ").replace("-", " ").split())


ALIASES = {field: {_normalise(alias) for alias in aliases} for field, aliases in FIELD_ALIASES.items()}
FIELD_FOR_NAME = {alias: field for field, aliases in ALIASES.items() for alias in aliases}


def _number(value):
    import math
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    try:
        return value if math.isfinite(value) else None
    except OverflowError:
        return None


def _metric(claim):
    metric = claim.get("metric") if isinstance(claim, dict) else None
    return metric if isinstance(metric, dict) else None


def assemble(claims, entity=None, currency=None, scale=None, as_of=None):
    """Return (statements, None) or raise ValueError with a readable reason."""
    rows, ignored = [], []
    for claim in claims if isinstance(claims, list) else []:
        metric = _metric(claim)
        if metric is None:
            continue
        claim_id = claim.get("id")
        name = _normalise(metric.get("name"))
        field = FIELD_FOR_NAME.get(name)
        if field is None:
            ignored.append({"claim_id": claim_id, "reason": "metric name is not a statement field"})
            continue
        if metric.get("period_type") not in PERIOD_TYPES:
            ignored.append({"claim_id": claim_id, "reason": "period_type " + str(metric.get("period_type")) +
                            " cannot form a comparable statement period"})
            continue
        if not (_text(metric.get("period_start")) and _text(metric.get("period_end"))):
            ignored.append({"claim_id": claim_id, "reason": "period_start and period_end are required"})
            continue
        scope = _normalise(metric.get("scope")) or "consolidated"
        if scope != "consolidated":
            ignored.append({"claim_id": claim_id, "reason": "only consolidated scope is assembled (" + scope + ")"})
            continue
        metric_entity = metric.get("entity") if _text(metric.get("entity")) else ""
        if entity is not None and _normalise(metric_entity) != _normalise(entity):
            ignored.append({"claim_id": claim_id, "reason": "entity does not match " + str(entity)})
            continue
        value = _number(metric.get("value"))
        if value is None:
            ignored.append({"claim_id": claim_id, "reason": "metric value is not finite"})
            continue
        if field in RATIO_FIELDS:
            unit = _normalise(metric.get("unit"))
            if unit in ("percent", "%", "百分比"):
                value = value / 100
        rows.append({"claim_id": claim_id, "field": field, "value": value,
                     "period_type": metric["period_type"], "period_start": metric["period_start"],
                     "period_end": metric["period_end"], "entity": metric_entity,
                     "currency": metric.get("currency", ""), "scale": metric.get("scale", ""),
                     "as_of": claim.get("as_of", "")})
    if not rows:
        raise ValueError("no usable claim.metric blocks for statements")
    entities = {_normalise(row["entity"]) for row in rows if row["entity"]}
    if len(entities) > 1:
        raise ValueError("multiple entities present; pass --entity to select one: " + ", ".join(sorted(entities)))
    if entity is None and entities:
        entity = next(row["entity"] for row in rows if row["entity"])
    currencies = {row["currency"].strip() for row in rows if _text(row["currency"])}
    scales = {row["scale"].strip() for row in rows if _text(row["scale"])}
    currency = currency or (currencies.pop() if len(currencies) == 1 else None)
    scale = scale or (scales.pop() if len(scales) == 1 else None)
    if not currency or not scale:
        raise ValueError("currency and scale must be consistent in the ledger or passed explicitly")
    periods, conflicts = {}, {}
    for row in rows:
        key = (row["period_type"], row["period_start"], row["period_end"])
        bucket = periods.setdefault(key, {})
        existing = bucket.get(row["field"])
        if existing is None:
            bucket[row["field"]] = {"value": row["value"], "claim_ids": [row["claim_id"]]}
        elif abs(existing["value"] - row["value"]) <= max(1e-9 * abs(existing["value"]), 1e-12):
            existing["claim_ids"].append(row["claim_id"])
        else:
            conflicts.setdefault(key, []).append(row["field"] + ": " +
                                                 existing["claim_ids"][0] + "=" + str(existing["value"]) +
                                                 " vs " + str(row["claim_id"]) + "=" + str(row["value"]))
    if conflicts:
        raise ValueError("conflicting values for the same period and field: " + json.dumps(
            {" / ".join(key): values for key, values in conflicts.items()}, ensure_ascii=False))
    ordered = sorted(periods, key=lambda key: (key[2], key[0]))
    if len(ordered) < 2:
        raise ValueError("at least two comparable periods are required; found " + str(len(ordered)))
    statements = {
        "schema_version": 1, "entity": entity or "", "currency": currency, "scale": scale,
        "as_of": as_of or max((row["as_of"] for row in rows if _text(row["as_of"])), default=""),
        "periods": [dict({"id": period_id(*key), "period_type": key[0],
                          "period_start": key[1], "period_end": key[2]}, **periods[key])
                    for key in ordered],
        "source_claims": sorted({row["claim_id"] for row in rows if isinstance(row["claim_id"], str)}),
        "ignored": ignored,
    }
    return statements, None


def period_id(period_type, period_start, period_end):
    return "%s@%s" % (period_type.upper(), str(period_end)[:10])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path, help="claims.json ledger")
    parser.add_argument("--entity", help="only assemble metrics for this entity")
    parser.add_argument("--currency")
    parser.add_argument("--scale")
    parser.add_argument("--as-of", dest="as_of")
    parser.add_argument("--out", type=Path)
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
    try:
        statements, _ = assemble(claims, args.entity, args.currency, args.scale, args.as_of)
    except ValueError as exc:
        print(json.dumps({"passed": False, "errors": [str(exc)]}, ensure_ascii=False))
        return 1
    text = json.dumps(statements, ensure_ascii=False, indent=2, allow_nan=False)
    if args.out:
        args.out.write_text(text + "\n", encoding="utf-8")
        print(json.dumps({"passed": True, "periods": len(statements["periods"]),
                          "written": str(args.out), "ignored": len(statements["ignored"])},
                         ensure_ascii=False))
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
