# 微软 FY2026：FCF 连续第二年下降，capex 强度 34\.9%

微软FY2025营收增长，为什么按CFO减现金资本开支定义的自由现金流反而下降？

研究截点 2026\-11\-06T14:23:37\.833839Z · asset · 解释FY24至FY25经营现金流与现金资本开支变化

## 执行摘要

结论：FY2026 收入 331,839（\+17\.8%）、CFO 182,935（\+34\.4%），但 capex 115,948（\+79\.6%），FCF 66,987，连续第二年下降、两年累计 −9\.6%。

最反直觉：FCF 下降全部来自资本开支：capex/收入从 18\.1% 升到 34\.9%，而经营现金流是净利润的 1\.37 倍，经营没有恶化。

接下来验证：看 FY2027 capex 增速能否降到收入增速以下、capex/收入能否回到 30% 以下；否则 FCF 仍会下降。

## 判断

FY2026 收入增长 17\.8%、经营现金流增长 34\.4%，但资本开支增长 79\.6% 到 115,948 百万美元；自由现金流 66,987，连续第二年下降、两年累计 −9\.6%。capex/收入从 18\.1% 升到 34\.9%，是 FCF 压力的全部来源；经营现金流仍是净利润的 1\.37 倍。结论：问题在投资强度，不在经营现金流；FY2027 看 capex 是否见顶。 [C11] [C12] [C13] [C14] [C15]

## 预测与失效条件

共识/基准预期：趋势外推：capex/收入维持 35% 以上

本报告预测：FY2027 的 capex/收入低于 33%

期限：FY2027 10\-K（2027\-07）

比较基准：FY2026 的 34\.9%

失效条件：capex/收入高于或等于 36%

## FCF 连续第二年下降，两年累计 −9\.6%

FCF 74\.071（FY2024）→71\.611（FY2025）→66\.987（FY2026）十亿美元；FY2026 −6\.5%。 [C1] [C5] [C6] [C9] [C13] [C14] [C11]

为什么重要：不是单年波动，而是连续两年下降；投资强度没有见顶。

## FCF 压力全部来自 capex

capex 44\.477（FY2024）→115\.948（FY2026），2\.61 倍；capex/收入 18\.1%→34\.9%；CFO 同期 \+54\.3%。 [C5] [C6] [C1] [C13] [C14] [C11]

为什么重要：经营现金流在增长，FCF 下降由投资强度解释；把它当经营恶化会误判。

## 经营现金流仍强：CFO 是净利润 1\.37 倍

FY2026 CFO 182\.935、净利润 133\.749 十亿美元；CFO/净利润 1\.37，利润有现金支撑。 [C12] [C13]

为什么重要：投资的钱来自经营现金流，不是举债或透支；这是主动扩张而非被动失血。

## capex 是扩张，不是维护不足

FY2026 capex 115\.948 vs 折旧 34\.300 十亿美元，capex/折旧 3\.38 倍。 [C14] [C15]

为什么重要：投入远超维护需求，指向产能/AI 基础设施扩张；若收入兑现，这是护城河。

## 这意味着什么

### FCF 压力是投资强度，不是经营恶化

CFO 增长 34\.4%，FCF 下降来自 capex \+79\.6%；看 FCF 必须同时看 capex/收入。（FY2027） [C13] [C14] [C11]

### capex/收入是关键跟踪指标

34\.9% 是历史高位；回到 30% 以下，FCF 才会修复。（FY2027） [C11] [C14]

### 经营现金流支撑扩张

CFO 是净利润 1\.37 倍，投资来自经营现金；不是靠举债维持 capex。（FY2027） [C12] [C13]

## 情景与触发条件

### capex 见顶

FY2027 capex 增速降到收入增速以下，FCF 修复。

触发：capex 增速 &lt; 收入增速；capex/收入 &lt;30%；FCF &gt;66,987

含义：FCF 压力缓解。

### 投资强度维持

capex/收入维持 30% 以上，FCF 继续下降。

