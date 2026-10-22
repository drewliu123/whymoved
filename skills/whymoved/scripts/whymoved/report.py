"""Turn an analysis Result into JSON (for agents) or a readable brief (for humans)."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from . import __version__
from .analyze import Result

RULES = [
    "A story published after the move window ended cannot be its cause. It may only point to one.",
    "Prefer the earliest credible story inside the lookback, not the most-shared one.",
    "If the market or sector moved the same way, say so before naming any company-specific cause.",
    "If no candidate story fits, answer 'no clear news' instead of inventing a reason.",
    "Cite source and timestamp for every reason you give.",
]

CAVEATS = [
    "Aggregator timestamps can lag the original report by minutes.",
    "Free news search misses paywalled wires, filings and social posts; check them if the answer matters.",
]


def _pct(x: float | None) -> str:
    return "n/a" if x is None else f"{x * 100:+.2f}%"


def to_dict(r: Result, max_items: int = 8) -> dict:
    w = r.window

    def story(s):
        return {
            "title": s.title,
            "source": s.source,
            "published": s.published.isoformat(),
            "minutes_from_window_start": round((s.published - w.start).total_seconds() / 60),
            "score": s.score,
            "kind": s.kind,
            "why_ranked": s.reasons,
            "url": s.url,
        }

    by = lambda t: sorted((s for s in r.stories if s.timing == t), key=lambda s: -s.score)
    return {
        "tool": f"whymoved {__version__}",
        "asset": {"symbol": r.asset.symbol, "kind": r.asset.kind, "market": r.asset.market, "name": r.name,
                  "timezone": r.asset.exchange_tz},
        "period": {"start": r.period_start.isoformat(), "end": r.period_end.isoformat(), "change": round(w.total_pct, 5)},
        "window": {
            "start": w.start.isoformat(),
            "end": w.end.isoformat(),
            "change": round(w.pct, 5),
            "share_of_period_move": round(w.share, 3),
            "spans_market_closure": w.is_gap,
            "price_start": w.price_start,
            "price_end": w.price_end,
        },
        "benchmarks": [{k: (round(v, 5) if isinstance(v, float) else v) for k, v in b.items()} for b in r.benchmarks],
        "market_context": r.context,
        "notable": is_notable(r),
        "typical_daily_move": None if r.daily_vol is None else round(r.daily_vol, 5),
        "move_vs_typical": None if move_multiple(r) is None else round(move_multiple(r), 2),
        "news": {
            "candidates": [story(s) for s in by("candidate")[:max_items]],
            "after_move": [story(s) for s in by("after_move")[:5]],
            "background": [story(s) for s in by("background")[:3]],
        },
        "rules": RULES,
        "caveats": CAVEATS + r.warnings,
    }


# Fallback when the asset's own volatility is unknown: below this the move is ordinary noise.
NOTABLE = {"stock": 0.015, "crypto": 0.025}
# A move this many times the asset's typical (one standard deviation) move is worth explaining.
NOTABLE_MULTIPLE = 1.0


def move_multiple(r: Result) -> float | None:
    """Size of the move relative to the asset's typical move over the same number of days."""
    if not r.daily_vol:
        return None
    move = max(abs(r.window.total_pct), abs(r.window.pct))
    return move / (r.daily_vol * r.period_days ** 0.5)


def is_notable(r: Result) -> bool:
    m = move_multiple(r)
    if m is not None:
        return m >= NOTABLE_MULTIPLE
    floor = NOTABLE.get(r.asset.kind, 0.02)
    return abs(r.window.total_pct) >= floor or abs(r.window.pct) >= floor


