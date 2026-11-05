"""Read-only live samples; stdlib only; no keys, cookies, or paid APIs."""
import concurrent.futures
import datetime as dt
import json
import pathlib
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / 'public-raw'
RAW.mkdir(parents=True, exist_ok=True)
NOW = dt.datetime.now(dt.timezone.utc)
START = NOW - dt.timedelta(days=30)

def url(base, params):
    return base + '?' + urllib.parse.urlencode(params)

CASES = [
    ('gdelt_nvda', url('https://api.gdeltproject.org/api/v2/doc/doc', {'query':'NVIDIA','mode':'artlist','format':'json','maxrecords':10,'sort':'datedesc','startdatetime':START.strftime('%Y%m%d%H%M%S'),'enddatetime':NOW.strftime('%Y%m%d%H%M%S')}), 'articles'),
    ('gdelt_fed', url('https://api.gdeltproject.org/api/v2/doc/doc', {'query':'"Federal Reserve" interest rates','mode':'artlist','format':'json','maxrecords':10,'sort':'datedesc','startdatetime':START.strftime('%Y%m%d%H%M%S'),'enddatetime':NOW.strftime('%Y%m%d%H%M%S')}), 'articles'),
    ('hn_nvda', url('https://hn.algolia.com/api/v1/search_by_date', {'query':'NVIDIA','tags':'story','numericFilters':f'created_at_i>{int(START.timestamp())},created_at_i<{int(NOW.timestamp())}','hitsPerPage':5}), 'hits'),
    ('hn_fed', url('https://hn.algolia.com/api/v1/search_by_date', {'query':'Federal Reserve','tags':'story','numericFilters':f'created_at_i>{int(START.timestamp())},created_at_i<{int(NOW.timestamp())}','hitsPerPage':5}), 'hits'),
]

def probe(case):
    name, endpoint, key = case
    record = {'case':name,'url':endpoint,'started_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'request_timeout_seconds':35}
    began = time.monotonic()
    try:
        request = urllib.request.Request(endpoint, headers={'User-Agent':'InvestmentResearchSourceValidation/1.0','Accept':'application/json'})
        with urllib.request.urlopen(request, timeout=35) as response:
            body = response.read(5_000_000)
            record.update(http_status=response.status, content_type=response.headers.get('Content-Type'))
        (RAW / (name + '.response')).write_bytes(body)
        parsed = json.loads(body)
        rows = parsed.get(key)
        if not isinstance(rows, list):
            raise ValueError(f'Missing expected list {key}')
        samples=[]
        for row in rows[:3]:
            sample = {k:row.get(k) for k in ('title','url','seendate','domain','language','sourcecountry','created_at','points','num_comments') if k in row}
            if name.startswith('hn_'):
                sample['discussion_url']='https://news.ycombinator.com/item?id='+str(row.get('objectID'))
            samples.append(sample)
        record.update(result='data-returned' if rows else 'no-results', returned_count=len(rows), total_matches=parsed.get('nbHits'), samples=samples, full_text_returned=False)
    except urllib.error.HTTPError as exc:
        record.update(result='http-error',http_status=exc.code,error=str(exc))
        (RAW/(name+'.response')).write_bytes(exc.read(100000))
    except Exception as exc:
        record.update(result='error',error=f'{type(exc).__name__}: {exc}')
    record['elapsed_seconds']=round(time.monotonic()-began,3)
    return record

# GDELT is paced serially to respect shared service limits; HN independent.
records=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    hn_jobs=[pool.submit(probe,c) for c in CASES[2:]]
    for case in CASES[:2]:
        if records:
            time.sleep(5)
        record=probe(case)
        records.append(record)
        print(json.dumps(record,ensure_ascii=False),flush=True)
        if record.get('http_status')==429:
            records.append({'case':CASES[1][0],'result':'skipped','reason':'GDELT rate limited; no further requests'}) if case==CASES[0] else None
            break
    for job in hn_jobs:
        record=job.result()
        records.append(record)
        print(json.dumps(record,ensure_ascii=False),flush=True)
report={'tested_at_utc':NOW.isoformat(),'lookback_start_utc':START.isoformat(),'python':sys.version,'results':records,'scope':'Direct public API samples, not full Last30Days research engine output. HTTP or parser success alone does not establish complete coverage.'}
(ROOT/'public-result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
