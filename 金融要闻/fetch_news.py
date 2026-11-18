"""抓取 + 过滤 + 评分（不含翻译，先验证）"""
import sys, os, re, json, ssl, urllib.request, datetime, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sources import SOURCES, TOPIC_KEYWORDS, IMPORTANCE, clean_text, kw_match

def fetch(url, ua, timeout=20):
    h = {'User-Agent': ua}
    ctx = ssl.create_default_context()
    op = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx),
                                     urllib.request.ProxyHandler({}))
    with op.open(urllib.request.Request(url, headers=h), timeout=timeout) as r:
        return r.read().decode('utf-8', 'replace')

def parse_rss(xml, src):
    """解析 RSS 2.0"""
    items = []
    for m in re.finditer(r'<item[^>]*>(.*?)</item>', xml, re.S):
        raw = m.group(1)
        def get(tag):
            mm = re.search(rf'<{tag}[^>]*>(.*?)</{tag}>', raw, re.S)
            return clean_text(mm.group(1)) if mm else ''
        title = get('title')
        link = get('link')
        desc = get('description')
        date = get('pubDate')
        if not title or not link: continue
        items.append(dict(title=title, link=link, desc=desc, date=date,
                          source=src['name'], source_id=src['id']))
    return items

# AI 与实物物资的关联关键词（用于交叉加权）
# ⚠️ 只保留「能直接指向实物需求」的词，避免 power/energy 这类泛词造成误判
#    例：「AI empowers small business」不应判为电力需求
AI_COMMODITY_LINK = {
    '电力': ['electricity', 'power grid', 'grid capacity', 'utility company',
             'power plant', 'natural gas', 'megawatt', 'gigawatt',
             'nuclear power', 'power demand', 'electricity demand',
             'energy consumption', 'data center power'],
    '铜铝': ['copper', 'aluminum', 'aluminium', 'transformer'],
    '芯片': ['chip', 'semiconductor', 'gpu', 'hbm', 'wafer', 'tsmc', 'foundry',
             'nvidia', 'data center', 'datacenter'],
}

def classify(title, desc):
    """匹配主题分类"""
    text = (title + ' ' + desc).lower()
    hits = []
    for topic, kws in TOPIC_KEYWORDS.items():
        if topic.startswith('_'):
            continue          # 私有键只用于交叉识别，不作为栏目
        if any(kw_match(text, k) for k in kws):
            hits.append(topic)
    return hits


def ai_commodity_link(title, desc):
    """判断 AI 新闻是否与实物物资相关（返回关联类型列表）
    仅当新闻含 AI 关键词 且 含物资关键词时才返回，用于交叉加权。
    """
    text = (title + ' ' + desc).lower()
    ai_kws = TOPIC_KEYWORDS['AI']
    if not any(kw_match(text, k) for k in ai_kws):
        return []
    links = []
    for name, kws in AI_COMMODITY_LINK.items():
        if any(kw_match(text, k) for k in kws):
            links.append(name)
    return links

