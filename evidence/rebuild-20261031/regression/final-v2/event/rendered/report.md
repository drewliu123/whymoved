# 【开发回归样本】12月Fed：加息有证据，70\.5%仍不是独立结论

Polymarket的2026年12月Fed决议合约正在定价什么，官方证据支持到哪一步？

研究截点 2026\-10\-31T17:21:33\.217142\+00:00 · event\_pricing · 事件定价：复用冻结证据的开发回归

证据模式：旧版 schema 1；本报告未按 schema 2 的来源与证据契约校验。

## 判断

市场把加25bp列为首要结果：Gamma参考70\.5%，维持27\.5%。官方证据支持把加息视为实质情景：9月全票加25bp，10月虽暂停但仍有加息异议，核心PCE仍有压力。独立初判曾暂偏维持；补齐9月资料后的最终观点改为维持与加25bp并列工作情景。没有校准模型，不能判断70\.5%是否错价，也不给独立点概率。下一项最明确观察是11月25日的核心PCE、实际消费及随后就业数据。 [C4] [C5] [C6] [C7] [C8] [C12] [C13] [C15]

重要限制：开发回归样本（dev sample，非 heldout）。仅将原冻结材料转换为 schema 2 报告；保留原 as\_of，无新增检索、事实、引语、计算或研究判断。claims 保留原 schema 1，本次结构校验及开发归档不等于 strict schema 2 claims 验证，也不提供严格历史可得性证明。 

重要限制：真实未来合约、完整规则、官方决议/PCE与盘口取得；独立概率、BLS基础数据与规则异常边界仍有缺口。 

重要限制：BLS就业与CPI即时页均403；未从搜索摘要补入未核实数字，因此缺直接劳动力与CPI基础数据。官方就业判断仅来自Fed声明。 

重要限制：reference class只定义“相似通胀/就业约束下的常规FOMC会议”，未建立逐次历史条件样本，也无校准反应函数；独立概率留null。定性初判不能转换为概率差或收益优势。 

重要限制：搜索插件在冻结初判前返回媒体与一家机构加息观点；未见盘口百分比，但不能称对所有外部观点完全盲法。9月决议在看价后才取得，最终观点存在锚定可能。 

重要限制：Gamma与CLOB异步且Gamma有缓存迹象；未抓No侧深度、成交历史、费用明细或CME对照，未做执行/滑点模拟。不把网站liquidity和累计volume当可成交深度。加25bp的Gamma lastTradePrice=0\.71而同Yes token的CLOB last\_trade\_price=0\.290，均无独立成交时戳；两字段不一致且均未用于方向/价格变动结论，未核实差异成因。 

重要限制：事件/子合约endDate相差5小时；fallback中next相对哪个时点、精确时区/截止秒、非常规变动取整的全部边界、oracle争议处理未由当前描述消除。未另抓规则指向的openmarket\.htm页面。 

重要限制：六个关键T0资料记录来自Fed、BEA、Polymarket，来源独立性有限；未扩搜社区，本轮无社区覆盖结论。 

重要限制：报告HTML与Markdown由同一report\.json生成，已作静态文本和引用检查；未在浏览器渲染、截图或验证移动设备。本轮已收到协调者转达的独立审查并定向修正，处置见independent\-review\.md；静态校验不代表完整独立QA，也不证明预测优势。 

## 当前判断：加息有证据，70\.5%尚无独立校准依据

看完市场后，以维持与加息25bp作为并列工作情景。官方材料足以解释为何市场偏向加息，但不足以检验70\.5%这个数值是否合理，因此不宣称存在定价优势。9月全票加25bp、10月暂停且仍有加息异议，说明“暂停后恢复收紧”是有根据的路径。 [C4] [C5] [C7] [C8] [C13]

为什么重要：区分可解释的政策情景与可交易的概率优势，避免把市场参考价当成独立研究结论。

相较基线：原 report\.json 的同名 finding 与原 claims\.json（C4, C5, C7, C8, C13）；开发样本复用。

研究增量（connection）：仅把原结论与其验证意义重新连接：区分可解释的政策情景与可交易的概率优势，避免把市场参考价当成独立研究结论。 本轮无新事实、计算或判断更新，非相对原研究的新发现。

## 市场参考、独立初判与市场后观点分别保留

市场参考：Gamma加25bp 70\.5%、维持27\.5%。独立初判：在读取任何Polymarket报价前，已在independent\-freeze\.json冻结“维持为暂定基准，加25bp为实质竞争情景”，未给数字概率。市场后观点：取得9月官方决议后，降低维持优先排序的把握，改为维持/加25bp并列工作情景；此修订受新增官方上下文支持，也可能受已见市场锚定影响，不能重新包装为独立预测。 [C7] [C8] [C12] [C13]

