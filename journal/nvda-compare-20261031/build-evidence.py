import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent
AS_OF = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
QUESTION = '截至研究截面，英伟达（NVDA）下一次财报前的市场预期是什么，关键分歧和证伪条件有哪些？'
IR = 'https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Announces-Financial-Results-for-Second-Quarter-Fiscal-2027/'
CALL = 'https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Sets-Conference-Call-for-Third-Quarter-Financial-Results/default.aspx'
QUOTE = 'https://investor.nvidia.com/stock-info/stock-quote-and-chart/default.aspx'
ZACKS = json.loads((ROOT / 'zacks-estimates.json').read_text())['url']
MARGIN = 'https://polymarket.com/event/nvidia-nvda-q3-adjusted-gross-margin-non-gaap-20261008120136000'
DC = 'https://polymarket.com/event/will-nvidia-nvda-q3-data-center-revenue-be-above-20261008120135000'
BOOK = json.loads((ROOT / 'margin-orderbook.json').read_text())


def source(url, publisher, tier, published_at):
    return dict(url=url, publisher=publisher, tier=tier, published_at=published_at)


def claim(cid, text, ctype, sources=None, basis=None):
    c = dict(id=cid, text=text, type=ctype, as_of=AS_OF, sources=sources or [])
    if basis:
        c['basis'] = basis
    return c


ir = source(IR, 'NVIDIA IR', 'T0', '2026-08-26')
z = source(ZACKS, 'Zacks', 'T1', '2026-10-30')
claims = [
    claim('C1', 'NVIDIA 2026-08-26公布截至2026-07-26的Q2 FY2027：总收入962.21亿美元，数据中心收入890亿美元；non-GAAP毛利率75.0%。', 'fact', [ir]),
    claim('C2', '公司对Q3 FY2027总收入指引为1080亿美元±2%，non-GAAP毛利率指引74.0%±50基点；指引不假设中国Data Center compute收入。', 'fact', [ir]),
    claim('C3', '公司2026-10-28公告：截至2026-10-25的Q3 FY2027业绩将于2026-11-17约13:20 PT公布，电话会14:00 PT/17:00 ET。', 'fact', [source(CALL, 'NVIDIA IR', 'T0', '2026-10-28')]),
    claim('C4', '官方IR行情页标注2026-10-30 4:00 PM：NVDA为204.64美元，前收213.66美元，变动-9.02美元/-4.22%；页面说明报价延迟20分钟，未明确该时间标记的时区。', 'price', [source(QUOTE, 'NVIDIA IR / quote feed', 'T0', '2026-10-30')]),
    claim('C5', 'Zacks 2026-10-30汇总的当季收入预期为1089.9亿美元，当季EPS预期2.49美元，后者30天上调1%；本次未取得样本人数与EPS完整调整口径。', 'consensus', [z]),
    claim('C6', 'Zacks 2026-10-30称，过去四季NVIDIA均超过其收入和EPS估计；上季收入962.2亿美元相对其918亿美元估计高4.82%，上季EPS为2.22美元。', 'consensus', [z]),
    claim('C7', 'Zacks收入预期比公司指引中值高9.9亿美元，约0.92%，仍在公司1058.4亿至1101.6亿美元指引区间内；超过公司中值不等于超过该预期。', 'inference', basis=['C2', 'C5']),
    claim('C8', '2026-10-31T05:03:55Z抓取的Polymarket数据中心收入阈值显示：>950亿美元为70%，>1000亿美元为88%；前者bid/ask为43¢/97¢，后者78¢/98¢。', 'price', [source(DC, 'Polymarket Gamma', 'T0', '2026-10-31T05:03:55Z')]),
    claim('C9', '2026-10-31T05:03:57Z毛利率73%至75%合约显示77.5%；05:04:28Z的CLOB订单簿最高买价73¢/20.1份、最低卖价82¢/20份；这是历史抓取报价，不保证随后仍可成交。', 'price', [source(MARGIN, 'Polymarket', 'T0', '2026-10-31T05:03:57Z'), source(BOOK['url'], 'Polymarket CLOB', 'T0', '2026-10-31T05:04:28Z')]),
    claim('C10', '毛利率合约按Q3官方最精确non-GAAP毛利率裁决，73%包含、75%不包含；如报区间取中点，缺指标或截至2026-12-31 23:59 ET未发布材料则归最低档，后续修订不计。', 'fact', [source(MARGIN, 'Polymarket rules', 'T0', '2026-10-31T05:03:57Z')]),
    claim('C11', '收入阈值显示值违背嵌套事件应有的单调关系，且价差很大，不宜拟合可靠收入分布；毛利率77.5%显示值也不能当作可直接成交价。', 'inference', basis=['C8', 'C9']),
    claim('C12', '公司毛利率指引区间73.5%至74.5%落在73%含至75%不含的合约区间内；指引与合约方向相容，但指引不是已实现毛利率。', 'inference', basis=['C2', 'C10']),
]
community = json.loads((ROOT / 'community.json').read_text())
for cid, idx, text in [
    ('C13', 0, 'r/stocks作者soukstah质疑下游AI软件收入能否覆盖资本投入所需回报；这是个人观点，帖子约844分/566评论，互动量为抓取或归档值。'),
    ('C14', 3, 'r/NVDA_Stock作者KeyTrainingk看好业务，但不认为盈利增长自动意味着股票便宜；帖子约40分/93评论，互动量为抓取或归档值。'),
    ('C15', 2, 'r/stocks作者Wonderful-Sail-1126认为不同模型路线均需要硬件，借租价叙事推断需求韧性；帖子约237分/165评论，租价数据未作基本面核验。'),
]:
    post = community['posts'][idx]
    claims.append(claim(cid, text, 'view', [source(post['url'], 'Reddit u/' + post['author'], 'T4', post['published_at'])]))
