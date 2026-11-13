# 催化日历：日期、状态与查询

## 为什么要有它

研究报告里最常见的一句话是「12 月 9 日 FOMC 是下一个催化」。它是判断的一部分，却通常只是段落里的散文：没有日期字段、无法排序、无法回答「上周该看的东西看了吗」、更新时也无法机器对照。

催化日历不新建第二套触发体系。触发 id 已经存在于 `opportunity.triggers`，非交易研究已有 `watch` 列表；本页只给它们加**可选**的 `due`（ISO 日期/时刻）与 `type`，再由只读脚本汇总成日历视图。

## 字段

| 位置 | 字段 | 要求 |
| --- | --- | --- |
| `opportunity.triggers[]` | `due` | 可选，ISO 日期或时刻；不得早于 `report.as_of` |
| `opportunity.triggers[]` | `type` | 可选，`earnings` / `macro` / `regulatory` / `company` / `industry` |
| `watch[]` | `due` | 同上；`watch` 没有 id，日历按位置标为 `W1`、`W2` |
| `watch[]` | `type` | 同上 |

```json
{
  "watch": [
    {"signal": "Q3 财报验证毛利率", "meaning": "判断 68% 毛利率能否维持",
     "due": "2026-12-15", "type": "earnings", "claim_ids": ["C3"]}
  ],
  "opportunity": {
    "triggers": [
      {"id": "T1", "signal": "12 月 FOMC 是否暗示终点", "by": "12/9 附近",
       "due": "2026-12-09T19:00:00Z", "type": "macro",
       "supports_if": "暗示不加息", "weakens_if": "维持鹰派措辞", "invalidates_if": "50bp",
       "claim_ids": ["C7"]}
    ]
  }
}
```

`by` 仍是给人读的窗口（「12/9 附近」），`due` 是可计算的那一天。两者并存，**不要**从 `by` 的文本里猜日期。

## 查询

实现与 CLI 都是 `scripts/catalyst_calendar.py`；不要再使用旧名 `calendar.py`——它会遮蔽标准库的 `calendar`。

```bash
# 扫描本机归档，看未来 30 天
python3 "$TY_DIR/scripts/catalyst_calendar.py" --home "$TY_HOME" --due 30

# 指定一个已冻结报告与日历起点
python3 "$TY_DIR/scripts/catalyst_calendar.py" "$WORK/report.json" --as-of 2026-11-14 --due 14
```

输出 `{passed, as_of, as_of_text, horizon_days, upcoming, overdue, undated, notes}`：

- `upcoming`：`due` 不早于日历起点；按日期升序；每条带 `days_from_as_of`、`run_id`、`source`、`kind`（trigger / watch）、`id`、`type`、`signal`、`claim_ids`。
- `overdue`：`due` 已经过去。**它不等于未触发**，只表示没有记录后续核对；这正好暴露「该看没看」。
- `undated`：没有 `due` 的条目。不从自由文本猜日期，因此旧 run 的触发都会落在这里——这是诚实的状态，不是缺陷。

`--as-of` 默认取所读报告中最大的 `report.as_of`。退出码：0 成功，1 报告校验失败或参数非法，2 无法读取文件。

## 边界

- **不是后台监控**。本页与脚本都不会定时抓取、不会提醒、不会写状态；它只把已冻结报告里的日期排成一张表。
- **不自动判定命中**。命中与否仍要写进更新报告的 `update.opportunity.trigger_results`，并附证据；日历里的 `overdue` 不能当结论。
- **不新建 id 空间**。trigger id 仍由 `opportunity.triggers` 定义；`watch` 用位置编号 `W1..Wn`，不是独立注册的实体。
- **过去日期是合法的**：报告在 `due` 之前冻结即可；用更晚的 `--as-of` 复查时它们自然变成 `overdue`。
- **历史研究**：如果研究对象是过去的事件，`due` 可以写成历史日期，但那样它只是记录，不进入「未来 30 天」视图。

## 与研究流程的关系

1. 计划阶段把催化写进 `watch` 或 `opportunity.triggers`，能给日期就给 `due`。
2. 交付前用 `catalyst_calendar.py` 自查一遍：近期的催化是否都在表里、有没有已经过期没核对的。
3. 更新研究时，先跑日历看旧触发状态，再把核对结果写进 `trigger_results`。
