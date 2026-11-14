# 盈利质量示例：微软 FY2026 利润增长有现金支撑吗？

问题：**FY2026 的利润增长有现金流支撑，还是主要来自会计口径？**

用官方损益表与现金流量表做确定性筛查，结论是**有现金支撑**，但资本开支强度在上升：

| 指标 | FY2024 | FY2025 | FY2026 | 读法 |
| --- | --- | --- | --- | --- |
| 经营现金流 | 118,548 | 136,162 | 182,935 | 为净利润的 1.37 倍 |
| 净利润 | 88,136 | 101,832 | 133,749 | 现金转化高于 1，利润有现金支撑 |
| 资本开支 | 44,477 | 64,551 | 115,948 | 为折旧的 3.38 倍，投入偏扩张 |
| 折旧摊销 | 22,287 | 34,153 | 34,300 | 资本开支强度升到 34.9% |

营业利润增加 19,095、收入增加 36,602，增量利润率约 **52%**，新增收入仍在创造利润。红旗筛查未触发；需要继续跟踪的是资本开支强度（占收入 22.9%）能否转化为后续收入。

## 这个示例演示什么

- **`report.quality` 嵌入完整报告**：两期 8 个报表字段全部带 `claim_ids`，盈利质量表、红旗与未挂字段提示都从冻结输入重算，报告里每个数字都能回到证据。
- **`change_explanation` 的完整结构**：两个竞争解释（现金支撑 vs 会计驱动）、一条区分检验（CFO/净利润 与资本开支/折旧）、观察结果支持 H1、削弱 H2。
- **数据不足时如实留白**：没有应收、存货与总资产，应计比率与周转天数为 null，并在限制中说明——不编造比率。

## 命令

```bash
# 盈利质量表（从账本装配，不手抄）
python3 scripts/quality_inputs.py examples/msft-earnings-quality/research/work/claims.json
python3 scripts/financial_quality.py examples/msft-earnings-quality/research/work/claims.json

# 契约与渲染
python3 scripts/analysis_contract.py check \
  --plan examples/msft-earnings-quality/research/work/plan.json \
  --report examples/msft-earnings-quality/research/work/report.json \
  --claims examples/msft-earnings-quality/research/work/claims.json \
  --sources examples/msft-earnings-quality/research/work/sources.json

# 一页纸
python3 scripts/memo_pack.py examples/msft-earnings-quality/research/work/report.json \
  --claims examples/msft-earnings-quality/research/work/claims.json \
  --sources examples/msft-earnings-quality/research/work/sources.json
```

## 边界

- 只覆盖两个财年，不能据此判断趋势拐点。
- 缺少应收、存货与总资产，应计与周转类指标不可得；报告如实标 null。
- 资本开支的「扩张 vs 维护」比值只是筛查线索，不构成投资结论。
- 与 [分部利润归因示例](../msft-segments/README.md)、[现金流示例](../msft-cashflow/README.md)使用同一套官方数字，口径一致。
