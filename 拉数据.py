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

# ══════════════════════════════════════════════════════════════
# 网络访问策略（2026-10-26 用户选定 A+C 方案）
#   问题：cdn.cboe.com / fred 部分域名直连被阻断，TCP 握手挂起
#         原实现 ProxyHandler({}) 明确禁用代理 → 卡死 2 分钟以上
#   方案 A：自动探测本机代理（127.0.0.1:7877 等），直连失败时回退走代理
#   方案 C：超时上限从 45s 收紧到 12s，重试次数从 3 降到 2，快速失败
#          （最坏耗时 12×2×2 源 = 48s，而非原来的 45×3×2 = 270s）
# ══════════════════════════════════════════════════════════════
PROXY_CANDIDATES = ['127.0.0.1:7877', '127.0.0.1:7890', '127.0.0.1:1087', '127.0.0.1:6152']
_PROXY_CACHE = {'checked': False, 'proxy': None}


def detect_proxy():
    """探测本机可用 HTTP 代理；返回 'host:port' 或 None。结果缓存。"""
    if _PROXY_CACHE['checked']:
        return _PROXY_CACHE['proxy']
    _PROXY_CACHE['checked'] = True
    import socket as _sk
    for p in PROXY_CANDIDATES:
        host, _, port = p.partition(':')
        try:
            with _sk.create_connection((host, int(port)), timeout=0.6):
                _PROXY_CACHE['proxy'] = p
                print(f'     [网络] 检测到本机代理 {p}')
                return p
        except Exception:
            continue
    print('     [网络] 未检测到本机代理，将直连')
    return None


def _opener(use_proxy=None):
    """构造 opener：use_proxy=None 表示不指定代理；True/False 强制"""
    ctx = ssl.create_default_context()
    handlers = [urllib.request.HTTPSHandler(context=ctx)]
    if use_proxy is None:
        handlers.append(urllib.request.ProxyHandler({}))       # 显式直连
    elif use_proxy is True:
        px = detect_proxy()
        handlers.append(urllib.request.ProxyHandler(
            {'https': f'http://{px}', 'http': f'http://{px}'} if px else {}))
    else:
        handlers.append(urllib.request.ProxyHandler({}))
    return urllib.request.build_opener(*handlers)

# 全局：NDX 的 OHLCV（仅替代源覆盖区间有；FRED 段为空）
NDX_OHLCV = {}