为什么重要：让读者看到初判和看价后判断的先后及锚定限制，不能把后见修订重写成独立预测。

相较基线：原 report\.json 的同名 finding 与原 claims\.json（C7, C8, C12, C13）；开发样本复用。

研究增量（connection）：仅把原结论与其验证意义重新连接：让读者看到初判和看价后判断的先后及锚定限制，不能把后见修订重写成独立预测。 本轮无新事实、计算或判断更新，非相对原研究的新发现。

## 通胀约束宽松，但需求并非处处加速

9月核心PCE环比0\.3%、同比3\.1%，8月核心环比也为0\.3%；10月Fed仍强调通胀高、经济强、就业稳定，暂不支持把降息作基准。另一方面，9月名义消费增0\.5%而实际消费不足0\.1%、实际可支配收入下降0\.3%。9月实际消费增速较8月放缓、实际DPI下降，但尚未确认持续或全面需求走弱；下一组数据需要区分价格推动和真实需求。 [C4] [C5] [C6] [C14]

为什么重要：把价格压力与实际需求分开，下一次数据才能区分继续收紧与等待的解释。

相较基线：原 report\.json 的同名 finding 与原 claims\.json（C4, C5, C6, C14）；开发样本复用。

研究增量（connection）：仅把原结论与其验证意义重新连接：把价格压力与实际需求分开，下一次数据才能区分继续收紧与等待的解释。 本轮无新事实、计算或判断更新，非相对原研究的新发现。

## 合约是一次会议的上限调整，异常条款会改变经济语义

按12月会议前后的目标区间上限变化结算，不能误读成今天到年底累计变动。正常25bp网格上的五档为降50\+、降25、不变、加25、加50\+，在这些条件下互斥并覆盖；非标准变化按规则例子向远离零的25bp档取整，未穷尽的非常规边界不可自行裁定。完整规则逐字保存于sources\.json/S1及原始响应。 [C2] [C16]

为什么重要：结算标签受合约比较基准与异常规则影响，宏观方向和合约结果必须分别复盘。

相较基线：原 report\.json 的同名 finding 与原 claims\.json（C2, C16）；开发样本复用。

研究增量（connection）：仅把原结论与其验证意义重新连接：结算标签受合约比较基准与异常规则影响，宏观方向和合约结果必须分别复盘。 本轮无新事实、计算或判断更新，非相对原研究的新发现。

## 参考价之和100\.75%，双边报价和深度必须一起看

五个Gamma Yes参考价相加100\.75%，五个最佳bid之和99\.50%、ask之和102\.00%。不把原值强行拼成精确概率分布，不从该偏差直接推导套利。加25bp和不变的spread都是0\.01美元/份，相当于1个百分点的支付价格；降25bp最佳bid只有20份，足见尾部参考价与可执行规模并非一回事。 [C9] [C10] [C11]

为什么重要：盘口时差、价差与可撤深度限制参考概率的执行意义。

相较基线：原 report\.json 的同名 finding 与原 claims\.json（C9, C10, C11）；开发样本复用。

研究增量（connection）：仅把原结论与其验证意义重新连接：盘口时差、价差与可撤深度限制参考概率的执行意义。 本轮无新事实、计算或判断更新，非相对原研究的新发现。

## 真实未来状态已核实，报价采用窗口而非伪同刻

事件和五个子合约均active=true、closed=false，子合约acceptingOrders=true。Gamma获取于17:17:21Z，但HTTP Date为17:14:28Z，子市场updatedAt为17:12:15Z至17:14:16Z；CLOB获取窗口17:17:41\.692–41\.992Z，订单簿内部时间为17:16:54\.639–17:17:40\.943Z。它们是同一研究窗口内的异步快照，不是原子同刻行情。另有加25bp的Gamma lastTradePrice=0\.71与CLOB last\_trade\_price=0\.290不一致；两端均无独立成交时戳，未用于结论或价格变动解释，原因未核实。 [C1] [C8] [C9] [C17]

为什么重要：区分事件仍可交易与异步报价窗口，避免把缓存和成交字段差异解释成同刻价格变化。

相较基线：原 report\.json 的同名 finding 与原 claims\.json（C1, C8, C9, C17）；开发样本复用。

