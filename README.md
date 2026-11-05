# 投研助手

围绕研究问题工作的本地Claude Code插件，源码版本0.6.0。它把官方数据、预期、独立报道、机构分析与社区线索连接起来，给出当前判断、重要发现及下一项会改变判断的观察；同一冻结内容生成Markdown和HTML，并可更新旧研究。

0.6.0增加美股SEC取证入口`scripts/sec_data.py`：标准库入口借独立Python3.11+运行EdgarTools5.62.1，按精确accession读取完整主文件/章节和原始报表，保留SEC出处、接受时间与原始期间口径。历史取证按真实接受时间筛选；获取包仍须核对原文件引文、定位和时间依据后进入sources/claims。行情等原有Financial Datasets入口保留。接入说明见[SEC数据参考](skills/research/references/sec-data.md)，真实季报、历史截点与证据链验证见[evidence/sec-integration-20261102/](evidence/sec-integration-20261102/README.md)。

0.5.1在方法选择之前加入[意图核对](skills/research/references/intent.md)：结合原问、相关用户上下文和最新纠正，区分实际值查询、预测与合约决策辅助；类似预测市场标题的短问先查匹配合约，核对年份与结算口径，再研究档位、含费成本、深度和独立判断。用户纠正后重新定题，red-team直接对照原话审查，不能只验收研究者缩窄的计划。明确只查官方实际值走简答路径；纯事实不强套分析契约或新研究归档。非交易预测以官方结果定义为核验目标。部分回答与答错任务分开裁定，改变主判断后的最终稿须聚焦复审。本次修改研究与审查提示词，不新增关键词分类器、不改变历史归档schema；语义识别由执行模型承担，回归案例不等于泛化保证。案例与运行办法见[意图回归](tests/intent/README.md)。

0.5.0将研究价值放到主线：价格相关研究明确市场押注、我们的分歧、证据优势、催化和剩余空间/做错代价，按优先研究、等待触发、价格已反映、未见优势排序。市场代理估计可支持有方向的条件判断，但须引用推断，不能冒充调查共识或已验证的价格隐含值。重要限制说明对判断或机会的具体影响，不以免责声明替代答案。

新增可选`report.opportunity.version=1`，主流程要求交易研究使用；旧报告与纯事实研究保持兼容。更新逐项核对父报告触发，记录判断强弱、价格变化和剩余机会，支持方向、幅度、时点、机制与价格兑现的分开复盘。协议和输出示例见[研究价值参考](skills/research/references/research-value.md)。记录和校验不自动判断机会是否存在，也不产生实时行情、后台监控或投资收益证明。

0.4.0增加四处分析升级：明确问题与方法匹配、区分竞争解释的检验、确定性经济模型及敏感性、市场隐含预期与研究假设比较。新研究归档强制分析契约，固定模型会在校验、渲染和归档时重算；旧归档仍按原格式读取，不追溯补写结论。

0.4.1补充[背景与变化研究顺序](skills/research/references/context.md)：按相关性检查长期条件、近期环境、事前预期、新增变化与传导、后续验证，并接入计划、取证和审查。沿用现有schema；这是研究与写作要求，不是自动背景采集或新的语义校验器。五层检查保留在底稿，正文仍为简明短评。离线样例只能验证给定材料下的组织与表达，联网取证效果需另行实测。

研究建议，不提供针对个人的买卖与配置指令。

## 获取完整项目

本仓库包含插件源码、测试、研究资料、证据及历史报告。第三方 EdgarTools 源码以固定提交的 Git 子模块保存；首次下载请使用 `git clone --recurse-submodules git@github.com:drewliu123/whymoved.git`。已有克隆可运行 `git submodule update --init --recursive` 获取第三方源码。Python 虚拟环境、系统缓存和本地凭据不入库，依赖运行时按下文说明配置。

## 使用

