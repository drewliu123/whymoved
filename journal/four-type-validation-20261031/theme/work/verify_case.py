# -*- coding: utf-8 -*-
import contextlib, datetime, hashlib, io, json, pathlib, runpy, sys
P=pathlib.Path('/Users/frankzhang/Desktop/投研助手/journal/four-type-validation-20261031/theme')
trusted=pathlib.Path('/Users/frankzhang/Desktop/投研助手/scripts')
# The existing validator imports local common.py; explicitly add only the reviewed project script directory.
sys.path.insert(0,str(trusted))
sys.argv=[str(trusted/'check_claims.py'),str(P/'claims.json'),'--json']
output=io.StringIO()
with contextlib.redirect_stdout(output),contextlib.redirect_stderr(output):
 try:runpy.run_path(str(trusted/'check_claims.py'),run_name='__main__')
 except SystemExit as e:code=int(e.code or 0)
log=output.getvalue()
(P/'logs/check_claims.log').write_text(log+'\nexit_code='+str(code)+'\n',encoding='utf-8')
(P/'logs/check_claims.exitcode').write_text(str(code)+'\n')
report=json.loads((P/'report.json').read_text())
claims=json.loads((P/'claims.json').read_text())
source=json.loads((P/'sources.json').read_text())
ids={c['id'] for c in claims['claims']}
errors=[]
required=['title','question','as_of','status','answer','findings','tables','alternatives','watch','gaps','sources']
for f in required:
 if f not in report: errors.append('missing report field '+f)
for field in ['findings','alternatives','watch']:
 for row in report[field]:
  if not set(row['claim_ids'])<=ids: errors.append('dangling claim ref')
for s in source['sources']:
 if hashlib.sha256((P/s['local_file']).read_bytes()).hexdigest()!=s['sha256']:errors.append('source hash mismatch '+s['id'])
for f in ['report.json','claims.json','sources.json','plan.json','calculations.json','datasets.json']:
 json.loads((P/f).read_text(encoding='utf-8'))
# Markdown generated from frozen report and must contain each original section unchanged.
md=(P/'report.md').read_text()
for field in ['answer']:
 if report[field] not in md:errors.append('markdown content drift')
for field in ['findings','alternatives']:
 for r in report[field]:
  if r['text'] not in md:errors.append('markdown section drift')
checks=json.loads(log)
validation={'as_of':report['as_of'],'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00','Z'),'status':'partial','check_claims':{'command':'python3 -I theme/work/verify_case.py (runpy executes existing /Users/frankzhang/Desktop/投研助手/scripts/check_claims.py with explicitly reviewed scripts directory on sys.path)','exit_code':code,'log':'logs/check_claims.log','result':checks,'limitations':'R1–R8是结构/来源层级/时间规则校验，不自动证明引用支持关系、数据准确性或研究判断正确。'},'structural_errors':errors,'source_count':6,'claim_count':len(ids),'arithmetic':{'status':'已满足','checks':['K1=27448×21%=5764.08百万美元','Q1 Δ利润/Δ收入=18/590=3.05085%','Q2 Δ利润/Δ收入=101/601=16.80532%','backlog/季度收入=15.2/3.951=3.8471倍','OCF-capex=FCF按三期原表重算'],'unknowns_not_zero':'主题利润输入缺失，未填零或主观情景数'},'protocol':{'A':{'status':'已满足','evidence':'report.answer与优先验证环节'},'B':{'status':'已满足' if code==0 and not errors else '未满足','evidence':'claims/source原文、实际文档、日期和口径断点；log保留'},'C':{'status':'已满足','evidence':'calculations.json；纯AI利润输入不足明确停止'},'D':{'status':'已满足','evidence':'主题机制、价值归属、分部敞口、经济量级与敏感性'},'E':{'status':'已满足','evidence':'扩产、并购混合、订单延期替代解释与改判指标；竞争直接资料不足保留缺口'},'F':{'status':'部分满足','evidence':'Markdown从report.json生成且文本完整性检查通过；HTML与浏览器检查父任务统一执行，尚未在本目录执行'}},'review':{'self_review':'已核对六官方文档；Q1/Q2数据中心口径分开，图中2H26利润率作展望；backlog与收入不同量度；公司现金不归AI','independent_review':'父任务独立审查四项定向修正已落实；见independent-review.md；未宣称额外独立复审通过','remaining_gaps':report['gaps']},'boundary':{'writes':'仅本theme目录','external_writes':False,'formal_journal_or_authors_modified':False,'downloaded_code_executed':False,'credentials_read':False,'python_isolated':True},'environment_failures':['poppler缺失，pdfinfo/pdftotext exit127；Read PDF无法渲染','Python -I无PDF包；使用系统PDFKit，未安装新依赖','初次build_case执行出现encoding识别错误exit1，文件重新UTF-8保存并加编码头后exit0；不影响最终JSON'], 'evidence_files':sorted(str(f.relative_to(P)) for f in (P/'raw').rglob('*') if f.is_file())}
(P/'validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(log,end='')
print('check_claims_exit_code='+str(code))
print('structural_errors='+str(errors))
print('validation.json written')
raise SystemExit(code if code else bool(errors))
