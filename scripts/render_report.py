#!/usr/bin/env python3
"""Validate and render one frozen v2 research report.

Public API: validate_report(report, ledger, sources=None) -> list[str];
render_markdown(report, ledger, sources=None) -> str and
render_html(report, ledger, sources=None) -> str (both validate before rendering).
CLI: render_report.py report.json --claims claims.json --sources sources.json
                      --out-dir directory [--overwrite]
"""

import argparse
import html
import json
import math
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import quote, urlsplit

REPORT_TYPES = {"event_pricing", "asset", "theme", "actor"}
INCREMENTS = {"new_fact", "calculation", "connection", "contradiction", "judgment_update"}
ID = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]*$")


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _date(value):
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def safe_link(value):
    """Only absolute http(s), without credentials or control characters."""
    if not isinstance(value, str) or re.search(r"[\x00-\x20\x7f]", value):
        return None
    try:
        parsed = urlsplit(value)
        if parsed.scheme.lower() not in {"https", "http"} or not parsed.hostname or parsed.username or parsed.password:
            return None
        parsed.port  # Reject malformed ports too.
    except ValueError:
        return None
    return quote(value, safe="/:?&=#%+~@!$*,-._")


def _numeric_value(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    try:
        return value if math.isfinite(value) else None
    except OverflowError:
        return None


def _waterfall_errors(rows, path):
    """Waterfall totals must agree with the accumulated deltas between them."""
    errors = []
    running = None
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        role = row.get("role")
        if role not in {"total", "delta"}:
            errors.append("%s.rows[%d].role must be total or delta" % (path, index))
            return errors
        value = _numeric_value(row.get("value"))
        if value is None:
            continue
        if role == "total":
            if running is not None:
                tolerance = max(1e-9 * max(abs(running), abs(value)), 1e-12)
                if abs(value - running) > tolerance:
                    errors.append("%s.rows[%d] total %s does not match the accumulated %s" % (path, index, value, running))
            running = value
        elif running is None:
            errors.append(path + ".rows must start with a total row")
            return errors
        else:
            running += value
    return errors


def _chart_errors(chart, path, refs):
    """Validate one chart (single or multi-series); shared by chart and charts[]."""
    errors = []
    if not isinstance(chart, dict):
        return [path + " must be an object"]
    for key in ("title", "x_label", "y_label", "unit"):
        if not _text(chart.get(key)):
            errors.append(path + "." + key + " must be nonempty text")
    if "series" in chart:
        if "rows" in chart:
            errors.append(path + " must use either rows or series, not both")
        series = chart.get("series")
        if not isinstance(series, list) or not series:
            errors.append(path + ".series must be a nonempty list")
        else:
            labels = None
            for n, item in enumerate(series):
                item_path = "%s.series[%d]" % (path, n)
                if not isinstance(item, dict):
                    errors.append(item_path + " must be an object")
                    continue
                extra = set(item) - {"name", "rows"}
                if extra:
                    errors.append(item_path + " has unknown fields: " + ", ".join(sorted(map(str, extra))))
                if not _text(item.get("name")):
                    errors.append(item_path + ".name must be nonempty text")
                item_rows = item.get("rows")
                if not isinstance(item_rows, list) or len(item_rows) < 2 or any(
                        not isinstance(row, dict) or not _text(row.get("label")) or not _number(row.get("value"))
                        for row in item_rows):
                    errors.append(item_path + ".rows requires at least two label/finite numeric value pairs")
                    continue
                item_labels = [row["label"] for row in item_rows]
                if labels is None:
                    labels = item_labels
                elif item_labels != labels:
                    errors.append(item_path + ".rows must share the same labels as the first series")
    else:
        rows = chart.get("rows")
        if not isinstance(rows, list) or len(rows) < 2 or any(not isinstance(row, dict) or not _text(row.get("label")) or not _number(row.get("value")) for row in rows):
            errors.append(path + ".rows requires at least two label/finite numeric value pairs")
    kind = chart.get("kind", "line")
    if kind not in {"line", "bar", "waterfall"}:
        errors.append(path + ".kind must be line, bar or waterfall")
    mode = chart.get("bar_mode")
    if mode is not None:
        if kind != "bar":
            errors.append(path + ".bar_mode is only valid for bar charts")
        elif not isinstance(mode, str) or mode not in {"grouped", "stacked"}:
            errors.append(path + ".bar_mode must be grouped or stacked")
        elif mode == "stacked":
            if "series" not in chart:
                errors.append(path + ".bar_mode stacked requires series")
            else:
                series = chart.get("series")
                if isinstance(series, list):
                    for n, item in enumerate(series):
                        rows = item.get("rows") if isinstance(item, dict) else None
                        if isinstance(rows, list) and any(isinstance(row, dict) and _number(row.get("value")) and row["value"] < 0
                                                          for row in rows):
                            errors.append("%s.series[%d] stacked bars cannot contain negative values" % (path, n))
    elif kind == "waterfall" and "series" in chart:
        errors.append(path + ".kind waterfall cannot use series")
    if kind == "waterfall":
        rows = chart.get("rows")
        if isinstance(rows, list):
            errors.extend(_waterfall_errors(rows, path))
    refs(chart, path)
    if "note" in chart and not isinstance(chart["note"], str):
        errors.append(path + ".note must be text")
    return errors


def _quality_errors(report, claims):
    """Validate optional report.quality: frozen statements plus optional thresholds."""
    quality = report.get("quality")
    if quality is None:
        return []
    from financial_quality import THRESHOLDS, validate_document
    claim_ids = {claim["id"] for claim in claims if isinstance(claim, dict) and isinstance(claim.get("id"), str)}
    errors = []
    if not isinstance(quality, dict):
        return ["quality must be an object"]
    extra = set(quality) - {"statements", "thresholds"}
    if extra:
        errors.append("quality has unknown fields: " + ", ".join(sorted(map(str, extra))))
    statements = quality.get("statements")
    if not isinstance(statements, dict):
        return errors + ["quality.statements must be an object"]
    errors.extend("quality.statements: " + error for error in validate_document(statements))
    thresholds = quality.get("thresholds")
    if thresholds is not None:
        if not isinstance(thresholds, dict):
            errors.append("quality.thresholds must be an object")
        else:
            for key, value in thresholds.items():
                if key not in THRESHOLDS:
                    errors.append("quality.thresholds." + str(key) + " is not a known threshold")
                elif isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 < value <= 1:
                    errors.append("quality.thresholds." + str(key) + " must be a number in (0, 1]")
    periods = statements.get("periods") if isinstance(statements.get("periods"), list) else []
    for index, period in enumerate(periods):
        if not isinstance(period, dict):
            continue
        for field, value in period.items():
            if not isinstance(value, dict) or "claim_ids" not in value:
                continue
            refs = value.get("claim_ids")
            if not isinstance(refs, list) or any(not isinstance(cid, str) or cid not in claim_ids for cid in refs):
                errors.append("quality.statements.periods[%d].%s.claim_ids contains unknown claims" % (index, field))
    return errors


def _event_study_errors(report, claims):
    """Validate optional report.event_study: frozen samples plus usable-size check."""
    document = report.get("event_study")
    if document is None:
        return []
    from event_study import analyse as analyse_events, validate_document as validate_events
    claim_ids = {claim["id"] for claim in claims if isinstance(claim, dict) and isinstance(claim.get("id"), str)}
    errors = ["event_study: " + error for error in validate_events(document)]
    if errors:
        return errors
    samples = document.get("samples") if isinstance(document.get("samples"), list) else []
    for index, sample in enumerate(samples):
        refs = sample.get("claim_ids") if isinstance(sample, dict) else None
        if refs is None:
            continue
        if any(not isinstance(cid, str) or cid not in claim_ids for cid in refs):
            errors.append("event_study: samples[%d].claim_ids contains unknown claims" % index)
    if errors:
        return errors
    try:
        analyse_events(document)
    except ValueError as exc:
        errors.append("event_study: " + str(exc))
    return errors


def validate_report(report, ledger, sources=None):
    """Check structure, dates, references and evidence validators; not semantic truth."""
    errors = []
    if not isinstance(report, dict):
        return ["report must be an object"]
    if report.get("schema_version") != 2:
        errors.append("report.schema_version must be 2")
    for field in ("title", "question", "task", "as_of"):
        if not _text(report.get(field)):
            errors.append("report.%s must be nonempty text" % field)
    if not isinstance(report.get("type"), str) or report.get("type") not in REPORT_TYPES:
        errors.append("report.type is invalid")
    if not _date(report.get("as_of")):
        errors.append("report.as_of must be an ISO date/datetime")
    if not isinstance(ledger, dict):
        return errors + ["ledger must be an object"]
    if sources is None and isinstance(ledger.get("sources"), dict):
        sources = ledger["sources"]
    claims = ledger.get("claims")
    if not isinstance(claims, list) or not claims:
        return errors + ["ledger.claims must be a nonempty list"]
    ids = set()
    for claim in claims:
        cid = claim.get("id") if isinstance(claim, dict) else None
        if not isinstance(cid, str) or not ID.fullmatch(cid):
            errors.append("claim id must be a safe nonempty identifier")
        elif cid in ids:
            errors.append("duplicate claim id: " + cid)
        else:
            ids.add(cid)
        if isinstance(claim, dict):
            basis = claim.get("basis", [])
            if not isinstance(basis, list) or any(not isinstance(value, str) for value in basis):
                errors.append("claim %s basis must be a list of strings" % cid)
            claim_date, report_date = _date(claim.get("as_of")), _date(report.get("as_of"))
            try:
                if claim_date and report_date and claim_date > report_date:
                    errors.append("claim %s as_of is after report" % cid)
            except TypeError:
                errors.append("claim/report as_of timezone mismatch")
    if ledger.get("as_of") != report.get("as_of"):
        errors.append("ledger.as_of differs from report")
    try:
        from check_claims import validate_ledger
        result = validate_ledger(ledger, sources=sources)
        if not result.get("passed"):
            errors.append("claims validation failed: " + json.dumps(result.get("failures"), ensure_ascii=False))
    except (ImportError, TypeError, ValueError, KeyError, AttributeError) as exc:
        errors.append("claims validator unavailable or invalid input: " + str(exc))
    if sources is not None:
        if not isinstance(sources, dict):
            errors.append("sources must be an object")
        else:
            if sources.get("as_of") != report.get("as_of"):
                errors.append("sources.as_of differs from report")
            try:
                from sources import validate_sources
                errors.extend("sources: " + str(e) for e in validate_sources(sources))
            except (ImportError, TypeError, ValueError, KeyError, AttributeError) as exc:
                errors.append("sources validator unavailable or invalid input: " + str(exc))

    def refs(item, path, required=True):
        value = item.get("claim_ids")
        if not isinstance(value, list) or (required and not value):
            errors.append(path + ".claim_ids must be a nonempty list" if required else path + ".claim_ids must be a list")
            return
        if any(not isinstance(cid, str) or cid not in ids for cid in value):
            errors.append(path + ".claim_ids contains unknown references")
        if len([cid for cid in value if isinstance(cid, str)]) != len(set(cid for cid in value if isinstance(cid, str))):
            errors.append(path + ".claim_ids contains duplicates")

    answer = report.get("answer")
    if not isinstance(answer, dict) or not _text(answer.get("text")):
        errors.append("answer requires text and claim_ids")
    else:
        refs(answer, "answer")
    shapes = {"findings": ("title", "text", "why_it_matters"), "alternatives": ("title", "text"),
              "watch": ("signal", "meaning"), "limitations": ("text",), "tables": ("title",)}
    table_refs, table_ids = set(), set()
    for field, texts in shapes.items():
        items = report.get(field)
        if not isinstance(items, list):
            errors.append(field + " must be a list")
            continue
        for n, item in enumerate(items):
            path = "%s[%d]" % (field, n)
            if not isinstance(item, dict):
                errors.append(path + " must be an object")
                continue
            for key in texts:
                if not _text(item.get(key)):
                    errors.append(path + "." + key + " must be nonempty text")
            refs(item, path, required=field != "limitations")
            if field == "findings":
                inc = item.get("increment")
                if not isinstance(inc, dict) or not isinstance(inc.get("kind"), str) or inc.get("kind") not in INCREMENTS or not all(_text(inc.get(k)) for k in ("baseline", "detail")):
                    errors.append(path + ".increment requires kind, baseline and detail")
                if "table_ids" in item:
                    links = item.get("table_ids")
                    if not isinstance(links, list) or not links or any(not isinstance(tid, str) or not _text(tid) for tid in links):
                        errors.append(path + ".table_ids must be a nonempty table id list")
                    elif len(set(links)) != len(links):
                        errors.append(path + ".table_ids contains duplicates")
                    else:
                        table_refs.update(links)
            elif field == "limitations" and not isinstance(item.get("material"), bool):
                errors.append(path + ".material must be boolean")
            elif field == "tables":
                cols, rows = item.get("columns"), item.get("rows")
                if not isinstance(cols, list) or not cols or not all(_text(c) for c in cols):
                    errors.append(path + ".columns must be nonempty text list")
                if not isinstance(rows, list) or any(not isinstance(row, list) or not isinstance(cols, list) or len(row) != len(cols) or any(not _cell(c) for c in row) for row in rows):
                    errors.append(path + ".rows must match columns with scalar finite values")
                if "note" in item and not isinstance(item["note"], str):
                    errors.append(path + ".note must be text")
                if "id" in item:
                    tid = item.get("id")
                    if not isinstance(tid, str) or not ID.fullmatch(tid) or tid in table_ids:
                        errors.append(path + ".id must be a unique safe identifier")
                    else:
                        table_ids.add(tid)
                if "units" in item:
                    units = item.get("units")
                    if not isinstance(units, list) or not isinstance(cols, list) or len(units) != len(cols) or not all(isinstance(unit, str) for unit in units):
                        errors.append(path + ".units must be one text per column (empty means no unit)")
    if table_refs - table_ids:
        errors.append("finding.table_ids must reference a table with an id: " +
                      ", ".join(sorted(table_refs - table_ids)))
    if report.get("findings") == [] and not _text(report.get("no_change_reason")):
        errors.append("empty findings requires no_change_reason")
    if "chart" in report:
        errors.extend(_chart_errors(report["chart"], "chart", refs))
    if "charts" in report:
        if "chart" in report:
            errors.append("report must use either chart or charts, not both")
        charts = report.get("charts")
        if not isinstance(charts, list) or not charts:
            errors.append("charts must be a nonempty list")
        else:
            for n, item in enumerate(charts):
                errors.extend(_chart_errors(item, "charts[%d]" % n, refs))
    if any(isinstance(c, dict) and not _text(c.get("text")) for c in claims):
        errors.append("claim text must be nonempty")
    calculations = report.get("calculations", [])
    errors.extend(validate_calculation_rows(calculations, ids))
    calculation_ids = {row.get("id") for row in calculations if isinstance(row, dict) and isinstance(row.get("id"), str)} if isinstance(calculations, list) else set()
    analysis = report.get("analysis")
    model_rows = analysis.get("models", []) if isinstance(analysis, dict) else []
    model_map = {m["id"]: m for m in model_rows if isinstance(m, dict) and isinstance(m.get("id"), str)} if isinstance(model_rows, list) else {}
    if calculation_ids & model_map.keys():
        errors.append("calculation and analysis model ids must not collide")
    calculation_ids.update(model_map)
    for claim in claims:
        if isinstance(claim, dict):
            links = claim.get("calculation_ids", [])
            if not isinstance(links, list) or any(not isinstance(cid, str) or cid not in calculation_ids for cid in links):
                errors.append("claim calculation_ids contains unknown calculation")
            if "calculation_id" in claim and (not isinstance(claim["calculation_id"], str) or claim["calculation_id"] not in calculation_ids):
                errors.append("claim calculation_id is unknown")
    for finding in report.get("findings", []) if isinstance(report.get("findings"), list) else []:
        if not isinstance(finding, dict):
            continue
        inc = finding.get("increment")
        links = finding.get("calculation_ids", [])
        if not isinstance(links, list) or any(not isinstance(cid, str) or cid not in calculation_ids for cid in links):
            errors.append("finding.calculation_ids contains unknown calculations")
        if isinstance(inc, dict) and inc.get("kind") == "calculation" and not links:
            errors.append("calculation increment requires finding.calculation_ids")
    update = report.get("update")
    if update is not None:
        if not isinstance(update, dict) or not isinstance(update.get("judgment_changed"), bool) or not _text(update.get("reason")):
            errors.append("update requires judgment_changed boolean and author reason")
        comp = update.get("comparability") if isinstance(update, dict) else None
        if not isinstance(comp, dict) or not isinstance(comp.get("status"), str) or comp.get("status") not in {"comparable", "mixed", "not_comparable"} or not _text(comp.get("reason")):
            errors.append("update.comparability requires status and reason")
    if "analysis" in report:
        from analysis_contract import validate_analysis
        errors.extend(validate_analysis(report["analysis"], claims, sources=sources))
    errors.extend(validate_valuation_summary(report))
    errors.extend(validate_conflicts(report, ledger, sources))
    if "transmission" in report:
        from transmission import validate_document as validate_transmission
        claims = ledger.get("claims") if isinstance(ledger, dict) else None
        errors.extend("transmission: " + error for error in validate_transmission(report["transmission"], claims))
    errors.extend(_quality_errors(report, claims))
    errors.extend(_event_study_errors(report, claims))
    from catalyst_calendar import validate_report_catalysts
    errors.extend(validate_report_catalysts(report))
    from opportunity_contract import validate_opportunity
    errors.extend(validate_opportunity(report, claims))
    return errors


VALUATION_METRICS = {
    "dcf": {"per_share"},
    "relative_valuation": {"per_share"},
    "reverse_dcf": {"implied_growth"},
}


def valuation_prices(models):
    """Distinct observed prices referenced by model inputs: {(value, unit): [model ids]}."""
    found = {}
    for model in models if isinstance(models, list) else []:
        if not isinstance(model, dict):
            continue
        spec = model.get("spec")
        inputs = spec.get("inputs") if isinstance(spec, dict) else None
        price = inputs.get("price") if isinstance(inputs, dict) else None
        if isinstance(price, dict) and _number(price.get("value")):
            found.setdefault((price["value"], price.get("unit")), []).append(model.get("id"))
    return found


def _period_label_error(label, window):
    """Very narrow label check: only year-bearing labels are compared, nothing is parsed freely."""
    match = re.search(r"(?:fy|FY)\s*((?:19|20)\d{2})", label)
    start, end = window.get("start"), window.get("end")
    if match and isinstance(start, str) and isinstance(end, str):
        year = int(match.group(1))
        if year != int(end[:4]) and year != int(start[:4]):
            return "label year %d does not match the model window %s..%s" % (year, start, end)
    match = re.search(r"((?:19|20)\d{2})\s*[Qq]([1-4])", label)
    if match and isinstance(start, str) and isinstance(end, str):
        year = int(match.group(1))
        if not (int(start[:4]) <= year <= int(end[:4])):
            return "quarter label year %d is outside the model window %s..%s" % (year, start, end)
    return None


def validate_valuation_summary(report):
    """A summary row may only name a model and a metric; every number comes from that model."""
    summary = report.get("valuation_summary")
    if summary is None:
        return []
    analysis = report.get("analysis")
    models = analysis.get("models") if isinstance(analysis, dict) else None
    if not isinstance(models, list) or not models:
        return ["valuation_summary requires analysis models"]
    if not isinstance(summary, dict):
        return ["valuation_summary must be an object"]
    errors = []
    unknown = set(summary) - {"rows", "note"}
    if unknown:
        errors.append("valuation_summary has unknown fields: " + ", ".join(sorted(map(str, unknown))))
    if "note" in summary and not isinstance(summary["note"], str):
        errors.append("valuation_summary.note must be text")
    rows = summary.get("rows")
    if not isinstance(rows, list) or not rows:
        return errors + ["valuation_summary.rows must be a nonempty list"]
    model_map = {m["id"]: m for m in models if isinstance(m, dict) and isinstance(m.get("id"), str)}
    seen = set()
    for n, row in enumerate(rows):
        path = "valuation_summary.rows[%d]" % n
        if not isinstance(row, dict):
            errors.append(path + " must be an object")
            continue
        extra = set(row) - {"model_id", "label", "metric", "period"}
        if extra:
            errors.append(path + " must only name model_id, label, metric and period; values come from the model")
        model_id = row.get("model_id")
        if not isinstance(model_id, str) or model_id not in model_map:
            errors.append(path + ".model_id must reference an analysis model")
            continue
        if model_id in seen:
            errors.append(path + ".model_id duplicates another row")
        seen.add(model_id)
        if not _text(row.get("label")):
            errors.append(path + ".label must be nonempty text")
        if "period" in row and not _text(row.get("period")):
            errors.append(path + ".period must be nonempty text when present")
        spec = model_map[model_id].get("spec") or {}
        kind = spec.get("kind")
        metric = row.get("metric")
        allowed = VALUATION_METRICS.get(kind, set())
        if not allowed:
            errors.append(path + " references a model that does not produce a valuation metric")
        elif metric not in allowed:
            errors.append(path + ".metric must be one of " + ", ".join(sorted(allowed)) + " for " + str(kind))
    referenced = [model_map[model_id] for model_id in seen if model_id in model_map]
    windows = set()
    for model in referenced:
        window = model.get("period_window")
        if isinstance(window, dict):
            windows.add((window.get("start"), window.get("end"), window.get("period_type")))
    if len(windows) > 1:
        for n, row in enumerate(rows):
            if isinstance(row, dict) and isinstance(row.get("model_id"), str) and row["model_id"] in model_map \
                    and not _text(row.get("period")):
                errors.append("valuation_summary.rows[%d].period is required when the compared models use different period windows" % n)
    for n, row in enumerate(rows):
        if not isinstance(row, dict) or not _text(row.get("period")):
            continue
        model = model_map.get(row.get("model_id"))
        window = model.get("period_window") if isinstance(model, dict) else None
        if not isinstance(window, dict):
            continue
        message = _period_label_error(row["period"], window)
        if message:
            errors.append("valuation_summary.rows[%d].period " % n + message)
    prices = valuation_prices(models)
    if len(prices) > 1:
        rendered = ", ".join("%s %s" % (value, unit) for value, unit in sorted(prices, key=str))
        errors.append("valuation_summary requires one observed price across models, found: " + rendered)
    return errors


def validate_conflicts(report, ledger, sources):
    """Optional record of disagreeing sources and the value finally adopted."""
    conflicts = report.get("conflicts")
    if conflicts is None:
        return []
    if not isinstance(conflicts, list) or not conflicts:
        return ["conflicts must be a nonempty list"]
    claims = ledger.get("claims") if isinstance(ledger, dict) else None
    claim_map = {c["id"]: c for c in claims if isinstance(c, dict) and isinstance(c.get("id"), str)} if isinstance(claims, list) else {}
    source_doc = sources if isinstance(sources, dict) else (ledger.get("sources") if isinstance(ledger, dict) else {})
    source_ids = {s["id"] for s in source_doc.get("candidates", [])
                  if isinstance(s, dict) and isinstance(s.get("id"), str)}
    errors = []
    for n, entry in enumerate(conflicts):
        path = "conflicts[%d]" % n
        if not isinstance(entry, dict):
            errors.append(path + " must be an object")
            continue
        extra = set(entry) - {"metric", "candidates", "adopted_claim_id", "unit", "rule", "reason"}
        if extra:
            errors.append(path + " has unknown fields: " + ", ".join(sorted(map(str, extra))))
        for field in ("metric", "unit", "rule", "reason"):
            if not _text(entry.get(field)):
                errors.append(path + "." + field + " must be nonempty text")
        adopted = entry.get("adopted_claim_id")
        adopted_claim = claim_map.get(adopted) if isinstance(adopted, str) else None
        if adopted_claim is None:
            errors.append(path + ".adopted_claim_id must reference a claim")
        elif adopted_claim.get("type") not in {"fact", "price", "consensus"}:
            errors.append(path + ".adopted_claim_id must be a fact/price/consensus claim")
        candidates = entry.get("candidates")
        values = []
        if not isinstance(candidates, list) or len(candidates) < 2:
            errors.append(path + ".candidates must list at least two sources")
        else:
            for i, candidate in enumerate(candidates):
                cpath = path + ".candidates[%d]" % i
                if not isinstance(candidate, dict):
                    errors.append(cpath + " must be an object")
                    continue
                extra = set(candidate) - {"source_id", "value"}
                if extra:
                    errors.append(cpath + " has unknown fields: " + ", ".join(sorted(map(str, extra))))
                if not isinstance(candidate.get("source_id"), str) or candidate["source_id"] not in source_ids:
                    errors.append(cpath + ".source_id must reference a source")
                value = candidate.get("value")
                if _number(value) is not True:
                    errors.append(cpath + ".value must be a finite number")
                else:
                    values.append(value)
            if len(values) >= 2 and len({round(value, 12) for value in values}) < 2:
                errors.append(path + ".candidates must report different values")
        if isinstance(adopted_claim, dict):
            metric = adopted_claim.get("metric")
            if isinstance(metric, dict) and values:
                unit = entry.get("unit")
                if _text(metric.get("unit")) and _text(unit) and metric["unit"].strip().casefold() != unit.strip().casefold():
                    errors.append(path + ".unit differs from the adopted claim metric unit")
                elif _number(metric.get("value")) is True:
                    adopted_value = metric["value"]
                    if not any(abs(adopted_value - value) <= max(1e-9 * abs(adopted_value), 1e-12) for value in values):
                        errors.append(path + ".adopted_claim_id metric value must match one candidate")
    return errors


def validate_calculation_rows(rows, claim_ids):
    """Check transparent formula/input/result records through calculations.py.

    Rows with a whitelisted `op` are recomputed and compared with the frozen
    result; rows without `op` remain records of a readable formula whose
    arithmetic needs external review. Neither path proves economic meaning.
    """
    from calculations import validate_calculations
    return validate_calculations(rows, claim_ids)


def _number(value):
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def _cell(value):
    return value is None or isinstance(value, (str, bool)) or _number(value)


def _str(value):
    return "—" if value is None else str(value)


def _metric_text(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return "—"
    try:
        if not math.isfinite(value):
            return "—"
    except OverflowError:
        return "—"
    return str(round(value, 4))


def _table_columns(table):
    """Column labels, with an optional per-column unit appended in the header."""
    columns = list(table["columns"])
    units = table.get("units")
    if isinstance(units, list) and len(units) == len(columns):
        return [column + ("（" + unit + "）" if _text(unit) else "") for column, unit in zip(columns, units)]
    return columns


def _checked(report, ledger, sources):
    errors = validate_report(report, ledger, sources)
    if errors:
        raise ValueError("\n".join(errors))


def _blocks(report, ledger, sources):
    """One content sequence for both formats, including their evidence audit."""
    yield ("h1", report["title"])
    yield ("p", report["question"])
    yield ("p", "研究截点 " + report["as_of"] + " · " + report["type"] + " · " + report["task"])
    legacy = ledger.get("schema_version", 1) == 1
    if legacy:
        yield ("p", "证据模式：旧版 schema 1；本报告未按 schema 2 的来源与证据契约校验。")
    yield ("h2", "判断")
    yield ("p", report["answer"]["text"], report["answer"]["claim_ids"])
    if report.get("opportunity"):
        from opportunity_contract import opportunity_blocks
        yield from opportunity_blocks(report["opportunity"])
    for limit in report["limitations"]:
        if limit["material"]:
            yield ("p", "重要限制：" + limit["text"], limit["claim_ids"])
    if report.get("no_change_reason"):
        yield ("p", report["no_change_reason"])
    tables_by_id = {table["id"]: table for table in report["tables"]
                    if isinstance(table, dict) and isinstance(table.get("id"), str)}
    referenced_tables = set()
    for finding in report["findings"]:
        yield ("h2", finding["title"])
        yield ("p", finding["text"], finding["claim_ids"])
        yield ("p", "为什么重要：" + finding["why_it_matters"])
        if "opportunity" not in report:
            yield ("p", "相较基线：" + finding["increment"]["baseline"])
            yield ("p", "研究增量（" + finding["increment"]["kind"] + "）：" + finding["increment"]["detail"])
        for table_id in finding.get("table_ids", []):
            table = tables_by_id.get(table_id)
            if table is not None:
                yield ("table", table)
                referenced_tables.add(table_id)
    if report.get("analysis"):
        yield from _analysis_blocks(report["analysis"], answer_text=report["answer"]["text"])
    if report.get("valuation_summary"):
        yield from _valuation_summary_blocks(report)
    calculations = report.get("calculations", [])
    for calculation in calculations:
        yield ("h2", calculation["description"])
        label = "计算式：" + calculation["formula"]
        if calculation.get("op"):
            label += "（op=" + str(calculation["op"]) + "，已按固定算子重算）"
        yield ("p", label, calculation["claim_ids"])
        yield ("table", {"title": calculation["id"] + " 输入", "columns": ["名称", "数值", "单位"],
                         "rows": [[v["name"], v.get("value", "= " + str(v.get("ref"))), v["unit"]] for v in calculation["inputs"]],
                         "claim_ids": [cid for v in calculation["inputs"] for cid in v.get("claim_ids", [])]})
        result_text = "结果：" + str(calculation["result"]["value"]) + " " + calculation["result"]["unit"]
        if calculation.get("op"):
            result_text += "（重算一致）"
        yield ("p", result_text)
    if any(isinstance(item, dict) and item.get("op") for item in calculations):
        yield ("p", "标注 op 的计算式已由固定算子重算；未标注的仅记录公式，未经重算。")
    for table in report["tables"]:
        if isinstance(table, dict) and table.get("id") in referenced_tables:
            continue
        yield ("table", table)
    if report.get("chart"):
        c = report["chart"]
        yield ("chart", c)
        yield ("table", _chart_table(c))
    for c in report.get("charts", []):
        yield ("chart", c)
        yield ("table", _chart_table(c))
    for field, heading in (("alternatives", "其他解释"), ("watch", "接下来观察什么")):
        if report[field]:
            yield ("h2", heading)
        for item in report[field]:
            yield ("h3", item.get("title", item.get("signal")))
            yield ("p", item.get("text", item.get("meaning")), item["claim_ids"])
    other = [item for item in report["limitations"] if not item["material"]]
    if other:
        yield ("h2", "其他限制")
        for item in other:
            yield ("p", item["text"], item["claim_ids"])
    if report.get("update"):
        update = report["update"]
        yield ("h2", "本轮更新说明")
        yield ("p", "判断变化：" + ("是" if update["judgment_changed"] else "否") + "；" + update["reason"])
        yield ("p", "可比性：" + update["comparability"]["status"] + "；" + update["comparability"]["reason"])
        if update.get("opportunity"):
            from opportunity_contract import update_blocks
            yield from update_blocks(update["opportunity"])
    if report.get("opportunity"):
        from opportunity_contract import opportunity_blocks
        yield from opportunity_blocks(report["opportunity"], appendix=True)
        if report["findings"]:
            yield ("h2", "附录：相对原文与旧判断的增量")
            for finding in report["findings"]:
                yield ("p", finding["title"] + "；基线：" + finding["increment"]["baseline"] + "；增加的判断：" + finding["increment"]["detail"], finding["claim_ids"])
    if report.get("analysis"):
        yield from _analysis_blocks(report["analysis"], appendix=True)
    if report.get("conflicts"):
        yield ("h2", "来源冲突与取舍")
        yield ("table", {"title": "冲突与采用", "columns": ["指标", "候选来源值", "采用主张", "单位", "取舍规则", "理由"],
                         "rows": [[entry["metric"],
                                   "；".join("%s=%s" % (candidate["source_id"], candidate["value"])
                                            for candidate in entry["candidates"]),
                                   entry["adopted_claim_id"], entry["unit"], entry["rule"], entry["reason"]]
                                  for entry in report["conflicts"]],
                         "claim_ids": [entry["adopted_claim_id"] for entry in report["conflicts"]]})
    from consensus import analyse as analyse_consensus, guidance_entries, snapshots as consensus_snapshots
    consensus_rows = consensus_snapshots(ledger["claims"])
    if consensus_rows:
        yield ("h2", "一致预期序列")
        yield ("table", {"title": "共识快照",
                         "columns": ["序列", "目标期间", "提供方", "截点", "中位", "样本量", "低", "高"],
                         "rows": [[row["series_id"], row["target_period"], row["provider"], row["as_of"],
                                   row["median"], row["sample_size"], row["low"], row["high"]]
                                  for row in consensus_rows],
                         "claim_ids": [row["claim_id"] for row in consensus_rows]})
        yield ("p", "修订只在同一序列与目标期间内比较；跨提供方不可直接比较，样本量与离散度须一并看。")
        growth = analyse_consensus(ledger["claims"]).get("period_growth") or []
        if growth:
            yield ("h3", "相邻财年的隐含增长")
            yield ("table", {"title": "共识隐含增长",
                             "columns": ["序列", "指标", "自", "至", "起点中位", "终点中位", "隐含增长"],
                             "rows": [[row["series_id"], row["metric"], row["from_period"], row["to_period"],
                                       row["from_median"], row["to_median"], _metric_text(row["implied_growth"])]
                                      for row in growth],
                             "claim_ids": list(dict.fromkeys([row["from_claim"] for row in growth] +
                                                             [row["to_claim"] for row in growth]))})
            yield ("p", "隐含增长只在同一序列、同一提供方、相邻财年之间计算；它不是研究判断，只是共识自己的算术。")
    guidance_rows = guidance_entries(ledger["claims"])
    if guidance_rows:
        yield ("h3", "公司指引（不是分析师共识）")
        yield ("table", {"title": "管理层指引",
                         "columns": ["主张", "指标", "目标期间", "中点", "低", "高", "截点"],
                         "rows": [[row["claim_id"], row["metric"], row["target_period"], row["midpoint"],
                                   row["low"], row["high"], row["as_of"]] for row in guidance_rows],
                         "claim_ids": [row["claim_id"] for row in guidance_rows]})
    if report.get("transmission"):
        from transmission import analyse as analyse_transmission
        document = report["transmission"]
        result = analyse_transmission(document)
        yield ("h2", "行业传导")
        yield ("p", "瓶颈：" + result["bottleneck"]["label"] + "（" + result["bottleneck"]["node"] + "）｜" +
               result["bottleneck"]["reason"],
               [cid for cid in document["bottleneck"].get("claim_ids", [])])
        directions = {"upstream": "瓶颈上游", "downstream": "瓶颈下游", "bottleneck": "瓶颈", "unrelated": "无路径"}
        yield ("table", {"title": "传导节点",
                         "columns": ["节点", "标签", "方向", "可观察指标"],
                         "rows": [[node["id"], node["label"], directions.get(result["directions"].get(node["id"]), "—"),
                                   "；".join(node.get("observables", []))] for node in document["nodes"]],
                         "claim_ids": list(dict.fromkeys(cid for node in document["nodes"]
                                                         for cid in node.get("claim_ids", [])))})
        if result["paths"]:
            yield ("p", "传导路径：" + "；".join(" → ".join(path) for path in result["paths"]))
        for warning in result["warnings"]:
            yield ("p", "传导提示：" + warning)
    if report.get("quality"):
        from financial_quality import analyse as analyse_quality
        quality = report["quality"]
        result = analyse_quality(quality["statements"], quality.get("thresholds"))
        period_rows = []
        claim_ids = []
        for period in quality["statements"].get("periods", []):
            for value in period.values():
                if isinstance(value, dict):
                    claim_ids.extend(cid for cid in value.get("claim_ids", []) if isinstance(cid, str))
        claim_ids = list(dict.fromkeys(claim_ids))
        fields = (("gross_margin", "毛利率"), ("operating_margin", "营业利润率"), ("net_margin", "净利率"),
                  ("cash_conversion", "现金转化"), ("accrual_ratio", "应计比率"),
                  ("capex_intensity", "资本开支/收入"), ("capex_to_da", "资本开支/折旧"),
                  ("sbc_ratio", "SBC/收入"), ("roic", "ROIC"))
        for row in result["periods"]:
            period_rows.append([row["id"]] + [_metric_text(row["metrics"].get(name)) for name, _ in fields])
        yield ("h2", "盈利质量")
        yield ("table", {"title": "关键指标", "columns": ["期间"] + [label for _, label in fields],
                         "rows": period_rows, "claim_ids": claim_ids})
        changes = result["changes"]
        if changes:
            change_fields = (("revenue_growth", "收入增长"), ("gross_margin_change", "毛利率变化"),
                             ("operating_margin_change", "营业利润率变化"), ("incremental_margin", "增量利润率"),
                             ("dso_change", "DSO变化"), ("dio_change", "DIO变化"), ("share_growth", "股本变化"))
            yield ("table", {"title": "环比变化",
                             "columns": ["区间"] + [label for _, label in change_fields],
                             "rows": [[item["from"] + " → " + item["to"]] +
                                      [_metric_text(item.get(name)) for name, _ in change_fields]
                                      for item in changes],
                             "claim_ids": claim_ids})
        unattributed = {period: fields for period, fields in (result.get("unattributed") or {}).items() if fields}
        if unattributed:
            yield ("p", "未挂 claim 的字段：" + "；".join(
                "%s：%s" % (period, "、".join(fields)) for period, fields in unattributed.items()))
        if result["flags"]:
            yield ("h3", "红旗")
            for item in result["flags"]:
                yield ("p", item["period"] + "｜" + item["code"] + "：" + item["message"])
        else:
            yield ("p", "未触发默认红旗阈值；这不等于没有风险。")
        yield ("p", "指标由嵌入的报表输入确定性计算；输入口径与来源仍须核对，阈值可在quality.thresholds覆盖。")
    if report.get("event_study"):
        from event_study import analyse as analyse_events
        result = analyse_events(report["event_study"])
        window = result["window"]
        yield ("h2", "事件研究")
        yield ("p", "事件类型：" + str(result["event"]) + "；窗口：−%s / +%s 个观测点" % (window["before"], window["after"]))
        def _pct(value):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                return "—"
            try:
                return "{:.2f}%".format(value * 100)
            except (OverflowError, ValueError):
                return "—"

        summary_rows = []
        for name, label in (("pre_return", "前窗"), ("post_return", "后窗"), ("total_return", "全窗"),
                            ("excess_post_return", "后窗超额"), ("excess_total_return", "全窗超额")):
            stats = result["summary"].get(name)
            if not stats:
                continue
            summary_rows.append([label, stats["n"], _pct(stats["median"]), _pct(stats["mean"]),
                                 _pct(stats["q1"]), _pct(stats["q3"]),
                                 _pct(stats["min"]), _pct(stats["max"]),
                                 _pct(stats["positive_rate"])])
        for name, entries in (result["summary"].get("benchmark_excess") or {}).items():
            for key, prefix in (("post_return", "后窗超额·"), ("total_return", "全窗超额·")):
                stats = entries.get(key)
                if not stats:
                    continue
                summary_rows.append([prefix + str(name), stats["n"], _pct(stats["median"]),
                                     _pct(stats["mean"]), _pct(stats["q1"]),
                                     _pct(stats["q3"]), _pct(stats["min"]),
                                     _pct(stats["max"]), _pct(stats["positive_rate"])])
        sample_claims = list(dict.fromkeys(cid for sample in report["event_study"].get("samples", [])
                                           if isinstance(sample, dict)
                                           for cid in sample.get("claim_ids", []) if isinstance(cid, str)))
        yield ("table", {"title": "参考类收益分布",
                         "columns": ["收益口径", "n", "中位", "均值", "Q1", "Q3", "最小", "最大", "为正比例"],
                         "rows": summary_rows, "claim_ids": sample_claims})
        has_excess = any(row.get("excess_total_return") is not None for row in result["samples"])
        columns = ["样本", "事件日", "前窗收益", "后窗收益", "全窗收益"]
        if has_excess:
            columns += ["后窗超额", "全窗超额"]
        rows = []
        for row in result["samples"]:
            cells = [row["id"], row["event_date"], _pct(row["pre_return"]),
                     _pct(row["post_return"]), _pct(row["total_return"])]
            if has_excess:
                cells += [_pct(row.get("excess_post_return")), _pct(row.get("excess_total_return"))]
            rows.append(cells)
        yield ("table", {"title": "样本明细", "columns": columns, "rows": rows, "claim_ids": sample_claims})
        if result["skipped"]:
            yield ("p", "跳过：" + "；".join("%s（%s）" % (row["id"], row["reason"]) for row in result["skipped"]))
        if result.get("warnings"):
            yield ("p", "样本警告：" + "；".join(result["warnings"]) + "。参考类统计不独立，不能当独立样本外推。")
        named = result["summary"].get("benchmark_excess") or {}
        if named:
            if result.get("beta_adjusted"):
                yield ("p", "前窗/后窗/全窗是绝对收益；超额是标的收益减基准收益（简单差）；"
                            "样本给出 beta 时超额按标的减 beta×基准计算。多基准时各基准的分布见「后窗超额·名称」行。"
                            "样本事前选定、不给p值；参考类分布不是预测。")
            else:
                yield ("p", "前窗/后窗/全窗是绝对收益；超额是标的收益减基准收益（简单差，未做 beta 调整）。"
                            "多基准时各基准的分布见「后窗超额·名称」行。样本事前选定、不给p值；参考类分布不是预测。")
        elif has_excess:
            if result.get("beta_adjusted"):
                yield ("p", "前窗/后窗/全窗是绝对收益；后窗超额/全窗超额是标的收益减基准收益（简单差）；"
                            "样本给出 beta 时超额按标的减 beta×基准计算。样本事前选定、不给p值；参考类分布不是预测。")
            else:
                yield ("p", "前窗/后窗/全窗是绝对收益；后窗超额/全窗超额是标的收益减基准收益（简单差，未做 beta 调整）。样本事前选定、不给p值；参考类分布不是预测。")
        else:
            yield ("p", "绝对收益、样本事前选定、不给p值；参考类分布不是预测，也不是超额收益。")
    yield ("audit", "来源与结论审计")
    from metrics import describe as _describe_metric, extract_metrics
    metric_rows = extract_metrics(ledger["claims"])
    if metric_rows:
        yield ("h3", "数值事实")
        yield ("table", {"title": "结构化数值与口径", "columns": ["主张", "实体", "指标", "数值", "单位", "期间", "口径", "范围"],
                         "rows": [[row["claim_id"], row["entity"], row["name"], row["value"], row["unit"],
                                   _describe_metric({"period_type": row["period_type"], "period_start": row["period_start"],
                                                     "period_end": row["period_end"], "scope": row["scope"],
                                                     "basis": row["basis"]}),
                                   row["basis"], row["scope"]] for row in metric_rows],
                         "claim_ids": [row["claim_id"] for row in metric_rows]})
    for claim in ledger["claims"]:
        yield ("claim", claim)
    source_doc = sources if sources is not None else ledger.get("sources", {})
    for source in source_doc.get("candidates", []):
        yield ("source", source)
    if legacy:
        for claim in ledger["claims"]:
            for source in claim.get("sources", []):
                yield ("source", source)
    if source_doc.get("source_status"):
        yield ("p", "来源状态：" + json.dumps(source_doc["source_status"], ensure_ascii=False, sort_keys=True))


def _valuation_summary_blocks(report):
    """Body table across valuation methods; every number is read from a frozen model."""
    summary = report["valuation_summary"]
    models = {model["id"]: model for model in report["analysis"]["models"]}
    prices = valuation_prices(report["analysis"]["models"])
    price = unit_price_ref = None
    if len(prices) == 1:
        (price, unit_price_ref), _ = next(iter(prices.items()))
    yield ("h2", "估值汇总")
    rows, claims = [], []
    has_period = any(isinstance(entry.get("period"), str) and entry["period"].strip()
                     for entry in summary["rows"] if isinstance(entry, dict))
    period_of = {entry.get("model_id"): entry.get("period") for entry in summary["rows"] if isinstance(entry, dict)}
    for entry in summary["rows"]:
        model = models[entry["model_id"]]
        kind = model["spec"]["kind"]
        outputs = model["result"]["outputs"]
        claims.extend(model.get("output_claim_ids", []))
        period = entry.get("period") if _text(entry.get("period")) else None
        if kind == "dcf":
            mid = outputs["per_share"]["value"]
            values = [row["outputs"]["per_share"]["value"] for row in model["result"]["sensitivity"]
                      if isinstance(row.get("outputs"), dict) and "per_share" in row["outputs"]]
            distinct = sorted(set(values))
            low, high = (distinct[0], distinct[-1]) if len(distinct) > 1 else (mid, mid)
            rows.append([entry["label"], "每股价值", low, mid, high, outputs["per_share"]["unit"],
                         (mid / price - 1) if price else "—"])
        elif kind == "relative_valuation":
            low, mid, high = (outputs["per_share_low"]["value"], outputs["per_share_median"]["value"],
                              outputs["per_share_high"]["value"])
            rows.append([entry["label"], "每股价值", low, mid, high, outputs["per_share_median"]["unit"],
                         (mid / price - 1) if price else "—"])
        else:
            rows.append([entry["label"], "隐含增长率", "—", outputs["implied_growth"]["value"], "—", "ratio", "—"])
    columns = ["方法", "指标", "低", "中", "高", "单位", "中位相对现价"]
    if has_period:
        columns.insert(1, "期间")
        rows = [[row[0], period_of.get(entry["model_id"]) or "—"] + row[1:]
                for row, entry in zip(rows, summary["rows"])]
    yield ("table", {"title": "方法区间对照", "columns": columns,
                     "rows": rows, "claim_ids": list(dict.fromkeys(claims))})
    if price:
        yield ("p", "参考现价（来自模型输入的带时刻价格）：" + str(price) + " " + str(unit_price_ref) + "。")
    yield ("p", "区间来自各方法的固定模型输出；不跨方法加权、不给概率、不是目标价。反向DCF一行是价格隐含的预期，不是估值。")
    if summary.get("note"):
        yield ("p", summary["note"])


def _analysis_blocks(analysis, appendix=False, answer_text=None):
    """Economic summary in the body; reproducible detail in a shared appendix."""
    if not appendix:
        yield ("h2", "分析判断")
        if analysis["conclusion"] != answer_text:
            yield ("p", analysis["conclusion"], analysis["conclusion_claim_ids"])
        yield ("p", "传导关系：" + " → ".join(analysis["mechanism_chain"]))
        if analysis["model_status"] != "computed":
            label = "模型数据缺失：" if analysis["model_status"] == "missing" else "模型不适用："
            yield ("p", label + analysis["model_reason"])
        market = analysis["market"]
        if market["status"] == "assessed":
            yield ("h3", "价格要求什么，研究判断有什么不同")
            for key, label in (("implied_expectation", "隐含预期"), ("research_expectation", "研究假设"), ("gap", "差异"), ("conditions", "改变判断的条件")):
                yield ("p", label + "：" + market[key], market["claim_ids"])
        elif market["status"] == "missing":
            yield ("p", "市场预期尚未评估：" + market["reason"])
        return
    yield ("h2", "附录：分析底稿与可复算模型")
    yield ("p", "方法：" + analysis["method"] + "；比较基准：" + analysis["baseline"], analysis["baseline_claim_ids"])
    yield ("table", {"title": "候选解释", "columns": ["编号", "解释"],
                     "rows": [[h["id"], h["explanation"]] for h in analysis["hypotheses"]], "claim_ids": []})
    for test in analysis["tests"]:
        yield ("h3", "区分性检验 " + test["id"])
        yield ("table", {"title": "不同解释的事前预测", "columns": ["解释", "预期观察"],
                         "rows": [[o["hypothesis_id"], o["prediction"]] for o in test["outcomes"]], "claim_ids": []})
        yield ("p", ("观察结果：" if test["status"] == "observed" else "观察缺失：" + test["gap_reason"] + "；") + test["interpretation"], test["claim_ids"])
        yield ("p", "支持：" + ", ".join(test["supports"]) + "；削弱：" + ", ".join(test["weakens"]))
        yield ("p", "下一观察：" + test["next_observation"] + "；时间/触发：" + test["by"] + "；支持条件：" + test["supports_if"] + "；削弱条件：" + test["weakens_if"])
    for model in analysis["models"]:
        heading = model["description"]
        if model.get("scenario") in {"bear", "base", "bull"}:
            heading = "[情景 " + model["scenario"] + "] " + heading
        yield ("h3", heading)
        yield ("p", "模型：" + model["spec"]["kind"] + "；币种：" + model["currency"] + "；金额与股数共同缩放：" + model["scale"] + "；期间：" + model["period"] + "；范围：" + model["scope"])
        peers = model["spec"].get("peers")
        if peers:
            peer_claims = list(dict.fromkeys(cid for peer in peers for cid in peer.get("claim_ids", [])))
            if model.get("peer_set_rationale"):
                yield ("p", "可比公司选择：" + model["peer_set_rationale"], peer_claims)
            yield ("table", {"title": "可比公司倍数", "columns": ["可比公司", "倍数", "备注"],
                             "rows": [[peer["name"], peer["multiple"], peer.get("note", "")] for peer in peers],
                             "claim_ids": peer_claims})
        segments = model["spec"].get("segments")
        if segments:
            segment_claims = list(dict.fromkeys(cid for segment in segments for cid in segment.get("claim_ids", [])))
            has_base_margin = any("base_margin" in segment for segment in segments)
            columns = ["分部", "基期收入", "量增长", "价增长"]
            columns += ["基期利润率", "情景利润率"] if has_base_margin else ["利润率"]
            rows = []
            for segment in segments:
                row = [segment["name"], segment["base_revenue"], segment["volume_growth"], segment["price_growth"]]
                if has_base_margin:
                    row += [segment.get("base_margin", "—"), segment["margin"]]
                else:
                    row.append(segment["margin"])
                rows.append(row)
            yield ("table", {"title": "分部驱动", "columns": columns, "rows": rows,
                             "claim_ids": segment_claims})
            projection = model["result"]["outputs"].get("projection")
            if isinstance(projection, list) and projection:
                yield ("table", {"title": "多年推演（%s %s）" % (model["currency"], model["scale"]),
                                 "columns": ["年度", "收入", "营业利润"],
                                 "rows": [[year["label"], year["revenue"]["value"], year["profit"]["value"]]
                                          for year in projection],
                                 "claim_ids": segment_claims})
                yield ("p", "推演逐年套用给定的收入增长率与利润率，从模型当年收入起步；不含 margin_delta 敏感性。")
        fade = model["spec"].get("fade_years")
        if isinstance(fade, int) and fade:
            yield ("p", "显式期后按 %d 年线性收敛到终值增长（多阶段），不是恒定增长。" % fade)
        yield ("table", {"title": "观察值与假设", "columns": ["变量", "数值", "单位", "性质", "假设理由"],
                         "rows": [[name, v["value"], v["unit"], v["role"], model["assumptions"].get(name, "")] for name, v in model["spec"]["inputs"].items()],
                         "claim_ids": list(dict.fromkeys(cid for v in model["spec"]["inputs"].values() for cid in v["claim_ids"]))})
        scalars = {name: model["result"]["outputs"][name]
                   for name in sorted(model["result"]["outputs"])
                   if isinstance(model["result"]["outputs"][name], dict)
                   and "value" in model["result"]["outputs"][name]
                   and "unit" in model["result"]["outputs"][name]}
        yield ("table", {"title": "固定模型重算结果", "columns": ["输出", "结果", "单位"],
                         "rows": [[name, v["value"], v["unit"]] for name, v in scalars.items()],
                         "claim_ids": model["output_claim_ids"]})
        yield ("table", {"title": "单参数敏感性（其余输入固定）", "columns": ["变量", "改为", "单位", "输出", "结果", "结果单位"],
                         "rows": [[row["input"], row["value"], row["unit"], name, row["outputs"][name]["value"],
                                   row["outputs"][name]["unit"]]
                                  for row in model["result"]["sensitivity"] for name in sorted(row["outputs"])
                                  if isinstance(row["outputs"][name], dict) and "value" in row["outputs"][name]],
                         "claim_ids": model["output_claim_ids"]})
        tornado_rows = model["result"].get("tornado")
        if tornado_rows:
            yield ("table", {"title": "龙卷风敏感性（按影响排序）",
                             "columns": ["输入", "低值", "高值", "输出（低）", "输出（高）", "变动幅度"],
                             "rows": [[row["input"], row["low"], row["high"], row["low_output"]["value"],
                                       row["high_output"]["value"], row["swing"]] for row in tornado_rows],
                             "claim_ids": model["output_claim_ids"]})
            yield ("p", "龙卷风逐项移动一个输入，不是联合情景；变动幅度是同一输出在两端之差。")
    scenario_sets = {}
    for model in analysis["models"]:
        if isinstance(model, dict) and model.get("scenario") in {"bear", "base", "bull"} \
                and isinstance(model.get("scenario_set"), str):
            scenario_sets.setdefault(model["scenario_set"], []).append(model)
    order = {"bear": 0, "base": 1, "bull": 2}
    for set_id, members in scenario_sets.items():
        members = sorted(members, key=lambda item: order.get(item.get("scenario"), 9))
        def scalar_outputs(outputs):
            return {name for name, value in outputs.items()
                    if isinstance(value, dict) and "value" in value and "unit" in value}

        outputs = [scalar_outputs(member["result"]["outputs"]) for member in members]
        common = set.intersection(*outputs) if outputs else set()
        columns = [name for name in sorted(members[0]["result"]["outputs"]) if name in common]
        if not columns:
            continue
        rows = [[member["scenario"]] + [member["result"]["outputs"][name]["value"] for name in columns]
                for member in members]
        claim_ids = list(dict.fromkeys(cid for member in members for cid in member.get("output_claim_ids", [])))
        yield ("h3", "情景对比：" + set_id)
        yield ("table", {"title": "情景输出对照",
                         "columns": ["情景"] + [name + "（" + members[0]["result"]["outputs"][name]["unit"] + "）"
                                                for name in columns],
                         "rows": rows, "claim_ids": claim_ids})
        yield ("p", "情景之间不是概率加权：不计算期望值、不给概率，也不把区间当作预测。")
        projections = [member["result"]["outputs"].get("projection") for member in members]
        if all(isinstance(item, list) and item for item in projections):
            labels = [row["label"] for row in projections[0]]
            aligned = all([row["label"] for row in item] == labels for item in projections) and all(
                all(isinstance(row.get(metric), dict) and "value" in row[metric] for row in item)
                for item in projections for metric in ("revenue", "profit"))
            if aligned:
                yield ("h3", "情景推演对照：" + set_id)
                for metric, title in (("revenue", "收入"), ("profit", "营业利润")):
                    columns = ["年度"] + ["%s（%s）" % (member["scenario"], members[0]["currency"])
                                          for member in members]
                    rows = [[label] + [item[index][metric]["value"] for item in projections]
                            for index, label in enumerate(labels)]
                    yield ("table", {"title": "情景%s推演" % title, "columns": columns, "rows": rows,
                                     "claim_ids": claim_ids})
                yield ("p", "三条路径各用自己情景模型的分部假设；不是概率加权，也不把任一路径当作预测。")
    yield ("p", "固定模型的数值已重算；来源含义、假设合理性与因果解释仍需研究审查。敏感性结果不是统计置信区间。")


def _source_text(source):
    parts = [str(source.get("id", "")), str(source.get("publisher", "")), str(source.get("tier", ""))]
    for key in ("published_at", "retrieved_at", "quote", "locator", "origin_id", "origin_basis", "evidence_kind", "access_status", "supports", "selection", "market_quote", "survey", "availability", "attribution"):
        if key in source:
            value = source[key]
            parts.append(key + "：" + (json.dumps(value, ensure_ascii=False, sort_keys=True) if isinstance(value, (dict, list)) else str(value)))
    return " · ".join(parts)


def _claim_text(claim):
    return "[%s] %s（%s；%s）" % (claim["id"], claim["text"], claim["type"], claim["as_of"])


def _md(value):
    # Literal text only: escape raw HTML and every Markdown structural character.
    value = html.escape(_str(value), quote=False)
    return re.sub(r"([\\`*_{}\[\]()#+.!|>~-])", r"\\\1", value).replace("\n", "<br>")


def render_markdown(report, ledger, sources=None):
    """Return Markdown from validated frozen report/ledger/sources dictionaries."""
    _checked(report, ledger, sources)
    out = []
    for block in _blocks(report, ledger, sources):
        kind, value = block[:2]
        if kind in {"h1", "h2", "h3", "audit"}:
            out.append(("#" * ({"h1": 1, "h2": 2, "h3": 3, "audit": 2}[kind])) + " " + _md(value))
        elif kind == "p":
            out.append(_md(value) + (" " + " ".join("[%s]" % _md(cid) for cid in block[2]) if len(block) > 2 else ""))
        elif kind == "table":
            out.append("### " + _md(value["title"]))
            columns = _table_columns(value)
            lines = ["| " + " | ".join(_md(c) for c in columns) + " |",
                     "| " + " | ".join("---" for c in columns) + " |"]
            lines.extend("| " + " | ".join(_md(c) for c in row) + " |" for row in value["rows"])
            out.append("\n".join(lines))
            out.append(" ".join("[%s]" % _md(cid) for cid in value["claim_ids"]))
            if value.get("note"):
                out.append(_md(value["note"]))
        elif kind == "claim":
            out.append(_md(_claim_text(value)))
            out.append(_md("依据：" + ", ".join(value.get("basis", [])) + "；来源：" + ", ".join(s.get("source_id", s.get("url", "")) for s in value.get("sources", []))))
        elif kind == "source":
            out.append(_md(_source_text(value)))
            url = safe_link(value.get("url"))
            out.append(("[" + _md(value.get("url", "")) + "](" + url + ")") if url else _md(value.get("url", "")))
    return "\n\n".join(out) + "\n"


STYLE = """
:root{color-scheme:light;--page:#fff;--ink:#000;--sub:#52514e;--rule:#deded9;--accent:#225eaa;--plot:#fcfcfb;--series:#2a78d6;--grid:#e1e0d9}
:root[data-theme=dark]{color-scheme:dark;--page:#141414;--ink:#f0efec;--sub:#c3c2b7;--rule:#444;--accent:#8ab9ef;--plot:#1a1a19;--series:#3987e5;--grid:#2c2c2a}
@media(prefers-color-scheme:dark){:root:not([data-theme=light]){color-scheme:dark;--page:#141414;--ink:#f0efec;--sub:#c3c2b7;--rule:#444;--accent:#8ab9ef;--plot:#1a1a19;--series:#3987e5;--grid:#2c2c2a}}
*{box-sizing:border-box}body{margin:0;background:var(--page);color:var(--ink);font:17px/1.85 'PingFang SC',system-ui,sans-serif;overflow-wrap:anywhere}main{max-width:850px;padding:34px 28px 80px;margin:auto}header{padding:14px 5vw;border-bottom:1px solid var(--rule);display:flex;justify-content:space-between;align-items:center;gap:16px}button{font:inherit;color:inherit;background:transparent;border:1px solid var(--rule);padding:6px 12px;border-radius:5px;cursor:pointer}a{color:var(--accent);text-underline-offset:4px}h1{font-size:clamp(28px,4vw,42px);line-height:1.35;letter-spacing:-.025em}h2{font-size:23px;margin-top:36px;line-height:1.5}h3{font-size:19px}p{white-space:pre-wrap}a:focus-visible,button:focus-visible,summary:focus-visible,[tabindex]:focus-visible{outline:3px solid var(--accent);outline-offset:4px}.refs{font-size:13px;margin-left:8px}.table-wrap{overflow:auto}table{border-collapse:collapse;width:100%;font-size:14px;font-variant-numeric:tabular-nums}caption{text-align:left;font-weight:650;padding:14px 0}th,td{padding:12px;text-align:left;vertical-align:top;border-top:1px solid var(--rule);white-space:pre-wrap}details{margin:32px 0;border-top:1px solid var(--rule);padding-top:20px}summary{cursor:pointer;font-weight:650}.source,.claim{font-size:14px;padding:12px 0;border-bottom:1px solid var(--rule)}.chart{background:var(--plot);padding:14px}.chart svg{width:100%;height:auto;display:block}.chart text{fill:var(--sub);font:12px system-ui,sans-serif}.line{stroke:var(--series);stroke-width:2;fill:none;stroke-linejoin:round}.dot{fill:var(--series);stroke:var(--plot);stroke-width:2}.grid{stroke:var(--grid)}.skip{position:absolute;left:-10000px}.skip:focus{left:20px;top:10px;background:var(--page)}@media(max-width:600px){main{padding:18px 6vw 60px}body{font-size:16px}th,td{min-width:100px;padding:10px 6px}header{font-size:14px}}@media print{header,.skip{display:none}main{max-width:none;padding:0}body{color:#000;background:#fff}details>*{display:block}.chart{break-inside:avoid}}
"""
SCRIPT = """
document.getElementById('theme').addEventListener('click',()=>{const d=document.documentElement;const dark=d.dataset.theme?d.dataset.theme==='dark':matchMedia('(prefers-color-scheme:dark)').matches;d.dataset.theme=dark?'light':'dark'});
document.getElementById('print').addEventListener('click',()=>window.print());
document.querySelectorAll('.refs a').forEach(a=>a.addEventListener('click',()=>{const t=document.getElementById(a.getAttribute('href').slice(1));if(t)t.closest('details').open=true}));
document.querySelectorAll('[data-readout]').forEach(n=>{const show=()=>{document.getElementById('chart-readout').textContent=n.dataset.readout;const cross=document.getElementById('chart-crosshair');cross.setAttribute('x1',n.dataset.x);cross.setAttribute('x2',n.dataset.x);cross.setAttribute('visibility','visible')};n.addEventListener('focus',show);n.addEventListener('pointerenter',show);n.addEventListener('keydown',e=>{if(['ArrowLeft','ArrowRight'].includes(e.key)){const nodes=Array.from(document.querySelectorAll('[data-readout]'));const i=nodes.indexOf(n);nodes[Math.max(0,Math.min(nodes.length-1,i+(e.key==='ArrowRight'?1:-1)))].focus();e.preventDefault()}})});
"""


def _h(value):
    return html.escape(_str(value), quote=True)


def _refs(ids):
    return '<span class="refs">' + " ".join('<a href="#claim-%s">[%s]</a>' % (_h(cid), _h(cid)) for cid in ids) + "</span>"


def _chart_table(c):
    """Companion data table for one chart, generated from the same rows."""
    if "series" in c:
        labels = [row["label"] for row in c["series"][0]["rows"]]
        return {"title": c["title"],
                "columns": [c["x_label"]] + [series["name"] + "（" + c["unit"] + "）" for series in c["series"]],
                "rows": [[label] + [series["rows"][index]["value"] for series in c["series"]]
                         for index, label in enumerate(labels)],
                "claim_ids": c["claim_ids"], "note": c.get("note", "")}
    if c.get("kind") == "waterfall":
        rows = [[row["label"] + ("（合计）" if row.get("role") == "total" else "（变动）"), row["value"]]
                for row in c["rows"]]
    else:
        rows = [[row["label"], row["value"]] for row in c["rows"]]
    return {"title": c["title"], "columns": [c["x_label"], c["y_label"] + "（" + c["unit"] + "）"],
            "rows": rows, "claim_ids": c["claim_ids"], "note": c.get("note", "")}


def _chart_series(chart):
    """Return [(name or None, rows)]; single-series charts keep one unnamed series."""
    if "series" in chart:
        return [(item["name"], item["rows"]) for item in chart["series"]]
    return [(None, chart["rows"])]


def _chart(c):
    kind = c.get("kind", "line")
    if kind == "bar":
        return _bar_chart(c)
    if kind == "waterfall":
        return _waterfall_chart(c)
    series = _chart_series(c)
    if len(series) == 1 and series[0][0] is None:
        return _single_chart(c)
    return _multi_chart(c, series)


def _bar_chart(c):
    if "series" in c:
        return _grouped_bar_chart(c)
    rows = c["rows"]
    values = [row["value"] for row in rows]
    lo, hi = min(min(values), 0), max(max(values), 0)
    scale = max(abs(lo), abs(hi), 1)
    low, high = lo / scale, hi / scale

    def y(value):
        return 190 - ((value / scale - low) / (high - low) if high != low else .5) * 150

    slot = 620 / len(rows)
    out = ['<section class="chart"><h2>%s</h2><svg viewBox="0 0 720 250" role="group" aria-label="%s（柱状）">' % (
        _h(c["title"]), _h(c["title"]))]
    for value in (lo, 0, hi):
        out.append('<line class="grid" x1="60" x2="680" y1="%s" y2="%s"/><text x="2" y="%s">%s</text>' % (
            y(value), y(value), y(value) - 5, _h(value)))
    for index, row in enumerate(rows):
        left = 60 + index * slot + slot * 0.15
        width = slot * 0.7
        top = y(max(row["value"], 0))
        height = abs(y(row["value"]) - y(0))
        label = row["label"] + " " + str(row["value"]) + " " + c["unit"]
        out.append('<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" fill="var(--series)" opacity="0.85" '
                   'tabindex="0" role="img" aria-label="%s" aria-describedby="chart-readout"><title>%s</title></rect>' % (
                       left, top, width, height, _h(label), _h(label)))
    out.append('<text x="60" y="220">%s</text><text x="680" y="220" text-anchor="end">%s</text></svg>' % (
        _h(rows[0]["label"]), _h(rows[-1]["label"])))
    out.append('<p id="chart-readout" role="tooltip" aria-live="polite">%s</p></section>' % _h(
        c["x_label"] + " · " + c["y_label"] + "（" + c["unit"] + "）"))
    return "".join(out)


def _grouped_bar_chart(c):
    series = _chart_series(c)
    if c.get("bar_mode") == "stacked":
        return _stacked_bar_chart(c, series)
    labels = [row["label"] for row in series[0][1]]
    values = [row["value"] for _, rows in series for row in rows]
    lo, hi = min(min(values), 0), max(max(values), 0)
    scale = max(abs(lo), abs(hi), 1)
    low, high = lo / scale, hi / scale

    def y(value):
        return 190 - ((value / scale - low) / (high - low) if high != low else .5) * 150

    group = 620 / len(labels)
    width = group / (len(series) + 1)
    out = ['<section class="chart"><h2>%s</h2><svg viewBox="0 0 720 250" role="group" aria-label="%s（分组柱状）">' % (
        _h(c["title"]), _h(c["title"]))]
    for value in (lo, 0, hi):
        out.append('<line class="grid" x1="60" x2="680" y1="%s" y2="%s"/><text x="2" y="%s">%s</text>' % (
            y(value), y(value), y(value) - 5, _h(value)))
    for series_index, (name, rows) in enumerate(series):
        opacity = max(0.35, 0.9 - series_index * 0.25)
        for index, row in enumerate(rows):
            left = 60 + index * group + (series_index + 0.5) * width
            top = y(max(row["value"], 0))
            height = abs(y(row["value"]) - y(0))
            label = name + " · " + row["label"] + " " + str(row["value"]) + " " + c["unit"]
            out.append('<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" fill="var(--series)" opacity="%s" '
                       'tabindex="0" role="img" aria-label="%s" aria-describedby="chart-readout"><title>%s</title></rect>' % (
                           left, top, width * 0.9, height, opacity, _h(label), _h(label)))
    out.append('<text x="60" y="220">%s</text><text x="680" y="220" text-anchor="end">%s</text></svg>' % (
        _h(labels[0]), _h(labels[-1])))
    out.append('<p style="font-size:13px">系列顺序（同组从左到右，色调由深到浅）：%s。精确数值见下方同源数据表。</p>' % _h(
        "、".join(name for name, _ in series)))
    out.append('<p id="chart-readout" role="tooltip" aria-live="polite">%s</p></section>' % _h(
        c["x_label"] + " · " + c["y_label"] + "（" + c["unit"] + "）"))
    return "".join(out)


def _stacked_bar_chart(c, series):
    labels = [row["label"] for row in series[0][1]]
    totals = [sum(rows[index]["value"] for _, rows in series) for index in range(len(labels))]
    hi = max(totals + [1])
    scale = max(abs(hi), 1)

    def y(value):
        return 190 - (value / scale) * 150

    slot = 620 / len(labels)
    out = ['<section class="chart"><h2>%s</h2><svg viewBox="0 0 720 250" role="group" aria-label="%s（堆叠柱状）">' % (
        _h(c["title"]), _h(c["title"]))]
    for value in (0, hi):
        out.append('<line class="grid" x1="60" x2="680" y1="%s" y2="%s"/><text x="2" y="%s">%s</text>' % (
            y(value), y(value), y(value) - 5, _h(value)))
    for index, label in enumerate(labels):
        left = 60 + index * slot + slot * 0.2
        width = slot * 0.6
        base = 0.0
        for series_index, (name, rows) in enumerate(series):
            value = rows[index]["value"]
            top = y(base + value)
            height = y(base) - y(base + value)
            opacity = max(0.35, 0.9 - series_index * 0.25)
            cell = "%s · %s %s %s" % (name, label, value, c["unit"])
            out.append('<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" fill="var(--series)" opacity="%s" '
                       'tabindex="0" role="img" aria-label="%s" aria-describedby="chart-readout"><title>%s</title></rect>' % (
                           left, top, width, height, opacity, _h(cell), _h(cell)))
            base += value
    out.append('<text x="60" y="220">%s</text><text x="680" y="220" text-anchor="end">%s</text></svg>' % (
        _h(labels[0]), _h(labels[-1])))
    out.append('<p style="font-size:13px">堆叠顺序（自下而上）：%s。精确数值见下方同源数据表。</p>' % _h(
        "、".join(name for name, _ in series)))
    out.append('<p id="chart-readout" role="tooltip" aria-live="polite">%s</p></section>' % _h(
        c["x_label"] + " · " + c["y_label"] + "（" + c["unit"] + "）"))
    return "".join(out)


def _waterfall_chart(c):
    rows = c["rows"]
    bars, running = [], None
    for row in rows:
        value = row["value"]
        if row.get("role") == "total":
            bars.append((0.0, value))
            running = value
        else:
            start = running if running is not None else 0.0
            end = start + value
            bars.append((start, end))
            running = end
    points = [0] + [point for bar in bars for point in bar]
    lo, hi = min(points), max(points)
    scale = max(abs(lo), abs(hi), 1)
    low, high = lo / scale, hi / scale

    def y(value):
        return 190 - ((value / scale - low) / (high - low) if high != low else .5) * 150

    slot = 620 / len(bars)
    out = ['<section class="chart"><h2>%s</h2><svg viewBox="0 0 720 250" role="group" aria-label="%s（瀑布）">' % (
        _h(c["title"]), _h(c["title"]))]
    for value in (lo, hi):
        out.append('<line class="grid" x1="60" x2="680" y1="%s" y2="%s"/><text x="2" y="%s">%s</text>' % (
            y(value), y(value), y(value) - 5, _h(value)))
    out.append('<line class="grid" x1="60" x2="680" y1="%s" y2="%s"/>' % (y(0), y(0)))
    previous = None
    for index, ((start, end), row) in enumerate(zip(bars, rows)):
        left = 60 + index * slot + slot * 0.2
        width = slot * 0.6
        top, height = y(max(start, end)), abs(y(end) - y(start))
        total = row.get("role") == "total"
        label = row["label"] + " " + str(row["value"]) + " " + c["unit"]
        out.append('<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" fill="var(--series)" opacity="%s"%s '
                   'tabindex="0" role="img" aria-label="%s" aria-describedby="chart-readout"><title>%s</title></rect>' % (
                       left, top, width, height, "0.9" if total else "0.5",
                       ' stroke="var(--series)" stroke-dasharray="3 2"' if not total else "",
                       _h(label), _h(label)))
        if previous is not None and float(start) != float(previous):
            out.append('<line x1="%.3f" x2="%.3f" y1="%.3f" y2="%.3f" stroke="var(--sub)" stroke-dasharray="2 3"/>' % (
                left - slot * 0.2, left, y(previous), y(previous)))
        previous = end
    out.append('<text x="60" y="220">%s</text><text x="680" y="220" text-anchor="end">%s</text></svg>' % (
        _h(rows[0]["label"]), _h(rows[-1]["label"])))
    out.append('<p id="chart-readout" role="tooltip" aria-live="polite">%s</p></section>' % _h(
        c["x_label"] + " · " + c["y_label"] + "（" + c["unit"] + "）"))
    return "".join(out)


def _multi_chart(c, series):
    labels = [row["label"] for row in series[0][1]]
    values = [row["value"] for _, rows in series for row in rows]
    lo, hi = min(values), max(values)
    scale = max(abs(lo), abs(hi), 1)
    low, high = lo / scale, hi / scale

    def x(i):
        return 60 + i / (len(labels) - 1) * 620

    def y(v):
        return 190 - ((v / scale - low) / (high - low) if high != low else .5) * 150

    out = ['<section class="chart"><h2>%s</h2><svg viewBox="0 0 720 250" role="group" aria-label="%s（%d个序列）">' % (_h(c["title"]), _h(c["title"]), len(series))]
    for v in (lo, hi):
        out.append('<line class="grid" x1="60" x2="680" y1="%s" y2="%s"/><text x="2" y="%s">%s</text>' % (y(v), y(v), y(v) - 5, _h(v)))
    dashes = ("none", "6 4", "2 3", "10 3 2 3")
    for index, (name, rows) in enumerate(series):
        dash = dashes[index % len(dashes)]
        style = "" if dash == "none" else ' style="stroke-dasharray:%s"' % dash
        out.append('<polyline class="line" points="%s"%s/>' % (
            " ".join("%.3f,%.3f" % (x(i), y(row["value"])) for i, row in enumerate(rows)), style))
        for i, row in enumerate(rows):
            out.append('<circle class="dot" cx="%.3f" cy="%.3f" r="3" aria-hidden="true"/>' % (x(i), y(row["value"])))
    out.append('<text x="60" y="220">%s</text><text x="680" y="220" text-anchor="end">%s</text></svg>' % (
        _h(labels[0]), _h(labels[-1])))
    legend = "；".join("%s（%s）" % (name, "实线" if dashes[index % len(dashes)] == "none" else "虚线%d" % (index + 1))
                      for index, (name, _) in enumerate(series))
    out.append('<p style="font-size:13px">系列：%s。精确数值见下方同源数据表。</p>' % _h(legend))
    out.append('<p id="chart-readout" role="tooltip" aria-live="polite">%s</p></section>' % _h(
        c["x_label"] + " · " + c["y_label"] + "（" + c["unit"] + "）"))
    return "".join(out)


def _single_chart(c):
    rows = c["rows"]
    vals = [r["value"] for r in rows]
    lo, hi = min(vals), max(vals)
    # Scaling before subtraction avoids overflowing for finite extreme values.
    scale = max(abs(lo), abs(hi), 1)
    low, high = lo / scale, hi / scale
    def x(i):
        return 60 + i / (len(rows) - 1) * 620
    def y(v):
        return 190 - ((v / scale - low) / (high - low) if high != low else .5) * 150
    out = ['<section class="chart"><h2>%s</h2><svg viewBox="0 0 720 250" role="group" aria-label="%s">' % (_h(c["title"]), _h(c["title"]))]
    for v in (lo, hi):
        out.append('<line class="grid" x1="60" x2="680" y1="%s" y2="%s"/><text x="2" y="%s">%s</text>' % (y(v), y(v), y(v) - 5, _h(v)))
    out.append('<polyline class="line" points="%s"/>' % " ".join("%.3f,%.3f" % (x(i), y(r["value"])) for i, r in enumerate(rows)))
    out.append('<line id="chart-crosshair" x1="60" x2="60" y1="25" y2="195" stroke="var(--sub)" visibility="hidden" pointer-events="none"/>')
    for i, row in enumerate(rows):
        label = row["label"] + " " + str(row["value"]) + " " + c["unit"]
        out.append('<circle class="dot" cx="%.3f" cy="%.3f" r="5" aria-hidden="true"/>' % (x(i), y(row["value"])))
        out.append('<circle cx="%.3f" cy="%.3f" r="14" fill="transparent" tabindex="0" role="img" aria-label="%s" aria-describedby="chart-readout" data-x="%.3f" data-readout="%s"><title>%s</title></circle>' % (x(i), y(row["value"]), _h(label), x(i), _h(label), _h(label)))
    out.append('<text x="60" y="220">%s</text><text x="680" y="240" text-anchor="end">%s</text></svg><p id="chart-readout" role="tooltip" aria-live="polite">%s</p></section>' % (_h(rows[0]["label"]), _h(rows[-1]["label"]), _h(c["x_label"] + " · " + c["y_label"] + "（" + c["unit"] + "）")))
    return "".join(out)


def render_html(report, ledger, sources=None):
    """Return standalone escaped HTML; external strings never become script/markup."""
    _checked(report, ledger, sources)
    out = []
    audit = False
    for block in _blocks(report, ledger, sources):
        kind, value = block[:2]
        if kind in {"h1", "h2", "h3", "p"}:
            out.append('<%s>%s%s</%s>' % (kind, _h(value), _refs(block[2]) if len(block) > 2 else "", kind))
        elif kind == "audit":
            out.append('<details id="audit"><summary>%s</summary>' % _h(value))
            audit = True
        elif kind == "table":
            out.append('<div class="table-wrap"><table><caption>%s</caption><thead><tr>%s</tr></thead><tbody>' % (_h(value["title"]), "".join('<th scope="col">%s</th>' % _h(c) for c in _table_columns(value))))
            out.extend('<tr>%s</tr>' % "".join('<td>%s</td>' % _h(c) for c in row) for row in value["rows"])
            out.append('</tbody></table>%s<p>%s</p></div>' % (_refs(value["claim_ids"]), _h(value.get("note", ""))))
        elif kind == "chart":
            out.append(_chart(value))
        elif kind == "claim":
            out.append('<div class="claim" id="claim-%s"><p>%s</p><p>%s</p></div>' % (_h(value["id"]), _h(_claim_text(value)), _h("依据：" + ", ".join(value.get("basis", [])) + "；来源：" + ", ".join(s.get("source_id", s.get("url", "")) for s in value.get("sources", [])))))
        elif kind == "source":
            url = safe_link(value.get("url"))
            link = '<a href="%s" target="_blank" rel="noopener noreferrer">%s</a>' % (_h(url), _h(value.get("url"))) if url else _h(value.get("url", ""))
            out.append('<div class="source"><p>%s</p>%s</div>' % (_h(_source_text(value)), link))
    if audit:
        out.append("</details>")
    return '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>' + _h(report["title"]) + '</title><style>' + STYLE + '</style></head><body><a class="skip" href="#content">跳到研究正文</a><header><span>投研助手</span><span><button id="theme" type="button">切换明暗</button> <button id="print" type="button">打印</button></span></header><main id="content" tabindex="-1">' + "\n".join(out) + '</main><script>' + SCRIPT + '</script></body></html>\n'


def read_document(path):
    """Read only regular JSON inputs; reject symlinks and explicit traversal."""
    path = Path(path).expanduser()
    if ".." in path.parts:
        raise ValueError("input path traversal refused")
    absolute = path.absolute()
    if absolute.is_symlink() or absolute.parent.is_symlink():
        # Only the named file and its immediate directory are inspected; an
        # ancestor symlink such as macOS /var is a normal location.
        raise ValueError("symlink input refused: " + str(path))
    if not path.is_file():
        raise ValueError("input must be a regular file: " + str(path))
    try:
        with path.open(encoding="utf-8") as f:
            return json.load(f, parse_constant=lambda value: (_ for _ in ()).throw(ValueError("non-finite JSON: " + value)))
    except (OSError, ValueError) as exc:
        raise ValueError("cannot read " + str(path) + ": " + str(exc)) from exc


def write_outputs(directory, markdown, page, overwrite=False):
    """Validate destinations before creating files; refuse symlinks and replacement by default."""
    directory = Path(directory).expanduser().absolute()
    if ".." in directory.parts or directory.is_symlink():
        # The output directory itself must not be a link; a symlinked parent
        # (macOS /var, a linked home) is a normal location.
        raise ValueError("unsafe output directory")
    paths = [directory / "report.md", directory / "report.html"]
    for path in paths:
        if path.is_symlink() or (path.exists() and (not overwrite or not path.is_file())):
            raise ValueError("output already exists or unsafe: " + str(path))
    directory.mkdir(parents=True, exist_ok=True)
    for path, content in zip(paths, (markdown, page)):
        # Exclusive creation also handles concurrent writers without silent replacement.
        with path.open("w" if overwrite else "x", encoding="utf-8") as f:
            f.write(content)
    return paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument("--claims", required=True, type=Path)
    parser.add_argument("--sources", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    try:
        report, ledger, sources = [read_document(p) for p in (args.report, args.claims, args.sources)]
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    try:
        markdown = render_markdown(report, ledger, sources)
        page = render_html(report, ledger, sources)
        paths = write_outputs(args.out_dir, markdown, page, args.overwrite)
        print(json.dumps({"written": [str(p) for p in paths]}, ensure_ascii=False))
        return 0
    except (OSError, ValueError, TypeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
