# 版本记录

[返回首页](README.md)

本页记录源码与研究协议演进。版本号不代表已部署到用户客户端，也不代表研究准确率或投资收益。

## 0.52.0 · 归档渲染回归与 CI 示例泛化

两处兼容性加固：

- `tests/test_archive_regression.py` 新增「重渲染每个真实归档并与冻结 `report.md` / `report.html` 逐字节比对」。本机 25 个归档全部一致——说明后续渲染器改动没有改变任何既有输出。CI 中会覆盖随仓库跟踪的归档。
- CI 不再硬编码微软案例：哈希校验、契约校验与渲染步骤改为遍历 `examples/*/`；新增示例自动纳入，README/TODO 里的「只测了一个例子」不再是隐患。
- 开发文档更新回归清单与 CI 描述。
- 测试：新增 1 个用例，全套 494 个测试通过。

## 0.51.0 · 第二个真实示例：分部利润归因

把上一轮的真实验收固化成可回归的示例 [examples/msft-segments](examples/msft-segments/README.md)：

- 新问题：FY2025 三大分部哪一块贡献了主要营业利润增长。结论是生产力与业务流程（+10,112），不是云（+6,776）；云的收入增量（+18,801）更大但利润增量更低。
- 内容：完整 plan / claims（12 条带 metric 的官方分部事实）/ sources（T0 年报分部表）/ report，`driver_build` 使用基期与情景利润率，重算合计 281,724 与 128,528、变化 19,095 与官报一致。
- 交付：同源 Markdown / HTML 与 `SHA256.json` 清单；根 README 与开发文档补入口。
- 测试：新增 [test_examples.py](tests/test_examples.py) 2 个用例——示例逐个校验契约并重渲染比对冻结产物；示例清单逐文件核对哈希。全套 493 个测试通过。
- 兼容：微软现金流示例的冻结产物与 CI 哈希不变。

## 0.50.0 · 分部基期利润率、模块改名与全链验收

本轮用真实分部数据跑完整研究链，发现并提出两处修复：

- **driver_build 新增可选 `base_margin`**：此前每个分部只有一个利润率，基期利润也用情景利润率计算，导致利润变化与增量利润率在利润率变化时失真。现在基期利润按 `base_margin`、情景利润按 `margin` 计算；缺省时保持旧行为。分部表在存在 `base_margin` 时新增「基期利润率 / 情景利润率」两列。
- **`calendar.py` 改名为 `catalyst_calendar.py`**：模块名与标准库 `calendar` 冲突，一旦环境先导入标准库，渲染器的懒加载就会失败。`scripts/calendar.py` 保留为兼容 CLI，命令不变；新增「先导入标准库 calendar 再导入渲染器」的回归测试。
- **真实数据验证加强**：微软分部复现测试现在同时断言营业利润变化等于 19,095，使用官方 FY2024 分部利润率作为 `base_margin`。
- 测试：新增 3 个用例（base_margin 分离、契约与渲染列、标准库同名遮蔽回归），全套 491 个测试通过。
- 文档：analysis-methods、architecture 与 catalysts 同步。

## 0.49.0 · 真实归档验收与路径修复

本轮按计划用真实研究跑完整流程，第一分钟就撞上一个真问题：**macOS 的临时目录在 `/var` 符号链接下，归档直接失败** `unsafe research runs directory`。

- 根因：安全校验拒绝了**任何祖先目录是符号链接**的路径。macOS `/var`、外置盘、链接的家目录都是合法位置，这条规则把正常用户挡在门外。
- 修复：只拒绝归档自己拥有的组件（`journal`、`journal/runs`）是符号链接，以及渲染输出目录本身是符号链接；祖先与父级符号链接放行。输入文件仍拒绝自身或其直接父目录是链接（保留重定向防护）。
- 验收：把微软示例归档到临时数据根、建一个更新 run（`judgment_changed=false`），`thread` 正确回溯 2 轮，`doctor` 2 个归档全部可加载，`memo_pack` 正常输出。
- `digest` 补一句边界：窗口按报告 `as_of` 计算，不是归档写入时间——补档历史研究不会落进当前窗口。
- 测试：新增 2 个用例（祖先符号链接可归档、输出目录父级符号链接可写），全套 486 个测试通过。

## 0.48.0 · 预期对照工具

研究里常同时出现两个「增长」：反向 DCF 的多年恒定隐含增长、共识相邻财年增幅。盘点指出它们目前只能手工对照，容易被当成同一口径相减。

- 新增 [expectation_compare.py](scripts/expectation_compare.py)：并列展示两侧，**强制标注期限不同、不可相减**；任一侧缺失时只展示已有侧并说明缺口，绝不合成单一「预期差」。
- 只读：从冻结报告读 reverse_dcf 结果，从账本读共识增长；不产生新数字、不改报告。
- 输出 JSON（含 horizons、gaps、notes）或 `--markdown` 表格；退出码 0/1/2。
- 测试：新增 [test_expectation_compare.py](tests/test_expectation_compare.py) 5 个用例（双侧、缺侧、Markdown、CLI 成败），全套 484 个测试通过。
- 文档：expectations 与 architecture 补说明。

## 0.47.0 · 一页纸完整度

盘点指出的两处 memo 缺口：

