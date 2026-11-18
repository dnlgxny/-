"""宏观新闻研究 · 每日生成（替代原「金融要闻」）

设计参考：TradingAgents 新闻分析师的报告结构（美股分析/latest/complete_report_zh.html）
  1. 执行摘要
  2. 利率与政策 — 主导驱动因素
  3. 通胀与增长
  4. AI 综合体新闻（指数重要）
  5. 地缘政治叠加
  6. 数据缺口（诚实披露）
  7. 关键要点汇总表

数据来源（全部真实可核实）：
  · FRED fredgraph.csv（无需 key）—— 利率/通胀/就业
  · Finnhub 市场新闻 —— 美股实时资讯
  · 工作台已有指标 —— 纳指点位/RSI/均线
"""
import json, os, re, ssl, time, urllib.request, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, '_data')

# ══════════ FRED 取数（fredgraph.csv，无需 API key）══════════
# ⚠️ 实测：自定义 UA 会被 FRED 拒绝/超时，必须用 urllib 默认 UA
FRED_SERIES = {
    'DGS10':      ('10年期美债收益率', '%'),
    'DGS2':       ('2年期美债收益率', '%'),
    'T10Y2Y':     ('10Y-2Y 期限利差', '%'),
    'FEDFUNDS':   ('联邦基金利率', '%'),
    'CPIAUCSL':   ('CPI 指数', ''),
    'CPILFESL':   ('核心 CPI 指数', ''),
    'PCEPILFE':   ('核心 PCE 指数', ''),
    'UNRATE':     ('失业率', '%'),
    'PAYEMS':     ('非农就业人数', '千人'),
    'VIXCLS':     ('VIX 恐慌指数', ''),
    'DTWEXBGS':   ('美元指数（广义）', ''),
}


def fetch_fred(series_id, days=400, tries=3):
    """取 FRED 序列，返回 [(date, value), ...] 升序

    ⚠️ FRED 对连续请求较敏感，实测偶发 TimeoutError / SSL handshake timeout。
       加 3 次重试 + 递增等待可显著提高成功率。
    """
    url = f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}'
    ctx = ssl.create_default_context()
    op = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx),
                                     urllib.request.ProxyHandler({}))
    text = None
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url)   # 不加自定义 UA
            with op.open(req, timeout=45) as r:
                text = r.read().decode('utf-8', 'replace')
            break
        except Exception as e:
            last = e
            if i < tries - 1:
                time.sleep(2 + i * 3)
    if text is None:
        raise last

    cutoff = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
    rows = []
    for line in text.strip().split('\n')[1:]:
        parts = line.split(',')
        if len(parts) < 2: continue
        d, v = parts[0].strip(), parts[1].strip()
        if not d or v in ('', '.'): continue
        if d < cutoff: continue
        try: rows.append((d, float(v)))
        except ValueError: continue
    return rows


def collect_macro():
    """并发采集全部宏观序列（2026-11-18 优化）

    串行 11 个序列含超时重试曾耗时 1046 秒，改为 6 线程并发后约 30-60 秒。
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    def one(sid):
        name, unit = FRED_SERIES[sid]
        try:
            rows = fetch_fred(sid, days=400, tries=2)
            if rows:
                return sid, {
                    'name': name, 'unit': unit,
                    'latest': rows[-1][1], 'latest_date': rows[-1][0],
                    'prev': rows[-2][1] if len(rows) > 1 else None,
                    'prev_date': rows[-2][0] if len(rows) > 1 else None,
                    'series': rows[-30:],
                    'n': len(rows),
                }
            return sid, {'name': name, 'error': '无数据'}
        except Exception as e:
            return sid, {'name': name, 'error': f'{type(e).__name__}: {str(e)[:50]}'}

    out = {}
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(one, sid): sid for sid in FRED_SERIES}
        for f in as_completed(futs):
            sid, v = f.result()
            out[sid] = v
    # 保持原始顺序
    return {sid: out[sid] for sid in FRED_SERIES if sid in out}


if __name__ == '__main__':
    m = collect_macro()
    for sid, v in m.items():
        if 'error' in v:
            print(f'  ❌ {sid} {v["name"]}: {v["error"]}')
        else:
            print(f'  ✅ {sid:<10} {v["name"]:<20} {v["latest"]:>10} {v["unit"]:<4} ({v["latest_date"]})')
