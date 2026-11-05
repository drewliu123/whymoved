# 可选预测与旧账本

只有用户要求登记可裁决预测/复盘时使用。普通研究归档不需要概率、假设或作者写入。旧journal.py/forecast.py及schema1保持兼容；不要把v2来源引用直接塞进旧账本。

## 登记步骤

1. 写明确二元问题、YES标准、窗口、裁决来源与证据截点；不能裁决就不报概率。
2. 有同截面且选项完全对应的可成交价格：`market`模式，final_prob等于market_prob。该字段是市场基准，不是独立预测，不能用来证明研究超越市场。
3. 无市场参照：`independent`模式。冻结通过校验的事实证据，不放推断、报告草稿、未知未来材料。独立调用3个touyan:forecaster，各自只读同输入，原样保留trials。已有research/prob-eval的结果只适用于其数据与协议，不外推所有类型。
4. 为旧流程生成独立schema1 claims，来源嵌入原字段；保留与v2的ID映射并跑旧校验。不要改变旧归档。
5. 执行forecast finalize后抄final_prob到memo my_prob，完成journal add。告知将写memos.jsonl；涉及作者立场的复盘还会更新作者评分。新作者只有用户明确要求时observe。

```bash
python3 "$TY_DIR/scripts/forecast.py" finalize "$WORK/forecast.json" --claims "$WORK/legacy-claims.json"
```

```bash
python3 "$TY_DIR/scripts/journal.py" add "$WORK/memo.json" --claims "$WORK/legacy-claims.json" --report "$WORK/report.md" --plan "$WORK/plan.json" --forecast "$WORK/forecast.json"
```

forecast.json示例（示例数值，仅说明契约）：

```json
{
  "as_of": "2026-10-31T18:00:00Z",
  "forecasts": [{
    "hypothesis_id": "H1", "mode": "independent",
    "question": "公司下一季度收入是否达到指定阈值？",
    "yes_means": "按同一披露口径季度收入达到100百万美元",
    "window_start": "2026-10-31", "window_end": "2027-02-28",
    "resolution_source": "公司正式季度披露",
    "evidence_ids": ["C1"], "trials": [0.4, 0.5, 0.45]
  }]
}
```

market模式删除trials，加market_prob与market_source。finalize写回final_prob、method_version、evidence_hash，冻结后不得改证据。

memo.json：

```json
{
  "question": "对应研究问题", "type": "asset", "entity": "示例公司",
  "as_of": "2026-10-31T18:00:00Z",
  "hypotheses": [{
    "id": "H1", "text": "指定季度收入达到100百万美元",
    "verify_by": "2027-02-28", "falsify_if": "同口径收入低于阈值",
    "my_prob": 0.45, "authors": []
  }]
}
```

my_prob只能来自finalize。market模式附同值market_prob。不要把示例概率用于实际报告。authors如填写，字段为handle/platform/stance（support或oppose），grade会据此评分。

## 复盘

```bash
python3 "$TY_DIR/scripts/journal.py" due
```

```bash
python3 "$TY_DIR/scripts/journal.py" show <memo_id>
```

读当时memo/claims/forecast，查正式结果，逐条依原裁决契约grade，延期不当然等于void，先看窗口规则。

```bash
python3 "$TY_DIR/scripts/journal.py" grade <memo_id> <hypothesis_id> hit --note "正式结果链接及判定依据"
```

```bash
python3 "$TY_DIR/scripts/journal.py" stats
```

hit/miss/void必须按原契约选择。汇报事实、推断、时机哪一层错了；样本量、选择偏差和market模式复制基准决定统计能支持的范围。
