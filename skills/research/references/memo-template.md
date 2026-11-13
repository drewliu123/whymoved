# 研究报告：先给判断，再展示增量

首段直接回答问题；接着选择最重要发现，解释机制/计算和用户为什么应关注。每项发现要说清相对什么基准多知道了什么，不按材料来源依次复述。最强竞争解释与下一观察接近相关判断。重大限制必须可见，其余放在对应数字/证据旁。没有统一免责声明段落或强制多空篇幅配比。

报告的研究价值由答案和增量决定，字段齐全只是交付条件。不同问题可有不同篇幅，不强制三发现、三假设、三图表。

## 默认正文：专业简明的研究短评

与主SKILL的默认表达一致，面向感兴趣但不预设金融背景的读者。先给当前判断及时间范围，用必要数据定位变化，解释主要驱动及传导机制，再指出会改变判断的观察。结构服务于问题，不机械填满栏目。简单问题几段讲清；复杂问题才展开多层原因和情景比较。用户要求其他深度或风格时覆盖默认。

背景按[context.md](context.md)取舍：正文在解释主要驱动时嵌入必要的长期条件与近期环境，并说明新增信息相对事前预期改变了什么；五层研究顺序留在底稿，不变成五个固定栏目。持续条件解释敏感性，新增变化解释时点，同一传导链不重复计贡献。

“发生了什么”与“为什么”要连接：财报/政策/价格变化如何进入盈利、现金流或估值，哪一部分已有证据、哪一部分是推断。保留必要专业术语，首次出现解释它在本题的含义；不堆术语，也不用过度口语的比喻代替机制。资产下跌先给指数/资产、明确期间、实际跌幅和同期基准；预测问题先给有依据的倾向和条件，不虚构概率。

研究增量是作者组织分析的要求。聊天正文用具体发现讲出增量，不展示increment.kind、基线字段、T层级或校验流程。完整报告的字段与证据仍照下述契约保存；聊天从同一冻结内容提炼，不新增结论。关键缺口在相关判断旁简短交代，执行日志与工具失败留在审计中，除非直接影响答案。

## 正文与证据附录

聊天短评、Markdown与HTML正文遵循同一写作原则：判断在前，关键事实与机制解释随后，下一项有区分力的观察收尾。证据与过程完整保存，不要求正文逐项展示研究底稿。

- 只有影响结论强度、适用范围或下一步判断的缺口进入正文，就近说明一次。重大缺口紧贴主判断，不连续堆放多段“重要限制”。
- 不在不同栏目重复“尚未证实”“不能排除”“不能据此”。尽量用“观察到什么会支持或削弱当前解释”表达不确定性，必要限定仍须保留。
- 正文呈现关键计算结果及经济含义；输入明细、公式、来源资格、主张编号、校验与审查记录放在附录或审计记录。“相较基线”“研究增量”字段用于组织分析，不直接作为正文标签。
- 没有新发现时，简短说明复核范围与判断未变的原因；不复制旧发现凑篇幅，不用长篇过程说明填充。
- 不为减少重复而隐去足以改变判断的风险，不通过删限定提高结论的确定性，不为改变显示顺序将实质重大缺口标成非重大。交付前检查生成后的正文，识别重复限制和无增量段落。

## report.json v2

以下虚构示例只说明原有报告正文契约，未联网取证，不能单独用于新归档；新归档还须合并后述analysis及对应plan、claims、sources：

```json
{
  "schema_version": 2,
  "title": "收入兑现的关键转到交付与成本",
  "question": "示例公司的订单是否已经转成利润？",
  "type": "theme", "task": "机制研究", "as_of": "2026-10-31T18:00:00Z",
  "answer": {"text": "已披露收入可以核实，利润兑现需要配对成本。", "claim_ids": ["C1", "C2"]},
  "findings": [{
    "title": "收入与利润之间还差成本桥", "text": "具体连接与计算写在这里。",
    "claim_ids": ["C1", "C2"], "why_it_matters": "决定下一次披露应优先核查什么。",
    "increment": {"kind": "connection", "baseline": "原披露只给收入", "detail": "连接交付与利润核查所需输入"}
  }],
  "alternatives": [{"title": "竞争解释", "text": "价格与组合也可能解释变化。", "claim_ids": ["C2"]}],
  "watch": [{"signal": "下一季度同口径成本桥", "meaning": "成本变化决定利润是否兑现。", "claim_ids": ["C2"]}],
  "limitations": [{"text": "当前没有配对成本数据。", "material": true, "claim_ids": ["C2"]}],
  "tables": [{"title": "已披露基数", "columns": ["指标", "百万美元"], "rows": [["季度收入", 100]], "claim_ids": ["C1"], "note": "示例数据"}]
}
```

