# AKShare 免费中文资讯实测

测试时间：2026-11-02T10:28:31.165097+08:00

官方文档：https://akshare.akfamily.xyz/data/stock/stock_research.html

临时 venv 隔离依赖；每项仅调用一次，45 秒硬超时。个股新闻直接采用 600519，未测试 NVDA。

## stock_info_global_cls
- 状态：timeout；exit=124；耗时=45.014 秒
- Python=3.12.13；AKShare=1.20.21；pandas=3.1.0
- 实际命令：`/tmp/akshare-free-20261101.kruquy/venv/bin/python -I /Users/frankzhang/Desktop/投研助手/evidence/free-sources-20261101/akshare/scripts/probe.py --worker stock_info_global_cls`
- 参数：{'symbol': '全部'}；函数签名：未取得
- 行数：未取得；列：未取得
- 最早：未取得；最新：未取得；未来日期异常：未取得
- 内容：未取得；字段：None；非空行：None；长度范围：None

## stock_info_global_em
- 状态：timeout；exit=124；耗时=45.013 秒
- Python=3.12.13；AKShare=1.20.21；pandas=3.1.0
- 实际命令：`/tmp/akshare-free-20261101.kruquy/venv/bin/python -I /Users/frankzhang/Desktop/投研助手/evidence/free-sources-20261101/akshare/scripts/probe.py --worker stock_info_global_em`
- 参数：{}；函数签名：未取得
- 行数：未取得；列：未取得
- 最早：未取得；最新：未取得；未来日期异常：未取得
- 内容：未取得；字段：None；非空行：None；长度范围：None

## stock_news_em
- 状态：timeout；exit=124；耗时=45.014 秒
- Python=3.12.13；AKShare=1.20.21；pandas=3.1.0
- 实际命令：`/tmp/akshare-free-20261101.kruquy/venv/bin/python -I /Users/frankzhang/Desktop/投研助手/evidence/free-sources-20261101/akshare/scripts/probe.py --worker stock_news_em`
- 参数：{'symbol': '600519'}；函数签名：未取得
- 行数：未取得；列：未取得
- 最早：未取得；最新：未取得；未来日期异常：未取得
- 内容：未取得；字段：None；非空行：None；长度范围：None

## 阻塞与限制

三个子进程各在45秒硬截止终止（含import初始化）。没有捕获HTTP响应，尚不能区分初始化耗时与上游网络阻塞，不能据此认定三个源失效。没有重试。行列、时间范围、两条标题及真实链接均未取得，正文未抓取，未来日期检查未完成。raw目录每来源文件仅保存无响应状态元数据，并非上游原始响应。

归档目录按要求保留20261101；实际机器时钟为2026-11-02 10:28 Asia/Shanghai，应明确区分目录日期与实测日期。

依赖安装成功（exit=0）；临时环境：/tmp/akshare-free-20261101.kruquy/venv。实际安装命令：`uv venv --python python3 /tmp/akshare-free-20261101.kruquy/venv`、`uv pip install --python /tmp/akshare-free-20261101.kruquy/venv/bin/python --no-cache akshare`。
