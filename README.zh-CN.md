# whymoved

[English](README.md) | **简体中文**

**它为什么涨了？带出处的答案，找不到就说找不到。**

输入 `/why 英伟达`，whymoved 会先找出这次涨跌**具体发生在哪个时间段**，再看大盘和板块有没有一起动，最后只把**异动之前**就已经公开的新闻当作可能的原因。

零配置、不需要任何 API key，只依赖 Python 标准库。可以作为 [Agent Skill](https://agentskills.io) 在 Claude Code、Codex、Cursor 等工具里使用，也可以直接在命令行运行。

## 和别的「为什么涨跌」工具有什么不一样

问 AI「这只股票今天为什么跌」，它通常会抓当天传播最广的那条新闻。但这条新闻经常是**跌完之后**才发的，内容只是在描述下跌，比如「特斯拉股价下挫……」。那是行情报道，不是原因。

whymoved 坚持一条别的工具会跳过的规则：

> **异动结束之后才发布的新闻，不可能是这次异动的原因。**

为了执行这条规则，它分三步：

1. **定位异动窗口**：用分钟线找出能解释大部分涨跌的最短时间段，包括隔夜跳空（比如盘后发财报，会表现为第二天盘前的跳空）。
2. **对照大盘**：同一时间段里，SPY、QQQ 和所属板块 ETF 怎么走（加密货币对照 BTC 或 ETH）。如果是整个市场在跌，会先说清楚。
3. **按时间给新闻分类**：异动前 24 小时内或异动中发布的，列为「可能的触发」；异动之后发布的，或者只是复述涨跌的，单独列为「涨跌之后的报道」。后者可能点名了原因，但本身永远不会被当作原因。

## 示例

```
$ python3 skills/whymoved/scripts/why.py TSLA --when 2026-10-14

TSLA · Tesla, Inc.
涨跌 -3.02%  (10-13 16:00 → 10-14 20:00 ET)
异动窗口 08:30–09:55 ET: -2.45%  (占整段涨跌 81%)
大盘对照: SPY -0.73% · QQQ -0.88% · XLY -1.31%  → 部分来自大盘

可能的触发（异动前或异动中发布）:
  1. 10-14 07:16  The Motley Fool  Why Wall Street Is Cautious About Tesla, and Why I'm Not Worried
  2. 10-14 02:10  Yahoo Finance  Tesla Roadster Reveal Nears as Elon Musk Fuels ‘Back to the Future’ Easter-Egg Speculation — TSLA CEO Says ‘Timing Is Everything’
  3. 10-13 11:45  Yahoo Finance  Tesla Stock's $1.5 Trillion Valuation Leaves a Nearly $1 Trillion Question
  4. 10-13 18:48  Yahoo Finance  Could Tesla's Roadster Reveal Trigger Another Stock Crash?
  5. 10-13 10:15  Yahoo Finance  Tesla Trades at 219x Earnings. Here’s Why I’m Not Buying the Bet on Its Future.
涨跌之后的报道（不是原因，但可能点名了原因）:
  - 10-14 10:08  Barron's  Tesla Stock Dips. Uber Raises a Trillion-Dollar Question.
  - 10-15 10:15  Barron's  A Tesla-SpaceX Merger Could Be Weeks Away
  - 10-15 22:42  MarketWatch  Tesla finally delivers on its promise to create a flying car

排名最高的候选：#1，发布于异动开始前 74 分钟。用 AI Agent 运行可得到带推理的归因。
```

普通工具最可能引用的就是 Barron's 这条。但它比异动窗口结束还晚了 13 分钟，内容也只是在描述下跌，所以 whymoved 把它归为行情报道。

在 AI Agent 里运行时，这份证据会连同推理规则一起交给模型：先看时间、先大盘后个股、宁可说「没有明确新闻」也不编原因。最终给出一段带出处和置信度的简短回答。

## 安装

**Claude Code**

```
/plugin marketplace add drewliu123/whymoved
/plugin install whymoved
```

**Codex、Cursor、Gemini CLI 等支持 Agent Skills 的工具**

```
npx skills add drewliu123/whymoved -g
```

**直接用命令行**

```bash
git clone https://github.com/drewliu123/whymoved
python3 whymoved/skills/whymoved/scripts/why.py NVDA
```

## 用法

在 Agent 里直接问：「英伟达今天为什么跌」「比特币昨天为什么暴涨」「why is TSLA down」。

命令行：

```bash
python3 why.py NVDA                       # 最近一个交易日，中文简报
python3 why.py BTC --lang en              # 最近 24 小时，英文简报
python3 why.py TSLA --when 2026-10-14     # 指定日期
python3 why.py ETH --days 7               # 一整周
python3 why.py 英伟达 --json              # 给 Agent 用的结构化证据
```

## 覆盖范围

| 资产 | 行情来源 | 说明 |
|---|---|---|
| 美股和 ETF | Yahoo Finance 分钟线，含盘前盘后；当天行情以 Nasdaq 兜底 | 约 55 天内为 5 分钟线，更早为小时线 |
| 加密货币 | Coinbase 交易所 K 线 | 内置 30 个常见币种，Coinbase 上有 `XXX-USD` 交易对的都能用 |

新闻来自 Google News RSS。对照基准：SPY、QQQ，以及约 70 只热门股票对应的板块 ETF；加密货币对照 BTC 或 ETH。

## 局限

- 免费新闻搜索覆盖不到付费通讯社、公告原文和社交媒体。「没有明确新闻」的意思是「公开标题里没有」，不代表「没有原因」。
- 聚合平台的发布时间可能比原始报道晚几分钟，whymoved 留了 10 分钟容差。
- 命令行里的排序是规则打分，因果判断交给按 `SKILL.md` 推理的 Agent，或者交给你自己。
- 不构成投资建议。

## 路线图

- [ ] A 股和港股
- [ ] 财报日历和 SEC 公告作为一等证据
- [ ] 社交媒体信号（X、Reddit）作为旁证
- [ ] 预测市场

## 许可证

MIT
