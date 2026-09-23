#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AU 系列「路线图」预览页生成器

CLAUDE.md 第 7 条：**每写完一章（以及开新坑时）先给下一段的路线图，别闷头往下写**。
样板就是这张页——一块案件板：三幕分段、章节排成格子、关键节点用该 AU 的主色标出来、
侧边挂着母题与伏笔账，最后放 2–3 个「她能凭喜好判断」的岔路（A/B/C）。
聊天里只给链接，别把整张表贴进聊天框。

    python3 tools/preview/render_roadmap.py .claude/roadmaps/<series>.json -o /tmp/.../路线图.html

⚠️ 配色直接写在 JSON 的 `_meta` 里（取该系列 au_palettes / 画册的四色），
所以每个系列的路线图长得都像它自己。单一深色设计，不跟随读者的明暗主题。

JSON 结构见 .claude/roadmaps/ 里的样板：
  _meta: title / eyebrow / sub / lede / accent,bg,text,muted / acts[] / motifs[] / debts[] / forks[]
  chapters: [{n, act(0..2), t 标题, w 这章干什么, key(1|2 关键度), pin(埋钩子), blank(空章)}]
"""
import json, html, argparse, os

E = lambda s: html.escape(s or '', quote=True)

TPL_CSS = """
:root{
  --bg:%(bg)s; --accent:%(accent)s; --text:%(text)s; --muted:%(muted)s;
  --panel:%(panel)s; --line:%(line)s; --ink-dim:%(dim)s;
  color-scheme:dark;
  --serif:"EB Garamond",Georgia,"Songti SC","Source Han Serif SC",serif;
  --mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace;
}
body{background:var(--bg);color:var(--text);font-family:var(--serif);line-height:1.75;
  -webkit-font-smoothing:antialiased;}
.wrap{max-width:52rem;margin:0 auto;padding-inline:16px;padding-block:2.6rem 4rem;}
.eyebrow{font-family:var(--mono);font-size:.64rem;letter-spacing:.24em;text-transform:uppercase;
  color:var(--accent);margin:0 0 .8rem;}
h1{font-size:clamp(1.8rem,6vw,2.8rem);font-weight:600;margin:0;letter-spacing:.01em;
  text-wrap:balance;line-height:1.15;}
.sub{margin:.5rem 0 0;font-family:var(--mono);font-size:.72rem;letter-spacing:.1em;color:var(--muted);}
.lede{margin:1.4rem 0 0;color:var(--text);opacity:.88;max-width:36em;}
.lede b{color:var(--accent);font-weight:600;}

.act{margin-top:3rem;}
.act__head{display:grid;grid-template-columns:auto 1fr;gap:.9rem;align-items:baseline;
  border-top:2px solid var(--accent);padding-top:1rem;}
.act__n{font-family:var(--mono);font-size:.7rem;letter-spacing:.14em;color:var(--bg);
  background:var(--accent);border-radius:2px;padding:.18rem .5rem;white-space:nowrap;}
.act__t{margin:0;font-size:1.35rem;font-weight:600;}
.act__d{margin:.6rem 0 0;grid-column:1/-1;color:var(--muted);font-size:.95rem;max-width:38em;}

.chs{list-style:none;margin:1.4rem 0 0;padding:0;display:grid;gap:.85rem;}
.ch{display:grid;grid-template-columns:auto 1fr;gap:.9rem;align-items:start;
  background:var(--panel);border:1px solid var(--line);border-radius:3px;padding:.85rem 1rem;}
.ch__n{font-family:var(--mono);font-size:.78rem;color:var(--muted);padding-top:.18rem;
  font-variant-numeric:tabular-nums;min-width:2.1rem;}
.ch__t{margin:0;font-size:1.05rem;font-weight:600;letter-spacing:.01em;}
.ch__w{margin:.25rem 0 0;color:var(--muted);font-size:.93rem;}
.ch--k1{border-color:color-mix(in srgb, var(--accent) 34%%, transparent);}
.ch--k2{border-color:var(--accent);background:color-mix(in srgb, var(--accent) 8%%, var(--panel));}
.ch--k2 .ch__t{color:var(--accent);}
.ch--k2 .ch__n{color:var(--accent);}
.ch--blank{border-style:dashed;background:transparent;}
.ch--blank .ch__t{color:var(--muted);font-style:italic;}
.pin{font-family:var(--mono);font-size:.56rem;letter-spacing:.1em;color:var(--bg);
  background:var(--accent);border-radius:2px;padding:.08rem .3rem;margin-left:.45rem;
  vertical-align:.18em;white-space:nowrap;}

.side{margin-top:3rem;display:grid;gap:1.6rem;grid-template-columns:1fr;}
@media (min-width:44rem){.side{grid-template-columns:1fr 1fr;}}
.box{border-top:1px solid var(--line);padding-top:1rem;}
.box h2{margin:0 0 .7rem;font-size:1.05rem;font-weight:600;}
.box ul{list-style:none;margin:0;padding:0;display:grid;gap:.5rem;}
.box li{font-size:.9rem;color:var(--muted);display:grid;grid-template-columns:auto 1fr;gap:.6rem;}
.box li::before{content:"·";color:var(--accent);}
.debt{display:grid;grid-template-columns:auto 1fr;gap:.6rem;align-items:start;}
.debt .k{font-family:var(--mono);font-size:.56rem;letter-spacing:.08em;padding:.12rem .34rem;
  border-radius:2px;white-space:nowrap;margin-top:.25rem;}
