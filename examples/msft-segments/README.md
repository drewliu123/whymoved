# 分部利润归因示例：微软 FY2025

问题：**FY2025 三大分部哪一块贡献了主要营业利润增长？**

公开叙事常把微软的增长等同于智能云。用官方分部表拆开看，结论不同：

| 分部 | FY2024 营业利润 | FY2025 营业利润 | 同比增量 | 收入增量 |
| --- | --- | --- | --- | --- |
| Productivity and Business Processes | 59,661 | 69,773 | **+10,112** | +13,990 |
| Intelligent Cloud | 37,813 | 44,589 | +6,776 | **+18,801** |
| More Personal Computing | 11,959 | 14,166 | +2,207 | +3,811 |

利润增量最大的是**生产力与业务流程分部**，不是云；云的收入增量更大，但利润增量更低——收入增速不能直接当成利润贡献。

## 研究怎么做的

1. 取证：官方年报分部业绩表（与 [微软现金流示例](../msft-cashflow/README.md)共用同一份冻结表格），收入与营业利润按分部、按年入账为 12 条带 `metric` 的事实主张。
2. 模型：`driver_build` 以 FY2024 分部收入为基期、实际收入增速为量增长（官方无量价拆分，价增长显式设为 0）、FY2024/FY2025 分部利润率分别为 `base_margin` / `margin`。模型重算出的合并收入 **281,724** 与营业利润 **128,528**、利润变化 **19,095** 与官方报表完全一致。
3. 分析：竞争解释 H1（云贡献主要利润增量）与 H2（生产力贡献主要）；区分检验 T1 用分部营业利润增量观测，支持 H2、削弱 H1。
4. 交付：同源 Markdown / HTML；`report.md` 与 `report.html` 是渲染器输出，哈希记录在 `SHA256.json`。

## 命令

```bash
# 契约与固定算术
python3 scripts/analysis_contract.py check \
  --plan examples/msft-segments/research/work/plan.json \
  --report examples/msft-segments/research/work/report.json \
  --claims examples/msft-segments/research/work/claims.json \
  --sources examples/msft-segments/research/work/sources.json

# 一页纸
python3 scripts/memo_pack.py examples/msft-segments/research/work/report.json \
  --claims examples/msft-segments/research/work/claims.json \
  --sources examples/msft-segments/research/work/sources.json
```

## 这个示例演示什么

- 分部驱动模型（含 `base_margin`）能精确复现已披露的分部加总与合并利润。
- 「收入增速 ≠ 利润贡献」可以用确定性计算说清楚，而不是靠感觉。
- 完整研究链在真实披露上可跑通：取证 → 主张 → 模型 → 区分检验 → 同源交付。

## 边界

- 官方只给分部收入与营业利润，没有量价拆分；价增长按 0 处理，因此不能从本示例推出「涨价贡献多少」。
- 分部利润率受分部间成本分摊影响；示例不调整分摊口径。
- 结论只覆盖 FY2024→FY2025 两个财年，不构成对未来的预测。
