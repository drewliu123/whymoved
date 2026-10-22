"""Glue: pick the period, find the window, compare with the market, gather news."""

from __future__ import annotations

import math
import re
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from . import filings as filings_mod
from . import news as news_mod
from .net import FetchError
from .prices import Bar, Series, coinbase, daily_returns, get_series, stock_bars
from .symbols import MARKETS, Asset, resolve
from .window import MoveWindow, change_between, find_window

# Popular tickers -> sector ETF, so "the whole sector moved" can be detected.
SECTOR_ETF = {
    **{t: "SMH" for t in "NVDA AMD AVGO TSM INTC MU QCOM ARM ASML AMAT LRCX KLAC MRVL TXN ON SMCI".split()},
    **{t: "XLK" for t in "AAPL MSFT ORCL CRM ADBE NOW IBM CSCO ACN INTU PLTR".split()},
    **{t: "XLC" for t in "GOOGL GOOG META NFLX DIS T VZ TMUS".split()},
    **{t: "XLY" for t in "AMZN TSLA HD MCD NKE SBUX BKNG LOW".split()},
    **{t: "XLF" for t in "JPM BAC WFC GS MS C SCHW BLK V MA AXP COIN HOOD BRK-B".split()},
    **{t: "XLE" for t in "XOM CVX COP SLB OXY EOG".split()},
    **{t: "XLV" for t in "UNH LLY JNJ PFE MRK ABBV TMO NVO".split()},
    **{t: "KWEB" for t in "BABA PDD JD BIDU NIO XPEV LI TME BILI".split()},
}
HK_TECH = {f"{c}.HK" for c in "0700 9988 3690 1810 1024 9618 9999 9888 0981 2015 9866 9868 0268 0992 6618 9992".split()}

# Approximate index weights of the largest holdings. A benchmark that holds the asset moves
# partly *because of* the asset (NVDA is ~20% of SMH), so we strip that share out before
# deciding whether "the market moved". Rough figures; refresh now and then.
WEIGHTS = {
    "SPY": {"NVDA": .075, "MSFT": .065, "AAPL": .065, "AMZN": .04, "META": .03, "AVGO": .025,
            "GOOGL": .02, "GOOG": .017, "TSLA": .02, "BRK-B": .016, "JPM": .015},
    "QQQ": {"NVDA": .095, "MSFT": .085, "AAPL": .085, "AMZN": .055, "AVGO": .05, "META": .035,
            "GOOGL": .028, "GOOG": .026, "TSLA": .03, "NFLX": .025, "COST": .025},
    "SMH": {"NVDA": .20, "TSM": .10, "AVGO": .08, "AMD": .05, "ASML": .05, "QCOM": .04, "MU": .04, "INTC": .04},
    "XLK": {"AAPL": .13, "MSFT": .12, "ORCL": .03, "CRM": .025, "PLTR": .03},
    "XLC": {"META": .20, "GOOGL": .11, "GOOG": .09, "NFLX": .05},
    "XLY": {"AMZN": .22, "TSLA": .16, "HD": .06},
    "XLF": {"BRK-B": .12, "JPM": .10, "V": .08, "MA": .06},
    "XLE": {"XOM": .23, "CVX": .16},
    "XLV": {"LLY": .12, "JNJ": .07, "UNH": .06},
    "KWEB": {"BABA": .10, "PDD": .07},
    "^HSI": {"0700.HK": .08, "9988.HK": .08, "0005.HK": .08, "3690.HK": .05, "1810.HK": .05},
    "3033.HK": {"0700.HK": .09, "9988.HK": .09, "3690.HK": .08, "1810.HK": .08},
}


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
    daily_vol: float | None = None   # standard deviation of daily returns before the period
    period_days: int = 1


def _local_date(b: Bar, tz: ZoneInfo) -> date:
    return b.t.astimezone(tz).date()


def _regular_close(asset: Asset) -> time:
    hh, mm = MARKETS[asset.market][1].split(":")
    return time(int(hh), int(mm))


def _stock_period(series: Series, when: str | None, days: int | None) -> list[Bar]:
    tz = ZoneInfo(series.asset.exchange_tz)
    by_day: OrderedDict[date, list[Bar]] = OrderedDict()
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
    close = _regular_close(series.asset)
    regular = [b for b in prev if b.t.astimezone(tz).time() < close]
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
    if asset.market == "hk":
        out = [("^HSI", "Hang Seng Index")]
        if asset.symbol in HK_TECH:
            out.append(("3033.HK", "Hang Seng Tech ETF"))
    elif asset.market == "cn":
        out = [("000300.SS", "CSI 300")]
        if asset.code.startswith(("300", "301")):
            out.append(("399006.SZ", "ChiNext"))
        elif asset.code.startswith("688"):
            out.append(("000688.SS", "STAR 50"))
    else:
        out = [("SPY", "S&P 500"), ("QQQ", "Nasdaq 100")]
        etf = SECTOR_ETF.get(asset.symbol)
        if etf:
            out.append((etf, "sector"))
    return [(s, label) for s, label in out if s != asset.symbol]


