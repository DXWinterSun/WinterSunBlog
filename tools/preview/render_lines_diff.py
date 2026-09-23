#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台词改稿 · 新旧对照预览页生成器

给 Winter 过目「某一批角色的台词要怎么改」时用这个，别再手打整页 HTML。
读一份改稿 JSON（见 .claude/lines-rewrite/ 里的样板）＋ sam/lines.json 的现状，
排成一张对照页：一人一块、五句按序、淡的是旧的、亮的是新的、每句注明料的出处。

    python3 tools/preview/render_lines_diff.py .claude/lines-rewrite/batch1.json \
        -o /tmp/.../台词改稿.html

然后用 Artifact 工具发布，聊天里只给链接（台词属创作文字，须 Winter 过目后才落盘）。
改完稿重新生成、重新发布到同一个链接，她刷新即看新版。

改稿 JSON 的结构：
{
  "_meta": {
    "title": "八个人，四十句",         # 也是 <title>，两到四个词的名字，别带解释
    "eyebrow": "…", "lede": "…",
    "howto": ["段一", "段二"],
    "order": ["gary", "trent", …],     # 角色排列顺序（用 lines.json 的 id）
    "forks": [ {"h": "标题", "p": "说明", "opts": ["<b>A</b> …", …]}, … ],
    "foot": "…"
  },
  "<角色id>": {
    "anchorKeep": true,                # 第 1 句（锚句）是否保留原句
    "quotes": [ {"label","line","lineCN","src"} × 5 ]   # src = 这句料是从哪儿挖的
  }
}

⚠️ 落盘前要记得的两件事（脚本不替你做）：
  1. label 全站唯一、同角色 5 条之间不互相包含；
  2. 改了锚句（第 1 句）＝ 画册 many-faces 的 inscription、spectrum、quiz 三处要一起改。
  落盘后跑 tools/check_palette_sync.py 和 tools/check_daily_rotation.py。
"""
import json, html, os, sys, argparse

# 本脚本在 tools/preview/ 下，仓库根要往上两级
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
E = lambda s: html.escape(s or '', quote=True)

CSS = """
:root{
  --paper:#f6f4ef; --paper-2:#efece4; --ink:#1a1c1a; --ink-2:#4a4e4a; --muted:#7c817a;
  --line:#dcdbd2; --line-2:#c6c5ba; --accent:#2f5d78; --old:#a8412c; --new:#3f7256;
  --serif:"EB Garamond",Georgia,"Songti SC","Source Han Serif SC",serif;
  --mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  color-scheme:dark;
  --paper:#15171a; --paper-2:#1c1f22; --ink:#e8e6df; --ink-2:#b4b2aa; --muted:#83877f;
  --line:#2b2f33; --line-2:#3a3f44; --accent:#7fb0c9; --old:#d1745c; --new:#7cae92;
}}
:root[data-theme="dark"]{
  color-scheme:dark;
  --paper:#15171a; --paper-2:#1c1f22; --ink:#e8e6df; --ink-2:#b4b2aa; --muted:#83877f;
  --line:#2b2f33; --line-2:#3a3f44; --accent:#7fb0c9; --old:#d1745c; --new:#7cae92;
}
body{background:var(--paper);color:var(--ink);font-family:var(--serif);
  -webkit-font-smoothing:antialiased;line-height:1.7;}
.wrap{max-width:46rem;margin:0 auto;padding-inline:16px;padding-block:2.6rem 4rem;}
.eyebrow{font-family:var(--mono);font-size:.66rem;letter-spacing:.2em;text-transform:uppercase;
  color:var(--muted);margin:0 0 .7rem;}
h1{font-size:clamp(1.9rem,6vw,2.7rem);font-weight:600;margin:0 0 .8rem;letter-spacing:.01em;
  text-wrap:balance;}