研究增量（connection）：仅把原结论与其验证意义重新连接：区分事件仍可交易与异步报价窗口，避免把缓存和成交字段差异解释成同刻价格变化。 本轮无新事实、计算或判断更新，非相对原研究的新发现。

### 盘口快照：价格为美元/1美元支付份额，规模为份（Yes侧）

| 结果 | Gamma参考 | CLOB bid / ask | 最佳bid份数 / ask份数 | 书内UTC时间 |
| --- | --- | --- | --- | --- |
| 降50\+bp | 0\.40% | 0\.003 / 0\.005 | 358248\.31 / 15457\.88 | 17:17:39\.444 |
| 降25bp | 0\.65% | 0\.006 / 0\.007 | 20 / 8556\.97 | 17:17:39\.597 |
| 不变 | 27\.50% | 0\.27 / 0\.28 | 27435\.55 / 24428\.43 | 17:17:39\.936 |
| 加25bp | 70\.50% | 0\.7 / 0\.71 | 3010\.62 / 48170\.95 | 17:17:40\.943 |
| 加50\+bp | 1\.70% | 0\.016 / 0\.018 | 2159\.38 / 880\.64 | 17:16:54\.639 |

[C8] [C9] [C11]

 开发转换：引用经原 claims\.json 核对；仅提供原研究表格的结论级关联。

### 显示深度：bid向下/ask向上各0\.01美元内（含边界），金额未计费用

| 结果 | bid累计份 | ask累计份 | bid美元名义额 | ask美元名义额 |
| --- | --- | --- | --- | --- |
| 降50\+bp | 5802059\.00 | 32483\.70 | 9229\.55 | 183\.55 |
| 降25bp | 7334089\.07 | 19802\.10 | 18339\.65 | 206\.78 |
| 不变 | 374743\.19 | 356202\.54 | 97707\.58 | 103054\.45 |
| 加25bp | 199409\.31 | 425768\.66 | 137622\.53 | 306071\.73 |
| 加50\+bp | 357830\.64 | 11276\.40 | 3599\.22 | 269\.04 |

[C9] [C11]

计算见calculations\.json。远尾bid累计份大但美元金额很小；深度可撤单。未抓No侧订单簿。 开发转换：引用经原 claims\.json 核对；仅提供原研究表格的结论级关联。

### 契约与时间边界

| 项目 | 核实结果 |
| --- | --- |
| 真实对象 | event id 770450；五个market id 3215005–3215009 |
| 事件状态 | active=true；closed=false；五个子合约acceptingOrders=true |
| 事件endDate | 2026\-12\-10T04:59:00Z = 12月9日23:59 EST |
| 五个子合约endDate | 2026\-12\-09T23:59:00Z = 12月9日18:59 EST |
| 官方决策会议 | 2026\-12\-08–09；附经济预测；声明发布即可结算 |
| 比较基准 | 12月会议前的目标区间上限；当前上限4\.00%仅是今日背景 |
| 默认/延期 | 原文到“the next scheduled meeting”end date无声明则No change；next相对哪个时点、时区及截止秒均不明。2027\-01\-26–27仅为12月之后的日历会议，不能确定为默认截止 |
| 规则来源 | Gamma description全文；FOMC正式声明为首要结算来源；规则另指openmarket\.htm，未另抓其当前页面 |

[C1] [C2] [C3] [C4] [C16]

 开发转换：引用经原 claims\.json 核对；仅提供原研究表格的结论级关联。

### 原 claims 内联来源目录（未新增取证）

| 原来源ID | 发布方 | 层级 | 发布时间（原记录） | URL | 所引用结论 |
| --- | --- | --- | --- | --- | --- |
| S1 | Polymarket | T0 | unknown | https://gamma\-api\.polymarket\.com/events?slug=fed\-decision\-in\-december\-20260729232808632 | C1, C2, C8, C17 |
| S3 | Federal Reserve | T0 | unknown | https://www\.federalreserve\.gov/monetarypolicy/fomccalendars\.htm | C3 |
| S4 | Federal Reserve | T0 | 2026\-10\-28T14:00:00\-04:00 | https://www\.federalreserve\.gov/newsevents/pressreleases/monetary20261028a\.htm | C4, C7 |
| S5 | BEA | T0 | 2026\-10\-29T08:30:00\-04:00 | https://www\.bea\.gov/news/2026/personal\-income\-and\-outlays\-september\-2026 | C5, C6 |
| S6 | Federal Reserve | T0 | 2026\-09\-16T14:00:00\-04:00 | https://www\.federalreserve\.gov/newsevents/pressreleases/monetary20260916a\.htm | C7 |
| S2 | Polymarket | T0 | unknown | https://clob\.polymarket\.com/book?token\_id=111662129652828266889360374468657435151479595863413519836161861837506140152890 | C9, C11, C17 |

