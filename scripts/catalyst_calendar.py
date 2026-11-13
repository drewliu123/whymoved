#!/usr/bin/env python3
"""Dated catalysts from frozen reports (Python 3.9+).

The plugin already has trigger ids inside `opportunity.triggers` and a free-text
`watch` list. This module adds the missing piece: an optional ISO `due` date and
a `type` on those existing entries, plus a read-only calendar view across
archived runs. It deliberately does not introduce a second trigger namespace:
ids stay where they already are, and nothing here writes state or monitors
anything in the background.

Fields added (all optional, so old reports stay valid):

    opportunity.triggers[].due    ISO date/datetime
    opportunity.triggers[].type   earnings | macro | regulatory | company | industry
    watch[].due                   ISO date/datetime (watch has no id; the calendar
    watch[].type                  labels rows as W1, W2, ... by position)

A dated entry means "this is when the observation should be checkable". It is
not a promise that anyone will check it, and an entry whose date has passed is
reported as overdue rather than silently dropped.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

CATALYST_TYPES = ("earnings", "macro", "regulatory", "company", "industry")


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _date(value):
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def validate_report_catalysts(report):
    """Validate optional due/type additions; existing free-text fields stay as they are."""
    errors = []
    as_of = _date(report.get("as_of"))
    for path, entries in (("watch", report.get("watch")),):
        if entries is None:
            continue
        if not isinstance(entries, list):
            continue
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict):
                continue
            errors.extend(_validate_entry(entry, "%s[%d]" % (path, index), as_of))
    opportunity = report.get("opportunity")
    triggers = opportunity.get("triggers") if isinstance(opportunity, dict) else None
    if isinstance(triggers, list):
        for index, trigger in enumerate(triggers):
            if not isinstance(trigger, dict):
                continue
            errors.extend(_validate_entry(trigger, "opportunity.triggers[%d]" % index, as_of))
    return errors


def _validate_entry(entry, path, as_of):
    errors = []
    if "type" in entry and (not isinstance(entry["type"], str) or entry["type"] not in CATALYST_TYPES):
        errors.append(path + ".type must be one of " + ", ".join(CATALYST_TYPES))
    if "due" not in entry:
        return errors
    due = _date(entry["due"])
    if due is None:
        errors.append(path + ".due must be an ISO date/datetime")
    elif as_of is not None and due < as_of:
        errors.append(path + ".due is before report.as_of; a dated catalyst must be checkable later")
    return errors


def _entry_from(entry, source, run_id, kind, identifier, claims_required):
    signal = entry.get("signal") or entry.get("meaning") or entry.get("by") or ""
    due = entry.get("due")
    return {
        "source": source,
        "run_id": run_id,
        "kind": kind,
        "id": identifier,
        "due": due if isinstance(due, str) else None,
        "type": entry.get("type") if isinstance(entry.get("type"), str) else None,
        "signal": signal,
        "claim_ids": [cid for cid in entry.get("claim_ids", []) if isinstance(cid, str)]
        if isinstance(entry.get("claim_ids"), list) else [],
    }


def extract_entries(report, source="<report>", run_id=None):
    """Return dated and undated catalyst rows for one frozen report."""
    rows = []
    opportunity = report.get("opportunity")
    triggers = opportunity.get("triggers") if isinstance(opportunity, dict) else None
    if isinstance(triggers, list):
        for trigger in triggers:
            if not isinstance(trigger, dict):
                continue
            identifier = trigger.get("id") if _text(trigger.get("id")) else "T?"
            rows.append(_entry_from(trigger, source, run_id, "trigger", identifier, True))
    watch = report.get("watch")
    if isinstance(watch, list):
        for index, entry in enumerate(watch):
            if not isinstance(entry, dict):
                continue
            rows.append(_entry_from(entry, source, run_id, "watch", "W%d" % (index + 1), False))
    return rows


def build_calendar(documents, as_of=None, horizon_days=None):
    """Split entries into upcoming, overdue and undated relative to as_of."""
    entries = []
    for source, run_id, report in documents:
        entries.extend(extract_entries(report, source, run_id))
    for entry in entries:
        due = _date(entry["due"]) if entry["due"] else None
        if due is None:
            entry["days_from_as_of"] = None
            entry["state"] = "undated"
            continue
        entry["days_from_as_of"] = None if as_of is None else round((due - as_of).total_seconds() / 86400, 3)
        entry["state"] = "undated" if as_of is None else ("overdue" if due < as_of else "upcoming")
    upcoming = [entry for entry in entries if entry["state"] == "upcoming"]
    if horizon_days is not None:
        upcoming = [entry for entry in upcoming if entry["days_from_as_of"] <= horizon_days]
    upcoming.sort(key=lambda entry: (_date(entry["due"]), entry["run_id"] or "", entry["id"]))
    overdue = [entry for entry in entries if entry["state"] == "overdue"]
    overdue.sort(key=lambda entry: _date(entry["due"]))
    undated = [entry for entry in entries if entry["state"] == "undated"]
    return {"as_of": None if as_of is None else as_of.isoformat(),
            "horizon_days": horizon_days, "upcoming": upcoming, "overdue": overdue, "undated": undated,
            "notes": ["日期只表示观察可核对的时间，不代表已监控或有自动提醒。",
                      "overdue 是已过观察时点但报告未记录核对状态的行，不等于未触发。",
                      "未填due的条目列在undated，不从free-text的by里猜日期。"]}


def _document_reports(paths, home):
    """Return (source, run_id, report) triples from files, run dirs or a research home."""
    documents = []
    if home is not None:
        runs = Path(home).resolve() / "journal" / "runs"
        if runs.is_dir():
            for run in sorted(p for p in runs.iterdir() if p.is_dir()):
                report = run / "report.json"
                if not report.is_file():
                    continue
                manifest = run / "manifest.json"
                run_id = run.name
                if manifest.is_file():
                    try:
                        run_id = json.loads(manifest.read_text(encoding="utf-8")).get("run_id", run_id)
                    except ValueError:
                        pass
                documents.append((str(report), run_id, json.loads(report.read_text(encoding="utf-8"))))
    for path in paths:
        path = Path(path)
        run_dir = path if path.is_dir() else path.parent
        if path.is_dir():
            path = path / "report.json"
        run_id = None
        manifest = run_dir / "manifest.json"
        if manifest.is_file():
            try:
                run_id = json.loads(manifest.read_text(encoding="utf-8")).get("run_id")
            except ValueError:
                run_id = None
        documents.append((str(path), run_id, json.loads(path.resolve().read_text(encoding="utf-8"))))
    return documents


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reports", nargs="*", type=Path, help="frozen report.json files or run directories")
    parser.add_argument("--home", type=Path, help="research home to scan journal/runs/*/report.json")
    parser.add_argument("--as-of", dest="as_of", help="ISO date used as the calendar origin (default: latest report as_of)")
    parser.add_argument("--due", type=int, metavar="DAYS", help="only show entries due within DAYS of as_of")
    args = parser.parse_args()
    if not args.reports and args.home is None:
        parser.error("provide at least one report or --home")
    try:
        documents = _document_reports(args.reports, args.home)
    except OSError as exc:
        print(json.dumps({"passed": False, "errors": [str(exc)]}, ensure_ascii=False))
        return 2
    except ValueError as exc:
        print(json.dumps({"passed": False, "errors": ["invalid report JSON: " + str(exc)]}, ensure_ascii=False))
        return 1
    errors = []
    for source, _, report in documents:
        if not isinstance(report, dict):
            errors.append(source + ": report must be an object")
            continue
        errors.extend(source + ": " + error for error in validate_report_catalysts(report))
    if errors:
        print(json.dumps({"passed": False, "errors": errors}, ensure_ascii=False, indent=2))
        return 1
    as_of = _date(args.as_of) if args.as_of else None
    if args.as_of and as_of is None:
        print(json.dumps({"passed": False, "errors": ["--as-of must be an ISO date"]}, ensure_ascii=False))
        return 1
    if as_of is None:
        stamps = [(_date(report.get("as_of")), report.get("as_of")) for _, _, report in documents]
        usable = [stamp for stamp in stamps if stamp[0] is not None]
        if usable:
            latest = max(usable, key=lambda stamp: stamp[0])
            as_of, as_of_text = latest[0], latest[1]
        else:
            as_of_text = None
    else:
        as_of_text = args.as_of
    calendar = build_calendar(documents, as_of, args.due)
    calendar["as_of_text"] = as_of_text
    calendar["passed"] = True
    print(json.dumps(calendar, ensure_ascii=False, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
