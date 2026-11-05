from pathlib import Path
from html.parser import HTMLParser
from urllib.request import Request, urlopen
from datetime import datetime, timezone
import json, hashlib, concurrent.futures
ROOT=Path('/Users/frankzhang/Desktop/投研助手/journal/four-type-validation-20261031/actor')
DOCS=[('S1','2025','q4'),('S2','2026','q1'),('S3','2026','q2'),('S4','2026','q3'),('S5','2026','q4'),('S6','2027','q1')]
class Text(HTMLParser):
    def __init__(self): super().__init__(); self.parts=[]; self.skip=0
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style'): self.skip+=1
        if tag in ('p','div','br','li','h1','h2','h3','tr'): self.parts.append('\n')
    def handle_endtag(self,tag):
        if tag in ('script','style'): self.skip=max(0,self.skip-1)
        if tag in ('p','div','li','h1','h2','h3','tr'): self.parts.append('\n')
    def handle_data(self,data):
        if not self.skip: self.parts.append(data)
def fetch(doc):
    sid,fy,q=doc
    folder=ROOT/'source-material'/sid
    folder.mkdir(exist_ok=False)
    url=f'https://www.microsoft.com/en-us/investor/events/fy-{fy}/earnings-fy-{fy}-{q}'
    stamp=datetime.now(timezone.utc).isoformat()
    result={'id':sid,'url':url,'retrieved_at':stamp}
    try:
        with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=50) as resp:
            raw=resp.read(); result.update(http_status=resp.status,final_url=resp.url)
        (folder/'page.html').write_bytes(raw)
        parser=Text(); parser.feed(raw.decode('utf-8'))
        text='\n'.join(line.strip() for line in ''.join(parser.parts).splitlines() if line.strip())
        (folder/'page.txt').write_text(text,encoding='utf-8')
        result.update(status='retrieved',bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),text_path=str(folder/'page.txt'))
    except Exception as exc: result.update(status='failed',error=str(exc))
    (folder/'retrieval.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return result
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
    results=list(pool.map(fetch,DOCS))
(ROOT/'source-material'/'retrieval-index.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(results,ensure_ascii=False,indent=2))
