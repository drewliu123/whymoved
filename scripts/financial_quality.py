#!/usr/bin/env python3
"""Earnings quality and forensic screening from standardized statements (Python 3.9+).

Real investment research asks a question models cannot: is this growth cash, or
is it accounting? This script turns two or more comparable periods into trend,
conversion, turnover and investment metrics plus a short list of red flags.

It only computes and flags. It does not conclude that a company is manipulating
earnings, does not score management, and does not replace reading the filing.
Every threshold is an empirical default that a researcher can override; a flag
is a prompt to check a disclosure, not a finding.

Input document:

    {"schema_version": 1, "entity": "EXAMPLE", "currency": "USD", "scale": "million",
     "as_of": "2026-11-14",
     "periods": [
        {"id": "FY2025", "period_type": "fy", "period_start": "2025-01-01",
         "period_end": "2025-12-31", "revenue": 1000, "cfo": {"value": 120, "claim_ids": ["C3"]}},
        {"id": "FY2024", "period_type": "fy", "period_start": "2024-01-01",
         "period_end": "2024-12-31", "revenue": 800}
     ]}

Every numeric field accepts a bare number or {"value": number, "claim_ids": [...]}.
Fields without claim_ids are reported as unattributed so the researcher can see
which numbers still need an evidence link.
"""

import argparse
import json
import math
import sys
from datetime import datetime
from pathlib import Path

SCHEMA_VERSION = 1
PERIOD_TYPES = ("fy", "quarter", "ltm")
FIELDS = (
    "revenue", "gross_profit", "operating_profit", "net_income", "cfo", "capex",
    "depreciation_amortization", "receivables", "inventory", "payables",
    "total_assets", "equity", "debt", "cash", "share_based_comp", "shares_diluted", "tax_rate",
)
PERIOD_REQUIRED = ("id", "period_end", "revenue")
PERIOD_OPTIONAL = ("period_type", "period_start") + FIELDS
THRESHOLDS = {
    "accrual_ratio": 0.10,
    "cash_conversion": 0.80,
    "dso_growth": 0.15,
    "dio_growth": 0.20,
    "capex_to_da": 0.80,
    "sbc_ratio": 0.10,
    "share_growth": 0.02,
    "margin_drop": 0.02,
    "conversion_drop": 0.05,
}


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
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _ratio(numerator, denominator):
    if numerator is None or denominator is None or denominator == 0:
        return None
    return numerator / denominator


def _field(period, name):
    """Return (value, claim_ids or None) for a numeric field."""
    raw = period.get(name)
    if raw is None:
        return None, None
    if isinstance(raw, dict):
        value = _number(raw.get("value"))
        refs = raw.get("claim_ids")
        return value, refs if isinstance(refs, list) else None
    return _number(raw), None


