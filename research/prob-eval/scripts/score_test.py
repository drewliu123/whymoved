#!/usr/bin/env python3
"""Score the pre-registered test-set methods. Calibration parameters are fixed from the dev set."""

import glob
import json
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from combine import logit, mean, sigmoid  # noqa: E402

A, B = 0.7, -0.5  # frozen in PROTOCOL.md before the test run


def main(trial_dir, out_path):
    with open(out_path, "w") as fh:
        for fn in sorted(glob.glob(f"{trial_dir}/Q*.json")):
            rows = json.load(open(fn))
            qid = rows[0]["qid"]
            got = {k: [r["out"]["p"] for r in rows if r["kind"] == k and r["out"] and 0 <= r["out"]["p"] <= 1] for k in ("M4", "M5", "M1")}
            preds = {}
            if got["M4"]:
                preds["M4"] = mean(got["M4"])
                first = [r["out"]["p"] for r in rows if r["kind"] == "M4" and r["trial"] == 0 and r["out"]]
                if first:
                    preds["M4_single"] = first[0]
            if got["M5"]:
                preds["M5"] = mean(got["M5"])
                preds["M5cal"] = min(max(sigmoid(A * logit(preds["M5"]) + B), 0.03), 0.97)
            if got["M1"]:
                preds["M1"] = got["M1"][0]
            for m, p in preds.items():
                fh.write(json.dumps({"qid": qid, "method": m, "p": p}) + "\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
