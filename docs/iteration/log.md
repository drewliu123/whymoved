# 迭代记录（Log）

每轮一条，倒序不必要——按时间正序追加，方便读演进。格式：目标 → 改动 → 验证证据 → 对投研意义的增量 → 遗留。

---

## Cycle 4 · 2026-11-14 · 盈利质量与红旗筛查

**对应卡片**：P0-2

**问题**：插件能算现金流桥和估值，却不能回答买方最先问的一句话——「这段增长是现金还是会计」。没有利润率趋势、没有现金转化、没有应计与周转、没有资本开支强度，NVDA 那类「用 non-GAAP EPS 得出不贵」的结论没有任何交叉检查。

**改动**

| 文件 | 变更 |
| --- | --- |
| `scripts/financial_quality.py`（新） | 报表输入校验（同期间类型、必填、拒绝未知字段）；逐期指标；环比变化；红旗清单；`--out`；退出码 0/1/2 |
| `examples/msft-quality/`（新） | 用已冻结的微软官方表格数字构造真实示例，README 记录来源、结果与「故意缺什么」 |
| `skills/research/references/financial-quality.md`（新） | 输入契约、指标公式、阈值表、边界与常见误用 |
| `skills/research/SKILL.md` | 研究链中指明：两期以上报表先跑筛查，输出是提示不是结论，数字仍须入账 |
| architecture / README / CHANGELOG | 入口表、能力描述、0.9.0 |
| `tests/test_financial_quality.py`（新） | 16 个用例：形状、期间混用、缺失字段、指标、变化、红旗、阈值覆盖、干净公司、CLI、示例回归 |

**关键设计决定**

1. **缺失即 `null`**：没有资产负债表科目就不算 DSO/DIO/ROIC，也不假设天数；这比给一个「看起来专业」的数字更可信。
2. **只给提示不给结论**：severity 只有 high/medium，没有总分与「通过/不通过」。红旗必须带证据字段，读者能立刻回到原文。
3. **阈值可覆盖且集中**：`THRESHOLDS` 一处定义，调用时可传 `thresholds`；文档明说默认值是经验区间，银行/REIT/SaaS 不适用。
4. **证据可挂但非强制**：字段支持 `{value, claim_ids}`，没挂的进 `unattributed`。工具不产生 claims——这套仓库的可信度来自账本，不能靠输出文件绕过去。
5. **增量利润率**：用 Δ营业利润 ÷ Δ收入，而不是利润率差的近似；这是「增长是否创造利润」的直接检验。

