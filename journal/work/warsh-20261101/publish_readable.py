# -*- coding: utf-8 -*-
"""Present the validated frozen research without audit fields in its main text."""
import json,html
from pathlib import Path
W=Path('/Users/frankzhang/Desktop/投研助手/journal/work/warsh-20261101')
r=json.loads((W/'report.json').read_text()); c=json.loads((W/'claims.json').read_text()); s=json.loads((W/'sources.json').read_text())
cm={x['id']:x for x in c['claims']};sm={x['id']:x for x in s['candidates']}
used=[]
for x in c['claims']:
 for ref in x['sources']:
  src=sm[ref['source_id']]
  if src['url'] not in used: used.append(src['url'])
md=['# '+r['title'],'','截至2026年11月1日（美国东部时间）；研究范围：政策框架、行动与市场传导。','',r['answer']['text'],''];h=['<h1>'+html.escape(r['title'])+'</h1>','<p class="meta">截至2026年11月1日（美国东部时间） · 政策框架与行动研究</p>','<p class="lead">'+html.escape(r['answer']['text'])+'</p>']
def refs(ids):
 urls=[]
 def walk(cid):
  for x in cm[cid].get('sources',[]):
   u=sm[x['source_id']]['url']
   if u not in urls: urls.append(u)
  for b in cm[cid].get('basis',[]): walk(b)
 for cid in ids: walk(cid)
 # Keep compact readable citations for main text; complete claim mapping in appendix.
 return urls[:4]
def section(title,text,ids):
 urls=refs(ids);ml=' '.join('[来源'+str(used.index(u)+1)+']('+u+')' for u in urls);hl=' '.join('<a href="'+html.escape(u,quote=True)+'">['+str(used.index(u)+1)+']</a>' for u in urls)
 md.extend(['## '+title,'',text+' '+ml,'']);h.extend(['<h2>'+html.escape(title)+'</h2>','<p>'+html.escape(text)+' <span class="refs">'+hl+'</span></p>'])
for i,f in enumerate(r['findings']):
 section(f['title'],f['text'],f['claim_ids'])
 if i==1:
  tb=r['tables'][0];md.extend(['| '+' | '.join(tb['columns'])+' |','| '+' | '.join(['---']*len(tb['columns']))+' |']+['| '+' | '.join(map(str,row))+' |' for row in tb['rows']]+[''])
  h.append('<div class="table-wrap"><table><thead><tr>'+''.join('<th>'+html.escape(v)+'</th>' for v in tb['columns'])+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in row)+'</tr>' for row in tb['rows'])+'</tbody></table></div>')
section('接下来最值得跟踪的两项观察',' '.join(x['signal']+'。'+x['meaning'] for x in r['watch']),['C10','C11','C19','C20'])
md.extend(['---','','## 证据附录','','记者会引文来自官方标注PRELIMINARY的版本。完整原始文件、检索候选与运行日志随研究归档保存。','']);h.append('<details><summary>证据附录：来源、原文定位、推断与检验</summary><p>记者会引文来自官方PRELIMINARY版本。原始材料和日志随研究归档保存。</p>')
for n,u in enumerate(used,1):
 src=next(x for x in s['candidates'] if x['url']==u)
 md.extend([str(n)+'. ['+src['publisher']+']('+u+')','']);h.append('<p>'+str(n)+'. <a href="'+html.escape(u,quote=True)+'">'+html.escape(src['publisher'])+'</a></p>')
appendix={'analysis':r['analysis'],'claims':c['claims'],'selected_source_fragments':[x for x in s['candidates'] if x['selection']['selected']],'source_status':s['source_status'],'research_increments':[{'title':x['title'],'increment':x['increment']} for x in r['findings']]}
txt=json.dumps(appendix,ensure_ascii=False,indent=2);md.extend(['### 完整证据与检验记录','','```json',txt,'```','']);h.append('<pre>'+html.escape(txt)+'</pre></details>')
css='body{font-family:-apple-system,BlinkMacSystemFont,"Noto Sans SC",sans-serif;color:#222;background:#faf9f6;margin:0;line-height:1.85}main{max-width:850px;margin:0 auto;padding:48px 26px 80px}h1{font-size:30px;line-height:1.45;margin:0 0 18px}h2{font-size:21px;margin:35px 0 12px}.meta{color:#666;font-size:14px}.lead{font-size:18px;border-left:3px solid #43635c;padding-left:18px}a{color:#345c54;text-underline-offset:3px}.refs{font-size:13px}table{border-collapse:collapse;width:100%;font-size:15px}th,td{padding:9px 12px;text-align:left;border-bottom:1px solid #dcdad4}.table-wrap{overflow:auto}details{margin-top:45px;border-top:1px solid #dcdad4;padding-top:20px}summary{cursor:pointer;font-weight:600}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px;line-height:1.6;background:#efeee9;padding:18px}@media(max-width:600px){main{padding:28px 18px}h1{font-size:25px}.lead{font-size:17px}}'
(W/'output'/'warsh-research.md').write_text('\n'.join(md))
(W/'output'/'warsh-research.html').write_text('<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(r['title'])+'</title><style>'+css+'</style></head><body><main>'+''.join(h)+'</main></body></html>')
print('Readable Markdown and HTML generated from frozen report, claims and sources.')
