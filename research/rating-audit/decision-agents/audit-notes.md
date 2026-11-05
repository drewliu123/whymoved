# 决策与记忆组审查工作底稿

审查日：2026-10-30。静态阅读，E2；未安装依赖、未运行外部代码或交易、未执行外部 SKILL/AGENTS。仅改本组研究产物。

五个仓库均由 GitHub API 获取默认分支 SHA，再以 SHA raw URL 下载。每项目 manifest.json 保存 repo、sha、默认分支、GitHub license 元数据及完整 tree；paths.txt 为目录索引。download-manifest.json 与 supplement-download-manifest.json 保存请求 URL、字节数和错误；source/ 保持上游路径。下载不等于通读，主报告列明用于结论的实际阅读文件/区间。

| 编号 | 仓库 | SHA | 代码/方法 | 深度 |
|---|---|---|---|---|
|14|AI4Finance-Foundation/FinGPT|ac5c5443fbeeafad801e7a3c188e4f24cfaad4d8|B/B|E2|
|15|AI4Finance-Foundation/FinRL|7e98df461cbc7772f16a545a2f13b521e5d0b8f4|B/B|E2|
|16|pipiku915/FinMem-LLM-StockTrading|be814aa47970de9bf2fdd6a1d5a60ae5cf361b46|B/B|E2|
|17|DVampire/FinAgent|17248a0b8b729ee3e093e30bb7bea7f52181f363|B/B|E2|
|18|Alchemist-X/predict-raven|21f70d9132918217ae6c2b5900dd3a15047d46ff|B/A|E2|

关键证据：FinGPT prompt.py:103–107 用真实未来方向标签要求教师生成支持解释，data.py:279–294 再去掉学生输入标签并把标签写入答案；utils.py:142–160 衡量方向 accuracy/幅度 MSE/ROUGE，非概率校准。FinRL 主环境:115–220 有现金、持仓、费用与 turbulence 清仓；:309–386 为动作至奖励路径；stoploss.py:355–362 的强平被现金条件包围，不能当无条件止损。

FinMem agent.py:565–610 训练才拿未来价差，测试按 investment_decision 变成 ±1/0；memorydb.py:138–218 query 无 as_of，:204–211 先截断再去重可能返回少于 top_k；portfolio.py:53–86 用持仓滚动盈亏符号反馈一组曾检索记忆，非逐证据因果贡献。

FinAgent environment/trading.py:117–154 state 含未来窗口，low_level_reflection.py:60–89 计算未来变化，train 模板:28/32 使用 with_next，valid 模板对应处不用 with_next；此差别不支持直接断言全部验证泄漏。BasicMemory.add 以秒级时间字符串作为键，similarity_search 吞掉所有异常；DiverseQuery 无时点过滤。高层反思把 previous_action/reasoning 变成 reasoning/improvement/summary/query 并写入向量记忆。实际环境 BUY/SELL 分别倾向满仓/清仓。

predict-raven bayes.ts 提供 LLR 截断、可信度上限、未验证证据软截断、证据簇跨轮衰减、log-odds 更新；:160–173 明言 credibleInterval 非校准区间，且 engine.ts:652 传 evidenceLedger.length 并非独立簇数。market-blind 默认 opt-in；evaluator.ts 设置隔离运行上下文。policy.ts 含扣费后 entry/hold-vs-exit/stop-loss，另有 saturatedHold 覆盖普通负优势退出；risk.ts 有 quarter Kelly、交易/事件/总敞口与流动性限额。fees.ts 缺费用元数据时有零费默认；book-sim.ts 用有限档快照模拟，限价触价无排队模型；reflect.ts 配对 Brier/skill 是评分统计，不是拟合校准器。

五个根 LICENSE 均逐字读到 MIT，要求保留版权与许可、无担保。各基模/LoRA、模型服务、数据与第三方依赖的完整许可证未逐个核验，不能由根 MIT 推导统一商用许可。

抓取错误：FinAgent finagent/utils/params.py 404，未作证据；其余下载成功。未修改重抓原文件。论文完整方法/实验正文此轮未重读，因此论文绩效结论只能沿用本地清单明确标注的摘要/作者自报，不升为 E2 论文或 E3。
