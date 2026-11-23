"""生成红利低波研究报告 HTML"""
import json, os
from datetime import datetime

D = os.path.dirname(os.path.abspath(__file__))
hl = json.load(open(os.path.join(D, 'hl_data.json'), encoding='utf-8'))

# 两只基金（来自工作台 holds.json）
FUNDS = {
    '012708': dict(name='东证红利低波A', code='012708',
                   track='中证东方红红利低波动指数（931446）',
                   start='2021-12-30', end='2026-11-20', n=1176, yrs=4.7,
                   nav=1.4301, chg=0.23, total=96.86, cagr=15.62,
                   rsi=66.78, ma20=1.4024, ma60=1.3801, ma250=1.3665,
                   divs=6, dd_raw=-0.06, dd_adj=-0.06, peak=1.431),
    '008163': dict(name='南方红利低波A', code='008163',
                   track='标普中国A股大盘红利低波50指数（SPCLLHCP）',
                   start='2020-01-21', end='2026-11-20', n=1644, yrs=6.5,
                   nav=1.1364, chg=0.62, total=71.76, cagr=8.65,
                   rsi=72.59, ma20=1.0961, ma60=1.0654, ma250=1.0699,
                   divs=7, dd_raw=-17.91, dd_adj=-7.89, peak=1.3843),
}

DIV_EVENTS = {
    '012708': ['2023-12-25  −7.31%', '2024-10-09  −6.56%', '2025-04-07  −5.42%', '2026-03-23  −3.61%'],
    '008163': ['2022-12-29  −5.01%', '2023-12-19  −11.03%', '2024-10-09  −6.59%', '2025-04-07  −4.33%'],
}

def pct(v, dec=1):
    return f'{v:+.{dec}f}%'

def color(v):
    return '#dc2626' if v > 0 else '#15803d'

S, Y, R, W, C = hl['stats'], hl['yearly'], hl['recent'], hl['win_rate'], hl['corr']

# ── 年度表 ──
yrows = ''
for y in sorted(Y.keys()):
    d = Y[y]
    yrows += f'<tr><td>{y}</td>'
    for c in ('hl', 'sh', 'hs'):
        yrows += f'<td class="n" style="color:{color(d[c])}">{pct(d[c])}</td>'
    diff = d['hl'] - d['hs']
    yrows += f'<td class="n" style="color:{color(diff)};font-weight:600">{pct(diff)}</td></tr>'

# ── 近期对比 ──
rrows = ''
for lbl in ('近1月', '近3月', '近半年', '近1年', '近3年'):
    if lbl not in R: continue
    d = R[lbl]
    rrows += f'<tr><td>{lbl}</td>'
    for c in ('hl', 'sh', 'hs'):
        rrows += f'<td class="n" style="color:{color(d[c])}">{pct(d[c])}</td>'
    rrows += f'<td class="n" style="color:{color(d["hl"]-d["hs"])};font-weight:600">{pct(d["hl"]-d["hs"])}</td></tr>'

# ── 基金卡 ──
funds_html = ''
for code, f in FUNDS.items():
    divs = ''.join(f'<li>{x}</li>' for x in DIV_EVENTS[code])
    dd_note = ''
    if abs(f['dd_raw'] - f['dd_adj']) > 1:
        dd_note = (f'<div class="warn">⚠️ 未复权回撤 <b>{f["dd_raw"]:.2f}%</b> 被 {f["divs"]} 次分红除权失真，'
                   f'<b>真实回撤仅 {f["dd_adj"]:.2f}%</b></div>')
    funds_html += f'''
<div class="fcard">
  <div class="fhead"><h3>{f['name']}<span class="fcode">{code}</span></h3>
    <div class="fnav">{f['nav']:.4f}<span class="fchg" style="color:{color(f['chg'])}">{pct(f['chg'],2)}</span></div></div>
  <div class="fmeta">跟踪 {f['track']}　·　{f['start']} ~ {f['end']}（{f['yrs']} 年）</div>
  <table class="ftab">
    <tr><th>复权累计收益</th><td class="n" style="color:{color(f['total'])}">{pct(f['total'])}</td>
        <th>年化</th><td class="n" style="color:{color(f['cagr'])}">{pct(f['cagr'],2)}</td></tr>
    <tr><th>RSI14</th><td class="n">{f['rsi']:.2f}</td>
        <th>分红次数</th><td class="n">{f['divs']}</td></tr>
    <tr><th>距 MA20</th><td class="n">{pct((f['nav']/f['ma20']-1)*100,2)}</td>
        <th>距 MA60</th><td class="n">{pct((f['nav']/f['ma60']-1)*100,2)}</td></tr>
    <tr><th>距 MA250</th><td class="n">{pct((f['nav']/f['ma250']-1)*100,2)}</td>
        <th>真实回撤</th><td class="n">{f['dd_adj']:.2f}%</td></tr>
  </table>
  {dd_note}
  <details><summary>分红除权记录（点击展开）</summary><ul class="divlist">{divs}</ul></details>
</div>'''

