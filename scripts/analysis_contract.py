#!/usr/bin/env python3
"""Question-to-method routing and verifiable analysis contracts (Python 3.9+).

No text classifier or causal oracle: the researcher explicitly selects question_kind.
Model arithmetic is recomputed; source meaning and assumptions still need review.
"""

import argparse
import json
import math
import re
import sys
from pathlib import Path

METHODS = {
    "change_explanation": {"method": "comparative_attribution", "inputs": ["performance_and_benchmark", "event_timeline", "prior_expectations"], "test": True, "models": []},
    "operating_outlook": {"method": "driver_bridge", "inputs": ["volume_price_or_revenue", "margins", "cash_requirements"], "test": True, "models": ["operating_bridge", "free_cash_flow", "driver_build"]},
    "valuation": {"method": "reverse_valuation", "inputs": ["timestamped_price", "shares_and_net_debt", "cash_flow", "discount_and_terminal_assumptions"], "test": True, "models": ["reverse_dcf", "relative_valuation"]},
    "event_forecast": {"method": "reference_class_scenarios", "inputs": ["resolution_contract", "reference_class", "conditional_drivers"], "test": True, "models": []},
    "theme_transmission": {"method": "transmission_bottleneck", "inputs": ["demand_to_cash_chain", "cancellation_and_delivery", "profit_capture"], "test": True, "models": []},
    "commitment_check": {"method": "commitment_reconciliation", "inputs": ["dated_commitment", "conditions_and_authority", "observed_action"], "test": False, "models": []},
}
SCENARIOS = {"bear", "base", "bull"}
MODEL_KINDS = {"operating_bridge", "free_cash_flow", "dcf", "reverse_dcf", "relative_valuation", "driver_build"}
IDENTIFIER = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]*$")


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _id(value):
    return isinstance(value, str) and bool(IDENTIFIER.fullmatch(value))


def route(question_kind):
    if not isinstance(question_kind, str) or question_kind not in METHODS:
        raise ValueError("unknown question_kind")
    return {"question_kind": question_kind, **METHODS[question_kind]}


def validate_design(plan):
    """Validate only explicit plan.analysis_version=1; old plans stay readable."""
    if "analysis_version" not in plan:
        return []
    errors = []
    if type(plan["analysis_version"]) is not int or plan["analysis_version"] != 1:
        errors.append("analysis_version must be 1")
    design = plan.get("research_design")
    if not isinstance(design, dict):
        return errors + ["research_design must be an object"]
    kind = design.get("question_kind")
    rule = METHODS.get(kind) if isinstance(kind, str) else None
    if rule is None:
        return errors + ["research_design.question_kind is invalid"]
    if design.get("method") != rule["method"]:
        errors.append("research_design.method does not match question_kind")
    for key in ("rationale", "baseline"):
        if not _text(design.get(key)):
            errors.append("research_design." + key + " must be nonempty text")
    if not isinstance(design.get("price_relevance"), bool):
        errors.append("research_design.price_relevance must be boolean")
    if kind == "valuation" and design.get("price_relevance") is not True:
        errors.append("valuation requires price_relevance=true")
    chain = design.get("mechanism_chain")
    if not isinstance(chain, list) or len(chain) < 2 or not all(_text(v) for v in chain):
        errors.append("research_design.mechanism_chain needs at least two linked variables")
    hypotheses = plan.get("hypotheses")
    if not isinstance(hypotheses, list):
        return errors + ["hypotheses must be a list"]
    ids = [h.get("id") for h in hypotheses if isinstance(h, dict)]
    if len(ids) != len(hypotheses) or any(not _id(v) for v in ids) or len(set(v for v in ids if isinstance(v, str))) != len(ids):
        errors.append("hypotheses require unique safe ids")
    known = {v for v in ids if _id(v)}
    explanations = [h.get("explanation", "").strip().casefold() for h in hypotheses if isinstance(h, dict) and isinstance(h.get("explanation"), str)]
    if rule["test"] and (len(known) < 2 or len(set(explanations)) < 2):
        errors.append("this question_kind requires at least two distinct competing hypotheses")
    tests = design.get("discrimination_tests")
    if not isinstance(tests, list) or (rule["test"] and not tests):
        return errors + ["research_design.discrimination_tests must be a list with tests for competing explanations"]
    test_ids = set()
    for n, test in enumerate(tests):
        path = "discrimination_tests[%d]" % n
        if not isinstance(test, dict):
            errors.append(path + " must be an object")
            continue
        tid = test.get("id")
        if not _id(tid) or tid in test_ids:
            errors.append(path + ".id must be unique and safe")
        else:
            test_ids.add(tid)
        for key in ("observe", "source", "by"):
            if not _text(test.get(key)):
                errors.append(path + "." + key + " is required")
        outcomes = test.get("outcomes")
        if not isinstance(outcomes, list) or len(outcomes) < 2:
            errors.append(path + ".outcomes needs distinct predictions for at least two hypotheses")
            continue
        outcome_ids, predictions = [], []
        for outcome in outcomes:
            if not isinstance(outcome, dict) or not isinstance(outcome.get("hypothesis_id"), str) or outcome.get("hypothesis_id") not in known or not _text(outcome.get("prediction")):
                errors.append(path + ".outcomes must reference hypotheses and give predictions")
            else:
                outcome_ids.append(outcome["hypothesis_id"])
                predictions.append(outcome["prediction"].strip().casefold())
        if len(set(outcome_ids)) != len(outcome_ids) or len(set(predictions)) < 2:
            errors.append(path + ".outcomes must have different hypotheses and predictions")
    covered = set()
    for query in plan.get("queries", []) if isinstance(plan.get("queries"), list) else []:
        if not isinstance(query, dict):
            continue
        links = query.get("test_ids")
        if not isinstance(links, list) or any(not isinstance(v, str) or v not in test_ids for v in links):
            errors.append("queries.test_ids must reference discrimination_tests (empty allowed for background)")
        else:
            covered.update(links)
    if test_ids - covered:
        errors.append("each discrimination test requires a linked query")
    return errors


