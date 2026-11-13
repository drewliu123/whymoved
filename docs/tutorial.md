# 跟做式教程：从一份冻结报告到四类研究

这条路径把仓库里的四个真实示例串起来。每一步都给命令、预期的输出要点，以及「这一步在练什么」。全程离线，不需要 API；所有数字来自仓库内冻结的官方披露。

## 0. 准备

要求 Python 3.9+，已经有本仓库的克隆目录。下面用两个环境变量区分「插件源码」和「研究数据」：

```bash
export TY_DIR="$HOME/投研助手"                 # 换成你自己的克隆路径
export TY_HOME="${TY_HOME:-$HOME/Desktop/投研助手}"   # 研究数据根
python3 -c "import json;print(json.load(open('$TY_DIR/.claude-plugin/plugin.json'))['version'])"
```

最后一条应打印当前插件版本（例如 `0.59.0`）。数据根不必提前建好，归档步骤会创建。

## 1. 先读一份已冻结的研究

打开 [微软现金流示例](../examples/msft-cashflow/README.md)，或直接看它的 [报告](../examples/msft-cashflow/research/work/report.md)。这份报告回答「营收增长为什么自由现金流反而下降」，结论是现金资本开支增量超过经营现金流增量。

再运行三条命令，确认它能被当前代码复现：

```bash
python3 "$TY_DIR/scripts/analysis_contract.py" check \
  --plan "$TY_DIR/examples/msft-cashflow/research/work/plan.json" \
  --report "$TY_DIR/examples/msft-cashflow/research/work/report.json" \
  --claims "$TY_DIR/examples/msft-cashflow/research/work/claims.json" \
  --sources "$TY_DIR/examples/msft-cashflow/research/work/sources.json"
```

预期输出是一行 JSON，`"passed": true`、`"errors": []`。契约会重算派生计算、校验每条数字的来源与量纲，并检查图表与表格的引用。

```bash
python3 "$TY_DIR/scripts/memo_pack.py" "$TY_DIR/examples/msft-cashflow/research/work/report.json" \
  --claims "$TY_DIR/examples/msft-cashflow/research/work/claims.json" \
  --sources "$TY_DIR/examples/msft-cashflow/research/work/sources.json" | head -20
```

预期的是一页纸：判断、关键发现、改变判断的条件、主要风险与溯源。**这一步练的是**：一份研究交付前先过契约，再出一页纸。

## 2. 把示例归档成一次 run，并做跨轮检索

先把数据根指向临时目录，避免污染你自己的归档：

```bash
export TOUYAN_HOME="$(mktemp -d)/home"
python3 "$TY_DIR/scripts/research_run.py" archive \
  --report "$TY_DIR/examples/msft-segments/research/work/report.json" \
  --claims "$TY_DIR/examples/msft-segments/research/work/claims.json" \
  --sources "$TY_DIR/examples/msft-segments/research/work/sources.json" \
  --plan "$TY_DIR/examples/msft-segments/research/work/plan.json"
```

预期输出含 `run_id`（形如 `R20261113T213320Z-40af4c3ef248`）与 manifest 中每个文件的哈希。归档不可覆盖，哈希就是证据。

```bash
python3 "$TY_DIR/scripts/research_run.py" list
python3 "$TY_DIR/scripts/research_memory.py" index --home "$TOUYAN_HOME"
python3 "$TY_DIR/scripts/research_memory.py" query --home "$TOUYAN_HOME" 微软 | head -12
python3 "$TY_DIR/scripts/digest.py" --home "$TOUYAN_HOME" --as-of 2026-11-14 --days 30 | head -20
```

**这一步练的是**：归档之后，跨轮检索、摘要与体检都基于同一份冻结输入，而不是重新读一遍手写笔记。

```bash
python3 "$TY_DIR/scripts/doctor.py" --home "$TOUYAN_HOME" --renders
```

预期 `"passed": true`、`renders_checked` 为归档数量、`errors` 为空。`--renders` 会用当前渲染器重渲染归档，确认历史输出没有被改写。

