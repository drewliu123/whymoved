"""Prepare a bounded recheck of an existing research run, preserving evidence dates."""
import json
from pathlib import Path
from datetime import datetime, timezone

work = Path(__file__).parent
baseline = json.loads((work / 'baseline-show.json').read_text())
now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
parent = baseline['manifest']['run_id']
reason = ('本轮重读Reuters收盘稿的指数及NVDA跌幅归属，并核对Amazon官方TTM现金流表；'
          '关键数值与原证据一致。定向搜索未找到在既定窗口内足以改变判断的新证据。'
          '本次为有限复核，未重新抓取全部社区或补齐阶段行业回报、订单及回款资料；不声称这些信号没有变化。')

def save(name, data):
    (work / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

for key in ('report', 'claims', 'sources', 'plan', 'calculations'):
    doc = baseline[key]
    doc['as_of'] = now
    if key == 'report':
        doc['title'] = '英伟达下跌复核：关键证据一致，当前判断未变'
        doc['findings'] = []
        doc['no_change_reason'] = reason
        doc['update'] = {'judgment_changed': False, 'reason': reason,
                         'comparability': {'status': 'comparable', 'reason': '沿用同一市场窗口、价格比较、单位及来源范围；本轮不增加新的交易日。'}}
    elif key == 'plan':
        doc['parent_run_id'] = parent
        doc['prior_judgment'] = baseline['report']['answer']['text']
        doc['queries'] = [
            {'query': 'Nvidia NVDA October 30 2026 stock fall Amazon Intel Reuters 4.2 7.2',
             'question': '原归因和同日比较是否出现影响判断的新证据',
             'purpose': '对同一窗口做定向复核', 'source': 'WebSearch', 'window': '2026-10-02/2026-11-01'},
            {'query': '重读既有Reuters完整收盘稿及Amazon官方现金流表',
             'question': '百分比主语、收盘语境和TTM数据是否与原账本一致',
             'purpose': '来源语义与口径复核', 'source': 'WebFetch', 'window': '2026-10-30报道及2026-10-29财报'}]
        doc['stop_condition'] = '完成两处关键来源及一次定向搜索；没有实质冲突则记录判断未变，不扩大到全市场重新检索'
    save(key + '.json', doc)

save('recheck-evidence.json', {
    'captured_at': now, 'capture_note': '工具输出接收与记录时刻，不冒充HTTP响应时间',
    'websearch': {'query': 'Nvidia NVDA October 30 2026 stock fall Amazon Intel Reuters 4.2 7.2',
                  'selected': ['https://www.investing.com/news/stock-market-news/nasdaq-futures-tumble-as-amazon-intel-results-deepen-ai-spending-woes-4986163'],
                  'selection_reason': '同一Reuters收盘稿可直接解决原有百分比归属疑问；其他结果不作为新增独立证据，未读取内容不入主张'},
    'reuters': {'url': 'https://www.investing.com/news/stock-market-news/nasdaq-futures-tumble-as-amazon-intel-results-deepen-ai-spending-woes-4986163',
                'status': 'read', 'reported_published': '2026-10-30 04:47', 'reported_updated': '2026-10-30 20:42',
                'timezone': 'not stated in returned output',
                'extract': '收盘稿中Nasdaq跌747.73点、2.86%；英伟达跌4.2%，芯片行业指数跌7.2%；后两句位于收盘语境，未各自再次写明close。记者将抛售联系到Intel、Amazon季报及AI支出回报担忧。',
                'source_ids': ['S6', 'S7']},
    'amazon': {'url': 'https://ir.aboutamazon.com/news-release/news-release-details/2026/Amazon-com-Announces-Third-Quarter-Results/default.aspx',
               'status': 'read', 'published': '2026-10-29',
               'locator': 'Supplemental Financial Information and Business Metrics第一张表，TTM至9月30日，USD millions',
               'extract': {'2026': {'operating_cash_flow': 168300, 'net_ppe_purchases': 210657, 'free_cash_flow': -42357},
                           '2025': {'operating_cash_flow': 130691, 'net_ppe_purchases': 115903, 'free_cash_flow': 14788}},
               'interpretation_limit': 'AI说明针对资本购买支出增量；不是将全部支出归于AI，也不是Q3单季数据。',
               'source_ids': ['S12', 'S15']}})

save('audit.json', {
    'schema_version': 2, 'parent_run': parent,
    'scope': '同一研究窗口的有限复核；没有新研究发现，判断未变',
    'timestamp_note': 'UTC冻结时间可能显示11月2日，新闻及市场范围仍截至美国东部11月1日；未扩充为11月2日研究',
    'queries': [{'query': 'Nvidia NVDA October 30 2026 stock fall Amazon Intel Reuters 4.2 7.2', 'tool': 'WebSearch', 'status': 'ok'},
                {'query': '既有Reuters与Amazon原URL', 'tool': 'WebFetch', 'status': 'ok', 'calls': 2}],
    'evidence': 'recheck-evidence.json',
    'reuse': '继承父run完整来源、21条主张和6项计算；未重新抓取Last30Days，来源原retrieved_at及主张原as_of均保留',
    'no_change_reason': reason,
    'review': {'status': 'pending focused review', 'prior_review': '父run审查意见及处置见父run audit.json；本轮未变更经济推断'},
    'execution': {'archive_result': 'update-result.json', 'validation_log': 'validation.json',
                  'tests': '研究输入与引用校验；未运行应用单元、集成或E2E测试'}})
print(json.dumps({'work': str(work), 'as_of': now, 'parent_run': parent}, ensure_ascii=False))
