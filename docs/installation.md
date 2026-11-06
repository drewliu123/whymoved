# 安装与首次运行

投研助手面向支持相应插件或 Skill 加载机制的 **Coding Agent**。本页先给出 Claude Code 的完整安装示例，再说明 Codex 与 DeepSeek Harness 等客户端的加载方式。核心 Python CLI 要求 Python 3.9+，仅使用标准库；阅读离线示例无需模型凭据或 SEC 运行时。以下终端命令使用 macOS / Linux 的 POSIX shell。

## 获取源码并指定数据目录

```bash
git clone https://github.com/drewliu123/whymoved.git
cd whymoved
export TOUYAN_ROOT="$PWD"
export TOUYAN_HOME="$PWD/.local/touyan-data"
mkdir -p "$TOUYAN_HOME"
python3 --version
```

`TOUYAN_ROOT` 是你实际 clone 后的插件源码根目录；`TOUYAN_HOME` 是本机运行数据根目录，二者用途不同。后续命令均从这个克隆目录执行。每次新开终端都需重新设置变量，或自行把实际绝对路径加入本机 shell 配置。不要复制作者桌面上的路径。

未设置 `TOUYAN_HOME` 时，现有代码仍默认使用 `~/Desktop/投研助手`，以兼容历史数据；新用户建议显式设置上面的隔离目录。归档写入 `$TOUYAN_HOME/journal/runs/`，工作输入通常放在 `$TOUYAN_HOME/journal/work/`。源码目录中的历史资料不代表新数据会自动迁入本机数据根。

仓库内第三方 EdgarTools 源码以子模块记录。核心离线 CLI、示例和单元测试不需要初始化子模块；需要阅读该第三方源码时再运行：

```bash
git submodule update --init --recursive
```

子模块源码与下面可选 SEC 虚拟环境是两回事，初始化子模块不会安装 Python 包。

## 先离线看一个完整例子

直接用浏览器打开 [微软现金流示例](../examples/msft-cashflow/index.html)，或在文件管理器中打开 `examples/msft-cashflow/index.html`。该文件可直接阅读，不需要启动服务器。研究输入位于 [示例工作目录](../examples/msft-cashflow/research/work/)，原始表格快照位于 [official-tables.json](../examples/msft-cashflow/research/evidence/official-tables.json)。示例是冻结材料演示，不是实时行情或当前投资建议。

使用本机 Python 检查证据账本与分析契约：

```bash
python3 scripts/research_plan.py examples/msft-cashflow/research/work/plan.json
python3 scripts/check_claims.py examples/msft-cashflow/research/work/claims.json \
  --sources examples/msft-cashflow/research/work/sources.json --json
python3 scripts/analysis_contract.py check \
  --plan examples/msft-cashflow/research/work/plan.json \
  --report examples/msft-cashflow/research/work/report.json \
  --claims examples/msft-cashflow/research/work/claims.json \
  --sources examples/msft-cashflow/research/work/sources.json
```

这些检查只读取仓库中的材料，不调用模型或联网。完整复算、渲染和开发验证见 [开发指南](development.md)。

## 在 Claude Code 中安装插件

