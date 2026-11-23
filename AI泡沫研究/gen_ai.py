"""AI 泡沫研究报告生成（2026-11-22）"""
import json, os, datetime

FIN = json.load(open('fin_summary.json', encoding='utf-8'))
TR  = json.load(open('trend.json', encoding='utf-8'))
ORDER = ['NVDA','MSFT','GOOGL','AMZN','META','AAPL','AVGO','AMD','ORCL','PLTR']

PRICE = {
 'NVDA':dict(p=125.53,dp=-14.01,dd=-48.4),'MSFT':dict(p=484.52,dp=-2.77,dd=-13.3),
 'GOOGL':dict(p=265.29,dp=-2.70,dd=-35.1),'AMZN':dict(p=246.82,dp=-4.10,dd=-14.1),
 'META':dict(p=560.84,dp=-5.93,dd=-28.1),'AAPL':dict(p=342.56,dp=-1.90,dd=-5.1),
 'AVGO':dict(p=304.41,dp=-12.19,dd=-38.5),'AMD':dict(p=424.39,dp=-13.25,dd=-35.6),
 'ORCL':dict(p=101.19,dp=-8.48,dd=-59.6),'PLTR':dict(p=143.49,dp=-6.63,dd=-32.6),
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
def P(x, d=1):
    return '—' if x is None else f'{x:.{d}f}%'

# ══ 主表：逐行拼接（修 bug：不用内联三元生成整行）══
rows = []
for s in ORDER:
    f = FIN.get(s); m = METRIC.get(s) or {}; p = PRICE.get(s) or {}
    if not f:
        continue
    fcf = f.get('fcf'); cr = f.get('capex_ratio')
    fcf_col = '#15803d' if (fcf is not None and fcf < 0) else '#111'
    cr_col = '#b91c1c' if (cr and cr > 30) else ('#b45309' if (cr and cr > 15) else '#15803d')
    pe = m.get('peTTM'); pe_s = f'{pe:.1f}' if isinstance(pe,(int,float)) else '—'
    rg = m.get('revenueGrowthTTMYoy'); rg_s = P(rg)
    dp = p.get('dp', 0); dd = p.get('dd', 0)
    dp_col = '#dc2626' if dp > 0 else '#15803d'
    dd_col = '#b91c1c' if dd < -30 else '#b45309'
    rows.append(
        f'<tr>'
        f'<td><b>{f["name"]}</b><br><span class="sym">{s}</span></td>'
        f'<td class="n">{p.get("p","—")}</td>'
        f'<td class="n" style="color:{dp_col}">{dp:+.2f}%</td>'
        f'<td class="n" style="color:{dd_col};font-weight:600">{dd:+.1f}%</td>'
        f'<td class="n">{B(f.get("revenue"))}</td>'
        f'<td class="n">{P(f.get("net_margin"))}</td>'
        f'<td class="n">{B(f.get("capex"))}</td>'
        f'<td class="n" style="color:{cr_col};font-weight:600">{P(cr)}</td>'
        f'<td class="n" style="color:{fcf_col};font-weight:600">{B(fcf)}</td>'
        f'<td class="n">{rg_s}</td>'
        f'<td class="n">{pe_s}</td>'
        f'</tr>'
    )
rows = '\n'.join(rows)
print(f'  ✓ 主表 {len([1 for s in ORDER if FIN.get(s)])} 行')

# ══ 趋势表 ══
trows = []
for s in ['MSFT','GOOGL','AMZN','META','ORCL','NVDA']:
    rs = [r for r in TR.get(s, []) if r.get('ratio') is not None]
    if not rs: continue
    name = FIN.get(s, {}).get('name', s)
    cells = []
    for r in rs[-5:]:
        v = r['ratio']
        c = '#b91c1c' if v > 30 else ('#b45309' if v > 15 else '#15803d')
        cells.append(f'<td class="n" style="color:{c}">{v:.1f}%</td>')
    while len(cells) < 5: cells.append('<td class="n">—</td>')
    first = rs[-5]['ratio'] if len(rs) >= 5 else rs[0]['ratio']
    last = rs[-1]['ratio']
    dcol = '#b91c1c' if last > first else '#15803d'
    trows.append(f'<tr><td><b>{name}</b></td>{"".join(cells)}'
                 f'<td class="n" style="font-weight:700;color:{dcol}">{last-first:+.1f}pp</td></tr>')
trows = '\n'.join(trows)
print(f'  ✓ 趋势表 {len(trows.splitlines())} 行')

# ══ 崩跌榜 ══
drops = sorted([(s, PRICE[s]['dd'], PRICE[s]['dp']) for s in PRICE], key=lambda x: x[1])
drows = []
for s, dd, dp in drops:
    nm = FIN.get(s, {}).get('name', s)
    drows.append(f'<tr><td><b>{nm}</b> <span class="sym">{s}</span></td>'
                 f'<td class="n">{PRICE[s]["p"]}</td>'
                 f'<td class="n" style="color:#dc2626">{dp:+.2f}%</td>'
                 f'<td class="n" style="color:#b91c1c;font-weight:600">{dd:+.1f}%</td></tr>')
drows = '\n'.join(drows)

tot_cap = sum(f['capex'] for f in FIN.values() if f.get('capex'))
tot_fcf = sum(f['fcf'] for f in FIN.values() if f.get('fcf') is not None)

CSS = open('style.css', encoding='utf-8').read() if os.path.exists('style.css') else ''

HTML = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>美股 AI 公司收支与泡沫研究 · 2026-11-22</title>
<style>{CSS}</style></head><body><div class="page">

<header>
<h1>美股 AI 公司收支与泡沫研究</h1>
<div class="meta">
<b>生成日期</b> {datetime.datetime.now():%Y-%m-%d %H:%M}　<b>行情日期</b> 2026-11-20 收盘　<b>财报</b> 各公司最近年报（10-K）<br>
<b>数据源</b> Finnhub（财务指标 + XBRL 财报三表 + 报价）　<b>覆盖</b> 10 家美股 AI 核心公司<br>
<b>方法</b> 现金流 vs 资本开支对比 · 历史 Capex/营收趋势 · 价格回撤交叉验证
</div>
</header>

<div class="warn">
<b>一句话结论（基于数据，非预测）</b><br>
从<b>现金流角度，这批公司整体未出现「烧钱维持增长」的典型泡沫特征</b>：
10 家合计资本开支 <b>{tot_cap/1e9:.0f}B</b>，合计自由现金流 <b>+{tot_fcf/1e9:.0f}B</b>，仅甲骨文 1 家 FCF 为负。<br>
但<b>结构性分化极端</b>：甲骨文 Capex 率达 <b>82.6%</b>、FCF <b>−23.7B</b>；微软/Meta Capex 率均超 34% 且快速攀升；
而英伟达/苹果/博通 Capex 率不足 3%。<br>
<b>股价已先行反映风险</b>：甲骨文距 52 周高点 <b>−59.6%</b>，英伟达 <b>−48.4%</b>（单日 −14.01%），博通 −38.5%。
</div>

<div class="big">
  <div><div class="l">10 家合计资本开支</div><div class="v">{tot_cap/1e9:.0f}B</div></div>
  <div><div class="l">10 家合计自由现金流</div><div class="v" style="color:#dc2626">+{tot_fcf/1e9:.0f}B</div></div>
  <div><div class="l">FCF 为负公司</div><div class="v" style="color:#b91c1c">1 / 10</div></div>
  <div><div class="l">Capex 率 &gt;30% 公司</div><div class="v" style="color:#b45309">3 家</div></div>
</div>

<h2>一、核心财务对比（最近年报）</h2>
<div class="card">
<table>
<tr><th>公司</th><th class="n">股价</th><th class="n">当日</th><th class="n">距52周高</th>
<th class="n">营收</th><th class="n">净利率</th><th class="n">资本开支</th><th class="n">Capex率</th>
<th class="n">自由现金流</th><th class="n">营收增速</th><th class="n">PE</th></tr>
{rows}
</table>
<p style="font-size:12.5px;color:#6b7280;margin-bottom:0">
Capex率 = 资本开支 ÷ 营收。<span style="color:#b91c1c">红</span> &gt;30%｜<span style="color:#b45309">橙</span> 15-30%｜<span style="color:#15803d">绿</span> &lt;15%。
自由现金流 = 经营现金流 − 资本开支。
</p>
</div>

<h2>二、Capex/营收 历史趋势（最关键证据）</h2>
<div class="card">
<table>
<tr><th>公司</th><th class="n">近5年序列（早→晚）</th><th class="n">变化</th></tr>
{trows}
</table>
<div class="note">
<b>趋势解读（纯数据）</b><br>
· <b>甲骨文</b>：Capex 率从 37.0% 升至 <b>82.6%</b>（+45.6pp）——每赚 1 元要花 0.83 元买设备<br>
· <b>微软</b>：13.3% → <b>34.9%</b>（+21.6pp），绝对额 28.1B → 115.9B（<b>4.1 倍</b>）<br>
· <b>Meta</b>：20.2% → <b>34.7%</b>（+14.5pp）<br>
· <b>谷歌</b>：10.5% → 22.7%　<b>亚马逊</b>：9.2% → 18.4%<br>
· <b>英伟达</b>：2.5% → 2.8% —— <b>几乎不变</b>，因为它是「卖铲子的」，不是买设备的
</div>
</div>

<h2>三、股价崩跌榜（市场已给出的定价）</h2>
<div class="card">
<table>
<tr><th>公司</th><th class="n">股价</th><th class="n">当日跌幅</th><th class="n">距52周高</th></tr>
{drows}
</table>
<div class="warn" style="margin-bottom:0">
<b>11-20 是系统性下跌日</b>：10 家公司<b>全部下跌</b>，其中英伟达 <b>−14.01%</b>、AMD −13.25%、博通 −12.19%、甲骨文 −8.48%。
<br>英伟达 52 周高 243.37 → 现价 125.53，<b>腰斩</b>。
</div>
</div>

<h2>四、泡沫判断：正反两面的数据</h2>

<div class="ok">
<b>✅ 支持「不是典型泡沫」的证据</b>
<ul>
<li><b>龙头极其赚钱</b>：英伟达净利率 <b>55.6%</b>、经营现金流 102.7B、FCF <b>+96.7B</b> —— 历史上罕见的盈利水平</li>
<li><b>整体 FCF 为正</b>：10 家合计自由现金流 <b>+{tot_fcf/1e9:.0f}B</b>，不是靠借债烧钱</li>
<li><b>研发投入真实</b>：微软 R&D 35.6B、苹果 45.8B、AMD 8.1B —— 不是财务工程</li>
<li><b>回购力度大</b>：英伟达 40.09B、苹果 86.4B —— 说明现金充裕而非紧缺</li>
<li><b>估值并不极端</b>：英伟达 PE <b>13.4</b>、谷歌 13.8、Meta 19.1 —— 远低于 2000 年互联网泡沫的 60-100 倍</li>
</ul>
</div>

<div class="warn">
<b>⚠️ 支持「存在泡沫成分」的证据</b>
<ul>
<li><b>资本开支增速远超营收增速</b>：微软 Capex 增 <b>4.1 倍</b>而营收仅增 1.97 倍；甲骨文 Capex 率翻倍到 82.6%</li>
<li><b>甲骨文自由现金流为负 −23.7B</b>：靠外部融资支撑扩张，且股价已跌 <b>−59.6%</b></li>
<li><b>亚马逊 FCF 仅 7.7B</b>：营收 716.9B 却只剩 1.1% 的 FCF，几乎全部投入资本开支</li>
<li><b>折旧压力尚未到来</b>：当前 Capex 会转为未来 3-5 年折旧，压缩届时利润</li>
<li><b>股价已提前崩塌</b>：英伟达腰斩、甲骨文 −59.6% —— 市场已开始定价「过度投资」</li>
<li><b>AMD / Palantir PE 超 90 倍</b>：局部存在明显高估</li>
</ul>
</div>

<h2>五、三个必须说清的口径问题</h2>
<div class="card">

<h3>① 「AI 公司」不是同一种生意</h3>
<p>数据显示出<b>三层结构</b>：</p>
<ul>
<li><b>卖铲子层</b>（英伟达、博通、AMD）：Capex 率 1-3%，赚的是别人的资本开支</li>
<li><b>自建基建层</b>（微软、谷歌、亚马逊、Meta、甲骨文）：Capex 率 18-83%，是<b>花钱方</b></li>
<li><b>应用层</b>（Palantir）：Capex 率 0.8%，轻资产</li>
</ul>
<p style="margin-bottom:0">用同一个「泡沫」标签覆盖这三层会得出错误结论。<b>真正的风险集中在中层</b>。</p>

<h3>② 资本开支不等于浪费</h3>
<p>微软 115.9B 的 Capex 对应的是 331.8B 营收和 133.7B 净利，<b>它仍在赚钱</b>。
泡沫的经典定义是「投入无法产生回报」，而当前数据<b>无法证明回报率已转负</b>——
因为数据中心的生命周期是 5-10 年，<b>收益尚未完全兑现，成本也尚未完全折旧</b>。</p>

<h3>③ 财报口径差异会导致误判（本次实测踩坑记录）</h3>
<p>各家现金流科目命名完全不同：</p>
<ul>
<li>微软：<code>Cash Provided by Operating Activity, Including Discontinued</code></li>
<li>苹果：<code>Cash generated by operating activities</code></li>
<li>亚马逊：<code>Purchases of property and equipment</code></li>
<li>甲骨文：<code>Payments to Acquire Property, Plant, and Equipment, Total</code></li>
</ul>
<p style="margin-bottom:0"><b>若用统一字段名匹配会漏掉 4 家公司</b>（首次尝试时微软/苹果/亚马逊/博通全部为空）。
本报告已用多模式匹配修正，但仍建议以公司原始 10-K 为准。</p>
</div>

<h2>六、数据来源与可复算</h2>
<div class="card">
<table>
<tr><th>数据</th><th>来源</th><th>接口</th><th>可复算</th></tr>
<tr><td>财务指标（PE/净利率/增速/52周高低）</td><td>Finnhub</td><td><code>/stock/metric?symbol=X&amp;metric=all</code></td><td>✅</td></tr>
<tr><td>财报三表（含现金流、资本开支）</td><td>Finnhub（XBRL 原始）</td><td><code>/stock/financials-reported?symbol=X</code></td><td>✅</td></tr>
<tr><td>股价与涨跌</td><td>Finnhub + 腾讯双源交叉验证</td><td><code>/quote</code>、<code>qt.gtimg.cn</code></td><td>✅</td></tr>
</table>
<p style="font-size:12.5px;color:#6b7280;margin-bottom:0">
原始数据：<code>AI泡沫研究/fin_summary.json</code>、<code>AI泡沫研究/trend.json</code>、<code>AI泡沫研究/*_m.json</code><br>
公司范围：NVDA / MSFT / GOOGL / AMZN / META / AAPL / AVGO / AMD / ORCL / PLTR（CRM 财报接口未返回，已排除）
</p>
</div>

<p style="margin-top:38px;padding-top:16px;border-top:1px solid #e3e5e7;font-size:12.5px;color:#9ca3af;line-height:1.8">
⚠️ 本报告只列财务事实、口径说明与历史趋势，<b>不构成投资建议，也不对「是否泡沫」给出预测性结论</b>。
财报为各公司最近一期年报（10-K），非季度数据。资本开支包含 property/equipment 采购，不含股权投资与并购。
所有数字来自 Finnhub 公开接口，可复算；若与公司 10-K 有差异，以 10-K 为准。
</p>

</div></body></html>'''

open('AI泡沫研究报告-2026-11-22.html','w',encoding='utf-8').write(HTML)
print(f'  ✓ 已生成 {os.path.getsize("AI泡沫研究报告-2026-11-22.html"):,} B')
