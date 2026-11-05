"""Build the evaluation question set: resolved after model cutoff, one per event, as-of market price."""
import json, random, sys, time, urllib.parse, urllib.request, concurrent.futures
from datetime import datetime, timezone, timedelta

CUTOFF = datetime(2026, 7, 3, tzinfo=timezone.utc)
LEAD_DAYS = 14

def get(u):
    r = urllib.request.Request(u, headers={'User-Agent': 'touyan-eval'})
    return json.load(urllib.request.urlopen(r, timeout=40))

def as_of_price(c):
    closed = datetime.fromisoformat(c['closed'] + 'T00:00:00+00:00')
    as_of = max(closed - timedelta(days=LEAD_DAYS), CUTOFF)
    if (closed - as_of).days < 5:
        return None
    try:
        h = get('https://clob.polymarket.com/prices-history?' + urllib.parse.urlencode({'market': c['token'], 'interval': 'max', 'fidelity': 720}))['history']
    except Exception:
        return None
    before = [x for x in h if x['t'] <= as_of.timestamp()]
    if not before or as_of.timestamp() - before[-1]['t'] > 3 * 86400:
        return None
    return {**c, 'as_of': as_of.strftime('%Y-%m-%dT%H:%M:%SZ'), 'p_market': before[-1]['p']}

cands = json.load(open(sys.argv[1]))
with concurrent.futures.ThreadPoolExecutor(8) as pool:
    rows = [r for r in pool.map(as_of_price, cands) if r]
rows = [r for r in rows if 0.05 <= r['p_market'] <= 0.95]
rng = random.Random(20261030)
by_event = {}
for r in rows:
    by_event.setdefault(r['event_id'] or r['id'], []).append(r)
picked = [rng.choice(sorted(v, key=lambda x: x['id'])) for k, v in sorted(by_event.items(), key=lambda kv: str(kv[0]))]
rng.shuffle(picked)
for i, r in enumerate(picked):
    r['qid'] = f'Q{i+1:03d}'
json.dump(picked, open(sys.argv[2], 'w'), ensure_ascii=False, indent=1)
print('eligible', len(rows), 'events', len(picked), 'yes rate', round(sum(r['yes'] for r in picked) / len(picked), 3))
mb = sum((r['p_market'] - r['yes']) ** 2 for r in picked) / len(picked)
print('market brier at as_of', round(mb, 4))
for r in picked[:80]:
    print(r['qid'], r['as_of'][:10], r['closed'], r['yes'], round(r['p_market'], 3), r['q'][:90])
