# 跨公司示例：苹果 FY2024 净利润为什么下降？

前四个示例都基于微软。这个示例用一家结构不同的公司（苹果，财年 9 月底结束）验证同一套工具是否仍成立。

问题：**FY2024 营业利润增长，为什么净利润反而下降？**

| 指标 | FY2023 | FY2024 | 读法 |
| --- | --- | --- | --- |
| 营业利润 | 114,301 | 123,216 | 经营仍在改善 |
| 税前利润 | 113,736 | 123,485 | 税前也在增长 |
| 所得税 | 16,741 | 29,749 | 税项大幅跳升 |
| 净利润 | 96,995 | 93,736 | 被税项拉低 |

结论：**净利润下降来自税项，不是经营恶化**。经营利润率 31.5%（上年 29.8%）、毛利率 46.2%，经营现金流 118,254 高于净利润，资本开支强度仅 2.4%，现金周期约 −75 天，质量筛查未触发红旗。

区分检验 T1：营业利润与税前利润上升、所得税从 16,741 升至 29,749 → 支持 H2（税项跳升）、削弱 H1（经营恶化）。

## 这个示例演示什么

- **跨公司通用性**：不同财年结束日（9 月底 vs 6 月底）、不同债务/现金结构，同一套契约、质量表与渲染仍然成立。
- **税项拆解**：只看净利润会把税项冲击误判成经营变差；税前利润与所得税单列后方向相反。
- **ROIC 的口径陷阱**：账面 ROIC 约 **75.6%**，但苹果的权益被回购压低、现金不含短期投资，数值偏高，**不做跨公司比较**——已在限制中写明。

## 命令

```bash
python3 scripts/quality_inputs.py examples/aapl-quality/research/work/claims.json > /tmp/aapl-statements.json
python3 scripts/financial_quality.py /tmp/aapl-statements.json

python3 scripts/analysis_contract.py check \
  --plan examples/aapl-quality/research/work/plan.json \
  --report examples/aapl-quality/research/work/report.json \
  --claims examples/aapl-quality/research/work/claims.json \
  --sources examples/aapl-quality/research/work/sources.json

python3 scripts/memo_pack.py examples/aapl-quality/research/work/report.json \
  --claims examples/aapl-quality/research/work/claims.json \
  --sources examples/aapl-quality/research/work/sources.json
```

## 数据来源与边界

- 数据来自 SEC XBRL company facts（CIK 0000320193，FY2023/FY2024 10-K 年度值），逐项核对后冻结；抓取时点 2026-11-14。
- 税项的具体一次性来源（如欧盟税务事项）需要读年报附注；本示例只核对到数字层面，不替读者下结论。
- 未取得折旧摊销，`capex_to_da` 为 null。
- 两个财年不足以判断长期趋势。
