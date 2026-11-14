# 数据时效表：每个示例停在哪个财年

这份页面记录 2026-11-14 时各示例的数据截点与下一次可更新时间。它不新增结论，只回答「这份报告现在有多新」。

| 示例 | 最新数据期 | 主要来源 | 下一次更新 |
| --- | --- | --- | --- |
| [msft-cashflow](../examples/msft-cashflow/README.md) | FY2026（2026-06） | SEC XBRL | FY2027 10-K，约 2027-07 |
| [msft-earnings-quality](../examples/msft-earnings-quality/README.md) | FY2026（2026-06） | SEC XBRL | FY2027 10-K，约 2027-07 |
| [msft-trend](../examples/msft-trend/README.md) | FY2026（2026-06） | SEC XBRL | FY2027 10-K，约 2027-07 |
| [msft-segments](../examples/msft-segments/README.md) | FY2025（2025-06） | 官方分部表 | 分部数据不可得，暂不更新 |
| [msft-reverse-dcf](../examples/msft-reverse-dcf/README.md) | FY2026 + 2026-11-13 收盘 | SEC XBRL + Nasdaq | 下一财年或价格变化 |
| [aapl-quality](../examples/aapl-quality/README.md) | FY2026（2026-09） | SEC XBRL | FY2027 10-K，约 2027-10 |
| [mega-cap-peers](../examples/mega-cap-peers/README.md) | 2026-11-13 收盘；最近财年盈利 | Nasdaq + SEC | 价格每日；盈利按各自财年 |
| [ai-capex-transmission](../examples/ai-capex-transmission/README.md) | FY2025（AMAT 2025-10；LRCX/KLAC 2025-06） | SEC XBRL | FY2026 10-K，约 2027-01 |
| [ai-capex-value-chain](../examples/ai-capex-value-chain/README.md) | FY2025 + NVDA FY2026 + 2026-11-13 收盘 | SEC + Nasdaq | 各公司下一财年 |
| [hyperscaler-capex-margins](../examples/hyperscaler-capex-margins/README.md) | FY2025 + MSFT FY2026 | SEC XBRL | 云厂商 FY2026，约 2027-02 |
| [sp500-fomc-event](../examples/sp500-fomc-event/README.md) | 2024–2026 年 10 月，23 次 | 美联储 + FRED | 2026-12-09 会议后补第 24 次 |
| [nvda-growth-quality](../examples/nvda-growth-quality/README.md) | FY2026（2026-01） | SEC XBRL | FY2027 10-K，约 2027-02 |
| [tsla-price-cut-quality](../examples/tsla-price-cut-quality/README.md) | FY2025（2025-12） | SEC XBRL | FY2026 10-K，约 2027-01 |
| [jpm-nim-provisions](../examples/jpm-nim-provisions/README.md) | FY2025 + 2026-11-13 收盘 | SEC + Nasdaq | 4Q26 财报，约 2027-01 |
| [lly-growth-quality](../examples/lly-growth-quality/README.md) | FY2025 + 2026-11-13 收盘 | SEC + Nasdaq | FY2026 10-K，约 2027-02 |
| [nke-turnaround](../examples/nke-turnaround/README.md) | FY2026（2026-05） | SEC XBRL | FY2027 10-K，约 2027-06 |

## 说明

- 「最新数据期」指报告实际引用的最后财年，不是公司已披露但未引用的数据。
- 微软分部明细停在 FY2025：FY2026 分部数据经微软 IR、SEC Archives 与 Financial Statement Data Sets 三次尝试均不可得；报告保留旧结构并记录边界。
- FOMC 2026 年 12 月 8–9 日会议尚未发生，未纳入；2026 年样本为截至 10 月的 7 次。
- 价格统一为 2026-11-13 Nasdaq 收盘；盈利按各公司最近财年，财年错位无法完全消除。

## 维护规则

1. 每季度检查一次本表；有新股时更新对应示例与本表。
2. 数据不可得时记录原因，不用估算或二手数字补齐。
3. 更新示例后同步更新 SHA256 清单与相关 README。
