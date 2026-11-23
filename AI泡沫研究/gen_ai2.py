"""AI 泡沫研究报告 · v2（单季口径，2026-11-22）"""
import json, os, datetime

FIN = json.load(open('fin_summary.json', encoding='utf-8'))
TR  = json.load(open('trend.json', encoding='utf-8'))
Q   = json.load(open('quarterly.json', encoding='utf-8'))
ORDER = ['NVDA','MSFT','GOOGL','AMZN','META','AAPL','AVGO','AMD','ORCL','PLTR','CRM']

PRICE = {
 'NVDA':dict(p=125.53,dp=-14.01,dd=-48.4),'MSFT':dict(p=484.52,dp=-2.77,dd=-13.3),
 'GOOGL':dict(p=265.29,dp=-2.70,dd=-35.1),'AMZN':dict(p=246.82,dp=-4.10,dd=-14.1),
 'META':dict(p=560.84,dp=-5.93,dd=-28.1),'AAPL':dict(p=342.56,dp=-1.90,dd=-5.1),
 'AVGO':dict(p=304.41,dp=-12.19,dd=-38.5),'AMD':dict(p=424.39,dp=-13.25,dd=-35.6),
 'ORCL':dict(p=101.19,dp=-8.48,dd=-59.6),'PLTR':dict(p=143.49,dp=-6.63,dd=-32.6),
 'CRM':dict(p=None,dp=None,dd=None),
}
def load_metric(s):
    for base in ['/tmp/ai_data', '.']:
        p = f'{base}/{s}_m.json'
        if os.path.exists(p):
            try: return json.load(open(p))['metric']
            except Exception: pass
    return {}
METRIC = {s: load_metric(s) for s in ORDER}

def B(x, d=1):
    if x is None: return '—'
    if abs(x) >= 1e12: return f'{x/1e12:.{d}f}万亿'
    return f'{x/1e9:.{d}f}B'

# ═══ 表1：最新单季横向对比 ═══
latest_rows = []
for s in ORDER:
    qq = Q.get(s, {}).get('quarters') or []
    if not qq: continue
    x = qq[-1]
    fcf = (x['ocf'] - x['capex']) if None not in (x['ocf'], x['capex']) else None
    cr = (x['capex']/x['rev']*100) if x.get('capex') and x.get('rev') else None
    cr_col = '#b91c1c' if (cr and cr > 40) else ('#b45309' if (cr and cr > 20) else '#15803d')
    fcf_col = '#15803d' if (fcf is not None and fcf < 0) else '#111'
    nm = Q[s]['name']
    latest_rows.append(
        f'<tr><td><b>{nm}</b><br><span class="sym">{s}</span></td>'
        f'<td class="n">{x["ed"]}</td><td class="n">{x["days"]}天</td>'
        f'<td class="n">{B(x["rev"])}</td>'
        f'<td class="n" style="color:{cr_col};font-weight:600">{f"{cr:.1f}%" if cr else "—"}</td>'
        f'<td class="n" style="color:{fcf_col};font-weight:600">{B(fcf) if fcf is not None else "—"}</td>'
        f'</tr>')
latest_rows = '\n'.join(latest_rows)

# ═══ 表2：同季度纵向（每人取最近5个同季）═══
seq_rows = []
for s in ['ORCL','MSFT','GOOGL','AMZN','META','NVDA','AVGO','AAPL']:
    qq = [x for x in (Q.get(s,{}).get('quarters') or []) if x.get('capex')]
    if len(qq) < 2: continue
    nm = Q[s]['name']
    cells = []
    for x in qq[-5:]:
        cr = x['capex']/x['rev']*100
        c = '#b91c1c' if cr > 40 else ('#b45309' if cr > 20 else '#15803d')
        cells.append(f'<td class="n" style="color:{c}">{cr:.1f}%</td>')
    while len(cells) < 5: cells.append('<td class="n">—</td>')
    first = qq[-5]['capex']/qq[-5]['rev']*100 if len(qq)>=5 else qq[0]['capex']/qq[0]['rev']*100
    last = qq[-1]['capex']/qq[-1]['rev']*100
    dc = '#b91c1c' if last > first else '#15803d'
    dates = '　'.join(x['ed'][:7] for x in qq[-5:])
    seq_rows.append(f'<tr><td><b>{nm}</b><br><span class="sym">{dates}</span></td>{"".join(cells)}'
                    f'<td class="n" style="font-weight:700;color:{dc}">{last-first:+.1f}pp</td></tr>')
