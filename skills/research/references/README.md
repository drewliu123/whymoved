# 参考文件索引

按研究环节查阅；SKILL.md 只写主干，具体规则在这里。每份文件都可以独立阅读。

## 定义问题与取证

| 文件 | 用途 |
| --- | --- |
| [intent.md](intent.md) | 先确认用户要作的判断：事实查询、预测、合约决策辅助；何时走简答路径 |
| [templates.md](templates.md) | 按对象（event_pricing/asset/theme/actor）选研究类型与 plan 契约 |
| [context.md](context.md) | 长期条件、近期环境、事前预期、新增变化与后续验证的检查顺序 |
| [sources.md](sources.md) | 来源资格（T0–T4）与阅读顺序；独立 origin 与转载去重 |
| [evidence.md](evidence.md) | sources/claims v2 契约、可选 `claim.metric`、共识与指引块、严格价格/调查字段 |
| [expectations.md](expectations.md) | 事前预期：调查、市场隐含定价、历史修订；不用公司指引冒充共识 |
| [sec-data.md](sec-data.md) | SEC 原始披露取证入口：精确 accession、原始报表、期间与分部口径 |
| [financial-data.md](financial-data.md) | Financial Datasets 只读适配器与授权/配额边界 |

## 分析方法与计算

| 文件 | 用途 |
| --- | --- |
| [analysis-methods.md](analysis-methods.md) | 问题→方法路由、竞争解释与区分检验、六种固定模型、market 预期比较、价格时效 |
| [research-value.md](research-value.md) | 研究增量、机会排序、催化与剩余空间、前瞻复盘 |
| [financial-quality.md](financial-quality.md) | 两期以上报表的盈利质量与红旗筛查（含从账本装配） |
| [event-study.md](event-study.md) | 参考类事件的窗口收益分布；观测点窗口、不给 p 值 |
| [transmission.md](transmission.md) | 行业传导图：节点、机制、时滞、瓶颈与上下游方向 |

## 交付与延续

| 文件 | 用途 |
| --- | --- |
| [memo-template.md](memo-template.md) | report.json 正文契约、估值汇总、图表、冲突、一页纸 memo、渲染与归档 |
| [catalysts.md](catalysts.md) | 催化日期字段、日历查询与「过期不等于未触发」 |
| [research-memory.md](research-memory.md) | 跨轮研究记忆、当时视角查询、判断沿革与多轮摘要 |
| [legacy-forecast.md](legacy-forecast.md) | 可选的可裁决概率登记与旧账本兼容（普通研究不需要） |

## 配套脚本

`scripts/` 下每个脚本的 docstring 写明了输入与边界；文档里出现的命令都可离线运行，不依赖网络或模型。
