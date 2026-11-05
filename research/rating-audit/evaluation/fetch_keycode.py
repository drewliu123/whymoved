import json,pathlib,urllib.request,concurrent.futures
R=pathlib.Path(__file__).resolve().parent
selection={
'forecastbench':['src/leaderboard/main.py','src/resolve/_prepare.py','src/resolve/resolve_all.py','src/question_sampling/_prepare.py','src/www.forecastbench.org/docs/index.md','requirements.runtime.txt','src/leaderboard/requirements.txt'],
'FINSABER':['backtest/toolkit/execution.py','backtest/toolkit/metrics.py','backtest/toolkit/backtest_framework_iso.py','backtest/data_util/backtest_dataset.py','backtest/data_util/finsaber_parquet_dataset.py','backtest/toolkit/trade_config.py','docs/execution.md','docs/validation.md','pyproject.toml'],
'agentic-forecasting':['aieng-forecasting/aieng/forecasting/data/cutoff.py','aieng-forecasting/aieng/forecasting/data/context.py','aieng-forecasting/aieng/forecasting/evaluation/prediction.py','aieng-forecasting/aieng/forecasting/evaluation/eval.py','aieng-forecasting/aieng/forecasting/evaluation/backtest.py','aieng-forecasting/aieng/forecasting/evaluation/task.py','aieng-forecasting/pyproject.toml']}
def fetch(item):
 n,p=item; d=json.loads((R/n/'metadata.json').read_text());u=f"https://raw.githubusercontent.com/{d['repository']}/{d['commit']}/{p}"
 try:
  b=urllib.request.urlopen(u,timeout=60).read();(R/n/p.replace('/','__')).write_bytes(b);return n,p,len(b)
 except Exception as e:return n,p,str(e)
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
 for x in ex.map(fetch,[(n,p) for n,ps in selection.items() for p in ps]):print(x)
