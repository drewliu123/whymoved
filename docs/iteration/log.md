# 迭代记录（Log）

每轮一条，倒序不必要——按时间正序追加，方便读演进。格式：目标 → 改动 → 验证证据 → 对投研意义的增量 → 遗留。

---

## Cycle 9 · 2026-11-14 · 价格时效与来源冲突

**对应卡片**：P1-2

**问题**：两处证据处理靠人记得。第一，市场评估可以用一份很旧的报价当「现价」——现有校验只禁止「报价晚于主张」，不禁止「报价太早」。第二，同一指标多个来源数值不一致时，报告通常只留下被采用的那一个，分歧与取舍理由消失。

**改动**

| 文件 | 变更 |
| --- | --- |
| `scripts/analysis_contract.py` | 市场评估新增价格时效校验：`quoted_at` 与 `claim.as_of` 间隔不得超过 `market.price_max_age_hours`（默认 96，1–8760）；无 sources 时跳过 |
| `scripts/render_report.py` | 新增可选 `report.conflicts[]` 的校验与附录渲染：候选来源值、采用主张、单位、规则、理由 |
| `tests/test_freshness_conflicts.py`（新） | 11 个用例：新鲜/过期报价、96 小时边界与自定义阈值、非法阈值、无 sources 跳过、冲突形状、采用主张类型、metric 数值与单位匹配、双格式渲染、无冲突兼容 |
| 文档 | analysis-methods 价格时效规则；memo-template conflicts 契约；SKILL 与研究价值参考同步；CHANGELOG 0.14.0 |

**关键设计决定**

1. **默认 96 小时而不是 24**：股票周末与长假会让 24 小时规则误伤正常的周一报告；日内/加密研究应在 `market.price_max_age_hours` 显式收紧到 24。规则可调比硬编码更不容易被绕过或误伤。
2. **只约束市场评估**：历史研究把 `as_of` 设在当时，报价与截点同时代即可；不把「旧报价」一律判错，避免把回溯研究逼成造假。
3. **冲突必须数值真的不同**：两个候选相同值不叫冲突，直接拒绝；否则这个字段会变成表演性严谨。
4. **采用主张要能对上**：若 adopted claim 带 `claim.metric`，其 unit 必须与冲突单位一致、value 必须等于某个候选值——防止「记录了冲突，采用的却是第三个数字」。
5. **无 sources 时不静默通过吗？** `validate_analysis` 在无 sources 调用时无法取报价时间，只能跳过并明确这是调用路径限制；归档与渲染路径都带 sources，检查是生效的。

