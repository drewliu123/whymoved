import json, math, datetime as dt, statistics as st
from pathlib import Path
R = Path(__file__).resolve().parent / "raw10"
def load(s):
    r = json.load(open(R / f"y_{s}.json"))["chart"]["result"][0]
    out = {dt.datetime.utcfromtimestamp(t).date().isoformat(): x for t, x in zip(r["timestamp"], r["indicators"]["quote"][0]["close"]) if x}
    return out, r["meta"]
g, gm = load("GC=F"); s, sm = load("SI=F")
d = sorted(k for k in g if k in s)
G = [g[k] for k in d]; S = [s[k] for k in d]
print("range", d[0], d[-1], len(d), "last meta", gm["regularMarketPrice"], sm["regularMarketPrice"])
lr = [math.log(G[i] / S[i]) for i in range(len(d))]
rg = [0] + [math.log(G[i] / G[i-1]) for i in range(1, len(d))]
rs = [0] + [math.log(S[i] / S[i-1]) for i in range(1, len(d))]
def corr(a, b):
    ma, mb = st.fmean(a), st.fmean(b)
    num = sum((x-ma)*(y-mb) for x, y in zip(a, b)); den = math.sqrt(sum((x-ma)**2 for x in a)*sum((y-mb)**2 for y in b))
    return num/den if den else float('nan')
def beta(y, x):
    mx, my = st.fmean(x), st.fmean(y)
    return sum((a-mx)*(b-my) for a, b in zip(x, y)) / sum((a-mx)**2 for a in x)
W = 60
ratio = [G[i]/S[i] for i in range(len(d))]
print("\n== 金银比 ==")
srt = sorted(ratio)
cur = ratio[-1]
print("now %.1f  10y pct %.0f%%  min %.1f(%s) max %.1f(%s)" % (cur, 100*sum(r <= cur for r in ratio)/len(ratio), min(ratio), d[ratio.index(min(ratio))], max(ratio), d[ratio.index(max(ratio))]))
for k in ["2025-11-04", "2026-01-26", "2026-01-29", "2026-04-01", "2026-07-01", "2026-09-03", "2026-10-01", "2026-10-30"]:
    kk = max(x for x in d if x <= k); i = d.index(kk); print(kk, "G %.0f S %.2f ratio %.1f" % (G[i], S[i], ratio[i]))
c60 = [None]*len(d); b60 = [None]*len(d)
for i in range(W, len(d)):
    c60[i] = corr(rg[i-W+1:i+1], rs[i-W+1:i+1]); b60[i] = beta(rs[i-W+1:i+1], rg[i-W+1:i+1])
