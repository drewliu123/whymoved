#!/usr/bin/env python3
"""Version 2 retrieval evidence, semantic selection, and offline last30days import.

No retrieval is performed here. Imported candidates require semantic review; engine
rank/engagement is provenance, never a substitute for relevance or evidence quality.
"""

import argparse
import copy
import hashlib
import ipaddress
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

TIERS = {"T0", "T1", "T2", "T3", "T4"}
SUPPORTS = {"fact", "price", "consensus", "view"}
KINDS = {"document", "market_quote", "survey", "opinion"}
STATUSES = {"ok", "partial", "no_results", "not_run", "error", "rate_limited",
            "auth_failed", "payment_required", "unreachable", "timeout", "schema_drift"}
ENGINE_STATES = {"ok", "partial", "no-results", "rate-limited", "auth-failed",
                 "payment-required", "unreachable", "timeout", "schema-drift",
                 "skipped-unconfigured", "error"}
SOCIAL = {"reddit", "x", "twitter", "youtube", "tiktok", "hackernews", "hn",
          "bluesky", "instagram", "xiaohongshu", "facebook"}
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$")


def _is_choice(value, choices):
    return isinstance(value, str) and value in choices


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def timestamp(value, unknown=False, date=False, utc=False):
    """Return (UTC datetime, precision, error); never conflate invalid and unknown."""
    if value is None or value == "unknown":
        return (None, "unknown", None if unknown else "timestamp is unknown")
    if not isinstance(value, str):
        return None, "invalid", "timestamp must be a string"
    precision = "date" if _DATE.fullmatch(value) else "instant"
    if precision == "date" and not date:
        return None, precision, "timestamp requires time and timezone (date precision is insufficient)"
    if precision != "date" and not _TIMESTAMP.fullmatch(value):
        return None, "invalid", "invalid ISO timestamp (time and timezone required)"
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if precision == "date":
            dt = dt.replace(tzinfo=timezone.utc)
        if utc and dt.utcoffset().total_seconds() != 0:
            return None, precision, "timestamp must use UTC"
        return dt.astimezone(timezone.utc), precision, None
    except (ValueError, OverflowError):
        return None, "invalid", "invalid calendar timestamp"


def canonicalize_url(value):
    """Normalize public HTTP(S) URLs without executing, fetching, or trusting them."""
    if not nonempty(value) or re.search(r"[\x00-\x20\x7f\\]", value) or re.search(r"%0[0ad]", value, re.I):
        raise ValueError("url contains whitespace, controls, or backslashes")
    try:
        parts = urlsplit(value)
        if parts.scheme.lower() not in {"http", "https"} or not parts.hostname:
            raise ValueError("url must be absolute http(s)")
        if parts.username is not None or parts.password is not None:
            raise ValueError("url must not contain credentials")
        host = parts.hostname.encode("idna").decode("ascii").lower().rstrip(".")
        if host == "localhost" or host.endswith((".localhost", ".local")) or "." not in host and ":" not in host:
            raise ValueError("url must name a public host")
        try:
            address = ipaddress.ip_address(host)
        except ValueError:
            address = None
        if address is not None and not address.is_global:
            raise ValueError("url must not point to a private or special address")
        if address is None and (not re.fullmatch(r"[a-z0-9.-]+", host) or any(not label or label.startswith("-") or label.endswith("-") for label in host.split("."))):
            raise ValueError("invalid url host")
        if address is None and (not re.search(r"[a-z]", host.split(".")[-1]) or all(re.fullmatch(r"(?:0x[0-9a-f]+|[0-9]+)", label) for label in host.split("."))):
            raise ValueError("url must not use ambiguous numeric address notation")
        port = parts.port
        netloc = "[" + host + "]" if ":" in host else host
        if port and (parts.scheme.lower(), port) not in {("http", 80), ("https", 443)}:
            netloc += ":" + str(port)
        query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
                 if not k.lower().startswith("utm_") and k.lower() not in {"fbclid", "gclid"}]
        return urlunsplit((parts.scheme.lower(), netloc, parts.path or "/", urlencode(sorted(query)), ""))
    except (ValueError, UnicodeError) as exc:
        raise ValueError(str(exc)) from None


