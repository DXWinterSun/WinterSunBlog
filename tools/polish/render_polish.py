#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
波兰语笔记本页生成器（多邻国错题 / 疑问 → 一题一张卡，按知识点归类）

2026-10-01 Winter：「我之后能做成我在多邻国遇到错的或者有疑问的地方的时候，我就来对话里给你并且问你，
你给我解释清楚之后，顺便整理到波兰语学习的笔记里，你可以进行更好的分类以便我学习……
如果我之后还问之前问过的，你有存档可以查就可以给我指路，也会加深我的记忆。」
同一天她又说：「能不能做成更多邻国的形式？」——所以每张卡照多邻国做题的样子排：题型标题、
说话的角色（我们用站里的小雪人，不用多邻国的角色）和气泡、她写的答案、底下绿 / 红结果条，讲解放在下面。

    python3 tools/polish/render_polish.py -o <scratchpad>/polish-notes.html   # 给她看的 Artifact
    python3 tools/polish/render_polish.py --blog                              # 博客上那一页 polish/index.html

- 数据只有一份：_data/polish/notes.yml（分类 areas + 笔记 notes）。还没有笔记时显示 demo.yml 里的两张样板。
- 第一次发布 Artifact 要带 capabilities={"comments": {"composer_only": true}}（卡片上的「批注」按钮靠它）。
  之后发布到同一个链接（记在 meta.artifact），不再传 capabilities。
- 行内记号：`==高亮==`、`**粗体**`；其余一律当纯文本转义。
- ⚠️ 只借多邻国的「样子」：不放它的名字、标志、角色和专用字体。

