"""Routing, discriminatory evidence, arithmetic and market-expectations integration."""

import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_reports import AS_OF, SCRIPTS, documents
from test_research_plan import plan as old_plan
from analysis_fixtures import add_model, add_price, upgrade
import analysis_contract
import analysis_models
import render_report
import research_run
from research_plan import validate_plan


def bundle(kind="change_explanation"):
    report, ledger, sources = documents()
    plan = old_plan()
    for key in ("question", "type", "task", "as_of"):
        plan[key] = report[key]
    upgrade(report, ledger, plan, kind)
    if kind in {"operating_outlook", "valuation"}:
        report["analysis"].update(model_status="missing", model_reason="缺少足够的配对财务数据")
    if kind == "valuation":
        report["analysis"]["market"].update(status="missing", reason="缺少可用价格与估值输入")
    return report, ledger, sources, plan


def priced_bundle():
    report, ledger, sources, plan = bundle("valuation")
    add_price(report, ledger, sources)
    model = add_model(report, ledger, "reverse_dcf")
    implied = model["result"]["outputs"]["implied_growth"]["value"]
    report["analysis"]["market"] = {"status": "assessed", "reason": "在显式折现和终值假设下反推增长",
        "claim_ids": ["P1", "OM1", "AM1"], "model_ids": ["M1"],
        "implied_expectation": "虚构价格在给定模型下隐含增长率为%.6f" % implied,
        "research_expectation": "研究使用10%的增长情景，不是已校准预测", "gap": "比较研究情景和隐含要求，差异依赖折现与终值假设",
        "conditions": "后续现金流和折现率变化时重算"}
    return report, ledger, sources, plan


def comps_bundle():
    report, ledger, sources, plan = bundle("valuation")
    add_price(report, ledger, sources)
    model = add_model(report, ledger, "relative_valuation")
    median = model["result"]["outputs"]["per_share_median"]["value"]
    report["analysis"]["market"] = {"status": "assessed", "reason": "在选定可比公司倍数下比较隐含价值",
        "claim_ids": ["P1", "OM1"], "model_ids": ["M1"],
        "implied_expectation": "可比公司中位倍数对目标指标隐含每股%.6f" % median,
        "research_expectation": "研究者认为可比集有限，只把区间当作参照而非估值结论",
        "gap": "当前价格与中位隐含价值的差异取决于可比集选择与目标指标口径",
        "conditions": "可比公司倍数或目标指标修正时重算"}
    return report, ledger, sources, plan


def summary_bundle():
    """Valuation bundle with DCF, comps and reverse DCF plus a method summary."""
    report, ledger, sources, plan = priced_bundle()
    add_model(report, ledger, "dcf", model_id="M2")
    add_model(report, ledger, "relative_valuation", model_id="M3")
    report["valuation_summary"] = {
        "rows": [
            {"model_id": "M2", "label": "DCF 基准情形", "metric": "per_share"},
            {"model_id": "M3", "label": "可比公司倍数", "metric": "per_share"},
            {"model_id": "M1", "label": "反向DCF隐含增长", "metric": "implied_growth"},
        ],
        "note": "不同方法的区间口径不同，不能直接相加。",
    }
    return report, ledger, sources, plan


def scenario_bundle():
    report, ledger, sources, plan = bundle("operating_outlook")
    bear = add_model(report, ledger, "operating_bridge", model_id="M1")
    bull = add_model(report, ledger, "operating_bridge", model_id="M2")
    bear.update(scenario="bear", scenario_set="S1")
    bull.update(scenario="bull", scenario_set="S1")
    bull["spec"]["inputs"]["scenario_margin"]["value"] = .3
    bull["result"] = analysis_models.compute_model(bull["spec"])
    return report, ledger, sources, plan