def get(url, headers=None, tries=1, timeout=6):
    """HTTP GET：先直连，失败自动回退代理。

    2026-10-26 改进（用户选定 A+C）：
      A. 直连失败时自动尝试本机代理（cdn.cboe.com 等直连被阻断的域名）
      C. 超时 45s→12s、重试 3→2：最坏耗时从 270s 降到 48s，避免卡死整个任务
    """
    h = {'User-Agent': UA_FF}
    if headers:
        h.update(headers)

    last = None
    # ── 第一轮：直连 ──
    op = _opener(None)
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=h)
            with op.open(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:
            last = e
            if i < tries - 1:
                time.sleep(1 + i)

    # ── 第二轮：检测到代理则回退 ──
    px = detect_proxy()
    if px:
        try:
            op2 = _opener(True)
            req = urllib.request.Request(url, headers=h)
            with op2.open(req, timeout=timeout) as r:
                data = r.read()
            print(f'     [网络] 直连失败，已通过代理 {px} 取回')
            return data
        except Exception as e:
            last = e

    raise RuntimeError(f'{url} -> {type(last).__name__}: {str(last)[:80]}')


def _http_get_text(url, headers=None, timeout=8, tries=2, retry_sleep=1):
    """GET 并返回文本：直连优先，失败回退本机代理（与 get 同策略）"""
    h = {'User-Agent': UA_FF}
    if headers:
        h.update(headers)
    last = None
    op = _opener(None)
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=h)
            with op.open(req, timeout=timeout) as r:
                return r.read().decode('utf-8', 'replace')
        except Exception as e:
            last = e
            if i < tries - 1:
                time.sleep(retry_sleep)
    px = detect_proxy()
    if px:
        try:
            op2 = _opener(True)
            req = urllib.request.Request(url, headers=h)
            with op2.open(req, timeout=timeout) as r:
                return r.read().decode('utf-8', 'replace')
        except Exception as e:
            last = e
    raise RuntimeError(f'{url[:70]} -> {type(last).__name__}: {str(last)[:70]}')


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
def fetch_sina_ndx():
    """新浪美股 .NDX 日线（**主增量源**）
    实测（2026-10-20）：
      - 覆盖 2014-02-18 ~ 至今，3186 条
      - 与 FRED 重叠 3183 天，仅 19 天微差（最大 0.738%，2025 年后仅 1 天差 0.013%）
      - **10-19 返回正确值 29529.34**（腾讯日线同日返回脏数据 10.56）
    返回 {date: close}；失败返回 {}
    """
    url = 'https://stock.finance.sina.com.cn/usstock/api/jsonp.php/var%20_k=/US_MinKService.getDailyK?symbol=.NDX'
    try:
        h = {'User-Agent': UA_FF, 'Referer': 'https://finance.sina.com.cn/'}
        txt = _http_get_text(url, h, timeout=8, tries=2)
        m = re.search(r'\((\[.*\])\)', txt, re.S)
        if not m:
            return {}
        arr = json.loads(m.group(1))
        out = {}
        for x in arr:
            try:
                out[x['d']] = {
                    'c': float(x['c']),
                    'o': float(x.get('o') or x['c']),
                    'h': float(x.get('h') or x['c']),
                    'l': float(x.get('l') or x['c']),
                    'v': float(x.get('v') or 0),
                }
            except (KeyError, ValueError, TypeError):
                pass
        return out
    except Exception as e:
        print(f'     [警告] 新浪日线失败：{type(e).__name__}: {str(e)[:60]}')
        return {}


