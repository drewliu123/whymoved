"""Opportunity research, frozen triggers and shared output regressions."""

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

from test_reports import documents, SCRIPTS, Text
sys.path.insert(0, str(SCRIPTS))
import opportunities
import opportunity_contract
import render_report
import research_run
import test_research_runs


def opportunity(status="watch"):
    def item(text):
        return {"text": text, "claim_ids": ["C2"]}
    return {"version": 1, "applicability": "trading",
            "market_view": dict(item("根据交付担忧推断市场仍押注兑现后移，属于研究估计。"), basis="proxy"),
            "variant": item("订单可能先于收入改善，倾向关注交付验证。"),
            "edge": item("将订单与交付时点连接，而非把需求增长当作已实现利润。"),
            "catalyst": dict(item("下一次披露检验交付。"), by="下一季度披露；到期仍无改善则重估"),
            "payoff": item("尚无可靠价格区间；等待交付可降低误判需求的代价，错过提前上涨是等待成本。"),
            "assessment": dict(item("分歧值得关注，等待交付改善再提高优先级。"), status=status),
            "triggers": [{"id": "T1", "signal": "交付能否同步改善", "by": "下一次季报", "claim_ids": ["C2"],
                          "supports_if": "交付与回款同步改善", "weakens_if": "订单增而交付继续延迟", "invalidates_if": "订单取消或到期仍不兑现"}]}


def add_opportunity(report, ledger, status="watch"):
    ledger["claims"].append({"id": "C2", "text": "收入改善支持继续检查交付；价格优势尚未确认。", "type": "inference", "as_of": ledger["as_of"], "sources": [], "basis": ["C1"]})
    report["opportunity"] = opportunity(status)


def update(previous="watch", current="priced_in"):
    return {"judgment_changed": True, "reason": "经营判断增强但价格吸引力下降", "comparability": {"status": "comparable", "reason": "同口径观察"},
            "opportunity": {"previous_status": previous, "current_status": current, "thesis_change": "strengthened",
                            "reason": "兑现更明确，价格反映也更充分", "price_move": "样例未提供可核验的新报价，不能测量期间涨跌",
                            "remaining_edge": "逻辑改善不等于剩余回报增加，本次列为价格已反映的测试情景", "claim_ids": ["C2"],
                            "trigger_results": [{"trigger_id": "T1", "status": "not_checked", "observation": "未取得新交付记录", "claim_ids": []}],
                            "review": {"direction": "待后续观察", "magnitude": "未提供数字", "timing": "未到期", "mechanism": "尚待核验", "price_realization": "没有可核验报价，未评估实际收益"}}}