## 3. 分部利润归因：收入增速不等于利润贡献

读 [分部示例](../examples/msft-segments/README.md)，再跑：

```bash
python3 "$TY_DIR/scripts/memo_pack.py" "$TY_DIR/examples/msft-segments/research/work/report.json" \
  --claims "$TY_DIR/examples/msft-segments/research/work/claims.json" \
  --sources "$TY_DIR/examples/msft-segments/research/work/sources.json" | head -24
```

预期看到：FY2025 营业利润增加 19,095，其中生产力与业务流程 10,112、智能云 6,776、个人计算 2,207——**利润增量第一是生产力分部，不是云**；云的收入增量更大。模型附录里能看到分部驱动表、基期/情景利润率与「固定模型重算结果」。

**这一步练的是**：用分部驱动模型把「增长来自哪里」拆到可核实的层面，而不是复述叙事。

## 4. 盈利质量：利润有没有现金支撑

读 [质量示例](../examples/msft-earnings-quality/README.md)，然后从账本装配报表、再跑筛查：

```bash
python3 "$TY_DIR/scripts/quality_inputs.py" "$TY_DIR/examples/msft-earnings-quality/research/work/claims.json" \
  > /tmp/msft-statements.json
python3 "$TY_DIR/scripts/financial_quality.py" /tmp/msft-statements.json | head -40
```

预期：`cash_conversion` 约 1.34、`accrual_ratio` 为负、`capex_to_da` 约 1.89，`flags` 为空。报表里每个字段都带 `claim_ids`，`unattributed` 若不为空会明确列出。

**这一步练的是**：质量指标从证据装配，不手抄；缺字段如实为 `null`，并在报告限制里说明。

## 5. 三年趋势：质量是在改善还是恶化

读 [三年趋势示例](../examples/msft-trend/README.md)。数据来自 SEC XBRL：

```bash
python3 "$TY_DIR/scripts/quality_inputs.py" "$TY_DIR/examples/msft-trend/research/work/claims.json" \
  > /tmp/msft-trend.json
python3 "$TY_DIR/scripts/financial_quality.py" /tmp/msft-trend.json | head -40
```

预期看到 `dso` 约 90.3、`cash_cycle` 约 −20.7（负现金周期）、`accrual_ratio` 为负；红旗未触发。报告内嵌收入与经营现金流折线图。

**这一步练的是**：三个期间的趋势判断，以及「应收天数上升是唯一压力点」这种有方向但不夸大的结论写法。

## 6. 收尾与清理

```bash
python3 "$TY_DIR/scripts/doctor.py" --home "$TOUYAN_HOME" --renders --as-of 2026-11-14
```

确认 `errors` 为空后，临时数据根可以直接删掉（它只包含本教程归档的那一轮）：

```bash
rm -rf "$(dirname "$TOUYAN_HOME")"
```

## 常见错误

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| `no journal/runs directory` | 数据根为空或路径写错 | 先跑一次 `research_run.py archive`，或检查 `TOUYAN_HOME` |
| `unsafe research runs directory` | `journal` 或 `journal/runs` 是符号链接 | 换成真实目录；祖先符号链接是允许的 |
| `analysis contract` 返回 `errors` | 契约失败 | 按错误里的字段路径修输入；不要改渲染产物 |
| `claims validation failed` | 主张缺来源、类型不符或引用了不存在的 id | 先跑 `sources.py validate` 与 `check_claims.py` 定位 |
| `doctor --renders` 报 `differs from the current renderer` | 渲染器变化或归档被改 | 不要手改归档；把差异当作兼容性问题报告 |

## 接下来读什么

- 方法口径：[analysis-methods](../skills/research/references/analysis-methods.md)、[financial-quality](../skills/research/references/financial-quality.md)
- 证据与结论写法：[evidence](../skills/research/references/evidence.md)、[memo-template](../skills/research/references/memo-template.md)
- 迭代过程与已知边界：[review-2026-11.md](iteration/review-2026-11.md)
