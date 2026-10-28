"""DeepSeek 批量翻译（标题 + 摘要）"""
import os, json, time, urllib.request, ssl

def get_key():
    p = os.path.expanduser('~/.dsh/.credentials.yaml')
    for line in open(p, encoding='utf-8'):
        if 'DEEPSEEK_API_KEY' in line:
            return line.split(':',1)[1].strip().strip('"').strip("'")
    return None

KEY = get_key()

def call(prompt, max_tokens=800, retries=2):
    if not KEY: raise RuntimeError('无 DEEPSEEK_API_KEY')
    body = json.dumps({
        'model': 'deepseek-chat',
        'messages': [{'role':'user','content':prompt}],
        'temperature': 0.2,
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
            with op.open(req, timeout=90) as r:
                d = json.loads(r.read().decode())
            return d['choices'][0]['message']['content'].strip()
        except Exception as e:
            if i == retries: raise
            time.sleep(3)

def translate_batch(items, batch_size=6):
    """批量翻译：一次请求翻译多条，节省 token"""
    out = []
    total_usage = {'prompt_tokens':0,'completion_tokens':0}
    for bi in range(0, len(items), batch_size):
        batch = items[bi:bi+batch_size]
        lines = []
        for k, it in enumerate(batch):
            lines.append(f"[{k}] TITLE: {it['title']}")
            if it['desc']:
                lines.append(f"[{k}] DESC: {it['desc'][:300]}")
        prompt = (
            '你是财经翻译。把下面每条新闻翻译成简体中文。\n'
            '要求：\n'
            '1. 严格按输入编号顺序输出，每条一行，格式：编号|中文标题|中文摘要\n'
            '2. 摘要若超过100字请压缩到80字以内，突出「发生了什么、对价格什么影响」\n'
            '3. 专有名词保留英文（如 OPEC+、WTI、Brent、Aramco）\n'
            '4. 只输出结果，不要任何解释\n\n'
            + '\n'.join(lines)
        )
        try:
            res = call(prompt, max_tokens=1400)
            for line in res.split('\n'):
                line = line.strip()
                if not line or '|' not in line: continue
                parts = [x.strip() for x in line.split('|')]
                if len(parts) < 2: continue
                try: idx = int(parts[0].replace('[','').replace(']',''))
                except: continue
                if 0 <= idx < len(batch):
                    batch[idx]['title_zh'] = parts[1]
                    batch[idx]['desc_zh'] = parts[2] if len(parts) > 2 else ''
            print(f'    批次 {bi//batch_size+1}: {len(batch)} 条翻译完成')
        except Exception as e:
            print(f'    批次 {bi//batch_size+1} 失败: {type(e).__name__}: {str(e)[:60]}')
            for it in batch:
                it.setdefault('title_zh', '')
                it.setdefault('desc_zh', '')
        out.extend(batch)
        time.sleep(0.5)
    return out

if __name__ == '__main__':
    print('测试翻译：')
    test = [{'title':'OPEC+ Set to Keep Oil Quotas Unchanged','desc':'The key OPEC+ producers managing their collective oil production are expected to keep quotas unchanged.'}]
    r = translate_batch(test)
    for x in r:
        print('  标题:', x.get('title_zh'))
        print('  摘要:', x.get('desc_zh'))
