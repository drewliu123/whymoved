# AI 资本开支两年：同行释放存货，AMAT 在堆存货

这是基于真实官方数据的行业传导示例。问题：**云厂商资本开支的增长，是否同幅传导到设备商收入、毛利与现金？**

数据来自 SEC XBRL 的 10-K 年度事实，六家公司各一个来源：

- 超大规模厂商资本开支：Microsoft（FY2025-06）、Alphabet（FY2025-12）、Amazon（FY2025-12）；
- 半导体设备商：Applied Materials（FY2025-10）、Lam Research（FY2025-06）、KLA（FY2025-06）。

| 指标 | FY2023 | FY2024 | FY2025 | 两年变化 |
| --- | --- | --- | --- | --- |
| 三家云厂商资本开支合计 | — | 180,011 | 287,817 | +59.9%（同比） |
| AMAT 收入 | 26,517 | 27,176 | 28,368 | **+7.0%** |
| LRCX 收入 | 17,428 | 14,905 | 18,435 | **+5.8%** |
| KLAC 收入 | 10,496 | 9,812 | 12,156 | **+15.8%** |
| AMAT 经营现金流 | 8,700 | 8,677 | 7,958 | **−8.5%** |
| LRCX 经营现金流 | 5,178 | 4,652 | 6,173 | **+19.2%** |
| KLAC 经营现金流 | 3,669 | 3,309 | 4,082 | **+11.3%** |

（单位：百万美元）

**结论：单年看 AMAT 掉队，两年看不是。** FY2025 同行收入增约 24%、AMAT 只增 4.4%，但 LRCX、KLAC 是从 FY2024 下滑中反弹；FY2023→FY2025 AMAT 收入 +7.0%，与 LRCX +5.8% 相当，只有 KLAC +15.8% 更强。真正持续背离的是现金流：AMAT 两年 −8.5%，同行 +11%–19%。问题不是「AMAT 收入掉队」，而是「同样的收入体量，AMAT 的现金转化更弱」。

**现金弱在哪里？** 应收天数从 70.3 降到 66.7，现金周期从 168.7 改善到 165.4 天——收款端没有变差。真正的拖累是存货与合同负债：

| FY2024→FY2025（百万美元） | 变动 | 对现金的近似影响 |
| --- | --- | --- |
| 存货 | 5,421→5,915 | −494 |
| 合同负债 | 2,849→2,566 | −283 |
| 应付账款 | 1,570→1,978 | +408 |
| 应收账款 | 5,234→5,185 | +49 |
| 其他经营项目（轧差） | — | −399 |

存货增加与预收款减少合计拖走约 7.8 亿美元现金，应付账款拉长只是部分对冲。**现金弱不是收款问题，而是备货与订单（合同负债）问题。**

把同行拉进来，差异更清楚：

| 公司（FY2024→FY2025） | 存货天数 | 现金周期 | 存货变化 | 合同负债变化 |
| --- | --- | --- | --- | --- |
| AMAT | 138.6→**148.3** | 168.7→165.4（−3.3） | +494 | −283 |
| LRCX | 196.1→**166.3** | 229.3→200.2（−29.1） | +90 | +1,128 |
| KLAC | 282.0→**246.7** | 316.8→279.5（−37.3） | +177 | −69 |

同样的行业环境，LRCX、KLAC 在去库存、现金周期改善近 30–37 天；AMAT 反而在加库存，现金周期只改善 3.3 天。**AMAT 的存货方向与同行相反，这比「营运资本」四个字更能解释现金差距。**

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

- **一年 vs 两年**：FY2025 单年 AMAT +4.4% vs 同行 +24%，但两年 AMAT +7.0% 与 LRCX +5.8% 相当；单年同比会被低基数反弹误导。
- **真正掉队的是现金流**：两年经营现金流 AMAT −8.5%，LRCX +19.2%、KLAC +11.3%；收入没持续掉队，现金转化持续偏弱。
- **现金桥拆到科目**：应收改善、现金周期下降，拖累来自存货增加 4.94 亿与合同负债减少 2.83 亿，应付账款增加 4.08 亿只是部分对冲。
- **合同负债是订单的领先指标**：预收款继续下降会比收入更早暴露需求走弱，这是下一份财报最该看的科目。
- **开头 30 秒**：执行摘要三句话给结论、反直觉与下一步；两张图分别是三年收入指数（FY2023=100）与两年收入/现金流变化。
- **节点证据**：每个数字都能回到具体公司的 10-K 年度事实，而不是行业报告里的二手汇总。
- **结论修正**：从「AMAT 收入掉队」改为「AMAT 现金转化弱」；下一步拆营运资本、验收与产品结构。
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
