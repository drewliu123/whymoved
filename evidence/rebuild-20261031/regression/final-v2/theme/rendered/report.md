# 【开发回归样本】AI用电到电力设备利润：Eaton的订单已来，交付兑现更值得验证

AI数据中心用电增长如何转成电力设备供应商收入与利润，哪个环节最值得验证？

研究截点 2026\-10\-31T17:25:57Z · theme · 主题到利润现金：复用冻结证据的开发回归

证据模式：旧版 schema 1；本报告未按 schema 2 的来源与证据契约校验。

## 判断

当前更值得验证的是Eaton Electrical Americas的数据中心配电与预集成供电设备：公司披露订单与收入增长，分部利润率出现恢复，与交付爬坡改善相容；尚未识别同批订单向收入的转换，价格、组合及并购基数也可解释部分变化。核心问题已从“AI会不会用更多电”推进到“新增产能能否把backlog按可接受成本转成收入、经营利润和现金”。本案例支持该环节优先研究，不足以判定全行业最优或计算纯AI增量利润。 [C5] [C11] [C13] [C16] [C17] [C19] [C21]

重要限制：开发回归样本（dev sample，非 heldout）。仅将原冻结材料转换为 schema 2 报告；保留原 as\_of，无新增检索、事实、引语、计算或研究判断。claims 保留原 schema 1，本次结构校验及开发归档不等于 strict schema 2 claims 验证，也不提供严格历史可得性证明。 

重要限制：纯AI的订单/收入绝对额、产品和地区拆分缺失；广义21%敞口不能代替。 

重要限制：未取得订单取消、延期、客户集中度、项目验收与收入确认合同条款；不能估算backlog兑现日期。 

重要限制：没有价格/量/组合/扩产成本利润桥，也无主题营运资本和现金分拆；主题增量利润与FCF不作点估计。 

重要限制：六个来源均为同一公司，缺竞品官方期间数据和客户侧项目核对；不作行业赢家排序。 

重要限制：Eaton Q3尚未发布；官方入口核实最新已实现季度，不等于穷尽全部监管/投资者会议文件。 

重要限制：WebFetch地区网页和主站多次失败、PDF工具缺失；origin\-edge与本地PDFKit补齐核心证据，失败详情保留。 

重要限制：父任务独立审查提出四项定向修正，本轮已落实并记录independent\-review\.md；HTML与浏览器呈现验收仍由父任务统一完成。 

## 研究边界与可证伪命题

地区以美洲电气分部为主，期间取2025Q4、2026Q1、2026Q2；季度同比用于经营比较，环比用于观察恢复，不能混同；同名分部不等于已剔除并购/汇率的恒定范围。命题：截至下一次及随后季度披露，强数据中心采购应体现为美洲交付增长，并伴随经营利润率及增量利润率恢复；若只有积压堆高而利润/现金不兑现，主题到盈利的链条仍未成立。实际证据截点为2026\-10\-31 17:25:57 UTC。官网显示Q3要到11月3日公布；最新实现季度为7月31日发布的Q2，9月2日扩产公告提供更晚的运营证据。 [C1] [C16] [C21]

为什么重要：固定季度、地区与证伪条件，避免把未披露季度或不同统计范围当作已实现趋势。

相较基线：原 report\.json 的同名 finding 与原 claims\.json（C1, C16, C21）；开发样本复用。

研究增量（connection）：仅把原结论与其验证意义重新连接：固定季度、地区与证伪条件，避免把未披露季度或不同统计范围当作已实现趋势。 本轮无新事实、计算或判断更新，非相对原研究的新发现。

## 从用电到设备收入：中间有四道门

分析路径：AI计算负荷/机架功率需求 → 可实施项目与供电接入/建设安排 → 按冗余、配电与热管理规格采购 → 订单与backlog → 产能、部件、人员与工程协同交付/验收 → 合同要求下确认收入 → 扣交付成本后的利润 → 应收回款减营运资本和capex后的现金。产品关联由grid\-to\-chip、Fibrebond和液冷披露支持；负荷到下单的转化率、并网时滞、收入确认条款及取消率是待验证推断。用电TWh是运行流量，设备更多跟新增/改造装机容量及架构有关；利用率变化未必触发等比例设备采购。电网瓶颈可能让设备提前下单，也可能推迟验收与回款，不能只画一条同步向上的箭头。 [C13] [C17] [C19]

为什么重要：逐段区分负荷、采购、交付、利润与现金，暴露从用电预测直接推导设备盈利的跳步。

相较基线：原 report\.json 的同名 finding 与原 claims\.json（C13, C17, C19）；开发样本复用。

研究增量（connection）：仅把原结论与其验证意义重新连接：逐段区分负荷、采购、交付、利润与现金，暴露从用电预测直接推导设备盈利的跳步。 本轮无新事实、计算或判断更新，非相对原研究的新发现。

## 为什么优先看配电交付和集成能力

Eaton已将数据中心订单增长连接到可观察的Electrical Americas分部，Fibrebond也明确计入该分部。模块化围护结构将电力设备预集成，价值可能来自更快交付、工程整合和可靠性；这些仍需项目价格、交期与贡献率证实。它比抽象用电预测更接近采购与利润验证点；本研究未取得变压器、开关设备、UPS等产品单项利润和产能数据，不能进一步排名某个单品最赚钱。 [C5] [C13] [C16] [C19]

