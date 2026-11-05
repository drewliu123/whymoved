# 研究价值、机会排序与前瞻复盘

## 研究应增加什么

交易相关研究按以下优先级形成判断：市场在押注什么、我们的分歧、证据优势、催化及时间、价格变化后剩余空间与做错代价。先给结论，再解释关键连接；减少防御性写作不等于放松证据要求。非交易问题按原问题给有用答案，不强制估值、机会排序或精确概率。

研究增量可以来自同口径计算、跨材料连接、矛盾定位、传导断点、预期修订或判断更新。链接多、来源热度高、新闻新不自动构成优势。说清相对哪一基准增加了什么，为什么会改变方向、强弱、时点或研究优先级；低热度但可核实的交付、订单、规则和数据细节可以比热门观点更重要。优势必须解释证据如何区分竞争解释，不能只声称“市场忽视”。

市场基准区分调查共识、价格隐含与研究者proxy估计。proxy需说明代理对象、范围、截点、推导链及局限，将重要推断入inference claims并以basis连接证据；写“据这些代理线索推断……”，不能写成已观测到的全市场共识。社区样本、单一机构、公司指引均不能自动代表市场。方向判断和空间讨论不强制精确概率。

## 可选 report.opportunity v1

这是供主流程实现和校验的可选扩展契约，不替代report.analysis，也不表示既有脚本已自动验证、渲染或归档其全部语义。旧报告无此对象仍兼容；不得为补新字段改写旧run。采用时严格按以下形状，文字均为非空字符串，claim_ids均为非空、无重复且引用本轮claims中真实存在的主张；重要推断本身入账，不能只引用几个事实后在对象文字中新增未入账结论。

非交易问题采用以下完整对象，不生成market_view、variant、edge、catalyst、payoff、assessment或triggers等机会字段：

```json
{"version": 1, "applicability": "not_applicable", "reason": "本轮只核对公开承诺的兑现，不研究交易机会。"}
```

交易研究采用以下字段契约。表中点号表示嵌套路径，非新增的点号键名：

| 字段 | 必填内容与含义 |
|---|---|
| version | 整数1 |
| applicability | trading |
| market_view | {text, basis, claim_ids}；basis仅consensus / price_implied / proxy，text交代市场押注对象、期间与依据；consensus及price_implied仍满足既有来源与主张资格 |
| variant | {text, claim_ids}；研究判断与市场基准的具体分歧；没有实质分歧时如实写明 |
| edge | {text, claim_ids}；计算、连接、矛盾或可核实线索如何构成证据优势；没有优势则明确承认 |
| catalyst | {text, by, claim_ids}；什么可观察事件会检验分歧，by为带时区日期/时间或明确可判定的事件窗口，不写“未来关注” |
| payoff | {text, claim_ids}；价格已走过多少、还剩什么空间、判断做错的损失路径/成本；缺可靠数字可定性说明方向、约束及未知，不编收益率、目标价或损失数字 |
| assessment | {status, text, claim_ids}；status仅research_now / watch / priced_in / no_edge；text解释排序理由与条件 |
| triggers | 非空列表；每项{id, signal, by, claim_ids, supports_if, weakens_if, invalidates_if}；id本轮唯一且稳定，其他文字非空，signal可核实，by明确检查窗口或到期条件；支持、削弱、失效条件可区分，不能只有“持续关注” |

market_view.basis约束引用类型：proxy必须至少引用一条inference，consensus必须至少引用一条consensus，price_implied必须同时包含price与inference；可混合引用更多相关claims，但不能仅改basis名称绕过来源资格。

四种assessment是研究优先级与机会判断，不是个人仓位或机械交易指令：

- research_now：证据与分歧使近期研究值得投入，说明为什么是现在、最近的催化以及需要解决的关键问题；不代表立即买卖或已确认错价。
- watch：条件尚未成熟，明确等待什么、何时检查，不能无限期挂起。
- priced_in：有据判断相关变化已大体进入价格，说明已经兑现的部分与余下空间为何有限；缺市场数据不能据此宣称已定价。
- no_edge：当前没有可辩护的分歧或证据优势，或空间与做错代价不支持优先研究，说明原因；不能把“未检索”冒充无优势的实证结论。

多个候选要给出有理由的研究优先顺序，综合证据质量、催化距离、剩余空间与失败代价，不制造客观分数；单一对象只需明确状态及理由。

### 与严格市场评估的边界

`report.analysis.market`的现有约束完全不变。price_relevance=true时，缺价格或可靠隐含预期证据仍须status=missing，写具体reason，claim_ids / model_ids为空；assessed仍需带时刻price主张、四项预期比较与关联模型输出，valuation仍需匹配reverse_dcf。不能用proxy、社区观点、机会对象或文字改名填补assessed所需输入。

