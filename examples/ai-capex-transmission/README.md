# 行业传导示例：AI 资本开支传导到半导体设备了吗？

这是第一个基于真实官方数据的行业传导示例。问题：**云厂商资本开支的增长，是否同幅传导到设备商收入、毛利与现金？**

数据来自 SEC XBRL 的 10-K 年度事实，四家公司各一个来源：

- 超大规模厂商资本开支：Microsoft（FY2025-06）、Alphabet（FY2025-12）、Amazon（FY2025-12）；
- 半导体设备商：Applied Materials（FY2025-10）。

| 节点 | FY2024 | FY2025 | 同比 |
| --- | --- | --- | --- |
| 三家云厂商资本开支合计 | 180,011 | 287,817 | **+59.9%** |
| AMAT 收入 | 27,176 | 28,368 | **+4.4%** |
| AMAT 毛利 | 12,897 | 13,808 | +7.1% |
| AMAT 经营现金流 | 8,677 | 7,958 | **−8.3%** |

（单位：百万美元）

**结论：总量层面的传导没有闭合。** 资本开支增长约 60%，设备商收入只增长约 4.4%，增速差约 55 个百分点；毛利率改善但经营现金流下降。传导瓶颈被定位在「设备交付与验收」与「客户结构」：资本开支没有消失，但收入确认滞后，且先进制程/存储敞口决定谁能接到订单。

## 传导链

```
CAPEX（三家云厂商资本开支）
  → DELIVERY（设备交付与验收，瓶颈：1–4 个季度）
  → REVENUE（AMAT 收入，+4.4%）
  → MARGIN（毛利率 48.7%）
  → CASH（经营现金流 −8.3%）
```

- 节点与边都带 `claim_ids`：数字来自四家公司的 XBRL 事实，机制（采购→交付→验收→收入）是明确标注的 inference。
- 瓶颈节点 `DELIVERY` 的判据是「资本开支增速远高于设备商收入增速」，并写进报告与一页纸。
- 报告会给出每个节点到瓶颈的距离、路径与「未到达瓶颈」的警告。

## 这个示例演示什么

- **传导不是自动的**：相邻两个节点的增速差 55 个百分点，直接否证「capex 是设备商收入的同步代理」。
- **开头 30 秒**：执行摘要三句话给结论、反直觉与下一步；两张图分别展示「capex 增速 vs 设备商收入/现金流」的背离，以及「毛利率上升、经营现金流率下降」的分化。
- **节点证据**：每个数字都能回到具体公司的 10-K 年度事实，而不是行业报告里的二手汇总。
- **瓶颈定位**：把「不传导」写成可检验的瓶颈假设（交付/结构），而不是一句「时滞」。
- **财年错位的诚实处理**：AMAT 财年 10 月结束，云厂商 12 月/6 月结束；同比比较存在期间错位，已写进限制。

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
