#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
读书笔记用：从 Winter 发来的欧路外挂词典（MDict 的 .mdx 文件）里查词，当写笔记时的参照本。

2026-09-26 Winter：「我比较喜欢用牛津第九版的那个词典，柯林斯也不错……有个参照本的话
相对来说会比较专业一点。」她每开一个新对话会把 .mdx 重新传一遍。

    pip install mdict-utils          # 每个新会话装一次
    python3 tools/reading/dict_lookup.py <词典.mdx> [<另一本.mdx> …] -w slug converge "hunker down"

- 只需要 .mdx（释义）；.mdd 是发音和图片，不用传。
- ⚠️ 词典文件绝不进仓库（仓库是公开的，那是人家的词典）：只放在会话的临时目录里。
- 笔记里只借用很短的一句英文释义（卡片上标出处），别整条照搬。
- 查不到原形时自己去掉词尾再查一次（throbs → throb）。
"""
import argparse, html, re, sys

try:
    from mdict_utils.base.readmdict import MDX
except ImportError:
    sys.exit('先装：pip install mdict-utils')


def load(path):
    d = {}
    for k, v in MDX(path).items():
        k = k.decode('utf-8', 'ignore').strip()
        v = v.decode('utf-8', 'ignore')
        d.setdefault(k.lower(), []).append(v)
    return d


def plain(h):
    h = re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>', ' ', h)
    h = re.sub(r'(?i)<br\s*/?>|</(p|div|li|h\d)>', '\n', h)
    h = html.unescape(re.sub(r'<[^>]+>', ' ', h))
    h = re.sub(r'[ \t]+', ' ', h)
    return re.sub(r'\n\s*\n+', '\n', h).strip()


def lookup(d, word, depth=0):
    out = []
    for v in d.get(word.lower(), []):
        m = re.match(r'@@@LINK=(.+)', v.strip())
        if m and depth < 3:          # 词典里的跳转条目（变形 → 原形）
            out += lookup(d, m.group(1).strip(), depth + 1)
        else:
            out.append(plain(v))
    return out


def main():
    ap = argparse.ArgumentParser(description='从 .mdx 词典里查词')
    ap.add_argument('mdx', nargs='+')
    ap.add_argument('-w', '--words', nargs='+', required=True)
    ap.add_argument('-n', '--max', type=int, default=4000, help='每条最多打印多少字（默认 4000）')
    a = ap.parse_args()
    for path in a.mdx:
        d = load(path)
        print(f'━━━━ {path}（{len(d)} 个词头）')
        for w in a.words:
            hits = lookup(d, w)
            print(f'\n── {w}' + ('' if hits else '　（查不到）'))
            for h in hits:
                print(h[:a.max])


if __name__ == '__main__':
    main()
