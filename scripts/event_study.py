#!/usr/bin/env python3
"""Reference-class event study over supplied price series (Python 3.9+).

For an event type ("earnings miss", "ETF outflow streak", "guidance cut"), this
computes what happened to the instrument around *similar past events that the
researcher chose in advance*. It answers "what did the reference class do",
not "what will happen now".

Input:

    {"schema_version": 1, "event": "guidance cut",
     "window": {"before": 5, "after": 10},
     "samples": [
        {"id": "E1", "date": "2025-05-15", "label": "FY25 guidance cut",
         "claim_ids": ["C1"],
         "prices": [{"date": "2025-05-08", "close": 100}, ...]}
     ]}

Window units are **observations** in each sample's own price series (typically
trading days), not calendar days: `before` points before the event close and
`after` points after it. Returns are absolute, not excess over a benchmark, and
no p-value is produced — small, hand-picked samples do not support significance
claims. Samples that cannot cover the window are skipped with a reason; at least
two usable samples are required.
"""

import argparse
import json
import math
import sys
from pathlib import Path

SCHEMA_VERSION = 1
MAX_WINDOW = 250


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    try:
        return value if math.isfinite(value) else None
    except OverflowError:
        return None


def _percentile(values, fraction):
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * fraction
    lower, upper = math.floor(position), math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def validate_document(document):
    """Validate structure of the event document (not sample coverage)."""
    if not isinstance(document, dict):
        return ["E1 document must be an object"]
    errors = []
    if document.get("schema_version") != SCHEMA_VERSION:
        errors.append("E1 schema_version must be %d" % SCHEMA_VERSION)
    if not _text(document.get("event")):
        errors.append("E1 event must be nonempty text")
    window = document.get("window")
    if not isinstance(window, dict):
        return errors + ["E1 window must be an object"]
    extra = set(window) - {"before", "after"}
    if extra:
        errors.append("E1 window has unknown fields: " + ", ".join(sorted(map(str, extra))))
    bounds = {}
    for name in ("before", "after"):
        value = window.get(name)
        if type(value) is not int or not 0 <= value <= MAX_WINDOW:
            errors.append("E1 window." + name + " must be an integer from 0 to %d" % MAX_WINDOW)
        else:
            bounds[name] = value
    if len(bounds) == 2 and bounds["after"] == 0:
        errors.append("E1 window.after must be at least one observation")
    samples = document.get("samples")
    if not isinstance(samples, list) or len(samples) < 2:
        return errors + ["E1 at least two samples are required"]
    seen = set()
    for index, sample in enumerate(samples):
        path = "E1 samples[%d]" % index
        if not isinstance(sample, dict):
            errors.append(path + " must be an object")
            continue
        extra = set(sample) - {"id", "date", "label", "claim_ids", "prices"}
        if extra:
            errors.append(path + " has unknown fields: " + ", ".join(sorted(map(str, extra))))
        identifier = sample.get("id")
        if not _text(identifier):
            errors.append(path + ".id must be nonempty text")
        elif identifier in seen:
            errors.append(path + ".id duplicates another sample")
        else:
            seen.add(identifier)
        if not _text(sample.get("date")):
            errors.append(path + ".date must be nonempty text")
        if "claim_ids" in sample and (not isinstance(sample["claim_ids"], list) or
                                      any(not _text(cid) for cid in sample["claim_ids"])):
            errors.append(path + ".claim_ids must be a list of claim ids")
        prices = sample.get("prices")
        if not isinstance(prices, list) or len(prices) < 2:
            errors.append(path + ".prices must be a series with at least two points")
            continue
        last = None
        for point in prices:
            if not isinstance(point, dict) or not _text(point.get("date")):
                errors.append(path + ".prices entries require a date")
                break
            close = _number(point.get("close"))
            if close is None or close <= 0:
                errors.append(path + ".prices entries require a positive finite close")
                break
            if last is not None and point["date"] <= last:
                errors.append(path + ".prices must be ordered by strictly increasing date")
                break
            last = point["date"]
    return errors


def sample_result(sample, before, after):
    """Return (result, None) or (None, reason) for one sample."""
    prices = [point for point in sample.get("prices", []) if isinstance(point, dict)]
    dates = [point.get("date") for point in prices]
    if sample.get("date") not in dates:
        return None, "event date is not in the price series"
    index = dates.index(sample["date"])
    if index - before < 0:
        return None, "not enough observations before the event"
    if index + after > len(prices) - 1:
        return None, "not enough observations after the event"
    start = _number(prices[index - before]["close"])
    event = _number(prices[index]["close"])
    end = _number(prices[index + after]["close"])
    if None in (start, event, end):
        return None, "prices contain a non-finite close"
    return {"id": sample.get("id"), "event_date": sample["date"],
            "label": sample.get("label", ""), "claim_ids": sample.get("claim_ids", []),
            "start_date": prices[index - before]["date"], "start_close": start,
            "event_close": event, "end_date": prices[index + after]["date"], "end_close": end,
            "pre_return": event / start - 1 if start else None,
            "post_return": end / event - 1 if event else None,
            "total_return": end / start - 1 if start else None}, None


def analyse(document):
    before, after = document["window"]["before"], document["window"]["after"]
    rows, skipped = [], []
    for sample in document.get("samples", []):
        if not isinstance(sample, dict):
            continue
        result, reason = sample_result(sample, before, after)
        if result is None:
            skipped.append({"id": sample.get("id"), "reason": reason})
        else:
            rows.append(result)
    if len(rows) < 2:
        raise ValueError("fewer than two usable samples after window checks; cannot describe a reference class")
    post = [row["post_return"] for row in rows if row["post_return"] is not None]
    pre = [row["pre_return"] for row in rows if row["pre_return"] is not None]
    total = [row["total_return"] for row in rows if row["total_return"] is not None]

    def summary(values):
        if not values:
            return None
        return {"n": len(values), "mean": sum(values) / len(values),
                "median": _percentile(values, 0.5), "min": min(values), "max": max(values),
                "q1": _percentile(values, 0.25), "q3": _percentile(values, 0.75),
                "positive_rate": sum(1 for value in values if value > 0) / len(values)}

    return {"passed": True, "event": document["event"], "window": document["window"],
            "samples": rows, "skipped": skipped,
            "summary": {"pre_return": summary(pre), "post_return": summary(post),
                        "total_return": summary(total)},
            "notes": ["窗口单位是每条价格序列自己的观测点（通常为交易日），不是自然日。",
                      "收益是绝对收益，不是相对基准的超额收益；样本由研究者事前选定。",
                      "不给p值或显著性结论：小样本与选择偏误不支持统计推断。",
                      "skipped列出的样本窗口不足或事件日缺失，不参与汇总。"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("document", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    try:
        document = json.loads(args.document.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(json.dumps({"passed": False, "errors": [str(exc)]}, ensure_ascii=False))
        return 2
    errors = validate_document(document)
    if not errors:
        try:
            result = analyse(document)
        except ValueError as exc:
            errors = [str(exc)]
    if errors:
        print(json.dumps({"passed": False, "errors": errors}, ensure_ascii=False, indent=2))
        return 1
    text = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)
    if args.out:
        args.out.write_text(text + "\n", encoding="utf-8")
        print(json.dumps({"passed": True, "samples": len(result["samples"]),
                          "written": str(args.out)}, ensure_ascii=False))
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
