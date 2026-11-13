# 迭代记录（Log）

每轮一条，倒序不必要——按时间正序追加，方便读演进。格式：目标 → 改动 → 验证证据 → 对投研意义的增量 → 遗留。

---

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
