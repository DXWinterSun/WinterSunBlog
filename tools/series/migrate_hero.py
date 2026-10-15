#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把系列首页里手写的 hero 区块搬进 front matter（2026-10-15 系列页改版）。

改版后系列页的页头（杂志头 → 满幅封面 → 色带 → 基调）全部由 _layouts/series.html 渲染，
系列首页只负责写 front matter 和「关于这个系列 / 设定档案」两段。这个脚本把老文件里
<section class="c-hero">…</section> 的四样东西抽出来写进 front matter：

    hero_eyebrow: "AU Story · Series"        眉标
    hero_title:   "Just Go Ahead Now"         大标题（英文；可含 <em>）
    byline:       "角色 · 作品 · 演员"          署名（状态那一段不写，模板从 series_status 取）
    lede:         "一句引言"                   情感引言（不带引号符号，模板会加）

然后把整个 hero 区块删掉。只对还含有 c-hero 区块的文件动手，跑第二遍是空操作。

    python3 tools/series/migrate_hero.py            # 真改
    python3 tools/series/migrate_hero.py --dry      # 只打印抽出来的东西
"""
import glob, html, re, sys

DRY = '--dry' in sys.argv
STATUS = {'ongoing', 'complete', 'hiatus', 'oneshot'}

def yq(s):
    """YAML 双引号值：值里不能有 ASCII 双引号（会截断），有就换成弯引号。"""
    s = s.replace('"', '“')
    return '"%s"' % s

def clean(s):
    s = html.unescape(s).replace('&middot;', '·')
    s = re.sub(r'\s+', ' ', s).strip()
    return s

changed = 0
for f in sorted(glob.glob('series/*/index.html')):
    src = open(f, encoding='utf-8').read()
    m = re.search(r'\n*<section class="c-hero[^"]*">.*?</section>\n*', src, re.S)
    if not m:
        continue
    hero = m.group(0)
    eyebrow = re.search(r'<div class="c-hero__eyebrow">(.*?)</div>', hero, re.S)
    title = re.search(r'<h1 class="c-hero__title">(.*?)</h1>', hero, re.S)
    byline = re.search(r'<span class="c-hero__byline-text">(.*?)</span>', hero, re.S)
    lede = re.search(r'<p class="c-hero__lede">(.*?)</p>', hero, re.S)
    if not (eyebrow and title and byline and lede):
        print('!! 结构不齐，跳过', f); continue
    eyebrow_t = clean(eyebrow.group(1))
    title_t = clean(title.group(1))
    parts = [p.strip() for p in clean(byline.group(1)).replace('&middot;', '·').split('·')]
    if parts and parts[-1].split()[0] in STATUS:
        parts = parts[:-1]
    byline_t = ' · '.join(parts)
    lede_t = re.sub(r'<span class="c-hero__quote[^"]*">.*?</span>', '', lede.group(1), flags=re.S)
    lede_t = clean(re.sub(r'<[^>]+>', '', lede_t))
    lede_t = lede_t.strip('“”"')
    if DRY:
        print(f, '|', eyebrow_t, '|', title_t, '|', byline_t, '|', lede_t[:30]); continue
    fm_end = src.index('\n---', 4)
    fm = src[:fm_end]
    add = ('\n# —— 页头（2026-10-15 起由 _layouts/series.html 渲染，不再手写 hero）——\n'
           'hero_eyebrow: %s\nhero_title: %s\nbyline: %s\nlede: %s' % (yq(eyebrow_t), yq(title_t), yq(byline_t), yq(lede_t)))
    out = fm + add + src[fm_end:]
    out = out.replace(hero, '\n\n', 1)
    open(f, 'w', encoding='utf-8').write(out)
    changed += 1
print('changed', changed)