def _same_result(actual, recorded):
    if isinstance(actual, dict):
        return isinstance(recorded, dict) and actual.keys() == recorded.keys() and all(_same_result(v, recorded[k]) for k, v in actual.items())
    if isinstance(actual, list):
        return isinstance(recorded, list) and len(actual) == len(recorded) and all(_same_result(a, b) for a, b in zip(actual, recorded))
    if type(actual) in (int, float):
        return type(recorded) in (int, float) and actual == recorded
    return type(actual) is type(recorded) and actual == recorded


SCALE_WORDS = (
    (r"trillion|\btrn\b|\btn\b|万亿", 1e12),
    (r"billion|\bbn\b|十亿", 1e9),
    (r"million|\bmn\b|百万", 1e6),
    (r"thousand|\bth\b|千", 1e3),
    (r"亿", 1e8),
    (r"万", 1e4),
)


def _finite_number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    try:
        return value if math.isfinite(value) else None
    except OverflowError:
        return None


def _scale_factor(text):
    """Parse a scale label into a multiplier; None means 'cannot verify'."""
    if not isinstance(text, str) or not text.strip():
        return None
    lowered = text.casefold()
    for pattern, factor in SCALE_WORDS:
        if re.search(pattern, lowered):
            return factor
    if re.search(r"单[位份]|\bone\b|\bunit\b|\b1\b", lowered):
        return 1.0
    return None


def _metric_dimension(unit):
    """Map a free-text metric unit to a canonical model-input dimension."""
    if not isinstance(unit, str):
        return None
    text = unit.casefold().replace(" ", "")
    if "/share" in text or "每股" in text:
        return "currency/share"
    if text in {"ratio", "percent", "%", "百分比", "比率"} or "ratio" in text or "percent" in text:
        return "ratio"
    if "share" in text or "股" in text:
        return "shares"
    if text == "currency" or re.search(r"usd|eur|cny|rmb|hkd|jpy|gbp|dollar|yuan|美元|人民币|港元|日元|元", text):
        return "currency"
    return None


PERIOD_WINDOW_TYPES = {"fy", "quarter", "ltm", "instant"}


def _iso_date(value):
    if not isinstance(value, str):
        return None
    try:
        from datetime import datetime
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed


def _period_window(model, path, errors):
    """Parse the optional machine-checkable model period window."""
    window = model.get("period_window")
    if window is None:
        return None
    if not isinstance(window, dict):
        errors.append(path + ".period_window must be an object")
        return None
    extra = set(window) - {"start", "end", "period_type"}
    if extra:
        errors.append(path + ".period_window has unknown fields: " + ", ".join(sorted(map(str, extra))))
    start, end = _iso_date(window.get("start")), _iso_date(window.get("end"))
    if start is None or end is None:
        errors.append(path + ".period_window requires ISO start and end")
        return None
    if start > end:
        errors.append(path + ".period_window.start must not be after end")
        return None
    kind = window.get("period_type")
    if kind is not None and (not isinstance(kind, str) or kind not in PERIOD_WINDOW_TYPES):
        errors.append(path + ".period_window.period_type must be one of " + ", ".join(sorted(PERIOD_WINDOW_TYPES)))
        return None
    return {"start": start, "end": end, "period_type": kind}


