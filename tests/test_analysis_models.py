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
    }
    values = dict(defaults[kind], **overrides)
    return {"kind": kind, "inputs": {
        name: {"value": value, "unit": MODEL_UNITS[kind][name],
               "role": "assumption", "claim_ids": []} for name, value in values.items()},
        "sensitivity": []}


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
                                 {"input": "discount_rate", "values": [.15]}])):
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


if __name__ == "__main__":
    unittest.main()
