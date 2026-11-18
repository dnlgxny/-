"""把 TradingAgents 英文报告翻译成中文（分段调用 DeepSeek）"""
import json, os, re, ssl, sys, time, urllib.request

KEY = os.getenv('DEEPSEEK_API_KEY', '')

def call(prompt, max_tokens=8000, retries=5):
    body = json.dumps({
        'model': 'deepseek-chat',
        'messages': [{'role': 'user', 'content': prompt}],
        'temperature': 0.1,
        'max_tokens': max_tokens,
    }).encode()
    ctx = ssl.create_default_context()
    op = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx),
                                     urllib.request.ProxyHandler({}))
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(
                'https://api.deepseek.com/chat/completions', data=body,
                headers={'Content-Type': 'application/json',
                         'Authorization': f'Bearer {KEY}'})
            with op.open(req, timeout=180) as r:
                d = json.loads(r.read().decode())
            return d['choices'][0]['message']['content'].strip()
        except Exception as e:
            last = e
            code = getattr(e, 'code', None)
            if i == retries - 1 or code in (401, 402):
                raise
            wait = 4 * (2 ** i)
            print(f'    重试 {i+1}/{retries}（{code}）等 {wait}s', flush=True)
            time.sleep(wait)
    raise last

SYS = '''你是金融报告翻译专家。把英文美股分析报告翻译成简体中文。

**铁律：**
1. **保留 Markdown 结构**（# 标题、表格、列表、代码块原样保留）
2. **数字、日期、代码、指标名一律不译**：27,197.15 / 2026-11-16 / MACD / RSI / ATR / SMA / EMA / Bollinger / .NDX / NVDA 等
3. **专有名词保留英文并附中文**：如 Nvidia（英伟达）、Fed（美联储）
4. 术语准确：Underweight→低配、Overweight→超配、Hold→持有、drawdown→回撤、support→支撑、resistance→阻力
5. **不得增删原意**，不得添加原文没有的结论
6. 表格的列标题也要翻译，但表格内的数字/代码不动

只输出译文，不要任何解释或前后缀。'''

def translate(text, tag=''):
    prompt = f'{SYS}\n\n---\n待翻译内容：\n\n{text}'
    out = call(prompt, max_tokens=8000)
    # 去掉可能的 ```markdown 包裹
    out = re.sub(r'^```(?:markdown)?\s*\n', '', out)
    out = re.sub(r'\n```\s*$', '', out)
    return out

def main():
    src = os.path.expanduser('~/WorkBuddy/开源/工作台/美股分析/latest/complete_report.md')
    dst = os.path.expanduser('~/WorkBuddy/开源/工作台/美股分析/latest/complete_report_zh.md')
    t = open(src, encoding='utf-8').read()

    # 按二级标题切块，每块控制在 ~6000 字符
    parts = re.split(r'\n(?=## )', t)
    chunks, cur = [], ''
    for p in parts:
        if len(cur) + len(p) > 6000 and cur:
            chunks.append(cur); cur = p
        else:
            cur += ('\n' if cur else '') + p
    if cur: chunks.append(cur)

    print(f'共 {len(chunks)} 段，总 {len(t):,} 字符', flush=True)
    result = []
    for i, c in enumerate(chunks, 1):
        print(f'  翻译 {i}/{len(chunks)}（{len(c):,} 字符）...', flush=True)
        t0 = time.time()
        try:
            zh = translate(c, f'{i}')
            result.append(zh)
            print(f'    ✅ {time.time()-t0:.1f}s', flush=True)
        except Exception as e:
            print(f'    ❌ {type(e).__name__}: {str(e)[:80]}', flush=True)
            result.append(c)   # 失败保留原文
    open(dst, 'w', encoding='utf-8').write('\n\n'.join(result))
    print(f'\n✅ 已保存 {dst}', flush=True)

if __name__ == '__main__':
    main()
