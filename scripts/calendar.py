#!/usr/bin/env python3
"""Compatibility CLI for the catalyst calendar.

The implementation lives in `catalyst_calendar.py` because a module named
`calendar` shadows the standard library and breaks any environment that has
already imported it. `python3 scripts/calendar.py` keeps working.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalyst_calendar import main

if __name__ == "__main__":
    raise SystemExit(main())
