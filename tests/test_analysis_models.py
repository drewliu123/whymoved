import copy
import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from analysis_models import MODEL_UNITS, compute_model


def spec(kind="dcf", **overrides):
    defaults = {
        "operating_bridge": {"base_revenue": 100, "revenue_growth": .2,
                             "base_margin": .2, "scenario_margin": .1},
        "free_cash_flow": {"operating_profit": 100, "tax_rate": .25,
                           "depreciation": 10, "capex": 20, "change_working_capital": 5},
        "dcf": {"free_cash_flow": 100, "growth": .1, "discount_rate": .1,
                "terminal_growth": 0, "years": 2, "net_debt": 100, "shares": 10},
        "reverse_dcf": {"free_cash_flow": 100, "discount_rate": .1,
                        "terminal_growth": 0, "years": 2, "net_debt": 100,
                        "shares": 10, "price": 110, "growth_low": -.5, "growth_high": .5},
        "relative_valuation": {"metric": 100, "net_debt": 20, "shares": 10, "price": 15},
        "driver_build": {"margin_delta": 0},
    }
    values = dict(defaults[kind], **overrides)
    item = {"kind": kind, "inputs": {
        name: {"value": value, "unit": MODEL_UNITS[kind][name],
               "role": "assumption", "claim_ids": []} for name, value in values.items()},
        "sensitivity": []}
    if kind == "relative_valuation":
        item["peers"] = [{"name": "A", "multiple": 8}, {"name": "B", "multiple": 12}]
    if kind == "driver_build":
        item["segments"] = [
            {"name": "A", "base_revenue": 100, "volume_growth": 0.1, "price_growth": 0.05, "margin": 0.2},
            {"name": "B", "base_revenue": 50, "volume_growth": -0.1, "price_growth": 0.02, "margin": 0.1},
        ]
    return item


def value(result, name):
    return result["outputs"][name]["value"]


