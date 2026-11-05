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

可选chart：`{title,x_label,y_label,unit,rows:[{label,value}],claim_ids,note}`。value必须有限数值，口径相同、时间顺序明确；图表依数据需要选用。渲染器附同源数据表、键盘读数、明暗/移动布局。不要双轴混量纲，不以图形暗示不存在的因果。

可选calculations列表：`{id,description,formula,inputs:[{name,value,unit,claim_ids}],result:{value,unit},claim_ids}`；对应claim可标calculation_id。公式只作可读记录，不执行来源文本。此旧计算记录只检查结构与引用，不自动重算，不能替代新analysis.models中的固定模型验证；真实计算命令和退出码另存evidence。

## analysis：底稿完整，正文简明

新报告须有`analysis.version: 1`，完整plan/analysis示例与模型精确字段见[analysis-methods.md](analysis-methods.md)。不要把本节逐条展开为正文栏目；正文呈现判断、机制、关键结果及相关缺口，预测矩阵、输入/假设和敏感性放证据附录。

- `question_kind / method / price_relevance / baseline / mechanism_chain`与plan.research_design一致，`hypotheses`按顺序复制plan的`{id, explanation}`。`baseline_claim_ids`及`conclusion_claim_ids`引用实际基准和结论证据，`conclusion`写当前判断。
- `tests`覆盖全部计划检验，各出现一次，id和outcomes逐项不变。每项有status（observed / missing）、claim_ids、interpretation、supports / weakens（H id）、next_observation、by、supports_if、weakens_if。observed至少引用一条fact / price / consensus，不能仅有view或inference；missing写gap_reason，claim_ids / supports / weakens均为空，不能用未找到证据支持或削弱解释。
- `models`每项有id / description / currency / scale / period / scope / assumptions / spec / result / output_claim_ids。spec只用四种固定compute_model：operating_bridge、free_cash_flow、dcf、reverse_dcf。全部输入分observed与assumption，后者在wrapper.assumptions逐输入说明理由；金额unit为currency，币种与缩放在wrapper说明，金额和股数用同一缩放。每个模型必须有单参数sensitivity，至少一个参数、两个不同取值。reverse_dcf的wrapper另有instrument，price输入value及币种每股unit、instrument与所引sources.market_quote逐项精确一致。CLI成功后冻结完整result，不能用手算结果代替。output_claim_ids对应inference，basis覆盖该模型所有输入claims。
- `model_status`为computed / missing / not_applicable，均写model_reason；computed有非空models，其余为空。经营展望需要经营桥或现金流，估值需要reverse_dcf；数据不够须missing，不能虚填模型。数值核对不保证因果或经济假设成立。
- `market`有status / reason / claim_ids / model_ids。price_relevance=true只允许assessed或missing；assessed有price类claim，写implied_expectation / research_expectation / gap / conditions，claim_ids包含全部关联模型output_claim_ids，valuation关联reverse_dcf及匹配价格。missing的claim_ids / model_ids为空，在相关判断旁披露具体缺口。非价格经营/人物等问题为false，market用not_applicable及reason，不强行得出估值结论。

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