为什么重要：把研究焦点放到可观察的交付与集成环节，同时保留无法排名产品利润的边界。

相较基线：原 report\.json 的同名 finding 与原 claims\.json（C5, C13, C16, C19）；开发样本复用。

研究增量（connection）：仅把原结论与其验证意义重新连接：把研究焦点放到可观察的交付与集成环节，同时保留无法排名产品利润的边界。 本轮无新事实、计算或判断更新，非相对原研究的新发现。

## 量级已重要，AI敞口仍不可辨识

2025 Data Centers &amp; Distributed IT占Eaton销售21%，乘全年27448百万美元约为5764百万美元，展示为约58亿美元。它是广义终端市场历史收入量级，包括非AI数据中心和分布式IT，并非AI纯度、TAM或市场份额。美洲期末backlog从132亿升至145亿、152亿美元，半年约增15\.15%；152亿相当于Q2分部单季销售的3\.85倍，只说明存量重要，不能据此宣称能锁定3\.85个季度收入。订单是期间流入，backlog是存量，取消、交付和统计范围变更均可能影响二者。 [C7] [C8] [C12]

为什么重要：历史广义敞口和积压存量说明量级，但不能替代纯AI收入或未来交付保证。

相较基线：原 report\.json 的同名 finding 与原 claims\.json（C7, C8, C12）；开发样本复用。

研究增量（connection）：仅把原结论与其验证意义重新连接：历史广义敞口和积压存量说明量级，但不能替代纯AI收入或未来交付保证。 本轮无新事实、计算或判断更新，非相对原研究的新发现。

## 利润断点最有信息价值

2026Q1美洲销售同比增加590百万美元，分部利润只增加18百万美元，增量比率3\.05%；Q2销售增601、利润增101，增量比率升至16\.81%。Q2平均利润率较Q1恢复约193基点，但较上年同期仍低约193基点（公司取整\+190/\-200基点）。Q1销售增20%含有机14、并购5、汇率1个百分点，Q2增18%全有机；3\.05%和16\.81%的比率未经范围调整。分部利润率恢复与交付爬坡改善相容，但没有识别同批订单转换，价格、组合及并购基数也可解释部分变化，不能独立证明效率提升或稀缺溢价扩大：增量利润率仍低于平均利润率，价格、产品组合、扩产启动和效率没有分拆桥。公司将下半年&gt;30%列作展望，需在Q3和Q4实际数据齐备后，按\(Q3经营利润\+Q4经营利润\)/\(Q3销售\+Q4销售\)&gt;30%检验；单季结果不能判断整个下半年展望兑现。 [C3] [C4] [C11] [C20]

为什么重要：增量利润与平均利润率的差异有助于检验兑现，范围变化限制其因果解释。

相较基线：原 report\.json 的同名 finding 与原 claims\.json（C3, C4, C11, C20）；开发样本复用。

研究增量（connection）：仅把原结论与其验证意义重新连接：增量利润与平均利润率的差异有助于检验兑现，范围变化限制其因果解释。 本轮无新事实、计算或判断更新，非相对原研究的新发现。

## 现金与全公司利润再加一道校验

Q2全公司OCF1127、capex253、FCF874百万美元，上年同期分别918、202、716，现金随经营改善，但没有主题/分部现金表。Q4与Q2存在季节差异，不能拿Q4高现金推导Q2恶化。Q2全公司GAAP净利从982降至821百万美元，调整后盈利却从1155增至1228；并购、利息、摊销等使分部利润不能直接替代股东盈利。分部信息将Fibrebond员工交易/留任费用等并购相关支出列在Corporate Other expense，摊销与重组也列Corporate；分部利润因此不是包含这些费用的全经济成本后利润。不能把全部Corporate费用归给AI。该FCF定义未扣收购价款，也不是AI投资净回报。 [C9] [C10]

为什么重要：全公司现金、净利与分部利润口径不同，避免将并购成本或全部现金归于AI主题。

相较基线：原 report\.json 的同名 finding 与原 claims\.json（C9, C10）；开发样本复用。

研究增量（connection）：仅把原结论与其验证意义重新连接：全公司现金、净利与分部利润口径不同，避免将并购成本或全部现金归于AI主题。 本轮无新事实、计算或判断更新，非相对原研究的新发现。

## 量化应停在输入边界

主题利润只给敏感性条件：同一批AI订单B，取消/削减比例d，本期收入确认交付率c，新增贡献率m、增量固定/启动成本及折旧F，则ΔR=B\(1−d\)c，ΔOP=ΔR×m−F；盈利要求B\(1−d\)cm&gt;F。现金还需扣现金税、营运资本和资本开支并加回非现金项。缺B、d、c、m、F及现金桥，点估计不成立。分部平均利润率不能代替m；21%广义历史敞口不能代替纯AI基数。calculations\.json保留公式和可重算已实现同比桥。 [C11] [C19]

