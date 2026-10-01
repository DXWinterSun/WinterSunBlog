#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
波兰语笔记本页生成器（多邻国错题 / 疑问 → 一题一张卡，按知识点归类）

2026-10-01 Winter：「我之后能做成我在多邻国遇到错的或者有疑问的地方的时候，我就来对话里给你并且问你，
你给我解释清楚之后，顺便整理到波兰语学习的笔记里，你可以进行更好的分类以便我学习……
如果我之后还问之前问过的，你有存档可以查就可以给我指路，也会加深我的记忆。」

    python3 tools/polish/render_polish.py -o <scratchpad>/polish-notes.html   # 给她看的 Artifact
    python3 tools/polish/render_polish.py --blog                              # 博客上那一页 polish/index.html

- 数据只有一份：_data/polish/notes.yml（分类 areas + 笔记 notes）。还没有笔记时显示 demo.yml 里的两张样板。
- 第一次发布 Artifact 要带 capabilities={"comments": {"composer_only": true}}（卡片上的「批注」按钮靠它）。
  之后发布到同一个链接（记在 meta.artifact），不再传 capabilities。
- 行内记号：`==高亮==`、`**粗体**`；其余一律当纯文本转义。

完整工作法（查档、讲解、归类、发布）见 .claude/skills/winter-polish-notes/SKILL.md。
"""
import argparse, datetime, html, json, os, re, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'preview'))
from render_draft import palette          # noqa: E402  跟章节预览页、读书笔记同一套 AU 配色

import yaml                               # noqa: E402

DATA = os.environ.get('POLISH_NOTES') or os.path.join(ROOT, '_data', 'polish', 'notes.yml')   # 自测时可指向临时文件
SITE = 'https://dxwintersun.github.io/WinterSunBlog'
PL_ORDER = 'aąbcćdeęfghijklłmnńoóprsśtuvwxyzźż'   # 波兰语字母表顺序（生词表按它排）

FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Volkhov:ital,wght@0,400;0,700;1,400'
         '&family=Noto+Serif+SC:wght@400;500;600;700&family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400&display=swap">')

CSS = '''
:root{
 color-scheme:light;
 --bg:color-mix(in srgb,__ACCENT__ 6%,#fbfaf6);--accent:__INK_ACCENT__;--ink:__BG__;
 --muted:color-mix(in srgb,__BG__ 60%,#fbfaf6);
 --surface:#fffefb;--glow:rgba(255,255,255,0);
 --line:color-mix(in srgb,var(--accent) 24%,transparent);
 --band:#eef0f4;--band-ink:#5b6472;--code-bg:color-mix(in srgb,var(--accent) 8%,#fff);
 --pl:#27368f;--example:#2d63c8;
 --wrong:#c8322b;--right:#2f7d4f;--ask:#2d63c8;
 --hl-wrong:#f6b4ac;--hl-right:#a8deb9;--hl:color-mix(in srgb,__ACCENT__ 32%,#fff3c4);--hl-mix:70%;
 --paper:#f6eedf;--paper-ink:#3b3329;--note-shadow:0 6px 16px rgba(40,30,20,.14);
 --shadow:0 1px 2px rgba(20,24,31,.06),0 6px 18px -12px rgba(20,24,31,.35);
}
:root[data-theme="dark"]{
 color-scheme:dark;
 --bg:__BG__;--accent:__ACCENT__;--ink:__TEXT__;--muted:__MUTED__;
 --surface:color-mix(in srgb,var(--bg) 91%,#fff);--glow:rgba(255,255,255,.05);
 --line:color-mix(in srgb,var(--accent) 26%,transparent);
 --band:rgba(255,255,255,.06);--band-ink:#aab2bf;--code-bg:color-mix(in srgb,var(--bg) 70%,#000);
 --pl:#a9b8ff;--example:#8fb0ff;--wrong:#ef7a70;--right:#7fcf9d;--ask:#8fb0ff;
 --hl-wrong:#b34a40;--hl-right:#3f8a5c;--hl:color-mix(in srgb,__ACCENT__ 55%,transparent);--hl-mix:55%;
 --paper:#f2eadd;--note-shadow:0 8px 20px rgba(0,0,0,.34);--shadow:none;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
body{margin:0;background:var(--bg);color:var(--ink);
 font-family:"Noto Serif SC","Songti SC",Georgia,serif;font-size:16.5px;line-height:1.9;
 -webkit-font-smoothing:antialiased;}
body::before{content:"";position:fixed;inset:0;pointer-events:none;z-index:0;
 background:radial-gradient(ellipse 900px 500px at 15% -10%,var(--glow),transparent 60%);}
.wrap{position:relative;z-index:1;max-width:44rem;margin:0 auto;padding:3.2rem 1.25rem 5rem;}
[hidden]{display:none!important}
.blognav{position:absolute;top:14px;left:14px;z-index:5;display:flex;gap:.5rem;}
.blognav a{display:inline-flex;align-items:center;min-height:34px;padding:0 .85rem;border:1px solid var(--line);
 border-radius:99px;background:var(--surface);color:var(--accent);text-decoration:none;font-size:.85rem;letter-spacing:.06em;}
.theme-btn{position:absolute;top:10px;right:10px;z-index:5;width:36px;height:36px;border-radius:50%;
 border:1px solid var(--line);background:var(--surface);cursor:pointer;font-size:17px;line-height:1;padding:0;}
.theme-btn:hover{border-color:var(--accent);}

/* 页头：跟读书笔记 / 章节预览同一套 */
.console{display:flex;flex-wrap:wrap;align-items:center;gap:8px 16px;padding:13px 18px;
 border:1px solid color-mix(in srgb,var(--accent) 34%,transparent);border-radius:4px;
 background:color-mix(in srgb,var(--accent) 8%,transparent);font-family:"EB Garamond",Georgia,serif;
 font-size:13px;letter-spacing:.06em;color:var(--muted);margin-bottom:2.4rem;}
.console b{color:var(--accent);font-weight:600;}
.console .dot{width:6px;height:6px;border-radius:50%;background:var(--accent);display:inline-block;
 box-shadow:0 0 6px var(--accent);flex:none;}
.console>span+span::before{content:"|";opacity:.38;margin-right:16px;}
.console>span.dot+span::before{content:none;}
.kicker{font-family:"Volkhov",Georgia,serif;font-style:italic;color:var(--muted);font-size:15px;
 text-align:center;margin:0 0 .6rem;}
h1{font-family:"Volkhov","Noto Serif SC",Georgia,serif;font-weight:700;font-size:clamp(32px,7vw,46px);
 text-align:center;margin:0 0 .45rem;line-height:1.2;letter-spacing:.02em;}
.sub{text-align:center;color:var(--accent);font-size:1rem;letter-spacing:.12em;margin:0;}
.rule{width:60px;height:1px;background:var(--accent);opacity:.6;margin:2.2rem auto;}
.lede{margin:0 0 1rem;color:var(--muted);font-size:.95rem;line-height:1.95;}
.lede b{color:var(--ink);font-weight:600;}
.demo-intro{margin:0 0 1.4rem;padding:.8rem 1rem;border:1px dashed var(--accent);border-radius:6px;
 font-size:.93rem;background:color-mix(in srgb,var(--accent) 5%,transparent);}
.demo-intro b{color:var(--accent);}

/* 搜索 */
.find{position:sticky;top:env(safe-area-inset-top,0px);z-index:6;margin:0 -1.25rem 1rem;padding:.6rem 1.25rem;
 background:color-mix(in srgb,var(--bg) 92%,transparent);backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px);}
.find label{display:flex;align-items:center;gap:.6rem;padding:0 .9rem;min-height:44px;border:1px solid var(--line);
 border-radius:99px;background:var(--surface);}
.find label:focus-within{border-color:var(--accent);}
.find input{flex:1;min-width:0;border:0;background:transparent;color:var(--ink);font:inherit;font-size:1rem;outline:none;}
.find input::placeholder{color:var(--muted);}
.find__n{font-size:.8rem;color:var(--muted);white-space:nowrap;}
.find__none{margin:.4rem 0 1rem;padding:.8rem 1rem;border-radius:6px;background:var(--band);font-size:.93rem;}

/* 目录 */
.toc{margin:0 0 1.6rem;border:1px solid var(--line);border-radius:6px;background:var(--surface);scroll-margin-top:4.5rem;}
.toc summary{display:flex;align-items:baseline;gap:.8rem;padding:.8rem 1rem;cursor:pointer;font-weight:600;list-style:none;}
.toc summary::-webkit-details-marker{display:none;}
.toc summary::after{content:"展开 ▾";margin-left:auto;font-size:.8rem;font-weight:400;color:var(--accent);}
.toc[open] summary::after{content:"收起 ▴";}
.toc summary small{font-weight:400;color:var(--muted);font-size:.82rem;}
.tabs{display:flex;flex-wrap:wrap;gap:.4rem;padding:0 1rem .7rem;}
.tab{appearance:none;border:1px solid var(--line);background:transparent;color:var(--ink);border-radius:99px;
 padding:.2rem .9rem;font:inherit;font-size:.85rem;cursor:pointer;min-height:34px;}
.tab.is-on{background:var(--accent);border-color:transparent;color:#fff;}
.pane{padding:0 0 .6rem;}
.pane h4{margin:.4rem 0 0;padding:.25rem 1rem;background:var(--band);color:var(--band-ink);font-size:.82rem;
 font-weight:600;letter-spacing:.08em;}
.pane ul{list-style:none;margin:0;padding:0;}
.pane li a{display:flex;align-items:baseline;gap:.6rem;padding:.35rem 1rem;color:var(--ink);text-decoration:none;
 border-bottom:1px solid color-mix(in srgb,var(--line) 60%,transparent);line-height:1.55;}
.pane li a:hover{background:var(--band);}
.pane .no{font-family:"EB Garamond",Georgia,serif;font-size:.86rem;color:var(--accent);
 font-variant-numeric:tabular-nums;white-space:nowrap;}
.pane .t{flex:1;min-width:0;font-size:.93rem;}
.pane .pt{padding:.3rem 1rem 0;font-size:.8rem;color:var(--muted);letter-spacing:.06em;}
.pane .x{font-size:.75rem;font-weight:600;padding:0 .45rem;border-radius:4px;background:var(--band);color:var(--accent);white-space:nowrap;}
.pane .w{font-family:"EB Garamond",Georgia,serif;font-weight:600;font-size:1.08rem;color:var(--pl);white-space:nowrap;}
.pane .wt{font-size:.72rem;padding:0 .4rem;border-radius:4px;background:var(--band);color:var(--band-ink);white-space:nowrap;}
.pane .wz{flex:1;min-width:0;font-size:.9rem;}
.letters{display:flex;flex-wrap:wrap;gap:.15rem;padding:.2rem .8rem .5rem;}
.letters a{display:inline-flex;align-items:center;justify-content:center;min-width:1.75rem;height:1.75rem;
 border-radius:5px;font-family:"EB Garamond",Georgia,serif;font-weight:600;text-decoration:none;
 color:var(--pl);background:var(--band);}
.copyline{display:flex;align-items:center;gap:.6rem;padding:.2rem 1rem .6rem;font-size:.84rem;color:var(--muted);}
.copy{appearance:none;flex:none;margin-left:auto;min-height:32px;padding:.2rem .9rem;border-radius:99px;cursor:pointer;
 border:1px solid color-mix(in srgb,var(--accent) 45%,transparent);background:transparent;color:var(--accent);
 font:inherit;font-size:.8rem;letter-spacing:.06em;white-space:nowrap;}
.copy:hover{background:color-mix(in srgb,var(--accent) 12%,transparent);}

/* 分类标题 */
.area{scroll-margin-top:4.5rem;}
h2{font-family:"Noto Serif SC",Georgia,serif;font-weight:600;margin:3rem 0 .2rem;font-size:1.22rem;
 color:var(--accent);display:flex;align-items:baseline;gap:.6rem;flex-wrap:wrap;}
h2 .ico{font-size:1.1rem;}
h2 i{font-family:"EB Garamond",Georgia,serif;font-weight:400;font-size:.95rem;color:var(--muted);}
h2 .cnt{margin-left:auto;font-size:.8rem;font-weight:400;color:var(--muted);}
.point{margin:1.6rem 0 .8rem;padding-bottom:.25rem;border-bottom:1px solid var(--line);font-size:1rem;font-weight:600;
 display:flex;align-items:baseline;gap:.6rem;flex-wrap:wrap;scroll-margin-top:4.5rem;}
.point small{font-weight:400;font-size:.8rem;color:var(--muted);}
.xref{display:block;margin:0 0 1rem;padding:.5rem .9rem;border:1px dashed var(--line);border-radius:6px;
 color:var(--ink);text-decoration:none;font-size:.9rem;}
.xref:hover{border-color:var(--accent);}
.xref b{color:var(--accent);font-weight:600;font-family:"EB Garamond",Georgia,serif;}
.xref small{color:var(--muted);}

/* ── 一张卡 ── */
.card{position:relative;margin:0 0 1.8rem;padding:1.05rem 1.25rem .9rem;background:var(--surface);
 border:1px solid var(--line);border-left:4px solid var(--ask);border-radius:6px;box-shadow:var(--shadow);
 scroll-margin-top:4.5rem;}
.card.is-wrong{border-left-color:var(--wrong);}
.card.is-ok{border-left-color:var(--right);}
.card:target{box-shadow:0 0 0 2px var(--accent);animation:flash 1.6s ease-out 1;}
@keyframes flash{0%{box-shadow:0 0 0 7px color-mix(in srgb,var(--accent) 40%,transparent)}100%{box-shadow:0 0 0 2px var(--accent)}}
@media (prefers-reduced-motion:reduce){.card:target{animation:none;}}
.card__meta{display:flex;flex-wrap:wrap;align-items:center;gap:.3rem .7rem;margin-bottom:.35rem;
 font-family:"EB Garamond",Georgia,serif;font-size:.86rem;letter-spacing:.08em;color:var(--muted);
 font-variant-numeric:tabular-nums;}
.card__no{color:var(--accent);font-weight:600;}
.pill{display:inline-flex;align-items:center;padding:0 .6rem;border-radius:99px;font-family:"Noto Serif SC",serif;
 font-size:.74rem;letter-spacing:.06em;line-height:1.7;white-space:nowrap;}
.pill--wrong{background:color-mix(in srgb,var(--wrong) 14%,transparent);color:var(--wrong);}
.pill--ask{background:color-mix(in srgb,var(--ask) 14%,transparent);color:var(--ask);}
.pill--ok{background:color-mix(in srgb,var(--right) 14%,transparent);color:var(--right);}
.pill--times{background:var(--accent);color:#fff;}
.pill--new{border:1px solid var(--accent);color:var(--accent);}
.pill--demo{border:1px dashed var(--muted);color:var(--muted);}
.card__meta .pill:first-of-type{margin-left:auto;}
.card__title{margin:0 0 .3rem;font-size:1.25rem;font-weight:700;line-height:1.5;}
.crumb{margin:0 0 .8rem;font-size:.8rem;color:var(--muted);letter-spacing:.04em;}
.crumb a{color:inherit;text-decoration:none;border-bottom:1px dotted currentColor;}
.crumb a:hover{color:var(--accent);}
.crumb .also{display:inline-block;}
.band{display:block;margin:.4rem -1.25rem .5rem;padding:.25rem 1.25rem;background:var(--band);color:var(--band-ink);
 font-size:.78rem;letter-spacing:.12em;}
.ask{margin:0 0 .5rem;font-size:.98rem;}
.pl{display:flex;align-items:flex-start;gap:.35rem;margin:0 0 .15rem;font-family:"EB Garamond",Georgia,serif;
 font-size:1.42rem;line-height:1.45;color:var(--pl);overflow-wrap:anywhere;}
.pl>span{padding-top:.05rem;}
.en{margin:0 0 .1rem;font-family:"EB Garamond",Georgia,serif;font-style:italic;font-size:1.02rem;color:var(--muted);}
.en::before{content:"题面 ";font-family:"Noto Serif SC",serif;font-style:normal;font-size:.72rem;letter-spacing:.1em;}
.zh{margin:0 0 .6rem;font-size:.97rem;}
.diff{display:grid;gap:.35rem;margin:.2rem 0 .7rem;}
.diff>div{display:flex;align-items:flex-start;gap:.6rem;margin:0;padding:.4rem .7rem;border-radius:5px;}
.diff b{flex:none;font-size:.78rem;letter-spacing:.08em;padding-top:.45rem;white-space:nowrap;}
.diff .is-mine{background:color-mix(in srgb,var(--wrong) 7%,transparent);}
.diff .is-mine b{color:var(--wrong);}
.diff .is-right{background:color-mix(in srgb,var(--right) 8%,transparent);}
.diff .is-right b{color:var(--right);}
.diff .pl{font-size:1.25rem;margin:0;}
.why p{margin:0 0 .55rem;font-size:.97rem;}
.memo{margin:.4rem 0 .8rem;padding:.6rem .9rem;border-radius:5px;background:color-mix(in srgb,var(--accent) 9%,transparent);
 border-left:3px solid var(--accent);font-weight:600;}
.memo b{display:inline-block;margin-right:.6em;font-size:.76rem;letter-spacing:.14em;color:var(--accent);}
.tbl{overflow-x:auto;margin:.2rem 0 .8rem;-webkit-overflow-scrolling:touch;}
.tbl table{width:100%;border-collapse:collapse;font-size:.92rem;}
.tbl th,.tbl td{padding:.35rem .6rem;border-bottom:1px solid var(--line);text-align:left;vertical-align:top;}
.tbl th{font-size:.78rem;font-weight:600;color:var(--band-ink);background:var(--band);letter-spacing:.06em;white-space:nowrap;}
.tbl td{font-family:"EB Garamond","Noto Serif SC",Georgia,serif;font-size:1.06rem;color:var(--pl);}
.tbl td.zh{font-family:"Noto Serif SC",serif;font-size:.86rem;color:var(--ink);}
.tbl td:first-child{white-space:nowrap;}
.extra{list-style:none;margin:0 0 .6rem;padding:0;font-size:.93rem;}
.extra li{margin:0 0 .35rem;}
.extra strong{display:inline-block;margin-right:.5em;padding:0 .45rem;border-radius:4px;background:var(--band);
 color:var(--band-ink);font-size:.76rem;letter-spacing:.08em;}
.ex{list-style:none;margin:0 0 .6rem;padding:0;}
.ex li{display:flex;align-items:flex-start;gap:.35rem;padding:.15rem 0;}
.ex .pl{display:block;font-size:1.15rem;margin:0;font-style:italic;color:var(--example);}
.ex small{display:block;font-family:"Noto Serif SC",serif;font-style:normal;font-size:.86rem;color:var(--muted);}
.words{list-style:none;margin:0 0 .6rem;padding:0;display:grid;gap:.1rem;}
.words li{display:flex;align-items:center;flex-wrap:wrap;gap:.1rem .55rem;padding:.2rem 0;
 border-bottom:1px solid color-mix(in srgb,var(--line) 55%,transparent);}
.words .w{font-family:"EB Garamond",Georgia,serif;font-weight:600;font-size:1.12rem;color:var(--pl);}
.words .wt{font-size:.72rem;padding:0 .4rem;border-radius:4px;background:var(--band);color:var(--band-ink);}
.words .wz{font-size:.92rem;}
.words .look{margin-left:auto;font-size:.78rem;color:var(--accent);text-decoration:none;white-space:nowrap;}
.words .look:hover{text-decoration:underline;}
.see{margin:.2rem 0 .6rem;font-size:.9rem;}
.see a{color:var(--accent);}
mark{color:inherit;background:transparent;padding:0 .12em;margin:0 -.03em;border-radius:.25em .45em .3em .5em;
 background-image:linear-gradient(100deg,transparent 0 1.5%,color-mix(in srgb,var(--hl) var(--hl-mix),transparent) 1.5% 98%,transparent 98%);
 -webkit-box-decoration-break:clone;box-decoration-break:clone;}
mark.wrong{background-image:linear-gradient(100deg,transparent 0 1.5%,color-mix(in srgb,var(--hl-wrong) var(--hl-mix),transparent) 1.5% 98%,transparent 98%);}
mark.right{background-image:linear-gradient(100deg,transparent 0 1.5%,color-mix(in srgb,var(--hl-right) var(--hl-mix),transparent) 1.5% 98%,transparent 98%);}

/* 听 */
.say{appearance:none;flex:none;display:inline-flex;align-items:center;justify-content:center;width:30px;height:30px;
 margin-top:.15rem;border:0;border-radius:50%;background:transparent;color:var(--example);cursor:pointer;padding:0;}
.say:hover{background:var(--band);}
.say svg{width:18px;height:18px;}
.say.is-on{animation:say .9s ease-in-out infinite;}
@keyframes say{50%{opacity:.35}}
@media (prefers-reduced-motion:reduce){.say.is-on{animation:none;}}

/* 她的批注、问答 */
.winter{position:relative;margin:1rem .2rem .7rem;padding:1rem 1.05rem .75rem;background:var(--paper);color:var(--paper-ink);
 border-radius:2px;transform:rotate(-.35deg);box-shadow:var(--note-shadow);line-height:1.85;}
.winter::before{content:"";position:absolute;top:-9px;left:50%;width:70px;height:17px;transform:translateX(-50%) rotate(-1.5deg);
 background:color-mix(in srgb,var(--accent) 45%,transparent);opacity:.8;}
.winter span{display:block;margin-bottom:.35rem;font-size:.68rem;letter-spacing:.2em;opacity:.55;}
.winter p{margin:0 0 .3rem;}
.qa{margin:.7rem 0 .4rem;padding:.65rem .85rem;border-radius:4px;background:color-mix(in srgb,var(--accent) 7%,transparent);font-size:.93rem;}
.qa p{margin:0;}
.qa p+p{margin-top:.35rem;}
.qa b{display:inline-block;margin-right:.6em;font-size:.78rem;letter-spacing:.14em;font-weight:600;color:var(--accent);}
.times{margin:.4rem 0 .5rem;font-size:.84rem;color:var(--muted);}

.card__foot{display:flex;flex-wrap:wrap;align-items:center;justify-content:flex-end;gap:.5rem .7rem;margin-top:.6rem;}
.card__back{margin-right:auto;font-size:.8rem;color:var(--muted);text-decoration:none;letter-spacing:.06em;}
.card__back:hover{color:var(--accent);}
.card__ask{appearance:none;min-height:34px;padding:.25rem 1rem;border-radius:99px;cursor:pointer;
 border:1px solid color-mix(in srgb,var(--accent) 45%,transparent);background:transparent;color:var(--accent);
 font:inherit;font-size:.82rem;letter-spacing:.16em;}
.card__ask:hover{background:color-mix(in srgb,var(--accent) 12%,transparent);}

.foot{margin-top:3.6rem;padding-top:1.4rem;border-top:1px solid color-mix(in srgb,var(--accent) 55%,transparent);
 color:var(--muted);font-size:.86rem;line-height:1.9;}
.foot p{margin:0 0 .5rem;}
details.tipbox{margin-top:1rem;}
details.tipbox summary{cursor:pointer;color:var(--accent);font-size:.9rem;letter-spacing:.08em;}
.tips{margin:.8rem 0 0;padding:0;list-style:none;counter-reset:tip;}
.tips li{position:relative;margin:0 0 .55rem;padding-left:2rem;font-size:.93rem;color:var(--ink);}
.tips li::before{counter-increment:tip;content:counter(tip);position:absolute;left:0;top:.2em;width:1.35rem;height:1.35rem;
 border:1px solid var(--line);border-radius:50%;text-align:center;font-family:"EB Garamond",Georgia,serif;font-size:.8rem;
 line-height:1.3rem;color:var(--accent);}
.toast{position:fixed;left:50%;bottom:calc(18px + env(safe-area-inset-bottom,0px));transform:translate(-50%,calc(100% + 40px));z-index:30;
 visibility:hidden;
 max-width:calc(100vw - 32px);padding:.55rem 1rem;border-radius:12px;background:var(--ink);color:var(--surface);
 font-size:.88rem;box-shadow:0 8px 24px -8px rgba(0,0,0,.45);transition:transform .25s ease;}
.toast.is-on{transform:translate(-50%,0);visibility:visible;}
@media (max-width:480px){
 .wrap{padding:3.2rem 1rem 5rem;}
 .find{margin:0 -1rem 1rem;padding:.6rem 1rem;}
 .card{padding:1rem 1rem .85rem;}
 .band{margin:.4rem -1rem .5rem;padding:.25rem 1rem;}
 .pl{font-size:1.3rem;}
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
(function () {   // 🔊 用设备自带的波兰语语音（iPhone 上是 Zosia）
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
        u.lang = lang; if (v) u.voice = v; u.rate = 0.85;
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
  var blocks = [].slice.call(document.querySelectorAll('.area, .point, .xref, .toc'));
  function fold(s) { return (s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/ł/g, 'l'); }
  input.addEventListener('input', function () {
    var q = fold(input.value).split(/\s+/).filter(Boolean);
    if (!q.length) { cards.forEach(function (c) { c.hidden = false; }); blocks.forEach(function (x) { x.hidden = false; });
      n.textContent = ''; none.hidden = true; return; }
    var hit = 0;
    cards.forEach(function (c) { var s = c.getAttribute('data-s');
      var ok = q.every(function (w) { return s.indexOf(w) >= 0; }); c.hidden = !ok; if (ok) hit++; });
    blocks.forEach(function (x) {
      if (x.classList.contains('xref') || x.classList.contains('toc')) { x.hidden = true; return; }
      x.hidden = !x.querySelector('.card[data-s]:not([hidden])') && !(x.classList.contains('point') && pointHas(x));
    });
    n.textContent = '找到 ' + hit + ' 条'; none.hidden = hit > 0;
  });
  function pointHas(h) {   // 知识点小标题后面跟着的卡片，有没有露出来的
    for (var el = h.nextElementSibling; el && !el.classList.contains('point'); el = el.nextElementSibling)
      if (el.classList.contains('card') && !el.hidden) return true;
    return false;
  }
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

SPEAKER = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
           'stroke-linejoin="round" aria-hidden="true"><path d="M4 9v6h4l5 4V5L8 9H4z"/>'
           '<path d="M16.5 8.5a5 5 0 0 1 0 7"/><path d="M19.5 5.5a9 9 0 0 1 0 13"/></svg>')


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


def say_btn(text, lang='pl'):
    return (f'<button type="button" class="say" data-say="{esc(plain(text))}" data-lang="{"en-US" if lang == "en" else "pl-PL"}" '
            f'aria-label="听" hidden>{SPEAKER}</button>')


def pl_line(text, mark='', cls='pl', lang='pl'):
    return f'<p class="{cls}" lang="{lang}">{say_btn(text, lang)}<span>{fmt(text, mark)}</span></p>'


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


def search_text(x, points):
    a, p = points[x['point']]
    bits = [x.get('title'), x.get('ask'), x.get('pl'), x.get('en'), x.get('zh'), x.get('mine'),
            x.get('why'), x.get('rule'), a['name'], p['name'], p.get('hint'), x.get('source'), f'no. {x["id"]}', x['id']]
    bits += as_list(x.get('right')) + as_list(x.get('extra')) + as_list(x.get('winter'))
    bits += [points[k][1]['name'] for k in as_list(x.get('also'))]
    for e in as_list(x.get('examples')):
        bits += [e.get('pl'), e.get('zh')]
    for w in as_list(x.get('words')):
        bits += [w.get('pl'), w.get('zh'), w.get('tag')]
    for q in as_list(x.get('qa')):
        bits += [q.get('q'), q.get('a')]
    for row in (x.get('table') or {}).get('rows') or []:
        bits += row
    return fold(' '.join(plain(b) for b in bits if b))


def copy_text(x):
    """这一张卡里所有的波兰语，一行一句、句末带标点，给 Google 翻译听。"""
    lines = []
    for s in [x.get('pl')] + as_list(x.get('right')):
        if s and stop(s) not in lines:
            lines.append(stop(s))
    ex = [stop(e['pl']) for e in as_list(x.get('examples')) if e.get('pl')]
    ws = [stop(w['pl']) for w in as_list(x.get('words')) if w.get('pl')]
    return '\n\n'.join('\n'.join(g) for g in (lines, ex, ws) if g)


# ── 一张卡 ──
def card(x, ctx):
    a, p = ctx['points'][x['point']]
    wrong = bool(x.get('mine'))
    kind = 'wrong' if wrong else 'ok' if x.get('ok') else 'ask'
    lang = x.get('lang') or 'pl'
    n = times(x)
    meta = [f'<span class="card__no">No. {esc(x["id"])}</span>',
            f'<span>{cn_date(x["date"], ctx["year"])}{" · " + esc(x["source"]) if x.get("source") else ""}</span>']
    meta.append(f'<span class="pill pill--{kind}">{ {"wrong": "做错了", "ok": "答对了", "ask": "有疑问"}[kind] }</span>')
    if n > 1:
        meta.append(f'<span class="pill pill--times">🔁 问过 {n} 次</span>')
    if ctx['show_new'] and last_date(x) == ctx['newest']:          # 全本都是同一天的就不标「新」，标了也没意义
        meta.append('<span class="pill pill--new">新</span>')
    if x.get('demo'):
        meta.append('<span class="pill pill--demo">样板 · 编的例子</span>')

    crumb = f'{a["icon"]} <a href="#a-{a["key"]}">{esc(a["name"])}</a> › <a href="#p-{esc(x["point"])}">{esc(p["name"])}</a>'
    also = as_list(x.get('also'))
    if also:
        crumb += '　<span class="also">也沾边：' + '、'.join(
            f'<a href="#p-{esc(k)}">{esc(ctx["points"][k][1]["name"])}</a>' for k in also) + '</span>'

    out = [f'<article class="card is-{kind}" id="n{esc(x["id"])}" data-comment-target '
           f'data-comment-label="No. {esc(x["id"])} {esc(plain(x["title"]))}" data-s="{esc(search_text(x, ctx["points"]))}">',
           f'<div class="card__meta">{"".join(meta)}</div>',
           f'<h3 class="card__title">{fmt(x["title"])}</h3>',
           f'<p class="crumb">{crumb}</p>']

    if x.get('ask') or x.get('pl'):
        out.append(f'<span class="band">{"题目" if x.get("pl") else "我问的"}</span>')
        if x.get('ask'):
            out.append(f'<p class="ask">❓ {fmt(x["ask"])}</p>')
        if x.get('pl'):
            out.append(pl_line(x['pl'], 'right' if wrong else '', lang=lang))
            if x.get('en'):
                out.append(f'<p class="en" lang="en">{fmt(x["en"])}</p>')
            if x.get('zh'):
                out.append(f'<p class="zh">{fmt(x["zh"])}</p>')
    if wrong:
        out.append('<div class="diff">'
                   f'<div class="is-mine"><b>✗ 我写的</b>{pl_line(x["mine"], "wrong", lang=lang)}</div>'
                   + ''.join(f'<div class="is-right"><b>✓ 正确</b>{pl_line(r, "right", lang=lang)}</div>' for r in as_list(x.get('right')))
                   + '</div>')

    out.append('<span class="band">为什么</span><div class="why">'
               + ''.join(f'<p>{fmt(par)}</p>' for par in str(x['why']).strip().split('\n') if par.strip()) + '</div>')
    if x.get('rule'):
        out.append(f'<p class="memo"><b>记住</b>{fmt(x["rule"])}</p>')
    t = x.get('table')
    if t:
        head = ''.join(f'<th>{fmt(h)}</th>' for h in t.get('head') or [])
        plc = set(t.get('pl') or range(1, 99))          # 哪几列是波兰语（默认第一列以外都是）
        rows = ''.join('<tr>' + ''.join(f'<td{f" lang={lang}" if i in plc else " class=zh"}>{fmt(c)}</td>'
                                        for i, c in enumerate(r)) + '</tr>' for r in t.get('rows') or [])
        out.append(f'<div class="tbl"><table>{"<thead><tr>" + head + "</tr></thead>" if head else ""}<tbody>{rows}</tbody></table></div>')
    if x.get('extra'):
        out.append('<ul class="extra">' + ''.join(f'<li>{fmt(e)}</li>' for e in as_list(x['extra'])) + '</ul>')
    if x.get('examples'):
        out.append('<span class="band">再看几句</span><ul class="ex">' + ''.join(
            f'<li lang="{lang}">{say_btn(e["pl"], lang)}<span class="pl">{fmt(e["pl"])}'
            f'<small lang="zh-CN">{fmt(e.get("zh", ""))}</small></span></li>'
            for e in as_list(x['examples'])) + '</ul>')
    if x.get('words'):
        rows = []
        for w in as_list(x['words']):
            q = w.get('look', w['pl'] if lang == 'pl' else False)   # 词组写 look: 要查的那个词；look: false 不挂链接
            rows.append(f'<li>{say_btn(w["pl"], lang)}<span class="w" lang="{lang}">{esc(w["pl"])}</span>'
                        + (f'<span class="wt">{esc(w["tag"])}</span>' if w.get('tag') else '')
                        + f'<span class="wz">{fmt(w.get("zh", ""))}</span>'
                        + (f'<a class="look" href="{ctx["polski"]}?q={esc(q)}" target="_blank" rel="noopener">查变格 ↗</a>' if q else '')
                        + '</li>')
        out.append('<span class="band">生词</span><ul class="words">' + ''.join(rows) + '</ul>')
    if x.get('see'):
        out.append('<p class="see">相关：' + '　'.join(
            f'<a href="#n{esc(s)}">No. {esc(s)} {fmt(ctx["index"][str(s)]["title"])}</a>' for s in as_list(x['see'])) + '</p>')
    if n > 1:
        out.append('<p class="times">问过的日子：' + '、'.join(
            cn_date(d, ctx['year']) for d in [x['date']] + as_list(x.get('asked'))) + '</p>')
    if x.get('winter'):
        out.append('<div class="winter"><span>WINTER 写的</span>' + ''.join(f'<p>{fmt(w)}</p>' for w in as_list(x['winter'])) + '</div>')
    if x.get('qa'):
        out.append('<div class="qa">' + ''.join(f'<p><b>问</b>{fmt(q["q"])}</p><p><b>答</b>{fmt(q["a"])}</p>'
                                                for q in as_list(x['qa'])) + '</div>')
    out.append('<div class="card__foot"><a class="card__back" href="#toc">↑ 目录</a>'
               f'<button type="button" class="copy" data-copy="{esc(copy_text(x))}">复制去 Google 翻译听</button>'
               + ('' if ctx['blog'] else '<button type="button" class="card__ask" hidden>批注</button>') + '</div>')
    out.append('</article>')
    return '\n'.join(out)


# ── 目录 ──
def toc(areas, points, notes, ctx):
    used = {}
    for x in notes:
        used.setdefault(x['point'], []).append(x)

    def link(x, extra=''):
        return (f'<li><a href="#n{esc(x["id"])}"><span class="no">No. {esc(x["id"])}</span>'
                f'<span class="t">{fmt(x["title"])}</span>{extra}</a></li>')

    by_point = []
    for a in areas:
        rows = []
        for p in a.get('points') or []:
            k = f'{a["key"]}.{p["key"]}'
            if k in used:
                rows.append(f'<p class="pt">{esc(p["name"])}</p><ul>' + ''.join(link(x) for x in used[k]) + '</ul>')
        if rows:
            by_point.append(f'<h4>{a["icon"]} {esc(a["name"])}</h4>' + ''.join(rows))

    by_time, cur = [], None
    for x in sorted(notes, key=lambda x: (last_date(x), x['id']), reverse=True):
        d = last_date(x)
        if d != cur:
            by_time.append(('</ul>' if cur else '') + f'<h4>{cn_date(d, ctx["year"])}</h4><ul>')
            cur = d
        by_time.append(link(x, '<span class="x">又问</span>' if as_date(x['date']) != d else ''))
    if cur:
        by_time.append('</ul>')

    words = {}
    for x in notes:
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
            letters.append(f'<a href="#wl-{esc(L)}">{esc(L)}</a>')
            cur = L
        wrows.append(f'<li><a href="#n{esc(x["id"])}"><span class="w" lang="pl">{esc(w["pl"])}</span>'
                     + (f'<span class="wt">{esc(w["tag"])}</span>' if w.get('tag') else '')
                     + f'<span class="wz">{fmt(w.get("zh", ""))}</span><span class="no">No. {esc(x["id"])}</span></a></li>')
    if cur:
        wrows.append('</ul>')
    word_copy = '\n'.join(stop(w['pl']) for w, _ in wl)

    reps = sorted([x for x in notes if times(x) > 1], key=lambda x: (-times(x), x['id']))

    panes = [('point', '按知识点', ''.join(by_point)),
             ('time', '按时间', ''.join(by_time))]
    if wl:
        panes.append(('words', f'生词 {len(wl)}',
                      f'<div class="copyline">按波兰语字母顺序排。<button type="button" class="copy" data-copy="{esc(word_copy)}">'
                      f'复制全部生词去听</button></div><div class="letters">{"".join(letters)}</div>' + ''.join(wrows)))
    if reps:
        panes.append(('again', f'🔁 问过不止一次 {len(reps)}',
                      '<ul>' + ''.join(link(x, f'<span class="x">{times(x)} 次</span>') for x in reps) + '</ul>'))
    tabs = ''.join(f'<button type="button" class="tab{" is-on" if i == 0 else ""}" role="tab" aria-selected="{"true" if i == 0 else "false"}" '
                   f'aria-controls="pane-{k}">{esc(lbl)}</button>' for i, (k, lbl, _) in enumerate(panes))
    body = ''.join(f'<div class="pane" id="pane-{k}" role="tabpanel"{"" if i == 0 else " hidden"}>{c}</div>'
                   for i, (k, _, c) in enumerate(panes))
    return (f'<details class="toc" id="toc" open><summary>📑 目录 <small>{len(notes)} 条 · '
            f'{len(used)} 个知识点</small></summary><div class="tabs" role="tablist">{tabs}</div>{body}</details>\n')


def body(areas, points, notes, ctx):
    main, alsos = {}, {}
    for x in notes:
        main.setdefault(x['point'], []).append(x)
        for k in as_list(x.get('also')):
            alsos.setdefault(k, []).append(x)
    out = []
    for a in areas:
        parts, cnt, rel = [], 0, 0
        for p in a.get('points') or []:
            k = f'{a["key"]}.{p["key"]}'
            if k not in main and k not in alsos:
                continue
            hint = f'<small>{esc(p["hint"])}</small>' if p.get('hint') else ''
            parts.append(f'<h3 class="point" id="p-{esc(k)}">{esc(p["name"])}{hint}</h3>')
            for x in main.get(k, []):
                parts.append(card(x, ctx))
                cnt += 1
            for x in alsos.get(k, []):
                rel += 1
                mp = points[x['point']][1]['name']
                parts.append(f'<a class="xref" href="#n{esc(x["id"])}"><b>No. {esc(x["id"])}</b> {fmt(x["title"])}'
                             f' <small>→ 这张卡放在「{esc(mp)}」那里</small></a>')
        if parts:
            out.append(f'<section class="area" id="a-{a["key"]}"><h2><span class="ico">{a["icon"]}</span>{esc(a["name"])}'
                       f'<i lang="pl">{esc(a.get("pl", ""))}</i><span class="cnt">{f"{cnt} 条" if cnt else f"相关 {rel} 条"}</span></h2>\n'
                       + '\n'.join(parts) + '</section>')
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

    pal = palette(meta.get('palette', ''))
    try:
        au = yaml.safe_load(open(os.path.join(ROOT, '_data', 'au_palettes.yml'), encoding='utf-8')) or {}
        ink_accent = (au.get(meta.get('palette', '')) or {}).get('accent_ink') or pal['accent']
    except OSError:
        ink_accent = pal['accent']
    css = CSS.replace('__INK_ACCENT__', ink_accent)
    for k, v in pal.items():
        css = css.replace(f'__{k.upper()}__', v)

    newest = max((last_date(x) for x in notes), default=None)
    ctx = {'points': points, 'index': index, 'blog': a.blog, 'newest': newest,
           'year': newest.year if newest else None,
           'show_new': sum(1 for x in notes if last_date(x) == newest) < len(notes),
           'polski': '../polski.html' if a.blog else f'{SITE}/polski.html'}

    used = {x['point'] for x in notes}
    reps = sum(1 for x in notes if times(x) > 1)
    if is_demo:
        cells = ['<span><b>状态</b> · 等你的第一题</span>', '<span><b>已记</b> · 0 条</span>']
    else:
        cells = [f'<span><b>已记</b> · {len(notes)} 条</span>', f'<span><b>知识点</b> · {len(used)} 个</span>',
                 f'<span><b>最近</b> · {cn_date(newest)}</span>']
        if reps:
            cells.append(f'<span><b>问过不止一次</b> · {reps} 条</span>')
    head = ('<div class="console"><span class="dot"></span>' + ''.join(cells) + '</div>\n'
            f'<p class="kicker">{esc(meta.get("kicker", ""))}</p>\n'
            f'<h1 lang="pl">{esc(meta.get("title", "Notatnik"))}</h1>\n<p class="sub">{esc(meta.get("sub", ""))}</p>\n'
            f'<div class="rule"></div>\n<p class="lede">{fmt(demo["blog_lede" if a.blog else "lede"])}</p>\n')
    if is_demo:
        head += f'<p class="demo-intro">{fmt(demo["demo_intro"])}</p>\n'
    find = ('<div class="find"><label><span aria-hidden="true">🔍</span>'
            '<input type="search" placeholder="搜一个词、一个格、一句中文……" aria-label="搜笔记" autocomplete="off" '
            'autocapitalize="off" spellcheck="false"><span class="find__n"></span></label></div>\n'
            '<p class="find__none" hidden>没找到。可能还没问过——直接来对话里问我就行。</p>\n')
    tips = ('' if a.blog else f'<details class="tipbox"><summary>{esc(demo["tips"]["heading"])}</summary><ol class="tips">'
            + ''.join(f'<li>{fmt(t)}</li>' for t in demo['tips']['items']) + '</ol></details>')
    foot = f'<div class="foot"><p>{fmt(demo["blog_foot" if a.blog else "foot"])}</p>{tips}</div>'
    inner = (f'<button type="button" class="theme-btn">🌕</button>\n<div class="wrap">\n{head}{find}'
             f'{toc(areas, points, notes, ctx)}{body(areas, points, notes, ctx)}\n{foot}\n</div>\n'
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
                f'{FONTS}\n<style>{css}</style>\n</head>\n<body>\n'
                '<nav class="blognav"><a href="../?view=gallery">← Gallery</a><a href="../polski.html">变格表</a></nav>\n'
                f'{inner}</body>\n</html>\n')
    else:
        page = f'<title>{title}</title>\n{FONTS}\n<style>{css}</style>\n{inner}'
    open(a.out, 'w', encoding='utf-8').write(page)
    print(f'✅ {a.out}（{"样板 " if is_demo else ""}{len(notes)} 条 · {len(used)} 个知识点 · 配色 {meta.get("palette") or "默认"}）')


if __name__ == '__main__':
    main()
