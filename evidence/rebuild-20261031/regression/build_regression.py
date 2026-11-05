#!/usr/bin/env python3
"""Offline dev regression conversion. Run with Python -I; stdlib only.

Writes exclusively below this script's directory. Original reports, claims,
source access records, and product scripts are never rewritten. This is not a
heldout evaluation or new research, and supplies no historical availability proof.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys

CASES = ('event', 'asset', 'theme', 'actor')
NOTICE = ('开发回归样本（dev sample，非 heldout）。仅将原冻结材料转换为 schema 2 报告；'
          '保留原 as_of，无新增检索、事实、引语、计算或研究判断。claims 保留原 schema 1，'
          '本次结构校验及开发归档不等于 strict schema 2 claims 验证，也不提供严格历史可得性证明。')
WHY = {
 'event': [
  '区分可解释的政策情景与可交易的概率优势，避免把市场参考价当成独立研究结论。',
  '让读者看到初判和看价后判断的先后及锚定限制，不能把后见修订重写成独立预测。',
  '把价格压力与实际需求分开，下一次数据才能区分继续收紧与等待的解释。',
  '结算标签受合约比较基准与异常规则影响，宏观方向和合约结果必须分别复盘。',
  '盘口时差、价差与可撤深度限制参考概率的执行意义。',
  '区分事件仍可交易与异步报价窗口，避免把缓存和成交字段差异解释成同刻价格变化。'],
 'asset': [
  '整月收益、高点回撤和单日下跌具有不同基准，混用会夸大或误读实际变化。',
  '利润率方向不能代替利润额；收入规模与毛利额共同决定原指引的业务含义。',
  '营运资本占用提供后续核查线索，但不足以诊断坏账或推断当月订单。'],
 'theme': [
  '固定季度、地区与证伪条件，避免把未披露季度或不同统计范围当作已实现趋势。',
  '逐段区分负荷、采购、交付、利润与现金，暴露从用电预测直接推导设备盈利的跳步。',
  '把研究焦点放到可观察的交付与集成环节，同时保留无法排名产品利润的边界。',
  '历史广义敞口和积压存量说明量级，但不能替代纯AI收入或未来交付保证。',
  '增量利润与平均利润率的差异有助于检验兑现，范围变化限制其因果解释。',
  '全公司现金、净利与分部利润口径不同，避免将并购成本或全部现金归于AI主题。',
  '显式缺失的输入阻止虚假精确点估计，并为后续数据提出可执行的验证需求。'],
 'actor': [
  '把支出、上线、商业化和资本回报分层验收，避免以公司总投入替代AI批次收益率。',
  '同时保留原承诺及修订后实际，判断方向兑现和金额时间兑现各自的证据。',
  '分类变化和交付延迟具有不同经济含义，不能将所有指引下调归于需求转弱。',
  '已有资产效率和价格也能解释增长，商业化信号不能独立归因新增资本回报。',
  '公开配置裁量与资源约束可观察，个人授权、激励及心理动机仍需另外取证。']}
TABLE_REFS = {
 'theme': [['C2','C3','C4','C10','C11','C12'], ['C5','C6'], ['C9']],
 'actor': [['C1','C2','C3','C4','C6','C7','C8','C24'], ['C2','C3','C4','C5'],
           ['C5','C6','C8','C13','C14','C15','C16','C17','C22']]}
THEME_ANSWER = ['C5','C11','C13','C16','C17','C19','C21']
TASKS = {'event':'事件定价：复用冻结证据的开发回归', 'asset':'资产变化与业务验证：复用冻结证据的开发回归',
         'theme':'主题到利润现金：复用冻结证据的开发回归', 'actor':'人物机构言行兑现：复用冻结证据的开发回归'}
BOOTSTRAP = 'import runpy,sys; sys.path.insert(0,sys.argv.pop(1)); target=sys.argv.pop(1); runpy.run_path(target,run_name="__main__")'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unique(values):
    return list(dict.fromkeys(values))


def source_catalog(ledger, original_sources):
    """Source list is anchored to actual inline claim sources, joined by URL.

    No publisher/origin/quote/date is inferred from a claim's own assertion.
    Original sources.json remains the authority for retrieval status and time.
    """
    originals = {s['url']: s for s in original_sources['sources']}
    catalog = {}
    for claim in ledger['claims']:
        for inline in claim.get('sources', []):
            url = inline['url']
            actual = originals.get(url, {})
            if url not in catalog:
                catalog[url] = {'id': actual.get('id') or inline.get('id') or inline.get('source_id'),
                                'inline': copy.deepcopy(inline), 'original': actual, 'claim_ids': []}
            catalog[url]['claim_ids'].append(claim['id'])
    for item in catalog.values():
        item['claim_ids'] = unique(item['claim_ids'])
    return list(catalog.values())


def convert_sources(report, catalog, original_sources, original_path):
    candidates = []
    statuses = {'regression_external_retrieval': {'status':'not_run', 'reason':NOTICE}}
    for item in catalog:
        inline, actual = item['inline'], item['original']
        sid = item['id']
        status = actual.get('status')
        # Do not promote local reuse to a successful historical retrieval.
        access = 'ok' if status in {'success','retrieved','ok'} else 'failed'
        retrieved = actual.get('retrieved_at') or actual.get('retrieved_at_end') or actual.get('first_retrieved_at')
        # Inline collected_at is used only when it was explicitly recorded.
        retrieved = retrieved or inline.get('collected_at') or 'unknown'
        quote, locator = '', ''
        if isinstance(actual.get('quote'), str):
            # Event S2 is explicitly a numeric record, not a prose quote.
            if 'data_quote' in actual and '原始数值记录' in actual['quote']:
                quote = ''
            else:
                quote = actual['quote']
            locator = actual.get('locator') or actual.get('local_evidence') or ''
        elif actual.get('excerpts'):
            excerpt = next((e for e in actual['excerpts'] if e.get('extraction','').startswith('verbatim')), None)
            if excerpt:
                quote, locator = excerpt['original'], excerpt['locator']
        elif actual.get('quotes'):
            excerpt = actual['quotes'][0]
            quote, locator = excerpt['quote'], excerpt['locator']
        candidates.append({
            'id':sid, 'url':inline['url'], 'publisher':inline['publisher'], 'tier':inline['tier'],
            'published_at':inline.get('published_at','unknown'), 'retrieved_at':retrieved,
            'quote':quote, 'locator':locator, 'origin_id':None,
            'origin_basis':'Unresolved in schema 1; publisher and URL are not proof of independent origin.',
            'supports':[], 'evidence_kind':'document', 'access_status':access,
            'selection':{'selected':False, 'relevance':'context', 'priority':'background',
                         'reason':'Legacy evidence catalog only; no new strict semantic selection performed.',
                         'purpose':'Development regression source audit; schema 1 claim citations remain unchanged.'},
            'provenance':{'original_sources_path':str(original_path), 'original_source_id':sid,
                          'original_status':status, 'claim_ids':item['claim_ids'],
                          'original_source_record':copy.deepcopy(actual),
                          'inline_source_record':copy.deepcopy(inline)}})
        statuses[sid] = {'status':'ok' if access == 'ok' else 'not_run',
                         'original_status':status,
                         'reason':'Original retrieval record reused, no new fetch.' if access == 'ok' else
                                  'Original sources.json records local reuse without explicit successful retrieval status.'}
    return {'schema_version':2, 'as_of':report['as_of'], 'historical':False,
            'mode':'development_regression_frozen_reuse',
            'historical_policy':'No historical availability assertions. historical=false describes a dev replay, not a reconstructed historical run.',
            'source_status':statuses, 'candidates':candidates,
            'original_source_audit':copy.deepcopy({k:v for k,v in original_sources.items() if k!='sources'})}


def convert_report(case, old, ledger, catalog):
    report = copy.deepcopy(old)
    assert ledger.get('schema_version',1) == 1, 'Refuse to downgrade a strict original ledger'
    ids = {c['id'] for c in ledger['claims']}
    report['schema_version'] = 2
    report['type'] = 'event_pricing' if case == 'event' else case
    report['task'] = TASKS[case]
    report['title'] = '【开发回归样本】' + old['title']
    report['answer'] = {'text':old['answer'], 'claim_ids':old.get('answer_claim_ids',THEME_ANSWER)}
    report['development_regression'] = {'heldout':False, 'new_research':False, 'strict_claims':False, 'notice':NOTICE}
    assert len(WHY[case]) == len(report['findings'])
    for finding, why in zip(report['findings'],WHY[case]):
        finding['why_it_matters'] = why
        finding['increment'] = {
            'kind':'connection',
            'baseline':'原 report.json 的同名 finding 与原 claims.json（'+', '.join(finding['claim_ids'])+'）；开发样本复用。',
            'detail':'仅把原结论与其验证意义重新连接：'+why+' 本轮无新事实、计算或判断更新，非相对原研究的新发现。'}
    report['limitations'] = [{'text':NOTICE, 'material':True, 'claim_ids':[]}]
    if old.get('status_reason'):
        report['limitations'].append({'text':old['status_reason'], 'material':True, 'claim_ids':[]})
    report['limitations'] += [{'text':gap, 'material':True, 'claim_ids':[]} for gap in old.get('gaps',[])]
    report['limitations'].append({'text':'原表述中 calculations.json、independent-freeze.json、inputs/、raw/ 等相对路径均指原样本目录；本包 legacy-calculations.json 仅为旧计算审计副本，未新做公式或算术认证。', 'material':False, 'claim_ids':[]})
    for n, table in enumerate(report['tables']):
        if not table.get('claim_ids'):
            table['claim_ids'] = TABLE_REFS[case][n]
        table['note'] = table.get('note','') + ' 开发转换：引用经原 claims.json 核对；仅提供原研究表格的结论级关联。'
        # Validate claim IDs embedded in legacy actor display columns too.
        if 'claim_ids' in table['columns']:
            column = table['columns'].index('claim_ids')
            for row in table['rows']:
                assert set(row[column].split(',')) <= ids
    # Preserve original inline source lists as a rendered source catalog table.
    report['tables'].append({'title':'原 claims 内联来源目录（未新增取证）',
        'columns':['原来源ID','发布方','层级','发布时间（原记录）','URL','所引用结论'],
        'rows':[[i['id'],i['inline']['publisher'],i['inline']['tier'],i['inline'].get('published_at','unknown'),
                 i['inline']['url'],', '.join(i['claim_ids'])] for i in catalog],
        'claim_ids':unique([cid for i in catalog for cid in i['claim_ids']]),
        'note':'按原内联来源 URL 关联原 sources.json；来源目录不证明 quote、历史可得性或独立性，缺失项不补造。'})
    if case == 'theme':
        edges = old['mechanism_edges']
        report['tables'].append({'title':'原研究机制链与证据边界', 'columns':['起点','终点','原研究状态'],
                                'rows':[[e['from_stage'],e['to_stage'],e['status']] for e in edges],
                                'claim_ids':unique([cid for e in edges for cid in e['claim_ids']])})
    if old.get('chart'):
        chart = report.pop('chart')
        # No new visualization or series: preserve every scalar in a data table.
        columns = unique([key for row in chart['rows'] for key in row])
        report['tables'].append({'title':chart['title']+'（原序列转表，无新计算）', 'columns':columns,
            'rows':[[row.get(key) for key in columns] for row in chart['rows']], 'claim_ids':chart['claim_ids'],
            'note':'原日收盘与盘中 high 字段原值保留，未重画或改造数据。'})
    def check_refs(value):
        if isinstance(value,dict):
            for key,item in value.items():
                if key == 'claim_ids' and isinstance(item,list):
                    assert set(item) <= ids, (case,item)
                check_refs(item)
        elif isinstance(value,list):
            for item in value:
                check_refs(item)
    check_refs(report)
    assert report['as_of'] == old['as_of'] == ledger['as_of']
    return report


def make_plan(case, report, original_plan):
    return {'schema_version':2, 'question':report['question'], 'type':report['type'], 'task':report['task'],
            'as_of':report['as_of'], 'historical':False, 'entity':{'event':'2026年12月Fed合约','asset':'NVDA',
            'theme':'Eaton Electrical Americas','actor':'Microsoft管理层'}[case],
            'decision_needed':'仅验证冻结输入转换、渲染和归档流程；不开展新的投研决定。',
            'prior_judgment':report['answer']['text'],
            'stop_condition':'开发回归渲染完成并记录归档成功或缺失元数据的阻塞；不检索新材料或伪造历史取证。',
            'comparison':{'period':report['as_of']+' 原研究截点', 'unit':'保留原报告各表与结论单位',
                          'scope':'四类型旧开发样本 '+case+'；非 heldout；未重建历史可得性'},
            'hypotheses':[{'explanation':'原冻结内容可在保留 schema 1 claims 条件下适配 schema 2 报告。',
                           'discriminating_observation':'render_report 校验/渲染退出码；research_run 归档与无变化差分。'}],
            'queries':[{'question':'原材料可否安全适配？','query':'offline local JSON audit; external queries not executed',
                        'source':'journal/four-type-validation-20261031/'+case,
                        'purpose':'开发回归，不做新研究或历史证明'}],
            'budget':{'max_queries':1,'max_followups':0}, 'executed_external_queries':0,
            'original_plan':copy.deepcopy(original_plan), 'development_notice':NOTICE}


def command(root, logdir, name, argv, env=None):
    result = subprocess.run(argv, cwd=str(root), env=env, text=True, capture_output=True)
    logdir.mkdir(parents=True,exist_ok=True)
    (logdir/(name+'.stdout.log')).write_text(result.stdout,encoding='utf-8')
    (logdir/(name+'.stderr.log')).write_text(result.stderr,encoding='utf-8')
    record = {'argv':argv,'shell':shlex.join(argv),'cwd':str(root),'exit_code':result.returncode,
              'stdout':str(logdir/(name+'.stdout.log')),'stderr':str(logdir/(name+'.stderr.log'))}
    if env and env.get('TOUYAN_HOME'):
        record['environment'] = {'TOUYAN_HOME':env['TOUYAN_HOME'],'PYTHONDONTWRITEBYTECODE':env.get('PYTHONDONTWRITEBYTECODE')}
    save(logdir/(name+'.command.json'),record)
    return result,record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--render-only',choices=CASES)
    parser.add_argument('--output-name', default='final-v2', help='Fresh owned child directory')
    args = parser.parse_args()
    root = args.root.resolve()
    script_dir = Path(__file__).resolve().parent
    assert script_dir == root/'evidence/rebuild-20261031/regression'
    assert args.output_name and Path(args.output_name).name == args.output_name
    dest = script_dir/args.output_name
    dest.mkdir(parents=True,exist_ok=True)
    sys.dont_write_bytecode = True
    sys.path.insert(0,str(root/'scripts'))
    import render_report
    import sources as sources_module
    if args.render_only:
        directory = dest/args.render_only
        report, claims = load(directory/'report.json'),load(directory/'claims.json')
        render_report.write_outputs(directory/'rendered',render_report.render_markdown(report,claims),
                                     render_report.render_html(report,claims), overwrite=True)
        print(json.dumps({'mode':'render_only_legacy_claims','sources2_archive':'blocked', 'case':args.render_only}))
        return 0
    original = root/'journal/four-type-validation-20261031'
    original_files = sorted(p for p in original.rglob('*') if p.is_file())
    before = {str(p.relative_to(root)):sha(p) for p in original_files}
    product_before = {str(p.relative_to(root)):sha(p) for p in sorted((root/'scripts').glob('*.py'))}
    save(dest/'original-manifest.before.json',{'originals':before,'product_scripts':product_before})
    all_commands, results = [], []
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', TOUYAN_HOME=str(dest/'strict-gate-home'))
    def cli(script,*argv):
        return [sys.executable,'-I','-c',BOOTSTRAP,str(root/'scripts'),str(root/'scripts'/script),*map(str,argv)]
    for case in CASES:
        folder = dest/case
        folder.mkdir(parents=True,exist_ok=True)
        old = load(original/case/'report.json')
        ledger = load(original/case/'claims.json')
        source_old = load(original/case/'sources.json')
        old_plan = load(original/case/'plan.json')
        catalog = source_catalog(ledger,source_old)
        report = convert_report(case,old,ledger,catalog)
        source_doc = convert_sources(report,catalog,source_old,original/case/'sources.json')
        plan = make_plan(case,report,old_plan)
        save(folder/'report.json',report)
        # Byte copy: absent version remains schema 1, with every source/basis intact.
        (folder/'claims.json').write_bytes((original/case/'claims.json').read_bytes())
        save(folder/'sources.json',source_doc)
        save(folder/'plan.json',plan)
        (folder/'legacy-calculations.json').write_bytes((original/case/'calculations.json').read_bytes())
        errors = sources_module.validate_sources(source_doc)
        save(folder/'sources-validation.json',{'passed':not errors,'errors':errors,
             'strict_claims_validation':False,'historical_availability_proved':False})
        refs_check = {'claims_byte_identical':sha(folder/'claims.json')==sha(original/case/'claims.json'),
                      'original_schema':ledger.get('schema_version',1),'report_schema':report['schema_version'],
                      'as_of_preserved':report['as_of']==old['as_of'], 'answer_text_preserved':report['answer']['text']==old['answer'],
                      'findings_text_preserved':all(a['text']==b['text'] for a,b in zip(report['findings'],old['findings'])),
                      'table_references_resolve':all(set(t['claim_ids']) <= {c['id'] for c in ledger['claims']} for t in report['tables']),
                      'new_external_queries':0,'heldout':False,'strict_claims_validation':False}
        save(folder/'transformation-checks.json',refs_check)
        assert all(refs_check[k] for k in ('claims_byte_identical','as_of_preserved','answer_text_preserved','findings_text_preserved','table_references_resolve'))
        if errors:
            render_cmd = [sys.executable,'-I',str(script_dir/'build_regression.py'),'--root',str(root),'--output-name',args.output_name,'--render-only',case]
        else:
            render_cmd = cli('render_report.py',folder/'report.json','--claims',folder/'claims.json','--sources',folder/'sources.json','--out-dir',folder/'rendered','--overwrite')
        rendered,rec = command(root,folder/'logs','render',render_cmd,env)
        all_commands.append(rec)
        assert rendered.returncode == 0, rendered.stderr
        markdown = (folder/'rendered/report.md').read_text()
        page = (folder/'rendered/report.html').read_text()
        label = '证据模式：旧版 schema 1；本报告未按 schema 2 的来源与证据契约校验。'
        assert label in markdown and label in page
        # Markdown table header, delimiter and rows must be contiguous lines.
        lines = markdown.splitlines()
        for i,line in enumerate(lines):
            if line.startswith('| ---'):
                assert i > 0 and lines[i-1].startswith('| ')
                assert i+1 < len(lines) and lines[i+1].startswith('| ')
        save(folder/'render-checks.json',{'legacy_label_in_both_formats':True,
             'markdown_table_delimiters_contiguous':True, 'markdown_table_count':sum(line.startswith('| ---') for line in lines),
             'html_table_count':page.count('<table>'),'browser_visual_check':'not_run'})
        archive_cmd = cli('research_run.py','archive','--report',folder/'report.json','--claims',folder/'claims.json',
                          '--sources',folder/'sources.json','--plan',folder/'plan.json')
        archived,rec = command(root,folder/'logs','archive',archive_cmd,env)
        all_commands.append(rec)
        row = {'case':case,'development_sample':True,'heldout':False,'render_exit':rendered.returncode,
               'source_validation_errors':errors,'archive_exit':archived.returncode,'claim_schema':ledger.get('schema_version',1),
               'report_schema':2,'sources_schema':2,'strict_claims_validated':False,'historical_availability_proved':False}
        assert archived.returncode != 0, 'Legacy claims must be rejected by the NEW archive gate'
        row['archive_status']='blocked_legacy_claims_expected'
        row['blocker']=archived.stderr
        row['update_status']='not_run_requires_safe_schema2_claims'
        row['no_change_note']='Legacy no-change updates are not valid strict acceptance. Safe schema 2 fixture tests belong to the parent validation.'
        results.append(row)
        save(dest/'commands.json',all_commands)
        save(dest/'results.json',{'notice':NOTICE,'cases':results})
    listed,rec = command(root,dest/'logs','list-runs',cli('research_run.py','list'),env)
    all_commands.append(rec)
    assert listed.returncode==0,listed.stderr
    assert len(json.loads(listed.stdout))==0
    after = {str(p.relative_to(root)):sha(p) for p in original_files}
    product_after = {str(p.relative_to(root)):sha(p) for p in sorted((root/'scripts').glob('*.py'))}
    save(dest/'original-manifest.after.json',{'originals':after,'product_scripts':product_after})
    integrity = {'original_files':len(before),'originals_unchanged':before==after,
                 'product_scripts_unchanged':product_before==product_after,
                 'scope':'Writes confined to evidence/rebuild-20261031/regression/', 'archived_development_runs':0,
                 'superseded_nonconforming_runs':6}
    save(dest/'integrity.json',integrity)
    assert integrity['originals_unchanged']
    save(dest/'commands.json',all_commands)
    save(dest/'results.json',{'notice':NOTICE,'cases':results,'integrity':integrity})
    lines = ['# Four development regression bundles','',NOTICE,'',
      'This is an offline format/pipeline regression, not heldout validation, new research, strict schema 2 claim proof, or historical reconstruction.',
      'Original answer/finding texts and as_of values are preserved; claims.json is copied byte-for-byte with implicit schema 1. No quotes, origin families, publication instants, retrieval instants, or availability records are invented.',
      'All finding increments are labeled connection with an explicit old-claim baseline and no-new-research disclosure. This expresses existing relationships, not novel research.',
      'Missing theme/actor table references are mapped to actual original claim IDs. The original asset price series is preserved as a scalar table; no chart is authored.',
      'Source candidates come from inline claims joined to original sources.json by exact URL. Original status/time/quote records are retained in provenance. All candidates are unselected, supports=[] and origin_id=null: no new semantic source certification.',
      'historical=false denotes a development replay; original as_of is not replaced with the build time. No availability assertion is supplied. Legacy claims do not qualify for NEW strict archives.',
      'Original source lists appear in every rendered report; source quotes are copied only from existing source fields, never synthesized from claim text.',
      '', '| case | render | sources2 validation | development archive | no-change update |',
      '| --- | --- | --- | --- | --- |']
    for r in results:
        lines.append('| '+r['case']+' | exit '+str(r['render_exit'])+' | '+('blocked' if r['source_validation_errors'] else 'pass')+' | '+r['archive_status']+' | '+str(r.get('no_change_exit','not run'))+' |')
    lines += ['', 'All four cases remain render-only: their byte-identical schema 1 claims are not valid NEW archive inputs. Expected archive rejection is recorded with actual commands and stderr. No claim schema is downgraded and no metadata is invented to pass the gate.',
      'Asset also lacks original retrieval instants for S1 and S3. Its render uses render_report API with sources=None and legacy claims, while its source catalog remains a report table. Missing source metadata is recorded as unknown.',
      'The initial archiver accepted legacy inputs and produced six sandbox archive/update runs. Those prior results, commands and runs are superseded/nonconforming, preserved only to expose former gate behavior. They do not count as valid archive or update evidence. See superseded-results.json and superseded-nonconforming-runs.json.',
      'No valid strict no-change update is demonstrated by these legacy bundles. The parent validation can cover safe schema 2 inputs with automated fixture tests; this conversion does not synthesize strict evidence.',
      '', '## Reproduction and evidence','',
      'Run: `python3 -I evidence/rebuild-20261031/regression/build_regression.py --root /Users/frankzhang/Desktop/投研助手`.',
      'The script refreshes only its owned development artifacts. Old sandbox runs remain labeled superseded; strict-gate-home must remain empty because archive attempts should be rejected.',
      'commands.json contains complete command argv, shell representation, environment overrides, exits, and log paths; per-case logs retain stdout/stderr. build.command.json/build.stdout.log/build.stderr.log record the outer transformation invocation.',
      'results.json, integrity.json and before/after original manifests provide outcomes and hashes. legacy-calculations.json is an unmodified old audit artifact, not a new schema 2 calculation document.',
      'Verification covers structure, content preservation, real CLI rendering/archiving and manifest/diff behavior; it does not add a browser/device visual check or claim a new complete product QA pass.',
      '',json.dumps(integrity,ensure_ascii=False,indent=2),'']
    (dest/'SUMMARY.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({'cases':results,'integrity':integrity},ensure_ascii=False,indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