[C1] [C2] [C8] [C17] [C3] [C4] [C7] [C5] [C6] [C9] [C11]

按原内联来源 URL 关联原 sources\.json；来源目录不证明 quote、历史可得性或独立性，缺失项不补造。

## 其他解释

### 最强反方：暂停是一次观察窗口，加息路径尚未结束

9月以12–0加25bp，10月2人仍要加息；核心PCE连续0\.3%且Fed形容就业稳定，支持把10月暂停解释为等待而非方向反转。若下一份核心通胀保持偏强、就业未明显恶化，加25bp的解释会增强；这是定性提示，并非已校准、可重复的改判阈值。这是对盘口前“维持优先”的实质挑战。 [C4] [C5] [C7] [C13] [C14]

### 加息情景的反方：单月实际消费放缓，委员会也已选择等待

9月实际消费增速较8月放缓、实际DPI下降，核心环比未比8月加速；这些单月数据尚未确认持续或全面需求走弱。10月Fed以10–2维持并表示等待更多信息，是继续等待的直接政策依据。总PCE环比升0\.5%不足以单独推出必须12月加息；后续核心价格和就业仅作定性更新提示，尚无校准改判阈值。 [C4] [C5] [C6] [C14]

### 规则替代解释：No change不总等于经济政策未变

无声明默认条款可能把No change变成程序性结果；紧急会议若先改变利率，12月相对会前不变也可能与今天利率不同。最终复盘应同时核对政策变化与合约裁决，不用合约标签代替宏观事实。 [C2] [C16]

## 接下来观察什么

### 11月25日8:30 EST：BEA十月个人收入与支出

检查核心PCE环比是否加速，实际消费与实际收入是否修复；价格与就业组合用于定性更新，不代表已校准、可重复的改判阈值；单次消费放缓不确认持续需求走弱。日期取自本次BEA发布，更新前再核实日历。 [C5] [C6] [C15]

### 随后BLS就业与CPI正式发布、修订及Fed正式沟通

以失业率、就业修订、核心价格广度交叉检验；本次BLS页面403，暂不填数字和未核实的发布日期。若出现就业持续恶化，重新评价降息情景；此为定性提示，尚无已校准、可重复的改判阈值。 [C4] [C14]

### 按日历惯例约11月18日前后关注10月会议纪要，实际发布时间另核实

日历写通常三周后发布；不把推算日期当已公布预约。核对观望者的条件和收紧支持面是否扩大，不能把两张异议票直接变成概率。该观察也仅是定性更新提示，并非已校准改判阈值。 [C3] [C4] [C13]

### 12月8–9日正式声明；延期时需澄清next的指代与裁决

可否定命题：12月正式声明若相对会前目标上限降息，或加息至少50bp，即落在本报告“维持/加25bp”两中心情景之外，记为中心情景未覆盖实际结果；这不等于此前排除尾部可能。保留正式声明和真实结算证据；无声明时不自行指定fallback会议。其余watch仅作定性更新提示，非已校准可重复阈值。无数值概率，不计算独立Brier/log loss。 [C2] [C3] [C16] [C18]

## 其他限制

原表述中 calculations\.json、independent\-freeze\.json、inputs/、raw/ 等相对路径均指原样本目录；本包 legacy\-calculations\.json 仅为旧计算审计副本，未新做公式或算术认证。 

## 来源与结论审计

\[C1\] 12月Fed事件active=true、closed=false；五个子合约也active=true、closed=false且acceptingOrders=true。事件endDate为2026\-12\-10T04:59:00Z，子合约均为2026\-12\-09T23:59:00Z。（fact；2026\-10\-31T17:21:33\.217142\+00:00）

依据：；来源：https://gamma\-api\.polymarket\.com/events?slug=fed\-decision\-in\-december\-20260729232808632

\[C2\] 规则按12月会议前后联邦基金目标区间上限的变化结算，不按从今天到年底的累计变化；非展示幅度向上取至25bp档，例子为12\.5bp算25bp。正式来源为12月8–9日会议声明，声明可触发提前结算；原文条件为“If no statement is released by the end date of the next scheduled meeting”则归No change；未明确next相对哪个时点，因此不能据此指定某次会议为默认截止。（fact；2026\-10\-31T17:21:33\.217142\+00:00）

依据：；来源：https://gamma\-api\.polymarket\.com/events?slug=fed\-decision\-in\-december\-20260729232808632