- 质量小节补「未挂 claim 的字段」——嵌入报告不再隐藏证据断点。
- 溯源小节补「图表 N 张：标题清单」——读者知道完整报告里有图，而不是以为没有。
- 两处都只在对应内容存在时出现；缺省时 memo 与之前完全一致。
- 测试：新增 2 个用例并扩展缺省断言，全套 479 个测试通过。
- 文档：memo-template 内容清单更新。

## 0.46.0 · 事件研究支持仅收益样本

盘点指出事件研究内嵌价格序列会让报告膨胀。原先计划把价格序列拆到归档新文件，但那会改动冻结文件清单、影响旧档案兼容；本轮改用更小的改动：

- 样本可以只写 `returns: {pre, post, total}`，不必带 `prices`。窗口覆盖由收集者负责（工具不再核对），汇总仍从样本收益重算。
- 体积对比：两个样本的文档从约 600 字节降到 269 字节；样本越多差距越大。
- 代价明确写进文档与输出 notes：returns-only 无法从价格逐点复核，需要复核时保留 `prices`；两种样本可以混用。
- 校验：`returns` 必须恰好含 pre/post/total 且为有限数值；形状错误、缺键、多余键都拒绝。
- 测试：新增 4 个事件研究用例与 1 个报告渲染用例，全套 477 个测试通过。
- 文档：event-study 参考补 returns-only 与取舍。

## 0.45.1 · 阶段性盘点（文档）

第 44 轮做了一次全量回顾，产出 [review-2026-11.md](docs/iteration/review-2026-11.md)：

- 规模：49 次提交、29 个脚本（8,641 行）、27 个测试文件、468 个用例、18 份参考文档。
- 能力→消费者矩阵：逐项列出生产者与下游读取者；结论是没有「写完没人读」的分析能力，三处弱消费（`implied_multiple_percentile`、`unattributed`、图表）都属于交付完整度问题。
- 十个最有价值的改动与已知弱点（含证据），并给出下一阶段排序：事件研究引用式存储 → memo 完整度 → 共识增长与反向 DCF 的受控对照 → 季度增长（暂缓）。
- 判断：方法层与交付层已完整，后续价值主要来自减少规模与完整性缺口，而不是再加方法。

本轮无代码行为变化，测试仍 468 个。

## 0.45.0 · 共识的相邻财年隐含增长

一致预期此前只能比较「同一目标期间的修订」，不能回答「共识自己预期明年增长多少」。

- 新增 `period_growth`：同一 `series_id`、同一提供方、年份连续（FY2026→FY2027）时，取各自最新快照的中位数计算隐含增长。
- 只在条件满足时计算：跨提供方、指标标签不一致、年份不连续、基期中位为零都跳过并给出 warning；非 FY 标签（如 next quarter、2027Q1）不推断。
- 报告附录在共识表后新增「相邻财年的隐含增长」表，并注明「这是共识自己的算术，不是研究判断」。
- 测试：新增 6 个单元用例与 1 个渲染用例，全套 468 个测试通过。
- 文档：expectations 与 memo-template 补说明。

## 0.44.0 · 堆叠柱状图

分组柱状能对比，但不能表达构成。新增 `chart.bar_mode`：

- `grouped`（默认）沿用分组柱状；`stacked` 变成堆叠柱状，自下而上按系列堆叠，用透明度区分系列。
- `stacked` 要求带 `series` 且所有值为非负——正负混合的堆叠柱会误导读者，直接拒绝。
- 图下注明堆叠顺序；同源数据表仍按系列展开，精确值以表为准。
- 兼容：`bar_mode` 缺省时输出不变，折线/单序列/分组柱状渲染字节相同。
- 测试：新增 2 个用例（堆叠渲染与双格式表格、三类负例），全套 461 个测试通过。
- 文档：memo-template 补 `bar_mode`。

## 0.43.1 · 别名冲突检测

上一版的别名表是「后者覆盖前者」：两个规范名共享同一别名时，结果取决于字典顺序，且没有任何提示。

- 冲突时按规范名字母序**先到先得**，并把冲突写进 index 的 `warnings`（例如 `alias 'nvidia' maps to both 'NVDA' and 'NVIDIA'`）。
- 别名值不是数组时只保留规范名本身，同样给 warning。
- 测试：新增 2 个用例（双向别名冲突、非法别名值），全套 459 个测试通过。
- 文档：research-memory 补冲突规则。

## 0.43.0 · 数据根体检 doctor

升级插件或迁移数据目录后，用户需要一个「先看看有没有坏」的入口。新增 [doctor.py](scripts/doctor.py)：

- 用当前校验器逐个加载 `journal/runs/` 的归档，任何不可读都列出具体 run 与错误。
- 重建研究记忆索引并报告实体数、别名数与跳过数；统计催化条目：带日期多少、无日期多少、相对参考时点已过期多少。
- 只读：不写缓存、不改归档、不自动修复；测试用哈希快照保证。
- 退出码：0 健康（允许 warning）、1 至少一个归档加载失败、2 数据根或 `journal/runs` 不存在。
- 测试：新增 [test_doctor.py](tests/test_doctor.py) 9 个用例（健康、过期、坏档、空目录、只读、CLI 退出码与环境变量默认根），全套 457 个测试通过。
- 文档：安装指南补「数据根体检」，architecture 入口表新增一行。

