# 估值覆盖图：哪些示例回答「价格是否已反映」

这份页面对应 2026-11-14 的示例集。它不新增数字，只把各示例的估值口径集中到一处，方便对照与审计。

## 已有价格判断的示例（9 个）

| 示例 | 估值指标 | 读数 | 口径与截点 | 回答的问题 |
| --- | --- | --- | --- | --- |
| [mega-cap-peers](../examples/mega-cap-peers/README.md) | P/E | 微软 29.2x；同行中位 37.2x | 2026-11-13 收盘 / 各自最近财年 EPS | 同行折价是否存在 |
| [msft-reverse-dcf](../examples/msft-reverse-dcf/README.md) | 反向 DCF 隐含增长 | 31.2%（5 年收敛 23.0%） | 523.88 美元；8% 折现、2.5% 终值 | 现价要求多少 FCF 增长 |
| [ai-capex-value-chain](../examples/ai-capex-value-chain/README.md) | P/E | AMAT 42.8x、KLAC 41.6x、LRCX 39.2x、NVDA 33.2x、云 27.4–37.2x | 2026-11-13 / 最近财年 EPS | 价值链各环节谁被定价得最满 |
| [jpm-nim-provisions](../examples/jpm-nim-provisions/README.md) | P/E、P/B | 16.9x、2.54x（十年最高） | 2026-11-13 / FY2025 净利与权益 | 净息差见顶时估值是否已反映 |
| [lly-growth-quality](../examples/lly-growth-quality/README.md) | P/E | 63.0x（四年区间 46.9–101.3x） | 2026-11-13 / FY2025 EPS | 高增长是否已被定价 |
| [tsla-price-cut-quality](../examples/tsla-price-cut-quality/README.md) | P/E | 362.9x（P/E 已失去意义） | 2026-11-13 / FY2025 EPS | 利润崩塌后价格在定价什么 |
| [aapl-quality](../examples/aapl-quality/README.md) | P/E | 39.7x（五年最高） | 2026-11-13 / FY2026 EPS | 好公司是否已在五年最高估值 |
| [nvda-growth-quality](../examples/nvda-growth-quality/README.md) | P/E | 33.2x（四年最低） | 2026-11-13 / FY2026 EPS | 股价新高是否等于估值新高 |
| [ai-capex-value-chain](../examples/ai-capex-value-chain/README.md) | AMAT 九年 P/E | 42.8x vs 11.1–26.9x | 财年末价格 / 当年 EPS | 设备溢价是周期高点还是结构性 |

## 刻意没有价格判断的示例

| 示例 | 原因 |
| --- | --- |
| msft-cashflow / msft-earnings-quality / msft-segments / msft-trend | 回答经营与现金流问题；估值由反向 DCF 示例承担，避免同一家公司两套价格叙事 |
| ai-capex-transmission | 回答「传导是否闭合」，不涉及价格 |
| hyperscaler-capex-margins | 回答利润率与现金流，价格留给价值链示例 |
| sp500-fomc-event | 事件研究回答方向分布，不以估值为中心 |
| nke-turnaround | 回答「企稳是否等于修复」，缺可比估值锚 |

## 口径说明

- **P/E**：收盘价 ÷（净利润 / 稀释加权股数）；各公司财年终点不同，倍数按各自最近财年。
- **P/B**：收盘价 × 普通股 ÷ 股东权益；用普通股而非稀释股数。
- **价格**：除特别说明外均为 2026-11-13 Nasdaq 收盘；未使用 forward 一致预期。
- **区间**：AMAT 为九年（FY2017–FY2025），苹果五年（FY2022–2026），礼来四年（FY2022–2025），英伟达四年（FY2023–2026）。

## 已知边界

- 没有 forward P/E、EV/EBITDA 或分部估值。
- 财年错位无法完全消除；跨公司比较只作参照。
- 估值判断不是目标价；反向 DCF 与 JPM 的条件映射都只是假设的算术。
