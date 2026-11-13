# 苹果 FY2024：经营利润增长，净利润被税项拉低

苹果 FY2024 经营利润增长，为什么净利润反而下降？

研究截点 2026\-11\-14T00:00:00Z · asset · 两年盈利质量与税项核对

## 判断

FY2024 营业利润 123,216 高于 FY2023 的 114,301，税前利润也从 113,736 升至 123,485；净利润却从 96,995 降到 93,736。差异来自所得税：从 16,741 跳升到 29,749，有效税率明显上升。经营层面没有恶化，现金流质量也稳健（经营现金流高于净利润、资本开支强度低、现金周期为负）；但税项的具体一次性来源需要读年报附注，本报告只核对到数字层面。 [C19] [C31] [C32] [C20] [I\-JUDGE]

重要限制：未取得折旧摊销，资本开支/折旧为 null；税项的具体一次性来源需读年报附注。 [C32]

重要限制：ROIC 按账面权益与有息负债计算，回购压低了权益、现金不含短期投资，数值偏高，不做跨公司比较。 [C28]

## 净利润下降来自税项，不是经营恶化

营业利润与税前利润都上升，只有所得税费用大幅增加，净利润才下降。 [C19] [C3] [C31] [C15] [C32] [C16]

为什么重要：把净利润下降直接当成经营变差，会错判这种一次性税项冲击。

相较基线：只看净利润的方向

研究增量（contradiction）：税前与税项拆开后方向相反

## 经营利润率仍在提升

毛利率与营业利润率均较上年上升，收入增长快于成本。 [C17] [C1] [C18] [C2]

为什么重要：经营层面的改善与税项冲击是两个独立事实，需要同时呈现。

相较基线：只看净利润

研究增量（new\_fact）：利润率与收入拆解

## 现金流质量稳健，资本开支强度低

经营现金流高于净利润，资本开支占收入比例很低，现金周期为负。 [C21] [C20] [C22] [C24] [C26]

为什么重要：税项冲击不改现金流结构；质量筛查未触发红旗。

相较基线：单看利润表

研究增量（connection）：现金流与营运资本结构

## 分析判断

净利润下降由税项造成，经营与现金流质量稳健；税项的一次性来源需读年报附注。 [I\-JUDGE]

传导关系：收入 → 营业利润 → 税前利润 → 所得税 → 净利润

模型不适用：本轮用确定性报表与税项拆解，不适用固定估值模型

### 两年利润与税项

| 指标 | FY2023（百万美元） | FY2024（百万美元） |
| --- | --- | --- |
| 营业利润 | 114301 | 123216 |
| 税前利润 | 113736 | 123485 |
| 所得税 | 16741 | 29749 |
| 净利润 | 96995 | 93736 |

[C19] [C32]

## 接下来观察什么

### 下一财年有效税率与所得税费用

验证税项跳升是否一次性 [C32]

## 附录：分析底稿与可复算模型

方法：comparative\_attribution；比较基准：FY2023 同口径 [C3] [C4]

### 候选解释

| 编号 | 解释 |
| --- | --- |
| H1 | 经营恶化导致净利润下降 |
| H2 | 税项跳升导致净利润下降，经营仍在改善 |



### 区分性检验 T1

### 不同解释的事前预测

| 解释 | 预期观察 |
| --- | --- |
| H1 | 营业利润下降 |
| H2 | 营业利润上升而所得税跳升 |



观察结果：营业利润与税前利润上升、所得税从 16,741 升至 29,749，支持 H2、削弱 H1。 [C19] [C3] [C31] [C32]

支持：H2；削弱：H1

下一观察：下一财年有效税率；时间/触发：2027\-10\-29；支持条件：有效税率回落且经营利润继续增长；削弱条件：经营利润转弱或税项继续抬升

固定模型的数值已重算；来源含义、假设合理性与因果解释仍需研究审查。敏感性结果不是统计置信区间。

## 盈利质量

### 关键指标

| 期间 | 毛利率 | 营业利润率 | 净利率 | 现金转化 | 应计比率 | 资本开支/收入 | 资本开支/折旧 | SBC/收入 | ROIC |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FY2023 | 0\.4413 | 0\.2982 | 0\.2531 | 1\.1397 | \-0\.0384 | 0\.0286 | — | 0\.0283 | 0\.71 |
| FY2024 | 0\.4621 | 0\.3151 | 0\.2397 | 1\.2616 | \-0\.0683 | 0\.0242 | — | 0\.0299 | 0\.7563 |

[C1] [C2] [C3] [C4] [C5] [C6] [C7] [C8] [C9] [C10] [C11] [C12] [C13] [C14] [C15] [C16] [C17] [C18] [C19] [C20] [C21] [C22] [C23] [C24] [C25] [C26] [C27] [C28] [C29] [C30] [C31] [C32]

