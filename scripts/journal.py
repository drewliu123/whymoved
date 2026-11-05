#!/usr/bin/env python3
"""Append-only review journal for research memos and their hypotheses.

  journal.py add <memo.json> --claims <claims.json> --report <memo.md> [--plan <plan.json>]
                                                      register hypotheses and archive the memo,
                                                      evidence ledger and plan under journal/<memo_id>/
  journal.py list                                     all memos
  journal.py show <memo_id>                           archived files and hypotheses of one memo
  journal.py due [--today YYYY-MM-DD]                 ungraded hypotheses past verify_by
  journal.py grade <memo_id> <hyp_id> hit|miss|void --note "..."
  journal.py stats                                    hit rate and Brier score vs market
"""

import argparse
import json
import shutil
import sys
from datetime import date
from pathlib import Path

import authors
import forecast
from check_claims import check_claim
from common import AUTHORS_FILE, JOURNAL_DIR, MEMOS_FILE, now_iso, read_jsonl, save_json, write_jsonl


def new_id(rows: list) -> str:
    today = date.today().strftime("%Y%m%d")
    n = sum(1 for r in rows if r["memo_id"].startswith(f"M{today}")) + 1
    return f"M{today}-{n:02d}"


def cmd_add(args) -> int:
    memo = json.loads(Path(args.memo).read_text(encoding="utf-8"))
    hyps = memo.get("hypotheses") or []
    bad = [h.get("id", "?") for h in hyps if not (h.get("id") and h.get("text") and h.get("verify_by"))]
    if not hyps or bad:
        print(f"每条假设都要有 id、text、verify_by；有问题的：{bad or '没有假设'}", file=sys.stderr)
        return 1
    for flag, path in (("--claims", args.claims), ("--report", args.report), ("--plan", args.plan), ("--forecast", args.forecast)):
        if path and not Path(path).is_file():
            print(f"{flag} 指向的文件不存在：{path}", file=sys.stderr)
            return 1

    # Only a ledger that passes R1-R8 may be archived as the basis of a memo.
    ledger = json.loads(Path(args.claims).read_text(encoding="utf-8"))
    claims = ledger.get("claims") or []
    ids = {c.get("id") for c in claims}
    failing = [c.get("id", "?") for c in claims if check_claim(c, ids)]
    if not claims or failing:
        print(f"证据账本没通过校验，先跑 check_claims.py 修好再登记；未通过：{failing or '账本为空'}", file=sys.stderr)
        return 1

    # A registered probability must be the one forecast.py computed, not a number typed into the memo.
    if args.forecast:
        doc = json.loads(Path(args.forecast).read_text(encoding="utf-8"))
        errs = [e for fc in doc.get("forecasts") or [] for e in forecast.problems(fc, ledger, doc.get("as_of", ""), True)]
        finals = {fc.get("hypothesis_id"): fc for fc in doc.get("forecasts") or []}
        for h in hyps:
            fc = finals.get(h["id"])
            if fc is None:
                continue
            if h.get("my_prob") != fc.get("final_prob"):
                errs.append(f"{h['id']}: my_prob {h.get('my_prob')} 与 forecast 的 final_prob {fc.get('final_prob')} 不一致")
            if fc.get("mode") == "market" and h.get("market_prob") != fc.get("market_prob"):
                errs.append(f"{h['id']}: market_prob 与 forecast 不一致")
        unknown = sorted(set(finals) - {h["id"] for h in hyps})
        if unknown:
            errs.append(f"forecast 引用了不存在的假设：{unknown}")
        if errs:
            print("概率预测没通过校验，先跑 forecast.py finalize：\n" + "\n".join(errs), file=sys.stderr)
            return 1
        for h in hyps:
            if h["id"] in finals:
                h["prob_mode"] = finals[h["id"]]["mode"]

    rows = read_jsonl(MEMOS_FILE)
    memo_id = new_id(rows)
    archive = JOURNAL_DIR / memo_id
    archive.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(args.memo, archive / "memo.json")
    shutil.copyfile(args.claims, archive / "claims.json")
    shutil.copyfile(args.report, archive / "memo.md")
    if args.plan:
        shutil.copyfile(args.plan, archive / "plan.json")
    if args.forecast:
        shutil.copyfile(args.forecast, archive / "forecast.json")

    for h in hyps:
        h.setdefault("outcome", None)
    rows.append({"memo_id": memo_id, "registered_at": now_iso(), "archive": memo_id, **memo})
    write_jsonl(MEMOS_FILE, rows)
    print(f"已登记 {memo_id}：{len(hyps)} 条假设，{len(claims)} 条证据，归档在 {archive}")
    for h in hyps:
        print(f"  {h['id']} 到期 {h['verify_by']}  {h['text']}")
    return 0


def cmd_show(args) -> int:
    memo = next((r for r in read_jsonl(MEMOS_FILE) if r["memo_id"] == args.memo_id), None)
    if not memo:
        print(f"找不到 {args.memo_id}", file=sys.stderr)
        return 1
    print(f"{memo['memo_id']}  {memo.get('question', '')}  截面 {memo.get('as_of', '')}")
    archive = JOURNAL_DIR / memo["archive"] if memo.get("archive") else None
    if archive and archive.is_dir():
        print(f"归档：{archive}")
        for f in sorted(archive.iterdir()):
            print(f"  {f.name}")
    else:
        print("归档：无（这份是加归档功能之前登记的）")
    for h in memo["hypotheses"]:
        print(f"{h['id']} 到期 {h['verify_by']}  结果 {h.get('outcome') or '未复盘'}  {h['text']}")
    return 0


