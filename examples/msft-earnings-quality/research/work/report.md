# 微软 FY2025：利润增长有现金支撑，但资本开支强度在上升

微软 FY2025 的利润增长有现金支撑吗？

研究截点 2026\-11\-14T00:00:00Z · asset · 盈利质量筛查

## 判断

FY2025 经营现金流 136,162 百万美元，是净利润 101,832 的 1\.34 倍，利润有现金支撑；资本开支 64,551 是折旧摊销 34,153 的 1\.89 倍，说明投入偏扩张而不是维护不足。两期利润率基本稳定，增量利润率约 52%，红旗筛查未发现异常。需要盯的是资本开支强度（占收入 22\.9%）能否转化为后续收入。 [C13] [C12] [C14] [C15] [I\-JUDGE]

## 利润有现金支撑

经营现金流 136,162 高于净利润 101,832，现金转化 1\.34 倍。 [C13] [C12]

为什么重要：若 CFO 低于净利润，利润增长可能依赖应计；这里方向相反。

相较基线：只看利润表的判断

研究增量（new\_fact）：引入现金流量表的交叉核对

## 资本开支高于折旧，投入偏扩张

资本开支 64,551 是折旧摊销 34,153 的 1\.89 倍。 [C14] [C15]

为什么重要：低于折旧才是维护不足；高于折旧通常意味着扩张，但也要看回报。

相较基线：未区分维护性与扩张性投入

研究增量（new\_fact）：资本开支与折旧的比值

## 增量利润率约 52%

营业利润增加 19,095，收入增加 36,602，增量利润率约 52%。 [C11] [C3] [C9] [C1]

为什么重要：新增收入仍在创造利润，而不是被成本吃掉。

相较基线：只看收入增速

研究增量（connection）：收入增量与利润增量的比值

## 分析判断

FY2025 利润增长有现金支撑，投入偏扩张；资本开支强度是后续要跟踪的变量。 [I\-JUDGE]

传导关系：收入 → 营业利润 → 净利润 → 经营现金流 → 资本开支

模型不适用：本轮用确定性报表筛查，不适用固定估值模型

### 现金与投入

| 指标 | FY2024（百万美元） | FY2025（百万美元） |
| --- | --- | --- |
| 经营现金流 | 118548 | 136162 |
| 净利润 | 88136 | 101832 |
| 资本开支 | 44477 | 64551 |
| 折旧摊销 | 22287 | 34153 |

[C13] [C12]

## 接下来观察什么

### 下一期资本开支与收入增速

验证扩张投入是否转化为收入 [C14]

## 限制与边界

未取得应收、存货与总资产，应计比率与周转天数为 null。 [C13]

## 附录：分析底稿与可复算模型

方法：comparative\_attribution；比较基准：FY2024 同口径报表 [C5] [C4]

### 候选解释

| 编号 | 解释 |
| --- | --- |
| H1 | 利润增长有现金支撑，投入偏扩张 |
| H2 | 利润增长主要来自会计口径 |



### 区分性检验 T1

### 不同解释的事前预测

| 解释 | 预期观察 |
| --- | --- |
| H1 | CFO/净利润 大于 1 且资本开支高于折旧 |
| H2 | CFO/净利润 小于 1 或资本开支低于折旧 |



观察结果：CFO 1\.34 倍净利润、资本开支 1\.89 倍折旧，支持 H1、削弱 H2。 [C13] [C12] [C14] [C15]

支持：H1；削弱：H2

下一观察：下一期资本开支与收入增速；时间/触发：2027\-07\-30；支持条件：资本开支继续高于折旧且收入增长；削弱条件：资本开支高企但收入停滞

固定模型的数值已重算；来源含义、假设合理性与因果解释仍需研究审查。敏感性结果不是统计置信区间。

## 盈利质量

### 关键指标

| 期间 | 毛利率 | 营业利润率 | 净利率 | 现金转化 | 应计比率 | 资本开支/收入 | 资本开支/折旧 | SBC/收入 | ROIC |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FY2024 | 0\.6976 | 0\.4464 | 0\.3596 | 1\.3451 | — | 0\.1814 | 1\.9956 | 0\.0438 | — |
| FY2025 | 0\.6882 | 0\.4562 | 0\.3615 | 1\.3371 | — | 0\.2291 | 1\.8901 | 0\.0425 | — |

[C1] [C2] [C3] [C4] [C5] [C6] [C7] [C8] [C9] [C10] [C11] [C12] [C13] [C14] [C15] [C16]

### 环比变化

| 区间 | 收入增长 | 毛利率变化 | 营业利润率变化 | 增量利润率 | DSO变化 | DIO变化 | 股本变化 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FY2024 → FY2025 | 0\.1493 | \-0\.0094 | 0\.0098 | 0\.5217 | — | — | — |

[C1] [C2] [C3] [C4] [C5] [C6] [C7] [C8] [C9] [C10] [C11] [C12] [C13] [C14] [C15] [C16]

未触发默认红旗阈值；这不等于没有风险。

指标由嵌入的报表输入确定性计算；输入口径与来源仍须核对，阈值可在quality\.thresholds覆盖。

