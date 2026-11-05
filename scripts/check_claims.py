#!/usr/bin/env python3
"""Validate an evidence ledger against rules R1-R8 (see references/evidence.md).

Exit 0 when every claim passes, 1 when any claim fails, 2 on unreadable input.
"""

import argparse
import json
import re
import sys
from pathlib import Path

from common import parse_date

TYPES = {"fact", "price", "consensus", "view", "inference"}
TIERS = {"T0", "T1", "T2", "T3", "T4"}
GENERALIZERS = re.compile(
    r"普遍|常见|大家|共识|主流|多数|大多|广泛|一致认为|普遍认为|"
    r"\bwidely\b|\bcommonly\b|\bmost\b|\bconsensus\b|\beveryone\b",
    re.IGNORECASE,
)


def publishers(sources, tiers) -> set:
    return {
        (s.get("publisher") or "").strip().lower()
        for s in sources
        if s.get("tier") in tiers and (s.get("publisher") or "").strip()
    }


def check_claim(claim: dict, ids: set) -> list:
    errs = []
    cid = claim.get("id", "?")
    ctype = claim.get("type")
    text = claim.get("text") or ""
    sources = claim.get("sources") or []

    # R1 required fields
    for field in ("id", "text", "type", "as_of"):
        if not claim.get(field):
            errs.append(f"R1 缺少字段 {field}")
    if ctype and ctype not in TYPES:
        errs.append(f"R1 type 必须是 {sorted(TYPES)} 之一，现在是 {ctype!r}")
    if ctype != "inference" and not sources:
        errs.append("R1 非推断结论至少要有 1 个来源")
    for s in sources:
        if s.get("tier") not in TIERS:
            errs.append(f"R1 来源 {s.get('url', '?')} 的 tier 无效：{s.get('tier')!r}")
        if not s.get("url"):
            errs.append("R1 来源缺少 url")

    tiers = {s.get("tier") for s in sources}

    # R2 facts
    if ctype == "fact" and "T0" not in tiers and len(publishers(sources, {"T0", "T1", "T2"})) < 2:
        errs.append("R2 事实需要 1 个 T0，或 ≥2 个不同发布方的 T0–T2")
    # R3 prices
    if ctype == "price" and not tiers & {"T0", "T1"}:
        errs.append("R3 价格只能来自盘口或隐含定价（T0/T1）")
    # R4 consensus
    if ctype == "consensus" and "T1" not in tiers and len(publishers(sources, {"T1", "T2"})) < 2:
        errs.append("R4 共识需要 1 个 T1，或 ≥2 个不同发布方的 T1–T2")
    # R5 community-only claims stay opinions
    if sources and tiers == {"T4"} and ctype != "view":
        errs.append("R5 只有社区来源（T4）的结论，type 只能是 view")
    # R6 generalizing words need breadth
    match = GENERALIZERS.search(text)
    if match and len(publishers(sources, TIERS)) < 3:
        errs.append(f"R6 用了泛化词“{match.group(0)}”，但不同发布方不足 3 个；改写措辞或补来源")
    # R7 inferences cite their basis
    if ctype == "inference":
        basis = claim.get("basis") or []
        if not basis:
            errs.append("R7 推断必须写 basis（依据的结论 id）")
        missing = [b for b in basis if b not in ids]
        if missing:
            errs.append(f"R7 basis 引用了不存在的 id：{missing}")
        if cid in basis:
            errs.append("R7 推断不能引用自己")
    # R8 no look-ahead
    as_of = parse_date(claim.get("as_of", ""))
    for s in sources:
        published = parse_date(s.get("published_at", ""))
        if as_of and published and published > as_of:
            errs.append(f"R8 来源发布时间 {s.get('published_at')} 晚于截面 {claim.get('as_of')}（穿越）")
    return errs