def cmd_list(args) -> int:
    rows = read_jsonl(MEMOS_FILE)
    if not rows:
        print("账本为空。")
        return 0
    for r in rows:
        done = sum(1 for h in r["hypotheses"] if h.get("outcome"))
        print(f"{r['memo_id']}  {r.get('as_of', '')[:10]}  {r.get('question', '')}  （已复盘 {done}/{len(r['hypotheses'])}）")
    return 0


def cmd_due(args) -> int:
    today = args.today or date.today().isoformat()
    due = [
        (r["memo_id"], h)
        for r in read_jsonl(MEMOS_FILE)
        for h in r["hypotheses"]
        if not h.get("outcome") and str(h.get("verify_by", "9999"))[:10] <= today
    ]
    if not due:
        print(f"截至 {today} 没有到期待复盘的假设。")
        return 0
    for memo_id, h in due:
        print(f"{memo_id} {h['id']}  到期 {h['verify_by']}  {h['text']}\n    证伪条件：{h.get('falsify_if', '-')}")
    return 0


def cmd_grade(args) -> int:
    rows = read_jsonl(MEMOS_FILE)
    memo = next((r for r in rows if r["memo_id"] == args.memo_id), None)
    hyp = next((h for h in (memo or {}).get("hypotheses", []) if h["id"] == args.hyp_id), None)
    if not hyp:
        print(f"找不到 {args.memo_id} {args.hyp_id}", file=sys.stderr)
        return 1
    if hyp.get("outcome"):
        print(f"{args.memo_id} {args.hyp_id} 已记为 {hyp['outcome']}，账本只追加，不改写。", file=sys.stderr)
        return 1
    hyp.update({"outcome": args.outcome, "graded_at": now_iso(), "note": args.note})
    write_jsonl(MEMOS_FILE, rows)
    print(f"{args.memo_id} {args.hyp_id} 记为 {args.outcome}")

    if args.outcome == "void":
        return 0
    db = authors.load()
    for a in hyp.get("authors") or []:
        right = (a.get("stance") == "support") == (args.outcome == "hit")
        rec = authors.grade(db, a["handle"], a.get("platform", "x"), args.memo_id, "hit" if right else "miss")
        print(f"  作者 @{rec['handle']}（{a.get('stance')}）→ {'hit' if right else 'miss'}，状态 {rec['status']}")
    save_json(AUTHORS_FILE, db)
    return 0


def brier(prob, outcome: int):
    return None if prob is None else (float(prob) - outcome) ** 2


def cmd_stats(args) -> int:
    graded = [h for r in read_jsonl(MEMOS_FILE) for h in r["hypotheses"] if h.get("outcome") in ("hit", "miss")]
    if not graded:
        print("还没有已复盘的假设。")
        return 0
    hits = sum(1 for h in graded if h["outcome"] == "hit")
    print(f"已复盘 {len(graded)} 条，命中 {hits}（{hits / len(graded):.0%}）")
    pairs = [
        (brier(h.get("my_prob"), h["outcome"] == "hit"), brier(h.get("market_prob"), h["outcome"] == "hit"))
        for h in graded
    ]
    pairs = [(m, k) for m, k in pairs if m is not None and k is not None]
    if pairs:
        mine = sum(m for m, _ in pairs) / len(pairs)
        market = sum(k for _, k in pairs) / len(pairs)
        verdict = "比市场更准" if mine < market else "不如市场" if mine > market else "与市场持平"
        print(f"Brier 分数（越低越好，{len(pairs)} 条有双方概率）：本助手 {mine:.4f} / 市场 {market:.4f} → {verdict}")
        if len(pairs) < 30:
            print("样本少于 30 条，差异不能当作结论。")
    # market-mode probabilities are the market price by construction; the independent
    # ones are where this assistant's own judgment can be checked.
    indep = [h for h in graded if h.get("prob_mode") == "independent" and h.get("my_prob") is not None]
    if indep:
        mine = sum(brier(h["my_prob"], h["outcome"] == "hit") for h in indep) / len(indep)
        print(f"无市场参照的独立判断 {len(indep)} 条：Brier {mine:.4f}（0.5 恒报为 0.2500）")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add")
    a.add_argument("memo")
    a.add_argument("--claims", required=True, help="已通过校验的证据账本")
    a.add_argument("--report", required=True, help="备忘录正文（Markdown）")
    a.add_argument("--plan", help="检索计划")
    a.add_argument("--forecast", help="forecast.py finalize 过的概率预测")
    a.set_defaults(func=cmd_add)
    sub.add_parser("list").set_defaults(func=cmd_list)
    s = sub.add_parser("show")
    s.add_argument("memo_id")
    s.set_defaults(func=cmd_show)
    d = sub.add_parser("due")
    d.add_argument("--today")
    d.set_defaults(func=cmd_due)
    g = sub.add_parser("grade")
    g.add_argument("memo_id")
    g.add_argument("hyp_id")
    g.add_argument("outcome", choices=["hit", "miss", "void"])
    g.add_argument("--note", default="")
    g.set_defaults(func=cmd_grade)
    sub.add_parser("stats").set_defaults(func=cmd_stats)
    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
