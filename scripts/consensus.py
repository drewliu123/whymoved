#!/usr/bin/env python3
"""Consensus snapshots, revisions and guidance records (Python 3.9+).

`expectations.md` already asks for the same target period at two cutoffs and for
company guidance to be labelled as guidance. This module makes those records
machine-checkable without inventing a data feed:

    consensus claim:  block "consensus" = {series_id, metric, target_period,
                      provider, sample_size, median, low, high}
    fact claim:       block "guidance" = {metric, target_period, midpoint,
                      low?, high?}

Hard rules: a series id + target period identifies the same expectations series;
snapshots must be ordered by claim as_of; dispersion is (high - low) / |median|;
guidance is only allowed on fact claims and never on consensus claims. The tool
computes revisions between snapshots and lists guidance separately; it does not
decide what is "in line" or "beating" anything.
"""

import argparse
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SERIES_ID = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]*$")
FISCAL_YEAR = re.compile(r"^\s*fy\s*((?:19|20)\d{2})\s*$", re.IGNORECASE)
CONSENSUS_REQUIRED = ("series_id", "metric", "target_period", "provider", "sample_size", "median", "low", "high")
GUIDANCE_REQUIRED = ("metric", "target_period", "midpoint")
GUIDANCE_OPTIONAL = ("low", "high")


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
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def validate_claim_blocks(claim):
    """Validate optional consensus/guidance blocks on one claim."""
    if not isinstance(claim, dict):
        return []
    errors = []
    ctype = claim.get("type")
    if "consensus" in claim:
        if ctype != "consensus":
            errors.append("C1 consensus block is only allowed on consensus claims")
        errors.extend(_validate_consensus(claim["consensus"], "consensus"))
    if "guidance" in claim:
        if ctype == "consensus":
            errors.append("C1 guidance cannot stand in for analyst consensus; label it as a fact")
        elif ctype != "fact":
            errors.append("C1 guidance block is only allowed on fact claims")
        errors.extend(_validate_guidance(claim["guidance"], "guidance"))
    return errors


def _validate_consensus(block, path):
    if not isinstance(block, dict):
        return [path + " must be an object"]
    errors = []
    unknown = set(block) - set(CONSENSUS_REQUIRED)
    if unknown:
        errors.append(path + " has unknown fields: " + ", ".join(sorted(map(str, unknown))))
    missing = [field for field in CONSENSUS_REQUIRED if field not in block]
    if missing:
        return errors + [path + " missing fields: " + ", ".join(missing)]
    if not isinstance(block["series_id"], str) or not SERIES_ID.fullmatch(block["series_id"]):
        errors.append(path + ".series_id must be a safe identifier")
    for field in ("metric", "target_period", "provider"):
        if not _text(block[field]):
            errors.append(path + "." + field + " must be nonempty text")
    if type(block["sample_size"]) is not int or block["sample_size"] < 2:
        errors.append(path + ".sample_size must be an integer >= 2")
    values = {}
    for field in ("median", "low", "high"):
        number = _number(block[field])
        if number is None:
            errors.append(path + "." + field + " must be a finite number")
        else:
            values[field] = number
    if len(values) == 3 and not values["low"] <= values["median"] <= values["high"]:
        errors.append(path + " requires low <= median <= high")
    return errors


def _validate_guidance(block, path):
    if not isinstance(block, dict):
        return [path + " must be an object"]
    errors = []
    unknown = set(block) - set(GUIDANCE_REQUIRED) - set(GUIDANCE_OPTIONAL)
    if unknown:
        errors.append(path + " has unknown fields: " + ", ".join(sorted(map(str, unknown))))
    missing = [field for field in GUIDANCE_REQUIRED if field not in block]
    if missing:
        return errors + [path + " missing fields: " + ", ".join(missing)]
    for field in ("metric", "target_period"):
        if not _text(block[field]):
            errors.append(path + "." + field + " must be nonempty text")
    values = {}
    for field in ("midpoint", "low", "high"):
        if field not in block:
            continue
        number = _number(block[field])
        if number is None:
            errors.append(path + "." + field + " must be a finite number")
        else:
            values[field] = number
    if "midpoint" in values and "low" in values and "high" in values:
        if not values["low"] <= values["midpoint"] <= values["high"]:
            errors.append(path + " requires low <= midpoint <= high")
    elif "low" in values and "high" in values and values["low"] > values["high"]:
        errors.append(path + " requires low <= high")
    return errors


def snapshots(claims):
    """Return consensus snapshots ordered by claim as_of, grouped downstream."""
    rows = []
    for claim in claims if isinstance(claims, list) else []:
        if not isinstance(claim, dict) or claim.get("type") != "consensus":
            continue
        block = claim.get("consensus")
        if not isinstance(block, dict) or _validate_consensus(block, "consensus"):
            continue
        rows.append({"claim_id": claim.get("id"), "as_of": claim.get("as_of", ""),
                     "series_id": block["series_id"], "metric": block["metric"],
                     "target_period": block["target_period"], "provider": block["provider"],
                     "sample_size": block["sample_size"], "median": block["median"],
                     "low": block["low"], "high": block["high"]})
    rows.sort(key=lambda row: (_date(row["as_of"]) or datetime.min.replace(tzinfo=timezone.utc),
                               row["claim_id"] or ""))
    return rows


