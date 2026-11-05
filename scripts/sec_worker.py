#!/usr/bin/env python3
"""Isolated EdgarTools worker. Only this process imports optional dependencies."""
import contextlib
import hashlib
import json
import math
import os
import sys
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

# Helpers remain importable with stdlib for offline contract tests.
from sec_data import PINNED_VERSION, envelope, parse_as_of, utc_now, validate_request


class SchemaError(Exception):
    pass


def clean(value):
    """Normalize known tabular missing values, retaining zero, signs and precision."""
    if value is None or type(value).__name__ in {"NAType", "NaTType"}:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, (str, int)):
        return value
    if isinstance(value, Decimal):
        return str(value) if value.is_finite() else None
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    if hasattr(value, "item"):
        return clean(value.item())
    if hasattr(value, "model_dump"):
        return clean(value.model_dump())
    raise SchemaError("unsupported exported value type")


def table_data(frame):
    if frame is None or isinstance(frame, str) or not hasattr(frame, "to_dict"):
        raise SchemaError("expected a tabular statement")
    columns = list(frame.columns)
    records = clean(frame.to_dict(orient="records"))
    result = {"columns": columns, "rows": records, "row_count": len(records),
              "value_basis": "XBRL instance values; presentation=False; no unit rescaling or quarter derivation",
              "missing_value_policy": "non-finite tabular missing values become null, never zero"}
    result["sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, ensure_ascii=False,
                                                 allow_nan=False).encode()).hexdigest()
    result["hash_basis"] = "canonical normalized table JSON before sha256/hash_basis fields"
    return result


def acceptance_utc(value):
    """SGML header uses naive US Eastern time; do not trust submissions' UTC label."""
    if not isinstance(value, datetime):
        return None
    if value.tzinfo is not None:
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    eastern = ZoneInfo("America/New_York")
    first = value.replace(tzinfo=eastern, fold=0)
    second = value.replace(tzinfo=eastern, fold=1)
    # Ambiguous/nonexistent local times cannot establish a precise cutoff.
    if first.utcoffset() != second.utcoffset():
        return None
    if first.astimezone(timezone.utc).astimezone(eastern).replace(tzinfo=None) != value:
        return None
    return first.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def at_cutoff(metadata, as_of):
    if as_of is None:
        return True, None
    accepted = metadata.get("acceptance_datetime")
    if not accepted:
        return False, "acceptance_datetime_unknown"
    return (True, None) if parse_as_of(accepted) <= parse_as_of(as_of) else (False, "accepted_after_cutoff")


def filing_metadata(filing):
    header = filing.header
    accepted_raw = getattr(header, "acceptance_datetime", None)
    accepted = acceptance_utc(accepted_raw)
    # The line is explicitly the parser-normalized SGML header, not a raw HTML quote.
    header_lines = getattr(header, "text", "").splitlines()
    acceptance_line = next((line for line in header_lines if "ACCEPTANCE-DATETIME" in line), None)
    primary = filing.document
    accession = filing.accession_no
    cik = str(filing.cik)
    metadata = {"company": filing.company, "cik": cik, "accession_number": accession,
                "form": filing.form, "filing_date": str(filing.filing_date),
                "period_of_report": str(filing.period_of_report) if filing.period_of_report else None,
                "acceptance_datetime": accepted, "acceptance_raw_eastern": str(accepted_raw) if accepted_raw else None,
                "acceptance_basis": "filing SGML header; America/New_York converted to UTC",
                "acceptance_header_line": acceptance_line, "acceptance_header_line_is_normalized": True,
                "sec_index_url": filing.url, "sec_submission_url": filing.text_url,
                "primary_document": getattr(primary, "document", None),
                "primary_document_url": getattr(primary, "url", None),
                "amendment": filing.form.endswith("/A"), "origin_id": "sec:" + accession}
    attachments = getattr(filing, "attachments", None)
    metadata["attachments"] = [
        {"document": doc.document, "document_type": doc.document_type, "url": doc.url,
         "description": doc.description}
        for doc in getattr(attachments, "documents", []) if doc is not None
    ]
    if primary is not None:
        content = primary.content
        if isinstance(content, str):
            raw = content.encode("utf-8")
            basis = "EdgarTools primary attachment decoded content, re-encoded UTF-8"
        elif isinstance(content, bytes):
            raw, basis = content, "primary attachment bytes"
        else:
            raw, basis = None, None
        metadata["primary_content_sha256"] = hashlib.sha256(raw).hexdigest() if raw is not None else None
        metadata["primary_content_hash_basis"] = basis
    return metadata


