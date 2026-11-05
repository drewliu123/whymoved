"""Build a frozen, equal-information representation pilot. Standard library only."""
from pathlib import Path
import json, hashlib
ROOT=Path(__file__).resolve().parent
cases={
 'fed_gap': {
  'question':'上次2024年7月31日问过降息，此后没跟踪。现在是2024年11月8日，只根据给定材料：目前政策状态怎样？旧判断哪些应更新？下一步最值得查什么？能否判断预测合约错价？',
  'old':[
   {'id':'O1','text':'2024-07-31政策利率为5.25%–5.50%。','depends_on':[]},
   {'id':'O2','text':'2024-07-31 FOMC尚要求对通胀持续回归2%更有信心，才适宜降息。','depends_on':[]},
   {'id':'J1','text':'首次降息仍待发生；当前研究对象是2024年9月会议是否降息。','depends_on':['O1','O2']},
   {'id':'J2','text':'若通胀信心改善，开始降息的条件可能增强；不等于之后每次会议都会降息。','depends_on':['O2']},
   {'id':'P1','text':'下次检查：2024年9月会议声明，核实是否启动降息及其依据。','depends_on':['J1']},
   {'id':'J3','text':'仅凭政策判断不能认定合约错价，还需合约规则和同期可交易报价。','depends_on':[]}
  ],
  'new':[],
  'checks':{'current_range':'4.50–4.75','cumulative_cut_bp':75,'expired_target':'2024-09','required_claim_ids':['O1','O2','J1','J2','P1','J3']}
 },
 'revision_stress':{
  'question':'以下为完全虚构的澜国央行实验，不可套用真实历史。2028-01-10后一直没跟踪，现为2028-04-10。更新当前判断和后续研究；旧判断哪些应复核或保留？是否能认定合约错价？',
  'old':[
   {'id':'O1','text':'截至2028-01-10，政策利率4.00%。','depends_on':[]},
   {'id':'O2','text':'2028-01-10发布的12月就业初值为减少40千人。','depends_on':[]},
   {'id':'O3','text':'2028-01-10已知核心通胀同比2.4%。','depends_on':[]},
   {'id':'J1','text':'就业收缩与低通胀共同支持宽松压力上升。','depends_on':['O2','O3']},
   {'id':'J2','text':'如果就业收缩延续且通胀不反弹，6月降息情景更强；这是条件判断。','depends_on':['J1']},
   {'id':'J3','text':'观察6月前是否至少降息一次；这是事件B。事件A是恰在6月会议降息。A发生必然意味着B发生，假定同一政策利率、同一含6月截止口径。','depends_on':[]},
   {'id':'P1','text':'下一步先读2月就业报告，检验就业收缩是否持续。','depends_on':['J1','J2']},
   {'id':'J4','text':'资本充足率要求10%，与当前就业、通胀判断没有依赖关系。','depends_on':[]}
  ],
  'new':[
   {'id':'N1','published_at':'2028-02-10','text':'12月就业由减少40千人修订为增加80千人；1月就业增加60千人。修订不改变1月10日当时公布过什么。'},
   {'id':'N2','published_at':'2028-03-20','text':'政策利率维持4.00%；央行表示通胀重新上行，需要更多信心，不预先承诺6月决定。'},
   {'id':'N3','published_at':'2028-04-08','text':'最新核心通胀同比3.1%。2月就业初值减少10千人，3月就业增加5千人；就业信息并非一边倒强劲。'},
   {'id':'N4','published_at':'2028-04-09','text':'事件A最后成交0.62，成交于4月1日；事件B最后成交0.55，成交于4月9日。未提供同步bid/ask、深度、费用或完整结算文件。'},
   {'id':'N5','published_at':'2028-04-09','text':'资本充足率要求仍为10%。'},
   {'id':'N6','published_at':'2028-04-10','text':'4月就业将在5月10日发布；4月通胀将在5月12日发布；下一政策会议5月20日，之后会议6月20日。'}
  ],
  'checks':{'current_rate':4.0,'old_december_employment':-40,'revised_december_employment':80,'current_core_inflation':3.1,'required_claim_ids':['O1','O2','O3','J1','J2','J3','P1','J4']}
 }
}
for date in ['20240918','20241107']:
 text=(ROOT/f'source-{date}.txt').read_text().splitlines()
 excerpt='\n'.join(text[304:309])
 cases['fed_gap']['new'].append({'id':'N'+('1' if date=='20240918' else '2'),'published_at':date,'text':excerpt,'url':f'https://www.federalreserve.gov/newsevents/pressreleases/monetary{date}a.htm'})
cases['fed_gap']['new'].append({'id':'N3','published_at':'2024-11-08','text':'本实验没有提供合约全文、报价、流动性或12月会议结果。'})
contract='''你是投研助手的宿主Agent，执行一次久别更新。只允许使用这个输入文件，不联网、不读取项目其他文件或其他实验输出。不要调用技能；这是封闭证据实验。所有历史判断均可复核，不是当前真理。输出必须独立回答原问题，写中文，先形成有用的判断。\n保存JSON到指定output_path，字段：answer（不超过500汉字）；current_state（对象）；claim_updates（每项id/status/reason/evidence_ids，status取retain/revise/retire/review）；next_checks（最多3项，question/source_or_event/why）；pricing_conclusion；limitations。只对给定旧条目更新，不创建无来源事实。历史版本须保留；不要把证据修订直接等同依赖结论全错。各表示组允许相同的自主推理。'''
manifest={'design':'3 representations x 2 cases, one fresh subagent per cell; identical historical semantic information and new evidence; no live retrieval or runtime token telemetry. Authored state preparation costs not measured.','conditions':{},'cases':{}}
for cid,c in cases.items():
 (ROOT/f'{cid}-ground-truth.json').write_text(json.dumps(c['checks'],ensure_ascii=False,indent=2))
 for mode in ['history','summary','state']:
  old=c['old']
  if mode=='history':
   memory='历史研究工作记录（按原记录逐条保留）：\n'+'\n'.join(f"{x['id']}: {x['text']} 依据条目：{','.join(x['depends_on']) or '无其他依赖'}。" for x in old)
  elif mode=='summary':
   memory='历史研究文字摘要（所有条目与依赖保留）：\n'+' '.join(f"【{x['id']}】{x['text']}（依据：{','.join(x['depends_on']) or '独立条目'}）" for x in old)
  else:
   memory={'as_of':'2024-07-31' if cid=='fed_gap' else '2028-01-10','claims':old,'dependency_edges':[{'from':dep,'to':x['id']} for x in old for dep in x['depends_on']]}
  output=ROOT/f'{cid}-{mode}-output.json'
  packet={'instructions':contract,'question':c['question'],'historical_memory':memory,'new_evidence':c['new'],'output_path':str(output)}
  p=ROOT/f'{cid}-{mode}-input.json'; p.write_text(json.dumps(packet,ensure_ascii=False,indent=2))
  manifest['conditions'][f'{cid}/{mode}']={'input_file':p.name,'input_utf8_bytes':p.stat().st_size,'input_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'old_claim_count':len(old),'dependency_count':sum(len(x['depends_on']) for x in old),'new_evidence_count':len(c['new'])}
 manifest['cases'][cid]={'question':c['question'],'ground_truth_file':f'{cid}-ground-truth.json'}
(ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print('Built 6 frozen inputs; same historical claims and dependencies in every representation.')