### 环比变化

| 区间 | 收入增长 | 毛利率变化 | 营业利润率变化 | 增量利润率 | DSO变化 | DIO变化 | 股本变化 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FY2023 → FY2024 | 0\.0202 | 0\.0208 | 0\.0169 | 1\.1503 | 0\.0888 | 0\.1494 | — |

[C1] [C2] [C3] [C4] [C5] [C6] [C7] [C8] [C9] [C10] [C11] [C12] [C13] [C14] [C15] [C16] [C17] [C18] [C19] [C20] [C21] [C22] [C23] [C24] [C25] [C26] [C27] [C28] [C29] [C30] [C31] [C32]

未触发默认红旗阈值；这不等于没有风险。

指标由嵌入的报表输入确定性计算；输入口径与来源仍须核对，阈值可在quality\.thresholds覆盖。

## 来源与结论审计

### 数值事实

### 结构化数值与口径

| 主张 | 实体 | 指标 | 数值 | 单位 | 期间 | 口径 | 范围 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C1 | AAPL | revenue | 383285 | USD million | fy；2022\-09\-25 → 2023\-09\-30；consolidated；gaap | gaap | consolidated |
| C2 | AAPL | gross\_profit | 169148 | USD million | fy；2022\-09\-25 → 2023\-09\-30；consolidated；gaap | gaap | consolidated |
| C3 | AAPL | operating\_profit | 114301 | USD million | fy；2022\-09\-25 → 2023\-09\-30；consolidated；gaap | gaap | consolidated |
| C4 | AAPL | net\_income | 96995 | USD million | fy；2022\-09\-25 → 2023\-09\-30；consolidated；gaap | gaap | consolidated |
| C5 | AAPL | cfo | 110543 | USD million | fy；2022\-09\-25 → 2023\-09\-30；consolidated；gaap | gaap | consolidated |
| C6 | AAPL | capex | 10959 | USD million | fy；2022\-09\-25 → 2023\-09\-30；consolidated；gaap | gaap | consolidated |
| C7 | AAPL | share\_based\_comp | 10833 | USD million | fy；2022\-09\-25 → 2023\-09\-30；consolidated；gaap | gaap | consolidated |
| C8 | AAPL | receivables | 29508 | USD million | fy；2022\-09\-25 → 2023\-09\-30；consolidated；gaap | gaap | consolidated |
| C9 | AAPL | inventory | 6331 | USD million | fy；2022\-09\-25 → 2023\-09\-30；consolidated；gaap | gaap | consolidated |
| C10 | AAPL | payables | 62611 | USD million | fy；2022\-09\-25 → 2023\-09\-30；consolidated；gaap | gaap | consolidated |
| C11 | AAPL | total\_assets | 352583 | USD million | fy；2022\-09\-25 → 2023\-09\-30；consolidated；gaap | gaap | consolidated |
| C12 | AAPL | equity | 62146 | USD million | fy；2022\-09\-25 → 2023\-09\-30；consolidated；gaap | gaap | consolidated |
| C13 | AAPL | debt | 105103 | USD million | fy；2022\-09\-25 → 2023\-09\-30；consolidated；gaap | gaap | consolidated |
| C14 | AAPL | cash | 29965 | USD million | fy；2022\-09\-25 → 2023\-09\-30；consolidated；gaap | gaap | consolidated |
| C15 | AAPL | pretax\_income | 113736 | USD million | fy；2022\-09\-25 → 2023\-09\-30；consolidated；gaap | gaap | consolidated |
| C16 | AAPL | income\_tax | 16741 | USD million | fy；2022\-09\-25 → 2023\-09\-30；consolidated；gaap | gaap | consolidated |
| C17 | AAPL | revenue | 391035 | USD million | fy；2023\-10\-01 → 2024\-09\-28；consolidated；gaap | gaap | consolidated |
| C18 | AAPL | gross\_profit | 180683 | USD million | fy；2023\-10\-01 → 2024\-09\-28；consolidated；gaap | gaap | consolidated |
| C19 | AAPL | operating\_profit | 123216 | USD million | fy；2023\-10\-01 → 2024\-09\-28；consolidated；gaap | gaap | consolidated |
| C20 | AAPL | net\_income | 93736 | USD million | fy；2023\-10\-01 → 2024\-09\-28；consolidated；gaap | gaap | consolidated |
| C21 | AAPL | cfo | 118254 | USD million | fy；2023\-10\-01 → 2024\-09\-28；consolidated；gaap | gaap | consolidated |
| C22 | AAPL | capex | 9447 | USD million | fy；2023\-10\-01 → 2024\-09\-28；consolidated；gaap | gaap | consolidated |
| C23 | AAPL | share\_based\_comp | 11688 | USD million | fy；2023\-10\-01 → 2024\-09\-28；consolidated；gaap | gaap | consolidated |
| C24 | AAPL | receivables | 33410 | USD million | fy；2023\-10\-01 → 2024\-09\-28；consolidated；gaap | gaap | consolidated |
| C25 | AAPL | inventory | 7286 | USD million | fy；2023\-10\-01 → 2024\-09\-28；consolidated；gaap | gaap | consolidated |
| C26 | AAPL | payables | 68960 | USD million | fy；2023\-10\-01 → 2024\-09\-28；consolidated；gaap | gaap | consolidated |
| C27 | AAPL | total\_assets | 364980 | USD million | fy；2023\-10\-01 → 2024\-09\-28；consolidated；gaap | gaap | consolidated |
| C28 | AAPL | equity | 56950 | USD million | fy；2023\-10\-01 → 2024\-09\-28；consolidated；gaap | gaap | consolidated |
| C29 | AAPL | debt | 96662 | USD million | fy；2023\-10\-01 → 2024\-09\-28；consolidated；gaap | gaap | consolidated |
| C30 | AAPL | cash | 29943 | USD million | fy；2023\-10\-01 → 2024\-09\-28；consolidated；gaap | gaap | consolidated |
| C31 | AAPL | pretax\_income | 123485 | USD million | fy；2023\-10\-01 → 2024\-09\-28；consolidated；gaap | gaap | consolidated |
| C32 | AAPL | income\_tax | 29749 | USD million | fy；2023\-10\-01 → 2024\-09\-28；consolidated；gaap | gaap | consolidated |

