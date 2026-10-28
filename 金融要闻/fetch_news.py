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

def classify(title, desc):
    """匹配主题分类"""
    text = (title + ' ' + desc).lower()
    hits = []
    for topic, kws in TOPIC_KEYWORDS.items():
        if any(kw_match(text, k) for k in kws):
            hits.append(topic)
    return hits

def score(item, topics):
    """评分 0-100：主题相关 + 重要性词 + 摘要完整度 + 时效性"""
    text = (item['title'] + ' ' + item['desc']).lower()
    s = 0
    detail = []

    # ① 主题相关（最高 45 分）
    if topics:
        s += 25
        detail.append(f'主题匹配+25（{"/".join(topics)}）')
        if len(topics) >= 2:
            s += 10
            detail.append('多主题+10')
    else:
        detail.append('无主题匹配+0')

    # ② 标题含关键品种（最高 15 分）
    title_l = item['title'].lower()
    if any(kw_match(title_l, k) for kws in TOPIC_KEYWORDS.values() for k in kws):
        s += 15
        detail.append('标题含品种+15')

    # ③ 重要性词（最高 25 分）
    imp = 0
    found = []
    for w, wgt in IMPORTANCE.items():
        if w in text:
            imp += wgt
            found.append(w)
    imp = min(imp, 25)
    if imp: 
        s += imp
        detail.append(f'重要性词+{imp}（{",".join(found[:3])}）')

    # ④ 摘要完整度（最高 10 分）
    dl = len(item['desc'])
    if dl >= 200: s += 10; detail.append('摘要详实+10')
    elif dl >= 100: s += 6; detail.append('摘要有内容+6')
    elif dl >= 40: s += 3; detail.append('摘要简短+3')
    else: detail.append('摘要缺失+0')

    # ⑤ 时效性（最高 5 分，24h 内）
    try:
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(item['date'])
        age_h = (datetime.datetime.now(datetime.timezone.utc) - dt).total_seconds()/3600
        if age_h <= 24: s += 5; detail.append('24h内+5')
        elif age_h <= 72: s += 2; detail.append('3天内+2')
    except Exception:
        pass

    return min(s, 100), detail

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
