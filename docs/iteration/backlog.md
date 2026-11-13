# 迭代待办（Backlog）

状态图例：`待认领` → `进行中` → `待验证` → `已完成` / `搁置（理由）`
优先级：P0 = 投研方法硬缺口；P1 = 显著提升研究深度；P2 = 支撑性/工程性。

排序原则：价值（是否让研究更像分析师做的事）÷ 成本（改动面、契约风险）。**同一轮只认领一张卡，且不与其他卡的写文件范围重叠。**

> 2026-11-14 修订：独立审计（专业分析师视角）指出两个比原 P0 更便宜、更关键的缺口——(a) `calculations[]` 从不重算，报告里除 5 个固定模型外所有数字都不可复算，且实盘 run 已出现「把第二个结果塞进 result.unit」的事故；(b) 事实只有文本，没有「数值+单位+期间+范围」结构，导致量价、质量、comps 下游各自发明输入格式。二者已插到最前，原排期顺延。

---

## 2026-11-14 盘点后的下一阶段（见 [review-2026-11.md](review-2026-11.md)）

方法层与交付层已完整；以下按「减少规模与完整性缺口」排序，不再新增方法。

### P0-7 事件研究存储

- 状态：✅ 部分完成（Cycle 45）：改用 returns-only 样本压缩体积，**未**动归档文件清单
- 判断：拆到归档新文件的收益与风险不匹配；若未来样本量级真正成为问题，再评估引用式存储
- 问题：`report.event_study` 内嵌样本价格序列，样本多时 `report.json` 与渲染都会膨胀。
- 方案：报告只保留事件定义、窗口、样本标识与聚合结果引用；价格序列写入归档新增的 `event-study.json`（需同步 `FILES`、manifest 哈希、`load_run` 巡检与归档测试）。**必须保持旧归档可加载**：没有该文件的 run 仍按内嵌方式读取。
- 验收：新格式往返、旧格式兼容、体积对比、manifest 覆盖、测试与文档。
- 风险：改归档文件清单影响面大；先在单个示例上验证再迁移。

### P1-8 memo 完整度

- 状态：✅ 已完成（Cycle 46）：未挂字段与图表清单已入 memo
- 方案：一页纸补两处——质量小节的 `unattributed` 提示；图表引用（至少列出「完整报告含 N 张图」并提供标题，避免读者以为没有图）。
- 成本 S；不改任何契约。

### P1-9 共识增长与反向 DCF 的受控对照

- 状态：✅ 已完成（Cycle 47）：独立只读工具，强制期限披露、禁止相减
- 方案：在报告附录并列「共识相邻财年隐含增长」与「反向 DCF 隐含增长率」，**必须标注两者期限不同**（相邻财年 vs 多年 CAGR），禁止合成单一「预期差」。
- 验收：期限标注强制存在；缺任一侧时降级为单侧展示。

### P2-8 暂缓项

- 季度共识增长（需要财年日历映射）、100% 堆叠、多图共享坐标轴、别名自动建议：价值低于实现成本，先不做。

---

## P0-0a 可复算的派生计算（calculations op 白名单）

- 状态：✅ 已完成（Cycle 2，见 [log.md](log.md)）
- 价值：HIGH / 成本：S–M。这是最便宜的高价值改动，且修的是**已经发生的真实事故**。
- 现状：`report.calculations[]` 只校验有限数值、单位与引用，**从不执行也不重算**（[render_report.py:217](../scripts/render_report.py)）。实盘 run `R20261112T153326Z`（NVDA）把 FY27 EPS 与 P/E 塞进 `result.unit` 字符串，全篇估值结论的支点既不是输入也不是结果，任何校验都碰不到。
- 方案：
  1. calculation 行加**可选** `op`，白名单算子：`ratio`、`growth`、`cagr`、`sum`、`product`、`difference`、`pct_change`、`share_of`、`bridge_add`。
  2. `inputs` 用 claim_id 或 calculation_id 引用，`precision` 明确舍入位数。
  3. 命中白名单 → 重算并与 `result` 比对（相对容差 1e-9）；未命中 → 保持今天的「仅记录」，渲染明确标注差异。
  4. 渲染区分「已重算 / 仅记录」，并在附录打印公式与输入值。
