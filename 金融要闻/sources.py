"""金融要闻 · 数据源定义（2026-10-28 实测可用）"""
import re, html

# 实测可用的源（2026-10-28）
SOURCES = [
    {
        'id': 'oilprice', 'name': 'OilPrice.com', 'lang': 'en',
        'url': 'https://oilprice.com/rss/main',
        'ua': 'Mozilla/5.0',
        'desc': '油价/能源专业媒体，条目含完整摘要',
    },
    {
        'id': 'mining', 'name': 'Mining.com', 'lang': 'en',
        'url': 'https://www.mining.com/feed/',
        'ua': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/131 Safari/537.36',
        'desc': '矿业/金属专业媒体（金、铜、锂、银）',
    },
    {
        'id': 'eia', 'name': 'EIA Today in Energy', 'lang': 'en',
        'url': 'https://www.eia.gov/rss/todayinenergy.xml',
        'ua': 'Mozilla/5.0',
        'desc': '美国能源署官方，权威数据解读',
    },
    {
        'id': 'eia_press', 'name': 'EIA Press Releases', 'lang': 'en',
        'url': 'https://www.eia.gov/rss/press_rss.xml',
        'ua': 'Mozilla/5.0',
        'desc': '美国能源署新闻稿',
    },
    # ── AI 内容（2026-11-10 新增）──
    {
        'id': 'tc_ai', 'name': 'TechCrunch AI', 'lang': 'en',
        'url': 'https://techcrunch.com/category/artificial-intelligence/feed/',
        'ua': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/131 Safari/537.36',
        'desc': 'AI 产业新闻（融资/模型/芯片）',
    },
    {
        'id': 'ieee_ai', 'name': 'IEEE Spectrum AI', 'lang': 'en',
        'url': 'https://spectrum.ieee.org/feeds/topic/artificial-intelligence.rss',
        'ua': 'Mozilla/5.0',
        'desc': 'AI 技术深度（IEEE 官方）',
    },
]

# 实物物资关键词（用于过滤 + 评分）
TOPIC_KEYWORDS = {
    # ══ 三大保留类别（2026-11-17 用户指定：只要 AI、石油、贵金属）══
    'AI': ['artificial intelligence', ' ai ', 'ai-', 'llm', 'large language model',
           'openai', 'anthropic', 'machine learning', 'agentic', 'generative ai',
           'chatgpt', 'gemini', 'claude', 'model release', 'ai model'],
    '石油': ['oil', 'crude', 'petroleum', 'opec', 'barrel', 'wti', 'brent',
             'refin', 'gasoline', 'diesel', 'shale', 'pipeline'],
    '贵金属': ['gold', 'silver', 'platinum', 'palladium', 'precious metal', 'bullion'],

    # ══ 以下仅用于 AI×物资 交叉识别，不单独作为栏目 ══
    '_电力': ['electricity', 'power grid', 'grid capacity', 'utility company',
              'power plant', 'natural gas', 'megawatt', 'gigawatt',
              'nuclear power', 'power demand', 'electricity demand',
              'energy consumption', 'data center power'],
    '_铜铝': ['copper', 'aluminum', 'aluminium', 'transformer'],
    '_芯片': ['chip', 'semiconductor', 'gpu', 'hbm', 'wafer', 'tsmc', 'foundry',
              'nvidia', 'data center', 'datacenter'],
}

# 重要性权重（用于评分）
IMPORTANCE = {
    'opec': 3, 'opec+': 3, 'sanctions': 3, 'war': 3, 'embargo': 3,
    'supply cut': 3, 'production cut': 3, 'record high': 2, 'record low': 2,
    'surge': 2, 'plunge': 2, 'soar': 2, 'crash': 2, 'spike': 2,
    'inventor': 2, 'demand': 1, 'forecast': 1, 'outlook': 1,
    'price': 1, 'market': 1,
}

def kw_match(text, kw):
    """关键词匹配：^ 前缀表示需要词边界（避免 tin 匹配 continuing）"""
    text_l = text.lower()
    if kw.startswith('^'):
        pat = kw[1:]
        # 用正则词边界
        return re.search(r'\b' + re.escape(pat.strip()) + r'\b', text_l) is not None
    return kw in text_l


def clean_text(s):
    """清洗 HTML/实体/空白"""
    if not s: return ''
    s = re.sub(r'<!\[CDATA\[|\]\]>', '', s)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = html.unescape(s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()
