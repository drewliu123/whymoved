# touyan 意图入口与审查离线回归

日期：2026-11-02。

行为结果先写入 `behavior-actual.json`，随后才读取 templates.md 和 analysis-methods.md 作提示词交叉检查；未根据后续检查回改案例判断。以下是提示词层面的具体触发条件与遗漏，不代表已复现运行时代码缺陷。

## 执行与证据边界

- 执行方式：Claude Agent SDK 内的单执行者，环境给出的模型标识为 `mythos-magpie-7064216996[1m]`。未派子 Agent，未另启模型会话。
- 行为输入仅为 skills/research/SKILL.md、skills/research/references/intent.md、agents/red-team.md、tests/intent/README.md、tests/intent/inputs.json。交叉检查额外读取 skills/research/references/templates.md 及其引用的 analysis-methods.md。
- 未读取 expected.json，未主动读取 memory 或 journal，未联网、执行交易、生成研究归档或修改插件源文件；仅写入本目录两份产物。
- 各案例独立使用该例 user_turns、discovery、previous_plan、plan、draft、validation，动作表示下一步计划，不表示动作已执行。合成发现及 validation 仅在该案例范围内作为给定事实。
- 没有本次主会话的历史聊天输入。但启动上下文自带用户全局规则与 memory 索引摘要，因此不能宣称完全没有任何预置个人上下文；未打开其引用文件，未将其作为案例路由依据。

## 行为结果概览

共 12 例：9 例 triage、3 例 review。用途分为 unresolved 1 例、fact_lookup 2 例、forecast 2 例、market_decision 6 例、other 1 例。两例合约审查拒绝答错任务，实际值审查通过其合成条件下的答题检查。这里的“通过”仅指该例 answer_fit，不是完整研究或联网事实核验通过。

未读取标准答案、未执行标准答案评分；因此不报告预期命中率或“12/12通过”。已执行 `python3 -I -` 内联结构检查，退出码 0：确认 12 个唯一 id 与输入顺序一致、顶层及逐例字段精确匹配、用途及动作代码合法且动作不重复、reason 为非空单行，9 例 triage 的 answer_fit/blocking 均为 null、3 例 review 均为 bool。检查只读取 inputs.json 与 behavior-actual.json，输出记录在本次工具调用日志，未另建日志文件。该结果只证明产物结构合规，不是行为预期评分。

## 发现 1：实际值查询获准进入，却没有可用的后续方法契约

级别：material；性质：明确的流程覆盖冲突。

触发条件：用户明确“只查官方已公布实际值”或“只查发布时间”，如 explicit_actual_overrides_history、review_actual_answer。

证据：

- intent.md:9、15 允许 fact_lookup，并明确未发布时可交付状态和发布时间，不强行预测或查盘口。
- templates.md:3 同样要求先确定用途、按问题选必要项。
- SKILL.md:62、64 无条件要求研究者选择六种 question_kind，所有新 plan 写 research_design；templates.md:20 还要求至少两个变量的机制链，除 commitment_check 外须竞争解释与检验。
- analysis-methods.md:15–24 的六种方法没有纯事实查询：commitment_check 也要求有日期承诺、条件、权限和行动，不能自然承接统计公布值查询。
- SKILL.md:140 和 analysis-methods.md:192 要求新归档满足完整新契约；red-team.md:28 又按六种方法审查。SKILL.md:68 对纯事实查询仅豁免背景检查，没有豁免上述方法契约。

影响：入口可正确选 fact_lookup，后续却可能被迫虚构竞争解释、套用预测/承诺核对，或因没有自然适配的方法而停在契约阶段。单纯查询已完整回答，也可能被审查按不相干的分析要求判缺项。

最小修正建议：明确 fact_lookup 的结束路径及适用字段，对方法、机制链、竞争检验、模型和价格检查给出一致的不适用规则；如仍要求统一归档，须定义对应合法契约。不能仅让研究者随意选一个分析 kind。未检查实现脚本，不能据此断言脚本必然报错。

## 发现 2：非交易预测被路由到要求裁决合约的方法

级别：material；性质：方法输入与用途边界不一致。

触发条件：用户要求“下月 CPI 可能多少、给判断和驱动、不看交易价格”，没有任何预测市场或裁决合约，如 forecast_unreleased。

证据：

- intent.md:10 允许普通 forecast，完成条件是有依据的数值/方向、情景及改变判断的条件。
- templates.md:22 明确纯 forecast 可 price_relevance=false。
- SKILL.md:62 要求选择六种方法并按必需输入取证；最贴近该问题的 event_forecast 在 analysis-methods.md:20 把“裁决合约”列为必需输入，且该页:13 说应按必需输入取证。
- templates.md:30 的 event_pricing 路径以“先读清合约”为前提；未说明无交易合约的宏观预测应如何确定目标公布口径并满足 event_forecast。

