"""Validate artifacts and create anonymized outputs for semantic review."""
from pathlib import Path
import json, hashlib, random
root=Path(__file__).resolve().parent
manifest=json.loads((root/'manifest.json').read_text())
files=[]
for key,meta in manifest['conditions'].items():
 p=root/meta['input_file']
 assert hashlib.sha256(p.read_bytes()).hexdigest()==meta['input_sha256'],f'Input changed: {p}'
 case,mode=key.split('/')
 out=root/f'{case}-{mode}-output.json'
 data=json.loads(out.read_text())
 required={'answer','current_state','claim_updates','next_checks','pricing_conclusion','limitations'}
 assert required <= data.keys(),(out,'missing fields')
 expected=set(json.loads((root/f'{case}-ground-truth.json').read_text())['required_claim_ids'])
 got=[x['id'] for x in data['claim_updates']]
 assert len(got)==len(set(got)) and set(got)==expected,(out,'claim ID coverage',got,expected)
 assert all(x['status'] in ['retain','revise','retire','review'] for x in data['claim_updates'])
 assert len(data['next_checks'])<=3
 files.append((key,data,out.stat().st_size,meta['input_utf8_bytes']))
random.Random(98271).shuffle(files)
blind=[]; mapping={}; sizes=[]
for i,(key,data,nout,nin) in enumerate(files):
 ident=f'R{i+1}'
 case,mode=key.split('/')
 blind.append({'id':ident,'case':case,'output':data})
 mapping[ident]=key
 sizes.append({'id':ident,'case':case,'condition':mode,'input_utf8_bytes':nin,'output_utf8_bytes':nout})
(root/'blind-outputs.json').write_text(json.dumps(blind,ensure_ascii=False,indent=2))
(root/'blind-key.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2))
(root/'artifact-checks.json').write_text(json.dumps({'passed':True,'checks':['input SHA256 unchanged','JSON required fields','complete unique old claim IDs','allowed statuses','next check budget'],'sizes':sizes},ensure_ascii=False,indent=2))
print('6 artifacts valid; blind review packet and byte measurements saved.')
