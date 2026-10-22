---
name: whymoved
description: Explain why a stock, ETF or crypto asset moved, with sources and timestamps. Use when the user asks why something went up or down ("why is NVDA down today", "why did BTC pump yesterday", "英伟达今天为什么跌", "比特币为什么涨"), or wants the catalyst behind a price move. Finds the exact move window, checks the market and sector, and only accepts news published before the move as a possible cause.
---

# whymoved

Answer "why did X move?" with evidence, not vibes.

## Step 1: get the evidence

Run the bundled script. It needs only Python 3.9+, no API keys.

```bash
python3 <skill_dir>/scripts/why.py SYMBOL --json [--when today|yesterday|YYYY-MM-DD] [--days N]
```

- `SYMBOL`: US stock/ETF tickers (NVDA, TSLA, SPY) or crypto (BTC, ETH, SOL). Chinese names like 英伟达, 比特币 also work.
- `--when`: defaults to the latest session (stocks) or the last 24 hours (crypto).
- `--days N`: explain a multi-day move, e.g. "this week" → `--days 5`.

The JSON contains:

| Field | Meaning |
|---|---|
| `period.change` | the whole move being explained (stocks: previous regular close through pre/post-market) |
| `period.regular_session_change` | stocks only: close-to-close regular session, which is what most apps show as "today" |
| `window` | the shortest stretch of time that explains most of the move (`start`, `end`, `change`, `spans_market_closure`) |
| `benchmarks`, `market_context` | what SPY / QQQ / the sector ETF (or BTC/ETH) did in the same window; `market_wide`, `partly_market` or `asset_specific` |
| `notable` | false means the move is within ordinary noise |
| `news.candidates` | stories published in the 24h before the window or during it, ranked |
| `news.after_move` | stories published after the move, or ones that just describe it; **never a cause**, but they often name one |
| `why_ranked` | per story: why the heuristic scored it (tier-1 source, names a concrete event, opinion or speculation, ...) |
| `caveats` | includes warnings, e.g. only hourly prices this far back, or news search failed. Mention them if they weaken the answer |

## Step 2: reason about it

Follow these rules, in this order:

1. **Timing rule.** A cause must be public before or at the start of the window. Anything in `after_move` can only *point to* a cause; if it does, check whether that cause was public before `window.start`.
2. **Market first.** If `market_context` is `market_wide`, lead with that: the asset moved with its market or sector. Only then mention asset-specific news, and only as a possible addition.
3. **Not notable.** If `notable` is false, say the move is normal noise and stop unless the user insists.
4. **Earliest credible trigger.** Prefer the earliest credible story close to `window.start` over the most widely shared one. Wire services and the company itself beat commentary.
5. **No story fits.** Say "no clear news explains this move" and list what you checked. Never invent a reason.
6. **Optional extra search.** If you have web search, look for filings, earnings releases, official posts or macro data released just before `window.start`. Apply the same timing rule to anything you find.

## Step 3: answer

Keep it short. Use the user's language. Times in the asset's timezone (ET for US stocks, UTC for crypto).

```
NVDA −4.8% today. Most of it happened 09:30–10:05 ET (−3.9%).

Main cause: [headline] — Reuters, 09:12 ET (18 min before the drop)
Context: SMH −2.1% in the same window, so part of this is sector-wide.
Not a cause: "Nvidia shares slide after..." (CNBC, 10:40) reports the move.
Confidence: medium. Free news search can miss paywalled wires.
```

Always state a confidence level (high / medium / low) and why.
