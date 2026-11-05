"""Verify captured live adapter outputs, then exercise the existing evidence contract."""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from sources import validate_sources
from check_claims import validate_ledger

folder = Path(__file__).resolve().parent
document = json.loads((folder/'1-document.json').read_text())
statements = json.loads((folder/'2-statements.json').read_text())
filings = json.loads((folder/'3-filings.json').read_text())
assert document['status'] == statements['status'] == filings['status'] == 'ok'
text = document['data']['text']
assert len(text) == 37895 and text.rstrip().endswith('There has been no adoption of any new and recently issued accounting pronouncements.')
assert hashlib.sha256(text.encode()).hexdigest() == 'cd14ab0a1188e10d6173830e3f6b49038ed0f10ac0883f74567d02b28a6fa9f2'
assert document['provenance']['accession_number'] == '0001045810-26-000075'
assert document['provenance']['acceptance_datetime'] == '2026-08-26T20:36:00Z'
assert document['completeness']['truncated'] is False
income = statements['data']['statements']['income']['rows']
revenue = next(r for r in income if r['concept'] == 'us-gaap_Revenues' and r['dimension'] is False)
assert revenue['2026-07-26 (Q2)'] == 96221000000
assert revenue['2026-07-26 (YTD)'] == 177837000000
cf = statements['data']['statements']['cashflow']
assert all('(YTD)' in c for c in cf['columns'] if c.startswith('2026-'))
cfo = next(r for r in cf['rows'] if r['concept'] == 'us-gaap_NetCashProvidedByUsedInOperatingActivities' and r['dimension'] is False)
assert cfo['2026-07-26 (YTD)'] == 74421000000
assert statements['data']['numeric_facts'] and statements['data']['units']
json.dumps(statements, allow_nan=False)
# Curated example, not an automatic fact-promotion rule. Quote exact returned text.
start = text.index('Three Months Ended', text.index('Second Quarter of Fiscal Year'))
end = text.index('\nGross margin', start)
quote = text[start:end]
assert '($ in millions, except per share data)' in quote and '$96,221' in quote
cutoff = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
source = {'id':'S1','url':document['data']['source_url'],'canonical_url':document['data']['source_url'],
          'publisher':'NVIDIA / SEC EDGAR','tier':'T0','published_at':document['provenance']['acceptance_datetime'],
          'retrieved_at':document['retrieved_at'],'quote':quote,
          'locator':'10-Q Part I, Item 2; Second Quarter of Fiscal Year 2027 Summary; Revenue; Jul 26, 2026; USD millions',
          'origin_id':document['provenance']['origin_id'],'origin_basis':'Original NVIDIA SEC filing, exact accession 0001045810-26-000075',
          'supports':['fact'],'evidence_kind':'document','access_status':'ok',
          'selection':{'selected':True,'reason':'Direct revenue row and period/unit headers from the specified filing.',
                       'relevance':'direct','purpose':'Validate SEC financial evidence ingestion','priority':'decisive'}}
sources={'schema_version':2,'as_of':cutoff,'historical':False,'source_status':{'sec':{'status':'ok'}},'candidates':[source]}
claims={'schema_version':2,'as_of':cutoff,'claims':[{'id':'C1','text':'英伟达披露，截至2026-07-26的季度收入为96,221百万美元。',
        'type':'fact','as_of':cutoff,'sources':[{'source_id':'S1'}]}]}
(folder/'sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf-8')
(folder/'claims.json').write_text(json.dumps(claims,ensure_ascii=False,indent=2),encoding='utf-8')
errors=validate_sources(sources)
assert not errors, errors
# CLI validates the ledger separately; keep this script independent of its evolving return signature.
print(json.dumps({'assertions':'passed','full_mda_characters':len(text),'quarter_revenue':revenue['2026-07-26 (Q2)'],
                  'ytd_operating_cashflow':cfo['2026-07-26 (YTD)'],'accepted_at':document['provenance']['acceptance_datetime'],
                  'numeric_fact_count':len(statements['data']['numeric_facts']),'source_contract':'passed'},ensure_ascii=False))