def validate_document(document):
    """Validate shape and comparability; returns F-prefixed errors."""
    if not isinstance(document, dict):
        return ["FQ1 document must be an object"]
    errors = []
    if document.get("schema_version") != SCHEMA_VERSION:
        errors.append("FQ1 schema_version must be %d" % SCHEMA_VERSION)
    for field in ("entity", "currency", "scale"):
        if not _text(document.get(field)):
            errors.append("FQ1 document." + field + " must be nonempty text")
    periods = document.get("periods")
    if not isinstance(periods, list) or len(periods) < 2:
        return errors + ["FQ1 at least two comparable periods are required"]
    seen, kinds = set(), set()
    for index, period in enumerate(periods):
        path = "periods[%d]" % index
        if not isinstance(period, dict):
            errors.append("FQ1 " + path + " must be an object")
            continue
        unknown = set(period) - set(PERIOD_REQUIRED) - set(PERIOD_OPTIONAL)
        if unknown:
            errors.append("FQ1 " + path + " has unknown fields: " + ", ".join(sorted(map(str, unknown))))
        for field in PERIOD_REQUIRED:
            if field not in period:
                errors.append("FQ1 " + path + " missing " + field)
        identifier = period.get("id")
        if not _text(identifier):
            errors.append("FQ1 " + path + ".id must be nonempty text")
        elif identifier in seen:
            errors.append("FQ1 " + path + ".id duplicates another period")
        else:
            seen.add(identifier)
        end = _date(period.get("period_end"))
        if end is None:
            errors.append("FQ2 " + path + ".period_end must be an ISO date")
        start = _date(period.get("period_start")) if "period_start" in period else None
        if "period_start" in period and start is None:
            errors.append("FQ2 " + path + ".period_start must be an ISO date")
        if start is not None and end is not None and start >= end:
            errors.append("FQ2 " + path + ".period_start must be before period_end")
        kind = period.get("period_type", "fy")
        if kind not in PERIOD_TYPES:
            errors.append("FQ1 " + path + ".period_type must be one of " + ", ".join(PERIOD_TYPES))
        kinds.add(kind)
        for field in FIELDS:
            if field not in period:
                continue
            value, refs = _field(period, field)
            if value is None:
                errors.append("FQ1 " + path + "." + field + " must be a finite number or {value, claim_ids}")
                continue
            if field == "revenue" and value <= 0:
                errors.append("FQ1 " + path + ".revenue must be positive")
            if field in ("capex", "debt", "cash", "shares_diluted") and value < 0:
                errors.append("FQ1 " + path + "." + field + " must be nonnegative")
            if field == "tax_rate" and not 0 <= value <= 1:
                errors.append("FQ1 " + path + ".tax_rate must be between 0 and 1")
            if refs is not None and (not refs or any(not _text(ref) for ref in refs)):
                errors.append("FQ3 " + path + "." + field + ".claim_ids must be a nonempty string list")
    if len(kinds) > 1:
        errors.append("FQ2 periods must share one period_type; mixing fy/quarter/ltm is not comparable")
    return errors


def _period_days(period):
    start, end = _date(period.get("period_start")), _date(period.get("period_end"))
    if start is None or end is None:
        return None
    days = (end - start).days
    return days if days > 0 else None


def period_metrics(period):
    """Compute level metrics for one period; missing inputs yield None."""
    revenue, _ = _field(period, "revenue")
    gross, _ = _field(period, "gross_profit")
    operating, _ = _field(period, "operating_profit")
    net, _ = _field(period, "net_income")
    cfo, _ = _field(period, "cfo")
    capex, _ = _field(period, "capex")
    da, _ = _field(period, "depreciation_amortization")
    receivables, _ = _field(period, "receivables")
    inventory, _ = _field(period, "inventory")
    payables, _ = _field(period, "payables")
    assets, _ = _field(period, "total_assets")
    equity, _ = _field(period, "equity")
    debt, _ = _field(period, "debt")
    cash, _ = _field(period, "cash")
    sbc, _ = _field(period, "share_based_comp")
    shares, _ = _field(period, "shares_diluted")
    tax, _ = _field(period, "tax_rate")
    days = _period_days(period)
    cogs = revenue - gross if revenue is not None and gross is not None else None
    metrics = {
        "revenue": revenue,
        "gross_margin": _ratio(gross, revenue),
        "operating_margin": _ratio(operating, revenue),
        "net_margin": _ratio(net, revenue),
        "cash_conversion": _ratio(cfo, net) if net is not None and net > 0 else None,
        "accrual_ratio": _ratio((net - cfo) if net is not None and cfo is not None else None,
                                assets) if assets is not None and assets > 0 else None,
        "dso": _ratio(receivables * days, revenue) if receivables is not None and days else None,
        "dio": _ratio(inventory * days, cogs) if inventory is not None and days and cogs and cogs > 0 else None,
        "dpo": _ratio(payables * days, cogs) if payables is not None and days and cogs and cogs > 0 else None,
        "capex_intensity": _ratio(capex, revenue),
        "capex_to_da": _ratio(capex, da) if capex is not None and da is not None and da > 0 else None,
        "sbc_ratio": _ratio(sbc, revenue),
        "invested_capital": (equity + debt - cash) if None not in (equity, debt, cash) else None,
        "roic": None,
        "shares_diluted": shares,
    }
    gross_cycle = [value for value in (metrics["dso"], metrics["dio"]) if value is not None]
    if metrics["dpo"] is not None:
        metrics["cash_cycle"] = sum(gross_cycle) - metrics["dpo"] if gross_cycle else None
    else:
        metrics["cash_cycle"] = None
    invested = metrics["invested_capital"]
    if operating is not None and invested is not None and invested > 0:
        after_tax = operating * (1 - tax) if tax is not None else operating
        metrics["roic"] = after_tax / invested
    return metrics