**验证证据**

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
# Ran 258 tests ... OK
python3 scripts/financial_quality.py examples/msft-quality/statements.json
```

- 真实数字（微软 FY2025，来自 `examples/msft-cashflow` 的官方表格）：毛利率 68.82%（−0.94pp）、营业利润率 45.62%（+0.98pp）、现金转化 1.337（−0.008）、资本开支/收入 22.91%、资本开支/折旧 1.89、股权激励 4.25%、增量利润率 52.17%——**红旗为空**。一个健康公司不该被制造噪音，这条被示例测试守住。
- 反例（虚构数据）：收入 +20%、现金转化从 1.2 降到 0.83、DSO +45%、DIO +29%、股本 +4%、资本开支/折旧 0.56 → 触发 7 条红旗，阈值覆盖测试可关闭其中两条。
- 期间混用（fy + quarter）→ `FQ2 periods must share one period_type`。

**投研意义增量**

1. 多一种分析师会用的方法：盈利质量筛查，从「只看利润表」到「利润、现金流、营运资本、投入强度一起看」。
2. 多回答一类问题：「增长有没有现金支撑」「应收/存货是不是在积累风险」「投入是在扩张还是吃老本」。
3. 多一条可核实连接：指标全部由输入确定性计算，输入可挂claim_ids，实盘数字可在示例里逐项追溯。
4. 边界更清楚：缺失不猜、行业差异写进文档、阈值可覆盖、不产生claims、不给结论。

**遗留**

- 与主张账本尚未自动对接：报表输入目前手写；下一步可做「从 claim.metric 批量装配 statements.json」的适配器，让质量筛查直接消费账本里已有的数值事实。
- 应计比率用期末总资产（未平均）；若两期资产都有，改为平均更稳，留作小改进。
- 未包含现金流质量的其他维度：递延收入、资本化率、一次性项目拆分，这些依赖更细的附注抽取。
- 报告渲染尚未集成质量表；当前通过文档与示例交付，等「报告附录可选区块」卡片一起做。

## Cycle 3 · 2026-11-14 · 结构化数值事实（claim.metric）

**对应卡片**：P0-0b

**问题**：事实只有文本。数字、单位、期间、范围全埋在句子里，三类经典事故——YTD 当季度、币种缩放不一致、分部当合并——只靠提示词警告；SEC 取证已经保留了 `period_type`、YTD/quarter 与 dimensions，但下游没有任何地方消费。这也是财务质量、驱动建模、comps 一致性的共同前提。

**改动**

| 文件 | 变更 |
| --- | --- |
| `scripts/metrics.py`（新） | `claim.metric` 形状校验（M1）、期间与 instant 语义（M2）、显式比较一致性（M3）、同组口径一致性（M4）；`extract_metrics` 导出；CLI 打印 `{passed, metrics, failures}` |
| `scripts/check_claims.py` | 账本校验接入 metric：形状错误与跨主张错误挂到对应 claim；metric 仅允许出现在 fact / price / consensus |
| `scripts/render_report.py` | 附录新增「数值事实」表（主张、实体、指标、数值、单位、期间、口径、范围），仅在存在 metric 时输出 |
| `tests/test_metrics.py`（新） | 17 个用例：必填/未知字段、数值类型、期间先后、instant、scope/basis、比较口径、跨实体、同组单位、导出、CLI、双格式渲染、无 metric 兼容 |
| 文档 | evidence.md 新章节（字段表 + 口径规则 + 示例）、memo-template、SKILL、SEC 参考、architecture 入口、CHANGELOG 0.8.0 |

**关键设计决定**

1. **`entity` 进入分组键**：同名指标跨公司比较很常见（comps 的 peer 倍数就是这样做），若不区分实体，AMD 的 EUR 口径会和 NVDA 的 USD 口径互相误伤。分组键 = `entity + name + scope + period_type`。
2. **只强制显式比较**：跨期比较是研究的常态（同比、环比），全局要求同期会把正常工作判成错误。因此口径一致性只在两种情形下强制——同组（同实体同指标同范围同期间类型）必须单位一致；写了 `comparison_with` 的一对必须期间类型一致。ytd vs quarter、gaap vs adjusted 在这里被拦住，合法同比（都是 quarter、期间不同）不受影响。
3. **instant 语义**：股本、股数、市价这类「某一时点」的指标不要求 period_start；若填了必须等于 period_end。
4. **只允许 fact / price / consensus**：view 与 inference 的数值应由模型或计算记录表达，避免把推断伪装成披露值。

**验证证据**

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
# Ran 241 tests ... OK
```

- 冻结示例：`report.md` / `report.html` 仍逐字节相同（无 metric 的账本渲染不变）。
- 口径演示（用 NVDA 风格数值构造）：
  - `quarter`（comparison_with 指向 `ytd`）→ `M3 comparison requires the same period_type: quarter vs ytd`
  - 同指标同实体但一边 `USD billion` 一边 `USD million` → 两条主张都报 `M4 ... must use one unit`
  - 跨实体（NVDA/USD vs AMD/EUR）→ 通过，不误伤
- 无 metric 的旧账本：校验、渲染、归档行为完全不变，未追溯改写。

**投研意义增量**

3. 多一条可核实的连接：数字第一次带上单位、期间与范围，能被程序比较；SEC 的期间属性终于有落点。
4. 边界更清楚：非 GAAP 必须显式标 `adjusted`；分部必须写 `segment:<name>`；同一指标不许悄悄换单位或缩放。

**遗留**