## 0.42.0 · 分组柱状图

`bar` 此前只能画单序列，分部同比对比只能并排两张图。现在 `kind: "bar"` 可以带 `series`：

- 每个标签一组，组内按系列从左到右排列，用填充透明度（由深到浅）区分——仍然不依赖颜色，兼容明暗主题。
- 图下列出系列顺序；同源数据表自动按系列展开成多列，精确值以表为准。
- `waterfall` 仍只允许单序列（桥没有分组语义）。
- 兼容：单序列柱状与折线的输出完全不变，冻结示例哈希继续通过。
- 测试：新增分组柱状用例、把「bar 不能带 series」的旧断言改为 waterfall，全套 448 个测试通过。

## 0.41.0 · 用真实报表验证固定模型

测试此前只能证明「模型按定义运行」，不能证明「定义本身合理」。本轮拿微软 FY2024/FY2025 已披露的损益与分部数据做端到端复现：

- `operating_bridge`：基期收入 245,122、营业利润率 44.64%、增长 14.93%、情景利润率 45.62% → 收入 281,724、营业利润 128,528、利润变化 19,095，且收入效应 + 利润率效应恰等于变化量。
- `driver_build`：三大分部（PBP / Intelligent Cloud / More Personal Computing）用实际收入增速与 FY2025 分部营业利润率 → 总收入 281,724、营业利润 128,528、增量利润率约 46.3%。
- 新增 [segments.json](examples/msft-quality/segments.json) 记录分部收入与营业利润（来源：已冻结官方表格）。两条回归进入 `tests/test_analysis_models.py`，全套 447 个测试通过。
- 示例 README 补「用固定模型复现官方报表」一节。

## 0.40.0 · 实体别名

同一标的在不同 run 里常写成 `NVDA` / `NVIDIA` / `英伟达`，记忆索引把它们当成三个实体，查询也就分裂了。

- 数据根下可放 `journal/aliases.json`：`{"NVDA": ["NVIDIA", "英伟达"]}`，规范名 + 别名数组，大小写不敏感。
- `index` 按规范名归并 `entities`，并输出可审计的 `alias_map`；`query` 命中任一别名都会返回该实体的全部 run。
- 别名文件缺失不影响功能；损坏或不是对象时忽略并写入 `warnings`，索引照常构建。
- 别名只影响检索与分组，不改归档里的原始 entity，也不做语义消歧。
- 测试：新增 4 个用例（归并、别名查询三写法、幂等、损坏文件降级），全套 445 个测试通过。
- 文档：research-memory 增「实体别名」章节。

## 0.39.0 · 基期标签窄校验

上一轮要求不同窗口时填写 `period`，但标签本身没校验：窗口是 FY2025、标签写 FY2024A 也能通过。

- 规则（只做窄检查，不解析自由文本）：标签形如「FY2025A」时，年份必须等于窗口起始或结束年；形如「2025Q3」时，年份必须落在窗口内；没有年份的标签（如「基期口径」）不检查。
- 目的：抓明显的年份笔误与错配，不引入财年末月份猜测（FY 结束月份因公司而异，猜会误伤）。
- 测试：新增 1 个用例（FY/季度/自由标签通过路径 + 两类年份不符），全套 441 个测试通过。

## 0.38.0 · 一页纸引用参考类分布

事件研究已经能嵌入报告，但一页纸仍然不展示。现在若报告嵌入 `event_study`，memo 增加「参考类事件」小节：

- 事件类型与窗口（观测点）；后窗与全窗的 n、中位、为正比例、Q1—Q3。
- 被跳过的样本数（窗口不足或事件日缺失）随行提示，细节留在完整报告。
- 末尾固定写明「绝对收益、样本事前选定、不给 p 值；参考类分布不是预测」。
- 数据仍从冻结输入重算；缺省时 memo 与原来完全一致。
- 测试：新增 1 个用例并扩展缺省断言，全套 440 个测试通过。

## 0.37.0 · 估值汇总的基期披露

DCF 用 FY2025 基期、comps 用 FY2026E 倍数，两者并列在「方法区间」里本身没问题——但读者必须知道。此前 `valuation_summary` 没有任何地方记录基期。

- 规则：当被比较模型的 `period_window` 不完全一致时，每一行必须补 `period` 文本（如 FY2025A / FY2026E）；缺了直接失败。
- 渲染：只要任一行写了 `period`，表格多一列「期间」；没有该字段的汇总表列不变（冻结示例不受影响）。
- memo：方法区间里把 `period` 附在方法名后，一页纸也能看到基期。
- 测试：新增 2 个用例（窗口不同时强制披露与渲染、窗口相同时不要求），全套 439 个测试通过。
- 文档：analysis-methods 与 memo-template 补规则。

## 0.36.1 · 归档兼容回归测试

新增 [tests/test_archive_regression.py](tests/test_archive_regression.py)：加载 `journal/runs/` 下每个真实归档，断言全部能被当前校验器读取，并用文件哈希快照证明加载过程不修改归档。

