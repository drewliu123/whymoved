#!/usr/bin/env python3
"""Single-pass, unauthenticated SEC source validation. No retries or redirects."""
import datetime as dt
import hashlib
import json
import pathlib
import platform
import subprocess
import sys
import time

ROOT = pathlib.Path(sys.argv[1]).resolve()
RAW = ROOT / 'raw'
RAW.mkdir(parents=True, exist_ok=True)
started = dt.datetime.now(dt.timezone.utc)
run_id = started.strftime('%Y%m%dT%H%M%S%fZ')
reference = dt.datetime(2026, 11, 1, tzinfo=dt.timezone.utc)
result = {
    'started_utc': started.isoformat(),
    'reference_date': '2026-11-01',
    'reference_interpretation': '2026-11-01T00:00:00+00:00',
    'difference_seconds_from_reference_midnight': (started-reference).total_seconds(),
    'calendar_day_difference_utc': (started.date()-reference.date()).days,
    'python_version': sys.version,
    'platform': platform.platform(),
    'command': ['python3', '-I', str(pathlib.Path(__file__).resolve()), str(ROOT)],
    'user_agent': 'InvestmentResearchSourceValidation',
    'request_policy': 'Serial GET; 30 seconds maximum per request; one attempt each; no redirects, retries, authentication, keys, cache reuse, trading or 403/rate-limit bypass.',
    'sdk_tested': False,
    'sdk_note': 'edgartools not installed or tested. Underlying public SEC HTTP endpoints only.',
    'requests': [],
    'recent_filings': [],
}
result['curl_version'] = subprocess.run(['curl', '--version'], capture_output=True, text=True).stdout.splitlines()[0]

def get(label, url):
    directory = RAW / (run_id + '-' + label)
    directory.mkdir(exist_ok=False)
    body = directory / 'response.body'
    headers = directory / 'response.headers'
    command = ['curl', '--silent', '--show-error', '--request', 'GET', '--max-time', '30', '--connect-timeout', '15', '--retry', '0', '--user-agent', result['user_agent'], '--header', 'Accept: application/json' if label != 'filing_document' else 'Accept: text/html', '--header', 'Cache-Control: no-cache', '--dump-header', str(headers), '--output', str(body), '--write-out', '%{http_code}\n%{time_total}\n%{size_download}\n%{url_effective}\n', url]
    t = time.monotonic()
    process = subprocess.run(command, capture_output=True, text=True, timeout=35)
    elapsed = time.monotonic()-t
    fields = process.stdout.splitlines()
    data = body.read_bytes() if body.exists() else b''
    entry = {'label': label, 'url': url, 'completed_utc': dt.datetime.now(dt.timezone.utc).isoformat(), 'command': command, 'exit_code': process.returncode, 'http_status': int(fields[0]) if fields and fields[0].isdigit() else None, 'elapsed_seconds_monotonic': round(elapsed, 6), 'curl_time_total_seconds': float(fields[1]) if len(fields)>1 else None, 'bytes_saved': len(data), 'physical_line_count': len(data.splitlines()), 'sha256': hashlib.sha256(data).hexdigest(), 'body_path': str(body), 'headers_path': str(headers), 'stderr': process.stderr, 'redirects_followed': False}
    result['requests'].append(entry)
    (directory / 'request.json').write_text(json.dumps(entry, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'label': label, 'http': entry['http_status'], 'exit': process.returncode, 'seconds': round(elapsed, 3), 'bytes': len(data)}), flush=True)
    parsed = None
    if entry['http_status'] == 200 and process.returncode == 0:
        try:
            parsed = json.loads(data)
        except (ValueError, UnicodeDecodeError) as error:
            entry['json_parse_error'] = str(error)
    return entry, parsed

submission, sub = get('submissions', 'https://data.sec.gov/submissions/CIK0001045810.json')
facts_request, facts = get('companyfacts', 'https://data.sec.gov/api/xbrl/companyfacts/CIK0001045810.json')
if sub:
    recent = sub.get('filings', {}).get('recent', {})
    dates = [x for x in recent.get('filingDate', []) if x]
    submission['statistics'] = {'entity_name': sub.get('name'), 'recent_filing_records': len(recent.get('accessionNumber', [])), 'earliest_filing_date': min(dates) if dates else None, 'latest_filing_date': max(dates) if dates else None, 'historical_file_references': len(sub.get('filings', {}).get('files', [])), 'scope': 'Dates/count cover filings.recent only; historical referenced JSON files not fetched.'}
    order = sorted(range(len(recent.get('accessionNumber', []))), key=lambda i: recent.get('filingDate', [''])[i], reverse=True)
    for i in order[:2]:
        accession = recent['accessionNumber'][i]
        document = recent['primaryDocument'][i]
        result['recent_filings'].append({'form': recent['form'][i], 'filing_date': recent['filingDate'][i], 'report_date': recent.get('reportDate', ['']*len(order))[i], 'accession_number': accession, 'primary_document': document, 'url': 'https://www.sec.gov/Archives/edgar/data/1045810/'+accession.replace('-', '')+'/'+document, 'url_basis': 'Generated from SEC submissions filings.recent: CIK 0001045810 stripped of leading zeros, accessionNumber stripped of hyphens, and primaryDocument appended to official SEC Archives path. Not a URL directly returned by the API.'})
