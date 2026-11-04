#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""💿 冬的碟柜：往 _data/discs.json 里记一张 CD（顺手把官方封面存进 discs/covers/）。

    python3 tools/discs/add.py --album "Teraz" --artist "Lady Pank" --year 2004 \
        --ver "波兰版 · BMG Poland · 1 CD" --status 全新 --memo "录音室版的 Stacja Warszawa 只在这张上" \
        --cover-url "https://…/600x600bb.jpg"            # 或 --cover-file 本地图
    python3 tools/discs/add.py --list                     # 看柜里有什么
    python3 tools/discs/add.py --edit lady-pank-teraz --memo "……"   # 改一张（只改给的字段）
    python3 tools/discs/add.py --rm lady-pank-teraz       # 删一张

封面一律用官方专辑图（iTunes 搜索接口的 artworkUrl100 把 100x100bb 换成 600x600bb 就是大图），
她拍的照片只用来认是哪张、哪一版。封面放 discs/covers/ 不放 images/，免得惊动对脸机器人。
"""
import argparse
import datetime as dt
import io
import json
import os
import re
import sys
import unicodedata
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, '_data', 'discs.json')
COVERS = os.path.join(ROOT, 'discs', 'covers')


def slug(s):
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    s = s.replace('ł', 'l').replace('Ł', 'L')
    s = re.sub(r'[^A-Za-z0-9]+', '-', s).strip('-').lower()
    return s or 'disc'


def load():
    return json.load(open(DATA, encoding='utf-8'))


def save(d):
    json.dump(d, open(DATA, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    open(DATA, 'a', encoding='utf-8').write('\n')


def save_cover(src_url, src_file, name):
    from PIL import Image
    if src_url:
        req = urllib.request.Request(src_url, headers={'User-Agent': 'Mozilla/5.0'})
        raw = urllib.request.urlopen(req, timeout=60).read()
        im = Image.open(io.BytesIO(raw))
    else:
        im = Image.open(src_file)
    im = im.convert('RGB')
    w, h = im.size
    if w != h:  # 裁成正方形（居中）
        m = min(w, h)
        im = im.crop(((w - m) // 2, (h - m) // 2, (w - m) // 2 + m, (h - m) // 2 + m))
    if im.size[0] > 600:
        im = im.resize((600, 600), Image.LANCZOS)
    os.makedirs(COVERS, exist_ok=True)
    out = os.path.join(COVERS, name)
    im.save(out, 'JPEG', quality=86, optimize=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--album'); ap.add_argument('--artist'); ap.add_argument('--year', type=int)
    ap.add_argument('--ver', help='版本：哪国版 · 发行公司 · 几 CD · 小册子'); ap.add_argument('--status', help='全新 / 签名 / 盒子裂了……（没写全新就是二手）')
    ap.add_argument('--memo', help='她的一句碎碎念（原话）'); ap.add_argument('--wall', help='唱片墙上那张专辑的 id（自动按名字对得上就不用写）')
    ap.add_argument('--cover-url'); ap.add_argument('--cover-file'); ap.add_argument('--id')
    ap.add_argument('--list', action='store_true'); ap.add_argument('--edit'); ap.add_argument('--rm')
    a = ap.parse_args()
    d = load()
    items = d.setdefault('items', [])

    if a.list:
        for it in items:
            print('%-28s %-26s %-14s %s  [%s]%s' % (it['id'], it['album'], it['artist'], it.get('year') or '', it.get('status') or '', ' 墙' if it.get('wall') else ''))
        print('共 %d 张' % len(items)); return
    if a.rm:
        n = len(items); d['items'] = [it for it in items if it['id'] != a.rm]
        if len(d['items']) == n: raise SystemExit('没有这张：' + a.rm)
        save(d); print('✓ 删了', a.rm); return
    if a.edit:
        it = next((x for x in items if x['id'] == a.edit), None)
        if not it: raise SystemExit('没有这张：' + a.edit)
        for k in ('album', 'artist', 'year', 'ver', 'status', 'memo', 'wall'):
            v = getattr(a, k)
            if v is not None: it[k] = v
        if a.cover_url or a.cover_file:
            it['cover'] = it['id'] + '.jpg'; save_cover(a.cover_url, a.cover_file, it['cover'])
        save(d); print('✓ 改了', it['id']); return

    if not (a.album and a.artist):
        raise SystemExit('至少要 --album 和 --artist')
    sid = a.id or slug(a.artist + ' ' + a.album)
    if any(x['id'] == sid for x in items):
        raise SystemExit('已经有这张了：%s（要改就 --edit %s）' % (sid, sid))
    it = {'id': sid, 'album': a.album, 'artist': a.artist, 'year': a.year, 'cover': None,
          'ver': a.ver or '', 'status': a.status or '', 'memo': a.memo or '', 'added': dt.date.today().isoformat()}
    if a.wall: it['wall'] = a.wall
    if a.cover_url or a.cover_file:
        it['cover'] = sid + '.jpg'; save_cover(a.cover_url, a.cover_file, it['cover'])
    items.append(it); save(d)
    print('✓ 记上了：%s — %s（%s）%s' % (it['artist'], it['album'], it.get('year') or '年份未知', '，封面存在 discs/covers/' + it['cover'] if it['cover'] else '，还没封面'))


if __name__ == '__main__':
    main()