SECTION_ITEMS = {
    "10-K": {"mda": "Item 7", "risk_factors": "Item 1A", "business": "Item 1"},
    "10-Q": {"mda": "Part I, Item 2", "risk_factors": "Part II, Item 1A"},
    "20-F": {"mda": "Item 5", "risk_factors": "Item 3", "business": "Item 4"},
}


def read_document(filing, request, result):
    attachment_name = request.get("attachment")
    if attachment_name:
        attachment = filing.attachments[attachment_name]
        text = attachment.text()
        url, locator = attachment.url, "attachment:" + attachment_name
        source = {"document": attachment.document, "type": attachment.document_type, "url": url}
    elif request.get("item") or request["section"] != "full_text":
        item = request.get("item") or SECTION_ITEMS.get(filing.form.replace("/A", ""), {}).get(request["section"])
        if not item:
            result.update(status="no_results", reason="This form has no mapping for the requested section; use an explicit item or full_text.")
            return
        report = filing.obj()
        if report is None:
            result.update(status="no_results", reason="Filing has no typed section parser; use full_text.")
            return
        text = report[item]
        url, locator = result["provenance"]["primary_document_url"], item
        source = None
    else:
        text = filing.text()
        url, locator = result["provenance"]["primary_document_url"], "primary document full text"
        source = None
    if not isinstance(text, str) or not text.strip():
        result.update(status="no_results", reason="Requested text is empty or unavailable; this is not proof of absence of the underlying information.")
        return
    truncated = text.rstrip().endswith("... (truncated)")
    result.update(status="partial" if truncated else "ok",
                  data={"text": text, "characters": len(text), "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                        "hash_basis": "exact returned text encoded as UTF-8", "source_url": url,
                        "locator": locator, "attachment": source},
                  completeness={"truncated": truncated, "scope": "requested parser text; not all filing attachments"})
    if not result["provenance"].get("acceptance_datetime"):
        result["notes"].append("Acceptance timestamp unavailable; historical availability remains unverified.")


def read_statements(filing, request, result):
    report = filing.obj()
    xbrl = filing.xbrl()
    if report is None or xbrl is None:
        result.update(status="no_results", reason="No structured XBRL statements for this filing; read the document instead.")
        return
    mapping = {"income": "income_statement", "balance": "balance_sheet", "cashflow": "cash_flow_statement"}
    names = list(mapping) if request["statement"] == "all" else [request["statement"]]
    tables, errors = {}, []
    for name in names:
        try:
            statement = getattr(report, mapping[name], None)
            if statement is None:
                errors.append({"statement": name, "status": "no_results"})
                continue
            frame = statement.to_dataframe(standard=False, presentation=False, include_unit=True, include_point_in_time=True)
            table = table_data(frame)
            if not table["rows"]:
                errors.append({"statement": name, "status": "no_results"})
            else:
                tables[name] = table
        except Exception as exc:
            status = classify_error(exc)
            if status in {"rate_limited", "auth_failed", "unreachable", "timeout"}:
                raise
            errors.append({"statement": name, "status": status, "reason": type(exc).__name__})
    numeric_facts = []
    facts_scope = "all numeric facts in this filing instance; text blocks excluded"
    try:
        # Instance facts retain original contexts, units, decimals, dimensions and raw value strings.
        for fact in xbrl.facts.get_facts():
            numeric = clean(fact.get("numeric_value"))
            if numeric is not None:
                numeric_facts.append(clean(fact))
        if not numeric_facts:
            errors.append({"section": "numeric_facts", "status": "no_results"})
    except Exception as exc:
        if classify_error(exc) in {"rate_limited", "auth_failed", "unreachable", "timeout"}:
            raise
        errors.append({"section": "numeric_facts", "status": classify_error(exc), "reason": type(exc).__name__})
    result.update(status="partial" if errors and tables else "ok" if tables else "no_results",
                  data={"statements": tables, "numeric_facts": numeric_facts, "facts_scope": facts_scope,
                        "units": clean(xbrl.units), "reporting_periods": clean(xbrl.reporting_periods),
                        "derivations": [], "errors": errors},
                  completeness={"truncated": False, "scope": "requested statements and numeric instance facts",
                                "requested_statements": names, "returned_statements": list(tables)})
    if errors and not tables and any(e["status"] not in {"no_results"} for e in errors):
        result["status"] = "error"


