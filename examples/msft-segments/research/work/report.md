# 微软 FY2025：利润增量主要来自生产力分部，不是云

微软 FY2025 三大分部哪一块贡献了主要营业利润增长？

研究截点 2026\-11\-14T00:00:00Z · asset · 分部利润归因

## 执行摘要

结论：FY2025 营业利润同比 \+19,095 百万美元：生产力 10,112、智能云 6,776、个人计算 2,207；利润增量第一是生产力分部。

最反直觉：云的收入增量更大（18,801 vs 13,990），但利润增量更低；收入增速不能直接当利润贡献。

接下来验证：看生产力分部的利润率能否维持；若云利润率随 AI 投入下降，利润贡献会更集中在生产力。

## 判断

按官方分部表，FY2025 营业利润同比增加 19,095 百万美元，其中生产力与业务流程 10,112、智能云 6,776、个人计算 2,207。增量最大的是生产力分部；云的收入增量更大（18,801 对 13,990），但利润增量更低，收入增速不能直接当成利润贡献。 [C8] [C10] [C12] [I\-JUDGE]

## 利润增量第一是生产力分部

生产力分部营业利润增加 10,112，高于智能云的 6,776。 [C8] [C2] [C10] [C4]

为什么重要：把「云增长」直接等同于「利润增长」会高估云对合并利润的贡献。

## 云的收入增量更大，利润增量更小

智能云收入增量 18,801，高于生产力分部的 13,990；利润增量却只有 6,776。 [C9] [C3] [C10] [C4]

为什么重要：收入增速与利润贡献是两件事，需要分别核对。

## 这意味着什么

### 利润引擎是生产力，不是云

生产力贡献 53% 的利润增量；把微软当纯云公司会误判利润来源。（FY2026） [I\-JUDGE] [C8] [C2] [C10] [C4]

### 云的收入与利润贡献不匹配

云收入增量 18,801、利润增量 6,776；AI 投入下云的利润率决定后续贡献。（FY2026） [C9] [C3] [C10] [C4]

### 分部结构决定估值叙事

生产力利润率更高、增速更稳；分部 mix 变化比总收入增速更能解释利润。（FY2026） [C2] [C4] [C8] [C10]

## 情景与触发条件

### 生产力继续领跑

生产力利润率维持，利润增量继续第一。

触发：生产力营业利润增速 &gt;15%；云利润率稳定

含义：利润引擎不变。

### 云利润追赶

云利润率提升，利润贡献超过生产力。

触发：云营业利润增速 &gt;20%；云利润率上升

含义：利润结构向云倾斜。

### 云利润率下滑

AI 投入压低云利润率，总收入增长但利润放缓。

触发：云利润率下降；总营业利润增速 &lt;10%

含义：收入增长不等于利润增长。

## 分析判断

FY2025 合并营业利润增量主要来自生产力与业务流程分部，云分部贡献次之。 [I\-JUDGE]

传导关系：分部收入 → 分部利润率 → 营业利润 → 合并营业利润

### 分部营业利润与增量

| 分部 | 收入增量（百万美元） | 利润增量（百万美元） |
| --- | --- | --- |
| PBP | 13990 | 10112 |
| IC | 18801 | 6776 |
| MPC | 3811 | 2207 |

[C8] [C10] [C12]

### 微软分部营业利润（百万美元）

| 分部 | FY2024（百万美元） | FY2025（百万美元） |
| --- | --- | --- |
| 生产力 | 59661 | 69773 |
| 智能云 | 37813 | 44589 |
| 个人计算 | 11959 | 14166 |

[C2] [C4] [C6] [C8] [C10] [C12]

同一单位；由分部披露值绘制。

## 接下来观察什么

### 下一份年报的分部利润率

验证生产力分部利润率能否维持 [C8]

## 限制与边界

官方只给分部收入与营业利润，没有量价拆分；价增长按 0 处理。 [I\-SEG]

## 附录：分析底稿与可复算模型

方法：driver\_bridge；比较基准：FY2024 分部收入与营业利润 [C1] [C3]

### 候选解释

| 编号 | 解释 |
| --- | --- |
| H1 | 云分部贡献主要利润增量 |
| H2 | 生产力分部贡献主要利润增量 |



### 区分性检验 T1

### 不同解释的事前预测

| 解释 | 预期观察 |
| --- | --- |
| H1 | 云分部增量最大 |
| H2 | 生产力分部增量最大 |



观察结果：生产力分部增量 10,112 大于云 6,776，支持 H2、削弱 H1。 [C8] [C10] [C12] [C2] [C4] [C6]

支持：H2；削弱：H1

