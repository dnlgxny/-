"""宏观新闻研究 · 每日主流程

替代原「金融要闻」流程，输出结构化宏观研究报告。
"""
import json, os, sys, datetime, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, '_data')

from macro_research import collect_macro
from analyze_macro import analyze


def load_index():
    """从工作台 indicators.json 取纳指现状"""
    wb = os.path.join(os.path.dirname(HERE), '_data', 'indicators.json')
    if not os.path.exists(wb): return None
    d = json.load(open(wb, encoding='utf-8'))
    c = d['close']; i = -1
    peak = max(c)
    return {
        'close': f'{c[i]:,.2f}',
        'date': d['dates'][i],
        'chg': f'{(c[i]/c[i-1]-1)*100:+.2f}%',
        'rsi': f'{d["rsi14"][i]:.2f}',
        'ma200': f'{d["ma200"][i]:,.2f}',
        'ma250': f'{d["ma250"][i]:,.2f}',
        'drawdown': f'{(c[i]/peak-1)*100:.2f}%',
    }


def fetch_news():
    """Finnhub 市场新闻"""
    k = os.environ.get('FINNHUB_API_KEY', '').strip()
    if not k:
        p = os.path.expanduser('~/.dsh/.credentials.yaml')
        if os.path.exists(p):
            for line in open(p, encoding='utf-8'):
                if 'FINNHUB' in line.upper():
                    k = line.split(':', 1)[1].strip().strip('"').strip("'")
                    break
    # 兜底：用已写入的 key
    if not k:
        k = 'dbu09g1r01qtr41gnv30dbu09g1r01qtr41gnv3g'

    import ssl, urllib.request
    url = f'https://finnhub.io/api/v1/news?category=general&token={k}'
    ctx = ssl.create_default_context()
    op = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx),
                                     urllib.request.ProxyHandler({}))
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with op.open(req, timeout=30) as r:
            rows = json.loads(r.read().decode())
        out = []
        for x in rows[:40]:
            ts = x.get('datetime')
            out.append({
                'time': datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M') if ts else '',
                'headline': x.get('headline', ''),
                'summary': (x.get('summary') or '')[:300],
                'source': x.get('source', ''),
            })
        return out
    except Exception as e:
        print(f'    [警告] Finnhub 新闻失败: {type(e).__name__}: {str(e)[:60]}', flush=True)
        return []


def main():
    t_all = time.time()
    print('=' * 64, flush=True)
    print(f'宏观新闻研究  {datetime.datetime.now():%Y-%m-%d %H:%M}', flush=True)
    print('=' * 64, flush=True)

    print('\n[1] 采集宏观数据（FRED）', flush=True)
    t0 = time.time()
    macro = collect_macro()
    ok = sum(1 for v in macro.values() if 'error' not in v)
    print(f'    {ok}/{len(macro)} 个序列成功（{time.time()-t0:.1f}s）', flush=True)

    print('\n[2] 读取纳指现状', flush=True)
    idx = load_index()
    print(f'    {"✅ " + idx["date"] + " " + idx["close"] if idx else "❌ 未取到"}', flush=True)

    print('\n[3] 抓取市场新闻（Finnhub）', flush=True)
    news = fetch_news()
    print(f'    {len(news)} 条', flush=True)

    print('\n[4] AI 生成研究报告', flush=True)
    t0 = time.time()
    try:
        report = analyze(macro, idx, news)
        print(f'    ✅ {len(report)} 字符（{time.time()-t0:.1f}s）', flush=True)
    except Exception as e:
        print(f'    ❌ {type(e).__name__}: {str(e)[:100]}', flush=True)
        print('    保留上次报告，不覆盖', flush=True)
        return 1

    # 落盘
    out = {
        'generatedAt': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
        'report': report,
        'macro': macro,
        'index': idx,
        'newsCount': len(news),
        'sources': ['FRED fredgraph.csv', 'Finnhub news', '工作台 indicators.json'],
    }
    os.makedirs(DATA_DIR, exist_ok=True)
    p = os.path.join(DATA_DIR, 'macro.json')
    json.dump(out, open(p, 'w'), ensure_ascii=False, indent=1)
    print(f'\n[5] 已保存 {p}（{os.path.getsize(p):,} B）', flush=True)
    print(f'\n总耗时 {time.time()-t_all:.1f}s', flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