在market=missing时，可以在opportunity中用basis=proxy及有据inference表达条件倾向，交代它依赖什么、尚未证明什么；不能称为已核实共识、已验证错价或已被定价。机会状态不等于market状态，不能由research_now反推assessed，也不能仅因missing自动抹掉所有有据研究判断。重要缺口紧贴它限制的判断说明一次。

## 触发更新与可选 report.update.opportunity

更新由旧触发条件、关键新证据或显著价格变化驱动，不靠换日期重复发布。先读parent run的冻结机会、触发、claims与截点；新run保留旧触发的原文与窗口在旧run，不修改过去的signal、门槛或by来迎合结果。当前需要的新触发放入新run.opportunity，沿用同一检验时保留id，不同含义用新id。

父run为trading时，新run必须保留trading opportunity及update.opportunity，不得静默丢弃；优势消失可降为no_edge并说明。其他没有交易机会基准的更新不强填该对象。更新对象所有字段均必填：

| 字段 | 内容 |
|---|---|
| previous_status | 旧run的assessment.status原值 |
| current_status | 新run的assessment.status原值 |
| thesis_change | strengthened / weakened / unchanged / invalidated |
| reason | 非空；新证据如何改变方向、强弱或时点，重要推断入本轮claims |
| price_move | 非空；旧截点至当前截点的实际价格变化、证券/选项、起止与口径；缺资料明确未取得，不能当零变化或凭方向猜幅度 |
| remaining_edge | 非空；在已经发生的价格变化后还剩什么研究优势/空间，以及做错的代价；可定性但须有据 |
| claim_ids | 非空、无重复的本轮主张引用，支撑reason / price_move / remaining_edge；重要判断以inference及basis入账，缺价格时引用说明缺口及其影响的有据推断，不编造price主张 |
| trigger_results | 列表，旧run全部triggers各恰好出现一次，不遗漏、不混入新触发；每项{trigger_id, status, observation, claim_ids} |

trigger_results.trigger_id对应旧run稳定id；status仅hit / not_hit / not_checked；observation非空，说明观察、检查时点、来源或未检查原因。claim_ids引用本轮已有claims，hit / not_hit须非空且有支持观察的证据；not_checked可为空，不能仅因没查到就写not_hit。hit表示原signal满足，支持/削弱/失效须再按原条件解释；not_hit只描述已核查窗口内未满足，不代表永久不会发生。到期且尚未检查仍写not_checked，不能宣称已失败。没有旧机会/触发时不伪造previous_status或结果；建立本轮新基准并说明无法作此比较。父run未采用trading时不强填交易更新对象。

可选`report.update.opportunity.review={direction,magnitude,timing,mechanism,price_realization}`。若提供，五项均须非空文本，依据冻结前瞻分别说明方向、幅度、时点、机制与价格兑现；区分未到期、已观察、未核实，不把研究复盘冒充自动交易收益验收。

可用`python3 "$TY_DIR/scripts/opportunities.py" list --home <数据根目录>`只读列出归档中的状态与触发；--home可省略，沿用TOUYAN_HOME或默认数据目录，--history包含旧版本。默认只列每条更新链最新记录，有分支则分别保留；同一状态内不按主观优势打分。这是读取冻结档案，不是后台监控或自动核实信号；not_checked不会因列出而变成已检查。

机制证据增强与机会优先级下降可以同时成立：价格已提前兑现可能压缩空间；反之价格下跌也不自动证明研究错误。正文同时交代方向/强弱变化和已经发生的价格变化，详情留附录。

## 前瞻冻结与复盘

普通研究可在现有plan、claims、report及不可覆盖run中冻结定性前瞻，不必启动旧概率账本。事前写清方向、幅度或有依据的定性范围、时点/事件窗口、基准及观察口径、机制链、催化、失效与到期条件；未知写未知，不用精确概率或任意数字制造可评分感。正式可裁决预测与概率评分仍按legacy-forecast.md，不混用字段或宣称已完成概率登记。

复盘读取当时冻结记录，分别比较方向、幅度、时点。机制是否兑现与价格是否兑现分别判断：业务判断正确但价格已反映、方向对但幅度/时点错、价格上涨但原机制未发生，都应按原记录报告。到期未触发、已失效、未检查分开说明；新解释记为新run推断，不事后重写原判断、触发或基准，不把同方向行情直接算成机制命中。

## 正文与审查

机会判断自然嵌入开头的结论、驱动解释和后续观察。正文给市场押注、分歧、关键证据、催化、剩余空间/失败代价中与当前问题有关的内容，契约详情和逐触发结果放附录，不变成机械八栏目或反复免责声明。

red-team以独立value_checks检查分歧证据、催化时点、价格空间、机会排序、失败后果与触发，以及更新/复盘纪律，不与analysis_checks混合。修正目标是让判断更明确、更可检验；不能把状态一律降为watch、添加更多限制或要求伪精确概率当作审查通过。