class ModelTests(unittest.TestCase):
    def test_operating_bridge_revenue_up_profit_down(self):
        result = compute_model(spec("operating_bridge"))
        for name, expected in {"base_profit": 20, "revenue": 120, "profit": 12,
                               "profit_change": -8, "profit_growth": -.4,
                               "revenue_growth_effect": 4, "margin_effect": -12}.items():
            self.assertAlmostEqual(value(result, name), expected, msg=name)
        self.assertAlmostEqual(value(result, "profit_change"),
                               value(result, "revenue_growth_effect") + value(result, "margin_effect"))
        self.assertEqual(result["outputs"]["profit"]["unit"], "currency")

    def test_operating_bridge_loss_to_profit(self):
        result = compute_model(spec("operating_bridge", base_margin=-.2, scenario_margin=.1))
        self.assertAlmostEqual(value(result, "base_profit"), -20)
        self.assertAlmostEqual(value(result, "profit"), 12)
        self.assertAlmostEqual(value(result, "profit_change"), 32)
        self.assertAlmostEqual(value(result, "revenue_growth_effect"), -4)
        self.assertAlmostEqual(value(result, "margin_effect"), 36)
        self.assertNotIn("profit_growth", result["outputs"])

    def test_operating_bridge_profit_to_loss(self):
        result = compute_model(spec("operating_bridge", base_margin=.2, scenario_margin=-.1))
        self.assertAlmostEqual(value(result, "base_profit"), 20)
        self.assertAlmostEqual(value(result, "profit"), -12)
        self.assertAlmostEqual(value(result, "profit_change"), -32)
        self.assertAlmostEqual(value(result, "revenue_growth_effect"), 4)
        self.assertAlmostEqual(value(result, "margin_effect"), -36)
        self.assertAlmostEqual(value(result, "profit_growth"), -1.6)

    def test_operating_bridge_widening_losses(self):
        result = compute_model(spec("operating_bridge", base_margin=-.1, scenario_margin=-.2))
        self.assertAlmostEqual(value(result, "base_profit"), -10)
        self.assertAlmostEqual(value(result, "profit"), -24)
        self.assertAlmostEqual(value(result, "profit_change"), -14)
        self.assertAlmostEqual(value(result, "revenue_growth_effect"), -2)
        self.assertAlmostEqual(value(result, "margin_effect"), -12)
        self.assertNotIn("profit_growth", result["outputs"])

    def test_operating_bridge_margins_outside_zero_to_one(self):
        for base_margin, scenario_margin in ((-2, -1.5), (1.2, 1.5)):
            with self.subTest(base_margin=base_margin, scenario_margin=scenario_margin):
                result = compute_model(spec("operating_bridge", base_margin=base_margin,
                                            scenario_margin=scenario_margin))
                self.assertAlmostEqual(value(result, "profit_change"),
                                       value(result, "revenue_growth_effect") + value(result, "margin_effect"))
        item = spec("operating_bridge", base_margin=-.1)
        item["sensitivity"] = [{"input": "scenario_margin", "values": [-.2, .2]}]
        result = compute_model(item)
        for scenario in result["sensitivity"]:
            self.assertNotIn("profit_growth", scenario["outputs"])
            self.assertAlmostEqual(value(scenario, "profit_change"),
                                   value(scenario, "revenue_growth_effect") + value(scenario, "margin_effect"))

    def test_negative_base_revenue_rejected(self):
        for revenue in (-1, -0.001):
            with self.subTest(revenue=revenue), self.assertRaisesRegex(
                    ValueError, "base_revenue must be nonnegative"):
                compute_model(spec("operating_bridge", base_revenue=revenue))
        item = spec("operating_bridge")
        item["sensitivity"] = [{"input": "base_revenue", "values": [-1]}]
        with self.assertRaisesRegex(ValueError, "base_revenue must be nonnegative"):
            compute_model(item)

    def test_zero_profit_base_omits_growth(self):
        for overrides in ({"base_margin": 0}, {"base_revenue": 0}):
            result = compute_model(spec("operating_bridge", **overrides))
            self.assertNotIn("profit_growth", result["outputs"])
            self.assertEqual(value(result, "base_profit"), 0)
            self.assertAlmostEqual(value(result, "profit_change"), value(result, "profit"))
            self.assertAlmostEqual(value(result, "profit_change"),
                                   value(result, "revenue_growth_effect") + value(result, "margin_effect"))

    def test_fcf_hand_calculation_and_negative_fcf(self):
        self.assertEqual(value(compute_model(spec("free_cash_flow")), "free_cash_flow"), 60)
        result = compute_model(spec("free_cash_flow", operating_profit=-100,
                                    change_working_capital=-10))
        self.assertEqual(value(result, "free_cash_flow"), -75)

    def test_dcf_hand_calculation(self):
        # CF1=110, CF2=121; PVs=100 each; TV=1210, PV(TV)=1000.
        result = compute_model(spec())
        for name, expected in {"enterprise_value": 1200, "equity_value": 1100,
                               "per_share": 110, "terminal_value_share": 5 / 6}.items():
            self.assertAlmostEqual(value(result, name), expected, msg=name)
        self.assertEqual(result["outputs"]["per_share"]["unit"], "currency/share")

    def test_dcf_negative_growth_and_net_cash(self):
        result = compute_model(spec(growth=-.5, terminal_growth=-.1, years=1, net_debt=-20))
        ev = 50 / 1.1 + (50 * .9 / .2) / 1.1
        self.assertAlmostEqual(value(result, "enterprise_value"), ev)
        self.assertAlmostEqual(value(result, "equity_value"), ev + 20)

    def test_negative_valuation_fcf_rejected(self):
        for kind in ("dcf", "reverse_dcf"):
            for fcf in (0, -1):
                with self.subTest(kind=kind, fcf=fcf), self.assertRaisesRegex(ValueError, "free_cash_flow"):
                    compute_model(spec(kind, free_cash_flow=fcf))

    def test_ranges(self):
        cases = [("operating_bridge", "revenue_growth", -1),
                 ("free_cash_flow", "tax_rate", -.1),
                 ("free_cash_flow", "tax_rate", 2), ("free_cash_flow", "capex", -1),
                 ("free_cash_flow", "depreciation", -1), ("dcf", "growth", -1),
                 ("dcf", "discount_rate", 0), ("dcf", "terminal_growth", -1),
                 ("dcf", "terminal_growth", .1), ("dcf", "terminal_growth", .2),
                 ("dcf", "years", 0), ("dcf", "years", 51), ("dcf", "years", 1.5),
                 ("dcf", "shares", 0), ("reverse_dcf", "price", 0),
                 ("reverse_dcf", "growth_low", -1), ("reverse_dcf", "growth_high", -.5)]
        for kind, name, invalid in cases:
            with self.subTest(kind=kind, name=name, invalid=invalid), self.assertRaises(ValueError):
                compute_model(spec(kind, **{name: invalid}))

    def test_numeric_types_and_finiteness_for_all_inputs(self):
        for kind, units in MODEL_UNITS.items():
            for name in units:
                for invalid in (True, False, None, "1", [], {}, math.nan, math.inf, -math.inf, 10 ** 1000):
                    with self.subTest(kind=kind, name=name, invalid=repr(invalid)), self.assertRaises(ValueError):
                        compute_model(spec(kind, **{name: invalid}))

    def test_wrong_units_for_all_inputs(self):
        for kind, units in MODEL_UNITS.items():
            for name in units:
                item = spec(kind)
                item["inputs"][name]["unit"] = "USD"
                with self.subTest(kind=kind, name=name), self.assertRaisesRegex(ValueError, "unit"):
                    compute_model(item)

    def test_required_and_unknown_fields(self):
        for key in ("kind", "inputs"):
            item = spec()
            del item[key]
            with self.assertRaisesRegex(ValueError, "missing"):
                compute_model(item)
        for location in ((), ("inputs",), ("inputs", "growth")):
            item = spec()
            row = item
            for key in location:
                row = row[key]
            row["unknown"] = 1
            with self.assertRaisesRegex(ValueError, "unknown"):
                compute_model(item)
        for name in MODEL_UNITS["dcf"]:
            item = spec()
            del item["inputs"][name]
            with self.assertRaisesRegex(ValueError, "missing"):
                compute_model(item)
        for key in ("value", "unit", "role", "claim_ids"):
            item = spec()
            del item["inputs"]["growth"][key]
            with self.assertRaisesRegex(ValueError, "missing"):
                compute_model(item)

    def test_malformed_objects_and_kind(self):
        for item in (None, [], 1, "dcf", {}, {"kind": [], "inputs": {}},
                     {"kind": "unknown", "inputs": {}}, {"kind": "dcf", "inputs": []}):
            with self.subTest(item=item), self.assertRaises(ValueError):
                compute_model(item)
        item = spec()
        item["inputs"]["growth"] = None
        with self.assertRaises(ValueError):
            compute_model(item)

    def test_metadata_shapes(self):
        for name, invalids in (("role", (None, [], {}, True, "fact", "")),
                               ("claim_ids", (None, "c1", {}, [1], [True], [""], [" "]))):
            for invalid in invalids:
                item = spec()
                item["inputs"]["growth"][name] = invalid
                with self.subTest(name=name, invalid=invalid), self.assertRaises(ValueError):
                    compute_model(item)
        item = spec()
        item["inputs"]["growth"].update(role="observed", claim_ids=["claim-1"])
        compute_model(item)

    def test_overflow_is_readable_value_error(self):
        cases = [spec("operating_bridge", base_revenue=1e308, revenue_growth=1e308),
                 spec("free_cash_flow", operating_profit=1e308, depreciation=1.7e308),
                 spec(free_cash_flow=1e308, growth=1),
                 spec(discount_rate=1e308, years=50),
                 spec(free_cash_flow=1e308, terminal_growth=.09999999999999999),
                 spec("reverse_dcf", price=1e308, shares=1e308)]
        for item in cases:
            with self.subTest(kind=item["kind"]), self.assertRaises(ValueError):
                compute_model(item)

    def test_reverse_roundtrip(self):
        for growth in (-.35, 0, .1, .38):
            forward = compute_model(spec(growth=growth, years=12, terminal_growth=.025))
            item = spec("reverse_dcf", price=value(forward, "per_share"),
                        years=12, terminal_growth=.025)
            result = compute_model(item)
            self.assertAlmostEqual(value(result, "implied_growth"), growth, places=9)
            self.assertLessEqual(abs(value(result, "residual")),
                                 1e-10 * value(result, "target_enterprise_value"))
            solved = compute_model(spec(growth=value(result, "implied_growth"), years=12,
                                        terminal_growth=.025))
            self.assertEqual(value(solved, "enterprise_value"), value(result, "solved_enterprise_value"))

    def test_reverse_endpoints(self):
        for growth in (-.5, .5):
            price = value(compute_model(spec(growth=growth, net_debt=0)), "per_share")
            result = compute_model(spec("reverse_dcf", price=price, net_debt=0))
            self.assertEqual(value(result, "implied_growth"), growth)
            self.assertEqual(value(result, "residual"), 0)

    def test_reverse_no_solution(self):
        for price in (.01, 100000):
            with self.assertRaisesRegex(ValueError, "bracket"):
                compute_model(spec("reverse_dcf", price=price))
        with self.assertRaisesRegex(ValueError, "target enterprise value must be positive"):
            compute_model(spec("reverse_dcf", price=1, net_debt=-100))

    def test_sensitivity_order_isolation_and_no_mutation(self):
        for kind, scenarios in (
                ("operating_bridge", [{"input": "revenue_growth", "values": [0, .1]},
                                      {"input": "scenario_margin", "values": [.3]}]),
                ("free_cash_flow", [{"input": "capex", "values": [0, 100]}]),
                ("dcf", [{"input": "discount_rate", "values": [.15, .2]},
                         {"input": "growth", "values": [0]}]),
                ("reverse_dcf", [{"input": "price", "values": [100, 120]},
                                 {"input": "discount_rate", "values": [.15]}]),
                ("relative_valuation", [{"input": "metric", "values": [90, 110]},
                                        {"input": "shares", "values": [5]}]),
                ("driver_build", [{"input": "margin_delta", "values": [-0.02, 0.02]}])):
            item = spec(kind)
            item["sensitivity"] = scenarios
            original = copy.deepcopy(item)
            result = compute_model(item)
            self.assertEqual(item, original)
            index = 0
            for row in scenarios:
                for scenario_value in row["values"]:
                    expected = spec(kind, **{row["input"]: scenario_value})
                    self.assertEqual(result["sensitivity"][index], {
                        "input": row["input"], "value": scenario_value,
                        "unit": MODEL_UNITS[kind][row["input"]],
                        "outputs": compute_model(expected)["outputs"]})
                    index += 1

    def test_bad_sensitivity(self):
        cases = [None, {}, [None], [{"input": "growth", "values": []}],
                 [{"input": "missing", "values": [1]}], [{"input": [], "values": [1]}],
                 [{"input": "growth"}], [{"input": "growth", "values": [0], "extra": 1}],
                 [{"input": "growth", "values": "0"}],
                 [{"input": "growth", "values": [0]}, {"input": "growth", "values": [.1]}]]
        for invalid in (True, math.inf, math.nan, -1):
            cases.append([{"input": "growth", "values": [invalid]}])
        for scenarios in cases:
            item = spec()
            item["sensitivity"] = scenarios
            with self.subTest(scenarios=scenarios), self.assertRaises(ValueError):
                compute_model(item)
        for name in ("years", "growth_low", "growth_high"):
            item = spec("reverse_dcf")
            item["sensitivity"] = [{"input": name, "values": [1]}]
            with self.assertRaisesRegex(ValueError, "cannot change"):
                compute_model(item)
        item = spec()
        item["sensitivity"] = [{"input": "discount_rate", "values": [0]}]
        with self.assertRaises(ValueError):
            compute_model(item)

    def test_optional_sensitivity(self):
        item = spec()
        del item["sensitivity"]
        self.assertEqual(compute_model(item)["sensitivity"], [])

    def test_cli(self):
        script = Path(__file__).resolve().parents[1] / "scripts" / "analysis_models.py"
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input.json"
            for content, passed in ((json.dumps(spec()), True),
                                    (json.dumps(spec(growth=-1)), False), ("{", False)):
                source.write_text(content, encoding="utf-8")
                process = subprocess.run([sys.executable, str(script), str(source)],
                                         capture_output=True, text=True)
                payload = json.loads(process.stdout)
                self.assertEqual(payload["passed"], passed)
                self.assertEqual(process.returncode == 0, passed)
                if passed:
                    self.assertEqual(payload["result"], compute_model(spec()))
                else:
                    self.assertTrue(payload["errors"])
            self.assertEqual(sorted(p.name for p in Path(directory).iterdir()), ["input.json"])