increment.kind可为new_fact/calculation/connection/contradiction/judgment_update。baseline是具体原文、比较基准或旧判断，不写“以前不知道”。detail解释实际增加的关系；标签不能替代证明。

findings为空时必须给no_change_reason，说明本轮检查了哪些信号、为何未改变判断。answer仍需证据引用。所有重要分析通过claim_ids入账。

可选chart：`{title,x_label,y_label,unit,rows:[{label,value}],claim_ids,note}`。value必须有限数值，口径相同、时间顺序明确；图表依数据需要选用。多序列改用`series:[{name,rows:[{label,value}]}]`替代`rows`：各序列的label必须完全一致（同一横轴），unit共享，渲染时以实线/虚线区分并在图下列出系列名；单序列仍保留原有悬停读数，多序列的精确数值以同源数据表为准。`rows`与`series`不能同时出现。需要多张图时用`charts:[...]`（每个元素与`chart`同构，单序列或多序列均可），`chart`与`charts`不能同时出现；每张图仍自动附同源数据表。可选`kind`：`line`（默认）/`bar`/`waterfall`。`bar`与`waterfall`只能用`rows`，不能带`series`。`waterfall`每行必须有`role`（`total`或`delta`），首行必须是`total`；后续`total`必须等于前面累计值，否则校验失败——这让利润桥、现金流桥自己检查算术。渲染时合计与变动用不同填充与线型区分，表格标签自动补「合计/变动」。渲染器附同源数据表、键盘读数、明暗/移动布局。不要双轴混量纲，不以图形暗示不存在的因果。

可选calculations列表：`{id,description,formula,inputs:[{name,value,unit,claim_ids}],result:{value,unit,precision?},claim_ids,op?}`；对应claim可标calculation_id。

行带`op`时由固定算子重算，并与冻结result比对，不一致即校验失败。白名单只有六个算子，输入顺序固定：

| op | 计算 | 输入要求 | 结果unit |
|---|---|---|---|
| ratio | a / b | 两个同unit | ratio |
| growth | a / b − 1 | 两个同unit | ratio |
| cagr | (a / b)^(1/years) − 1 | end、begin同unit，years为year | ratio |
| difference | a − b | 两个同unit | 同输入unit |
| sum | a + b + … | 全部同unit | 同输入unit |
| product | a × b × … | 恰好一个非ratio输入 | 该非ratio输入的unit |

输入可用`value`（须带claim_ids）或`ref`引用更早的计算id（最多两层引用链，不能前向或自引用）；`ref`解析到被引用行**记录**的result值而非未舍入的内部值，读者按文档中可见数字即可复现整条链；`precision`（0–12）允许记录舍入后的结果。未标`op`的行仍是可读公式记录，只检查结构、单位与引用，不执行来源文本，渲染时不标「已重算」。两者都不能替代analysis.models的固定模型；真实计算命令和退出码另存evidence。

虚构示例（C1–C3只示意引用）：

```json
{
  "id": "A1", "description": "虚构收入同比", "formula": "(now/base-1)",
  "op": "growth", "claim_ids": ["C1"],
  "inputs": [
    {"name": "now", "value": 120, "unit": "USD", "claim_ids": ["C1"]},
    {"name": "base", "value": 100, "unit": "USD", "claim_ids": ["C2"]}
  ],
  "result": {"value": 0.2, "unit": "ratio"}
}
```

不要在unit里塞第二个结果或口径说明：unit只写单位，推导过程写description/formula/新增行。

## 数值事实：可选 claim.metric

数值不只写在文本里。fact / price / consensus 主张可加`metric`块：`{name, value, unit, period_type, period_start, period_end, entity?, scope?, currency?, scale?, basis?, locator?, comparison_with?}`。period_type为fy / quarter / ytd / ltm / instant；除instant外period_start必填。显式比较用`comparison_with`，双方unit / currency / scale / period_type必须一致，gaap与adjusted不得混比；同一entity + name + scope + period_type组内口径必须一致。metric只允许出现在fact / price / consensus上，进入附录「数值事实」表。完整字段与规则见[evidence.md](evidence.md)。

