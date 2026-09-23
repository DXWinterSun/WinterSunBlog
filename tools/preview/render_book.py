#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多章「合订本」预览页生成器（一次给 Winter 看好几章时用）

2026-09-23 Winter 改了工作方式：**「比起你写一章我核对一下再接着写，我想你直接按大纲
写个十几篇，我一起看，省得我要一直盯着了。」** 一章一张预览页就不够用了——这个脚本把
一批草稿排成一本：顶上一张目录（点了跳到那一章），下面一章接一章，配色仍按该 AU 取。

单章交付照旧用 `render_draft.py`（它是那张页的唯一样板，别动它）；这个脚本直接复用
它的 markdown 渲染与配色，只换外壳。

    python3 tools/preview/render_book.py \
        --series "The Ball He Couldn't Reach" \
        --kicker "The Ball He Couldn't Reach · Brad Cairn AU" \
        --title  "第一批 · 第 1–6 章" \
        --notes  衔接说明.md \
        -o /tmp/.../合订本.html \
        ch1.md:1:没人问过那血是哪来的:悸动·暗涌 \
        ch2.md:2:门口那只空狗碗:怅惘·暗涌

每个 source 的格式是 `文件路径:章号:中文章名:mood`（后三段可省，省了就只显示文件名）。
mood 里的分隔符随便写，会原样显示。

