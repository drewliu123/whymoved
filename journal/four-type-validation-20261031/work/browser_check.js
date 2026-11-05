const fs=await import('node:fs/promises');
const base='/Users/frankzhang/Desktop/投研助手/journal/four-type-validation-20261031';
const task=await taskSpace(16);const page=task.page('p1');
await page.goto('data:text/html;charset=utf-8,'+encodeURIComponent(await fs.readFile(base+'/index.html','utf8')));
const reports={};
for(const key of ['event','asset','theme','actor']){
 const report=JSON.parse(await fs.readFile(base+'/'+key+'/report.json','utf8'));
 await page.click('loc=css:nav button[data-key="'+key+'"]');
 const check=await page.evaluate(r=>{
  const content=document.querySelector('main').textContent;
  const expected=[r.title,r.question,r.answer,...r.findings.flatMap(f=>[f.title,f.text]),...r.alternatives.flatMap(a=>[a.title,a.text]),...r.watch.flatMap(w=>[w.signal,w.meaning]),...r.tables.flatMap(t=>[...t.columns,...t.rows.flat()])];
  return {missing:expected.filter(t=>!content.includes(String(t))),heading:document.querySelector('h1').textContent,tables:document.querySelectorAll('table').length,overflow:document.documentElement.scrollWidth>innerWidth,claimCount:document.querySelectorAll('[id^="claim-"]').length};
 },report);
 reports[key]=check;
}
await page.click('loc=css:nav button[data-key="asset"]');
await page.focus('loc=css:.chart rect[tabindex="0"] >> nth=0');
const keyboard=await page.evaluate(()=>document.querySelector('.readout').textContent);
await page.click('loc=css:main .answer .refs a >> nth=0');
const evidence=await page.evaluate(()=>document.querySelector('#claim-C1').closest('details').open);
const modes={};
for(const theme of ['light','dark']){
 if(await page.evaluate(()=>document.documentElement.dataset.theme)!==theme){
  const current=await page.evaluate(()=>document.documentElement.dataset.theme||(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light'));
  if(current!==theme)await page.click('loc=css:#theme');
 }
 await page.evaluate(()=>scrollTo(0,0));
 modes[theme]=await page.evaluate(()=>({background:getComputedStyle(document.body).backgroundColor,line:getComputedStyle(document.querySelector('.chart-line')).stroke,overflow:document.documentElement.scrollWidth>innerWidth}));
 await page.screenshot({path:base+'/asset-desktop-'+theme+'.png'});
}
await page.cdp('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});
const mobile={};
for(const key of ['event','asset','theme','actor']){
 await page.click('loc=css:nav button[data-key="'+key+'"]');
 await page.evaluate(()=>scrollTo(0,0));
 mobile[key]=await page.evaluate(()=>({width:innerWidth,overflow:document.documentElement.scrollWidth>innerWidth,tableScroll:document.querySelector('.table-wrap').scrollWidth>document.querySelector('.table-wrap').clientWidth}));
 if(key==='theme'||key==='asset')await page.screenshot({path:base+'/'+key+'-mobile-dark.png'});
}
await page.cdp('Emulation.clearDeviceMetricsOverride');
await page.click('loc=css:nav button[data-key="theme"]');await page.evaluate(()=>scrollTo(0,0));
await page.screenshot({path:base+'/theme-desktop.png'});
const result={checked_at:new Date().toISOString(),renderer:'index.html',reports,keyboard,evidence_expands:evidence,modes,mobile,scope:'Browser DOM content, viewport, interaction, style and screenshot checks. Does not validate source truth, future outcomes or printer output.'};
await fs.writeFile(base+'/browser-validation.json',JSON.stringify(result,null,2));
console.log(JSON.stringify(result));
