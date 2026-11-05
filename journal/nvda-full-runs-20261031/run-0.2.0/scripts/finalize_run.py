import pathlib,json,sys,subprocess,os,hashlib
r=pathlib.Path(sys.argv[1]); plugin=pathlib.Path(sys.argv[2]); p=r/'claims.json'; d=json.loads(p.read_text()); by={c['id']:c for c in d['claims']}
by['C8']['text']='增长兑现与AI投入回报可作为待检验研究方向；旧季收入仍高增长且指引毛利率下降，最后交易日存在板块冲击叙事。现有证据无法识别10月全月主因，未确认10月NVDA订单恶化，也不能用最后一天新闻解释全月。'
by['C9']['text']='后续分别核对收入兑现、现金回收和客户投入回报；关注中国收入假设、Rubin交付转化，以及第三方融资平台最终协议和资金到位。平台未落地不能单独证伪近期增长，融资落地也不能证明终端需求持续。'
by['C10']['text']='反方是AI投入回报担忧不必立刻减少GPU采购，高增长仍可能兑现；Q3总收入指引区间1058.4至1101.6亿美元、两种毛利率区间均73.5%至74.5%。达到公司指引不能证明满足股票隐含预期或客户长期回报，毛利率下降不代表毛利额下降。'
d['claims'].append(dict(id='C11',text='官方FY2027 Q2经营现金流240.77亿美元，半年累计744.21亿美元，据此Q1为503.44亿美元；Q2应收账款变动占用现金223.46亿美元。收入高增长应同时核查现金转化，这些旧季数字不证明10月订单或融资恶化。',type='fact',as_of=d['as_of'],sources=by['C3']['sources']))
d['claims'].append(dict(id='C12',text='H1在截面至2026年12月31日23:59:59 ET窗口内，FY2027 Q3首次合格官方披露数据中心收入严格超过1000亿美元：三个冻结证据单次判断原p为0.63、0.64、0.68，原版forecast.py算得final_prob=0.65。仅使用C3/C4/C5；无经核实截面成交参照，可信度较低，同模型多调用不构成统计独立，不声称更准。',type='inference',as_of=d['as_of'],sources=[],basis=['C3','C4','C5']))
p.write_text(json.dumps(d,ensure_ascii=False,indent=2))
f=r/'forecast.json'; fc=json.loads(f.read_text()); tr=json.loads((r/'forecaster-trials.json').read_text()); fc['forecasts'][0]['trials']=[t['p'] for t in tr['trials']]; fc['forecasts'][0]['market_search_gap']='Matching Polymarket revenue contract found; displayed midpoint not execution. $100B Gamma Yes bid0.72 ask0.98, last0.72, updated12:28:16Z after as_of; CLOB YES and NO book403, no verified timestamped depth. Does not assert global absence of prices.'; f.write_text(json.dumps(fc,ensure_ascii=False,indent=2))
commands=[('check-claims-final',[sys.executable,str(plugin/'scripts/check_claims.py'),str(p),'--json']),('forecast-finalize',[sys.executable,str(plugin/'scripts/forecast.py'),'finalize',str(f),'--claims',str(p)]),('forecast-check',[sys.executable,str(plugin/'scripts/forecast.py'),'check',str(f),'--claims',str(p)])]
records=[]; env=os.environ.copy();env['TOUYAN_HOME']=str(r)
for name,cmd in commands:
 x=subprocess.run(cmd,capture_output=True,text=True,env=env,cwd=str(r));(r/'logs'/f'{name}.stdout.log').write_text(x.stdout);(r/'logs'/f'{name}.stderr.log').write_text(x.stderr);records.append(dict(name=name,command=cmd,exit_code=x.returncode));print(name,x.returncode,x.stdout.strip())
 if x.returncode:raise SystemExit(x.returncode)
(r/'validation-execution.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
fc=json.loads(f.read_text())['forecasts'][0]
memo=dict(question=d['question'],type='asset',entity='NVIDIA NVDA',as_of=d['as_of'],market_snapshot=[],hypotheses=[dict(id='H1',text=fc['question'],verify_by=fc['window_end'],falsify_if='首次合格数值≤USD100B（相等为NO）；或窗口结束缺失合格披露，按规则NO但标记缺失。只用首次季度值、不采纳后续修订，四舍五入显示100.0B无更精确值也不推定超标。',my_prob=fc['final_prob'],authors=[],prob_mode='independent',question=fc['question'],yes_means=fc['yes_means'],window_start=fc['window_start'],window_end=fc['window_end'],resolution_source=fc['resolution_source'])],trial_run=True,statistics_policy='isolated trial only; do not grade or write official statistics')
(r/'memo.json').write_text(json.dumps(memo,ensure_ascii=False,indent=2))