- 验收：旧 formula-only 行继续合法；白名单算子有正例+篡改用例；嵌套深度 ≤2；不允许来源文本当表达式；归档往返一致。
- 风险：滑向自制公式语言 → 硬性限制算子数、嵌套深度、禁止自由表达式；它只证明算术一致，不证明输入值等于原文（那属于 P0-0b）。
- 主要文件：`scripts/render_report.py`（validate_calculation_rows 与渲染）、新 `scripts/calculations.py` 或复用、`tests/test_reports.py`、`skills/research/references/memo-template.md`、CHANGELOG

## P0-0b 数值事实结构（claim.metric）

- 状态：✅ 已完成（Cycle 3，见 [log.md](log.md)）
- 遗留增强：模型输入与 metric 的一致性校验（需先定义缩放映射），见 P1-0c。
- 价值：HIGH / 成本：M。是财务质量、驱动建模、comps 一致性的共同前提。
- 现状：claim 只有 `{id, text, type, as_of, sources, basis}`，数字只活在自然语言里；SEC 入口保留了 period_type / YTD / dimensions / scope，但下游没有任何地方消费。YTD 当季度、币种缩放不一致、分部当合并，全靠提示词警告。
- 方案：fact / consensus / price 三类 claim 加**可选** `metric`：`{name, value, unit, currency, scale, period_start, period_end, period_type: fy|quarter|ytd|ltm|instant, scope: consolidated|segment:<name>, basis: gaap|adjusted, locator}`。
  - `check_claims` 增加：同一 `name` 在不同 claim 间 unit/currency/scale/period_type 必须一致；显式 `comparison_with` 的一对 claim 若 period_type 不同则报错；模型输入的 metric 期间须落在 wrapper.period 内。
  - **只在字段存在时校验**，旧档案零迁移。
- 验收：正例/反例；旧 claim 不受影响；渲染不改；与 P0-0a 成对上线（否则「已重算」会制造虚假安心）。
- 风险：契约膨胀与「假强制」→ 不设必填；只在显式比较关系时强制期间一致性；`basis: adjusted` 显式标记，防止非 GAAP 混入 GAAP 比较。

## P0-1 相对估值：可比公司分析（comps）

- 状态：✅ 已完成（Cycle 1，见 [log.md](log.md)）
- 交付：`relative_valuation` 固定模型（peers 分布、隐含 EV/股权/每股区间、隐含倍数、相对中位数溢价）、契约与证据绑定、附录渲染、13 个新测试、文档与 0.7.0。
- 遗留增强：✅ `implied_multiple_percentile` 已于 Cycle 13 补齐。

## P0-2 财务质量与法证筛查

- 状态：✅ 已完成（Cycle 4，见 [log.md](log.md)）
- 遗留：✅ 账本装配（Cycle 14）、✅ 报告嵌入（Cycle 27）、✅ memo 红旗（Cycle 28）、✅ 平均资产应计与未挂字段（Cycle 31）。
- 价值：HIGH / 成本：M。「增长是现金还是会计」是回报最高的一问；当前完全没有比率、应计、周转。
- 方案：`scripts/financial_quality.py`（或 P0-0b 之后的模型 kind），输入两期以上 metric facts，输出：
  - 毛利率/营业利润率/净利率趋势；CFO/NI 现金转化；应计比率 `(NI−CFO)/平均总资产`
  - DSO / DIO / DPO / 现金周期；capex/D&A；capex/收入；SBC/收入
  - ROIC（**打印投资资本定义**）；净股本变动（回购 vs 稀释）
  - 红旗清单：每条含阈值、依据字段、解释；只作提示不作结论
- 验收：正例+边界（负利润、零分母、缺字段拒绝计算而非猜）；行业 profile 可覆盖阈值；文档写明「经验区间」。
- 主要文件：新 `scripts/financial_quality.py`、`tests/test_financial_quality.py`、references 新文档、README/architecture 入口表

## P0-3 驱动式经营模型（driver build）

- 状态：✅ 已完成（Cycle 5，见 [log.md](log.md)）
- 遗留：分部表补每段派生贡献；单分部量价敏感性需要多维情景（P1-3）。
- 价值：HIGH / 成本：M–L。现有 operating_bridge 是 4 个标量，文档自己承认不含量价效应；而行业分析本体就是分部与量价。
- 方案：`driver_build`：`segments[] {name, base_revenue, volume_growth, price_growth | revenue_growth, margin}`；输出分段收入/利润贡献、量价结构利润率四效应、增量利润率 = Δ利润/Δ收入；**恒等式检查**：分部加总=合计、`(1+v)(1+p)` 复原收入、精确相等。
- 验收：恒等式、零基数、负增长、单分部、分部利润加总与合并口径不一致时报错而非静默。
- 风险：数组输入与现有扁平 `_fields/_ranges` 冲突 → 需要真正输入 schema；6 个分部 = 18 个不可验证假设 → 每个驱动强制 assumption + 敏感性。
- 主要文件：`scripts/analysis_models.py`、`scripts/analysis_contract.py`、`scripts/render_report.py`、测试、analysis-methods

