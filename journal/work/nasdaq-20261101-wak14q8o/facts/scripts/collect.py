import urllib.request, json, datetime, pathlib, re, concurrent.futures
from html.parser import HTMLParser
ROOT=pathlib.Path('/Users/frankzhang/Desktop/投研助手/journal/work/nasdaq-20261101-wak14q8o/facts')
URLS={
'amazon':'https://ir.aboutamazon.com/news-release/news-release-details/2026/Amazon-com-Announces-Third-Quarter-Results/default.aspx',
'alphabet':'https://www.sec.gov/Archives/edgar/data/1652044/000165204426000080/googexhibit991q32026.htm',
'intel':'https://www.intc.com/filings-reports/all-sec-filings/content/0000050863-26-000188/q326earningsrelease.htm',
'reuters-close':'https://www.investing.com/news/stock-market-news/nasdaq-futures-tumble-as-amazon-intel-results-deepen-ai-spending-woes-4986163',
'reuters-alphabet':'https://www.investing.com/news/stock-market-news/alphabets-heavy-cloud-spending-drives-biggerthanexpected-cash-burn-4980612'}
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00','Z')
class Parser(HTMLParser):
 def __init__(self): super().__init__();self.text=[];self.hide=0
 def handle_starttag(self,t,a):
  if t in ['script','style']:self.hide+=1
  if t in ['p','div','tr','h1','h2','li']:self.text.append('\n')
 def handle_endtag(self,t):
  if t in ['script','style']:self.hide=max(0,self.hide-1)
 def handle_data(self,d):
  if not self.hide:self.text.append(d+' ')
def fetch(pair):
 name,url=pair; folder=ROOT/'downloads'/name;folder.mkdir(parents=True,exist_ok=False)
 log={'url':url,'request_at':now(),'method':'GET','name':name}
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=25) as r: data=r.read();log.update(http_status=r.status,final_url=r.url)
  log['received_at']=now();(folder/'raw.html').write_bytes(data)
  p=Parser();p.feed(data.decode('utf-8','replace'));text='\n'.join(re.sub(r'\s+',' ',line).strip() for line in ''.join(p.text).splitlines() if line.strip());(folder/'text.txt').write_text(text)
  lines=[s for s in text.splitlines() if re.search(r'free cash|cash flow|201\.9|46\.0|42\.4|195|205|128\.2|LSEG|Pursche|burn|consensus|capital expenditure|2027|2\.67|3\.02|October 2',s,re.I)]
  print(name, '\n'.join(lines)[:14000])
 except Exception as e:log.update(received_at=now(),error=str(e));print(name,str(e))
 (folder/'request.json').write_text(json.dumps(log,indent=2));return log
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:logs=list(pool.map(fetch,URLS.items()))
(ROOT/'request-log.json').write_text(json.dumps(logs,indent=2))
