#!/usr/bin/env python3
"""Put price-implied growth next to consensus growth, without merging them (Python 3.9+).

Two "growth" numbers show up in research and are easy to confuse:

- reverse DCF implied growth: the constant multi-year growth rate that the current
  price implies, given explicit discount and terminal assumptions;
- consensus period growth: the year-over-year change between two adjacent fiscal
  year medians from the same expectation series.

They answer different questions over different horizons. This script prints them
side by side with the horizon spelled out and refuses to subtract one from the
other. It reads a frozen report and its claims; it computes nothing new beyond
what those already contain.

    python3 "$TY_DIR/scripts/expectation_compare.py" report.json --claims claims.json [--markdown]
"""

import argparse
import json
import sys
from pathlib import Path


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _ratio(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    try:
        return value
    except OverflowError:
        return None


def implied_growth_side(report):
    """Reverse-DCF implied growth per model, with the horizon its spec declares."""
    analysis = report.get("analysis") if isinstance(report, dict) else None
    models = analysis.get("models") if isinstance(analysis, dict) else None
    rows = []
    for model in models if isinstance(models, list) else []:
        if not isinstance(model, dict):
            continue
        spec = model.get("spec") if isinstance(model.get("spec"), dict) else {}
        if spec.get("kind") != "reverse_dcf":
            continue
        outputs = (model.get("result") or {}).get("outputs") or {}
        growth = _ratio((outputs.get("implied_growth") or {}).get("value"))
        if growth is None:
            continue
        inputs = spec.get("inputs") or {}
        years = (inputs.get("years") or {}).get("value")
        rows.append({"model_id": model.get("id"), "instrument": model.get("instrument", ""),
                     "implied_growth": growth, "years": years,
                     "horizon": ("未来 %s 年的恒定增长（价格隐含）" % years) if isinstance(years, (int, float))
                     else "多年恒定增长（价格隐含，年限未记录）"})
    return rows


def consensus_side(claims):
    """Adjacent fiscal-year growth from the same expectation series."""
    import consensus
    result = consensus.analyse(claims)
    rows = []
    for row in result.get("period_growth") or []:
        rows.append({"series_id": row["series_id"], "metric": row["metric"],
                     "from_period": row["from_period"], "to_period": row["to_period"],
                     "implied_growth": row["implied_growth"],
                     "from_claim": row["from_claim"], "to_claim": row["to_claim"],
                     "horizon": "相邻财年共识增幅（%s → %s）" % (row["from_period"], row["to_period"])})
    return rows, result.get("warnings") or []


def build(report, claims):
    price_rows = implied_growth_side(report)
    consensus_rows, warnings = consensus_side(claims)
    notes = [
        "两列口径不同：左列是价格隐含的多年恒定增长，右列是相邻财年的共识增幅。",
        "不要相减成单一「预期差」：期限、假设与信息来源都不同，相减会制造不存在的精度。",
        "任一侧缺失时只展示已有的一侧，并说明缺失原因。",
    ]
    findings = []
    if not price_rows:
        findings.append("报告中没有可用的 reverse_dcf 模型结果，价格隐含增长缺失。")
    if not consensus_rows:
        findings.append("账本中没有相邻财年的共识快照，共识增长缺失。")
    return {"passed": True, "price_implied_growth": price_rows,
            "consensus_growth": consensus_rows, "warnings": warnings,
            "notes": notes, "gaps": findings}


def render_markdown(result):
    lines = ["# 预期对照（口径不同，不可相减）", ""]
    if result["price_implied_growth"]:
        lines.append("## 价格隐含增长（反向 DCF）")
        lines.append("")
        lines.append("| 模型 | 标的 | 隐含增长 | 期限 |")
        lines.append("| --- | --- | --- | --- |")
        for row in result["price_implied_growth"]:
            lines.append("| %s | %s | %.4f | %s |" % (row["model_id"], row["instrument"],
                                                      row["implied_growth"], row["horizon"]))
    if result["consensus_growth"]:
        lines.append("")
        lines.append("## 共识相邻财年增长")
        lines.append("")
        lines.append("| 序列 | 指标 | 自 | 至 | 隐含增长 |")
        lines.append("| --- | --- | --- | --- | --- |")
        for row in result["consensus_growth"]:
            lines.append("| %s | %s | %s | %s | %.4f |" % (row["series_id"], row["metric"],
                                                          row["from_period"], row["to_period"],
                                                          row["implied_growth"]))
    lines.extend(["", "## 边界", ""])
    for note in result["notes"]:
        lines.append("- " + note)
    for gap in result["gaps"]:
        lines.append("- 缺失：" + gap)
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument("--claims", type=Path, required=True)
    parser.add_argument("--markdown", action="store_true")
    args = parser.parse_args()
    try:
        report = json.loads(args.report.read_text(encoding="utf-8"))
        ledger = json.loads(args.claims.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(json.dumps({"passed": False, "errors": [str(exc)]}, ensure_ascii=False))
        return 2
    if not isinstance(report, dict):
        print(json.dumps({"passed": False, "errors": ["report must be an object"]}, ensure_ascii=False))
        return 1
    claims = ledger.get("claims") if isinstance(ledger, dict) else None
    if not isinstance(claims, list):
        print(json.dumps({"passed": False, "errors": ["ledger.claims must be a list"]}, ensure_ascii=False))
        return 1
    result = build(report, claims)
    if args.markdown:
        print(render_markdown(result), end="")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