[C1] [C2] [C3] [C4] [C5] [C6] [C7] [C8] [C9] [C10] [C11] [C12] [C13] [C14] [C15] [C16] [C17] [C18] [C19] [C20] [C21] [C22] [C23] [C24] [C25] [C26] [C27] [C28] [C29] [C30] [C31] [C32]

\[C1\] AAPL FY2023 revenue 383285 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C2\] AAPL FY2023 gross\_profit 169148 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C3\] AAPL FY2023 operating\_profit 114301 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C4\] AAPL FY2023 net\_income 96995 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C5\] AAPL FY2023 cfo 110543 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C6\] AAPL FY2023 capex 10959 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C7\] AAPL FY2023 share\_based\_comp 10833 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C8\] AAPL FY2023 receivables 29508 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C9\] AAPL FY2023 inventory 6331 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C10\] AAPL FY2023 payables 62611 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C11\] AAPL FY2023 total\_assets 352583 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C12\] AAPL FY2023 equity 62146 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C13\] AAPL FY2023 debt 105103 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C14\] AAPL FY2023 cash 29965 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C15\] AAPL FY2023 pretax\_income 113736 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C16\] AAPL FY2023 income\_tax 16741 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C17\] AAPL FY2024 revenue 391035 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C18\] AAPL FY2024 gross\_profit 180683 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C19\] AAPL FY2024 operating\_profit 123216 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C20\] AAPL FY2024 net\_income 93736 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C21\] AAPL FY2024 cfo 118254 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C22\] AAPL FY2024 capex 9447 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C23\] AAPL FY2024 share\_based\_comp 11688 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C24\] AAPL FY2024 receivables 33410 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C25\] AAPL FY2024 inventory 7286 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C26\] AAPL FY2024 payables 68960 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C27\] AAPL FY2024 total\_assets 364980 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C28\] AAPL FY2024 equity 56950 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C29\] AAPL FY2024 debt 96662 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C30\] AAPL FY2024 cash 29943 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C31\] AAPL FY2024 pretax\_income 123485 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C32\] AAPL FY2024 income\_tax 29749 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[I\-JUDGE\] FY2024 经营利润与税前利润上升，净利润下降由所得税费用跳升造成；现金流质量稳健（inference；2026\-11\-14T00:00:00Z）

依据：C19, C31, C32, C20, C21, C24；来源：

S1 · U\.S\. SEC · T0 · published\_at：2024\-11\-01 · retrieved\_at：2026\-11\-14T00:00:00Z · quote：us\-gaap company facts, 10\-K USD: RevenueFromContractWithCustomerExcludingAssessedTax 383,285 / 391,035; NetIncomeLoss 96,995 / 93,736 · locator：data\.sec\.gov companyfacts CIK0000320193（Apple），取 FY2023–FY2024 10\-K 年度值 · origin\_id：sec\-aapl\-companyfacts · origin\_basis：Direct official publication · evidence\_kind：document · access\_status：ok · supports：\["fact"\] · selection：\{"priority": "decisive", "purpose": "两年盈利质量与税项核对", "reason": "官方 XBRL 年度事实，可逐项复核", "relevance": "direct", "selected": true\}

[https://data\.sec\.gov/api/xbrl/companyfacts/CIK0000320193\.json](https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json)

来源状态：\{"sec": \{"status": "ok"\}\}
