"""Whitelisted recomputation for report.calculations.

Covers operator arithmetic, unit contracts, evidence references, reference
chains, rounding, failure modes and rendering. Derived numbers are only
recomputed; semantic meaning stays a researcher and reviewer responsibility.
"""

import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import calculations
import render_report
from test_reports import documents

CLAIMS = {"C1", "C2", "C3"}
USD = {"name": "a", "value": 100, "unit": "USD", "claim_ids": ["C1"]}
USD_B = {"name": "b", "value": 40, "unit": "USD", "claim_ids": ["C2"]}


def base(calc_id="A1", inputs=None, result=None, **extra):
    row = {"id": calc_id, "description": "虚构透明计算", "formula": "a - b", "claim_ids": ["C1"],
           "inputs": inputs if inputs is not None else [dict(USD), dict(USD_B)],
           "result": result if result is not None else {"value": 60, "unit": "USD"}}
    row.update(extra)
    return row


def errors(rows, claims=CLAIMS):
    return calculations.validate_calculations(rows, claims)


class LegacyCalculationTests(unittest.TestCase):
    def test_legacy_rows_keep_shape_checks_only(self):
        self.assertEqual(errors([base()]), [])
        wrong = base(result={"value": 999, "unit": "USD"})
        self.assertEqual(errors([wrong]), [], "rows without op are never executed")

    def test_shape_failures_still_rejected(self):
        for mutate in (
            lambda r: r.pop("description"),
            lambda r: r.update(formula=""),
            lambda r: r.update(claim_ids=[]),
            lambda r: r.update(claim_ids=["C404"]),
            lambda r: r.update(inputs=[]),
            lambda r: r["inputs"][0].update(claim_ids=[]),
            lambda r: r["inputs"][0].update(value=True),
            lambda r: r["inputs"][0].update(value=float("nan")),
            lambda r: r["inputs"][0].update(unit=""),
            lambda r: r.update(result={"value": "60", "unit": "USD"}),
            lambda r: r.update(result={"value": 60}),
            lambda r: r.update(id="1bad"),
        ):
            row = base()
            mutate(row)
            self.assertTrue(errors([row]))
        self.assertEqual(errors("not a list"), ["calculations must be a list"])
        self.assertTrue(errors([base(), base()]), "duplicate ids rejected")
        self.assertTrue(errors([None]))


