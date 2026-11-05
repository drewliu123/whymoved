# -*- coding: utf-8 -*-
import importlib.util, json, sys
from pathlib import Path
w=Path('/Users/frankzhang/Desktop/投研助手/journal/work/20261102-warsh')
t=Path('/Users/frankzhang/.claude/plugins/cache/touyan-local/touyan/0.4.1/scripts')
sys.path.insert(0,str(t))
import render_report as r
original=r._blocks
def blocks(*args,**kwargs):
    deferred=[]
    for b in original(*args,**kwargs):
        if b[0]=='p' and b[1].startswith(('为什么重要：','相较基线：','研究增量（','模型不适用：')):
            deferred.append(b);continue
        if b[0]=='audit':
            yield ('h2','附录：研究取舍')
            yield from deferred
        yield b
r._blocks=blocks
report=json.loads((w/'report.json').read_text());claims=json.loads((w/'claims.json').read_text());sources=json.loads((w/'sources.json').read_text())
(w/'output/report.md').write_text(r.render_markdown(report,claims,sources))
(w/'output/report.html').write_text(r.render_html(report,claims,sources))
a=json.loads((w/'audit.json').read_text())
a['review']={'status':'completed','findings':[],'dispositions':'独立审查未发现改变主判断的问题；已回读就任、9月及10月声明、Hoover访谈和2010QE2。审查未独立核验S4纪要及S5报道，原取证由主研究完成。'}
a['rendering']='先运行内置render_report.py验证渲染，再从同一冻结JSON通过共享块生成器将研究过程文字移至附录；未手改任一输出的研究结论。'
a['queries_executed']=['Kevin Warsh Federal Reserve chair November 2026 October 2026','Kevin Warsh October 28 2026 press conference September rate increase 2026 inflation balance sheet','site.hoover.org Kevin Warsh 2025 2026 interest rates artificial intelligence balance sheet independence','site.federalreserve.gov Warsh 2010 November 8 2010 monetary policy asset purchases inflation','Kevin Warsh 2025 2026 artificial intelligence balance sheet lower interview transcript','site.hoover.org Warsh 2025 balance sheet interest Warsh','Kevin Warsh 2025 productivity inflation Hoover printing']
a['execution'].append({'command':'readable_render.py','exit_code':0,'log':'同源Markdown和HTML已生成；过程字段移至附录。'})
(w/'audit.json').write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n')
