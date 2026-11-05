# 意图分流与答题审查回归

这是提示词行为样例，输入包含首次短问、明确事实查询、未发布预测、两次纠正、年份歧义、找不到合约及计划缩窄的审查反例。发现结果为冻结的合成材料，不是联网行情验证。它们不进入Python单元测试计数。

## 执行

给一个没有当前会话历史的执行者以下文件：

- `skills/research/SKILL.md`
- `skills/research/references/intent.md`
- `agents/red-team.md`
- 本目录的`inputs.json`

执行者不要读取`expected.json`。按插件入口规则处理triage，按red-team规则处理review，不执行联网、交易、研究归档或修改插件。每例返回一行决策理由，并输出如下JSON到单独的结果文件：

```json
{
  "cases": [
    {
      "id": "与输入一致",
      "task_mode": "fact_lookup|forecast|market_decision|other|unresolved",
      "actions": ["下一步必要动作代码"],
      "answer_fit": null,
      "blocking": null,
      "reason": "一两句可复核的判断依据"
    }
  ]
}
```

`unresolved`仅用于尚未确定用途的入口探查，不是完成后的audit.intent.task_mode。review必须给answer_fit与blocking布尔值；triage两项为null。动作代码如下，选下一步必要动作，可组合，不把未执行动作写成已执行：

| 代码 | 动作 |
|---|---|
| search_market | 搜索匹配预测市场 |
| verify_rules | 核对精确合约身份、期间、结算与档位 |
| forecast_outcomes | 研究合约结果并映射真实选项 |
| assess_costs | 核对报价/深度/费用，与研究判断比较 |
| official_lookup | 核对官方实际值或发布状态 |
| build_forecast | 建立有依据的预测、驱动与情景 |
| replan | 按纠正重新定义目标、计划与检索 |
| clarify_contract | 澄清无法区分的合约/年份 |
| report_gap | 保留原任务，说明已查结果与关键缺口 |
| compare_benchmark | 核对实际表现与同期基准 |
| final_release_only | 以未公布/发布时间作为最终答案 |
| choose_contract_final | 未解歧义就选定合约并给最终交易判断 |
| invent_probabilities | 把点预测或任意情景范围编成精确胜率 |
| fabricate_market | 编造未找到的市场 |
| downgrade_fact | 将明确交易任务静默降为纯事实查询 |

单独的评分者用`expected.json`检查必需动作、禁止动作、用途及审查裁定，同时读reason，避免只命中代码却解释相反。缺例、重复id或非法字段应报失败，不能只检查返回的样本。保存执行者实际输出、模型/运行方式、评分和局限。自动检查命令（reason含义仍需人工或独立审查）：

```bash
python3 tests/intent/score.py <actual.json>
```

## 证据边界

离线回归可检验给定输入下的用途判断与计划一致却答错问题的拒绝；不能证明真实工具调用、完整联网研究、费用计算、交易优势或新会话的自动热加载。Python原有测试与`claude plugin validate`另外运行。没有执行本套案例时须写未运行，不把关键词检查或文件存在当行为通过。