## P0-4 估值汇总表（football field）

- 状态：✅ 已完成（Cycle 6，见 [log.md](log.md)）
- 遗留：DCF 区间仍是单参数敏感性；未展示主导假设列。
- 价值：HIGH / 成本：S。IC 要的就是一张表：方法 → 低/中/高每股 → 对现价隐含空间 → 主导假设。现在 DCF 与 comps 躺在两张附录表里，读者要自己动手，报告自然「没有结论」。
- 方案：`report.valuation_summary` 从**已冻结模型输出**生成；行 = DCF 区间、reverse-DCF 隐含、comps 分位；列 = 低/中/高/每股/相对现价/主导假设。**不加权、不给概率、不给「公允价值」单值**，reverse-DCF 行标注「这是预期，不是估值」。
- 验收：篡改行数值不能通过（重算或用模型输出）；无模型时该块不存在而非空表；双格式渲染。

## P0-5 催化日历（与 triggers 共用 id 空间）

- 状态：✅ 已完成（Cycle 7，见 [log.md](log.md)）
- 遗留：合并 update.trigger_results 状态；watch 位置编号会漂移。
- 价值：HIGH / 成本：S–M。催化目前只是机会对象里的文字与自由文本 watch；没有日期、没有状态机、无法回答「上周该看的东西看了吗」。
- 方案：`report.catalysts[]`：`{id, by（日期或窗口）, type, expectation, discriminating_signal, claim_ids, status: upcoming|hit|not_hit|expired|not_checked}`；渲染按日期排序的附录时间线；提供 `--due N` 查询。
- **关键约束**：不能另建第二套触发系统。`opportunity.triggers` 改为它的视图（同 id、同 by），全仓一套触发体系。
- 验收：schema 校验；跨 run 状态继承；日历不宣称「已被监控」。

## P0-6 跨轮次研究记忆（research memory）

- 状态：✅ 已完成（Cycle 8，见 [log.md](log.md)）
- 遗留：判断沿革已由 `thread` 覆盖（Cycle 20）；✅ 实体别名表（Cycle 37）与 ✅ 冲突检测（Cycle 41）；增量索引；沿革未带证据摘要。
- 价值：HIGH / 成本：M。「持续性投研」的核心：回答「我们之前对 X 判断过什么、依据哪条证据、现在改变了吗」；也是唯一能防事后诸葛的东西。
- 方案：`scripts/research_memory.py index|query`：扫描 `journal/runs/*/`，抽取实体（plan.entity + 代码）、as_of、判断、assessment 状态、触发 id、claim 类型，生成可重建、幂等、带内容哈希的 `journal/index.json`；按实体查询返回时间排序的判断与冻结文件链接；`--as-of` 给当时视图。
- 约束：只存指针不合并数字；不产生 claim；不改归档；每条打印父 run 的 as_of；禁止用旧 inference 直接支撑新结论。

## P1-1 一致预期序列、修订与指引 vs 实际

- 状态：✅ 已完成（Cycle 12；指引 vs 实际的期间映射未做，见遗留）
- 遗留：guidance.target_period 与 claim.metric 日期期间的映射；跨 run 序列汇总；季度序列增长未做；隐含增长未进 memo。
- 方案：(a) consensus claim 加 `series {series_id, metric, target_period, provider, n, median, low, high, as_of}`，用 P0-0a 的 growth 算子算修订；(b) claim 加 `guidance {metric, target_period, midpoint, range, as_of, company_guidance: true}`，契约硬规则：**指引永远不能充当 consensus**；(c) 渲染「预期 vs 实际 vs 修订」小表。
- 风险：数据在付费墙后，做成字段后长期为空 → 要求 provider + n + method 三件套；`missing` 为默认；禁止拿分析师目标价当 consensus。

## P1-2 数据新鲜度与来源冲突

