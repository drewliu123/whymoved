"""Command-line entry point: `whymoved NVDA` (installed) or `python3 why.py NVDA` (skill)."""

from __future__ import annotations

import argparse
import json
import sys

from . import __version__
from .analyze import analyze
from .net import FetchError
from .report import to_dict, to_text


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="whymoved", description="Why did a stock, ETF or crypto asset move? Sources and timestamps included.")
    p.add_argument("symbol", help="ticker or name: NVDA, TSLA, BTC, 0700.HK, 600519, 英伟达, 腾讯, 比特币 ...")
    p.add_argument("--when", default=None, help="today (default), yesterday, or a date like 2026-10-14")
    p.add_argument("--days", type=int, default=None, help="explain a multi-day move ending at --when")
    p.add_argument("--lang", default="zh", choices=["zh", "en"], help="language of the text brief")
    p.add_argument("--json", action="store_true", help="print machine-readable evidence for AI agents")
    p.add_argument("--max", type=int, default=5, help="max candidate stories to show")
    p.add_argument("--version", action="version", version=f"whymoved {__version__}")
    a = p.parse_args(argv)
    try:
        r = analyze(a.symbol, when=a.when, days=a.days, resolve_links=a.json)
    except (FetchError, ValueError) as e:
        print(f"whymoved: {e}", file=sys.stderr)
        return 1
    if a.json:
        print(json.dumps(to_dict(r, max_items=max(a.max, 8)), ensure_ascii=False, indent=2))
    else:
        print(to_text(r, lang=a.lang, max_items=a.max))
    return 0