- 覆盖真实数据：本机 25 个归档、CI 16 个（随仓库跟踪数量）；任一新契约让旧档案不可读都会直接失败。
- 只读：不写缓存、不改 manifest；CRC 由各 run 的 manifest 负责，这里只验证「可加载 + 未改动」。
- 开发文档的回归清单补上这项检查。
- 全套 437 个测试通过。

## 0.36.0 · 摘要按问题合并

用真实归档跑验收时发现：本机 25 轮研究只对应 15 个问题，其中一个问题跑了 7 轮。`digest.py` 原来逐轮平铺，读者会把重跑误读成「跨期多次确认」。

- 「本窗口研究」改为按问题合并：显示最新一轮的判断与标题，其余轮次折叠为「同题 N 轮（另：run ids）；结论版本 M 个」。
- 结论版本数按判断原文去重，能一眼看出「同一问题跑了几次、结论变过几次」。
- 边界新增一句：重复实验不等于多次独立验证。
- 测试：新增同题三轮（结论两个版本）用例，全套 435 个测试通过。

## 0.35.0 · 质量表打磨

两处遗留收口：

- 应计比率：有上期总资产时改用**期初期末平均**（`(净利润−CFO) ÷ 平均总资产`），只有单期资产时退回期末总资产；口径写进输出 notes 与文档。
- 未挂证据可见：嵌入报告的「盈利质量」小节新增一行「未挂 claim 的字段」，按期间列出没有 `claim_ids` 的字段——嵌入场景同样能看到证据链断点，而不是被渲染抹掉。
- 测试：应计改平均后更新断言；新增「未挂字段」渲染用例，全套 434 个测试通过。
- 文档：financial-quality 与 memo-template 同步。

## 0.34.0 · 模型期间窗口

模型 wrapper 的 `period` 一直是自由文本，无法核对「这个输入到底属于哪一期」。新增可选 `period_window`：

- 结构：`{start, end, period_type?}`，ISO 日期，start 不晚于 end，period_type 取 fy / quarter / ltm / instant；未知字段拒绝。
- 校验：一旦写了窗口，observed 输入所引用 claim 的 `metric` 期间必须落在窗口内（period_end 不晚于 end、period_start 不早于 start），且 period_type 与窗口一致。
- 兼容：不写 `period_window` 的模型行为完全不变；`period` 仍作为人读描述保留，二者不应互相矛盾。
- 测试：新增 2 个用例（期间越界与类型不一致、窗口形状五类负例），全套 432 个测试通过。
- 文档：analysis-methods 与 memo-template 补字段规则。

## 0.33.0 · 事件研究嵌入报告

参考类事件研究此前是独立脚本产物。新增可选 `report.event_study`，字段与 event_study 输入完全一致（event / window / samples）：

- 校验：复用 `event_study.validate_document`，核对样本 `claim_ids` 是否存在，并要求至少两条可用样本（覆盖不足时直接失败，而不是渲染一张空分布）。
- 渲染：附录新增「事件研究」小节——参考类收益分布（n、中位、均值、Q1/Q3、min/max、为正比例）与样本明细，附「绝对收益、样本事前选定、不给 p 值；参考类分布不是预测」的说明。
- 兼容：没有该字段的报告渲染字节不变，冻结示例哈希继续通过。
- 测试：新增 3 个用例（校验与双格式渲染、四类负例含可用样本不足、无字段兼容），全套 430 个测试通过。
- 文档：memo-template 与 event-study 参考补嵌入说明。

## 0.32.0 · 一页纸引用瓶颈与红旗

报告已经能嵌入传导图与质量报表，但一页纸 memo 仍只讲判断与区间。现在：

- 若报告嵌入 `transmission`：memo 增加「传导瓶颈」小节——瓶颈节点与理由、源头到瓶颈的路径、以及无关节点/环路提示。
- 若报告嵌入 `quality`：memo 增加「质量红旗」小节——按严重度排序取前五条，超出部分写「其余 N 条见完整报告」；无红旗时明确写「未触发默认阈值；这不等于没有风险」。
- 数据仍只从冻结输入重算，不在 memo 里手写数值；两节缺省时 memo 与原来完全一致。
- 测试：新增 3 个用例（瓶颈、红旗与阈值覆盖、默认无两节），全套 427 个测试通过。

## 0.31.0 · 盈利质量嵌入报告

盈利质量筛查此前是独立脚本，结论与报表不随报告归档。新增可选 `report.quality = {statements, thresholds?}`：

- `statements` 与 financial_quality 的输入完全一致，字段值可为裸数字或 `{value, claim_ids}`；`thresholds` 覆盖默认阈值（已知键名、(0,1]）。
- 校验：报表结构复用 `financial_quality.validate_document`，并逐字段核对 `claim_ids` 是否存在；未知字段、未知阈值键、非法阈值都失败。
- 渲染：附录新增「盈利质量」小节——关键指标表（毛利率/营业利润率/净利率/现金转化/应计/资本开支/SBC/ROIC）、环比变化表（收入增长、利润率变化、增量利润率、周转变化、股本变化）与红旗清单；指标在渲染时由嵌入输入重新计算，不冻结结论。
- 兼容：没有该字段的报告渲染字节不变，冻结示例哈希继续通过。
- 测试：新增 4 个用例（校验与渲染、阈值覆盖、六类负例、无字段兼容），全套 420 个测试通过。
- 文档：memo-template 与 financial-quality 参考补嵌入说明。