为什么重要：显式缺失的输入阻止虚假精确点估计，并为后续数据提出可执行的验证需求。

相较基线：原 report\.json 的同名 finding 与原 claims\.json（C11, C19）；开发样本复用。

研究增量（connection）：仅把原结论与其验证意义重新连接：显式缺失的输入阻止虚假精确点估计，并为后续数据提出可执行的验证需求。 本轮无新事实、计算或判断更新，非相对原研究的新发现。

### 同分部经营对照：Electrical Americas（未作恒定范围调整）

| 期间 | 收入（百万美元） | 分部经营利润（百万美元） | 经营利润率 | 滚动12个月有机订单同比 | 期末backlog（十亿美元） |
| --- | --- | --- | --- | --- | --- |
| 2025Q4 | 3506 | 1046 | 29\.8% | 16% | 13\.2 |
| 2026Q1 | 3600 | 922 | 25\.6% | 42% | 14\.5 |
| 2026Q2 | 3951 | 1088 | 27\.5% | 41% | 15\.2 |

[C2] [C3] [C4] [C10] [C11] [C12]

Q1美洲销售增20%含有机14/并购5/汇率1个百分点；Q2增18%全有机，增量利润比率未经恒定范围调整。分部利润未包含列Corporate的并购相关费用（含Fibrebond员工交易/留任）、摊销和重组，不是全经济成本后利润；不能把Corporate全部归AI。 开发转换：引用经原 claims\.json 核对；仅提供原研究表格的结论级关联。

### 数据中心专项披露：只能各自同比

| 期间 | 覆盖范围 | 当季订单同比 | 当季收入同比 | 限制 |
| --- | --- | --- | --- | --- |
| 2026Q1 | Electrical Americas | 约240% | 约50% | 非AI单独；未披露绝对额 |
| 2026Q2 | Electrical Sector | 约85% | 约65% | 覆盖扩大；非同口径趋势；未注明有机 |

[C5] [C6]

 开发转换：引用经原 claims\.json 核对；仅提供原研究表格的结论级关联。

### 现金兑现：全公司，不能归因AI

| 期间 | OCF（百万美元） | capex（百万美元） | FCF（百万美元） | FCF定义 |
| --- | --- | --- | --- | --- |
| 2025Q4 | 1965 | 392 | 1573 | OCF−PP&amp;E capex |
| 2025Q2 | 918 | 202 | 716 | OCF−PP&amp;E capex |
| 2026Q2 | 1127 | 253 | 874 | OCF−PP&amp;E capex |

[C9]

 开发转换：引用经原 claims\.json 核对；仅提供原研究表格的结论级关联。

### 原 claims 内联来源目录（未新增取证）

| 原来源ID | 发布方 | 层级 | 发布时间（原记录） | URL | 所引用结论 |
| --- | --- | --- | --- | --- | --- |
| S1 | Eaton | T0 | unknown | https://www\.eaton\.com/us/en\-us/company/investor\-relations/financial\-presentations\-webcasts\.html | C1, C23 |
| S4 | Eaton | T0 | 2026\-07\-31 | https://www\.eaton\.com/content/dam/eaton/company/investor\-relations/quarterly\-earnings/filings/2026/q2/q2\-20265\-earnings\-complete\.pdf | C1, C4, C9, C10, C13, C15 |
| S2 | Eaton | T0 | 2026\-02\-03 | https://www\.eaton\.com/content/dam/eaton/company/investor\-relations/quarterly\-earnings/filings/2025/q4/4Q\-2025\-earnings\-complete\.pdf | C2, C7, C9 |
| S3 | Eaton | T0 | 2026\-05\-05 | https://www\.eaton\.com/content/dam/eaton/company/investor\-relations/quarterly\-earnings/filings/2026/q1/q1\-2026\-analyst\-presentation\.pdf | C2, C3, C5, C13 |
| S5 | Eaton | T0 | 2026\-07\-31 | https://www\.eaton\.com/content/dam/eaton/company/investor\-relations/quarterly\-earnings/filings/2026/q2/q2\-2026\-analyst\-presentation\.pdf | C4, C5, C7, C20 |
| S6 | Eaton | T0 | 2026\-09\-02 | https://www\.eaton\.com/us/en\-us/company/news\-insights/news\-releases/2026/eaton\-expands\-manufacturing\-for\-modular\-electrical\-enclosures\.html | C14 |

[C1] [C23] [C4] [C9] [C10] [C13] [C15] [C2] [C7] [C3] [C5] [C20] [C14]

按原内联来源 URL 关联原 sources\.json；来源目录不证明 quote、历史可得性或独立性，缺失项不补造。

### 原研究机制链与证据边界

| 起点 | 终点 | 原研究状态 |
| --- | --- | --- |
| AI负荷/设备功率 | 项目获电与采购 | 待检验，缺项目匹配 |
| 数据中心采购 | 专项订单与收入 | 披露支持，口径有断点 |
| 美洲订单/backlog | 美洲收入与分部利润 | 共同变化与交付爬坡改善相容；非同批订单转换或项目因果识别 |
| 分部利润 | 主题现金 | 未识别 |

[C17] [C19] [C5] [C3] [C4] [C11] [C9]

