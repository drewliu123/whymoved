import json, pathlib, urllib.request, concurrent.futures, datetime
w=pathlib.Path(__file__).resolve().parent
def get(u):
 return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'research/0.5.0'}),timeout=25))
e=get('https://gamma-api.polymarket.com/events/slug/october-inflation-china-annual')
(w/'event.json').write_text(json.dumps(e,ensure_ascii=False,indent=2))
print('EVENT',json.dumps({k:e.get(k) for k in ['id','title','slug','description','volume','liquidity','endDate','negRisk']},ensure_ascii=False))
jobs=[]
for m in e.get('markets',[]):
 tokens=json.loads(m['clobTokenIds']) if isinstance(m.get('clobTokenIds'),str) else m.get('clobTokenIds',[])
 outcomes=json.loads(m['outcomes']) if isinstance(m.get('outcomes'),str) else m.get('outcomes',[])
 print('MARKET',json.dumps({k:m.get(k) for k in ['id','question','groupItemTitle','description','active','closed','bestBid','bestAsk','lastTradePrice','liquidity','feesEnabled','feeType','orderMinSize','orderPriceMinTickSize']},ensure_ascii=False))
 for o,t in zip(outcomes,tokens):jobs.append((m['id'],m.get('groupItemTitle'),o,t))
def book(j):
 mid,label,out,t=j
 try:
  b=get('https://clob.polymarket.com/book?token_id='+t)
  (w/('book-'+mid+'-'+out+'.json')).write_text(json.dumps(b,indent=2))
  bids=sorted(b.get('bids',[]),key=lambda x:float(x['price']),reverse=True)
  asks=sorted(b.get('asks',[]),key=lambda x:float(x['price']))
  try:fee=get('https://clob.polymarket.com/fee-rate?token_id='+t)
  except Exception as ex:fee={'error':str(ex)}
  return {'id':mid,'label':label,'outcome':out,'token':t,'timestamp':b.get('timestamp'),'bids':bids[:4],'asks':asks[:4],'fee':fee}
 except Exception as ex:return {'id':mid,'label':label,'outcome':out,'token':t,'error':str(ex)}
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:books=list(pool.map(book,jobs))
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
(w/'snapshot.json').write_text(json.dumps({'retrieved_at':now,'books':books},ensure_ascii=False,indent=2))
print('SNAPSHOT',now)
for b in books:print(json.dumps(b,ensure_ascii=False))