触发：capex/收入 &gt;30%；FCF &lt;66,987；CFO 增速 &lt;20%

含义：FCF 压力延续。

### 收入加速

收入增速超过 capex 增速，capex 强度被动下降。

触发：收入增速 &gt;20%；capex 增速 &lt;15%；FCF 企稳

含义：扩张被收入消化。

## 分析判断

FY2025营收增长，并没有带来同方向的CFO减现金capex自由现金流：经营现金流增加17\.614十亿美元，但现金资本开支增加20\.074十亿美元，净抵消后FCF减少2\.460十亿美元。下降来自资本现金需求增量更大，CFO总额本身并未下降。 [C6] [C7] [C8]

传导关系：收入 → 经营活动现金流CFO → 现金PPE资本开支 → CFO减现金capex自由现金流

模型不适用：本题重算财报CFO减现金PPE支出；固定free\_cash\_flow是NOPAT\+折旧\-capex\-营运资本变化的FCFF，不能混作本口径。独立Python算术见arithmetic\.py及arithmetic\-output\.json；formula记录只作结构校验，不称模型算术验证。

## FY2024 CFO\-capex

计算式：118548\-44477 [C6]

### A1 输入

| 名称 | 数值 | 单位 |
| --- | --- | --- |
| CFO24 | 118548 | 百万美元 |
| capex24 | 44477 | 百万美元 |

[C2] [C3]

结果：74071 百万美元

## FY2025 CFO\-capex

计算式：136162\-64551 [C6]

### A2 输入

| 名称 | 数值 | 单位 |
| --- | --- | --- |
| CFO25 | 136162 | 百万美元 |
| capex25 | 64551 | 百万美元 |

[C2] [C3]

结果：71611 百万美元

## 收入同比百分比

计算式：\(281724/245122\-1\)\*100 [C6]

### A3 输入

| 名称 | 数值 | 单位 |
| --- | --- | --- |
| revenue24 | 245122 | 百万美元 |
| revenue25 | 281724 | 百万美元 |

[C1] [C1]

结果：14\.932156232406712 percent

## FCF同比百分比

计算式：\(\(136162\-64551\)/\(118548\-44477\)\-1\)\*100 [C6]

### A4 输入

| 名称 | 数值 | 单位 |
| --- | --- | --- |
| CFO24 | 118548 | 百万美元 |
| capex24 | 44477 | 百万美元 |
| CFO25 | 136162 | 百万美元 |
| capex25 | 64551 | 百万美元 |

[C2] [C3] [C2] [C3]

结果：\-3\.3211378272198333 percent

## CFO增量

计算式：136162\-118548 [C7]

### A5 输入

| 名称 | 数值 | 单位 |
| --- | --- | --- |
| CFO24 | 118548 | 百万美元 |
| CFO25 | 136162 | 百万美元 |

[C2] [C2]

结果：17614 百万美元

## 现金capex增量

计算式：64551\-44477 [C7]

### A6 输入

| 名称 | 数值 | 单位 |
| --- | --- | --- |
| capex24 | 44477 | 百万美元 |
| capex25 | 64551 | 百万美元 |

[C3] [C3]

结果：20074 百万美元

## FCF变化桥

计算式：\(136162\-118548\)\-\(64551\-44477\) [C7]

### A7 输入

| 名称 | 数值 | 单位 |
| --- | --- | --- |
| CFO24 | 118548 | 百万美元 |
| capex24 | 44477 | 百万美元 |
| CFO25 | 136162 | 百万美元 |
| capex25 | 64551 | 百万美元 |

[C2] [C3] [C2] [C3]

结果：\-2460 百万美元

## 投资净流出变化（流出正值）

计算式：72599\-96970 [C8]

### A8 输入

| 名称 | 数值 | 单位 |
| --- | --- | --- |
| CFI24\_outflow | 96970 | 百万美元 |
| CFI25\_outflow | 72599 | 百万美元 |

[C4] [C4]

结果：\-24371 百万美元

