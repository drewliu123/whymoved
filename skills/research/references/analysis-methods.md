# 方法、区分检验与可重算分析

研究者选择问题、解释证据并作经济判断；脚本检查契约和固定算术，不证明因果或假设合理。本页全部示例虚构、无联网取证，C/H/M编号只说明连接方式，不是实际证据。

## 1. 研究者明确选择方法

对象type与question_kind分开，混合问题选一个主问题并在rationale解释。route按研究者明确选择查表，不自动语义分类。

```bash
python3 "$TY_DIR/scripts/analysis_contract.py" route theme_transmission
```

返回question_kind、method、inputs、test、models；按必需输入取证，而非只复制方法名。

| question_kind | method | 必需输入 | 模型要求 |
|---|---|---|---|
| change_explanation | comparative_attribution | 实际表现与同期基准、事件时间线、事前预期 | 按需 |
| operating_outlook | driver_bridge | 量价或收入、利润率、现金需求 | operating_bridge、free_cash_flow或driver_build |
| valuation | reverse_valuation | 带时刻价格、股数及净债务、现金流或可比倍数分布、折现与终值假设 | reverse_dcf或relative_valuation |
| event_forecast | reference_class_scenarios | 可验证的预测目标口径（resolution_contract）、参考类、条件驱动 | 按需 |
| theme_transmission | transmission_bottleneck | 需求到现金链条、取消与交付、利润归属 | 按需 |
| commitment_check | commitment_reconciliation | 有日期承诺、条件及权限、可观察行动 | 按需 |

非交易forecast的resolution_contract指可核验的结果定义：指标、地区、目标期、官方公布口径/精度、来源与核验时点，不要求存在交易市场；market_decision才需精确交易合约及其结算/兜底规则。沿用route返回的字段名，不把普通预测误判为缺市场合约。纯fact_lookup按主Skill简答路径结束，不进入本页分析契约或新分析归档，不虚造机制或竞争解释。

前五种须至少两种不同解释与区分检验；commitment_check可不设竞争检验，但仍记录解释。模型必需但输入缺失时用model_status=missing及model_reason，不填造数据。

## 2. 不同预测决定取证方向

先问“同一观察在两种解释下会有什么不同”，再写检索。共同预测、管理层重复表态、没找到反证，都不能单独区分解释。检验有id、observe、source、by、outcomes，至少两种不同hypothesis_id及不同prediction。每条queries有test_ids，背景查询可[]，每个检验都要有查询覆盖。

以下是完整的虚构plan字段示例；归档还需要对应report、claims及sources，不代表已实际完成取证。

```json
{
  "schema_version": 2,
  "question": "示例公司的订单到现金在哪一环受阻？",
  "type": "theme", "task": "机制研究", "entity": "虚构示例公司",
  "as_of": "2026-11-01T12:00:00+08:00", "historical": false,
  "decision_needed": "区分交付与回款瓶颈，确定下一项观察。",
  "prior_judgment": "首次研究，尚未判断断点。",
  "comparison": {"period": "本期与前期同批次", "unit": "交付量及逾期应收金额", "scope": "同一合并业务范围"},
  "budget": {"max_queries": 4, "max_followups": 1},
  "stop_condition": "检验得到同口径观察，或预算内无法补齐关键缺口。",
  "analysis_version": 1,
  "research_design": {
    "question_kind": "theme_transmission",
    "method": "transmission_bottleneck",
    "rationale": "定位订单到现金的断点，区分交付与回款瓶颈。",
    "baseline": "前一期同范围交付及回款。",
    "price_relevance": false,
    "mechanism_chain": ["订单", "交付验收", "收入", "现金回收"],
    "discrimination_tests": [{
      "id": "T1", "observe": "同批次交付与逾期应收变化",
      "source": "季度交付披露及应收账龄附注", "by": "下一份季度披露",
      "outcomes": [
        {"hypothesis_id": "H1", "prediction": "交付减少，已验收批次回款正常"},
        {"hypothesis_id": "H2", "prediction": "交付稳定，已验收批次逾期应收增加"}
      ]
    }]
  },
  "hypotheses": [
    {"id": "H1", "explanation": "交付瓶颈阻断现金兑现", "discriminating_observation": "交付减少而回款正常"},
    {"id": "H2", "explanation": "回款瓶颈阻断现金兑现", "discriminating_observation": "交付稳定而逾期应收增加"}
  ],
  "queries": [{
    "question": "同批次交付与回款怎样变化？",
    "query": "示例公司 季度 交付 应收账龄", "source": "季度交付披露及应收账龄附注",
    "purpose": "区分交付与回款瓶颈", "test_ids": ["T1"]
  }]
}
```

