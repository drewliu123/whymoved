# 跨轮研究记忆：之前判断过什么

## 一句话

研究是接力的，不是每次都从零开始。这个工具把 `journal/runs/` 里已冻结的研究整理成一个**只存指针的索引**，让你能回答：关于某个标的或主题，我们什么时候说过什么、依据了多少主张、用了哪些模型、后来有没有更新判断。

它不合并数字、不新建主张、不改写归档，也不把旧推断当成新证据。

## 索引里有什么

每轮研究一条记录：

| 字段 | 含义 |
| --- | --- |
| `run_id` / `as_of` | 归档编号与冻结截点 |
| `title` / `question` / `task` / `type` | 这一轮到底在回答什么 |
| `entity` / `entities` | 研究对象；`entities` 还包含 `claim.metric.entity`（同业、对手方） |
| `judgment` | 报告正文给出的判断原文（`answer.text`） |
| `opportunity_status` | research_now / watch / priced_in / no_edge（若有） |
| `parent_run` / `judgment_changed` | 更新链与「是否改变判断」，来自该 run 的 update 记录 |
| `claim_count` / `metric_names` / `model_kinds` | 证据与计算的规模与种类 |
| `triggers` | 触发 id 与 `due`（没有日期就是空串） |
| `finding_titles` | 主要发现标题，便于检索 |
| `report_sha256` | 冻结报告哈希，指向可核验的原件 |

索引文件是**派生缓存**：任何时刻都可以从归档重建，`index_hash` 只对索引内容做哈希。归档本身的哈希由各自 manifest 负责，索引不替代它。

## 用法

```bash
# 重建索引（默认写到 $TY_HOME/journal/index.json）
python3 "$TY_DIR/scripts/research_memory.py" index --home "$TY_HOME"

# 查询：某标的历史判断，按时间倒序
python3 "$TY_DIR/scripts/research_memory.py" query --home "$TY_HOME" BTC

# 当时视角：只看到 2026-10-15 为止的研究
python3 "$TY_DIR/scripts/research_memory.py" query --home "$TY_HOME" NVDA --as-of 2026-10-15

# 只看最近两条
python3 "$TY_DIR/scripts/research_memory.py" query --home "$TY_HOME" NVDA --limit 2
```

查询是大小写不敏感的子串匹配，范围包括标题、问题、任务、实体、指标名、发现标题与判断原文。`--as-of` 很关键：它给出的是「当时我们知道什么」，而不是用今天的结论回头解释过去。

输出：

```json
{"term": "BTC", "count": 1, "matches": [
  {"run_id": "R20261112T165159Z-7e129f55cff0", "as_of": "2026-11-12T16:50:00Z",
   "title": "比特币：趋势下行+机构分发，反弹是卖出机会而非买入机会",
   "question": "看看现在比特币", "entity": "Bitcoin (BTC-USDT-SWAP)",
   "entities": ["Bitcoin (BTC-USDT-SWAP)"],
   "judgment": "偏空……", "opportunity_status": "watch", "parent_run": "",
   "judgment_changed": null, "claim_count": 12, "metric_names": [],
   "model_kinds": [], "triggers": [{"id": "TR1", "due": ""}],
   "report_sha256": "..."}
], "notes": ["索引只保存指针……"]}
```

（示例为真实归档的裁剪结果。）

## 判断沿革：thread

索引已经记录每轮的 `parent_run`。`thread` 把它还原成一条判断沿革：

```bash
python3 "$TY_DIR/scripts/research_memory.py" thread --home "$TY_HOME" R20261101T000000Z-cccccccccccc
```

输出 `lineage`（旧→新，按 `parent_run` 回溯到最早一轮）、每轮的 `judgment`、`judgment_changed`（该轮相对于父轮是否声明改变判断）、`model_kinds`、`opportunity_status` 与 `depth`，以及请求那一轮的直接 `children`。

用法：

- **更新前先看沿革**：确认这次要改的是哪一段判断，旧判断原文是什么，避免「其实两轮前已经改过」。
- **写更新报告时**：`judgment_changed` 必须与沿革一致；声称「维持判断」却在正文推翻旧结论，沿革会把矛盾暴露出来。
- **分支更新**：同一父轮可以有多个子轮，`children` 列出直接子轮；不同子轮之间没有顺序关系，不能当成一条时间线。

沿革同样只是指针：判断原文复制自各轮报告，引用前回冻结 run 读证据。

## 多轮摘要：digest

单轮查询回答「某标的」，`digest.py` 回答「这段时间我们做了什么、接下来要看什么」：

```bash
python3 "$TY_DIR/scripts/digest.py" --home "$TY_HOME" --as-of 2026-11-14 --days 14 --out "$WORK/digest.md"
```

内容：

- **判断变化**：窗口内 `update.judgment_changed=true` 的 run，附判断原文。
- **本窗口研究**：窗口内所有 run，按截点倒序。
- **未来 30 天的催化**：从各 run 的 trigger / watch 里取有 `due` 且落在未来 30 天的条目，带距今天数。
- **过期未核对**：`due` 已过但报告未记录核对的条目；文档里明确「过期不等于未触发」。
- **边界**：没有 `due` 的观察项不进催化小节；摘要只复制冻结内容，不给买卖建议。

窗口起点 = `--as-of` 减 `--days`；归档总数与坏档数一并列出，避免「看起来只有两轮」的错觉。

## 边界

- **指针不是证据**：索引里的 `judgment` 是报告原文的复制，用于检索；引用它支撑新结论没有意义——必须回到冻结 run 读 claims 与 sources，再按当前研究重新入账。旧 `inference` 尤其不能直接当作新结论的依据。
- **不合并数字**：同名指标在不同 run 的口径可能不同（期间、币种、缩放、分部），索引只记录指标名，不给出「最新值」。数值比较请走 `claim.metric` 与 `financial_quality.py`。
- **实体抽取是文本匹配**：`entities` 来自 `plan.entity` 与 `claim.metric.entity`；查询是子串匹配，可能召回「BTC」相关的所有轮次，也可能漏掉只写代号的报告。它帮你找，不替你判断。
- **跳过坏档不静默**：读不了的 run 会进 `skipped` 并写明原因；索引失败不等于归档不存在。
- **只读**：`index` 只写索引文件，`query` 完全不写盘。归档文件的内容哈希在测试中逐字节比对，确保没有被改动。
- **不是后台监控**：没有轮询、没有提醒；它只是同一个目录下已冻结研究的检索视图。

## 在研究流程里的位置

1. **开始新研究前**：`query` 一下实体，看看旧判断、旧触发与旧缺口，决定这一轮到底要更新什么。
2. **更新研究时**：用旧 `run_id` 作 `parent_run`；先在记忆里找父报告，再决定 `judgment_changed`。
3. **写结论时**：如果本轮推翻了旧判断，明确写出旧判断是什么、哪个新证据改变了它——这正是记忆索引存在的意义。
4. **定期维护**：`index` 可以随时重建；索引与归档不一致时，以归档为准。