## 0.30.0 · 传导图嵌入报告

行业传导图此前是独立产物，研究结论与链条不在同一份档案里。新增可选 `report.transmission`：结构与[transmission.md](skills/research/references/transmission.md)的输入完全一致，嵌入后随报告一起归档与渲染。

- 校验：复用 `transmission.validate_document`，并用账本核对节点、边与瓶颈的 `claim_ids` 是否真实存在；未知引用直接失败（错误前缀 `transmission:`）。
- 渲染：附录生成「行业传导」小节——瓶颈与理由、节点表（节点/标签/方向/可观察指标）、传导路径、以及无关节点/环路/无证据告警。
- 兼容：没有该字段的报告渲染字节不变，冻结示例哈希继续通过。
- 测试：新增 3 个用例（校验与双格式渲染、三类负例、无字段兼容），全套 416 个测试通过。
- 文档：memo-template 与 transmission 参考补嵌入说明。

## 0.29.0 · 能力地图与维护清单

插件已有 20 多个脚本与 17 份参考文档，新读者和后续迭代都容易找不到入口。本轮只做导航与维护规范，不改研究契约：

- README 新增「能力地图」：九个常见问题 → 用什么回答 → 对应参考文档（贵不贵、增长是否现金、预期修订、催化、历史判断、同类事件、行业传导、数字可核、一页纸）。
- 新增 [参考文件索引](skills/research/references/README.md)，按「定义问题与取证 / 分析方法与计算 / 交付与延续」分组，每份文件一句话用途；SKILL 顶部指向该索引。
- `docs/development.md` 新增「新增能力的检查清单」：脚本 docstring 与退出码、测试正反边界、向后兼容、参考文档与索引、architecture 入口、版本与 changelog 三方一致、回归命令、不伪造原则。
- 测试：既有 [test_packaging.py](tests/test_packaging.py) 自动检查 README/architecture 链接可解析、manifest 版本与 CHANGELOG 最新条目一致；全套 413 个测试通过。

## 0.28.0 · 柱状与瀑布图

折线适合趋势，不适合「分部贡献」与「利润桥」。`chart` / `charts[]` 新增可选 `kind`：

- `bar`：单序列柱状，支持负值（自动以 0 为基准画轴）；不能与 `series` 同时使用。
- `waterfall`：每行必须声明 `role`（`total` 或 `delta`），首行必须是 `total`，后续每个 `total` 必须等于前面累计值——桥的算术由校验器自己检查，写错直接失败。
- 渲染：总计与变动用不同填充与虚线边框区分；瀑布的连接线用虚线；同源数据表标签自动补「合计/变动」。
- 兼容：`kind` 缺省为 `line`，所有旧图表渲染不变，冻结示例哈希继续通过。
- 测试：新增 5 个用例（柱状含负值、瀑布自检、累计不匹配、kind/series/role 负例、折线不回归），全套 413 个测试通过。
- 文档：memo-template 补 `kind`、`role` 与自检规则。

## 0.27.0 · 多轮研究摘要 digest

单轮查询回答「某标的」，但没有一页纸回答「这两周我们做了什么、接下来要看什么」。新增 [digest.py](scripts/digest.py)：

- 判断变化：窗口内 `judgment_changed=true` 的 run 与判断原文。
- 本窗口研究：窗口内全部 run，按截点倒序，附实体与判断。
- 未来 30 天催化：从各 run 的 trigger/watch 取有 `due` 且落在未来 30 天的条目，带距今天数。
- 过期未核对：`due` 已过但未记录核对的条目，并注明「过期不等于未触发」。
- 参数：`--as-of`（窗口终点）、`--days`（窗口长度，默认 30）、`--out`；退出码 0/1/2。
- 边界：没有 `due` 的观察项不进催化小节；摘要只复制冻结内容，不新增证据、不给建议。
- 测试：新增 [test_digest.py](tests/test_digest.py) 7 个用例（窗口、变化、催化、过期、空催化、参数、CLI），全套 408 个测试通过。

## 0.26.0 · 模型输入与 metric 的数值一致性

模型 observed 输入引用 claim 时，只校验了 claim 类型，数值从不比对：一条「收入 1200」的 claim 可以被当成「capex 60」的证据写进模型，两边都能通过校验。本轮把这条链接上。

- 量纲：`metric.unit` 映射为 currency / ratio / shares / currency/share，与输入 unit 不一致直接失败——引用了错误证据。
- 数值：量纲一致时用 wrapper.scale 与 metric.scale 的换算倍数对齐量级再比较，误差超过 1e-9 失败；price 输入不走金额缩放，只比每股数值。
- 不猜：缩放文本无法解析或任一侧缺 scale 时跳过并保持通过，宁可标为无法核对，也不制造假错误。
- 兼容：旧归档的 claim 没有 metric 块，完全不触发；有 metric 的 claim 若未被模型引用，也不受影响。
- 测试：新增 4 个用例（金额匹配/数值不符/量纲不符/缩放不可解析、股本匹配与不符、每股匹配与不符），全套 401 个测试通过。

## 0.25.0 · 行业传导图