def score(item, topics):
    """评分 1-10（2026-11-17 重设计）

    ⚠️ 设计原则：本工作台关注「实物物资 + AI 算力对物资的传导」
       纯 AI 概念文章（如「AI 是否有意识」「如何把 AI 融入产品」）
       对物资无影响，必须低分，不能因为出现 AI 字样就得高分。

    评分锚点（先定档，再微调）：
      10 = 重大供给冲击/政策突变，直接影响价格（OPEC 减产、制裁、战争断供）
       9 = 重要价格事件（暴涨暴跌 >5%、库存大幅超预期、大矿停产）
       8 = 明确的需求/供应变化（数据中心电力大单、矿企扩产、央行购金）
       7 = 行业重要动态（财报超预期、产能规划、政策表态）
       6 = 有价值但影响有限（一般行业新闻、技术进展）
       5 = 背景信息（趋势判断、分析观点）
       4 = 弱相关（提到物资但非核心）
     1-3 = 与物资无关（AI 伦理/产品/论文/教程等）

    关键约束：topics 若只有「AI」且无 AI×物资交叉 → 最高 6 分
    """
    text = (item['title'] + ' ' + item['desc']).lower()
    tl = item['title'].lower()
    detail = []
    links = item.get('ai_links') or []
    is_ai_only = (topics == ['AI']) and not links

    # ══ ① 强供给冲击信号（决定 9-10 分）══
    supply_shock = [
        'opec+ cut', 'production cut', 'output cut', 'supply cut', 'embargo',
        'sanction', 'invasion', 'war', 'attack', 'strike', 'blockade',
        'halt', 'shut down', 'shutdown', 'force majeure', 'outage',
        'record high', 'record low', 'all-time high', 'all-time low',
    ]
    hits = [w for w in supply_shock if w in text]

    # ══ ② 价格异动幅度（标题里出现百分比）══
    import re as _re
    pcts = [float(x) for x in _re.findall(r'(\d+(?:\.\d+)?)\s*%', item['title'])]
    big_move = max(pcts) if pcts else 0

    # ══ ③ 需求侧信号（AI→物资传导的核心）══
    demand_signal = [
        'data center', 'datacenter', 'power purchase', 'electricity demand',
        'energy demand', 'buy.*turbine', 'megawatt', 'gigawatt',
        'capacity expansion', 'new mine', 'production increase',
        'central bank', 'reserve', 'etf inflow', 'inventory draw',
    ]
    d_hits = [w for w in demand_signal if _re.search(w, text)]

    # ══ 定档 ══
    base = 5
    if len(hits) >= 2 and (big_move >= 3 or links):
        base = 10; detail.append(f'多重供给冲击（{",".join(hits[:3])}）')
    elif hits and big_move >= 5:
        base = 10; detail.append(f'供给冲击+价格异动{big_move}%')
    elif hits:
        base = 9; detail.append(f'供给冲击（{",".join(hits[:2])}）')
    elif big_move >= 5:
        base = 9; detail.append(f'价格异动{big_move}%')
    elif d_hits and links:
        base = 8; detail.append(f'需求信号+物资传导（{",".join(d_hits[:2])}）')
    elif links:
        base = 8; detail.append(f'AI×物资传导（{"／".join(links)}）')
    elif d_hits:
        base = 7; detail.append(f'需求信号（{",".join(d_hits[:2])}）')
    elif big_move >= 2:
        base = 7; detail.append(f'价格变动{big_move}%')
    elif topics and topics != ['AI']:
        base = 6; detail.append(f'物资主题（{"／".join(topics)}）')

    # ══ 微调（±1，不跨越档位太多）══
    adj = 0
    # 时效：6h 内 +1
    try:
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(item['date'])
        age_h = (datetime.datetime.now(datetime.timezone.utc) - dt).total_seconds()/3600
        item['_age_h'] = age_h
        if age_h <= 6:   adj += 1; detail.append('6h内+1')
        elif age_h > 72: adj -= 1; detail.append('超3天-1')
    except Exception:
        pass
    # 多主题（跨物资类）+1
    real_topics = [t for t in topics if not t.startswith('_')]
    if len(real_topics) >= 2:
        adj += 1; detail.append('多物资主题+1')
    # 标题直接点名物资 +1
    if any(kw_match(tl, k) for t in ('石油','贵金属') for k in TOPIC_KEYWORDS[t]):
        adj += 1; detail.append('标题含物资+1')

    # ══ 硬约束：纯 AI 文章封顶 6 分 ══
    if is_ai_only:
        base = min(base, 6)
        adj = min(adj, 0)   # 不给加分
        detail.append('纯AI无物资关联→封顶6')

    sc = max(1, min(10, base + adj))
    return int(sc), detail


def main():
    all_items = []
    print('='*70)
    print('抓取测试')
    print('='*70)
    for src in SOURCES:
        try:
            xml = fetch(src['url'], src['ua'])
            items = parse_rss(xml, src)
            print(f"  {src['name']:<24} ✅ {len(items)} 条")
            all_items.extend(items)
        except Exception as e:
            print(f"  {src['name']:<24} ❌ {type(e).__name__}: {str(e)[:60]}")

    print(f'\n  合计 {len(all_items)} 条')

    # 分类 + 评分
    for it in all_items:
        it['topics'] = classify(it['title'], it['desc'])
        it['score'], it['score_detail'] = score(it, it['topics'])
        it['id'] = hashlib.md5(it['link'].encode()).hexdigest()[:12]

    # 只保留与实物物资相关的
    relevant = [x for x in all_items if x['topics']]
    print(f'  实物物资相关: {len(relevant)} 条')
    print()

    # 去重（按标题相似）
    seen = set(); uniq = []
    for x in sorted(relevant, key=lambda y:-y['score']):
        key = re.sub(r'[^a-z0-9]', '', x['title'].lower())[:60]
        if key in seen: continue
        seen.add(key); uniq.append(x)
    print(f'  去重后: {len(uniq)} 条')
    print()

    print('='*70)
    print('Top 15（按评分）')
    print('='*70)
    for k, it in enumerate(uniq[:15], 1):
        print(f"\n{k:2d}. [{it['score']:3d}分] {it['title'][:72]}")
        print(f"    来源: {it['source']} | 主题: {'/'.join(it['topics'])}")
        if it['desc']:
            print(f"    摘要: {it['desc'][:100]}")
        print(f"    评分依据: {'; '.join(it['score_detail'])}")

    json.dump(uniq, open('out_raw.json','w'), ensure_ascii=False, indent=1)
    print(f'\n→ out_raw.json（{len(uniq)} 条）')

if __name__ == '__main__':
    os.makedirs('.', exist_ok=True)
    main()