class TornadoTests(unittest.TestCase):
    def tornado_spec(self, output="per_share", entries=None):
        item = spec("dcf")
        item["sensitivity"] = []
        item["tornado"] = {"output": output, "inputs": entries or [
            {"input": "discount_rate", "low": .08, "high": .12},
            {"input": "growth", "low": .05, "high": .15},
            {"input": "terminal_growth", "low": .0, "high": .02}]}
        return item

    def test_ranked_by_swing_and_outputs_match_forward_runs(self):
        item = self.tornado_spec()
        result = compute_model(item)
        self.assertNotIn("sensitivity", result["outputs"])
        self.assertIn("tornado", result)
        swings = [row["swing"] for row in result["tornado"]]
        self.assertEqual(swings, sorted(swings, reverse=True))
        self.assertEqual({row["input"] for row in result["tornado"]},
                         {"discount_rate", "growth", "terminal_growth"})
        for row in result["tornado"]:
            expected_low = compute_model(spec("dcf", **{row["input"]: row["low"]}))["outputs"]["per_share"]
            expected_high = compute_model(spec("dcf", **{row["input"]: row["high"]}))["outputs"]["per_share"]
            self.assertEqual(row["low_output"], expected_low)
            self.assertEqual(row["high_output"], expected_high)
            self.assertAlmostEqual(row["swing"], abs(expected_high["value"] - expected_low["value"]))
            self.assertEqual(row["output"], "per_share")

    def test_tornado_alone_is_enough_at_the_model_level(self):
        item = self.tornado_spec()
        del item["sensitivity"]
        self.assertIn("tornado", compute_model(item))

    def test_tornado_validation(self):
        cases = [
            lambda t: t.update(output="missing_output"),
            lambda t: t.update(output=""),
            lambda t: t.update(inputs=[]),
            lambda t: t.update(inputs=[{"input": "nope", "low": 1, "high": 2}]),
            lambda t: t.update(inputs=[{"input": "growth", "low": 1, "high": 1}]),
            lambda t: t.update(inputs=[{"input": "growth", "low": "1", "high": 2}]),
            lambda t: t.update(inputs=[{"input": "growth", "low": 1}]),
            lambda t: t.update(inputs=[{"input": "growth", "low": 1, "high": 2, "extra": 1}]),
            lambda t: t.update(extra=1),
            lambda t: t.update(inputs=[{"input": "growth", "low": .1, "high": .2},
                                       {"input": "growth", "low": .3, "high": .4}]),
        ]
        for mutate in cases:
            item = self.tornado_spec()
            mutate(item["tornado"])
            with self.subTest(mutate=mutate), self.assertRaises(ValueError):
                compute_model(item)
        for invalid in ("tornado", [], 1):
            item = self.tornado_spec()
            item["tornado"] = invalid
            with self.assertRaises(ValueError):
                compute_model(item)

    def test_reverse_dcf_cannot_sweep_solver_bounds(self):
        item = spec("reverse_dcf")
        item["sensitivity"] = []
        item["tornado"] = {"output": "implied_growth", "inputs": [{"input": "growth_low", "low": -.4, "high": -.6}]}
        with self.assertRaisesRegex(ValueError, "cannot change"):
            compute_model(item)

    def test_output_missing_at_one_end_is_an_error(self):
        item = spec("operating_bridge")
        item["sensitivity"] = []
        item["tornado"] = {"output": "profit_growth", "inputs": [{"input": "base_margin", "low": .2, "high": -.2}]}
        with self.assertRaisesRegex(ValueError, "not defined at the swept"):
            compute_model(item)