report.analysis逐项覆盖全部计划检验，各出现一次，id及outcomes逐项复制，不能事后改预测。observed的claim_ids非空，且至少一条为fact / price / consensus，不能仅有view或inference。supports / weakens引用本检验涉及的H id，不得同一H两边都出现；观察无区分力时可均为空。missing必须gap_reason，并清空claim_ids / supports / weakens，不能裁定方向。所有状态均保留interpretation、next_observation、by、supports_if、weakens_if。

以下analysis合并到既有report.json，不是完整报告。假定C1是前期基准fact，C2是同口径本期交付及应收fact，C3是basis引用C1/C2的结论inference；实际使用需相应claims及合格sources。

```json
{
  "analysis": {
    "version": 1,
    "question_kind": "theme_transmission", "method": "transmission_bottleneck",
    "price_relevance": false,
    "baseline": "前一期同范围交付及回款。", "baseline_claim_ids": ["C1"],
    "mechanism_chain": ["订单", "交付验收", "收入", "现金回收"],
    "hypotheses": [
      {"id": "H1", "explanation": "交付瓶颈阻断现金兑现"},
      {"id": "H2", "explanation": "回款瓶颈阻断现金兑现"}
    ],
    "tests": [{
      "id": "T1",
      "outcomes": [
        {"hypothesis_id": "H1", "prediction": "交付减少，已验收批次回款正常"},
        {"hypothesis_id": "H2", "prediction": "交付稳定，已验收批次逾期应收增加"}
      ],
      "status": "observed", "claim_ids": ["C1", "C2"],
      "interpretation": "虚构披露显示交付稳定、逾期应收增加，更符合回款瓶颈；还需排除客户组合变化。",
      "supports": ["H2"], "weakens": ["H1"],
      "next_observation": "同批次应收能否收回", "by": "下一份季度披露",
      "supports_if": "交付稳定且同批次逾期应收继续增加，支持H2",
      "weakens_if": "同批次回款恢复且现金受交付减少影响，削弱H2"
    }],
    "conclusion": "当前更应核查回款环节。", "conclusion_claim_ids": ["C3"],
    "model_status": "not_applicable", "model_reason": "本轮定位传导断点，不作金额预测。", "models": [],
    "market": {
      "status": "not_applicable", "reason": "只问经营传导，不判断价格反映的预期。",
      "claim_ids": [], "model_ids": []
    }
  }
}
```

analysis的question_kind / method / price_relevance / baseline / mechanism_chain与research_design完全一致；hypotheses按顺序复制plan的id / explanation。baseline_claim_ids、conclusion_claim_ids非空且引用实际证据。检验缺失时仍保留原outcomes及其余字段，只把status改missing、增加gap_reason，并清空三组证据/裁定列表；interpretation说明缺口，不能说支持或削弱H。

## 3. 固定模型、输入与真实重算

仅六种模型由compute_model验证，不eval来源公式。spec.inputs精确字段如下，每项都写`{value, unit, role, claim_ids}`；数值有限，ratio用小数。

