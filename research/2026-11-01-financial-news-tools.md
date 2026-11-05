# 交易与投研数据源、GitHub 项目及 MCP 选型调研

调研日期：2026-11-01。核查方式：公开 GitHub README、供应商官方文档及价格页。未安装项目，未配置凭据，未调用付费数据接口，未实测新闻完整性、到达延迟或历史回填。下文的推荐是接入候选优先级，不是生产可用性认证。

## 判断与推荐原则

最有价值的组合是：社区线索发现 + 持续新闻监测 + 官方披露核验 + 行情与宏观数据。Last30Days 能做好第一项，但一个工具很难同时解决全部四项。

需要区分四类东西：

- 数据源：交易所、监管机构、统计机构、媒体与数据供应商。
- 数据接口和客户端：将上述来源变成可查询数据，例如 API、Python SDK。
- 接入工具：MCP server、插件、Skill，将数据交给 AI 使用。
- 采集和存储系统：RSS 聚合、数据库、定时采集，决定自己能积累多少可复查的历史。

同一个 Finnhub API 的多个 MCP 包装器仍是一个来源；多家媒体转载同一通讯社的新闻，也不能当成多个独立证据。

## 新闻与线索工具

| 项目 | 用途及推荐判断 | 覆盖、历史和费用边界 |
|---|---|---|
| [mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill) | 优先保留。跨社区研究近期观点、争论、关注度及新线索；可作为 Skill/插件接入。 | README 描述 Reddit、X、YouTube、HN、Polymarket、GitHub 等多种来源；可用性取决于渠道、凭据和依赖。默认研究近30天不等于每个渠道都能完整回溯30天，官方 X 常规搜索的历史窗口尤其需要核对。MIT 代码许可证不代表拥有内容转载权。 |
| [sansan0/TrendRadar](https://github.com/sansan0/TrendRadar) | 中文资讯持续监测的优先候选。聚合热榜、RSS、关键词过滤、去重、通知，并提供查询已采集数据的 MCP。 | 热榜依赖 [ourongxing/newsnow](https://github.com/ourongxing/newsnow)；另有 RSS/Atom 采集。支持本地 SQLite、远程对象存储等路径。未证明能自动补齐采集启动前的历史。热榜可能漏掉低热度但重要的交易事件。GPL-3.0。 |
| [alex9smith/gdelt-doc-api](https://github.com/alex9smith/gdelt-doc-api) | 全球地缘政治、能源、贸易、产业事件的免费检索候选。Python 客户端，适合程序查询。 | 检索新闻元数据、来源、国家、语言、覆盖量及语气。ArticleList 单次最多250条；README 的可靠历史窗口与 GDELT 历年文档表述存在差异，长期回溯应按实际接口验证。返回元数据不等于获得全文。MIT。 |
| [cyanheads/gdelt-mcp-server](https://github.com/cyanheads/gdelt-mcp-server) | 希望 AI 直接查 GDELT 时可评估的社区 MCP。 | 提供新闻搜索、覆盖趋势、语气、语言/地区分析及电视相关工具。是第三方包装器；无 GDELT API key 要求，但有上游限流、返回数量和缓存限制。Apache-2.0。 |
| [Finlight MCP / callbk/finlight-mcp](https://github.com/callbk/finlight-mcp) | 美股与全球财经新闻的轻量付费试点候选。支持 ticker、来源、语言、国家、日期等过滤，以及情绪/公司标签。 | 需要供应商账号和额度。价格页的免费档为5,000次/月、延迟12小时、1个月历史；Pro Light 为29美元/月、10,000次/月、标称实时。Pro Light 的历史权限在价格页不同位置存在冲突，购买前需确认。仓库 MIT；全文、再分发权限和新闻覆盖完整性另核验。 |
| [Finnhub 官方 MCP](https://finnhub.io/static/finnhub-how-to-connect-mcp-server.html) | 需要新闻、公司资料、财务、预期和行情的统一入口时优先看官方服务。 | 官方说明包含 newsroom、press_releases 等工具；OAuth 授权，数据范围和额度取决于订阅。官方托管 MCP 不等于代码开源。优先比较它与社区包装器是否提供相同数据。 |
| [Benzinga API](https://docs.benzinga.com/home) | 美股公司事件、分析师评级、新闻等交易相关信息的商业候选。 | 新闻 API 文档推荐用 updatedSince 增量取数；历史权限和费用应按合同/API产品确认。官方 MCP 公告的搜索结果描述 API 发现与示例查询，不能据此当作直接返回实时新闻的 MCP。公告正文抓取返回403，未完成全文核验。 |

### 全球事件库的边界

[GDELT 官方数据页](https://www.gdeltproject.org/data.html)描述 GDELT 2.0 Events/GKG 每15分钟更新，并提供原始文件与 BigQuery 查询路径。Events/GKG 是结构化事件与实体主题数据；DOC 是新闻检索接口。它们的数据结构、历史范围和取数方式不同。

官方较早的 DOC 更新公告允许更长历史搜索；Python 客户端和 MCP 包装器又写有各自窗口限制。因此本报告不把“仅能查最近3个月”当成 GDELT 整体的统一限制，也不承诺任意历史区间都能完整获取文章。底层数据开放不代表 BigQuery 查询计算免费。

## 中文资讯与历史数据库

| 项目 | 推荐用途 | 接入与限制 |
|---|---|---|
| [金十官方 MCP](https://mcp.jin10.com/app/doc.html) | 中文宏观、外汇及大宗商品相关快讯的优先试点候选；官方文档确认快讯与新闻搜索。 | 官方端点 `https://mcp.jin10.com/mcp`，账号激活 Token 后接入；有 `search_flash`、`search_news` 等工具。本次未核到官方开源服务端仓库。指南未披露价格、额度、历史深度和延迟承诺；不应默认免费。 |
| [AKShare](https://github.com/akfamily/akshare) | 免费研究原型、中文财经资讯和公告适配。 | [资讯文档](https://akshare.akfamily.xyz/data/stock/stock_research.html)中财联社电报最近20条、东方财富全球快讯最近200条；这类最新列表不构成历史数据库。接口依赖上游网站，可能变化或下线。代码MIT；项目声明数据用于学术研究，不能推导为免费商用新闻授权。 |
| [Tushare](https://github.com/waditu/tushare) / [Pro新闻](https://tushare.pro/document/2?doc_id=143) | 需要中文新闻历史、按源和时间查询时优先评估。 | `news` 单次最多1500条；长篇 `major_news` 单次400条。[权限表](https://tushare.pro/document/2?doc_id=290)列新闻个人1000元/年、400次/分钟、总调用不限，独立于积分。权限表写3年以上历史，单项文档有6年/8年以上说法，需按来源确认。代码BSD-3-Clause；数据库权限和媒体再分发授权分开。 |
| [RSSHub](https://github.com/DIYgod/RSSHub) | 将财联社、金十、东方财富等内容接入统一 RSS 订阅体系。 | 能力依赖具体路由、上游和缓存；金融路由文档部分来自项目文档部署，未实测有效性。不是统一历史库，需持续采集。AGPL-3.0；自建有运维成本，全文覆盖与媒体版权另外确认。 |
| [上交所公司公告](https://www.sse.com.cn/disclosure/listedinfo/announcement/) / [巨潮资讯](https://www.cninfo.com.cn/) | 公司事件、监管披露的一手证据核验。 | 官方披露平台，不是开源插件；没有确认到可匿名、稳定商用的统一公告 REST API。网页可读、内部接口可调用、正式数据API授权是不同条件。批量接入可看[巨潮官方数据API入口](https://webapi.cninfo.com.cn/#/apiDoc)。 |

中文免费原型可用 AKShare + RSSHub + 公告原文；要查询过去30天快讯，优先比较 Tushare 和金十官方接口的实际历史权限。RSSHub、TrendRadar、AKShare 可能连接相同上游，不能当成三份独立来源。

## 公司、宏观与行情数据及 MCP

| 项目 | 推荐判断 | 费用与接入边界 |
|---|---|---|
| [Alpha Vantage 官方 MCP](https://github.com/alphavantage/alpha_vantage_mcp) | 优先试用的官方综合数据MCP；`NEWS_SENTIMENT`覆盖当前和历史金融新闻/情绪，另有财务、行情、宏观等。 | MIT代码；API key与端点权限另算。[官方付费说明](https://www.alphavantage.co/premium/)的免费配额25次/日，不能支撑高频监控。情绪评分是加工指标，不能当成事实或市场预期。 |
| [Financial Datasets 官方 MCP](https://github.com/financial-datasets/mcp-server) | 美股公司研究候选，财务三表、行情、`get_company_news`统一查询。 | MIT代码；[数据服务另收费](https://www.financialdatasets.ai/pricing)，个人和商业用途不同。wrapper提交稀疏，需验证当前兼容性；未确认新闻全文、出版社覆盖和再分发权限。 |
| [EdgarTools](https://github.com/dgunning/edgartools) | 美股研究的一手披露底座：10-K、10-Q、8-K、Form 4、13F及XBRL。 | 第三方MIT库，有可选本地MCP；不是SEC官方MCP。SEC公共数据免费，需身份标识并遵守访问频率要求。托管connector可有独立费用；[SEC官方API](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)是底层依据。 |
| [FRED](https://fred.stlouisfed.org/docs/api/fred/) + [社区MCP](https://github.com/stefanoamorelli/fred-mcp-server) | 宏观数据序列、实际值和历史观察值的基础来源。 | FRED免费API key；该wrapper为AGPL-3.0，非美联储官方。部分序列来自第三方。回测应评估[ALFRED](https://alfred.stlouisfed.org/)历史版本；本次未确认该wrapper完整支持vintage。不提供统一分析师预期调查。 |
| [OpenBB](https://github.com/OpenBB-finance/OpenBB) / [MCP文档](https://docs.openbb.co/odp/v4/python/extensions/interface/openbb-mcp) | 多供应商数据集成层；需要统一公共、商业和内部数据时采用。 | 自身不生成全部金融数据，权限取决于provider。此次GitHub解析到 `openbq-org/OpenBB`，README仍有旧组织链接；LICENSE为Apache-2.0。只有一两个来源时可直接用官方MCP，减少维护层。 |
| [Massive 官方 MCP](https://github.com/massive-com/mcp_massive) | 原Polygon生态的行情及金融API接入候选，也涉及Benzinga相关产品。 | MIT代码，需key和产品权限；README标明experimental，可能有breaking changes。新闻权限不因安装MCP自动获得。[官方价格](https://massive.com/pricing)。 |
| [EODHD 官方 MCP](https://github.com/EodHistoricalData/EODHD-MCP-Server) | 行情、基本面、新闻与情绪的另一综合候选。 | MIT代码，需相应数据订阅，部分marketplace产品额外授权。适合作为对照候选，不建议一开始与所有综合供应商同时接入。[官方说明](https://eodhd.com/lp/eodhd-mcp-server)。 |

## 加密与预测市场的补充

- [CCXT](https://github.com/ccxt/ccxt)：MIT，统一交易所行情、逐笔、盘口及K线；是客户端而非新闻库。历史、速率和数据权利依交易所而定。本报告只评估公开读取用途。
- [Polymarket官方Python SDK](https://github.com/Polymarket/py-sdk)：MIT，公开读取市场、价格和盘口的候选。旧 `py-clob-client` 已归档，接入时优先核对当前官方SDK与[市场数据文档](https://docs.polymarket.com/market-data/prices-order-books.md)。历史分辨率与保留期不同，不应承诺全部分钟历史。市场价格是交易参与者的定价信息，不能作为事件已经发生的证据，也不自动等同无偏概率。

## 建议的第一批组合

- 中文宏观/交易事件：金十官方MCP + FRED/ALFRED + Last30Days；需要中文历史快讯时增加Tushare，公告回官方披露平台核验。
- 美股公司研究：Finnhub或Alpha Vantage择一试点 + EdgarTools + Last30Days；需要更专业盘中新闻时比较Benzinga或Finlight付费档。
- 全球地缘与产业主题：GDELT + Last30Days + 配置好的RSS订阅，关键事实回政府、公司、监管机构原文。
- 多源统一管理：以上数据源验证后，再决定是否通过OpenBB统一；不要把多个API包装器算作新增独立信息。

这些是文档核查后的组合建议，尚未执行接入测试。

## 持续订阅和存储

[Miniflux](https://github.com/miniflux/v2) 是值得考虑的自托管 RSS 阅读与采集入口：支持 RSS、Atom、JSON Feed、全文提取、REST API、Webhook，使用 PostgreSQL，Apache-2.0。它本身不生产金融新闻。

若只是让个人投研助手积累每日新闻，优先考虑 Miniflux/PostgreSQL 或现成工具的 SQLite。数据量和查询需求证明有必要后，再考虑额外搜索引擎或向量数据库。数据库 MCP 只解决查询已有数据，不能补出不存在的新闻、预期调查或历史记录。

## 接入前的实际验收

用同一组研究问题做比较，比工具数量和星标数更有价值。例如：

1. 查某公司最近30天的业绩、指引、评级及监管事件，逐条返回原始链接和发布时间。
2. 查某宏观数据发布的实际值、此前市场预期、前值及修订值；不能用新闻情绪替代预期数据。
3. 对一个地缘事件并行查媒体报道和社区讨论，识别转载、翻译与重复消息。
4. 查一条已知发生在两个月前的事件，验证历史权限、分页及漏数。

保存新闻原始发布时间、首次采集时间、更新时间和时区；保留原始 URL、上游供应商、正文获取状态。对交易回测尤其需要确认当时可见的数据和后来修订数据，避免回看时引入未来信息。

## 参考入口

- [Last30Days 原仓库](https://github.com/mvanhorn/last30days-skill)
- [TrendRadar 原仓库](https://github.com/sansan0/TrendRadar)
- [Finlight 价格页](https://finlight.me/pricing)
- [Finnhub 官方 MCP 指南](https://finnhub.io/static/finnhub-how-to-connect-mcp-server.html)
- [GDELT 数据入口](https://www.gdeltproject.org/data.html)
- [GDELT DOC 初始文档](https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/amp/)
- [GDELT 长历史更新说明](https://blog.gdeltproject.org/doc-2-0-updates-1-5-year-searching-and-updated-mobile-interface/)
- [金融API目录](https://github.com/jeff3388/awesome-financial-data-apis)：用于发现候选，具体覆盖和价格仍需回供应商确认。
- [另类数据目录](https://github.com/happyendpointhq/awesome-alternative-data)：覆盖新闻、情绪等类别；目录收录不代表可用性保证。
