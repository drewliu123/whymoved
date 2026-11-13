# 开发与验证

安装及运行时分层见 [安装指南](installation.md)。贡献代码前，先在自己实际 clone 的目录中设置隔离数据根。Python 3.9 是核心最低支持版本，CI 同时检查 3.11 和 3.12；核心模块与测试仅使用标准库，不需要安装主依赖。新增语法和标准库 API 应保持 3.9 兼容，例如运行时类型标注可使用 `list[str]`，不能无条件使用较新版本才支持的 API。

## 本地基线

在仓库根目录执行：

```bash
export TOUYAN_HOME="$PWD/.local/touyan-data"
export PYTHONDONTWRITEBYTECODE=1
python3 -m unittest discover -s tests
```

当前基线为 416 个测试，以命令实际输出为准。测试用临时数据目录隔离大部分写入；显式设置数据根也可避免手工 CLI 命令落入历史默认目录。不要为运行核心测试安装 EdgarTools，也不要把第三方子模块自己的测试混入这个入口。

## 离线示例回归

[微软现金流示例](../examples/msft-cashflow/index.html)包含冻结的官方表格、研究输入及报告。以下命令不需要模型、API Key 或网络。两个脚本会重算并写回各自目录中的派生 JSON；运行后检查差异，数值改变应能解释并与冻结输入对应。

```bash
python3 examples/msft-cashflow/research/recompute_bridge.py
python3 examples/msft-cashflow/research/work/arithmetic.py
python3 scripts/research_plan.py examples/msft-cashflow/research/work/plan.json
python3 scripts/sources.py validate examples/msft-cashflow/research/work/sources.json
python3 scripts/check_claims.py examples/msft-cashflow/research/work/claims.json \
  --sources examples/msft-cashflow/research/work/sources.json --json
python3 scripts/analysis_contract.py check \
  --plan examples/msft-cashflow/research/work/plan.json \
  --report examples/msft-cashflow/research/work/report.json \
  --claims examples/msft-cashflow/research/work/claims.json \
  --sources examples/msft-cashflow/research/work/sources.json
```

工作输入在 [research/work](../examples/msft-cashflow/research/work/)，表格快照在 [official-tables.json](../examples/msft-cashflow/research/evidence/official-tables.json)。`calculations.json` 是透明计算记录；标了`op`的行由白名单算子重算，自由公式字符串不由核心 CLI 当成任意代码执行。上述算术脚本执行示例特定的复算，分析契约检查另外重算固定模型；二者都不能证明经济假设成立。

可另行渲染到本机隔离目录，避免覆盖已冻结的演示网页：

```bash
python3 scripts/render_report.py examples/msft-cashflow/research/work/report.json \
  --claims examples/msft-cashflow/research/work/claims.json \
  --sources examples/msft-cashflow/research/work/sources.json \
  --out-dir "$TOUYAN_HOME/example-render"
```

输出为 `report.md` 和 `report.html`；目录内已有输出时默认拒绝覆盖，重复运行可选择新的输出目录。通用渲染器输出与仓库中自含展示页的排版不要求逐字节相同。

## CI 覆盖范围

[离线工作流](../.github/workflows/tests.yml)在 Python 3.9 / 3.11 / 3.12 下运行单元测试、两个示例算术脚本、来源与证据契约、分析契约以及 Markdown/HTML 渲染。运行数据写到 runner 的临时目录，不安装核心 pip 依赖，也不初始化第三方子模块。

“离线”指这些检查不调用真实数据服务或模型；GitHub runner 获取代码及 Python 工具链仍需要平台网络。SEC 与金融接口的单元测试使用模拟响应。CI 通过不能代表真实 SEC 联网、账户权限、Claude Code 插件安装或浏览器视觉交互已验证。这些能力需在本机按实际环境单独检查，并如实记录状态和限制。

## 代码与数据边界

[scripts](../scripts/)是确定性 CLI 与契约实现，[tests](../tests/)是标准库回归测试，[研究协议](../skills/research/SKILL.md)及其参考文档描述模型应遵循的流程，[agents](../agents/)定义取证和审查职责。修改研究提示词时同步检查对应引用及协议，避免把流程要求误描述成代码已自动保证的能力。

`TOUYAN_HOME` 只指定研究数据根，不会移动插件源码，也不隔离 Last30Days 自己的缓存。默认数据根保留 `~/Desktop/投研助手` 以兼容既有用户；开发时显式使用 `$PWD/.local/touyan-data`，不要为了本机方便更改共享默认路径。

真实 SEC 配置与虚拟环境属于本机环境，生成办法见 [SEC 运行时安装](installation.md#可选sec-原始披露运行时)。[配置结构示例](../data/sec-runtime.example.json)只展示占位路径，不能直接复制为可用配置。不要提交身份、API Key、本机绝对运行时路径、虚拟环境或缓存；测试不应读取用户真实身份或联网。

## 新增能力的检查清单

增加一个脚本、模型种类或契约字段时，按以下清单同步，缺一项就会出现「文档写了、校验不认」的第三种状态：

1. **脚本**：docstring 写清输入、输出、边界与退出码（0 通过 / 1 输入不符合契约 / 2 无法读取）；错误用英文短句并带路径，不抛 traceback。
2. **测试**：正例、负例、边界各至少一条；涉及渲染的加 Markdown 与 HTML 双格式断言；涉及归档的加 `archive`/`load` 往返。
3. **契约**：可选字段必须向后兼容；旧档案保持可加载、可渲染；渲染变更用「字段存在才生效」的方式隔离，否则冻结示例哈希会失败。
4. **参考文档**：在 `skills/research/references/` 增加或更新说明，并在 [索引](../skills/research/references/README.md) 登记。
5. **入口表**：`docs/architecture.md` 的主代码入口表加一行。
6. **版本与记录**：`CHANGELOG.md` 加条目；`.claude-plugin/plugin.json` 与 `marketplace.json` 版本同步（`tests/test_packaging.py` 会检查三者一致）；`docs/iteration/log.md` 记本轮目标、改动、验证证据与遗留。
7. **回归**：`python3 -m unittest discover -s tests` 全绿；`examples/msft-cashflow/SHA256.json` 校验通过；冻结报告重新渲染逐字节相同。
8. **不伪造**：缺失写 `missing`/`null` 并说明原因；cannot verify（例如缩放不可解析）与 error 分开处理。

## 提交前复查

先阅读改动的最终 diff，确认文档从实际 clone 目录可执行、链接目标存在、生成输出没有混入无关变更。运行与改动相应的测试及离线示例检查，记录 Python 版本、执行结果及未验证范围。协议、schema 或固定模型变化应加入能验证行为的回归测试；纯文字修订通常只需链接和命令核对。

修改源码后，需按宿主的插件或 Skill 加载机制更新副本，再验证实际工具与权限；Claude Code 的市场更新命令见[更新说明](installation.md#更新已安装副本)，Codex、DeepSeek Harness 等加载路径见[兼容说明](installation.md#其他-coding-agent-的加载方式)。离线CLI通过、插件被识别与完整研究执行是不同的验证层次。
