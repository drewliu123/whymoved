"""Glue: pick the period, find the window, compare with the market, gather news."""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from . import news as news_mod
from .net import FetchError
from .prices import Bar, Series, coinbase, get_series, stock_bars
from .symbols import Asset, resolve
from .window import MoveWindow, change_between, find_window

# Popular tickers -> sector ETF, so "the whole sector moved" can be detected.
SECTOR_ETF = {
    **{t: "SMH" for t in "NVDA AMD AVGO TSM INTC MU QCOM ARM ASML AMAT LRCX KLAC MRVL TXN ON SMCI".split()},
    **{t: "XLK" for t in "AAPL MSFT ORCL CRM ADBE NOW IBM CSCO ACN INTU PLTR".split()},
    **{t: "XLC" for t in "GOOGL GOOG META NFLX DIS T VZ TMUS".split()},
    **{t: "XLY" for t in "AMZN TSLA HD MCD NKE SBUX BKNG LOW".split()},
    **{t: "XLF" for t in "JPM BAC WFC GS MS C SCHW BLK V MA AXP COIN HOOD".split()},
    **{t: "XLE" for t in "XOM CVX COP SLB OXY EOG".split()},
    **{t: "XLV" for t in "UNH LLY JNJ PFE MRK ABBV TMO NVO".split()},
}
REGULAR_CLOSE = time(16, 0)


@dataclass
class Result:
    asset: Asset
    name: str
    period_start: datetime
    period_end: datetime
    window: MoveWindow
    benchmarks: list[dict] = field(default_factory=list)
    context: str = "asset_specific"
    stories: list[news_mod.Story] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def _local_date(b: Bar, tz: ZoneInfo) -> date:
    return b.t.astimezone(tz).date()


def _stock_period(series: Series, when: str | None, days: int | None) -> list[Bar]:
    tz = ZoneInfo(series.asset.exchange_tz)
    by_day: "OrderedDict[date, list[Bar]]" = OrderedDict()
    for b in series.bars:
        by_day.setdefault(_local_date(b, tz), []).append(b)
    dates = list(by_day)
    if len(dates) < 2:
        raise FetchError("not enough trading days in the price data")

    if when in (None, "", "today", "latest"):
        idx = len(dates) - 1
    elif when == "yesterday":
        idx = len(dates) - 2
    else:
        target = date.fromisoformat(when)
        if target not in by_day:
            raise FetchError(f"no trading data for {target} (weekend or market holiday?)")
        idx = dates.index(target)
    n = max(1, days or 1)
    first = idx - n + 1
    if first < 1:
        raise FetchError("not enough history before the requested period")

    prev = by_day[dates[first - 1]]
    regular = [b for b in prev if b.t.astimezone(tz).time() < REGULAR_CLOSE]
    baseline = (regular or prev)[-1]
    period = [baseline]
    for d in dates[first: idx + 1]:
        period.extend(by_day[d])
    return period


def _fetch_range(asset: Asset, when: str | None, days: int | None, now: datetime) -> tuple[datetime, datetime]:
    n = max(1, days or 1)
    if when in (None, "", "today", "latest"):
        end = now
    elif when == "yesterday":
        end = now if asset.kind == "stock" else datetime.combine(now.date(), time(), timezone.utc)
    else:
        d = date.fromisoformat(when)
        end = min(now, datetime.combine(d + timedelta(days=1), time(), timezone.utc) + timedelta(hours=6))
    if asset.kind == "stock":
        start = end - timedelta(days=int(n * 1.6) + 6)
    else:
        start = end - timedelta(days=n, hours=1)
    return start, end


def _crypto_period(series: Series, start: datetime) -> list[Bar]:
    before = [b for b in series.bars if b.t < start]
    after = [b for b in series.bars if b.t >= start]
    return ([before[-1]] if before else []) + after


