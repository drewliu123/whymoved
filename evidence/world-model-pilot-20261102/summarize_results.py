from pathlib import Path
import json
root=Path(__file__).resolve().parent
key=json.loads((root/'blind-key.json').read_text())
review=json.loads((root/'review.json').read_text())
checks=json.loads((root/'artifact-checks.json').read_text())
rows=[]
for r in review['reviews']:
 case,mode=key[r['id']].split('/')
 assert r['score']==sum(x['score'] for x in r['checks'])
 assert r['max_score']==len(r['checks'])
 size=next(x for x in checks['sizes'] if x['id']==r['id'])
 rows.append({'case':case,'condition':mode,'score':r['score'],'max_score':r['max_score'],'hard_failures':r['hard_failures'],'additional_findings':r['additional_findings'],'input_utf8_bytes':size['input_utf8_bytes'],'output_utf8_bytes':size['output_utf8_bytes']})
totals=[]
for mode in ['history','summary','state']:
 sub=[x for x in rows if x['condition']==mode]
 totals.append({'condition':mode,'score':sum(x['score'] for x in sub),'max_score':sum(x['max_score'] for x in sub),'input_utf8_bytes':sum(x['input_utf8_bytes'] for x in sub),'output_utf8_bytes':sum(x['output_utf8_bytes'] for x in sub)})
result={'rows':rows,'totals':totals,'conclusion':'No incremental correctness observed for explicit dependency state over equal-information full history or summary in these two closed-evidence cases. All prespecified checks pass. This is a representation pilot, not a full agentic research benchmark.'}
(root/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(totals,ensure_ascii=False,indent=2))