\[C3\] Fed日历列2026年12月8–9日会议并附经济预测；12月之后的日历会议列2027年1月26–27日，日历说明日期在前次会议确认前为暂定。（fact；2026\-10\-31T17:21:33\.217142\+00:00）

依据：；来源：https://www\.federalreserve\.gov/monetarypolicy/fomccalendars\.htm

\[C4\] 10月28日Fed以10–2维持3\.75%–4\.00%；Cook与Hammack要求加25bp。声明形容经济强劲、就业与劳动力同步、失业率变化不大，通胀仍高，需要更多信息。（fact；2026\-10\-31T17:21:33\.217142\+00:00）

依据：；来源：https://www\.federalreserve\.gov/newsevents/pressreleases/monetary20261028a\.htm

\[C5\] BEA在10月29日公布9月PCE：总价格环比0\.5%、同比3\.6%，核心环比0\.3%、同比3\.1%；8月核心环比同为0\.3%。（fact；2026\-10\-31T17:21:33\.217142\+00:00）

依据：；来源：https://www\.bea\.gov/news/2026/personal\-income\-and\-outlays\-september\-2026

\[C6\] 同份BEA发布中，9月名义PCE环比0\.5%，实际PCE增幅不足0\.1%（表格四舍五入为0\.0%），较8月0\.5%的实际增速放缓；实际可支配收入环比下降0\.3%。（fact；2026\-10\-31T17:21:33\.217142\+00:00）

依据：；来源：https://www\.bea\.gov/news/2026/personal\-income\-and\-outlays\-september\-2026

\[C7\] 9月16日Fed以12–0加息25bp至3\.75%–4\.00%，10月随后维持。（fact；2026\-10\-31T17:21:33\.217142\+00:00）

依据：；来源：https://www\.federalreserve\.gov/newsevents/pressreleases/monetary20260916a\.htm, https://www\.federalreserve\.gov/newsevents/pressreleases/monetary20261028a\.htm

\[C8\] Gamma原始Yes参考价依次为：降50\+bp 0\.40%、降25bp 0\.65%、不变27\.50%、加25bp 70\.50%、加50\+bp 1\.70%；获取时间2026\-10\-31T17:17:21\.213899Z，HTTP Date为17:14:28Z。（price；2026\-10\-31T17:21:33\.217142\+00:00）

依据：；来源：https://gamma\-api\.polymarket\.com/events?slug=fed\-decision\-in\-december\-20260729232808632

\[C9\] CLOB五档Yes bid/ask依次为0\.003/0\.005、0\.006/0\.007、0\.27/0\.28、0\.70/0\.71、0\.016/0\.018；获取窗口17:17:41\.692–41\.992Z，书内时间为17:16:54\.639–17:17:40\.943Z。（price；2026\-10\-31T17:21:33\.217142\+00:00）

依据：；来源：https://clob\.polymarket\.com/book?token\_id=111662129652828266889360374468657435151479595863413519836161861837506140152890

\[C10\] 按保存盘口计算，五个Gamma Yes参考价之和100\.75%，bid和99\.50%，ask和102\.00%；保留原值不强行归一化，不能将其当无摩擦精确概率分布。（inference；2026\-10\-31T17:21:33\.217142\+00:00）

依据：C8, C9；来源：

\[C11\] 加25bp最佳bid/ask显示3010\.62/48170\.95份，按价格乘份数约2107\.43/34201\.37美元；不变为27435\.55/24428\.43份。显示深度可撤单，不等于保证成交。（price；2026\-10\-31T17:21:33\.217142\+00:00）

依据：；来源：https://clob\.polymarket\.com/book?token\_id=111662129652828266889360374468657435151479595863413519836161861837506140152890

\[C12\] 盘口前定性初判以维持为暂定基准、加25bp为实质竞争情景、降息不作基准。10月的等待选择支持暂停，但核心价格仍有压力，无法把异议票数换成概率；缺条件化样本，不给独立数字概率。（inference；2026\-10\-31T17:21:33\.217142\+00:00）

依据：C4, C5, C6；来源：

\[C13\] 盘口后补见9月全票加息，更合理的竞争解释是10月暂歇后恢复收紧；这削弱把10月维持外推至12月的把握。最终将维持与加25bp并列工作情景，加息的证据基础充分，但没有独立模型支持认定70\.5%高估或低估。（inference；2026\-10\-31T17:21:33\.217142\+00:00）

依据：C4, C5, C6, C7, C8；来源：