## 收购及无形等流出变化（流出正值）

计算式：5978\-69132 [C8]

### A9 输入

| 名称 | 数值 | 单位 |
| --- | --- | --- |
| acquisition24 | 69132 | 百万美元 |
| acquisition25 | 5978 | 百万美元 |

[C5] [C5]

结果：\-63154 百万美元

## 其余投资项目净流出变化残差

计算式：\(72599\-96970\)\-\(64551\-44477\)\-\(5978\-69132\) [C8]

### A10 输入

| 名称 | 数值 | 单位 |
| --- | --- | --- |
| CFI24 | 96970 | 百万美元 |
| CFI25 | 72599 | 百万美元 |
| capex24 | 44477 | 百万美元 |
| capex25 | 64551 | 百万美元 |
| acquisition24 | 69132 | 百万美元 |
| acquisition25 | 5978 | 百万美元 |

[C4] [C4] [C3] [C3] [C5] [C5]

结果：18709 百万美元

### 同口径年度比较（金额：十亿美元）

| 指标 | FY2024（十亿美元） | FY2025（十亿美元） | FY2026（十亿美元） |
| --- | --- | --- | --- |
| 收入 | 245\.122 | 281\.724 | 331\.839 |
| 经营现金流 | 118\.548 | 136\.162 | 182\.935 |
| 现金资本开支 | 44\.477 | 64\.551 | 115\.948 |
| 自由现金流 | 74\.071 | 71\.611 | 66\.987 |
| capex/收入 | 18\.1 | 22\.9 | 34\.9 |

[C1] [C5] [C6] [C9] [C11] [C12] [C13] [C14]

截至 6 月 30 日完整财年，微软合并口径；FCF=CFO−现金资本开支；由披露值计算并四舍五入。

### 经营现金流、资本开支与自由现金流（十亿美元）

| 财年 | 经营现金流（十亿美元） | 现金资本开支（十亿美元） | 自由现金流（十亿美元） |
| --- | --- | --- | --- |
| FY2024 | 118\.548 | 44\.477 | 74\.071 |
| FY2025 | 136\.162 | 64\.551 | 71\.611 |
| FY2026 | 182\.935 | 115\.948 | 66\.987 |

[C5] [C6] [C13] [C14] [C1] [C11]

同一单位；FCF=CFO−现金资本开支。

## 其他解释

### CFO总额下滑的解释不符合同口径数字

CFO同比上升，故H2无法解释此次FCF减少。这只核对总额，不能据此判定应收、税款等所有经营现金转换都健康。 [C2] [C7] [C9]

## 接下来观察什么

### 后续更新：取下一完整财年数据，按相同口径复查

继续研究时，取后续完整财年的同口径CFO、现金资本开支及现金转换率，重算变化桥并核查解释是否延续；本例仅解释FY2024至FY2025，不代表最新经营结论。 [C9]

## 限制与边界

FY2026 数据来自 SEC XBRL；现金资本开支不含非现金取得资产，与公司口径可能不同。 [C14]

## 附录：相对原文与旧判断的增量

FCF 连续第二年下降，两年累计 −9\.6%；基线：FY2025 FCF 小幅下降；增加的判断：FY2026 再降，累计 −9\.6% [C1] [C5] [C6] [C9] [C13] [C14] [C11]

FCF 压力全部来自 capex；基线：只看 FCF 下降；增加的判断：capex 强度翻倍 [C5] [C6] [C1] [C13] [C14] [C11]

经营现金流仍强：CFO 是净利润 1\.37 倍；基线：只看 FCF 为负增长；增加的判断：CFO/净利润 1\.37 [C12] [C13]

capex 是扩张，不是维护不足；基线：capex 只是成本；增加的判断：capex/折旧 3\.38x [C14] [C15]

## 附录：分析底稿与可复算模型

方法：comparative\_attribution；比较基准：FY2024与FY2025截至6月30日完整财年、微软合并口径；金额百万美元，流出在分析中取正值。 [C1] [C2] [C3] [C4] [C5]