.debt .k--pin{color:var(--bg);background:var(--accent);}
.debt .k--def{color:var(--accent);border:1px solid var(--accent);}
.box li.debt::before{content:none;}

.ask{margin-top:3.6rem;border-top:2px solid var(--accent);padding-top:1.4rem;}
.ask h2{margin:0 0 .3rem;font-size:1.4rem;font-weight:600;}
.ask>p{margin:0 0 1.4rem;color:var(--muted);font-size:.95rem;}
.forks{list-style:none;margin:0;padding:0;display:grid;gap:1.6rem;}
.fork{display:grid;grid-template-columns:auto 1fr;gap:.85rem;align-items:start;}
.fork .k{font-family:var(--mono);font-size:.66rem;color:var(--bg);background:var(--accent);
  border-radius:2px;padding:.12rem .4rem;margin-top:.35rem;}
.fork h3{margin:0 0 .25rem;font-size:1.08rem;font-weight:600;}
.fork>div>p{margin:0;color:var(--muted);font-size:.93rem;}
.opt{display:block;margin-top:.5rem;padding-left:.9rem;border-left:2px solid var(--line);
  font-size:.92rem;color:var(--muted);}
.opt b{color:var(--accent);font-weight:600;}
.opt+.opt{margin-top:.45rem;}
.foot{margin-top:3rem;padding-top:1.1rem;border-top:1px solid var(--line);
  font-size:.78rem;color:var(--muted);}
"""


def mix(hex_a, hex_b, t):
    """把两个 #rrggbb 按 t 混一下，给面板底色 / 细线用。"""
    a = [int(hex_a[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(hex_b[i:i + 2], 16) for i in (1, 3, 5)]
    return '#%02x%02x%02x' % tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('data', help='路线图 JSON')
    ap.add_argument('-o', '--out', required=True)
    a = ap.parse_args()

    d = json.load(open(a.data, encoding='utf-8'))
    m = d['_meta']
    css = TPL_CSS % {
        'bg': m['bg'], 'accent': m['accent'], 'text': m['text'], 'muted': m['muted'],
        'panel': mix(m['bg'], m['text'], .05),
        'line': mix(m['bg'], m['text'], .16),
        'dim': mix(m['bg'], m['text'], .55),
    }

    def chapter(c):
        cls = 'ch'
        if c.get('blank'):
            cls += ' ch--blank'
        elif c.get('key') == 2:
            cls += ' ch--k2'
        elif c.get('key') == 1:
            cls += ' ch--k1'
        pin = '<span class="pin">埋钩子</span>' if c.get('pin') else ''
        title = E(c['t']) if c['t'] else '还没定'
        return ('<li class="%s"><span class="ch__n">%02d</span><div>'
                '<h3 class="ch__t">%s%s</h3><p class="ch__w">%s</p></div></li>'
                % (cls, c['n'], title, pin, E(c['w'])))

    acts = []
    for i, act in enumerate(m['acts']):
        chs = [c for c in d['chapters'] if c['act'] == i]
        acts.append(
            '<section class="act">\n    <header class="act__head">'
            '<span class="act__n">第 %s 幕</span><h2 class="act__t">%s</h2>'
            '<p class="act__d">%s</p></header>\n    <ol class="chs">%s</ol>\n  </section>'
            % (E(act['n']), E(act['title']), E(act['desc']), ''.join(chapter(c) for c in chs)))

    debts = ''.join(
        '<li class="debt"><span class="k %s">%s</span><span>%s</span></li>'
        % ('k--pin' if x['k'] == '埋了要收' else 'k--def', E(x['k']), E(x['v']))
        for x in m.get('debts', []))

    forks = ''.join(
        '<li class="fork"><span class="k">%02d</span><div><h3>%s</h3><p>%s</p>%s</div></li>'
        % (i + 1, E(f['h']), E(f['p']), ''.join('<span class="opt">%s</span>' % o for o in f['opts']))
        for i, f in enumerate(m.get('forks', [])))

    out = [
        '<title>%s</title>' % E(m['title']),
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
        'family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400&display=swap">',
        '<style>%s</style>' % css,
        '<div class="wrap">',
        '  <p class="eyebrow">%s</p>' % E(m.get('eyebrow', '')),
        '  <h1>%s</h1>' % E(m['title']),
        '  <p class="sub">%s</p>' % E(m.get('sub', '')),
        '  <p class="lede">%s</p>' % m.get('lede', ''),
        '  ' + '\n  '.join(acts),
        '  <div class="side">',
        '    <div class="box"><h2>母题（每章尽量带一两个）</h2><ul>%s</ul></div>'
        % ''.join('<li><span>%s</span></li>' % E(x) for x in m.get('motifs', [])),
        '    <div class="box"><h2>伏笔账</h2><ul>%s</ul></div>' % debts,
        '  </div>',
        '  <section class="ask"><h2>三个岔路等你挑</h2>',
        '    <p>都是剧情走向，凭感觉选就行。挑完我写第一章。</p>',
        '    <ul class="forks">%s</ul>' % forks,
        '  </section>',
        '  <p class="foot">这是路线图，不是成稿——章名和写法动笔时还会调。'
        '空着的格子是留给你的：想写什么就往里塞。系列圣经已经入库，换个对话也接得上。</p>',
        '</div>',
    ]
    open(a.out, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    print('✓ %s（%d 章 / %d 幕 / %d 个岔路）'
          % (a.out, len(d['chapters']), len(m['acts']), len(m.get('forks', []))))


if __name__ == '__main__':
    main()