\[C14\] 9月实际消费增速放缓、实际DPI下降，与通胀压力仍在可以同时成立，但单月数据尚未确认持续或全面需求走弱。10月Fed以10–2选择维持，也支持继续等待有政策依据。核心价格与就业的后续组合仅作定性更新提示，尚非已校准、可重复的改判阈值。（inference；2026\-10\-31T17:21:33\.217142\+00:00）

依据：C4, C5, C6；来源：

\[C15\] BEA列下一次个人收入与支出发布为2026年11月25日8:30 a\.m\. EST；应核对核心PCE与实际消费，而非只看总价格。之后12月8–9日声明和实际规则结算是最终核对节点。（inference；2026\-10\-31T17:21:33\.217142\+00:00）

依据：C2, C3, C5, C6；来源：

\[C16\] 规则存在元数据时点不一致和延期措辞风险：事件与子合约endDate相差5小时；没有界定“next scheduled meeting”的next相对哪个时点，也没有精确时区/截止秒；日历仅证明2027年1月26–27日在12月会议之后，不能确定它就是默认截止；紧急会改变会前利率时不能直接用今天4\.00%上限作差。No change也可能来自无声明默认条款。（inference；2026\-10\-31T17:21:33\.217142\+00:00）

依据：C1, C2, C3, C4；来源：

\[C17\] 加25bp的Gamma lastTradePrice为0\.71，同一Yes token的CLOB last\_trade\_price为0\.290；两端都未给独立成交时戳。这两个字段不一致，未用于方向或价格变动解释，差异原因未核实。（price；2026\-10\-31T17:21:33\.217142\+00:00）

依据：；来源：https://gamma\-api\.polymarket\.com/events?slug=fed\-decision\-in\-december\-20260729232808632, https://clob\.polymarket\.com/book?token\_id=111662129652828266889360374468657435151479595863413519836161861837506140152890

\[C18\] 可否定命题：12月正式声明若相对会议前上限降息或加息至少50bp，即超出维持/加25bp两中心情景，应记为中心情景未覆盖；其余watch仅作定性更新提示，无已校准可重复阈值。无数值概率不计算独立Brier/log loss。（inference；2026\-10\-31T17:21:33\.217142\+00:00）

依据：C2, C13, C14；来源：

S1 · Polymarket · T0 · published\_at：unknown · retrieved\_at：2026\-10\-31T17:17:21\.213899\+00:00 · quote：The FED interest rates are defined in this market by the upper bound of the target federal funds range\. The decisions on the target federal funds range are made by the Federal Open Market Committee \(FOMC\) meetings\.<br><br>This market will resolve to the amount of basis points the upper bound of the target federal funds rate is changed by versus the level it was prior to the Federal Reserve's December 2026 meeting\.<br><br>If the target federal funds rate is changed to a level not expressed in the displayed options, the change will be rounded up to the nearest 25 and will resolve to the relevant bracket\. \(e\.g\. if there's a cut/increase of 12\.5 bps it will be considered to be 25 bps\)<br><br>The resolution source for this market is the FOMC’s statement after its meeting scheduled for December 8\-9, 2026 according to the official calendar: https://www\.federalreserve\.gov/monetarypolicy/fomccalendars\.htm\.<br><br>The level and change of the target federal funds rate is also published at the official website of the Federal Reserve at https://www\.federalreserve\.gov/monetarypolicy/openmarket\.htm\.<br><br>This market may resolve as soon as the FOMC’s statement for their December meeting with relevant data is issued\. If no statement is released by the end date of the next scheduled meeting, this market will resolve to the "No change" bracket\. · locator：\[0\]\.description; \[0\]\.active/closed/endDate; \[0\]\.markets\[\*\] · origin\_id：None · origin\_basis：Unresolved in schema 1; publisher and URL are not proof of independent origin\. · evidence\_kind：document · access\_status：ok · supports：\[\] · selection：\{"priority": "background", "purpose": "Development regression source audit; schema 1 claim citations remain unchanged\.", "reason": "Legacy evidence catalog only; no new strict semantic selection performed\.", "relevance": "context", "selected": false\}

