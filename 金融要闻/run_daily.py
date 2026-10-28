"""金融要闻 · 每日更新主流程"""
import sys, os, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_news import fetch, parse_rss, classify, score
from sources import SOURCES
from translate import translate_batch
from ai_analyze import analyze_batch
from market_data import collect_market_context

def main():
    print('='*72)
    print('金融要闻 · 每日更新  ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
    print('='*72)

    all_items = []
    print('\n[1] 抓取')
    for src in SOURCES:
        try:
            xml = fetch(src['url'], src['ua'])
            items = parse_rss(xml, src)
            print(f"    {src['name']:<24} ✅ {len(items)} 条")
            all_items.extend(items)
        except Exception as e:
            print(f"    {src['name']:<24} ❌ {type(e).__name__}: {str(e)[:50]}")

    print(f'\n[2] 分类 + 评分')
    import hashlib
    for it in all_items:
        it['topics'] = classify(it['title'], it['desc'])
        it['score'], it['score_detail'] = score(it, it['topics'])
        it['id'] = hashlib.md5(it['link'].encode()).hexdigest()[:12]

    relevant = [x for x in all_items if x['topics']]
    print(f'    实物物资相关: {len(relevant)}/{len(all_items)} 条')

    # 去重
    seen=set(); uniq=[]
    for x in sorted(relevant, key=lambda y:-y['score']):
        key=''.join(c for c in x['title'].lower() if c.isalnum())[:60]
        if key in seen: continue
        seen.add(key); uniq.append(x)
    print(f'    去重后: {len(uniq)} 条')

    # 限制数量（按评分取前 N）
    TOP_N = 40
    keep = uniq[:TOP_N]
    print(f'    保留评分前 {len(keep)} 条')

    print(f'\n[3] 翻译（{len(keep)} 条）')
    keep = translate_batch(keep, batch_size=6)

    # 收集所有涉及主题的行情
    all_topics = sorted({t for it in keep for t in (it.get('topics') or [])})
    print(f'\n[4] 收集关联行情（主题: {"/".join(all_topics)}）')
    market_ctx = collect_market_context(all_topics)
    print(f'    A股 {len(market_ctx.get("stocks",[]))} 只，商品 {len(market_ctx.get("commodities",[]))} 个')
    for st in market_ctx.get('stocks', [])[:5]:
        chg = f"{st['chg_pct']:+.2f}%" if st.get('chg_pct') is not None else '—'
        print(f"      {st['name']}({st['code']}) {st['price']} {chg}")
    for cm in market_ctx.get('commodities', [])[:5]:
        chg = f"{cm['chg_pct']:+.2f}%" if cm.get('chg_pct') is not None else '—'
        print(f"      {cm['name']} {cm['price']} {chg}")

    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    print(f'\n[5] AI 事件说明（含数据佐证，{len(keep)} 条）')
    keep, done = analyze_batch(keep, batch_size=5, market_ctx=market_ctx, data_time=now_str)
    print(f'    完成 {done}/{len(keep)} 条')

    # 时效性统计
    import datetime as _dt
    now = _dt.datetime.now(_dt.timezone.utc)
    for it in keep:
        try:
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(it['date'])
            it['age_hours'] = round((now - dt).total_seconds()/3600, 1)
        except Exception:
            it['age_hours'] = None

    fresh = sum(1 for it in keep if it.get('age_hours') is not None and it['age_hours'] <= 24)
    print(f'    24h 内新鲜新闻: {fresh}/{len(keep)} 条')

    print(f'\n[6] 输出 _data/news.json（{len(keep)} 条）')
    out = {
        'generatedAt': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
        'total': len(keep),
        'sources': [s['name'] for s in SOURCES],
        'market': market_ctx,
        'marketTime': now_str,
        'items': keep,
    }
    os.makedirs('_data', exist_ok=True)
    json.dump(out, open('_data/news.json','w'), ensure_ascii=False, indent=1)

    # 摘要打印
    print()
    print('='*72)
    print('Top 10 预览')
    print('='*72)
    for k, it in enumerate(keep[:10], 1):
        t = it.get('title_zh') or it['title']
        d = it.get('desc_zh') or ''
        print(f"\n{k:2d}. [{it['score']}分/{it.get('certainty','?')}] {t}")
        print(f"    {'/'.join(it['topics'])} · {it['source']}")
        if it.get('event'): print(f"    事件: {it['event']}")
        if it.get('data_note'): print(f"    数据: {it['data_note']}")
        if it.get('impact'): print(f"    影响: {it['impact']}")
        print(f"    {it['link'][:88]}")

if __name__ == '__main__':
    main()