### 候选解释

| 编号 | 解释 |
| --- | --- |
| H1 | 现金capex增量超过CFO增量，导致CFO\-capex下降。 |
| H2 | CFO总额下滑是FCF下降主因。 |



### 区分性检验 T1

### 不同解释的事前预测

| 解释 | 预期观察 |
| --- | --- |
| H1 | CFO上升但现金capex增加更多，deltaCFO减deltaCapex为负。 |
| H2 | CFO同比减少，下降的CFO是FCF收缩的主要贡献。 |



观察结果：CFO上升17614而capex上升20074百万美元，支持H1并削弱H2；不代表所有现金转换环节健康。 [C2] [C3] [C7]

支持：H1；削弱：H2

下一观察：用户发起后续更新时，取下一完整财年的同口径CFO、cash capex、CFO/收入与FCF/收入及组成。；时间/触发：继续更新并取得相应完整财年数据时；本轮未执行后续财年核验；支持条件：现金capex增量继续大于CFO增量时，支持该期资本现金需求抵消解释。；削弱条件：CFO下降并成为FCF下降主要贡献时，削弱将H1外推至该期。

固定模型的数值已重算；来源含义、假设合理性与因果解释仍需研究审查。敏感性结果不是统计置信区间。

## 来源与结论审计

\[C1\] 微软合并收入FY2024为245122、FY2025为281724百万美元，均截至6月30日完整财年。（fact；2026\-11\-06T14:23:37\.833839Z）

依据：；来源：S1

\[C2\] Net cash from operations FY2024为118548、FY2025为136162百万美元。（fact；2026\-11\-06T14:23:37\.833839Z）

依据：；来源：S2

\[C3\] Additions to property and equipment报表现金流FY2024为\(44477\)、FY2025为\(64551\)百万美元；本题cash capex取流出正值44477、64551。（fact；2026\-11\-06T14:23:37\.833839Z）

依据：；来源：S3, S4

\[C4\] Net cash used in investing FY2024为\(96970\)、FY2025为\(72599\)百万美元。（fact；2026\-11\-06T14:23:37\.833839Z）

依据：；来源：S4

\[C5\] Acquisition of companies, net of cash acquired and divestitures, and purchases of intangible and other assets现金流FY2024为\(69132\)、FY2025为\(5978\)百万美元。（fact；2026\-11\-06T14:23:37\.833839Z）

依据：；来源：S4

\[C6\] 按CFO减cash capex定义，FCF由74071降至71611百万美元，减少2460百万美元，降幅3\.32113782721983%；同期收入增长14\.93215623240672%。（inference；2026\-11\-06T14:23:37\.833839Z）

依据：C1, C2, C3；来源：

\[C7\] CFO增加17614百万美元，现金capex增加20074百万美元，后者超过前者2460百万美元；FCF变化=17614\-20074=\-2460百万美元。支持H1，削弱CFO总额下降的H2。（inference；2026\-11\-06T14:23:37\.833839Z）

依据：C2, C3, C6；来源：

\[C8\] 投资净流出减少24371百万美元不等于现金capex下降：收购及无形等支出流出减少63154百万美元，而现金PPE支出反而增加20074百万美元；其余投资项目的合计变化亦影响净额。（inference；2026\-11\-06T14:23:37\.833839Z）

依据：C3, C4, C5；来源：

\[C9\] CFO没有下降不能证明所有经营现金转换健康；若用户继续更新，应取得后续完整财年的同口径CFO、cash capex、CFO/收入与\(CFO\-capex\)/收入并检查组成。本例仅解释FY2024至FY2025，不代表最新经营结论。（inference；2026\-11\-06T14:23:37\.833839Z）

依据：C1, C2, C3, C7；来源：

\[C10\] 这里的FCF是财报CFO减现金PPE支出的透明算术口径，不等于项目固定模型的FCFF，不用于DCF；全公司现金PPE支出不能全部归为AI专属投入，这些数字也不能推出AI ROI。（inference；2026\-11\-06T14:23:37\.833839Z）

