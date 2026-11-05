#!/usr/bin/env python3
"""Question-to-method routing and verifiable analysis contracts (Python 3.9+).

No text classifier or causal oracle: the researcher explicitly selects question_kind.
Model arithmetic is recomputed; source meaning and assumptions still need review.
"""

import argparse
import json
import re
import sys
from pathlib import Path

METHODS = {
    "change_explanation": {"method": "comparative_attribution", "inputs": ["performance_and_benchmark", "event_timeline", "prior_expectations"], "test": True, "models": []},
    "operating_outlook": {"method": "driver_bridge", "inputs": ["volume_price_or_revenue", "margins", "cash_requirements"], "test": True, "models": ["operating_bridge", "free_cash_flow"]},
    "valuation": {"method": "reverse_valuation", "inputs": ["timestamped_price", "shares_and_net_debt", "cash_flow", "discount_and_terminal_assumptions"], "test": True, "models": ["reverse_dcf"]},
    "event_forecast": {"method": "reference_class_scenarios", "inputs": ["resolution_contract", "reference_class", "conditional_drivers"], "test": True, "models": []},
    "theme_transmission": {"method": "transmission_bottleneck", "inputs": ["demand_to_cash_chain", "cancellation_and_delivery", "profit_capture"], "test": True, "models": []},
    "commitment_check": {"method": "commitment_reconciliation", "inputs": ["dated_commitment", "conditions_and_authority", "observed_action"], "test": False, "models": []},
}
MODEL_KINDS = {"operating_bridge", "free_cash_flow", "dcf", "reverse_dcf"}
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
        for key in ("description", "currency", "scale", "period", "scope"):
            if not _text(model.get(key)):
                errors.append(path + "." + key + " is required (currency and shares use the same scale)")
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
                elif value.get("role") == "observed" and any(claim_map[c].get("type") not in {"fact", "price", "consensus"} for c in cids):
                    errors.append(path + "." + name + " observed input must cite fact/price/consensus")
            if set(assumptions) != expected_assumptions:
                errors.append(path + ".assumptions must match assumption inputs exactly")
            if spec.get("kind") == "reverse_dcf":
                price = inputs.get("price", {})
                price_refs = price.get("claim_ids", []) if isinstance(price, dict) else []
                if not isinstance(price, dict) or price.get("role") != "observed" or not isinstance(price_refs, list) or not price_refs or any(not isinstance(c, str) or c not in claim_map or claim_map[c].get("type") != "price" for c in price_refs):
                    errors.append(path + " reverse_dcf requires an observed price claim")
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
        if not isinstance(sensitivity, list) or not sensitivity:
            errors.append(path + ".spec.sensitivity requires at least one parameter sweep")
        else:
            for sweep in sensitivity:
                values = sweep.get("values") if isinstance(sweep, dict) else None
                if not isinstance(values, list) or len({v for v in values if type(v) in (int, float)}) < 2:
                    errors.append(path + ".spec.sensitivity needs at least two different parameter values")
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
        if not any(claim_map[c].get("type") == "price" for c in market_refs):
            errors.append("market assessment needs a timestamped price claim")
        for model in models:
            if isinstance(model, dict) and model.get("id") in links:
                output_refs = model.get("output_claim_ids")
                if not isinstance(output_refs, list) or any(not isinstance(v, str) for v in output_refs) or not set(output_refs).issubset(set(market_refs)):
                    errors.append("market assessment must cite linked model output claims")
        if kind == "valuation" and not any(m.get("id") in links and isinstance(m.get("spec"), dict) and m["spec"].get("kind") == "reverse_dcf" for m in models if isinstance(m, dict)):
            errors.append("valuation market assessment requires a linked reverse_dcf model")
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
