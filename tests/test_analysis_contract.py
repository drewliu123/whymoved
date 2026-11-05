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