def ex_asset(bench_change: float | None, weight: float, asset_change: float) -> float | None:
    """What the benchmark did without the asset's own contribution."""
    if bench_change is None or not weight:
        return bench_change
    return (bench_change - weight * asset_change) / (1 - weight)


def _one_benchmark(asset: Asset, sym: str, label: str, w: MoveWindow, p_start: datetime, p_end: datetime,
                   f_start: datetime, f_end: datetime, today: bool) -> dict | None:
    try:
        if asset.kind == "crypto":
            bars, sec = coinbase(f"{sym}-USD", f_start, f_end)
        else:
            bars, sec, _ = stock_bars(sym, f_start, f_end, today)
    except FetchError:
        return None
    row = {
        "symbol": sym,
        "label": label,
        "window_change": change_between(bars, sec, w.start, w.end),
        "period_change": change_between(bars, sec, p_start, p_end),
    }
    weight = WEIGHTS.get(sym, {}).get(asset.symbol, 0.0)
    if weight:
        row["asset_weight"] = weight
        row["window_change_ex_asset"] = ex_asset(row["window_change"], weight, w.pct)
    return row


def _context(w: MoveWindow, benchmarks: list[dict]) -> str:
    moves = [b.get("window_change_ex_asset", b["window_change"]) for b in benchmarks]
    moves = [m for m in moves if m is not None]
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


def _stdev(xs: list[float]) -> float | None:
    if len(xs) < 10:
        return None
    mean = sum(xs) / len(xs)
    return math.sqrt(sum((x - mean) ** 2 for x in xs) / (len(xs) - 1))


def analyze(raw_symbol: str, when: str | None = None, days: int | None = None, now: datetime | None = None,
            resolve_links: bool = False) -> Result:
    now = now or datetime.now(timezone.utc)
    asset = resolve(raw_symbol)
    f_start, f_end = _fetch_range(asset, when, days, now)
    is_today = when in (None, "", "today", "latest") and not days
    try:
        series = get_series(asset, f_start, f_end, today=is_today)
    except FetchError as e:
        kind = {"crypto": "crypto pair on Coinbase", "hk": "Hong Kong stock code", "cn": "Shanghai/Shenzhen stock code"}
        what = kind.get(asset.market, "US stock or ETF ticker")
        raise FetchError(f"no price data for '{raw_symbol}'. Is it a valid {what}? ({e})") from e

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
    result = Result(asset=asset, name=name, period_start=p_start, period_end=p_end, window=w,
                    period_days=max(1, days or 1))

    # Everything below is independent network I/O: run it side by side.
    sign = 1 if w.pct > 0 else -1
    want_filings = asset.kind == "stock" and asset.market == "us"
    with ThreadPoolExecutor(max_workers=8) as pool:
        bench_f = [pool.submit(_one_benchmark, asset, s, label, w, p_start, p_end, f_start, f_end, is_today)
                   for s, label in _benchmark_list(asset)]
        vol_f = pool.submit(daily_returns, asset, period[0].t)
        filings_f = pool.submit(filings_mod.sec_filings, asset.symbol, w.start, w.end) if want_filings else None
        news_f = pool.submit(news_mod.gather, asset, _search_name(name), w.start, w.end, sign,
                             None, (lambda: filings_f.result()) if filings_f else None)

        result.benchmarks = [r for r in (f.result() for f in bench_f) if r]
        result.context = _context(w, result.benchmarks)
        try:
            result.daily_vol = _stdev(vol_f.result())
        except Exception:  # the noise threshold falls back to fixed levels
            pass
        try:
            result.stories = news_f.result()
        except Exception as e:  # news is best-effort; prices are the backbone
            result.warnings.append(f"news search failed: {e}")
        if filings_f:
            try:
                filings_f.result()
            except Exception as e:
                result.warnings.append(f"SEC filings unavailable: {e}")

    if resolve_links:
        shown = []
        for t, k in (("candidate", 8), ("after_move", 5)):
            shown += sorted((s for s in result.stories if s.timing == t), key=lambda s: -s.score)[:k]
        news_mod.resolve_urls(shown)
    return result


_SUFFIX = re.compile(
    r"(,? (Limited|Co\.,? Ltd\.?|Co\.,?|Corporation|Corp\.?|Inc\.?|Holdings?|Group|Ltd\.?|plc|N\.V\.|S\.A\.)),?$", re.I)


def _search_name(name: str) -> str:
    """'NVIDIA Corporation' -> 'NVIDIA', 'Alibaba Group Holding Limited' -> 'Alibaba'."""
    prev = None
    while prev != name:
        prev, name = name, _SUFFIX.sub("", name.strip())
    return name.strip().rstrip(",")
