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
    {
        'id': 'sa', 'name': 'Seeking Alpha', 'lang': 'en',
        'url': 'https://seekingalpha.com/market_currents.xml',
        'ua': 'Mozilla/5.0',
        'desc': '市场快讯（含商品相关）',
    },
]

# 实物物资关键词（用于过滤 + 评分）
TOPIC_KEYWORDS = {
    '石油': ['oil', 'crude', 'petroleum', 'opec', 'barrel', 'wti', 'brent', 'refin', 'gasoline', 'diesel'],
    '天然气': ['natural gas', 'lng', 'gas price', 'henry hub'],
    '贵金属': ['gold', 'silver', 'platinum', 'palladium', 'precious metal', 'bullion'],
    '工业金属': ['copper', 'aluminum', 'aluminium', 'zinc', 'nickel', 'iron ore', 'steel',
                '^lead ', '^tin ', '^lead$', '^tin$'],   # lead/tin 需词边界，避免匹配 Latin/continuing
    '锂/电池金属': ['lithium', 'cobalt', 'graphite', 'rare earth', 'battery metal'],
    '农产品': ['wheat', 'corn', 'soybean', 'coffee', 'sugar', 'cocoa', 'cotton'],
    '煤炭': ['coal', 'thermal coal', 'coking coal'],
    '铀': ['uranium', 'nuclear fuel'],
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
