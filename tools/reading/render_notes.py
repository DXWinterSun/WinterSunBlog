#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
读书笔记页生成器（书页照片 → 高亮词句笔记 → 可批注的 Artifact 网页）

2026-09-26 Winter 在读《A Single Shot》原著：**「我给你发书页的照片，里面会有高亮的词或短语，
你能整理成笔记，artifact 给我，我也可以批注……之后放在博客上可以做我的笔记，省得我自己写了。」**
她要的「批注」就是 Artifact 自带的批注功能（跟看章节草稿时一样：选中一句、或点卡片上的
「批注」，发给 Claude），网页本身不存任何东西。

    python3 tools/reading/render_notes.py _data/reading/a-single-shot.yml \\
        -o <scratchpad>/a-single-shot-notes.html

然后用 Artifact 工具发布（第一次发布要带 capabilities={"comments": {"composer_only": true}}，
卡片上的「批注」按钮靠它打开批注框）。**一本书只有一张页、一个链接**：新的一批照片整理完，
往数据文件的 batches 末尾追加，重新生成、发布到同一个链接（链接记在数据文件 book.artifact）。

- 数据文件里 `batches` 为空时，页面显示「先挑详略」样板（样板内容在同目录 demo.yml）。
- 详略按 `book.detail`（lite / standard / full）决定每张卡显示哪些栏。
- 行内记号：`==高亮==`（荧光笔）、`**粗体**`。其余一律按纯文本转义。
- 2026-09-26 Winter 定的规矩：蓝笔＝生词、粉笔＝值得对照的用法（每条写 color）；
  原文只留前后几个词（context），一页一批，每批末尾附「欧路词典导入列表」。