## 其他解释

### 强订单可能是长交期锁产能，而非当期利润保证

这是待检验替代解释：订单和积压可以先于项目通电，客户为交期提前采购甚至多源预订；本次未取得取消/重复预订数据，不能认定已发生。若后续交付迟缓、延期上升而backlog不降，应降低收入与现金兑现速度判断。 [C12] [C17] [C19]

### 扩产兑现会消除部分稀缺，竞争也可能压价

9月2日超过242百万美元的新厂投资计划拟使Fibrebond美国产能翻倍，原Minden产能此前三年已翻倍；属于实质供给反证，但公告不披露新厂投产日期。产能兑现可提收入，也可能增加启动成本或在需求放缓时压低利用率。官网还明确提示价格竞争与替代技术风险。没有竞品订单、价格和成本证据，不能宣称永久稀缺或Eaton份额必升；模块化、液冷和供电架构变化可改变价值在不同产品间的归属，未必降低整体支出。 [C14] [C18] [C22] [C23]

### 行业主题与并购/其他终端市场增长混在一起

Q2 Electrical Global的44%销售增幅有25个百分点来自Boyd Thermal并购贡献，有机18%、汇率1%；不能全部归于AI。Q1/Q2数据中心专项披露又跨Americas/Sector口径，不能连成一条增长曲线。若未来仍只提供混合口径和分部总利润，应维持“重要敞口、无法归因纯AI利润”的判断。 [C6] [C15] [C19]

## 接下来观察什么

### 11月3日Q3及随后季度：同口径数据中心订单、销售与取消/延期说明

确认Electrical Americas与Sector拆分、有机与并购拆分；否则不解释专项增速的季度变化。 [C1] [C5] [C6]

### 美洲分部交付/收入、backlog金额和book\-to\-bill

收入提高且积压有序兑现支持交付爬坡；仅积压增高仍可能是供给或项目阻滞。滚动比率不作季度转化率。 [C4] [C12] [C17]

### 美洲经营利润率、同比Δ利润/Δ收入与扩产成本桥

以未经范围调整的Q1 3\.05%、Q2 16\.81%为已实现参照。下半年&gt;30%须待Q3/Q4数据齐备后按\(Q3经营利润\+Q4经营利润\)/\(Q3销售\+Q4销售\)核对，不能用单季替代半年；本次仅核实Q3发布日期，不推测Q4发布日期。收入增而利润率长期停滞将削弱价值捕获判断。 [C11] [C20] [C21]

### 全公司OCF、capex、FCF及营运资本解释；争取分部/主题现金数据

现金与利润共同改善才增强兑现证据；公司现金改善不能单独证明AI回款。 [C9] [C19] [C21]

### Fibrebond新厂开工、投产、利用率和新增订单覆盖；竞品交期与报价

区分计划与实际产能；若供给释放伴随降价/利用率下滑，应下调稀缺利润假设。现有公告没有投产时间。 [C14] [C18] [C22]

## 其他限制

原表述中 calculations\.json、independent\-freeze\.json、inputs/、raw/ 等相对路径均指原样本目录；本包 legacy\-calculations\.json 仅为旧计算审计副本，未新做公式或算术认证。 

## 来源与结论审计

\[C1\] 截至截点，Eaton官网列示Q3 2026将于11月3日发布；本研究最新已实现季度为2026Q2，不能将Q3指引当实际。（fact；2026\-10\-31T17:25:57Z）

依据：；来源：S1, S4

\[C2\] Electrical Americas 2025Q4销售3506百万美元、分部经营利润1046百万美元；滚动12个月有机订单同比增16%，backlog为13\.2十亿美元。（fact；2026\-10\-31T17:25:57Z）

依据：；来源：S2, S3

\[C3\] Electrical Americas 2026Q1销售3600百万美元、经营利润922百万美元，同比分别20%和2%（公司取整）；销售增长含有机14、并购5、汇率1个百分点；利润率25\.6%，上年30\.0%；滚动订单增42%，backlog14\.5十亿美元，同比增44%。（fact；2026\-10\-31T17:25:57Z）

依据：；来源：S3

\[C4\] Electrical Americas 2026Q2销售3951百万美元、经营利润1088百万美元；销售同比增18%全有机，未经恒定范围调整；利润率27\.5%，上年29\.5%；滚动有机订单同比增41%，backlog15\.2十亿美元、同比增33%，滚动book\-to\-bill 1\.3。（fact；2026\-10\-31T17:25:57Z）

依据：；来源：S4, S5

\[C5\] 2026Q1 Electrical Americas数据中心当季订单约增240%、收入约增50%；2026Q2披露改为Electrical Sector数据中心当季订单约增85%、收入约增65%；后者未在该条注明有机口径。（fact；2026\-10\-31T17:25:57Z）

依据：；来源：S3, S5

\[C6\] 两季数据中心专项口径不同，240%到85%不能被解释为同一业务订单减速，50%到65%也不能直接写成同一业务收入加速。（inference；2026\-10\-31T17:25:57Z）

依据：C5；来源：