没有metric的旧账本继续合法，渲染结果不变；不要为了填字段把区间、估算或未经核对的数字写成精确值。

## 一致预期：可选 claim.consensus / claim.guidance

consensus主张可带`consensus`块（series_id、metric、target_period、provider、sample_size、median、low、high），同一series_id与target_period的多个截点用于计算修订；fact主张可带`guidance`块（metric、target_period、midpoint、可选low/high）。指引不能冒充共识：`guidance`放在consensus上会被拒绝。附录渲染「一致预期序列」与「公司指引（不是分析师共识）」。详见[evidence.md](evidence.md)与[expectations.md](expectations.md)。

## 事件研究：可选 report.event_study

需要历史类比时，可把 event_study 的输入文档（event / window / samples）放进 `report.event_study`，随报告一起归档。校验复用 `event_study.validate_document`，核对样本 `claim_ids` 是否存在，并要求至少两条可用样本；渲染在附录生成「事件研究」小节——参考类收益分布（n、中位、均值、四分位、正为比例）与样本明细，并注明「绝对收益、样本事前选定、不给 p 值」。

字段与独立运行完全一致；没有该字段的报告渲染不变。

## 盈利质量：可选 report.quality

两期以上报表可把质量筛查嵌进报告：`report.quality = {statements, thresholds?}`。`statements` 与[financial-quality.md](financial-quality.md)的输入完全一致（字段值可为裸数字或`{value, claim_ids}`）；`thresholds`可覆盖默认阈值（键名必须是已知阈值，取值在(0,1]）。

校验会检查报表结构与各字段的 `claim_ids` 是否存在；渲染在附录生成「盈利质量」小节：关键指标表（利润率、现金转化、应计、周转、资本开支、SBC、ROIC）、环比变化表、红旗清单。指标在校验/渲染时由嵌入输入重新计算，不是冻结的结论；没有该字段的报告渲染不变。

## 行业传导：可选 report.transmission

主题研究可把传导图直接嵌进报告：`report.transmission` 的字段与[transmission.md](transmission.md)的输入完全一致（nodes / edges / bottleneck）。校验会用账本核对各节点、边与瓶颈的 `claim_ids` 是否存在；渲染在附录生成「行业传导」小节：瓶颈与理由、节点表（节点、标签、方向、可观察指标）、传导路径与告警。没有该字段的报告渲染不变。

不要为了填字段硬造节点：`observables` 必须是能核对的观察，`lag` 必须是时间窗口或触发条件。

## 来源冲突：可选 report.conflicts

同一指标多个来源给出不同数值时，不要悄悄挑一个。用可选`conflicts`记录取舍：

```json
{"conflicts": [{
  "metric": "Q3 收入", "unit": "million USD",
  "candidates": [{"source_id": "S1", "value": 120}, {"source_id": "S2", "value": 118}],
  "adopted_claim_id": "C3",
  "rule": "以公司原始披露为准", "reason": "第二来源为转引且与原始披露不一致"}]}
```

规则：`candidates`至少两条且数值必须不同；`source_id`须存在于sources；`adopted_claim_id`须是fact / price / consensus主张；`unit`统一，若采用主张带`metric`，其unit须一致、value须等于某个候选值。渲染在附录「来源冲突与取舍」表。没有该字段的报告渲染不变。不要用它表演严谨：只有真实分歧才记录。

## 估值汇总：只读模型输出

多个估值方法并存时，用可选`valuation_summary`把它们并排成一张表。**这一节不允许写任何数字**：每行只能引用`model_id`与`metric`，渲染时从冻结的模型结果读取，避免手抄、事后改数与口径混用。

```json
{
  "rows": [
    {"model_id": "M2", "label": "DCF 基准情形", "metric": "per_share"},
    {"model_id": "M3", "label": "可比公司倍数", "metric": "per_share"},
    {"model_id": "M1", "label": "反向DCF隐含增长", "metric": "implied_growth"}
  ],
  "note": "不同方法的区间口径不同，不能直接相加。"
}
```

规则：`rows`非空、`model_id`唯一且必须在`analysis.models`中；`metric`须匹配模型种类（dcf / relative_valuation → per_share，reverse_dcf → implied_growth）；所有模型引用的带时刻价格必须一致，否则无法比较相对现价；`note`可选文本。渲染列为方法 / 指标 / 低 / 中 / 高 / 单位 / 中位相对现价，并注明「不跨方法加权、不给概率、不是目标价；反向DCF一行是预期不是估值」。没有该字段的报告渲染结果不变。

