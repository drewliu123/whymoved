# 微软 FY2023–FY2025：增长质量总体稳定，应收周转值得跟踪

微软 FY2023–FY2025 的增长质量在恶化吗？

研究截点 2026\-11\-14T00:00:00Z · asset · 三年盈利质量与周转趋势

## 判断

三年看，经营现金流始终高于净利润、应计为负、现金周期为负，利润有现金支撑，增长质量没有恶化迹象；但应收周转天数从 FY2023 到 FY2025 上升，说明信用条件在放松，需要与新披露的应收增速对照。库存周转天数下降、应付天数上升，营运资本整体仍为负。 [C37] [C36] [C40] [C8] [I\-JUDGE]

## 经营现金流持续高于净利润

FY2023、FY2024、FY2025 三年 CFO 均高于净利润，现金转化稳定高于 1。 [C5] [C4] [C37] [C36]

为什么重要：若现金转化跌破 1 且应计转正，才是质量恶化的典型信号；这里相反。

相较基线：单年质量筛查

研究增量（new\_fact）：三年一致的现金支撑

## 现金周期为负且改善

应付天数高于应收与库存天数之和，营运资本继续为经营提供资金。 [C42] [C40] [C41] [C33]

为什么重要：负现金周期意味着增长不占用自有资金；这是质量稳定的结构原因。

相较基线：只看利润表

研究增量（connection）：营运资本结构对现金的贡献

## 资本回报率可算且处于较高水平

营业利润、税前利润与所得税、有息负债、现金与权益齐全，ROIC 按税后营业利润/投入资本可算；口径只含现金及等价物。 [C35] [C47] [C48] [C44] [C45] [C46]

为什么重要：质量筛查不只看百分比利润率，还要看投入资本回报；口径写清才不会高估。

相较基线：此前只有利润率与现金转化

研究增量（new\_fact）：补入债务、现金与税项后 ROIC 可算

## 应收周转天数上升是唯一压力点

应收从 FY2023 到 FY2025 增长快于收入，应收天数上升；库存天数下降部分抵消。 [C8] [C40] [C1] [C33]

为什么重要：应收快于收入若持续，可能是信用放宽或回款变慢，需要下一期核对。

相较基线：总体稳定的判断

研究增量（contradiction）：应收端出现反向信号

## 分析判断

增长质量总体稳定，现金周期为负；应收周转是唯一需要跟踪的压力点。 [I\-JUDGE]

传导关系：收入 → 利润 → 经营现金流 → 应收与应付 → 现金周期

模型不适用：本轮用确定性报表与周转计算，不适用固定估值模型

### 三年关键报表

| 指标 | FY2023（百万美元） | FY2024（百万美元） | FY2025（百万美元） |
| --- | --- | --- | --- |
| 收入 | 211915 | 245122 | 281724 |
| 经营现金流 | 87582 | 118548 | 136162 |
| 净利润 | 72361 | 88136 | 101832 |
| 应收 | 48688 | 56924 | 69905 |

[C33] [C37] [C36]

### 收入与经营现金流（百万美元）

| 财年 | 收入（百万美元） | 经营现金流（百万美元） |
| --- | --- | --- |
| FY2023 | 211915 | 87582 |
| FY2024 | 245122 | 118548 |
| FY2025 | 281724 | 136162 |

[C1] [C17] [C33] [C5] [C21] [C37]

## 接下来观察什么

### 下一期应收增速与收入增速

验证应收天数上升是否持续 [C40]

## 限制与边界

未取得折旧摊销，资本开支/折旧仍为 null；投入资本口径只含现金及等价物，不含短期投资；XBRL 事实可能被后续重述。 [C38]

## 附录：分析底稿与可复算模型

方法：comparative\_attribution；比较基准：FY2023 同口径 [C5] [C4]

### 候选解释

| 编号 | 解释 |
| --- | --- |
| H1 | 增长质量稳定，利润有现金支撑 |
| H2 | 增长质量恶化，靠应计与放宽信用 |



