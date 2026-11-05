"""Read the exact filing behind the MCP result, retaining full MD&A."""
import hashlib
import json
import os
import sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(root/'research/edgartools-eval-venv/lib/python3.12/site-packages'))
os.environ.setdefault('EDGAR_LOCAL_DATA_DIR',str(root/'research/edgartools-study/data'))
os.environ.setdefault('EDGAR_CACHE_DIR',str(root/'research/edgartools-study/cache'))
from edgar import find, set_identity
set_identity(os.environ['EDGAR_IDENTITY'])
filing=find('0001045810-26-000075')
report=filing.obj()
out=Path(sys.argv[1])
mda=report['Part I, Item 2']
text=str(mda) if mda is not None else ''
(out/'mda-full.txt').write_text(text,encoding='utf-8')
result={'accession':filing.accession_no,'sec_url':filing.url,'filed':str(filing.filing_date),
        'mda_full_characters':len(text),'mda_sha256':hashlib.sha256(text.encode()).hexdigest()}
for name in ['income_statement','cash_flow_statement']:
 try:
  stmt=getattr(report,name)
  df=stmt.to_dataframe()
  (out/(name+'-filing.csv')).write_text(df.to_csv(index=False),encoding='utf-8')
  result[name]={'columns':list(df.columns),'preview':df.head(15).to_dict(orient='records')}
 except Exception as exc: result[name]={'error':str(exc)}
(out/'filing-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,default=str)[:17000])