不要用它制造「综合目标价」：表格是方法对照，不是加权结论。

## analysis：底稿完整，正文简明

新报告须有`analysis.version: 1`，完整plan/analysis示例与模型精确字段见[analysis-methods.md](analysis-methods.md)。不要把本节逐条展开为正文栏目；正文呈现判断、机制、关键结果及相关缺口，预测矩阵、输入/假设和敏感性放证据附录。

- `question_kind / method / price_relevance / baseline / mechanism_chain`与plan.research_design一致，`hypotheses`按顺序复制plan的`{id, explanation}`。`baseline_claim_ids`及`conclusion_claim_ids`引用实际基准和结论证据，`conclusion`写当前判断。
- `tests`覆盖全部计划检验，各出现一次，id和outcomes逐项不变。每项有status（observed / missing）、claim_ids、interpretation、supports / weakens（H id）、next_observation、by、supports_if、weakens_if。observed至少引用一条fact / price / consensus，不能仅有view或inference；missing写gap_reason，claim_ids / supports / weakens均为空，不能用未找到证据支持或削弱解释。
- `models`每项有id / description / currency / scale / period / scope / assumptions / spec / result / output_claim_ids。spec只用六种固定compute_model：operating_bridge、free_cash_flow、dcf、reverse_dcf、relative_valuation、driver_build。全部输入分observed与assumption，后者在wrapper.assumptions逐输入说明理由；可选`period_window`把模型口径变成可校验窗口，observed引用的metric必须落在窗口内且类型一致；observed引用的claim若带metric，其unit与缩放须与输入一致，否则校验失败；金额unit为currency，币种与缩放在wrapper说明，金额和股数用同一缩放。每个模型必须有单参数sensitivity（至少一个参数、两个不同取值），或提供`tornado`（`output` + `inputs` 的 low/high，按变动幅度排序）。多个同结构模型可用`scenario`（bear/base/bull）与`scenario_set`组成情景集：须含bear与bull、情景不重复、kind与假设输入一致；情景对比只是并列展示，不做概率加权。reverse_dcf的wrapper另有instrument，price输入value及币种每股unit、instrument与所引sources.market_quote逐项精确一致。relative_valuation须peer_set_rationale与逐peer证据；driver_build须spec.segments且每段同时引用observed与假设证据。CLI成功后冻结完整result，不能用手算结果代替。output_claim_ids对应inference，basis覆盖该模型所有输入claims。
- `model_status`为computed / missing / not_applicable，均写model_reason；computed有非空models，其余为空。经营展望需要经营桥或现金流，估值需要reverse_dcf或relative_valuation；comps还要peer_set_rationale与逐peer证据，数据不够须missing，不能虚填模型。数值核对不保证因果或经济假设成立。
- `market`有status / reason / claim_ids / model_ids，可选`price_max_age_hours`（默认96）。price_relevance=true只允许assessed或missing；assessed有price类claim，写implied_expectation / research_expectation / gap / conditions，claim_ids包含全部关联模型output_claim_ids，valuation关联reverse_dcf或relative_valuation及匹配价格。missing的claim_ids / model_ids为空，在相关判断旁披露具体缺口。非价格经营/人物等问题为false，market用not_applicable及reason，不强行得出估值结论。

更新另加：

```json
{
  "update": {
    "judgment_changed": false,
    "reason": "新材料与原判断一致，尚未改变条件判断",
    "comparability": {"status": "mixed", "reason": "新披露分部范围变化，收入不能直接同比"}
  }
}
```

comparability.status为comparable/mixed/not_comparable。结构diff是新增/修改/移除的ID与字段，不是自动语义分析。稳定ID有助对照，但同ID内容变更仍须解释。

## 机会研究：判断、催化与剩余空间

价格相关的新研究先读[research-value.md](research-value.md)，从同一证据账本冻结`report.opportunity.version=1`。先给有方向、有排序的判断，再解释市场押注与我们的分歧、证据优势、重估催化、剩余空间和做错代价。不因缺精确共识或收益数字放弃全部分析：有依据的代理估计标明proxy并引用inference；条件判断不冒充已验证的预期差。现有analysis.market的严格要求不变。