依据：C2, C3；来源：

\[C11\] MSFT FY2026 revenue 331839 百万美元（fact；2026\-11\-06T14:23:37\.833839Z）

依据：；来源：S5

\[C12\] MSFT FY2026 net\_income 133749 百万美元（fact；2026\-11\-06T14:23:37\.833839Z）

依据：；来源：S5

\[C13\] MSFT FY2026 cfo 182935 百万美元（fact；2026\-11\-06T14:23:37\.833839Z）

依据：；来源：S5

\[C14\] MSFT FY2026 cash capex 115948 百万美元（fact；2026\-11\-06T14:23:37\.833839Z）

依据：；来源：S5

\[C15\] MSFT FY2026 depreciation 34300 百万美元（fact；2026\-11\-06T14:23:37\.833839Z）

依据：；来源：S5

S1 · Microsoft · T0 · published\_at：unknown · retrieved\_at：2026\-11\-06T14:14:24\.369Z · quote：INCOME STATEMENTS<br>\(In millions, except per share amounts\)<br>Year Ended June 30,	2025		2024		2023<br>Revenue:					<br>Product	<br>$<br>63,946		<br>$<br>64,773		<br>$<br>64,699<br>Service and other	217,778		180,349		147,216<br>Total revenue	281,724		245,122		211,915 · locator：官方年报DOM文本 lines 1133\-1145; table 15 \(official\-tables\.json index\) · origin\_id：microsoft\-fy2025\-annual\-report · origin\_basis：同一Microsoft FY2025官方年报，片段共享一个原始出处，不计独立来源。 · evidence\_kind：document · access\_status：ok · supports：\["fact"\] · selection：\{"priority": "decisive", "purpose": "FY24/FY25收入", "reason": "直接提供同一财年、单位与合并范围的原始行及表头。", "relevance": "direct", "selected": true\}

