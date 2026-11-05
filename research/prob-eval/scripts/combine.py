#!/usr/bin/env python3
"""Deterministic probability combination used by the candidate methods.

The model supplies judgments (prior, per-cluster log-likelihood ratios, trial
probabilities); this module owns the arithmetic so the final number is
reproducible and every contribution is auditable.
"""

import math

EPS = 1e-4
LLR_CAP = 1.5  # one information cluster can move odds by at most ~4.5x


def logit(p):
    p = min(max(p, EPS), 1 - EPS)
    return math.log(p / (1 - p))


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def mean(ps):
    return sum(ps) / len(ps)


def median(ps):
    s = sorted(ps)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def structured(prior, clusters, cap=LLR_CAP):
    """prior in (0,1); clusters: [{"id": str, "llr": float}]. Returns posterior and leave-one-out contributions."""
    llrs = [max(-cap, min(cap, float(c["llr"]))) for c in clusters]
    total = logit(prior) + sum(llrs)
    post = sigmoid(total)
    loo = []
    for c, l in zip(clusters, llrs):
        without = sigmoid(total - l)
        loo.append({"id": c.get("id"), "llr_used": l, "delta_pp": round((post - without) * 100, 2)})
    return post, loo


def extremize(p, a):
    """Logit-scale extremizing (a>1) or shrinking (a<1) toward 0.5."""
    return sigmoid(a * logit(p))


def pool_logit(p1, p2, w):
    """Weighted logit pooling: w on p1, 1-w on p2."""
    return sigmoid(w * logit(p1) + (1 - w) * logit(p2))