下一观察：下一份年报的分部利润率；时间/触发：2027\-07\-30；支持条件：生产力分部利润率维持或提升；削弱条件：云分部利润率显著抬升并反超

### 微软 FY2025 分部驱动模型

模型：driver\_build；币种：USD；金额与股数共同缩放：million；期间：FY2024 基期至 FY2025（FY 结束于 6 月）；范围：三大分部合并口径

### 分部驱动

| 分部 | 基期收入 | 量增长 | 价增长 | 基期利润率 | 情景利润率 |
| --- | --- | --- | --- | --- | --- |
| PBP | 106820 | 0\.13096798352368477 | 0 | 0\.558519003931848 | 0\.5775432497309826 |
| IC | 87464 | 0\.21495701088447827 | 0 | 0\.43232644287935607 | 0\.4196019385498518 |
| MPC | 50838 | 0\.07496360989810769 | 0 | 0\.2352374208269405 | 0\.2592179179856905 |

[C1] [C2] [C7] [C8] [I\-SEG] [C3] [C4] [C9] [C10] [C5] [C6] [C11] [C12]

### 观察值与假设

| 变量 | 数值 | 单位 | 性质 | 假设理由 |
| --- | --- | --- | --- | --- |
| margin\_delta | 0 | ratio | assumption | 官方无分部量价拆分，统一利润率冲击设为0仅作敏感性参照 |

[I\-SEG]

### 固定模型重算结果

| 输出 | 结果 | 单位 |
| --- | --- | --- |
| base\_profit | 109433\.0 | currency |
| base\_revenue | 245122\.0 | currency |
| incremental\_margin | 0\.5216928036719313 | ratio |
| interaction\_effect | 0\.0 | currency |
| price\_effect | 0\.0 | currency |
| profit | 128528\.00000000003 | currency |
| profit\_change | 19095\.00000000003 | currency |
| revenue | 281724\.0 | currency |
| revenue\_change | 36602\.0 | currency |
| revenue\_growth | 0\.14932156232406713 | ratio |
| segment\_count | 3 | count |
| volume\_effect | 36602\.000000000015 | currency |

[O\-SEG]

### 单参数敏感性（其余输入固定）

| 变量 | 改为 | 单位 | 输出 | 结果 | 结果单位 |
| --- | --- | --- | --- | --- | --- |
| margin\_delta | \-0\.01 | ratio | base\_profit | 109433\.0 | currency |
| margin\_delta | \-0\.01 | ratio | base\_revenue | 245122\.0 | currency |
| margin\_delta | \-0\.01 | ratio | incremental\_margin | 0\.44472323916725887 | ratio |
| margin\_delta | \-0\.01 | ratio | interaction\_effect | 0\.0 | currency |
| margin\_delta | \-0\.01 | ratio | price\_effect | 0\.0 | currency |
| margin\_delta | \-0\.01 | ratio | profit | 125710\.76000000001 | currency |
| margin\_delta | \-0\.01 | ratio | profit\_change | 16277\.76000000001 | currency |
| margin\_delta | \-0\.01 | ratio | revenue | 281724\.0 | currency |
| margin\_delta | \-0\.01 | ratio | revenue\_change | 36602\.0 | currency |
| margin\_delta | \-0\.01 | ratio | revenue\_growth | 0\.14932156232406713 | ratio |
| margin\_delta | \-0\.01 | ratio | segment\_count | 3 | count |
| margin\_delta | \-0\.01 | ratio | volume\_effect | 36602\.000000000015 | currency |
| margin\_delta | 0\.01 | ratio | base\_profit | 109433\.0 | currency |
| margin\_delta | 0\.01 | ratio | base\_revenue | 245122\.0 | currency |
| margin\_delta | 0\.01 | ratio | incremental\_margin | 0\.5986623681766029 | ratio |
| margin\_delta | 0\.01 | ratio | interaction\_effect | 0\.0 | currency |
| margin\_delta | 0\.01 | ratio | price\_effect | 0\.0 | currency |
| margin\_delta | 0\.01 | ratio | profit | 131345\.24000000002 | currency |
| margin\_delta | 0\.01 | ratio | profit\_change | 21912\.24000000002 | currency |
| margin\_delta | 0\.01 | ratio | revenue | 281724\.0 | currency |
| margin\_delta | 0\.01 | ratio | revenue\_change | 36602\.0 | currency |
| margin\_delta | 0\.01 | ratio | revenue\_growth | 0\.14932156232406713 | ratio |
| margin\_delta | 0\.01 | ratio | segment\_count | 3 | count |
| margin\_delta | 0\.01 | ratio | volume\_effect | 36602\.000000000015 | currency |

[O\-SEG]

