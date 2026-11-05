"""Exercise installed Last30Days free Reddit parser, not its paid fallbacks."""
import datetime as dt
import json
import pathlib
import sys
import time
import urllib.error
import urllib.request

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,'/Users/frankzhang/.claude/plugins/cache/last30days-skill/last30days/3.30.0/skills/last30days/scripts')
from lib import reddit_search, http
endpoint=reddit_search.search_url('NVIDIA',time_filter='month')
record={'scope':'Single public search page using installed Last30Days URL builder and parser; not full research engine. No config, cookies, credentials or paid fallback.','url':endpoint,'tested_at_utc':dt.datetime.now(dt.timezone.utc).isoformat()}
began=time.monotonic()
try:
    req=urllib.request.Request(endpoint,headers={'User-Agent':http.BROWSER_USER_AGENT,'Accept':'text/html'})
    with urllib.request.urlopen(req,timeout=30) as response:
        body=response.read(5_000_000)
        record['http_status']=response.status
    (ROOT/'public-raw'/'reddit_nvda.response').write_bytes(body)
    text=body.decode('utf-8',errors='replace')
    problem=reddit_search.unrecognized_body(text)
    if problem:
        record.update(result='unrecognized-or-blocked',error=problem)
    else:
        rows,cursor=reddit_search.parse_page(text,query='NVIDIA')
        (ROOT/'reddit-items.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
        record.update(result='data-returned' if rows else 'no-results',returned_count=len(rows),has_next_page=bool(cursor),samples=rows[:3])
except urllib.error.HTTPError as exc:
    record.update(result='http-error',http_status=exc.code,error=str(exc))
except Exception as exc:
    record.update(result='error',error=f'{type(exc).__name__}: {exc}')
record['elapsed_seconds']=round(time.monotonic()-began,3)
(ROOT/'reddit-result.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
print(json.dumps(record,ensure_ascii=False,indent=2))
