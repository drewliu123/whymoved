# 迭代记录（Log）

每轮一条，倒序不必要——按时间正序追加，方便读演进。格式：目标 → 改动 → 验证证据 → 对投研意义的增量 → 遗留。

---

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
