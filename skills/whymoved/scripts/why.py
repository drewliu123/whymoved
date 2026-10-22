#!/usr/bin/env python3
"""whymoved CLI.

    python3 why.py NVDA                  # today's move, Chinese brief
    python3 why.py BTC --when yesterday --lang en
    python3 why.py TSLA --when 2026-10-14 --json
    python3 why.py ETH --days 7          # the whole week
    python3 why.py 0700.HK               # Hong Kong; 600519 for Shanghai, 300750 for Shenzhen
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from whymoved.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
