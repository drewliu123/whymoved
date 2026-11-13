# 行业传导图：节点、机制、时滞与瓶颈

## 什么时候用

主题研究常写成一段传导叙述：「AI 用电需求 → 并网排队 → 变压器交付 → 设备商毛利」。这段话里每一环都可能断：需求没有对应订单、并网容量卡住、交付周期太长、毛利被成本吃掉。传导图把这条链变成可检查的结构：

- 每个节点有**可观察指标**与对应主张；
- 每条边写清**机制**与**时滞**；
- 明确一个**瓶颈**节点，并找出哪些节点能到达它。

它回答「链条在哪一环最可能断、断点用什么指标核对」，不回答「这次一定断」。

## 输入

```json
{
  "schema_version": 1,
  "theme": "AI 用电需求传导",
  "as_of": "2026-11-14",
  "nodes": [
    {"id": "DEMAND", "label": "AI 训练用电需求", "kind": "demand",
     "observables": ["数据中心新签订单", "云厂商capex指引"], "claim_ids": ["C1"]},
    {"id": "GRID", "label": "并网容量", "kind": "capacity",
     "observables": ["并网排队时长", "电网投资计划"], "claim_ids": ["C2"]},
    {"id": "EQUIP", "label": "变压器交付", "kind": "capex",
     "observables": ["交付周期", "在手订单"], "claim_ids": ["C3"]},
    {"id": "MARGIN", "label": "设备商毛利", "kind": "margin",
     "observables": ["毛利率", "产能利用率"], "claim_ids": ["C4"]}
  ],
  "edges": [
    {"from": "DEMAND", "to": "GRID", "mechanism": "并网排队", "lag": "6-18个月", "claim_ids": ["C2"]},
    {"from": "GRID", "to": "EQUIP", "mechanism": "扩容订单", "lag": "3-9个月", "claim_ids": ["C3"]},
    {"from": "EQUIP", "to": "MARGIN", "mechanism": "产能利用率", "lag": "1-2个季度", "claim_ids": ["C4"]}
  ],
  "bottleneck": {"node": "GRID", "reason": "并网审批与电网投资节奏", "claim_ids": ["C2"]}
}
```

- 节点 `id` 必须是安全标识且唯一；`kind` 取 demand / capex / capacity / price / margin / policy / cash / other。
- `observables` 至少一条，且必须是**能核对**的观察（「订单」「排队时长」），不是「景气度」这类空词。
- 边必须有 `mechanism` 与 `lag`；时滞是研究者给出的窗口，工具不做换算。
- `claim_ids` 可选，但给了就不能为空；配合 `--claims` 时会核对是否真的存在。
- 自环、重复边、悬空引用直接拒绝；环路只提示不判错（价格与需求可能真的互相反馈）。

## 运行与输出

```bash
python3 "$TY_DIR/scripts/transmission.py" "$WORK/transmission.json" --claims "$WORK/claims.json"
```

输出：

- `directions`：每个节点相对瓶颈的位置——`upstream`（能到达瓶颈）、`downstream`（瓶颈之后）、`bottleneck`、`unrelated`（与瓶颈无路径连接）。
- `distances`：到瓶颈的跳数（不是时间）。
- `paths`：从各个源头（无入边的节点）到瓶颈的路径；多条源头会给出多条。
- `warnings`：无关节点、环路、没有挂 claim_ids 的节点、终点不在路径上的节点。

## 边界

- **不判断机制真假**：`mechanism` 是研究者的解释，工具只检查它被写出来、有方向、有时滞。
- **跳数不是时间**：`distances` 是图上的跳数；真正的时滞在各边的 `lag` 里，不能被加总成一条时间线。
- **瓶颈由研究者指定**：工具不会自动挑「最重要的节点」；换一个瓶颈，整张图的方向判断都会变，这个选择要在正文解释。
- **一个主题一张图**：不要把所有宏观变量都塞进来；无关节点会立刻被标成 `unrelated`。
- **不产生主张**：节点与边只是组织已有证据；引用数字仍须回到 claims 与来源。
