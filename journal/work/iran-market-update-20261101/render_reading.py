from pathlib import Path
import json,html
W=Path(__file__).parent
r=json.loads((W/'report.json').read_text());c=json.loads((W/'claims.json').read_text());s=json.loads((W/'sources.json').read_text())
md=['# '+r['title'],'','行情快照：2026年11月1日22:44（美国东部），即11月2日03:44 UTC。','',r['answer']['text'],'']
body=['<h1>'+html.escape(r['title'])+'</h1>','<p class="date">行情快照：2026年11月1日22:44（美国东部） · 11月2日03:44 UTC</p>','<p>'+html.escape(r['answer']['text'])+'</p>']
for t in r['tables']:
 md+=['## '+t['title'],'','| '+' | '.join(t['columns'])+' |','| '+' | '.join(['---']*len(t['columns']))+' |']
 body+=['<h2>'+html.escape(t['title'])+'</h2><div class="scroll"><table><thead><tr>'+''.join('<th>'+html.escape(str(x))+'</th>' for x in t['columns'])+'</tr></thead><tbody>']
 for row in t['rows']:
  md+=['| '+' | '.join(map(str,row))+' |'];body+=['<tr>'+''.join('<td>'+html.escape(str(x))+'</td>' for x in row)+'</tr>']
 body+=['</tbody></table></div><p class="note">'+html.escape(t['note'])+'</p>'];md+=['',t['note'],'']
sections=[(x['title'],[x['text']]) for x in r['findings']]+[(x['title'],[x['text']]) for x in r['alternatives']]+[('接下来观察什么',[x['signal']+'：'+x['meaning'] for x in r['watch']])]
for title,paras in sections:
 md+=['## '+title,''];body+=['<h2>'+html.escape(title)+'</h2>']
 for text in paras:md+=[text,''];body+=['<p>'+html.escape(text)+'</p>']
text=r['limitations'][0]['text'];md+=[text,''];body+=['<p class="note">'+html.escape(text)+'</p>']
md+=['## 证据附录','','以下保存归属、主张依据与检验状态。',''];body+=['<details><summary>证据附录：来源、主张与检验状态</summary>']
for x in c['claims']:
 refs=', '.join(z['source_id'] for z in x.get('sources',[])) or '依据 '+', '.join(x.get('basis',[]));text=x['id']+' ['+x['type']+'] '+x['text']+'（'+refs+'）';md+=[text,''];body+=['<p>'+html.escape(text)+'</p>']
for x in s['candidates']:
 if not x['selection']['selected']:continue
 text=x['id']+' · '+x['publisher']+' · '+str(x['published_at']);md+=['- ['+text+']('+x['url']+')','  > '+x['quote'],'  定位：'+x['locator'],''];body+=['<p><a href="'+html.escape(x['url'],quote=True)+'">'+html.escape(text)+'</a></p><blockquote>'+html.escape(x['quote'])+'</blockquote><p>'+html.escape(x['locator'])+'</p>']
analysis=json.dumps(r['analysis'],ensure_ascii=False,indent=2);md+=['### 完整分析底稿','','```json',analysis,'```',''];body+=['<h3>完整分析底稿</h3><pre>'+html.escape(analysis)+'</pre></details>']
style='body{font-family:system-ui,sans-serif;color:#202124;background:#fff;max-width:900px;margin:48px auto;padding:0 24px;line-height:1.85}h1{font-size:28px;line-height:1.4}h2{font-size:21px;margin-top:32px}.date,.note{color:#666;font-size:14px}a{color:#245a94}blockquote{border-left:3px solid #ddd;margin-left:0;padding-left:16px;color:#555;overflow-wrap:anywhere}details{margin-top:40px;border-top:1px solid #ddd;padding-top:20px}summary{cursor:pointer;font-weight:600}pre{white-space:pre-wrap;font-size:12px;line-height:1.5}table{border-collapse:collapse;width:100%;font-size:14px}th,td{border-bottom:1px solid #ddd;padding:10px;text-align:left;white-space:nowrap}.scroll{overflow-x:auto}'
(W/'output').mkdir(exist_ok=True)
(W/'output'/'美伊停火研究-市场补充.md').write_text('\n'.join(md));(W/'output'/'美伊停火研究-市场补充.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(r['title'])+'</title><style>'+style+'</style><body>'+''.join(body)+'</body></html>')
print('Readable versions generated from frozen report, claims and sources.')
