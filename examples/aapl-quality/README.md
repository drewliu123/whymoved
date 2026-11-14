# 苹果 FY2026：税项扰动已过，利润与现金流创新高

这个示例用一家结构不同的公司（苹果，财年 9 月底结束）验证同一套工具是否仍成立。

问题：**FY2024 的净利润下降是税项还是经营问题？后续两年是否反转？**

| 指标 | FY2024 | FY2025 | FY2026 | 读法 |
| --- | --- | --- | --- | --- |
| 收入 | 391,035 | 416,161 | 478,834 | 持续增长 |
| 营业利润 | 123,216 | 133,050 | 158,063 | 经营连增 |
| 有效税率 | 24.1% | 15.6% | 17.0% | 税项回落 |
| 净利润 | 93,736 | 112,010 | 132,175 | 已反转并创新高 |
| 经营现金流 | 118,254 | 111,482 | 145,097 | 高于净利润 |

结论：**FY2024 的净利润下降是税项，不是经营恶化；FY2025/26 已经反转。** FY2026 收入 +15.1%、营业利润 +18.8%、净利润 +18.0%，CFO 145,097 是净利润的 1.10 倍，capex 仅 9,041（占收入 1.9%）。

区分检验 T1：营业利润与税前利润上升、所得税从 16,741 升至 29,749 → 支持 H2（税项跳升）、削弱 H1（经营恶化）。

## 估值：39.7x 是五年最高

| 财年 | 2022 | 2023 | 2024 | 2025 | 当前 |
| --- | --- | --- | --- | --- | --- |
| P/E | 22.6x | 27.9x | 37.4x | 34.2x | **39.7x** |

39.7x 不是无盈利支撑——FY2026 净利润 132,175 百万美元、同比 +18%；但它已是五年最高。若 FY2027 增速降到 5% 以下，P/E 压缩会比盈利下降更快。

## 这个示例演示什么

- **跨公司通用性**：不同财年结束日（9 月底 vs 6 月底）、不同债务/现金结构，同一套契约、质量表与渲染仍然成立；示例已刷新到 FY2026。
- **税项拆解与确认**：只看净利润会把税项冲击误判成经营变差；FY2025/26 税率回落、利润反转，确认 FY2024 是一次性扰动。
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