seq_rows = '\n'.join(seq_rows)

# ═══ 表3：年报口径（保留） ═══
ann_rows = []
for s in ORDER:
    f = FIN.get(s); m = METRIC.get(s) or {}; p = PRICE.get(s) or {}
    if not f: continue
    fcf = f.get('fcf'); cr = f.get('capex_ratio')
    fcf_col = '#15803d' if (fcf is not None and fcf < 0) else '#111'
    cr_col = '#b91c1c' if (cr and cr > 30) else ('#b45309' if (cr and cr > 15) else '#15803d')
    pe = m.get('peTTM'); pe_s = f'{pe:.1f}' if isinstance(pe,(int,float)) else '—'
    dp = p.get('dp'); dd = p.get('dd')
    dp_s = f'{dp:+.2f}%' if dp is not None else '—'
    dd_s = f'{dd:+.1f}%' if dd is not None else '—'
    dp_col = '#dc2626' if (dp or 0) > 0 else '#15803d'
    dd_col = '#b91c1c' if (dd or 0) < -30 else '#b45309'
    p_s = f'{p["p"]}' if p.get('p') else '未取到'
    ann_rows.append(
        f'<tr><td><b>{f["name"]}</b> <span class="sym">{s}</span></td>'
        f'<td class="n">{p_s}</td><td class="n" style="color:{dp_col}">{dp_s}</td>'
        f'<td class="n" style="color:{dd_col};font-weight:600">{dd_s}</td>'
        f'<td class="n">{B(f.get("revenue"))}</td>'
        f'<td class="n" style="color:{cr_col}">{f"{cr:.1f}%" if cr else "—"}</td>'
        f'<td class="n" style="color:{fcf_col}">{B(fcf) if fcf is not None else "—"}</td>'
        f'<td class="n">{pe_s}</td></tr>')
ann_rows = '\n'.join(ann_rows)

tot_cap = sum(f['capex'] for f in FIN.values() if f.get('capex'))
tot_fcf = sum(f['fcf'] for f in FIN.values() if f.get('fcf') is not None)
CSS = open('style.css', encoding='utf-8').read()

HTML = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>美股 AI 公司收支与泡沫研究 · 2026-11-22（单季口径）</title>
<style>{CSS}</style></head><body><div class="page">

<header>
<h1>美股 AI 公司收支与泡沫研究</h1>
<div class="meta">
<b>生成日期</b> {datetime.datetime.now():%Y-%m-%d %H:%M}　<b>行情</b> 2026-11-20 收盘　<b>财报</b> 年报 10-K + 单季 10-Q<br>
<b>数据源</b> Finnhub（XBRL 原始申报）　<b>覆盖</b> 11 家美股 AI 核心公司 / <b>162 个真单季</b><br>
<b>本版变更</b> 采用<b>单季口径</b>（更灵敏），年报作为对照保留
</div>
</header>

<div class="note">
<b>📌 本版说明：为什么改用单季口径</b><br>
上一版用年报（10-K），但年报只能看到年度平均，<b>掩盖了季内的急剧变化</b>。<br>
本版实测发现：Finnhub 季报接口的 <code>startDate</code> 是财年起点而非季度起点，
原始数据是<b>财年内累计值</b>。经校验，直接筛选<b>期间 80–100 天的记录</b>即为真单季，
无需减算（避免传递误差）。共提取 <b>162 个真单季</b>，最新至 2026-09-30。<br>
<b>关键改善</b>：甲骨文单季 Capex 率已达 <b>147.3%</b>，年报口径（82.6%）严重低估了当前强度。
</div>

