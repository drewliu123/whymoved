import json,pathlib,sys,subprocess,os,hashlib,datetime
r=pathlib.Path(sys.argv[1]); plugin=pathlib.Path(sys.argv[2]); env=os.environ.copy();env['TOUYAN_HOME']=str(r)
cmd=[sys.executable,str(plugin/'scripts/journal.py'),'add',str(r/'memo.json'),'--claims',str(r/'claims.json'),'--report',str(r/'memo.md'),'--plan',str(r/'plan.json'),'--forecast',str(r/'forecast.json')]
x=subprocess.run(cmd,capture_output=True,text=True,env=env,cwd=str(r));(r/'logs/journal-add.stdout.log').write_text(x.stdout);(r/'logs/journal-add.stderr.log').write_text(x.stderr);print('journal add exit=',x.returncode);print(x.stdout);print(x.stderr)
if x.returncode:raise SystemExit(x.returncode)
rows=[json.loads(l) for l in (r/'journal/memos.jsonl').read_text().splitlines() if l]; mid=rows[-1]['memo_id']; archive=r/'journal'/mid
matches={name:(r/name).read_bytes()==(archive/name).read_bytes() for name in ['memo.json','claims.json','memo.md','plan.json','forecast.json']}
a=json.loads((r/'data/authors.json').read_text()); original=json.loads((plugin/'data/authors.json').read_text()); preserved=all(v.get('status')==a['authors'].get(k,{}).get('status') for k,v in original['authors'].items() if v.get('status')=='demoted')
execution=dict(plugin_version='0.2.0',plugin_root=str(plugin),TOUYAN_HOME=str(r),question_as_of='2026-10-31T12:19:06Z',completed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),mode='isolated complete trial; not official statistics',memo_id=mid,archive=str(archive),steps={
'1':'asset route; exact as_of and last completed-session price basis',
'2':'five fixed asset angles in plan.json',
'3':'T0 official IR/newsroom and Polymarket; T2 Reuters; T4 Reddit/HN; seed library copied and demoted retained',
'4':{'fact_agent':'touyan:fact-collector a869664bad5f20e40;5 web calls;unverified candidates,parent raw verification recorded','community_agent':'touyan:community-scout add7637e35200db27;actual last30days96.73sec exit0;partial sources','market':'main researcher ran search/event, Gamma raw and both YES/NO CLOB attempts;403 depth;after-cutoff updates excluded from forecast inputs'},
'5':{'initial_claims':10,'final_claims':12,'check_claims_exit_code':0,'log':'logs/check-claims-final.stdout.log'},
'6':{'agent':'touyan:red-team a6ca97bbd0808af8b','report':'red-team.json','integrated':'C8/C9/C10 narrowed; C11 cash conversion added; contract boundaries explicit'},
'6.5':{'mode':'independent','hypotheses':1,'input':'forecast-input-H1.json','input_claim_types':['fact'],'evidence_ids':['C3','C4','C5'],'fallback_agent':'general-purpose because touyan:forecaster unregistered','trials':[0.63,0.64,0.68],'final_prob':0.65,'finalize_exit_code':0,'check_exit_code':0,'independence':'same inherited model, separate isolated single-input calls; not statistically independent','no_price_scope':'No verified executable as_of depth in attempted Polymarket market; not assertion no global price'},
'7':{'journal_add_command':cmd,'journal_add_exit_code':x.returncode,'archive_byte_equality':matches}},
web_budget={'web_tool_calls':8,'breakdown':'fact5, community fallback2, main initialWebFetch1','additional_raw_nonprice_fetches':5,'raw_breakdown':'parent3:IR earnings403, Reuters200, newsroom200;community Reddit2:403','approx_search_fetch_total_excluding_price_and_market_operations':13,'note':'Approximately12 budget used as convergence target; no further searches. Official price widget and quote API, widget source, Gamma and CLOB market operations excluded.'},
failures_and_degradations=[
'Initial forecast.py --help with python -I failed ModuleNotFoundError common; scripts executed normally with trusted plugin script path thereafter; network JSON readers used python -I.',
'Official IR direct earnings and historical paths403; newsroom raw200; official historical data succeeded in isolated ego browser using observed quote service.',
'Initial WebFetch outputs from fact agent did not establish original URL body; candidates not accepted until parent raw verification.',
'Browser widget external fetch hit CORS; selected-date click blocked by privacy dialog; inspected dialog, rejected nonessential cookies, observed same-origin official API succeeded; TaskSpace11 finished keep[] exactly once.',
'last30days global config-link automatic approval rejected Sensitive-Source Provenance; no retry or alternate retrieval of denied secrets, used isolated config with keychain disabled; quick reduced actual query plan to Reddit/HN.',
'last30days exit0 with partial Reddit timeout;X unconfigured;public Reddit JSON403;engagement collected after as_of;author unverified;one view only.',
'Polymarket displayed probabilities are midpoints and nonmonotonic across thresholds;not execution;YES/NO depth403;Gamma updates after cutoff prevent contemporaneous reconstruction.',
'Full-month causal attribution, stock valuation/consensus/options/flows, October order/export events and exact next earnings date unverified.'
],
author_library={'file':'data/authors.json','demoted_preserved':preserved,'entire_seed_byte_equal':(r/'data/authors.json').read_bytes()==(plugin/'data/authors.json').read_bytes(),'new_authors':0,'reason':'No candidate met at least two theme-hit posts and >=half relevance condition'},
write_boundaries={'only_run_written':True,'no_plugin_edits':True,'no_Git_writes':True,'no_official_journal':True,'no_other_run_or_old_report_reads':True,'browser_space':'touyan-020-nvda-20261031-isolated id11 closed'},
sha256={name:hashlib.sha256((r/name).read_bytes()).hexdigest() for name in ['claims.json','forecast-input-H1.json','forecast.json','memo.md','memo.json','plan.json']})
(r/'execution.json').write_text(json.dumps(execution,ensure_ascii=False,indent=2))
print('archive_equal',matches,'demoted_preserved',preserved,'memo_chars',len((r/'memo.md').read_text()),'chinese_chars',sum('一'<=c<='鿿' for c in (r/'memo.md').read_text()))
print('memo_id',mid)
