#!/usr/bin/env python3
"""上线用：python3 .claude/bibles/everything-in-transit-revised/assemble.py [--dry] [--date="YYYY-MM-DD HH:MM:SS"]
把 .claude/bibles/everything-in-transit-revised/chN.md 换进 _posts/，按 v2 章号重命名，旧网址进 redirect_from。"""
import os, re, glob, sys, yaml, datetime
os.chdir('/home/user/WinterSunBlog')
REV = '.claude/bibles/everything-in-transit-revised'
NOW = next((a.split('=',1)[1] for a in sys.argv if a.startswith('--date=')), None) or datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')
old = {}
for f in glob.glob('_posts/*-everything-in-transit-chapter-*.md'):
    n = int(re.search(r'chapter-(\d+)-', f).group(1)); old[n] = f
# v2 章号 -> 旧文件号列表（空 = 新写）
MAP = {1:[1],2:[2],3:[3],4:[]}
for v in range(5, 28): MAP[v] = [v-1]
MAP[28] = [27, 28]; MAP[29] = [29]; MAP[30] = [30]; MAP[31] = [31]; MAP[32] = []
NEW_SLUG = {4: 'a-month-of-beer', 32: 'the-best-of-everything'}

def split(path):
    t = open(path, encoding='utf-8').read()
    _, fm, body = t.split('---', 2)
    return yaml.safe_load(fm), body.lstrip('\n')

def url_of(f):
    fm, _ = split(f)
    d = re.search(r'^date:\s*(\d{4}-\d\d-\d\d)', open(f, encoding='utf-8').read(), re.M).group(1).split('-')
    slug = re.sub(r'^\d{4}-\d\d-\d\d-', '', os.path.basename(f))[:-3]
    return f'/{d[0]}/{d[1]}/{d[2]}/{slug}/'

def q(s): return '"' + s.replace('"', '\\"') + '"'

plan = []
for v, olds in sorted(MAP.items()):
    src = f'{REV}/ch{v}.md'
    if not os.path.exists(src): sys.exit(f'缺 {src}')
    new_fm, body = split(src)
    if olds:
        base = old[olds[0]]; bfm, _ = split(base)
        date = re.search(r'^date:\s*(.+)$', open(base, encoding='utf-8').read(), re.M).group(1).strip(); prefix = os.path.basename(base)[:10]
        slug = re.sub(r'^everything-in-transit-chapter-\d+-', '', re.sub(r'^\d{4}-\d\d-\d\d-', '', os.path.basename(base))[:-3])
        redirects = list(bfm.get('redirect_from') or [])
        for o in olds:
            u = url_of(old[o]); 
            if u not in redirects and not (o == v and len(olds) == 1): redirects.append(u)
        image = bfm.get('image', 'rob-cove-au.jpeg')
    else:
        date = NOW + ' +0800'; prefix = NOW[:10]; slug = NEW_SLUG[v]; redirects = []; image = 'rob-cove-au.jpeg'
    newfile = f'_posts/{prefix}-everything-in-transit-chapter-{v}-{slug}.md'
    if olds and len(olds) == 1 and olds[0] == v:
        pass  # 章号没变，网址不变
    lines = ['---', 'layout: post', f'title: {q(new_fm["title"])}', f'date: {date}', f'image: {image}',
             'tags: [' + ', '.join(new_fm['tags']) + ']', 'categories: ["AU Story"]',
             'series: "Everything in Transit"', 'series_title: "Everything in Transit · Rob Cove AU"',
             f'series_order: {v}', 'series_status: ongoing', 'series_type: Series', f'chapter_type: Chapter {v}',
             f'summary: {q(new_fm["summary"])}']
    if redirects:
        lines.append('redirect_from:'); lines += [f'  - {r}' for r in redirects]
    lines.append('---')
    plan.append((newfile, [old[o] for o in olds], '\n'.join(lines) + '\n\n' + body.rstrip() + '\n'))

if '--dry' in sys.argv:
    for nf, ofs, _ in plan: print(nf, '<-', ofs)
    sys.exit()
for nf, ofs, text in plan:
    for o in ofs:
        if os.path.exists(o): os.system(f'git rm -q "{o}"')
for nf, ofs, text in plan:
    open(nf, 'w', encoding='utf-8').write(text)
print('写入', len(plan), '章')
