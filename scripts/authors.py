#!/usr/bin/env python3
"""Author library: track community authors and promote/demote them by review hit rate.

  authors.py list [--category C] [--status S]
  authors.py observe <handle> --platform x --category event_pricing [--memo M] [--claim "..."]
  authors.py grade <handle> --platform x --memo M hit|miss
"""

from __future__ import annotations

import argparse
import sys

from common import AUTHORS_FILE, load_json, now_iso, save_json

MIN_GRADED = 3
PROMOTE_AT = 0.60
DEMOTE_AT = 0.30


def key(handle: str, platform: str) -> str:
    return f"{platform}:{handle.lstrip('@').lower()}"


def load() -> dict:
    return load_json(AUTHORS_FILE, {"authors": {}})


def restatus(a: dict) -> None:
    graded = a["hits"] + a["misses"]
    if graded < MIN_GRADED:
        return  # too few reviews to move anyone
    rate = a["hits"] / graded
    a["status"] = "core" if rate >= PROMOTE_AT else "demoted" if rate <= DEMOTE_AT else "watch"


def ensure(db: dict, handle: str, platform: str, category: str | None) -> dict:
    k = key(handle, platform)
    a = db["authors"].setdefault(k, {
        "handle": handle.lstrip("@"), "platform": platform, "categories": [],
        "status": "watch", "hits": 0, "misses": 0, "observations": [], "first_seen": now_iso(),
    })
    if category and category not in a["categories"]:
        a["categories"].append(category)
    return a


def cmd_list(args) -> int:
    rows = list(load()["authors"].values())
    if args.category:
        rows = [a for a in rows if args.category in a["categories"]]
    if args.status:
        rows = [a for a in rows if a["status"] == args.status]
    rows.sort(key=lambda a: ({"core": 0, "watch": 1, "demoted": 2}[a["status"]], -(a["hits"] + a["misses"])))
    if not rows:
        print("作者库为空或没有匹配项。")
        return 0
    for a in rows:
        graded = a["hits"] + a["misses"]
        rate = f"{a['hits'] / graded:.0%}" if graded else "-"
        print(f"{a['status']:<8} {a['platform']}:@{a['handle']:<20} 命中 {a['hits']}/{graded} ({rate})  {','.join(a['categories'])}")
    return 0


def cmd_observe(args) -> int:
    db = load()
    a = ensure(db, args.handle, args.platform, args.category)
    a["observations"].append({"at": now_iso(), "memo": args.memo, "claim": args.claim})
    save_json(AUTHORS_FILE, db)
    print(f"已记录 {args.platform}:@{a['handle']}（{a['status']}）")
    return 0


def grade(db: dict, handle: str, platform: str, memo: str | None, outcome: str) -> dict:
    a = ensure(db, handle, platform, None)
    graded_memos = {g["memo"] for g in a.setdefault("grades", []) if g.get("memo")}
    if memo and memo in graded_memos:
        return a  # idempotent: one grade per author per memo
    a["hits" if outcome == "hit" else "misses"] += 1
    a["grades"].append({"at": now_iso(), "memo": memo, "outcome": outcome})
    restatus(a)
    return a


def cmd_grade(args) -> int:
    db = load()
    before = db["authors"].get(key(args.handle, args.platform), {}).get("status")
    a = grade(db, args.handle, args.platform, args.memo, args.outcome)
    save_json(AUTHORS_FILE, db)
    change = f"{before} → {a['status']}" if before and before != a["status"] else a["status"]
    print(f"{args.platform}:@{a['handle']} 记为 {args.outcome}，命中 {a['hits']}/{a['hits'] + a['misses']}，状态 {change}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("list")
    s.add_argument("--category")
    s.add_argument("--status", choices=["core", "watch", "demoted"])
    s.set_defaults(func=cmd_list)
    o = sub.add_parser("observe")
    o.add_argument("handle")
    o.add_argument("--platform", default="x")
    o.add_argument("--category")
    o.add_argument("--memo")
    o.add_argument("--claim", default="")
    o.set_defaults(func=cmd_observe)
    g = sub.add_parser("grade")
    g.add_argument("handle")
    g.add_argument("--platform", default="x")
    g.add_argument("--memo")
    g.add_argument("outcome", choices=["hit", "miss"])
    g.set_defaults(func=cmd_grade)
    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
