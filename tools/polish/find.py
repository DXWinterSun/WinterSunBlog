#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查波兰语笔记本：她问的这个，以前问过没有？

    python3 tools/polish/find.py kawy                # 搜一个词
    python3 tools/polish/find.py 生格 否定            # 空格分开的几个词要全部对上
    python3 tools/polish/find.py --id 007            # 看一条的全部内容
    python3 tools/polish/find.py --points            # 列出分类和每类几条
    python3 tools/polish/find.py --all               # 全部笔记的编号和标题

- 不分大小写，不管字母上的小符号（搜 zolw 能找到 żółw，搜 kawe 能找到 kawę）。
- 精确对不上时，会把四个字母以上的词去掉词尾再试一次（kawę → kaw，能对上 kawa / kawy），
  这一批标成「可能相关」——波兰语词尾变来变去，同一个词在笔记里常常是另一个样子。
"""
import argparse, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from render_polish import DATA, as_list, fold, plain, search_text, times, cn_date   # noqa: E402

import yaml                                                                         # noqa: E402


def load():
    data = yaml.safe_load(open(DATA, encoding='utf-8')) or {}
    points = {}
    for a in data.get('areas') or []:
        for p in a.get('points') or []:
            points[f'{a["key"]}.{p["key"]}'] = (a, p)
    return data, points, data.get('notes') or []


def where(x, points):
    a, p = points[x['point']]
    return f'{a["name"]} › {p["name"]}'


def line(x, points):
    n = times(x)
    again = f' · 🔁 问过 {n} 次' if n > 1 else ''
    return f'  No. {x["id"]} · {cn_date(x["date"])}{again} · {where(x, points)} · {plain(x["title"])}'


def show(x, points):
    print(line(x, points).strip())
    for k in ('ask', 'pl', 'en', 'zh', 'mine'):
        if x.get(k):
            print(f'  {k}: {plain(x[k])}')
    for r in as_list(x.get('right')):
        print(f'  right: {plain(r)}')
    print('  why:\n    ' + plain(x['why']).replace('\n', '\n    '))
    if x.get('rule'):
        print(f'  rule: {plain(x["rule"])}')
    if x.get('asked'):
        print('  又问过：' + '、'.join(cn_date(d) for d in as_list(x['asked'])))
    for q in as_list(x.get('qa')):
        print(f'  问：{plain(q["q"])}\n  答：{plain(q["a"])}')


def main():
    ap = argparse.ArgumentParser(description='查波兰语笔记本')
    ap.add_argument('words', nargs='*')
    ap.add_argument('--id')
    ap.add_argument('--points', action='store_true')
    ap.add_argument('--all', action='store_true')
    a = ap.parse_args()
    data, points, notes = load()
    meta = data.get('meta') or {}

    if a.points:
        cnt = {}
        for x in notes:
            cnt[x['point']] = cnt.get(x['point'], 0) + 1
        for ar in data.get('areas') or []:
            print(f'{ar["icon"]} {ar["name"]}（{ar["key"]}）')
            for p in ar.get('points') or []:
                k = f'{ar["key"]}.{p["key"]}'
                print(f'    {k:<16} {p["name"]}' + (f'  ← {cnt[k]} 条' if k in cnt else ''))
        return
    if a.id:
        xs = [x for x in notes if str(x['id']) == a.id.zfill(3)]
        if not xs:
            sys.exit(f'没有 No. {a.id}')
        show(xs[0], points)
        return
    if a.all or not a.words:
        print(f'笔记本里一共 {len(notes)} 条；网页 {meta.get("artifact") or "（还没发布）"}')
        for x in notes:
            print(line(x, points))
        return

    terms = [fold(w) for w in a.words]
    hay = {x['id']: search_text(x, points) for x in notes}
    exact = [x for x in notes if all(t in hay[x['id']] for t in terms)]
    stems = [t[:-2] if len(t) >= 6 else t[:-1] if len(t) >= 4 else t for t in terms]
    near = [x for x in notes if x not in exact and all(s in hay[x['id']] for s in stems)]
    if exact:
        print(f'✅ 对上了 {len(exact)} 条：')
        for x in exact:
            print(line(x, points))
    if near:
        print(f'🤔 可能相关 {len(near)} 条（去掉词尾后对上的，自己看一眼是不是一回事）：')
        for x in near:
            print(line(x, points))
    if not exact and not near:
        print('没找到——没问过（也可以换个说法再搜一次：原形、中文、知识点名）。')
    if meta.get('artifact') and (exact or near):
        print(f'网页：{meta["artifact"]}')


if __name__ == '__main__':
    main()