.lede{margin:0;color:var(--ink-2);font-size:1.03rem;max-width:34em;}
.lede b{color:var(--ink);font-weight:600;}
.nums{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:var(--line);
  border-block:1px solid var(--line);margin:2.2rem 0 0;}
.nums div{background:var(--paper);padding:.9rem .2rem 1rem;text-align:center;}
.nums b{display:block;font-size:1.55rem;font-weight:600;font-variant-numeric:tabular-nums;line-height:1.2;}
.nums span{font-family:var(--mono);font-size:.62rem;letter-spacing:.13em;color:var(--muted);text-transform:uppercase;}
.nums .hot b{color:var(--old);}
.howto{margin:1.6rem 0 0;padding:.9rem 1rem;background:var(--paper-2);border-left:3px solid var(--accent);
  font-size:.92rem;color:var(--ink-2);}
.howto p{margin:0;}
.howto p + p{margin-top:.45rem;}
.card{margin-top:2.6rem;border-top:2px solid var(--ink);padding-top:1.1rem;}
.who{display:flex;align-items:flex-start;gap:.65rem;flex-wrap:wrap;}
.who__dot{width:12px;height:12px;border-radius:50%;outline:2px solid;outline-offset:1px;
  flex:none;margin-top:.5rem;}
.who__id{flex:1 1 11rem;min-width:0;}
.who__id h2{margin:0;font-size:1.32rem;font-weight:600;letter-spacing:.01em;}
.who__id p{margin:.05rem 0 0;font-size:.82rem;color:var(--muted);}
.who__meta{display:flex;gap:.3rem;flex-wrap:wrap;align-items:center;padding-top:.35rem;}
.chip{font-family:var(--mono);font-size:.6rem;letter-spacing:.08em;color:var(--ink-2);
  border:1px solid var(--line-2);border-radius:2px;padding:.16rem .38rem;white-space:nowrap;}
.chip--none{color:var(--muted);border-style:dashed;}
.qs{list-style:none;margin:1.1rem 0 0;padding:0;display:grid;gap:1.5rem;}
.q{display:grid;gap:.5rem;}
.q__top{display:flex;align-items:center;gap:.45rem;flex-wrap:wrap;}
.q__n{font-family:var(--mono);font-size:.68rem;color:var(--paper);background:var(--ink-2);
  border-radius:2px;padding:.05rem .32rem;flex:none;font-variant-numeric:tabular-nums;}
.q__labs{display:flex;align-items:center;gap:.35rem;flex-wrap:wrap;}
.lab{font-family:var(--mono);font-size:.68rem;letter-spacing:.07em;}
.lab--old{color:var(--muted);text-decoration:line-through;text-decoration-color:var(--old);}
.lab--new{color:var(--new);font-weight:600;}
.arr{color:var(--muted);font-size:.7rem;}
.tag{font-family:var(--mono);font-size:.58rem;letter-spacing:.09em;padding:.1rem .32rem;
  border-radius:2px;white-space:nowrap;}
.tag--anchor{color:var(--accent);border:1px solid var(--accent);}
.tag--warn{color:var(--paper);background:var(--old);}
.tag--keep{color:var(--muted);border:1px dashed var(--line-2);}
.side{display:grid;grid-template-columns:auto 1fr;gap:.6rem;align-items:start;}
.side__k{font-family:var(--mono);font-size:.6rem;letter-spacing:.1em;padding-top:.32rem;
  width:1.2rem;text-align:center;flex:none;}
