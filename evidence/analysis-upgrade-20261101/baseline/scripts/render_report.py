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
    if report.get("findings") == [] and not _text(report.get("no_change_reason")):
        errors.append("empty findings requires no_change_reason")
    chart = report.get("chart")
    if chart is not None:
        if not isinstance(chart, dict):
            errors.append("chart must be an object")
        else:
            for key in ("title", "x_label", "y_label", "unit"):
                if not _text(chart.get(key)):
                    errors.append("chart." + key + " must be nonempty text")
            rows = chart.get("rows")
            if not isinstance(rows, list) or len(rows) < 2 or any(not isinstance(row, dict) or not _text(row.get("label")) or not _number(row.get("value")) for row in rows):
                errors.append("chart.rows requires at least two label/finite numeric value pairs")
            refs(chart, "chart")
            if "note" in chart and not isinstance(chart["note"], str):
                errors.append("chart.note must be text")
    if any(isinstance(c, dict) and not _text(c.get("text")) for c in claims):
        errors.append("claim text must be nonempty")
    calculations = report.get("calculations", [])
    errors.extend(validate_calculation_rows(calculations, ids))
    calculation_ids = {row.get("id") for row in calculations if isinstance(row, dict) and isinstance(row.get("id"), str)} if isinstance(calculations, list) else set()
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
    return errors


def validate_calculation_rows(rows, claim_ids):
    """Check transparent formula/input/result records; never evaluate formula text.

    Arithmetic correctness needs external review. This validates only finite values,
    units and resolvable evidence links, and does not claim recomputation.
    """
    if not isinstance(rows, list):
        return ["calculations must be a list"]
    errors, seen = [], set()
    for n, row in enumerate(rows):
        path = "calculations[%d]" % n
        if not isinstance(row, dict):
            errors.append(path + " must be an object")
            continue
        cid = row.get("id")
        if not isinstance(cid, str) or not ID.fullmatch(cid) or cid in seen:
            errors.append(path + ".id must be a unique safe identifier")
        else:
            seen.add(cid)
        for field in ("description", "formula"):
            if not _text(row.get(field)):
                errors.append(path + "." + field + " must be nonempty text")
        def refs(item, location):
            refs = item.get("claim_ids")
            if not isinstance(refs, list) or not refs or any(not isinstance(c, str) or c not in claim_ids for c in refs):
                errors.append(location + ".claim_ids must resolve")
        refs(row, path)
        inputs = row.get("inputs")
        if not isinstance(inputs, list) or not inputs:
            errors.append(path + ".inputs must be nonempty list")
        else:
            for i, item in enumerate(inputs):
                location = path + ".inputs[%d]" % i
                if not isinstance(item, dict) or not _text(item.get("name")) or not _text(item.get("unit")) or not _number(item.get("value")):
                    errors.append(location + " requires name, finite value and unit")
                else:
                    refs(item, location)
        result = row.get("result")
        if not isinstance(result, dict) or not _number(result.get("value")) or not _text(result.get("unit")):
            errors.append(path + ".result requires finite value and unit")
    return errors


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
    for limit in report["limitations"]:
        if limit["material"]:
            yield ("p", "重要限制：" + limit["text"], limit["claim_ids"])
    if report.get("no_change_reason"):
        yield ("p", report["no_change_reason"])
    for finding in report["findings"]:
        yield ("h2", finding["title"])
        yield ("p", finding["text"], finding["claim_ids"])
        yield ("p", "为什么重要：" + finding["why_it_matters"])
        yield ("p", "相较基线：" + finding["increment"]["baseline"])
        yield ("p", "研究增量（" + finding["increment"]["kind"] + "）：" + finding["increment"]["detail"])
    for calculation in report.get("calculations", []):
        yield ("h2", calculation["description"])
        yield ("p", "计算式：" + calculation["formula"], calculation["claim_ids"])
        yield ("table", {"title": calculation["id"] + " 输入", "columns": ["名称", "数值", "单位"],
                         "rows": [[v["name"], v["value"], v["unit"]] for v in calculation["inputs"]],
                         "claim_ids": [cid for v in calculation["inputs"] for cid in v["claim_ids"]]})
        yield ("p", "结果：" + str(calculation["result"]["value"]) + " " + calculation["result"]["unit"])
    for table in report["tables"]:
        yield ("table", table)
    if report.get("chart"):
        c = report["chart"]
        yield ("chart", c)
        yield ("table", {"title": c["title"], "columns": [c["x_label"], c["y_label"] + "（" + c["unit"] + "）"],
                         "rows": [[r["label"], r["value"]] for r in c["rows"]], "claim_ids": c["claim_ids"], "note": c.get("note", "")})
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
    yield ("audit", "来源与结论审计")
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
            lines = ["| " + " | ".join(_md(c) for c in value["columns"]) + " |",
                     "| " + " | ".join("---" for c in value["columns"]) + " |"]
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


def _chart(c):
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
            out.append('<div class="table-wrap"><table><caption>%s</caption><thead><tr>%s</tr></thead><tbody>' % (_h(value["title"]), "".join('<th scope="col">%s</th>' % _h(c) for c in value["columns"])))
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
    if any(p.is_symlink() for p in [absolute] + list(absolute.parents)):
        raise ValueError("symlink input refused: " + str(path))
    if not path.is_file():
        raise ValueError("input must be a regular file: " + str(path))
    with path.open(encoding="utf-8") as f:
        return json.load(f, parse_constant=lambda value: (_ for _ in ()).throw(ValueError("non-finite JSON: " + value)))


def write_outputs(directory, markdown, page, overwrite=False):
    """Validate destinations before creating files; refuse symlinks and replacement by default."""
    directory = Path(directory).expanduser().absolute()
    if ".." in directory.parts or any(p.is_symlink() for p in [directory] + list(directory.parents)):
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