| kind | 输入及unit | 输出 |
|---|---|---|
| operating_bridge | base_revenue: currency；revenue_growth: ratio；base_margin: ratio；scenario_margin: ratio | base_profit、revenue、profit、profit_change、revenue_growth_effect、margin_effect（currency）；基准利润为正时profit_growth（ratio） |
| free_cash_flow | operating_profit: currency；tax_rate: ratio；depreciation: currency；capex: currency；change_working_capital: currency | free_cash_flow（currency） |
| dcf | free_cash_flow: currency；growth: ratio；discount_rate: ratio；terminal_growth: ratio；years: year；net_debt: currency；shares: shares | enterprise_value、equity_value（currency）、per_share（currency/share）、terminal_value_share（ratio） |
| reverse_dcf | free_cash_flow: currency；discount_rate: ratio；terminal_growth: ratio；years: year；net_debt: currency；shares: shares；price: currency/share；growth_low: ratio；growth_high: ratio | implied_growth（ratio），target_enterprise_value、solved_enterprise_value、residual（currency） |
| driver_build | margin_delta: ratio；spec.segments非空 | segment_count（count）、base_revenue、revenue、revenue_change、volume_effect、price_effect、interaction_effect、base_profit、profit、profit_change（currency）；基准收入为正时revenue_growth（ratio）；收入变化非零时incremental_margin（ratio） |
| relative_valuation | metric: currency；net_debt: currency；shares: shares；price: currency/share；spec.peers非空 | peer_count（count）、peer_multiple_min/q1/median/q3/max/mean（ratio）、implied_ev_median、implied_equity_median（currency）、per_share_median/per_share_low/per_share_high（currency/share）、implied_multiple_at_price、implied_multiple_percentile（ratio）、可比中位隐含每股为正时price_vs_peer_median（ratio） |

经营桥用收入增长和利润率作桥，revenue_growth_effect是收入增长项，不自动识别纯数量效应，量价归因需额外证据。利润率接受有限数值，支持亏损、扭亏及利润率超过100%的情景；基准利润为零或负时省略profit_growth，使用绝对利润变化及桥拆解说明，避免负基数增长率误导。

free_cash_flow模型是简化的企业自由现金流FCFF：税后营业利润+折旧−资本支出−营运资本增量。DCF及reverse_dcf的free_cash_flow均要求FCFF，discount_rate为与币种及名义口径一致的加权平均资本成本WACC；先计算企业价值EV，再减净债务得到股权价值。不能将已扣利息的股权自由现金流FCFE搭配WACC，或对其再扣净债务。

DCF的free_cash_flow为FCF0，须匹配完整年度或明确年化的基期，years单位为年；不能把季度FCF直接当年度输入。模型先将FCF0增长至第1年再折现，终值基于最后一年现金流继续按terminal_growth增长。reverse_dcf以price×shares+net_debt为目标，反求给定年限内恒定增长率，这是条件隐含预期。净债务、股数和价格须同范围、同一估值截点。当前估值模型不适用于零或负FCF；明确记录模型缺失及原因，不能据此判断企业没有价值。

估值需正FCF、股数、价格及折现率，years为1–50整数，terminal_growth小于discount_rate。reverse_dcf增长上下界必须包住目标，否则如实报无解，不能伪造结果。金额unit固定currency，币种、缩放、期间、范围写wrapper.currency / scale / period / scope。金额和股数同一缩放（百万美元与百万股），price仍为美元/股；不混用分部利润与全公司资本支出。reverse_dcf wrapper另须instrument（如NVDA）；模型price输入value、wrapper.currency对应的每股报价unit（如USD/share）及instrument必须与所引sources.market_quote的value / unit / instrument精确一致。

模型输入与metric的数值一致性：observed输入引用的claim若带`metric`块，校验会比较口径——metric.unit映射到currency / ratio / shares / currency/share，与输入unit不一致直接失败（引用了错误证据）；量纲一致时，用wrapper.scale与metric.scale的缩放倍数把两边换算到同一量级再比较，误差超过1e-9即失败。缩放文本无法解析（或任一侧缺失scale）时**跳过而不是猜**：宁可标为无法核对，也不制造假错误。price输入不走金额缩放，只比较每股数值。修正方式是对齐metric或改引正确claim，不是放宽校验。