完整工作法（读照片、写笔记、回批注、放博客）见 .claude/skills/winter-reading-notes/SKILL.md。
"""
import argparse, datetime, html, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'preview'))
from render_draft import palette          # noqa: E402  跟章节预览页同一套 AU 配色

import yaml                               # noqa: E402

# 每种详略显示哪些栏（词条、音标、页码、原形、看不清、Winter 批注、问答永远显示）
LEVELS = {
    'lite':     {'cn', 'context'},
    'standard': {'pos', 'kind', 'cn', 'context', 'gist', 'note'},
    'full':     {'pos', 'kind', 'cn', 'en', 'context', 'gist', 'note', 'extra'},
}

# 两支荧光笔（Winter 2026-09-26 定的规矩）：蓝＝生词；粉＝词认识，但这个搭配 / 用法值得对照、下次再看一眼
PENS = {
    'blue': ('生词', '#7fd6dc'),
    'pink': ('对照', '#f2a7c6'),
}

FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Volkhov:ital,wght@0,400;0,700;1,400'
         '&family=Noto+Serif+SC:wght@400;500;600;700&family=EB+Garamond:ital,wght@0,400;0,500;1,400&display=swap">')

CSS = '''
:root{
 color-scheme:dark;
 --bg:__BG__;--accent:__ACCENT__;--ink:__TEXT__;--muted:__MUTED__;--hl:__HL__;--hl-pink:__HLPINK__;
 --surface:color-mix(in srgb,var(--bg) 91%,#fff);
 --line:color-mix(in srgb,var(--accent) 24%,transparent);
 --paper:#f2eadd;--paper-ink:#3b3329;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
 font-family:"Noto Serif SC","Songti SC",Georgia,serif;font-size:16.5px;line-height:1.9;
 -webkit-font-smoothing:antialiased;}
body::before{content:"";position:fixed;inset:0;pointer-events:none;z-index:0;
 background:radial-gradient(ellipse 900px 500px at 15% -10%,rgba(255,255,255,.055),transparent 60%),
            radial-gradient(ellipse 700px 500px at 100% 8%,rgba(255,255,255,.035),transparent 55%);}
.wrap{position:relative;z-index:1;max-width:44rem;margin:0 auto;padding:3.2rem 1.25rem 5rem;}

/* 页头：跟章节预览页同一套（状态条 / 斜体小标 / 衬线大标题） */
.console{display:flex;flex-wrap:wrap;align-items:center;gap:8px 16px;
 padding:13px 18px;border:1px solid color-mix(in srgb,var(--accent) 34%,transparent);
 border-radius:4px;background:color-mix(in srgb,var(--accent) 8%,transparent);
 font-family:"EB Garamond",Georgia,serif;font-size:13px;letter-spacing:.06em;
 color:var(--muted);margin-bottom:2.4rem;}
.console b{color:var(--accent);font-weight:600;}
.console .dot{width:6px;height:6px;border-radius:50%;background:var(--accent);
 display:inline-block;box-shadow:0 0 6px var(--accent);flex:none;}
.console>span+span::before{content:"|";opacity:.38;margin-right:16px;}
.console>span.dot+span::before{content:none;}
.kicker{font-family:"Volkhov",Georgia,serif;font-style:italic;color:var(--muted);
 font-size:15px;text-align:center;margin:0 0 .6rem;text-wrap:balance;}
h1{font-family:"Volkhov","Noto Serif SC",Georgia,serif;font-weight:700;
 font-size:clamp(30px,6vw,42px);text-align:center;margin:0 0 .45rem;line-height:1.2;
 letter-spacing:.01em;text-wrap:balance;}
.sub{text-align:center;color:var(--accent);font-size:1rem;letter-spacing:.12em;margin:0;}
.rule{width:60px;height:1px;background:var(--accent);opacity:.6;margin:2.2rem auto 2.2rem;}
.lede{margin:0 0 1rem;color:var(--muted);font-size:.95rem;line-height:1.95;}
.lede b{color:var(--ink);font-weight:600;}

h2{font-family:"Volkhov","Noto Serif SC",Georgia,serif;font-weight:400;font-style:italic;
 margin:3.2rem 0 .35rem;font-size:1.22rem;letter-spacing:.02em;color:var(--accent);
 display:flex;align-items:center;gap:14px;text-wrap:balance;}
h2::after{content:"";flex:1;min-width:24px;height:1px;
 background:linear-gradient(to right,color-mix(in srgb,var(--accent) 55%,transparent),transparent);}
.batch__sub{margin:0 0 1.4rem;color:var(--muted);font-size:.84rem;letter-spacing:.08em;
 font-variant-numeric:tabular-nums;}
.section-text{margin:0 0 1.4rem;font-size:.97rem;}
.fine{margin:.2rem 0 0;color:var(--muted);font-size:.84rem;}

/* 目录：批次多了才出现 */
.toc{display:flex;flex-wrap:wrap;gap:8px;margin:1.6rem 0 0;padding:0;list-style:none;}
.toc a{display:inline-block;padding:.25rem .8rem;border:1px solid var(--line);border-radius:99px;
 color:var(--ink);text-decoration:none;font-size:.84rem;font-variant-numeric:tabular-nums;}
.toc a:hover,.toc a:focus-visible{border-color:var(--accent);color:var(--accent);outline:none;}

/* ── 一条笔记 ── */
.card{position:relative;margin:0 0 1.3rem;padding:1.1rem 1.25rem .95rem;background:var(--surface);
 border:1px solid var(--line);border-radius:6px;scroll-margin-top:1.2rem;}
.card__meta{display:flex;flex-wrap:wrap;align-items:baseline;gap:.2rem .9rem;margin-bottom:.3rem;
 font-family:"EB Garamond",Georgia,serif;font-size:.84rem;letter-spacing:.1em;color:var(--muted);
 font-variant-numeric:tabular-nums;}
.card__page{color:var(--accent);}
.card__kind{margin-left:auto;padding:0 .6rem;border:1px solid var(--line);border-radius:99px;
 font-family:"Noto Serif SC","Songti SC",serif;font-size:.74rem;letter-spacing:.08em;color:var(--accent);}
.card__head{display:flex;flex-wrap:wrap;align-items:baseline;gap:.15rem .7rem;margin:0 0 .2rem;}
.card__term{margin:0;font-family:"Volkhov",Georgia,serif;font-weight:700;font-size:1.5rem;
 line-height:1.3;letter-spacing:.01em;color:var(--ink);overflow-wrap:anywhere;}
.card__ipa{font-family:ui-sans-serif,-apple-system,"Segoe UI","Helvetica Neue",Arial,sans-serif;
 font-size:.86rem;color:var(--muted);}
.card__pos{font-family:"EB Garamond",Georgia,serif;font-style:italic;font-size:1.02rem;color:var(--accent);}
.card__lemma{font-size:.8rem;color:var(--muted);}
.card__lemma i{font-family:"EB Garamond",Georgia,serif;font-size:1rem;color:var(--ink);}
.card__cn{margin:0 0 .75rem;font-size:1.06rem;font-weight:500;}
.card__en{margin:-.45rem 0 .8rem;font-family:"EB Garamond",Georgia,serif;font-style:italic;
 font-size:1.04rem;color:var(--muted);}
.card__quote{margin:0 0 .55rem;padding:.05rem 0 .05rem 1rem;border-left:2px solid var(--accent);
 font-family:"EB Garamond",Georgia,serif;font-size:1.16rem;line-height:1.62;color:var(--ink);}
.card__gist{margin:0 0 .7rem;padding-left:1rem;color:var(--muted);font-size:.93rem;}
.card__note{margin:0 0 .5rem;font-size:.95rem;}
.card__note b,.card__extra strong,.card__unsure b{display:inline-block;margin-right:.6em;
 font-size:.78rem;letter-spacing:.14em;font-weight:600;color:var(--accent);}
.card__extra{margin:0 0 .5rem;padding:0;list-style:none;font-size:.93rem;}
.card__extra li{margin:0 0 .25rem;padding-left:1rem;position:relative;}
.card__extra li::before{content:"";position:absolute;left:.15rem;top:.85em;width:5px;height:1px;
 background:var(--accent);}
.card__unsure{margin:.2rem 0 .6rem;padding:.4rem .75rem;border:1px dashed color-mix(in srgb,var(--hl) 55%,transparent);
 border-radius:4px;font-size:.88rem;color:var(--ink);}
.card__unsure b{color:var(--hl);}

/* 荧光笔：颜色按她书上那支笔调（book.highlighter） */
mark{color:inherit;background:transparent;padding:0 .14em;margin:0 -.04em;
 background-image:linear-gradient(100deg,transparent 0 1.5%,color-mix(in srgb,var(--hl) 40%,transparent) 1.5% 98%,transparent 98%);
 border-radius:.25em .45em .3em .5em;
 -webkit-box-decoration-break:clone;box-decoration-break:clone;}

mark.pink{background-image:linear-gradient(100deg,transparent 0 1.5%,color-mix(in srgb,var(--hl-pink) 42%,transparent) 1.5% 98%,transparent 98%);}
.card__pen{padding:0 .6rem;border-radius:99px;font-family:"Noto Serif SC","Songti SC",serif;font-size:.74rem;
 letter-spacing:.08em;color:var(--bg);background:var(--hl);}
.card__pen.pink{background:var(--hl-pink);}
.card__pen+.card__kind{margin-left:0;}
.card__meta .card__pen{margin-left:auto;}
.card__cn .card__pos{margin-right:.5em;}
.card__ctx{margin:0 0 .7rem;}
.card__ctx .card__quote{margin-bottom:.3rem;}
.card__ctx-page{display:inline-block;margin:0 0 .25rem;font-family:"EB Garamond",Georgia,serif;
 font-size:.84rem;letter-spacing:.1em;color:var(--accent);font-variant-numeric:tabular-nums;}
.card__ctx .card__gist{margin:0;}
.card__later{margin:.2rem 0 .6rem;font-size:.86rem;color:var(--hl-pink);letter-spacing:.06em;}
.card__cmp{margin:.3rem 0 .7rem;padding:.7rem .85rem;border:1px dashed color-mix(in srgb,var(--hl-pink) 60%,transparent);
 border-radius:4px;font-size:.93rem;}
.card__cmp-h{margin:0 0 .45rem;font-size:.78rem;letter-spacing:.14em;font-weight:600;color:var(--hl-pink);}
.card__cmp-row{display:grid;grid-template-columns:auto 1fr;gap:.1rem .7rem;margin:0 0 .35rem;align-items:baseline;}
.card__cmp-row span{font-family:"EB Garamond",Georgia,serif;font-size:.84rem;color:var(--muted);
 font-variant-numeric:tabular-nums;white-space:nowrap;}
.card__cmp-row q{quotes:none;font-family:"EB Garamond",Georgia,serif;font-size:1.05rem;}
.card__cmp-row small{grid-column:2;color:var(--muted);font-size:.86rem;}
.card__cmp p{margin:.45rem 0 0;}

/* 欧路词典导入列表 */
.eudic{margin:1.6rem 0 0;padding:.9rem 1rem 1rem;border:1px solid var(--line);border-radius:6px;}
.eudic__h{display:flex;align-items:center;gap:.8rem;margin:0 0 .6rem;font-size:.95rem;font-weight:600;line-height:1.5;}
.eudic__copy{appearance:none;flex:none;white-space:nowrap;margin-left:auto;min-height:32px;padding:.2rem .9rem;border-radius:99px;cursor:pointer;
 border:1px solid color-mix(in srgb,var(--accent) 45%,transparent);background:transparent;color:var(--accent);
 font:inherit;font-size:.8rem;font-weight:400;letter-spacing:.12em;}
.eudic__copy:hover{background:color-mix(in srgb,var(--accent) 14%,transparent);}
.eudic pre{margin:0;padding:.7rem .85rem;border-radius:4px;background:color-mix(in srgb,var(--bg) 70%,#000);
 font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:.9rem;line-height:1.6;
 white-space:pre-wrap;word-break:break-word;user-select:all;-webkit-user-select:all;}

/* Winter 的批注：一张贴在卡上的便条（同博客 c-note 的纸色） */
.card__winter{position:relative;margin:1rem .2rem .7rem;padding:1rem 1.05rem .75rem;
 background:var(--paper);color:var(--paper-ink);border-radius:2px;transform:rotate(-.35deg);
 box-shadow:0 8px 20px rgba(0,0,0,.34);line-height:1.85;}
.card__winter::before{content:"";position:absolute;top:-9px;left:50%;width:70px;height:17px;
 transform:translateX(-50%) rotate(-1.5deg);background:color-mix(in srgb,var(--accent) 45%,transparent);opacity:.8;}
.card__winter-who{display:block;margin-bottom:.35rem;font-size:.68rem;letter-spacing:.2em;opacity:.55;}
.card__winter p{margin:0 0 .3rem;}
.card__winter p:last-child{margin-bottom:0;}

/* 批注里的问答 */
.card__qa{margin:.7rem 0 .4rem;padding:.65rem .85rem;border-radius:4px;
 background:color-mix(in srgb,var(--accent) 7%,transparent);font-size:.93rem;}
.card__qa p{margin:0;}
.card__qa p+p{margin-top:.35rem;}
.card__qa b{display:inline-block;margin-right:.6em;font-size:.78rem;letter-spacing:.14em;font-weight:600;}
.card__q b{color:var(--accent);}
.card__a b{color:var(--muted);}

.card__foot{display:flex;justify-content:flex-end;margin-top:.5rem;}
.card__ask{appearance:none;min-height:36px;padding:.3rem 1rem;border-radius:99px;cursor:pointer;
 border:1px solid color-mix(in srgb,var(--accent) 45%,transparent);background:transparent;
 color:var(--accent);font:inherit;font-size:.82rem;letter-spacing:.16em;}
.card__ask:hover{background:color-mix(in srgb,var(--accent) 14%,transparent);}
.card__ask:focus-visible{outline:2px solid var(--accent);outline-offset:2px;}

/* 样板区：三种详略并排比较 */
.pick{margin:0 0 1.6rem;}
.pick__label{display:inline-block;margin:0 0 .5rem;font-family:"EB Garamond",Georgia,serif;
 font-size:.95rem;letter-spacing:.12em;color:var(--accent);}
.pick__label small{margin-left:.5em;font-family:"Noto Serif SC","Songti SC",serif;font-size:.8rem;
 letter-spacing:.06em;color:var(--muted);}

.tips{margin:0;padding:0;list-style:none;counter-reset:tip;}
.tips li{position:relative;margin:0 0 .55rem;padding-left:2rem;font-size:.95rem;}
.tips li::before{counter-increment:tip;content:counter(tip);position:absolute;left:0;top:.18em;
 width:1.35rem;height:1.35rem;border:1px solid var(--line);border-radius:50%;text-align:center;
 font-family:"EB Garamond",Georgia,serif;font-size:.8rem;line-height:1.3rem;color:var(--accent);}
details.tipbox{margin-top:1.2rem;}
details.tipbox summary{cursor:pointer;color:var(--accent);font-size:.9rem;letter-spacing:.08em;}
details.tipbox .tips{margin-top:.8rem;}

.foot{margin-top:3.6rem;padding-top:1.4rem;border-top:1px solid color-mix(in srgb,var(--accent) 55%,transparent);
 color:var(--muted);font-size:.86rem;line-height:1.9;}
.foot p{margin:0 0 .5rem;}
.foot b{color:var(--accent);font-weight:600;}

@media (max-width:480px){
 body{font-size:16px;}
 .wrap{padding:2.4rem 1rem 4rem;}
 .card{padding:1rem 1rem .85rem;}
 .card__term{font-size:1.36rem;}
 .card__quote{font-size:1.1rem;}
 .console{padding:11px 14px;gap:6px 12px;}
 .console>span+span::before{margin-right:12px;}
}
'''

# 卡片上的「批注」按钮：打开 Artifact 自带的批注框，锚在这张卡上（页面本身什么都不存）。
# 拿不到批注能力（旧版查看器 / 没有权限）就保持隐藏——选中文字照样能批注。
JS = '''
[].forEach.call(document.querySelectorAll('.eudic__copy'), function (b) {
  b.addEventListener('click', function () {
    var t = b.closest('.eudic').querySelector('pre').textContent;
    function done() { var o = b.textContent; b.textContent = '已复制'; setTimeout(function () { b.textContent = o; }, 1400); }
    if (navigator.clipboard) navigator.clipboard.writeText(t).then(done, function () {});
  });
});
(function () {
  var btns = [].slice.call(document.querySelectorAll('.card__ask'));
  if (!btns.length || !window.claude || !window.claude.use) return;
  window.claude.use('comments').then(function (c) {
    if (!c) return;
    function off() { btns.forEach(function (x) { x.hidden = true; }); }
    btns.forEach(function (b) {
      b.hidden = false;
      b.addEventListener('click', function () {
        c.openComposer({ element: b.closest('.card') }).catch(function (e) {
          var code = e && e.code;
          if (code === 'unavailable' || code === 'not_granted' ||
              code === 'capability_disabled' || code === 'capability_removed') off();
        });
      });
    });
  }).catch(function () {});
})();
'''


def esc(s):
    return html.escape(str(s), quote=True)


def fmt(s, pen='blue'):
    """纯文本转义 + 两个行内记号：==高亮== / **粗体**。高亮按这条笔记的荧光笔颜色上色。"""
    s = html.escape(str(s).strip(), quote=False)
    s = re.sub(r'==(.+?)==', (r'<mark class="pink">\1</mark>' if pen == 'pink' else r'<mark>\1</mark>'), s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    return s.replace('\n', '<br>')


def as_list(v):
    if v in (None, '', []):
        return []
    return v if isinstance(v, list) else [v]


def card(n, level, cid, winter_label='Winter 的批注', index=None):
    """一条笔记。顺序照 Winter 2026-09-26 定的：词＋音标 → 词性＋中文＋英文释义 →
    原文语境（短语＋页码＋大意）→ 解读 → 搭配 / 易混。"""
    show = LEVELS[level]
    pen = n.get('color') or 'blue'
    out = [f'<article class="card" id="{esc(cid)}" data-comment-target>']

    meta = [f'<span class="card__no">No. {esc(n.get("id", "—"))}</span>']
    if pen in PENS:
        meta.append(f'<span class="card__pen {pen}">{PENS[pen][0]}</span>')
    if 'kind' in show and n.get('kind'):
        meta.append(f'<span class="card__kind">{esc(n["kind"])}</span>')
    out.append('<div class="card__meta">' + ''.join(meta) + '</div>')

    head = [f'<h3 class="card__term" lang="en">{esc(n["term"])}</h3>']
    if n.get('ipa'):
        head.append(f'<span class="card__ipa">{esc(n["ipa"])}</span>')
    if n.get('lemma'):
        head.append(f'<span class="card__lemma">原形 <i lang="en">{esc(n["lemma"])}</i></span>')
    out.append('<div class="card__head">' + ''.join(head) + '</div>')

    if n.get('cn'):
        pos = (f'<span class="card__pos" lang="en">{esc(n["pos"])}</span>'
               if 'pos' in show and n.get('pos') else '')
        out.append(f'<p class="card__cn">{pos}{fmt(n["cn"])}</p>')
    if 'en' in show and n.get('en'):
        out.append(f'<p class="card__en" lang="en">{fmt(n["en"])}</p>')

    ctx = n.get('context') or n.get('sentence')
    if ctx:
        page = (f'<span class="card__ctx-page">p. {esc(n["page"])}</span>'
                if n.get('page') not in (None, '') else '')
        gist = (f'<p class="card__gist">{fmt(n["gist"])}</p>'
                if 'gist' in show and n.get('gist') else '')
        out.append(f'<div class="card__ctx">{page}'
                   f'<blockquote class="card__quote" lang="en">{fmt(ctx, pen)}</blockquote>{gist}</div>')

    if n.get('compare_later'):
        out.append('<p class="card__later">后面会对照</p>')
    cmp = n.get('compare')
    if cmp:
        rows = []
        for oid in as_list(cmp.get('with')):
            o = (index or {}).get(str(oid))
            if not o:
                sys.exit(f'No. {n.get("id")} 要对照的 No. {oid} 不存在')
            octx = o.get('context') or o.get('sentence') or o['term']
            og = f'<small>{fmt(o["gist"])}</small>' if o.get('gist') else ''
            rows.append(f'<div class="card__cmp-row"><span>No. {esc(oid)} · p. {esc(o.get("page", "—"))}</span>'
                        f'<q lang="en">{fmt(octx, o.get("color") or "blue")}</q>{og}</div>')
        og = f'<small>{fmt(n["gist"])}</small>' if n.get('gist') else ''
        rows.append(f'<div class="card__cmp-row"><span>这一条 · p. {esc(n.get("page", "—"))}</span>'
                    f'<q lang="en">{fmt(ctx or n["term"], pen)}</q></div>')
        body = f'<p>{fmt(cmp["text"])}</p>' if cmp.get('text') else ''
        out.append(f'<div class="card__cmp"><p class="card__cmp-h">放在一起对照</p>{"".join(rows)}{body}</div>')

    if 'note' in show and n.get('note'):
        out.append(f'<p class="card__note"><b>解读</b>{fmt(n["note"])}</p>')
    if 'extra' in show and n.get('extra'):
        items = ''.join(f'<li>{fmt(x)}</li>' for x in as_list(n['extra']))
        out.append(f'<ul class="card__extra">{items}</ul>')
    if n.get('unsure'):
        out.append(f'<p class="card__unsure"><b>看不太清</b>{fmt(n["unsure"])}</p>')

    ws = as_list(n.get('winter'))
    if ws:
        body = ''.join(f'<p>{fmt(w)}</p>' for w in ws)
        label = n.get('winter_label') or winter_label
        out.append(f'<div class="card__winter"><span class="card__winter-who">{esc(label)}</span>{body}</div>')
    for qa in as_list(n.get('qa')):
        out.append('<div class="card__qa">'
                   f'<p class="card__q"><b>问</b>{fmt(qa["q"])}</p>'
                   f'<p class="card__a"><b>答</b>{fmt(qa["a"])}</p></div>')

    out.append('<div class="card__foot"><button type="button" class="card__ask" hidden>批注</button></div>')
    out.append('</article>')
    return '\n'.join(out)


def eudic_words(notes):
    """欧路词典导入用：一律原形；eudic 字段可手动指定（短语拆开会变成几个无关的词时用）。"""
    words = []
    for x in notes:
        w = str(x.get('eudic') or x.get('lemma') or x['term']).strip()
        if w and w not in words:
            words.append(w)
    return words


def eudic_box(words, title):
    return ('<div class="eudic"><p class="eudic__h">📋 欧路词典导入列表（' + esc(title) + '）'
            '<button type="button" class="eudic__copy">复制</button></p>'
            f'<pre lang="en">{esc(" ".join(words))}</pre></div>')


def cn_date(d):
    if isinstance(d, str):
        try:
            d = datetime.date.fromisoformat(d)
        except ValueError:
            return d
    return f'{d.month} 月 {d.day} 日'


def batch_section(b, level, index, title):
    n = b['n']
    bits = [f'第 {b["pages"]} 页'] if b.get('pages') else [f'第 {n} 批']
    if b.get('date'):
        bits.append(cn_date(b['date']))
    notes = b.get('notes') or []
    sub = [f'{len(notes)} 条']
    if b.get('photos'):
        sub.append(f'{b["photos"]} 张照片')
    if b.get('remark'):
        sub.append(esc(b['remark']))
    cards = '\n'.join(card(x, level, f'n{x["id"]}', index=index) for x in notes)
    box = eudic_box(eudic_words(notes), title) if notes else ''
    return (f'<section class="batch" id="b{n}">\n<h2>{" · ".join(bits)}</h2>\n'
            f'<p class="batch__sub">{" · ".join(sub)}</p>\n{cards}\n{box}\n</section>')


def tips_list(items):
    return '<ol class="tips">' + ''.join(f'<li>{fmt(t)}</li>' for t in items) + '</ol>'


def demo_body(demo, book):
    c, a, t = demo['compare'], demo['after'], demo['tips']
    level = book.get('detail') or 'standard'
    if book.get('detail_picked'):
        # 她已经挑定详略：只留她选的那一版
        p = demo['picked']
        label = next((lab for lv, lab, _ in c['levels'] if lv == level), level)
        first = (f'<section id="pick">\n<h2>{esc(p["heading"])}</h2>\n'
                 f'<p class="section-text">{fmt(p["text"].replace("{label}", label))}</p>\n'
                 + card(c['note'], level, f'demo-{level}')
                 + f'\n<p class="fine">{fmt(p["fine"])}</p>\n</section>\n')
        after_level = level
    else:
        picks = []
        for lvl, label, note in c['levels']:
            small = f'<small>{esc(note)}</small>' if note else ''
            picks.append(f'<div class="pick"><span class="pick__label">{esc(label)}{small}</span>\n'
                         + card(c['note'], lvl, f'demo-{lvl}') + '</div>')
        first = (f'<section id="pick">\n<h2>{esc(c["heading"])}</h2>\n'
                 f'<p class="section-text">{fmt(c["text"])}</p>\n' + '\n'.join(picks)
                 + f'\n<p class="fine">{fmt(c["fine"])}</p>\n</section>\n')
        after_level = a.get('level', 'standard')
    return (first
            + f'<section id="after">\n<h2>{esc(a["heading"])}</h2>\n'
            f'<p class="section-text">{fmt(a["text"])}</p>\n'
            + card(a['note'], after_level, 'demo-after') + '\n</section>\n'
            f'<section id="tips">\n<h2>{esc(t["heading"])}</h2>\n{tips_list(t["items"])}\n</section>')


def main():
    ap = argparse.ArgumentParser(description='把读书笔记数据渲染成可批注的 Artifact 网页')
    ap.add_argument('data', help='笔记数据文件，如 _data/reading/a-single-shot.yml')
    ap.add_argument('-o', '--out', required=True, help='输出的 .html（改完用同一路径重新生成、重新发布，链接不变）')
    a = ap.parse_args()

    data = yaml.safe_load(open(a.data, encoding='utf-8')) or {}
    book = data.get('book') or {}
    batches = data.get('batches') or []
    demo = yaml.safe_load(open(os.path.join(HERE, 'demo.yml'), encoding='utf-8'))
    level = book.get('detail') or 'standard'
    if level not in LEVELS:
        sys.exit(f'book.detail 只能是 {"/".join(LEVELS)}，现在是 {level!r}')

    # 编号不能重复（批注锚在卡片 id 上，重号会串）
    index = {}
    for b in batches:
        for x in b.get('notes') or []:
            if str(x['id']) in index:
                sys.exit(f'笔记编号重复：{x["id"]}')
            if (x.get('color') or 'blue') not in PENS:
                sys.exit(f'No. {x["id"]} 的 color 只能是 blue / pink')
            index[str(x['id'])] = x

    pal = palette(book.get('palette', ''))
    pens = book.get('highlighters') or {}
    css = (CSS.replace('__HLPINK__', pens.get('pink') or PENS['pink'][1])
              .replace('__HL__', pens.get('blue') or book.get('highlighter') or PENS['blue'][1]))
    for k, v in pal.items():
        css = css.replace(f'__{k.upper()}__', v)

    title = book.get('title', '')
    total = sum(len(b.get('notes') or []) for b in batches)
    last = batches[-1] if batches else None

    cells = []
    if last:
        status = book.get('status') or '待你批注'
        cells.append(f'<span><b>状态</b> · {esc(status)}</span>')
        cells.append(f'<span><b>已记</b> · {total} 条</span>')
        if last.get('pages'):
            upto = re.split(r'[–-]', str(last['pages']))[-1].strip()
            cells.append(f'<span><b>读到</b> · 第 {esc(upto)} 页</span>')
    else:
        cells.append('<span><b>状态</b> · 等第一批照片</span>')
        cells.append('<span><b>已记</b> · 0 条</span>')
    console = '<div class="console"><span class="dot"></span>' + ''.join(cells) + '</div>\n'

    kick = esc(' · '.join(str(x) for x in (book.get('author'), book.get('year')) if x))
    if book.get('about'):                 # 第二行单独起，免得手机上从半截断开
        kick += f'<br>{esc(book["about"])}'
    head = (f'{console}<p class="kicker">{kick}</p>\n'
            f'<h1 lang="en">{esc(title)}</h1>\n<p class="sub">原著笔记 · 高亮词句</p>\n<div class="rule"></div>\n'
            f'<p class="lede">{fmt(demo["lede"])}</p>\n')

    if batches:
        toc = ''
        if len(batches) > 1:
            toc = '<ul class="toc">' + ''.join(
                f'<li><a href="#b{b["n"]}">'
                + (f'p. {esc(b["pages"])}' if b.get('pages') else f'第 {b["n"]} 批') + '</a></li>' for b in batches) + '</ul>\n'
        body = toc + '\n'.join(batch_section(b, level, index, title) for b in batches)
        foot = (f'<div class="foot"><p>{fmt(demo["foot"])}</p>\n'
                f'<details class="tipbox"><summary>{esc(demo["tips"]["heading"])}</summary>'
                f'{tips_list(demo["tips"]["items"])}</details></div>')
    else:
        body = demo_body(demo, book)
        foot = f'<div class="foot"><p>{fmt(demo["foot"])}</p></div>'

    page_title = book.get('page_title') or f'{title} 原著笔记'
    page = (f'<title>{esc(page_title)}</title>\n{FONTS}\n<style>{css}</style>\n'
            f'<div class="wrap">\n{head}{body}\n{foot}\n</div>\n<script>{JS}</script>\n')
    open(a.out, 'w', encoding='utf-8').write(page)
    print(f'✅ {a.out}（{len(batches)} 批 · {total} 条 · 详略 {level} · 配色 {book.get("palette") or "默认"}）')


if __name__ == '__main__':
    main()