class DriverBuildTests(unittest.TestCase):
    def test_revenue_and_profit_decomposition(self):
        result = compute_model(spec("driver_build"))
        expected = {
            "segment_count": 2, "base_revenue": 150, "revenue": 161.4,
            "revenue_change": 11.4, "volume_effect": 5, "price_effect": 6,
            "interaction_effect": 0.4, "base_profit": 25, "profit": 27.69,
            "profit_change": 2.69, "revenue_growth": 161.4 / 150 - 1,
            "incremental_margin": 2.69 / 11.4,
        }
        for name, number in expected.items():
            self.assertAlmostEqual(value(result, name), number, places=9, msg=name)
        total = (value(result, "volume_effect") + value(result, "price_effect")
                 + value(result, "interaction_effect"))
        self.assertAlmostEqual(total, value(result, "revenue_change"), places=9)
        self.assertAlmostEqual(value(result, "profit_change"),
                               value(result, "profit") - value(result, "base_profit"), places=9)

    def test_margin_delta_flows_through_every_segment(self):
        result = compute_model(spec("driver_build", margin_delta=-0.02))
        self.assertAlmostEqual(value(result, "profit"), 27.69 - 0.02 * 161.4, places=9)
        self.assertAlmostEqual(value(result, "revenue"), 161.4, places=9)

    def test_single_segment_and_zero_growth(self):
        item = spec("driver_build")
        item["segments"] = [{"name": "only", "base_revenue": 100, "volume_growth": 0,
                             "price_growth": 0, "margin": 0.2}]
        result = compute_model(item)
        self.assertEqual(value(result, "revenue"), 100)
        self.assertEqual(value(result, "revenue_change"), 0)
        self.assertNotIn("incremental_margin", result["outputs"])
        self.assertEqual(value(result, "revenue_growth"), 0)
        self.assertAlmostEqual(value(result, "profit"), 20)

    def test_base_margin_separates_base_and_scenario_profit(self):
        item = spec("driver_build")
        item["segments"][0]["base_margin"] = 0.15
        item["segments"][1]["base_margin"] = 0.05
        result = compute_model(item)
        self.assertAlmostEqual(value(result, "base_profit"), 100 * 0.15 + 50 * 0.05)
        self.assertAlmostEqual(value(result, "profit"), 161.4 * 0 + 115.5 * 0.2 + 45.9 * 0.1, places=9)
        self.assertAlmostEqual(value(result, "profit_change"),
                               value(result, "profit") - value(result, "base_profit"), places=9)
        plain = compute_model(spec("driver_build"))
        self.assertAlmostEqual(value(plain, "base_profit"), 100 * 0.2 + 50 * 0.1)

    def test_projection_builds_sequential_years(self):
        item = spec("driver_build")
        item["projection"] = [{"label": "Y1", "revenue_growth": 0.1, "margin": 0.22},
                              {"label": "Y2", "revenue_growth": 0.05, "margin": 0.24}]
        result = compute_model(item)
        rows = result["outputs"]["projection"]
        self.assertEqual([row["label"] for row in rows], ["Y1", "Y2"])
        self.assertAlmostEqual(rows[0]["revenue"]["value"], value(result, "revenue") * 1.1)
        self.assertAlmostEqual(rows[0]["profit"]["value"], rows[0]["revenue"]["value"] * 0.22)
        self.assertAlmostEqual(rows[1]["revenue"]["value"], rows[0]["revenue"]["value"] * 1.05)
        self.assertAlmostEqual(rows[1]["profit"]["value"], rows[1]["revenue"]["value"] * 0.24)
        self.assertNotIn("projection", compute_model(spec("driver_build"))["outputs"])

    def test_tornado_cannot_target_the_projection_array(self):
        item = spec("driver_build")
        item["projection"] = [{"label": "Y1", "revenue_growth": 0.1, "margin": 0.2}]
        item["tornado"] = {"output": "projection",
                           "inputs": [{"input": "margin_delta", "low": -0.01, "high": 0.01}]}
        with self.assertRaisesRegex(ValueError, "must name a scalar output"):
            compute_model(item)

    def test_projection_validation(self):
        cases = [
            [{"label": "Y1", "revenue_growth": -1, "margin": 0.2}],
            [{"label": "Y1", "revenue_growth": 0.1, "margin": 0.2}, {"label": "y1", "revenue_growth": 0.1, "margin": 0.2}],
            [{"label": "", "revenue_growth": 0.1, "margin": 0.2}],
            [{"label": "Y1", "revenue_growth": 0.1}],
            [{"label": "Y%d" % n, "revenue_growth": 0.1, "margin": 0.2} for n in range(11)],
        ]
        for projection in cases:
            item = spec("driver_build")
            item["projection"] = projection
            with self.assertRaises(ValueError):
                compute_model(item)
        bridge = spec("operating_bridge")
        bridge["projection"] = [{"label": "Y1", "revenue_growth": 0.1, "margin": 0.2}]
        with self.assertRaisesRegex(ValueError, "only supported by driver_build"):
            compute_model(bridge)

    def test_base_margin_must_be_numeric(self):
        item = spec("driver_build")
        item["segments"][0]["base_margin"] = "0.2"
        with self.assertRaises(ValueError):
            compute_model(item)

    def test_negative_segment_margin_is_allowed(self):
        item = spec("driver_build")
        item["segments"] = [{"name": "growth", "base_revenue": 100, "volume_growth": 0.5,
                             "price_growth": -0.1, "margin": -0.2}]
        result = compute_model(item)
        self.assertAlmostEqual(value(result, "profit"), 100 * 1.5 * 0.9 * -0.2)

    def test_segment_validation(self):
        bad_inputs = [
            [],
            [{}],
            [{"name": "", "base_revenue": 10, "volume_growth": 0, "price_growth": 0, "margin": 0}],
            [{"name": "A", "base_revenue": -1, "volume_growth": 0, "price_growth": 0, "margin": 0}],
            [{"name": "A", "base_revenue": 1, "volume_growth": -1, "price_growth": 0, "margin": 0}],
            [{"name": "A", "base_revenue": 1, "volume_growth": 0, "price_growth": -2, "margin": 0}],
            [{"name": "A", "base_revenue": 1, "volume_growth": 0, "price_growth": 0, "margin": "0"}],
            [{"name": "A", "base_revenue": 1, "volume_growth": 0, "price_growth": 0, "margin": 0, "extra": 1}],
            [{"name": "A", "base_revenue": 1, "volume_growth": 0, "price_growth": 0, "margin": 0,
              "claim_ids": [""]}],
            [{"name": "A", "base_revenue": 1, "volume_growth": 0, "price_growth": 0, "margin": 0},
             {"name": " a ", "base_revenue": 2, "volume_growth": 0, "price_growth": 0, "margin": 0}],
        ]
        for segments in bad_inputs:
            item = spec("driver_build")
            item["segments"] = segments
            with self.subTest(segments=segments), self.assertRaises(ValueError):
                compute_model(item)

    def test_segments_required_and_scoped_to_driver_build(self):
        item = spec("driver_build")
        del item["segments"]
        with self.assertRaisesRegex(ValueError, "segments"):
            compute_model(item)
        wrong = spec("dcf")
        wrong["segments"] = [{"name": "A", "base_revenue": 1, "volume_growth": 0,
                              "price_growth": 0, "margin": 0}]
        with self.assertRaisesRegex(ValueError, "only supported"):
            compute_model(wrong)

    def test_margin_delta_range(self):
        for bad in (-1.5, 2):
            with self.assertRaisesRegex(ValueError, "margin_delta"):
                compute_model(spec("driver_build", margin_delta=bad))