driver_build把收入拆成分部量价。spec.segments每段写name、base_revenue（基期收入）、volume_growth、price_growth（均须大于−1）、margin（情景段营业利润率）与可选base_margin（基期段营业利润率）及claim_ids；给了base_margin时基期利润按基期利润率计算，利润变化与增量利润率才有意义；不给时基期利润沿用情景利润率（向后兼容）。claim_ids必须同时包含observed（fact / price / consensus，支撑基期收入）与假设（inference / view，支撑驱动），缺一边即契约失败——这是防止把没有依据的分部拆解写成精确结果。spec.inputs只有margin_delta（−1到1，assumption），表示统一的利润率冲击，wrapper.assumptions须解释它。

收入恒等式：base×(1+v)(1+p)=base+volume_effect+price_effect+interaction_effect，三项效应之和在模型内部精确等于revenue_change（volume_effect=Σbase×v，price_effect=Σbase×p，interaction_effect=Σbase×v×p，不要重复计入交互项）。incremental_margin=Δprofit÷Δrevenue，收入不变时省略该输出。利润为Σ段收入×(margin+margin_delta)；基期利润为Σ基期收入×(base_margin，缺省用margin)。

`tornado.output`必须命名标量输出，不能指向多年推演数组；情景集对照也只比较标量输出，推演按各情景模型分别展示。可选`projection`做多年推演：列表每项写`label`、`revenue_growth`（>−1）与`margin`，从模型当年收入起逐年复合，输出每年收入与营业利润，报告渲染「多年推演」表。推演逐年套用给定增长率与利润率，不叠加`margin_delta`敏感性；它是情景算术，不是预测，增长率与利润率的来历仍要写进假设与证据。

边界：分部相互独立，不建模共享成本、协同或分部间转移价；margin是营业利润率而不是净利率；margin_delta是统一冲击，不是分部特定情景，也不能当概率加权。敏感性扫margin_delta可以看整体利润率变化的传导，但单参数扫描仍不是联合情景。情景集：同一驱动结构可以生成bear / base / bull多个模型，各自wrapper写`scenario`（bear/base/bull）与`scenario_set`（同一共享id）。同一set须至少两个模型、含bear与bull、情景不重复、`spec.kind`一致、假设输入集合相同，且每个情景至少有一个assumption输入——否则拒绝。渲染时模型标题标注情景，附录末尾给「情景对比」表（只列各情景共有的输出）。情景之间不是概率加权：不计算期望值、不给概率、不把区间当预测。

relative_valuation用一组可比公司的倍数分布给目标指标定价。spec.peers每项写name与multiple，可选note和claim_ids；claim_ids须引用fact / price / consensus证据，wrapper另写peer_set_rationale说明这批公司为什么可比（业务、规模、增长、会计口径）。模型输出peer_count、min/q1/median/q3/max/mean：n小或分布偏斜时只看中位数会高估精度，须同时报告分位与样本量。分位采用线性插值，n=1时min=median=max。再用中位倍数与四分位给隐含EV、隐含股权与隐含每股区间，并用当前价格反推implied_multiple_at_price（现价隐含多少倍）、implied_multiple_percentile（现价隐含倍数在peer分布中的分位，按严格小于计算）和price_vs_peer_median（相对可比中位数的溢价/折价）；后一项在可比中位隐含每股不为正时省略，避免负基数比率误导。

metric必须为正：亏损、负EBITDA或负收入不能用倍数法，应改用现金流模型或明确写model_status=missing。net_debt可为负表示净现金，shares与price须为正。目标指标与peer倍数必须同一口径：EV/EBITDA、EV/Sales对metric=EBITDA或收入并扣净债务；P/E对metric=净利润；不能用P/E乘EBITDA混用股权价值与企业价值。comps回答“相对这个可比集贵不贵”，不能证明可比集选对，也不产出目标价；样本少、可比性弱、口径不一时把限制写在相关判断旁。零或负FCF的标的可用comps估值，但仍须说明该方法何时失效。敏感性可扫metric（如指引区间两端），不能把单参数扫描当联合情景。