.side__t{min-width:0;}
.side--old{opacity:.62;}
.side--old .side__k{color:var(--old);}
.side--old .side__t{border-left:2px solid var(--line-2);padding-left:.7rem;}
.side--new .side__k{color:var(--new);}
.side--new .side__t{border-left:2px solid var(--new);padding-left:.7rem;}
.en{margin:0;font-style:italic;font-size:.95rem;color:var(--ink-2);}
.side--new .en{color:var(--ink);}
.cn{margin:.15rem 0 0;font-size:1rem;}
.side--new .cn{font-weight:500;}
.src{margin:0 0 0 1.8rem;font-size:.76rem;color:var(--muted);text-wrap:pretty;}
@media (max-width:520px){.src{margin-left:0;}.side__k{width:1rem;}}
.ask{margin-top:3.4rem;border-top:2px solid var(--ink);padding-top:1.4rem;}
.ask h2{font-size:1.4rem;font-weight:600;margin:0 0 .3rem;}
.ask > p{margin:0 0 1.2rem;color:var(--ink-2);font-size:.95rem;}
.forks{list-style:none;margin:0;padding:0;display:grid;gap:1.1rem;}
.forks li{display:grid;grid-template-columns:auto 1fr;gap:.8rem;align-items:start;}
.forks .k{font-family:var(--mono);font-size:.66rem;color:var(--paper);background:var(--accent);
  border-radius:2px;padding:.1rem .38rem;margin-top:.3rem;}
.forks h3{margin:0 0 .2rem;font-size:1.02rem;font-weight:600;}
.forks p{margin:0;color:var(--ink-2);font-size:.93rem;}
.opt{display:block;margin-top:.35rem;padding-left:.9rem;border-left:2px solid var(--line-2);
  font-size:.9rem;color:var(--ink-2);}
.opt b{color:var(--ink);font-weight:600;}
.foot{margin-top:3rem;padding-top:1.1rem;border-top:1px solid var(--line);
  font-size:.78rem;color:var(--muted);}
