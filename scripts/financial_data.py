#!/usr/bin/env python3
"""Read-only Financial Datasets adapter using Dexter's public endpoint contracts.

Independent stdlib implementation, not Dexter's TypeScript/LangChain runtime.
Never pays x402 challenges, follows redirects, or promotes API data to T0 evidence.
"""
import argparse
import hashlib
import json
import math
import os
import re
import socket
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

BASE_URL = "https://api.financialdatasets.ai"
ENDPOINTS = {
    "income": ("/financials/income-statements/", "income_statements"),
    "balance": ("/financials/balance-sheets/", "balance_sheets"),
    "cashflow": ("/financials/cash-flow-statements/", "cash_flow_statements"),
    "financials": ("/financials/", "financials"),
    "snapshot": ("/prices/snapshot/", "snapshot"),
}
MAX_RESPONSE_BYTES = 10 * 1024 * 1024


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def request_params(operation, ticker, period="annual", limit=4,
                   report_period_gte=None, report_period_lte=None):
    if operation not in ENDPOINTS:
        raise ValueError("unsupported operation")
    ticker = ticker.strip().upper()
    if not re.fullmatch(r"[A-Z0-9][A-Z0-9.^=-]{0,24}", ticker):
        raise ValueError("invalid ticker")
    if period not in {"annual", "quarterly", "ttm"}:
        raise ValueError("invalid reporting period")
    if type(limit) is not int or not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100")
    for value in (report_period_gte, report_period_lte):
        if value is not None:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                raise ValueError("report dates require YYYY-MM-DD")
            date.fromisoformat(value)
    if report_period_gte and report_period_lte and report_period_gte > report_period_lte:
        raise ValueError("report date range is reversed")
    params = {"ticker": ticker}
    if operation == "snapshot":
        if report_period_gte or report_period_lte:
            raise ValueError("snapshot does not support report period filters")
    else:
        params.update(period=period, limit=limit)
        if report_period_gte:
            params["report_period_gte"] = report_period_gte
        if report_period_lte:
            params["report_period_lte"] = report_period_lte
    return params


def fetch_data(operation, ticker, *, period="annual", limit=4,
               report_period_gte=None, report_period_lte=None,
               public_probe=False, timeout=20, opener=None):
    params = request_params(operation, ticker, period, limit,
                            report_period_gte, report_period_lte)
    if not math.isfinite(timeout) or not 0 < timeout <= 120:
        raise ValueError("timeout must be finite and between 0 and 120 seconds")
    endpoint, field = ENDPOINTS[operation]
    url = BASE_URL + endpoint + "?" + urlencode(params)
    result = {
        "schema_version": 1,
        "provider": "financial_datasets",
        "contract_reference": "https://github.com/virattt/dexter/tree/main/src/tools/finance",
        "operation": operation,
        "params": params,
        "source_url": url,
        "retrieved_at": utc_now(),
        "status": "not_run",
        "http_status": None,
        "data": None,
        "raw_response": None,
        "notes": ["Provider data requires provenance and accounting-period review before research use.",
                  "Retrieval time and report period do not establish historical public availability."],
    }
    # Probe is explicitly unauthenticated even if the environment has a key.
    key = "" if public_probe else os.environ.get("FINANCIAL_DATASETS_API_KEY", "")
    result["access_mode"] = "public_probe" if public_probe else "api_key" if key else "unconfigured"
    if not key and not public_probe:
        result["reason"] = "FINANCIAL_DATASETS_API_KEY is not configured; no request sent."
        return result
    headers = {"Accept": "application/json", "User-Agent": "Touyan-Research/financial-data"}
    if key:
        headers["X-API-KEY"] = key
    request = Request(url, headers=headers, method="GET")
    client = opener or build_opener(NoRedirect())
    try:
        with client.open(request, timeout=timeout) as response:
            result["http_status"] = response.status
            raw = response.read(MAX_RESPONSE_BYTES + 1)
        if len(raw) > MAX_RESPONSE_BYTES:
            result.update(status="error", reason="Response exceeds size limit; not parsed.")
            return result
        result["response_sha256"] = hashlib.sha256(raw).hexdigest()
        try:
            payload = json.loads(raw)
            # Python accepts NaN/Infinity and overflowing exponents; the evidence JSON must not.
            json.dumps(payload, allow_nan=False)
        except (ValueError, UnicodeError):
            result.update(status="schema_drift", reason="Response is not valid JSON.")
            return result
        result["raw_response"] = payload
        if not isinstance(payload, dict) or "error" in payload or field not in payload:
            result.update(status="schema_drift", reason="Expected success field is missing or API returned an error.")
            return result
        data = payload[field]
        if operation in {"income", "balance", "cashflow"}:
            valid = isinstance(data, list) and all(isinstance(row, dict) and row for row in data)
        elif operation == "snapshot":
            valid = isinstance(data, dict) and bool(data)
        else:
            valid = isinstance(data, dict) and all(
                isinstance(data.get(name), list) and all(isinstance(row, dict) and row for row in data[name])
                for name in ("income_statements", "balance_sheets", "cash_flow_statements"))
        if not valid:
            result.update(status="schema_drift", reason="Unexpected data shape; no normalized data returned.")
            return result
        result["data"] = data  # Preserve currency, period, accession number and other provider fields.
        empty = not data or operation == "financials" and not any(data.values())
        if payload.get("next_page_url"):
            result.update(status="partial", reason="Provider has another page; this adapter preserves only the first page.")
        else:
            result["status"] = "no_results" if empty else "ok"
    except HTTPError as error:
        result["http_status"] = error.code
        result["status"] = {401: "auth_failed", 403: "auth_failed", 402: "payment_required",
                            429: "rate_limited"}.get(error.code, "error")
        result["reason"] = "Provider HTTP %s; no automatic retry, redirect or payment performed." % error.code
        error.close()
    except (TimeoutError, socket.timeout):
        result.update(status="timeout", reason="Provider request timed out.")
    except URLError as error:
        result.update(status="timeout" if isinstance(error.reason, (TimeoutError, socket.timeout)) else "unreachable",
                      reason="Provider connection failed; inspect connectivity separately.")
    except OSError:
        result.update(status="unreachable", reason="Provider connection or response read failed.")
    result["retrieved_at"] = utc_now()
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=sorted(ENDPOINTS))
    parser.add_argument("ticker")
    parser.add_argument("--period", choices=["annual", "quarterly", "ttm"], default="annual")
    parser.add_argument("--limit", type=int, default=4)
    parser.add_argument("--report-period-gte")
    parser.add_argument("--report-period-lte")
    parser.add_argument("--public-probe", action="store_true", help="Explicitly attempt an unauthenticated GET; never pays.")
    parser.add_argument("--timeout", type=float, default=20)
    parser.add_argument("--out", type=Path, help="Save to a new JSON file; refuses overwrite.")
    args = parser.parse_args(argv)
    try:
        result = fetch_data(args.operation, args.ticker, period=args.period, limit=args.limit,
                            report_period_gte=args.report_period_gte, report_period_lte=args.report_period_lte,
                            public_probe=args.public_probe, timeout=args.timeout)
    except ValueError as error:
        parser.error(str(error))
    text = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("x", encoding="utf-8") as handle:
            handle.write(text)
    sys.stdout.write(text)
    return 0 if result["status"] in {"ok", "no_results"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
