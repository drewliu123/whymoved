# 跨轮研究记忆示例：一次复核如何被记住

这个示例展示研究记忆的最小工作流：**两条真实归档**（父研究 + 一次复核），以及 `thread` 与 `digest` 如何把它们连起来。

- 父 run：微软 FY2025「营收增长但 FCF 下降」的完整研究（与 [现金流示例](../msft-cashflow/README.md)同一份输入）；
- 子 run：一次复核更新，`judgment_changed=false`，理由「复核官方年报与自由现金流计算，未发现新证据」；
- 两条 run 都在 `home/journal/runs/` 下，带 manifest、哈希与冻结的 `report.md` / `report.html`。

## 冻结输出

| 文件 | 内容 |
| --- | --- |
| [thread.json](thread.json) | 子 run 的沿革：`length=2`，顺序为父 → 子；父轮 `judgment_changed=null`，子轮 `false` |
| [digest.md](digest.md) | 2026-11-14 起 30 天的摘要：本窗口 2 轮、同题 2 轮、结论版本 1 个 |

这两份输出由测试从示例 home 重放并逐字节比对；如果 `thread` 或 `digest` 的逻辑变化，测试会直接失败。

## 命令

```bash
# 在示例 home 上重放（会写 journal/index.json，测试在临时副本上运行）
python3 scripts/research_memory.py index --home examples/memory-workflow/home
python3 scripts/research_memory.py thread --home examples/memory-workflow/home R20261114T062832Z-83a837b1bc84
python3 scripts/digest.py --home examples/memory-workflow/home --as-of 2026-11-14 --days 30
```

## 这个示例演示什么

- **沿革不是重跑**：子 run 明确记录「判断未变」，`thread` 仍保留父子关系；`digest` 把同题多轮折叠并标注「结论版本 1 个」，不会把两轮当成两次独立验证。
- **记忆只存指针**：索引记录 run id、截点、判断、主张数与模型名；原始证据仍在各自归档里。
- **可重放**：示例 home 是普通数据根，`doctor`、`opportunities`、`digest` 都按同一规则读取。

## 边界

- 示例只有两条 run、一次「未变」更新；「论点变化」路径由 [机会契约](../../skills/research/references/research-value.md)与真实 NVDA 链验收覆盖，但未在此示例中冻结。
- 摘要窗口按报告 `as_of` 计算；补档历史研究不会落进当前窗口。