主题研究里「需求 → 产能 → 交付 → 毛利」通常是一段话，断点靠感觉。新增 [transmission.py](scripts/transmission.py)：把传导链变成可校验的图。

- 节点：安全 id、标签、种类（demand/capex/capacity/price/margin/policy/cash/other）、至少一条可观察指标、可选 claim_ids。
- 边：from/to、机制、时滞；自环、重复边、悬空引用直接拒绝；环路只提示不判错。
- 瓶颈：明确一个节点与理由；输出每个节点相对瓶颈的方向（upstream / downstream / bottleneck / unrelated）、到瓶颈的跳数、从各源头到瓶颈的路径。
- 告警：无关节点、环路、未挂 claim_ids 的节点；配合 `--claims` 可核对引用是否真实存在。
- 边界：不判断机制真假；跳数不是时间（时滞在各边 lag 里，不可加总）；瓶颈由研究者指定。
- 测试：新增 [test_transmission.py](tests/test_transmission.py) 11 个用例（形状、引用、方向/距离/路径、多源头、无关节点、环路、无证据节点、CLI），全套 398 个测试通过。
- 文档：[transmission.md](skills/research/references/transmission.md) 含完整示例、输出说明与边界。

## 0.24.0 · 判断沿革（thread）

研究记忆已经记录每轮的 `parent_run`，但没有把它变成可读的沿革。新增 `research_memory.py thread --home DIR <run_id>`：

- 按 `parent_run` 从目标轮回溯到最早一轮，输出旧→新的 `lineage`：判断原文、`judgment_changed`、模型种类、机会状态与深度；同时给出该轮的直接子轮。
- 分支更新各子轮是并列关系，不拼成时间线；缺失父轮时沿革在已知处停止；异常自引用/循环有访问集合保护，不会死循环。
- 未知 run 退出 1；缺 home 退出 2；与 `index/query` 一致只读、不写盘。
- 测试：新增 6 个用例（三轮回溯、子轮、未知 run、缺父轮、循环保护、CLI），全套 383 个测试通过。
- 文档：research-memory 增加「判断沿革」章节。

## 0.23.0 · 多图容器 charts[]

`report.chart` 只能放一张图，而一份报告经常需要「趋势」「分部结构」「估值对照」三张。新增可选 `report.charts[]`：

- 每个元素与 `chart` 同构（单序列或 `series` 多序列），各自校验、各自渲染，并按数组顺序排列。
- `chart` 与 `charts` 不能同时出现，避免顺序歧义；单图报告完全保持原行为。
- 每张图仍自动生成同源数据表（单序列两列、多序列每序列一列），Markdown 中读者看到的是按序排列的数据表，HTML 中是按序排列的图 + 表。
- 测试：新增 3 个用例（双图校验与双格式渲染、5 类负例、单图不回归），全套 377 个测试通过；冻结示例哈希不变。

## 0.22.0 · 一页式 IC memo

完整报告是档案，但读者常先要一页。新增 [memo_pack.py](scripts/memo_pack.py)：从冻结报告、claims 与 sources 裁剪出 memo.md。

- 内容：判断、最多三条关键发现、方法区间（数字只从冻结模型输出读）、有日期的催化、改变判断的条件（tests 的 supports_if/weakens_if 与 watch）、主要风险（material limitations 与备选解释）与溯源。
- 校验：先跑与渲染相同的全套校验，不过就失败；`--claims` 必填，`--max-findings` 控制条数；不新增证据、不产生新数字、不改 report.json。
- 转义：只转义会改变行内 Markdown 结构的字符；连字符、全角括号保持可读；表格单元额外转义竖线。
- 测试：新增 [test_memo_pack.py](tests/test_memo_pack.py) 8 个用例（结构、条数上限、估值读数一致、有日期催化、转义、CLI 成功与失败），全套 374 个测试通过。
- 文档：memo-template 增一页纸章节，architecture 补入口。

## 0.21.0 · 多序列图表

报告图表此前只能画一条序列，而「收入与利润率一起看」「标的与基准对比」恰恰需要多条。`report.chart` 新增可选 `series`：

- 结构：`series: [{name, rows: [{label, value}]}]` 替代 `rows`；各序列的 label 必须完全一致（共享横轴），单位共享；`rows` 与 `series` 不能同时出现。
- 渲染：同一缩放内画多条折线，以实线/虚线区分（不依赖颜色，兼容明暗主题与色觉差异），图下列出系列名，精确数值仍由同源数据表承载；单序列图完全保留原有悬停读数与键盘交互。
- 一致性：同源数据表自动变为「期间 + 每个序列一列」，仍从同一份 `series` 生成，不手写。
- 测试：新增 3 个用例（校验与双格式渲染、7 类负例、单序列交互不回归），全套 366 个测试通过；冻结示例哈希不变。
- 文档：memo-template 补 `series` 用法。

## 0.20.0 · 参考类事件研究

「历史上这类事件之后怎么走」此前只能靠印象或一次性举例。新增 [event_study.py](scripts/event_study.py)：在**事前选定**的样本上计算事件窗口收益分布。