[https://www\.microsoft\.com/investor/reports/ar25/index\.html](https://www.microsoft.com/investor/reports/ar25/index.html)

S2 · Microsoft · T0 · published\_at：unknown · retrieved\_at：2026\-11\-06T14:14:24\.369Z · quote：CASH FLOWS STATEMENTS<br>\(In millions\)<br>Year Ended June 30,	2025		2024		2023<br>Operations					<br>Net income	<br>$<br>101,832		<br>$<br>88,136		<br>$<br>72,361<br>Adjustments to reconcile net income to net cash from operations:					<br>Depreciation, amortization, and other	34,153		22,287		13,861<br>Stock\-based compensation expense	11,974		10,734		9,611<br>Net recognized losses on investments and derivatives	609		305		196<br>Deferred income taxes	\(7,056\)		\(4,738\)		\(6,059\)<br>Changes in operating assets and liabilities:					<br>Accounts receivable	\(10,581\)		\(7,191\)		\(4,087\)<br>Inventories	309		1,284		1,242<br>Other current assets	\(3,044\)		\(1,648\)		\(1,991\)<br>Other long\-term assets	\(2,950\)		\(6,817\)		\(2,833\)<br>Accounts payable	569		3,545		\(2,721\)<br>Unearned revenue	5,438		5,348		5,535<br>Income taxes	\(38\)		1,687		\(358\)<br>Other current liabilities	5,922		4,867		2,272<br>Other long\-term liabilities	\(975\)		749		553<br>Net cash from operations	136,162		118,548		87,582 · locator：官方年报DOM文本 lines 1273\-1299; table 18 \(official\-tables\.json index\) · origin\_id：microsoft\-fy2025\-annual\-report · origin\_basis：同一Microsoft FY2025官方年报，片段共享一个原始出处，不计独立来源。 · evidence\_kind：document · access\_status：ok · supports：\["fact"\] · selection：\{"priority": "decisive", "purpose": "FY24/FY25经营现金流", "reason": "直接提供同一财年、单位与合并范围的原始行及表头。", "relevance": "direct", "selected": true\}

[https://www\.microsoft\.com/investor/reports/ar25/index\.html](https://www.microsoft.com/investor/reports/ar25/index.html)

S3 · Microsoft · T0 · published\_at：unknown · retrieved\_at：2026\-11\-06T14:14:24\.369Z · quote：CASH FLOWS STATEMENTS<br>\(In millions\)<br>Year Ended June 30,	2025		2024		2023 · locator：官方年报DOM文本 lines 1273\-1275; table 18 \(official\-tables\.json index\) · origin\_id：microsoft\-fy2025\-annual\-report · origin\_basis：同一Microsoft FY2025官方年报，片段共享一个原始出处，不计独立来源。 · evidence\_kind：document · access\_status：ok · supports：\["fact"\] · selection：\{"priority": "decisive", "purpose": "现金流表头与期间", "reason": "直接提供同一财年、单位与合并范围的原始行及表头。", "relevance": "direct", "selected": true\}

[https://www\.microsoft\.com/investor/reports/ar25/index\.html](https://www.microsoft.com/investor/reports/ar25/index.html)

S4 · Microsoft · T0 · published\_at：unknown · retrieved\_at：2026\-11\-06T14:14:24\.369Z · quote：CASH FLOWS STATEMENTS<br>\(In millions\)<br>Year Ended June 30,	2025		2024		2023<br>Investing					<br>Additions to property and equipment	\(64,551\)		\(44,477\)		\(28,107\)<br>Acquisition of companies, net of cash acquired and divestitures, and purchases of intangible and other assets	\(5,978\)		\(69,132\)		\(1,670\)<br>Purchases of investments	\(29,775\)		\(17,732\)		\(37,651\)<br>Maturities of investments	16,079		24,775		33,510<br>Sales of investments	9,309		10,894		14,354<br>Other, net	2,317		\(1,298\)		\(3,116\)<br>Net cash used in investing	\(72,599\)		\(96,970\)		\(22,680\) · locator：官方年报DOM文本 lines 1309\-1316; table 18 \(official\-tables\.json index\) · origin\_id：microsoft\-fy2025\-annual\-report · origin\_basis：同一Microsoft FY2025官方年报，片段共享一个原始出处，不计独立来源。 · evidence\_kind：document · access\_status：ok · supports：\["fact"\] · selection：\{"priority": "decisive", "purpose": "现金PPE支出、收购及无形等支出与投资净流出", "reason": "直接提供同一财年、单位与合并范围的原始行及表头。", "relevance": "direct", "selected": true\}

[https://www\.microsoft\.com/investor/reports/ar25/index\.html](https://www.microsoft.com/investor/reports/ar25/index.html)

S5 · U\.S\. SEC · T0 · published\_at：unknown · retrieved\_at：2026\-11\-05T00:00:00Z · quote：10\-K company facts: Revenues 331,839; NetIncomeLoss 133,749; NetCashProvidedByUsedInOperatingActivities 182,935; PaymentsToAcquirePropertyPlantAndEquipment 115,948; Depreciation 34,300 \(FY2026\) · locator：data\.sec\.gov companyfacts CIK0000789019（Microsoft），FY2026 10\-K 年度值 · origin\_id：sec\-msft\-fy26 · origin\_basis：Direct official publication · evidence\_kind：document · access\_status：ok · supports：\["fact"\] · selection：\{"priority": "decisive", "purpose": "FY2026 现金流与资本开支", "reason": "官方 XBRL 年度事实", "relevance": "direct", "selected": true\}

[https://data\.sec\.gov/api/xbrl/companyfacts/CIK0000789019\.json](https://data.sec.gov/api/xbrl/companyfacts/CIK0000789019.json)

来源状态：\{"community": \{"reason": "本题为财报现金流算术归因，社区材料不增加同口径检验信息。", "status": "not\_run"\}, "official": \{"reason": "Lead通过ego\-browser读取官方年报；本轮已读取保存全文、表格与真实下载元数据。", "status": "ok"\}\}