def period_changes(previous, current):
    """Period-over-period changes; None when either side is missing."""
    changes = {}

    def add(name, old, new):
        changes[name] = (new - old) if old is not None and new is not None else None

    def growth(name, old, new):
        changes[name] = (new / old - 1) if old not in (None, 0) and new is not None else None

    growth("revenue_growth", previous.get("revenue"), current.get("revenue"))
    add("gross_margin_change", previous.get("gross_margin"), current.get("gross_margin"))
    add("operating_margin_change", previous.get("operating_margin"), current.get("operating_margin"))
    add("net_margin_change", previous.get("net_margin"), current.get("net_margin"))
    growth("dso_change", previous.get("dso"), current.get("dso"))
    growth("dio_change", previous.get("dio"), current.get("dio"))
    growth("share_growth", previous.get("shares_diluted"), current.get("shares_diluted"))
    add("cash_conversion_change", previous.get("cash_conversion"), current.get("cash_conversion"))
    changes["incremental_margin"] = None
    revenue_now, revenue_prev = current.get("revenue"), previous.get("revenue")
    op_now, op_prev = current.get("operating_margin"), previous.get("operating_margin")
    if None not in (revenue_now, revenue_prev, op_now, op_prev) and revenue_now != revenue_prev:
        profit_now, profit_prev = op_now * revenue_now, op_prev * revenue_prev
        changes["incremental_margin"] = (profit_now - profit_prev) / (revenue_now - revenue_prev)
    return changes


def flags_for(period, changes, thresholds=None):
    """Return red-flag hints with the evidence that produced them."""
    limits = dict(THRESHOLDS)
    if thresholds:
        limits.update(thresholds)
    flags = []

    def flag(code, severity, message, evidence):
        flags.append({"code": code, "severity": severity, "message": message, "evidence": evidence})

    accrual = period.get("accrual_ratio")
    if accrual is not None and accrual > limits["accrual_ratio"]:
        flag("high_accruals", "high",
             "净利润中应计占比偏高，利润的现金支撑需要核对", {"accrual_ratio": accrual})
    conversion = period.get("cash_conversion")
    if conversion is not None and conversion < limits["cash_conversion"]:
        flag("weak_cash_conversion", "medium",
             "经营现金流低于净利润，需核对应收、存货与一次性项目", {"cash_conversion": conversion})
    sbc = period.get("sbc_ratio")
    if sbc is not None and sbc > limits["sbc_ratio"]:
        flag("high_sbc", "medium",
             "股权激励占收入偏高，non-GAAP利润与稀释需一并看", {"sbc_ratio": sbc})
    capex_da = period.get("capex_to_da")
    if capex_da is not None and capex_da < limits["capex_to_da"]:
        flag("low_capex_vs_da", "medium",
             "资本开支低于折旧摊销，需确认是维护性投入不足还是资产处置", {"capex_to_da": capex_da})
    if changes:
        revenue_growth = changes.get("revenue_growth")
        if revenue_growth is not None and revenue_growth > 0 and changes.get("cash_conversion_change") is not None \
                and changes["cash_conversion_change"] < -limits["conversion_drop"]:
            flag("growth_without_cash", "high",
                 "收入增长但现金转化下降，增长的质量需要证据", {
                     "revenue_growth": revenue_growth,
                     "cash_conversion_change": changes["cash_conversion_change"]})
        dso_change = changes.get("dso_change")
        if dso_change is not None and dso_change > limits["dso_growth"]:
            flag("receivables_outpacing_revenue", "high",
                 "应收账款周转天数上升快于收入，需核对账龄与客户结构", {"dso_change": dso_change})
        dio_change = changes.get("dio_change")
        if dio_change is not None and dio_change > limits["dio_growth"]:
            flag("inventory_build", "medium",
                 "存货周转天数明显上升，需核对备货理由与跌价准备", {"dio_change": dio_change})
        share_growth = changes.get("share_growth")
        if share_growth is not None and share_growth > limits["share_growth"]:
            flag("dilution", "medium",
                 "股本增加，回购是否抵消稀释需要核对", {"share_growth": share_growth})
        op_change = changes.get("operating_margin_change")
        if op_change is not None and op_change < -limits["margin_drop"] and revenue_growth is not None and revenue_growth > 0:
            flag("operating_deleverage", "medium",
                 "收入增长而营业利润率下降，增量成本需要拆解", {
                     "revenue_growth": revenue_growth, "operating_margin_change": op_change})
        gross_change = changes.get("gross_margin_change")
        if gross_change is not None and gross_change < -limits["margin_drop"]:
            flag("gross_margin_pressure", "medium",
                 "毛利率下降，需区分价格、产品结构与成本", {"gross_margin_change": gross_change})
        incremental = changes.get("incremental_margin")
        if incremental is not None and incremental < 0 and revenue_growth is not None and revenue_growth > 0:
            flag("negative_incremental_margin", "high",
                 "新增收入的增量利润为负，增长可能在消耗利润", {"incremental_margin": incremental})
    return flags