def _metric_period_errors(name, cids, claim_map, window, path):
    """Observed inputs must sit inside the model's declared period window."""
    if not window:
        return []
    errors = []
    for cid in cids:
        metric = claim_map[cid].get("metric")
        if not isinstance(metric, dict):
            continue
        kind = metric.get("period_type")
        if window.get("period_type") and isinstance(kind, str) and kind != window["period_type"]:
            errors.append(path + "." + name + " cites " + cid + " metric period_type " + kind +
                          " but the model window is " + window["period_type"])
        end, start = _iso_date(metric.get("period_end")), _iso_date(metric.get("period_start"))
        if end is not None and end > window["end"]:
            errors.append(path + "." + name + " cites " + cid + " metric period_end after the model period window")
        if start is not None and start < window["start"]:
            errors.append(path + "." + name + " cites " + cid + " metric period_start before the model period window")
    return errors


def _metric_input_errors(name, row, cids, claim_map, wrapper_scale, path):
    """Check an observed model input against the metric block of the cited claim.

    Only runs when both sides expose a parseable scale and the dimensions agree;
    otherwise the input is reported as unverifiable by omission rather than by error.
    """
    errors = []
    input_unit = row.get("unit")
    input_value = _finite_number(row.get("value"))
    if input_unit not in {"currency", "ratio", "shares", "currency/share"} or input_value is None:
        return errors
    wrapper_factor = _scale_factor(wrapper_scale) if input_unit in {"currency", "shares"} else 1.0
    for cid in cids:
        metric = claim_map[cid].get("metric")
        if not isinstance(metric, dict):
            continue
        dimension = _metric_dimension(metric.get("unit"))
        if dimension is None:
            continue
        if dimension != input_unit:
            errors.append(path + "." + name + " unit " + str(input_unit) + " differs from the metric unit " +
                          str(metric.get("unit")) + " of claim " + cid)
            continue
        metric_value = _finite_number(metric.get("value"))
        if metric_value is None:
            continue
        if input_unit in {"currency", "shares"}:
            metric_factor = _scale_factor(metric.get("scale"))
            if wrapper_factor is None or metric_factor is None:
                continue
        else:
            metric_factor = 1.0
        expected = metric_value * metric_factor
        actual = input_value * wrapper_factor
        tolerance = max(1e-9 * max(abs(expected), abs(actual)), 1e-12)
        if abs(actual - expected) > tolerance:
            errors.append(path + "." + name + " value " + str(input_value) + " (model scale " + str(wrapper_scale) +
                          ") differs from claim " + cid + " metric " + str(metric_value) + " " +
                          str(metric.get("unit")) + " / " + str(metric.get("scale")))
    return errors


def _price_age_errors(market, market_refs, claim_map, sources, path, max_age_hours):
    """Reject a verdict built on a price quote that is stale relative to its claim."""
    from sources import timestamp
    errors = []
    source_map = {s["id"]: s for s in sources.get("candidates", [])
                  if isinstance(s, dict) and _id(s.get("id"))}
    for cid in market_refs:
        claim = claim_map.get(cid)
        if not isinstance(claim, dict) or claim.get("type") != "price":
            continue
        claim_time, _, claim_error = timestamp(claim.get("as_of"), utc=True)
        if claim_error or claim_time is None:
            continue
        for ref in claim.get("sources", []):
            source = source_map.get(ref.get("source_id")) if isinstance(ref, dict) else None
            quote = source.get("market_quote") if isinstance(source, dict) else None
            if not isinstance(quote, dict):
                continue
            quoted, _, error = timestamp(quote.get("quoted_at"), utc=True)
            if error or quoted is None:
                continue
            age = (claim_time - quoted).total_seconds() / 3600
            if age < 0:
                continue
            if age > max_age_hours:
                errors.append("%s price claim %s quotes a %.1f hour old price; max is %s hours"
                              % (path, cid, age, max_age_hours))
    return errors


