#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作台数据准备：拉齐全部数据源 → 计算指标 → 输出 _data/*.json

数据口径（严格遵循 工作台_设计确认稿-2026-10-14.md）
  ① FRED NASDAQ100   1986-01-02 起   NDX 价格（不含股息）  ← 读本地 cache-长序列/
  ② FRED VXNCLS      2001-02-02 起   纳指100 隐含波动率      ← 读本地 cache-长序列/
  ③ CBOE VIX         1990-01-02 起   标普500 隐含波动率
  ④ CNN Fear&Greed   2020-07-17 起   情绪（需 Referer 含 cnn）
  ⑤ 蛋卷 pe/pb/roe   2016-10-12 起   周频估值
  ⑥ nikkei225jp      2019-06-06 起   股息率（JSONP，列15）
  ⑦ SEC N-PORT       2019-11-29 起   前十大权重（季度）

⚠️ 红线：禁止推算；取不到就标缺口，不许填假数据。
"""
import os
import re
import csv
import ssl
import json
import math
import time
import datetime
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                      # 项目根
OUT = os.path.join(HERE, '_data')
# 缓存目录：优先「仓库内」（云端可用），回落「项目根」（本机既有布局）
_CACHE_LOCAL = os.path.join(HERE, 'cache-长序列')
_CACHE_ROOT = os.path.join(ROOT, 'cache-长序列')
CACHE = _CACHE_LOCAL if os.path.isdir(_CACHE_LOCAL) else _CACHE_ROOT
os.makedirs(OUT, exist_ok=True)

UA_FF = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
         '(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')

# 2002-10-09 = 互联网泡沫见底次日，设计稿 A1 规定的起点
START = '2002-10-09'


def get(url, headers=None, tries=3, timeout=45):
    h = {'User-Agent': UA_FF}
    if headers:
        h.update(headers)
    ctx = ssl.create_default_context()
    op = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx),
                                     urllib.request.ProxyHandler({}))
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=h)
            with op.open(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:
            last = e
            time.sleep(2 + i * 2)
    raise RuntimeError(f'{url} -> {type(last).__name__}: {str(last)[:80]}')


def save(name, obj):
    p = os.path.join(OUT, name)
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, separators=(',', ':'))
    print(f'  [OK] {name}  ({os.path.getsize(p):,} B)')


def read_fred_csv(path, col):
    """读 FRED 格式 CSV（observation_date,<col>），跳过空值"""
    rows = []
    with open(path, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            v = (r.get(col) or '').strip()
            if v not in ('', '.'):
                try:
                    rows.append([r['observation_date'], float(v)])
                except ValueError:
                    pass
    return rows


def fetch_fred_online(series_id):
    """直连 FRED 取完整 CSV（GitHub Actions 云端可用；本机被封时返回 None）
    返回 [(date, value)] 或 None
    """
    url = f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}'
    for proxy in (None, 'http://127.0.0.1:7877'):
        try:
            h = {'User-Agent': UA_FF, 'Accept': 'text/csv'}
            ctx = ssl.create_default_context()
            handlers = [urllib.request.HTTPSHandler(context=ctx)]
            handlers.append(urllib.request.ProxyHandler({'https': proxy, 'http': proxy} if proxy else {}))
            op = urllib.request.build_opener(*handlers)
            req = urllib.request.Request(url, headers=h)
            with op.open(req, timeout=30) as r:
                txt = r.read().decode('utf-8', 'replace')
            if txt.startswith('observation_date') and txt.count('\n') > 100:
                out = []
                for line in txt.strip().split('\n')[1:]:
                    p = line.split(',')
                    if len(p) >= 2 and p[1].strip() not in ('', '.'):
                        try:
                            out.append([p[0], float(p[1])])
                        except ValueError:
                            pass
                if out:
                    return out
        except Exception:
            continue
    return None


def ensure_cache(path, series_id, col):
    """确保有可用的基底序列：
       ① 本地缓存存在 → 直接用
       ② 不存在 → 直连 FRED 取（云端场景）并落盘
       ③ 都失败 → 抛错
    """
    if os.path.exists(path):
        rows = read_fred_csv(path, col)
        if len(rows) > 1000:
            return rows, '本地缓存'
    print(f'     [信息] 本地缓存缺失，尝试直连 FRED 取 {series_id} ...')
    rows = fetch_fred_online(series_id)
    if not rows:
        raise RuntimeError(f'{series_id}：本地缓存缺失且线上不可达')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(f'observation_date,{col}\n')
        for d, v in rows:
            f.write(f'{d},{v}\n')
    print(f'     已落盘 {os.path.basename(path)}（{len(rows)} 行）')
    return rows, '直连 FRED'


def _band(depth):
    a = abs(depth)
    if a >= 0.15:
        return 'A'
    if a >= 0.10:
        return 'B'
    if a >= 0.05:
        return 'C'
    return 'D'


# ============ ① NDX 价格 ============
def fetch_tencent_ndx():
    """腾讯 us.NDX 日线（FRED 被封时的增量源）；返回 {date: close}"""
    url = 'https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=k&param=us.NDX,day,,,2000,qfq'
    raw = get(url, {'Referer': 'https://gu.qq.com/'}).decode('utf-8', 'replace')
    j = json.loads(raw[raw.index('=') + 1:])
    d = j['data']['us.NDX']
    arr = None
    for k in ('qfqday', 'day'):
        if k in d and d[k]:
            arr = d[k]
            break
    out = {}
    for x in (arr or []):
        try:
            out[x[0]] = float(x[2])
        except (ValueError, IndexError):
            pass
    return out


def load_ndx():
    print('[1] NDX 价格 ...')
    rows, base_src = ensure_cache(os.path.join(CACHE, 'fred_ndx.csv'), 'NASDAQ100', 'NASDAQ100')
    base_end = rows[-1][0]
    base = {d: v for d, v in rows}
    src = f'FRED NASDAQ100（{base_src}）'

    # FRED 封锁时，用腾讯补最新（先校验重叠期一致性）
    try:
        tx = fetch_tencent_ndx()
        overlap = [d for d in tx if d in base]
        if overlap:
            diffs = [abs(tx[d] - base[d]) for d in overlap]
            max_diff = max(diffs)
            if max_diff > 0.5:
                print(f'     [警告] 腾讯与 FRED 重叠期最大差异 {max_diff:.2f}，放弃拼接')
            else:
                added = 0
                for d in sorted(tx):
                    if d > base_end:
                        rows.append([d, round(tx[d], 2)])
                        added += 1
                if added:
                    rows.sort(key=lambda r: r[0])
                    src = f'FRED NASDAQ100（本地缓存）+ 腾讯 us.NDX 补 {added} 日'
                    print(f'     腾讯补 {added} 日（重叠 {len(overlap)} 日最大差异 {max_diff:.3f}）→ 末 {rows[-1][0]}')
    except Exception as e:
        print(f'     [警告] 腾讯补数失败（{type(e).__name__}: {str(e)[:60]}），仅用缓存')

    save('ndx.json', {
        'src': src, 'unit': '指数点（价格口径，不含股息）',
        'start': rows[0][0], 'end': rows[-1][0], 'n': len(rows), 'rows': rows,
        'note': 'FRED 直连被封，历史来自本地缓存；最新由腾讯 us.NDX 增量拼接',
    })
    return rows


# ============ ② VXN ============
def fetch_cboe_vxn():
    """CBOE VXN 官方 CSV（2009 起）；返回 {date: close}"""
    raw = get('https://cdn-api.cboe.com/api/global/us_indices/daily_prices/VXN_History.csv').decode('utf-8', 'replace')
    out = {}
    for r in csv.DictReader(raw.splitlines()):
        try:
            d = datetime.datetime.strptime(r['DATE'], '%m/%d/%Y').strftime('%Y-%m-%d')
            out[d] = float(r['CLOSE'])
        except Exception:
            pass
    return out


def load_vxn():
    print('[2] VXN ...')
    rows, base_src = ensure_cache(os.path.join(CACHE, 'fred_vxn.csv'), 'VXNCLS', 'VXNCLS')
    base_end = rows[-1][0]
    base = {d: v for d, v in rows}
    src = f'FRED VXNCLS（{base_src}）'

    # FRED 封锁时用 CBOE 补最新（CBOE 只有 2009 起，仅用于补尾部）
    try:
        cb = fetch_cboe_vxn()
        overlap = [d for d in cb if d in base]
        if overlap:
            max_diff = max(abs(cb[d] - base[d]) for d in overlap)
            if max_diff > 0.01:
                print(f'     [警告] CBOE 与 FRED 重叠期最大差异 {max_diff:.3f}，放弃拼接')
            else:
                added = 0
                for d in sorted(cb):
                    if d > base_end:
                        rows.append([d, round(cb[d], 2)])
                        added += 1
                if added:
                    rows.sort(key=lambda r: r[0])
                    src = f'FRED VXNCLS（本地缓存）+ CBOE 补 {added} 日'
                    print(f'     CBOE 补 {added} 日（重叠 {len(overlap)} 日差异 {max_diff:.4f}）→ 末 {rows[-1][0]}')
    except Exception as e:
        print(f'     [警告] CBOE 补数失败（{type(e).__name__}: {str(e)[:60]}），仅用缓存')

    save('vxn.json', {
        'src': src, 'unit': '隐含波动率',
        'start': rows[0][0], 'end': rows[-1][0], 'n': len(rows), 'rows': rows,
        'note': 'FRED 直连被封，历史来自本地缓存（2001 起，覆盖 2002）；最新由 CBOE 增量拼接',
    })
    return rows


# ============ ③ VIX（CBOE）============
def load_vix():
    print('[3] VIX（CBOE 官方 CSV）...')
    raw = get('https://cdn-api.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv').decode('utf-8', 'replace')
    rows = []
    for r in csv.DictReader(raw.splitlines()):
        try:
            d = datetime.datetime.strptime(r['DATE'], '%m/%d/%Y').strftime('%Y-%m-%d')
            rows.append([d, float(r['CLOSE'])])
        except Exception:
            pass
    rows.sort()
    save('vix.json', {
        'src': 'CBOE VIX_History.csv', 'unit': '隐含波动率',
        'start': rows[0][0], 'end': rows[-1][0], 'n': len(rows), 'rows': rows,
        'note': 'CBOE 无 CORS，须预生成',
    })
    return rows


# ============ ④ CNN 恐慌贪婪 ============
def load_cnn():
    print('[4] CNN Fear & Greed ...')
    HDR = {'Referer': 'https://www.cnn.com/',
           'Accept': 'application/json, text/plain, */*',
           'Origin': 'https://www.cnn.com'}
    base = 'https://production.dataviz.cnn.io/index/fearandgreed/graphdata'
    d = json.loads(get(base, HDR).decode('utf-8'))
    hist = d.get('fear_and_greed_historical', {}).get('data', [])
    try:
        d2 = json.loads(get(base + '/2020-07-17', HDR).decode('utf-8'))
        h2 = d2.get('fear_and_greed_historical', {}).get('data', [])
        if len(h2) > len(hist):
            hist = h2
    except Exception as e:
        print(f'     [警告] 长历史失败（{str(e)[:50]}），用近 1 年')
    fg = d['fear_and_greed']
    rows = []
    for it in hist:
        dt = datetime.datetime.fromtimestamp(it['x'] / 1000, datetime.timezone.utc).strftime('%Y-%m-%d')
        rows.append([dt, round(it['y'], 2)])
    rows.sort()
    save('cnn.json', {
        'src': 'CNN Fear & Greed Index', 'unit': '0-100（越低越恐慌）',
        'current': {'score': round(fg['score'], 1), 'rating': fg['rating'],
                    'ts': fg['timestamp'],
                    'prev_close': round(fg.get('previous_close', 0), 1),
                    'prev_week': round(fg.get('previous_1_week', 0), 1),
                    'prev_month': round(fg.get('previous_1_month', 0), 1),
                    'prev_year': round(fg.get('previous_1_year', 0), 1)},
        'start': rows[0][0], 'end': rows[-1][0], 'n': len(rows), 'rows': rows,
        'note': '美股口径；历史最早 2020-07-17（更早返回 500）',
    })
    return rows


# ============ ⑤ 蛋卷估值 ============
def load_danjuan():
    print('[5] 蛋卷 pe/pb/roe（周频）...')
    out = {}
    for kind in ('pe', 'pb', 'roe'):
        raw = get(f'https://danjuanfunds.com/djapi/index_eva/{kind}_history/NDX?day=all').decode('utf-8')
        d = json.loads(raw)
        arr = None
        for k, v in d.get('data', {}).items():
            if isinstance(v, list) and v:
                arr = v
                break
        rows = []
        for it in (arr or []):
            dt = datetime.datetime.fromtimestamp(it['ts'] / 1000, datetime.timezone.utc).strftime('%Y-%m-%d')
            val = it.get('pe') or it.get('pb') or it.get('roe')
            rows.append([dt, round(float(val), 4)])
        rows.sort()
        out[kind] = {'rows': rows, 'n': len(rows),
                     'start': rows[0][0] if rows else None,
                     'end': rows[-1][0] if rows else None}
        print(f'     {kind}: {len(rows)} 点 {rows[0][0] if rows else "-"} ~ {rows[-1][0] if rows else "-"}')
    out['src'] = '蛋卷 danjuanfunds（与雪球同源）'
    out['note'] = '周频；起点 2016-10-12，非 2002'
    save('danjuan.json', out)

    d = json.loads(get('https://danjuanfunds.com/djapi/index_eva/detail/NDX').decode('utf-8'))
    v = d['data']
    keep = {k: v.get(k) for k in ('index_code', 'name', 'pe', 'pb', 'roe', 'yeild',
                                  'pe_percentile', 'pb_percentile', 'peg', 'eva_type', 'date')}
    keep['src'] = '蛋卷 detail/NDX'
    save('danjuan_now.json', keep)
    return out


# ============ ⑥ 股息率（nikkei225jp，JSONP）============
def load_dividend():
    print('[6] 股息率（nikkei225jp 列15）...')
    # ⚠️ 该源无 Referer 会返回 404（实测），必须带站点 Referer
    raw = get('https://nikkei225jp.com/_data/_nfsDATA/json_DAY/US_PER.json',
              {'Referer': 'https://nikkei225jp.com/'}).decode('utf-8', 'replace')
    body = raw[raw.index('['): raw.rindex(']') + 1]      # 去 JSONP 壳
    arr = json.loads(body)
    rows = []
    for r in arr:
        if len(r) > 15 and str(r[15]).strip() not in ('', 'None'):
            d = datetime.datetime.fromtimestamp(r[0] / 1000, datetime.timezone.utc).strftime('%Y-%m-%d')
            rows.append([d, round(float(r[15]), 4)])
    rows.sort()
    save('dividend.json', {
        'src': 'nikkei225jp US_PER.json 列15', 'unit': '%',
        'start': rows[0][0], 'end': rows[-1][0], 'n': len(rows), 'rows': rows,
        'note': 'NDX 指数级股息率；周频；经列3收盘价交叉验证与腾讯一致',
    })
    return rows


# ============ ⑦ 前十大权重（SEC N-PORT）============
def load_weights():
    print('[7] 前十大权重（SEC N-PORT）...')
    UA_DECL = 'Research/1.0 (contact: research@example.com)'
    url = 'https://www.sec.gov/Archives/edgar/data/1067839/000106783926000030/primary_doc.xml'
    xml = get(url, {'User-Agent': UA_DECL}).decode('utf-8', 'replace')
    blocks = re.findall(r'<invstOrSec>(.*?)</invstOrSec>', xml, re.S)
    rows = []
    for b in blocks:
        n = re.search(r'<name>(.*?)</name>', b)
        p = re.search(r'<pctVal>(.*?)</pctVal>', b)
        if n and p:
            try:
                rows.append([n.group(1).strip(), round(float(p.group(1)), 3)])
            except ValueError:
                pass
    rows.sort(key=lambda x: -x[1])
    rep = re.search(r'<repPdDate>(.*?)</repPdDate>', xml)
    save('weights.json', {
        'src': 'SEC EDGAR N-PORT (CIK 0001067839, Invesco QQQ Trust)',
        'asOf': rep.group(1) if rep else None,
        'total': len(rows), 'top': rows[:10],
        'top10_sum': round(sum(r[1] for r in rows[:10]), 2),
        'note': '季度披露；免费长历史自 2019-11-29 起',
    })
    return rows


# ============ ⑧ 本地计算指标 ============
def calc_indicators(ndx_rows):
    """由 NDX 序列自算（设计稿 A2/A3）：MA、r500、r250、RSI、回撤分段
    ⚠️ 传入拼接后的序列（FRED 缓存 + 替代源增量），避免漏掉最新交易日
    """
    print('[8] 本地计算指标（MA/r500/r250/RSI/回撤）...')
    full = ndx_rows
    dates = [x[0] for x in full]
    close = [x[1] for x in full]

    def ma_at(i, n):
        return None if i + 1 < n else sum(close[i - n + 1:i + 1]) / n

    try:
        start_i = dates.index(START)
    except ValueError:
        start_i = next(i for i, d in enumerate(dates) if d >= START)

    out = {'dates': [], 'close': [], 'ma250': [], 'ma500': [], 'r250': [], 'r500': [], 'rsi14': []}
    ag = al = None
    for i in range(start_i, len(full)):
        out['dates'].append(dates[i])
        out['close'].append(round(close[i], 2))
        m250, m500 = ma_at(i, 250), ma_at(i, 500)
        out['ma250'].append(round(m250, 2) if m250 else None)
        out['ma500'].append(round(m500, 2) if m500 else None)
        out['r250'].append(round(close[i] / m250, 4) if m250 else None)
        out['r500'].append(round(close[i] / m500, 4) if m500 else None)
        if i >= 14:
            if ag is None:
                g = l = 0.0
                for j in range(i - 13, i + 1):
                    ch = close[j] - close[j - 1]
                    g += max(ch, 0)
                    l += max(-ch, 0)
                ag, al = g / 14, l / 14
            else:
                ch = close[i] - close[i - 1]
                ag = (ag * 13 + max(ch, 0)) / 14
                al = (al * 13 + max(-ch, 0)) / 14
            out['rsi14'].append(round(100 - 100 / (1 + ag / al), 2) if al > 0 else 100.0)
        else:
            out['rsi14'].append(None)

    # 回撤分段：峰→谷单段（A2），A/B/C 分级（A3）
    segs = []
    peak_v, peak_d = out['close'][0], out['dates'][0]
    in_dd, trough_d, trough_v = False, None, None
    for d, v in zip(out['dates'], out['close']):
        if v >= peak_v:
            if in_dd and trough_v is not None:
                depth = trough_v / peak_v - 1
                if depth <= -0.05:
                    segs.append({'peakDate': peak_d, 'peakValue': round(peak_v, 2),
                                 'troughDate': trough_d, 'troughValue': round(trough_v, 2),
                                 'depth': round(depth, 4), 'level': _band(depth)})
            peak_v, peak_d = v, d
            in_dd, trough_d, trough_v = False, None, None
        else:
            if not in_dd:
                in_dd = True
            if trough_v is None or v < trough_v:
                trough_d, trough_v = d, v
    if in_dd and trough_v is not None:
        depth = trough_v / peak_v - 1
        if depth <= -0.05:
            segs.append({'peakDate': peak_d, 'peakValue': round(peak_v, 2),
                         'troughDate': trough_d, 'troughValue': round(trough_v, 2),
                         'depth': round(depth, 4), 'level': _band(depth)})

    from collections import Counter
    cnt = Counter(s['level'] for s in segs)
    out['segments'] = segs
    out['segCounts'] = {'A': cnt.get('A', 0), 'B': cnt.get('B', 0), 'C': cnt.get('C', 0)}

    rets = [math.log(out['close'][i] / out['close'][i - 1]) for i in range(1, len(out['close']))]

    def vol(n):
        if len(rets) < n:
            return None
        s = rets[-n:]
        mu = sum(s) / len(s)
        sd = (sum((x - mu) ** 2 for x in s) / (len(s) - 1)) ** 0.5
        return round(sd * math.sqrt(252) * 100, 2)

    peak_all = max(out['close'])
    out['vol'] = {'m1': vol(21), 'm3': vol(63), 'm6': vol(126), 'y1': vol(252), 'y5': vol(1260)}
    out['curDrawdown'] = round(out['close'][-1] / peak_all - 1, 4)
    out['curPeak'] = round(peak_all, 2)
    out['src'] = '本地自算（基于 FRED NASDAQ100）'
    out['start'] = out['dates'][0]
    out['end'] = out['dates'][-1]
    save('indicators.json', out)
    return out


if __name__ == '__main__':
    print('=' * 60)
    print('工作台数据准备')
    print('=' * 60)
    ok, fail = [], []
    ndx_rows = None

    # 前 7 步互相独立
    for name, fn in [('NDX', load_ndx), ('VXN', load_vxn), ('VIX', load_vix), ('CNN', load_cnn),
                     ('蛋卷', load_danjuan), ('股息率', load_dividend), ('权重', load_weights)]:
        try:
            r = fn()
            if name == 'NDX':
                ndx_rows = r
            ok.append(name)
        except Exception as e:
            print(f'  [X] {name} 失败: {type(e).__name__}: {str(e)[:110]}')
            fail.append(name)

    # 第 8 步依赖 NDX 拼接结果
    if ndx_rows:
        try:
            calc_indicators(ndx_rows)
            ok.append('指标计算')
        except Exception as e:
            print(f'  [X] 指标计算 失败: {type(e).__name__}: {str(e)[:110]}')
            fail.append('指标计算')
    else:
        print('  [X] NDX 取数失败，跳过指标计算')
        fail.append('指标计算')

    print('=' * 60)
    print(f'成功 {len(ok)}/{len(ok)+len(fail)}：{"、".join(ok)}')
    if fail:
        print(f'失败：{"、".join(fail)}')