以下是虚构comps spec，仅说明peers形状；C1–C6只示意引用关系，不是实际证据。metrics与倍数同口径（EV/EBITDA），净债务与股数同缩放。

```json
{
  "kind": "relative_valuation",
  "inputs": {
    "metric": {"value": 120, "unit": "currency", "role": "observed", "claim_ids": ["C1"]},
    "net_debt": {"value": 30, "unit": "currency", "role": "observed", "claim_ids": ["C2"]},
    "shares": {"value": 40, "unit": "shares", "role": "observed", "claim_ids": ["C3"]},
    "price": {"value": 22, "unit": "currency/share", "role": "observed", "claim_ids": ["C4"]}
  },
  "peers": [
    {"name": "虚构可比甲", "multiple": 9.5, "note": "同细分、增速略低", "claim_ids": ["C5"]},
    {"name": "虚构可比乙", "multiple": 11.0, "claim_ids": ["C5"]},
    {"name": "虚构可比丙", "multiple": 12.5, "note": "规模更大", "claim_ids": ["C6"]}
  ],
  "sensitivity": [{"input": "metric", "values": [110, 130]}]
}
```

observed引用fact / price / consensus；assumption引用inference / view。wrapper可选`period_window: {start, end, period_type?}`（ISO日期，start不晚于end，period_type取fy/quarter/ltm/instant）：一旦写了，observed输入所引用claim的metric期间必须落在窗口内，且period_type一致，否则失败。`period`仍是给人读的描述，`period_window`才是可校验的口径；两者不要写成互相矛盾。wrapper.assumptions逐输入名映射理由，键集合恰好等于假设输入集合。每个模型必须有至少一项单参数sensitivity、至少两个不同取值，每次只改一个输入，其余固定；reverse_dcf敏感性不能改growth_low / growth_high / years。可用`tornado`替代sensitivity：`{"output": "<输出名>", "inputs": [{"input": "<输入>", "low": 0.08, "high": 0.10}, ...]}`，逐输入推到低/高两端并按选定输出的变动幅度排序；`output`必须是该模型确实输出的名称且在被扫两端都存在，否则报错。解释参数范围，不把单参数扫描或龙卷风当联合情景预测。

以下是独立虚构经营示例，不与前文共用C编号。C1/C2为收入及利润率fact，C3/C4为有依据的假设inference或view；C5为输出inference，basis至少包含C1、C2、C3、C4。把spec对象单独保存为model-spec.json，wrapper留在report.analysis.models。

```json
{
  "id": "M1", "description": "虚构收入与利润率情景桥",
  "currency": "USD", "scale": "金额百万美元；股数若使用则百万股",
  "period": "基准年度至下一年度", "scope": "同一合并业务范围、营业利润口径",
  "assumptions": {
    "revenue_growth": "虚构情景设收入增长25%，仅展示算术。",
    "scenario_margin": "虚构情景设利润率50%，以25%对照。"
  },
  "spec": {
    "kind": "operating_bridge",
    "inputs": {
      "base_revenue": {"value": 80, "unit": "currency", "role": "observed", "claim_ids": ["C1"]},
      "revenue_growth": {"value": 0.25, "unit": "ratio", "role": "assumption", "claim_ids": ["C3"]},
      "base_margin": {"value": 0.25, "unit": "ratio", "role": "observed", "claim_ids": ["C2"]},
      "scenario_margin": {"value": 0.5, "unit": "ratio", "role": "assumption", "claim_ids": ["C4"]}
    },
    "sensitivity": [{"input": "scenario_margin", "values": [0.25, 0.5]}]
  },
  "output_claim_ids": ["C5"]
}
```

该wrapper是计算前输入，尚缺result，不可直接归档。执行：