def analyse(document, thresholds=None):
    """Return the deterministic quality report for a validated statement document."""
    periods = sorted(document["periods"], key=lambda item: _date(item["period_end"]))
    rows, unattributed = [], {}
    for period in periods:
        metrics = period_metrics(period)
        rows.append({"id": period["id"], "period_end": period["period_end"],
                     "period_type": period.get("period_type", "fy"), "metrics": metrics})
        missing = []
        for field in FIELDS:
            if field not in period:
                continue
            _, refs = _field(period, field)
            if not refs:
                missing.append(field)
        unattributed[period["id"]] = missing
    all_flags, changes = [], []
    for index, row in enumerate(rows):
        if index == 0:
            delta = None
        else:
            delta = period_changes(rows[index - 1]["metrics"], row["metrics"])
            changes.append({"from": rows[index - 1]["id"], "to": row["id"], **delta})
        for flag in flags_for(row["metrics"], delta, thresholds):
            all_flags.append({"period": row["id"], **flag})
    notes = [
        "指标由输入数字确定性计算，输入是否正确仍需与原文核对。",
        "红旗是核查提示，不是舞弊或投资结论；阈值是经验默认值。",
        "同一期间类型才可比较；缺失字段不填补，直接略过相应指标。",
        "未标注 claim_ids 的字段列在 unattributed 中，说明证据链尚未接上。",
    ]
    return {"passed": True, "entity": document["entity"], "currency": document["currency"],
            "scale": document["scale"], "as_of": document.get("as_of", ""),
            "periods": rows, "changes": changes, "flags": all_flags,
            "unattributed": unattributed, "notes": notes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("statements", type=Path, help="standardized statements JSON")
    parser.add_argument("--out", type=Path, help="write the result JSON here instead of stdout")
    args = parser.parse_args()
    try:
        document = json.loads(args.statements.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(json.dumps({"passed": False, "errors": [str(exc)]}, ensure_ascii=False))
        return 2
    errors = validate_document(document)
    if errors:
        print(json.dumps({"passed": False, "errors": errors}, ensure_ascii=False, indent=2))
        return 1
    result = analyse(document)
    text = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)
    if args.out:
        args.out.write_text(text + "\n", encoding="utf-8")
        print(json.dumps({"passed": True, "written": str(args.out)}, ensure_ascii=False))
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