class OperatorTests(unittest.TestCase):
    def check(self, op, inputs, value, unit="USD", precision=None):
        result = {"value": value, "unit": unit}
        if precision is not None:
            result["precision"] = precision
        rows = [base(inputs=inputs, result=result, op=op)]
        self.assertEqual(errors(rows), [])

    def test_ratio(self):
        self.check("ratio", [dict(USD), dict(USD_B)], 2.5, "ratio")

    def test_growth(self):
        self.check("growth", [{"name": "now", "value": 120, "unit": "USD", "claim_ids": ["C1"]},
                              {"name": "base", "value": 100, "unit": "USD", "claim_ids": ["C2"]}], 0.2, "ratio")

    def test_cagr(self):
        self.check("cagr", [{"name": "end", "value": 121, "unit": "USD", "claim_ids": ["C1"]},
                            {"name": "begin", "value": 100, "unit": "USD", "claim_ids": ["C2"]},
                            {"name": "years", "value": 2, "unit": "year", "claim_ids": ["C3"]}], 0.1, "ratio")

    def test_difference_and_sum(self):
        self.check("difference", [dict(USD), dict(USD_B)], 60)
        self.check("sum", [dict(USD), dict(USD_B), {"name": "c", "value": 10, "unit": "USD", "claim_ids": ["C3"]}], 150)

    def test_product(self):
        self.check("product", [{"name": "revenue", "value": 100, "unit": "USD", "claim_ids": ["C1"]},
                               {"name": "margin", "value": 0.25, "unit": "ratio", "claim_ids": ["C2"]}], 25)

    def test_recomputation_mismatch_is_rejected(self):
        rows = [base(op="difference", result={"value": 61, "unit": "USD"})]
        self.assertTrue(any("recomputation" in e for e in errors(rows)))

    def test_rounding_precision(self):
        exact = {"value": 0.15, "unit": "ratio", "precision": 2}
        inputs = [{"name": "now", "value": 281724, "unit": "USD", "claim_ids": ["C1"]},
                  {"name": "base", "value": 245122, "unit": "USD", "claim_ids": ["C2"]}]
        self.assertEqual(errors([base(inputs=inputs, result=exact, op="growth")]), [])
        unrounded = dict(exact)
        del unrounded["precision"]
        self.assertTrue(errors([base(inputs=inputs, result=unrounded, op="growth")]))
        for bad in (-1, 13, 2.0, True):
            row = base(inputs=inputs, result=dict(exact, precision=bad), op="growth")
            self.assertTrue(errors([row]), bad)

    def test_unit_contracts(self):
        cases = [
            ("ratio", [dict(USD), dict(USD_B)], {"value": 2.5, "unit": "percent"}),
            ("ratio", [dict(USD), {"name": "b", "value": 4, "unit": "shares", "claim_ids": ["C2"]}],
             {"value": 25, "unit": "ratio"}),
            ("sum", [dict(USD), {"name": "b", "value": 4, "unit": "shares", "claim_ids": ["C2"]}],
             {"value": 104, "unit": "USD"}),
            ("sum", [dict(USD), dict(USD_B)], {"value": 140, "unit": "shares"}),
            ("difference", [dict(USD), dict(USD_B), dict(USD_B)], {"value": 60, "unit": "USD"}),
            ("product", [{"name": "a", "value": 100, "unit": "USD", "claim_ids": ["C1"]},
                         {"name": "b", "value": 4, "unit": "shares", "claim_ids": ["C2"]}],
             {"value": 400, "unit": "USD"}),
            ("product", [{"name": "a", "value": 2, "unit": "ratio", "claim_ids": ["C1"]},
                         {"name": "b", "value": 3, "unit": "ratio", "claim_ids": ["C2"]}],
             {"value": 6, "unit": "ratio"}),
            ("cagr", [{"name": "end", "value": 121, "unit": "USD", "claim_ids": ["C1"]},
                      {"name": "begin", "value": 100, "unit": "USD", "claim_ids": ["C2"]},
                      {"name": "years", "value": 2, "unit": "USD", "claim_ids": ["C3"]}],
             {"value": 0.1, "unit": "ratio"}),
            ("ratio", [dict(USD)], {"value": 100, "unit": "ratio"}),
        ]
        for op, inputs, result in cases:
            self.assertTrue(errors([base(inputs=inputs, result=result, op=op)]), op)

    def test_unknown_op_and_bad_operands(self):
        self.assertTrue(errors([base(op="eval")]))
        self.assertTrue(errors([base(op=["difference"])]))
        zero = [dict(USD), {"name": "b", "value": 0, "unit": "USD", "claim_ids": ["C2"]}]
        self.assertTrue(errors([base(inputs=zero, result={"value": 0, "unit": "ratio"}, op="ratio")]))
        self.assertTrue(errors([base(inputs=zero, result={"value": -1, "unit": "ratio"}, op="growth")]))
        negative = [{"name": "end", "value": -50, "unit": "USD", "claim_ids": ["C1"]},
                    {"name": "begin", "value": 100, "unit": "USD", "claim_ids": ["C2"]},
                    {"name": "years", "value": 2, "unit": "year", "claim_ids": ["C3"]}]
        self.assertTrue(errors([base(inputs=negative, result={"value": 0, "unit": "ratio"}, op="cagr")]))

    def test_overflow_is_a_value_error(self):
        huge = [{"name": "a", "value": 1e308, "unit": "USD", "claim_ids": ["C1"]},
                {"name": "b", "value": 10, "unit": "ratio", "claim_ids": ["C2"]}]
        result = errors([base(inputs=huge, result={"value": 1e308, "unit": "USD"}, op="product")])
        self.assertTrue(any("finite" in e or "overflow" in e for e in result))