def _url_error(value):
    try:
        canonicalize_url(value)
        return None
    except ValueError as exc:
        return str(exc)


def validate_sources(doc):
    """Return structural/time/provenance errors in a version 2 sources document.

    Unknown publication dates are allowed for current research, not malformed
    dates. Historical availability is enforced against each claim by the ledger
    validator. A candidate may remain unselected or have supports=[] for review.
    """
    if not isinstance(doc, dict):
        return ["sources must be an object"]
    errs = []
    if type(doc.get("schema_version")) is not int or doc.get("schema_version") != 2:
        errs.append("sources schema_version must be 2")
    cutoff, _, error = timestamp(doc.get("as_of"), utc=True)
    if error:
        errs.append("sources.as_of: " + error)
    if type(doc.get("historical")) is not bool:
        errs.append("sources.historical must be boolean")
    statuses = doc.get("source_status")
    if not isinstance(statuses, dict) or not statuses:
        errs.append("source_status must be a nonempty object (including not_run sources)")
    else:
        for name, status in statuses.items():
            if not nonempty(name) or not isinstance(status, dict) or not _is_choice(status.get("status"), STATUSES):
                errs.append("source_status %r has invalid status" % name)
    candidates = doc.get("candidates")
    if not isinstance(candidates, list):
        return errs + ["sources.candidates must be an array"]
    ids = set()
    for index, candidate in enumerate(candidates):
        prefix = "candidate[%s]" % index
        if not isinstance(candidate, dict):
            errs.append(prefix + " must be an object")
            continue
        cid = candidate.get("id")
        if not nonempty(cid):
            errs.append(prefix + ".id is required")
        elif cid in ids:
            errs.append(prefix + ".id is duplicate: " + cid)
        else:
            ids.add(cid)
        for field in ("publisher", "origin_basis"):
            if not nonempty(candidate.get(field)):
                errs.append(prefix + "." + field + " is required")
        for field in ("url", "canonical_url"):
            if field == "canonical_url" and field not in candidate:
                continue
            error = _url_error(candidate.get(field))
            if error:
                errs.append(prefix + "." + field + ": " + error)
        if candidate.get("canonical_url") and not _url_error(candidate.get("url")) and not _url_error(candidate["canonical_url"]):
            if urlsplit(candidate["canonical_url"]).hostname != urlsplit(candidate["url"]).hostname:
                errs.append(prefix + ".canonical_url must have the same host as url")
        if not _is_choice(candidate.get("tier"), TIERS):
            errs.append(prefix + ".tier must be T0..T4")
        if "published_at" not in candidate:
            errs.append(prefix + ".published_at is required (use unknown if unresolved)")
        published, precision, error = timestamp(candidate.get("published_at"), unknown=True, date=True)
        if error:
            errs.append(prefix + ".published_at: " + error)
        after_cutoff = cutoff and published and (published > cutoff if precision == "instant" else published.date() > cutoff.date())
        selection = candidate.get("selection")
        if after_cutoff and not (isinstance(selection, dict) and selection.get("selected") is False):
            errs.append(prefix + ".published_at is after sources.as_of; candidate must be explicitly unselected")
        retrieved, _, error = timestamp(candidate.get("retrieved_at"))
        if error:
            errs.append(prefix + ".retrieved_at: " + error)
        if published and retrieved and published > retrieved:
            errs.append(prefix + ".published_at is after retrieved_at")
        if "origin_id" not in candidate or candidate.get("origin_id") is not None and not nonempty(candidate.get("origin_id")):
            errs.append(prefix + ".origin_id must be a confirmed family string or null")
        supports = candidate.get("supports")
        if not isinstance(supports, list) or any(not isinstance(s, str) or s not in SUPPORTS for s in supports):
            errs.append(prefix + ".supports must be an array of fact/price/consensus/view")
        if not _is_choice(candidate.get("evidence_kind"), KINDS):
            errs.append(prefix + ".evidence_kind is invalid")
        if not _is_choice(candidate.get("access_status"), {"ok", "snippet", "failed"}):
            errs.append(prefix + ".access_status must be ok/snippet/failed")
        for field in ("quote", "locator"):
            if not isinstance(candidate.get(field), str):
                errs.append(prefix + "." + field + " must be a string")
        selection = candidate.get("selection")
        if not isinstance(selection, dict):
            errs.append(prefix + ".selection is required")
        else:
            if type(selection.get("selected")) is not bool:
                errs.append(prefix + ".selection.selected must be boolean")
            if not _is_choice(selection.get("relevance"), {"direct", "context", "irrelevant"}):
                errs.append(prefix + ".selection.relevance is invalid")
            if not _is_choice(selection.get("priority"), {"decisive", "useful", "background"}):
                errs.append(prefix + ".selection.priority is invalid")
            for field in ("reason", "purpose"):
                if not nonempty(selection.get(field)):
                    errs.append(prefix + ".selection." + field + " is required")
            if selection.get("selected") and selection.get("relevance") == "irrelevant":
                errs.append(prefix + ": irrelevant candidate cannot be selected")
            if selection.get("selected") and (candidate.get("access_status") == "failed" or not nonempty(candidate.get("quote")) or not nonempty(candidate.get("locator"))):
                errs.append(prefix + ": selected candidate needs accessible quote and locator")
    return errs


