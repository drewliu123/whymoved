# AI 资本开支：设备同行接住了，AMAT 掉队

这是基于真实官方数据的行业传导示例。问题：**云厂商资本开支的增长，是否同幅传导到设备商收入、毛利与现金？**

数据来自 SEC XBRL 的 10-K 年度事实，六家公司各一个来源：

- 超大规模厂商资本开支：Microsoft（FY2025-06）、Alphabet（FY2025-12）、Amazon（FY2025-12）；
- 半导体设备商：Applied Materials（FY2025-10）、Lam Research（FY2025-06）、KLA（FY2025-06）。

| 节点 | FY2024 | FY2025 | 同比 |
| --- | --- | --- | --- |
| 三家云厂商资本开支合计 | 180,011 | 287,817 | **+59.9%** |
| AMAT 收入 | 27,176 | 28,368 | **+4.4%** |
| LRCX 收入 | 14,905 | 18,436 | **+23.7%** |
| KLAC 收入 | 9,812 | 12,156 | **+23.9%** |
| AMAT 经营现金流 | 8,677 | 7,958 | **−8.3%** |
| LRCX 经营现金流 | 4,652 | 6,173 | **+32.7%** |
| KLAC 经营现金流 | 3,309 | 4,082 | **+23.4%** |

（单位：百万美元）

**结论：行业接住了 AI 资本开支，掉队的是 AMAT。** 设备同行收入增约 24%、现金流增 23%–33%，AMAT 收入只增 4.4%、现金流下降 8.3%。用「设备环节没接住」解释 AMAT 的弱增长是错的；问题更可能在产品结构、客户份额或中国收入。

## 传导链

```
CAPEX（三家云厂商资本开支）
  → DELIVERY（设备交付与验收，瓶颈：1–4 个季度）
  → REVENUE（AMAT 收入，+4.4%）
  → MARGIN（毛利率 48.7%）
  → CASH（经营现金流 −8.3%）
```

- 节点与边都带 `claim_ids`：数字来自各家公司的 XBRL 事实，机制（采购→交付→验收→收入）是明确标注的 inference。
- 传导链仍以 AMAT 为样本；同行对照说明瓶颈不在行业需求，而在 AMAT 公司层面，因此 `DELIVERY` 的解释权重被下调。
- 报告会给出每个节点到瓶颈的距离、路径与「未到达瓶颈」的警告。

## 这个示例演示什么

- **同行对照推翻行业解释**：LRCX、KLAC 收入增约 24%、现金流增 23%–33%，AMAT 只有 4.4% 与 −8.3%；同样的行业顺风，结果不同，问题指向公司变量。
- **开头 30 秒**：执行摘要三句话给结论、反直觉与下一步；两张图分别展示「三家公司收入/现金流增速」与「AMAT 毛利率上升、现金流率下降」。
- **节点证据**：每个数字都能回到具体公司的 10-K 年度事实，而不是行业报告里的二手汇总。
- **瓶颈假设修正**：从「行业交付瓶颈」改为「AMAT 公司因素」，并留下产品结构/客户份额/中国收入三个待验证方向。
- **财年错位的诚实处理**：AMAT 财年 10 月结束，LRCX/KLAC 与云厂商 6 月/12 月结束；同比比较存在期间错位，已写进限制。

## 命令

```bash
# 从冻结报告抽出传导图并独立校验
python3 - <<'PY'
import json
from pathlib import Path
report = json.loads(Path("examples/ai-capex-transmission/research/work/report.json").read_text(encoding="utf-8"))
Path("/tmp/ai-capex-transmission.json").write_text(json.dumps(report["transmission"], ensure_ascii=False), encoding="utf-8")
PY
python3 scripts/transmission.py /tmp/ai-capex-transmission.json

# 契约、渲染与一页纸
python3 scripts/analysis_contract.py check \
  --plan examples/ai-capex-transmission/research/work/plan.json \
  --report examples/ai-capex-transmission/research/work/report.json \
  --claims examples/ai-capex-transmission/research/work/claims.json \
  --sources examples/ai-capex-transmission/research/work/sources.json

python3 scripts/memo_pack.py examples/ai-capex-transmission/research/work/report.json \
  --claims examples/ai-capex-transmission/research/work/claims.json \
  --sources examples/ai-capex-transmission/research/work/sources.json
```

## 边界

- 总量资本开支不是设备商需求的完整代理：云厂商还采购自研芯片、网络设备、内存与电力设施，AMAT 只覆盖部分设备环节。
- 财年不对齐（10 月 vs 12 月/6 月），同比不是严格同期。
- 没有订单、分部收入与中国区敞口数据，瓶颈只是可检验假设。
- 不构成对 AMAT 或云厂商的投资结论。