claims.extend([
    claim('C16', '这组资料能支持对收入兑现与毛利率区间的观察，不能单独推出财报后股价上涨概率或股票便宜；价格反应还需要预期门槛和估值证据。', 'inference', basis=['C2', 'C4', 'C5', 'C14']),
    claim('C17', '最强反方是即使当季增长兑现，客户回报和后续增长仍可能不足以支撑估值；这里将其作为研究风险，未把社区质疑当成已证实的融资或需求恶化。', 'inference', basis=['C5', 'C13', 'C14', 'C15']),
    claim('C18', '公司总收入指引区间同时覆盖1089.9亿美元预期的两侧；过去四季超出Zacks预期为有限样本，无法单独确立本季超预期概率。', 'inference', basis=['C2', 'C5', 'C6']),
])
ledger = dict(question=QUESTION, as_of=AS_OF, claims=claims)
(ROOT / 'claims.json').write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + '\n')
plan = json.loads((ROOT / 'plan.json').read_text())
plan.update(as_of=AS_OF, horizon='2026-11-17 Q3 FY2027财报；合约最晚裁决材料截止2026-12-31 23:59 ET', gaps=[
    '未取得带时点和到期日的期权隐含波幅、空头持仓和标准forward PE。',
    'Zacks样本人数与EPS完整调整口径未取得，不代表所有参与者。',
    'X未配置可用后端；Reddit部分超时，仅保留5个线程，不能量化多空比例。',
    '未找到已核实、与总收入超过1089.9亿美元完全匹配的可成交合约；一次补搜SSL失败，不证明市场不存在。',
    '盘口为05:03至05:04 UTC的历史快照，与冻结结束并非完全同时。',
    '未取得可核实的一线媒体最新反方原文、10月Rubin收入或Blackwell独立收入。',
])
(ROOT / 'plan.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n')
contract = dict(hypothesis_id='H2', mode='independent',
    question='截至2026-12-31 23:59 ET首次公布的NVIDIA Q3 FY2027总收入是否严格超过1089.9亿美元？',
    yes_means='窗口内首次发布的Q3 FY2027官方财报总收入严格大于108.99 billion USD。等于阈值为NO；截止前未发布或未披露该指标为NO；采用首次材料最精确数值，不计后续修订。',
    window_start=AS_OF, window_end='2027-01-01T04:59:00Z',
    resolution_source=IR + '；以NVIDIA IR该季度首次业绩新闻稿或首次监管财报总收入为准，11月17为计划披露日，12月31 23:59 ET为截止。',
    evidence_ids=['C1', 'C2', 'C3', 'C5', 'C6'])
input_doc = dict(as_of=AS_OF, contract=contract,
    evidence=[c for c in claims if c['id'] in contract['evidence_ids']])
(ROOT / 'forecast-input-H2.json').write_text(json.dumps(input_doc, ensure_ascii=False, indent=2) + '\n')
print('Evidence frozen:', AS_OF, 'claims:', len(claims))