⚠️ 改稿后**用同一个 `-o` 路径重新生成、重新发布**，链接不变，她刷新即看新版。
⚠️ 草稿一写完就先落盘到 `.claude/bibles/<series-slug>-drafts/`，别只留在会话临时目录里。
"""
import os, sys, re, html, argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_draft import palette, to_html, CSS          # noqa: E402  复用样板脚本

EXTRA_CSS = '''
<style>
/* ── 合订本外壳（在 render_draft 的样式之后加载，只补不覆盖） ── */
.toc{margin:2.4rem 0 3.4rem;border:1px solid color-mix(in srgb,var(--accent) 26%,transparent);
 border-radius:4px;padding:1.2rem 1.4rem;background:color-mix(in srgb,var(--accent) 5%,transparent);}
.toc h2{margin:0 0 .9rem;font-family:"EB Garamond",Georgia,serif;font-style:italic;
 font-size:1.05rem;color:var(--accent);letter-spacing:.04em;font-weight:600;}
.toc ol{list-style:none;margin:0;padding:0;display:grid;gap:.55rem;}
.toc li{display:grid;grid-template-columns:auto 1fr auto;gap:.8rem;align-items:baseline;}
.toc a{color:var(--ink);text-decoration:none;border-bottom:1px solid transparent;
 font-size:1.02rem;}
.toc a:hover,.toc a:focus{border-bottom-color:var(--accent);}
.toc .num{font-family:"EB Garamond",Georgia,serif;font-size:.8rem;color:var(--accent);
 letter-spacing:.1em;font-variant-numeric:tabular-nums;}
.toc .md{font-family:"EB Garamond",Georgia,serif;font-size:.74rem;color:var(--muted);
 letter-spacing:.1em;white-space:nowrap;}
.chap{margin-top:4.5rem;scroll-margin-top:1.5rem;}
.chap:first-of-type{margin-top:3rem;}
.chap__head{text-align:center;margin-bottom:2.2rem;}
.chap__n{font-family:"EB Garamond",Georgia,serif;font-size:.78rem;letter-spacing:.3em;
 color:var(--accent);text-transform:uppercase;}
.chap__t{font-family:"Volkhov","Noto Serif SC",Georgia,serif;font-weight:700;
 font-size:clamp(22px,4vw,30px);margin:.5rem 0 .3rem;line-height:1.3;text-wrap:balance;}
.chap__m{font-family:"EB Garamond",Georgia,serif;font-size:.78rem;letter-spacing:.14em;
 color:var(--muted);margin:0;}
.chap__rule{width:56px;height:1px;background:var(--accent);opacity:.6;margin:1.3rem auto 0;}
.backtop{display:block;text-align:center;margin-top:2.6rem;font-family:"EB Garamond",Georgia,serif;
 font-size:.76rem;letter-spacing:.18em;color:var(--muted);text-decoration:none;}
.backtop:hover{color:var(--accent);}
.sep{border:0;border-top:1px solid color-mix(in srgb,var(--ink) 14%,transparent);
 margin:4.2rem 0 0;}
</style>
'''


def parse_src(spec):
    """`路径:章号:章名:mood` —— 路径里可能带冒号（绝对路径不会），从右边切。"""
    parts = spec.split(':')
    path = parts[0]
    n = parts[1] if len(parts) > 1 else ''
    title = parts[2] if len(parts) > 2 else os.path.basename(path)
    mood = parts[3] if len(parts) > 3 else ''
    return path, n, title, mood


def main():
    ap = argparse.ArgumentParser(description='把好几章草稿排成一本合订本预览页')
    ap.add_argument('sources', nargs='+', help='每个写成 路径:章号:中文章名:mood')
    ap.add_argument('-o', '--out', required=True)
    ap.add_argument('--title', required=True, help='整本的大标题，如「第一批 · 第 1–6 章」')
    ap.add_argument('--series', default='', help='series_name，用于取该 AU 配色')
    ap.add_argument('--kicker', default='', help='大标题上方那行斜体系列名')
    ap.add_argument('--sub', default='', help='大标题下面那行中文副标')
    ap.add_argument('--notes', default='', help='页尾衔接说明（.md 或 .html）')
    ap.add_argument('--eyebrow', default='草稿 / 待冬璇过目')
    a = ap.parse_args()

    pal = palette(a.series)
    css = CSS
    for k, v in pal.items():
        css = css.replace(f'__{k.upper()}__', v)

    chaps, toc, total = [], [], 0
    for i, spec in enumerate(a.sources, 1):
        path, n, title, mood = parse_src(spec)
        src = open(path, encoding='utf-8').read()
        if src.lstrip().startswith('---'):
            src = src.split('---', 2)[2]
        body = to_html(src)
        total += len(re.sub(r'<[^>]+>|\s', '', body))
        cid = 'ch%d' % i
        label = ('Chapter %s' % n) if n else ('第 %d 篇' % i)
        toc.append('<li><span class="num">%s</span>'
                   '<a href="#%s">%s</a><span class="md">%s</span></li>'
                   % (html.escape(n or str(i)), cid, html.escape(title), html.escape(mood)))
        chaps.append(
            '<section class="chap" id="%s">\n'
            '  <header class="chap__head"><p class="chap__n">%s</p>'
            '<h2 class="chap__t">%s</h2><p class="chap__m">%s</p>'
            '<div class="chap__rule"></div></header>\n%s\n'
            '  <a class="backtop" href="#top">↑ 回目录</a>\n</section>\n<hr class="sep">'
            % (cid, html.escape(label), html.escape(title), html.escape(mood), body))

    foot = ''
    if a.notes:
        raw = open(a.notes, encoding='utf-8').read()
        foot = raw if a.notes.endswith(('.html', '.htm')) else to_html(raw)
        foot = '<div class="foot">%s</div>' % foot

    cells = ['<span><b>状态</b> · %s</span>' % html.escape(a.eyebrow)]
    if a.series:
        cells.append('<span><b>系列</b> · %s</span>' % html.escape(a.series))
    cells.append('<span><b>本批</b> · %d 章 / 约 %s 字</span>'
                 % (len(a.sources), format(total, ',')))
    console = '<div class="console"><span class="dot"></span>%s</div>' % ''.join(cells)

    page = [
        '<title>%s</title>' % html.escape(a.kicker or a.title),
        css, EXTRA_CSS,
        '<div class="wrap" id="top">',
        console,
        ('<p class="kicker">%s</p>' % html.escape(a.kicker)) if a.kicker else '',
        '<h1>%s</h1>' % html.escape(a.title),
        ('<div class="sub">%s</div>' % html.escape(a.sub)) if a.sub else '',
        '<div class="toc"><h2>这一批</h2><ol>%s</ol></div>' % ''.join(toc),
        '\n'.join(chaps),
        foot,
        '</div>',
    ]
    open(a.out, 'w', encoding='utf-8').write('\n'.join(x for x in page if x) + '\n')
    print('✅ %s（%d 章 / %s 字 / 配色 %s）'
          % (a.out, len(a.sources), format(total, ','), a.series or '默认'))


if __name__ == '__main__':
    main()
