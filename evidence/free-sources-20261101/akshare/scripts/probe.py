import sys, json, time, subprocess, concurrent.futures, platform, traceback
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
OUT = Path(__file__).resolve().parents[1]
SOURCES = {'stock_info_global_cls': {'symbol':'全部'}, 'stock_info_global_em': {}, 'stock_news_em': {'symbol':'600519'}}
def save(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=str), encoding='utf-8')
def worker(name):
    started=time.monotonic(); raw=[]
    result={'source':name,'arguments':SOURCES[name], 'started_at':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()}
    try:
        import requests, inspect, importlib.metadata
        original=requests.Session.send
        def capture(session, request, **kwargs):
            kwargs['timeout']=min(float(kwargs.get('timeout') or 40),40)
            t=time.monotonic()
            response=original(session,request,**kwargs)
            raw.append({'url':response.url,'http_status':response.status_code,'elapsed_seconds':round(time.monotonic()-t,3),'body':response.text})
            save(OUT/'raw'/f'{name}.json',raw)
            return response
        requests.Session.send=capture
        import akshare as ak
        import pandas as pd
        fn=getattr(ak,name)
        result.update(python_version=platform.python_version(),akshare_version=ak.__version__,pandas_version=pd.__version__,signature=str(inspect.signature(fn)))
        frame=fn(**SOURCES[name])
        records=json.loads(frame.to_json(orient='records',force_ascii=False,date_format='iso'))
        save(OUT/'raw'/f'{name}-data.json', records)
        result.update(row_count=len(frame),columns=list(frame.columns),http_statuses=[r['http_status'] for r in raw])
        title='新闻标题' if '新闻标题' in frame else '标题'
        link=next((x for x in ['新闻链接','链接'] if x in frame),None)
        content=next((x for x in ['新闻内容','内容','摘要'] if x in frame),None)
        result['samples']=[{'title':r.get(title),'url':r.get(link) if link else None} for r in records[:2]]
        result['link_status']='returned' if link else 'missing: API returns no URL column'
        result['content_field']=content
        values=frame[content].fillna('').astype(str) if content else []
        result['content_nonempty_rows']=int(sum(bool(x.strip()) for x in values))
        result['content_length_range']=[min(map(len,values)),max(map(len,values))] if len(values) else None
        result['body_assessment']='摘要字段，不证明全文' if content=='摘要' else '已返回内容文本字段；未独立抓取原文页面，不能确认完整全文'
        dates=frame['发布日期'].astype(str)+' '+frame['发布时间'].astype(str) if '发布日期' in frame else frame['发布时间'].astype(str)
        parsed=pd.to_datetime(dates,errors='coerce')
        now=pd.Timestamp.now(tz='Asia/Shanghai').tz_localize(None)
        valid=parsed.dropna()
        future=valid[valid>now+pd.Timedelta(minutes=5)]
        result.update(earliest_time=str(valid.min()) if len(valid) else None,latest_time=str(valid.max()) if len(valid) else None,time_parse_failures=int(parsed.isna().sum()),future_date_count=len(future),future_date_examples=[str(x) for x in future[:3]],time_check_reference=str(now),time_zone_assumption='Asia/Shanghai; future threshold +5 minutes')
        result['status']='pass' if len(frame)>0 and title in frame and len(valid)>0 and not len(future) else 'data_anomaly'
    except Exception as exc:
        result.update(status='error',error=f'{type(exc).__name__}: {exc}',traceback=traceback.format_exc())
    result['elapsed_seconds']=round(time.monotonic()-started,3)
    if not (OUT/'raw'/f'{name}.json').exists(): save(OUT/'raw'/f'{name}.json',raw)
    save(OUT/f'{name}-result.json',result)
    return 0 if result['status']=='pass' else 1

def run(name):
    cmd=[sys.executable,'-I',str(Path(__file__).resolve()),'--worker',name]
    t=time.monotonic()
    try:
        proc=subprocess.run(cmd,capture_output=True,text=True,timeout=45,cwd='/tmp')
        exit_code=proc.returncode
        log=proc.stdout+'\n'+proc.stderr
    except subprocess.TimeoutExpired as exc:
        exit_code=124
        log='45-second hard timeout\n'+str(exc)
    (OUT/f'{name}.log').write_text(log,encoding='utf-8')
    path=OUT/f'{name}-result.json'
    result=json.loads(path.read_text()) if path.exists() else {'source':name,'arguments':SOURCES[name],'status':'timeout' if exit_code==124 else 'error'}
    result.update(command=cmd,exit_code=exit_code,wall_seconds=round(time.monotonic()-t,3),log=str(OUT/f'{name}.log'))
    save(path,result)
    return result
if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='--worker':sys.exit(worker(sys.argv[2]))
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool: results=list(pool.map(run,SOURCES))
    report={'tested_at':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'official_documentation':'https://akshare.akfamily.xyz/data/stock/stock_research.html','scope':'三项各调用一次，免费公开请求；个股样例采用600519，未测试NVDA；无付费API、凭据访问或全局配置修改。','raw_description':'*-data.json 为 AKShare DataFrame 原始记录；raw/<source>.json 为 requests 捕获的上游原始响应（如有）。','results':results}
    save(OUT/'results.json',report)
    lines=['# AKShare 免费中文资讯实测','',f"测试时间：{report['tested_at']}",'',f"官方文档：{report['official_documentation']}",'','临时 venv 隔离依赖；每项仅调用一次，45 秒硬超时。个股新闻直接采用 600519，未测试 NVDA。','']
    for r in results:
        lines += [f"## {r['source']}",f"- 状态：{r['status']}；exit={r['exit_code']}；耗时={r['wall_seconds']} 秒",f"- Python={r.get('python_version','未取得')}；AKShare={r.get('akshare_version','未取得')}；pandas={r.get('pandas_version','未取得')}",f"- 实际命令：`{' '.join(r['command'])}`",f"- 参数：{r['arguments']}；函数签名：{r.get('signature','未取得')}",f"- 行数：{r.get('row_count','未取得')}；列：{r.get('columns','未取得')}",f"- 最早：{r.get('earliest_time','未取得')}；最新：{r.get('latest_time','未取得')}；未来日期异常：{r.get('future_date_count','未取得')}",f"- 内容：{r.get('body_assessment','未取得')}；字段：{r.get('content_field')}；非空行：{r.get('content_nonempty_rows')}；长度范围：{r.get('content_length_range')}"]
        for sample in r.get('samples',[]):lines.append(f"- 样例：{sample['title']} — {sample['url'] or '链接缺失（接口未返回）'}")
        if r.get('error'):lines.append(f"- 错误：{r['error']}")
        lines.append('')
    (OUT/'results.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
