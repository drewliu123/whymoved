from pathlib import Path
import json,html
W=Path(__file__).parent
r=json.loads((W/'report.json').read_text());c=json.loads((W/'claims.json').read_text());s=json.loads((W/'sources.json').read_text())
sections=[('判断',[r['answer']['text']])]+[(x['title'],[x['text']]) for x in r['findings']]+[(x['title'],[x['text']]) for x in r['alternatives']]+[('接下来观察什么',[x['signal']+'：'+x['meaning'] for x in r['watch']])]
md=['# '+r['title'],'','研究截点：2026年11月1日（美国东部）；UTC '+r['as_of'],'']
body=['<h1>'+html.escape(r['title'])+'</h1>','<p class="date">研究截点：2026年11月1日（美国东部） · '+html.escape(r['as_of'])+'</p>']
for title,paras in sections:
 md+=['## '+title,'']
 body+=['<h2>'+html.escape(title)+'</h2>']
 for text in paras:md+=[text,''];body+=['<p>'+html.escape(text)+'</p>']
md+=['## 证据附录','','以下保存归属、推断依据与检验状态；未取得的事实不视为否定证据。','']
body+=['<details><summary>证据附录：来源、主张与检验状态</summary>']
for x in c['claims']:
 refs=', '.join(z['source_id'] for z in x.get('sources',[])) or '依据 '+', '.join(x.get('basis',[]))
 text=x['id']+' ['+x['type']+'] '+x['text']+'（'+refs+'）'
 md+=[text,''];body+=['<p>'+html.escape(text)+'</p>']
for x in s['candidates']:
 if not x['selection']['selected']:continue
 text=x['id']+' · '+x['publisher']+' · '+str(x['published_at'])
 md+=['- ['+text+']('+x['url']+')','  > '+x['quote'],'  定位：'+x['locator'],'']
 body+=['<p><a href="'+html.escape(x['url'],quote=True)+'">'+html.escape(text)+'</a></p><blockquote>'+html.escape(x['quote'])+'</blockquote><p>'+html.escape(x['locator'])+'</p>']
analysis=json.dumps(r['analysis'],ensure_ascii=False,indent=2)
md+=['### 完整分析底稿','','```json',analysis,'```','']
body+=['<h3>完整分析底稿</h3><pre>'+html.escape(analysis)+'</pre></details>']
style='body{font-family:system-ui,sans-serif;color:#202124;background:#fff;max-width:820px;margin:48px auto;padding:0 24px;line-height:1.85}h1{font-size:28px;line-height:1.4}h2{font-size:21px;margin-top:32px}.date{color:#666;font-size:14px}a{color:#245a94}blockquote{border-left:3px solid #ddd;margin-left:0;padding-left:16px;color:#555}details{margin-top:40px;border-top:1px solid #ddd;padding-top:20px}summary{cursor:pointer;font-weight:600}pre{white-space:pre-wrap;font-size:12px;line-height:1.5}'
(W/'output'/'美伊停火研究.md').write_text('\n'.join(md))
(W/'output'/'美伊停火研究.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(r['title'])+'</title><style>'+style+'</style><body>'+''.join(body)+'</body></html>')
print('Readable Markdown and HTML generated from the same frozen report, claims and sources.')
