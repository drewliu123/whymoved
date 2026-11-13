# 版本记录

[返回首页](README.md)

本页记录源码与研究协议演进。版本号不代表已部署到用户客户端，也不代表研究准确率或投资收益。

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