def select_sources(doc):
    """Honor explicit semantic annotations, returning a copy with auditable dedup.

    Lexicographic relevance/priority precedes original engine order. No weighted
    score or engagement threshold is used. Only exact fragments sharing a URL
    and explicitly confirmed retransmissions are folded. Different locators or
    statements in one document survive; topic/origin alone never collapses them.
    """
    errors = validate_sources(doc)
    if errors:
        raise ValueError("; ".join(errors))
    result = copy.deepcopy(doc)
    candidates = result["candidates"]
    relevance = {"direct": 0, "context": 1, "irrelevant": 2}
    priority = {"decisive": 0, "useful": 1, "background": 2}

    def key(pair):
        index, candidate = pair
        sel = candidate["selection"]
        rank = candidate.get("provenance", {}).get("engine_rank") if isinstance(candidate.get("provenance"), dict) else None
        if type(rank) not in (int, float) or rank < 0:
            rank = index
        return relevance[sel["relevance"]], priority[sel["priority"]], rank, index

    ordered = sorted(enumerate(candidates), key=key)
    urls, retransmissions = {}, {}
    for _, candidate in ordered:
        candidate["canonical_url"] = canonicalize_url(candidate.get("canonical_url") or candidate["url"])
        if not candidate["selection"]["selected"]:
            continue
        fragment_key = (candidate["canonical_url"], " ".join(candidate["quote"].split()), candidate["locator"].strip())
        duplicate = urls.get(fragment_key)
        # A confirmed retransmission must identify both the family and exact
        # statement; an engine topic cluster is not an independence judgment.
        retransmission = candidate.get("retransmission")
        family_key = None
        if isinstance(retransmission, dict) and retransmission.get("confirmed") is True and candidate.get("origin_id") and nonempty(retransmission.get("statement_id")) and nonempty(retransmission.get("basis")):
            family_key = (candidate["origin_id"], retransmission["statement_id"])
            duplicate = duplicate or retransmissions.get(family_key)
        if duplicate:
            sel = candidate["selection"]
            sel["annotation_reason"] = sel.get("annotation_reason", sel["reason"])
            sel["selected"] = False
            sel["reason"] = "Duplicate evidence of " + duplicate
            sel["duplicate_of"] = duplicate
        else:
            urls[fragment_key] = candidate["id"]
            if family_key:
                retransmissions[family_key] = candidate["id"]
    result["candidates"] = [candidate for _, candidate in ordered]
    result["selection_summary"] = {
        "selected": [c["id"] for c in result["candidates"] if c["selection"]["selected"]],
        "method": "explicit semantic relevance, priority, then original engine rank; no engagement weighting",
    }
    return result