```text
/touyan:research 英伟达这个月为什么下跌？先比较行业表现，再判断公司特有因素
/touyan:research AI用电如何进入电力设备利润？找最值得验证的传导环节
/touyan:research update <run_id> 核对新增披露是否改变原判断
/touyan:research review
```

默认采用专业简明的研究短评：先给当前判断与关键数据，再解释主要驱动和传导机制，最后说明哪些观察会改变判断。面向对投研有兴趣、但不预设金融背景的读者；必要术语首次出现时简要解释。简单问题几段讲清，复杂问题按需展开；用户可要求更通俗、更深入或其他风格。完整Markdown/HTML保留展开的证据与计算，聊天与报告共享冻结结论。

普通研究不要求登记概率。只有明确要求可裁决预测/复盘时，进入保留的forecast/journal流程。

## 本轮改造的研究链

1. 定义用户要解决的判断、时间、比较基准与候选解释。
2. 按缺口检索：T0官方、T1调查/预期、T2独立报道、T3机构机制、T4社区线索。
3. 保存全部候选、引擎原排名、原文定位、日期、原始出处家族和选择理由。相关性与证据资格分别处理，不按热度覆盖原排名。
4. 主研究者连接事实、计算和竞争解释，逐项说明相对原文/基准/旧判断的增量。
5. 严格v2结论校验与独立研究审查，优先修会改变主判断的问题。
6. 同源Markdown/HTML、可展开证据、按需图表与数据表、不可覆盖研究归档。
7. 用户触发更新：保留旧run、新建子run，比较新增/修订/移除的证据与结论，记录判断是否改变及比较口径。

报告先回答问题，重大限制紧邻主判断。没有改变判断的新信息可以直接报告。脚本校验结构、引用、时间、来源资格与固定模型数值；原文含义和经济因果仍需要研究审查。

## 四处分析升级

| 能力 | 执行与验收 |
|---|---|
| 问题与方法匹配 | 从变化解释、经营展望、估值、事件预测、主题传导、承诺核对六种意图中明确选路由；冻结方法、理由、基准及机制链，错误匹配的新归档失败 |
| 区分竞争解释 | 每个解释写不同的可观察预测；关键查询绑定检验，报告保留事前预测、观察、支持/削弱和下一检验。missing状态不得裁定支持或削弱 |
| 可复算经济模型 | 营业利润桥、自由现金流、DCF、反向DCF四个固定模型；区分观察值与情景假设，记录假设理由、币种、共同缩放、期间和范围；至少两个不同参数值的单参数敏感性，结果篡改拒绝 |
| 市场隐含预期 | 涉及价格时记录隐含预期、研究假设、差异和翻转条件；估值必须关联反向DCF，报价数值、币种和证券与证据一致。缺数据直接披露missing；非价格研究说明不适用 |

详细字段、适用边界及可运行示例见[分析方法参考](skills/research/references/analysis-methods.md)。路由基于研究者显式选择，不自动理解自然语言问题；固定模型校验不证明假设合理或因果成立，反向估值的增长率也不是市场参与者的一致预测。

```bash
python3 scripts/analysis_contract.py route valuation
```

```bash
python3 scripts/analysis_models.py <model-spec.json>
```

```bash
python3 scripts/analysis_contract.py check --plan <plan.json> --report <report.json> --claims <claims.json> --sources <sources.json>
```

新计划仍是schema2，增加`analysis_version=1`与`research_design`；报告增加`analysis.version=1`，模型输入和重算结果直接冻结在`report.analysis.models`。新归档不接受缺分析契约的旧输入；加载旧归档保留兼容。模型缺失不等于计算通过，市场缺失不等于预期已验证，两者在Markdown/HTML显式展示。

涉及预期差、财报/宏观发布、事件概率和预期修订时，主Skill与取证Agent按[预期取证参考](skills/research/references/expectations.md)选择调查、市场定价、财报共识和历史快照，核对事前公开时间。0.3.2新增该检索指导；未新增数据连接器或修改校验schema，也不代表已实测所列入口。新对话显式调用`/touyan:research`可加载已安装版本的流程；源码文件修改本身不会更新插件缓存。