固定模型的数值已重算；来源含义、假设合理性与因果解释仍需研究审查。敏感性结果不是统计置信区间。

## 来源与结论审计

### 数值事实

### 结构化数值与口径

| 主张 | 实体 | 指标 | 数值 | 单位 | 期间 | 口径 | 范围 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C1 | MSFT | revenue | 106820 | USD million | fy；2023\-07\-01 → 2024\-06\-30；segment:PBP；gaap | gaap | segment:PBP |
| C2 | MSFT | operating\_income | 59661 | USD million | fy；2023\-07\-01 → 2024\-06\-30；segment:PBP；gaap | gaap | segment:PBP |
| C3 | MSFT | revenue | 87464 | USD million | fy；2023\-07\-01 → 2024\-06\-30；segment:IC；gaap | gaap | segment:IC |
| C4 | MSFT | operating\_income | 37813 | USD million | fy；2023\-07\-01 → 2024\-06\-30；segment:IC；gaap | gaap | segment:IC |
| C5 | MSFT | revenue | 50838 | USD million | fy；2023\-07\-01 → 2024\-06\-30；segment:MPC；gaap | gaap | segment:MPC |
| C6 | MSFT | operating\_income | 11959 | USD million | fy；2023\-07\-01 → 2024\-06\-30；segment:MPC；gaap | gaap | segment:MPC |
| C7 | MSFT | revenue | 120810 | USD million | fy；2024\-07\-01 → 2025\-06\-30；segment:PBP；gaap | gaap | segment:PBP |
| C8 | MSFT | operating\_income | 69773 | USD million | fy；2024\-07\-01 → 2025\-06\-30；segment:PBP；gaap | gaap | segment:PBP |
| C9 | MSFT | revenue | 106265 | USD million | fy；2024\-07\-01 → 2025\-06\-30；segment:IC；gaap | gaap | segment:IC |
| C10 | MSFT | operating\_income | 44589 | USD million | fy；2024\-07\-01 → 2025\-06\-30；segment:IC；gaap | gaap | segment:IC |
| C11 | MSFT | revenue | 54649 | USD million | fy；2024\-07\-01 → 2025\-06\-30；segment:MPC；gaap | gaap | segment:MPC |
| C12 | MSFT | operating\_income | 14166 | USD million | fy；2024\-07\-01 → 2025\-06\-30；segment:MPC；gaap | gaap | segment:MPC |

[C1] [C2] [C3] [C4] [C5] [C6] [C7] [C8] [C9] [C10] [C11] [C12]

\[C1\] PBP FY2024 收入 106820 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C2\] PBP FY2024 营业利润 59661 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C3\] IC FY2024 收入 87464 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C4\] IC FY2024 营业利润 37813 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C5\] MPC FY2024 收入 50838 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C6\] MPC FY2024 营业利润 11959 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C7\] PBP FY2025 收入 120810 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C8\] PBP FY2025 营业利润 69773 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C9\] IC FY2025 收入 106265 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C10\] IC FY2025 营业利润 44589 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C11\] MPC FY2025 收入 54649 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[C12\] MPC FY2025 营业利润 14166 百万美元（fact；2026\-11\-14T00:00:00Z）

依据：；来源：S1

\[I\-SEG\] 官方只披露分部收入与营业利润，量价无法拆分，价增长按0处理（inference；2026\-11\-14T00:00:00Z）

依据：C7；来源：

\[O\-SEG\] 分部驱动模型在给定输入下的收入与利润合计（inference；2026\-11\-14T00:00:00Z）

依据：I\-SEG, C1, C2, C7, C8, C3, C4, C9, C10, C5, C6, C11, C12；来源：

\[I\-JUDGE\] FY2025 营业利润增量主要来自生产力与业务流程分部，而非云分部（inference；2026\-11\-14T00:00:00Z）

依据：C8, C10, C12, C2, C4, C6；来源：

S1 · Microsoft · T0 · published\_at：2025\-07\-30 · retrieved\_at：2026\-11\-06T14:23:37Z · quote：\(In millions\)	2025		2024<br>Productivity and Business Processes				<br>Revenue	<br>$<br>120,810 · locator：官方年报分部业绩表（examples/msft\-cashflow evidence index 7） · origin\_id：msft\-ar25\-segments · origin\_basis：Direct official publication · evidence\_kind：document · access\_status：ok · supports：\["fact"\] · selection：\{"priority": "decisive", "purpose": "分部利润归因", "reason": "分部收入与营业利润原始表", "relevance": "direct", "selected": true\}

[https://www\.microsoft\.com/investor/reports/ar25/index\.html](https://www.microsoft.com/investor/reports/ar25/index.html)

来源状态：\{"official": \{"status": "ok"\}\}
