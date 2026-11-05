# 两篇 belief-state 论文核查（2026-11-02）

## 结论与证据范围

两篇均真实存在，编号与标题完全匹配。结论来自直接访问 arxiv.org 摘要页及全文 HTML，而非沿用原构想或第三方摘要。web_search 用于发现与交叉检查；web_fetch 因 multiple usable web providers 配置错误失败，随后 Python urllib 成功读取原站。未运行论文实验，以下数值是作者报告，不是独立复现。未改生产代码。

| 编号 | 标题 | 一手提交信息 |
|---|---|---|
| 2609.00455 | Towards a Belief-Based World Model for LLM Agents | 2026-08-31 v1；2026-09-30 v2 |
| 2610.01415 | Beyond Memory: Harnessing Long-Horizon Agents with Explicit Belief States | 2026-10-01 v1 |

## 1. BB-WM：问当前不确定性，而不只预测动作结果

一手链接：
- 摘要：https://arxiv.org/abs/2609.00455
- 本次读取全文：https://arxiv.org/html/2609.00455v2
- 作者代码：https://github.com/skumar-ml/belief-world-models
- 作者预计算轨迹：https://huggingface.co/datasets/skumar-ml/belief-world-models

作者 Shubham Kumar、Harshit Kumar、Narendra Ahuja、Saurabh Jha。原文问题：若 world model 已表示当前状态的 belief，直接暴露给冻结的 LLM policy 是否有助决策？研究没有解决在开放世界中学习可靠 world model 的问题。

### 实际应用与测量

- ALFWorld：模拟家庭找物、拿取、清洗/加热/冷却并放置；134 unseen 任务，最多30环境动作。
- ScienceWorld：十房间科学教学模拟，如物态变化、种植物、混合化学品；24任务类型、211 unseen episodes；预算随任务。
- BabyAI-Text：局部视野网格导航、拾取、排序与相邻放置；100任务，四任务家族，64环境动作。

三个冻结模型为 Llama-3.1-8B-Instruct、Qwen3-14B（关闭thinking）、Sonnet4.6；分别在ReAct与ReflAct内比较 Original、Belief、WALL-E、BB-WM。前两模型3次运行，Sonnet1次。指标reward-within-budget，按已消耗环境步画曲线；ALFWorld/BabyAI为成功率，ScienceWorld允许中间任务奖励。

### 机制

模型维护确定性状态（位置、背包等）与物品隐藏位置的分类分布，位置先验、状态空间、更新规则均按环境手工设计。搜到则位置分布坍缩，搜不到则排除该容器并重新归一化。LLM用自然语言查询当前belief；组合方法同时提供WALL-E式动作合法性检查。ScienceWorld/BabyAI的动作检查用模拟器oracle。

主实验总体支持belief与有限simulation互补。Memory-only消融保留确定性已见状态、去掉未知物体位置分布，Belief表现更好。ALFWorld另以Zipf(alpha=1.25)初始化位置，并比较同样可能位置但不显示概率的Belief-NoProb：最终预算附近表现近似，显式概率主要提高前期搜索效率。

### 局限及不可外推点

原文§6明确：belief是hand-crafted、benchmark-specific；并未学到开放环境下正确belief。所谓simulation主要是动作valid/invalid，未把当前belief传播成完整假设未来belief。主要不确定性为物品藏在哪里，远窄于金融因果、价格或政策状态。查询不消耗环境步，所以环境步效率不能等同于token、延迟或总成本效率。强模型在容易任务上已接近饱和，提升较小；没有与并行belief-tracking方法做全面竞赛，也不以最高榜单分为目标。

## 2. PoS：显式维护当前理解及尚未完成/尚未查清的需求

一手链接：
- 摘要：https://arxiv.org/abs/2610.01415
- 本次读取全文：https://arxiv.org/html/2610.01415v1
- 作者代码：https://github.com/luoyu100/PoS
- 作者机制说明：https://github.com/luoyu100/PoS/blob/master/docs/method.md
- 作者完整结果与成本：https://github.com/luoyu100/PoS/blob/master/docs/results.md

