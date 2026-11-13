#!/usr/bin/env python3
"""Multi-run digest: recent judgments, changes and upcoming catalysts (Python 3.9+).

One run answers one question; a week of research needs a page that says what
changed, what is due and what was missed. This script reads the archived runs
through the research-memory index and the catalyst calendar and writes Markdown.

    python3 "$TY_DIR/scripts/digest.py" --home "$TY_HOME" --as-of 2026-11-14 --days 14

It copies judgments and trigger signals; it computes no new numbers and makes no
recommendations. A run without a dated catalyst contributes to the judgment
sections only.
"""

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


def _date(value):
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _clip(value, limit=180):
    text = " ".join(str(value).split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def build_digest(home, as_of=None, days=30):
    """Return Markdown digest text; raises ValueError for unusable input."""
    import calendar as calendar_tool
    import research_memory
    origin = _date(as_of) if as_of else datetime.now(timezone.utc)
    if origin is None:
        raise ValueError("--as-of must be an ISO date")
    if days < 1:
        raise ValueError("--days must be at least 1")
    window_start = origin - timedelta(days=days)
    index = research_memory.build_index(home)
    recent = []
    for record in index["runs"]:
        stamp = _date(record.get("as_of"))
        if stamp is not None and window_start <= stamp <= origin:
            recent.append(record)
    recent.sort(key=lambda item: (_date(item.get("as_of")) or datetime.min.replace(tzinfo=timezone.utc)),
                reverse=True)
    lines = ["# 研究摘要（%s 起 %d 天）" % (origin.date().isoformat(), days), ""]
    lines.append("归档 %d 轮；本窗口 %d 轮；实体 %d 个；跳过 %d 个坏档。" % (
        len(index["runs"]), len(recent), len(index["entities"]), len(index["skipped"])))
    changed = [record for record in recent if record.get("judgment_changed") is True]
    lines.extend(["", "## 判断变化", ""])
    if changed:
        for record in changed:
            lines.append("- %s ｜ %s ｜ %s" % (record.get("as_of", ""), record.get("run_id", ""),
                                               _clip(record.get("title", ""))))
            lines.append("  - 判断：%s" % _clip(record.get("judgment", ""), 220))
    else:
        lines.append("- 本窗口没有声明改变判断的更新。")
    lines.extend(["", "## 本窗口研究", ""])
    if recent:
        for record in recent:
            lines.append("- %s ｜ %s ｜ %s ｜ %s" % (
                record.get("as_of", ""), record.get("run_id", ""), _clip(record.get("entity", ""), 60),
                _clip(record.get("title", ""))))
            lines.append("  - 判断：%s" % _clip(record.get("judgment", "")))
    else:
        lines.append("- 本窗口没有新归档。")
    entries = []
    for record in index["runs"]:
        report = None
        try:
            report = json.loads((Path(home).resolve() / "journal" / "runs" / record["run_id"] / "report.json")
                                .read_text(encoding="utf-8"))
        except (OSError, ValueError):
            report = None
        if isinstance(report, dict):
            for entry in calendar_tool.extract_entries(report, record["run_id"], record["run_id"]):
                entries.append(entry)
    for entry in entries:
        due = _date(entry.get("due"))
        entry["days"] = None if due is None else round((due - origin).total_seconds() / 86400, 3)
    upcoming = sorted((entry for entry in entries if entry["days"] is not None and 0 <= entry["days"] <= 30),
                      key=lambda item: (item["days"], item["run_id"] or "", item["id"]))
    overdue = sorted((entry for entry in entries if entry["days"] is not None and entry["days"] < 0),
                     key=lambda item: item["days"])
    lines.extend(["", "## 未来 30 天的催化", ""])
    if upcoming:
        for entry in upcoming:
            lines.append("- %s（%+.1f 天）｜%s ｜ %s" % (entry.get("due", ""), entry["days"],
                                                       entry.get("type") or "未分类",
                                                       _clip(entry.get("signal", ""))))
    else:
        lines.append("- 归档里没有带日期且落在未来 30 天的催化（没有 due 的观察项不算）。")
    lines.extend(["", "## 过期未核对", ""])
    if overdue:
        for entry in overdue[:20]:
            lines.append("- %s（%.1f 天前）｜%s ｜ %s" % (entry.get("due", ""), -entry["days"],
                                                       entry.get("run_id") or "", _clip(entry.get("signal", ""))))
        if len(overdue) > 20:
            lines.append("- 其余 %d 条见 calendar.py" % (len(overdue) - 20))
        lines.append("- 过期不等于未触发：只表示没有记录核对结果。")
    else:
        lines.append("- 没有过期未核对的催化。")
    lines.extend(["", "## 边界", "",
                  "- 摘要只复制已冻结报告里的判断与触发，不新增证据，也不给买卖建议。",
                  "- 没有 `due` 的观察项不进催化小节；不要从自由文本猜日期。",
                  "- 判断是否改变以各 run 自己的 `update.judgment_changed` 为准。"])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", type=Path, required=True)
    parser.add_argument("--as-of", dest="as_of")
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    try:
        text = build_digest(args.home, args.as_of, args.days)
    except FileNotFoundError as exc:
        print(json.dumps({"passed": False, "errors": [str(exc)]}, ensure_ascii=False))
        return 2
    except ValueError as exc:
        print(json.dumps({"passed": False, "errors": [str(exc)]}, ensure_ascii=False))
        return 1
    if args.out:
        args.out.write_text(text, encoding="utf-8")
        print(json.dumps({"passed": True, "written": str(args.out), "chars": len(text)}, ensure_ascii=False))
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
