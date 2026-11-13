# 盈利质量与红旗筛查

## 什么时候用

公司经营、财报、估值或事件解释类研究，若已取得两期以上**同口径**报表（年报对年报、季报对季报），先跑一次质量筛查，再写判断。它回答的问题不是「公司好不好」，而是「这段增长是现金还是会计」「利润与现金为什么分叉」「投入是在扩张还是在吃老本」。

不做：不给买卖建议、不给舞弊结论、不用来替代读财报。红旗是核查清单，不是发现。

```bash
python3 "$TY_DIR/scripts/financial_quality.py" "$WORK/statements.json" [--out "$WORK/quality.json"]
```

退出码：0 通过，1 输入不符合契约，2 无法读取/解析。输出为确定性 JSON，可原样冻结到本轮工作目录。

## 输入

```json
{
  "schema_version": 1,
  "entity": "EXAMPLE", "currency": "USD", "scale": "million", "as_of": "2026-11-14",
  "periods": [
    {"id": "FY2024", "period_type": "fy", "period_start": "2023-07-01", "period_end": "2024-06-30",
     "revenue": 1000, "gross_profit": 500, "operating_profit": 200, "net_income": 150,
     "cfo": 180, "capex": 60, "depreciation_amortization": 80,
     "receivables": 120, "inventory": 80, "payables": 60,
     "total_assets": 900, "equity": 500, "debt": 200, "cash": 100,
     "share_based_comp": 40, "shares_diluted": 100, "tax_rate": 0.2}
  ]
}
```

- 必填：`schema_version`、`entity`、`currency`、`scale`、`periods[]`（至少两期）、每期 `id` / `period_end` / `revenue`。
- 期间：`period_type` 为 `fy` / `quarter` / `ltm`，全部期间必须同类型，混用直接拒绝（FQ2）；`period_start` 可选，但缺它就**不计算**周转与应计类指标，而不是假设一个天数。
- 数值字段可写裸数字，或 `{"value": 120, "claim_ids": ["C3"]}`。没有 `claim_ids` 的字段会列在输出的 `unattributed` 里——这是证据链尚未接上的提示，不是错误。
- 未列出的字段名直接拒绝（FQ1），避免把 `ebitda`、`fcf` 之类的自定义口径悄悄塞进来。所有比率输出为小数（0.42 而非 42%）。
- 可选字段 `pretax_income` 与 `income_tax` 用于推导税率：未给 `tax_rate` 时按两者之比计算，显式 `tax_rate` 优先。`ROIC` 需要 `equity`、`debt`、`cash` 齐全（投入资本 = 权益 + 有息负债 − 现金）；`cash` 只应填现金及等价物，不含短期投资，否则会低估 ROIC。

## 从主张账本装配

手写报表 JSON 等于把转录风险搬回来。若账本里已经有 `claim.metric`，用适配器直接装配：

```bash
python3 "$TY_DIR/scripts/quality_inputs.py" "$WORK/claims.json" \
  --entity "EXAMPLE" --out "$WORK/statements.json"
python3 "$TY_DIR/scripts/financial_quality.py" "$WORK/statements.json"
```

规则：

- 只取 `period_type` 为 fy / quarter / ltm、同时有 `period_start` 与 `period_end`、`scope=consolidated` 的 metric；`instant`、分部、缺起止日期的会被列进 `ignored` 并写明原因。
- 指标名按别名表映射（中英文皆可，如「营业收入」→revenue、「SBC」→share_based_comp）；映射不到的名字不会猜。
- 同一期间同一字段出现两个不同数值 → 直接失败并列出冲突，不静默取一个；数值相同则合并 `claim_ids`。
- `currency` 与 `scale` 必须能从账本唯一推断，否则用 `--currency` / `--scale` 显式给出；`tax_rate` 的 percent 会换算成小数。
- 输出仍保留每个字段的 `claim_ids` 与 `source_claims`，`financial_quality` 的 `unattributed` 因此为空。
- 多实体账本必须 `--entity` 选择；至少两个可比期间，否则拒绝。

## 输出指标