<h2>一、最新单季：Capex 率与自由现金流</h2>
<div class="card">
<table>
<tr><th>公司</th><th class="n">季度截止</th><th class="n">期间</th><th class="n">单季营收</th>
<th class="n">单季 Capex率</th><th class="n">单季自由现金流</th></tr>
{latest_rows}
</table>
<p style="font-size:12.5px;color:#6b7280;margin-bottom:0">
只采用期间 80–100 天的记录（真单季）。Capex率 = 单季资本开支 ÷ 单季营收。
<span style="color:#b91c1c">红</span> &gt;40%｜<span style="color:#b45309">橙</span> 20-40%｜<span style="color:#15803d">绿</span> &lt;20%。
</p>
</div>

<h2>二、单季 Capex 率五年演变（最关键证据）</h2>
<div class="card">
<table>
<tr><th>公司 / 季度</th><th class="n">序列（早→晚）</th><th class="n">变化</th></tr>
{seq_rows}
</table>
<div class="warn">
<b>单季数据揭示的三个事实</b><br>
· <b>甲骨文</b>：单季 Capex 率从 10.6% 飙升至 <b>147.3%</b> —— 单季资本开支已超过营收本身<br>
· <b>微软</b>：17.5% → <b>42.7%</b>，单季 Capex 率突破 40%<br>
· <b>谷歌</b>：9.0% → <b>32.5%</b>；<b>Meta</b>：19.5% → <b>33.7%</b><br>
· <b>亚马逊</b>：单季自由现金流连续为负（2026 Q1 <b>−18.17B</b>）<br>
· <b>英伟达/苹果/博通/AMD</b>：始终低于 4%，是「卖铲子」而非「建机房」
</div>
</div>

<h2>三、年报口径对照（10-K 完整数据）</h2>
<div class="card">
<table>
<tr><th>公司</th><th class="n">股价</th><th class="n">当日</th><th class="n">距52周高</th>
<th class="n">年营收</th><th class="n">Capex率</th><th class="n">自由现金流</th><th class="n">PE</th></tr>
{ann_rows}
</table>
<p style="font-size:12.5px;color:#6b7280;margin-bottom:0">
年报 10 家合计资本开支 <b>{tot_cap/1e9:.0f}B</b>，合计自由现金流 <b>+{tot_fcf/1e9:.0f}B</b>。
Salesforce（CRM）行情与财务指标接口未返回，仅保留单季数据。
</p>
</div>

<h2>四、泡沫判断：数据正反两面</h2>

<div class="ok">
<b>✅ 支持「整体不是烧钱式泡沫」</b>
<ul>
<li><b>龙头盈利极强</b>：英伟达单季营收 81.61B、FCF <b>+48.59B</b>，Capex 率仅 2.2%</li>
<li><b>苹果/博通现金牛</b>：单季 FCF 51.55B / 8.01B，Capex 率不足 2%</li>
<li><b>年报层面 FCF 整体为正</b>：10 家合计 <b>+{tot_fcf/1e9:.0f}B</b></li>
<li><b>估值不极端</b>：英伟达 PE 13.4、谷歌 13.8、Meta 19.1，远低于 2000 年泡沫的 60-100 倍</li>
<li><b>研发真实</b>：微软 R&D 35.6B、苹果 45.8B，非财务工程</li>
</ul>
</div>

<div class="warn">
<b>⚠️ 支持「存在泡沫成分」</b>
<ul>
<li><b>甲骨文单季 Capex 率达 147.3%</b>：花得比赚得多，单季 FCF <b>−5.40B</b></li>
<li><b>微软单季 Capex 率 42.7%</b>，但单季 FCF 从 25.66B 降至 18.63B（<b>−27%</b>）</li>
<li><b>亚马逊单季 FCF 连续为负</b>：2022 −17.74B → 2026 −18.17B，扩张未停</li>
<li><b>四家超大规模厂商（微软/谷歌/亚马逊/Meta）单季 Capex 率均在 24-43%</b></li>
<li><b>折旧压力尚未兑现</b>：当前 Capex 将转为未来 3-5 年折旧</li>
<li><b>股价已定价风险</b>：甲骨文 −59.6%、英伟达 −48.4%（单日 −14.01%）</li>
</ul>
</div>

