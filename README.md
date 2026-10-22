# whymoved

**English** | [简体中文](README.zh-CN.md)

**Ask why anything moved. Get receipts, not vibes.**

`/why NVDA` finds *when* the move actually happened, checks whether the whole market or sector moved with it, and only accepts news that was public **before** the move as a possible cause.

Zero config. No API keys. Python standard library only. Works as an [Agent Skill](https://agentskills.io) in Claude Code, Codex, Cursor and other hosts, or as a plain CLI.

## Why another "why is it moving" tool?

Most AI answers to "why did this stock drop?" grab the most-shared headline of the day. Very often that headline was published **after** the drop and simply describes it ("Tesla stock dips…"). That is a report, not a cause.

whymoved applies one rule other tools skip:

> **A story published after the move ended cannot be its cause.**

It enforces that rule with three steps:

1. **Find the move window.** From intraday bars, find the shortest stretch of time that explains most of the move, including overnight gaps (earnings after the close show up as a gap into the next pre-market).
2. **Check the market.** Compare SPY, QQQ and the sector ETF (or BTC/ETH for crypto) over the same window. If everything fell, it says so first.
3. **Sort news by time.** Candidates are stories from the 24 hours before the window or during it. Stories published after the move, or that merely restate it, go into a separate "reported after the move" list. They can name a cause, but are never treated as one.

## Example

```
$ python3 skills/whymoved/scripts/why.py TSLA --when 2026-10-14 --lang en

TSLA · Tesla, Inc.
Move -3.08%  (10-13 16:00 → 10-14 20:00 ET)
Move window 08:30–09:55 ET: -2.45%  (80% of the move)
Market check: SPY -0.73% · QQQ -0.88% · XLY -1.31%  → partly the market

Possible triggers (published before or during the window):
  1. 10-14 07:16  The Motley Fool  Why Wall Street Is Cautious About Tesla, and Why I'm Not Worried
  2. 10-14 02:10  Yahoo Finance  Tesla Roadster Reveal Nears as Elon Musk Fuels ‘Back to the Future’ Easter-Egg Speculation — TSLA CEO Says ‘Timing Is Everything’
  3. 10-13 11:45  Yahoo Finance  Tesla Stock's $1.5 Trillion Valuation Leaves a Nearly $1 Trillion Question
  4. 10-13 18:48  Yahoo Finance  Could Tesla's Roadster Reveal Trigger Another Stock Crash?
  5. 10-13 10:15  Yahoo Finance  Tesla Trades at 219x Earnings. Here’s Why I’m Not Buying the Bet on Its Future.
Reported after the move (not a cause, may name one):
  - 10-14 10:08  Barron's  Tesla Stock Dips. Uber Raises a Trillion-Dollar Question.
  - 10-15 10:15  Barron's  A Tesla-SpaceX Merger Could Be Weeks Away
  - 10-15 22:42  MarketWatch  Tesla finally delivers on its promise to create a flying car

Top-ranked candidate: #1, published 74 min before the move started. Run it through an AI agent to weigh causality.
```

The Barron's headline is the one a naive tool would quote. It was published 13 minutes *after* the window ended and describes the drop, so whymoved files it as a report.

Run inside an AI agent, the skill hands this evidence to the model with explicit reasoning rules (timing first, market before company, "no clear news" over invented reasons) and gets back a short answer with sources and a confidence level.

## Install

**Claude Code**

```
/plugin marketplace add drewliu123/whymoved
/plugin install whymoved
```

**Codex, Cursor, Gemini CLI and other Agent Skills hosts**

```
npx skills add drewliu123/whymoved -g
```

**Plain CLI**

```bash
git clone https://github.com/drewliu123/whymoved
python3 whymoved/skills/whymoved/scripts/why.py NVDA
```

## Usage

In an agent, just ask: *"why is NVDA down today?"*, *"why did BTC pump yesterday?"*, *"比特币为什么涨了"*.

From the command line:

```bash
python3 why.py NVDA                       # latest session, Chinese brief
python3 why.py BTC --lang en              # last 24 hours, English brief
python3 why.py TSLA --when 2026-10-14     # a specific day
python3 why.py ETH --days 7               # a whole week
python3 why.py 英伟达 --json              # machine-readable evidence for agents
```

## Coverage

| Asset | Prices | Notes |
|---|---|---|
| US stocks and ETFs | Yahoo Finance intraday, incl. pre/post market; Nasdaq as a same-day fallback | 5-minute bars for the last ~55 days, hourly before that |
| Crypto | Coinbase Exchange candles | 30 common tickers built in; anything listed as `XXX-USD` on Coinbase works |

News comes from Google News RSS. Benchmarks: SPY, QQQ and a sector ETF for ~70 popular tickers; BTC or ETH for crypto.

## Limits

- Free news search misses paywalled wires, filings and social posts. Treat "no clear news" as "nothing in public headlines", not "no reason".
- Aggregator timestamps can lag the original report by a few minutes; whymoved allows a 10-minute tolerance.
- The CLI's ranking is heuristic. Causality is judged by the agent following `SKILL.md`, or by you.
- Not investment advice.

## Roadmap

- [ ] A-shares and Hong Kong stocks
- [ ] Earnings calendar and SEC filings as first-class evidence
- [ ] Social signals (X, Reddit) as corroboration
- [ ] Prediction markets

## License

MIT
