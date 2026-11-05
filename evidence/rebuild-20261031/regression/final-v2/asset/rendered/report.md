# 【开发回归样本】NVDA回撤之后，先分清增长与现金

英伟达10月跌了多少，为什么跌，业务变化怎样验证？

研究截点 2026\-10\-31T17:14:08Z · asset · 资产变化与业务验证：复用冻结证据的开发回归

证据模式：旧版 schema 1；本报告未按 schema 2 的来源与证据契约校验。

## 判断

10月价格收益为−10\.39%，月内最高收盘至月末回撤−14\.46%。业务原指引仍支持收入与示例毛利额扩张；最后一天的板块抛售有AI投入回报担忧的媒体解释，现有材料仍不能排序整月主因。现金回收是下一步核查线索。 [C1] [C2] [C9] [C7]

重要限制：开发回归样本（dev sample，非 heldout）。仅将原冻结材料转换为 schema 2 报告；保留原 as\_of，无新增检索、事实、引语、计算或研究判断。claims 保留原 schema 1，本次结构校验及开发归档不等于 strict schema 2 claims 验证，也不提供严格历史可得性证明。 

重要限制：本例复用先前冻结材料，没有新增近期检索；不能称为重新完成最新研究。 

重要限制：缺少全月基准行情、同期一致预期与估值，不能排序整月下跌原因。 

重要限制：财务数据为8月披露；未确认10月订单、客户ROI和业务现状。 

## 月跌幅与高点回撤是两件事

10月价格收益 −10\.39%；最高收盘至月末 −14\.46%；最后一日 −4\.22%。先涨后跌，不能用高点回撤替代整月收益。 [C1] [C2]

为什么重要：整月收益、高点回撤和单日下跌具有不同基准，混用会夸大或误读实际变化。

相较基线：原 report\.json 的同名 finding 与原 claims\.json（C1, C2）；开发样本复用。

研究增量（connection）：仅把原结论与其验证意义重新连接：整月收益、高点回撤和单日下跌具有不同基准，混用会夸大或误读实际变化。 本轮无新事实、计算或判断更新，非相对原研究的新发现。

## 毛利率下降，毛利额仍可能增长

收入指引中点环比约 \+12\.24%，毛利率从75%到74%；两项中点隐含毛利额仍增约 10\.78%。关键是增长的规模和质量，不能只看利润率方向。 [C3] [C4] [C7]

为什么重要：利润率方向不能代替利润额；收入规模与毛利额共同决定原指引的业务含义。

相较基线：原 report\.json 的同名 finding 与原 claims\.json（C3, C4, C7）；开发样本复用。

研究增量（connection）：仅把原结论与其验证意义重新连接：利润率方向不能代替利润额；收入规模与毛利额共同决定原指引的业务含义。 本轮无新事实、计算或判断更新，非相对原研究的新发现。

## 现金回收提供后续核查线索

Q2经营现金流/收入约25\.02%，Q1约61\.68%；Q2应收变动占用223\.46亿美元。它提示核查营运资本，尚不能诊断坏账或10月订单。 [C6] [C8]

为什么重要：营运资本占用提供后续核查线索，但不足以诊断坏账或推断当月订单。

相较基线：原 report\.json 的同名 finding 与原 claims\.json（C6, C8）；开发样本复用。

研究增量（connection）：仅把原结论与其验证意义重新连接：营运资本占用提供后续核查线索，但不足以诊断坏账或推断当月订单。 本轮无新事实、计算或判断更新，非相对原研究的新发现。

### 同口径看增长与现金

| 指标 | Q1 FY27 | Q2 FY27 | Q3原指引／中点示例 |
| --- | --- | --- | --- |
| 收入（十亿美元） | 81\.615 | 96\.221 | 108 ±2% |
| 毛利率 | 74\.9% | 75\.0% | 74\.0% ±0\.5个百分点 |
| 毛利额（十亿美元） | 未在本例计算 | 72\.142（GAAP披露） | 示例79\.92 |
| 经营现金流（十亿美元） | 50\.344（由半年减Q2） | 24\.077 | 未预测 |
| 经营现金流/收入 | 约61\.68% | 约25\.02% | 未预测 |

[C3] [C4] [C6] [C7] [C8]

 开发转换：引用经原 claims\.json 核对；仅提供原研究表格的结论级关联。

### 原 claims 内联来源目录（未新增取证）

| 原来源ID | 发布方 | 层级 | 发布时间（原记录） | URL | 所引用结论 |
| --- | --- | --- | --- | --- | --- |
| S2 | NVIDIA IR / Q4 historical quote service | T0 | 2026\-10\-30 | https://investor\.nvidia\.com/stock\-info/historical\-price\-lookup/default\.aspx | C1, C2 |
| S1 | NVIDIA | T0 | 2026\-08\-26 | https://nvidianews\.nvidia\.com/news/nvidia\-announces\-financial\-results\-for\-second\-quarter\-fiscal\-2027 | C3, C4, C6 |
| S3 | Reuters via AOL | T2 | 2026\-10\-30T20:23:00Z | https://www\.aol\.co\.uk/articles/nasdaq\-futures\-tumble\-amazon\-intel\-084615000\.html | C5 |

