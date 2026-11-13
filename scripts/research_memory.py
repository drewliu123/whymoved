#!/usr/bin/env python3
"""Cross-run research memory: what did we judge before, on which evidence (Python 3.9+).

Every archive under journal/runs/ is already immutable and hash-verified. What
was missing is a way to ask "what did we say about this entity, when, and with
which claims and models" without opening runs one by one.

This module builds a derived, rebuildable index of *pointers*: run id, as-of,
title, question, entity, judgment text, claim count, metric names, model kinds,
opportunity status, trigger ids and the report hash. It never merges numbers,
never creates claims, never rewrites archives, and never turns an old inference
into new evidence. The index is a cache; the frozen run remains the record.

    research_memory.py index --home DIR [--out PATH]
    research_memory.py query --home DIR TERM [--as-of DATE] [--limit N]
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = 1


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


def _hash(payload):
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _unique(values):
    seen, out = set(), []
    for value in values:
        if not _text(value):
            continue
        key = value.strip().casefold()
        if key in seen:
            continue
        seen.add(key)
        out.append(value.strip())
    return out


def run_record(run_dir):
    """Return (record, None) for one archive, or (None, reason) when it cannot be read."""
    report_path = run_dir / "report.json"
    if not report_path.is_file():
        return None, "missing report.json"
    try:
        report = _read_json(report_path)
    except (OSError, ValueError) as exc:
        return None, "invalid report.json: " + str(exc)
    if not isinstance(report, dict):
        return None, "report.json is not an object"
    plan = {}
    if (run_dir / "plan.json").is_file():
        try:
            loaded = _read_json(run_dir / "plan.json")
            plan = loaded if isinstance(loaded, dict) else {}
        except (OSError, ValueError):
            plan = {}
    claims = []
    if (run_dir / "claims.json").is_file():
        try:
            loaded = _read_json(run_dir / "claims.json")
            claims = loaded.get("claims") if isinstance(loaded, dict) else []
        except (OSError, ValueError):
            claims = []
    claims = claims if isinstance(claims, list) else []
    manifest = {}
    if (run_dir / "manifest.json").is_file():
        try:
            loaded = _read_json(run_dir / "manifest.json")
            manifest = loaded if isinstance(loaded, dict) else {}
        except (OSError, ValueError):
            manifest = {}
    analysis = report.get("analysis") if isinstance(report.get("analysis"), dict) else {}
    models = analysis.get("models") if isinstance(analysis.get("models"), list) else []
    opportunity = report.get("opportunity") if isinstance(report.get("opportunity"), dict) else {}
    assessment = opportunity.get("assessment") if isinstance(opportunity.get("assessment"), dict) else {}
    triggers = opportunity.get("triggers") if isinstance(opportunity.get("triggers"), list) else []
    update = report.get("update") if isinstance(report.get("update"), dict) else {}
    metric_names, metric_entities = [], []
    for claim in claims:
        if not isinstance(claim, dict):
            continue
        metric = claim.get("metric")
        if not isinstance(metric, dict):
            continue
        if _text(metric.get("name")):
            metric_names.append(metric["name"])
        if _text(metric.get("entity")):
            metric_entities.append(metric["entity"])
    entity = plan.get("entity") if _text(plan.get("entity")) else ""
    entities = _unique([entity] + metric_entities)
    answer = report.get("answer") if isinstance(report.get("answer"), dict) else {}
    record = {
        "run_id": manifest.get("run_id") if _text(manifest.get("run_id")) else run_dir.name,
        "as_of": report.get("as_of") if _text(report.get("as_of")) else manifest.get("as_of", ""),
        "title": report.get("title", ""),
        "question": report.get("question", ""),
        "task": report.get("task", ""),
        "type": report.get("type", ""),
        "entity": entity,
        "entities": entities,
        "judgment": answer.get("text", ""),
        "opportunity_status": assessment.get("status", ""),
        "parent_run": manifest.get("parent_run") or "",
        "judgment_changed": update.get("judgment_changed") if isinstance(update.get("judgment_changed"), bool) else None,
        "claim_count": len([claim for claim in claims if isinstance(claim, dict)]),
        "metric_names": _unique(metric_names),
        "model_kinds": _unique([model.get("spec", {}).get("kind") for model in models
                                if isinstance(model, dict) and isinstance(model.get("spec"), dict)]),
        "triggers": [{"id": trigger.get("id", ""), "due": trigger.get("due", "")}
                     for trigger in triggers if isinstance(trigger, dict)],
        "finding_titles": [item.get("title", "") for item in report.get("findings", [])
                           if isinstance(item, dict) and _text(item.get("title"))],
        "report_sha256": hashlib.sha256(report_path.read_bytes()).hexdigest(),
        "search": " ".join(_text(value) and value.strip().casefold() or "" for value in (
            report.get("title", ""), report.get("question", ""), report.get("task", ""),
            report.get("type", ""), entity, " ".join(entities), " ".join(metric_names),
            " ".join(item.get("title", "") for item in report.get("findings", []) if isinstance(item, dict)),
            answer.get("text", ""))),
    }
    return record, None


def load_aliases(home):
    """Read journal/aliases.json: {canonical: [alias, ...]} -> (normalized map, warnings)."""
    path = Path(home).resolve() / "journal" / "aliases.json"
    if not path.is_file():
        return {}, []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {}, ["aliases.json cannot be read and was ignored: " + str(exc)]
    if not isinstance(data, dict):
        return {}, ["aliases.json must be an object mapping canonical names to alias lists"]
    mapping, warnings = {}, []

    def register(key, target):
        if key in mapping and mapping[key] != target:
            warnings.append("alias %r maps to both %r and %r; keeping the first" % (key, mapping[key], target))
            return
        mapping[key] = target

    for canonical in sorted(data):
        aliases = data[canonical]
        if not _text(canonical):
            continue
        name = canonical.strip()
        register(name.casefold(), name)
        if not isinstance(aliases, list):
            warnings.append("aliases for %r must be a list and were ignored" % name)
            continue
        for alias in aliases:
            if _text(alias):
                register(alias.strip().casefold(), name)
    return mapping, warnings


def build_index(home):
    """Rebuild the pointer index from journal/runs; deterministic and side-effect free."""
    runs_dir = Path(home).resolve() / "journal" / "runs"
    if not runs_dir.is_dir():
        raise FileNotFoundError("no journal/runs directory under " + str(Path(home).resolve()))
    runs, skipped = [], []
    for run_dir in sorted(path for path in runs_dir.iterdir() if path.is_dir()):
        record, reason = run_record(run_dir)
        if record is None:
            skipped.append({"run": run_dir.name, "reason": reason})
            continue
        runs.append(record)
    runs.sort(key=lambda item: (item["run_id"],))
    aliases, warnings = load_aliases(home)
    entities = {}
    for record in runs:
        for entity in record["entities"]:
            canonical = aliases.get(entity.strip().casefold(), entity)
            entities.setdefault(canonical, []).append(record["run_id"])
    for key in entities:
        entities[key].sort()
    payload = {"schema_version": SCHEMA_VERSION, "runs": runs,
               "entities": dict(sorted(entities.items())), "skipped": skipped,
               "alias_map": dict(sorted(aliases.items())), "warnings": warnings}
    payload["index_hash"] = _hash(payload)
    return payload


def query_index(index, term, as_of=None, limit=None):
    """Filter runs by a case-insensitive term with an optional point-in-time view."""
    needle = term.strip().casefold()
    if not needle:
        raise ValueError("query term must be nonempty")
    cutoff = _date(as_of) if as_of else None
    if as_of and cutoff is None:
        raise ValueError("--as-of must be an ISO date")
    aliases = index.get("alias_map") or {}
    canonical = aliases.get(needle)
    matches = []
    for record in index.get("runs", []):
        hits_text = needle in record.get("search", "")
        hits_alias = bool(canonical) and any(
            aliases.get(str(entity).strip().casefold()) == canonical
            for entity in record.get("entities", []))
        if not hits_text and not hits_alias:
            continue
        stamp = _date(record.get("as_of"))
        if cutoff is not None and (stamp is None or stamp > cutoff):
            continue
        matches.append(record)
    matches.sort(key=lambda item: (_date(item.get("as_of")) or datetime.min.replace(tzinfo=timezone.utc),
                                   item.get("run_id", "")), reverse=True)
    if limit is not None:
        matches = matches[:limit]
    return {"term": term, "as_of": as_of, "count": len(matches),
            "matches": [{"run_id": item["run_id"], "as_of": item.get("as_of", ""),
                         "title": item.get("title", ""), "question": item.get("question", ""),
                         "entity": item.get("entity", ""), "entities": item.get("entities", []),
                         "judgment": item.get("judgment", ""),
                         "opportunity_status": item.get("opportunity_status", ""),
                         "parent_run": item.get("parent_run", ""),
                         "judgment_changed": item.get("judgment_changed"),
                         "claim_count": item.get("claim_count", 0),
                         "metric_names": item.get("metric_names", []),
                         "model_kinds": item.get("model_kinds", []),
                         "triggers": item.get("triggers", []),
                         "report_sha256": item.get("report_sha256", "")} for item in matches],
            "notes": ["索引只保存指针；判断与证据以冻结报告为准，旧 inference 不能直接支撑新结论。",
                      "judgment_changed 取自该 run 的 update 记录，None 表示没有更新关系。"]}


def lineage(index, run_id):
    """Walk parent_run links for one run: ancestors ordered, plus direct children."""
    runs = {record["run_id"]: record for record in index.get("runs", [])}
    if run_id not in runs:
        raise ValueError("unknown run id: " + str(run_id))
    chain, seen = [], set()
    current = run_id
    while current and current not in seen:
        seen.add(current)
        record = runs.get(current)
        if record is None:
            break
        chain.append(record)
        current = record.get("parent_run") or ""
    chain.reverse()
    children = sorted(record["run_id"] for record in index.get("runs", [])
                      if record.get("parent_run") == run_id)
    rows = []
    for position, record in enumerate(chain):
        rows.append({"run_id": record["run_id"], "as_of": record.get("as_of", ""),
                     "title": record.get("title", ""), "question": record.get("question", ""),
                     "entity": record.get("entity", ""), "judgment": record.get("judgment", ""),
                     "judgment_changed": record.get("judgment_changed"),
                     "opportunity_status": record.get("opportunity_status", ""),
                     "model_kinds": record.get("model_kinds", []),
                     "parent_run": record.get("parent_run", ""),
                     "depth": position})
    return {"run_id": run_id, "entity": rows[-1].get("entity", ""), "length": len(rows),
            "lineage": rows, "children": children,
            "notes": ["lineage按parent_run回溯到最早一轮，顺序为旧→新。",
                      "judgment_changed取自每轮自己的update记录；None表示该轮未声明更新关系。",
                      "children只列直接子run；分支更新的完整家族需逐个run查看。"]}


def _write_index(index, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(index, ensure_ascii=False, indent=2, sort_keys=False, allow_nan=False) + "\n"
    path.write_text(text, encoding="utf-8")
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    index_parser = sub.add_parser("index")
    index_parser.add_argument("--home", type=Path, required=True)
    index_parser.add_argument("--out", type=Path)
    query_parser = sub.add_parser("query")
    query_parser.add_argument("--home", type=Path, required=True)
    query_parser.add_argument("term")
    query_parser.add_argument("--as-of", dest="as_of")
    query_parser.add_argument("--limit", type=int)
    thread_parser = sub.add_parser("thread")
    thread_parser.add_argument("--home", type=Path, required=True)
    thread_parser.add_argument("run_id")
    args = parser.parse_args()
    try:
        index = build_index(args.home)
    except FileNotFoundError as exc:
        print(json.dumps({"passed": False, "errors": [str(exc)]}, ensure_ascii=False))
        return 2
    except OSError as exc:
        print(json.dumps({"passed": False, "errors": [str(exc)]}, ensure_ascii=False))
        return 2
    if args.cmd == "thread":
        try:
            result = lineage(index, args.run_id)
        except ValueError as exc:
            print(json.dumps({"passed": False, "errors": [str(exc)]}, ensure_ascii=False))
            return 1
        result["passed"] = True
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    if args.cmd == "index":
        target = args.out or (Path(args.home).resolve() / "journal" / "index.json")
        try:
            written = _write_index(index, target)
        except OSError as exc:
            print(json.dumps({"passed": False, "errors": [str(exc)]}, ensure_ascii=False))
            return 2
        print(json.dumps({"passed": True, "runs": len(index["runs"]), "skipped": index["skipped"],
                          "written": str(written), "index_hash": index["index_hash"]},
                         ensure_ascii=False, indent=2))
        return 0
    try:
        result = query_index(index, args.term, args.as_of, args.limit)
    except ValueError as exc:
        print(json.dumps({"passed": False, "errors": [str(exc)]}, ensure_ascii=False))
        return 1
    result["passed"] = True
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
