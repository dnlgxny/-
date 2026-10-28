"""AI 事件说明：用 DeepSeek 生成「事件本质 + 影响判断 + 确定性标注」"""
import os, json, time, urllib.request, ssl, re

def get_key():
    p = os.path.expanduser('~/.dsh/.credentials.yaml')
    for line in open(p, encoding='utf-8'):
        if 'DEEPSEEK_API_KEY' in line:
            return line.split(':',1)[1].strip().strip('"').strip("'")
    return None

KEY = get_key()

def call(prompt, max_tokens=2000, retries=2):
    if not KEY: raise RuntimeError('无 DEEPSEEK_API_KEY')
    body = json.dumps({
        'model': 'deepseek-chat',
        'messages': [{'role':'user','content':prompt}],
        'temperature': 0.3,
        'max_tokens': max_tokens,
    }).encode()
    ctx = ssl.create_default_context()
    op = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx),
                                     urllib.request.ProxyHandler({}))
    for i in range(retries+1):
        try:
            req = urllib.request.Request('https://api.deepseek.com/chat/completions',
                data=body, headers={'Content-Type':'application/json',
                                    'Authorization': f'Bearer {KEY}'})
            with op.open(req, timeout=120) as r:
                d = json.loads(r.read().decode())
            return d['choices'][0]['message']['content'].strip(), d.get('usage',{})
        except Exception as e:
            if i == retries: raise
            time.sleep(4)

PROMPT_TMPL = '''你是资深大宗商品分析师。请为下面每条新闻生成【事件说明】，**必须结合我给出的实际行情数据**。

**铁律（违反即作废）：**
1. **所有数字必须来自我提供的数据或新闻原文**，绝对不得编造价格、涨跌幅、机构、时间
2. 写涨跌幅时必须标明是「A股」还是「国际期货」，不得混淆
3. 若我未提供某品种数据，就写"暂无该品种数据"，不得猜测
4. 只说明事件性质与市场影响机制，**不给买卖建议**

**输出格式（严格一行，用 | 分隔）：**
编号|事件本质（20字内，说清发生了什么）|数据佐证（35字内，必须含具体数字）|影响判断（35字内，说清影响什么品种、往哪方向）|确定性（高/中/低）

**确定性判定：**
- 高 = 新闻有明确数据/官方表态，且行情数据可验证
- 中 = 新闻属报道但细节不全，或行情与新闻方向不一致（背离）
- 低 = 市场传闻、预期、或原文信息模糊

---
**当前实际行情（{data_time}）：**
{market_data}
---

**新闻列表：**
{items}'''

def format_market_data(ctx, dt_str):
    """把行情上下文格式化成文本"""
    lines = []
    if ctx.get('stocks'):
        parts = []
        for s in ctx['stocks']:
            chg = f"{s['chg_pct']:+.2f}%" if s.get('chg_pct') is not None else '—'
            parts.append(f"{s['name']}({s['code']}) {s['price']}  {chg}")
        lines.append('A股：' + '；'.join(parts))
    if ctx.get('commodities'):
        parts = []
        for c in ctx['commodities']:
            chg = f"{c['chg_pct']:+.2f}%" if c.get('chg_pct') is not None else '—'
            parts.append(f"{c['name']} {c['price']}  {chg}")
        lines.append('国际期货：' + '；'.join(parts))
    return '\n'.join(lines) if lines else '（本次无关联行情数据）'


def analyze_batch(items, batch_size=5, market_ctx=None, data_time=''):
    """批量生成事件说明（含真实行情佐证）"""
    done = 0
    md_text = format_market_data(market_ctx or {}, data_time)
    for bi in range(0, len(items), batch_size):
        batch = items[bi:bi+batch_size]
        lines = []
        for k, it in enumerate(batch):
            lines.append(f"[{k}] 标题: {it['title']}")
            if it.get('desc_zh'): lines.append(f"[{k}] 摘要: {it['desc_zh'][:200]}")
            elif it.get('desc'): lines.append(f"[{k}] 摘要: {it['desc'][:200]}")
        prompt = PROMPT_TMPL.format(items='\n'.join(lines), market_data=md_text, data_time=data_time or '实时')
        try:
            res, usage = call(prompt, max_tokens=1600)
            for line in res.split('\n'):
                line=line.strip()
                if not line or '|' not in line: continue
                p=[x.strip() for x in line.split('|')]
                if len(p)<5: continue
                try: idx=int(p[0].replace('[','').replace(']','').split('.')[0])
                except: continue
                if 0<=idx<len(batch):
                    batch[idx]['event'] = p[1]
                    batch[idx]['data_note'] = p[2] if len(p)>2 else ''
                    batch[idx]['impact'] = p[3] if len(p)>3 else ''
                    batch[idx]['certainty'] = p[4] if len(p)>4 and p[4] in ('高','中','低') else '中'
            ok=sum(1 for x in batch if x.get('event'))
            done+=ok
            print(f'    批次 {bi//batch_size+1}: {ok}/{len(batch)} 条 ({usage.get("total_tokens",0)} tokens)')
        except Exception as e:
            print(f'    批次 {bi//batch_size+1} 失败: {type(e).__name__}: {str(e)[:60]}')
        time.sleep(0.8)
    return items, done

if __name__ == '__main__':
    print('测试事件说明生成：')
    test=[{'title':'OPEC+ Set to Keep Oil Quotas Unchanged',
           'desc_zh':'消息人士称，OPEC+主要产油国周日会议预计维持12月产量配额不变。'}]
    r,done = analyze_batch(test, 1)
    for x in r:
        print('  事件本质:', x.get('event'))
        print('  影响判断:', x.get('impact'))
        print('  确定性:', x.get('certainty'))