### 区分性检验 T1

### 不同解释的事前预测

| 解释 | 预期观察 |
| --- | --- |
| H1 | 现金转化高于 1、应计为负、现金周期为负 |
| H2 | 现金转化下降或应计转正、周转天数显著拉长 |



观察结果：现金转化高于 1、应计为负、现金周期为负，支持 H1；应收天数上升削弱「完全稳定」，列入观察。 [C37] [C36] [C40] [C8] [C42] [C41]

支持：H1；削弱：H2

下一观察：下一期应收增速与收入增速；时间/触发：2027\-07\-30；支持条件：应收增速回落到收入增速附近；削弱条件：应收增速继续显著高于收入

固定模型的数值已重算；来源含义、假设合理性与因果解释仍需研究审查。敏感性结果不是统计置信区间。

## 盈利质量

### 关键指标

| 期间 | 毛利率 | 营业利润率 | 净利率 | 现金转化 | 应计比率 | 资本开支/收入 | 资本开支/折旧 | SBC/收入 | ROIC |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FY2023 | 0\.6892 | 0\.4177 | 0\.3415 | 1\.2103 | \-0\.0369 | 0\.1326 | — | 0\.0454 | 0\.3279 |
| FY2024 | 0\.6976 | 0\.4464 | 0\.3596 | 1\.3451 | \-0\.0658 | 0\.1814 | — | 0\.0438 | 0\.3032 |
| FY2025 | 0\.6882 | 0\.4562 | 0\.3615 | 1\.3371 | \-0\.0607 | 0\.2291 | — | 0\.0425 | 0\.2971 |

[C1] [C2] [C3] [C4] [C5] [C6] [C7] [C8] [C9] [C10] [C11] [C12] [C13] [C14] [C15] [C16] [C17] [C18] [C19] [C20] [C21] [C22] [C23] [C24] [C25] [C26] [C27] [C28] [C29] [C30] [C31] [C32] [C33] [C34] [C35] [C36] [C37] [C38] [C39] [C40] [C41] [C42] [C43] [C44] [C45] [C46] [C47] [C48]

### 环比变化

| 区间 | 收入增长 | 毛利率变化 | 营业利润率变化 | 增量利润率 | DSO变化 | DIO变化 | 股本变化 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FY2023 → FY2024 | 0\.1567 | 0\.0084 | 0\.0287 | 0\.6297 | 0\.0135 | \-0\.5559 | — |
| FY2024 → FY2025 | 0\.1493 | \-0\.0094 | 0\.0098 | 0\.5217 | 0\.0656 | \-0\.3665 | — |

[C1] [C2] [C3] [C4] [C5] [C6] [C7] [C8] [C9] [C10] [C11] [C12] [C13] [C14] [C15] [C16] [C17] [C18] [C19] [C20] [C21] [C22] [C23] [C24] [C25] [C26] [C27] [C28] [C29] [C30] [C31] [C32] [C33] [C34] [C35] [C36] [C37] [C38] [C39] [C40] [C41] [C42] [C43] [C44] [C45] [C46] [C47] [C48]

未触发默认红旗阈值；这不等于没有风险。

指标由嵌入的报表输入确定性计算；输入口径与来源仍须核对，阈值可在quality\.thresholds覆盖。

## 来源与结论审计

### 数值事实

### 结构化数值与口径

