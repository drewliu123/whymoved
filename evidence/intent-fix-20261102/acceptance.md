# touyan 0.5.1 本地验收

日期：2026-11-02。

已将用途识别、纠正后重新定题及按原始用户问题独立审查固化进插件；本轮新增的个人记忆内容已撤回。源码与本地已安装插件版本均为 0.5.1，更新命令要求重启/新会话应用，当前会话不声明热加载。

## 变更

- 方法选择前区分事实查询、预测、合约决策辅助与其他研究；类似预测市场标题的短问先搜索匹配市场，核对期间与口径。明确只查官方实际值保留简答路径。
- 合约决策先核对精确规则、档位、来源与兜底，再研究驱动、结果映射、真实报价、费用与逐档深度，比较独立判断和含费门槛。
- 用户纠正后更新整体计划与完成条件；子 Agent 及审查者收到原始问题和纠正原话。答错任务即使结构、引用、算术通过，也不得验收。
- 区分完整回答、诚实的部分回答和答错任务；不强迫编造精确概率。用途、主判断或答案覆盖改变后，最终稿须聚焦复审。

## 验证与证据

| 验证 | 结果 | 证据 |
|---|---|---|
| 源码原有自动测试 | 172 项通过，退出码 0 | [checks.json](checks.json)、[测试日志](unit-tests.stderr.log) |
| 已安装副本原有自动测试 | 172 项通过，退出码 0 | [installed-tests.json](installed-tests.json)、[测试日志](installed-tests.stderr.log) |
| 本地安装与源码一致性 | 49/49 个受检源码、测试及清单文件 SHA-256 一致 | [installation.json](installation.json) |
| 最终离线行为案例 | 14/14 符合冻结预期，评分命令退出码 0；主会话另阅读了逐例 reason | [评分](behavior-final-score.json)、[命令与输入输出哈希](behavior-final-command.json)、[实际输出](behavior-final.json) |
| 原四项提示词发现的聚焦复查 | 四项均已解除，限定范围内无剩余项 | [复查报告](review-final.md) |
| 最终插件清单校验 | 退出码 0，success=true，无 manifest errors | [final-validate.json](final-validate.json) |
| 目录校验 | 通过；保留缺图标及两处 .DS_Store 共三项非阻断 warning，未运行 strict | [目录校验输出](plugin-validate.stdout.log) |
| 文件引用 | 检查通过 | [link-check.json](link-check.json) |
| 修改后差异检查 | 主会话检查主入口、审查、模板、方法与版本差异；新增意图规则和案例亦已阅读 | [source.diff](source.diff) |

实际更新命令及结果保存在 [marketplace-update.json](marketplace-update.json) 与 [plugin-update.json](plugin-update.json)。

## 验证边界

14 例是冻结合成输入下执行模型对任务用途、下一步动作与审查裁定的离线判断，不是联网取证、真实报价、费用或交易能力验证。最终轮是同一执行者对原发现修正后的聚焦复查，不宣称新的盲测或长期稳定性。未执行真实联网端到端研究、运行时最终稿复审场景或多轮模型稳定性测试。

本轮没有 Git 提交、push、PR、外部评论或交易。历史研究归档及数据 schema 未修改。
