#!/usr/bin/env python3
"""SEC research retrieval entry point (stdlib, Python 3.9+).

EdgarTools runs in a separate Python 3.11+ process. Identity comes only from
EDGAR_IDENTITY; the runtime config contains interpreter/package paths only.
"""
import argparse
import json
import math
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PINNED_VERSION = "5.62.1"
STATUSES = {"ok", "partial", "no_results", "not_run", "error", "rate_limited",
            "auth_failed", "payment_required", "unreachable", "timeout", "schema_drift"}


def utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_as_of(value):
    if value is None:
        return None
    if not isinstance(value, str) or not re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})", value):
        raise ValueError("as-of requires an ISO timestamp with time and timezone")
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def validate_request(request):
    operation = request.get("operation")
    if operation not in {"doctor", "filings", "document", "statements"}:
        raise ValueError("unsupported SEC operation")
    parse_as_of(request.get("as_of"))
    if operation == "filings":
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.\- ]{0,79}", request.get("identifier", "")):
            raise ValueError("identifier must be a ticker, CIK, or company name")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 /\-]{0,24}", request.get("form", "")):
            raise ValueError("invalid SEC form")
        for key, maximum in (("limit", 20), ("scan_limit", 100)):
            if type(request.get(key)) is not int or not 1 <= request[key] <= maximum:
                raise ValueError("%s must be between 1 and %s" % (key, maximum))
        if request["scan_limit"] < request["limit"]:
            raise ValueError("scan-limit must be at least limit")
    if operation in {"document", "statements"}:
        if not re.fullmatch(r"\d{10}-\d{2}-\d{6}", request.get("accession", "")):
            raise ValueError("accession requires the exact dashed SEC file number")
    if operation == "document":
        if request.get("section") not in {"full_text", "mda", "risk_factors", "business"}:
            raise ValueError("unsupported section")
        if request.get("item") and (request["section"] != "full_text" or request.get("attachment")):
            raise ValueError("item cannot be combined with a named section or attachment")
        if request.get("item") and (len(request["item"]) > 120 or any(ord(c) < 32 for c in request["item"])):
            raise ValueError("invalid item name")
        attachment = request.get("attachment")
        if attachment and (request["section"] != "full_text" or not re.fullmatch(r"[A-Za-z0-9_.\-]{1,180}", attachment)):
            raise ValueError("attachment requires an exact filename and no named section")
    if operation == "statements" and request.get("statement") not in {"all", "income", "balance", "cashflow"}:
        raise ValueError("unsupported statement")
    return request


def envelope(request):
    return {"schema_version": 1, "provider": "edgartools", "adapter_version": 1,
            "operation": request["operation"], "params": dict(request), "retrieved_at": utc_now(),
            "status": "not_run", "data": None, "provenance": None,
            "completeness": {"truncated": False},
            "notes": ["Retrieval package, not sources/claims or independent corroboration.",
                      "Report period is not public availability; retain exact accession and original periods."]}


def load_runtime(home):
    path = Path(home) / "data/sec-runtime.json"
    if not path.is_file():
        return None
    config = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(config, dict) or set(config) - {"schema_version", "python", "site_packages"}:
        raise ValueError("SEC runtime config may contain only schema_version/python/site_packages")
    if config.get("schema_version") != 1 or not isinstance(config.get("python"), str):
        raise ValueError("invalid SEC runtime config")
    executable = Path(config["python"]).expanduser()
    if not executable.is_absolute() or not executable.is_file():
        raise ValueError("SEC runtime python must name an existing absolute interpreter path")
    packages = config.get("site_packages")
    if packages is not None and (not isinstance(packages, str) or not Path(packages).is_absolute()
                                 or not Path(packages).is_dir()):
        raise ValueError("SEC site_packages must name an existing absolute directory")
    return {"python": str(executable), "site_packages": packages}


def fetch_data(request, *, home=None, timeout=120, runner=None):
    validate_request(request)
    if not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or not 0 < timeout <= 600:
        raise ValueError("timeout must be finite and between 0 and 600 seconds")
    home = Path(home or os.environ.get("TOUYAN_HOME", Path.home() / "Desktop/投研助手")).expanduser().resolve()
    result = envelope(request)
    try:
        runtime = load_runtime(home)
    except (OSError, ValueError) as exc:
        result["reason"] = "SEC runtime configuration is invalid: " + str(exc)
        return result
    if runtime is None:
        result["reason"] = "Configure the independent runtime in TOUYAN_HOME/data/sec-runtime.json."
        return result
    if request["operation"] != "doctor" and not os.environ.get("EDGAR_IDENTITY", "").strip():
        result["reason"] = "EDGAR_IDENTITY is not configured; no SEC request sent."
        return result
    worker_request = dict(request, runtime=runtime, home=str(home), expected_version=PINNED_VERSION)
    command = [runtime["python"], str(Path(__file__).with_name("sec_worker.py"))]
    try:
        completed = (runner or subprocess.run)(command, input=json.dumps(worker_request),
            capture_output=True, text=True, timeout=timeout, env=os.environ.copy())
        if completed.returncode != 0:
            raise ValueError("SEC worker exited unsuccessfully")
        payload = json.loads(completed.stdout)
        json.dumps(payload, allow_nan=False)
        if (not isinstance(payload, dict) or payload.get("provider") != "edgartools"
                or payload.get("operation") != request["operation"] or payload.get("status") not in STATUSES):
            raise ValueError("invalid worker response")
        # Never expose process stderr or identities in the public package.
        identity = os.environ.get("EDGAR_IDENTITY", "").strip()
        if identity:
            serialized = json.dumps(payload, ensure_ascii=False)
            if identity in serialized:
                raise ValueError("worker response contained contact identity")
        return payload
    except subprocess.TimeoutExpired:
        result.update(status="timeout", reason="SEC retrieval process timed out and was stopped; no automatic retry.")
    except (ValueError, UnicodeError):
        result.update(status="schema_drift", reason="SEC worker did not return a valid finite retrieval package.")
    except OSError:
        result.update(status="not_run", reason="SEC runtime could not be started; run doctor and check interpreter dependencies.")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="operation", required=True)
    for name in ("doctor", "filings", "document", "statements"):
        child = commands.add_parser(name)
        child.add_argument("--out", type=Path, help="New JSON file; refuses overwrite before retrieval")
        child.add_argument("--timeout", type=float, default=120)
        if name != "doctor":
            child.add_argument("--as-of", dest="as_of")
        if name == "filings":
            child.add_argument("identifier")
            child.add_argument("--form", default="10-Q")
            child.add_argument("--limit", type=int, default=5)
            child.add_argument("--scan-limit", type=int, default=50)
        elif name in {"document", "statements"}:
            child.add_argument("--accession", required=True)
            if name == "document":
                child.add_argument("--section", choices=["full_text", "mda", "risk_factors", "business"], default="full_text")
                child.add_argument("--item")
                child.add_argument("--attachment", help="Exact filename within this filing")
            else:
                child.add_argument("--statement", choices=["all", "income", "balance", "cashflow"], default="all")
    args = vars(parser.parse_args(argv))
    out, timeout = args.pop("out"), args.pop("timeout")
    if out and out.exists():
        parser.error("output already exists; choose a new evidence path")
    try:
        result = fetch_data(args, timeout=timeout)
    except ValueError as exc:
        parser.error(str(exc))
    text = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("x", encoding="utf-8") as handle:
            handle.write(text)
    sys.stdout.write(text)
    return 0 if result["status"] in {"ok", "no_results"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