| 主张 | 实体 | 指标 | 数值 | 单位 | 期间 | 口径 | 范围 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C1 | MSFT | revenue | 211915 | USD million | fy；2022\-07\-01 → 2023\-06\-30；consolidated；gaap | gaap | consolidated |
| C2 | MSFT | gross\_profit | 146052 | USD million | fy；2022\-07\-01 → 2023\-06\-30；consolidated；gaap | gaap | consolidated |
| C3 | MSFT | operating\_profit | 88523 | USD million | fy；2022\-07\-01 → 2023\-06\-30；consolidated；gaap | gaap | consolidated |
| C4 | MSFT | net\_income | 72361 | USD million | fy；2022\-07\-01 → 2023\-06\-30；consolidated；gaap | gaap | consolidated |
| C5 | MSFT | cfo | 87582 | USD million | fy；2022\-07\-01 → 2023\-06\-30；consolidated；gaap | gaap | consolidated |
| C6 | MSFT | capex | 28107 | USD million | fy；2022\-07\-01 → 2023\-06\-30；consolidated；gaap | gaap | consolidated |
| C7 | MSFT | share\_based\_comp | 9611 | USD million | fy；2022\-07\-01 → 2023\-06\-30；consolidated；gaap | gaap | consolidated |
| C8 | MSFT | receivables | 48688 | USD million | fy；2022\-07\-01 → 2023\-06\-30；consolidated；gaap | gaap | consolidated |
| C9 | MSFT | inventory | 2500 | USD million | fy；2022\-07\-01 → 2023\-06\-30；consolidated；gaap | gaap | consolidated |
| C10 | MSFT | payables | 18095 | USD million | fy；2022\-07\-01 → 2023\-06\-30；consolidated；gaap | gaap | consolidated |
| C11 | MSFT | total\_assets | 411976 | USD million | fy；2022\-07\-01 → 2023\-06\-30；consolidated；gaap | gaap | consolidated |
| C12 | MSFT | equity | 206223 | USD million | fy；2022\-07\-01 → 2023\-06\-30；consolidated；gaap | gaap | consolidated |
| C13 | MSFT | debt | 47237 | USD million | fy；2022\-07\-01 → 2023\-06\-30；consolidated；gaap | gaap | consolidated |
| C14 | MSFT | cash | 34704 | USD million | fy；2022\-07\-01 → 2023\-06\-30；consolidated；gaap | gaap | consolidated |
| C15 | MSFT | pretax\_income | 89311 | USD million | fy；2022\-07\-01 → 2023\-06\-30；consolidated；gaap | gaap | consolidated |
| C16 | MSFT | income\_tax | 16950 | USD million | fy；2022\-07\-01 → 2023\-06\-30；consolidated；gaap | gaap | consolidated |
| C17 | MSFT | revenue | 245122 | USD million | fy；2023\-07\-01 → 2024\-06\-30；consolidated；gaap | gaap | consolidated |
| C18 | MSFT | gross\_profit | 171008 | USD million | fy；2023\-07\-01 → 2024\-06\-30；consolidated；gaap | gaap | consolidated |
| C19 | MSFT | operating\_profit | 109433 | USD million | fy；2023\-07\-01 → 2024\-06\-30；consolidated；gaap | gaap | consolidated |
| C20 | MSFT | net\_income | 88136 | USD million | fy；2023\-07\-01 → 2024\-06\-30；consolidated；gaap | gaap | consolidated |
| C21 | MSFT | cfo | 118548 | USD million | fy；2023\-07\-01 → 2024\-06\-30；consolidated；gaap | gaap | consolidated |
| C22 | MSFT | capex | 44477 | USD million | fy；2023\-07\-01 → 2024\-06\-30；consolidated；gaap | gaap | consolidated |
| C23 | MSFT | share\_based\_comp | 10734 | USD million | fy；2023\-07\-01 → 2024\-06\-30；consolidated；gaap | gaap | consolidated |
| C24 | MSFT | receivables | 56924 | USD million | fy；2023\-07\-01 → 2024\-06\-30；consolidated；gaap | gaap | consolidated |
| C25 | MSFT | inventory | 1246 | USD million | fy；2023\-07\-01 → 2024\-06\-30；consolidated；gaap | gaap | consolidated |
| C26 | MSFT | payables | 21996 | USD million | fy；2023\-07\-01 → 2024\-06\-30；consolidated；gaap | gaap | consolidated |
| C27 | MSFT | total\_assets | 512163 | USD million | fy；2023\-07\-01 → 2024\-06\-30；consolidated；gaap | gaap | consolidated |
| C28 | MSFT | equity | 268477 | USD million | fy；2023\-07\-01 → 2024\-06\-30；consolidated；gaap | gaap | consolidated |
| C29 | MSFT | debt | 44937 | USD million | fy；2023\-07\-01 → 2024\-06\-30；consolidated；gaap | gaap | consolidated |
| C30 | MSFT | cash | 18315 | USD million | fy；2023\-07\-01 → 2024\-06\-30；consolidated；gaap | gaap | consolidated |
| C31 | MSFT | pretax\_income | 107787 | USD million | fy；2023\-07\-01 → 2024\-06\-30；consolidated；gaap | gaap | consolidated |
| C32 | MSFT | income\_tax | 19651 | USD million | fy；2023\-07\-01 → 2024\-06\-30；consolidated；gaap | gaap | consolidated |
| C33 | MSFT | revenue | 281724 | USD million | fy；2024\-07\-01 → 2025\-06\-30；consolidated；gaap | gaap | consolidated |
| C34 | MSFT | gross\_profit | 193893 | USD million | fy；2024\-07\-01 → 2025\-06\-30；consolidated；gaap | gaap | consolidated |
| C35 | MSFT | operating\_profit | 128528 | USD million | fy；2024\-07\-01 → 2025\-06\-30；consolidated；gaap | gaap | consolidated |
| C36 | MSFT | net\_income | 101832 | USD million | fy；2024\-07\-01 → 2025\-06\-30；consolidated；gaap | gaap | consolidated |
| C37 | MSFT | cfo | 136162 | USD million | fy；2024\-07\-01 → 2025\-06\-30；consolidated；gaap | gaap | consolidated |
| C38 | MSFT | capex | 64551 | USD million | fy；2024\-07\-01 → 2025\-06\-30；consolidated；gaap | gaap | consolidated |
| C39 | MSFT | share\_based\_comp | 11974 | USD million | fy；2024\-07\-01 → 2025\-06\-30；consolidated；gaap | gaap | consolidated |
| C40 | MSFT | receivables | 69905 | USD million | fy；2024\-07\-01 → 2025\-06\-30；consolidated；gaap | gaap | consolidated |
| C41 | MSFT | inventory | 938 | USD million | fy；2024\-07\-01 → 2025\-06\-30；consolidated；gaap | gaap | consolidated |
| C42 | MSFT | payables | 27724 | USD million | fy；2024\-07\-01 → 2025\-06\-30；consolidated；gaap | gaap | consolidated |
| C43 | MSFT | total\_assets | 619003 | USD million | fy；2024\-07\-01 → 2025\-06\-30；consolidated；gaap | gaap | consolidated |
| C44 | MSFT | equity | 343479 | USD million | fy；2024\-07\-01 → 2025\-06\-30；consolidated；gaap | gaap | consolidated |
| C45 | MSFT | debt | 43151 | USD million | fy；2024\-07\-01 → 2025\-06\-30；consolidated；gaap | gaap | consolidated |
| C46 | MSFT | cash | 30242 | USD million | fy；2024\-07\-01 → 2025\-06\-30；consolidated；gaap | gaap | consolidated |
| C47 | MSFT | pretax\_income | 123627 | USD million | fy；2024\-07\-01 → 2025\-06\-30；consolidated；gaap | gaap | consolidated |
| C48 | MSFT | income\_tax | 21795 | USD million | fy；2024\-07\-01 → 2025\-06\-30；consolidated；gaap | gaap | consolidated |

