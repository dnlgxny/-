"""用 DeepSeek 生成「宏观新闻研究」报告（中文）

参考 TradingAgents 新闻分析师的结构：
  1. 执行摘要
  2. 利率与政策 — 主导驱动因素
  3. 通胀与增长
  4. AI 综合体新闻
  5. 地缘政治叠加
  6. 数据缺口
  7. 关键要点汇总表
"""
import json, os, ssl, time, urllib.request

def _key():
    k = os.environ.get('DEEPSEEK_API_KEY', '').strip()
    if k: return k
    p = os.path.expanduser('~/.dsh/.credentials.yaml')
    if os.path.exists(p):
        for line in open(p, encoding='utf-8'):
            if 'DEEPSEEK_API_KEY' in line:
                return line.split(':', 1)[1].strip().strip('"').strip("'")
    return None


def call(prompt, max_tokens=4000, retries=5):
    K = _key()
    if not K: raise RuntimeError('无 DEEPSEEK_API_KEY')
    body = json.dumps({
        'model': 'deepseek-chat',
        'messages': [{'role': 'user', 'content': prompt}],
        'temperature': 0.2,
        'max_tokens': max_tokens,
    }).encode()
    ctx = ssl.create_default_context()
    op = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx),
                                     urllib.request.ProxyHandler({}))
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request('https://api.deepseek.com/chat/completions',
                data=body, headers={'Content-Type': 'application/json',
                                    'Authorization': f'Bearer {K}'})
            with op.open(req, timeout=180) as r:
                d = json.loads(r.read().decode())
            return d['choices'][0]['message']['content'].strip()
        except Exception as e:
            last = e
            code = getattr(e, 'code', None)
            if i == retries - 1 or code in (401, 402):
                raise
            wait = 4 * (2 ** i)
            print(f'      重试 {i+1}/{retries}（{code}）等 {wait}s', flush=True)
            time.sleep(wait)
    raise last


PROMPT = '''你是资深宏观研究员。基于**下面提供的真实数据**，撰写一份「宏观新闻研究」报告。

**铁律（违反即无效）：**
1. **所有数字必须来自我提供的数据或新闻原文**，绝对不得编造
2. 数据缺失的项，明确写「数据未取到」，不得用记忆或推测填充
3. 区分「已确认事实」与「市场预期/推测」
4. **只陈述事实与分析机制，不给买卖建议**（不出现"建议买入/减仓/目标价"等）
5. 用简体中文，保留数字与代码原文

**输出结构（严格按此 7 节，Markdown 格式）：**

```
# 宏观新闻研究

## 1. 执行摘要
（3-4 句概括：当前宏观环境的核心矛盾是什么，对股票市场（尤其科技股）意味着什么）

## 2. 利率与政策 — 主导驱动因素
（表格 + 分析：10Y/2Y 收益率、期限利差、联邦基金利率。说明当前利率环境对估值的影响机制）

## 3. 通胀与增长
（表格 + 分析：CPI/核心PCE/失业率/非农。说明通胀趋势与增长动能）

## 4. AI 综合体新闻
（基于提供的新闻，梳理 AI/半导体/数据中心相关的关键事件，说明其对产业链的影响）

## 5. 地缘政治叠加
（基于新闻中的地缘事件，如中东、中美关系等）

## 6. 数据缺口
（诚实列出本次未取到的数据及影响）

## 7. 关键要点汇总表
（| 维度 | 现状 | 数据 | 对市场的影响机制 |）
```

---
**真实数据如下：**

### 宏观指标
{macro}

### 美股指数现状
{index}

### 今日新闻（Finnhub）
{news}
'''


def build_macro_text(macro):
    lines = ['| 指标 | 最新值 | 日期 | 前值 |', '|---|---:|---|---:|']
    for sid, v in macro.items():
        if 'error' in v: continue
        prev = v.get('prev')
        lines.append(f"| {v['name']}（{sid}） | {v['latest']} {v['unit']} | {v['latest_date']} | {prev if prev is not None else '—'} |")
    return '\n'.join(lines)


def build_index_text(idx):
    if not idx: return '（未取到）'
    lines = [f"- 纳指100 收盘：{idx.get('close')}（{idx.get('date')}）",
             f"- 日涨跌：{idx.get('chg')}",
             f"- RSI14：{idx.get('rsi')}",
             f"- MA200：{idx.get('ma200')}　MA250：{idx.get('ma250')}",
             f"- 距峰回撤：{idx.get('drawdown')}"]
    return '\n'.join(lines)


def build_news_text(news_items, limit=25):
    if not news_items: return '（未取到新闻）'
    out = []
    for i, a in enumerate(news_items[:limit], 1):
        t = a.get('time', '')
        h = a.get('headline', '')
        s = (a.get('summary') or '')[:150]
        out.append(f"{i}. [{t}] {h}")
        if s: out.append(f"   {s}")
    return '\n'.join(out)


def analyze(macro, index_data, news_items):
    prompt = PROMPT.format(
        macro=build_macro_text(macro),
        index=build_index_text(index_data),
        news=build_news_text(news_items),
    )
    return call(prompt, max_tokens=4500)
