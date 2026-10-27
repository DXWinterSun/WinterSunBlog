#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""📻 冬的电台：把 YouTube Music 上的公开歌单抓成 _data/radio_tracks.json。

    python3 tools/songs/sync_radio.py            # 按 _data/radio.yml 里的每个台抓一遍
    python3 tools/songs/sync_radio.py --station polski --url "https://music.youtube.com/playlist?list=PL…"

读 _data/radio.yml（台的名字 / 歌单链接 / 歌名英文小注 / 手工修正），用 yt-dlp 只取歌单的「目录」
（不下载任何音频），写出每首歌的 id / 歌名 / 艺人 / 时长 / 封面图地址。链接空着的台跳过、原样保留。
机器人每周跑一次（.github/workflows/radio-sync.yml）；有变化才提交。
"""
import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CFG = os.path.join(ROOT, '_data', 'radio.yml')
OUT = os.path.join(ROOT, '_data', 'radio_tracks.json')

# 歌名后面挂着的无用尾巴（官方视频 / 歌词版这类），去掉；「(Wersja 2012)」「(2014 Remastered)」这种版本说明留着
JUNK = re.compile(r'\s*[\(\[【](?:official|oficjaln\w*|teledysk|lyric\w*|audio|video|wideo|hd|hq|4k|visualizer|music video)[^\)\]】]*[\)\]】]',
                  re.I)


def list_id(url):
    m = re.search(r'[?&]list=([\w-]+)', url or '')
    return m.group(1) if m else (url or '').strip()


def fetch(url):
    """yt-dlp --flat-playlist -J：只要目录，不碰音频。"""
    cmd = [sys.executable, '-m', 'yt_dlp', '--flat-playlist', '-J', '--no-warnings', url]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if out.returncode != 0:
        raise SystemExit('yt-dlp 没抓到：%s\n%s' % (url, out.stderr[-800:]))
    return json.loads(out.stdout)


def clean_title(t):
    t = JUNK.sub('', t or '').strip()
    return re.sub(r'\s+', ' ', t)


def split_entry(e, fix):
    """从一条目录项里认出 歌名 / 艺人。YouTube Music 自己上传的曲目频道名是「艺人 - Topic」。"""
    vid = e.get('id') or ''
    ch = (e.get('channel') or e.get('uploader') or '').strip()
    title = clean_title(e.get('title'))
    artist = ''
    if ch.endswith(' - Topic'):
        artist = ch[:-len(' - Topic')].strip()
    elif ' - ' in title:
        a, t = title.split(' - ', 1)
        artist, title = a.strip(), t.strip()
    else:
        artist = ch
    if artist == 'Release - Topic' or artist == 'Various Artists':
        artist = ''
    f = (fix or {}).get(vid) or {}
    return {
        'id': vid,
        'title': f.get('title', title),
        'artist': f.get('artist', artist),
        'dur': int(e.get('duration') or 0),
        'thumb': 'https://i.ytimg.com/vi/%s/hqdefault.jpg' % vid if vid else '',
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--station', help='只抓这一个台（radio.yml 里的 id）')
    ap.add_argument('--url', help='临时指定歌单链接（不写回 radio.yml）')
    a = ap.parse_args()

    cfg = yaml.safe_load(open(CFG, encoding='utf-8')) or {}
    fix = cfg.get('fix') or {}
    data = {'stations': {}}
    if os.path.exists(OUT):
        try:
            data = json.load(open(OUT, encoding='utf-8'))
        except Exception:
            pass
    data.setdefault('stations', {})

    today = dt.date.today().isoformat()
    for st in cfg.get('stations') or []:
        sid = st['id']
        if a.station and sid != a.station:
            continue
        url = a.url if (a.url and (not a.station or sid == a.station)) else (st.get('url') or '')
        if not url:
            print('·', sid, '还没有歌单链接，跳过')
            continue
        lid = list_id(url)
        info = fetch('https://www.youtube.com/playlist?list=' + lid)
        tracks = [split_entry(e, fix) for e in (info.get('entries') or []) if e and e.get('id')]
        old = data['stations'].get(sid) or {}
        old_ids = [t.get('id') for t in old.get('tracks') or []]
        new_ids = [t['id'] for t in tracks]
        # 每首歌第一次出现的日子记下来（页面上「最近放进来的」靠它）
        seen = {t.get('id'): t.get('added') for t in old.get('tracks') or [] if t.get('added')}
        for t in tracks:
            t['added'] = seen.get(t['id']) or today
        changed = old_ids != new_ids
        data['stations'][sid] = {
            'list': lid,
            'title': info.get('title') or st.get('name'),
            'count': len(tracks),
            'duration': sum(t['dur'] for t in tracks),
            'synced': today,
            'tracks': tracks,
        }
        added = [t['title'] for t in tracks if t['id'] not in old_ids]
        gone = len([i for i in old_ids if i not in new_ids])
        print('✓ %s：%d 首%s%s' % (sid, len(tracks),
                                  ('，新来 %d 首：%s' % (len(added), ' / '.join(added[:6]))) if added else '',
                                  ('，少了 %d 首' % gone) if gone else ''))
        if not changed:
            print('  曲目没变。')
        # 没写英文小注的歌提醒一句，方便下个对话补
        gloss = cfg.get('gloss') or {}
        miss = [t['title'] for t in tracks if re.split(r'\s*\(', t['title'].lower())[0].strip() not in gloss]
        if miss:
            print('  还没写英文小注的：', ' / '.join(miss[:12]), ('… 共 %d 首' % len(miss)) if len(miss) > 12 else '')

    json.dump(data, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    open(OUT, 'a', encoding='utf-8').write('\n')


if __name__ == '__main__':
    main()
