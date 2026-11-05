#!/usr/bin/env python3
"""Read-only Polymarket lookups via the public Gamma API.

  polymarket.py search "<keywords>"   find active events
  polymarket.py event  "<slug>"       outcome probabilities and price changes
"""

import argparse
import json
import sys
import urllib.parse
import urllib.request

GAMMA = "https://gamma-api.polymarket.com"


def fetch(path: str, params: dict):
    url = f"{GAMMA}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "touyan/0.1"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.load(resp)


def pct(value) -> str:
    if value in (None, ""):
        return "-"
    return f"{float(value) * 100:+.1f}pt"


def cmd_search(args) -> int:
    data = fetch("/public-search", {"q": args.query, "limit_per_type": args.limit, "events_status": "active"})
    events = data.get("events") or []
    if not events:
        print("没有找到活跃市场。换个关键词再试。")
        return 1
    for e in events:
        print(f"{e.get('slug')}\n    {e.get('title')}  | 截止 {str(e.get('endDate', ''))[:10]}")
    return 0


def cmd_event(args) -> int:
    events = fetch("/events", {"slug": args.slug})
    if not events:
        print(f"没有找到 slug={args.slug}", file=sys.stderr)
        return 1
    e = events[0]
    rows = []
    for m in e.get("markets", []):
        prices = json.loads(m.get("outcomePrices") or "[]")
        rows.append({
            "outcome": m.get("groupItemTitle") or m.get("question"),
            "prob": float(prices[0]) if prices else None,
            "chg_1d": m.get("oneDayPriceChange"),
            "chg_1w": m.get("oneWeekPriceChange"),
            "chg_1m": m.get("oneMonthPriceChange"),
            "closed": m.get("closed"),
        })
    rows.sort(key=lambda r: r["prob"] or 0, reverse=True)
    if args.json:
        print(json.dumps({
            "slug": e.get("slug"), "title": e.get("title"), "end_date": e.get("endDate"),
            "url": f"https://polymarket.com/event/{e.get('slug')}",
            "description": e.get("description"), "outcomes": rows,
        }, ensure_ascii=False, indent=2))
        return 0
    print(f"{e.get('title')}\nhttps://polymarket.com/event/{e.get('slug')}  | 截止 {str(e.get('endDate', ''))[:10]}\n")
    print(f"{'选项':<28}{'概率':>8}{'1天':>10}{'1周':>10}{'1月':>10}")
    for r in rows:
        prob = "-" if r["prob"] is None else f"{r['prob'] * 100:.1f}%"
        print(f"{str(r['outcome'])[:27]:<28}{prob:>8}{pct(r['chg_1d']):>10}{pct(r['chg_1w']):>10}{pct(r['chg_1m']):>10}")
    if args.rules:
        print("\n结算规则：\n" + (e.get("description") or "（无）"))
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search")
    s.add_argument("query")
    s.add_argument("--limit", type=int, default=8)
    s.set_defaults(func=cmd_search)
    e = sub.add_parser("event")
    e.add_argument("slug")
    e.add_argument("--json", action="store_true", help="机器可读输出")
    e.add_argument("--rules", action="store_true", help="附带结算规则原文")
    e.set_defaults(func=cmd_event)
    args = p.parse_args()
    try:
        return args.func(args)
    except OSError as exc:
        print(f"请求 Polymarket 失败：{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