"""


def load_lines():
    with open(os.path.join(ROOT, 'sam/lines.json'), encoding='utf-8') as f:
        return {c['id']: c for c in json.load(f)['characters']}


def chapter_counts():
    """auLink → 该系列章数。用来在角色头上标『AU · N 章』。"""
    import re, glob, collections
    slug2name, counts = {}, collections.Counter()
    for f in glob.glob(os.path.join(ROOT, 'series/*/index.html')):
        s = open(f, encoding='utf-8').read()
        sn = re.search(r'^series_name:\s*"([^"]*)"', s, re.M)
        pl = re.search(r'^permalink:\s*(\S+)', s, re.M)
        if sn and pl:
            slug2name[pl.group(1).strip().rstrip('/').split('/')[-1]] = sn.group(1)
    for f in glob.glob(os.path.join(ROOT, '_posts/*.md')):
        m = re.search(r'^series:\s*"([^"]*)"', open(f, encoding='utf-8').read(3000), re.M)
        if m:
            counts[m.group(1)] += 1
    return slug2name, counts


def render_block(cid, cur, draft, slug2name, counts):
    n = draft[cid]
    au = cur.get('auLink')
    if au:
        name = slug2name.get(au.rstrip('/').split('/')[-1])
        au_chip = '<span class="chip">AU · %d 章</span>' % counts.get(name, 0)
    else:
        au_chip = '<span class="chip chip--none">还没有 AU</span>'
    head = ('<header class="who">\n'
            '        <span class="who__dot" style="background:%s;outline-color:%s"></span>\n'
            '        <div class="who__id"><h2>%s</h2><p>%s · %s</p></div>\n'
            '        <div class="who__meta">%s</div>\n'
            '      </header>') % (cur['accent'], cur['bg'], E(cur['name']),
                                  E(cur['filmCN']), cur['year'], au_chip)
    items = []
    for i in range(5):
        o, w = cur['quotes'][i], n['quotes'][i]
        same = o['line'].strip() == w['line'].strip()
        tags = []
        if i == 0:
            tags.append('<span class="tag tag--anchor">锚句 · 也印在画册上</span>')
            if not n.get('anchorKeep'):
                tags.append('<span class="tag tag--warn">这一句要换</span>')
        if same:
            tags.append('<span class="tag tag--keep">句子留着，只换标题</span>')
        oldpart = '' if same else (
            '<div class="side side--old"><span class="side__k">旧</span>'
            '<div class="side__t"><p class="en">%s</p><p class="cn">%s</p></div></div>'
            % (E(o['line']), E(o['lineCN'])))
        if o['label'] != w['label']:
            lab = ('<span class="lab lab--old">%s</span><span class="arr">→</span>'
                   '<span class="lab lab--new">%s</span>') % (E(o['label']), E(w['label']))
        else:
            lab = '<span class="lab lab--new">%s</span>' % E(w['label'])
        items.append(
            '<li class="q">\n'
            '          <div class="q__top"><span class="q__n">%d</span>'
            '<div class="q__labs">%s</div>%s</div>\n'
            '          %s\n'
            '          <div class="side side--new"><span class="side__k">新</span>'
            '<div class="side__t"><p class="en">%s</p><p class="cn">%s</p></div></div>\n'
            '          <p class="src">%s</p>\n        </li>'
            % (i + 1, lab, ''.join(tags), oldpart, E(w['line']), E(w['lineCN']), E(w.get('src', ''))))
    return ('<section class="card">\n      %s\n      <ol class="qs">\n        %s\n      </ol>\n    </section>'
            % (head, '\n        '.join(items)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('draft', help='改稿 JSON')
    ap.add_argument('-o', '--out', required=True, help='输出的 HTML')
    a = ap.parse_args()

    draft = json.load(open(a.draft, encoding='utf-8'))
    meta = draft.pop('_meta')
    cur_all = load_lines()
    slug2name, counts = chapter_counts()
    order = meta.get('order') or list(draft)

    missing = [c for c in order if c not in cur_all]
    if missing:
        sys.exit('lines.json 里没有这些 id：%s' % missing)

    changed = sum(1 for c in order for i in range(5)
                  if cur_all[c]['quotes'][i]['line'].strip() != draft[c]['quotes'][i]['line'].strip())
    anchors = sum(1 for c in order if not draft[c].get('anchorKeep'))

    forks = '\n      '.join(
        '<li><span class="k">%02d</span><div>\n        <h3>%s</h3>\n        <p>%s</p>\n'
        '        <span class="opt">%s</span>\n      </div></li>'
        % (i + 1, E(f['h']), E(f['p']), '<br>'.join(f.get('opts', [])))
        for i, f in enumerate(meta.get('forks', [])))

    out = [
        '<title>%s</title>' % E(meta['title']),
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
        'family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400&display=swap">',
        '<style>%s</style>' % CSS,
        '<div class="wrap">',
        '  <p class="eyebrow">%s</p>' % E(meta.get('eyebrow', '')),
        '  <h1>%s</h1>' % E(meta['title']),
        '  <p class="lede">%s</p>' % meta['lede'],
        '  <div class="nums">',
        '    <div><b>%d</b><span>个人</span></div>' % len(order),
        '    <div><b>%d</b><span>句真的换了</span></div>' % changed,
        '    <div class="hot"><b>%d</b><span>句锚句要换</span></div>' % anchors,
        '  </div>',
        '  <div class="howto">%s</div>' % ''.join('<p>%s</p>' % p for p in meta.get('howto', [])),
        '',
        '    ' + '\n\n    '.join(render_block(c, cur_all[c], draft, slug2name, counts) for c in order),
        '',
        '  <section class="ask">',
        '    <h2>%s</h2>' % E(meta.get('ask_title', '等你拍板')),
        '    <p>%s</p>' % E(meta.get('ask_lede', '')),
        '    <ul class="forks">\n      %s\n    </ul>' % forks,
        '  </section>',
        '  <p class="foot">%s</p>' % meta.get('foot', ''),
        '</div>',
    ]
    with open(a.out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')
    print('✓ %s（%d 人 / %d 句改动 / %d 句锚句）' % (a.out, len(order), changed, anchors))


if __name__ == '__main__':
    main()
