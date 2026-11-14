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

**结论：不能把「FOMC 后偏涨」当方向依据。** 6/8 绝对收益为正，但 2024-07-31 会后 3 个观测点下跌约 6.1%；更关键的是，**相对纳斯达克**的后窗超额中位约 −0.33%、为正仅 25%——绝对收益主要来自市场整体上涨，加基准后方向反转。样本只有 8 次、集中在同一个上涨年份，参考类分布是背景，不是预测。

## 这个示例演示什么

- **真实价格事件研究**：`event_study` 的完整价格序列路径（不是 returns-only），每个样本的事件日/前窗/后窗收盘都能回到 claims。
- **官方数据源组合**：FRED 的 S&P 500 与 NASDAQCOM 序列（T0）+ 美联储日历（T0）确定事件、窗口与基准。
- **基准调整**：每个样本附带逐日对齐的纳斯达克收盘，工具计算简单超额（未做 beta 调整）；加基准后方向从正转负。
- **诚实的统计边界**：不给 p 值、不给概率；明确「绝对收益、未去漂移、样本小、同一政策周期」。
- **尾部优先的写法**：结论不是「多数为正」，而是「正样本占比高但尾部主导均值」。

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