## 目录与CLI

| 路径 | 职责 |
|---|---|
| skills/research/SKILL.md | 主研究流程 |
| skills/research/references/ | 四类方法、来源选择、证据/报告契约、可选旧预测 |
| agents/ | 原始取证、社区线索、研究审查、可选冻结证据预测 |
| scripts/sec_data.py | 标准库SEC取证入口，独立EdgarTools运行时，输出原始获取包 |
| scripts/research_plan.py | 问题/比较/检索计划及新版分析设计校验 |
| scripts/analysis_contract.py | 六类问题路由、区分性检验、模型与市场预期契约 |
| scripts/analysis_models.py | 四个确定性经济模型及单参数敏感性重算 |
| scripts/sources.py | 来源契约、确定性选择审计、Last30Days导入 |
| scripts/check_claims.py | schema1兼容及schema2严格整账本校验 |
| scripts/render_report.py | 冻结report.json生成Markdown/HTML |
| scripts/opportunity_contract.py | 机会判断、证据依据类型、触发与父报告更新一致性 |
| scripts/opportunities.py | 只读汇总最新归档机会与触发，按研究优先级列出；--history保留历史 |
| scripts/research_run.py | archive/update/show/list/diff，hash清单与不可覆盖归档 |
| scripts/forecast.py、journal.py、authors.py | 保留的概率、到期复盘与作者评分 |
| scripts/polymarket.py | 原有Gamma只读参考值查询，严格v2需补选项/报价时刻/盘口 |
| tests/ | 标准库自动测试，隔离数据目录 |
| evidence/rebuild-20261031/ | 本轮基线、验证、示范与限制说明 |

```bash
python3 scripts/research_plan.py <plan.json>
```

```bash
python3 scripts/sources.py import-last30days <raw.json> --out <candidates.json>
```

```bash
python3 scripts/sources.py select <sources.json> --out <selected-sources.json>
```

```bash
python3 scripts/check_claims.py <claims.json> --sources <sources.json> --json
```

```bash
python3 scripts/render_report.py <report.json> --claims <claims.json> --sources <sources.json> --out-dir <output>
```

```bash
python3 scripts/research_run.py archive --report <report.json> --claims <claims.json> --sources <sources.json> --plan <plan.json>
```

新归档仅接受claims schema2及新版分析契约；旧schema1兼容渲染带显式标识，旧研究归档与预测账本仍可读取。可用--audit冻结查询、执行和审查记录JSON。update使用相同完整新输入，改命令为update并加--parent-run；report必须记录update判断与可比性。旧式自由公式计算文件仍可通过--calculations附加，其公式只作透明记录，不执行任意表达式，也不声称自动重算；0.4.0的固定模型单独保存在report.analysis.models，会自动重算。show/list读取归档，diff增加analysis_changed，但结构变化不等于经济意义判断。

## 数据与兼容

TOUYAN_HOME指定数据根，默认`~/Desktop/投研助手`。新研究：`journal/runs/<run_id>/`；工作输入：`journal/work/`。新归档不写`journal/memos.jsonl`或`data/authors.json`，无预测也可归档。旧journal add/due/grade/stats与schema1继续使用原格式，旧档案不按新规则重判。主动执行旧grade仍会写旧评分账本。

测试/示范使用隔离TOUYAN_HOME。本轮源码改造不会自动覆盖已安装副本或热加载当前会话。

## 可选金融数据接口

新增Python标准库适配器`scripts/financial_data.py`，按Dexter的公开端点契约调用Financial Datasets：利润表、资产负债表、现金流量表、三表合并和当前行情快照。它复用数据接口，不运行Dexter的Agent；自然语言路由及新闻暂未接入该适配器；SEC原始披露另走下述EdgarTools入口。用法与证据边界见[金融接口参考](skills/research/references/financial-data.md)。