[C1] [C2] [C3] [C4] [C6] [C5]

按原内联来源 URL 关联原 sources\.json；来源目录不证明 quote、历史可得性或独立性，缺失项不补造。

### NVDA日收盘价（美元）（原序列转表，无新计算）

| date | close | high |
| --- | --- | --- |
| 2026\-09\-30 | 228\.38 | — |
| 2026\-10\-01 | 230\.86 | 232\.29 |
| 2026\-10\-02 | 233\.95 | 237\.88 |
| 2026\-10\-05 | 238\.9 | 240\.1 |
| 2026\-10\-06 | 239\.24 | 243\.37 |
| 2026\-10\-07 | 237\.47 | 239\.08 |
| 2026\-10\-08 | 230\.48 | 237\.07 |
| 2026\-10\-09 | 229\.28 | 233\.92 |
| 2026\-10\-12 | 226\.32 | 228\.86 |
| 2026\-10\-13 | 228\.52 | 228\.64 |
| 2026\-10\-14 | 221\.3 | 226 |
| 2026\-10\-15 | 217\.23 | 218\.47 |
| 2026\-10\-16 | 214\.13 | 218\.68 |
| 2026\-10\-19 | 217\.09 | 219\.62 |
| 2026\-10\-20 | 216\.47 | 218\.46 |
| 2026\-10\-21 | 221\.97 | 222\.19 |
| 2026\-10\-22 | 212\.21 | 218\.88 |
| 2026\-10\-23 | 210\.96 | 213\.85 |
| 2026\-10\-26 | 216 | 217\.75 |
| 2026\-10\-27 | 217\.94 | 219\.19 |
| 2026\-10\-28 | 215\.38 | 219\.99 |
| 2026\-10\-29 | 213\.66 | 215\.33 |
| 2026\-10\-30 | 204\.64 | 209\.06 |

[C1] [C2]

原日收盘与盘中 high 字段原值保留，未重画或改造数据。

## 其他解释

### 担忧未必变成近期订单下滑

客户回报疑虑可以与继续采购并存；板块共同重估也可能解释部分回撤；兑现原指引，仍可能不足以满足更高预期。区分这些路径，需要行业比较、同期预期与后续披露。 [C10]

## 接下来观察什么

### 下一季收入、后续指引与毛利额

检验扩张是否兑现；原指引收入区间1058\.4—1101\.6亿美元。 [C4] [C7] [C11]

### 应收、经营现金流及现金转化

区分交付扩张的资金占用与持续回收压力。 [C6] [C8] [C11]

## 其他限制

原表述中 calculations\.json、independent\-freeze\.json、inputs/、raw/ 等相对路径均指原样本目录；本包 legacy\-calculations\.json 仅为旧计算审计副本，未新做公式或算术认证。 

## 来源与结论审计

\[C1\] NVDA最近已收盘日为2026\-10\-30，收204\.64美元；9月30日228\.38美元，10月价格累计变化\-10\.39%（204\.64/228\.38\-1）；10月23日210\.96美元，最后一周\-3\.00%；10月29日213\.66美元，最后一天\-4\.22%。均为收盘价格收益，不含股息。（price；2026\-10\-31T17:14:08Z）

依据：；来源：https://investor\.nvidia\.com/stock\-info/historical\-price\-lookup/default\.aspx

\[C2\] 完整10月日行情中最高盘中价为10月6日243\.37美元，至月末回撤15\.91%；该日239\.24美元也是月内最高收盘价，至月末收盘回撤14\.46%。10月先涨后跌，不能把高点回撤当作整月跌幅。（price；2026\-10\-31T17:14:08Z）

依据：；来源：https://investor\.nvidia\.com/stock\-info/historical\-price\-lookup/default\.aspx

\[C3\] NVIDIA 8月26日公布FY2027 Q2（截至7月26日）：总收入962\.21亿美元，环比18%、同比106%；数据中心收入890亿美元，环比18%、同比117%；GAAP和non\-GAAP毛利率均75\.0%。这是本轮已取得的季度财务基准，不能据此声称10月经营现状已确认。 同份财报直接披露GAAP毛利额721\.42亿美元。（fact；2026\-10\-31T17:14:08Z）

依据：；来源：https://nvidianews\.nvidia\.com/news/nvidia\-announces\-financial\-results\-for\-second\-quarter\-fiscal\-2027

