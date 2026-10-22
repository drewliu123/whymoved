#!/usr/bin/env python3
"""whymoved CLI.

    python3 why.py NVDA                  # today's move, Chinese brief
    python3 why.py BTC --when yesterday --lang en
    python3 why.py TSLA --when 2026-10-14 --json
    python3 why.py ETH --days 7          # the whole week
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from whymoved.analyze import analyze  # noqa: E402
from whymoved.net import FetchError  # noqa: E402
from whymoved.report import to_dict, to_text  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="why", description="Why did a stock or crypto asset move? Sources and timestamps included.")
    p.add_argument("symbol", help="ticker or name: NVDA, TSLA, BTC, ETH, 英伟达, 比特币 ...")
    p.add_argument("--when", default=None, help="today (default), yesterday, or a date like 2026-10-14")
    p.add_argument("--days", type=int, default=None, help="explain a multi-day move ending at --when")
    p.add_argument("--lang", default="zh", choices=["zh", "en"], help="language of the text brief")
    p.add_argument("--json", action="store_true", help="print machine-readable evidence for AI agents")
    p.add_argument("--max", type=int, default=5, help="max candidate stories to show")
    a = p.parse_args(argv)
    try:
        r = analyze(a.symbol, when=a.when, days=a.days)
    except (FetchError, ValueError) as e:
        print(f"whymoved: {e}", file=sys.stderr)
        return 1
    if a.json:
        print(json.dumps(to_dict(r, max_items=max(a.max, 8)), ensure_ascii=False, indent=2))
    else:
        print(to_text(r, lang=a.lang, max_items=a.max))
    return 0


if __name__ == "__main__":
    sys.exit(main())
