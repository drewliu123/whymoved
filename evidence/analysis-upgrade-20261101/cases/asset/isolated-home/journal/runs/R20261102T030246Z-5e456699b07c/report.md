# 虚构验收示范（非市场研究） · asset

收入发生了什么变化？

研究截点 2026\-10\-31T12:00:00Z · asset · 财报观察

## 判断

本期收入增加。 [C1]

重要限制：只有单期数据 [C1]

## 收入增加

披露收入为 12。 [C1]

为什么重要：更新收入判断。

相较基线：上一截点未披露

研究增量（new\_fact）：补充本期披露值

## 分析判断

本期收入增加。 [C1]

传导关系：收入 → 利润率 → 营业利润 → 现金流

### 价格要求什么，研究判断有什么不同

隐含预期：虚构价格在给定模型下隐含增长率为0\.089332 [P1] [OM1] [AM1]

研究假设：研究使用10%的增长情景，不是已校准预测 [P1] [OM1] [AM1]

差异：比较研究情景和隐含要求，差异依赖折现与终值假设 [P1] [OM1] [AM1]

改变判断的条件：后续现金流和折现率变化时重算 [P1] [OM1] [AM1]

## 分析底稿与可复算模型

方法：reverse\_valuation；比较基准：已披露收入和利润基数 [C1]

### 候选解释

| 编号 | 解释 |
| --- | --- |
| H1 | 需求兑现进入利润 |
| H2 | 收入增长但成本吞噬增量 |



### 区分性检验 T1

### 不同解释的事前预测

| 解释 | 预期观察 |
| --- | --- |
| H1 | 同口径利润增长 |
| H2 | 同口径利润下降 |



观察结果：单项披露不足以区分两种解释 [C1]

支持：；削弱：

下一观察：下一期同口径交付与现金流；时间/触发：下次财报；支持条件：利润增长；削弱条件：利润下降

### 虚构数据固定模型验收

模型：reverse\_dcf；币种：USD；金额与股数共同缩放：million \(money and shares\)；期间：一年基期；DCF明确期5年；范围：虚构同一公司

### 观察值与假设

| 变量 | 数值 | 单位 | 性质 | 假设理由 |
| --- | --- | --- | --- | --- |
| free\_cash\_flow | 10 | currency | observed |  |
| discount\_rate | 0\.1 | ratio | assumption | 虚构情景参数，用于检验敏感性 |
| terminal\_growth | 0\.02 | ratio | assumption | 虚构情景参数，用于检验敏感性 |
| years | 5 | year | assumption | 虚构情景参数，用于检验敏感性 |
| net\_debt | 20 | currency | observed |  |
| shares | 10 | shares | observed |  |
| price | 15 | currency/share | observed |  |
| growth\_low | \-0\.5 | ratio | assumption | 虚构情景参数，用于检验敏感性 |
| growth\_high | 1\.0 | ratio | assumption | 虚构情景参数，用于检验敏感性 |

[C1] [AM1] [P1]

### 固定模型重算结果

| 输出 | 结果 | 单位 |
| --- | --- | --- |
| implied\_growth | 0\.08933182778127957 | ratio |
| target\_enterprise\_value | 170 | currency |
| solved\_enterprise\_value | 170\.00000000018048 | currency |
| residual | 1\.8047785488306545e\-10 | currency |

[OM1]

### 单参数敏感性（其余输入固定）

| 变量 | 改为 | 单位 | 输出 | 结果 | 结果单位 |
| --- | --- | --- | --- | --- | --- |
| discount\_rate | 0\.09 | ratio | implied\_growth | 0\.05617657158290967 | ratio |
| discount\_rate | 0\.09 | ratio | target\_enterprise\_value | 170 | currency |
| discount\_rate | 0\.09 | ratio | solved\_enterprise\_value | 169\.99999998754302 | currency |
| discount\_rate | 0\.09 | ratio | residual | \-1\.2456979447961203e\-08 | currency |
| discount\_rate | 0\.11 | ratio | implied\_growth | 0\.12015133342356421 | ratio |
| discount\_rate | 0\.11 | ratio | target\_enterprise\_value | 170 | currency |
| discount\_rate | 0\.11 | ratio | solved\_enterprise\_value | 170\.00000001650633 | currency |
| discount\_rate | 0\.11 | ratio | residual | 1\.6506334077348583e\-08 | currency |

[OM1]

固定模型的数值已重算；来源含义、假设合理性与因果解释仍需研究审查。敏感性结果不是统计置信区间。

### 披露值

| 项目 | 收入 |
| --- | --- |
| 本期 | 12 |

[C1]

披露口径

## 接下来观察什么

### 下一次披露

验证趋势是否持续 [C1]

## 本轮更新说明

判断变化：否；验收只修改下一观察，不虚构新发现

可比性：comparable；同一虚构输入与口径

## 来源与结论审计

\[C1\] Revenue increased to 12\.（fact；2026\-10\-31T12:00:00Z）

依据：；来源：S1

\[P1\] 虚构收盘价15美元，仅验收用（price；2026\-10\-31T12:00:00Z）

依据：；来源：SP

\[AM1\] 虚构情景假设，仅用于计算验收，不是市场事实（inference；2026\-10\-31T12:00:00Z）

依据：C1；来源：

\[OM1\] 固定模型在给定假设下的结果（inference；2026\-10\-31T12:00:00Z）

依据：C1, AM1, P1；来源：

S1 · Example Official · T0 · published\_at：2026\-10\-30T12:00:00Z · retrieved\_at：2026\-10\-31T12:00:00Z · quote：Revenue increased to 12\. · locator：paragraph 1 · origin\_id：O1 · origin\_basis：Direct official publication · evidence\_kind：document · access\_status：ok · supports：\["fact"\] · selection：\{"priority": "decisive", "purpose": "reported revenue", "reason": "direct evidence", "relevance": "direct", "selected": true\}

[https://example\.com/official](https://example.com/official)

SP · 虚构报价验收源 · T0 · published\_at：2026\-10\-30T12:00:00Z · retrieved\_at：2026\-10\-31T12:00:00Z · quote：Fictional close 15 USD/share · locator：paragraph 1 · origin\_id：fictional\-price · origin\_basis：Direct official publication · evidence\_kind：market\_quote · access\_status：ok · supports：\["price"\] · selection：\{"priority": "decisive", "purpose": "reported revenue", "reason": "direct evidence", "relevance": "direct", "selected": true\} · market\_quote：\{"direction": "close", "instrument": "FICTIONAL", "outcome": "common equity", "quote\_type": "close", "quoted\_at": "2026\-10\-31T12:00:00Z", "unit": "USD/share", "value": 15\}

[https://example\.com/fictional\-price](https://example.com/fictional-price)

来源状态：\{"official": \{"status": "ok"\}\}
