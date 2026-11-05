# RAP 与 WKM：一手论文核对及投研插件迁移笔记

核对日期：2026-11-02。未改业务代码。本文是研究归纳，不构成已验证的金融效果。

## 结论

RAP 已把“显式状态 + LLM 预测动作后状态 + 奖励 + MCTS 搜索”用于积木规划、数学推理、逻辑证明。WKM 把“从成功/尝试轨迹提炼全局任务知识 + 当前状态摘要检索动作经验 + 概率约束”用于家务、网购和科学实验模拟器。两者侧重不同：RAP 是推理时模拟和搜索；WKM 是训练知识辅助器及检索约束。WKM 作者明确说它不是能配合 MCTS 预测世界的 world model。

对投研插件而言，较有依据的迁移是研究流程规划、证据状态维护、工具动作约束及失败经验复用。本文没有金融实验，不能据此声称能提高收益、预测股价、推演可靠的宏观反事实。

## 原始来源与读取范围

- RAP 正式 EMNLP 2023 论文：[ACL 页面](https://aclanthology.org/2023.emnlp-main.507/)、[正式全文 PDF](https://aclanthology.org/2023.emnlp-main.507.pdf)。已下载并读取正文及表格。
- RAP 论文给出的代码原址：[Ber666/llm-reasoners](https://github.com/Ber666/llm-reasoners)，当前官方组织仓库：[maitrix-org/llm-reasoners](https://github.com/maitrix-org/llm-reasoners)，[RAP 实现目录](https://github.com/maitrix-org/llm-reasoners/tree/main/examples/RAP)。已读取官方当前 README，未运行复现。
- WKM：[arXiv 2405.14205](https://arxiv.org/abs/2405.14205)、[v3 HTML 全文](https://arxiv.org/html/2405.14205v3)。已下载并读取 HTML 正文，以下 WKM 机制与数值以这个版本为准。
- WKM 正式发表：[NeurIPS 2024 页面](https://papers.nips.cc/paper_files/paper/2024/hash/d032263772946dd5026e7f3cd22bce5b-Abstract-Conference.html)、[正式 PDF](https://proceedings.neurips.cc/paper_files/paper/2024/file/d032263772946dd5026e7f3cd22bce5b-Paper-Conference.pdf)。正式页面/摘要与标题、会议信息已核对；PDF 下载超时，未用不完整 PDF 作为表格来源。
- WKM [官方仓库](https://github.com/zjunlp/WKM)、[官方 README](https://raw.githubusercontent.com/zjunlp/WKM/main/README.md)、[训练数据](https://huggingface.co/datasets/zjunlp/WKM-train-data)。已读 README，未逐行审计或运行实现。
- 默认 web_fetch 出现多提供方配置冲突；Agent Reach 因自身状态目录权限失败；随后用 curl 公开直链读取成功，未扩大权限。

## 1. RAP：Reasoning with Language Model is Planning with World Model

### 机制（§3）

同一个冻结 LLM 通过不同 few-shot prompt 承担两个角色：agent 根据状态生成候选动作 p(a|s)，world model 根据当前状态与动作生成后继状态 p(s'|s,a)。推理轨迹交替记录 state/action，使用 MCTS 的选择、展开、模拟和回传寻找高奖励路径，也可对多路径结果聚合。RAP 不在本论文中训练一个专门的转移网络；它通过提示调用预训练 LLM 的知识来模拟转移。

奖励是任务设计的一部分，包括动作 likelihood、重复采样答案的一致性、LLM 自评及目标满足程度。后两者尤其不能当成经校准的真实世界概率。

### 方向与状态定义（§4）

- Blocksworld：state=积木配置，action=拿起/放下/堆叠/拆下；依据领域规则与当前状态枚举合法动作，LLM 预测配置变化。并非纯粹无规则地让模型编排动作。
- GSM8K：state=已求出的中间变量，action=提出下一子问题，world model 回答并更新变量。
- PrOntoQA：state=当前聚焦的事实，action=选择逻辑规则，world model 单跳推导下一事实；同时检查最终真假与整条证明。

### 对照与原始结果

默认底座 LLaMA-33B。对照为 CoT、least-to-most 与 self-consistency（依任务适用），另有 GPT-4 CoT。

- Table 1 Blocksworld：LLaMA-33B RAP(20) 的 2/4/6-step 成功率分别为 1.00/0.88/0.42；同底座 CoT 为 0.17/0.02/0.00；GPT-4 CoT 为 0.50/0.63/0.40。论文称总体约 64%，相对 GPT-4 CoT 约 33% 改善。这仅是该积木任务设定，不是通用超越 GPT-4；RAP(10) 在 6-step 仅 0.26，也低于 GPT-4 CoT。
- Table 2 GSM8K：CoT 29.4%，CoT+SC(10) 46.8%，least-to-most+SC(10) 42.5%，RAP(10) 48.6%，聚合后 51.6%。注意正文误写/另写为 48.8%，与表格 48.6% 有不一致，此处明确采用表格；不能静默混用。
- Table 3 PrOntoQA：CoT 最终预测/证明准确率为 87.8%/64.8%，RAP 为 94.2%/78.8%；CoT+SC 最终预测为 89.8%。MCTS 与 SC 各 20 次迭代/采样。
- §5.1 Table 4 的 Llama-2 70B full Blocksworld 另分 Easy/Hard；Easy 的示例选择预先知道问题最短步数。不可把 Easy 结果当无额外信息的真实部署。

### 增量与局限

相较单条 CoT，增量是显式跟踪后继状态、能够回溯探索替代动作、按未来路径奖励选择步骤。原文实验不等于严格隔离“状态本身”“LLM 模拟器本身”“搜索额外算力”的因果贡献；MCTS 次数与 SC 次数相同也不保证 token/延迟相同。冻结模型的转移幻觉和自评误差会被搜索放大；任务专门奖励与动作合法性知识需要迁移设计。论文 Limitations 明说 fine-tuning 与外部工具整合是未来方向。

## 2. Agent Planning with World Knowledge Model（WKM）

### 机制（§2–3）

环境自身提供 transition function。WKM 对 history 生成当前状态知识，而非接收候选动作预测未来状态。

训练：先用 expert trajectories 训练 experienced agent，再让它探索采样；对 expert/chosen 与 sampled/rejected 轨迹进行比较，自生成任务知识；从专家轨迹逐步总结状态知识，组成 (state, previous-action, next-action) 知识库。WKM 与 agent 使用同一底座、不同 LoRA，agent 也要重训以适应 task knowledge。即使 sampled 轨迹最终成功，若专家路径更短，文中仍可把 sampled 称为 rejected，不能把 rejected 一律解释成失败。

推理：先生成全局 task knowledge 并拼入任务；每步根据当前 history 生成 state knowledge，按上一动作过滤并做语义近邻检索，用检索所得下一动作分布与 agent 概率加权决定动作。动态的是当前状态摘要；模型/知识库没有在线吸收反馈持续更新。

### 任务、对照与原始结果（§4）

任务为 ALFWorld（文本家务模拟器）、WebShop（购物模拟器）、ScienceWorld（科学实验模拟器）；不是在真实家庭、真实购物网站或真实实验室部署。ALFWorld 奖励为二元成功，另外两者为密集完成度，统一报告 average reward；不能把所有分数都叫成功率。

底座 Mistral-7B、Gemma-7B、Llama-3-8B。对照包括 one-shot ReAct、Reflexion；训练型 NAT（SFT 利用 rejected）、ETO（DPO）、KnowAgent（人工动作知识）；另列旧版 GPT-3.5/GPT-4。

Table 1 中 Mistral-7B 的 WKM 分数为：ALFWorld seen/unseen 73.57/76.87，WebShop 65.48，ScienceWorld seen/unseen 62.12/53.62。相比同底座最强基线分别改善 3.13/5.44/1.39/2.80/1.77 个百分点（按论文 0–100 展示尺度）。这些是较能说明知识模块增量的比较。

论文“超过 GPT-4”的摘要比较需谨慎：ALFWorld 73.57/76.87 来自 Mistral-7B WKM；WebShop 66.64 来自 Llama-3-8B WKM，不能拼成单一模型在所有任务的成绩。GPT-4 此处是 one-shot ReAct 且非领域微调，对照不能证明 WKM 的底层世界知识整体强于 GPT-4。

Table 3：ALFWorld unseen 的“含无效动作轨迹占比”ETO 36.57%、KnowAgent 44.78%、WKM 29.85%。表题叫 hallucinated action rates，但 caption 实际定义是含无效动作的轨迹比例，不是逐动作错误率，更不是事实幻觉率。

§3.4 报告 WKM+检索相对 pure agent 推理时间约 2.5:1。不要把更短的环境动作轨迹等同于更低总推理成本。

### 消融与迁移限制

Figure 3：task+state 组合有效；task knowledge 贡献通常比 state 约束更显著、在 unseen 更稳定；作者认为基于训练集的状态库会限制泛化。对比 chosen/rejected 生成知识优于仅用 chosen。此处无逐项引用图上数字，避免从图片猜值。

Figure 6：直接把自然语言 state knowledge 拼进 agent 上下文，比状态库检索+概率约束差，甚至比仅 task knowledge 差。这只能说明该实验中的状态信息注入方式，不能外推成“显式结构化状态总是有害”；RAP 的显式后继状态也与这里不同。

Table 4 weak-guide-strong 只用 task knowledge，未用 state 约束：作者无法从 OpenAI API 获取所需 token distribution，因此这个结果不能证明完整 WKM decoding 可直接接入闭源 API 插件。

§5 原话：作者认为自己是 world knowledge model 而不是 world model，因为尚不能与 MCTS 等搜索共同预测世界。Limitations：仅文本、无法随世界变化/agent feedback 动态更新、额外推理开销、难判断 agent 原本已知何种知识。

## 3. 投研插件的可检验增量（本文建议，非论文实证）

最稳妥的目标是先建立研究过程模型，而不是市场价格模拟器。

1. 状态：每个 thesis 的已证实/未证实事实、来源与截至时间、财务变量定义、冲突证据、尚缺问题、工具可用性、预算。状态的可核验事实与模型推断分栏保存。
2. 动作：查公告、取财报、核对口径、查反方证据、计算估值、补行业数据；动作前置条件与输出契约由工具 schema/规则验证。例如未获最新财报则不生成“已更新”的估值结论。
3. 规划：借 RAP 对候选研究动作做短视野预测，预测内容是“可能获得什么证据、能消除哪种不确定性”；拿到真实工具反馈立即修正。对价格/因果路径的情景分支必须标为假设，并有独立历史校准。
4. 经验：借 WKM 从成功研究与走弯路的过程提炼 task-specific workflow，当前状态检索相似研究案例，优先约束工具参数与行动顺序；不要把旧结论当实时事实，也不要直接套用训练集状态经验。
5. 验证：同一底座、同一工具权限、相同检索/调用/token 预算，对比现有 agent；分开消融显式状态、工作流知识、检索约束和搜索。评价引用可核验率、时间截断违规、遗漏关键反证、无效工具调用、任务完成率、成本与延迟；金融预测和收益必须另用按时间切分的回测评价，防止事后信息泄露。

是否有论文增量：仅加入状态表、MCTS 或全局/局部知识分工已有明显先例。更可辩护的贡献候选是时点一致且有证据出处的研究状态、在线可纠错的工具结果模型、面向投研的信息价值规划，以及在真实投研任务上的独立消融与成本收益证明。以上是候选，需要实验支持，不能预先宣称创新成立。
