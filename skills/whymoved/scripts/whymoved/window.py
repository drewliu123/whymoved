"""Find the move window: the shortest stretch of time that explains most of a move.

Daily percentage change says *how much*. The window says *when*, and "when" is what
lets us rule news in or out as a cause.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta

from .prices import Bar

# A window must explain at least this share of the strongest one-directional run.
CORE_SHARE = 0.7


@dataclass(frozen=True)
class MoveWindow:
    start: datetime          # close time of the last bar before the move (UTC)
    end: datetime            # close time of the bar where the move is complete (UTC)
    pct: float               # move inside the window, e.g. 0.052 = +5.2%
    total_pct: float         # move over the whole period
    price_start: float
    price_end: float
    is_gap: bool             # True if the window spans a market closure (overnight / weekend)

    @property
    def share(self) -> float:
        """How much of the period's move happened inside the window."""
        if self.total_pct == 0:
            return 0.0
        return self.pct / self.total_pct


def _log_returns(bars: list[Bar]) -> list[float]:
    return [math.log(b.close / a.close) for a, b in zip(bars, bars[1:]) if a.close > 0 and b.close > 0]


def find_window(bars: list[Bar], interval_s: int) -> MoveWindow:
    if len(bars) < 2:
        raise ValueError("need at least two price bars")
    bars = [b for b in bars if b.close > 0]
    r = _log_returns(bars)
    total = sum(r)
    # Direction of the move we are explaining. Flat day: use the larger absolute run.
    sign = 1.0 if total >= 0 else -1.0
    prefix = [0.0]
    for x in r:
        prefix.append(prefix[-1] + x)

    def best_run(sgn: float) -> tuple[float, int, int]:
        # Kadane on sgn * returns. Returns (value, i, j) where the run covers returns i..j-1.
        best, bi, bj = 0.0, 0, 0
        cur, ci = 0.0, 0
        for k, x in enumerate(r):
            if cur <= 0:
                cur, ci = 0.0, k
            cur += sgn * x
            if cur > best:
                best, bi, bj = cur, ci, k + 1
        return best, bi, bj

    run, i0, j0 = best_run(sign)
    if abs(total) < 1e-9:
        up, down = best_run(1.0), best_run(-1.0)
        sign, (run, i0, j0) = (1.0, up) if up[0] >= down[0] else (-1.0, down)
    if run <= 0:
        i0, j0 = 0, len(r)

    # Shrink to the shortest sub-run that still explains CORE_SHARE of the run.
    target = CORE_SHARE * run
    bi, bj = i0, j0
    for i in range(i0, j0):
        for j in range(i + 1, j0 + 1):
            if j - i >= bj - bi:
                break
            if sign * (prefix[j] - prefix[i]) >= target:
                bi, bj = i, j
                break

    a, b = bars[bi], bars[bj]
    step = timedelta(seconds=interval_s)  # bar timestamps are open times; prices are closes
    gap = any(
        (bars[k + 1].t - bars[k].t).total_seconds() > 3 * interval_s for k in range(bi, bj)
    )
    return MoveWindow(
        start=a.t + step,
        end=b.t + step,
        pct=b.close / a.close - 1,
        total_pct=bars[-1].close / bars[0].close - 1,
        price_start=a.close,
        price_end=b.close,
        is_gap=gap,
    )


def change_between(bars: list[Bar], interval_s: int, start: datetime, end: datetime) -> float | None:
    """Percent change between the last closes known at `start` and at `end`."""
    step = timedelta(seconds=interval_s)
    before = [b for b in bars if b.t + step <= start]
    upto = [b for b in bars if b.t + step <= end]
    if not before or not upto:
        return None
    return upto[-1].close / before[-1].close - 1
