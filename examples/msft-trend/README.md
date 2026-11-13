# 三年趋势示例：微软 FY2023–FY2025 的增长质量在恶化吗？

问题：**增长质量有没有恶化？** 单年筛查容易误判，这个示例用三个财年看趋势。

数据来自 SEC XBRL company facts（10-K 年度事实），全部数字可逐项复核：

| 指标 | FY2023 | FY2024 | FY2025 |
| --- | --- | --- | --- |
| 收入 | 211,915 | 245,122 | 281,724 |
| 经营现金流 | 87,582 | 118,548 | 136,162 |
| 净利润 | 72,361 | 88,136 | 101,832 |
| 应收 | 48,688 | 56,924 | 69,905 |
| 库存 | 2,500 | 1,246 | 938 |
| 应付 | 18,095 | 21,996 | 27,724 |

质量表（确定性重算）给出的关键读数：

- 现金转化 **1.34**（三年均高于 1）、应计比率 **−6.1%**（为负）；
- 应收周转天数 **90.3**、库存 **3.9**、应付 **114.9**，现金周期 **−20.7**（负值意味着增长不占用自有资金）；
- 毛利率 68.8%、营业利润率 45.6%，红旗筛查未触发。

结论：**增长质量总体稳定**，现金与营运资本结构支持利润；但应收天数从 FY2023 到 FY2025 上升，是唯一需要跟踪的压力点。区分检验 T1 支持 H1（质量稳定）、削弱 H2（靠应计与放宽信用），同时把应收上升写进观察与限制。

## 这个示例演示什么

- **三年趋势**：不是两个期间的单点比较，质量表按最新期间给指标、按相邻期间给变化。
- **应计与周转**：年报里有应收、库存、应付与总资产，于是 DSO / DIO / DPO / 现金周期 / 应计比率都能计算，而不是 null。
- **图表**：报告嵌入收入与经营现金流的折线图，数值与同源表一致。
- **缺少数据仍如实留白**：没有折旧摊销、债务与现金，`capex_to_da` 与 `ROIC` 为 null，并在限制里说明。

## 命令

```bash
# 从账本装配两期以上报表，再做质量筛查
python3 scripts/quality_inputs.py examples/msft-trend/research/work/claims.json > /tmp/msft-statements.json
python3 scripts/financial_quality.py /tmp/msft-statements.json

# 契约、渲染与一页纸
python3 scripts/analysis_contract.py check \
  --plan examples/msft-trend/research/work/plan.json \
  --report examples/msft-trend/research/work/report.json \
  --claims examples/msft-trend/research/work/claims.json \
  --sources examples/msft-trend/research/work/sources.json

python3 scripts/memo_pack.py examples/msft-trend/research/work/report.json \
  --claims examples/msft-trend/research/work/claims.json \
  --sources examples/msft-trend/research/work/sources.json
```

## 边界

- XBRL 事实可能被后续 10-K 重述；本示例只冻结抓取时点的数值。
- 没有折旧摊销、债务与现金，`capex_to_da` 与 `ROIC` 不可得；市值不在本示例范围。
- 三个财年不足以判断长期趋势，也不构成投资结论。