**验证证据**

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
# Ran 310 tests ... OK
```

- 时效：报价晚于截点 0 小时通过；正好 96 小时通过；96.5 小时失败 `quotes a 96.5 hour old price; max is 96`；把阈值改 1000 后 200 小时也通过。
- 阈值：0 / 10000 / True / "24" / None 全部拒绝。
- 冲突：两个来源 12 vs 10 通过并渲染「来源冲突与取舍」；同值拒绝；未知 source / 未知 adopted claim / inference 采用 / 缺 unit / 多余字段 / 字符串数值全部拒绝；采用主张 metric=12 与候选 11 不一致时失败；unit 为 percent 与冲突单位不符时失败。
- 冻结示例：`report.md` / `report.html` 逐字节相同，22 个文件哈希匹配。

**投研意义增量**

1. 多一条证据纪律：过期报价不再能撑起「当前价格隐含什么」的判断。
2. 多一条可核实连接：来源分歧有结构化记录，读者能看到未采用的数字与取舍规则。
3. 边界更清楚：历史研究不被误伤，日内研究可显式收紧。

**遗留**

- 时效目前只覆盖市场评估的 price claim；consensus（如 45 天）与 filing（一个报告期）的陈旧度仍未系统检查。
- conflicts 只做记录与校验，不会自动比对 claims 里的同名 metric 值；下一步可让 `claim.metric` 同名同口径的差异自动提示登记冲突。
- 未提供「冲突未解决」的阻断级别；当前是可选项，靠研究纪律使用。

## Cycle 8 · 2026-11-14 · 跨轮研究记忆（research memory）

**对应卡片**：P0-6

**问题**：研究是接力的，但此前只能逐个打开归档才知道「关于这个标的，上一轮判断了什么、依据多少主张、后来改没改」。没有实体索引，也没有「当时视角」。这是「持续性投研」与一次性截图的区别，也是唯一能防事后诸葛的机制。

**改动**

| 文件 | 变更 |
| --- | --- |
| `scripts/research_memory.py`（新） | `index` 重建指针索引（run_id、截点、标题、问题、实体、判断原文、机会状态、父 run、判断变化、主张数、指标名、模型种类、触发 id/due、报告哈希）；`query` 子串检索 + `--as-of` 当时视角 + `--limit`；坏档进 `skipped` |
| `tests/test_research_memory.py`（新） | 10 个用例：索引与跳过、实体、幂等与逐字节稳定、归档不被改动、查询过滤/排序/限制/无匹配、CLI 退出码、真实归档只读回归 |
| 文档 | 新增 [research-memory.md](../../skills/research/references/research-memory.md)；SKILL 要求研究/更新前先查；architecture 入口；CHANGELOG 0.13.0 |

**关键设计决定**

1. **只存指针**：索引复制判断原文用于检索，但明确「引用旧判断必须回冻结 run 读 claims/sources，旧 inference 不能直接支撑新结论」。不合并数字、不新建主张。
2. **`--as-of` 是核心功能**：回答「当时我们知道什么」，而不是用今天的结论回头解释过去。
3. **幂等可重建**：连续两次 `index` 输出逐字节相同，`index_hash` 只覆盖索引内容；查询完全不写盘。测试用归档文件哈希快照证明读索引没有改动原件。
4. **坏档不静默**：缺 report.json 或 JSON 损坏的 run 进入 `skipped` 并写明原因，索引其余部分照常可用。
5. **实体来源显式**：`plan.entity` 为主，`claim.metric.entity` 补充（同业、对手方），不做猜测式消歧；查询是子串匹配，会漏会多，文档写明。

**验证证据**

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
# Ran 299 tests ... OK
```

- 本机真实归档：25 个 run 全部索引成功、0 跳过；`query BTC` 命中 BTC run，返回判断原文、`opportunity_status=watch`、3 个 trigger（`due` 为空串——该 run 没有日期）、`claim_count=12`、`report_sha256` 完整。
- 幂等：连续两次构建结果相等；写入两次文件逐字节相同。
- 归档安全：索引前后 `journal/runs/**` 所有文件哈希完全一致。
- 冻结示例：`report.md` / `report.html` 仍逐字节相同，22 个文件哈希匹配。

**投研意义增量**

1. 多一种持续性工作流：研究之间可以接力，而不是每次从零。
2. 多回答一类问题：「我们之前对 X 判断过什么、依据多少证据、后来改了吗」。
3. 多一条可核实连接：每条记忆带 run_id 与报告哈希，随时可回到原件。
4. 边界更清楚：指针不是证据、不合并数字、实体匹配会漏会多。

**遗留**

- 尚无「同一论点的跨轮时间线」视图：目前按 run 列出判断，未把连续更新串成一条 thread（`parent_run` 已入索引，可在此基础上做）。
- 增量索引未做，每次全量重建；对当前规模（25 run）无影响。
- 实体消歧仍靠文本；若未来出现大量同名实体，需要显式别名表。
- 查询结果不含 claim id 列表，只给数量；需要逐条证据时回原件。

## Cycle 7 · 2026-11-14 · 催化日历（共用触发 id）

**对应卡片**：P0-5

**问题**：报告里「12 月 9 日 FOMC 是下一个催化」只是散文。`opportunity.triggers` 有 id、有 `by`（自由文本），但没有可计算日期，无法排序、无法回答「上周该看的东西看了吗」；非交易研究的 `watch` 连 id 都没有。审计同时警告：不能为此新建第二套触发系统。

