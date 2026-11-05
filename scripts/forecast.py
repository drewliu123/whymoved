#!/usr/bin/env python3
"""Turn a hypothesis into a reproducible probability.

  forecast.py finalize <forecast.json> --claims <claims.json>   compute and write final_prob
  forecast.py check <forecast.json> --claims <claims.json>      verify an already finalized file

The method comes from research/prob-eval: 185 resolved Polymarket questions,
forecast 14 days before resolution on frozen evidence, 60 used for development
and 125 held out (see RESULTS.md there).

  market       a tradable price exists at as_of. final_prob is that price.
               Letting a model adjust the price did not help on the held-out
               set; when it moved the price by more than 3 points it was right
               only 18 times in 54. Research explains the price, it does not
               overwrite it.
  independent  no price exists. Three rules-first forecasters read only the
               frozen evidence; final_prob is their mean, clipped to
               [0.03, 0.97]. A recalibration fitted on the dev set made the
               held-out score worse, so none is applied.

Exit 0 when the file is valid, 1 with a list of problems otherwise.
"""

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

from common import parse_date, save_json

METHOD_VERSION = "touyan-forecast-v2"
INDEPENDENT_CLIP = (0.03, 0.97)
MIN_TRIALS = 3
MODES = {"market", "independent"}
CONTRACT_FIELDS = ("question", "yes_means", "window_start", "window_end", "resolution_source")


def is_prob(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) and 0 <= x <= 1


def evidence_hash(ledger: dict, ids: list) -> str:
    """Hash the cited claims so a later edit to the ledger is detectable."""
    by_id = {c.get("id"): c for c in ledger.get("claims") or []}
    payload = [
        {"id": i, "text": by_id[i].get("text"), "urls": sorted(s.get("url", "") for s in by_id[i].get("sources") or [])}
        for i in sorted(ids) if i in by_id
    ]
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def compute(fc: dict) -> float:
    if fc["mode"] == "market":
        return round(fc["market_prob"], 4)
    p = sum(fc["trials"]) / len(fc["trials"])
    return round(min(max(p, INDEPENDENT_CLIP[0]), INDEPENDENT_CLIP[1]), 4)


def problems(fc: dict, ledger: dict, as_of: str, finalized: bool) -> list:
    errs = []
    tag = f"{fc.get('hypothesis_id', '?')}:"
    for field in ("hypothesis_id", "mode", "evidence_ids", *CONTRACT_FIELDS):
        if fc.get(field) in (None, "", []):
            errs.append(f"{tag} 缺少字段 {field}")
    mode = fc.get("mode")
    if mode not in MODES:
        errs.append(f"{tag} mode 必须是 {sorted(MODES)} 之一")
    if mode == "market":
        if not is_prob(fc.get("market_prob")):
            errs.append(f"{tag} market 模式需要 market_prob（截面时点的可成交价格）")
        if not fc.get("market_source"):
            errs.append(f"{tag} market 模式需要 market_source")
    if mode == "independent":
        trials = fc.get("trials") or []
        if len(trials) < MIN_TRIALS:
            errs.append(f"{tag} independent 模式需要至少 {MIN_TRIALS} 个 forecaster 结果")
        if not all(is_prob(t) for t in trials):
            errs.append(f"{tag} trials 必须全部是 [0,1] 内的有限数")
    start, end, cut = parse_date(fc.get("window_start", "")), parse_date(fc.get("window_end", "")), parse_date(as_of)
    if start and end and start > end:
        errs.append(f"{tag} window_start 晚于 window_end")
    if end and cut and end < cut:
        errs.append(f"{tag} 结算窗口在截面之前已结束，应直接查结果而不是预测")
    ids = {c.get("id") for c in ledger.get("claims") or []}
    missing = [i for i in fc.get("evidence_ids") or [] if i not in ids]
    if missing:
        errs.append(f"{tag} evidence_ids 引用了账本中不存在的结论：{missing}")
    if finalized and not errs:
        if fc.get("method_version") != METHOD_VERSION:
            errs.append(f"{tag} method_version 不是 {METHOD_VERSION}，请重新 finalize")
        elif fc.get("final_prob") != compute(fc):
            errs.append(f"{tag} final_prob 与按规则重算的 {compute(fc)} 不符")
        elif fc.get("evidence_hash") != evidence_hash(ledger, fc["evidence_ids"]):
            errs.append(f"{tag} 证据账本在 finalize 之后被改动过，请重新 finalize")
    return errs


def load(args):
    doc = json.loads(Path(args.forecast).read_text(encoding="utf-8"))
    ledger = json.loads(Path(args.claims).read_text(encoding="utf-8"))
    return doc, ledger


def cmd_finalize(args) -> int:
    doc, ledger = load(args)
    errs = [e for fc in doc.get("forecasts") or [] for e in problems(fc, ledger, doc.get("as_of", ""), False)]
    if not doc.get("forecasts"):
        errs.append("forecasts 为空")
    if errs:
        print("\n".join(errs), file=sys.stderr)
        return 1
    for fc in doc["forecasts"]:
        fc["final_prob"] = compute(fc)
        fc["method_version"] = METHOD_VERSION
        fc["evidence_hash"] = evidence_hash(ledger, fc["evidence_ids"])
    save_json(Path(args.forecast), doc)
    for fc in doc["forecasts"]:
        source = f"市场价（{fc['market_source']}）" if fc["mode"] == "market" else "无市场参照，3 个独立判断均值"
        print(f"{fc['hypothesis_id']} {fc['final_prob']:.1%}  {source}  {fc['question']}")
    return 0


def cmd_check(args) -> int:
    doc, ledger = load(args)
    errs = [e for fc in doc.get("forecasts") or [] for e in problems(fc, ledger, doc.get("as_of", ""), True)]
    if errs:
        print("\n".join(errs), file=sys.stderr)
        return 1
    print(f"{len(doc['forecasts'])} 条预测通过校验")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, func in (("finalize", cmd_finalize), ("check", cmd_check)):
        s = sub.add_parser(name)
        s.add_argument("forecast")
        s.add_argument("--claims", required=True)
        s.set_defaults(func=func)
    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