class RelativeValuationTests(unittest.TestCase):
    def peers(self, *multiples):
        return [{"name": "P%d" % index, "multiple": multiple}
                for index, multiple in enumerate(multiples)]

    def test_peer_distribution_and_implied_value(self):
        item = spec("relative_valuation")
        item["peers"] = self.peers(8, 10, 12, 14)
        result = compute_model(item)
        expected = {"peer_count": 4, "peer_multiple_min": 8, "peer_multiple_q1": 9.5,
                    "peer_multiple_median": 11, "peer_multiple_q3": 12.5,
                    "peer_multiple_max": 14, "peer_multiple_mean": 11,
                    "implied_ev_median": 1100, "implied_equity_median": 1080,
                    "per_share_median": 108, "per_share_low": 93, "per_share_high": 123,
                    "implied_multiple_at_price": 1.7}
        for name, number in expected.items():
            self.assertAlmostEqual(value(result, name), number, msg=name)
        self.assertAlmostEqual(value(result, "price_vs_peer_median"), 15 / 108 - 1)
        self.assertEqual(result["outputs"]["peer_count"]["unit"], "count")
        self.assertEqual(result["outputs"]["per_share_median"]["unit"], "currency/share")

    def percentile(self, price):
        item = spec("relative_valuation", price=price)
        item["peers"] = self.peers(8, 10, 12, 14)
        return value(compute_model(item), "implied_multiple_percentile")

    def test_implied_multiple_percentile(self):
        self.assertEqual(self.percentile(15), 0.0)
        self.assertEqual(self.percentile(98), 0.25)
        self.assertEqual(self.percentile(111), 0.5)
        self.assertEqual(self.percentile(200), 1.0)

    def test_peer_order_does_not_change_the_result(self):
        first, second = spec("relative_valuation"), spec("relative_valuation")
        first["peers"] = self.peers(14, 8, 12, 10)
        second["peers"] = self.peers(8, 10, 12, 14)
        self.assertEqual(compute_model(first)["outputs"], compute_model(second)["outputs"])
        self.assertEqual(first["peers"][0]["name"], "P0")

    def test_single_peer_and_net_cash(self):
        item = spec("relative_valuation", net_debt=-50)
        item["peers"] = self.peers(10)
        result = compute_model(item)
        for name in ("peer_multiple_min", "peer_multiple_median", "peer_multiple_max"):
            self.assertEqual(value(result, name), 10)
        self.assertEqual(value(result, "implied_equity_median"), 1050)
        self.assertEqual(value(result, "per_share_median"), 105)
        self.assertEqual(value(result, "peer_count"), 1)

    def test_nonpositive_implied_equity_omits_premium(self):
        item = spec("relative_valuation", net_debt=5000)
        item["peers"] = self.peers(8, 12)
        result = compute_model(item)
        self.assertLess(value(result, "per_share_median"), 0)
        self.assertNotIn("price_vs_peer_median", result["outputs"])

    def test_metric_must_be_positive(self):
        for bad in (0, -100):
            item = spec("relative_valuation", metric=bad)
            item["peers"] = self.peers(10)
            with self.subTest(metric=bad), self.assertRaisesRegex(ValueError, "metric"):
                compute_model(item)

    def test_peer_set_is_required_and_validated(self):
        item = spec("relative_valuation")
        del item["peers"]
        with self.assertRaisesRegex(ValueError, "peers"):
            compute_model(item)
        for invalid in ([], {}, "peers", [None], [{}], [{"name": "A"}],
                        [{"name": "", "multiple": 10}], [{"name": "A", "multiple": 0}],
                        [{"name": "A", "multiple": -1}], [{"name": "A", "multiple": True}],
                        [{"name": "A", "multiple": "10"}], [{"name": "A", "multiple": math.nan}],
                        [{"name": "A", "multiple": 10, "extra": 1}],
                        [{"name": "A", "multiple": 10, "note": 1}],
                        [{"name": "A", "multiple": 10, "claim_ids": None}],
                        [{"name": "A", "multiple": 10, "claim_ids": "C1"}],
                        [{"name": "A", "multiple": 10, "claim_ids": [1]}],
                        [{"name": "A", "multiple": 10, "claim_ids": [""]}],
                        [{"name": "A", "multiple": 10}, {"name": " a ", "multiple": 12}]):
            bad = copy.deepcopy(item)
            bad["peers"] = invalid
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                compute_model(bad)

    def test_peers_only_belong_to_relative_valuation(self):
        item = spec()
        item["peers"] = self.peers(10)
        with self.assertRaisesRegex(ValueError, "only supported"):
            compute_model(item)

    def test_overflow_is_readable(self):
        item = spec("relative_valuation", metric=1e308)
        item["peers"] = self.peers(10)
        with self.assertRaises(ValueError):
            compute_model(item)