def _strict_claim(claim, source_map, cutoff, historical):
    """Validate resolved evidence, never inline source assertions."""
    from sources import canonicalize_url, nonempty, timestamp
    errs = []
    if not isinstance(claim, dict):
        return ["R1 claim must be an object"]
    for field in ("id", "text", "type", "as_of"):
        if not nonempty(claim.get(field)):
            errs.append("R1 missing or invalid " + field)
    ctype = claim.get("type")
    if not isinstance(ctype, str) or ctype not in TYPES:
        errs.append("R1 invalid claim type")
        ctype = None
    claim_time, _, error = timestamp(claim.get("as_of"), utc=True)
    if error:
        errs.append("R8 claim.as_of: " + error)
    elif cutoff and claim_time > cutoff:
        errs.append("R8 claim.as_of is after ledger.as_of")
    refs = claim.get("sources", [])
    if not isinstance(refs, list):
        errs.append("R1 sources must be an array of source_id references")
        refs = []
    if ctype != "inference" and not refs:
        errs.append("R1 non-inference claim requires sources")
    if "basis" in claim and (not isinstance(claim["basis"], list)
                             or any(not nonempty(item) for item in claim["basis"])):
        errs.append("R7 basis must be an array of nonempty claim id strings")
    resolved, seen = [], set()
    for ref in refs:
        if not isinstance(ref, dict) or not nonempty(ref.get("source_id")):
            errs.append("R1 sources must reference source_id")
            continue
        sid = ref["source_id"]
        if set(ref) != {"source_id"}:
            errs.append("R1 source reference must contain only source_id; evidence belongs in sources document")
        if sid in seen:
            errs.append("R1 duplicate source_id: " + sid)
            continue
        seen.add(sid)
        source = source_map.get(sid)
        if source is None:
            errs.append("R1 unresolved source_id: " + sid)
            continue
        resolved.append(source)
        selection = source.get("selection")
        if not isinstance(selection, dict) or selection.get("selected") is not True:
            errs.append("R1 " + sid + " is not selected")
        if source.get("access_status") != "ok":
            errs.append("R1 " + sid + " requires access_status=ok (snippet is insufficient)")
        if not nonempty(source.get("quote")) or not nonempty(source.get("locator")):
            errs.append("R1 " + sid + " requires quote and locator")
        expected_kinds = {"price": {"market_quote"}, "consensus": {"survey"},
                          "fact": {"document", "opinion"}, "view": {"document", "opinion", "survey", "market_quote"}}
        if ctype in expected_kinds and source.get("evidence_kind") not in expected_kinds[ctype]:
            errs.append("R1 " + sid + " evidence_kind cannot support claim type " + ctype)
        supports = source.get("supports")
        if ctype != "inference" and (not isinstance(supports, list) or ctype not in supports):
            errs.append("R1 " + sid + " does not declare support for " + str(ctype))
        published, precision, error = timestamp(source.get("published_at"), unknown=True, date=True)
        if error:
            errs.append("R8 " + sid + ".published_at: " + error)
        retrieved, _, retrieval_error = timestamp(source.get("retrieved_at"))
        if retrieval_error:
            errs.append("R8 " + sid + ".retrieved_at: " + retrieval_error)
        availability = source.get("availability")
        available = None
        proof_valid = False
        if availability is not None:
            if not isinstance(availability, dict):
                errs.append("R8 " + sid + ".availability must be an object")
            else:
                available, _, availability_error = timestamp(availability.get("available_at"))
                if availability_error:
                    errs.append("R8 " + sid + ".availability.available_at: " + availability_error)
                proof_valid = available is not None and all(nonempty(availability.get(f)) for f in ("evidence_url", "quote", "locator"))
                if proof_valid:
                    try:
                        canonicalize_url(availability["evidence_url"])
                    except ValueError:
                        proof_valid = False
                if not proof_valid:
                    errs.append("R8 " + sid + ".availability needs available_at, public evidence_url, quote, locator")
                if claim_time and available and available > claim_time:
                    errs.append("R8 " + sid + " availability is after claim.as_of")
        if claim_time:
            if published and (published > claim_time if precision == "instant" else published.date() > claim_time.date()):
                errs.append("R8 " + sid + " was published after claim.as_of")
            # A date has no within-day ordering. Later retrieval, unknown dates,
            # and historical mutable pages require a dated availability record.
            captured = retrieved is not None and retrieved <= claim_time
            proved = proof_valid and available <= claim_time
            if not captured and not proved:
                errs.append("R8 " + sid + " needs availability proof at/before claim.as_of (retrieved later)")
            if historical and precision == "unknown" and not proved:
                errs.append("R8 " + sid + " unknown publication date requires explicit historical availability proof")
            if precision == "date" and published and published.date() == claim_time.date() and not (captured or proved):
                errs.append("R8 " + sid + " date precision cannot establish same-day ordering")
    # Only a confirmed origin_id counts toward independent corroboration.
    # Different publishers syndicating the same wire story remain one family.
    def families(sources):
        # Union every shared origin, actual URL, or canonical URL. Canonical
        # overrides cannot split one actual document into independent families;
        # transitive aliases cannot manufacture a third family either.
        parents = list(range(len(sources)))
        def root(index):
            while parents[index] != index:
                parents[index] = parents[parents[index]]
                index = parents[index]
            return index
        identities = {}
        confirmed = []
        for index, source in enumerate(sources):
            urls = {canonicalize_url(source["url"]),
                    canonicalize_url(source.get("canonical_url") or source["url"])}
            keys = [("url", url) for url in urls]
            if nonempty(source.get("origin_id")) and nonempty(source.get("origin_basis")):
                confirmed.append(index)
                keys.append(("origin", source["origin_id"]))
            for identity in keys:
                if identity in identities:
                    parents[root(index)] = root(identities[identity])
                else:
                    identities[identity] = index
        return {root(index) for index in confirmed}

    def attributed(source):
        attribution = source.get("attribution")
        return (isinstance(attribution, dict) and attribution.get("original") is True
                and attribution.get("statement_kind") == "attributed_statement"
                and nonempty(attribution.get("speaker"))
                and claim.get("attributed_to") == attribution["speaker"]
                and claim.get("fact_scope") == "attributed_statement")

    if ctype == "fact":
        eligible = [s for s in resolved if s.get("tier") in {"T0", "T1", "T2"}
                    and s.get("evidence_kind") == "document" and "fact" in (s.get("supports") or [])]
        statements = [s for s in resolved if s.get("tier") in {"T0", "T1", "T2", "T3"}
                      and s.get("evidence_kind") in {"document", "opinion"} and attributed(s)]
        if not any(s.get("tier") == "T0" for s in eligible) and len(families(eligible)) < 2 and not statements:
            errs.append("R2 fact needs 1 T0 document or 2 confirmed independent T0–T2 origin families; an original attributed statement proves only the attribution")
        for source in resolved:
            if source.get("tier") == "T3" and not attributed(source):
                errs.append("R2 T3 can support only a view or an original attributed statement")
            if source.get("evidence_kind") == "opinion" and not attributed(source):
                errs.append("R2 opinion cannot prove forecast truth; use view or an original attributed statement")
    elif ctype == "price":
        import math
        def finite_number(value):
            if type(value) not in (int, float):
                return False
            try:
                return math.isfinite(value)
            except (OverflowError, ValueError):
                return False
        eligible = [s for s in resolved if s.get("tier") in {"T0", "T1"} and s.get("evidence_kind") == "market_quote"]
        if len(eligible) != len(resolved):
            errs.append("R3 every referenced price source must be a T0/T1 market_quote")
        if not eligible:
            errs.append("R3 price requires T0/T1 market_quote evidence")
        for source in eligible:
            quote = source.get("market_quote")
            if not isinstance(quote, dict):
                errs.append("R3 market_quote metadata is required")
                continue
            for field in ("instrument", "outcome", "direction", "unit"):
                if not nonempty(quote.get(field)):
                    errs.append("R3 market_quote." + field + " is required")
            quote_type = quote.get("quote_type")
            if not isinstance(quote_type, str) or quote_type not in {"indicative", "executable", "trade", "close", "derived"}:
                errs.append("R3 market_quote.quote_type must be indicative/executable/trade/close/derived")
            if claim.get("price_kind") != quote_type or not nonempty(claim.get("price_kind")):
                errs.append("R3 claim.price_kind must match market_quote.quote_type")
            if quote_type == "executable":
                bid, ask = quote.get("bid"), quote.get("ask")
                if not finite_number(bid) or not finite_number(ask) or bid > ask:
                    errs.append("R3 executable quote requires finite ordered bid and ask")
            value = quote.get("value")
            if not finite_number(value):
                errs.append("R3 market_quote.value must be a finite number")
            quoted, _, error = timestamp(quote.get("quoted_at"))
            if error:
                errs.append("R3 market_quote.quoted_at: " + error)
            elif claim_time and quoted > claim_time:
                errs.append("R8 market quote is after claim.as_of")
            retrieved, _, _ = timestamp(source.get("retrieved_at"))
            if quoted and retrieved and quoted > retrieved:
                errs.append("R8 market quote is after source retrieval")
    elif ctype == "consensus":
        eligible = []
        for source in resolved:
            if source.get("tier") not in {"T1", "T2"} or source.get("evidence_kind") != "survey":
                errs.append("R4 every referenced consensus source must be a T1/T2 survey")
                continue
            survey = source.get("survey")
            if not isinstance(survey, dict):
                errs.append("R4 survey metadata is required")
                continue
            valid = True
            for field in ("population", "method"):
                if not nonempty(survey.get(field)):
                    errs.append("R4 survey." + field + " is required")
                    valid = False
            if nonempty(survey.get("population")) and claim.get("consensus_scope") != survey["population"]:
                errs.append("R4 claim.consensus_scope must match survey.population; one survey does not establish universal market consensus")
                valid = False
            if type(survey.get("sample_size")) is not int or survey["sample_size"] < 2:
                errs.append("R4 survey.sample_size must be an integer >=2")
                valid = False
            start, _, error_start = timestamp(survey.get("fieldwork_start"), date=True)
            end, end_precision, error_end = timestamp(survey.get("fieldwork_end"), date=True)
            if error_start or error_end:
                errs.append("R4 survey fieldwork timestamps are invalid")
                valid = False
            elif start > end or claim_time and (end > claim_time if end_precision == "instant" else end.date() >= claim_time.date()):
                errs.append("R8 survey fieldwork must finish before claim.as_of (same-day requires precise time)")
                valid = False
            if valid:
                eligible.append(source)
        if not any(s.get("tier") == "T1" for s in eligible) and len(families(eligible)) < 2:
            errs.append("R4 consensus needs 1 T1 survey or 2 confirmed independent T1–T2 survey families; publisher names are insufficient")
    if ctype != "view" and any(s.get("tier") == "T4" for s in resolved):
        errs.append("R5 T4 evidence supports view only")
    if ctype not in {"view", "fact", "inference"} and any(s.get("tier") == "T3" for s in resolved):
        errs.append("R5 T3 evidence supports view or original attributed statement only")
    text = claim.get("text")
    if isinstance(text, str) and GENERALIZERS.search(text) and len(families(resolved)) < 3:
        # A survey has explicit breadth in population/sample/method, rather
        # than counting publishers that repeat its result.
        if ctype != "consensus":
            errs.append("R6 generalization needs >=3 confirmed independent origin families")
    if ctype == "inference":
        basis = claim.get("basis")
        if not isinstance(basis, list) or not basis or any(not nonempty(item) for item in basis):
            errs.append("R7 inference needs a nonempty array of basis claim ids")
    return errs


