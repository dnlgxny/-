"""实物物资 → 关联标的行情（腾讯/新浪实测可用）"""
import re, ssl, urllib.request, json

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/131 Safari/537.36'

# 主题 → 关联 A 股标的（腾讯代码）
THEME_STOCKS = {
    '石油': [
        ('sh601857', '中国石油'), ('sh600028', '中国石化'),
        ('sh600938', '中国海油'), ('sh601808', '中海油服'),
    ],
    '天然气': [
        ('sh600803', '新奥股份'), ('sh600956', '新天绿能'),
        ('sz002267', '陕天然气'),
    ],
    '贵金属': [
        ('sh600547', '山东黄金'), ('sh601899', '紫金矿业'),
        ('sh600489', '中金黄金'), ('sz002155', '湖南黄金'),
    ],
    '工业金属': [
        ('sh601899', '紫金矿业'), ('sh600362', '江西铜业'),
        ('sh601600', '中国铝业'), ('sh600219', '南山铝业'),
    ],
    '锂/电池金属': [
        ('sz002466', '天齐锂业'), ('sz300750', '宁德时代'),
        ('sh600111', '北方稀土'),
    ],
    '煤炭': [
        ('sh601088', '中国神华'), ('sh600188', '兖矿能源'),
        ('sh601225', '陕西煤业'),
    ],
    '铀': [
        ('sh601985', '中国核电'), ('sh600886', '国投电力'),
    ],
    '农产品': [
        ('sz000876', '新希望'), ('sh600598', '北大荒'),
    ],
}

# 商品期货/现货（新浪实时）
THEME_COMMODITY = {
    '石油': [('hf_CL', 'WTI原油'), ('hf_OIL', '布伦特原油')],
    '天然气': [('hf_NG', '天然气')],
    '贵金属': [('hf_GC', 'COMEX黄金'), ('hf_SI', 'COMEX白银')],
    '工业金属': [('hf_CAD', 'LME铜'), ('hf_AHD', 'LME铝')],
}

def _fetch_tencent(codes):
    url = 'https://qt.gtimg.cn/q=' + ','.join(codes)
    ctx = ssl.create_default_context()
    op = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx),
                                     urllib.request.ProxyHandler({}))
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Referer':'https://gu.qq.com/'})
    with op.open(req, timeout=15) as r:
        return r.read().decode('gbk', 'replace')

def get_stock_quotes(codes):
    """返回 {code: {name, price, chg, chg_pct, high, low, turnover}}"""
    raw = _fetch_tencent(codes)
    out = {}
    for m in re.finditer(r'v_(\w+)="([^"]*)"', raw):
        code, data = m.group(1), m.group(2)
        p = data.split('~')
        if len(p) < 45: continue
        try:
            out[code] = {
                'name': p[1], 'price': float(p[3]) if p[3] else None,
                'prev': float(p[4]) if p[4] else None,
                'open': float(p[5]) if p[5] else None,
                'chg': float(p[31]) if len(p)>31 and p[31] else None,
                'chg_pct': float(p[32]) if len(p)>32 and p[32] else None,
                'high': float(p[33]) if len(p)>33 and p[33] else None,
                'low': float(p[34]) if len(p)>34 and p[34] else None,
                'turnover_pct': float(p[38]) if len(p)>38 and p[38] else None,
                'pe': float(p[39]) if len(p)>39 and p[39] else None,
                'pb': float(p[46]) if len(p)>46 and p[46] else None,
            }
        except (ValueError, IndexError):
            pass
    return out

def _fetch_sina_hf():
    """新浪外盘期货（WTI/布伦特/金/银/铜/天然气）"""
    codes = [c for lst in THEME_COMMODITY.values() for c,_ in lst]
    url = 'https://hq.sinajs.cn/list=' + ','.join(codes)
    ctx = ssl.create_default_context()
    op = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx),
                                     urllib.request.ProxyHandler({}))
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Referer':'https://finance.sina.com.cn/'})
    with op.open(req, timeout=15) as r:
        return r.read().decode('gbk', 'replace')

def get_commodity_quotes():
    """新浪外盘期货。实测格式（2026-10-28）：
       var hq_str_hf_CL="101.184,,101.150,101.170,101.430,99.750,10:39:07,99.900,100.170,0,4,5,2026-10-28,纽约原油,0"
       字段: [0]最新价 [1]空 [2]买价 [3]卖价 [4]最高 [5]最低 [6]时间 [7]昨收 [8]开盘
             [9][10][11] [12]日期 [13]中文名 [14]
       涨跌幅 = (最新价/昨收 - 1) × 100
    """
    out = {}
    try:
        raw = _fetch_sina_hf()
        for m in re.finditer(r'var hq_str_(\w+)="([^"]*)"', raw):
            code, data = m.group(1), m.group(2)
            p = data.split(',')
            if len(p) < 14: continue
            try:
                price = float(p[0]) if p[0] else None
                prev  = float(p[7]) if len(p)>7 and p[7] else None
                high  = float(p[4]) if len(p)>4 and p[4] else None
                low   = float(p[5]) if len(p)>5 and p[5] else None
                name  = p[13] if len(p)>13 and p[13] else code
                chg_pct = round((price/prev - 1)*100, 2) if (price and prev and prev>0) else None
                chg_amt = round(price - prev, 3) if (price and prev) else None
                out[code] = {'name': name, 'price': price, 'prev': prev,
                             'chg_pct': chg_pct, 'chg_amt': chg_amt,
                             'high': high, 'low': low}
            except (ValueError, IndexError):
                pass
    except Exception as e:
        print(f'    [警告] 商品行情失败: {type(e).__name__}')
    return out

def collect_market_context(topics):
    """根据新闻主题，收集相关标的行情（用于 AI 分析）"""
    codes = []
    names = {}
    for t in topics:
        for c, n in THEME_STOCKS.get(t, []):
            if c not in codes:
                codes.append(c); names[c] = n
    if not codes:
        return {}

    stocks = get_stock_quotes(codes)
    comms = get_commodity_quotes() if any(t in THEME_COMMODITY for t in topics) else {}

    ctx = {'stocks': [], 'commodities': []}
    for c in codes:
        if c in stocks:
            s = stocks[c]
            if s.get('price'):
                ctx['stocks'].append({
                    'name': names.get(c, s['name']), 'code': c[2:],
                    'price': s['price'], 'chg_pct': s.get('chg_pct'),
                })
    for t in topics:
        for c, n in THEME_COMMODITY.get(t, []):
            if c in comms:
                cm = comms[c]
                ctx['commodities'].append({
                    'name': n or cm.get('name'), 'price': cm.get('price'),
                    'chg_pct': cm.get('chg_pct'), 'chg_amt': cm.get('chg_amt'),
                    'high': cm.get('high'), 'low': cm.get('low'),
                })
    return ctx

if __name__ == '__main__':
    print('=== 测试：石油主题的关联标的 ===')
    ctx = collect_market_context(['石油'])
    print('  A股:')
    for s in ctx['stocks']:
        print(f"    {s['name']}({s['code']}) {s['price']}  {s['chg_pct']:+.2f}%")
    print('  商品:')
    for c in ctx['commodities']:
        print(f"    {c['name']} {c['price']}  {c['chg_pct'] if c['chg_pct'] is not None else '?'}%")

    print()
    print('=== 测试：贵金属 ===')
    ctx = collect_market_context(['贵金属'])
    for s in ctx['stocks'][:4]:
        print(f"    {s['name']}({s['code']}) {s['price']}  {s['chg_pct']:+.2f}%")
    for c in ctx['commodities']:
        print(f"    {c['name']} {c['price']}")
