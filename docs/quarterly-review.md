# 季度复核清单

每季度跑一次，目的不是产出新报告，而是确认已有 16 个示例仍然可信、可读、可追溯。

## 下一次复核：2027-01-15

选这个时间，是因为以下数据已经落地：

| 时间 | 事件 | 对应示例 |
| --- | --- | --- |
| 2026-12-09 | FOMC 12 月会议 | sp500-fomc-event（补第 24 个样本） |
| 2026-12 | AMAT FY2026 10-K（10 月财年） | ai-capex-transmission（最终分辨公司 vs 行业） |
| 2027-01 | 特斯拉 4Q26 财报 | tsla-price-cut-quality（FY2026 数据） |
| 2027-02 | 礼来、英伟达 FY2026 10-K | lly-growth-quality、nvda-growth-quality |
| 2027-06 | 耐克 FY2027 10-K | nke-turnaround |
| 2027-07 | 微软 FY2027 10-K | msft-cashflow、msft-earnings-quality、msft-trend |
| 2027-10 | 苹果 FY2027 10-K | aapl-quality |

## 六步检查

1. **时效表**：打开 [data-freshness.md](data-freshness.md)，逐行核对「最新数据期」是否仍成立；有新股就更新示例与本表。
2. **README 与报告一致**：抽查已刷新示例的 H1、结论段与数字，确认没有停在旧财年（第 154 轮曾发现两处）。
3. **估值口径**：打开 [valuation-coverage.md](valuation-coverage.md)，确认新增价格判断的示例已登记，P/E 与 P/B 口径未漂移。
4. **哈希与渲染**：运行 `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests`；确认所有 `examples/*/SHA256.json` 匹配、冻结渲染一致。
5. **质量门槛**：确认情景 ≤4、图表不混单位、含义不重复发现、answer ≤350 仍能拦住新问题。
6. **提交与推送**：本地提交后推送 `origin/main`，确认工作区干净（`journal/runs/` 除外）。

## 复核后的记录

- 在本文件追加一行日期、复核人、发现的问题与处理。
- 若数据不可得，记录原因与尝试路径，不用估算或二手数字补齐。
- 若某示例结论被新数据推翻，优先改写该示例，而不是新增一篇。

## 不做

- 不为「保持更新」而编造数据。
- 不因季度到了就强行新增示例。
- 不把复核变成改版式。
