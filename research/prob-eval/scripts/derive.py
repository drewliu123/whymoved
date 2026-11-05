#!/usr/bin/env python3
"""Turn raw trial outputs into per-method forecasts.

  derive.py <evidence_trials.json> <questions_all.json> <out.jsonl> [--params params.json]

Writes M1 (first direct trial), M2 (mean of direct trials), M2med, M3 (mean of
structured posteriors), M3prior, M23 (mean of M2 and M3), M4 (mean of market-
assisted trials) and, when params are given, tuned blends with the market.
"""

import json
import sys
from collections import defaultdict

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from combine import extremize, mean, median, pool_logit, structured  # noqa: E402


def derive(rows, market, params=None):
    by = defaultdict(lambda: defaultdict(list))
    for r in rows:
        if r.get("out"):
            by[r["qid"]][r["kind"]].append(r)
    out = {}
    for qid, kinds in by.items():
        f = {}
        d = [x["out"]["p"] for x in sorted(kinds["direct"], key=lambda x: x["trial"]) if 0 <= x["out"]["p"] <= 1]
        if d:
            f["M1"] = d[0]
            f["M2"] = mean(d)
            f["M2med"] = median(d)
        s = []
        priors = []
        for x in kinds["structured"]:
            o = x["out"]
            if 0 < o["prior"] < 1:
                post, _ = structured(o["prior"], o["clusters"])
                s.append(post)
                priors.append(o["prior"])
        if s:
            f["M3"] = mean(s)
            f["M3prior"] = mean(priors)
        if "M2" in f and "M3" in f:
            f["M23"] = (f["M2"] + f["M3"]) / 2
        k = [x["out"]["p"] for x in kinds["market"] if 0 <= x["out"]["p"] <= 1]
        if k:
            f["M4"] = mean(k)
        if params and qid in market:
            for name, (src, w, a) in params.items():
                if src in f:
                    f[name] = pool_logit(extremize(f[src], a), market[qid], w)
        out[qid] = f
    return out


def main():
    rows = json.load(open(sys.argv[1]))
    market = {q["qid"]: q["p_market"] for q in json.load(open(sys.argv[2]))}
    params = json.load(open(sys.argv[sys.argv.index("--params") + 1])) if "--params" in sys.argv else None
    with open(sys.argv[3], "w") as fh:
        for qid, f in derive(rows, market, params).items():
            for m, p in f.items():
                fh.write(json.dumps({"qid": qid, "method": m, "p": p}) + "\n")


if __name__ == "__main__":
    main()