def validate_analysis(analysis, claims, design=None, hypotheses=None, sources=None):
    """Validate evidence links and recompute fixed models, optionally against a plan."""
    errors = []
    if not isinstance(analysis, dict):
        return ["analysis must be an object"]
    if type(analysis.get("version")) is not int or analysis.get("version") != 1:
        errors.append("analysis.version must be 1")
    claim_map = {c["id"]: c for c in claims if isinstance(c, dict) and _id(c.get("id"))} if isinstance(claims, list) else {}

    def refs(value, path, required=True):
        if not isinstance(value, list) or (required and not value) or any(not isinstance(v, str) or v not in claim_map for v in value):
            errors.append(path + " must reference existing claims")
            return []
        if len(set(value)) != len(value):
            errors.append(path + " contains duplicate claims")
        return value

    kind = analysis.get("question_kind")
    rule = METHODS.get(kind) if isinstance(kind, str) else None
    if rule is None:
        errors.append("analysis.question_kind is invalid")
    elif analysis.get("method") != rule["method"]:
        errors.append("analysis.method does not match question_kind")
    if design is not None:
        for key in ("question_kind", "method", "price_relevance", "baseline", "mechanism_chain"):
            if analysis.get(key) != design.get(key):
                errors.append("analysis." + key + " differs from research_design")
    for key in ("baseline", "conclusion", "model_reason"):
        if not _text(analysis.get(key)):
            errors.append("analysis." + key + " must be nonempty text")
    refs(analysis.get("baseline_claim_ids"), "analysis.baseline_claim_ids")
    refs(analysis.get("conclusion_claim_ids"), "analysis.conclusion_claim_ids")
    chain = analysis.get("mechanism_chain")
    if not isinstance(chain, list) or len(chain) < 2 or not all(_text(v) for v in chain):
        errors.append("analysis.mechanism_chain needs linked variables")
    price_relevance = analysis.get("price_relevance")
    if not isinstance(price_relevance, bool) or (kind == "valuation" and price_relevance is not True):
        errors.append("analysis.price_relevance must be boolean and true for valuation")
    tests = analysis.get("tests")
    if not isinstance(tests, list) or (rule and rule["test"] and not tests):
        errors.append("analysis.tests must contain the planned tests")
        tests = []
    planned_tests = {t["id"]: t for t in design.get("discrimination_tests", []) if isinstance(t, dict) and _id(t.get("id"))} if isinstance(design, dict) else None
    recorded_h = analysis.get("hypotheses")
    if not isinstance(recorded_h, list) or not recorded_h:
        errors.append("analysis.hypotheses must record the competing explanations")
        recorded_h = []
    known_h = set()
    for h in recorded_h:
        if not isinstance(h, dict) or not _id(h.get("id")) or not _text(h.get("explanation")):
            errors.append("analysis.hypotheses requires safe ids and explanations")
        elif h["id"] in known_h:
            errors.append("analysis.hypotheses has duplicate ids")
        else:
            known_h.add(h["id"])
    if isinstance(hypotheses, list) and recorded_h != [{"id": h.get("id"), "explanation": h.get("explanation")} for h in hypotheses if isinstance(h, dict)]:
        errors.append("analysis.hypotheses differs from the plan")
    explanations = {h["explanation"].strip().casefold() for h in recorded_h if isinstance(h, dict) and _text(h.get("explanation"))}
    if rule and rule["test"] and (len(known_h) < 2 or len(explanations) < 2):
        errors.append("analysis requires distinct competing hypotheses")
    tids = set()
    for n, test in enumerate(tests):
        path = "analysis.tests[%d]" % n
        if not isinstance(test, dict):
            errors.append(path + " must be an object")
            continue
        tid = test.get("id")
        if not _id(tid) or tid in tids:
            errors.append(path + ".id must be unique and safe")
        else:
            tids.add(tid)
        if planned_tests is not None and (not _id(tid) or tid not in planned_tests):
            errors.append(path + ".id is not in the plan")
        outcomes = test.get("outcomes")
        if not isinstance(outcomes, list) or len(outcomes) < 2:
            errors.append(path + ".outcomes must record distinct predictions")
        else:
            predicted_h, predictions = [], []
            for o in outcomes:
                if not isinstance(o, dict) or not isinstance(o.get("hypothesis_id"), str) or o["hypothesis_id"] not in known_h or not _text(o.get("prediction")):
                    errors.append(path + ".outcomes must reference hypotheses and give predictions")
                else:
                    predicted_h.append(o["hypothesis_id"])
                    predictions.append(o["prediction"].strip().casefold())
            if len(set(predicted_h)) != len(predicted_h) or len(set(predictions)) < 2:
                errors.append(path + ".outcomes must distinguish different hypotheses")
        if planned_tests is not None and _id(tid) and tid in planned_tests and outcomes != planned_tests[tid]["outcomes"]:
            errors.append(path + ".outcomes differs from the plan")
        status = test.get("status")
        if not isinstance(status, str) or status not in {"observed", "missing"}:
            errors.append(path + ".status must be observed or missing")
        cited = refs(test.get("claim_ids"), path + ".claim_ids", required=status == "observed")
        for key in ("interpretation", "next_observation", "by", "supports_if", "weakens_if"):
            if not _text(test.get(key)):
                errors.append(path + "." + key + " must be nonempty text")
        sides = []
        for key in ("supports", "weakens"):
            values = test.get(key)
            if not isinstance(values, list) or any(not _id(v) or (known_h is not None and v not in known_h) for v in values):
                errors.append(path + "." + key + " must reference hypotheses")
                values = []
            elif len(set(values)) != len(values):
                errors.append(path + "." + key + " contains duplicates")
            sides.append(set(values))
        if sides[0] & sides[1]:
            errors.append(path + " cannot support and weaken the same hypothesis")
        if status == "observed" and cited and not any(claim_map[c].get("type") in {"fact", "price", "consensus"} for c in cited):
            errors.append(path + " needs a fact/price/consensus observation, not only views or inferences")
        if status == "missing" and (not _text(test.get("gap_reason")) or any(sides) or cited):
            errors.append(path + " missing observation needs gap_reason, empty claims/supports/weakens")
        eligible = {o["hypothesis_id"] for o in outcomes if isinstance(o, dict) and isinstance(o.get("hypothesis_id"), str)} if isinstance(outcomes, list) else set()
        if (sides[0] | sides[1]) - eligible:
            errors.append(path + " verdict references an untested hypothesis")
    if planned_tests is not None and tids != set(planned_tests):
        errors.append("analysis.tests must cover every planned test exactly once")
    models = analysis.get("models")
    if not isinstance(models, list):
        errors.append("analysis.models must be a list")
        models = []
    model_ids, kinds = set(), set()
    scenario_models = {}
    for n, model in enumerate(models):
        path = "analysis.models[%d]" % n
        if not isinstance(model, dict):
            errors.append(path + " must be an object")
            continue
        mid = model.get("id")
        if not _id(mid) or mid in model_ids:
            errors.append(path + ".id must be unique and safe")
        else:
            model_ids.add(mid)
        scenario = model.get("scenario")
        scenario_set = model.get("scenario_set")
        if scenario is not None or scenario_set is not None:
            if not isinstance(scenario, str) or scenario not in SCENARIOS:
                errors.append(path + ".scenario must be bear, base or bull")
            elif not _id(scenario_set):
                errors.append(path + ".scenario_set must be a safe id shared by the scenario models")
            else:
                scenario_models.setdefault(scenario_set, []).append((mid, scenario, model))
        for key in ("description", "currency", "scale", "period", "scope"):
            if not _text(model.get(key)):
                errors.append(path + "." + key + " is required (currency and shares use the same scale)")
        period_window = _period_window(model, path, errors)
        spec = model.get("spec")
        if not isinstance(spec, dict):
            errors.append(path + ".spec must be an object")
            continue
        if isinstance(spec.get("kind"), str):
            kinds.add(spec["kind"])
        input_claims = set()
        assumptions = model.get("assumptions")
        if not isinstance(assumptions, dict):
            errors.append(path + ".assumptions must map input names to reasons")
            assumptions = {}
        inputs = spec.get("inputs")
        if isinstance(inputs, dict):
            expected_assumptions = set()
            for name, value in inputs.items():
                if not isinstance(value, dict):
                    continue
                cids = refs(value.get("claim_ids"), path + ".inputs." + name + ".claim_ids")
                input_claims.update(cids)
                if value.get("role") == "assumption":
                    expected_assumptions.add(name)
                    if not _text(assumptions.get(name)):
                        errors.append(path + ".assumptions." + name + " needs a reason")
                    if any(claim_map[c].get("type") not in {"inference", "view"} for c in cids):
                        errors.append(path + "." + name + " assumption must cite inference/view claims")
                elif value.get("role") == "observed":
                    if any(claim_map[c].get("type") not in {"fact", "price", "consensus"} for c in cids):
                        errors.append(path + "." + name + " observed input must cite fact/price/consensus")
                    else:
                        errors.extend(_metric_input_errors(name, value, cids, claim_map, model.get("scale"), path))
                        errors.extend(_metric_period_errors(name, cids, claim_map, period_window, path))
            if set(assumptions) != expected_assumptions:
                errors.append(path + ".assumptions must match assumption inputs exactly")
            peers = spec.get("peers")
            if peers is not None or spec.get("kind") == "relative_valuation":
                if spec.get("kind") != "relative_valuation":
                    errors.append(path + ".spec.peers is only supported by relative_valuation")
                elif not isinstance(peers, list) or not peers:
                    errors.append(path + ".spec.peers must be a nonempty peer list")
                else:
                    seen_peers = set()
                    for n, peer in enumerate(peers):
                        peer_path = path + ".spec.peers[%d]" % n
                        if not isinstance(peer, dict):
                            errors.append(peer_path + " must be an object")
                            continue
                        name = peer.get("name")
                        if not isinstance(name, str) or not name.strip():
                            errors.append(peer_path + ".name is required")
                        elif name.strip().casefold() in seen_peers:
                            errors.append(peer_path + ".name duplicates another peer")
                        else:
                            seen_peers.add(name.strip().casefold())
                        multiple = peer.get("multiple")
                        if type(multiple) not in (int, float) or not multiple > 0:
                            errors.append(peer_path + ".multiple must be a positive number")
                        peer_refs = refs(peer.get("claim_ids"), peer_path + ".claim_ids")
                        if any(claim_map[c].get("type") not in {"fact", "price", "consensus"} for c in peer_refs):
                            errors.append(peer_path + ".claim_ids must cite fact/price/consensus evidence")
                        input_claims.update(peer_refs)
            if spec.get("kind") == "relative_valuation" and not _text(model.get("peer_set_rationale")):
                errors.append(path + ".peer_set_rationale must explain why the peer set is comparable")
            segments = spec.get("segments")
            if segments is not None or spec.get("kind") == "driver_build":
                if spec.get("kind") != "driver_build":
                    errors.append(path + ".spec.segments is only supported by driver_build")
                elif not isinstance(segments, list) or not segments:
                    errors.append(path + ".spec.segments must be a nonempty segment list")
                else:
                    seen_segments = set()
                    for n, segment in enumerate(segments):
                        seg_path = path + ".spec.segments[%d]" % n
                        if not isinstance(segment, dict):
                            errors.append(seg_path + " must be an object")
                            continue
                        name = segment.get("name")
                        if not isinstance(name, str) or not name.strip():
                            errors.append(seg_path + ".name is required")
                        elif name.strip().casefold() in seen_segments:
                            errors.append(seg_path + ".name duplicates another segment")
                        else:
                            seen_segments.add(name.strip().casefold())
                        base = segment.get("base_revenue")
                        if type(base) not in (int, float) or not base >= 0:
                            errors.append(seg_path + ".base_revenue must be nonnegative")
                        for field in ("volume_growth", "price_growth"):
                            value = segment.get(field)
                            if type(value) not in (int, float) or not value > -1:
                                errors.append(seg_path + "." + field + " must be greater than -1")
                        if type(segment.get("margin")) not in (int, float):
                            errors.append(seg_path + ".margin must be numeric")
                        if "base_margin" in segment and type(segment.get("base_margin")) not in (int, float):
                            errors.append(seg_path + ".base_margin must be numeric when present")
                        seg_refs = refs(segment.get("claim_ids"), seg_path + ".claim_ids")
                        claim_types = {claim_map[c].get("type") for c in seg_refs}
                        if not claim_types & {"fact", "price", "consensus"}:
                            errors.append(seg_path + ".claim_ids must include the observed base")
                        if not claim_types & {"inference", "view"}:
                            errors.append(seg_path + ".claim_ids must include the evidenced drivers")
                        input_claims.update(seg_refs)
            projection = spec.get("projection")
            if projection is not None:
                if spec.get("kind") != "driver_build":
                    errors.append(path + ".spec.projection is only supported by driver_build")
                elif not isinstance(projection, list) or not projection:
                    errors.append(path + ".spec.projection must be a nonempty list")
                elif len(projection) > 10:
                    errors.append(path + ".spec.projection supports at most 10 years")
                else:
                    seen_labels = set()
                    for n, step in enumerate(projection):
                        step_path = path + ".spec.projection[%d]" % n
                        if not isinstance(step, dict):
                            errors.append(step_path + " must be an object")
                            continue
                        label = step.get("label")
                        if not isinstance(label, str) or not label.strip():
                            errors.append(step_path + ".label is required")
                        elif label.strip().casefold() in seen_labels:
                            errors.append(step_path + ".label duplicates another projection year")
                        else:
                            seen_labels.add(label.strip().casefold())
                        growth = step.get("revenue_growth")
                        if type(growth) not in (int, float) or not growth > -1:
                            errors.append(step_path + ".revenue_growth must be greater than -1")
                        if type(step.get("margin")) not in (int, float):
                            errors.append(step_path + ".margin must be numeric")
            if spec.get("kind") in ("reverse_dcf", "relative_valuation"):
                price = inputs.get("price", {})
                price_refs = price.get("claim_ids", []) if isinstance(price, dict) else []
                if not isinstance(price, dict) or price.get("role") != "observed" or not isinstance(price_refs, list) or not price_refs or any(not isinstance(c, str) or c not in claim_map or claim_map[c].get("type") != "price" for c in price_refs):
                    errors.append(path + " valuation model requires an observed price claim")
                if not _text(model.get("instrument")):
                    errors.append(path + ".instrument must identify the priced security")
                if isinstance(sources, dict) and isinstance(price, dict):
                    source_map = {s["id"]: s for s in sources.get("candidates", []) if isinstance(s, dict) and _id(s.get("id"))}
                    for cid in price_refs if isinstance(price_refs, list) else []:
                        if not isinstance(cid, str) or cid not in claim_map:
                            continue
                        for ref in claim_map[cid].get("sources", []):
                            s = source_map.get(ref.get("source_id"), {}) if isinstance(ref, dict) else {}
                            quote = s.get("market_quote", {})
                            if not isinstance(quote, dict) or quote.get("value") != price.get("value") or quote.get("unit") != str(model.get("currency")) + "/share" or quote.get("instrument") != model.get("instrument"):
                                errors.append(path + " price value/unit/instrument differs from quoted evidence")
        output_ids = refs(model.get("output_claim_ids"), path + ".output_claim_ids")
        for cid in output_ids:
            claim = claim_map[cid]
            basis = claim.get("basis")
            if claim.get("type") != "inference" or not isinstance(basis, list) or any(not isinstance(v, str) for v in basis) or not input_claims.issubset(set(basis)):
                errors.append(path + " output inference must cite all input claims in basis")
            if cid in input_claims:
                errors.append(path + " output cannot be its own input")
        try:
            from analysis_models import compute_model
            actual = compute_model(spec)
            if not _same_result(actual, model.get("result")):
                errors.append(path + ".result differs from deterministic recomputation")
        except (ValueError, TypeError, OverflowError, ImportError) as exc:
            errors.append(path + ": " + str(exc))
        sensitivity = spec.get("sensitivity")
        tornado = spec.get("tornado")
        if tornado is None and (not isinstance(sensitivity, list) or not sensitivity):
            errors.append(path + ".spec requires at least one sensitivity sweep or a tornado block")
        if sensitivity is not None and not isinstance(sensitivity, list):
            errors.append(path + ".spec.sensitivity must be a list")
        elif isinstance(sensitivity, list) and sensitivity:
            for sweep in sensitivity:
                values = sweep.get("values") if isinstance(sweep, dict) else None
                if not isinstance(values, list) or len({v for v in values if type(v) in (int, float)}) < 2:
                    errors.append(path + ".spec.sensitivity needs at least two different parameter values")
        if tornado is not None:
            if not isinstance(tornado, dict):
                errors.append(path + ".spec.tornado must be an object")
            else:
                extra = set(tornado) - {"output", "inputs"}
                if extra:
                    errors.append(path + ".spec.tornado has unknown fields: " + ", ".join(sorted(map(str, extra))))
                if not _text(tornado.get("output")):
                    errors.append(path + ".spec.tornado.output must name a model output")
                else:
                    model_result = model.get("result")
                    reported = model_result.get("outputs") if isinstance(model_result, dict) else None
                    target = tornado["output"]
                    if isinstance(reported, dict) and target in reported and not (
                            isinstance(reported[target], dict) and "value" in reported[target]):
                        errors.append(path + ".spec.tornado.output must name a scalar output")
                entries = tornado.get("inputs")
                inputs = spec.get("inputs") if isinstance(spec.get("inputs"), dict) else {}
                if not isinstance(entries, list) or not entries:
                    errors.append(path + ".spec.tornado.inputs must be a nonempty list")
                else:
                    seen_tornado = set()
                    for n, row in enumerate(entries):
                        tpath = path + ".spec.tornado.inputs[%d]" % n
                        if not isinstance(row, dict):
                            errors.append(tpath + " must be an object")
                            continue
                        extra = set(row) - {"input", "low", "high"}
                        if extra:
                            errors.append(tpath + " has unknown fields: " + ", ".join(sorted(map(str, extra))))
                        name = row.get("input")
                        if not isinstance(name, str) or name not in inputs:
                            errors.append(tpath + ".input must name a model input")
                        elif name in seen_tornado:
                            errors.append(tpath + ".input duplicates another tornado input")
                        else:
                            seen_tornado.add(name)
                            if spec.get("kind") == "reverse_dcf" and name in ("growth_low", "growth_high", "years"):
                                errors.append(tpath + " cannot change " + name)
                        low, high = row.get("low"), row.get("high")
                        if type(low) not in (int, float) or type(high) not in (int, float):
                            errors.append(tpath + ".low and .high must be numbers")
                        elif low == high:
                            errors.append(tpath + " requires two different values")
    for set_id, members in scenario_models.items():
        if len(members) < 2:
            errors.append("analysis model scenario_set " + set_id + " needs at least two models")
            continue
        names = [scenario for _, scenario, _ in members]
        if len(set(names)) != len(names):
            errors.append("analysis model scenario_set " + set_id + " duplicates a scenario")
        if "bear" not in names or "bull" not in names:
            errors.append("analysis model scenario_set " + set_id + " must include bear and bull")
        kinds_in_set = set()
        for _, _, model in members:
            spec = model.get("spec")
            if isinstance(spec, dict) and isinstance(spec.get("kind"), str):
                kinds_in_set.add(spec["kind"])
        if len(kinds_in_set) > 1:
            errors.append("analysis model scenario_set " + set_id + " must share one model kind")
        assumption_sets = []
        for _, _, model in members:
            spec = model.get("spec")
            inputs = spec.get("inputs") if isinstance(spec, dict) else None
            names_with_role = set()
            if isinstance(inputs, dict):
                for name, value in inputs.items():
                    if isinstance(value, dict) and value.get("role") == "assumption":
                        names_with_role.add(name)
            if not names_with_role:
                errors.append("analysis model scenario_set " + set_id + " requires at least one assumption input per scenario")
            assumption_sets.append(names_with_role)
        if assumption_sets and any(item != assumption_sets[0] for item in assumption_sets):
            errors.append("analysis model scenario_set " + set_id + " must share the same assumption inputs")
    model_status = analysis.get("model_status")
    if not isinstance(model_status, str) or model_status not in {"computed", "missing", "not_applicable"}:
        errors.append("analysis.model_status must be computed/missing/not_applicable")
    if (model_status == "computed") != bool(models):
        errors.append("analysis.model_status must agree with models")
    if rule and rule["models"]:
        if model_status == "not_applicable":
            errors.append("this question_kind requires a model or an explicit missing-data status")
        if model_status == "computed" and not set(rule["models"]) & kinds:
            errors.append("analysis model kind does not match the research method")
    market = analysis.get("market")
    if not isinstance(market, dict):
        return errors + ["analysis.market must be an object"]
    status = market.get("status")
    if not isinstance(status, str) or status not in {"assessed", "missing", "not_applicable"}:
        errors.append("analysis.market.status must be assessed/missing/not_applicable")
    if not _text(market.get("reason")):
        errors.append("analysis.market.reason is required")
    if price_relevance is True and status == "not_applicable":
        errors.append("price-relevant research cannot mark market not_applicable")
    if price_relevance is False and status != "not_applicable":
        errors.append("non-price research must mark market not_applicable")
    market_refs = refs(market.get("claim_ids"), "analysis.market.claim_ids", required=status == "assessed")
    links = market.get("model_ids")
    if not isinstance(links, list) or any(not isinstance(v, str) or v not in model_ids for v in links):
        errors.append("analysis.market.model_ids must resolve")
        links = []
    elif len(set(links)) != len(links):
        errors.append("analysis.market.model_ids contains duplicates")
    if status == "assessed":
        for key in ("implied_expectation", "research_expectation", "gap", "conditions"):
            if not _text(market.get(key)):
                errors.append("analysis.market." + key + " is required")
        max_age = market.get("price_max_age_hours", 96)
        if isinstance(max_age, bool) or type(max_age) not in (int, float) or not 1 <= max_age <= 8760:
            errors.append("analysis.market.price_max_age_hours must be a number between 1 and 8760")
        elif isinstance(sources, dict):
            errors.extend(_price_age_errors(market, market_refs, claim_map, sources, "analysis.market", max_age))
        if not any(claim_map[c].get("type") == "price" for c in market_refs):
            errors.append("market assessment needs a timestamped price claim")
        for model in models:
            if isinstance(model, dict) and model.get("id") in links:
                output_refs = model.get("output_claim_ids")
                if not isinstance(output_refs, list) or any(not isinstance(v, str) for v in output_refs) or not set(output_refs).issubset(set(market_refs)):
                    errors.append("market assessment must cite linked model output claims")
        if kind == "valuation" and not any(
                m.get("id") in links and isinstance(m.get("spec"), dict)
                and m["spec"].get("kind") in {"reverse_dcf", "relative_valuation"}
                for m in models if isinstance(m, dict)):
            errors.append("valuation market assessment requires a linked reverse_dcf or relative_valuation model")
    elif links or (status == "missing" and market_refs):
        errors.append("missing/not_applicable market must not claim assessed models or missing evidence")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    route_parser = sub.add_parser("route")
    route_parser.add_argument("question_kind", choices=sorted(METHODS))
    check = sub.add_parser("check")
    for name in ("plan", "report", "claims", "sources"):
        check.add_argument("--" + name, required=True, type=Path)
    args = parser.parse_args()
    try:
        if args.cmd == "route":
            result = route(args.question_kind)
        else:
            from render_report import read_document
            from research_run import _validate_bundle
            _validate_bundle(*(read_document(getattr(args, name)) for name in ("report", "claims", "sources", "plan")), require_analysis=True)
            result = {"passed": True, "note": "Contracts and fixed arithmetic verified; economic meaning still needs review."}
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