def _engine_status(raw):
    if not isinstance(raw, dict) or not raw:
        raise ValueError("last30days compatibility error: missing source_status")
    statuses = {}
    for name, outcome in raw.items():
        if isinstance(outcome, dict):
            state = outcome.get("state")
            detail = copy.deepcopy(outcome)
        else:
            state, detail = outcome, {}
        if not _is_choice(state, ENGINE_STATES):
            raise ValueError("last30days compatibility error: unknown source state %r" % state)
        mapped = "not_run" if state == "skipped-unconfigured" else state.replace("-", "_")
        detail.update(status=mapped, engine_state=state)
        statuses[name] = detail
    return statuses


def import_last30days(raw, raw_path=None):
    """Adapt last30days 3.30 full Report or agent export 1.4, offline.

    The complete raw report is retained. Ranked candidates AND unranked source
    items are carried forward. No body, family, quote location, survey, market
    quote, or semantic judgment is fabricated from title, rank, or publisher.
    """
    if not isinstance(raw, dict):
        raise ValueError("last30days compatibility error: report must be an object")
    full = all(field in raw for field in ("ranked_candidates", "items_by_source", "generated_at", "clusters", "source_status"))
    agent = raw.get("schema_version") == "1.4" and all(field in raw for field in ("results", "query", "generated_at", "clusters", "source_status"))
    if not full and not agent:
        raise ValueError("last30days compatibility error: expected 3.30 Report or agent schema 1.4")
    if full and not isinstance(raw["items_by_source"], dict):
        raise ValueError("last30days compatibility error: items_by_source must be an object")
    rows = raw["ranked_candidates"] if full else raw["results"]
    if not isinstance(rows, list) or not isinstance(raw["clusters"], list):
        raise ValueError("last30days compatibility error: candidates and clusters must be arrays")
    generated, _, error = timestamp(raw.get("generated_at"))
    if error:
        raise ValueError("last30days compatibility error: generated_at: " + error)
    as_of = generated.isoformat().replace("+00:00", "Z")
    statuses = _engine_status(raw["source_status"])
    items, seen_items, candidates, seen_ids = {}, set(), [], set()
    if full:
        for source, pool in raw["items_by_source"].items():
            if not isinstance(pool, list) or any(not isinstance(item, dict) for item in pool):
                raise ValueError("last30days compatibility error: invalid source item pool")
            for item in pool:
                if not nonempty(item.get("item_id")) or not nonempty(item.get("url")):
                    raise ValueError("last30days compatibility error: source item lacks item_id/url")
                items[(source, item["item_id"])] = item

    def append_candidate(row, source_item, rank, unranked=False):
        if not isinstance(row, dict) or not nonempty(row.get("url")) or not nonempty(row.get("source")):
            raise ValueError("last30days compatibility error: candidate lacks source/url")
        source = row["source"]
        engine_id = row.get("candidate_id") or row.get("item_id")
        if not nonempty(engine_id):
            raise ValueError("last30days compatibility error: candidate lacks identifier")
        internal = "S" + str(len(candidates) + 1)
        identity = (source, engine_id, unranked)
        if identity in seen_ids:
            raise ValueError("last30days compatibility error: duplicate engine candidate identifier")
        seen_ids.add(identity)
        original = source_item or {}
        published = original.get("published_at") or row.get("published_at") or "unknown"
        body = original.get("body") or ""
        snippet = original.get("snippet") or row.get("snippet") or row.get("summary") or ""
        # SourceItem.body is verbatim collected text; agent summary is not.
        quote = body or (snippet if full else "")
        metadata = original.get("metadata") if isinstance(original.get("metadata"), dict) else {}
        locator = metadata.get("locator") or ("body" if body else "snippet" if snippet and full else "")
        social = source.lower() in SOCIAL
        candidate = {
            "id": internal, "url": row["url"], "publisher": original.get("author") or source,
            "tier": "T4" if social else "T2", "published_at": published, "retrieved_at": as_of,
            "quote": quote, "locator": locator, "origin_id": None,
            "origin_basis": "Unresolved: engine source/cluster does not establish independent origin",
            "supports": ["view"] if social else [], "evidence_kind": "opinion" if social else "document",
            "access_status": "ok" if body else "snippet",
            "selection": {"selected": False, "reason": "Requires semantic review and evidence verification",
                          "relevance": "context", "purpose": "review", "priority": "background"},
            "platform": source,
            "provenance": {"engine": "last30days", "engine_version": "3.30.0",
                           "engine_candidate_id": row.get("candidate_id"), "engine_item_id": row.get("item_id"),
                           "engine_rank": rank, "unranked": unranked, "raw_candidate": copy.deepcopy(row)},
        }
        if original.get("author"):
            candidate["author"] = original["author"]
        # Missing engagement stays missing, never zero.
        if "engagement" in original or "engagement" in row:
            candidate["engagement"] = copy.deepcopy(original.get("engagement", row.get("engagement")))
        candidates.append(candidate)

    for rank, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            raise ValueError("last30days compatibility error: candidate must be an object")
        if not nonempty(row.get("source")) or (row.get("item_id") is not None and not nonempty(row.get("item_id"))):
            raise ValueError("last30days compatibility error: candidate source/item_id must be strings")
        original = items.get((row.get("source"), row.get("item_id")))
        source_items = row.get("source_items", [])
        if not isinstance(source_items, list) or any(not isinstance(item, dict) for item in source_items):
            raise ValueError("last30days compatibility error: invalid candidate source_items")
        if original is None and source_items:
            original = next((item for item in source_items if item.get("item_id") == row.get("item_id")), source_items[0])
        append_candidate(row, original, rank)
        seen_items.add((row.get("source"), row.get("item_id")))
        # Fused candidates can contain distinct URLs/viewpoints. Preserve them
        # as pool items, rather than treating fusion as proof of duplication.
        for item in source_items:
            source = item.get("source") or row.get("source")
            if not nonempty(source) or not nonempty(item.get("item_id")) or not nonempty(item.get("url")):
                raise ValueError("last30days compatibility error: fused source item lacks valid source/item_id/url")
            item_key = (source, item.get("item_id"))
            if item_key not in items:
                items[item_key] = dict(item, source=source)
    for (source, item_id), item in items.items():
        if (source, item_id) not in seen_items:
            append_candidate(dict(item, source=source), item, None, unranked=True)
    raw_bytes = json.dumps(raw, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    result = {"schema_version": 2, "as_of": as_of, "historical": False,
              "candidates": candidates, "source_status": statuses,
              "retrieval": {"engine": "last30days", "engine_version": "3.30.0", "profile": "full" if full else "agent-1.4",
                            "raw_report": copy.deepcopy(raw), "raw_sha256": hashlib.sha256(raw_bytes).hexdigest(),
                            "hash_basis": "canonical JSON UTF-8", "clusters": copy.deepcopy(raw["clusters"]),
                            "recall_limit": "Only the engine-returned candidate pool; not complete platform recall"}}
    if raw_path is not None:
        result["retrieval"]["raw_path"] = str(raw_path)
    errors = validate_sources(result)
    if errors:
        raise ValueError("last30days compatibility error: " + "; ".join(errors))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "select", "import-last30days"):
        command = sub.add_parser(name)
        command.add_argument("input", type=Path)
        if name != "validate":
            command.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        doc = json.loads(args.input.read_text(encoding="utf-8"))
        if args.command == "validate":
            errors = validate_sources(doc)
            print(json.dumps({"passed": not errors, "errors": errors}, ensure_ascii=False, indent=2))
            return 1 if errors else 0
        result = select_sources(doc) if args.command == "select" else import_last30days(doc, args.input)
        # Explicit output only; never writes a cache or research ledger.
        args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"out": str(args.out), "candidates": len(result["candidates"])}, ensure_ascii=False))
        return 0
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