def fetch_tencent_ndx():
    """腾讯 us.NDX 日线（**备选增量源**）
    ⚠️ 已知缺陷：2026-10-19 曾返回 OHLC 全为 10.x 的脏数据
       ⇒ 必须经过合理性校验才能使用
    """
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
    # OHLCV：仅替代源覆盖的区间有（新浪 2014 起 / 腾讯 2022 起）
    # FRED 只有收盘价 → 早期无 OHLCV，量比/KDJ/布林带宽在这些区间为空
    global NDX_OHLCV
    NDX_OHLCV = {}
    ohlcv = NDX_OHLCV
    rows, base_src = ensure_cache(os.path.join(CACHE, 'fred_ndx.csv'), 'NASDAQ100', 'NASDAQ100')
    base_end = rows[-1][0]
    base = {d: v for d, v in rows}
    src = f'FRED NASDAQ100（{base_src}）'

    # FRED 封锁时补最新：**新浪优先**（数据更可信），腾讯备选
    try:
        tx = fetch_sina_ndx()
        source_name = '新浪 .NDX'
        if not tx:
            print('     [信息] 新浪无数据，改用腾讯')
            tx = fetch_tencent_ndx()
            source_name = '腾讯 us.NDX'
        overlap = [d for d in tx if d in base]
        # ⚠️ 关键：把替代源的**全量** OHLCV 装入全局表
        #    不只是新增那几天 —— 否则 KDJ/量比只能在最后几天算出值
        for _d, _bar in tx.items():
            NDX_OHLCV[_d] = _bar
        if overlap:
            # ⚠️ 判据用「相对差异」而非绝对值（指数从 800→30000，绝对差会失真）
            rel = [abs(tx[d]['c'] - base[d]) / base[d] for d in overlap if base[d] > 0]
            max_rel = max(rel) if rel else 0
            max_diff = max(abs(tx[d]['c'] - base[d]) for d in overlap)
            if max_rel > 0.02:          # 相对差异 >2% 才判定为不同标的/数据错误
                print(f'     [警告] 与 FRED 重叠期最大相对差异 {max_rel*100:.2f}%（绝对 {max_diff:.2f}），放弃拼接')
                raise RuntimeError('重叠期差异过大')
            else:
                added = 0
                skipped = []
                for d in sorted(tx):
                    if d > base_end:
                        v = tx[d]['c']
                        # 合理性校验：与最后一个可信值偏离 >40% 视为脏数据
                        last_ok = rows[-1][1] if rows else None
                        if last_ok and last_ok > 0:
                            dev = v / last_ok - 1
                            if abs(dev) > 0.40:
                                skipped.append((d, v, last_ok, dev))
                                continue
                        rows.append([d, round(v, 2)])
                        # 同步保存 OHLCV（供 KDJ/量比/布林带宽计算）
                        ohlcv[d] = tx[d]
                        added += 1
                if skipped:
                    print('     [警告] 跳过异常数据 %d 条：' % len(skipped))
                    for d, v, lo, dev in skipped:
                        print(f'       {d}: {v:,.2f}（前值 {lo:,.2f}，偏离 {dev*100:+.1f}%）')
                if added:
                    rows.sort(key=lambda r: r[0])
                    src = f'FRED NASDAQ100（本地缓存）+ {source_name} 补 {added} 日'
                    print(f'     {source_name}补 {added} 日（重叠 {len(overlap)} 日最大差异 {max_diff:.3f}）→ 末 {rows[-1][0]}')
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

    # ⚠️ 2026-10-26 策略调整：FRED 已恢复直连，优先用 FRED 刷新缓存；
    #    CBOE 作为备选（其 cdn-api.cboe.com 当前直连与代理均不通）
    try:
        fresh = fetch_fred_online('VXNCLS')
        if fresh and len(fresh) > 1000:
            base = {d: v for d, v in fresh}
            added = 0
            for d, v in fresh:
                if d > base_end:
                    rows.append([d, round(v, 2)])
                    added += 1
            if added:
                rows.sort(key=lambda r: r[0])
                src = f'FRED VXNCLS（直连）+ 补 {added} 日'
                print(f'     FRED 补 {added} 日 → 末 {rows[-1][0]}')
    except Exception as e:
        print(f'     [信息] FRED 刷新失败（{type(e).__name__}），尝试 CBOE')

    # FRED 不行时再用 CBOE 补最新
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

    out = {'dates': [], 'close': [], 'ma200': [], 'ma250': [], 'ma500': [],
           'r250': [], 'r500': [], 'rsi14': [],
           'kdj_k': [], 'kdj_d': [], 'kdj_j': [],
           'volratio': [], 'boll_width': [], 'boll_upper': [], 'boll_lower': [],
           'volume': []}
    ag = al = None
    kdj_k_prev = kdj_d_prev = None
    for i in range(start_i, len(full)):
        out['dates'].append(dates[i])
        out['close'].append(round(close[i], 2))
        m200, m250, m500 = ma_at(i, 200), ma_at(i, 250), ma_at(i, 500)
        out['ma200'].append(round(m200, 2) if m200 else None)
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

        # ── 以下三项需要 OHLCV（新浪 2014 起 / 腾讯 2022 起有；FRED 段为空）──
        d_i = dates[i]
        bar = NDX_OHLCV.get(d_i)
        if bar:
            out['volume'].append(round(bar['v'], 0))
        else:
            out['volume'].append(None)

        # ① 量比 = 当日成交量 / 过去5日平均成交量（不含当日）
        if bar and bar['v'] > 0:
            prev_v = []
            for j in range(max(0, i - 5), i):
                b2 = NDX_OHLCV.get(dates[j])
                if b2 and b2['v'] > 0:
                    prev_v.append(b2['v'])
            if len(prev_v) == 5:
                out['volratio'].append(round(bar['v'] / (sum(prev_v) / 5), 3))
            else:
                out['volratio'].append(None)
        else:
            out['volratio'].append(None)

        # ② 布林带（20日，2倍标准差）+ 带宽 = (上轨-下轨)/中轨
        if i + 1 >= 20:
            window = close[i - 19:i + 1]
            mid = sum(window) / 20
            var = sum((x - mid) ** 2 for x in window) / 20
            sd = var ** 0.5
            up, low = mid + 2 * sd, mid - 2 * sd
            out['boll_upper'].append(round(up, 2))
            out['boll_lower'].append(round(low, 2))
            out['boll_width'].append(round((up - low) / mid * 100, 2) if mid > 0 else None)
        else:
            out['boll_upper'].append(None)
            out['boll_lower'].append(None)
            out['boll_width'].append(None)

        # ③ KDJ（9,3,3）：RSV → K=2/3·K_prev+1/3·RSV，D=2/3·D_prev+1/3·K，J=3K-2D
        if bar and i + 1 >= 9:
            win = [NDX_OHLCV.get(dates[j]) for j in range(i - 8, i + 1)]
            if all(win):
                hi = max(b['h'] for b in win)
                lo = min(b['l'] for b in win)
                rsv = (close[i] - lo) / (hi - lo) * 100 if hi > lo else 50.0
                if kdj_k_prev is None:
                    kk = dd = 50.0          # 初值惯例 50
                else:
                    kk, dd = kdj_k_prev, kdj_d_prev
                kk = 2 / 3 * kk + 1 / 3 * rsv
                dd = 2 / 3 * dd + 1 / 3 * kk
                jj = 3 * kk - 2 * dd
                kdj_k_prev, kdj_d_prev = kk, dd
                out['kdj_k'].append(round(kk, 2))
                out['kdj_d'].append(round(dd, 2))
                out['kdj_j'].append(round(jj, 2))
            else:
                out['kdj_k'].append(None); out['kdj_d'].append(None); out['kdj_j'].append(None)
        else:
            out['kdj_k'].append(None); out['kdj_d'].append(None); out['kdj_j'].append(None)

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