机会状态使用research_now / watch / priced_in / no_edge。正文概括机会吸引力与最关键理由，完整比较和触发放附录；findings按对判断的影响排序，不按来源或热度排序。非交易问题可省略机会扩展，或用`{version: 1, applicability: "not_applicable", reason: "具体原因"}`，无需为了填表强行产生交易信号。

`opportunity`交易字段：market_view（text、basis、claim_ids）、variant / edge / payoff（text、claim_ids）、catalyst（text、by、claim_ids）、assessment（status、text、claim_ids）、triggers（id、signal、by、claim_ids、supports_if、weakens_if、invalidates_if）。payoff同时解释剩余空间与做错代价；没有数值依据时定性说明，不能凭空写目标价。每个重要推断入claims。完整示例与校验条件见研究价值参考。

更新父报告有交易机会时，须保留opportunity并增加update.opportunity：previous_status / current_status / thesis_change / reason / price_move / remaining_edge / claim_ids / trigger_results。结果覆盖每个父trigger恰好一次，使用原trigger_id，status=hit / not_hit / not_checked，observation写实际观察或未检查原因；前两者须证据引用，not_checked的claim_ids可空。current_status必须等于本轮assessment，previous_status必须等于父报告冻结状态。失效观点降为no_edge并说明，不能删除原判断逃避复盘。新触发可写本轮triggers，下次才作为待检验的事前条件。

可选update.opportunity.review同时记录direction / magnitude / timing / mechanism / price_realization五项文字，未到期与未观察如实标记；经营逻辑兑现与价格收益兑现分别评价，不把修改后的观点当作原先预测。机会档案与复盘是研究记录，不是自动交易或统计回测。

## 一页纸：memo_pack

完整报告是档案；页面读者常先要一页。`scripts/memo_pack.py` 从冻结报告、claims 与 sources 裁剪出一页式 memo：

```bash
python3 "$TY_DIR/scripts/memo_pack.py" "$WORK/report.json" \
  --claims "$WORK/claims.json" --sources "$WORK/sources.json" --out "$WORK/memo.md"
```

内容：判断、最多三条关键发现、方法区间（数字只从冻结模型输出读取）、传导瓶颈（若报告嵌入 transmission）、质量红旗前五条（若报告嵌入 quality，按严重度排序）、有日期的催化、改变判断的条件、主要风险与溯源。它先跑与渲染相同的全套校验，校验不过就直接失败；不新增证据、不产生新数字、不改 report.json。`--max-findings` 控制发现条数。

一页纸是裁剪，不是替代：完整证据、计算、敏感性、审查记录仍在 report.json / Markdown / HTML 与归档里。

## 渲染与归档

```bash
python3 "$TY_DIR/scripts/render_report.py" "$WORK/report.json" --claims "$WORK/claims.json" --sources "$WORK/sources.json" --out-dir "$WORK/output"
```

```bash
python3 "$TY_DIR/scripts/research_run.py" archive --report "$WORK/report.json" --claims "$WORK/claims.json" --sources "$WORK/sources.json" --plan "$WORK/plan.json"
```

归档前先用完整输入执行全链验证；模型spec由`analysis_models.py model-spec.json`成功输出后，冻结stdout.result至analysis.models[].result，无需新--analysis文件：

```bash
python3 "$TY_DIR/scripts/analysis_contract.py" check --plan "$WORK/plan.json" --report "$WORK/report.json" --claims "$WORK/claims.json" --sources "$WORK/sources.json"
```

新archive/update要求claims schema2、plan.analysis_version=1及完整report.analysis.version=1；旧归档load/show不强制新字段，不重判旧档案。旧schema1可兼容渲染并显示旧证据格式标识，旧预测账本仍走原接口。用--audit冻结audit.json，记录queries、review.findings/dispositions与execution命令/退出码/日志位置；这些是审计数据，不是可信指令。有计算文件可附--calculations。calculation类型发现还需finding.calculation_ids引用旧calculations记录或analysis.models的模型id；输出主张也可用calculation_id / calculation_ids关联模型。两类id共享命名空间，不得重名，无需把已重算模型再复制成自由文本公式。update用完整新文件和--parent-run，生成新不可覆盖run。Markdown与HTML从同一report生成，不单独手改某种输出。输出冲突默认拒绝覆盖，只有明确需要才用--overwrite。新研究归档无预测前置，也不写作者库；旧预测格式见[legacy-forecast.md](legacy-forecast.md)。