class OpportunityTest(unittest.TestCase):
    def setUp(self):
        self.r, self.l, self.s = documents()
        add_opportunity(self.r, self.l)

    def test_valid_proxy_and_all_statuses(self):
        for status in opportunity_contract.STATUSES:
            self.r["opportunity"]["assessment"]["status"] = status
            self.assertEqual(render_report.validate_report(self.r, self.l, self.s), [])

    def test_nontrading_and_historical_reports(self):
        self.r["opportunity"] = {"version": 1, "applicability": "not_applicable", "reason": "仅核对经营事实"}
        self.assertEqual(render_report.validate_report(self.r, self.l, self.s), [])
        self.r.pop("opportunity")
        self.assertEqual(render_report.validate_report(self.r, self.l, self.s), [])

    def test_missing_fields_and_bad_refs_rejected(self):
        for mutate in (lambda o: o.pop("payoff"), lambda o: o["edge"].update(claim_ids=["unknown"]),
                       lambda o: o["catalyst"].update(by=""), lambda o: o["triggers"].append(copy.deepcopy(o["triggers"][0])),
                       lambda o: o.update(version=True), lambda o: o["assessment"].update(status=[]),
                       lambda o: o["market_view"].update(basis={}), lambda o: o["triggers"][0].update(invalidates_if="")):
            r = copy.deepcopy(self.r)
            mutate(r["opportunity"])
            self.assertTrue(render_report.validate_report(r, self.l, self.s))
            with self.assertRaises(ValueError):
                render_report.render_html(r, self.l, self.s)

    def test_proxy_not_disguised_as_consensus_or_price(self):
        for basis in ("consensus", "price_implied"):
            self.r["opportunity"]["market_view"]["basis"] = basis
            self.assertTrue(render_report.validate_report(self.r, self.l, self.s))
        self.r["opportunity"]["market_view"].update(basis="proxy", claim_ids=["C1"])
        self.assertTrue(render_report.validate_report(self.r, self.l, self.s))

    def test_not_applicable_rejects_hidden_trading_fields(self):
        self.r["opportunity"].update(applicability="not_applicable", reason="事实查询")
        self.assertTrue(render_report.validate_report(self.r, self.l, self.s))

    def test_shared_output_and_literal_payload(self):
        self.r["opportunity"]["variant"]["text"] = '<img src=x onerror="alert(1)">[x](javascript:alert(1))'
        page = render_report.render_html(self.r, self.l, self.s)
        markdown = render_report.render_markdown(self.r, self.l, self.s)
        parser = Text(); parser.feed(page)
        self.assertNotIn("img", [t for t, _ in parser.tags])
        for text in ("等待触发", "研究代理估计", "剩余空间与做错代价", "订单取消或到期仍不兑现"):
            self.assertIn(text, "".join(parser.text))
            self.assertIn(text, markdown)
        self.assertLess(markdown.index("等待触发"), markdown.index("附录："))
        self.assertGreater(markdown.index("相对原文与旧判断的增量"), markdown.index("附录：机会判断"))

    def test_update_outcome_requires_checked_evidence(self):
        self.r["opportunity"]["assessment"]["status"] = "priced_in"
        self.r["update"] = update()
        self.assertEqual(render_report.validate_report(self.r, self.l, self.s), [])
        for status in ("hit", "not_hit"):
            self.r["update"]["opportunity"]["trigger_results"][0]["status"] = status
            self.assertTrue(render_report.validate_report(self.r, self.l, self.s))
        self.r["update"]["opportunity"]["trigger_results"][0].update(status="hit", claim_ids=["C1"])
        self.assertEqual(render_report.validate_report(self.r, self.l, self.s), [])
        for output in (render_report.render_markdown(self.r, self.l, self.s), render_report.render_html(self.r, self.l, self.s)):
            self.assertIn("机制兑现", output)
            self.assertIn("价格兑现", output)
            self.assertIn("期间价格变化", output)

    def test_malformed_update_and_review(self):
        self.r["update"] = update(current="watch")
        self.r["update"]["opportunity"]["review"].pop("timing")
        self.assertTrue(render_report.validate_report(self.r, self.l, self.s))
        self.r["update"]["opportunity"] = []
        self.assertTrue(render_report.validate_report(self.r, self.l, self.s))

    def test_parent_status_and_all_triggers_are_bound(self):
        parent = copy.deepcopy(self.r)
        self.r["opportunity"]["assessment"]["status"] = "priced_in"
        self.r["update"] = update()
        self.assertEqual(opportunity_contract.validate_parent_opportunity(parent, self.r), [])
        self.r["update"]["opportunity"]["previous_status"] = "research_now"
        self.assertTrue(opportunity_contract.validate_parent_opportunity(parent, self.r))
        self.r["update"] = update()
        self.r["update"]["opportunity"]["trigger_results"][0]["trigger_id"] = "replacement"
        self.assertTrue(opportunity_contract.validate_parent_opportunity(parent, self.r))
        self.r.pop("opportunity")
        self.assertTrue(opportunity_contract.validate_parent_opportunity(parent, self.r))


class OpportunityRunsTest(unittest.TestCase):
    def test_archive_update_list_and_parent_immutability(self):
        fixture = test_research_runs.ResearchRunsTest()
        fixture.setUp()
        try:
            add_opportunity(fixture.report, fixture.ledger)
            first = fixture.archive()
            parent = research_run.load_run(first["run_id"], fixture.home)
            saved = (Path(first["path"]) / "report.json").read_bytes()
            fixture.report["opportunity"]["assessment"]["status"] = "priced_in"
            fixture.report["update"] = update()
            second = fixture.archive(parent_run=first["run_id"])
            loaded = research_run.load_run(second["run_id"], fixture.home)
            self.assertTrue(loaded["diff"]["opportunity_changed"])
            self.assertEqual((Path(first["path"]) / "report.json").read_bytes(), saved)
            self.assertEqual(opportunities.list_opportunities(fixture.home)[0]["run_id"], second["run_id"])
            self.assertEqual(len(opportunities.list_opportunities(fixture.home, history=True)), 2)
            fixture.report["update"]["opportunity"]["previous_status"] = "no_edge"
            with self.assertRaisesRegex(ValueError, "frozen parent"):
                fixture.archive(parent_run=first["run_id"])
            fixture.report["update"] = update()
            fixture.report["update"]["opportunity"]["trigger_results"][0]["trigger_id"] = "T2"
            with self.assertRaisesRegex(ValueError, "every frozen parent trigger"):
                fixture.archive(parent_run=first["run_id"])
            self.assertEqual(parent["report"]["opportunity"]["assessment"]["status"], "watch")
        finally:
            fixture.tearDown()


if __name__ == "__main__":
    unittest.main()
