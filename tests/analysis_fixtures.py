"""Explicitly fictional analysis fixtures; never fetched or presented as market data."""

import copy

from analysis_contract import route
from analysis_models import MODEL_UNITS, compute_model


def upgrade(report, ledger, plan, kind="change_explanation"):
    plan["analysis_version"] = 1
    plan["hypotheses"] = [
        {"id": "H1", "explanation": "需求兑现进入利润", "discriminating_observation": "利润与交付同比改善"},
        {"id": "H2", "explanation": "收入增长但成本吞噬增量", "discriminating_observation": "收入增而利润降"},
    ]
    outcomes = [{"hypothesis_id": "H1", "prediction": "同口径利润增长"},
                {"hypothesis_id": "H2", "prediction": "同口径利润下降"}]
    design = {"question_kind": kind, "method": route(kind)["method"], "rationale": "按问题选择可检验的方法",
              "baseline": "已披露收入和利润基数", "price_relevance": kind == "valuation",
              "mechanism_chain": ["收入", "利润率", "营业利润", "现金流"],
              "discrimination_tests": [{"id": "T1", "observe": "同口径收入和利润", "source": "公司财报", "by": "下次财报",
                                        "outcomes": outcomes}]}
    plan["research_design"] = design
    for query in plan["queries"]:
        query["test_ids"] = ["T1"]
    report["analysis"] = {
        "version": 1, "question_kind": kind, "method": design["method"], "baseline": design["baseline"],
        "baseline_claim_ids": ["C1"], "price_relevance": design["price_relevance"], "mechanism_chain": copy.deepcopy(design["mechanism_chain"]),
        "hypotheses": [{"id": h["id"], "explanation": h["explanation"]} for h in plan["hypotheses"]],
        "conclusion": report["answer"]["text"], "conclusion_claim_ids": ["C1"],
        "tests": [{"id": "T1", "outcomes": copy.deepcopy(outcomes), "status": "observed", "claim_ids": ["C1"],
                   "interpretation": "单项披露不足以区分两种解释", "supports": [], "weakens": [],
                   "next_observation": "下一次同口径利润", "by": "下次财报", "supports_if": "利润增长", "weakens_if": "利润下降"}],
        "models": [], "model_status": "not_applicable", "model_reason": "本回归样本只作定性比较",
        "market": {"status": "not_applicable", "reason": "本题只核对经营披露，不评估价格", "claim_ids": [], "model_ids": []},
    }
    return report["analysis"]


def add_model(report, ledger, kind="operating_bridge", model_id="M1"):
    values = {
        "operating_bridge": {"base_revenue": 100, "revenue_growth": .3, "base_margin": .2, "scenario_margin": .15},
        "free_cash_flow": {"operating_profit": 20, "tax_rate": .25, "depreciation": 5, "capex": 8, "change_working_capital": 2},
        "dcf": {"free_cash_flow": 10, "growth": .1, "discount_rate": .1, "terminal_growth": .02, "years": 5, "net_debt": 20, "shares": 10},
        "reverse_dcf": {"free_cash_flow": 10, "discount_rate": .1, "terminal_growth": .02, "years": 5, "net_debt": 20, "shares": 10,
                        "price": 15, "growth_low": -.5, "growth_high": 1.0},
    }[kind]
    assumption_id, output_id = "A" + model_id, "O" + model_id
    ledger["claims"].extend([
        {"id": assumption_id, "text": "虚构情景假设，仅用于计算验收，不是市场事实", "type": "inference", "as_of": report["as_of"], "sources": [], "basis": ["C1"]},
        {"id": output_id, "text": "固定模型在给定假设下的结果", "type": "inference", "as_of": report["as_of"], "sources": [], "basis": ["C1", assumption_id]},
    ])
    spec = {"kind": kind, "inputs": {}, "sensitivity": []}
    assumptions = {}
    for name, value in values.items():
        observed = name in {"base_revenue", "operating_profit", "free_cash_flow", "net_debt", "shares", "price"}
        cid = "P1" if name == "price" else "C1" if observed else assumption_id
        spec["inputs"][name] = {"value": value, "unit": MODEL_UNITS[kind][name], "role": "observed" if observed else "assumption", "claim_ids": [cid]}
        if not observed:
            assumptions[name] = "虚构情景参数，用于检验敏感性"
    if kind == "reverse_dcf":
        ledger["claims"][-1]["basis"].append("P1")
    parameter = {"operating_bridge": "scenario_margin", "free_cash_flow": "capex", "dcf": "growth", "reverse_dcf": "discount_rate"}[kind]
    sweep = {"scenario_margin": [.1, .2], "capex": [6, 10], "growth": [.05, .15], "discount_rate": [.09, .11]}[parameter]
    spec["sensitivity"] = [{"input": parameter, "values": sweep}]
    model = {"id": model_id, "instrument": "FICTIONAL", "description": "虚构数据固定模型验收", "currency": "USD", "scale": "million (money and shares)",
             "period": "一年基期；DCF明确期5年", "scope": "虚构同一公司", "spec": spec, "assumptions": assumptions,
             "output_claim_ids": [output_id], "result": compute_model(spec)}
    report["analysis"]["models"].append(model)
    report["analysis"].update(model_status="computed", model_reason="固定计算器重算并比较单参数情景")
    return model


def add_price(report, ledger, sources):
    source = copy.deepcopy(sources["candidates"][0])
    source.update(id="SP", url="https://example.com/fictional-price", publisher="虚构报价验收源", quote="Fictional close 15 USD/share",
                  supports=["price"], evidence_kind="market_quote", origin_id="fictional-price",
                  market_quote={"quoted_at": report["as_of"], "instrument": "FICTIONAL", "outcome": "common equity",
                                "direction": "close", "value": 15, "unit": "USD/share", "quote_type": "close"})
    sources["candidates"].append(source)
    ledger["claims"].append({"id": "P1", "text": "虚构收盘价15美元，仅验收用", "type": "price", "as_of": report["as_of"],
                             "sources": [{"source_id": "SP"}], "basis": [], "price_kind": "close"})
