# last30days 原理图解（费曼版）

> 依据：本机安装的 last30days v3.30.0（`~/.claude/plugins/cache/last30days-skill/last30days/3.30.0/`）的 SKILL.md、CONCEPTS.md、mcp/README.md、pyproject.toml，以及 2026-11-01 实际运行的 `doctor` 结果。

## 0. 一句话

last30days = **一本给 Claude 看的操作手册（Skill）** + **一台 Python 抓取排序引擎（Engine）**。
Claude 当主编：定选题、拆搜索词、写稿；引擎当跑腿记者团：同时去 Reddit / X / YouTube / HN / Polymarket / GitHub 抓近 30 天的帖子，按点赞、评论、真金白银的赔率排好序交回来。

## 1. 三层结构：Skill ≠ MCP ≠ Tool

```mermaid
flowchart TB
    U[你：/last30days 英伟达财报] --> C

    subgraph Host[Claude Code（Harness / 宿主）]
        C[Claude 模型<br/>主编：规划 + 判断 + 写作]
        T1[Read]:::tool
        T2[Write]:::tool
        T3[Bash]:::tool
        T4[WebSearch]:::tool
        T5[AskUserQuestion]:::tool
        C --> T1 & T2 & T3 & T4 & T5
    end

    T1 -->|按条件读| S[SKILL.md + references/*.md<br/>操作手册]
    T2 -->|写查询计划 JSON| P[(plan.json 临时文件)]
    T3 -->|python3.12 last30days.py --plan ...| E

    subgraph E[Python 引擎 scripts/last30days.py]
        direction LR
        F[并发抓取] --> N[归一化/去重] --> R[打分重排] --> K[聚类] --> O[输出证据+页脚]
    end

    E --> X1[Reddit 公开页]
    E --> X2[X: bird + Chrome cookie]
    E --> X3[yt-dlp → YouTube]
    E --> X4[HN Algolia API]
    E --> X5[Polymarket Gamma API]
    E --> X6[gh CLI → GitHub]
    E -.未开启.-> X7[TikTok/IG/Threads…<br/>需 ScrapeCreators key]
    E -.未开启.-> X8[小红书 localhost:18060<br/>xiaohongshu-mcp 服务]

    classDef tool fill:#eef,stroke:#88f
```

## 2. 一次调研的完整时序

```mermaid
sequenceDiagram
    participant 你
    participant Claude
    participant Skill as SKILL.md/references
    participant Web as WebSearch
    participant Eng as Python 引擎
    participant Src as 各平台

    你->>Claude: /last30days 主题
    Claude->>Skill: Read 根手册 + runtime.md
    Claude->>Eng: Bash: 找 Python 3.12、首跑检查、doctor --cached
    Claude->>Web: Step 0.5 解析实体（X 账号、subreddit、GitHub 仓库）
    Claude->>Claude: Step 0.75 自己写查询计划 JSON（LAW 7：你是规划者）
    Claude->>Eng: Bash: last30days.py --plan plan.json --emit=compact
    par 并发扇出
        Eng->>Src: Reddit
        Eng->>Src: X
        Eng->>Src: YouTube
        Eng->>Src: HN / Polymarket / GitHub
    end
    Eng-->>Claude: 排好序的证据簇 + 统计页脚
    Claude->>Web: 补充网页搜索
    Claude->>你: 按 LAW 1-11 写成“What I learned:” + 引用 + 页脚
    Eng-->>Eng: 保存 md 到 ~/Documents/Last30Days
```

## 3. 引擎内部流水线

```mermaid
flowchart LR
    A[查询计划<br/>N 个子查询] --> B[Fan-out<br/>子查询 × 来源<br/>线程池+超时]
    B --> C[Subquery stream<br/>每条流各自排序]
    C --> D[Fusion<br/>按规范化 URL 合并成 Candidate]
    D --> E[Entity grounding<br/>没提到主实体 → 强降权]
    E --> F[Rerank<br/>有 LLM key 用模型打分<br/>无 key 用本地词法+互动量]
    F --> G[Cluster<br/>MMR 选代表]
    G --> H[Render<br/>证据区 + 页脚]
```

## 4. 依赖地图

```mermaid
flowchart TB
    subgraph 必需
        PY[Python ≥ 3.12<br/>零 pip 依赖，只用标准库]
        CC[一个会调工具的宿主<br/>Claude Code/Codex/Cursor…]
    end
    subgraph 来源级可选
        YT[yt-dlp → YouTube]
        GH[gh → GitHub]
        ND[node → 内置 bird X 客户端]
        CK[Chrome cookie 同意 → X]
        SC[SCRAPECREATORS_API_KEY → TikTok/IG/Threads/LinkedIn/Pinterest + 回填]
        XAI[XAI_API_KEY / X_BEARER_TOKEN → 免 cookie 的 X]
        BS[BSKY_* → Bluesky]
        PPLX[PERPLEXITY / OPENROUTER → Perplexity]
        PP[*-pp-cli → digg/techmeme/arxiv/trustpilot]
        XHS[xiaohongshu-mcp 本地服务 → 小红书]
    end
    subgraph 质量增强可选
        LLM[OPENAI/GEMINI/OPENROUTER key → LLM 重排]
        GQ[GROQ_API_KEY → 无字幕视频转写]
    end
```

## 5. 你这台机器现在的状态（2026-11-01 doctor 实测）

| 状态 | 来源 | 说明 |
|---|---|---|
| ● 可用 | Reddit | 公开免 key 抓取；无 ScrapeCreators 回填 |
| ● 可用 | YouTube | yt-dlp 2026.10.21，搜索+字幕+评论 |
| ● 可用 | Hacker News | 免 key |
| ● 可用 | Polymarket | 免 key |
| ● 可用 | GitHub | gh 2.101.0 |
| ● 可用 | Library | 已存 3 份简报，会作为“历史背景”出现 |
| ◐ 已开未验证 | X | bird + Chrome cookie，要跑一次才知道会话是否有效 |
| ○ 可开 | Web | 目前由 Claude 自己的 WebSearch 代劳 |
| ○ 可开 | 小红书 | INCLUDE_SOURCES 已写，但 18060 端口没服务在跑，所以实际不生效 |
| ○ 可开 | TikTok/IG/Threads/LinkedIn/Pinterest/Meta Ads/Telegram | 都卡在 ScrapeCreators key |
| ○ 可开 | Bluesky / Truth Social / Perplexity / digg / techmeme / arxiv / trustpilot / amazon | 各缺 key 或 CLI |

凭据：`.env` 里没有任何 API key，全靠免 key 路径 + 浏览器 cookie。
