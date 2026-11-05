"""Reframe one frozen research record; never refresh or modify the original run."""

import copy
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))
import opportunities
import render_report
import research_run
from test_reports import documents
from test_opportunities import add_opportunity

OUT = Path(__file__).resolve().parent / "cases"
ORIGINAL = "R20261102T051254Z-e3879bd00b29"


def write(path, document):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run():
    OUT.mkdir(exist_ok=False)
    old = research_run.load_run(ORIGINAL, ROOT)
    original_files = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(old["path"]).iterdir() if p.is_file()}
    report = copy.deepcopy(old["report"])
    report.pop("update", None)
    plan = copy.deepcopy(old["plan"])
    plan.pop("parent_run_id", None)
    report["answer"]["text"] = "我倾向于选后最初几天继续谈判与拖延，优先研究11月8日的前端风险；月底35美分尚未显示清晰优势。值得追的是选后克制承诺能否延长并兑现，这比继续谈判的表态更能区分近期打击与继续拖延。"
    report["answer"]["claim_ids"] = ["C31", "C32", "C33"]
    report["analysis"]["conclusion"] = report["answer"]["text"]
    report["analysis"]["conclusion_claim_ids"] = report["answer"]["claim_ids"]
    def item(text, ids):
        return {"text": text, "claim_ids": ids}
    report["opportunity"] = {
        "version": 1, "applicability": "trading",
        "market_view": dict(item("冻结期限曲线把较高的风险集中于选后初期；在嵌套未打击事件的解释假设下，11月4日至8日条件价格比约22.5%。", ["C16", "C29"]), basis="price_implied"),
        "variant": item("暂偏向选后最初数日延续边谈边施压，短端风险可能比月底累计风险更值得检验。", ["C31"]),
        "edge": item("将期限报价换算成不同区间的条件价格比，定位前端风险集中，再与具名外交表态比较；形状差不是公允价值差。", ["C29", "C30", "C31"]),
        "catalyst": dict(item("选后克制承诺延至11月8日之后并可核查执行，会直接检验前端风险；最后通牒配合执行准备则反向。", ["C32"]), by="原研究截点之后至2026年11月8日；本案例未刷新"),
        "payoff": item("旧快照11月8日YES可买价73美分，需要独立判断未打击概率高于73%才能在忽略其他成本时有正期望；一次合格打击会令YES失败。7.7美分曲线形状差不能当成预期收益。", ["C13", "C30", "C33"]),
        "assessment": dict(item("优先等待可核查续接克制承诺。方向有倾向，但公开表态可能已入价，目前尚不能把曲线异常当作可成交优势。", ["C31", "C32", "C33"]), status="watch"),
        "triggers": [{"id": "V1", "signal": "选后克制期限与执行准备", "by": "2026年11月3日至8日；过期需重新研究", "claim_ids": ["C32"],
                      "supports_if": "明确延长不打击承诺至11月8日后且获可核查执行", "weakens_if": "新最后通牒与执行准备配套出现", "invalidates_if": "发生合约定义的合格打击，或期限内关键检验不再支持原判断"}]}
    folder = OUT / "frozen-event"
    paths = []
    for name, doc in (("report", report), ("claims", old["claims"]), ("sources", old["sources"]), ("plan", plan)):
        path = folder / (name + ".json")
        write(path, doc)
        paths.append(path)
    audit = {"case_kind": "frozen_research_reframe", "source_run": ORIGINAL,
             "warning": "仅重组原研究冻结证据；未联网重核来源，未刷新报价，不是当前交易信号、事前预测或收益验收。"}
    write(folder / "audit.json", audit)
    archived = research_run.archive_run(*paths, home=OUT / "isolated-home", audit_path=folder / "audit.json")
    loaded = research_run.load_run(archived["run_id"], OUT / "isolated-home")
    (folder / "before.md").write_text((Path(old["path"]) / "report.md").read_text(), encoding="utf-8")
    (folder / "report.md").write_text((Path(loaded["path"]) / "report.md").read_text(), encoding="utf-8")
    (folder / "report.html").write_text((Path(loaded["path"]) / "report.html").read_text(), encoding="utf-8")
    synthetic = []
    reasons = {"research_now": "虚构样例：分歧与催化值得优先研究，不代表下单建议。", "watch": "虚构样例：等待交付与回款确认。", "priced_in": "虚构样例：经营方向成立，但假设价格已反映主要改善。", "no_edge": "虚构样例：没有比现有解释更强的研究优势。"}
    for status, text in reasons.items():
        r, ledger, sources = documents()
        add_opportunity(r, ledger, status)
        r["opportunity"]["assessment"]["text"] = text
        render_report.write_outputs(OUT / ("synthetic-" + status), render_report.render_markdown(r, ledger, sources), render_report.render_html(r, ledger, sources))
        synthetic.append({"status": status, "kind": "synthetic_contract_case", "passed": True})
    r, ledger, sources = documents()
    r["opportunity"] = {"version": 1, "applicability": "not_applicable", "reason": "单项事实核对不扩成交易研究"}
    assert not render_report.validate_report(r, ledger, sources)
    unchanged = original_files == {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(old["path"]).iterdir() if p.is_file()}
    assert unchanged
    result = {"real_case": {"source_run": ORIGINAL, "derived_run": archived["run_id"], "kind": "frozen_research_reframe", "original_unchanged": unchanged, "passed": True},
              "synthetic_cases": synthetic, "nontrading": True,
              "opportunities": opportunities.list_opportunities(OUT / "isolated-home"),
              "not_evaluated": ["live retrieval", "prospective forecasting", "actual returns", "automated semantic evaluation"]}
    write(OUT / "results.json", result)
    print(json.dumps({"case_results": str(OUT / "results.json"), "real_case": "frozen evidence only", "synthetic_cases": len(synthetic), "original_unchanged": unchanged}, ensure_ascii=False))


if __name__ == "__main__":
    run()