**改动**

| 文件 | 变更 |
| --- | --- |
| `scripts/calendar.py`（新） | 校验 `due`/`type`（可选）；从 trigger 与 watch 抽取条目；`build_calendar` 分 upcoming / overdue / undated 并按日期排序；CLI 支持报告路径、run 目录、`--home`、`--as-of`、`--due N` |
| `scripts/render_report.py` | `validate_report` 接入催化字段校验 |
| `tests/test_calendar.py`（新） | 13 个用例：可选字段、非法/过期日期、类型枚举、抽取保留 id、状态与排序、horizon、无 as_of、CLI 单文件/目录/home/退出码 |
| 文档 | 新增 [catalysts.md](../../skills/research/references/catalysts.md)（字段、查询、边界）；research-value 的 triggers 行补 due/type；SKILL 与 architecture 补入口；CHANGELOG 0.12.0 |

**关键设计决定**

1. **扩展而非新建**：trigger id 留在 `opportunity.triggers`，watch 用位置编号 W1..Wn；日历只是视图。审计的警告（两套触发体系会 id 漂移）被直接规避。
2. **`by` 与 `due` 并存**：`by` 是人读窗口（「12/9 附近」），`due` 是可计算日期。脚本绝不从自由文本猜日期——旧 run 的触发全部进 `undated`，这是诚实状态。
3. **过期不等于未触发**：`overdue` 只表示观察时点已过、报告没有记录核对；命中与否仍须写进 `update.opportunity.trigger_results` 并附证据。文档把这条写成硬边界。
4. **过去日期在冻结时被拒绝，在复查时变成 overdue**：校验要求 `due >= report.as_of`（冻结时不能写一个已经过期的「未来催化」）；用更晚的 `--as-of` 查询时它自然进入 overdue。两个动作合起来才是完整的过期语义。
5. **不改归档**：日历只读，不写状态、不提醒、不轮询。