def guidance_entries(claims):
    rows = []
    for claim in claims if isinstance(claims, list) else []:
        if not isinstance(claim, dict) or claim.get("type") != "fact":
            continue
        block = claim.get("guidance")
        if not isinstance(block, dict) or _validate_guidance(block, "guidance"):
            continue
        rows.append({"claim_id": claim.get("id"), "as_of": claim.get("as_of", ""),
                     "metric": block["metric"], "target_period": block["target_period"],
                     "midpoint": block["midpoint"], "low": block.get("low"), "high": block.get("high")})
    return rows


def _dispersion(row):
    if row["median"] == 0:
        return None
    return (row["high"] - row["low"]) / abs(row["median"])


def _period_growth(series):
    """Implied growth between consecutive fiscal years of the same series."""
    rows, warnings = [], []
    grouped = {}
    for item in series:
        match = FISCAL_YEAR.match(str(item.get("target_period", "")))
        if not match:
            continue
        grouped.setdefault(item["series_id"], []).append((int(match.group(1)), item))
    for series_id, items in sorted(grouped.items()):
        items.sort(key=lambda pair: pair[0])
        for (year_from, earlier), (year_to, later) in zip(items, items[1:]):
            if year_to != year_from + 1:
                continue
            if earlier["providers"] != later["providers"]:
                warnings.append("period growth skipped for " + series_id + ": providers differ between " +
                                earlier["target_period"] + " and " + later["target_period"])
                continue
            if earlier["metric"].strip().casefold() != later["metric"].strip().casefold():
                warnings.append("period growth skipped for " + series_id + ": metric labels differ")
                continue
            if not earlier["snapshots"] or not later["snapshots"]:
                continue
            start, end = earlier["snapshots"][-1], later["snapshots"][-1]
            if start["median"] in (0, None):
                warnings.append("period growth skipped for " + series_id + ": base median is zero")
                continue
            rows.append({"series_id": series_id, "metric": later["metric"],
                         "from_period": earlier["target_period"], "to_period": later["target_period"],
                         "from_median": start["median"], "to_median": end["median"],
                         "from_claim": start["claim_id"], "to_claim": end["claim_id"],
                         "implied_growth": end["median"] / start["median"] - 1})
    return rows, warnings


def analyse(claims):
    """Group snapshots into series, compute revisions and surface comparability warnings."""
    rows = snapshots(claims)
    groups = {}
    for row in rows:
        groups.setdefault((row["series_id"], row["target_period"]), []).append(row)
    series, warnings = [], []
    for (series_id, target_period), items in sorted(groups.items()):
        providers = sorted({item["provider"] for item in items})
        metrics = sorted({item["metric"].strip().casefold() for item in items})
        if len(providers) > 1:
            warnings.append(series_id + " " + target_period + " mixes providers: " + ", ".join(providers) +
                            "; revisions across providers are not comparable")
        if len(metrics) > 1:
            warnings.append(series_id + " " + target_period + " mixes metric labels: " + ", ".join(metrics))
        if len(items) < 2:
            warnings.append(series_id + " " + target_period + " has a single snapshot; no revision available")
        revisions = []
        for previous, current in zip(items, items[1:]):
            delta = current["median"] - previous["median"]
            pct = (delta / previous["median"]) if previous["median"] != 0 else None
            if delta > 0:
                direction = "up"
            elif delta < 0:
                direction = "down"
            else:
                direction = "flat"
            revisions.append({"from": previous["claim_id"], "to": current["claim_id"],
                              "from_as_of": previous["as_of"], "to_as_of": current["as_of"],
                              "delta": delta, "pct": pct, "direction": direction})
        series.append({"series_id": series_id, "target_period": target_period,
                       "metric": items[0]["metric"], "providers": providers,
                       "snapshots": [{"claim_id": item["claim_id"], "as_of": item["as_of"],
                                      "provider": item["provider"], "sample_size": item["sample_size"],
                                      "median": item["median"], "low": item["low"], "high": item["high"],
                                      "dispersion": _dispersion(item)} for item in items],
                       "revisions": revisions})
    growth_rows, growth_warnings = _period_growth(series)
    warnings.extend(growth_warnings)
    return {"passed": True, "series": series, "period_growth": growth_rows,
            "guidance": guidance_entries(claims), "warnings": warnings,
            "notes": ["修订只在同一series_id与target_period内计算，跨提供方不可直接比较。",
                      "period_growth只在同一序列、同一提供方、相邻财年之间计算；非FY标签不推断。",
                      "离散度=(high-low)/|median|，样本量必须一并看。",
                      "指引与共识分开列出；指引不能替代分析师共识。"]}


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
    errors = []
    for claim in claims:
        for error in validate_claim_blocks(claim):
            errors.append(str(claim.get("id") if isinstance(claim, dict) else "?") + ": " + error)
    if errors:
        print(json.dumps({"passed": False, "errors": errors}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(analyse(claims), ensure_ascii=False, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
