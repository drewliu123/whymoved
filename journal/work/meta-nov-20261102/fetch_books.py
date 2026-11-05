import json, urllib.request, concurrent.futures, datetime
from pathlib import Path
w=Path('/Users/frankzhang/Desktop/投研助手/journal/work/meta-nov-20261102')
e=json.loads((w/'evidence/gamma-event.json').read_text())[0]
markets=e['markets']
def fetch(m):
    result={'id':m['id'],'label':m['groupItemTitle'],'slug':m['slug'],'feeSchedule':m.get('feeSchedule'),'tokens':[]}
    for outcome, token in zip(json.loads(m['outcomes']),json.loads(m['clobTokenIds'])):
        item={'outcome':outcome,'token_id':token}
        for key,path in [('book','book'),('fee','fee-rate')]:
            url='https://clob.polymarket.com/'+path+'?token_id='+token
            try:
                req=urllib.request.Request(url,headers={'User-Agent':'Research/1.0'})
                with urllib.request.urlopen(req,timeout=20) as r: item[key]=json.load(r)
                item[key+'_retrieved_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
            except Exception as exc: item[key+'_error']=str(exc)
        result['tokens'].append(item)
    return result
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool: results=list(pool.map(fetch,markets))
(w/'evidence/clob-books.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
for m in results:
    line=[m['label']]
    for t in m['tokens']:
        b=t.get('book',{})
        bids=sorted(b.get('bids',[]),key=lambda x:float(x['price']),reverse=True)
        asks=sorted(b.get('asks',[]),key=lambda x:float(x['price']))
        line.append({'outcome':t['outcome'],'bid':bids[:1],'ask':asks[:3],'timestamp':b.get('timestamp'),'fee':t.get('fee'),'error':t.get('book_error')})
    print(json.dumps(line,ensure_ascii=False))