class RealDataTests(unittest.TestCase):
    """The fixed models must reproduce a real published income statement."""

    def root(self):
        return Path(__file__).resolve().parents[1] / "examples" / "msft-quality"

    def test_operating_bridge_reproduces_msft_example(self):
        periods = json.loads((self.root() / "statements.json").read_text(encoding="utf-8"))["periods"]
        previous, current = periods
        spec = {"kind": "operating_bridge", "inputs": {
            "base_revenue": {"value": previous["revenue"], "unit": "currency", "role": "observed", "claim_ids": ["C1"]},
            "revenue_growth": {"value": current["revenue"] / previous["revenue"] - 1, "unit": "ratio",
                               "role": "observed", "claim_ids": ["C1"]},
            "base_margin": {"value": previous["operating_profit"] / previous["revenue"], "unit": "ratio",
                            "role": "observed", "claim_ids": ["C1"]},
            "scenario_margin": {"value": current["operating_profit"] / current["revenue"], "unit": "ratio",
                                "role": "observed", "claim_ids": ["C1"]}},
            "sensitivity": [{"input": "scenario_margin", "values": [0.45, 0.46]}]}
        outputs = compute_model(spec)["outputs"]
        self.assertAlmostEqual(outputs["revenue"]["value"], current["revenue"], places=6)
        self.assertAlmostEqual(outputs["profit"]["value"], current["operating_profit"], places=6)
        self.assertAlmostEqual(outputs["profit_change"]["value"],
                               current["operating_profit"] - previous["operating_profit"], places=6)
        self.assertAlmostEqual(outputs["revenue_growth_effect"]["value"] +
                               outputs["margin_effect"]["value"],
                               outputs["profit_change"]["value"], places=6)

    def test_driver_build_reproduces_msft_segments(self):
        segments = json.loads((self.root() / "segments.json").read_text(encoding="utf-8"))
        periods = json.loads((self.root() / "statements.json").read_text(encoding="utf-8"))["periods"]
        current_revenue = periods[1]["revenue"]
        current_profit = periods[1]["operating_profit"]
        spec = {"kind": "driver_build",
                "inputs": {"margin_delta": {"value": 0, "unit": "ratio", "role": "assumption", "claim_ids": ["A1"]}},
                "segments": [{"name": now["segment"], "base_revenue": before["revenue"],
                              "volume_growth": now["revenue"] / before["revenue"] - 1, "price_growth": 0,
                              "base_margin": before["operating_income"] / before["revenue"],
                              "margin": now["operating_income"] / now["revenue"], "claim_ids": ["C1", "A1"]}
                             for before, now in zip(segments["FY2024"], segments["FY2025"])],
                "sensitivity": [{"input": "margin_delta", "values": [-0.01, 0.01]}]}
        outputs = compute_model(spec)["outputs"]
        self.assertAlmostEqual(outputs["revenue"]["value"], current_revenue, places=6)
        self.assertAlmostEqual(outputs["profit"]["value"], current_profit, places=6)
        self.assertAlmostEqual(outputs["profit_change"]["value"],
                               current_profit - periods[0]["operating_profit"], places=6)
        self.assertAlmostEqual(outputs["revenue_growth"]["value"], current_revenue / periods[0]["revenue"] - 1, places=9)
        self.assertGreater(outputs["incremental_margin"]["value"], 0)


if __name__ == "__main__":
    unittest.main()
