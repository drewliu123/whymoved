# Dexter 同源金融接口：最小只读适配

本地入口：`scripts/financial_data.py`。独立 Python 3.9+ 标准库实现，按 Dexter 的公开 API 契约调用同一家供应商 Financial Datasets；没有导入或运行 Dexter 的 TypeScript/LangChain Agent，也没有复用其自然语言路由器。

## 覆盖范围

| operation | 服务端路径 | 用途 |
|---|---|---|
| income | /financials/income-statements/ | 利润表 |
| balance | /financials/balance-sheets/ | 资产负债表 |
| cashflow | /financials/cash-flow-statements/ | 现金流量表 |
| financials | /financials/ | 三张报表 |
| snapshot | /prices/snapshot/ | 当前行情快照 |

基址固定为 `https://api.financialdatasets.ai`；未实现新闻、SEC全文、选股、历史价格及自然语言公司识别。ticker 必须明确指定，市场与标的覆盖取决于供应商。

## 调用

下列命令从插件源码根目录执行。研究 Agent 应把脚本路径换成插件根下的绝对路径，输出放在本轮独立 WORK 目录。

```bash
python3 scripts/financial_data.py income AAPL --period annual --limit 5
python3 scripts/financial_data.py financials MSFT --period quarterly --limit 4 --report-period-lte 2025-12-31
python3 scripts/financial_data.py snapshot AAPL
```

程序只从进程环境读取 `FINANCIAL_DATASETS_API_KEY`，不扫描本机凭据文件、不加载 `.env`、不打印或接受命令行 Key。Key 由用户在自己的服务配置中管理，不能贴到对话或版本库。更改外部服务配置、付费或安装插件不是此脚本的职责。

未配置时返回 `not_run`，不发送网络请求。若只是确认公开访问限制，可以显式发起不带 Key 的探测：

```bash
python3 scripts/financial_data.py income AAPL --limit 1 --public-probe
python3 scripts/financial_data.py snapshot AAPL --public-probe
```

`--public-probe` 即使环境中已有 Key 也不会发送。HTTP 402 记录为 `payment_required`，从不执行 x402 付款；401/403 为 `auth_failed`，429 为 `rate_limited`，不自动重试，不跟随重定向。连通性探测也只能证明该次请求的状态，不能证明所有账户或所有端点必须付费。

可选 `--out <new-file.json>` 保存完整结果，拒绝覆盖已有文件。退出码：0 为 `ok` / `no_results`，2 为未配置、部分数据或失败。`partial` 并非完整成功，调用者应检查 JSON 状态。

## 研究接入与证据边界

输出包含 operation、params、source_url、retrieved_at、http_status、status、data、raw_response 及成功 JSON 响应的 SHA-256。保留供应商返回的 currency、period、accession_number；不做字段缩放或单位猜测。report_period_gte/lte 只过滤报告期，不代表该报告在历史截点已经披露。

这是原始获取包，不是 sources v2 候选，也不直接创建 claims。fact-collector 读取包后，根据真实披露与供应商出处补原文、定位、证券身份、报价时刻、币种、缩放、报告期和公开时间，再按现有来源契约创建候选。供应商 URL 不是 SEC/交易所原始文件，不能自动赋予 T0 资格；无证据资格的数据可保留为未选候选或检索线索。

`ok` 只表示预期容器结构可读取，不代表字段齐全或数字正确。用于模型之前必须核对实际字段与口径，缺失不能当作零。若服务端带 next_page_url，首版保留第一页并返回 `partial`，不宣称已取得完整历史；当前快照不用于假装重建历史报价。

## 实测与实现参考

2026-11-01 本轮公开访问探测：AAPL 利润表与行情快照均收到 HTTP 402，服务端要求 API Key 或 x402 支付。当前未配置 Key，尚未验证授权成功后的真实数据。其余端点仅依据上游契约实现并使用模拟响应测试，不能视为已获真实数据。

上游：
- https://github.com/virattt/dexter/blob/main/src/tools/finance/fundamentals.ts
- https://github.com/virattt/dexter/blob/main/src/tools/finance/stock-price.ts
- https://github.com/virattt/dexter/blob/main/src/tools/finance/api.ts

上游 main 会变动；本轮精确 commit、源码摘要及公开探测保存在 `evidence/dexter-interface-20261101/`。接口兼容不表示 Financial Datasets 的数据免费，数据许可与调用权限需由供应商确认。

离线测试：`python3 -m unittest discover -s tests -p test_financial_data.py -v`。源码更改不会自动更新已安装插件缓存。