\[C7\] Eaton披露Data Centers &amp; Distributed IT占2025全公司销售21%；2025公司销售27448百万美元。该分类包括Distributed IT，不等于纯AI数据中心。（fact；2026\-10\-31T17:25:57Z）

依据：；来源：S2, S5

\[C8\] 以披露分类和全年销售相乘，2025 Data Centers &amp; Distributed IT销售量级约5764百万美元；这是历史敞口近似，不是AI收入、市场TAM或市占率。（inference；2026\-10\-31T17:25:57Z）

依据：C7；来源：

\[C9\] 2026Q2全公司经营现金1127百万美元、capex253百万美元、FCF874百万美元；2025Q2分别918、202、716。2025Q4分别1965、392、1573，现金口径均为全公司。（fact；2026\-10\-31T17:25:57Z）

依据：；来源：S2, S4

\[C10\] 2026Q2全公司GAAP归属净利润821百万美元，上年982；调整后盈利1228，上年1155。Fibrebond员工交易/留任等并购相关费用在分部信息中计为Corporate Other expense，摊销与重组亦列Corporate；分部利润未包含这些全经济成本，不等于全公司净利润或现金，Corporate全部费用不能归AI。（fact；2026\-10\-31T17:25:57Z）

依据：；来源：S4

\[C11\] 按原表重算，Electrical Americas 2026Q1同比增量利润/增量收入约3\.05%，2026Q2约16\.81%；Q2利润率环比改善约193基点但同比仍低约193基点，公司按披露利润率取整表述为\+190/\-200基点。Q1销售增20%含有机14、并购5、汇率1个百分点；Q2增18%全为有机。两个增量比率未经范围调整，不能单独证明效率改善。（inference；2026\-10\-31T17:25:57Z）

依据：C3, C4；来源：

\[C12\] 美洲backlog从2025Q4的13\.2十亿美元升至2026Q2的15\.2，增长约15\.15%；期末存量相当于Q2季度销售约3\.85倍，不能当作3\.85个季度的交付保证。（inference；2026\-10\-31T17:25:57Z）

依据：C2, C4；来源：

\[C13\] Eaton的官方产品范围从Grid Connection、Gray Space、White Space延伸至软件服务和冷却；Fibrebond提供预集成模块化电力围护结构，计入Electrical Americas。（fact；2026\-10\-31T17:25:57Z）

依据：；来源：S3, S4

\[C14\] 2026年9月Eaton宣布超过242百万美元投入Arkansas新厂，拟将Fibrebond美国定制电气围护结构产能翻倍；Minden产能此前三年已翻倍。公告未给新厂投产日期，且服务数据中心、公用事业等多个市场。（fact；2026\-10\-31T17:25:57Z）

依据：；来源：S6

\[C15\] Q2 Electrical Global销售增长44%中，有机18%、Boyd Thermal并购贡献25%、汇率1%；不能把该分部全部增长归为AI新增需求。（fact；2026\-10\-31T17:25:57Z）

依据：；来源：S4

\[C16\] 最值得验证的是Electrical Americas中数据中心相关配电/预集成供电设备的backlog转交付，再转增量经营利润与现金；已有订单与收入增长披露及分部利润率恢复，与交付爬坡改善相容；未识别同批订单转换，价格、组合及并购基数亦可解释，AI独立盈利归因尚未建立。（inference；2026\-10\-31T17:25:57Z）

依据：C3, C4, C5, C9, C11, C13；来源：

\[C17\] 用电增长先要形成获电/建设安排和设备规格，才可能成为设备采购；订单积累后还需制造、安装/验收与回款。运行TWh不能直接乘设备单价推导收入；投运延迟对订单、交付、收入、现金可发生在不同时间。（inference；2026\-10\-31T17:25:57Z）

依据：C5, C9, C13, C14；来源：

\[C18\] 扩产同时支持交付并削弱永久稀缺假设：若产能释放快于有效采购，价格与利用率可能承压；现有分部数字不能识别扩产成本、价格、产品组合各自贡献。（inference；2026\-10\-31T17:25:57Z）

依据：C3, C4, C14；来源：

\[C19\] 本次核对的六个官方来源未提供AI专属收入基数、增量毛利率/成本桥、取消延期条款及项目回款结构，不能计算可辩护的AI增量利润点估计或给出取消率。（inference；2026\-10\-31T17:25:57Z）

依据：C3, C4, C5, C7, C9, C13, C14；来源：

\[C20\] Q2材料将Electrical Americas下半年利润率&gt;30%展示为展望，全年28\.8–29\.2%为指引，均未在本截点实现。（fact；2026\-10\-31T17:25:57Z）

依据：；来源：S5

\[C21\] 若后续订单/积压仍强而增量利润率与现金兑现继续改善，交付爬坡解释增强；若订单延期、margin恢复停滞或现金落后，应下调利润兑现判断。（inference；2026\-10\-31T17:25:57Z）

依据：C4, C9, C11, C14, C20；来源：

\[C22\] 竞争和替代的证据限于Eaton披露的竞争定价/技术风险、模块化和液冷路线变化；没有直接竞品订单、价格、成本曲线，不能断言Eaton具永久定价权或排名全行业最优。（inference；2026\-10\-31T17:25:57Z）

