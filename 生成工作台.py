#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成工作台单页 HTML（内联 ECharts + 内联数据）+ 发布包 dist/

用法：
    python3 拉数据.py        # ① 先拉数据（输出 _data/*.json）
    python3 生成工作台.py     # ② 生成 工作台.html 与 dist/

设计依据：工作台_设计确认稿-2026-10-14.md
  D1 图表库内联本地 assets/echarts.min.js（5.5.1），不用 CDN
  D3 单页 HTML，浅色白卡风

发布包 dist/ 结构（供 GitHub Pages 使用）：
  dist/index.html            成品页
  dist/manifest.webmanifest  PWA 清单
  dist/sw.js                 Service Worker
  dist/icons/*.png           图标
"""
import os
import re
import json
import shutil
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(HERE, '_data')
TPL = os.path.join(HERE, '_template.html')
OUT = os.path.join(HERE, '工作台.html')
DIST = os.path.join(HERE, 'dist')
ECHARTS = os.path.join(ROOT, 'assets', 'echarts.min.js')
ICONS = os.path.join(HERE, 'icons')


def load(name):
    p = os.path.join(DATA, name)
    if not os.path.exists(p):
        raise FileNotFoundError(f'缺少数据文件 {name}，请先运行 拉数据.py')
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def build_html():
    """生成成品 HTML 字符串"""
    if not os.path.exists(ECHARTS):
        raise FileNotFoundError(f'缺少 ECharts：{ECHARTS}')

    payload = {
        'generatedAt': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
        'ndx': load('ndx.json'),
        'vxn': load('vxn.json'),
        'vix': load('vix.json'),
        'cnn': load('cnn.json'),
        'danjuan': load('danjuan.json'),
        'danjuan_now': load('danjuan_now.json'),
        'dividend': load('dividend.json'),
        'weights': load('weights.json'),
        'indicators': load('indicators.json'),
        'footNote': '回撤口径：峰→谷单段｜起点 2002-10-09（互联网泡沫见底次日）',
    }

    with open(TPL, encoding='utf-8') as f:
        html = f.read()
    with open(ECHARTS, encoding='utf-8') as f:
        echarts_js = f.read()

    # 内联 ECharts（先替换 ECharts，再替换 payload，避免 </script> 干扰）
    html = html.replace('/*__ECHARTS__*/', echarts_js)
    js = json.dumps(payload, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
    html = html.replace('/*__PAYLOAD__*/', js)
    return html, payload


def bump_sw_version(dist, stamp):
    """把 sw.js 的 CACHE 版本换成新戳 —— 否则用户会一直拿到旧缓存"""
    p = os.path.join(dist, 'sw.js')
    if not os.path.exists(p):
        return
    with open(p, encoding='utf-8') as f:
        s = f.read()
    s = re.sub(r"const CACHE = 'openwork-[^']*'", f"const CACHE = 'openwork-{stamp}'", s)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(s)


def build_dist(stamp):
    """构造 GitHub Pages 发布目录"""
    if os.path.exists(DIST):
        shutil.rmtree(DIST)
    os.makedirs(os.path.join(DIST, 'icons'), exist_ok=True)

    # 图标
    n_icon = 0
    if os.path.isdir(ICONS):
        for fn in os.listdir(ICONS):
            if fn.endswith('.png'):
                shutil.copy2(os.path.join(ICONS, fn), os.path.join(DIST, 'icons', fn))
                n_icon += 1

    # manifest / sw
    for fn in ('manifest.webmanifest', 'sw.js'):
        src = os.path.join(HERE, fn)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(DIST, fn))

    bump_sw_version(DIST, stamp)

    # .nojekyll：GitHub Pages 默认跑 Jekyll，会忽略下划线开头文件；加上更稳
    open(os.path.join(DIST, '.nojekyll'), 'w').close()

    return n_icon


def main():
    html, payload = build_html()
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(html)

    stamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    n_icon = build_dist(stamp)
    shutil.copy2(OUT, os.path.join(DIST, 'index.html'))

    size = os.path.getsize(OUT)
    print(f'[OK] 已生成 {OUT}')
    print(f'     体积 {size:,} B（约 {size/1024/1024:.2f} MB，含内联 ECharts）')
    print(f'     指标序列 {len(payload["indicators"]["dates"])} 个交易日'
          f'（{payload["indicators"]["start"]} ~ {payload["indicators"]["end"]}）')
    print(f'     回撤段数 A/B/C = {payload["indicators"]["segCounts"]["A"]}'
          f'/{payload["indicators"]["segCounts"]["B"]}/{payload["indicators"]["segCounts"]["C"]}')
    print(f'[OK] 发布包 dist/（戳 {stamp}，{n_icon} 个图标）')
    for fn in sorted(os.listdir(DIST)):
        p = os.path.join(DIST, fn)
        if os.path.isdir(p):
            print(f'     {fn}/  ({len(os.listdir(p))} 个文件)')
        else:
            print(f'     {fn}  ({os.path.getsize(p):,} B)')


if __name__ == '__main__':
    main()