class ReferenceTests(unittest.TestCase):
    def chain(self):
        first = base("A1", op="difference", result={"value": 60, "unit": "USD"})
        second = base("A2", inputs=[{"name": "equity", "ref": "A1", "unit": "USD"},
                                    {"name": "cash", "value": 40, "unit": "USD", "claim_ids": ["C2"]}],
                      result={"value": 100, "unit": "USD"}, op="sum")
        return [first, second]

    def test_reference_chain_resolves_earlier_results(self):
        self.assertEqual(errors(self.chain()), [])

    def test_reference_failures(self):
        for mutate in (
            lambda rows: rows[1]["inputs"][0].update(ref="A404"),
            lambda rows: rows[1]["inputs"][0].update(ref="A2"),
            lambda rows: rows[1]["inputs"][0].update(unit="shares"),
            lambda rows: rows[1]["inputs"][0].update(value=60),
            lambda rows: rows[1]["inputs"][0].update(claim_ids=["C1"]),
            lambda rows: rows.reverse(),
        ):
            rows = self.chain()
            mutate(rows)
            self.assertTrue(errors(rows))

    def test_reference_depth_is_limited(self):
        rows = self.chain()
        rows.append(base("A3", inputs=[{"name": "again", "ref": "A2", "unit": "USD"},
                                       {"name": "k", "value": 2, "unit": "USD", "claim_ids": ["C2"]}],
                        result={"value": 102, "unit": "USD"}, op="sum"))
        self.assertTrue(any("depth" in e for e in errors(rows)))

    def test_reference_uses_the_recorded_result(self):
        first = base("A1", op="growth", inputs=[
            {"name": "now", "value": 165.15, "unit": "USD/share", "claim_ids": ["C1"]},
            {"name": "peak", "value": 243.37, "unit": "USD/share", "claim_ids": ["C1"]}],
            result={"value": -0.3214, "unit": "ratio", "precision": 4})
        second = base("A2", op="growth", inputs=[
            {"name": "pre", "value": 200.13, "unit": "USD/share", "claim_ids": ["C2"]},
            {"name": "peak", "value": 243.37, "unit": "USD/share", "claim_ids": ["C2"]}],
            result={"value": -0.1777, "unit": "ratio", "precision": 4})
        third = base("A3", op="ratio", inputs=[
            {"name": "pre", "ref": "A2", "unit": "ratio"},
            {"name": "total", "ref": "A1", "unit": "ratio"}],
            result={"value": 0.5529, "unit": "ratio", "precision": 4})
        self.assertEqual(errors([first, second, third]), [])

    def test_reference_to_uncomputed_row_is_rejected(self):
        rows = [base("A1"), base("A2", inputs=[{"name": "x", "ref": "A1", "unit": "USD"},
                                               {"name": "y", "value": 2, "unit": "USD", "claim_ids": ["C2"]}],
                                 result={"value": 102, "unit": "USD"}, op="sum")]
        self.assertTrue(errors(rows))


class RenderTests(unittest.TestCase):
    def rows(self):
        return [{"id": "A1", "description": "虚构透明计算", "formula": "a - b", "claim_ids": ["C1"],
                 "inputs": [{"name": "a", "value": 100, "unit": "USD", "claim_ids": ["C1"]},
                            {"name": "b", "value": 40, "unit": "USD", "claim_ids": ["C1"]}],
                 "result": {"value": 60, "unit": "USD"}}]

    def test_op_rows_are_marked_and_legacy_rows_are_not(self):
        report, ledger, sources = documents()
        report["calculations"] = [dict(self.rows()[0], op="difference")]
        self.assertEqual(render_report.validate_report(report, ledger, sources), [])
        for render in (render_report.render_markdown, render_report.render_html):
            text = render(report, ledger, sources).replace("\\", "")
            for word in ("op=difference", "已按固定算子重算", "重算一致", "未标注的仅记录公式"):
                self.assertIn(word, text)
        legacy = documents()
        legacy[0]["calculations"] = self.rows()
        text = render_report.render_markdown(*legacy).replace("\\", "")
        self.assertNotIn("已按固定算子重算", text)
        self.assertNotIn("未标注的仅记录公式", text)

    def test_reference_input_renders_reference_name(self):
        report, ledger, sources = documents()
        first = dict(self.rows()[0], op="difference")
        second = dict(self.rows()[0], id="A2", formula="A1 + c", op="sum",
                      inputs=[{"name": "equity", "ref": "A1", "unit": "USD"},
                              {"name": "cash", "value": 40, "unit": "USD", "claim_ids": ["C1"]}],
                      result={"value": 100, "unit": "USD"})
        report["calculations"] = [first, second]
        self.assertEqual(render_report.validate_report(report, ledger, sources), [])
        text = render_report.render_markdown(report, ledger, sources).replace("\\", "")
        self.assertIn("= A1", text)


if __name__ == "__main__":
    unittest.main()