<h2>五、口径说明与数据质量</h2>
<div class="card">

<h3>① 单季 vs 年报：哪个更准确</h3>
<p><b>两者都准确，但回答不同问题</b>：</p>
<ul>
<li><b>年报（10-K）</b>：经审计、字段最全、跨公司可比。适合判断<b>长期趋势</b></li>
<li><b>单季（10-Q）</b>：未经年度审计，但能捕捉<b>季内拐点</b>。适合判断<b>当下强度</b></li>
</ul>
<p style="margin-bottom:0">本版<b>以单季为主、年报对照</b>。若两者冲突，说明趋势正在加速或减速——这本身是重要信息。</p>

<h3>② 实战踩坑记录（4 个）</h3>
<ul>
<li><b>季报 startDate 是财年起点</b>，不是季度起点。微软的「Q2」期间是 183 天（半年累计）</li>
<li><b>不能靠 startDate 分组</b>：同一财年不同季度 startDate 相同，会把 3 个季度算成 1 个</li>
<li><b>正确做法</b>：按 <code>endDate − startDate</code> 的天数筛，80-100 天为真单季</li>
<li><b>字段名逐年变化</b>：亚马逊 2026 年把 <code>Total net sales</code> 改为 <code>Net sales</code>，导致匹配失败</li>
</ul>

<h3>③ 已知缺口</h3>
<ul>
<li><b>资产负债表（bs）为空</b>：微软、苹果、甲骨文的 10-K/10-Q 均返回 bs=0，无法计算资产负债率</li>
<li><b>Salesforce（CRM）</b>：报价与 metric 接口未返回，仅有单季财务</li>
<li><b>自由现金流为计算值</b>：FCF = 经营现金流 − 资本开支，<b>未扣股权激励（SBC）</b></li>
<li><b>季报无 Q4</b>：10-Q 只含 Q1~Q3，Q4 需从 10-K 全年减算</li>
</ul>
</div>

<h2>六、数据来源与可复算</h2>
<div class="card">
<table>
<tr><th>数据</th><th>接口</th><th>参数</th><th>可复算</th></tr>
<tr><td>年报（10-K）</td><td><code>/stock/financials-reported</code></td><td><code>symbol=X</code></td><td>✅</td></tr>
<tr><td>季报（10-Q）</td><td><code>/stock/financials-reported</code></td><td><code>symbol=X&amp;freq=quarterly</code></td><td>✅</td></tr>
<tr><td>财务指标</td><td><code>/stock/metric</code></td><td><code>symbol=X&amp;metric=all</code></td><td>✅</td></tr>
<tr><td>股价</td><td><code>/quote</code> + 腾讯双源</td><td><code>symbol=X</code></td><td>✅</td></tr>
</table>
<p style="font-size:12.5px;color:#6b7280;margin-bottom:0">
原始数据：<code>quarterly.json</code>（162 季）、<code>fin_summary.json</code>（年报）、<code>trend.json</code>
</p>
</div>

<p style="margin-top:38px;padding-top:16px;border-top:1px solid #e3e5e7;font-size:12.5px;color:#9ca3af;line-height:1.8">
⚠️ 本报告只列财务事实、口径说明与历史趋势，<b>不构成投资建议，也不对「是否泡沫」给出预测性结论</b>。
所有数字来自 Finnhub 公开接口（SEC XBRL），可复算；若与公司原始 10-K/10-Q 有差异，以原始申报为准。
</p>

</div></body></html>'''

open('AI泡沫研究报告-2026-11-22.html','w',encoding='utf-8').write(HTML)
print(f'  ✓ 已生成 {os.path.getsize("AI泡沫研究报告-2026-11-22.html"):,} B')
print(f'  ✓ 单季表 {len(latest_rows.splitlines())} 行 / 序列表 {len(seq_rows.splitlines())} 行 / 年报表 {len(ann_rows.splitlines())} 行')