| 指标 | 公式 | 说明 |
| --- | --- | --- |
| gross_margin / operating_margin / net_margin | 对应利润 ÷ 收入 | 水平值，同时给出期间变化（ratio 差，不是百分比变化） |
| cash_conversion | CFO ÷ 净利润 | 净利为正时才计算；>1 表示利润有现金支撑 |
| accrual_ratio | (净利润 − CFO) ÷ 平均总资产 | 有上期总资产时用期初期末平均，否则退回期末总资产；正值高说明利润的应计占比大 |
| dso / dio / dpo | 应收（存货、应付）× 期间天数 ÷ 收入（成本） | 需要 `period_start` 才能算天数；COGS = 收入 − 毛利 |
| cash_cycle | DSO + DIO − DPO | 任一分项缺失则为 null |
| capex_intensity | 资本开支 ÷ 收入 | 重资产程度 |
| capex_to_da | 资本开支 ÷ 折旧摊销 | <1 提示维护性投入可能不足 |
| sbc_ratio | 股权激励 ÷ 收入 | 非 GAAP 利润与稀释的交叉检查 |
| invested_capital | 权益 + 债务 − 现金 | 定义写死在输出含义里，不用各家口径 |
| roic | 营业利润 × (1 − 税率) ÷ invested_capital | 缺税率时用税前营业利润并在口径说明中体现；投入资本必须为正 |
| incremental_margin | Δ营业利润 ÷ Δ收入 | 新增收入的边际利润；收入不变则不计算 |
| revenue_growth / share_growth | 环比 | 增长与稀释 |

字段缺失一律输出 `null`，不填补、不猜。`unattributed` 逐期列出没有 `claim_ids` 的字段。

## 红旗与默认阈值

| code | 默认阈值 | 指向 |
| --- | --- | --- |
| high_accruals | accrual_ratio > 0.10 | 利润的现金支撑，需核对一次性项目与收入确认 |
| weak_cash_conversion | cash_conversion < 0.80 | CFO 与净利的缺口，查应收、存货、递延 |
| growth_without_cash | 收入增长且现金转化下降 > 5pp | 增长质量，最值得优先查的一条 |
| receivables_outpacing_revenue | DSO 上升 > 15% | 账龄、客户结构、渠道压货 |
| inventory_build | DIO 上升 > 20% | 备货理由、跌价准备 |
| dilution | 股本增长 > 2% | 回购是否抵消稀释 |
| low_capex_vs_da | capex_to_da < 0.8 | 维护性投入不足或资产处置 |
| operating_deleverage | 收入增长但营业利润率降 > 2pp | 增量成本结构 |
| gross_margin_pressure | 毛利率降 > 2pp | 价格、结构、成本三选一 |
| negative_incremental_margin | 增量利润率为负 | 增长在消耗利润 |
| high_sbc | sbc_ratio > 0.10 | non-GAAP 与稀释 |

阈值可在调用时覆盖（`thresholds` 参数），代码里集中定义在 `THRESHOLDS`。severity 只有 `high` / `medium` 两级；没有「通过/不通过」的总结论。

## 边界与常见误用

- **不是舞弊判断**：Beneish 式的模型也需要行业与规模校准；这里只做可核查的指标提示。
- **行业差异大**：银行、REIT、SaaS 的周转与资本开支含义完全不同。默认阈值是经验值，跨行业比较前先改阈值或只看方向。
- **口径风险**：非 GAAP 净利润、LTM 拼期、分部与合并混用都会污染指标。输入前把口径写进 `scope` 与文本；有疑问就只跑 GAAP 口径。
- **不产生主张**：输出是计算记录，不自动成为 claims。要写进报告的数字与判断仍须走来源与主张账本；把这些数字挂成 `claim.metric` 或计算记录，再让结论引用它们。
- **不能替代读财报**：指标异常时，下一步永远是读附注与 MD&A，找机制，而不是加大红旗阈值。

## 嵌入报告

把同一份 statements 放进 `report.quality.statements` 即可随报告归档：校验会核对报表结构与字段的 `claim_ids`，渲染在附录生成「盈利质量」小节（指标表、环比变化、红旗）。可选 `quality.thresholds` 覆盖默认阈值。嵌入时指标在渲染时重新计算，不冻结结论；独立运行时用 `financial_quality.py`，两者输入结构一致。

## 真实示例

[微软 FY2024–FY2025 盈利质量示例](../../examples/msft-quality/README.md) 使用已冻结的官方表格数字：毛利率 68.8%、现金转化 1.34、资本开支/折旧 1.89、增量利润率 52.2%，红旗为空；资产负债表科目缺失时 DSO/ROIC 等输出 `null`。

```bash
python3 "$TY_DIR/scripts/financial_quality.py" examples/msft-quality/statements.json
```