TEXT = {
    "en": {
        "period": "Move", "window": "Move window", "share": "{p}% of the move",
        "overshoot": "partly given back afterwards", "gap": "across a market closure",
        "bench": "Market check", "ctx": {
            "asset_specific": "mostly its own move", "partly_market": "partly the market",
            "market_wide": "mostly the market"},
        "cand": "Possible triggers (published before or during the window)",
        "after": "Reported after the move (not a cause, may name one)",
        "none": "No story published before the move clearly explains it.",
        "likely": "Top-ranked candidate: #1, published {m}. Run it through an AI agent to weigh causality.",
        "also": "If anything specific added to it, the closest match is #1, published {m}.",
        "before": "{n} min before the move started", "into": "{n} min after the move started",
        "market": {"stock": "The market or its sector moved the same way, so this looks like a broad move rather than company news.",
                   "crypto": "The wider crypto market moved the same way, so this looks like a market-wide move."},
        "quiet": "This is within normal day-to-day noise; there may be nothing to explain.",
        "typical": "{x:.1f}× a typical move",
    },
    "zh": {
        "period": "涨跌", "window": "异动窗口", "share": "占整段涨跌 {p}%",
        "overshoot": "之后回吐了一部分", "gap": "跨越休市跳空",
        "bench": "大盘对照", "ctx": {
            "asset_specific": "主要是自身行情", "partly_market": "部分来自大盘",
            "market_wide": "主要随大盘"},
        "cand": "可能的触发（异动前或异动中发布）",
        "after": "涨跌之后的报道（不是原因，但可能点名了原因）",
        "none": "没有找到异动前发布、能明确解释这次涨跌的新闻。",
        "likely": "排名最高的候选：#1，发布于{m}。用 AI Agent 运行可得到带推理的归因。",
        "also": "如果有个股因素叠加，最相关的是 #1，发布于{m}。",
        "before": "异动开始前 {n} 分钟", "into": "异动开始后 {n} 分钟",
        "market": {"stock": "大盘或板块同向波动，这次更像是整体行情，而不是个股消息。",
                   "crypto": "整个加密市场同向波动，这次更像是市场整体行情。"},
        "quiet": "这个幅度属于日常正常波动，可能并没有特别的原因。",
        "typical": "约为平日波动的 {x:.1f} 倍",
    },
}


TZ_LABEL = {"America/New_York": "ET", "Asia/Hong_Kong": "HKT", "Asia/Shanghai": "BJT"}


def _bench(b: dict) -> str:
    s = f"{b['symbol']} {_pct(b['window_change'])}"
    if b.get("window_change_ex_asset") is not None:
        s += f" (ex-asset {_pct(b['window_change_ex_asset'])})"
    return s


def _t(dt: datetime, tz: ZoneInfo, with_date: bool = False) -> str:
    local = dt.astimezone(tz)
    return local.strftime("%m-%d %H:%M" if with_date else "%H:%M")


def to_text(r: Result, lang: str = "zh", max_items: int = 5) -> str:
    L = TEXT.get(lang, TEXT["en"])
    tz = ZoneInfo(r.asset.exchange_tz)
    tzname = TZ_LABEL.get(r.asset.exchange_tz, "UTC")
    w = r.window
    multi_day = w.start.astimezone(tz).date() != w.end.astimezone(tz).date()
    share = L["overshoot"] if w.share > 1.05 else L["share"].format(p=f"{max(w.share, 0) * 100:.0f}")
    lines = [
        f"{r.asset.symbol} · {r.name}",
        f"{L['period']} {_pct(w.total_pct)}  ({_t(r.period_start, tz, True)} → {_t(r.period_end, tz, True)} {tzname})"
        + (f"  · {L['typical'].format(x=move_multiple(r))}" if move_multiple(r) is not None else ""),
        f"{L['window']} {_t(w.start, tz, multi_day)}–{_t(w.end, tz, multi_day)} {tzname}: {_pct(w.pct)}"
        f"  ({share}{'; ' + L['gap'] if w.is_gap else ''})",
    ]
    if r.benchmarks:
        bench = " · ".join(_bench(b) for b in r.benchmarks)
        lines.append(f"{L['bench']}: {bench}  → {L['ctx'][r.context]}")

    cands = sorted((s for s in r.stories if s.timing == "candidate"), key=lambda s: -s.score)[:max_items]
    after = sorted((s for s in r.stories if s.timing == "after_move"), key=lambda s: -s.score)[:3]
    lines.append("")
    lines.append(L["cand"] + ":")
    if cands:
        for i, s in enumerate(cands, 1):
            lines.append(f"  {i}. {_t(s.published, tz, True)}  {s.source}  {s.title}")
    else:
        lines.append("  —")
    if after:
        lines.append(L["after"] + ":")
        for s in after:
            lines.append(f"  - {_t(s.published, tz, True)}  {s.source}  {s.title}")
    lines.append("")
    if not is_notable(r):
        lines.append(L["quiet"])
    if r.context == "market_wide":
        lines.append(L["market"][r.asset.kind])
    if cands:
        mins = round((cands[0].published - w.start).total_seconds() / 60)
        m = L["before"].format(n=-mins) if mins < 0 else L["into"].format(n=mins)
        lines.append(L["also" if r.context == "market_wide" else "likely"].format(m=m))
    else:
        lines.append(L["none"])
    for warn in r.warnings:
        lines.append(f"! {warn}")
    return "\n".join(lines)