cv = [x for x in c60 if x is not None]
print("\n== 60日相关/贝塔 ==")
print("corr now %.2f  10y median %.2f  p10 %.2f  p90 %.2f" % (c60[-1], st.median(cv), sorted(cv)[len(cv)//10], sorted(cv)[9*len(cv)//10]))
print("beta now %.2f  10y median %.2f" % (b60[-1], st.median([x for x in b60 if x])))
for k in ["2025-12-31", "2026-02-27", "2026-04-30", "2026-06-30", "2026-08-31", "2026-09-30", "2026-10-15"]:
    kk = max(x for x in d if x <= k); i = d.index(kk); print(kk, "corr %.2f beta %.2f" % (c60[i], b60[i]))
# 上涨/下跌日不对称贝塔（近一年、过去10年）
def asym(lo):
    idx = [i for i in range(1, len(d)) if d[i] >= lo]
    up = [i for i in idx if rg[i] > 0]; dn = [i for i in idx if rg[i] < 0]
    bu = sum(rs[i]*rg[i] for i in up)/sum(rg[i]**2 for i in up); bd = sum(rs[i]*rg[i] for i in dn)/sum(rg[i]**2 for i in dn)
    return bu, bd
print("asym beta 10y up/down %.2f/%.2f ; since 2025-11 %.2f/%.2f ; since 2026-04 %.2f/%.2f" % (*asym(d[0]), *asym("2025-11-04"), *asym("2026-04-01")))
# 白银独立走势：用前60日贝塔剥离黄金后的残差，20日累计
res = [None]*len(d)
for i in range(W+1, len(d)):
    res[i] = rs[i] - b60[i-1]*rg[i]
cum20 = [None]*len(d)
for i in range(W+21, len(d)):
    cum20[i] = sum(res[i-19:i+1])
cvv = [x for x in cum20 if x is not None]; sd = st.pstdev(cvv)
print("\n== 白银20日独立残差 ==  now %.1f%%  z %.2f" % (100*cum20[-1], cum20[-1]/sd))
for k in ["2026-01-26", "2026-02-27", "2026-04-01", "2026-09-09", "2026-10-30"]:
    kk = max(x for x in d if x <= k); i = d.index(kk); print(kk, "res20 %.1f%% z %.2f" % (100*cum20[i], cum20[i]/sd))
# 回测1：金银比z（相对250日均值）极端后，未来20/60日金银比变化
def episodes(cond, gap=20):
    out, last = [], -10**9
    for i in range(len(d)):
        if cond(i) and i - last >= gap: out.append(i); last = i
    return out
Lw = 250
zr = [None]*len(d)
for i in range(Lw, len(d)):
    seg = lr[i-Lw:i]; m, sdv = st.fmean(seg), st.pstdev(seg); zr[i] = (lr[i]-m)/sdv
print("\n== 金银比z(250日) now %.2f ==" % zr[-1])
for name, cond in [("比值z>+1.5(银相对便宜)", lambda i: zr[i] is not None and zr[i] > 1.5), ("比值z<-1.5(银相对贵)", lambda i: zr[i] is not None and zr[i] < -1.5)]:
    for h in (20, 60):
        ep = [i for i in episodes(cond) if i+h < len(d)]
        fw = [100*(lr[i+h]-lr[i]) for i in ep]
        if fw:
            hit = sum((f < 0) if "便宜" in name else (f > 0) for f in fw)/len(fw)
            print(name, "h=%d n=%d 比值均变 %+.1f%% 中位 %+.1f%% 回归命中 %.0f%%" % (h, len(fw), st.fmean(fw), st.median(fw), 100*hit))
# 回测2：残差20日z极端后，未来20日残差累计
for name, cond in [("残差z<-1.5(银独立跑输)", lambda i: cum20[i] is not None and cum20[i]/sd < -1.5), ("残差z>+1.5(银独立跑赢)", lambda i: cum20[i] is not None and cum20[i]/sd > 1.5)]:
    for h in (20, 60):
        ep = [i for i in episodes(cond) if i+h < len(d)]
        fw = [100*sum(res[i+1:i+h+1]) for i in ep]
        if fw:
            hit = sum((f > 0) if "跑输" in name else (f < 0) for f in fw)/len(fw)
            print(name, "h=%d n=%d 后续残差均值 %+.1f%% 中位 %+.1f%% 反转命中 %.0f%%" % (h, len(fw), st.fmean(fw), st.median(fw), 100*hit))
# 回测3：相关性跌破0.6后，未来20日金银比绝对变化 vs 平时
for h in (20,):
    low = [i for i in episodes(lambda i: c60[i] is not None and c60[i] < 0.6) if i+h < len(d)]
    allv = [abs(lr[i+h]-lr[i]) for i in range(W, len(d)-h)]
    print("\n相关<0.6 后20日 |比值变化| 均值 %.1f%% (n=%d) vs 全样本 %.1f%%" % (100*st.fmean([abs(lr[i+h]-lr[i]) for i in low]) if low else float('nan'), len(low), 100*st.fmean(allv)))
# 自相关：金银比20日变化与下一个20日变化
ch = [lr[i]-lr[i-20] for i in range(20, len(d)-20, 20)]
print("金银比20日变化一阶自相关(非重叠) %.2f n=%d" % (corr(ch[:-1], ch[1:]), len(ch)-1))