[https://gamma\-api\.polymarket\.com/events?slug=fed\-decision\-in\-december\-20260729232808632](https://gamma-api.polymarket.com/events?slug=fed-decision-in-december-20260729232808632)

S3 · Federal Reserve · T0 · published\_at：unknown · retrieved\_at：2026\-10\-31T17:16:27\.865600\+00:00 · quote：December<br>8\-9\*<br>\* Meeting associated with a Summary of Economic Projections\. · locator：2026 FOMC Meetings &gt; December；2027 &gt; January；日历说明 · origin\_id：None · origin\_basis：Unresolved in schema 1; publisher and URL are not proof of independent origin\. · evidence\_kind：document · access\_status：ok · supports：\[\] · selection：\{"priority": "background", "purpose": "Development regression source audit; schema 1 claim citations remain unchanged\.", "reason": "Legacy evidence catalog only; no new strict semantic selection performed\.", "relevance": "context", "selected": false\}

[https://www\.federalreserve\.gov/monetarypolicy/fomccalendars\.htm](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm)

S4 · Federal Reserve · T0 · published\_at：2026\-10\-28T14:00:00\-04:00 · retrieved\_at：2026\-10\-31T17:16:28\.913975\+00:00 · quote：The Committee decided to maintain the target range for the federal funds rate at 3\-3/4 to 4 percent, in support of the Federal Reserve's dual mandate\. · locator：正文政策段、经济评价、通胀段、异议段；txt 285–289行 · origin\_id：None · origin\_basis：Unresolved in schema 1; publisher and URL are not proof of independent origin\. · evidence\_kind：document · access\_status：ok · supports：\[\] · selection：\{"priority": "background", "purpose": "Development regression source audit; schema 1 claim citations remain unchanged\.", "reason": "Legacy evidence catalog only; no new strict semantic selection performed\.", "relevance": "context", "selected": false\}

[https://www\.federalreserve\.gov/newsevents/pressreleases/monetary20261028a\.htm](https://www.federalreserve.gov/newsevents/pressreleases/monetary20261028a.htm)

S5 · BEA · T0 · published\_at：2026\-10\-29T08:30:00\-04:00 · retrieved\_at：2026\-10\-31T17:16:27\.948502\+00:00 · quote：From the preceding month, the PCE price index for September increased 0\.5 percent \. Excluding food and energy, the PCE price index increased 0\.3 percent\. · locator：正文价格、实际消费、月度对照表、Next release；txt 68–71行 · origin\_id：None · origin\_basis：Unresolved in schema 1; publisher and URL are not proof of independent origin\. · evidence\_kind：document · access\_status：ok · supports：\[\] · selection：\{"priority": "background", "purpose": "Development regression source audit; schema 1 claim citations remain unchanged\.", "reason": "Legacy evidence catalog only; no new strict semantic selection performed\.", "relevance": "context", "selected": false\}

[https://www\.bea\.gov/news/2026/personal\-income\-and\-outlays\-september\-2026](https://www.bea.gov/news/2026/personal-income-and-outlays-september-2026)

S6 · Federal Reserve · T0 · published\_at：2026\-09\-16T14:00:00\-04:00 · retrieved\_at：2026\-10\-31T17:17:42\.004357\+00:00 · quote：The Committee decided to raise the target range for the federal funds rate by 1/4 percentage point to 3\-3/4 to 4 percent, in support of the Federal Reserve's dual mandate\. · locator：正文投票与政策段 · origin\_id：None · origin\_basis：Unresolved in schema 1; publisher and URL are not proof of independent origin\. · evidence\_kind：document · access\_status：ok · supports：\[\] · selection：\{"priority": "background", "purpose": "Development regression source audit; schema 1 claim citations remain unchanged\.", "reason": "Legacy evidence catalog only; no new strict semantic selection performed\.", "relevance": "context", "selected": false\}

[https://www\.federalreserve\.gov/newsevents/pressreleases/monetary20260916a\.htm](https://www.federalreserve.gov/newsevents/pressreleases/monetary20260916a.htm)

S2 · Polymarket · T0 · published\_at：unknown · retrieved\_at：2026\-10\-31T17:17:41\.991648\+00:00 · quote： · locator：bids/asks\[\*\]\.price,size; timestamp; hash · origin\_id：None · origin\_basis：Unresolved in schema 1; publisher and URL are not proof of independent origin\. · evidence\_kind：document · access\_status：ok · supports：\[\] · selection：\{"priority": "background", "purpose": "Development regression source audit; schema 1 claim citations remain unchanged\.", "reason": "Legacy evidence catalog only; no new strict semantic selection performed\.", "relevance": "context", "selected": false\}

[https://clob\.polymarket\.com/book?token\_id=111662129652828266889360374468657435151479595863413519836161861837506140152890](https://clob.polymarket.com/book?token_id=111662129652828266889360374468657435151479595863413519836161861837506140152890)

S1 · Polymarket · T0 · published\_at：unknown

[https://gamma\-api\.polymarket\.com/events?slug=fed\-decision\-in\-december\-20260729232808632](https://gamma-api.polymarket.com/events?slug=fed-decision-in-december-20260729232808632)

S1 · Polymarket · T0 · published\_at：unknown

[https://gamma\-api\.polymarket\.com/events?slug=fed\-decision\-in\-december\-20260729232808632](https://gamma-api.polymarket.com/events?slug=fed-decision-in-december-20260729232808632)

S3 · Federal Reserve · T0 · published\_at：unknown

[https://www\.federalreserve\.gov/monetarypolicy/fomccalendars\.htm](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm)

S4 · Federal Reserve · T0 · published\_at：2026\-10\-28T14:00:00\-04:00

[https://www\.federalreserve\.gov/newsevents/pressreleases/monetary20261028a\.htm](https://www.federalreserve.gov/newsevents/pressreleases/monetary20261028a.htm)

S5 · BEA · T0 · published\_at：2026\-10\-29T08:30:00\-04:00

[https://www\.bea\.gov/news/2026/personal\-income\-and\-outlays\-september\-2026](https://www.bea.gov/news/2026/personal-income-and-outlays-september-2026)

S5 · BEA · T0 · published\_at：2026\-10\-29T08:30:00\-04:00

[https://www\.bea\.gov/news/2026/personal\-income\-and\-outlays\-september\-2026](https://www.bea.gov/news/2026/personal-income-and-outlays-september-2026)

S6 · Federal Reserve · T0 · published\_at：2026\-09\-16T14:00:00\-04:00

[https://www\.federalreserve\.gov/newsevents/pressreleases/monetary20260916a\.htm](https://www.federalreserve.gov/newsevents/pressreleases/monetary20260916a.htm)

S4 · Federal Reserve · T0 · published\_at：2026\-10\-28T14:00:00\-04:00

[https://www\.federalreserve\.gov/newsevents/pressreleases/monetary20261028a\.htm](https://www.federalreserve.gov/newsevents/pressreleases/monetary20261028a.htm)

S1 · Polymarket · T0 · published\_at：unknown

[https://gamma\-api\.polymarket\.com/events?slug=fed\-decision\-in\-december\-20260729232808632](https://gamma-api.polymarket.com/events?slug=fed-decision-in-december-20260729232808632)

S2 · Polymarket · T0 · published\_at：unknown

[https://clob\.polymarket\.com/book?token\_id=111662129652828266889360374468657435151479595863413519836161861837506140152890](https://clob.polymarket.com/book?token_id=111662129652828266889360374468657435151479595863413519836161861837506140152890)

S2 · Polymarket · T0 · published\_at：unknown

[https://clob\.polymarket\.com/book?token\_id=111662129652828266889360374468657435151479595863413519836161861837506140152890](https://clob.polymarket.com/book?token_id=111662129652828266889360374468657435151479595863413519836161861837506140152890)

S1 · Polymarket · T0 · published\_at：unknown

[https://gamma\-api\.polymarket\.com/events?slug=fed\-decision\-in\-december\-20260729232808632](https://gamma-api.polymarket.com/events?slug=fed-decision-in-december-20260729232808632)

S2 · Polymarket · T0 · published\_at：unknown

[https://clob\.polymarket\.com/book?token\_id=111662129652828266889360374468657435151479595863413519836161861837506140152890](https://clob.polymarket.com/book?token_id=111662129652828266889360374468657435151479595863413519836161861837506140152890)

来源状态：\{"S1": \{"original\_status": "success", "reason": "Original retrieval record reused, no new fetch\.", "status": "ok"\}, "S2": \{"original\_status": "success", "reason": "Original retrieval record reused, no new fetch\.", "status": "ok"\}, "S3": \{"original\_status": "success", "reason": "Original retrieval record reused, no new fetch\.", "status": "ok"\}, "S4": \{"original\_status": "success", "reason": "Original retrieval record reused, no new fetch\.", "status": "ok"\}, "S5": \{"original\_status": "success", "reason": "Original retrieval record reused, no new fetch\.", "status": "ok"\}, "S6": \{"original\_status": "success", "reason": "Original retrieval record reused, no new fetch\.", "status": "ok"\}, "regression\_external\_retrieval": \{"reason": "开发回归样本（dev sample，非 heldout）。仅将原冻结材料转换为 schema 2 报告；保留原 as\_of，无新增检索、事实、引语、计算或研究判断。claims 保留原 schema 1，本次结构校验及开发归档不等于 strict schema 2 claims 验证，也不提供严格历史可得性证明。", "status": "not\_run"\}\}
