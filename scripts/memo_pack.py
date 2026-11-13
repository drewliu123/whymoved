#!/usr/bin/env python3
"""One-page IC memo from a frozen report (Python 3.9+).

The full report is the record; a reader often needs a single page first. This
script derives that page from the frozen report, claims and sources — it copies
judgment, findings, catalysts, invalidation conditions and risks, and reads
valuation numbers from the frozen model outputs. It never computes new numbers
and never writes a report.json.

    python3 "$TY_DIR/scripts/memo_pack.py" report.json \\
        --claims claims.json --sources sources.json --out memo.md
"""

import argparse
import json
import re
import sys
from pathlib import Path

MAX_FINDINGS = 3
MAX_TEXT = 420
INLINE_ESCAPE = re.compile(r"([\\`*_\[\]])")
CELL_ESCAPE = re.compile(r"([\\`*_\[\]|])")


def _escape(value):
    """Escape only characters that would change inline Markdown structure."""
    return INLINE_ESCAPE.sub(r"\\\1", str(value)).replace("\n", " ")


def _cell(value):
    return CELL_ESCAPE.sub(r"\\\1", str(value)).replace("\n", " ")


def _clip(value, limit=MAX_TEXT):
    text = " ".join(str(value).split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def _date(value):
    return str(value or "").strip()


def _findings(report, limit):
    rows = []
    for finding in report.get("findings", []):
        if not isinstance(finding, dict):
            continue
        rows.append("**%s** — %s" % (_escape(finding.get("title", "")),
                                     _escape(_clip(finding.get("why_it_matters", "")))))
        if len(rows) >= limit:
            break
    return rows


def _valuation(report):
    summary = report.get("valuation_summary")
    analysis = report.get("analysis")
    if not isinstance(summary, dict) or not isinstance(analysis, dict):
        return []
    models = {model["id"]: model for model in analysis.get("models", []) if isinstance(model, dict)}
    rows = []
    for entry in summary.get("rows", []):
        model = models.get(entry.get("model_id"))
        if not isinstance(model, dict):
            continue
        spec = model.get("spec") or {}
        outputs = (model.get("result") or {}).get("outputs") or {}
        kind = spec.get("kind")
        label = entry.get("label", "")
        if isinstance(entry.get("period"), str) and entry["period"].strip():
            label = str(label) + "（" + entry["period"].strip() + "）"
        if kind == "relative_valuation" and "per_share_median" in outputs:
            rows.append("| %s | 每股价值 | %s | %s | %s | %s |" % (
                _cell(label), outputs["per_share_low"]["value"],
                outputs["per_share_median"]["value"], outputs["per_share_high"]["value"],
                _cell(outputs["per_share_median"]["unit"])))
        elif kind == "dcf" and "per_share" in outputs:
            mid = outputs["per_share"]["value"]
            values = [row["outputs"]["per_share"]["value"] for row in model.get("result", {}).get("sensitivity", [])
                      if isinstance(row, dict) and isinstance(row.get("outputs"), dict) and "per_share" in row["outputs"]]
            low, high = (min(values), max(values)) if values else (mid, mid)
            rows.append("| %s | 每股价值 | %s | %s | %s | %s |" % (
                _cell(label), low, mid, high, _cell(outputs["per_share"]["unit"])))
        elif kind == "reverse_dcf" and "implied_growth" in outputs:
            rows.append("| %s | 隐含增长率 | — | %s | — | ratio |" % (
                _cell(label), outputs["implied_growth"]["value"]))
    return rows


def _catalysts(report):
    from catalyst_calendar import extract_entries
    rows = []
    for entry in extract_entries(report):
        if not entry.get("due"):
            continue
        rows.append("- %s ｜ %s ｜ %s" % (_date(entry["due"]), _escape(entry.get("type") or ""),
                                          _escape(_clip(entry.get("signal", ""), 160))))
    rows.sort()
    return rows


def _conditions(report):
    rows = []
    analysis = report.get("analysis")
    if isinstance(analysis, dict):
        for test in analysis.get("tests", []):
            if not isinstance(test, dict):
                continue
            for field in ("weakens_if", "supports_if"):
                if test.get(field):
                    rows.append("- %s：%s" % (_escape(test.get("id", "")), _escape(_clip(test[field], 200))))
    for item in report.get("watch", []):
        if isinstance(item, dict) and item.get("signal"):
            rows.append("- 观察 %s：%s" % (_escape(_clip(item["signal"], 120)),
                                          _escape(_clip(item.get("meaning", ""), 160))))
    return rows


def _risks(report):
    rows = []
    for limit in report.get("limitations", []):
        if isinstance(limit, dict) and limit.get("material"):
            rows.append("- " + _escape(_clip(limit.get("text", ""), 240)))
    for item in report.get("alternatives", []):
        if isinstance(item, dict) and item.get("title"):
            rows.append("- 备选解释：" + _escape(item["title"]))
    return rows


def _bottleneck(report):
    """Bottleneck and paths from an embedded transmission map, if any."""
    document = report.get("transmission")
    if not isinstance(document, dict):
        return []
    from transmission import analyse
    try:
        result = analyse(document)
    except (KeyError, TypeError, ValueError):
        return []
    lines = ["", "## 传导瓶颈", "",
             "- 瓶颈：%s（%s）｜%s" % (_escape(result["bottleneck"]["label"]),
                                      _escape(result["bottleneck"]["node"]),
                                      _escape(result["bottleneck"]["reason"]))]
    if result.get("paths"):
        lines.append("- 路径：%s" % _escape("；".join(" → ".join(path) for path in result["paths"])))
    if result.get("warnings"):
        lines.append("- 提示：%s" % _escape("；".join(result["warnings"])))
    return lines


def _quality_flags(report):
    """Top red flags from embedded quality statements, if any."""
    quality = report.get("quality")
    if not isinstance(quality, dict) or not isinstance(quality.get("statements"), dict):
        return []
    from financial_quality import analyse
    try:
        result = analyse(quality["statements"], quality.get("thresholds"))
    except (KeyError, TypeError, ValueError):
        return []
    lines = ["", "## 质量红旗", ""]
    severity = {"high": 0, "medium": 1}
    flags = sorted(result.get("flags") or [], key=lambda item: severity.get(str(item.get("severity")), 2))
    if not flags:
        lines.append("- 未触发默认红旗阈值；这不等于没有风险。")
        return lines
    unattributed = {period: fields for period, fields in (result.get("unattributed") or {}).items() if fields}
    if unattributed:
        lines.append("- 未挂 claim 的字段：%s" % "；".join(
            "%s：%s" % (_escape(period), _escape("、".join(fields))) for period, fields in unattributed.items()))
    for item in flags[:5]:
        lines.append("- %s｜%s：%s" % (_escape(item["period"]), _escape(item["code"]),
                                       _escape(item["message"])))
    if len(flags) > 5:
        lines.append("- 其余 %d 条见完整报告" % (len(flags) - 5))
    return lines


def _ratio(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return "—"
    try:
        return str(round(value, 4))
    except (OverflowError, ValueError):
        return "—"


def _event_study(report):
    """Reference-class distribution from an embedded event study, if any."""
    document = report.get("event_study")
    if not isinstance(document, dict):
        return []
    from event_study import analyse as analyse_events
    try:
        result = analyse_events(document)
    except (KeyError, TypeError, ValueError):
        return []
    window = result["window"]
    lines = ["", "## 参考类事件", "",
             "- 事件：%s；窗口：−%s / +%s 个观测点" % (_escape(str(result["event"])), window["before"], window["after"])]
    for name, label in (("post_return", "后窗"), ("total_return", "全窗")):
        stats = result["summary"].get(name)
        if not stats:
            continue
        lines.append("- %s：n=%d，中位 %s，为正 %s，Q1—Q3 %s—%s" % (
            label, stats["n"], _ratio(stats["median"]), _ratio(stats["positive_rate"]),
            _ratio(stats["q1"]), _ratio(stats["q3"])))
    if result.get("skipped"):
        lines.append("- 跳过 %d 条样本（窗口不足或事件日缺失），详见完整报告。" % len(result["skipped"]))
    lines.append("- 绝对收益、样本事前选定、不给 p 值；参考类分布不是预测。")
    return lines


def _chart_inventory(report):
    charts = []
    if isinstance(report.get("chart"), dict):
        charts.append(report["chart"])
    charts.extend(item for item in report.get("charts", []) if isinstance(item, dict))
    if not charts:
        return []
    titles = "、".join(_escape(_clip(chart.get("title", ""), 60)) for chart in charts[:4])
    if len(charts) > 4:
        titles += "等 %d 张" % len(charts)
    return ["- 图表 %d 张：%s（完整报告或 HTML 版可查看）" % (len(charts), titles)]


def _figure(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return "—"
    try:
        return "{:,.0f}".format(value) if abs(value) >= 1000 else "{:.4g}".format(value)
    except (OverflowError, ValueError):
        return "—"


def _projection(report):
    """Multi-year paths copied from frozen model outputs; no new numbers."""
    analysis = report.get("analysis") if isinstance(report, dict) else None
    models = analysis.get("models") if isinstance(analysis, dict) else None
    rows = []
    for model in models if isinstance(models, list) else []:
        if not isinstance(model, dict):
            continue
        outputs = (model.get("result") or {}).get("outputs") or {}
        projection = outputs.get("projection")
        if not isinstance(projection, list) or not projection:
            continue
        unit = ("%s %s" % (model.get("currency", ""), model.get("scale", ""))).strip()
        shown = [step for step in projection[:3] if isinstance(step, dict)]
        parts = ["%s %s/%s" % (_escape(str(step.get("label", ""))),
                               _figure((step.get("revenue") or {}).get("value")),
                               _figure((step.get("profit") or {}).get("value"))) for step in shown]
        suffix = "；等 %d 年" % len(projection) if len(projection) > 3 else ""
        label = str(model.get("id") or "模型")
        if model.get("scenario"):
            label += "（%s）" % model["scenario"]
        rows.append("- %s：%s%s（各年收入/营业利润，%s）" % (_escape(label), "；".join(parts), suffix, _escape(unit)))
    if not rows:
        return []
    return ["", "## 多年路径", ""] + rows + ["- 路径只复述冻结模型里的年度假设结果，不是预测；增长率与利润率的来历见完整报告。"]


def build_memo(report, ledger=None, max_findings=MAX_FINDINGS):
    """Return memo markdown derived only from frozen fields; no new numbers."""
    answer = report.get("answer") if isinstance(report.get("answer"), dict) else {}
    lines = ["# " + _escape(report.get("title", ""))]
    lines.append("")
    lines.append("%s ｜ 截点 %s ｜ %s ｜ %s" % (_escape(_clip(report.get("question", ""), 240)),
                                                _date(report.get("as_of")),
                                                _escape(report.get("type", "")),
                                                _escape(report.get("task", ""))))
    lines.extend(["", "## 判断", "", _escape(_clip(answer.get("text", ""), MAX_TEXT * 2))])
    findings = _findings(report, max_findings)
    if findings:
        lines.extend(["", "## 关键发现", ""] + ["%d. %s" % (index, row) for index, row in enumerate(findings, 1)])
    lines.extend(_projection(report))
    valuation = _valuation(report)
    if valuation:
        lines.extend(["", "## 方法区间（来自冻结模型输出）", "",
                      "| 方法 | 指标 | 低 | 中 | 高 | 单位 |", "| --- | --- | --- | --- | --- | --- |"] + valuation)
        lines.append("")
        lines.append("不跨方法加权、不给概率、不是目标价；反向DCF一行是价格隐含的预期。")
    lines.extend(_bottleneck(report))
    lines.extend(_quality_flags(report))
    lines.extend(_event_study(report))
    catalysts = _catalysts(report)
    if catalysts:
        lines.extend(["", "## 接下来看什么", ""] + catalysts)
    conditions = _conditions(report)
    if conditions:
        rows = conditions[:8]
        lines.extend(["", "## 什么会改变判断", ""] + rows)
        if len(conditions) > 8:
            lines.append("- 其余条件见完整报告")
    risks = _risks(report)
    if risks:
        lines.extend(["", "## 主要风险", ""] + risks[:6])
        if len(risks) > 6:
            lines.append("- 其余限制见完整报告")
    lines.extend(["", "## 溯源", ""])
    claims = ledger.get("claims") if isinstance(ledger, dict) else None
    lines.append("- 主张数：%s；完整证据与计算见 report.json / claims.json / sources.json。" % (
        len(claims) if isinstance(claims, list) else "未提供"))
    lines.extend(_chart_inventory(report))
    lines.append("- 一页纸只做裁剪，不新增证据，也不替代完整报告与档案哈希。")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument("--claims", type=Path)
    parser.add_argument("--sources", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--max-findings", type=int, default=MAX_FINDINGS)
    args = parser.parse_args()
    try:
        report = json.loads(args.report.read_text(encoding="utf-8"))
        ledger = json.loads(args.claims.read_text(encoding="utf-8")) if args.claims else None
        sources = json.loads(args.sources.read_text(encoding="utf-8")) if args.sources else None
    except (OSError, ValueError) as exc:
        print(json.dumps({"passed": False, "errors": [str(exc)]}, ensure_ascii=False))
        return 2
    from render_report import validate_report
    if not isinstance(ledger, dict):
        print(json.dumps({"passed": False, "errors": ["memo_pack requires --claims for validated output"]},
                         ensure_ascii=False))
        return 1
    errors = validate_report(report, ledger, sources)
    if errors:
        print(json.dumps({"passed": False, "errors": errors}, ensure_ascii=False, indent=2))
        return 1
    if args.max_findings < 1:
        print(json.dumps({"passed": False, "errors": ["--max-findings must be at least 1"]}, ensure_ascii=False))
        return 1
    memo = build_memo(report, ledger, args.max_findings)
    if args.out:
        args.out.write_text(memo, encoding="utf-8")
        print(json.dumps({"passed": True, "written": str(args.out), "chars": len(memo)}, ensure_ascii=False))
    else:
        print(memo)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
