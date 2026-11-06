from pathlib import Path
from decimal import Decimal
import re,json,hashlib
ROOT=Path(__file__).resolve().parent
rows=json.loads((ROOT/'evidence/official-tables.json').read_text())
by_id={x['index']:x['text'] for x in rows}

def pair(table,label):
 line=next(x for x in table.splitlines() if x.startswith(label+'\t'))
 parts=[x.strip() for x in line.split('\t')[1:] if x.strip()]
 vals=[]
 for x in parts:
  if re.fullmatch(r'\(?[\d,]+\)?',x):
   vals.append(-int(x[1:-1].replace(',','')) if x.startswith('(') else int(x.replace(',','')))
 assert len(vals)>=2,(label,parts)
 return {'FY2025':vals[0],'FY2024':vals[1],'verbatim_row':line}

revenue=pair(by_id[15],'Total revenue')
cfo=pair(by_id[18],'Net cash from operations')
capex_raw=pair(by_id[18],'Additions to property and equipment')
cfi=pair(by_id[18],'Net cash used in investing')
acq=pair(by_id[18],'Acquisition of companies, net of cash acquired and divestitures, and purchases of intangible and other assets')
capex={y:-capex_raw[y] for y in ['FY2024','FY2025']}
fcf={y:cfo[y]-capex[y] for y in capex}
dcfo=cfo['FY2025']-cfo['FY2024'];dcapex=capex['FY2025']-capex['FY2024'];delta=fcf['FY2025']-fcf['FY2024']
assert delta==dcfo-dcapex
assert fcf=={'FY2024':74071,'FY2025':71611}
percent=lambda a,b:str((Decimal(b)/Decimal(a)-1)*100)
out={'source':json.loads((ROOT/'evidence/download.json').read_text()),'unit':'USD million','definition':'FCF = net cash from operations - cash additions to property and equipment; cash capex = positive outflow magnitude','rows':{'revenue':revenue,'cfo':cfo,'cash_capex_original_signed_row':capex_raw,'net_cash_used_in_investing':cfi,'acquisition_and_other_assets_outflow':acq},'cash_capex':capex,'free_cash_flow':fcf,'delta_cfo':dcfo,'delta_cash_capex':dcapex,'delta_fcf':delta,'revenue_growth_percent':percent(revenue['FY2024'],revenue['FY2025']),'fcf_growth_percent':percent(fcf['FY2024'],fcf['FY2025']),'cash_conversion_percent':{y:str(Decimal(cfo[y])/Decimal(revenue[y])*100) for y in capex},'assertion':'deltaFCF = deltaCFO - deltaCashCapex; verified by Python integer arithmetic','tool_boundary':'This independent arithmetic check is separate from the project calculation-record schema checker; the project fixed FCFF model is not used.'}
(ROOT/'evidence/calculation-proof.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['unit','free_cash_flow','delta_cfo','delta_cash_capex','delta_fcf','revenue_growth_percent','fcf_growth_percent']},ensure_ascii=False,indent=2))
