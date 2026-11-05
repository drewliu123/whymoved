"""Marginal-preserving version: hawk bloc = w * comonotone + (1-w) * independent.
Both components keep each voter's own p, so the mixture does too. Non-hawks independent."""
import json, sys

def indep(ps):
    d = [1.0]
    for p in ps:
        n = [0.0] * (len(d) + 1)
        for k, v in enumerate(d):
            n[k] += v * (1 - p); n[k + 1] += v * p
        d = n
    return d

def comono(ps):
    s = sorted(ps, reverse=True) + [0.0]
    d = [0.0] * (len(ps) + 1)
    d[0] = 1 - s[0]
    for k in range(1, len(ps) + 1):
        d[k] = s[k - 1] - s[k]
    return d

def conv(a, b):
    n = [0.0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            n[i + j] += x * y
    return n

cfg = json.load(open(sys.argv[1], encoding="utf-8"))
hawks = [v["p"] for v in cfg["voters"] if v.get("bloc") == "hawk"]
others = indep([v["p"] for v in cfg["voters"] if v.get("bloc") != "hawk"])
mk = cfg["market"]; ms = sum(mk.values())
print(f"{'w(同向权重)':<12}" + "".join(f"{k+'票':>8}" for k in ["0", "1", "2", "3", "4+"]))
for w in cfg["w"]:
    h = [w * c + (1 - w) * i for c, i in zip(comono(hawks), indep(hawks))]
    t = conv(h, others)
    b = t[:4] + [sum(t[4:])]
    print(f"{w:<14}" + "".join(f"{x*100:>7.1f}%" for x in b))
print(f"{'盘口(归一)':<12}" + "".join(f"{mk[k]/ms*100:>7.1f}%" for k in ["0", "1", "2", "3", "4+"]))
