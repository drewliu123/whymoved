import concurrent.futures, json, time, urllib.request, urllib.parse, html
from pathlib import Path
from datetime import datetime, timezone
from html.parser import HTMLParser
ROOT=Path('/Users/frankzhang/Desktop/投研助手/evidence/rebuild-20261031/live')
class Text(HTMLParser):
    def __init__(self): super().__init__(); self.skip=0; self.out=[]
    def handle_starttag(self,t,a):
        if t in ('script','style'): self.skip+=1
        if t in ('p','div','tr','h1','h2','h3','li','br','section'): self.out.append('\n')
        if t in ('td','th'): self.out.append(' | ')
    def handle_endtag(self,t):
        if t in ('script','style'): self.skip=max(0,self.skip-1)
        if t in ('p','div','tr','h1','h2','h3','li','section'): self.out.append('\n')
    def handle_data(self,d):
        if not self.skip: self.out.append(d)

def fetch(task):
    name,url=task
    folder=ROOT/'raw'/'fetched'/name
    folder.mkdir(parents=True,exist_ok=False)
    start=time.monotonic(); row={'name':name,'url':url,'retrieved_at':datetime.now(timezone.utc).isoformat(),'method':'unauthenticated urllib GET; no cookies'}
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; ResearchEvidence/1.0)'})
        with urllib.request.urlopen(req,timeout=45) as response:
            data=response.read(); row.update(status=response.status,final_url=response.url,content_type=response.headers.get('Content-Type'))
        (folder/'response.bin').write_bytes(data)
        content=data.decode('utf-8',errors='replace')
        if 'json' in (row.get('content_type') or '') or url.startswith('https://hn.algolia.com'):
            (folder/'body.json').write_text(json.dumps(json.loads(content),ensure_ascii=False,indent=2)+'\n')
        else:
            parser=Text(); parser.feed(content)
            lines=[' '.join(line.split()) for line in ''.join(parser.out).splitlines()]
            (folder/'body.txt').write_text('\n'.join(line for line in lines if line)+'\n')
    except Exception as e: row.update(status='failed',error=str(e))
    row['elapsed_seconds']=round(time.monotonic()-start,3)
    (folder/'fetch.json').write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n')
    return row

if __name__=='__main__':
    tasks=[
        ('official-call','https://www.microsoft.com/en-us/investor/events/fy-2025/earnings-fy-2025-q4'),
        ('official-release','https://www.microsoft.com/en-us/Investor/earnings/FY-2025-Q4/press-release-webcast'),
        ('official-annual','https://www.microsoft.com/investor/reports/ar25/'),
        ('geekwire','https://www.geekwire.com/2025/microsoft-plans-record-30b-in-quarterly-capital-spending-to-meet-surging-ai-demand/'),
        ('techradar','https://www.techradar.com/pro/microsoft-says-it-will-spend-billions-this-years-as-ai-moves-pay-off'),
        ('hn-leases-search','https://hn.algolia.com/api/v1/search?'+urllib.parse.urlencode({'query':'finance leases','tags':'comment','hitsPerPage':30})),
        ('hn-capex-search','https://hn.algolia.com/api/v1/search?'+urllib.parse.urlencode({'query':'Microsoft capex','tags':'story','hitsPerPage':30})),
    ]
    with concurrent.futures.ThreadPoolExecutor(max_workers=7) as pool:
        rows=list(pool.map(fetch,tasks))
    (ROOT/'logs'/'fetch-batch.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(rows,ensure_ascii=False,indent=2))
