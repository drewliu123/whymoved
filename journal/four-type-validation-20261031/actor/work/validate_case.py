from pathlib import Path
import subprocess, sys, json, re, hashlib, html
from datetime import datetime,timezone
R=Path('/Users/frankzhang/Desktop/投研助手/journal/four-type-validation-20261031/actor')
SCRIPTS=Path('/Users/frankzhang/Desktop/投研助手/scripts')
cmd=[sys.executable,'-I','-c',"import sys, runpy; sys.path.insert(0, '/Users/frankzhang/Desktop/投研助手/scripts'); sys.argv=['/Users/frankzhang/Desktop/投研助手/scripts/check_claims.py', '/Users/frankzhang/Desktop/投研助手/journal/four-type-validation-20261031/actor/claims.json', '--json']; runpy.run_path(sys.argv[0], run_name='__main__')"]
run=subprocess.run(cmd,cwd=str(R/'work'),capture_output=True,text=True)
(R/'logs/check_claims.stdout.log').write_text(run.stdout)
(R/'logs/check_claims.stderr.log').write_text(run.stderr)
(R/'logs/check_claims.exit_code.txt').write_text(str(run.returncode)+'\n')
(R/'logs/check_claims.command.json').write_text(json.dumps({'argv':cmd,'cwd':str(R/'work'),'exit_code':run.returncode,'executed_at':datetime.now(timezone.utc).isoformat(),'note':'Runs existing unmodified checker via runpy; -I excludes cwd/import environment. Only explicitly trusted local scripts directory added for common.py dependency.'},ensure_ascii=False,indent=2)+'\n')
def load(name):return json.loads((R/name).read_text())
report=load('report.json'); claims=load('claims.json'); sources=load('sources.json'); calcs=load('calculations.json')
ids={c['id'] for c in claims['claims']}
issues=[]
for f in report['findings']+report['alternatives']+report['watch']:
    for cid in f['claim_ids']:
        if cid not in ids:issues.append('unknown '+cid)
for t in report['tables']:
    for row in t['rows']:
        for cid in re.findall(r'\bC\d+\b',' '.join(map(str,row))):
            if cid not in ids:issues.append('unknown table '+cid)
for src in sources['sources']:
    lines=(R/src['local_text']).read_text().splitlines()
    for q in src['quotes']:
        line=int(q['locator'].split(':')[-1])
        if lines[line-1]!=q['quote']:issues.append('quote mismatch '+q['id'])
        if src['published_at']>'2026-10-31':issues.append('future source '+src['id'])
    # Preserve actual speaker from nearest transcript label before quoted passage.
    for q in src['quotes']:
        n=int(q['locator'].split(':')[-1]); speaker='unknown'
        for line in reversed(lines[:n]):
            if re.match(r'^(AMY HOOD|SATYA NADELLA|JONATHAN NEILSON):',line):
                speaker=line.split(':',1)[0];break
        q['speaker']=speaker
(R/'sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2)+'\n')
expected={'K1':145.3,'K3':{'difference':20.0,'growth_pct':103.1},'K4':29.5,'K6':{'reported_Jan_Sep':118.1,'implied_Oct_Dec':51.9},'K7':18.6}
for k,val in expected.items():
    actual=next(c['result'] for c in calcs['calculations'] if c['id']==k)
    if actual!=val: issues.append(f'calculation mismatch {k}: {actual}')
text=(R/'report.md').read_text(); page=html.unescape((R/'report.html').read_text())
for f in report['findings']+report['alternatives']:
    if f['text'] not in text:issues.append('Markdown missing canonical paragraph')
    if f['text'] not in page:issues.append('HTML missing canonical paragraph')
for g in report['gaps']:
    if g not in text or g not in page:issues.append('gap presentation mismatch')
checks={'claim_references':not any('unknown' in i for i in issues),'quote_equality':not any('quote mismatch' in i for i in issues),'no_future_sources':not any('future' in i for i in issues),'calculation_recomputed':not any('calculation' in i for i in issues),'canonical_paragraphs_in_both_presentations':not any('missing canonical' in i or 'presentation mismatch' in i for i in issues),'issues':issues}
(R/'logs/local_review.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
validation={'as_of':report['as_of'],'completed_at':datetime.now(timezone.utc).isoformat(),'overall':'部分满足','claim_checker':{'script':str(SCRIPTS/'check_claims.py'),'exit_code':run.returncode,'result':json.loads(run.stdout) if run.returncode in (0,1) else None,'stdout':'logs/check_claims.stdout.log','stderr':'logs/check_claims.stderr.log','command':'logs/check_claims.command.json','scope':'R1-R8 structure/source-tier/time rules only; does not validate factual truth, accounting quality or causal ROI'},'protocol_checks':[{'id':'A','result':'已满足','evidence':'report first answer distinguishes investment / capacity / monetization / ROI; latest miss is prominent'},{'id':'B','result':'已满足' if run.returncode==0 and not issues else '未满足','evidence':'27 ledger claims; 6 official sources; 86 exact paragraphs verified against archived text; checker logs','limitation':'Issuer disclosures not independently audited in this case; quant outcomes and management assertions separated.'},{'id':'C','result':'已满足','evidence':'calculations.json K1-K7; Decimal arithmetic; no ROI fabricated','limitation':'Rounded quarter sums not precise annual filing figures; full-year growth-rate comparison omitted for lack of baseline.'},{'id':'D','result':'部分满足','evidence':'conditional statements, execution and timing, usable capacity boundary, allocation, funding and supplier limits addressed','limitation':'Board authorization thresholds and pay incentives not sourced; no psychological motive inferred.'},{'id':'E','result':'已满足','evidence':'3 sourced alternatives and 4 next checks with downgrade conditions'},{'id':'F','result':'部分满足','evidence':'Markdown/HTML generated from report.json; same main paragraphs, tables and sources checked','limitation':'No visual/browser rendering verification of local HTML, no image export; coordinator-relayed independent review corrections recorded, not a full independent audit; this is human-coordinated content validation, not full automated delivery acceptance.'}],'local_checks':checks,'accounting_review':['Cash PPE distinct from finance-lease-inclusive capex; no mechanical addition identity','CY2026 guidance distinct from FY26/FY27; FY27 H2 explicitly Jan-Jun 2027','190→175 guidance change classified separately from 175→170 delivery revision','FY27 Q1 >50 guidance versus 45.2 actual preserved','No published growth equated with AI investment ROI','Building-life change does not extend GPU depreciation assumption','Announcement of 2GW Wisconsin excluded from completed capacity; different capacity measures not summed','New segment reporting warning prevents invalid segment margin comparison'],'independent_review_followup':{'status':'six coordinator-relayed corrections addressed','record':'independent-review.md','new_retrieval':False},'self_challenge':{'independent':False,'reason':'User explicitly requested direct execution without delegation. Self-review is not represented as independent review.','principal_challenge':'Commercial success can reflect old-capacity optimization and pricing; unresolved incrementality of AI capital returns retained in answer.'},'write_boundary':str(R),'external_writes':False,'formal_journal_registration':False,'credential_access':False,'downloaded_code_execution':False,'source_failures_recorded':True}
(R/'validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'check_claims_exit_code':run.returncode,'checker':run.stdout.strip(),'local_checks':checks,'protocol_status':validation['overall']},ensure_ascii=False,indent=2))
sys.exit(0 if run.returncode==0 and not issues else 1)