class AnalysisContractTests(unittest.TestCase):
    def check(self, data):
        research_run._validate_bundle(*data, require_analysis=True)

    def test_six_question_routes(self):
        self.assertEqual(len(analysis_contract.METHODS), 6)
        for kind in analysis_contract.METHODS:
            data = bundle(kind)
            self.assertEqual(validate_plan(data[3]), [], kind)
            self.check(data)
            self.assertTrue(analysis_contract.route(kind)["inputs"])
        for bad in ("anything", [], None):
            with self.assertRaises(ValueError):
                analysis_contract.route(bad)

    def test_method_mismatch_baseline_and_chain(self):
        for field, value in (("method", "freeform"), ("baseline", ""), ("rationale", ""), ("mechanism_chain", ["cash"])):
            data = bundle()
            data[3]["research_design"][field] = value
            self.assertTrue(validate_plan(data[3]), field)
        data = bundle(); data[0]["analysis"]["baseline"] = "different baseline"
        with self.assertRaisesRegex(ValueError, "differs from research_design"):
            self.check(data)

    def test_competing_predictions_and_linked_queries(self):
        for mutate in (
            lambda p: p["hypotheses"].pop(),
            lambda p: p["hypotheses"][1].update(explanation=p["hypotheses"][0]["explanation"]),
            lambda p: p["queries"][0].update(test_ids=[]),
            lambda p: p["research_design"]["discrimination_tests"][0]["outcomes"][1].update(prediction="同口径利润增长"),
            lambda p: p["research_design"]["discrimination_tests"][0]["outcomes"][1].update(hypothesis_id="H404"),
        ):
            data = bundle(); mutate(data[3])
            self.assertTrue(validate_plan(data[3]))

    def test_test_coverage_drift_and_invented_verdicts(self):
        for mutate in (
            lambda a: a.update(tests=[]),
            lambda a: a["tests"][0].update(id="T404"),
            lambda a: a["tests"][0].update(supports=["H404"]),
            lambda a: a["tests"][0].update(supports=["H1"], weakens=["H1"]),
            lambda a: a["tests"][0]["outcomes"][0].update(prediction="changed after seeing result"),
            lambda a: a["hypotheses"][0].update(explanation="changed hypothesis"),
            lambda a: a["tests"][0].update(by=""),
        ):
            data = bundle(); mutate(data[0]["analysis"])
            with self.assertRaises(ValueError):
                self.check(data)

    def test_missing_test_cannot_support_or_weaken(self):
        data = bundle(); test = data[0]["analysis"]["tests"][0]
        test.update(status="missing", claim_ids=[], supports=[], weakens=[], gap_reason="公司未披露")
        self.check(data)
        for key, value in (("supports", ["H1"]), ("claim_ids", ["C1"]), ("gap_reason", "")):
            bad = copy.deepcopy(data); bad[0]["analysis"]["tests"][0][key] = value
            with self.assertRaises(ValueError):
                self.check(bad)

    def test_standalone_verdict_requires_tested_hypothesis(self):
        data = bundle()
        analysis = data[0]["analysis"]
        analysis["hypotheses"].append({"id": "H3", "explanation": "另一种尚未检验的解释"})
        for side in ("supports", "weakens"):
            bad = copy.deepcopy(data)
            bad[0]["analysis"]["tests"][0].update(supports=[], weakens=[])
            bad[0]["analysis"]["tests"][0][side] = ["H3"]
            errors = render_report.validate_report(*bad[:3])
            self.assertTrue(any("untested hypothesis" in e for e in errors))

    def test_standalone_explanations_must_be_distinct(self):
        data = bundle()
        hypotheses = data[0]["analysis"]["hypotheses"]
        hypotheses[1]["explanation"] = "  " + hypotheses[0]["explanation"] + "  "
        errors = render_report.validate_report(*data[:3])
        self.assertTrue(any("distinct competing hypotheses" in e for e in errors))

    def test_model_is_a_calculation_reference_through_archive(self):
        data = bundle("operating_outlook")
        add_model(data[0], data[1])
        data[1]["claims"][-1]["calculation_id"] = "M1"
        data[1]["claims"][-1]["calculation_ids"] = ["M1"]
        finding = data[0]["findings"][0]
        finding["increment"]["kind"] = "calculation"
        finding["calculation_ids"] = ["M1"]
        finding["claim_ids"] = ["OM1"]
        self.check(data)
        for render in (render_report.render_markdown, render_report.render_html):
            self.assertIn("M1", render(*data[:3]))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            paths = []
            for name, document in zip(("report", "claims", "sources", "plan"), data):
                path = root / (name + ".json")
                path.write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")
                paths.append(path)
            archived = research_run.archive_run(*paths, home=root / "home")
            self.assertEqual(research_run.load_run(archived["run_id"], root / "home")["report"]["findings"][0]["calculation_ids"], ["M1"])
        bad = copy.deepcopy(data)
        bad[0]["calculations"] = [{"id": "M1"}]
        self.assertTrue(any("collide" in e for e in render_report.validate_report(*bad[:3])))

    def test_model_metadata_changes_require_comparability_disclosure(self):
        data = bundle("operating_outlook")
        add_model(data[0], data[1])
        parent = dict(zip(("report", "claims", "sources", "plan"), copy.deepcopy(data)))
        parent["manifest"] = {"run_id": "parent"}
        for field, value in (("currency", "EUR"), ("scale", "billion"), ("instrument", "OTHER")):
            bad = copy.deepcopy(data)
            bad[0]["analysis"]["models"][0][field] = value
            bad[0]["update"] = {"judgment_changed": False, "reason": "口径更新", "comparability": {"status": "comparable", "reason": "错误地声称可比"}}
            with self.assertRaisesRegex(ValueError, "mixed or not_comparable"):
                research_run.compare_run(parent, *bad)
            bad[0]["update"]["comparability"]["status"] = "mixed"
            diff = research_run.compare_run(parent, *bad)
            self.assertTrue(any(issue["path"].endswith("." + field) for issue in diff["comparability_issues"]))

    def test_model_recomputed_and_assumptions_separate(self):
        data = bundle("operating_outlook")
        model = add_model(data[0], data[1])
        self.check(data)
        self.assertAlmostEqual(model["result"]["outputs"]["profit"]["value"], 19.5)
        for mutate in (
            lambda m: m["result"]["outputs"]["profit"].update(value=25),
            lambda m: m["spec"]["inputs"]["scenario_margin"].update(role="observed"),
            lambda m: m.update(assumptions={}),
            lambda m: m["spec"].update(sensitivity=[]),
            lambda m: m.update(scope=""),
            lambda m: m.update(output_claim_ids=["C1"]),
        ):
            bad = copy.deepcopy(data); mutate(bad[0]["analysis"]["models"][0])
            with self.assertRaises(ValueError):
                self.check(bad)

    def test_model_output_basis_must_include_every_input(self):
        data = bundle("operating_outlook"); add_model(data[0], data[1])
        data[1]["claims"][-1]["basis"] = ["C1"]
        with self.assertRaisesRegex(ValueError, "all input claims"):
            self.check(data)

    def test_required_model_can_be_missing_not_not_applicable(self):
        data = bundle("operating_outlook"); self.check(data)
        data[0]["analysis"].update(model_status="not_applicable")
        with self.assertRaisesRegex(ValueError, "requires a model"):
            self.check(data)
        data = bundle("valuation"); add_model(data[0], data[1], "dcf")
        with self.assertRaisesRegex(ValueError, "does not match"):
            self.check(data)

    def test_market_reverse_valuation_and_missing_price(self):
        data = priced_bundle(); self.check(data)
        for mutate in (
            lambda a: a["market"].update(claim_ids=["C1"]),
            lambda a: a["market"].update(model_ids=[]),
            lambda a: a["market"].update(gap=""),
            lambda a: a.update(price_relevance=False),
            lambda a: a["market"].update(status="not_applicable"),
            lambda a: a["models"][0]["spec"]["inputs"]["price"].update(claim_ids=["C1"]),
        ):
            bad = copy.deepcopy(data); mutate(bad[0]["analysis"])
            with self.assertRaises(ValueError):
                self.check(bad)

    def test_valuation_summary_reads_frozen_model_outputs(self):
        data = summary_bundle()
        self.check(data)
        for render in (render_report.render_markdown, render_report.render_html):
            text = render(*data[:3]).replace("\\", "")
            for word in ("估值汇总", "方法区间对照", "DCF 基准情形", "可比公司倍数",
                         "反向DCF隐含增长", "每股价值", "隐含增长率", "参考现价",
                         "不跨方法加权", "不能直接相加"):
                self.assertIn(word, text)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            paths = []
            for name, document in zip(("report", "claims", "sources", "plan"), data):
                path = root / (name + ".json")
                path.write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")
                paths.append(path)
            archived = research_run.archive_run(*paths, home=root / "home")
            loaded = research_run.load_run(archived["run_id"], root / "home")
            self.assertEqual(loaded["report"]["valuation_summary"], data[0]["valuation_summary"])
            self.assertIn("估值汇总", (Path(archived["path"]) / "report.md").read_text())

    def test_valuation_summary_cannot_carry_its_own_numbers(self):
        for mutate in (
            lambda s: s["rows"][0].update(low=1),
            lambda s: s["rows"][0].update(model_id="M404"),
            lambda s: s["rows"].append(dict(s["rows"][0])),
            lambda s: s["rows"][0].update(metric="implied_growth"),
            lambda s: s["rows"][0].pop("label"),
            lambda s: s.update(note=1),
            lambda s: s.update(extra=1),
            lambda s: s.update(rows=[]),
        ):
            data = summary_bundle()
            mutate(data[0]["valuation_summary"])
            with self.assertRaises(ValueError):
                self.check(data)

    def test_valuation_summary_rejects_non_valuation_models_and_price_drift(self):
        data = summary_bundle()
        data[0]["valuation_summary"]["rows"].append(
            {"model_id": "M404", "label": "缺失模型", "metric": "per_share"})
        with self.assertRaises(ValueError):
            self.check(data)
        data = summary_bundle()
        data[0]["analysis"]["models"][2]["spec"]["inputs"]["price"]["value"] = 16
        data[0]["analysis"]["models"][2]["result"] = analysis_models.compute_model(
            data[0]["analysis"]["models"][2]["spec"])
        with self.assertRaisesRegex(ValueError, "one observed price"):
            self.check(data)
        data = summary_bundle()
        data[0]["analysis"]["models"].append({"id": "M9", "spec": {"kind": "operating_bridge"}})
        data[0]["valuation_summary"]["rows"].append(
            {"model_id": "M9", "label": "经营桥", "metric": "per_share"})
        with self.assertRaises(ValueError):
            self.check(data)

    def test_tornado_replaces_sensitivity_and_renders_ranked(self):
        data = bundle("operating_outlook")
        model = add_model(data[0], data[1], "operating_bridge")
        spec = model["spec"]
        spec["sensitivity"] = []
        spec["tornado"] = {"output": "profit", "inputs": [
            {"input": "scenario_margin", "low": .1, "high": .2},
            {"input": "revenue_growth", "low": .2, "high": .4}]}
        model["result"] = analysis_models.compute_model(spec)
        self.check(data)
        for render in (render_report.render_markdown, render_report.render_html):
            text = render(*data[:3]).replace("\\", "")
            for word in ("龙卷风敏感性（按影响排序）", "变动幅度", "scenario_margin", "revenue_growth", "不是联合情景"):
                self.assertIn(word, text)

    def test_tornado_validation_in_contract(self):
        for mutate in (
            lambda s: s.update(tornado={"output": "profit", "inputs": [{"input": "missing", "low": 1, "high": 2}]}),
            lambda s: s.update(tornado={"output": "profit", "inputs": [{"input": "growth", "low": 1, "high": 1}]}),
            lambda s: s.update(tornado={"output": "profit", "inputs": []}),
            lambda s: s.update(tornado={"output": "", "inputs": [{"input": "growth", "low": 1, "high": 2}]}),
            lambda s: s.update(tornado={"output": "profit", "inputs": [{"input": "growth", "low": 1, "high": 2}], "extra": 1}),
            lambda s: s.update(tornado={"output": "profit", "inputs": [{"input": "growth", "low": 1, "high": 2},
                                                                      {"input": "growth", "low": 3, "high": 4}]}),
        ):
            data = bundle("operating_outlook")
            model = add_model(data[0], data[1], "operating_bridge")
            model["spec"]["sensitivity"] = []
            mutate(model["spec"])
            with self.assertRaises(ValueError):
                self.check(data)

    def test_empty_sensitivity_without_tornado_is_rejected(self):
        data = bundle("operating_outlook")
        add_model(data[0], data[1], "operating_bridge")
        data[0]["analysis"]["models"][0]["spec"]["sensitivity"] = []
        with self.assertRaisesRegex(ValueError, "sensitivity sweep or a tornado"):
            self.check(data)

    def test_tornado_tampering_fails_recomputation(self):
        data = bundle("operating_outlook")
        model = add_model(data[0], data[1], "operating_bridge")
        model["spec"]["sensitivity"] = []
        model["spec"]["tornado"] = {"output": "profit", "inputs": [
            {"input": "scenario_margin", "low": .1, "high": .2}]}
        model["result"] = analysis_models.compute_model(model["spec"])
        model["result"]["tornado"][0]["swing"] = 999
        with self.assertRaisesRegex(ValueError, "recomputation"):
            self.check(data)

    def test_scenario_set_requires_bear_and_bull_and_renders(self):
        data = scenario_bundle()
        self.check(data)
        for render in (render_report.render_markdown, render_report.render_html):
            text = render(*data[:3]).replace("\\", "")
            for word in ("[情景 bear]", "[情景 bull]", "情景对比：S1", "情景输出对照", "不是概率加权"):
                self.assertIn(word, text)

    def test_scenario_set_failures(self):
        def mutate(fn):
            data = scenario_bundle()
            fn(data[0]["analysis"]["models"])
            return data
        cases = [
            lambda models: models[0].update(scenario="sideways"),
            lambda models: models[1].pop("scenario_set"),
            lambda models: models[0].pop("scenario"),
            lambda models: models[1].update(scenario="bear"),
            lambda models: models[1].update(scenario="base"),
            lambda models: models[0].update(scenario_set="S2"),
            lambda models: (models[1].update(scenario_set="S2"), models[0].update(scenario_set="S3")),
        ]
        for fn in cases:
            data = mutate(fn)
            with self.assertRaises(ValueError):
                self.check(data)

    def test_scenario_set_must_share_kind_and_assumptions(self):
        data = scenario_bundle()
        other = add_model(data[0], data[1], "dcf", model_id="M3")
        other.update(scenario="base", scenario_set="S1")
        with self.assertRaisesRegex(ValueError, "share one model kind"):
            self.check(data)

        data = scenario_bundle()
        bull = data[0]["analysis"]["models"][1]
        bull["spec"]["inputs"]["revenue_growth"] = {"value": .3, "unit": "ratio", "role": "observed", "claim_ids": ["C1"]}
        bull["assumptions"].pop("revenue_growth")
        with self.assertRaisesRegex(ValueError, "same assumption inputs"):
            self.check(data)

        data = scenario_bundle()
        model = data[0]["analysis"]["models"][0]
        model.pop("scenario")
        model.pop("scenario_set")
        for name, value in (("revenue_growth", .3), ("scenario_margin", .15), ("base_margin", .2)):
            model["spec"]["inputs"][name] = {"value": value, "unit": "ratio", "role": "observed", "claim_ids": ["C1"]}
        model["assumptions"] = {}
        model["result"] = analysis_models.compute_model(model["spec"])
        model.update(scenario="bear", scenario_set="S1")
        with self.assertRaisesRegex(ValueError, "at least one assumption input"):
            self.check(data)

    def attach_metric(self, data, claim_id, **metric):
        block = {"name": "revenue", "value": 100, "unit": "USD million", "period_type": "fy",
                 "period_start": "2025-01-01", "period_end": "2025-12-31", "entity": "EXAMPLE",
                 "currency": "USD", "scale": "million"}
        block.update(metric)
        if block.get("period_type") == "instant":
            block.pop("period_start", None)
        for claim in data[1]["claims"]:
            if claim.get("id") == claim_id:
                claim["metric"] = block
                return
        raise AssertionError(claim_id)

    def test_model_input_metric_coherence(self):
        data = bundle("operating_outlook")
        add_model(data[0], data[1], "operating_bridge")
        self.attach_metric(data, "C1")
        self.check(data)
        for mutate, expected in (
            (lambda d: self.attach_metric(d, "C1", value=120), "differs from claim C1 metric"),
            (lambda d: self.attach_metric(d, "C1", unit="ratio"), "unit currency differs from the metric unit"),
            (lambda d: self.attach_metric(d, "C1", scale="thousand"), "differs from claim C1 metric"),
        ):
            bad = bundle("operating_outlook")
            add_model(bad[0], bad[1], "operating_bridge")
            mutate(bad)
            with self.assertRaisesRegex(ValueError, expected):
                self.check(bad)

    def test_model_period_window_checks_evidence_dates(self):
        data = bundle("operating_outlook")
        add_model(data[0], data[1], "operating_bridge")
        self.attach_metric(data, "C1")
        data[0]["analysis"]["models"][0]["period_window"] = {
            "start": "2025-01-01", "end": "2025-12-31", "period_type": "fy"}
        self.check(data)
        bad = bundle("operating_outlook")
        add_model(bad[0], bad[1], "operating_bridge")
        self.attach_metric(bad, "C1", period_start="2024-01-01", period_end="2024-12-31")
        bad[0]["analysis"]["models"][0]["period_window"] = {
            "start": "2025-01-01", "end": "2025-12-31", "period_type": "fy"}
        with self.assertRaisesRegex(ValueError, "before the model period window"):
            self.check(bad)
        bad = bundle("operating_outlook")
        add_model(bad[0], bad[1], "operating_bridge")
        self.attach_metric(bad, "C1", period_type="quarter",
                           period_start="2025-01-01", period_end="2025-03-31")
        bad[0]["analysis"]["models"][0]["period_window"] = {
            "start": "2025-01-01", "end": "2025-12-31", "period_type": "fy"}
        with self.assertRaisesRegex(ValueError, "metric period_type quarter"):
            self.check(bad)

    def test_model_period_window_shape(self):
        for window in ({"start": "2025-02-01", "end": "2025-01-01"},
                       {"start": "nope", "end": "2025-01-01"},
                       {"start": "2025-01-01", "end": "2025-12-31", "period_type": "half"},
                       {"start": "2025-01-01", "end": "2025-12-31", "extra": 1},
                       "nope"):
            data = bundle("operating_outlook")
            add_model(data[0], data[1], "operating_bridge")
            data[0]["analysis"]["models"][0]["period_window"] = window
            with self.subTest(window=window), self.assertRaises(ValueError):
                self.check(data)

    def test_unparseable_scale_skips_instead_of_guessing(self):
        data = bundle("operating_outlook")
        add_model(data[0], data[1], "operating_bridge")
        self.attach_metric(data, "C1", value=999999)
        data[0]["analysis"]["models"][0]["scale"] = "same scale as the statement"
        self.check(data)

    def shares_bundle(self, metric_value):
        data = comps_bundle()
        ledger = data[1]
        ledger["claims"].append({"id": "C9", "text": "虚构摊薄股本", "type": "fact",
                                 "as_of": data[0]["as_of"], "sources": [{"source_id": "S1"}],
                                 "metric": {"name": "shares", "value": metric_value, "unit": "million shares",
                                            "period_type": "instant", "period_end": data[0]["as_of"],
                                            "entity": "EXAMPLE", "scale": "million"}})
        model = data[0]["analysis"]["models"][0]
        model["spec"]["inputs"]["shares"]["claim_ids"] = ["C9"]
        model["result"] = analysis_models.compute_model(model["spec"])
        for claim in ledger["claims"]:
            if claim.get("id") == "OM1":
                claim["basis"].append("C9")
        return data

    def test_shares_and_per_share_coherence(self):
        self.check(self.shares_bundle(10))
        with self.assertRaisesRegex(ValueError, "differs from claim C9 metric"):
            self.check(self.shares_bundle(12))

        data = priced_bundle()
        self.attach_metric(data, "P1", name="price", value=15, unit="USD/share",
                           period_type="instant", period_end=data[0]["as_of"])
        self.check(data)
        bad = priced_bundle()
        self.attach_metric(bad, "P1", name="price", value=16, unit="USD/share",
                           period_type="instant", period_end=bad[0]["as_of"])
        with self.assertRaisesRegex(ValueError, "differs from claim P1 metric"):
            self.check(bad)

    def test_driver_build_supports_operating_outlook(self):
        data = bundle("operating_outlook")
        model = add_model(data[0], data[1], "driver_build")
        self.check(data)
        self.assertEqual(model["result"]["outputs"]["segment_count"]["value"], 2)
        self.assertAlmostEqual(model["result"]["outputs"]["revenue"]["value"], 161.4)
        for render in (render_report.render_markdown, render_report.render_html):
            text = render(*data[:3]).replace("\\", "")
            for word in ("分部驱动", "虚构分部甲", "volume_effect", "incremental_margin"):
                self.assertIn(word, text)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            paths = []
            for name, document in zip(("report", "claims", "sources", "plan"), data):
                path = root / (name + ".json")
                path.write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")
                paths.append(path)
            archived = research_run.archive_run(*paths, home=root / "home")
            loaded = research_run.load_run(archived["run_id"], root / "home")
            self.assertEqual(loaded["report"]["analysis"]["models"][0]["spec"]["segments"],
                             data[0]["analysis"]["models"][0]["spec"]["segments"])

    def test_driver_build_requires_evidenced_segments(self):
        for mutate in (
            lambda m: m["spec"].pop("segments"),
            lambda m: m["spec"].update(segments=[]),
            lambda m: m["spec"]["segments"][0].pop("claim_ids"),
            lambda m: m["spec"]["segments"][0].update(claim_ids=["AM1"]),
            lambda m: m["spec"]["segments"][0].update(claim_ids=["C1"]),
            lambda m: m["spec"]["segments"][0].update(base_revenue=-1),
            lambda m: m["spec"]["segments"][0].update(volume_growth=-1),
            lambda m: m["spec"]["segments"][0].update(margin="0.2"),
            lambda m: m["spec"]["segments"][0].update(name=m["spec"]["segments"][1]["name"]),
        ):
            data = bundle("operating_outlook")
            add_model(data[0], data[1], "driver_build")
            mutate(data[0]["analysis"]["models"][0])
            with self.assertRaises(ValueError):
                self.check(data)

    def test_segments_are_rejected_outside_driver_build(self):
        data = bundle("operating_outlook")
        add_model(data[0], data[1], "operating_bridge")
        data[0]["analysis"]["models"][0]["spec"]["segments"] = [
            {"name": "A", "base_revenue": 1, "volume_growth": 0, "price_growth": 0,
             "margin": 0, "claim_ids": ["C1", "AM1"]}]
        with self.assertRaisesRegex(ValueError, "only supported"):
            self.check(data)

    def test_driver_build_result_cannot_be_forged(self):
        data = bundle("operating_outlook")
        add_model(data[0], data[1], "driver_build")
        data[0]["analysis"]["models"][0]["result"]["outputs"]["revenue"]["value"] = 170
        with self.assertRaisesRegex(ValueError, "recomputation"):
            self.check(data)

    def test_relative_valuation_supports_valuation_question(self):
        data = comps_bundle()
        self.check(data)
        model = data[0]["analysis"]["models"][0]
        self.assertEqual(model["spec"]["kind"], "relative_valuation")
        self.assertEqual(model["result"]["outputs"]["peer_count"]["value"], 3)
        for render in (render_report.render_markdown, render_report.render_html):
            text = render(*data[:3]).replace("\\", "")
            for word in ("可比公司倍数", "虚构可比甲", model["peer_set_rationale"], "peer_multiple_median"):
                self.assertIn(word, text)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            paths = []
            for name, document in zip(("report", "claims", "sources", "plan"), data):
                path = root / (name + ".json")
                path.write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")
                paths.append(path)
            archived = research_run.archive_run(*paths, home=root / "home")
            loaded = research_run.load_run(archived["run_id"], root / "home")
            self.assertEqual(loaded["report"]["analysis"]["models"][0]["spec"]["peers"],
                             data[0]["analysis"]["models"][0]["spec"]["peers"])
            self.assertIn("可比公司倍数", (Path(archived["path"]) / "report.md").read_text())

    def test_relative_valuation_requires_evidenced_peer_set(self):
        for mutate in (
            lambda m: m.pop("peer_set_rationale"),
            lambda m: m.update(peer_set_rationale=""),
            lambda m: m["spec"]["peers"][0].pop("claim_ids"),
            lambda m: m["spec"]["peers"][0].update(claim_ids=[]),
            lambda m: m["spec"]["peers"][0].update(claim_ids=["OM1"]),
            lambda m: m["spec"]["peers"][1].update(name=m["spec"]["peers"][0]["name"].upper()),
            lambda m: m["spec"]["peers"][0].update(multiple=0),
            lambda m: m["spec"]["peers"][0].update(unit=1),
        ):
            data = comps_bundle()
            mutate(data[0]["analysis"]["models"][0])
            with self.assertRaises(ValueError):
                self.check(data)

    def test_relative_valuation_result_cannot_be_forged(self):
        data = comps_bundle()
        data[0]["analysis"]["models"][0]["result"]["outputs"]["per_share_median"]["value"] = 1
        with self.assertRaisesRegex(ValueError, "recomputation"):
            self.check(data)
        data = comps_bundle()
        del data[0]["analysis"]["models"][0]["result"]["outputs"]["peer_count"]
        with self.assertRaisesRegex(ValueError, "recomputation"):
            self.check(data)

    def test_relative_valuation_output_basis_must_include_peer_claims(self):
        data = comps_bundle()
        data[1]["claims"][-1]["basis"] = ["P1"]
        with self.assertRaisesRegex(ValueError, "all input claims"):
            self.check(data)

    def test_peers_are_rejected_outside_relative_valuation(self):
        data = priced_bundle()
        data[0]["analysis"]["models"][0]["spec"]["peers"] = [{"name": "A", "multiple": 10, "claim_ids": ["C1"]}]
        with self.assertRaisesRegex(ValueError, "only supported"):
            self.check(data)

    def test_missing_market_is_disclosed_in_both_formats(self):
        data = bundle("valuation"); self.check(data)
        for render in (render_report.render_markdown, render_report.render_html):
            text = render(*data[:3])
            self.assertIn("市场预期尚未评估", text)
            self.assertIn("缺少可用价格与估值输入", text)
            self.assertIn("模型数据缺失", text)

    def test_model_and_market_shared_rendering_and_literal_text(self):
        data = priced_bundle(); data[0]["analysis"]["market"]["gap"] = "<script>alert(1)</script>"
        for render in (render_report.render_markdown, render_report.render_html):
            text = render(*data[:3])
            for word in ("隐含预期", "研究假设", "固定模型重算结果", "单参数敏感性", "币种", "不同解释的事前预测"):
                self.assertIn(word, text)
            self.assertNotIn("<script>alert(1)</script>", text)

    def test_new_archive_requires_analysis_before_any_write(self):
        report, ledger, sources = documents(); plan = old_plan()
        for key in ("question", "type", "task", "as_of"):
            plan[key] = report[key]
        with tempfile.TemporaryDirectory() as tmp:
            paths = []
            for name, doc in zip(("report", "claims", "sources", "plan"), (report, ledger, sources, plan)):
                path = Path(tmp).resolve() / (name + ".json"); path.write_text(json.dumps(doc)); paths.append(path)
            home = Path(tmp).resolve() / "home"
            with self.assertRaisesRegex(ValueError, "new archives require"):
                research_run.archive_run(*paths, home=home)
            self.assertFalse(home.exists())
            # The same old input is valid when loading a pre-upgrade archive.
            research_run._validate_bundle(report, ledger, sources, plan)

    def test_cli_check_route_and_archive_update(self):
        data = priced_bundle()
        with tempfile.TemporaryDirectory() as tmp:
            paths = []
            for name, doc in zip(("report", "claims", "sources", "plan"), data):
                path = Path(tmp).resolve() / (name + ".json"); path.write_text(json.dumps(doc)); paths.append(path)
            command = [sys.executable, str(SCRIPTS / "analysis_contract.py"), "check"]
            for name, path in zip(("report", "claims", "sources", "plan"), paths):
                command.extend(["--" + name, str(path)])
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(json.loads(result.stdout)["passed"])
            home = Path(tmp).resolve() / "home"
            parent = research_run.archive_run(*paths, home=home)
            loaded = research_run.load_run(parent["run_id"], home)
            self.assertEqual(loaded["report"]["analysis"], data[0]["analysis"])
            data[0]["update"] = {"judgment_changed": False, "reason": "只更新下一观察", "comparability": {"status": "comparable", "reason": "口径相同"}}
            data[0]["analysis"]["tests"][0]["next_observation"] = "下一次现金流披露"
            paths[0].write_text(json.dumps(data[0]))
            child = research_run.archive_run(*paths, home=home, parent_run=parent["run_id"])
            self.assertTrue(child["diff"]["analysis_changed"])
            self.assertEqual(research_run.load_run(child["run_id"], home)["manifest"]["parent_run"], parent["run_id"])
            data[0]["analysis"]["models"][0]["result"]["outputs"]["implied_growth"]["value"] = .99
            paths[0].write_text(json.dumps(data[0]))
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("recomputation", result.stderr)

    def test_quote_binding_and_result_types_cannot_be_forged(self):
        for mutate in (
            lambda d: d[2]["candidates"][-1]["market_quote"].update(value=16),
            lambda d: d[2]["candidates"][-1]["market_quote"].update(unit="EUR/share"),
            lambda d: d[0]["analysis"]["models"][0].update(instrument="OTHER"),
            lambda d: d[0]["analysis"]["market"].update(claim_ids=["P1"]),
            lambda d: d[0]["analysis"]["models"][0]["spec"].update(sensitivity=[{"input": "discount_rate", "values": [.1, .1]}]),
        ):
            data = priced_bundle(); mutate(data)
            with self.assertRaises(ValueError):
                self.check(data)
        self.assertFalse(analysis_contract._same_result({"value": 1.0}, {"value": True}))

    def test_four_object_types_archive_and_reload(self):
        for obj_type, kind in (("asset", "valuation"), ("theme", "theme_transmission"),
                               ("event_pricing", "event_forecast"), ("actor", "commitment_check")):
            data = priced_bundle() if obj_type == "asset" else bundle(kind)
            data[0]["type"] = data[3]["type"] = obj_type
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp).resolve(); paths = []
                for name, doc in zip(("report", "claims", "sources", "plan"), data):
                    path = root / (name + ".json"); path.write_text(json.dumps(doc)); paths.append(path)
                result = research_run.archive_run(*paths, home=root / "home")
                loaded = research_run.load_run(result["run_id"], root / "home")
                self.assertEqual(loaded["report"]["type"], obj_type)
                self.assertIn("分析底稿与可复算模型", (Path(result["path"]) / "report.md").read_text())

    def test_old_manifest_remains_readable_without_rewriting(self):
        import hashlib
        report, ledger, sources = documents(); plan = old_plan()
        for key in ("question", "type", "task", "as_of"):
            plan[key] = report[key]
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp).resolve(); run_id = "R20261031T120000Z-012345abcdef"
            root = home / "journal/runs" / run_id; root.mkdir(parents=True)
            files = {}
            for name, doc in zip(("report", "claims", "sources", "plan"), (report, ledger, sources, plan)):
                files[name + ".json"] = json.dumps(doc)
            files["report.md"] = render_report.render_markdown(report, ledger, sources)
            files["report.html"] = render_report.render_html(report, ledger, sources)
            for name, text in files.items():
                (root / name).write_text(text)
            manifest = {"schema_version": 2, "run_id": run_id, "created_at": AS_OF, "as_of": AS_OF,
                        "files": {name: hashlib.sha256(text.encode()).hexdigest() for name, text in files.items()}}
            (root / "manifest.json").write_text(json.dumps(manifest))
            before = {p.name: p.read_bytes() for p in root.iterdir()}
            loaded = research_run.load_run(run_id, home)
            self.assertNotIn("analysis", loaded["report"])
            self.assertEqual(before, {p.name: p.read_bytes() for p in root.iterdir()})

    def test_malformed_analysis_fails_without_traceback(self):
        mutations = [lambda a: a.update(question_kind=[]), lambda a: a.update(model_status=[]),
                     lambda a: a["tests"][0].update(id=[]), lambda a: a["tests"][0].update(outcomes=[{}, {}]),
                     lambda a: a["tests"][0].update(supports=[{}]), lambda a: a["market"].update(status={}),
                     lambda a: a.update(hypotheses=[{}]), lambda a: a.update(baseline_claim_ids=[{}])]
        for mutate in mutations:
            data = bundle(); mutate(data[0]["analysis"])
            self.assertTrue(render_report.validate_report(*data[:3]))


if __name__ == "__main__":
    unittest.main()
