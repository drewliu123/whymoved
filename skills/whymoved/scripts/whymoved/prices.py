"""Price bars from free, keyless endpoints.

- Stocks / ETFs: Yahoo Finance chart API (intraday, incl. pre/post market)
- Crypto: Coinbase Exchange public candles
"""

from __future__ import annotations

import urllib.parse
from dataclasses import dataclass
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from .net import FetchError, fetch_json
from .symbols import Asset


@dataclass(frozen=True)
class Bar:
    t: datetime   # bar open time, UTC
    close: float


@dataclass
class Series:
    asset: Asset
    bars: list[Bar]
    interval_s: int
    display_name: str | None = None


def _yahoo_interval(start: datetime) -> tuple[str, int]:
    age = datetime.now(timezone.utc) - start
    if age < timedelta(days=55):
        return "5m", 300
    if age < timedelta(days=700):
        return "1h", 3600
    return "1d", 86400


def yahoo(symbol: str, start: datetime, end: datetime) -> tuple[list[Bar], int, str | None]:
    interval, seconds = _yahoo_interval(start)
    q = urllib.parse.urlencode({
        "period1": int(start.timestamp()),
        "period2": int(end.timestamp()),
        "interval": interval,
        "includePrePost": "true",
    })
    data, last = None, None
    for host in ("query2", "query1"):
        url = f"https://{host}.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(symbol)}?{q}"
        try:
            data = fetch_json(url, timeout=10, retries=1)
            break
        except FetchError as e:
            last = e
    if data is None:
        raise FetchError(f"Yahoo unavailable for {symbol}: {last}")
    chart = data.get("chart", {}) if isinstance(data, dict) else {}
    if chart.get("error") or not chart.get("result"):
        raise FetchError(f"Yahoo has no data for {symbol}: {chart.get('error')}")
    res = chart["result"][0]
    meta = res.get("meta", {})
    name = meta.get("longName") or meta.get("shortName")
    ts = res.get("timestamp") or []
    closes = (res.get("indicators", {}).get("quote") or [{}])[0].get("close") or []
    bars = [
        Bar(datetime.fromtimestamp(t, timezone.utc), float(c))
        for t, c in zip(ts, closes)
        if c is not None
    ]
    return bars, seconds, name


def coinbase(product: str, start: datetime, end: datetime) -> tuple[list[Bar], int]:
    span = end - start
    # Coinbase returns at most 300 candles per request.
    for seconds in (300, 900, 3600, 21600, 86400):
        if span.total_seconds() / seconds <= 300:
            break
    q = urllib.parse.urlencode({
        "granularity": seconds,
        "start": start.isoformat(),
        "end": end.isoformat(),
    })
    rows = fetch_json(f"https://api.exchange.coinbase.com/products/{product}/candles?{q}")
    if not isinstance(rows, list) or not rows:
        raise FetchError(f"Coinbase has no data for {product}")
    # row = [time, low, high, open, close, volume], newest first
    bars = sorted(
        (Bar(datetime.fromtimestamp(r[0], timezone.utc), float(r[4])) for r in rows),
        key=lambda b: b.t,
    )
    return bars, seconds


def nasdaq_today(symbol: str, kind: str = "stocks") -> tuple[list[Bar], int]:
    """Latest session, 1-minute bars, plus a synthetic bar for the previous close.

    Only covers the most recent session, so it is a fallback for "today" questions.
    Nasdaq encodes US/Eastern wall-clock time as if it were UTC.
    """
    url = f"https://api.nasdaq.com/api/quote/{urllib.parse.quote(symbol)}/chart?assetclass={kind}&charttype=rs"
    data = fetch_json(url, timeout=10, retries=1)
    d = (data or {}).get("data") if isinstance(data, dict) else None
    if not d or not d.get("chart"):
        if kind == "stocks":
            return nasdaq_today(symbol, "etf")
        raise FetchError(f"Nasdaq has no data for {symbol}")
    et = ZoneInfo("America/New_York")

    def as_utc(ms: int) -> datetime:
        naive = datetime.fromtimestamp(ms / 1000, timezone.utc).replace(tzinfo=None)
        return naive.replace(tzinfo=et).astimezone(timezone.utc)

    bars = [Bar(as_utc(p["x"]), float(p["y"])) for p in d["chart"] if p.get("y") is not None]
    prev_close = d.get("chartPrevClose")
    if bars and prev_close:
        day = bars[0].t.astimezone(et).date() - timedelta(days=1)
        while day.weekday() >= 5:  # skip weekends; holidays are rare enough for a fallback
            day -= timedelta(days=1)
        close_t = datetime.combine(day, time(15, 59), et).astimezone(timezone.utc)
        bars.insert(0, Bar(close_t, float(prev_close)))
    return bars, 60


def stock_bars(symbol: str, start: datetime, end: datetime, allow_today_fallback: bool) -> tuple[list[Bar], int, str | None]:
    try:
        return yahoo(symbol, start, end)
    except FetchError:
        if not allow_today_fallback:
            raise
        bars, sec = nasdaq_today(symbol)
        return bars, sec, None


def get_series(asset: Asset, start: datetime, end: datetime, today: bool = False) -> Series:
    if asset.kind == "crypto":
        bars, sec = coinbase(asset.coinbase_product, start, end)
        return Series(asset, bars, sec)
    bars, sec, name = stock_bars(asset.symbol, start, end, today)
    return Series(asset, bars, sec, display_name=name)