- 状态：✅ 已完成（Cycle 9，见 [log.md](log.md)）
- 遗留：consensus/filing 陈旧度；冲突未解决无阻断级别；未自动比对同名 metric。
- 方案：(a) `check_claims` 计算 `quote_age = as_of − quoted_at/published_at`，按类型阈值（用于 market.assessed 的 price 超时 → error，其余 warning）；(b) `report.conflicts[] {metric, candidates[{source_id, value}], adopted_source_id, rule, reason}`，渲染脚注表。
- 验收：阈值可配置；长周期研究不被误伤；冲突仅在真实并存时要求。

## P1-3 情景集 + 龙卷风敏感性

- 状态：✅ 已完成（龙卷风 Cycle 10；情景集 Cycle 11）
- 遗留：共享 driver set 对象；对比表展示关键假设值。
- 方案：允许 N 个同 kind 模型带 `scenario: bear|base|bull` 并共享 driver-set id；契约要求至少一上一下、输入全为 assumption；`sensitivity_mode: tornado` 输出按影响幅度排序。两者都**不给概率**；≤4 个情景；图注写明各输入独立假设。

## P1-4 块级渲染 / IC memo 包

- 状态：✅ 全部完成（内联表格 15、多序列 17、一页纸 18、多图 19、柱状/瀑布 24、分组柱状 39）
- 遗留：✅ 堆叠柱状（Cycle 42）；多图共享坐标轴；100% 堆叠未做。
- 方案：(a) findings 加 `table_ids` 内联；(b) `charts[]` 支持多序列与日期轴，同源数据表保留；(c) 列级 units；(d) `memo_pack`：一页判断 + variant + 估值汇总 + 催化 + 证伪条件。
- 风险：`render_report.py` 是爆炸半径最大的文件；schema 变化需旧档案仍可渲染。

## P2-1 事件研究与历史类比

- 状态：✅ 脚本（Cycle 16）、✅ 报告嵌入（Cycle 29）、✅ memo 引用（Cycle 35）；超额收益未做
- 方案：`scripts/event_study.py`：给定事件样本与收益序列，计算 [-N,+N] 窗口累计收益分布、胜率、中位数；样本逐条引用来源；禁止事后挑样本；报 n 不给 p 值。

## P2-4 行业传导图

- 状态：✅ 已完成（Cycle 21，见 [log.md](log.md)）
- 遗留：✅ 报告渲染集成（Cycle 26）与 ✅ memo 引用瓶颈（Cycle 28）；时滞区间推导；跨主题合并。

## P2-2 Watchlist 摘要

- 状态：✅ 已完成（Cycle 23；Cycle 32 按问题合并）；未接入定时任务。
- 遗留：合并键是问题原文；结论版本不做语义相似；判断变化未按问题合并。
- 方案：汇总多个 run 的判断变化生成 digest，不另起扫描器。

## P2-3 安装与开发文档补齐

- 状态：✅ 已完成（Cycle 25）：README 能力地图、参考索引、开发检查清单
- 遗留：能力地图需人工同步；安装文档未逐条列出新脚本（无新增依赖）。

## 搁置

- **研究质量自评分脚本**：结构性自评可刷分、易官僚化，red-team 已在做语义审查。除非能设计出不可作弊的判据，否则不做。
- **WACC/CAPM 构建**：beta 选择不可验证，确定性 CAPM 只增加精度不增加真值。保持 `discount_rate` 为显式假设 + 区间敏感性。
- **SOTP / NAV**：依赖分部与资产清单，L 成本、极高假精度风险，等 P0-3 落地后再评估。

---

## P1-5 从主张账本装配质量报表

- 状态：✅ 已完成（Cycle 14，见 [log.md](log.md)）
- 遗留：guidance/consensus 不入装配；行业自定义指标白名单；分部报表未做。

## P1-0d 模型期间窗口

- 状态：✅ 已完成（Cycle 30，见 [log.md](log.md)）
- 遗留：assumption 无期间；✅ 跨模型窗口披露（Cycle 34）；✅ 标签窄校验（Cycle 36）；季度与财季对应仍无法校验。

## P1-0c 模型输入与 metric 的一致性

- 状态：✅ 已完成（Cycle 22，见 [log.md](log.md)）
- 遗留：特殊每股口径会跳过；期间一致性未校验；缩放词表静态。
- 方案：模型 observed 输入引用带 metric 的 claim 时，校验数值与单位换算一致。前提是先定义 `scale` 的规范映射（million/billion/万/亿），或要求 metric.scale 使用枚举；换算失败时报告“无法核对”而不是报错。
- 风险：缩放文本解析误判；应限定枚举并允许显式 unknown。