def list_filings(company, request, result):
    filings = company.get_filings(form=request["form"], amendments=True)
    total = len(filings) if filings is not None else 0
    records, excluded, unknown = [], [], []
    scanned = 0
    for index in range(min(total, request["scan_limit"])):
        metadata = filing_metadata(filings[index])
        scanned += 1
        allowed, reason = at_cutoff(metadata, request.get("as_of"))
        if allowed:
            records.append(metadata)
        elif reason == "acceptance_datetime_unknown":
            unknown.append(metadata["accession_number"])
        else:
            excluded.append(metadata["accession_number"])
        # Continue to the scan bound for historical queries: order need not be acceptance order.
        if not request.get("as_of") and len(records) >= request["limit"]:
            break
    records.sort(key=lambda row: (row.get("acceptance_datetime") or "", row["filing_date"]), reverse=True)
    selected = records[:request["limit"]]
    incomplete = (bool(unknown) or (scanned < total and len(selected) < request["limit"])
                  or (bool(request.get("as_of")) and scanned < total))
    result.update(status="partial" if incomplete else "ok" if selected else "no_results",
                  data={"company": company.name, "cik": str(company.cik), "filings": selected,
                        "excluded_after_cutoff": excluded, "unknown_acceptance": unknown},
                  provenance={"sec_submissions_url": "https://data.sec.gov/submissions/CIK%010d.json" % int(company.cik)},
                  completeness={"truncated": scanned < total or len(records) > request["limit"],
                                "scope": "bounded filing search; not complete SEC history",
                                "available_count": total, "scanned_count": scanned,
                                "returned_count": len(selected), "scan_limit": request["scan_limit"]})


def classify_error(exc):
    response = getattr(exc, "response", None)
    code = getattr(response, "status_code", None) or getattr(exc, "status_code", None)
    if code in (401, 403):
        return "auth_failed"
    if code == 429 or "TooManyRequests" in type(exc).__name__:
        return "rate_limited"
    if code == 402:
        return "payment_required"
    name = type(exc).__name__.lower()
    if "timeout" in name:
        return "timeout"
    if any(part in name for part in ("connect", "network", "unreachable")):
        return "unreachable"
    if isinstance(exc, (ImportError, ModuleNotFoundError)):
        return "not_run"
    if isinstance(exc, SchemaError):
        return "schema_drift"
    return "error"


def execute(request, provider=None):
    public_request = {k: v for k, v in request.items() if k not in {"runtime", "home", "expected_version"}}
    validate_request(public_request)
    result = envelope(public_request)
    if request["operation"] != "doctor" and not os.environ.get("EDGAR_IDENTITY", "").strip():
        result["reason"] = "EDGAR_IDENTITY is not configured; no SEC request sent."
        return result
    try:
        if provider is None:
            if sys.version_info < (3, 11):
                result["reason"] = "EdgarTools requires an independent Python 3.11+."
                return result
            packages = request.get("runtime", {}).get("site_packages")
            if packages:
                sys.path.insert(0, packages)
            home = Path(request["home"])
            os.environ["EDGAR_LOCAL_DATA_DIR"] = str(home / "data/sec-cache/data")
            os.environ["EDGAR_CACHE_DIR"] = str(home / "data/sec-cache/cache")
            import edgar as provider
        version = getattr(provider, "__version__", None)
        if version is None:
            from edgar.__about__ import __version__
            version = __version__
        result["library_version"] = version
        if version != request.get("expected_version", PINNED_VERSION):
            result.update(status="schema_drift", reason="EdgarTools version differs from the validated pinned runtime.")
            return result
        if request["operation"] == "doctor":
            result.update(status="ok", data={"python": sys.version.split()[0], "edgartools_version": version,
                                             "identity_configured": bool(os.environ.get("EDGAR_IDENTITY", "").strip()),
                                             "sec_network_requested": False})
            return result
        provider.set_identity(os.environ["EDGAR_IDENTITY"])
        if request["operation"] == "filings":
            identifier = request["identifier"]
            company = provider.Company(int(identifier) if identifier.isdigit() else identifier)
            list_filings(company, request, result)
        else:
            filing = provider.find(request["accession"])
            if filing is None:
                result.update(status="no_results", reason="SEC filing was not found.")
                return result
            metadata = filing_metadata(filing)
            if metadata["accession_number"] != request["accession"]:
                raise SchemaError("resolved accession mismatch")
            result["provenance"] = metadata
            allowed, reason = at_cutoff(metadata, request.get("as_of"))
            if not allowed:
                result.update(status="partial" if reason == "acceptance_datetime_unknown" else "no_results",
                              reason=reason, completeness={"truncated": False, "availability_verified": False,
                                                         "excluded_by_as_of": True})
                return result
            if request["operation"] == "document":
                read_document(filing, request, result)
            else:
                read_statements(filing, request, result)
    except Exception as exc:
        result.update(status=classify_error(exc), data=None,
                      reason="SEC retrieval failed (%s); inspect runtime/connectivity or filing coverage. No automatic retry." % type(exc).__name__)
    result["retrieved_at"] = utc_now()
    return result


def main():
    request = json.load(sys.stdin)
    # Keep provider progress/log prints out of the JSON protocol.
    with contextlib.redirect_stdout(sys.stderr):
        result = execute(request)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