[C1] [C2] [C3] [C4] [C5] [C6] [C7] [C8] [C9] [C10] [C11] [C12] [C13] [C14] [C15] [C16] [C17] [C18] [C19] [C20] [C21] [C22] [C23] [C24] [C25] [C26] [C27] [C28] [C29] [C30] [C31] [C32] [C33] [C34] [C35] [C36] [C37] [C38] [C39] [C40] [C41] [C42] [C43] [C44] [C45] [C46] [C47] [C48]

\[C1\] MSFT FY2023 revenue 211915 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C2\] MSFT FY2023 gross\_profit 146052 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C3\] MSFT FY2023 operating\_profit 88523 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C4\] MSFT FY2023 net\_income 72361 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C5\] MSFT FY2023 cfo 87582 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C6\] MSFT FY2023 capex 28107 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C7\] MSFT FY2023 share\_based\_comp 9611 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C8\] MSFT FY2023 receivables 48688 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C9\] MSFT FY2023 inventory 2500 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C10\] MSFT FY2023 payables 18095 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C11\] MSFT FY2023 total\_assets 411976 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C12\] MSFT FY2023 equity 206223 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C13\] MSFT FY2023 debt 47237 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C14\] MSFT FY2023 cash 34704 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C15\] MSFT FY2023 pretax\_income 89311 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C16\] MSFT FY2023 income\_tax 16950 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C17\] MSFT FY2024 revenue 245122 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C18\] MSFT FY2024 gross\_profit 171008 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C19\] MSFT FY2024 operating\_profit 109433 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C20\] MSFT FY2024 net\_income 88136 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C21\] MSFT FY2024 cfo 118548 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C22\] MSFT FY2024 capex 44477 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C23\] MSFT FY2024 share\_based\_comp 10734 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C24\] MSFT FY2024 receivables 56924 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C25\] MSFT FY2024 inventory 1246 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C26\] MSFT FY2024 payables 21996 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C27\] MSFT FY2024 total\_assets 512163 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C28\] MSFT FY2024 equity 268477 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C29\] MSFT FY2024 debt 44937 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C30\] MSFT FY2024 cash 18315 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C31\] MSFT FY2024 pretax\_income 107787 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C32\] MSFT FY2024 income\_tax 19651 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C33\] MSFT FY2025 revenue 281724 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C34\] MSFT FY2025 gross\_profit 193893 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C35\] MSFT FY2025 operating\_profit 128528 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C36\] MSFT FY2025 net\_income 101832 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C37\] MSFT FY2025 cfo 136162 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C38\] MSFT FY2025 capex 64551 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C39\] MSFT FY2025 share\_based\_comp 11974 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C40\] MSFT FY2025 receivables 69905 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C41\] MSFT FY2025 inventory 938 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C42\] MSFT FY2025 payables 27724 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C43\] MSFT FY2025 total\_assets 619003 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C44\] MSFT FY2025 equity 343479 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C45\] MSFT FY2025 debt 43151 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C46\] MSFT FY2025 cash 30242 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C47\] MSFT FY2025 pretax\_income 123627 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C48\] MSFT FY2025 income\_tax 21795 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[I\-JUDGE\] FY2023–FY2025 增长质量总体稳定：现金转化高于 1、应计为负、现金周期为负；应收周转天数上升是唯一压力点（inference；2026\-11\-14T00:00:00Z）

依据：C37, C36, C40, C8, C33, C1；来源：

S1 · U\.S\. SEC · T0 · published\_at：2025\-07\-30 · retrieved\_at：2026\-11\-14T00:00:00Z · quote：us\-gaap company facts, 10\-K USD: RevenueFromContractWithCustomerExcludingAssessedTax 211,915 / 245,122 / 281,724 · locator：data\.sec\.gov companyfacts CIK0000789019（Microsoft），取 FY2023–FY2025 10\-K 年度值 · origin\_id：sec\-msft\-companyfacts · origin\_basis：Direct official publication · evidence\_kind：document · access\_status：ok · supports：\["fact"\] · selection：\{"priority": "decisive", "purpose": "三年趋势与质量筛查", "reason": "官方 XBRL 年度事实，可逐项复核", "relevance": "direct", "selected": true\}

[https://data\.sec\.gov/api/xbrl/companyfacts/CIK0000789019\.json](https://data.sec.gov/api/xbrl/companyfacts/CIK0000789019.json)

来源状态：\{"sec": \{"status": "ok"\}\}
