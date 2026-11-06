# 投研助手 · Touyan

从一个投研问题出发，**找到证据、看清分歧，形成有依据的判断**。

投研助手为 **Coding Agent** 提供一套可延续的研究方法：围绕问题规划取证、比较解释、调用计算工具，再由独立审查梳理关键结论。报告连到原文，后续追问沿着已有证据和判断继续推进。

仓库包含研究 Skill、Python 工具和兼容插件清单。你可以按所用客户端的插件或 Skill 机制加载；下文以 Claude Code 展示安装方式。

[![Core checks](https://github.com/drewliu123/whymoved/actions/workflows/tests.yml/badge.svg)](https://github.com/drewliu123/whymoved/actions/workflows/tests.yml)

## 先看一个真实例子

**问题：微软 FY2025 营收增长，为什么自由现金流反而下降？**

核对官方年报后，研究给出的解释是：经营活动多带来 **176.14 亿美元**现金，但现金资本开支多了 **200.74 亿美元**，所以按「经营现金流 − 现金资本开支」计算的自由现金流减少 **24.60 亿美元**。营收增长约 **14.9%**，该口径自由现金流下降约 **3.3%**。

![微软真实案例的研究结果与现金流变化桥](examples/msft-cashflow/preview-compact.png)

- **[直接阅读研究报告](examples/msft-cashflow/research/work/report.md)**：先看判断和发现，再追溯计算与来源。
- **[查看完整案例](examples/msft-cashflow/README.md)**：研究输入、官方表格、独立算术脚本和运行记录。
- **[打开交互展示页](examples/msft-cashflow/index.html)**：下载后在浏览器查看研究结果、证据与计算、完整报告。

这次研究于 **2026-11-06** 完成，比较微软 **FY2024 与 FY2025** 的官方披露。报告把分散的财务指标连成一条现金流变化桥，并给出后续更新时值得继续核对的变量。

## 用它研究什么

- **解释变化**：公司为什么下跌？比较实际表现、背景和新增证据，区分不同解释。
- **梳理经营传导**：AI 用电增长如何进入设备公司的订单、利润和现金？找到值得深入核查的环节。
- **延续已有判断**：新披露改变了什么？保留旧研究，对比新增证据、判断变化和下一步观察。

每次研究围绕一个需要回答的问题展开。主研究 Agent 组织取证与分析，取证和审查 Agent 分工协作，工具展开计算与引用。你看到的是当前判断、重要发现和接下来该关注什么，完整底稿随报告保留。

## 快速开始

### 1. 直接看研究效果

```bash
git clone https://github.com/drewliu123/whymoved.git
cd whymoved
```

在浏览器打开 [案例展示页](examples/msft-cashflow/index.html)，或直接在 GitHub 阅读 [Markdown 报告](examples/msft-cashflow/research/work/report.md)。

### 2. 安装到 Coding Agent（以 Claude Code 为例）

准备支持插件的 Claude Code、可用模型、网页与终端工具，以及 Python 3.9+。在实际克隆目录执行：

```bash
export TOUYAN_HOME="$PWD/.local/touyan-data"
mkdir -p "$TOUYAN_HOME"
claude plugin marketplace add .
claude plugin install touyan@touyan-local
claude
```

新会话中调用：

```text
/touyan:research 英伟达这个月为什么下跌？先比较行业表现，再判断公司特有因素
/touyan:research AI用电如何进入电力设备利润？找最值得验证的传导环节
/touyan:research update <run_id> 核对新增披露是否改变原判断
```

使用 Codex、DeepSeek Harness 或其他客户端？查看 **[安装与加载方式](docs/installation.md#其他-coding-agent-的加载方式)**。

`TOUYAN_HOME` 用于存放本机研究数据。数据目录、插件更新和可选接口的设置见[安装指南](docs/installation.md)。

## 研究怎样组织

| 层次 | 职责 |
| --- | --- |
| 主研究 Agent | 界定要作的判断，选择方法，规划取证，连接事实并形成结论 |
| 取证与审查 Agent | 根据证据缺口检索、比较不同解释，独立复核主判断与原始问题 |
| Workflow / 研究协议 | 连接研究计划、证据、主张、审查、报告和更新，保持过程可追溯 |
| Python 工具 | 检查引用、时间和分析契约，重算固定财务模型，渲染并保存研究档案 |
| 宿主客户端 | 提供模型、网页、文件、终端与子 Agent 等执行能力 |

固定模型覆盖经营利润桥、FCFF、DCF 和反向 DCF，并提供单参数敏感性比较。设计与计算口径见[架构说明](docs/architecture.md)和[分析方法](skills/research/references/analysis-methods.md)。

## 按研究需要连接数据

| 能力 | 如何启用 |
| --- | --- |
| 核心研究、证据校验、报告与归档 | Python 3.9+ 标准库，配合宿主的模型与网页工具 |
| SEC 原始披露 | 配置独立运行时，以精确文件和原始报表开展取证；见[设置步骤](docs/installation.md#可选sec-原始披露运行时) |
| Financial Datasets 适配器 | 对接财务报表与行情服务；账户授权与配置见[金融接口说明](skills/research/references/financial-data.md) |
| 社区材料 | 通过 Last30Days 补充讨论、观点与反例；见[来源说明](skills/research/references/sources.md) |

第三方 EdgarTools 源码以固定提交的子模块保留。需要阅读时，执行 `git submodule update --init --recursive`。

## 验证与开发

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
```

[CI](.github/workflows/tests.yml) 在 Python 3.9、3.11 和 3.12 下检查核心测试、真实示例文件哈希、独立算术、研究契约及报告渲染。重放示例与参与开发见 **[开发指南](docs/development.md)**。

## 继续探索

| 入口 | 内容 |
| --- | --- |
| [真实示例](examples/msft-cashflow/README.md) | 从问题到判断、官方出处、计算与运行记录 |
| [研究 Skill](skills/research/SKILL.md) / [Agent 定义](agents) / [脚本](scripts) | 研究方法、协作角色与验证工具 |
| [安装](docs/installation.md) / [架构](docs/architecture.md) / [开发与贡献](docs/development.md) | 运行、设计和维护说明 |
| [研究资料](research/README.md) | 实验、方法比较、原始研究资料与第三方源码 |
| [验证证据](evidence/README.md) | 取证、回归与各轮验收记录 |
| [研究档案](journal/README.md) | 历次研究报告、判断变化与工作记录 |
| [历史导出](delivery/README.md) / [数据说明](data/README.md) | 发布材料、运行数据与配置说明 |
| [版本记录](CHANGELOG.md) / [档案策略](docs/archive-policy.md) | 版本演进与完整历史的保留方式 |

研究过程和历史档案可从上表继续探索。项目代码采用 [MIT License](LICENSE)，第三方依赖与引用材料保留各自许可。