作者 Yu Luo 等12人；南开大学、阿里巴巴、清华大学。PoS为Progression of States，是推理期框架，无新增模型训练。

### 实际应用与测量

| 任务 | 原文实际评估 | 指标 |
|---|---|---|
| ALFWorld | 134 valid_unseen家庭模拟任务 | 任务成功率 |
| LOCA-Bench | 跨源工作流、结构化分析、环境操作；15种seed任务×5环境seed×7长度，共525个；8K至256K | 任务成功率 |
| RCA-100 | 全部103例运维故障诊断 | 故障类型与根因实体同时正确的joint accuracy；另报单项 |
| ClinDiag | 302常见+302罕见临床病例，固定604例 | 诊断与参考临床等价的准确率 |

LOCA具体例子有发票检查、课程助理、Excel市场研究、库存更新等。ClinDiag因数据访问限制排除Emergency/MIMIC-IV-Ext子集，不能称全量ClinDiag。

三个backbone为Qwen3.7-Plus、Kimi-K3、GLM-5.3；基线包括Raw Trajectory/ReAct、ACON、PACE、HiAgent、LongHorizon-Harness；消融去掉一致性验证、去掉trapping恢复；另有长上下文与恢复策略分析。

### 机制

belief为B=(当前世界W、目标G、知识缺口ΔE、成就缺口ΔA)。W包含实体、状态、关系及证据/置信信息。挑一个Active Gap指导行动；动作观察形成候选更新，由Belief Sentinel审查内部一致性和证据支持后提交。用缺口持续、进展停滞、状态复现检测Belief Trapping；区分Static、Cycle、Drift，按知识/成就缺口生成恢复约束。

这与BB-WM不同：PoS不是对潜在真实状态的规范化贝叶斯后验。作者实现说明指出confidence彼此独立、不归一。诊断进展部分以置信度变化衡量，因此置信变化本身不能视为真相更准确。

### 报告结果与局限

| backbone | ALFWorld | LOCA | RCA joint | ClinDiag |
|---|---:|---:|---:|---:|
| Qwen3.7-Plus | 88.81 | 56.38 | 38.83 | 45.03 |
| Kimi-K3 | 94.03 | 74.29 | 51.46 | 54.80 |
| GLM-5.3 | 97.01 | 70.86 | 49.51 | 52.15 |

作者报告12种benchmark×backbone组合中均优于所比基线。Qwen ALFWorld最强基线72.39→88.81，+16.42个百分点（22.68%相对改善）；Qwen RCA最强基线28.16→38.83，+10.67个百分点（37.89%相对改善）。不要把相对百分比写成百分点。

RCA/Qwen成本分析：Raw Trajectory任务代理与总token均355.70K；PoS任务代理281.20K、总计1800.13K。虽然任务代理token减少20.9%，总token为5.06倍，不能称整体节约成本。

原文Appendix G：自然语言belief维护增加计算与冗余，可能遗漏信息、语义失真；依赖backbone既有领域知识，缺少系统外部领域知识检索。内部一致不代表事实或因果正确。工具操作与专科知识失败仍在；例如LOCA环境操作成功率仅36.00–41.14%。作者仓库只附Raw、完整PoS及两消融，没有公开其他四种基线的实现；使用live API无固定模型snapshot，复现存在漂移。医疗为基准模拟交互，不是临床部署验证。

## 对原构想的可引用边界

可以引用：显式表示当前已知/未知、维护任务缺口、一致性审查与停滞恢复，能在上述交互基准改善决策或执行表现。

不能据此宣称：已经验证金融世界模型、可校准经济状态概率、获得可靠因果反事实/收益预测、证明知识图谱或向量记忆无用、证明全局低成本、证明线上生产可靠性。若用于投研，属于迁移假设，仍需证据来源与时点、竞争假说、概率校准、状态更新错误率、任务收益及调用成本等独立评测。
