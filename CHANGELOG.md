# 版本记录

[返回首页](README.md)

本页记录源码与研究协议演进。版本号不代表已部署到用户客户端，也不代表研究准确率或投资收益。

## 0.12.0 · 催化日历

报告里的「12 月 9 日 FOMC 是下一个催化」通常只是段落里的散文：没有日期字段、无法排序、无法回答「上周该看的东西看了吗」。本轮给已有的触发体系补上日期，而不是另建一套。

- 字段：`opportunity.triggers[]` 与 `watch[]` 新增**可选** `due`（ISO 日期/时刻，不得早于 `report.as_of`）与 `type`（earnings / macro / regulatory / company / industry）。`by` 仍是给人读的窗口，不从文本猜日期。
- 校验：`due` 必须可解析且不早于报告截点；`type` 必须为枚举值；旧报告不填这两个字段完全不受影响。
- 查询：[calendar.py](scripts/calendar.py) 只读扫描报告或 `journal/runs`，输出 `upcoming`（按日期排序、带距今天数）/ `overdue`（已过观察时点、不等于未触发）/ `undated`；支持 `--as-of` 与 `--due N`。
- 边界：不新建 id 空间（trigger id 保持原处，watch 用位置编号 W1..Wn），不后台监控、不自动判定命中；过期不等于未触发，核对结果仍须写进 `update.opportunity.trigger_results`。
- 文档：[catalysts.md](skills/research/references/catalysts.md) 说明字段、查询与边界；research-value 与 SKILL 同步。
- 测试：新增 [test_calendar.py](tests/test_calendar.py) 12 个用例（校验、抽取、状态、排序、horizon、home 扫描、退出码），全套 289 个测试通过。

## 0.11.0 · 估值汇总（football field）

同一份研究常有 DCF、可比公司与反向 DCF 三个模型，但它们此前各自躺在附录，读者要自己对照；正文里手抄模型数字又容易走样。新增可选 `report.valuation_summary`：行只写 `model_id`、`label`、`metric`，**不允许携带任何数字**，渲染时从冻结模型结果读取。

- 校验：`model_id` 唯一且必须存在于 `analysis.models`；`metric` 必须匹配模型种类（dcf / relative_valuation → per_share，reverse_dcf → implied_growth）；所有模型引用的带时刻价格必须一致；行内出现其它字段（包括 `low`/`mid` 这类数值）直接拒绝。
- 渲染：正文「估值汇总」表列出方法、指标、低/中/高、单位与中位相对现价；DCF 区间取自敏感性扫描，comps 取四分位，反向 DCF 单列为隐含增长率；脚注明确「不跨模型加权、不给概率、不是目标价」。
- 兼容：没有该字段的报告渲染字节不变，冻结示例哈希继续通过。
- 测试：新增 3 个用例（只读模型、禁止自带数字、非估值模型与价格漂移），全套 272 个测试通过。
- 文档：memo-template 新增字段说明与示例，analysis-methods 与 SKILL 指明用法。

## 0.10.0 · 驱动式经营模型

`operating_bridge` 只有收入增长与利润率两个标量，文档自己承认不含量价归因；分部与量价拆分只能写成一句话假设。新增 `driver_build` 固定模型：按分部给基期收入、量增长、价增长与分部利润率，确定性汇总为收入、利润与四项效应。

- 恒等式：`base×(1+v)(1+p) = base + volume_effect + price_effect + interaction_effect`，三项效应之和精确等于收入变化；利润为 Σ 分部收入 ×（利润率 + `margin_delta`）。
- 输出：`segment_count`、`base_revenue`、`revenue`、`revenue_change`、三项效应、`base_profit`、`profit`、`profit_change`；基准收入为正时 `revenue_growth`，收入变化非零时 `incremental_margin = Δ利润 ÷ Δ收入`。
- 契约：`spec.segments` 每段须同时引用 observed（fact/price/consensus，支撑基期收入）与假设（inference/view，支撑驱动），缺一边即失败；`margin_delta` 是唯一标量输入，须写成 assumption 并在 wrapper 解释；`operating_outlook` 可由 driver_build 支撑。
- 渲染：模型附录新增「分部驱动」表；无 segments 的报告渲染字节不变，冻结示例哈希继续通过。
- 测试：新增 7 个模型用例与 4 个契约用例（恒等式、单分部、零增长、负利润率、驱动证据、篡改重算、越界使用），全套 269 个测试通过。
- 文档：分析方法的模型表、量价分解说明与边界；SKILL 与 memo-template 同步。

## 0.9.0 · 盈利质量与红旗筛查

插件此前只有现金流桥与固定估值模型，没有回答「这段增长是现金还是会计」的工具。新增[financial_quality.py](scripts/financial_quality.py)：读两期以上同口径报表，输出利润率趋势、现金转化、应计比率、DSO/DIO/DPO 与现金周期、资本开支强度、资本开支/折旧、股权激励占比、投入资本与 ROIC、增量利润率，并给出带阈值与证据字段的红旗清单。

