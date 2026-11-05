from pathlib import Path
import json, html
W=Path(__file__).parent
r,c,s=[json.loads((W/(n+'.json')).read_text()) for n in ['report','claims','sources']]
esc=html.escape
md=['# '+r['title'],'','研究截点：'+r['as_of']+'。完整曲线03:44 UTC，月底复核05:06 UTC。','',r['answer']['text'],'']
body=['<h1>'+esc(r['title'])+'</h1>','<p class="date">'+esc(r['as_of'])+' · 完整曲线03:44 UTC，月底复核05:06 UTC</p>','<p>'+esc(r['answer']['text'])+'</p>']
for t in r['tables']:
 md+=['## '+t['title'],'','| '+' | '.join(t['columns'])+' |','| '+' | '.join(['---']*len(t['columns']))+' |']
 body+=['<h2>'+esc(t['title'])+'</h2><div class="scroll"><table><thead><tr>'+''.join('<th>'+esc(str(x))+'</th>' for x in t['columns'])+'</tr></thead><tbody>']
 for row in t['rows']:
  md+=['| '+' | '.join(map(str,row))+' |'];body+=['<tr>'+''.join('<td>'+esc(str(x))+'</td>' for x in row)+'</tr>']
 md+=['',t['note'],''];body+=['</tbody></table></div><p class="note">'+esc(t['note'])+'</p>']
sections=[(x['title'],[x['text']]) for x in r['findings']+r['alternatives']]+[('哪些新信息值得跟踪',[x['signal']+'：'+x['meaning'] for x in r['watch']])]
for title,paras in sections:
 md+=['## '+title,''];body+=['<h2>'+esc(title)+'</h2>']
 for text in paras:md+=[text,''];body+=['<p>'+esc(text)+'</p>']
md+=['## 关键来源',''];body+=['<h2>关键来源</h2><ul>']
for sid in ['S29','S39','S40','S38']:
 x=next(x for x in s['candidates'] if x['id']==sid)
 label=x['publisher']+' · '+x['published_at']
 md+=['- ['+label+']('+x['url']+')'];body+=['<li><a href="'+esc(x['url'],quote=True)+'">'+esc(label)+'</a></li>']
body+=['</ul>']
md+=['','## 证据与计算附录',''];body+=['<details><summary>证据与计算附录</summary>']
for x in c['claims']:
 text=x['id']+' ['+x['type']+'] '+x['text']+'；依据 '+', '.join([z['source_id'] for z in x.get('sources',[])]+x.get('basis',[]))
 md+=[text,''];body+=['<p>'+esc(text)+'</p>']
for x in s['candidates']:
 if not x['selection']['selected']:continue
 md+=['- ['+x['id']+' '+x['publisher']+']('+x['url']+')','  > '+x['quote'],'  定位：'+x['locator'],'']
 body+=['<p><a href="'+esc(x['url'],quote=True)+'">'+esc(x['id']+' '+x['publisher'])+'</a></p><blockquote>'+esc(x['quote'])+'</blockquote><p>'+esc(x['locator'])+'</p>']
for label,data in [('检验与判断底稿',r['analysis']),('固定计算',r['calculations'])]:
 text=json.dumps(data,ensure_ascii=False,indent=2);md+=['### '+label,'','```json',text,'```',''];body+=['<h3>'+esc(label)+'</h3><pre>'+esc(text)+'</pre>']
body+=['</details>']
style='body{font-family:system-ui,sans-serif;max-width:900px;margin:48px auto;padding:0 24px;line-height:1.85;color:#202124;background:#fff}h1{font-size:28px;line-height:1.4}h2{font-size:21px;margin-top:32px}.date,.note{font-size:14px;color:#666}table{border-collapse:collapse;width:100%;font-size:14px}td,th{padding:10px;border-bottom:1px solid #ddd;text-align:left;white-space:nowrap}.scroll{overflow-x:auto}a{color:#245a94}details{margin-top:40px;border-top:1px solid #ddd;padding-top:20px}summary{cursor:pointer;font-weight:600}pre{white-space:pre-wrap;font-size:12px;line-height:1.5}blockquote{border-left:3px solid #ddd;padding-left:16px;margin-left:0;overflow-wrap:anywhere}'
(W/'output').mkdir(exist_ok=True)
(W/'output'/'美伊停火-定价判断.md').write_text('\n'.join(md))
(W/'output'/'美伊停火-定价判断.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(r['title'])+'</title><style>'+style+'</style><body>'+''.join(body)+'</body></html>')
print('Readable HTML and Markdown generated from frozen bundle.')