\[C4\] 同一官方财报给FY2027 Q3总收入指引1080亿美元±2%，不假设来自中国的数据中心计算收入；GAAP和non\-GAAP毛利率指引均74\.0%±50基点。指引是管理层预期，不是已实现收入。（fact；2026\-10\-31T17:14:08Z）

依据：；来源：https://nvidianews\.nvidia\.com/news/nvidia\-announces\-financial\-results\-for\-second\-quarter\-fiscal\-2027

\[C5\] Reuters 10月30日收盘报道把科技股抛售联系到Amazon和Intel季报失望及AI巨额投入回报担忧，并记录NVDA当日跌4\.2%；Wealthspire的Oliver Pursche表示本周焦点是AI何时取得正回报。这里只保留该媒体及受访者归因，不外推为整月已证实因果。（view；2026\-10\-31T17:14:08Z）

依据：；来源：https://www\.aol\.co\.uk/articles/nasdaq\-futures\-tumble\-amazon\-intel\-084615000\.html

\[C6\] FY2027 Q2经营现金流240\.77亿美元，半年累计744\.21亿美元；Q2应收账款变动占用现金223\.46亿美元。（fact；2026\-10\-31T17:14:08Z）

依据：；来源：https://nvidianews\.nvidia\.com/news/nvidia\-announces\-financial\-results\-for\-second\-quarter\-fiscal\-2027

\[C7\] Q3收入指引中点较Q2高约12\.24%；以两项指引中点相乘，Q3示例毛利额799\.2亿美元，Q2直接披露GAAP毛利额721\.42亿美元，增约10\.78%。这不是已实现利润，也不是股价回报预测。（inference；2026\-10\-31T17:14:08Z）

依据：C3, C4；来源：

\[C8\] Q2经营现金流/收入约25\.02%；从半年减Q2得到Q1经营现金流503\.44亿美元，同期收入816\.15亿美元，该比值约61\.68%。单季变动受营运资本及其他现金流项目影响，应收占用不等于坏账。（inference；2026\-10\-31T17:14:08Z）

依据：C3, C6；来源：

\[C9\] 这批材料更适合检验增长兑现、利润和现金回收的质量，尚不足以把10月跌幅判定为订单恶化。最后交易日的AI投入回报担忧有媒体归因支持，全月相对表现、估值与预期修订仍缺资料，不能识别整月主因。（inference；2026\-10\-31T17:14:08Z）

依据：C1, C2, C3, C4, C5, C6；来源：

\[C10\] 最强反方是客户投入回报担忧可能不影响近期GPU采购，收入与毛利额仍能扩张；板块共同重估也可能解释部分回撤，不能只寻找公司特有原因。另一种路径是公司兑现原指引但低于股票隐含要求；区分这些解释需要冻结时点的行业比较、一致预期与估值。（inference；2026\-10\-31T17:14:08Z）

依据：C3, C4, C5, C7；来源：

\[C11\] 下一次应同口径检查收入对原指引区间的兑现、后续指引、毛利额和现金回收，而不能以单个季度现金流变化直接认定需求失效。（inference；2026\-10\-31T17:14:08Z）

依据：C3, C4, C6, C7, C8；来源：

 · NVIDIA IR / Q4 historical quote service · T0 · published\_at：2026\-10\-30

[https://investor\.nvidia\.com/stock\-info/historical\-price\-lookup/default\.aspx](https://investor.nvidia.com/stock-info/historical-price-lookup/default.aspx)

 · NVIDIA IR / Q4 historical quote service · T0 · published\_at：2026\-10\-30

[https://investor\.nvidia\.com/stock\-info/historical\-price\-lookup/default\.aspx](https://investor.nvidia.com/stock-info/historical-price-lookup/default.aspx)

 · NVIDIA · T0 · published\_at：2026\-08\-26

[https://nvidianews\.nvidia\.com/news/nvidia\-announces\-financial\-results\-for\-second\-quarter\-fiscal\-2027](https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-second-quarter-fiscal-2027)

 · NVIDIA · T0 · published\_at：2026\-08\-26

[https://nvidianews\.nvidia\.com/news/nvidia\-announces\-financial\-results\-for\-second\-quarter\-fiscal\-2027](https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-second-quarter-fiscal-2027)

 · Reuters via AOL · T2 · published\_at：2026\-10\-30T20:23:00Z

[https://www\.aol\.co\.uk/articles/nasdaq\-futures\-tumble\-amazon\-intel\-084615000\.html](https://www.aol.co.uk/articles/nasdaq-futures-tumble-amazon-intel-084615000.html)

 · NVIDIA · T0 · published\_at：2026\-08\-26

[https://nvidianews\.nvidia\.com/news/nvidia\-announces\-financial\-results\-for\-second\-quarter\-fiscal\-2027](https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-second-quarter-fiscal-2027)