完整工作法（查档、讲解、归类、发布）见 .claude/skills/winter-polish-notes/SKILL.md。
"""
import argparse, datetime, html, os, re, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

import yaml                               # noqa: E402

DATA = os.environ.get('POLISH_NOTES') or os.path.join(ROOT, '_data', 'polish', 'notes.yml')   # 自测时可指向临时文件
SITE = 'https://dxwintersun.github.io/WinterSunBlog'
PL_ORDER = 'aąbcćdeęfghijklłmnńoóprsśtuvwxyzźż'   # 波兰语字母表顺序（生词表按它排）

# 多邻国的题型 → 卡上那行大标题
TASKS = {'listen': '听写', 'fill': '补词', 'translate': '翻译', 'choose': '选意思', 'speak': '跟读', 'match': '配对'}

FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Nunito:wght@600;700;800;900'
         '&family=Noto+Sans+SC:wght@400;500;700;900&display=swap">')

CSS = '''
/* 照多邻国做题页的样子：白底、灰色粗描边、底边加厚的「实体按钮」、绿 / 红结果条；说话的是站里的小雪人 */
:root{
 color-scheme:light;
 --bg:#ffffff;--surface:#ffffff;--soft:#f7f7f7;--ink:#3c3c3c;--text:#4b4b4b;--muted:#777777;--faint:#afafaf;
 --line:#e5e5e5;--line-deep:#d6d6d6;
 --blue:#1899d6;--blue-soft:#ddf4ff;--blue-line:#84d8ff;
 --green:#58a700;--green-btn:#58cc02;--green-bg:#d7ffb8;--green-line:#a5ed6e;
 --red:#ea2b2b;--red-bg:#ffdfe0;--red-line:#ffb2b2;
 --amber:#cc7a00;--amber-bg:#fff2d6;--key-bg:#fff7dd;--key-line:#ffd75e;
 --snow:#ffffff;--snow-line:#c9d6de;--hat:#3c3c3c;--nose:#ff9600;
 --font:"Nunito","PingFang SC","Hiragino Sans GB","Noto Sans SC","Microsoft YaHei",system-ui,sans-serif;
}
:root[data-theme="dark"]{
 color-scheme:dark;
 --bg:#131f24;--surface:#131f24;--soft:#1b2a31;--ink:#f1f7fb;--text:#dce6ec;--muted:#8fa3ad;--faint:#5c707a;
 --line:#37464f;--line-deep:#2b3940;
 --blue:#49c0f8;--blue-soft:#1b3442;--blue-line:#2f6a86;
 --green:#79d634;--green-btn:#58cc02;--green-bg:#1f3524;--green-line:#3f6b2a;
 --red:#ff7878;--red-bg:#3b2226;--red-line:#7a3a3f;
 --amber:#ffb84d;--amber-bg:#3a2e17;--key-bg:#2c2a1a;--key-line:#6b5a1f;
 --snow:#eaf2f6;--snow-line:#8fa3ad;--hat:#0d161a;--nose:#ff9600;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
body{margin:0;background:var(--bg);color:var(--text);font-family:var(--font);font-size:16px;line-height:1.75;
 -webkit-font-smoothing:antialiased;}
.wrap{max-width:42rem;margin:0 auto;padding:3.4rem 1.25rem 5rem;}
[hidden]{display:none!important}
a{color:var(--blue);}
button{font-family:var(--font);}
:focus-visible{outline:3px solid var(--blue-line);outline-offset:2px;}

/* 实体按钮：2px 描边 + 底边加厚，按下去会「沉」一下 */
.chunk{appearance:none;display:inline-flex;align-items:center;justify-content:center;gap:.4rem;min-height:40px;
 padding:.25rem 1rem;border:2px solid var(--line);border-bottom-width:4px;border-radius:14px;background:var(--surface);
 color:var(--text);font:inherit;font-weight:800;font-size:.9rem;cursor:pointer;text-decoration:none;
 transition:transform .05s ease,border-bottom-width .05s ease;}
.chunk:hover{background:var(--soft);}
.chunk:active{transform:translateY(2px);border-bottom-width:2px;}
.chunk--blue{color:var(--blue);}

.blognav{position:absolute;top:12px;left:12px;z-index:5;display:flex;gap:.5rem;}
.blognav a{min-height:36px;padding:0 .8rem;font-size:.82rem;}
.theme-btn{position:absolute;top:10px;right:10px;z-index:5;width:40px;height:40px;min-height:40px;padding:0;
 border-radius:50%;font-size:18px;}

/* ── 页头 ── */
.top{display:flex;align-items:center;gap:.9rem;margin:0 0 .4rem;}
.top .snowman{width:58px;height:70px;flex:none;}
.top h1{margin:0;font-weight:900;font-size:clamp(34px,8vw,44px);line-height:1.05;color:var(--ink);letter-spacing:.01em;}
.top p{margin:.15rem 0 0;font-weight:800;color:var(--muted);font-size:.95rem;}
.stats{display:flex;flex-wrap:wrap;gap:.5rem;margin:1.2rem 0 1rem;padding:0;list-style:none;}
.stats li{display:flex;align-items:center;gap:.35rem;padding:.25rem .8rem;border:2px solid var(--line);border-radius:12px;
 font-weight:800;font-size:.88rem;color:var(--muted);}
.stats b{font-size:1rem;color:var(--ink);font-variant-numeric:tabular-nums;}
.lede{margin:0 0 1rem;color:var(--muted);font-size:.95rem;}
.lede b{color:var(--ink);}
.demo-intro{margin:0 0 1.2rem;padding:.8rem 1rem;border:2px dashed var(--blue-line);border-radius:14px;background:var(--blue-soft);font-size:.93rem;}

/* 搜索 */
.find{position:sticky;top:env(safe-area-inset-top,0px);z-index:6;margin:0 -1.25rem 1rem;padding:.6rem 1.25rem;
 background:color-mix(in srgb,var(--bg) 94%,transparent);backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px);}
.find label{display:flex;align-items:center;gap:.6rem;padding:0 1rem;min-height:48px;border:2px solid var(--line);
 border-radius:16px;background:var(--soft);}
.find label:focus-within{border-color:var(--blue-line);background:var(--surface);}
.find input{flex:1;min-width:0;border:0;background:transparent;color:var(--ink);font:inherit;font-weight:700;font-size:1rem;outline:none;}
.find input::placeholder{color:var(--faint);font-weight:700;}
.find__n{font-size:.8rem;font-weight:800;color:var(--muted);white-space:nowrap;}
.find__none{margin:.4rem 0 1rem;padding:.8rem 1rem;border-radius:14px;background:var(--soft);font-weight:700;}

/* 目录 */
.toc{margin:0 0 1.8rem;border:2px solid var(--line);border-radius:16px;background:var(--surface);scroll-margin-top:5rem;overflow:hidden;}
.toc summary{display:flex;align-items:baseline;gap:.7rem;padding:.85rem 1rem;cursor:pointer;font-weight:900;font-size:1.05rem;
 color:var(--ink);list-style:none;}
.toc summary::-webkit-details-marker{display:none;}
.toc summary::after{content:"展开";margin-left:auto;font-size:.8rem;font-weight:800;color:var(--blue);}
.toc[open] summary::after{content:"收起";}
.toc summary small{font-weight:700;color:var(--muted);font-size:.82rem;}
.tabs{display:flex;flex-wrap:wrap;gap:.45rem;padding:0 1rem .8rem;}
.tab.is-on{background:var(--blue-soft);border-color:var(--blue-line);color:var(--blue);}
.pane{padding:0 0 .5rem;}
.pane h4{margin:.5rem 0 0;padding:.3rem 1rem;background:var(--soft);color:var(--muted);font-size:.8rem;font-weight:900;letter-spacing:.06em;}
.pane ul{list-style:none;margin:0;padding:0;}
.pane li a{display:flex;align-items:baseline;gap:.6rem;padding:.4rem 1rem;color:var(--text);text-decoration:none;
 border-bottom:2px solid var(--soft);line-height:1.5;}
.pane li a:hover{background:var(--soft);}
.pane .no{font-weight:800;font-size:.8rem;color:var(--faint);font-variant-numeric:tabular-nums;white-space:nowrap;}
.pane .t{flex:1;min-width:0;font-size:.93rem;font-weight:700;}
.pane .pt{padding:.35rem 1rem 0;font-size:.8rem;font-weight:800;color:var(--muted);}
.pane .x{font-size:.72rem;font-weight:900;padding:0 .5rem;border-radius:8px;background:var(--blue-soft);color:var(--blue);white-space:nowrap;}
.pane .w{font-weight:900;font-size:1.02rem;color:var(--ink);white-space:nowrap;}
.pane .wt{font-size:.72rem;font-weight:800;padding:0 .45rem;border-radius:8px;background:var(--soft);color:var(--muted);white-space:nowrap;}
.pane .wz{flex:1;min-width:0;font-size:.9rem;}
.letters{display:flex;flex-wrap:wrap;gap:.3rem;padding:.2rem 1rem .5rem;}
.letters a{min-width:2.1rem;min-height:2.1rem;padding:0 .4rem;font-size:.9rem;}
.copyline{display:flex;align-items:center;gap:.6rem;padding:.2rem 1rem .6rem;font-size:.84rem;font-weight:700;color:var(--muted);}
.copyline .chunk{margin-left:auto;}

/* ── 单元横幅（大类）与知识点分隔线 ── */
.area{scroll-margin-top:5rem;}
.area__head{display:flex;align-items:center;gap:.8rem;margin:2.6rem 0 1rem;padding:.9rem 1.1rem;border-radius:16px;
 background:var(--hue);border-bottom:4px solid color-mix(in srgb,var(--hue) 72%,#000);color:#fff;}
.area__head .ico{font-size:1.6rem;line-height:1;}
.area__head div{flex:1;min-width:0;}
.area__head small{display:block;font-size:.76rem;font-weight:800;letter-spacing:.08em;opacity:.85;}
.area__head h2{margin:0;font-size:1.2rem;font-weight:900;line-height:1.35;}
.area__head .cnt{flex:none;padding:.15rem .7rem;border-radius:10px;background:rgba(255,255,255,.22);font-weight:900;font-size:.85rem;}
.point{display:flex;align-items:center;gap:.8rem;margin:1.8rem 0 1rem;font-size:.95rem;font-weight:900;color:var(--muted);
 scroll-margin-top:5rem;}
.point::before,.point::after{content:"";flex:1;height:2px;background:var(--line);}
.point span{text-align:center;max-width:80%;}
.point small{display:block;font-size:.76rem;font-weight:700;color:var(--faint);}
.xref{display:flex;align-items:baseline;flex-wrap:wrap;gap:.2rem .6rem;margin:0 0 1rem;padding:.6rem 1rem;border:2px dashed var(--line);
 border-radius:14px;color:var(--text);text-decoration:none;font-size:.9rem;font-weight:700;}
.xref:hover{border-color:var(--blue-line);}
.xref b{color:var(--faint);font-weight:900;}
.xref small{color:var(--muted);font-weight:700;}

/* 日子分组 */
.day{scroll-margin-top:5rem;}
.day__head{display:flex;align-items:center;gap:.8rem;margin:2rem 0 1rem;font-size:1rem;font-weight:900;color:var(--muted);}
.day__head::after{content:"";flex:1;height:2px;background:var(--line);}
.day__head small{order:3;font-size:.8rem;font-weight:800;color:var(--faint);}
.chips{display:flex;flex-wrap:wrap;gap:.35rem;margin:.2rem 0 0;}
.chip{display:inline-flex;align-items:center;gap:.25rem;padding:.05rem .6rem;border:2px solid var(--line);border-radius:10px;
 font-size:.76rem;font-weight:800;color:var(--muted);}

/* ── 一张卡＝一句话：句子打头 → 意思 → 你写的 / 答案 → 卡点 → 讲解 ── */
.card{padding:1rem 1.2rem .2rem;}
.card__no{display:inline-flex;align-items:center;justify-content:center;min-width:30px;height:30px;padding:0 .4rem;border-radius:10px;
 background:var(--ink);color:var(--bg);font-size:.95rem;font-weight:900;font-variant-numeric:tabular-nums;}
.sent{display:flex;align-items:flex-start;gap:.15rem;margin:.7rem 0 .2rem;}
.sent h3{margin:0 0 0 .3rem;font-size:1.45rem;font-weight:900;line-height:1.35;color:var(--ink);overflow-wrap:anywhere;}
.sent .say{margin-top:.1rem;}
.say--slow{font-size:1.15rem;}
.sent--q h3{margin:0;font-size:1.2rem;}
.mean{margin:0 0 .1rem;font-weight:700;color:var(--muted);}
.mean[lang="en"]{font-size:.9rem;color:var(--faint);}
.answers{display:grid;gap:.45rem;margin:.8rem 0 .2rem;}
.ans{display:flex;align-items:baseline;flex-wrap:wrap;gap:.2rem .7rem;padding:.55rem .9rem;border:2px solid var(--line);border-radius:14px;}
.ans b{flex:none;font-size:.82rem;font-weight:900;}
.ans p{margin:0;min-width:0;font-weight:800;font-size:1.08rem;overflow-wrap:anywhere;}
.ans.is-ok,.ans.is-typo{background:var(--green-bg);border-color:var(--green-line);color:var(--green);}
.ans.is-wrong{background:var(--red-bg);border-color:var(--red-line);color:var(--red);}
.ans mark{background:none;color:inherit;border-bottom:2px solid currentColor;border-radius:0;padding:0 .05em;}
.ans .tiles{border:0;margin:0;padding:.1rem 0;}
.ans .tile{min-height:38px;font-size:.98rem;background:var(--surface);border-color:var(--green-line);color:var(--green);}
.stuck{margin:.6rem 0 0;font-weight:700;color:var(--text);}
.stuck b{display:inline-block;margin-right:.6em;padding:0 .5rem;border-radius:8px;background:var(--amber-bg);color:var(--amber);font-size:.78rem;font-weight:900;}
.tip{margin:1rem -1.2rem 0;}
.tip__h{margin:0 0 .5rem;font-size:.78rem;font-weight:900;letter-spacing:.12em;color:var(--faint);}
.lesson{margin:0 0 .5rem;font-size:1.05rem;font-weight:900;color:var(--ink);}
.sub{margin:.9rem 0 .4rem;font-size:.92rem;font-weight:900;color:var(--ink);}
.sub small{font-weight:700;color:var(--muted);}
.card__foot{margin:0 -1.2rem;}
.pane .t small{display:block;font-size:.8rem;font-weight:700;color:var(--muted);}

/* ── 一张卡 ── */
.card{position:relative;margin:0 0 2rem;background:var(--surface);border:2px solid var(--line);border-bottom-width:4px;
 border-radius:20px;scroll-margin-top:5rem;overflow:hidden;}
.card:target{border-color:var(--blue-line);box-shadow:0 0 0 4px var(--blue-soft);}
.card__top{padding:1rem 1.2rem .2rem;}
.card__meta{display:flex;flex-wrap:wrap;align-items:center;gap:.35rem .6rem;font-weight:800;font-size:.82rem;color:var(--faint);
 font-variant-numeric:tabular-nums;}
.pill{display:inline-flex;align-items:center;padding:0 .6rem;border-radius:10px;font-size:.75rem;font-weight:900;line-height:1.8;white-space:nowrap;}
.pill--wrong{background:var(--red-bg);color:var(--red);}
.pill--ok{background:var(--green-bg);color:var(--green);}
.pill--typo{background:var(--amber-bg);color:var(--amber);}
.pill--ask{background:var(--blue-soft);color:var(--blue);}
.pill--times{background:var(--blue);color:#fff;}
.pill--new{border:2px solid var(--blue-line);color:var(--blue);line-height:1.6;}
.pill--demo{border:2px dashed var(--faint);color:var(--muted);line-height:1.6;}
.card__meta .pill:first-of-type{margin-left:auto;}
.card__title{margin:.35rem 0 .2rem;font-size:1.22rem;font-weight:900;line-height:1.45;color:var(--ink);}
.crumb{margin:0;font-size:.8rem;font-weight:700;color:var(--muted);}
.crumb a{color:inherit;text-decoration:none;border-bottom:2px dotted var(--line-deep);}
.crumb a:hover{color:var(--blue);}
.crumb .also{display:inline-block;}

/* 做题区 */
.ex{padding:.8rem 1.2rem 0;}
.ex__task{margin:0 0 .7rem;font-size:1.3rem;font-weight:900;color:var(--ink);line-height:1.3;}
.stage{display:flex;align-items:flex-end;gap:.7rem;margin:0 0 .9rem;}
.stage .snowman{width:62px;height:76px;flex:none;}
.bubble{position:relative;min-width:0;padding:.65rem .9rem;border:2px solid var(--line);border-radius:16px;background:var(--surface);}
.bubble::before{content:"";position:absolute;left:-10px;bottom:18px;width:16px;height:16px;background:var(--surface);
 border-left:2px solid var(--line);border-bottom:2px solid var(--line);transform:rotate(45deg);}
.bubble__line{display:flex;align-items:flex-start;gap:.45rem;margin:0;font-weight:700;font-size:1.18rem;line-height:1.5;color:var(--ink);overflow-wrap:anywhere;}
.bubble__zh{margin:.25rem 0 0;font-size:.88rem;font-weight:700;color:var(--muted);}
.audio{display:flex;border:2px solid var(--line);border-bottom-width:4px;border-radius:16px;overflow:hidden;}
.audio .say{width:74px;height:58px;border-radius:0;}
.audio .say+.say{border-left:2px solid var(--line);}
.audio .say svg{width:30px;height:30px;}
.audio .say .turtle{font-size:1.6rem;line-height:1;}
.answer{margin:0 0 .9rem;padding:.75rem 1rem;min-height:3.2rem;border:2px solid var(--line);border-radius:16px;background:var(--soft);
 font-weight:700;font-size:1.12rem;color:var(--ink);overflow-wrap:anywhere;}
.answer.is-ok,.answer.is-typo{background:var(--green-bg);border-color:var(--green-line);color:var(--green);}
.answer.is-wrong{background:var(--red-bg);border-color:var(--red-line);color:var(--red);}
.answer .blank{border-bottom:2px solid currentColor;padding:0 .2em;}
.answer mark{background:none;color:inherit;border-bottom:2px solid currentColor;padding:0 .1em;}
.tiles{display:flex;flex-wrap:wrap;gap:.45rem;margin:0 0 .9rem;padding:.6rem 0;border-top:2px solid var(--line);border-bottom:2px solid var(--line);}
.tile{display:inline-flex;align-items:center;min-height:44px;padding:.2rem .85rem;border:2px solid var(--line);border-bottom-width:4px;
 border-radius:14px;background:var(--surface);font-weight:700;font-size:1.05rem;color:var(--ink);}
.tiles.is-ok .tile{background:var(--green-bg);border-color:var(--green-line);color:var(--green);}
.tiles.is-wrong .tile{background:var(--red-bg);border-color:var(--red-line);color:var(--red);}
/* 底下那条结果 */
.result{margin:0 -1.2rem;padding:.9rem 1.2rem 1rem;background:var(--green-bg);color:var(--green);}
.result.is-wrong{background:var(--red-bg);color:var(--red);}
.result__verdict{display:flex;align-items:center;gap:.6rem;margin:0 0 .35rem;font-size:1.3rem;font-weight:900;}
.result__icon{display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;flex:none;border-radius:50%;
 background:var(--surface);font-size:1.05rem;}
.result p{margin:0;}
.result__label{margin-top:.35rem!important;font-weight:900;font-size:.95rem;}
.result__sol{display:flex;align-items:flex-start;gap:.4rem;font-weight:700;font-size:1.1rem;}
.result__sol mark{background:none;color:inherit;border-bottom:2px solid currentColor;}
.result__mean{font-weight:700;}
.result__mean+.result__mean{font-size:.92rem;opacity:.85;}
.result .say{color:inherit;}
/* 她问的：右边一个聊天气泡 */
.chat{display:flex;justify-content:flex-end;margin:0 0 .9rem;}
.chat p{margin:0;max-width:85%;padding:.6rem .95rem;border-radius:18px 18px 4px 18px;background:var(--blue-soft);
 border:2px solid var(--blue-line);color:var(--ink);font-weight:700;}
.chat small{display:block;font-size:.72rem;font-weight:900;color:var(--blue);letter-spacing:.06em;}

/* ── 讲解（像多邻国的「小贴士」） ── */
.tip{padding:1rem 1.2rem .4rem;border-top:2px solid var(--line);}
.tip h4{display:flex;align-items:center;gap:.4rem;margin:1rem 0 .45rem;font-size:.95rem;font-weight:900;color:var(--ink);}
.tip h4:first-child{margin-top:0;}
.why p{margin:0 0 .6rem;font-size:.97rem;}
.key{display:flex;gap:.6rem;align-items:flex-start;margin:.3rem 0 .9rem;padding:.75rem .95rem;border:2px solid var(--key-line);
 border-radius:16px;background:var(--key-bg);color:var(--ink);font-weight:800;}
.key span{flex:none;font-size:1.1rem;line-height:1.5;}
.tbl{overflow-x:auto;margin:.2rem 0 .9rem;border:2px solid var(--line);border-radius:14px;-webkit-overflow-scrolling:touch;}
.tbl table{width:100%;border-collapse:collapse;font-size:.92rem;}
.tbl th,.tbl td{padding:.45rem .7rem;text-align:left;vertical-align:top;}
.tbl th{background:var(--soft);color:var(--muted);font-size:.78rem;font-weight:900;white-space:nowrap;}
.tbl tr+tr td{border-top:2px solid var(--soft);}
.tbl td{font-weight:800;color:var(--ink);}
.tbl td.zh{font-weight:700;font-size:.86rem;color:var(--muted);}
.tbl td:first-child{white-space:nowrap;}
mark{color:inherit;background:transparent;border-radius:.3em;padding:0 .12em;
 background:color-mix(in srgb,var(--blue-line) 45%,transparent);-webkit-box-decoration-break:clone;box-decoration-break:clone;}
mark.wrong{background:color-mix(in srgb,var(--red-line) 60%,transparent);}
mark.right{background:color-mix(in srgb,var(--green-line) 70%,transparent);}
.extra{list-style:none;margin:0 0 .7rem;padding:0;font-size:.93rem;}
.extra li{margin:0 0 .45rem;}
.extra strong{display:inline-block;margin-right:.5em;padding:0 .5rem;border-radius:8px;background:var(--soft);color:var(--muted);
 font-size:.76rem;font-weight:900;}
.phr{list-style:none;margin:0 0 .7rem;padding:0;}
.phr li{display:flex;align-items:flex-start;gap:.6rem;padding:.35rem 0;}
.phr .say{width:36px;height:36px;border-radius:50%;background:var(--blue-soft);color:var(--blue);}
.phr .say svg{width:18px;height:18px;}
.phr .pl{font-weight:800;font-size:1.06rem;color:var(--ink);}
.phr small{display:block;font-weight:700;font-size:.86rem;color:var(--muted);}
.words{display:flex;flex-wrap:wrap;gap:.6rem;margin:0 0 .8rem;padding:0;list-style:none;}
.words li{display:flex;flex-direction:column;align-items:flex-start;gap:.15rem;}
.words .tile{gap:.4rem;cursor:pointer;}
.words .tile:active{transform:translateY(2px);border-bottom-width:2px;}
.words .tile .wt{font-size:.7rem;font-weight:900;padding:0 .4rem;border-radius:7px;background:var(--soft);color:var(--muted);}
.words .wz{font-size:.82rem;font-weight:700;color:var(--muted);padding-left:.3rem;}
.words .look{font-size:.74rem;font-weight:800;text-decoration:none;padding-left:.3rem;}
.see{margin:.2rem 0 .7rem;font-size:.9rem;font-weight:700;}
.times{margin:.4rem 0 .6rem;font-size:.84rem;font-weight:700;color:var(--muted);}
.winter{display:flex;justify-content:flex-end;margin:.6rem 0;}
.winter div{max-width:88%;padding:.6rem .95rem;border-radius:18px 18px 4px 18px;background:var(--blue-soft);border:2px solid var(--blue-line);}
.winter span{display:block;font-size:.72rem;font-weight:900;color:var(--blue);}
.winter p{margin:0;}
.qa{margin:.6rem 0;}
.qa p{margin:0 0 .4rem;padding:.55rem .9rem;border-radius:16px;font-size:.93rem;}
.qa .q{margin-left:auto;max-width:88%;width:fit-content;background:var(--blue-soft);}
.qa .a{max-width:92%;background:var(--soft);}
.qa b{margin-right:.5em;font-size:.76rem;font-weight:900;color:var(--blue);}

/* 听：按钮 */
.say{appearance:none;flex:none;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;
 border:0;border-radius:10px;background:transparent;color:var(--blue);cursor:pointer;padding:0;}
.say:hover{background:var(--blue-soft);}
.say svg{width:24px;height:24px;}
.say.is-on{animation:say .9s ease-in-out infinite;}
@keyframes say{50%{opacity:.35}}
@media (prefers-reduced-motion:reduce){.say.is-on{animation:none;}}
.tile.say{width:auto;height:auto;color:var(--ink);}

.card__foot{display:flex;flex-wrap:wrap;align-items:center;justify-content:flex-end;gap:.5rem .6rem;padding:.6rem 1.2rem 1rem;}
.card__back{margin-right:auto;font-size:.82rem;font-weight:800;color:var(--muted);text-decoration:none;}
.card__back:hover{color:var(--blue);}

/* 小雪人（站里的吉祥物，代替多邻国的角色） */
.snowman .ball{fill:var(--snow);stroke:var(--snow-line);stroke-width:1.4;}
.snowman .hat{fill:var(--hat);}
.snowman .band{fill:var(--hue,#1899d6);}
.snowman .nose{fill:var(--nose);}
.snowman .ink{fill:var(--hat);}
.snowman .line{stroke:var(--hat);}

.foot{margin-top:3rem;padding-top:1.2rem;border-top:2px solid var(--line);color:var(--muted);font-size:.88rem;font-weight:700;}
.foot p{margin:0 0 .5rem;}
details.tipbox{margin-top:1rem;}
details.tipbox summary{cursor:pointer;color:var(--blue);font-weight:900;}
.tips{margin:.8rem 0 0;padding:0;list-style:none;counter-reset:tip;}
.tips li{position:relative;margin:0 0 .55rem;padding-left:2.1rem;color:var(--text);}
.tips li::before{counter-increment:tip;content:counter(tip);position:absolute;left:0;top:.1em;width:1.5rem;height:1.5rem;
 border:2px solid var(--line);border-radius:50%;text-align:center;font-size:.8rem;font-weight:900;line-height:1.3rem;color:var(--blue);}
.toast{position:fixed;left:50%;bottom:calc(18px + env(safe-area-inset-bottom,0px));transform:translate(-50%,calc(100% + 40px));z-index:30;
 visibility:hidden;max-width:calc(100vw - 32px);padding:.6rem 1rem;border-radius:14px;background:var(--ink);color:var(--bg);
 font-weight:700;font-size:.88rem;box-shadow:0 8px 24px -8px rgba(0,0,0,.45);transition:transform .25s ease;}
.toast.is-on{transform:translate(-50%,0);visibility:visible;}
@media (max-width:480px){
 .wrap{padding:3.4rem 1rem 5rem;}
 .find{margin:0 -1rem 1rem;padding:.6rem 1rem;}
 .card{padding:.9rem 1rem .2rem;}
 .tip,.card__foot{margin-left:-1rem;margin-right:-1rem;}
 .sent h3{font-size:1.3rem;}
 .ex,.tip{padding-left:1rem;padding-right:1rem;}
 .result{margin:0 -1rem;padding-left:1rem;padding-right:1rem;}
 .card__foot{padding:.6rem 1rem 1rem;}
 .stage .snowman{width:52px;height:64px;}
 .ex__task{font-size:1.18rem;}
}
'''

JS = r'''
(function () {
  var root = document.documentElement, b = document.querySelector('.theme-btn');
  function paint() { var d = root.getAttribute('data-theme') === 'dark';
    b.textContent = d ? '🌑' : '🌕'; b.setAttribute('aria-label', d ? '现在是夜间，切到明亮' : '现在是明亮，切到夜间'); }
  try { var mine = localStorage.getItem('ws-polish-theme');
    if ((mine || localStorage.getItem('wiw-theme')) === 'dark') root.setAttribute('data-theme', 'dark'); } catch (e) {}
  paint();
  b.addEventListener('click', function () {
    var d = root.getAttribute('data-theme') === 'dark';
    if (d) root.removeAttribute('data-theme'); else root.setAttribute('data-theme', 'dark');
    try { localStorage.setItem('ws-polish-theme', d ? 'light' : 'dark'); } catch (e) {}
    paint();
  });
})();
var toastEl = document.querySelector('.toast'), toastT = null;
function toast(msg) { toastEl.textContent = msg; toastEl.classList.add('is-on');
  clearTimeout(toastT); toastT = setTimeout(function () { toastEl.classList.remove('is-on'); }, 2600); }
(function () {   // 🔊 用设备自带的语音（iPhone 上的波兰语是 Zosia）；🐢 是慢速
  var ss = window.speechSynthesis;
  if (!ss || !window.SpeechSynthesisUtterance) return;
  var voices = [];
  function load() { try { voices = ss.getVoices() || []; } catch (e) { voices = []; } }
  load(); if ('onvoiceschanged' in ss) ss.onvoiceschanged = load;
  function voiceFor(lang) { var p = new RegExp('^' + lang.slice(0, 2), 'i');
    for (var i = 0; i < voices.length; i++) if (p.test(voices[i].lang || '')) return voices[i]; return null; }
  var warned = false;
  [].forEach.call(document.querySelectorAll('.say'), function (btn) {
    btn.hidden = false;
    btn.addEventListener('click', function () {
      if (!voices.length) load();
      var lang = btn.getAttribute('data-lang') || 'pl-PL', v = voiceFor(lang);
      if (!v && voices.length && !warned && lang === 'pl-PL') { warned = true;
        toast('这台设备好像没装波兰语语音，读出来可能不准。可以点卡片底下的「复制去 Google 翻译听」。'); }
      try {
        ss.cancel();
        var u = new SpeechSynthesisUtterance(btn.getAttribute('data-say'));
        u.lang = lang; if (v) u.voice = v; u.rate = parseFloat(btn.getAttribute('data-rate') || '0.9');
        btn.classList.add('is-on');
        u.onend = u.onerror = function () { btn.classList.remove('is-on'); };
        ss.speak(u);
      } catch (e) {}
    });
  });
})();
[].forEach.call(document.querySelectorAll('.copy'), function (btn) {
  btn.addEventListener('click', function () {
    var t = btn.getAttribute('data-copy');
    var label = btn.getAttribute('data-label') || btn.textContent;
    btn.setAttribute('data-label', label);
    function done(ok) { btn.textContent = ok ? '已复制 ✓' : '复制不了，长按文字手动复制'; setTimeout(function () { btn.textContent = label; }, 1600); }
    function fallback() {
      try { var ta = document.createElement('textarea'); ta.value = t; ta.setAttribute('readonly', '');
        ta.style.position = 'fixed'; ta.style.opacity = '0'; document.body.appendChild(ta); ta.select(); ta.setSelectionRange(0, t.length);
        var ok = document.execCommand('copy'); document.body.removeChild(ta); done(ok); } catch (e) { done(false); }
    }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(t).then(function () { done(true); }, fallback);
    else fallback();
  });
});
(function () {   // 目录的页签
  var tabs = [].slice.call(document.querySelectorAll('.tab'));
  tabs.forEach(function (t) {
    t.addEventListener('click', function () {
      tabs.forEach(function (x) { var on = x === t; x.classList.toggle('is-on', on); x.setAttribute('aria-selected', on);
        document.getElementById(x.getAttribute('aria-controls')).hidden = !on; });
    });
  });
})();
(function () {   // 搜索：不用打字母上的小符号，空格分开的几个词要全部对上
  var input = document.querySelector('.find input'); if (!input) return;
  var n = document.querySelector('.find__n'), none = document.querySelector('.find__none');
  var cards = [].slice.call(document.querySelectorAll('.card[data-s]'));
  var blocks = [].slice.call(document.querySelectorAll('.day, .toc'));
  function fold(s) { return (s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/ł/g, 'l'); }
  input.addEventListener('input', function () {
    var q = fold(input.value).split(/\s+/).filter(Boolean);
    if (!q.length) { cards.forEach(function (c) { c.hidden = false; }); blocks.forEach(function (x) { x.hidden = false; });
      n.textContent = ''; none.hidden = true; return; }
    var hit = 0;
    cards.forEach(function (c) { var s = c.getAttribute('data-s');
      var ok = q.every(function (w) { return s.indexOf(w) >= 0; }); c.hidden = !ok; if (ok) hit++; });
    blocks.forEach(function (x) {
      x.hidden = x.classList.contains('toc') || !x.querySelector('.card[data-s]:not([hidden])');
    });
    n.textContent = '找到 ' + hit + ' 句'; none.hidden = hit > 0;
  });
})();
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
          if (code === 'unavailable' || code === 'not_granted' || code === 'capability_disabled' || code === 'capability_removed') off();
        });
      });
    });
  }).catch(function () {});
})();
'''

SPEAKER = ('<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M3 9.5v5a1 1 0 0 0 1 1h3.2l4.3 3.6a.9.9 0 0 0 1.5-.7V5.6'
           'a.9.9 0 0 0-1.5-.7L7.2 8.5H4a1 1 0 0 0-1 1z"/><path d="M15.6 8.6a5 5 0 0 1 0 6.8" fill="none" stroke="currentColor" '
           'stroke-width="2.2" stroke-linecap="round"/><path d="M18.4 5.9a9 9 0 0 1 0 12.2" fill="none" stroke="currentColor" '
           'stroke-width="2.2" stroke-linecap="round"/></svg>')

# 站里的小雪人（_includes/snowman.html 同一只），帽带颜色跟着这一类的颜色走
SNOWMAN = ('<svg class="snowman" viewBox="0 0 66 80" aria-hidden="true" focusable="false">'
           '<path class="hat" d="M23 21h20v-9a2 2 0 0 0-2-2H25a2 2 0 0 0-2 2z"/>'
           '<rect class="hat" x="17" y="20" width="32" height="4" rx="2"/>'
           '<rect class="band" x="23" y="15" width="20" height="3"/>'
           '<circle class="ball" cx="33" cy="59" r="17"/><circle class="ball" cx="33" cy="35" r="13"/>'
           '<circle class="ink" cx="28.5" cy="33" r="1.9"/><circle class="ink" cx="37.5" cy="33" r="1.9"/>'
           '<path class="nose" d="M33 36l8 2.5-8 2z"/>'
           '<path class="line" d="M28 41.5q5 3.5 10 0" fill="none" stroke-width="1.3" stroke-linecap="round"/>'
           '<path class="line" d="M19 55l-11-7M47 55l11-7" fill="none" stroke-width="1.5" stroke-linecap="round"/>'
           '<circle class="ink" cx="33" cy="54" r="1.7"/><circle class="ink" cx="33" cy="61" r="1.7"/>'
           '<circle class="ink" cx="33" cy="68" r="1.7"/></svg>')


# ── 小工具 ──
def esc(s):
    return html.escape(str(s), quote=True)


def fmt(s, mark=''):
    """纯文本转义 + 两个行内记号：==高亮== / **粗体**。"""
    s = html.escape(str(s).strip(), quote=False)
    cls = f' class="{mark}"' if mark else ''
    s = re.sub(r'==(.+?)==', rf'<mark{cls}>\1</mark>', s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    return s.replace('\n', '<br>')


def plain(s):
    return re.sub(r'==|\*\*', '', str(s or '')).strip()


def as_list(v):
    if v in (None, '', []):
        return []
    return v if isinstance(v, list) else [v]


def fold(s):
    s = unicodedata.normalize('NFD', str(s or '').lower())
    return ''.join(c for c in s if not unicodedata.combining(c)).replace('ł', 'l')


def pl_key(w):
    w = str(w).lower()
    return tuple(PL_ORDER.index(c) if c in PL_ORDER else 100 + ord(c) for c in w)


def stop(s):
    """复制去 Google 翻译时每行都要有句末标点，不然它会把几行连着读（她的老习惯，见课本教辅 skill）。"""
    s = plain(s)
    return s if re.search(r'[.!?…]$', s) else s + '.'


def as_date(d):
    if isinstance(d, datetime.date):
        return d
    return datetime.date.fromisoformat(str(d))


def cn_date(d, year=None):
    d = as_date(d)
    return (f'{d.year}年' if year and d.year != year else '') + f'{d.month}月{d.day}日'


def say_btn(text, lang='pl', cls='say', inner=None, rate=None, label='听'):
    r = f' data-rate="{rate}"' if rate else ''
    return (f'<button type="button" class="{cls}" data-say="{esc(plain(text))}" data-lang="{"en-US" if lang == "en" else "pl-PL"}"{r} '
            f'aria-label="{label}" hidden>{SPEAKER if inner is None else inner}</button>')


# ── 数据 ──
def load(demo):
    data = yaml.safe_load(open(DATA, encoding='utf-8')) or {}
    meta, areas = data.get('meta') or {}, data.get('areas') or []
    notes = data.get('notes') or []
    is_demo = not notes
    if is_demo:
        notes = demo.get('notes') or []

    points = {}
    for a in areas:
        for p in a.get('points') or []:
            points[f'{a["key"]}.{p["key"]}'] = (a, p)

    index = {}
    for x in notes:
        xid = str(x.get('id', ''))
        if not re.fullmatch(r'\d{3,}', xid):
            sys.exit(f'笔记编号要写成三位数字的字符串，如 "007"：{xid!r}')
        if xid in index:
            sys.exit(f'笔记编号重复：{xid}')
        for f in ('date', 'point', 'title', 'why'):
            if not x.get(f):
                sys.exit(f'No. {xid} 缺 {f}')
        for p in [x['point']] + as_list(x.get('also')):
            if p not in points:
                sys.exit(f'No. {xid} 的知识点 {p!r} 不在 areas 里（写成「大类.知识点」，如 noun.gen；都不合适就先去 areas 里加）')
        if x.get('task') and x['task'] not in TASKS:
            sys.exit(f'No. {xid} 的 task 只能是 {"/".join(TASKS)}')
        index[xid] = x
    for x in notes:
        for s in as_list(x.get('see')):
            if str(s) not in index:
                sys.exit(f'No. {x["id"]} 的 see 指向不存在的编号 {s}')
    return meta, areas, points, notes, index, is_demo


def times(x):
    return 1 + len(as_list(x.get('asked')))


def last_date(x):
    return max([as_date(x['date'])] + [as_date(d) for d in as_list(x.get('asked'))])


def kind_of(x):
    """做错了 / 差一点（多邻国判「拼写错误」）/ 答对了 / 有疑问"""
    if x.get('ok'):
        return 'ok'
    if x.get('typo'):
        return 'typo'
    return 'wrong' if x.get('mine') else 'ask'


def search_text(x, points):
    a, p = points[x['point']]
    bits = [x.get('title'), x.get('ask'), x.get('pl'), x.get('en'), x.get('zh'), x.get('mine'),
            x.get('why'), ' '.join(as_list(x.get('rule'))), a['name'], p['name'], p.get('hint'), x.get('source'), f'no. {x["id"]}', x['id'],
            TASKS.get(x.get('task'), '')]
    bits += as_list(x.get('right')) + as_list(x.get('extra')) + as_list(x.get('winter'))
    bits += [points[k][1]['name'] for k in as_list(x.get('also'))]
    for e in as_list(x.get('examples')):
        bits += [e.get('pl'), e.get('zh')]
    for w in as_list(x.get('words')):
        bits += [w.get('pl'), w.get('zh'), w.get('tag')]
    for q in as_list(x.get('qa')):
        bits += [q.get('q'), q.get('a')]
    for t in as_list(x.get('table')):
        for row in t.get('rows') or []:
            bits += row
    return fold(' '.join(plain(b) for b in bits if b))


def copy_text(x):
    """这一张卡里所有的波兰语，一行一句、句末带标点，给 Google 翻译听。"""
    if (x.get('lang') or 'pl') != 'pl':
        return ''
    lines = []
    for s in [x.get('pl')] + as_list(x.get('right')):
        if s and stop(s) not in lines:
            lines.append(stop(s))
    ex = [stop(e['pl']) for e in as_list(x.get('examples')) if e.get('pl')]
    ws = [stop(w['pl']) for w in as_list(x.get('words')) if w.get('pl')]
    return '\n\n'.join('\n'.join(g) for g in (lines, ex, ws) if g)


# ── 一张卡＝多邻国的一句话 ──
# Winter 2026-10-01：「你还是按知识点而不是句子来的，这样太乱了」——所以卡片打头就是那句波兰语，
# 下面照她那份总结的顺序：意思 → 你写的 / 答案 → 卡点 → 讲解。知识点不上卡，只留在目录和搜索里。
SECTIONS = [('sentence', '多邻国的句子'), ('vocab', '零碎词汇'), ('en', '顺带聊到的英语')]


def section_of(x):
    return x.get('section') or ('en' if (x.get('lang') or 'pl') == 'en' else 'sentence')


def answer_block(x, kind, lang):
    """你写的 / 答案：多邻国那种绿框、红框。"""
    to_en = x.get('task') == 'translate' and (x.get('to') or 'en') == 'en'
    out = []
    if x.get('mine'):
        state = {'ok': 'is-ok', 'typo': 'is-typo', 'wrong': 'is-wrong'}[kind]
        mark = '✓' if kind in ('ok', 'typo') else '✗'
        if to_en:
            mine = ''.join(f'<span class="tile">{esc(w)}</span>' for w in plain(x['mine']).split())
            out.append(f'<div class="ans {state}"><b>{mark} 你写的</b><div class="tiles" lang="en">{mine}</div></div>')
        else:
            out.append(f'<div class="ans {state}"><b>{mark} 你写的</b><p lang="{lang}">{fmt(x["mine"], "wrong" if kind == "wrong" else "")}</p></div>')
    if kind in ('wrong', 'typo'):
        for r in as_list(x.get('right')) or [x.get('pl')]:
            out.append(f'<div class="ans is-ok"><b>✓ {"答案" if kind == "wrong" else "应该是"}</b>'
                       f'<p lang="{lang}">{fmt(r, "right")}</p></div>')
    return '<div class="answers">' + ''.join(out) + '</div>' if out else ''


def card(x, ctx):
    kind, lang, n = kind_of(x), x.get('lang') or 'pl', times(x)
    sec = section_of(x)
    meta = [f'<span class="card__no">{int(x["id"])}</span>']
    if x.get('task'):
        meta.append(f'<span class="chip">{TASKS[x["task"]]}</span>')
    if sec == 'sentence' or kind != 'ask':
        meta.append(f'<span class="pill pill--{kind}">{ {"wrong": "做错了", "typo": "差一点", "ok": "答对了", "ask": "有疑问"}[kind] }</span>')
    if n > 1:
        meta.append(f'<span class="pill pill--times">🔁 问过 {n} 次</span>')
    if ctx['show_new'] and last_date(x) == ctx['newest']:          # 全本都是同一天的就不标「新」，标了也没意义
        meta.append('<span class="pill pill--new">新</span>')
    if x.get('demo'):
        meta.append('<span class="pill pill--demo">样板 · 编的例子</span>')

    out = [f'<article class="card is-{kind}" id="n{esc(x["id"])}" data-comment-target '
           f'data-comment-label="{int(x["id"])}. {esc(plain(x.get("pl") or x["title"]))}" data-s="{esc(search_text(x, ctx["points"]))}">',
           f'<div class="card__meta">{"".join(meta)}</div>']
    # 打头：那句话（没有句子的提问，打头就是那个问题）
    if x.get('pl'):
        out.append(f'<div class="sent" lang="{lang}">{say_btn(x["pl"], lang)}'
                   + (say_btn(x['pl'], lang, 'say say--slow', '<span aria-hidden="true">🐢</span>', 0.5, '慢一点') if lang == 'pl' else '')
                   + f'<h3>{fmt(x["pl"])}</h3></div>')
        mean = ''.join(f'<p class="mean"{" lang=en" if k == "en" else ""}>{fmt(x[k])}</p>'
                       for k in ('zh', 'en') if x.get(k) and not (k == 'en' and x.get('task') == 'translate'))
        out.append(mean)
    else:
        out.append(f'<div class="sent sent--q"><h3>{fmt(x.get("ask") or x["title"])}</h3></div>')
    out.append(answer_block(x, kind, lang))
    if x.get('stuck'):
        out.append(f'<p class="stuck"><b>卡点</b>{fmt(x["stuck"])}</p>')
    if x.get('ask') and x.get('pl'):
        out.append(f'<p class="stuck"><b>疑问</b>{fmt(x["ask"])}</p>')

    tip = [f'<p class="lesson">💡 {fmt(x["title"])}</p><div class="why">'
           + ''.join(f'<p>{fmt(par)}</p>' for par in str(x['why']).strip().split('\n') if par.strip()) + '</div>']
    for r in as_list(x.get('rule')):
        tip.append(f'<p class="key"><span aria-hidden="true">📌</span>{fmt(r)}</p>')
    for t in as_list(x.get('table')):
        head = ''.join(f'<th>{fmt(h)}</th>' for h in t.get('head') or [])
        plc = set(t.get('pl') or range(1, 99))          # 哪几列是波兰语（默认第一列以外都是）
        rows = ''.join('<tr>' + ''.join(f'<td{f" lang={lang}" if i in plc else " class=zh"}>{fmt(c)}</td>'
                                        for i, c in enumerate(r)) + '</tr>' for r in t.get('rows') or [])
        tip.append(f'<div class="tbl"><table>{"<thead><tr>" + head + "</tr></thead>" if head else ""}<tbody>{rows}</tbody></table></div>')
    if x.get('extra'):
        tip.append('<ul class="extra">' + ''.join(f'<li>{fmt(e)}</li>' for e in as_list(x['extra'])) + '</ul>')
    if x.get('examples'):
        tip.append('<p class="sub">再看几句</p><ul class="phr">' + ''.join(
            f'<li>{say_btn(e["pl"], lang)}<span><span class="pl" lang="{lang}">{fmt(e["pl"])}</span>'
            f'<small>{fmt(e.get("zh", ""))}</small></span></li>' for e in as_list(x['examples'])) + '</ul>')
    if x.get('words'):
        rows = []
        for w in as_list(x['words']):
            q = w.get('look', w['pl'] if lang == 'pl' else False)   # 词组写 look: 要查的那个词；look: false 不挂链接
            tag = f'<span class="wt">{esc(w["tag"])}</span>' if w.get('tag') else ''
            rows.append('<li>' + say_btn(w['pl'], lang, 'tile say', f'<span lang="{lang}">{esc(w["pl"])}</span>{tag}', label=f'听 {plain(w["pl"])}')
                        + f'<span class="wz">{fmt(w.get("zh", ""))}</span>'
                        + (f'<a class="look" href="{ctx["polski"]}?q={esc(q)}" target="_blank" rel="noopener">查变格 ↗</a>' if q else '')
                        + '</li>')
        tip.append('<p class="sub">生词 <small>点一下听</small></p><ul class="words">' + ''.join(rows) + '</ul>')
    if x.get('see'):
        def short(s):
            y = ctx['index'][str(s)]
            return fmt(y.get('pl') or y['title'])
        tip.append('<p class="see">🔗 ' + '　'.join(f'<a href="#n{esc(s)}">{int(s)}. {short(s)}</a>' for s in as_list(x['see'])) + '</p>')
    if n > 1:
        tip.append('<p class="times">问过的日子：' + '、'.join(
            cn_date(d, ctx['year']) for d in [x['date']] + as_list(x.get('asked'))) + '</p>')
    if x.get('winter'):
        tip.append('<div class="winter"><div><span>我写的</span>' + ''.join(f'<p>{fmt(w)}</p>' for w in as_list(x['winter'])) + '</div></div>')
    if x.get('qa'):
        tip.append('<div class="qa">' + ''.join(f'<p class="q"><b>问</b>{fmt(q["q"])}</p><p class="a"><b>答</b>{fmt(q["a"])}</p>'
                                                for q in as_list(x['qa'])) + '</div>')
    out.append('<section class="tip"><p class="tip__h">讲解</p>' + ''.join(tip) + '</section>')
    ct = copy_text(x)
    out.append('<div class="card__foot"><a class="card__back" href="#toc">↑ 目录</a>'
               + (f'<button type="button" class="chunk chunk--blue copy" data-copy="{esc(ct)}">复制去 Google 翻译听</button>' if ct else '')
               + ('' if ctx['blog'] else '<button type="button" class="chunk chunk--blue card__ask" hidden>批注</button>') + '</div>')
    out.append('</article>')
    return '\n'.join(out)


# ── 目录：句子一览（默认）· 生词 · 按知识点 ──
def toc(areas, points, notes, ctx):
    def link(x, extra=''):
        head = fmt(x.get('pl') or x['title'])
        return (f'<li><a href="#n{esc(x["id"])}"><span class="no">{int(x["id"])}</span>'
                f'<span class="t"><span{" lang=pl" if x.get("pl") else ""}>{head}</span>'
                + (f'<small>{fmt(x["zh"])}</small>' if x.get('zh') else '') + f'</span>{extra}</a></li>')

    by_sent = []
    for key, name in SECTIONS:
        xs = [x for x in notes if section_of(x) == key]
        if xs:
            by_sent.append(f'<h4>{esc(name)}</h4><ul>' + ''.join(link(x) for x in xs) + '</ul>')

    used = {}
    for x in notes:
        for k in [x['point']] + as_list(x.get('also')):
            used.setdefault(k, []).append(x)
    by_point = []
    for a in areas:
        rows = []
        for p in a.get('points') or []:
            k = f'{a["key"]}.{p["key"]}'
            if k in used:
                rows.append(f'<p class="pt">{esc(p["name"])}</p><ul>' + ''.join(link(x) for x in used[k]) + '</ul>')
        if rows:
            by_point.append(f'<h4>{a["icon"]} {esc(a["name"])}</h4>' + ''.join(rows))

    words = {}
    for x in notes:
        if (x.get('lang') or 'pl') != 'pl':
            continue
        for w in as_list(x.get('words')):
            words.setdefault(w['pl'].lower(), (w, x))
    wl = sorted(words.values(), key=lambda t: pl_key(t[0]['pl']))
    letters, wrows, cur = [], [], None
    for w, x in wl:
        L = w['pl'][0].upper()
        if L != cur:
            if cur:
                wrows.append('</ul>')
            wrows.append(f'<h4 id="wl-{esc(L)}">{esc(L)}</h4><ul>')
            letters.append(f'<a class="chunk" href="#wl-{esc(L)}">{esc(L)}</a>')
            cur = L
        wrows.append(f'<li><a href="#n{esc(x["id"])}"><span class="w" lang="pl">{esc(w["pl"])}</span>'
                     + (f'<span class="wt">{esc(w["tag"])}</span>' if w.get('tag') else '')
                     + f'<span class="wz">{fmt(w.get("zh", ""))}</span><span class="no">{int(x["id"])}</span></a></li>')
    if cur:
        wrows.append('</ul>')
    word_copy = '\n'.join(stop(w['pl']) for w, _ in wl)

    reps = sorted([x for x in notes if times(x) > 1], key=lambda x: (-times(x), x['id']))
    panes = [('sent', '全部句子', ''.join(by_sent))]
    if wl:
        panes.append(('words', f'生词 {len(wl)}',
                      f'<div class="copyline">按波兰语字母顺序排。<button type="button" class="chunk chunk--blue copy" data-copy="{esc(word_copy)}">'
                      f'复制全部生词去听</button></div><div class="letters">{"".join(letters)}</div>' + ''.join(wrows)))
    if reps:
        panes.append(('again', f'🔁 问过不止一次 {len(reps)}',
                      '<ul>' + ''.join(link(x, f'<span class="x">{times(x)} 次</span>') for x in reps) + '</ul>'))
    panes.append(('point', '按知识点', ''.join(by_point)))
    tabs = ''.join(f'<button type="button" class="chunk tab{" is-on" if i == 0 else ""}" role="tab" aria-selected="{"true" if i == 0 else "false"}" '
                   f'aria-controls="pane-{k}">{esc(lbl)}</button>' for i, (k, lbl, _) in enumerate(panes))
    body = ''.join(f'<div class="pane" id="pane-{k}" role="tabpanel"{"" if i == 0 else " hidden"}>{c}</div>'
                   for i, (k, _, c) in enumerate(panes))
    return (f'<details class="toc" id="toc"><summary>📑 目录 <small>全部句子 · 生词表</small></summary>'
            f'<div class="tabs" role="tablist">{tabs}</div>{body}</details>\n')


def body(notes, ctx):
    """正文：先是多邻国的句子（按日子分组，最新的日子在上面），再是零碎词汇、顺带聊到的英语。"""
    out = []
    sents = [x for x in notes if section_of(x) == 'sentence']
    days = {}
    for x in sents:
        days.setdefault(as_date(x['date']), []).append(x)
    for d in sorted(days, reverse=True):
        xs = sorted(days[d], key=lambda x: x['id'])
        out.append(f'<section class="day" id="d{d.isoformat()}"><h2 class="day__head"><span>{cn_date(d, ctx["year"])}</span>'
                   f'<small>{len(xs)} 句</small></h2>\n' + '\n'.join(card(x, ctx) for x in xs) + '</section>')
    for key, name in SECTIONS[1:]:
        xs = [x for x in notes if section_of(x) == key]
        if xs:
            out.append(f'<section class="day" id="s-{key}"><h2 class="day__head"><span>{esc(name)}</span>'
                       f'<small>{len(xs)} 条</small></h2>\n' + '\n'.join(card(x, ctx) for x in xs) + '</section>')
    return '\n'.join(out)


def main():
    ap = argparse.ArgumentParser(description='把波兰语笔记数据渲染成网页')
    ap.add_argument('-o', '--out', help='给 Winter 看的 Artifact（改完用同一路径重新生成、发布到同一个链接）')
    ap.add_argument('--blog', action='store_true', help='生成博客上的那一页 polish/index.html')
    a = ap.parse_args()
    if not a.out and not a.blog:
        ap.error('要么给 -o（给 Winter 看的 Artifact），要么 --blog（博客上的那一页）')

    demo = yaml.safe_load(open(os.path.join(HERE, 'demo.yml'), encoding='utf-8'))
    meta, areas, points, notes, index, is_demo = load(demo)

    newest = max((last_date(x) for x in notes), default=None)
    ctx = {'points': points, 'index': index, 'blog': a.blog, 'newest': newest,
           'year': newest.year if newest else None,
           'show_new': sum(1 for x in notes if last_date(x) == newest) < len(notes),
           'polski': '../polski.html' if a.blog else f'{SITE}/polski.html'}

    used = {k for x in notes for k in [x['point']] + as_list(x.get('also'))}
    reps = sum(1 for x in notes if times(x) > 1)
    wrong = sum(1 for x in notes if kind_of(x) in ('wrong', 'typo'))
    if is_demo:
        stats = ['<li>📒 等你的第一题</li>']
    else:
        stats = [f'<li>📒 <b>{sum(1 for x in notes if section_of(x) == "sentence")}</b> 句</li>', f'<li>✗ <b>{wrong}</b> 道错题</li>']
        if reps:
            stats.append(f'<li>🔁 <b>{reps}</b> 句问过不止一次</li>')
    head = (f'<div class="top">{SNOWMAN}<div><h1 lang="pl">{esc(meta.get("title", "Notatnik"))}</h1>'
            f'<p>{esc(meta.get("sub", ""))}</p></div></div>\n'
            f'<ul class="stats">{"".join(stats)}</ul>\n<p class="lede">{fmt(demo["blog_lede" if a.blog else "lede"])}</p>\n')
    if is_demo:
        head += f'<p class="demo-intro">{fmt(demo["demo_intro"])}</p>\n'
    find = ('<div class="find"><label><span aria-hidden="true">🔍</span>'
            '<input type="search" id="find" placeholder="搜一个词、一个格、一句中文……" aria-label="搜笔记" autocomplete="off" '
            'autocapitalize="off" spellcheck="false"><span class="find__n"></span></label></div>\n'
            '<p class="find__none" hidden>没找到。可能还没问过——直接来对话里问我就行。</p>\n')
    tips = ('' if a.blog else f'<details class="tipbox"><summary>{esc(demo["tips"]["heading"])}</summary><ol class="tips">'
            + ''.join(f'<li>{fmt(t)}</li>' for t in demo['tips']['items']) + '</ol></details>')
    foot = f'<div class="foot"><p>{fmt(demo["blog_foot" if a.blog else "foot"])}</p>{tips}</div>'
    inner = (f'<button type="button" class="chunk theme-btn">🌕</button>\n<div class="wrap">\n{head}{find}'
             f'{toc(areas, points, notes, ctx)}{body(notes, ctx)}\n{foot}\n</div>\n'
             f'<div class="toast" role="status" aria-live="polite"></div>\n<script>{JS}</script>\n')

    title = '波兰语笔记本'
    if a.blog:
        a.out = os.path.join(ROOT, 'polish', 'index.html')
        os.makedirs(os.path.dirname(a.out), exist_ok=True)
        page = ('<!doctype html>\n<html lang="zh-CN">\n<head>\n<meta charset="utf-8">\n'
                '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
                f'<title>{title} · Winter Sun</title>\n'
                '<meta name="description" content="学波兰语时做错的、看不懂的地方，一题一张卡，按知识点分好类。">\n'
                '<link rel="icon" href="../favicon.ico">\n'
                '<!-- 这一页由 tools/polish/render_polish.py --blog 生成，别手改；改 _data/polish/notes.yml 再重新生成 -->\n'
                f'{FONTS}\n<style>{CSS}</style>\n</head>\n<body>\n'
                '<nav class="blognav"><a class="chunk" href="../?cat=winters">← 冬的笔记</a><a class="chunk" href="../polski.html">变格表</a></nav>\n'
                f'{inner}</body>\n</html>\n')
    else:
        page = f'<title>{title}</title>\n{FONTS}\n<style>{CSS}</style>\n{inner}'
    open(a.out, 'w', encoding='utf-8').write(page)
    print(f'✅ {a.out}（{"样板 " if is_demo else ""}{len(notes)} 句 · {len(used)} 个知识点）')


if __name__ == '__main__':
    main()
