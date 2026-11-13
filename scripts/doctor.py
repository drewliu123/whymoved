#!/usr/bin/env python3
"""Health check for a Touyan data root (Python 3.9+).

Run this after upgrading the plugin or moving the data directory: it loads every
archived run with the current validators, rebuilds the research-memory index,
audits catalyst dates and reports what is missing or unreadable. It never writes
into the data root and never fixes anything automatically.

    python3 "$TY_DIR/scripts/doctor.py" [--home PATH] [--as-of DATE]

Exit codes: 0 healthy (warnings allowed), 1 at least one archive failed to load,
2 the data root or its journal/runs directory is missing.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def _date(value):
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def run_checks(home, as_of=None):
    """Return (passed, summary, errors, warnings); never raises for bad archives."""
    root = Path(home).expanduser().resolve()
    summary = {"home": str(root), "runs": 0, "loaded": 0, "failed": 0,
               "skipped_manifest": 0, "entities": 0, "aliases": 0,
               "dated_catalysts": 0, "undated_catalysts": 0, "overdue": 0}
    errors, warnings = [], []
    runs_dir = root / "journal" / "runs"
    if not runs_dir.is_dir():
        return False, summary, ["no journal/runs directory under " + str(root)], warnings
    import research_run
    run_ids = sorted(path.name for path in runs_dir.iterdir()
                     if path.is_dir() and path.name.startswith("R"))
    summary["runs"] = len(run_ids)
    if not run_ids:
        warnings.append("journal/runs exists but contains no archived runs yet")
    origin = _date(as_of) if as_of else None
    catalogs = []
    for run_id in run_ids:
        try:
            loaded = research_run.load_run(run_id, root)
        except Exception as exc:  # noqa: BLE001 - report every unreadable archive
            errors.append(run_id + ": " + str(exc)[:240])
            continue
        summary["loaded"] += 1
        manifest = loaded.get("manifest") or {}
        if not manifest.get("run_id"):
            summary["skipped_manifest"] += 1
        report = loaded.get("report") or {}
        if origin is None:
            stamp = _date(report.get("as_of"))
            if stamp is not None and (origin is None or stamp > origin):
                origin = stamp
        catalogs.append((run_id, report))
    import research_memory
    try:
        index = research_memory.build_index(root)
        summary["entities"] = len(index["entities"])
        summary["aliases"] = len(index.get("alias_map") or {})
        warnings.extend(index.get("warnings") or [])
        if index.get("skipped"):
            warnings.append("memory index skipped %d archive(s)" % len(index["skipped"]))
    except FileNotFoundError:
        warnings.append("memory index unavailable: journal/runs missing")
    import catalyst_calendar as calendar_tool
    for run_id, report in catalogs:
        for entry in calendar_tool.extract_entries(report, run_id, run_id):
            due = _date(entry.get("due"))
            if due is None:
                summary["undated_catalysts"] += 1
            else:
                summary["dated_catalysts"] += 1
                if origin is not None and due < origin:
                    summary["overdue"] += 1
    if summary["undated_catalysts"]:
        warnings.append("%d catalyst entries have no due date; free-text windows are not parsed"
                        % summary["undated_catalysts"])
    if summary["overdue"]:
        warnings.append("%d dated catalysts are before the reference date; overdue means unchecked,"
                        " not untriggered" % summary["overdue"])
    return not errors, summary, errors, warnings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", type=Path)
    parser.add_argument("--as-of", dest="as_of")
    args = parser.parse_args()
    if args.as_of is not None and _date(args.as_of) is None:
        print(json.dumps({"passed": False, "errors": ["--as-of must be an ISO date"]}, ensure_ascii=False))
        return 1
    if args.home is not None:
        home = args.home
    else:
        from common import HOME as default_home
        home = default_home
    root = Path(home).expanduser().resolve()
    if not (root / "journal" / "runs").is_dir():
        print(json.dumps({"passed": False, "summary": {"home": str(root)},
                          "errors": ["no journal/runs directory under " + str(root)], "warnings": []},
                         ensure_ascii=False, indent=2))
        return 2
    passed, summary, errors, warnings = run_checks(home, args.as_of)
    payload = {"passed": passed, "summary": summary, "errors": errors, "warnings": warnings}
    print(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
