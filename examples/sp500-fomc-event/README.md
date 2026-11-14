# 事件研究示例：FOMC 决议日后，标普 500 有稳定方向吗？

这是第一个基于**真实价格序列**的事件研究示例。数据来自两个官方来源：

- S&P 500 日度收盘：FRED `SP500` 序列（Federal Reserve Bank of St. Louis），2023-12-15 至 2024-12-31；
- 会议日期：Federal Reserve 2024 年 FOMC 日历（声明日取每次会议第二天）。

样本事前选定：2024 年 8 次会议，窗口 −3 / +3 个**观测点**（交易日），不做事件后筛选。

| 口径 | n | 中位 | 均值 | Q1 | Q3 | 最小 | 最大 | 为正比例 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 前窗（事件日前 3 点 → 事件日） | 8 | 0.51% | 0.45% | −1.09% | 1.56% | −2.96% | 4.56% | 50% |
| 后窗（事件日 → 后 3 点） | 8 | 1.35% | 0.46% | 0.11% | 1.84% | **−6.08%** | 3.24% | 75% |
| 全窗（前窗起点 → 后窗终点） | 8 | 1.61% | 0.89% | 0.48% | 2.07% | −5.00% | 4.75% | 75% |
| 后窗超额（相对 NASDAQCOM） | 8 | **−0.33%** | −0.22% | −0.59% | −0.11% | −1.53% | 1.87% | **25%** |
| 全窗超额（相对 NASDAQCOM） | 8 | **−0.53%** | −0.43% | −1.12% | 0.04% | −1.86% | 1.67% | 37.5% |
| 后窗超额（相对 DJIA） | 8 | **+0.37%** | +0.36% | +0.16% | +0.75% | −0.85% | 1.40% | **75%** |
| 全窗超额（相对 DJIA） | 8 | +0.17% | +0.40% | −0.17% | +0.53% | −0.35% | 2.41% | 50% |
| 后窗超额·beta 调整（NASDAQCOM β=0.673） | 8 | **+0.05%** | — | −0.04% | +0.17% | — | — | 75% |
| 全窗超额·beta 调整（NASDAQCOM β=0.673） | 8 | +0.02% | — | −0.49% | +0.47% | — | — | 50% |
| 后窗超额·beta 调整（DJIA β=0.912） | 8 | **+0.45%** | — | +0.20% | +0.84% | — | — | 75% |
| 全窗超额·beta 调整（DJIA β=0.912） | 8 | +0.27% | — | +0.10% | +0.58% | — | — | 87.5% |

**结论：不能把「FOMC 后偏涨」当方向依据，也不能声称存在稳定的事件效应。** 6/8 绝对收益为正，但 2024-07-31 会后 3 个观测点下跌约 6.1%。三组口径对照：绝对收益中位 +1.35%；简单超额纳斯达克 −0.33%（25% 为正）、道指 +0.37%（75%）；按 beta 调整后纳斯达克约 +0.05%（75%）、道指约 +0.45%（75%）。**方向与幅度随基准和 beta 改变**。样本只有 8 次、集中在同一个上涨年份，参考类分布是背景，不是预测。

## 这个示例演示什么

- **真实价格事件研究**：`event_study` 的完整价格序列路径（不是 returns-only），每个样本的事件日/前窗/后窗收盘都能回到 claims。
- **官方数据源组合**：FRED 的 S&P 500 与 NASDAQCOM 序列（T0）+ 美联储日历（T0）确定事件、窗口与基准。
- **多基准对照**：每个样本附带逐日对齐的纳斯达克与道指收盘，工具分别计算简单超额（未做 beta 调整）；两个基准给出相反方向，说明结论依赖基准选择。
- **诚实的统计边界**：不给 p 值、不给概率；明确「绝对收益、未去漂移、样本小、同一政策周期」。
- **尾部优先的写法**：结论不是「多数为正」，而是「正样本占比高但尾部主导均值」。
- **一张图看清背离**：按事件日期并列「后窗绝对收益」与「相对纳斯达克超额（β=1）」——7/8 为绝对正、6/8 为负超额，尾部 7 月 31 日同时是最大绝对跌幅与最大正超额（纳指跌得更多）。

## beta 怎么来的

beta 不是手填的，用 [beta.py](../../scripts/beta.py) 从 FRED 两条对齐序列回归：

```bash
python3 scripts/beta.py /tmp/sp500.csv /tmp/nasdaq.csv --csv --min-observations 200
# beta 0.6731, R² 0.9169, n 261
python3 scripts/beta.py /tmp/sp500.csv /tmp/djia.csv --csv --min-observations 200
# beta 0.9123, R² 0.6716, n 261
```

CSV 直接来自 FRED（`fredgraph.csv?id=SP500` 等，2023-12-15 至 2024-12-31）。beta 是回归假设：估计窗口、R² 与样本量都写在报告限制里，不是风险模型。

**beta 不是常数。** 把 beta 在估计值附近移动，后窗超额中位随之变化：

| 基准 | beta 0.5 / 0.7 | 估计值 | beta 0.9 / 1.1 |
| --- | --- | --- | --- |
| NASDAQCOM | +0.42%（β=0.5） | +0.05%（β=0.673） | **−0.24%（β=0.9）** |
| DJIA | +0.76%（β=0.7） | +0.45%（β=0.912） | +0.33%（β=1.1） |

纳斯达克的超额在 beta 0.5–0.9 之间跨零，道指始终为正。只报一个 beta 点估计，会把符号翻转藏起来。

## 命令

```bash
# 从冻结报告抽出事件研究输入并独立重算
python3 - <<'PY'
import json
from pathlib import Path
report = json.loads(Path("examples/sp500-fomc-event/research/work/report.json").read_text(encoding="utf-8"))
Path("/tmp/fomc-events.json").write_text(json.dumps(report["event_study"], ensure_ascii=False), encoding="utf-8")
PY
python3 scripts/event_study.py /tmp/fomc-events.json

# 契约、渲染与一页纸
python3 scripts/analysis_contract.py check \
  --plan examples/sp500-fomc-event/research/work/plan.json \
  --report examples/sp500-fomc-event/research/work/report.json \
  --claims examples/sp500-fomc-event/research/work/claims.json \
  --sources examples/sp500-fomc-event/research/work/sources.json

python3 scripts/memo_pack.py examples/sp500-fomc-event/research/work/report.json \
  --claims examples/sp500-fomc-event/research/work/claims.json \
  --sources examples/sp500-fomc-event/research/work/sources.json
```

## 边界

- 绝对收益，没有基准调整；2024 年指数整体上涨，事件窗口正收益可能来自市场漂移。
- 样本只有 8 次、同一政策周期；不能外推到不同利率环境。
- FRED 序列可能被后续修订；示例冻结抓取时点（2026-11-14）的数值。
- 窗口是观测点个数，不是自然日；不同交易日历下自然日长度不同。