def _benchmark_list(asset: Asset) -> list[tuple[str, str]]:
    if asset.kind == "crypto":
        return [("ETH", "Ethereum")] if asset.symbol == "BTC" else [("BTC", "Bitcoin")]
    out = [("SPY", "S&P 500"), ("QQQ", "Nasdaq 100")]
    etf = SECTOR_ETF.get(asset.symbol)
    if etf:
        out.append((etf, "sector"))
    return out


def _benchmarks(asset: Asset, w: MoveWindow, p_start: datetime, p_end: datetime, f_start: datetime, f_end: datetime, today: bool) -> list[dict]:
    rows = []
    for sym, label in _benchmark_list(asset):
        try:
            if asset.kind == "crypto":
                bars, sec = coinbase(f"{sym}-USD", f_start, f_end)
            else:
                bars, sec, _ = stock_bars(sym, f_start, f_end, today)
        except FetchError:
            continue
        rows.append({
            "symbol": sym,
            "label": label,
            "window_change": change_between(bars, sec, w.start, w.end),
            "period_change": change_between(bars, sec, p_start, p_end),
        })
    return rows


def _context(w: MoveWindow, benchmarks: list[dict]) -> str:
    moves = [b["window_change"] for b in benchmarks if b["window_change"] is not None]
    if not moves or w.pct == 0:
        return "asset_specific"
    # Strongest benchmark move in the same direction as the asset.
    same = [m for m in moves if m * w.pct > 0]
    if not same:
        return "asset_specific"
    ratio = max(abs(m) for m in same) / abs(w.pct)
    if ratio >= 0.6:
        return "market_wide"
    if ratio >= 0.3:
        return "partly_market"
    return "asset_specific"


def analyze(raw_symbol: str, when: str | None = None, days: int | None = None, now: datetime | None = None) -> Result:
    now = now or datetime.now(timezone.utc)
    asset = resolve(raw_symbol)
    f_start, f_end = _fetch_range(asset, when, days, now)
    is_today = when in (None, "", "today", "latest") and not days
    try:
        series = get_series(asset, f_start, f_end, today=is_today)
    except FetchError as e:
        kind = "crypto pair on Coinbase" if asset.kind == "crypto" else "US stock or ETF ticker"
        raise FetchError(f"no price data for '{raw_symbol}'. Is it a valid {kind}? ({e})") from e

    if asset.kind == "stock":
        period = _stock_period(series, when, days)
    else:
        if when in (None, "", "today", "latest"):
            p_start = now - timedelta(days=max(1, days or 1))
        elif when == "yesterday":
            p_start = datetime.combine(now.date() - timedelta(days=1), time(), timezone.utc)
        else:
            p_start = datetime.combine(date.fromisoformat(when), time(), timezone.utc)
        period = _crypto_period(series, p_start)
        if when not in (None, "", "today", "latest"):
            p_end = p_start + timedelta(days=max(1, days or 1))
            period = [b for b in period if b.t < p_end]
    if len(period) < 3:
        raise FetchError("not enough price bars in the requested period")

    w = find_window(period, series.interval_s)
    step = timedelta(seconds=series.interval_s)
    p_start, p_end = period[0].t + step, period[-1].t + step
    name = series.display_name or asset.name
    result = Result(asset=asset, name=name, period_start=p_start, period_end=p_end, window=w)

    result.benchmarks = _benchmarks(asset, w, p_start, p_end, f_start, f_end, is_today)
    result.context = _context(w, result.benchmarks)
    try:
        result.stories = news_mod.gather(asset, _search_name(name), w.start, w.end, 1 if w.pct > 0 else -1)
    except (FetchError, Exception) as e:  # news is best-effort; prices are the backbone
        result.warnings.append(f"news search failed: {e}")
    return result


def _search_name(name: str) -> str:
    """'NVIDIA Corporation' -> 'NVIDIA', 'Tesla, Inc.' -> 'Tesla'."""
    for suffix in (" Corporation", " Corp.", " Corp", ", Inc.", " Inc.", " Inc", " Holdings", " Ltd.", " plc", " N.V."):
        if name.endswith(suffix):
            name = name[: -len(suffix)]
    return name.strip().rstrip(",")
