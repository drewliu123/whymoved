"""Command-line entry point: `why NVDA`, `why BTC --when yesterday`, `why 英伟达 --json`."""

from __future__ import annotations

import argparse
import json
import os
import sys

from .analyze import analyze
from .net import FetchError
from .report import to_dict, to_text


def default_lang(symbol: str) -> str:
    """Chinese if the user typed Chinese or runs a Chinese locale, English otherwise."""
    if any("一" <= ch <= "鿿" for ch in symbol):
        return "zh"
    for var in ("LC_ALL", "LC_MESSAGES", "LANG"):
        val = os.environ.get(var)
        if val:
            return "zh" if val.lower().startswith("zh") else "en"
    return "en"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="why", description="Why did a stock or crypto asset move? Sources and timestamps included.")
    p.add_argument("symbol", help="ticker or name: NVDA, TSLA, BTC, ETH, WIF-USD, 英伟达, 比特币 ...")
    p.add_argument("--when", default=None, help="today (default), yesterday, or a date like 2026-10-14")
    p.add_argument("--days", type=int, default=None, help="explain a multi-day move ending at --when")
    p.add_argument("--lang", default=None, choices=["zh", "en"], help="language of the text brief (default: from input and locale)")
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
        print(to_text(r, lang=a.lang or default_lang(a.symbol), max_items=a.max))
    return 0