## 已完成

- P3-4 第三个真实示例（盈利质量）— 2026-11-14，Cycle 53
- P2-10 体检重渲染与命名守卫 — 2026-11-14，Cycle 52
- P2-9 归档渲染回归 + CI 示例泛化 — 2026-11-14，Cycle 51
- P3-3 第二个真实示例（分部利润归因）— 2026-11-14，Cycle 50
- P3-2 分部基期利润率 + 标准库同名修复 + 全链验收 — 2026-11-14，Cycle 49
- P3-1 真实归档验收与符号链接修复 — 2026-11-14，Cycle 48
- P1-9 预期对照工具 — 2026-11-14，Cycle 47
- P1-8 一页纸完整度 — 2026-11-14，Cycle 46
- P0-7 事件研究仅收益样本 — 2026-11-14，Cycle 45
- P1-1b 共识相邻财年隐含增长 — 2026-11-14，Cycle 43
- P1-4g 堆叠柱状图 — 2026-11-14，Cycle 42
- P0-6d 别名冲突检测 — 2026-11-14，Cycle 41
- P2-7 数据根体检 doctor — 2026-11-14，Cycle 40
- P1-4f 分组柱状图 — 2026-11-14，Cycle 39
- P2-6 真实报表模型验证 — 2026-11-14，Cycle 38
- P0-6c 实体别名 — 2026-11-14，Cycle 37
- P1-0f 基期标签窄校验 — 2026-11-14，Cycle 36
- P2-1c 一页纸引用参考类分布 — 2026-11-14，Cycle 35
- P1-0e 估值汇总基期披露 — 2026-11-14，Cycle 34
- P2-5 归档兼容回归测试 — 2026-11-14，Cycle 33
- P2-2b 摘要按问题合并 — 2026-11-14，Cycle 32
- P0-2c 质量表打磨（平均资产应计 / 未挂字段）— 2026-11-14，Cycle 31
- P1-0d 模型期间窗口 — 2026-11-14，Cycle 30
- P2-1b 事件研究嵌入报告 — 2026-11-14，Cycle 29
- P1-4e 一页纸引用瓶颈与红旗 — 2026-11-14，Cycle 28
- P0-2b 盈利质量嵌入报告 — 2026-11-14，Cycle 27
- P2-4b 传导图嵌入报告 — 2026-11-14，Cycle 26
- P2-3 能力地图与维护清单 — 2026-11-14，Cycle 25
- P1-4d 柱状与瀑布图 — 2026-11-14，Cycle 24
- P2-2 多轮研究摘要 digest — 2026-11-14，Cycle 23
- P1-0c 模型输入与 metric 一致性 — 2026-11-14，Cycle 22
- P2-4 行业传导图 — 2026-11-14，Cycle 21
- P0-6b 判断沿革 thread — 2026-11-14，Cycle 20
- P1-4 块级渲染 / IC memo 包 — 2026-11-14，Cycle 15–19
- P1-4c 一页式 IC memo — 2026-11-14，Cycle 18
- P1-4b 多序列图表 — 2026-11-14，Cycle 17
- P2-1 参考类事件研究 — 2026-11-14，Cycle 16
- P1-4a 块级渲染：内联表格与列级单位 — 2026-11-14，Cycle 15
- P1-5 账本装配质量报表 — 2026-11-14，Cycle 14
- P1-1 一致预期序列与修订 — 2026-11-14，Cycle 12
- P1-3 情景集 + 龙卷风敏感性 — 2026-11-14，Cycle 10–11
- P1-2 价格时效与来源冲突 — 2026-11-14，Cycle 9
- P0-6 跨轮研究记忆 — 2026-11-14，Cycle 8
- P0-5 催化日历 — 2026-11-14，Cycle 7
- P0-4 估值汇总（football field）— 2026-11-14，Cycle 6
- P0-3 驱动式经营模型（driver_build）— 2026-11-14，Cycle 5
- P0-2 盈利质量与红旗筛查 — 2026-11-14，Cycle 4
- P0-0b 结构化数值事实（claim.metric）— 2026-11-14，Cycle 3
- P0-0a 可复算派生计算（calculations op）— 2026-11-14，Cycle 2
- P0-1 相对估值（comps）— 2026-11-14，Cycle 1