- 输入：事件定义、`window.before/after`（**观测点**而非自然日，after≥1、上限 250）、多条样本（事件日期 + 严格递增的价格序列 + 可选 claim_ids）。
- 输出：每条样本的 pre / post / total 收益与端点价格；`n`、均值、中位、四分位、min/max、上涨占比；窗口不足或事件日缺失的样本进入 `skipped` 并写明原因；可用样本少于两条直接失败。
- 边界：绝对收益而非超额收益；**不输出 p 值或显著性结论**；样本事前选定，工具无法阻止事后筛选，但会留下完整样本与 skipped 记录供审查。
- 文档：[event-study.md](skills/research/references/event-study.md) 说明输入、计算口径、边界与在事件预测/变化解释中的用法。
- 测试：新增 [test_event_study.py](tests/test_event_study.py) 11 个用例（窗口边界、样本校验、收益与分位、跳过原因、不足两条、CLI），全套 363 个测试通过。

## 0.19.0 · 块级渲染：内联表格与列级单位

报告里最重要的表常常讲的是某一条发现，但它此前只能出现在正文末尾的统一表格区，读者要来回跳。两处小改动解决这个问题，同时不改变任何未被使用的旧报告：

- `tables[]` 支持可选安全 `id`；`findings[].table_ids` 引用后，该表内联渲染在对应发现之后，并从正文表格区移除，避免重复。未引用的表顺序与输出不变。
- `tables[]` 支持可选 `units`（与 `columns` 等长，空字符串表示该列无单位），渲染为「列名（单位）」，Markdown 与 HTML 同源。
- 校验：`id` 唯一且安全、`units` 长度与列数一致且为文本、`table_ids` 非空去重且必须解析到带 id 的表；未知引用直接失败而不是静默丢表。
- 测试：新增 3 个用例（校验负例、内联只渲染一次且顺序正确、未引用表输出不变），全套 352 个测试通过；冻结示例哈希不变。
- 文档：memo-template 补 `table_ids` / `units` 用法。

## 0.18.0 · 从主张账本装配质量报表

`financial_quality.py` 需要一份标准化报表文档；手写它等于把转录风险搬回来。新增 [quality_inputs.py](scripts/quality_inputs.py)，从账本里的 `claim.metric` 直接装配，字段仍指回 claim id。

- 映射：中英文指标名按别名表映射到 17 个报名字段（「营业收入」→revenue、SBC→share_based_comp、D&A→depreciation_amortization 等），映射不到的不猜，列进 `ignored`。
- 期间：只取 fy / quarter / ltm 且同时有 `period_start`/`period_end`、`scope=consolidated` 的 metric；`instant`、分部、缺日期都会被跳过并写明原因。
- 冲突：同一期间同一字段两个不同数值直接失败并列出；数值相同则合并 claim id。
- 口径：`currency`/`scale` 必须唯一可推断，否则用 `--currency`/`--scale` 显式给出；`tax_rate` 的 percent 自动换算为小数；多实体需 `--entity`；至少两个可比期间。
- 输出保留 `claim_ids`/`source_claims`，因此 `financial_quality` 的 `unattributed` 为空——数字真的接回了证据。
- 测试：新增 [test_quality_inputs.py](tests/test_quality_inputs.py) 9 个用例（装配、别名与换算、忽略原因、冲突、合并、结构失败、口径、CLI 端到端），全套 349 个测试通过。
- 文档：financial-quality 增「从主张账本装配」，evidence 与 architecture 补入口。

## 0.17.1 · 可比公司分位补齐

`relative_valuation` 已经给出「现价隐含多少倍」，但没说这个倍数在 peer 分布里处于什么位置。新增 `implied_multiple_percentile`：现价隐含倍数严格高于多少 proportion 的 peer 倍数（0 表示最低，1 表示最高）。

- 计算：`count(peer_multiple < implied_multiple_at_price) / peer_count`，严格小于，遇并列给出保守分位。
- 渲染：沿用模型输出表，无需新表；comps 文档补充字段说明。
- 测试：新增分位用例（最低 0、并列 0.25、中位 0.5、最高 1.0），全套 340 个测试通过。

## 0.17.0 · 一致预期序列与指引分离

`expectations.md` 早就要求「同一目标期间在两个截点比较」，也要求「不用公司指引冒充分析师共识」，但此前没有结构化字段：修订只能手算，指引与共识混在文本里。

- `consensus` claim 可带可选 `consensus` 块：`series_id`、`metric`、`target_period`、`provider`、`sample_size`（≥2）、`median`、`low`、`high`，要求 `low ≤ median ≤ high`，未知字段拒绝。
- `fact` claim 可带可选 `guidance` 块：`metric`、`target_period`、`midpoint`、可选 `low`/`high`。**硬规则：`guidance` 不允许出现在 consensus 主张上**，直接报错。
- 新工具 [consensus.py](scripts/consensus.py)：按 `series_id + target_period` 分组，按截点排序，输出 `delta`、`pct`、`up/down/flat` 与离散度 `(high−low)/|median|`；跨提供方、指标名不一致、单快照都会进 `warnings`；指引单独列出。
- 渲染：附录新增「一致预期序列」与「公司指引（不是分析师共识）」两张表，无相关块时输出不变。
- 测试：新增 [test_consensus.py](tests/test_consensus.py) 16 个用例（块校验、类型硬规则、ledger 接入、修订/排序/离散度/零中位、提供方混用、CLI、双格式渲染），全套 339 个测试通过。
- 文档：evidence、expectations、memo-template、architecture 同步。

