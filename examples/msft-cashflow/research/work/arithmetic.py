#!/usr/bin/env python3
"""Independent Decimal arithmetic from read official table rows, NOT project formula validation."""
import json, re, hashlib
from pathlib import Path
from decimal import Decimal, getcontext
getcontext().prec=36
W=Path(__file__).resolve().parent
E=W.parent/'evidence'
tables=json.loads((E/'official-tables.json').read_text())
by_index={x['index']:x['text'] for x in tables}
def row(idx,label):
    text=by_index[idx]
    assert 'Year Ended June 30,' in text and '2025' in text and '2024' in text
    match=re.search(r'^'+re.escape(label)+r'\t([^\n]+)',text,re.M)
    assert match, label
    vals=re.findall(r'\(?[\d,]+\)?',match.group(1))
    values=[Decimal(v.replace(',','').strip('()')) for v in vals[:2]]
    return {'FY2024':values[1],'FY2025':values[0]}
inputs={'revenue':row(15,'Total revenue'),'cfo':row(18,'Net cash from operations'),'cash_capex_outflow':row(18,'Additions to property and equipment'),'cfi_net_outflow':row(18,'Net cash used in investing'),'acquisition_intangible_other_outflow':row(18,'Acquisition of companies, net of cash acquired and divestitures, and purchases of intangible and other assets')}
r,c,p,i,a=[inputs[k] for k in inputs]
fcf={y:c[y]-p[y] for y in c}
delta=lambda x:x['FY2025']-x['FY2024']
out={'fcf_FY2024':fcf['FY2024'],'fcf_FY2025':fcf['FY2025'],'delta_fcf':delta(fcf),'revenue_growth_pct':delta(r)/r['FY2024']*100,'fcf_growth_pct':delta(fcf)/fcf['FY2024']*100,'delta_cfo':delta(c),'delta_cash_capex':delta(p),'capex_increment_excess':delta(p)-delta(c),'delta_cfi_net_outflow':delta(i),'delta_acquisition_intangible_other_outflow':delta(a),'delta_other_investing_net_outflow':delta(i)-delta(p)-delta(a),'cfo_revenue_FY2024_pct':c['FY2024']/r['FY2024']*100,'cfo_revenue_FY2025_pct':c['FY2025']/r['FY2025']*100,'fcf_revenue_FY2024_pct':fcf['FY2024']/r['FY2024']*100,'fcf_revenue_FY2025_pct':fcf['FY2025']/r['FY2025']*100}
assert out['fcf_FY2024']==74071 and out['fcf_FY2025']==71611
assert out['delta_fcf']==-2460 and out['delta_cfo']==17614 and out['delta_cash_capex']==20074
assert delta(fcf)==delta(c)-delta(p)
assert delta(i)==delta(p)+delta(a)+out['delta_other_investing_net_outflow']
result={'status':'passed','method':'Independent Python Decimal arithmetic parsed from official-tables.json, assertions on accounting bridge; not a semantic evidence review or project fixed-model recomputation.','input_unit':'USD millions; outflows positive','period':'Years ended June 30; columns FY2025 then FY2024 in original','inputs':inputs,'outputs':out,'input_sha256':hashlib.sha256((E/'official-tables.json').read_bytes()).hexdigest()}
serialized=json.dumps(result,ensure_ascii=False,indent=2,default=str)+'\n'
(W/'arithmetic-output.json').write_text(serialized)
print(serialized,end='')