```bash
python3 scripts/financial_data.py income AAPL --period annual --limit 5
```

正常调用从进程环境读取`FINANCIAL_DATASETS_API_KEY`；未配置返回not_run。可用`--public-probe`确认不带Key时的访问状态，不执行付款。本轮公开实测AAPL利润表与行情快照均返回HTTP 402；授权后的真实数据尚未验证。测试使用模拟响应，不把它当作真实数据成功。获取包需核对证券、口径和出处后进入现有sources/claims流程，具体见参考文档。此改动尚未应用到已安装插件缓存。

## SEC原始披露接口

美股SEC取证使用`scripts/sec_data.py`，先doctor检查运行时，再filings定位精确accession，document读取完整主文件/章节，statements读取原始报表。获取操作支持`--out NEW_JSON`（拒覆盖）、`--timeout secs`与带时区`--as-of RFC3339`；精确文件也按真实接受时间拒绝未来/未知时间。输出统一为`provider: edgartools`的status/data/provenance/completeness获取包，不直接创建sources/claims。

```bash
python3 scripts/sec_data.py doctor
python3 scripts/sec_data.py filings NVDA --form 10-Q --limit 5
```

独立Python3.11+与EdgarTools5.62.1路径从`TOUYAN_HOME/data/sec-runtime.json`的python/site_packages读取；配置不含身份，`EDGAR_IDENTITY`仅取调用进程环境，不复用测试邮箱。缺身份或运行时记not_run，partial/错误不得视为ok。SEC原文件、完整章节、报表原始期间/YTD/quarter、concept与分部、T0引文/定位及独立时间依据等要求见[SEC数据参考](skills/research/references/sec-data.md)。EdgarTools解析与同一SEC源不双计独立来源，报表不自动推导单季值。

## Last30Days与运行时

插件入口Python3.9+，只用标准库；SEC解析另由独立Python3.11+的EdgarTools运行时执行。社区取证优先复用可选[Last30Days](https://github.com/mvanhorn/last30days-skill)引擎，已对3.30.0 raw契约适配；引擎需独立Python3.12+。

引擎负责多平台召回、原始排序、去重和聚类。适配器保存raw、items_by_source、ranked_candidates、clusters及完整状态，再补原文与研究选择，不复制其认证代码。平台失败、部分失败与无结果分别记录；未知结构拒绝兼容。不是所有平台的完整召回。

TOUYAN_HOME不隔离引擎cache/last-run；即使--save-dir为空也可能写缓存。平台可用性由当次diagnose与实际source_status决定。无引擎时可用限定域名网页搜索补查，但需明确降级，不能宣称跑过引擎。

## 安装和更新

本目录是本地插件源码，尚未配置GitHub仓库。首次添加市场：

```bash
claude plugin marketplace add ~/Desktop/投研助手
```

```bash
claude plugin install touyan@touyan-local
```

已安装用户自行应用新版源码：

```bash
claude plugin marketplace update touyan-local
```

```bash
claude plugin update touyan@touyan-local
```

完成更新后开启新会话确认版本。安装状态以实际插件命令结果及缓存版本为准，不能仅凭源码版本认定更新已生效。

## 验证与能力边界

实际测试入口：

```bash
python3 -m unittest discover -s tests
```

研究综合仍依赖主模型和当前检索条件。严格校验不证明来源真实、引文语义或机制正确；来源家族、相关性和增量需要有依据的研究者判断。已开发的四例属于回归样本，不能证明泛化优势。没有公平对照、前瞻评分和成本测量时，不宣称优于专业研究员或有预测alpha。

潜在长期价值来自可追溯判断历史、跨来源矛盾与承诺核对、少重复阅读；本版提供记录和更新基础，不承诺后台自动跟踪。完整的实际验证结果见本轮evidence，不把未运行项目当通过。