## 0.16.0 · 情景集（bear / base / bull）

研究人员常需要三个情景，但此前只能建三个互不相干的模型：无法保证结构一致，也没有并排对比。新增可选的 `scenario` 与 `scenario_set` wrapper 字段。

- 契约：同一 `scenario_set` 至少两个模型、必须含 `bear` 与 `bull`、情景不重复、`spec.kind` 一致、假设输入集合相同，且每个情景至少有一个 assumption 输入；缺失任一条件直接拒绝。
- 渲染：模型标题标注情景（`[情景 bear]`），附录末尾新增「情景对比」表，只列各情景共有的输出；注明「情景之间不是概率加权，不计算期望值、不给概率」。
- 兼容：没有 scenario 字段的模型输出与渲染完全不变，冻结示例哈希继续通过。
- 测试：新增 4 个契约用例（正向渲染、结构失败、kind/假设不一致、零假设），全套 322 个测试通过。
- 文档：analysis-methods、memo-template、SKILL 同步。

## 0.15.0 · 龙卷风敏感性

单参数敏感性此前平铺成一张「变量 / 改为 / 输出 / 结果」的长表，读者看不出哪个假设最要紧。新增可选 `tornado` 块：指定一个输出，把每个输入推到 low/high 两端，按输出变动幅度排序。

- 模型：`spec.tornado = {output, inputs:[{input, low, high}]}`，每个模型须有 `sensitivity` 或 `tornado` 之一；`output` 必须是该模型确实输出的名称且在被扫两端都存在；`reverse_dcf` 不能扫 `growth_low` / `growth_high` / `years`。
- 输出：`result.tornado` 逐行给出输入、两端取值、两端输出与 `swing`，按 `swing` 降序；无 tornado 的模型结果结构不变。
- 渲染：附录新增「龙卷风敏感性（按影响排序）」表，并注明「逐项移动一个输入，不是联合情景」。
- 测试：新增 6 个模型用例与 4 个契约用例（排序与正算一致、单独使用、校验、求解边界、输出在端点缺失、篡改重算），全套 319 个测试通过。
- 文档：analysis-methods、memo-template、SKILL 同步。

## 0.14.0 · 价格时效与来源冲突

两处证据处理此前靠人记得：市场评估可以用一份很旧的报价当「现价」；同一指标多个来源数值不一致时，报告里通常只留下被采用的那一个，分歧消失。

- 价格时效：`status=assessed`时校验所引 price claim 的 `market_quote.quoted_at` 与 `claim.as_of` 的间隔，超过 `market.price_max_age_hours`（默认 96 小时，覆盖周末；日内研究可收紧）直接失败。历史研究把截点设在当时，报价与截点同时代即可。阈值须为 1–8760 的数值。
- 来源冲突：新增可选 `report.conflicts[]`，记录 `metric`、`unit`、至少两个不同数值的 `candidates`（含 `source_id`）、`adopted_claim_id`、`rule` 与 `reason`。采用主张须是 fact/price/consensus；若其带 `metric`，unit 必须一致、value 必须等于某个候选值。附录新增「来源冲突与取舍」表。
- 兼容：没有 `conflicts` 字段的报告渲染字节不变，冻结示例哈希继续通过。
- 测试：新增 [test_freshness_conflicts.py](tests/test_freshness_conflicts.py) 11 个用例（新鲜度边界与阈值、无 sources 时跳过、冲突形状/证据/数值匹配、双格式渲染），全套 310 个测试通过。
- 文档：analysis-methods 补价格时效规则，memo-template 补 conflicts 契约，SKILL 与研究价值参考同步。

## 0.13.0 · 跨轮研究记忆

研究是接力的，但此前只能逐个打开归档才知道「关于这个标的，上一轮判断了什么、依据多少主张、后来改没改」。新增 [research_memory.py](scripts/research_memory.py)：把 `journal/runs/` 整理成只存指针的索引，支持按实体/关键词与当时视角查询。

- `index`：重建 `journal/index.json`（约 25 个真实归档秒级完成），记录 run_id、截点、标题、问题、实体、判断原文、机会状态、父 run、判断是否变化、主张数、指标名、模型种类、触发 id 与 due、报告哈希；坏档进入 `skipped` 并写明原因。
- `query`：大小写不敏感子串匹配（标题、问题、任务、实体、指标名、发现标题、判断原文），`--as-of` 给「当时我们知道什么」的视角，`--limit` 限制条数，结果按截点倒序。
- 确定性：索引可重建、幂等（连续两次输出逐字节相同），`index_hash` 只覆盖索引内容；查询不写盘。
- 边界：索引只存指针，不合并数字、不新建主张、不改归档；旧 inference 不能直接支撑新结论；实体抽取是文本匹配，会漏会多。
- 文档：[research-memory.md](skills/research/references/research-memory.md) 说明字段、查询与边界；SKILL 要求在开始研究或更新前先查记忆。
- 测试：新增 [test_research_memory.py](tests/test_research_memory.py) 10 个用例（索引、跳过坏档、实体、幂等、归档不被改动、查询、CLI、真实归档只读回归），全套 299 个测试通过。

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