- 契约：期间类型必须一致（混用 fy/quarter/ltm 直接拒绝）；缺字段输出 `null` 而不是猜；每次调用可用 `thresholds` 覆盖默认阈值；未列字段拒绝，避免自定义口径混入。
- 证据：数值字段可写 `{value, claim_ids}`，依赖主张账本；没有引用的字段列入 `unattributed`，提示证据链尚未接上。
- 边界：只做核查提示，不做舞弊判断、不给结论、不产生 claims；比率统一为小数。
- 示例：[微软 FY2024–FY2025](../../examples/msft-quality/README.md) 用已冻结官方表格：毛利率 68.82%、现金转化 1.337、资本开支/折旧 1.89、增量利润率 52.17%，红旗为空；资产负债表缺失时 DSO/DIO/ROIC 为 `null`。
- 文档：[financial-quality.md](skills/research/references/financial-quality.md) 含输入、公式、阈值表与常见误用；SKILL 在研究链中指明何时先跑筛查。
- 测试：新增 16 个用例（含示例回归），全套 258 个测试通过；冻结示例哈希不变。

## 0.8.0 · 结构化数值事实

事实此前只有文本：数字、单位、期间与范围都埋在句子里，YTD 当季度、币种缩放不一致、分部当合并只能靠提示词警告；SEC 取证已保留的 `period_type`、YTD/quarter 与分部维度也没有下游消费者。

新增可选 `claim.metric` 块，把 fact / price / consensus 的数字变成可检查结构：`name`、`value`、`unit`、`period_type`（fy / quarter / ytd / ltm / instant）、`period_start` / `period_end`，可选 `entity`、`scope`、`currency`、`scale`、`basis`、`locator` 与 `comparison_with`。

- 形状校验：字段、数值有限性、期间可解析与先后、instant 期间一致性、scope / basis 枚举；未知字段直接拒绝；metric 只允许出现在 fact / price / consensus 上。
- 口径校验：同一 `entity + name + scope + period_type` 组内 `unit` / `currency` / `scale` / `basis` 必须一致；显式 `comparison_with` 要求双方都声明 metric，且上述口径与 `period_type` 一致——ytd 与 quarter 互比、gaap 与 adjusted 混比都会报错，合法同比（同为 quarter、期间不同）不受影响。
- 可读：附录新增「数值事实」表（主张、实体、指标、数值、单位、期间、口径、范围）；没有 metric 的报告渲染字节不变，微软示例哈希继续通过。
- 工具：[metrics.py](scripts/metrics.py) 可独立导出 `{passed, metrics, failures}`，供后续财务质量、驱动模型与 comps 一致性检查消费。
- 文档：evidence.md 新增字段与口径规则（含 M3/M4 说明），memo-template、SKILL、SEC 参考补充落库要求。
- 测试：新增 [test_metrics.py](tests/test_metrics.py) 17 个用例，覆盖形状、期间陷阱、比较一致性、跨实体、导出与渲染；全套 241 个测试通过。

旧账本无需迁移：不写 metric 就完全保持原行为。

## 0.7.1 · 可复算的派生计算

报告里除固定模型外的数字此前只作记录，从不重算：`calculations[]` 校验数值、单位与引用，公式字符串不执行。实盘 run 出现过把第二个结果塞进 `result.unit` 的情况，估值支点因此不可核验。

新增可选`op`字段，命中白名单即由[calculations.py](scripts/calculations.py)重算并与冻结结果比对，不一致直接校验失败；未标`op`的旧行保持原行为，只作透明记录。渲染标注「已按固定算子重算 / 重算一致」，未标注行仍按原样输出，冻结示例逐字节不变。

- 算子：`ratio`、`growth`、`cagr`、`difference`、`sum`、`product`，输入顺序固定，结果单位有明确契约；`difference`/`sum`要求同单位，`product`只允许一个非ratio输入。
- 引用：输入可用`ref`引用更早的计算id，最多两层链，禁止前向、自引用与交叉单位；`result.precision`（0–12）允许记录舍入值。
- 失败可见：除零、负基数、溢出、未知算子、单位不符、结果不符都返回可读错误，不抛 traceback。
- 文档：[memo-template.md](skills/research/references/memo-template.md) 说明六个算子与单位契约并给出可运行示例，并明确「unit只写单位，不要塞第二个结果」。
- 测试：新增 [test_calculations.py](tests/test_calculations.py) 18 个用例，覆盖算子、单位、引用链、舍入、失败模式、渲染与旧行兼容；全套 223 个测试通过，冻结示例哈希不变。

## 0.7.0 · 相对估值与可比公司

在绝对估值之外加入分析师最常用的相对估值：`relative_valuation` 固定模型读取目标指标、净债务、股数与带时刻价格，并按一组可比公司的倍数分布给出隐含 EV、隐含股权与隐含每股区间，同时反推当前价格隐含的倍数与相对可比中位数的溢价/折价。`valuation` 问题现在可由 `reverse_dcf` 或 `relative_valuation` 支撑，两者也可并用互相检验。

