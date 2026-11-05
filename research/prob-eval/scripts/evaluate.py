#!/usr/bin/env python3
"""Score forecasting methods on the frozen question set.

  evaluate.py <questions.json> <forecasts.jsonl> [--split dev|test|all] [--baseline B0]

forecasts.jsonl rows: {"qid": "...", "method": "...", "p": 0.42}
Methods B0 (market at as_of), B1 (0.5) and B2 (dev base rate) are added automatically.
"""

import argparse
import json
import math
import random
import sys
from collections import defaultdict

CLIP = (0.01, 0.99)


def brier(p, y):
    return (p - y) ** 2


def logloss(p, y):
    p = min(max(p, CLIP[0]), CLIP[1])
    return -math.log(p if y else 1 - p)


def paired_bootstrap(diffs, n=10000, seed=7):
    rng = random.Random(seed)
    k = len(diffs)
    means = sorted(sum(diffs[rng.randrange(k)] for _ in range(k)) / k for _ in range(n))
    return means[int(0.025 * n)], means[int(0.975 * n)]


def split_of(qid):
    return "dev" if int(qid[1:]) <= 60 else "test"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("questions")
    ap.add_argument("forecasts")
    ap.add_argument("--split", default="dev", choices=["dev", "test", "all"])
    ap.add_argument("--baseline", default="B0")
    args = ap.parse_args()

    qs = {q["qid"]: q for q in json.load(open(args.questions))}
    qs = {k: v for k, v in qs.items() if args.split == "all" or split_of(k) == args.split}
    dev_qs = [q for q in json.load(open(args.questions)) if split_of(q["qid"]) == "dev"]
    base_rate = sum(q["yes"] for q in dev_qs) / len(dev_qs)

    preds = defaultdict(dict)
    for k, q in qs.items():
        preds["B0"][k] = q["p_market"]
        preds["B1"][k] = 0.5
        preds["B2"][k] = base_rate
    failures = defaultdict(int)
    for line in open(args.forecasts):
        if not line.strip():
            continue
        r = json.loads(line)
        if r["qid"] not in qs:
            continue
        p = r.get("p")
        if p is None or not isinstance(p, (int, float)) or not 0 <= p <= 1 or math.isnan(p):
            failures[r["method"]] += 1
            continue
        preds[r["method"]][r["qid"]] = float(p)

    ids = sorted(qs)
    base = preds[args.baseline]
    print(f"split={args.split} n={len(ids)} base_rate(dev)={base_rate:.3f}")
    print(f"{'method':<16}{'cover':>7}{'brier':>9}{'logloss':>9}{'d_brier_vs_' + args.baseline:>18}{'95% CI':>22}")
    rows = []
    for m, pm in preds.items():
        # Missing forecasts count as 0.5, per protocol.
        ps = [pm.get(i, 0.5) for i in ids]
        ys = [qs[i]["yes"] for i in ids]
        bs = sum(brier(p, y) for p, y in zip(ps, ys)) / len(ids)
        ll = sum(logloss(p, y) for p, y in zip(ps, ys)) / len(ids)
        diffs = [brier(pm.get(i, 0.5), qs[i]["yes"]) - brier(base[i], qs[i]["yes"]) for i in ids]
        lo, hi = paired_bootstrap(diffs) if m != args.baseline else (0.0, 0.0)
        rows.append((bs, m, len(pm), ll, sum(diffs) / len(ids), lo, hi))
    for bs, m, cov, ll, d, lo, hi in sorted(rows):
        print(f"{m:<16}{cov:>7}{bs:>9.4f}{ll:>9.4f}{d:>+18.4f}   [{lo:+.4f}, {hi:+.4f}]")
    if failures:
        print("invalid forecasts:", dict(failures))


if __name__ == "__main__":
    sys.exit(main())