- **模型输入与 metric 的一致性校验**（P1-0c）：模型输入引用了一条带 metric 的 observed claim 时，两者数值应当一致；但 wrapper 的 `scale` 是自由文本（million/billion），需要先定义缩放映射，否则会误报。等下一步再做。
- 冲突未处理：同组同期间但数值不同目前不报错（那是来源冲突，应由 P1-2 的 conflicts 记录负责），避免把正常的来源分歧当作错误。
- `comparison_with` 是单向声明即可，不强制双方互指；反向缺失不会报错。

## Cycle 2 · 2026-11-14 · 可复算的派生计算

**对应卡片**：P0-0a

**问题**：`report.calculations[]` 只校验结构、数值与引用，公式字符串不执行——除 5 个固定模型外，报告里所有派生数字都不可复算。实盘 run `R20261112T153326Z`（NVDA）把 FY27 EPS 与 P/E 写进 `result.unit` 字符串，`CAL1` 的 6 个输入只产出 2.43，而 9.22 / 17.9x 这两个真正的估值支点既不是输入也不是结果，任何校验都碰不到；`CAL2` 同样把三个百分比塞进一个 unit 字符串。

**改动**

| 文件 | 变更 |
| --- | --- |
| `scripts/calculations.py`（新） | 白名单算子 `ratio / growth / cagr / difference / sum / product`；单位契约；`ref` 引用更早计算（≤2 层，禁止前向/自引用）；`result.precision` 舍入；重算比对（默认相对 1e-9） |
| `scripts/render_report.py` | `validate_calculation_rows` 委托新模块；带 `op` 的行渲染「已按固定算子重算」「重算一致」，`ref` 输入显示 `= A1`；存在 op 行时追加一句说明；无 op 的报告输出字节不变 |
| `tests/test_calculations.py`（新） | 19 个用例：六个算子、单位契约、引用链、深度、前向/自引用、舍入、除零/负基数/溢出、未知算子、旧行兼容、渲染标注 |
| 文档 | memo-template 六算子表 + 可运行示例 + 「unit 只写单位」；architecture、development、CHANGELOG 0.7.1 |

**关键设计决定**：`ref` 解析到被引用行**记录**的 result 值，而不是内部未舍入的浮点。理由：报告的可核验性来自读者能看见的数字；若下游用内部全精度，读者按文档复现不出整条链。这个决定是在用真实 run 的数字做演示时发现的——用内部值算得 0.55278，按记录值算得 0.5529，前者会让一份「正确地四舍五入」的报告校验失败。