**验证证据**

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
# Ran 289 tests ... OK
```

- 用真实用户归档验证兼容性：`calendar.py journal/runs/R20261112T165159Z-... --as-of 2026-11-14` 读出 6 条 trigger，全部进入 `undated`（该 run 只有自由文本 `by`），`run_id` 从 manifest 正确解析。
- 状态与排序：`due` 11-20 / 12-01 / 12-09 在 11-14 视角按日期排序；把 `--as-of` 推到 12-10，三条全部变 overdue。
- `--due 10` 只保留 10 天内到期的 upcoming；`undated` 不参与过滤。
- 冻结示例：`report.md` / `report.html` 逐字节相同，22 个文件哈希全部匹配。

**投研意义增量**

1. 多一种投研工作流：从「文中的催化」到「可排序、可复查的日历」。
2. 多回答一类问题：「接下来 30 天有什么会改变判断」「哪些该看的已经过期没核对」。
3. 多一条可核实连接：每条催化带 claim_ids 与所属 run。
4. 边界更清楚：不监控、不自动判命中、不猜日期。

**遗留**

- 日历还没有把 update 的 `trigger_results` 合并进来显示「已核对/未核对」状态；下一步可让 `calendar.py` 读取父子 run 并按 trigger id 关联。
- 旧 run 的 `by` 文本无法批量转成 `due`；迁移只能靠研究者逐条补，不自动化。
- `watch` 的位置编号在条目增删后会漂移；需要稳定引用时应改用 opportunity.triggers。

## Cycle 6 · 2026-11-14 · 估值汇总（football field）+ 发布一致性

**对应卡片**：P0-4

**问题**：DCF、comps、反向 DCF 各自躺在附录，读者要自己对照；正文手抄模型数字既可能走样，也无法被程序核对。IC 需要的是一张「方法 → 区间 → 相对现价 → 口径」的表，同时不能变成加权的目标价。

**改动**

| 文件 | 变更 |
| --- | --- |
| `scripts/render_report.py` | 新增 `valuation_summary` 校验与渲染：行只能引用 `model_id`/`label`/`metric`，数值全部从冻结模型读取；DCF 区间取敏感性扫描、comps 取四分位、反向 DCF 单列隐含增长率；脚注声明不加权、不给概率、不是目标价 |
| `tests/test_analysis_contract.py` | 3 个用例：只读模型 + 归档往返 + 双格式渲染；行内自带数字/未知模型/重复模型/metric 不匹配/价格漂移均拒绝 |
| `tests/test_packaging.py`（新） | 4 个发布一致性用例：两个 manifest 版本一致、CHANGELOG 最新条目与版本一致、architecture 脚本链接存在、README 相对链接存在 |
| 文档 | memo-template 新增「估值汇总：只读模型输出」；analysis-methods 与 SKILL 指明用法；CHANGELOG 0.11.0；版本 0.11.0 |

**关键设计决定**

1. **汇总节不允许有数字**：任何 `low`/`mid`/`high` 字段直接拒绝，只能写 `model_id` 与 `metric`。这是把「数字必须可重算」这条原则延伸到交付层——汇总表不能成为手抄的后门。
2. **价格从模型输入取**：汇总里的「相对现价」用模型 `price` 输入的值与单位；所有模型引用的价格必须一致，否则拒绝。避免在汇总里再写一个可能过期的价格。
3. **不做加权**：列只到「中位相对现价」，没有综合分、没有概率、没有目标价；反向 DCF 行明确标注是预期不是估值。

**过程事故与修复（值得记录）**

Cycle 5 的 CHANGELOG 条目**没有真正写入**：那条命令先用 `json.loads` 读 manifest 再追加 CHANGELOG，而 Cycle 4 的版本脚本把字面量 `\n` 写进了 JSON，导致 `json.loads` 抛错、脚本在写 CHANGELOG 之前就中止；我只看到 stderr 里的 traceback 没有逐条核对产物，就提交了。结果 0.10.0 条目缺失、测试基线停在 258，直到本轮更新文档时发现。

修复：补写 0.10.0 与 0.11.0 两条记录、恢复基线，并新增 [test_packaging.py](../../tests/test_packaging.py)——版本号、CHANGELOG 最新条目、文档链接现在由测试强制一致，同类「发布了但没记录」不会再静默通过。另修复 manifest 里的字面量换行，JSON 恢复合法。

**验证证据**

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
# Ran 276 tests ... OK
```

- 汇总渲染：三个模型（DCF/comps/反向 DCF）并排，正文出现「估值汇总」「方法区间对照」「每股价值」「隐含增长率」「参考现价」「不跨方法加权」「不能直接相加」。
- 负例：`rows[0].low = 1` → `must only name model_id, label and metric`；`model_id="M404"` → `must reference an analysis model`；`metric="implied_growth"` 用在 DCF 上 → `metric must be one of per_share`；两个模型价格 15 vs 16 → `requires one observed price`。
- 冻结示例：`report.md` / `report.html` 仍逐字节相同。
- 发布一致性：manifest 版本、CHANGELOG 最新条目、architecture/README 链接全部由测试覆盖。

**投研意义增量**

1. 多一种交付形态：从「三张附录表」到「一张方法对照表」，判断可直接落在区间相对现价的位置上。
2. 多一条可核实连接：汇总数字无法手写，只能来自已重算的模型输出。
3. 边界更清楚：明确禁止加权、概率与目标价，反向 DCF 被标为预期。

**遗留**

- DCF 的区间来自单参数敏感性，不是联合区间；真正的情景区间见 P1-3。
- 汇总不显示「主导假设」列；如果未来模型 wrapper 增加结构化的关键假设字段，可补。
- 发布一致性测试只覆盖 manifest/CHANGELOG/文档链接，不校验 `evidence/` 历史记录（那些不应重写）。

## Cycle 5 · 2026-11-14 · 驱动式经营模型（driver_build）

**对应卡片**：P0-3

**问题**：`operating_bridge` 只有收入增长与利润率两个标量，文档自己写明不含量价归因；分部、量价、增量利润率只能写成一句假设，再对这句假设做敏感性——用精确的桥包装未拆解的假设。

