# 2026 研究总览：19 个案例里的五个共同机制

这不是新数据，而是把已有 19 个完整示例放在一起看。每个判断都能回到对应报告与原始披露。

## 1. 资本开支正在吃掉现金流，而不是利润

- 微软 FY2026：CFO 182,935、capex 115,948，FCF 66,987，连续两年下降；capex/收入 34.9%（[msft-cashflow](../examples/msft-cashflow/README.md)）。
- 云厂商：利润率仍在扩张，FCF 利润率全部下降（[hyperscaler-capex-margins](../examples/hyperscaler-capex-margins/README.md)）。
- 埃克森：FY2025 分红+回购 375 亿，是 FCF 236 亿的 1.59 倍（[xom-capital-allocation](../examples/xom-capital-allocation/README.md)）。

**共同点**：利润表没有立刻恶化，现金先紧。**反例**：英伟达 CFO 仍在增长，capex 不是主要矛盾（[nvda-growth-quality](../examples/nvda-growth-quality/README.md)）。

## 2. 收入企稳不等于利润修复

- 耐克：收入 FY2026 +0.2%，但毛利率、净利率、CFO 都没有回到 FY2022–24（[nke-turnaround](../examples/nke-turnaround/README.md)）。
- 辉瑞：收入在 FY2023 腰斩后企稳，净利润仍只有峰值四分之一；研发费用刚性（[pfe-post-covid-reset](../examples/pfe-post-covid-reset/README.md)）。
- 特斯拉：收入 FY2024 见顶，利润率下滑先来自费用而非降价（[tsla-price-cut-quality](../examples/tsla-price-cut-quality/README.md)）。

**共同点**：收入是滞后指标，毛利率、费用率与现金流才是修复的证据。

## 3. 现金流质量的分化比利润增速更大

| 公司 | CFO/净利润 | 读法 |
| --- | --- | --- |
| 微软 FY2026 | 1.37 | 利润有现金支撑 |
| 苹果 FY2026 | 1.10 | 现金流强于利润 |
| 英伟达 FY2026 | 0.86 | 增长伴随应收与存货占用 |

**共同点**：同为「好公司」，现金转化差异很大；只看净利润会漏掉营运资本。

## 4. 估值与增长的错配是结构性的

- 英伟达 P/E 从 117x 降到 33x：盈利跑赢股价（[nvda-growth-quality](../examples/nvda-growth-quality/README.md)）。
- 特斯拉 P/E 363x：利润崩塌，估值没有（[tsla-price-cut-quality](../examples/tsla-price-cut-quality/README.md)）。
- 礼来 63x 处于自身 47–101x 区间中位（[lly-growth-quality](../examples/lly-growth-quality/README.md)）。
- 辉瑞 21x + 6% 股息率：低 P/E 是盈利低谷，高股息率是怀疑（[pfe-post-covid-reset](../examples/pfe-post-covid-reset/README.md)）。
- JPM P/B 2.54x 是十年最高（[jpm-nim-provisions](../examples/jpm-nim-provisions/README.md)）。

**共同点**：同一个 P/E 数字，在不同盈利周期里含义相反；估值必须先看盈利处于什么位置。

## 5. 事件效应不稳定，样本量比基准选择更重要

FOMC 2024–2026 共 23 次：绝对后窗中位 +1.35%→+0.45%→−0.02%，为正比例 75%→50%→42.9%；合并后基准超额趋零（[sp500-fomc-event](../examples/sp500-fomc-event/README.md)）。

**共同点**：单年 8 次样本会制造叙事；样本扩到 23 次，效应消失。

## 这些判断的边界

- 19 个示例都是历史数据，不是实时预测；财年终点不同，跨公司比较只作参照。
- 没有 forward 一致预期、EV/EBITDA 或分部估值。
- 微软分部明细、AMAT FY2026 等数据仍不可得（[data-sources](data-sources.md)）。
- 所有估值判断都是条件算术，不是目标价。

## 如果只看三篇

1. [微软现金流](../examples/msft-cashflow/README.md)：资本开支如何吃掉 FCF。
2. [辉瑞后疫情](../examples/pfe-post-covid-reset/README.md)：收入企稳为什么不等于利润修复。
3. [FOMC 事件研究](../examples/sp500-fomc-event/README.md)：样本扩展如何把效应拉回零。