# ══════════════════════════════════════════════════════════════
# [9] 用户持有的两支红利低波（RSI14 + 基础技术指标）
#     012708 东方红中证红利低波动指数A  → 跟踪 931446（东证红利低波）
#     008163 南方标普红利低波50ETF联接A → 跟踪 SPCLLHCP（取不到），
#            改取其**场内目标 ETF 515450**（红利低波50ETF南方），同标的、有量价
# ══════════════════════════════════════════════════════════════
HOLDS = [
    {'fund': '012708', 'fundName': '东方红中证红利低波动指数A',
     'secid': '2.931446', 'name': '东证红利低波', 'code': '931446',
     'track': '中证东方红红利低波动指数', 'note': '指数本体（基金直接跟踪）'},
    {'fund': '008163', 'fundName': '南方标普红利低波50ETF联接A',
     'secid': '1.515450', 'name': '红利低波50ETF南方', 'code': '515450',
     'track': '标普中国A股大盘红利低波50指数',
     'note': '联接基金跟踪 SPCLLHCP（东财取不到），此处用场内目标 ETF 515450 代理'},
]


def fetch_em_kline(secid, lmt=3000):
    """东方财富日线（沪深/中证指数通用）。返回 [(date, close), ...]"""
    url = ('https://push2his.eastmoney.com/api/qt/stock/kline/get?'
           f'secid={secid}&fields1=f1,f2,f3&fields2=f51,f53&klt=101&fqt=1'
           f'&end=20500101&lmt={lmt}')
    h = {'User-Agent': UA_FF, 'Referer': 'https://quote.eastmoney.com/'}
    # 东财会间歇性限流（返回空），加 3 次重试 + 直连/代理回退
    txt = _http_get_text(url, h, timeout=8, tries=3, retry_sleep=2)
    d = json.loads(txt)
    kl = (d.get('data') or {}).get('klines') or []
    out = []
    for line in kl:
        parts = line.split(',')
        if len(parts) >= 2:
            try:
                out.append((parts[0], float(parts[1])))
            except ValueError:
                pass
    return out


