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
    '电力/天然气': ['electricity', 'power grid', 'grid capacity', 'utility company',
                    'power plant', 'natural gas', 'megawatt', 'gigawatt', 'terawatt',
                    'nuclear power', 'power demand', 'electricity demand',
                    'energy consumption', 'data center power'],
    '铜/铝': ['copper', 'aluminum', 'aluminium', 'wiring', 'transformer'],
    '贵金属': ['gold', 'silver', 'platinum', 'palladium'],
    '稀土/锂': ['rare earth', 'lithium', 'cobalt', 'magnet', 'battery metal'],
    '芯片/半导体': ['chip', 'semiconductor', 'gpu', 'hbm', 'wafer', 'tsmc', 'foundry'],
}


def classify(title, desc):
    """匹配主题分类"""
    text = (title + ' ' + desc).lower()
    hits = []
    for topic, kws in TOPIC_KEYWORDS.items():
        if any(kw_match(text, k) for k in kws):
            hits.append(topic)
    return hits


def ai_commodity_link(title, desc):
    """判断 AI 新闻是否与实物物资相关（返回关联类型列表）
    仅当新闻含 AI 关键词 且 含物资关键词时才返回，用于交叉加权。
    """
    text = (title + ' ' + desc).lower()
    ai_kws = TOPIC_KEYWORDS['AI/算力']
    if not any(kw_match(text, k) for k in ai_kws):
        return []
    links = []
    for name, kws in AI_COMMODITY_LINK.items():
        if any(kw_match(text, k) for k in kws):
            links.append(name)
    return links

def score(item, topics):
    """评分 1-10 分（1=最不重要，10=最重要）

    评分维度（加权求和后映射到 1-10）：
      ① 主题相关  权重 3.0  —— 是否属实物物资
      ② 标题品种  权重 2.0  —— 标题直接点名品种，关注度更高
      ③ 重要性词  权重 3.5  —— OPEC/制裁/战争/暴涨暴跌等
      ④ 摘要详实  权重 1.0  —— 信息量
      ⑤ 时效性    权重 1.5  —— 24h 内加分
    """
    text = (item['title'] + ' ' + item['desc']).lower()
    detail = []

    # ① 主题相关（0~3.0）
    w1 = 0.0
    if topics:
        w1 = 2.0
        detail.append(f'主题{"／".join(topics)}+2.0')
        if len(topics) >= 2:
            w1 += 1.0
            detail.append('多主题+1.0')
    else:
        detail.append('无主题+0')

    # ② 标题含品种（0~2.0）
    w2 = 0.0
    title_l = item['title'].lower()
    if any(kw_match(title_l, k) for kws in TOPIC_KEYWORDS.values() for k in kws):
        w2 = 2.0
        detail.append('标题含品种+2.0')

    # ②b AI × 实物物资 交叉加权（0~2.5）
    #     这是本工作台最关心的：AI 算力扩张如何影响电力/铜/天然气/稀土需求
    w2b = 0.0
    links = item.get('ai_links') or []
    if links:
        w2b = 2.0 if len(links) >= 2 else 1.5
        detail.append(f'AI×物资({"／".join(links)})+{w2b:.1f}')

    # ③ 重要性词（0~3.5）
    imp = 0.0
    found = []
    for w, wgt in IMPORTANCE.items():
        if w in text:
            imp += wgt * 0.35
            found.append(w)
    w3 = min(imp, 3.5)
    if w3 > 0:
        detail.append(f'重要性词+{w3:.1f}（{",".join(found[:3])}）')

    # ④ 摘要完整度（0~1.0）
    dl = len(item['desc'])
    w4 = 1.0 if dl >= 200 else (0.6 if dl >= 100 else (0.3 if dl >= 40 else 0.0))
    if w4: detail.append(f'摘要+{w4}')

    # ⑤ 时效性（0~1.5）
    w5 = 0.0
    try:
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(item['date'])
        age_h = (datetime.datetime.now(datetime.timezone.utc) - dt).total_seconds()/3600
        if age_h <= 6:        w5 = 1.5; detail.append('6h内+1.5')
        elif age_h <= 24:     w5 = 1.0; detail.append('24h内+1.0')
        elif age_h <= 72:     w5 = 0.4; detail.append('3天内+0.4')
    except Exception:
        pass

    raw = w1 + w2 + w2b + w3 + w4 + w5   # 满分 13.5（含 AI 交叉 2.5）
    # 映射到 1-10（2026-11-10 重校：加入 AI 源后整体分布上移，需重新锚定）
    #   raw < 3    → 1~4 分（弱相关）
    #   raw 3~6    → 4~6 分（一般）
    #   raw 6~9    → 6~8 分（重要）
    #   raw >= 9   → 8~10 分（重大）
    if raw < 3:      sc = 1 + raw * 1.0
    elif raw < 6:    sc = 4 + (raw - 3) * 0.67
    elif raw < 9:    sc = 6 + (raw - 6) * 0.67
    else:            sc = 8 + (raw - 9) * 0.45
    # ⑥ 重大事件加成（决定 9-10 分档）
    #    只有「多主题交叉 + 强重要性词 + 高时效」三者兼具才加，避免通胀
    strong_imp = any(w in text for w in
        ('opec', 'sanction', 'embargo', 'war', 'invasion', 'crisis', 'collapse',
         'plunge', 'crash', 'soar', 'surge', 'record high', 'record low',
         'supply cut', 'production cut', 'attack', 'strike'))
    bonus = 0
    if strong_imp and len(topics) >= 2 and w5 >= 1.0:
        bonus = 2; detail.append('重大事件+2（多主题+强词+快讯）')
    elif strong_imp and (len(topics) >= 2 or w2b >= 1.5):
        bonus = 1; detail.append('重要事件+1')
    sc += bonus

    sc = max(1, min(10, round(sc)))
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