影响：将官方统计的预测目标误视为缺失市场合约，额外触发市场检索或合约澄清；也可能凭空包装裁决合约。price_relevance=false 只解决价格要求，没有解除合约必需输入。

最小修正建议：区分“可核验的预测目标/官方公布口径”和“交易合约裁决规则”。event_forecast 对非交易预测要求前者，只有 market_decision 才必需精确合约及成本比较；同步主流程、模板、方法输入说明与审查适用范围。

## 发现 3：真实缺口下何时算停止、答完或阻塞，缺少统一判定

级别：material；性质：完成状态与审查裁定遗漏，不是要求补造概率。

触发条件：已核对合约与驱动、执行预算内定向补查，但费用或深度仍取不到；或者拿不到可靠概率，只能给有据倾向、门槛及剩余缺口。

证据：

- intent.md:30 允许缺可靠概率时提供有据暂定倾向和门槛，不要求伪造概率。
- intent.md:31 要求实际执行定向补查，不能仅交待查清单便宣布研究完成；:33 说先满足 required_answer 再生成报告。
- intent.md:50 要区分“有据的部分回答”和“答错问题”，但没有明确前者应如何映射 answered 和 finding severity。
- templates.md:15 的 stop_condition 同时容纳“问题得到回答”和“预算内无法补齐关键缺口”。
- red-team.md:15 要具体说明未满足项，:64 的 answer_fit 只有布尔 answered 与 reason；没有单独的部分回答/预算耗尽状态，也没有统一说明哪些 required_answer 缺口必须 blocking。

影响：两名遵守规则的审查者可对同一份诚实的部分回答给出不同 answered/blocking；主流程也可能把预算耗尽误解为任务完成，或把无法补齐的输入当作无限重试条件。现有 12 例没有真正“已执行关键取证但仍缺输入”的 review 案例，无法用本轮结果验证这一边界。

最小修正建议：明确区分停止研究与完整答题，约定 answered=true 的必要条件、部分回答的 answered 值与 blocking 条件。允许交付清楚标记的部分结果，但不得因此宣称完整满足合约决策任务；加入已补查失败、概率缺失但有定性门槛等独立审查案例。

## 发现 4：独立意图审查规则明确，但修改后的最终稿缺少复审闭环

级别：material；性质：最终审查绑定遗漏。

触发条件：red-team 已审查版本 A，主研究者根据 targeted_followup 取得新证据，新增或改变结论形成版本 B；尤其是期间发生用户纠正，研究目标也改变。

证据：

- intent.md:37 规定纠正后更新目标、计划、完成条件及取证与审查；:41 明确审查者先独立读用户原话，再看计划。
- SKILL.md:120 规定独立审查与一轮定向补查，新增结论重入账、重校验，但没有明确要求将补查后的最终草稿重新交还独立审查者。
- red-team.md:73 同样只要求主研究者新增结论重新入账校验。
- SKILL.md:124–140 的冻结、全链检查与归档步骤，没有明确要求最终 report 与当前用户纠正及独立审查版本相匹配；结构和重算检查本身不能核验语义。

影响：先前版本的 answer_fit/审查处置可能随最终稿一起归档，即便最终稿已改变主判断或用途。入口规则上的独立性虽已写清，最后一版交付仍可能只有主研究者自查。

最小修正建议：对改变主判断、用途或 required_answer 覆盖的修改执行一次聚焦的独立复审，绑定最新用户原话/纠正、计划与最终报告版本；将一次补查预算与复审次数区分。无法复审时明确最终版本未审，不沿用旧通过结论。未运行真实 Agent 调用，不能宣称该遗漏已在运行时发生。

## 已明确且未发现直接冲突的部分

- 最新的明确实际值限定优先于旧交易上下文：intent.md:15、red-team.md:14 与 templates.md:3 一致。
- 用户纠正后重新定题而非局部补丁：SKILL.md:58、intent.md:35–37 一致，templates.md:3 保留纠正原话。
- 审查先按用户原话独立确定用途，计划不是权威：SKILL.md:120、intent.md:41、red-team.md:7 一致。review_narrowed_plan 与 review_point_only 均据此作否决，没有发现“计划一致即可通过”的文本规则。
- 合约身份、规则、真实选项、带时刻报价、深度、费用和独立判断不可被点预测替代，且不能把任意情景区间当胜率；本次查阅文本在这些要求上相容。

## 验证局限

本轮为一次离线、人工语义执行，不测真实检索、官方数据、费用计算、交易优势、研究归档、插件自动加载或多次模型运行稳定性。未读取期望结果，未运行评分器、Python 原有单测或 claude plugin validate；也未读取脚本、其余引用资料或任何历史研究。以上四项为限定提示词范围的证据和修正建议，不声称实现层没有其他豁免、运行时必然失败或源文件已经修复。