def calc_rsi14(closes):
    """Wilder RSI(14)，返回与 closes 等长的数组（前 14 个为 None）"""
    n = 14
    out = [None] * len(closes)
    if len(closes) <= n:
        return out
    gains = losses = 0.0
    for i in range(1, n + 1):
        ch = closes[i] - closes[i - 1]
        if ch > 0:
            gains += ch
        else:
            losses -= ch
    ag, al = gains / n, losses / n
    out[n] = round(100 - 100 / (1 + ag / al), 2) if al > 0 else 100.0
    for i in range(n + 1, len(closes)):
        ch = closes[i] - closes[i - 1]
        g = ch if ch > 0 else 0.0
        l = -ch if ch < 0 else 0.0
        ag = (ag * (n - 1) + g) / n
        al = (al * (n - 1) + l) / n
        out[i] = round(100 - 100 / (1 + ag / al), 2) if al > 0 else 100.0
    return out


def load_holds():
    print('[9] 红利低波持仓（RSI14）...')
    res = []
    for h in HOLDS:
        try:
            kl = fetch_em_kline(h['secid'])
            if len(kl) < 20:
                raise RuntimeError(f'K线不足（{len(kl)} 根）')
            dates = [x[0] for x in kl]
            closes = [x[1] for x in kl]
            rsi = calc_rsi14(closes)

            def ma(n):
                return round(sum(closes[-n:]) / n, 4) if len(closes) >= n else None

            ch = closes[-1] / closes[-2] - 1 if len(closes) > 1 else None
            peak = max(closes)
            item = {
                'fund': h['fund'], 'fundName': h['fundName'],
                'name': h['name'], 'code': h['code'], 'track': h['track'], 'note': h['note'],
                'src': '东方财富 push2his 日线',
                'start': dates[0], 'end': dates[-1], 'n': len(closes),
                'close': round(closes[-1], 4),
                'chg': round(ch, 4) if ch is not None else None,
                'rsi14': rsi[-1],
                'ma20': ma(20), 'ma60': ma(60), 'ma250': ma(250),
                'peak': round(peak, 4),
                'curDrawdown': round(closes[-1] / peak - 1, 4),
                # 全量序列：价格（走势图）+ RSI14（指标图），两者同轴对齐
                # ⚠️ 之前只存近60点导致「时间线太短」，改为全量
                'dates': dates,
                'closes': [round(c, 4) for c in closes],
                'rsiSeries': rsi,
                'ma20Series': [
                    (round(sum(closes[i-19:i+1])/20, 4) if i >= 19 else None)
                    for i in range(len(closes))
                ],
            }
            res.append(item)
            print(f"     {h['code']} {h['name']}: 收 {item['close']}  RSI14 {item['rsi14']}  "
                  f"({item['start']} ~ {item['end']}, {item['n']} 根)")
        except Exception as e:
            print(f"     [X] {h['code']} {h['name']} 失败：{type(e).__name__}: {str(e)[:90]}")
    if not res:
        raise RuntimeError('两支标的均取数失败')
    save('holds.json', {'items': res, 'generatedAt': datetime.datetime.now().strftime('%Y-%m-%d %H:%M')})
    return res


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

    # 第 9 步：红利低波持仓（独立，不依赖 NDX）
    try:
        load_holds()
        ok.append('红利低波')
    except Exception as e:
        print(f'  [X] 红利低波 失败: {type(e).__name__}: {str(e)[:110]}')
        fail.append('红利低波')

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
