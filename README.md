# whymoved

**English** | [简体中文](README.zh-CN.md)

[![CI](https://github.com/drewliu123/whymoved/actions/workflows/ci.yml/badge.svg)](https://github.com/drewliu123/whymoved/actions/workflows/ci.yml)
![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)
![Zero dependencies](https://img.shields.io/badge/dependencies-0-brightgreen)
![No API keys](https://img.shields.io/badge/API%20keys-none-brightgreen)
[![Agent Skill](https://img.shields.io/badge/Agent%20Skill-Claude%20Code%20%C2%B7%20Codex%20%C2%B7%20Cursor-8A2BE2)](https://agentskills.io)
[![License: MIT](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

**Ask why anything moved. Get receipts, not vibes.**

`/why TSLA` finds *when* the move actually happened, checks whether the whole market or sector moved with it, and only accepts news that was public **before** the move as a possible cause.

US stocks and ETFs, Hong Kong and mainland China A-shares, and crypto. Zero config, no API keys, Python standard library only. Works as an [Agent Skill](https://agentskills.io) in Claude Code, Codex, Cursor and other hosts, or as a plain CLI.

<p align="center"><img src="docs/demo.svg" alt="whymoved TSLA output: the move window, a market check, candidate triggers and stories reported after the move" width="860"></p>

## Why another "why is it moving" tool?

Most AI answers to "why did this stock drop?" grab the most-shared headline of the day. Very often that headline was published **after** the drop and simply describes it ("Tesla stock dips…"). That is a report, not a cause.

whymoved applies one rule other tools skip:

> **A story published after the move ended cannot be its cause.**

It enforces that rule with three steps:

1. **Find the move window.** From intraday bars, find the shortest stretch of time that explains most of the move, including overnight gaps (earnings after the close show up as a gap into the next pre-market).
2. **Check the market.** Compare the index and the sector over the same window: SPY, QQQ and a sector ETF for US stocks, Hang Seng for Hong Kong, CSI 300 / ChiNext / STAR 50 for A-shares, BTC or ETH for crypto. If a benchmark holds the asset itself (NVDA is ~20% of SMH), that share is removed first, so a stock cannot "explain itself".
3. **Sort the evidence by time.** News (Google News, plus Chinese-language media for HK and A-shares) and, for US stocks, **SEC filings** with their exact acceptance time. Candidates are items from the 24 hours before the window or during it. Items published after the move, or that merely restate it, go into a separate "reported after the move" list. They can name a cause, but are never treated as one.

It also tells you whether the move is worth explaining at all: the size is compared with the asset's **own** typical daily move, so 2% is noise for TSLA but news for KO.

## Example: Tesla, 21 October 2026

Tesla reported Q3 results after the close. The evening's obvious headlines were *"Tesla Third-Quarter Earnings Top Views"* and *"SpaceX and Tesla Consider Merger"*. Quote either one and you have the wrong answer: the stock sat flat after the release, and the drop began more than 30 minutes later.

The CLI output is in the screenshot above. Run inside an agent, the skill hands that evidence to the model together with explicit reasoning rules, and the answer looks like this:

```
TSLA −3.9% after hours on Oct 21, almost all of it 17:35–18:55 ET, while the Q3 earnings call was under way.

Not the earnings release: results were out before 17:00 ET ("Earnings Top Views", Yahoo Finance 16:58)
and the stock was flat afterwards ("Trades Flat After Hours", 17:13).
Likely cause: what was said on the call. Seeking Alpha's call recap (18:03) sits inside the window;
reports after the move name a capex guidance cut to $20B and a softer Optimus timeline
(Yahoo Finance 19:56, Investing.com 22:18).
Market: SPY −0.3%; Nasdaq 100 and the consumer discretionary sector were flat once Tesla is removed.
Not a cause: the SEC 8-K (20:41 ET) was filed after the drop; it confirms the results, not the timing.
Confidence: medium. The timing fits the call; the capex detail comes from after-the-move reports.
```

The rules the agent follows: timing first, market before company, "no clear news" over invented reasons, always a confidence level. They live in [`SKILL.md`](skills/whymoved/SKILL.md).

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

**Command line**

```bash
pipx install git+https://github.com/drewliu123/whymoved   # or: uv tool install git+https://...
whymoved NVDA
```

Or without installing anything:

```bash
git clone https://github.com/drewliu123/whymoved
python3 whymoved/skills/whymoved/scripts/why.py NVDA
```

## Usage

In an agent, just ask: *"why is NVDA down today?"*, *"why did BTC pump yesterday?"*, *"腾讯今天为什么跌"*, *"茅台为什么涨了"*.

From the command line:

```bash
whymoved NVDA                       # latest session, Chinese brief
whymoved BTC --lang en              # last 24 hours, English brief
whymoved TSLA --when 2026-10-21     # a specific day
whymoved ETH --days 7               # a whole week
whymoved 0700.HK                    # Hong Kong: 700, 0700.HK or 腾讯
whymoved 600519                     # Shanghai/Shenzhen: 600519, 300750.SZ or 茅台
whymoved 英伟达 --json              # machine-readable evidence for agents, with publisher URLs
```

## Coverage

| Asset | Prices | Evidence | Benchmarks |
|---|---|---|---|
| US stocks and ETFs | Yahoo Finance intraday incl. pre/post market; Nasdaq as a same-day fallback | Google News (en) + SEC EDGAR filings | SPY, QQQ, sector ETF for ~80 popular tickers |
| Hong Kong | Yahoo Finance intraday | Google News (en + zh) | Hang Seng, Hang Seng Tech ETF for tech names |
| Shanghai / Shenzhen | Yahoo Finance intraday | Google News (en + zh) | CSI 300, plus ChiNext or STAR 50 |
| Crypto | Coinbase Exchange candles | Google News (en) | BTC or ETH |

Intraday bars are 5-minute for the last ~55 days and hourly before that.

## Limits

- Free news search misses paywalled wires, social posts and many exchange announcements. Treat "no clear news" as "nothing in public headlines", not "no reason".
- Aggregator timestamps can lag the original report by a few minutes; whymoved allows a 10-minute tolerance. SEC filings often trail the press release by hours, so a filing after the move points to an event but does not prove its timing.
- The CLI's ranking is heuristic. Causality is judged by the agent following `SKILL.md`, or by you.
- SEC asks automated clients for a contact address. Set `WHYMOVED_CONTACT=you@example.com` to use your own.
- Not investment advice.

## Development

```bash
python3 -m unittest discover -s tests   # offline, no network
ruff check .
```

Reports of a wrong or missing explanation are the most useful issues: please include the command and output ([template](https://github.com/drewliu123/whymoved/issues/new?template=wrong_answer.yml)).

## Roadmap

- [x] Hong Kong and mainland China A-shares
- [x] SEC filings as first-class evidence
- [ ] Earnings calendar (know a release is coming before it lands)
- [ ] Exchange announcements for HK (HKEXnews) and A-shares (巨潮资讯)
- [ ] Social signals (X, Reddit) as corroboration
- [ ] Prediction markets

## License

MIT