def validate_ledger(ledger, sources=None):
    """Validate schema 1 (default) or strict schema 2, without mutating inputs.

    Strict price extras: market_quote={quoted_at,instrument,outcome,direction,
    value,unit,quote_type}; claim.price_kind matches quote_type. Executable quotes
    also require bid/ask. Consensus: survey={population,sample_size,method,
    fieldwork_start,fieldwork_end}; claim.consensus_scope matches population.
    Later retrieval requires availability={available_at,evidence_url,quote,locator};
    historical unknown publication dates always need this proof. Attributed
    statements require claim.attributed_to, claim.fact_scope='attributed_statement'
    and source.attribution={speaker,original:true,statement_kind:'attributed_statement'};
    they do not establish forecast truth.
    """
    from sources import nonempty, timestamp, validate_sources
    if not isinstance(ledger, dict):
        return {"passed": False, "total": 0, "failures": {"_ledger": ["R1 ledger must be an object"]}}
    claims = ledger.get("claims")
    failures = {}
    def fail(key, error):
        failures.setdefault(key, []).append(error)
    if not isinstance(claims, list):
        return {"passed": False, "total": 0, "failures": {"_ledger": ["R1 claims must be an array"]}}
    version = ledger.get("schema_version", 1)
    if type(version) is not int or version not in {1, 2}:
        fail("_ledger", "R1 unsupported schema_version")
        return {"passed": False, "total": len(claims), "failures": failures}
    strict = version == 2
    if strict and not claims:
        fail("_ledger", "R1 strict ledger requires at least one claim")
    ids = set()
    id_counts = {}
    for claim in claims:
        cid = claim.get("id") if isinstance(claim, dict) else None
        if nonempty(cid):
            ids.add(cid)
            id_counts[cid] = id_counts.get(cid, 0) + 1
    duplicate_ids = sorted(cid for cid, count in id_counts.items() if count > 1)
    if duplicate_ids:
        fail("_ledger", "R1 duplicate ids: " + repr(duplicate_ids))
    source_map, cutoff, historical = {}, None, False
    if strict:
        cutoff, _, error = timestamp(ledger.get("as_of"), utc=True)
        if error:
            fail("_ledger", "R8 ledger.as_of: " + error)
        source_doc = sources if sources is not None else ledger.get("sources")
        source_errors = validate_sources(source_doc)
        for error in source_errors:
            fail("_sources", error)
        if isinstance(source_doc, dict):
            historical = source_doc.get("historical") is True
            source_time, _, _ = timestamp(source_doc.get("as_of"), utc=True)
            if cutoff and source_time and cutoff != source_time:
                fail("_sources", "R8 sources.as_of must match ledger.as_of")
            candidates = source_doc.get("candidates")
            if isinstance(candidates, list) and not source_errors:
                source_map = {c["id"]: c for c in candidates if isinstance(c, dict) and nonempty(c.get("id"))}
    keys = []
    for index, claim in enumerate(claims):
        cid = claim.get("id") if isinstance(claim, dict) else None
        key = cid if nonempty(cid) and cid != "_ledger" and cid != "_sources" else "#" + str(index + 1)
        if key in keys:
            key += "#" + str(index + 1)
        keys.append(key)
        if strict:
            errors = _strict_claim(claim, source_map, cutoff, historical)
        elif isinstance(claim, dict):
            try:
                errors = check_claim(claim, ids)
            except (TypeError, AttributeError, ValueError):
                errors = ["R1 malformed legacy claim"]
        else:
            errors = ["R1 claim must be an object"]
        if errors:
            failures.setdefault(key, []).extend(errors)
    if strict:
        graph = {}
        claim_times = {c["id"]: timestamp(c.get("as_of"), utc=True)[0]
                       for c in claims if isinstance(c, dict) and nonempty(c.get("id"))}
        for index, claim in enumerate(claims):
            if not isinstance(claim, dict) or claim.get("type") != "inference":
                continue
            basis = claim.get("basis")
            if not isinstance(basis, list) or not nonempty(claim.get("id")):
                continue
            valid_basis = [b for b in basis if nonempty(b)]
            graph[claim["id"]] = valid_basis
            inference_time = claim_times.get(claim["id"])
            for b in valid_basis:
                if b not in ids:
                    fail(keys[index], "R7 missing basis id: " + b)
                elif inference_time and claim_times.get(b) and claim_times[b] > inference_time:
                    fail(keys[index], "R8 inference basis is later than inference.as_of: " + b)
            if len(valid_basis) != len(set(valid_basis)):
                fail(keys[index], "R7 duplicate basis ids")
        # Iterative strongly connected components find every cycle member,
        # including overlapping cycles, without recursion limits.
        adjacency = {node: [b for b in basis if b in graph] for node, basis in graph.items()}
        reverse = {node: [] for node in adjacency}
        for node, children in adjacency.items():
            for child in children:
                reverse[child].append(node)
        visited, finish = set(), []
        for root in adjacency:
            if root in visited:
                continue
            stack = [(root, False)]
            while stack:
                node, leaving = stack.pop()
                if leaving:
                    finish.append(node)
                elif node not in visited:
                    visited.add(node)
                    stack.append((node, True))
                    stack.extend((child, False) for child in reversed(adjacency[node]) if child not in visited)
        assigned, cyclic = set(), set()
        for root in reversed(finish):
            if root in assigned:
                continue
            component, stack = set(), [root]
            while stack:
                node = stack.pop()
                if node not in assigned:
                    assigned.add(node)
                    component.add(node)
                    stack.extend(reverse[node])
            if len(component) > 1 or root in adjacency[root]:
                cyclic.update(component)
        for index, claim in enumerate(claims):
            if isinstance(claim, dict) and nonempty(claim.get("id")) and claim["id"] in cyclic:
                fail(keys[index], "R7 inference cycle detected")
    return {"passed": not failures, "total": len(claims), "failures": failures}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("ledger", type=Path)
    p.add_argument("--json", action="store_true", help="机器可读输出")
    p.add_argument("--sources", type=Path, help="schema 2 sources document")
    args = p.parse_args()
    try:
        ledger = json.loads(args.ledger.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"读不了账本：{exc}", file=sys.stderr)
        return 2

    source_doc = None
    if args.sources:
        try:
            source_doc = json.loads(args.sources.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            print(f"读不了来源：{exc}", file=sys.stderr)
            return 2
    result = validate_ledger(ledger, source_doc)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"{'✓' if result['passed'] else '✗'} ledger ({result['total']} claims)")
        for cid, errors in result["failures"].items():
            print(str(cid))
            for error in errors:
                print("    " + error)
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