**验证证据**

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
# Ran 224 tests ... OK
```

- 冻结示例：`report.md` / `report.html` 重新渲染与冻结文件逐字节相同（215 个文件哈希校验通过）。
- 用实盘 NVDA 数字重建链路并通过校验：总跌幅 −32.14%、丑闻前段 −17.77%、占比 55.29%（与实际报告一致，但现在是可复算的）。
- 反向验证：把 55.29% 篡改为 60% → `calculations[2].result differs from deterministic recomputation`；把结果塞进 narrative unit → `growth result unit must be ratio`。
- 旧档案：NVDA 的 `CAL1`/`CAL2` 无 `op`，仍按原样加载、渲染、归档，不被追溯改写。

**投研意义增量**

3. 多一条可核实的连接：P/E、涨跌幅占比、预期差这类「多步派生数字」从「模型自己抄对了」变成「固定算子可重算、篡改即失败」。
4. 边界更清楚：算子数量与顺序固定、单位必须自洽、unit 不允许夹带第二个结果、缺 op 的行在文档与渲染中都被明确标为「仅记录」。

**遗留**

- 无 `op` 的行仍允许 narrative unit（旧档案必须保持可读）。下一步可加一个**非阻断 lint**（`calculations.py lint`）列出可疑 unit 与未标注公式，供研究者主动清理，而不是收紧校验破坏兼容。
- 算子顺序是位置式的：`ratio/growth` 为 a÷b、`cagr` 为 end/begin/years。已写进文档与表；错序通常会被重算比对拦住，但不是绝对。
- `percent` 结果不支持：百分比要写成 ratio（0.1493 而不是 14.93）。这是有意的，避免 ×100 歧义。

## Cycle 1 · 2026-11-14 · 相对估值（可比公司）

**对应卡片**：P0-1（已完成的原始排期）

**问题**：插件只有绝对估值（DCF / 反向 DCF）。`valuation` 问题被硬绑定到 `reverse_dcf`，而反向 DCF 要求正 FCF，直接抛错——亏损或周期底部的公司今天无法估值。分析师的第一个问题「相对可比公司贵不贵」没有工具可以回答。

**改动**

| 文件 | 变更 |
| --- | --- |
| `scripts/analysis_models.py` | 新增 kind `relative_valuation` 与 `peers` 输入；线性插值分位；输出 peer 分布、隐含 EV/股权/每股区间、`implied_multiple_at_price`、`price_vs_peer_median`；`peers` 出现在其它 kind 会报错 |
| `scripts/analysis_contract.py` | `METHODS.valuation.models` 增加该 kind；market.assessed 允许 `reverse_dcf` 或 `relative_valuation`；校验 `spec.peers` 结构与逐 peer 证据（fact/price/consensus）；要求 `peer_set_rationale`；price/instrument 绑定扩展到两种估值模型；输出 basis 必须覆盖 peer claims |
| `scripts/render_report.py` | 模型附录新增「可比公司选择」说明与「可比公司倍数」表；仅在 spec 含 peers 时输出，旧报告字节不变 |
| `tests/test_analysis_models.py` | 新增 `RelativeValuationTests`：分布与隐含值、顺序无关、单 peer、净现金、负隐含股权、metric>0、peer 结构/重名/类型/claim_ids、越界使用、溢出 |
| `tests/test_analysis_contract.py` | 新增 4 个用例：comps 支撑 valuation + 归档往返 + 双格式渲染；peer 证据缺失/类型错误/重名；result 篡改与 basis 不全；peers 用于非 comps 模型 |
| `tests/analysis_fixtures.py` | `add_model` 支持新 kind，输出 basis 改为由实际输入推导（更真实） |
| 文档 | analysis-methods（路由表、模型表、comps 语义与边界、可运行 spec 示例、market 规则）、memo-template、research-value、SKILL、README、architecture、CHANGELOG、版本 0.7.0 |

**验证证据**

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
# Ran 205 tests ... OK
```

- 算术抽查：metric=100、net_debt=20、shares=10、peers=[8,10,12,14] → median 11、q1 9.5、q3 12.5、隐含每股 108、区间 93–123、现价 15 隐含 1.7×、较可比中位折价 −86.1%。
- 冻结示例哈希：22 个文件全部匹配 `SHA256.json`；`render_report` 重新渲染 `report.md` / `report.html` 与冻结文件逐字节相同。
- `analysis_contract.py check` 对微软示例返回 `passed: true`。
- 归档往返：带 peers 的 valuation run 可 archive + load，`spec.peers` 原样保留，`report.md` 含可比公司表。

**投研意义增量**（对照 rubric）

1. 多一种分析师会用的方法：从「只能反推现金流」到「能相对可比集定价」，且能回答亏损标的。
2. 多回答一类问题：「现价隐含多少倍 EBITDA」「相对可比中位数折价多少」。
3. 多一条可核实连接：每个 peer 倍数必须引用 fact/price/consensus，输出 inference 的 basis 覆盖全部 peer claims，结果由固定算术重算。
4. 边界更清楚：metric 必须为正、口径必须与倍数匹配、n 与四分位必须披露、不产出目标价。

**遗留**

- 只有倍数分布的统计量，没有「目标公司当前倍数在 peer 分位中的位置」的显式输出（`implied_multiple_at_price` 可自行对照，但没有分位排名）。可在后续 comps 增强中补 `implied_multiple_percentile`。
- 审计指出更高优先级的两个缺口，已插入 backlog 作为 P0-0a / P0-0b，下一轮先做 P0-0a。
- `docs/development.md` 的测试基线已从 192 更新为 205。