- 模型：`scripts/analysis_models.py` 新增 kind 与 `peers`（name、multiple、可选 note 与 claim_ids）；确定性输出 `peer_count`、`peer_multiple_min/q1/median/q3/max/mean`、`implied_ev_median`、`implied_equity_median`、`per_share_median/low/high`、`implied_multiple_at_price`，可比中位隐含每股为正时输出 `price_vs_peer_median`。分位采用线性插值，结果与 peer 顺序无关。
- 契约：`spec.peers` 逐项须引用 fact / price / consensus，wrapper 须写 `peer_set_rationale`；相对估值同样要求 observed 价格、`instrument` 与来源 `market_quote` 的 value / unit / instrument 精确一致；输出 inference 的 basis 须覆盖全部输入与 peer claims。`valuation` 的 market.assessed 关联模型放宽为 `reverse_dcf` 或 `relative_valuation` 二选一。
- 边界：metric 必须为正（亏损或负基数不能套倍数）；目标指标须与倍数同口径（EV/EBITDA、EV/Sales 对 metric 扣净债务，P/E 对净利润）；comps 只回答相对可比集贵不贵，不产出目标价，也不证明可比集选对；样本量 n 与四分位必须同时披露。
- 渲染：模型附录新增「可比公司倍数」表与「可比公司选择」说明，由冻结的 spec.peers 生成；无 peers 的旧模型渲染字节不变，微软示例哈希继续通过。
- 测试：新增相对估值算术、边界、证据绑定、重算伪造、peers 越界使用及归档往返用例，全套 205 个测试通过。

- [分析方法](skills/research/references/analysis-methods.md)
- [迭代计划与待办](docs/iteration/README.md)

## 2026-11-06 · 公开仓库整理

保持插件源码版本 **0.6.0**，不改变研究协议及既有数据根的兼容行为。

- 重组首页，加入微软FY2025真实案例的输入、输出、截图与复核入口。
- 修正公开克隆与安装目录说明，提供独立运行数据根和SEC可选运行时准备步骤。
- 加入核心离线测试与真实示例的CI检查。
- 为研究、证据、研究档案、历史导出和数据目录建立索引；历史路径不迁移。
- SEC运行缓存与本机运行时配置停止作为共享源码跟踪，本地文件保留；提供配置示例。

## 0.6.0 · SEC 原始披露

增加[SEC取证入口](scripts/sec_data.py)，通过独立Python3.11+运行EdgarTools5.62.1，按精确accession读取主文件、章节和原始报表，保留来源、接受时间及原始期间口径。历史取证按真实接受时间筛选；获取包经原文、定位和时间核查后进入来源与主张账本。

- [接入说明](skills/research/references/sec-data.md)
- [真实季报、历史截点和证据链验证](evidence/sec-integration-20261102/README.md)

## 0.5.1 · 意图核对

研究前结合原问、相关上下文和用户纠正，区分实际值查询、预测及合约决策辅助；明确只查实际值时走简答路径。独立审查对照原话，不仅验收缩窄后的计划；改变用途或主判断后重新审查。

这是研究与审查提示词的更新，不是新增关键词分类器或改变旧归档schema。

- [意图规则](skills/research/references/intent.md)
- [意图回归案例与运行方式](tests/intent/README.md)

## 0.5.0 · 研究价值与更新

价格相关研究明确市场押注、研究分歧、证据、催化、剩余空间及判断错误的后果，形成研究优先级。新增可选机会对象，更新时核对旧触发与新证据，记录判断和剩余研究空间变化。

记录和校验不自动证明交易优势，也不提供后台监控或收益证明。详见[研究价值参考](skills/research/references/research-value.md)。

## 0.4.1 · 背景与变化

在计划、取证和审查中按相关性检查长期条件、近期环境、事前预期、新增变化与传导以及后续验证。沿用schema；这是研究要求，不是自动背景采集器或新的语义校验器。详见[背景研究顺序](skills/research/references/context.md)。

## 0.4.0 · 分析设计与固定模型

增加问题与方法匹配、竞争解释检验、确定性经济模型与敏感性，以及市场隐含预期与研究假设比较。新研究归档要求分析契约，固定模型在检查、渲染和归档时重算；旧归档继续按原格式读取，不追溯改写结论。

- [分析方法](skills/research/references/analysis-methods.md)
- [该轮验收材料](evidence/analysis-upgrade-20261101)

## 0.3.2 · 预期取证指导

增加调查、市场定价、财报共识和历史快照的检索与事前时间核对指导。该更新不新增数据连接器或改变校验schema，也不表示所有列举入口均已联网实测。详见[预期取证参考](skills/research/references/expectations.md)。

## 更早材料

更早的源码、研究过程、回归和交付记录继续保留在[证据档案](evidence/README.md)、[研究档案](journal/README.md)与[历史导出](delivery/README.md)。这些材料的存在不应被自动解释为当前版本已覆盖其所有能力。