if facts:
    records = []
    concepts = 0
    namespaces = facts.get('facts', {})
    for namespace in namespaces.values():
        concepts += len(namespace)
        for concept in namespace.values():
            for unit_records in concept.get('units', {}).values():
                records.extend(unit_records)
    def date_range(key):
        values = [r[key] for r in records if r.get(key)]
        return {'earliest': min(values) if values else None, 'latest': max(values) if values else None}
    facts_request['statistics'] = {'entity_name': facts.get('entityName'), 'namespace_count': len(namespaces), 'concept_count': concepts, 'fact_unit_records': len(records), 'filed_dates': date_range('filed'), 'period_end_dates': date_range('end'), 'period_start_dates': date_range('start'), 'count_definition': 'Sum of all entries in facts[namespace][concept].units[unit]; entries can repeat economic facts across filings/contexts, not unique economic observations.'}
if result['recent_filings'] and all(r['http_status'] not in (403, 429) for r in result['requests']):
    doc, _ = get('filing_document', result['recent_filings'][0]['url'])
    result['recent_filings'][0]['document_verification'] = {'http_status': doc['http_status'], 'exit_code': doc['exit_code'], 'body_path': doc['body_path']}
result['finished_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
result['script_exit_code'] = 0 if all(r['http_status'] == 200 and r['exit_code'] == 0 for r in result['requests'][:2]) else 1
result['outcome'] = 'Both public APIs reachable and parseable' if sub and facts else 'Public API validation incomplete or blocked; see actual HTTP/error evidence'
result['limitations'] = ['No old cache used; live one-pass requests only.', 'No archive directory crawl or additional historical submissions fetched.', 'HTTP success does not independently verify economic data accuracy.', 'No SDK coverage.', 'No retries or alternate transport attempted after access failure.']
(ROOT/'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
lines = ['# SEC / NVIDIA 免费公开数据实测', '', '- 开始 UTC：'+result['started_utc'], '- 结束 UTC：'+result['finished_utc'], '- 与 2026-11-01 UTC 日历日差：'+str(result['calendar_day_difference_utc'])+'；距该日 UTC 零点秒数：'+str(result['difference_seconds_from_reference_midnight']), '- Python：'+platform.python_version()+'；'+result['curl_version'], '- 命令：`'+' '.join(result['command'])+'`', '- 脚本退出码：'+str(result['script_exit_code']), '- User-Agent：`InvestmentResearchSourceValidation`（无虚构邮箱）', '- 无 key、只读、不交易；串行，每项最多一次，30 秒总超时，不重试、不跟随重定向、不绕过 403/限流。', '', '| 请求 | HTTP | curl退出码 | 耗时秒 | 字节 | 物理行数 |', '|---|---:|---:|---:|---:|---:|']
for r in result['requests']:
    lines.append('| '+r['label']+' | '+str(r['http_status'])+' | '+str(r['exit_code'])+' | '+str(r['elapsed_seconds_monotonic'])+' | '+str(r['bytes_saved'])+' | '+str(r['physical_line_count'])+' |')
    if r.get('statistics'):
        lines.extend(['', r['label']+' 统计：`'+json.dumps(r['statistics'], ensure_ascii=False)+'`', ''])
    if r['stderr']:
        lines.extend(['', '请求错误：`'+r['stderr'].strip()+'`', ''])
lines.extend(['', '## 两条近期申报'])
if not result['recent_filings']:
    lines.append('submissions 未成功获取/解析，无法诚实提供本次实测的申报条目、记录数及日期范围；未使用旧数据补齐。')
for filing in result['recent_filings']:
    lines.extend(['', '- '+filing['filing_date']+' '+filing['form']+'；accession '+filing['accession_number']+'；报告日期 '+filing['report_date'], '  - ['+filing['primary_document']+']('+filing['url']+')', '  - 链接生成依据：CIK 去前导零 + accessionNumber 去连字符 + primaryDocument，置于官方 SEC Archives 路径；并非 API 直接返回的完整 URL。', '  - 文档验证：'+json.dumps(filing.get('document_verification', '未请求'), ensure_ascii=False)])
lines.extend(['', '## 边界与证据', '', '- edgartools 未安装、SDK 未测，仅实测底层 SEC 公开 API。', '- 原始响应和响应头分别存于 raw 中各自全新独立子目录；自写脚本在 scripts。', '- 物理行数不代表 JSON 记录数；统计口径以 result.json 为准。', '- 如请求被拒绝，记录实际 HTTP 和退出码，不将环境访问失败认定为产品缺陷。', '- 详细命令、版本、HTTP、耗时、响应哈希和绝对路径见 result.json。'])
(ROOT/'result.md').write_text('\n'.join(lines)+'\n')
print('RESULT '+str(ROOT/'result.json'), flush=True)
sys.exit(result['script_exit_code'])