```bash
python3 "$TY_DIR/scripts/analysis_models.py" "$WORK/model-spec.json"
```

CLI打印`{passed: true, result: {outputs, sensitivity}}`，只把result原样冻结为wrapper.result。此示例已实际调用compute_model：基准利润20、收入100、利润50、变化30、收入增长项5、利润率项25，利润增长1.5；敏感性利润率0.25时利润25、变化5。完整outputs及所有敏感性点须冻结，不能只保存摘要、四舍五入手算数或外层passed。

output_claim_ids均为inference，basis覆盖模型所有输入claims，不能把输出自引为输入。model_status为computed时models非空，其余missing / not_applicable时为空；三种状态均写model_reason。经营展望及估值需要匹配模型或显式missing；其他问题可解释不适用。来源含义、假设合理性与经济因果仍由研究者判断。

## 4. 当前价格隐含什么

price_relevance=true时market只用assessed / missing；false必须not_applicable并写reason。assessed需price类claim及四项比较；market.claim_ids包含全部关联模型output_claim_ids。valuation还须关联reverse_dcf或relative_valuation及匹配价格（两者可同时使用并互相检验）；非valuation价格问题不必强配估值模型，可解释方法并令model_ids=[]。报价与调查预期继续按[expectations.md](expectations.md)取证，不把当前价冒充过去共识。

```json
{
  "status": "assessed", "reason": "比较同一截点价格与研究情景。",
  "claim_ids": ["C_price", "C_implied", "C_research"], "model_ids": ["M_reverse"],
  "implied_expectation": "给定现金流、折现和终值假设，价格对应的增长要求及模型结果。",
  "research_expectation": "有证据和假设依据的研究增长情景。",
  "gap": "同口径差异及其经济含义。",
  "conditions": "会改变差异的经营观察、期限或折现条件。"
}
```

这是字段示意，C/M需换成实际记录且C_implied含对应模型输出。价格时效：`status=assessed`时，所引price claim的`market_quote.quoted_at`距`claim.as_of`不得超过`market.price_max_age_hours`（默认96小时，覆盖周末；日内研究应显式收紧到24小时或更短）。超时直接校验失败，不能拿过期报价当「现价」下判断；历史研究把`as_of`设在当时，报价与当时截点同时代即可。阈值须是1–8760之间的数值。

缺价格或不能识别隐含预期时使用`{"status":"missing","reason":"具体缺失输入及其对价格判断的影响","claim_ids":[],"model_ids":[]}`，在相关判断旁披露，不写“已被定价”。经营/人物等非价格问题用`{"status":"not_applicable","reason":"只核查公开承诺兑现，不判断价格","claim_ids":[],"model_ids":[]}`。

多个估值模型并存时，用`report.valuation_summary`并排展示（见[memo-template.md](memo-template.md)）：该节只引用`model_id`与`metric`，数字一律从冻结模型读取，不允许在正文或汇总里手抄模型结果，也不允许跨方法加权成「目标价」。被比较模型的`period_window`不一致时，每行必须写`period`（基期标签），渲染会多一列「期间」——不同基期可以并列，但不能悄悄混用。

## 5. 全链核对与交付

```bash
python3 "$TY_DIR/scripts/analysis_contract.py" check --plan "$WORK/plan.json" --report "$WORK/report.json" --claims "$WORK/claims.json" --sources "$WORK/sources.json"
```

此命令实际验证完整bundle、plan与analysis一致性、引用及固定模型重算。无需新--analysis文件：分析嵌入report，设计嵌入plan。保存命令、退出码、日志及red-team处置到audit。新archive/update强制此契约；旧load/show不强制补齐，不重判历史，更新旧run时以当前契约生成新输入。

正文只给判断、机制、关键结果、比较口径及改变结论的缺口。不同预测矩阵、模型参数与敏感性、C/H/M编号、命令和审查记录放附录或审计。red-team逐项检查方法、区分证据、模型、价格预期并记录关键错，无需多空投票；数值核对不能替代经济判断。
