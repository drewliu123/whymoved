#!/usr/bin/env python3
"""Immutable local research runs, independent of the forecast/legacy journal API.

  research_run.py archive --report report.json --claims claims.json --sources sources.json --plan plan.json [--calculations calculations.json] [--audit audit.json] [--parent-run R...]
  research_run.py update --parent-run R... <same input flags>
  research_run.py diff R... --report report.json --claims claims.json --sources sources.json
  research_run.py show R...
  research_run.py list

Public API: archive_run(report_path, claims_path, sources_path, plan_path,
calculations_path=None, parent_run=None, home=None, run_id=None, audit_path=None) -> dict;
load_run(run_id, home=None) -> dict; list_runs(home=None) -> list[dict];
compare_run(parent, report, ledger, sources) -> dict (structural comparison only).
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

from render_report import read_document, render_html, render_markdown, validate_calculation_rows, validate_report

RUN_ID = re.compile(r"^R\d{8}T\d{6}Z-[a-f0-9]{12}$")
FILES = {"report.json", "claims.json", "sources.json", "plan.json", "calculations.json", "audit.json", "report.md", "report.html", "diff.json"}


def _json(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")


def _hash(data):
    return hashlib.sha256(data).hexdigest()


def _root(home=None, create=False):
    root = Path(home if home is not None else os.environ.get("TOUYAN_HOME", Path.home() / "Desktop" / "投研助手")).expanduser().absolute()
    root = root / "journal" / "runs"
    if ".." in root.parts or any(p.is_symlink() for p in [root] + list(root.parents)):
        raise ValueError("unsafe research runs directory")
    if create:
        root.mkdir(parents=True, exist_ok=True)
    return root


def _valid_id(value):
    if not isinstance(value, str) or not RUN_ID.fullmatch(value):
        raise ValueError("invalid run_id")
    return value


def _validate_bundle(report, ledger, sources, plan, calculations=None):
    errors = validate_report(report, ledger, sources)
    if not isinstance(plan, dict) or not plan:
        errors.append("plan must be a nonempty object")
    if isinstance(plan, dict):
        # Missing shared validation fails closed.
        try:
            from research_plan import validate_plan
        except ImportError:
            errors.append("research_plan.validate_plan unavailable")
        else:
            errors.extend("plan: " + str(e) for e in validate_plan(plan))
        if plan.get("historical") != sources.get("historical"):
            errors.append("plan.historical differs from sources")
        for field in ("question", "type", "task", "as_of"):
            if field in plan and plan[field] != report.get(field):
                errors.append("plan." + field + " differs from report")
    if calculations is not None:
        if not isinstance(calculations, dict) or calculations.get("schema_version") != 2 or calculations.get("as_of") != report.get("as_of"):
            errors.append("calculations document requires schema_version 2 and matching as_of")
        else:
            errors.extend(validate_calculation_rows(calculations.get("calculations"), {c["id"] for c in ledger.get("claims", []) if isinstance(c, dict) and isinstance(c.get("id"), str)}))
            if calculations.get("calculations") != report.get("calculations", []):
                errors.append("archived calculations must equal frozen report.calculations")
    if errors:
        raise ValueError("\n".join(errors))


def _changes(old, new):
    a = {item["id"]: item for item in old}
    b = {item["id"]: item for item in new}
    return {"added": sorted(b.keys() - a.keys()), "removed": sorted(a.keys() - b.keys()),
            "changed": sorted(k for k in a.keys() & b.keys() if a[k] != b[k])}


def _metadata_differences(old, new, path=""):
    """Only compare supplied period/unit/scope fields. No prose inference."""
    differences = []
    if isinstance(old, dict) and isinstance(new, dict):
        for key in sorted(old.keys() | new.keys()):
            location = (path + "." if path else "") + key
            if key in {"period", "unit", "scope"} and old.get(key) != new.get(key):
                differences.append({"path": location, "before": old.get(key), "after": new.get(key)})
            elif key in old and key in new:
                differences.extend(_metadata_differences(old[key], new[key], location))
    elif isinstance(old, list) and isinstance(new, list):
        if all(isinstance(x, dict) and isinstance(x.get("id"), str) for x in old + new):
            a, b = {x["id"]: x for x in old}, {x["id"]: x for x in new}
            for key in sorted(a.keys() & b.keys()):
                differences.extend(_metadata_differences(a[key], b[key], path + "[" + key + "]"))
        else:
            for i, (left, right) in enumerate(zip(old, new)):
                differences.extend(_metadata_differences(left, right, path + "[%d]" % i))
    return differences


def compare_run(parent, report, ledger, sources, plan=None):
    """Compare IDs/structured fields; the author supplies judgment and comparability."""
    errors = validate_report(report, ledger, sources)
    if errors:
        raise ValueError("\n".join(errors))
    update = report.get("update")
    if update is None:
        raise ValueError("comparison requires explicit report.update judgment and comparability explanation")
    old_sources = parent["sources"]["candidates"]
    # Evidence identity is the source ID. Evidence text/access/locator changes are
    # separated from candidate ranking changes so neither is mistaken for truth.
    evidence_fields = ("id", "url", "canonical_url", "tier", "publisher", "quote", "locator", "origin_id", "origin_basis", "supports", "evidence_kind", "access_status", "published_at", "market_quote", "survey", "availability", "attribution")
    def evidence(items):
        return [{key: item.get(key) for key in evidence_fields} for item in items]
    comparison = {"schema_version": 2, "parent_run": parent["manifest"]["run_id"],
                  "method": "structural_ids_and_fields", "judgment": update,
                  "sources": _changes(old_sources, sources["candidates"]),
                  "evidence": _changes(evidence(old_sources), evidence(sources["candidates"])),
                  "claims": _changes(parent["claims"]["claims"], ledger["claims"]),
                  "comparability_issues": []}
    for key, old, new in (("report", parent["report"], report), ("claims", parent["claims"], ledger), ("sources", parent["sources"], sources)):
        comparison["comparability_issues"].extend(_metadata_differences(old, new, key))
    if plan is not None:
        comparison["comparability_issues"].extend(_metadata_differences(parent["plan"], plan, "plan"))
    if comparison["comparability_issues"] and update["comparability"]["status"] == "comparable":
        raise ValueError("structured period/unit/scope differs; author must declare mixed or not_comparable")
    return comparison


def load_run(run_id, home=None):
    """Verify every immutable manifest file before loading a run."""
    run_id = _valid_id(run_id)
    directory = _root(home) / run_id
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("run not found or unsafe: " + run_id)
    manifest = read_document(directory / "manifest.json")
    if not isinstance(manifest, dict) or manifest.get("schema_version") != 2 or manifest.get("run_id") != run_id:
        raise ValueError("invalid run manifest")
    hashes = manifest.get("files")
    required = {"report.json", "claims.json", "sources.json", "plan.json", "report.md", "report.html"}
    if not isinstance(hashes, dict) or not required.issubset(hashes) or not set(hashes).issubset(FILES):
        raise ValueError("invalid manifest file inventory")
    if {p.name for p in directory.iterdir()} != set(hashes) | {"manifest.json"}:
        raise ValueError("run file inventory changed")
    for name, digest in hashes.items():
        path = directory / name
        if path.is_symlink() or not path.is_file() or not isinstance(digest, str) or _hash(path.read_bytes()) != digest:
            raise ValueError("run hash mismatch or unsafe file: " + name)
    result = {"manifest": manifest, "path": str(directory)}
    for name in ("report", "claims", "sources", "plan", "calculations", "audit", "diff"):
        if name + ".json" in hashes:
            result[name] = read_document(directory / (name + ".json"))
    # Always revalidate saved inputs. A hash is integrity evidence, not semantic validation.
    _validate_bundle(result["report"], result["claims"], result["sources"], result["plan"], result.get("calculations"))
    parent_id = manifest.get("parent_run")
    if parent_id:
        _valid_id(parent_id)
        parent_path = _root(home) / parent_id / "manifest.json"
        parent_manifest = read_document(parent_path)
        if _hash(parent_path.read_bytes()) != manifest.get("parent_manifest_sha256"):
            raise ValueError("parent manifest changed")
        if not isinstance(parent_manifest, dict) or parent_manifest.get("run_id") != parent_id:
            raise ValueError("invalid parent manifest")
        for name, digest in parent_manifest.get("files", {}).items():
            if name not in FILES:
                raise ValueError("unsafe parent manifest path")
            path = parent_path.parent / name
            if path.is_symlink() or not path.is_file() or _hash(path.read_bytes()) != digest:
                raise ValueError("parent file changed: " + name)
    return result


def list_runs(home=None):
    root = _root(home)
    if not root.exists():
        return []
    rows = []
    for directory in sorted(root.iterdir()):
        if directory.name.startswith(".stage-"):
            continue
        if directory.name.startswith(".reserve-") and RUN_ID.fullmatch(directory.name[len(".reserve-"):]) and directory.is_file() and not directory.is_symlink():
            continue
        if not RUN_ID.fullmatch(directory.name):
            raise ValueError("unexpected entry in runs: " + directory.name)
        run = load_run(directory.name, home)
        rows.append({"run_id": directory.name, "title": run["report"]["title"], "as_of": run["report"]["as_of"],
                     "created_at": run["manifest"]["created_at"], "parent_run": run["manifest"].get("parent_run")})
    return rows


def archive_run(report_path, claims_path, sources_path, plan_path, calculations_path=None, parent_run=None, home=None, run_id=None, audit_path=None):
    """Validate and atomically publish once; audit is metadata, never trusted evidence."""
    paths = [Path(p).expanduser().absolute() for p in (report_path, claims_path, sources_path, plan_path)]
    for optional in (calculations_path, audit_path):
        if optional is not None:
            paths.append(Path(optional).expanduser().absolute())
    if len({str(p) for p in paths}) != len(paths):
        raise ValueError("duplicate input paths")
    documents = [read_document(p) for p in paths]
    report, ledger, sources, plan = documents[:4]
    if not isinstance(ledger, dict) or type(ledger.get("schema_version")) is not int or ledger["schema_version"] != 2:
        raise ValueError("new archives require claims schema_version 2")
    calculations = documents[4] if calculations_path is not None else None
    audit = documents[4 + int(calculations_path is not None)] if audit_path is not None else None
    if audit_path is not None and not isinstance(audit, dict):
        raise ValueError("audit must be a JSON object; its contents are untrusted metadata")
    _validate_bundle(report, ledger, sources, plan, calculations)
    comparison = None
    parent = None
    if parent_run:
        parent = load_run(parent_run, home)
        if plan.get("parent_run_id") is not None and plan["parent_run_id"] != parent_run:
            raise ValueError("plan.parent_run_id differs from --parent-run")
        comparison = compare_run(parent, report, ledger, sources, plan)
    elif report.get("update") is not None or plan.get("parent_run_id") is not None:
        raise ValueError("report.update/plan.parent_run_id requires --parent-run")
    # Render before any directory mutation.
    markdown = render_markdown(report, ledger, sources)
    page = render_html(report, ledger, sources)
    timestamp = datetime.now(timezone.utc)
    run_id = _valid_id(run_id or "R" + timestamp.strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:12])
    root = _root(home)
    final = root / run_id
    if final.exists() or final.is_symlink():
        raise ValueError("immutable run already exists: " + run_id)
    _root(home, create=True)
    stage = Path(tempfile.mkdtemp(prefix=".stage-", dir=str(root)))
    try:
        content = {"report.json": _json(report), "claims.json": _json(ledger), "sources.json": _json(sources), "plan.json": _json(plan),
                   "report.md": markdown.encode("utf-8"), "report.html": page.encode("utf-8")}
        if calculations is not None:
            content["calculations.json"] = _json(calculations)
        if audit is not None:
            content["audit.json"] = _json(audit)
        if comparison is not None:
            content["diff.json"] = _json(comparison)
        for name, data in content.items():
            with (stage / name).open("xb") as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
        manifest = {"schema_version": 2, "run_id": run_id, "created_at": timestamp.isoformat().replace("+00:00", "Z"),
                    "as_of": report["as_of"], "files": {name: _hash(data) for name, data in content.items()},
                    "audit_role": "untrusted_metadata" if audit is not None else None,
                    "parent_run": parent_run, "parent_manifest_sha256": _hash((Path(parent["path"]) / "manifest.json").read_bytes()) if parent else None}
        with (stage / "manifest.json").open("xb") as f:
            f.write(_json(manifest))
            f.flush()
            os.fsync(f.fileno())
        # POSIX rename refuses an existing nonempty run directory. A per-ID
        # exclusive reservation also prevents simultaneous same-ID publications.
        reservation = root / (".reserve-" + run_id)
        try:
            fd = os.open(str(reservation), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            raise ValueError("run_id is being published")
        os.close(fd)
        try:
            if final.exists() or final.is_symlink():
                raise ValueError("immutable run already exists: " + run_id)
            if parent:
                # Detect any parent mutation between comparison and publication.
                checked_parent = load_run(parent_run, home)
                if checked_parent["manifest"] != parent["manifest"]:
                    raise ValueError("parent changed during archive")
            os.rename(str(stage), str(final))
        finally:
            reservation.unlink()
        return {"run_id": run_id, "path": str(final), "manifest": manifest, "diff": comparison}
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def _inputs(parser, plan=True):
    for field in ("report", "claims", "sources") + (("plan",) if plan else ()):
        parser.add_argument("--" + field, required=True, type=Path)
    if plan:
        parser.add_argument("--calculations", type=Path)
        parser.add_argument("--audit", type=Path, help="freeze query/review/execution metadata; does not certify its contents")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    for command in ("archive", "update"):
        command_parser = sub.add_parser(command)
        _inputs(command_parser)
        command_parser.add_argument("--parent-run", required=command == "update")
    sub.add_parser("list")
    show = sub.add_parser("show")
    show.add_argument("run_id")
    diff = sub.add_parser("diff")
    diff.add_argument("run_id")
    _inputs(diff, plan=False)
    diff.add_argument("--plan", type=Path, help="include structured plan comparability fields")
    args = parser.parse_args()
    try:
        if args.cmd in {"archive", "update"}:
            result = archive_run(args.report, args.claims, args.sources, args.plan, args.calculations, args.parent_run, audit_path=args.audit)
        elif args.cmd == "show":
            result = load_run(args.run_id)
        elif args.cmd == "list":
            result = list_runs()
        else:
            result = compare_run(load_run(args.run_id), read_document(args.report), read_document(args.claims), read_document(args.sources), read_document(args.plan) if args.plan else None)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