依据：C13, C14, C15, C23；来源：

\[C23\] Eaton官网风险提示包括competitive pressures on sales and pricing及introduction of competing technologies。（fact；2026\-10\-31T17:25:57Z）

依据：；来源：S1

S1 · Eaton · T0 · published\_at：unknown · retrieved\_at：2026\-10\-31T17:23:30\.434003Z · quote：Eaton will announce third quarter 2026 earnings on Tuesday, November 3, 2026, before the opening of the New York Stock Exchange\. · locator：Third quarter 2026 · origin\_id：None · origin\_basis：Unresolved in schema 1; publisher and URL are not proof of independent origin\. · evidence\_kind：document · access\_status：ok · supports：\[\] · selection：\{"priority": "background", "purpose": "Development regression source audit; schema 1 claim citations remain unchanged\.", "reason": "Legacy evidence catalog only; no new strict semantic selection performed\.", "relevance": "context", "selected": false\}

[https://www\.eaton\.com/us/en\-us/company/investor\-relations/financial\-presentations\-webcasts\.html](https://www.eaton.com/us/en-us/company/investor-relations/financial-presentations-webcasts.html)

S4 · Eaton · T0 · published\_at：2026\-07\-31 · retrieved\_at：2026\-10\-31T17:20:35\.056681Z · quote：Electrical Americas $ 1,088 $ 987 $ 2,010 $ 1,891 · locator：p8 Business Segment Information；2026Q2/2025Q2/2026H1/2025H1 · origin\_id：None · origin\_basis：Unresolved in schema 1; publisher and URL are not proof of independent origin\. · evidence\_kind：document · access\_status：ok · supports：\[\] · selection：\{"priority": "background", "purpose": "Development regression source audit; schema 1 claim citations remain unchanged\.", "reason": "Legacy evidence catalog only; no new strict semantic selection performed\.", "relevance": "context", "selected": false\}

[https://www\.eaton\.com/content/dam/eaton/company/investor\-relations/quarterly\-earnings/filings/2026/q2/q2\-20265\-earnings\-complete\.pdf](https://www.eaton.com/content/dam/eaton/company/investor-relations/quarterly-earnings/filings/2026/q2/q2-20265-earnings-complete.pdf)

S2 · Eaton · T0 · published\_at：2026\-02\-03 · retrieved\_at：2026\-10\-31T17:23:48\.446234Z · quote：Sales for the Electrical Americas segment were a record $3\.5 billion, up 21% from the fourth quarter of 2024\. · locator：p3 Business Segment Results · origin\_id：None · origin\_basis：Unresolved in schema 1; publisher and URL are not proof of independent origin\. · evidence\_kind：document · access\_status：ok · supports：\[\] · selection：\{"priority": "background", "purpose": "Development regression source audit; schema 1 claim citations remain unchanged\.", "reason": "Legacy evidence catalog only; no new strict semantic selection performed\.", "relevance": "context", "selected": false\}

[https://www\.eaton\.com/content/dam/eaton/company/investor\-relations/quarterly\-earnings/filings/2025/q4/4Q\-2025\-earnings\-complete\.pdf](https://www.eaton.com/content/dam/eaton/company/investor-relations/quarterly-earnings/filings/2025/q4/4Q-2025-earnings-complete.pdf)

S3 · Eaton · T0 · published\_at：2026\-05\-05 · retrieved\_at：2026\-10\-31T17:21:34\.772577Z · quote：In Q1, Electrical Americas data center orders are up approximately 240% and revenue up approximately 50% versus 1Q25 demonstrating continued strong momentum in this rapid growth market\. · locator：p3 Highlights · origin\_id：None · origin\_basis：Unresolved in schema 1; publisher and URL are not proof of independent origin\. · evidence\_kind：document · access\_status：ok · supports：\[\] · selection：\{"priority": "background", "purpose": "Development regression source audit; schema 1 claim citations remain unchanged\.", "reason": "Legacy evidence catalog only; no new strict semantic selection performed\.", "relevance": "context", "selected": false\}

[https://www\.eaton\.com/content/dam/eaton/company/investor\-relations/quarterly\-earnings/filings/2026/q1/q1\-2026\-analyst\-presentation\.pdf](https://www.eaton.com/content/dam/eaton/company/investor-relations/quarterly-earnings/filings/2026/q1/q1-2026-analyst-presentation.pdf)

S5 · Eaton · T0 · published\_at：2026\-07\-31 · retrieved\_at：2026\-10\-31T17:25:18\.151337Z · quote：In Q2, Electrical Sector data center orders are up approximately 85% and revenue up approximately 65% versus 2Q25 demonstrating continued strong momentum in this rapid growth market\. · locator：p3 Highlights · origin\_id：None · origin\_basis：Unresolved in schema 1; publisher and URL are not proof of independent origin\. · evidence\_kind：document · access\_status：ok · supports：\[\] · selection：\{"priority": "background", "purpose": "Development regression source audit; schema 1 claim citations remain unchanged\.", "reason": "Legacy evidence catalog only; no new strict semantic selection performed\.", "relevance": "context", "selected": false\}

[https://www\.eaton\.com/content/dam/eaton/company/investor\-relations/quarterly\-earnings/filings/2026/q2/q2\-2026\-analyst\-presentation\.pdf](https://www.eaton.com/content/dam/eaton/company/investor-relations/quarterly-earnings/filings/2026/q2/q2-2026-analyst-presentation.pdf)

S6 · Eaton · T0 · published\_at：2026\-09\-02 · retrieved\_at：2026\-10\-31T17:24:01\.837020Z · quote：CLEVELAND – Intelligent power management company Eaton \(NYSE:ETN\) today announced a more than $242 million investment to expand its U\.S\. manufacturing footprint with a new facility in North Little Rock, Arkansas\. · locator：opening paragraph · origin\_id：None · origin\_basis：Unresolved in schema 1; publisher and URL are not proof of independent origin\. · evidence\_kind：document · access\_status：ok · supports：\[\] · selection：\{"priority": "background", "purpose": "Development regression source audit; schema 1 claim citations remain unchanged\.", "reason": "Legacy evidence catalog only; no new strict semantic selection performed\.", "relevance": "context", "selected": false\}

[https://www\.eaton\.com/us/en\-us/company/news\-insights/news\-releases/2026/eaton\-expands\-manufacturing\-for\-modular\-electrical\-enclosures\.html](https://www.eaton.com/us/en-us/company/news-insights/news-releases/2026/eaton-expands-manufacturing-for-modular-electrical-enclosures.html)

 · Eaton · T0 · published\_at：unknown

[https://www\.eaton\.com/us/en\-us/company/investor\-relations/financial\-presentations\-webcasts\.html](https://www.eaton.com/us/en-us/company/investor-relations/financial-presentations-webcasts.html)

 · Eaton · T0 · published\_at：2026\-07\-31

[https://www\.eaton\.com/content/dam/eaton/company/investor\-relations/quarterly\-earnings/filings/2026/q2/q2\-20265\-earnings\-complete\.pdf](https://www.eaton.com/content/dam/eaton/company/investor-relations/quarterly-earnings/filings/2026/q2/q2-20265-earnings-complete.pdf)

 · Eaton · T0 · published\_at：2026\-02\-03

[https://www\.eaton\.com/content/dam/eaton/company/investor\-relations/quarterly\-earnings/filings/2025/q4/4Q\-2025\-earnings\-complete\.pdf](https://www.eaton.com/content/dam/eaton/company/investor-relations/quarterly-earnings/filings/2025/q4/4Q-2025-earnings-complete.pdf)

 · Eaton · T0 · published\_at：2026\-05\-05

[https://www\.eaton\.com/content/dam/eaton/company/investor\-relations/quarterly\-earnings/filings/2026/q1/q1\-2026\-analyst\-presentation\.pdf](https://www.eaton.com/content/dam/eaton/company/investor-relations/quarterly-earnings/filings/2026/q1/q1-2026-analyst-presentation.pdf)

 · Eaton · T0 · published\_at：2026\-05\-05

[https://www\.eaton\.com/content/dam/eaton/company/investor\-relations/quarterly\-earnings/filings/2026/q1/q1\-2026\-analyst\-presentation\.pdf](https://www.eaton.com/content/dam/eaton/company/investor-relations/quarterly-earnings/filings/2026/q1/q1-2026-analyst-presentation.pdf)

 · Eaton · T0 · published\_at：2026\-07\-31

[https://www\.eaton\.com/content/dam/eaton/company/investor\-relations/quarterly\-earnings/filings/2026/q2/q2\-20265\-earnings\-complete\.pdf](https://www.eaton.com/content/dam/eaton/company/investor-relations/quarterly-earnings/filings/2026/q2/q2-20265-earnings-complete.pdf)

 · Eaton · T0 · published\_at：2026\-07\-31

[https://www\.eaton\.com/content/dam/eaton/company/investor\-relations/quarterly\-earnings/filings/2026/q2/q2\-2026\-analyst\-presentation\.pdf](https://www.eaton.com/content/dam/eaton/company/investor-relations/quarterly-earnings/filings/2026/q2/q2-2026-analyst-presentation.pdf)

 · Eaton · T0 · published\_at：2026\-05\-05

[https://www\.eaton\.com/content/dam/eaton/company/investor\-relations/quarterly\-earnings/filings/2026/q1/q1\-2026\-analyst\-presentation\.pdf](https://www.eaton.com/content/dam/eaton/company/investor-relations/quarterly-earnings/filings/2026/q1/q1-2026-analyst-presentation.pdf)

 · Eaton · T0 · published\_at：2026\-07\-31

[https://www\.eaton\.com/content/dam/eaton/company/investor\-relations/quarterly\-earnings/filings/2026/q2/q2\-2026\-analyst\-presentation\.pdf](https://www.eaton.com/content/dam/eaton/company/investor-relations/quarterly-earnings/filings/2026/q2/q2-2026-analyst-presentation.pdf)

 · Eaton · T0 · published\_at：2026\-02\-03

[https://www\.eaton\.com/content/dam/eaton/company/investor\-relations/quarterly\-earnings/filings/2025/q4/4Q\-2025\-earnings\-complete\.pdf](https://www.eaton.com/content/dam/eaton/company/investor-relations/quarterly-earnings/filings/2025/q4/4Q-2025-earnings-complete.pdf)

 · Eaton · T0 · published\_at：2026\-07\-31

[https://www\.eaton\.com/content/dam/eaton/company/investor\-relations/quarterly\-earnings/filings/2026/q2/q2\-2026\-analyst\-presentation\.pdf](https://www.eaton.com/content/dam/eaton/company/investor-relations/quarterly-earnings/filings/2026/q2/q2-2026-analyst-presentation.pdf)

 · Eaton · T0 · published\_at：2026\-02\-03

[https://www\.eaton\.com/content/dam/eaton/company/investor\-relations/quarterly\-earnings/filings/2025/q4/4Q\-2025\-earnings\-complete\.pdf](https://www.eaton.com/content/dam/eaton/company/investor-relations/quarterly-earnings/filings/2025/q4/4Q-2025-earnings-complete.pdf)

 · Eaton · T0 · published\_at：2026\-07\-31

[https://www\.eaton\.com/content/dam/eaton/company/investor\-relations/quarterly\-earnings/filings/2026/q2/q2\-20265\-earnings\-complete\.pdf](https://www.eaton.com/content/dam/eaton/company/investor-relations/quarterly-earnings/filings/2026/q2/q2-20265-earnings-complete.pdf)

 · Eaton · T0 · published\_at：2026\-07\-31

[https://www\.eaton\.com/content/dam/eaton/company/investor\-relations/quarterly\-earnings/filings/2026/q2/q2\-20265\-earnings\-complete\.pdf](https://www.eaton.com/content/dam/eaton/company/investor-relations/quarterly-earnings/filings/2026/q2/q2-20265-earnings-complete.pdf)

 · Eaton · T0 · published\_at：2026\-05\-05

[https://www\.eaton\.com/content/dam/eaton/company/investor\-relations/quarterly\-earnings/filings/2026/q1/q1\-2026\-analyst\-presentation\.pdf](https://www.eaton.com/content/dam/eaton/company/investor-relations/quarterly-earnings/filings/2026/q1/q1-2026-analyst-presentation.pdf)

 · Eaton · T0 · published\_at：2026\-07\-31

[https://www\.eaton\.com/content/dam/eaton/company/investor\-relations/quarterly\-earnings/filings/2026/q2/q2\-20265\-earnings\-complete\.pdf](https://www.eaton.com/content/dam/eaton/company/investor-relations/quarterly-earnings/filings/2026/q2/q2-20265-earnings-complete.pdf)

 · Eaton · T0 · published\_at：2026\-09\-02

[https://www\.eaton\.com/us/en\-us/company/news\-insights/news\-releases/2026/eaton\-expands\-manufacturing\-for\-modular\-electrical\-enclosures\.html](https://www.eaton.com/us/en-us/company/news-insights/news-releases/2026/eaton-expands-manufacturing-for-modular-electrical-enclosures.html)

 · Eaton · T0 · published\_at：2026\-07\-31

[https://www\.eaton\.com/content/dam/eaton/company/investor\-relations/quarterly\-earnings/filings/2026/q2/q2\-20265\-earnings\-complete\.pdf](https://www.eaton.com/content/dam/eaton/company/investor-relations/quarterly-earnings/filings/2026/q2/q2-20265-earnings-complete.pdf)

 · Eaton · T0 · published\_at：2026\-07\-31

[https://www\.eaton\.com/content/dam/eaton/company/investor\-relations/quarterly\-earnings/filings/2026/q2/q2\-2026\-analyst\-presentation\.pdf](https://www.eaton.com/content/dam/eaton/company/investor-relations/quarterly-earnings/filings/2026/q2/q2-2026-analyst-presentation.pdf)

 · Eaton · T0 · published\_at：unknown

[https://www\.eaton\.com/us/en\-us/company/investor\-relations/financial\-presentations\-webcasts\.html](https://www.eaton.com/us/en-us/company/investor-relations/financial-presentations-webcasts.html)

来源状态：\{"S1": \{"original\_status": "success", "reason": "Original retrieval record reused, no new fetch\.", "status": "ok"\}, "S2": \{"original\_status": "success", "reason": "Original retrieval record reused, no new fetch\.", "status": "ok"\}, "S3": \{"original\_status": "success", "reason": "Original retrieval record reused, no new fetch\.", "status": "ok"\}, "S4": \{"original\_status": "success", "reason": "Original retrieval record reused, no new fetch\.", "status": "ok"\}, "S5": \{"original\_status": "success", "reason": "Original retrieval record reused, no new fetch\.", "status": "ok"\}, "S6": \{"original\_status": "success", "reason": "Original retrieval record reused, no new fetch\.", "status": "ok"\}, "regression\_external\_retrieval": \{"reason": "开发回归样本（dev sample，非 heldout）。仅将原冻结材料转换为 schema 2 报告；保留原 as\_of，无新增检索、事实、引语、计算或研究判断。claims 保留原 schema 1，本次结构校验及开发归档不等于 strict schema 2 claims 验证，也不提供严格历史可得性证明。", "status": "not\_run"\}\}
