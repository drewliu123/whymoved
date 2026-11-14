# 能力索引

每项能力对应「在哪里能看到」与「在哪里被验证」。示例列指向可读报告或教程；测试列是可执行证据；参考文档给口径与边界。没有示例的能力会注明「仅测试」，这不是缺陷，但读者应知道去哪里找可运行的证据。

| 能力 | 示例 / 教程 | 测试 | 参考文档 |
| --- | --- | --- | --- |
| 来源分层、选择与去重 | [现金流示例](../examples/msft-cashflow/README.md) | `test_sources.py`、`test_evidence_v2.py` | [evidence](../skills/research/references/evidence.md) |
| 研究计划与问题路由 | [教程第 1 步](tutorial.md)、[苹果示例](../examples/aapl-quality/README.md) | `test_research_plan.py`、`test_analysis_contract.py` | [templates](../skills/research/references/templates.md) |
| 数值事实与口径校验（量纲/缩放/期间） | [质量示例](../examples/msft-earnings-quality/README.md) | `test_metrics.py`、`test_analysis_contract.py` | [analysis-methods](../skills/research/references/analysis-methods.md) |
| 相对估值（comps、分位、现价隐含倍数） | [大型科技同行 P/E 示例](../examples/mega-cap-peers/README.md) | `test_analysis_models.py`、`test_analysis_contract.py` |
| 反向 DCF（价格隐含增长） | [微软反向 DCF 示例](../examples/msft-reverse-dcf/README.md) | `test_analysis_models.py`、`test_analysis_contract.py` | [analysis-methods](../skills/research/references/analysis-methods.md) |
| 驱动式经营模型与多年推演 | [分部示例](../examples/msft-segments/README.md) | `test_analysis_models.py`、`test_analysis_contract.py` | [analysis-methods](../skills/research/references/analysis-methods.md) |
| 敏感性 / 龙卷风 / 三情景 | 仅测试 | `test_analysis_models.py`、`test_analysis_contract.py` | [analysis-methods](../skills/research/references/analysis-methods.md) |
| 可复算计算（op 白名单、引用链） | [现金流示例](../examples/msft-cashflow/README.md) | `test_calculations.py`、`test_reports.py` | [evidence](../skills/research/references/evidence.md) |
| 共识快照、修订、指引分离、相邻财年增长 | 仅测试 | `test_consensus.py` | [expectations](../skills/research/references/expectations.md) |
| 盈利质量与法证筛查（含 ROIC） | [趋势示例](../examples/msft-trend/README.md)、[苹果示例](../examples/aapl-quality/README.md) | `test_financial_quality.py`、`test_quality_inputs.py` | [financial-quality](../skills/research/references/financial-quality.md) |
| 催化日历（到期、过期、无日期） | [教程第 2 步](tutorial.md) | `test_calendar.py` | [catalysts](../skills/research/references/catalysts.md) |
| 事件研究（参考类分布） | [FOMC 事件示例](../examples/sp500-fomc-event/README.md) | `test_event_study.py` |
| Beta 估计（对齐序列回归） | — | `test_beta.py` | [event-study](../skills/research/references/event-study.md) | [event-study](../skills/research/references/event-study.md) |
| 行业传导（节点、方向、瓶颈） | [AI 资本开支传导示例](../examples/ai-capex-transmission/README.md) | `test_transmission.py` | [transmission](../skills/research/references/transmission.md) |
| 跨轮研究记忆、沿革、实体别名 | [教程第 2 步](tutorial.md)、[跨轮记忆示例](../examples/memory-workflow/README.md) | `test_research_memory.py`、`test_memory_example.py` | [research-memory](../skills/research/references/research-memory.md) |
| 多轮摘要（判断/论点/触发） | 仅测试 | `test_digest.py` | [research-memory](../skills/research/references/research-memory.md) |
| 一页纸 memo（含质量、传导、事件、多年路径） | [教程第 3–5 步](tutorial.md) | `test_memo_pack.py` | [memo-template](../skills/research/references/memo-template.md) |
| 价格隐含增长 vs 共识增长对照 | 仅测试 | `test_expectation_compare.py` | [expectations](../skills/research/references/expectations.md) |
| 不可覆盖归档、更新链、哈希、重渲染一致 | [教程第 2 步](tutorial.md) | `test_research_runs.py`、`test_archive_regression.py` | [architecture](architecture.md) |
| 渲染（Markdown/HTML、各类图表、同源表） | 四个示例的报告 | `test_reports.py`、`test_examples.py` | [memo-template](../skills/research/references/memo-template.md) |
| 数据根体检（含 `--renders`） | [教程第 6 步](tutorial.md) | `test_doctor.py` | [installation](installation.md) |
| 示例回归与教程可执行 | [教程](tutorial.md) | `test_examples.py`、`test_tutorial.py` | [development](development.md) |
| CLI 错误约定与文档链接 | — | `test_cli_errors.py`、`test_docs.py` | [development](development.md) |
| 发布一致性（版本/CHANGELOG/入口） | — | `test_packaging.py` | [development](development.md) |
| SEC 官方检索（可选运行时） | — | `test_sec_cli.py` | [sec-data](../skills/research/references/sec-data.md) |
| 可选数据接口（Financial Datasets / Polymarket） | — | `test_optional_apis.py` | [financial-data](../skills/research/references/financial-data.md) |
| 机会记录与更新分支 | — | `test_opportunities.py` | [research-value](../skills/research/references/research-value.md) |

## 怎么读这张表

- 想快速理解一种方法：先读「示例」列里的报告，再看参考文档的口径与边界。
- 想确认某能力是否可靠：看「测试」列；测试名基本对应能力，失败时能定位。
- 「仅测试」不代表不重要，而是还没有可公开的真实数据示例；估值类示例因缺少可靠离线价格源而暂缓。