## 来源与结论审计

### 数值事实

### 结构化数值与口径

| 主张 | 实体 | 指标 | 数值 | 单位 | 期间 | 口径 | 范围 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C1 | MSFT | revenue | 245122 | USD million | fy；2023\-07\-01 → 2024\-06\-30；consolidated；gaap | gaap | consolidated |
| C2 | MSFT | gross\_profit | 171008 | USD million | fy；2023\-07\-01 → 2024\-06\-30；consolidated；gaap | gaap | consolidated |
| C3 | MSFT | operating\_profit | 109433 | USD million | fy；2023\-07\-01 → 2024\-06\-30；consolidated；gaap | gaap | consolidated |
| C4 | MSFT | net\_income | 88136 | USD million | fy；2023\-07\-01 → 2024\-06\-30；consolidated；gaap | gaap | consolidated |
| C5 | MSFT | cfo | 118548 | USD million | fy；2023\-07\-01 → 2024\-06\-30；consolidated；gaap | gaap | consolidated |
| C6 | MSFT | capex | 44477 | USD million | fy；2023\-07\-01 → 2024\-06\-30；consolidated；gaap | gaap | consolidated |
| C7 | MSFT | depreciation\_amortization | 22287 | USD million | fy；2023\-07\-01 → 2024\-06\-30；consolidated；gaap | gaap | consolidated |
| C8 | MSFT | share\_based\_comp | 10734 | USD million | fy；2023\-07\-01 → 2024\-06\-30；consolidated；gaap | gaap | consolidated |
| C9 | MSFT | revenue | 281724 | USD million | fy；2024\-07\-01 → 2025\-06\-30；consolidated；gaap | gaap | consolidated |
| C10 | MSFT | gross\_profit | 193893 | USD million | fy；2024\-07\-01 → 2025\-06\-30；consolidated；gaap | gaap | consolidated |
| C11 | MSFT | operating\_profit | 128528 | USD million | fy；2024\-07\-01 → 2025\-06\-30；consolidated；gaap | gaap | consolidated |
| C12 | MSFT | net\_income | 101832 | USD million | fy；2024\-07\-01 → 2025\-06\-30；consolidated；gaap | gaap | consolidated |
| C13 | MSFT | cfo | 136162 | USD million | fy；2024\-07\-01 → 2025\-06\-30；consolidated；gaap | gaap | consolidated |
| C14 | MSFT | capex | 64551 | USD million | fy；2024\-07\-01 → 2025\-06\-30；consolidated；gaap | gaap | consolidated |
| C15 | MSFT | depreciation\_amortization | 34153 | USD million | fy；2024\-07\-01 → 2025\-06\-30；consolidated；gaap | gaap | consolidated |
| C16 | MSFT | share\_based\_comp | 11974 | USD million | fy；2024\-07\-01 → 2025\-06\-30；consolidated；gaap | gaap | consolidated |

[C1] [C2] [C3] [C4] [C5] [C6] [C7] [C8] [C9] [C10] [C11] [C12] [C13] [C14] [C15] [C16]

\[C1\] MSFT FY2024 revenue 245122 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C2\] MSFT FY2024 gross\_profit 171008 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C3\] MSFT FY2024 operating\_profit 109433 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C4\] MSFT FY2024 net\_income 88136 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C5\] MSFT FY2024 cfo 118548 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C6\] MSFT FY2024 capex 44477 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C7\] MSFT FY2024 depreciation\_amortization 22287 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C8\] MSFT FY2024 share\_based\_comp 10734 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C9\] MSFT FY2025 revenue 281724 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C10\] MSFT FY2025 gross\_profit 193893 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C11\] MSFT FY2025 operating\_profit 128528 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C12\] MSFT FY2025 net\_income 101832 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C13\] MSFT FY2025 cfo 136162 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C14\] MSFT FY2025 capex 64551 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C15\] MSFT FY2025 depreciation\_amortization 34153 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C16\] MSFT FY2025 share\_based\_comp 11974 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[I\-JUDGE\] FY2025 利润增长有现金支撑，同时资本开支强度显著上升（inference；2026\-11\-14T00:00:00Z）

依据：C13, C12, C14, C15；来源：

S1 · Microsoft · T0 · published\_at：2025\-07\-30 · retrieved\_at：2026\-11\-06T14:23:37Z · quote：INCOME STATEMENTS \.\.\. 2025 2024 Revenue $ 281,724 $ 245,122 \.\.\. Net income $ 101,832 $ 88,136 · locator：官方年报损益表与现金流量表（examples/msft\-cashflow evidence index 6/18） · origin\_id：msft\-ar25\-primary · origin\_basis：Direct official publication · evidence\_kind：document · access\_status：ok · supports：\["fact"\] · selection：\{"priority": "decisive", "purpose": "盈利质量筛查", "reason": "官方报表原始数字", "relevance": "direct", "selected": true\}

[https://www\.microsoft\.com/investor/reports/ar25/index\.html](https://www.microsoft.com/investor/reports/ar25/index.html)

来源状态：\{"official": \{"status": "ok"\}\}