先按 [Claude Code 官方安装说明](https://code.claude.com/docs/en/setup)安装并完成本机授权，确认 `claude --version` 可用。在实际 clone 目录执行：

```bash
claude plugin marketplace add "$TOUYAN_ROOT"
claude plugin install touyan@touyan-local
```

从已设置 `TOUYAN_HOME` 的同一终端启动 Claude Code，让插件继承数据目录：

```bash
claude
```

在新会话中调用：

```text
/touyan:research 微软现金流增长由哪些因素驱动？先核对官方披露与比较期间
```

自然语言研究依赖宿主的模型、可用检索工具和相应账户权限；上面的 `/touyan:research` 是 Claude Code 中的命名空间调用示例。

## 其他 Coding Agent 的加载方式

### Codex：使用兼容的插件市场入口

具备 `plugin` 命令的 Codex 版本提供以下入口，在实际克隆目录执行：

```bash
codex plugin marketplace add "$TOUYAN_ROOT"
codex plugin add touyan@touyan-local
```

命令语法已按本机 `codex plugin --help`、`codex plugin marketplace add --help` 和 `codex plugin add --help` 核对；Codex 公开实现支持读取 `.claude-plugin/marketplace.json`，也包含 Claude Code 格式插件清单的兼容处理。参见[市场加载实现](https://github.com/openai/codex/blob/main/codex-rs/core-plugins/src/marketplace.rs)及[插件清单实现](https://github.com/openai/codex/blob/main/codex-rs/core-plugins/src/manifest.rs)。

本轮核对的是命令和清单格式，没有替用户执行安装或完整模型调用。安装后按客户端确认 Skill 已加载，并核对网页工具、终端、子 Agent 与权限的映射；不要将不同客户端的命令名称视为一致。

### DeepSeek Harness：通过 Skill 加载机制使用

DeepSeek Harness 的本地 Skill provider 支持自定义技能目录。使用该机制时，将完整仓库中的 `skills` 目录加入宿主的 Skill 搜索目录，并保留同一仓库的 `scripts`、`agents` 和参考文档。该方式是加载研究 Skill，不是把本仓库当成 TypeScript / npm 原生扩展安装。

本例曾由 DeepSeek Harness 会话 Agent 按研究协议执行，调用项目脚本完成核验与输出；这不等同于已替所有版本完成一键插件安装测试。具体配置入口以客户端版本为准。

### 其他支持 Skill 的客户端

也可以让具备文件、网页和终端工具的 Coding Agent 读取[研究 Skill](../skills/research/SKILL.md)，按协议调用完整仓库中的脚本。支持独立子 Agent 时加载对应[角色定义](../agents/)；缺少独立审查能力时应记录未执行，不能把同一 Agent 的自查标为独立复核。

不要只复制孤立的 `SKILL.md`：正文按文件位置定位插件根，丢失相邻参考或仓库的 `scripts` 会导致路径失效。Skill加载、插件安装识别、工具映射及完整研究执行分别核对，不能只凭其中一步宣布全部兼容。

## 更新已安装副本

在实际克隆目录先更新源码，再更新本地市场及插件：

```bash
git pull --ff-only
claude plugin marketplace update touyan-local
claude plugin update touyan@touyan-local
```

开启新会话并核对实际插件版本；编辑源码不会自动更新 Claude Code 的缓存副本。更新时保留原 `TOUYAN_HOME` 即可继续读取原数据。插件加载问题先检查 [插件清单](../.claude-plugin/plugin.json)及 [本地市场清单](../.claude-plugin/marketplace.json)，不要用源码版本替代已安装版本的确认。

## 可选：SEC 原始披露运行时

只有需要实时 SEC 获取时才配置这一部分。入口仍可用核心 Python 3.9+，独立解析进程需要本机 **Python 3.11+** 和固定版本 **edgartools==5.62.1**。以下命令会创建本机虚拟环境，并从包索引安装依赖；离线示例和核心测试无需执行。

在 clone 根目录、已设置 `TOUYAN_HOME` 的终端中执行（也可将 `python3.11` 换成本机已安装的其他 Python 3.11+）：

```bash
python3.11 -m venv .local/sec-venv
.local/sec-venv/bin/python -m pip install 'edgartools==5.62.1'
.local/sec-venv/bin/python - <<'PY'
import json
import os
import sys
import sysconfig
from pathlib import Path

data_root = Path(os.environ["TOUYAN_HOME"]).expanduser()
target = data_root / "data" / "sec-runtime.json"
target.parent.mkdir(parents=True, exist_ok=True)
config = {
    "schema_version": 1,
    "python": os.path.abspath(sys.executable),
    "site_packages": sysconfig.get_paths()["purelib"],
}
# 首次配置拒绝覆盖，避免误写已有运行时。
with target.open("x", encoding="utf-8") as handle:
    json.dump(config, handle, ensure_ascii=False, indent=2)
    handle.write("\n")
print(target)
PY
python3 scripts/sec_data.py doctor
```

配置由虚拟环境内的 Python 生成，`sys.executable` 保留该虚拟环境的解释器路径，`sysconfig.get_paths()["purelib"]` 给出本机真实包目录；不要手写 Python 小版本目录，也不要把虚拟环境解释器符号链接解析成系统解释器。已有配置时先自行检查本地文件，再决定如何迁移；命令的 `FileExistsError` 表示已有文件，未被覆盖。可参考 [配置结构示例](../data/sec-runtime.example.json)，其中占位路径不能直接运行。真实配置保存在数据根下，不应提交给仓库。

SEC 要求的 `EDGAR_IDENTITY` 由用户自行在本机调用进程环境中设置，使用符合 SEC 要求的联系身份；不要写入 runtime JSON、研究输入、仓库或对话。`doctor` 检查独立运行时，不代表已成功联网取证。配置好身份后，用户可自行运行：

```bash
python3 scripts/sec_data.py filings MSFT --form 10-K --limit 2
```

缺少身份或运行时会返回 `not_run`；只有实际返回包才能判断获取状态。`partial`、错误或空结果不等于完整取证。获取包进入研究前仍需核对文件、引文、期间和公开时间，见 [SEC 数据参考](../skills/research/references/sec-data.md)。

## 其他可选来源

[Financial Datasets 适配器](../skills/research/references/financial-data.md)按需从调用进程读取 `FINANCIAL_DATASETS_API_KEY`；未配置时返回 `not_run`，账户权限和费用由服务方决定。核心离线流程不要求该 Key。社区检索可选 Last30Days，使用独立 Python 3.12+ 运行时；平台授权、缓存和实际可用性需单独确认，`TOUYAN_HOME` 不隔离该引擎自身的缓存。具体来源规则见 [来源参考](../skills/research/references/sources.md)。