HTML = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>红利低波研究报告 · 2026-11-21</title>
<style>
*{{box-sizing:border-box}}
body{{margin:0;background:#f7f8f9;color:#1a1a1a;font-size:15px;line-height:1.85;
 font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif}}
.page{{max-width:1100px;margin:0 auto;padding:44px 38px 100px}}
header{{border-bottom:3px solid #111;padding-bottom:22px;margin-bottom:30px}}
h1{{font-size:30px;margin:0 0 8px;font-weight:700;letter-spacing:-.4px}}
.meta{{color:#666;font-size:13.5px;line-height:2}}
.meta b{{color:#111}}
h2{{font-size:21px;margin:42px 0 16px;padding-top:18px;border-top:1px solid #e3e5e7;font-weight:700}}
h3{{font-size:17px;margin:0;font-weight:700}}
.card{{background:#fff;border:1px solid #e3e5e7;border-radius:10px;padding:20px 24px;margin-bottom:16px}}
table{{width:100%;border-collapse:collapse;font-size:13.5px;margin:14px 0}}
th{{background:#f3f5f6;text-align:left;padding:9px 11px;border:1px solid #e3e5e7;font-weight:600;font-size:12.5px;color:#374151}}
td{{padding:9px 11px;border:1px solid #e3e5e7}}
td.n{{text-align:right;font-variant-numeric:tabular-nums}}
tr:nth-child(even) td{{background:#fcfcfd}}
.fcard{{background:#fff;border:1px solid #e3e5e7;border-radius:10px;padding:20px 24px;margin-bottom:16px}}
.fhead{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px}}
.fcode{{font-size:12px;background:#eef2f5;color:#4b5563;padding:2px 8px;border-radius:4px;margin-left:8px;font-weight:500}}
.fnav{{font-size:26px;font-weight:700;font-variant-numeric:tabular-nums}}
.fchg{{font-size:14px;margin-left:8px;font-weight:600}}
.fmeta{{color:#6b7280;font-size:12.5px;margin-bottom:12px}}
.ftab{{margin:10px 0}}
.ftab th{{width:22%;background:#fafbfc}}
.ftab td.n{{width:28%}}
.warn{{background:#fef3c7;border-left:4px solid #f59e0b;padding:10px 14px;border-radius:6px;
 font-size:13px;margin:12px 0;line-height:1.7}}
details{{margin-top:10px;font-size:13px}}
summary{{cursor:pointer;color:#2563eb;font-weight:500}}
.divlist{{margin:8px 0 0;padding-left:22px;color:#4b5563}}
.divlist li{{margin:4px 0;font-variant-numeric:tabular-nums}}
.note{{background:#eff6ff;border-left:4px solid #2563eb;padding:12px 16px;border-radius:6px;
 font-size:13.5px;margin:14px 0;line-height:1.8}}
.big{{display:flex;gap:14px;flex-wrap:wrap;margin:16px 0}}
.big div{{flex:1;min-width:150px;background:#fafbfc;border:1px solid #e3e5e7;border-radius:8px;padding:14px 16px}}
.big .l{{font-size:12px;color:#6b7280}}
.big .v{{font-size:22px;font-weight:700;font-variant-numeric:tabular-nums;margin-top:3px}}
ul{{margin:10px 0;padding-left:24px}}
li{{margin:5px 0}}
code{{background:#f0f2f4;padding:1.5px 5px;border-radius:3px;font-size:12.5px}}
</style></head><body><div class="page">

<header>
<h1>红利低波研究报告</h1>
<div class="meta">
<b>生成日期</b> {datetime.now():%Y-%m-%d %H:%M}　<b>数据截至</b> 2026-11-20<br>
<b>数据源</b> akshare（指数，前复权）／天天基金（基金净值）　<b>分析区间</b> {hl['range'][0]} ~ {hl['range'][1]}（{hl['n']} 交易日）<br>
<b>方法</b> market-data-fetch skill（真实行情直取）　框架约束：指数/ETF 不用多智能体框架
</div>
</header>

<h2>一、核心结论</h2>
<div class="note">
在纳指100 距峰回撤 <b>−19.84%</b>（2026-11-20）的同期，中证红利低波指数 <b>逆势上涨</b>：
<br>· 近 3 个月：红利低波 <b style="color:#dc2626">+{R['近3月']['hl']:.1f}%</b>　vs　沪深300 <b style="color:#15803d">{R['近3月']['hs']:.1f}%</b>（差 {R['近3月']['hl']-R['近3月']['hs']:+.1f} 个百分点）
<br>· 近 1 年：红利低波 <b style="color:#dc2626">+{R['近1年']['hl']:.1f}%</b>　vs　沪深300 <b style="color:#15803d">{R['近1年']['hs']:.1f}%</b>
<br>· 长期（13.8 年）：年化 <b>{S['hl']['cagr']:.2f}%</b> vs 沪深300 <b>{S['hs']['cagr']:.2f}%</b>，最大回撤 <b>{S['hl']['mdd']:.1f}%</b> vs <b>{S['hs']['mdd']:.1f}%</b>
</div>

<div class="big">
  <div><div class="l">红利低波年化（13.8年）</div><div class="v" style="color:#dc2626">{S['hl']['cagr']:.2f}%</div></div>
  <div><div class="l">沪深300 年化</div><div class="v" style="color:#15803d">{S['hs']['cagr']:.2f}%</div></div>
  <div><div class="l">滚动1年跑赢沪深300</div><div class="v">{W['hl']:.1f}%</div></div>
  <div><div class="l">与沪深300相关性</div><div class="v">{C['hl_hs300']:.2f}</div></div>
</div>

<h2>二、两只持仓基金</h2>
{funds_html}

<h2>三、指数层面：红利低波 vs 沪深300 vs 上证红利</h2>
<div class="card">
<p style="font-size:13px;color:#6b7280;margin-top:0">
注：两只基金跟踪的指数（931446 / SPCLLHCP）akshare 无公开数据，此处采用
<b>中证红利低波（000149）</b> 作为策略基准，<b>上证红利（000015）</b> 作对照。
</p>
<table>
<tr><th>指数</th><th class="n">累计</th><th class="n">年化</th><th class="n">最大回撤</th>
<th class="n">年化波动</th><th class="n">Sharpe</th><th class="n">Calmar</th></tr>
<tr><td><b>中证红利低波（000149）</b></td>
<td class="n" style="color:#dc2626">{S['hl']['total']:+.0f}%</td>
<td class="n" style="color:#dc2626">{S['hl']['cagr']:.2f}%</td>
<td class="n">{S['hl']['mdd']:.1f}%</td>
<td class="n">{S['hl']['vol']:.1f}%</td>
<td class="n">{S['hl']['sharpe']:.2f}</td>
<td class="n">{S['hl']['calmar']:.2f}</td></tr>
<tr><td>上证红利（000015）</td>
<td class="n">{S['sh']['total']:+.0f}%</td><td class="n">{S['sh']['cagr']:.2f}%</td>
<td class="n">{S['sh']['mdd']:.1f}%</td><td class="n">{S['sh']['vol']:.1f}%</td>
<td class="n">{S['sh']['sharpe']:.2f}</td><td class="n">{S['sh']['calmar']:.2f}</td></tr>
<tr><td>沪深300</td>
<td class="n">{S['hs']['total']:+.0f}%</td><td class="n">{S['hs']['cagr']:.2f}%</td>
<td class="n">{S['hs']['mdd']:.1f}%</td><td class="n">{S['hs']['vol']:.1f}%</td>
<td class="n">{S['hs']['sharpe']:.2f}</td><td class="n">{S['hs']['calmar']:.2f}</td></tr>
</table>
</div>

<h2>四、分年度收益</h2>
<div class="card">
<table>
<tr><th>年份</th><th class="n">红利低波</th><th class="n">上证红利</th><th class="n">沪深300</th><th class="n">红利低波超额</th></tr>
{yrows}
</table>
<p style="font-size:12.5px;color:#6b7280;margin:8px 0 0">
注：首尾年份为不完整年度（按该年首末交易日计算）。
</p>
</div>

<h2>五、近期相对表现</h2>
<div class="card">
<table>
<tr><th>区间</th><th class="n">红利低波</th><th class="n">上证红利</th><th class="n">沪深300</th><th class="n">红利低波超额</th></tr>
{rrows}
</table>
</div>

<h2>六、走势与年度收益图</h2>
<div class="card"><div id="chart" style="width:100%;height:420px"></div></div>

<h2>七、必须说清的四个问题</h2>
<div class="card">
<h3 style="margin-bottom:10px">① 008163 的历史回撤被分红严重失真</h3>
<p>天天基金返回的是<b>未复权单位净值</b>。南方红利低波（008163）在 2020-2026 年间分红 7 次，
其中 2023-12-19 单日 <code>−11.03%</code>、2024-10-09 单日 <code>−6.59%</code>，均为除权而非真实下跌。<br>
<b>未复权回撤 −17.91% → 复权后真实回撤 −7.89%</b>。若只看净值曲线会严重误判该基金的风险。</p>

<h3 style="margin:20px 0 10px">② 红利低波并非「不跌」</h3>
<p>长期最大回撤 <b>{S['hl']['mdd']:.1f}%</b>（2015 年股灾期间），年化波动 <b>{S['hl']['vol']:.1f}%</b>。
与沪深300 相关性 <b>{C['hl_hs300']:.2f}</b> —— 分散效果存在但<b>不是对冲</b>，系统性下跌时同样会跌。</p>

<h3 style="margin:20px 0 10px">③ 滚动 1 年跑赢沪深300 的时间只占 {W['hl']:.1f}%</h3>
<p>13.8 年样本中，红利低波在滚动 1 年维度跑赢沪深300 的比例为 <b>{W['hl']:.1f}%</b>（{W['n']} 个观测）。
超额收益主要来自<b>少数几年的极端分化</b>（如 2016-2018、2024-2026），而非每年稳定跑赢。</p>

<h3 style="margin:20px 0 10px">④ 跟踪指数数据缺口</h3>
<p>012708 跟踪的 <code>931446</code> 与 008163 跟踪的 <code>SPCLLHCP</code>，
<b>akshare 均无公开日线</b>（实测 KeyError）。本报告用 000149 作策略基准替代，<b>两者成分股并不相同</b>，
不可直接等同。</p>
</div>

<h2>八、数据来源与可复算</h2>
<div class="card">
<table>
<tr><th>数据</th><th>来源</th><th>区间</th><th>可复算</th></tr>
<tr><td>中证红利低波 000149</td><td>akshare <code>stock_zh_index_daily</code>（新浪）</td><td>{hl['range'][0]} ~ {hl['range'][1]}</td><td>✅</td></tr>
<tr><td>上证红利 000015</td><td>同上</td><td>— 2026-11-20</td><td>✅</td></tr>
<tr><td>沪深300</td><td>同上</td><td>2002-01-04 ~ 2026-11-20</td><td>✅</td></tr>
<tr><td>012708 净值</td><td>天天基金 <code>f10/lsjz</code>（单位净值）</td><td>2021-12-30 ~ 2026-11-20</td><td>✅</td></tr>
<tr><td>008163 净值</td><td>同上</td><td>2020-01-21 ~ 2026-11-20</td><td>✅</td></tr>
</table>
<p style="font-size:12.5px;color:#6b7280;margin-top:10px">
原始数据：<code>工作台/_data/holds.json</code>、<code>红利低波研究/hl_data.json</code>
</p>
</div>

<p style="margin-top:40px;padding-top:18px;border-top:1px solid #e3e5e7;font-size:12.5px;color:#9ca3af;line-height:1.8">
⚠️ 本报告只列统计事实与口径说明，<b>不构成投资建议</b>。历史收益不代表未来表现。
指数与基金口径不同，不可直接比较。分红复权处理为近似方法，与基金公司官方复权净值可能有微小差异。
</p>

</div>
<script src="echarts.min.js"></script>
<script>
const D = {json.dumps(dict(dates=hl['series_dates'], series=hl['series'],
                          yearly=hl['yearly']), ensure_ascii=False)};
const c = echarts.init(document.getElementById('chart'));
const years = Object.keys(D.yearly).map(Number);
c.setOption({{
  animation: false,
  tooltip: {{ trigger: 'axis' }},
  legend: {{ data: ['红利低波','上证红利','沪深300'], top: 0, textStyle:{{fontSize:12}} }},
  grid: [{{ left: 62, right: 58, top: 42, height: 200 }},
         {{ left: 62, right: 58, top: 285, height: 110 }}],
  xAxis: [
    {{ type:'category', data:D.dates, gridIndex:0, axisLabel:{{fontSize:10,color:'#9ca3af'}},
       axisLine:{{lineStyle:{{color:'#e3e5e7'}}}}, splitLine:{{show:false}} }},
    {{ type:'category', data:years, gridIndex:1, axisLabel:{{fontSize:10,color:'#9ca3af'}},
       axisLine:{{lineStyle:{{color:'#e3e5e7'}}}} }}
  ],
  yAxis: [
    {{ type:'value', gridIndex:0, scale:true,
       axisLabel:{{fontSize:10,color:'#9ca3af',formatter:v=>v>=1000?(v/1000).toFixed(0)+'k':v}},
       splitLine:{{lineStyle:{{color:'#f1f3f4'}}}} }},
    {{ type:'value', gridIndex:1, name:'年度%', nameTextStyle:{{fontSize:10,color:'#9ca3af'}},
       axisLabel:{{fontSize:10,color:'#9ca3af',formatter:'{{value}}%'}},
       splitLine:{{lineStyle:{{color:'#f8f9fa'}}}} }}
  ],
  dataZoom: [{{ type:'inside', xAxisIndex:0, start:55, end:100 }}],
  series: [
    {{ name:'红利低波', type:'line', data:D.series.hl, xAxisIndex:0, yAxisIndex:0,
       showSymbol:false, smooth:true, lineStyle:{{width:2.2,color:'#dc2626'}}, itemStyle:{{color:'#dc2626'}},
       areaStyle:{{color:'rgba(220,38,38,.06)'}} }},
    {{ name:'上证红利', type:'line', data:D.series.sh, xAxisIndex:0, yAxisIndex:0,
       showSymbol:false, smooth:true, lineStyle:{{width:1.4,color:'#f59e0b'}}, itemStyle:{{color:'#f59e0b'}} }},
    {{ name:'沪深300', type:'line', data:D.series.hs, xAxisIndex:0, yAxisIndex:0,
       showSymbol:false, smooth:true, lineStyle:{{width:1.4,color:'#6b7280'}}, itemStyle:{{color:'#6b7280'}} }},
    {{ name:'红利低波', type:'bar', data:years.map(y=>+D.yearly[String(y)].hl.toFixed(2)),
       xAxisIndex:1, yAxisIndex:1, itemStyle:{{color:'#dc2626',opacity:.8}}, barWidth:'42%' }},
    {{ name:'沪深300', type:'bar', data:years.map(y=>+D.yearly[String(y)].hs.toFixed(2)),
       xAxisIndex:1, yAxisIndex:1, itemStyle:{{color:'#9ca3af',opacity:.8}}, barWidth:'42%' }}
  ]
}});
window.addEventListener('resize', ()=>c.resize());
</script>
</body></html>'''

out = os.path.join(D, '红利低波研究报告-2026-11-21.html')
open(out, 'w', encoding='utf-8').write(HTML)
print(f'✅ {out}')
print(f'   {os.path.getsize(out):,} B')