**改动**

| 文件 | 变更 |
| --- | --- |
| `scripts/analysis_models.py` | 新增 `driver_build`：`segments` 数组（name、base_revenue、volume_growth、price_growth、margin、claim_ids）+ 标量 `margin_delta`；输出收入、利润与四项效应 |
| `scripts/analysis_contract.py` | `operating_outlook` 接受该模型；每段证据必须同时含 observed 与假设两类；段校验（重名、负基数、增长率 ≤ −1、类型）；`segments` 越界使用报错 |
| `scripts/render_report.py` | 模型附录新增「分部驱动」表；无 segments 的报告字节不变 |
| 测试 | 模型用例 7 个（恒等式、单分部、零增长、负利润率、越界、区间、敏感性），契约用例 4 个（支撑 operating_outlook、证据缺失、越界、篡改重算） |
| 文档 | analysis-methods（模型表、恒等式、边界）、SKILL、memo-template、CHANGELOG 0.10.0 |

**关键设计决定**

1. **恒等式而不是近似**：`base×(1+v)(1+p) = base + volume_effect + price_effect + interaction_effect`，三项效应之和必须精确等于收入变化。第一版把 `price_effect` 写成 `base×(1+v)×p`，等于把交互项算了两遍；测试的恒等式断言当场暴露，改成 `base×p` 后才成立。这类原子级错误正是确定性模型存在的理由。
2. **每段必须两类证据**：基期收入来自 fact/price/consensus，驱动（量、价、利润率）来自 inference/view。只有一类直接失败——防止把拍脑袋的分部拆解伪装成披露数据。
3. **只保留一个标量输入**：`margin_delta` 表示统一利润率冲击，必须写成 assumption 并在 wrapper 解释。分部驱动本身不进 `inputs`，避免把「敏感性能扫所有分部参数」的错觉写进契约（那需要真正的多维情景，见 P1-3）。
4. **边界写清**：分部独立、不建模共享成本与转移价、margin 是营业利润率、margin_delta 不是概率加权情景。

**验证证据**

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
# Ran 269 tests ... OK
```

- 虚构两分部（100 @ +10% 量 / +5% 价 / 20% 利润率；50 @ −10% 量 / +2% 价 / 10% 利润率）：
  收入 161.4（基期 150）、收入变化 11.4、效应 5 + 6 + 0.4 = 11.4 精确相等、利润 27.69、利润变化 2.69、增量利润率 23.6%。
- `margin_delta = −0.02` → 利润 27.69 − 0.02×161.4 = 24.462，收入不变。
- 契约负例：段只引 inference（缺 observed）→ `must include the observed base`；只引 observed（缺驱动）→ `must include the evidenced drivers`；`segments` 用于 DCF → `only supported by driver_build`；篡改收入 → `differs from deterministic recomputation`。
- 冻结示例：`report.md` / `report.html` 仍逐字节相同。
- 真实过程 bug：新增的 `claim_types` 局部变量最初命名为 `kinds`，遮蔽了模型 kind 集合，导致所有 operating_outlook 模型被判「与研究方法不匹配」；新增契约测试立刻抓到，已改名并复测。

**投研意义增量**

1. 多一种分析师会用的方法：分部量价拆解 + 增量利润率，而不是只给收入一个增长率。
2. 多回答一类问题：「增长来自量还是价」「新增收入到底创造了多少利润」「哪个分部在拖累利润率」。
3. 多一条可核实连接：每段基期收入与驱动分别挂到主张，恒等式由代码重算。
4. 边界更清楚：单参数扫描不被说成情景分析，分部口径与共享成本限制写进文档。

**遗留**

- 分部表只展示驱动，不展示每段收入/利润贡献；下一步可以在渲染里补一列派生值（不新增输出结构）。
- 敏感性只能扫全局 `margin_delta`，不能扫单个分部的量价；真正的多参数情景见 P1-3。
- SOTP 仍不做：需要分部估值倍数与资产清单，假精度风险高。

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
