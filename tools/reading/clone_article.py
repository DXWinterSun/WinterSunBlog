#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网页文章 → 可划线的阅读页（Winter 在上面用她读书的三支笔划词，Claude 读回划线做笔记）

2026-10-14 Winter 读《卫报》那篇 McDonagh / Malkovich / Rockwell 访谈时说：**「我看见一个生词自己查的方式
还是太老套了……是不是可以你帮我做一个这个网页的文章的克隆，我在读的时候可以在上面用我习惯的颜色标注
词和短语，就像我读书一样，然后你就可以帮我做笔记了？」**

    python3 tools/reading/clone_article.py <网址> -o <scratchpad>/<slug>.html
    python3 tools/reading/clone_article.py --html 已下载.html --url <网址> -o …    # 抓不到时先 curl 下来再喂

然后用 Artifact 工具发布，第一次发布必须带
    capabilities = {"db": {}, "comments": {"composer_only": true}}
——划线存在这张页自己的数据库 `highlights` 集合里（手机电脑同一份），Claude 用 ArtifactData 读回来整理笔记；
comments 是笔盒里那颗 💬：她选中字 / 点一处划线再点它，才弹 Artifact 自带的批注框（她 2026-10-14：
「不需要每次画词都弹出，我主动点击的时候才给我批注的框」）。
之后重新发布不传 capabilities。她划完说「整理一下」→ 读 `highlights` → 照读书笔记那套写进
`_data/reading/<slug>.yml`（`page` 写段落号，`book.page_unit: 段`）→ 把整理过的划线标成 noted。

三支笔跟她读书时一样（见 .claude/skills/winter-reading-notes/SKILL.md）：蓝＝生词、粉＝对照、橙＝好句。

⚠️ 仓库是公开的：文章全文只在发布出去的（私密）网页里，**不要**把抓下来的全文存进仓库；
笔记数据里也只录划线所在的短语（跟书的规矩一样）。
"""
import argparse, datetime, html, json, os, re, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'preview'))
from render_draft import palette          # noqa: E402  跟预览页同一套配色（默认金色；--series 可指定 AU）

PENS = [  # id, 名字, 颜色（跟 render_notes.py 的 PENS 同色）, 一句说明
    ('blue',   '生词',   '#7fd6dc', '不认识的词'),
    ('pink',   '对照',   '#f2a7c6', '词认识，但这个用法新鲜、值得再看一眼'),
    ('purple', '专名',   '#cdb4f0', '人名、地名、片名、东西的名字'),       # 2026-10-14 她加的
    ('yellow', '长难句', '#f3dd7a', '看不太懂的长句，要拆开讲'),           # 2026-10-14 她加的
    ('orange', '好句',   '#f7b27c', '表达效果好的句子'),
    ('sam',    'Sam',    '#e0566b', '关于他、值得收藏的话——画成下划线，能单独导出给小红书'),   # 2026-10-14 她加的
]
SAM = 'sam'   # 这一支不是荧光笔：下划线，可以跟别的颜色叠在同一段字上；单独导出

FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400'
         '&family=Noto+Serif+SC:wght@400;500;600&display=swap">')


# ───────────────────────────── 抓正文 ─────────────────────────────

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (reading-clone)'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode('utf-8', 'replace')


def extract(raw, url):
    """尽量通用：先按《卫报》的结构找，找不到就退到 <article> / 最大的一堆 <p>。"""
    from bs4 import BeautifulSoup
    s = BeautifulSoup(raw, 'html.parser')
    meta = {'url': url, 'site': re.sub(r'^www\.', '', re.sub(r'^https?://([^/]+).*$', r'\1', url))}

    h1 = s.find('h1')
    meta['title'] = h1.get_text(' ', strip=True) if h1 else (s.title.string.strip() if s.title and s.title.string else url)
    stand = s.find(attrs={'data-gu-name': 'standfirst'}) or s.find('meta', attrs={'name': 'description'})
    meta['standfirst'] = (stand.get_text(' ', strip=True) if hasattr(stand, 'get_text') and stand.name != 'meta'
                          else (stand.get('content', '') if stand else ''))

    author, date = '', ''
    for sc in s.select('script[type="application/ld+json"]'):
        try:
            d = json.loads(sc.string or '')
        except Exception:
            continue
        for item in (d if isinstance(d, list) else [d]):
            if not isinstance(item, dict):
                continue
            if item.get('@type') in ('NewsArticle', 'Article', 'ReportageNewsArticle'):
                a = item.get('author')
                if isinstance(a, dict):
                    a = [a]
                if isinstance(a, list):
                    author = ', '.join(x.get('name', '') for x in a if isinstance(x, dict) and x.get('name'))
                date = (item.get('datePublished') or '')[:10]
    if not author:
        a = s.select_one('a[rel="author"]')
        author = a.get_text(strip=True) if a else ''
    meta['author'], meta['date'] = author, date
    om = s.find('meta', attrs={'property': 'og:site_name'})
    if om and om.get('content'):
        meta['site'] = om['content']

    body = s.find(attrs={'data-gu-name': 'body'}) or s.find('article') or s.body
    paras = []
    for el in body.find_all(['p', 'h2', 'h3', 'blockquote']):
        if el.find_parent(['figure', 'aside', 'nav', 'footer', 'form']):
            continue
        if el.name == 'p' and el.find_parent('blockquote'):
            continue
        t = re.sub(r'\s+', ' ', el.get_text(' ', strip=True))
        t = re.sub(r'\s+([,.;:!?’”)])', r'\1', t)      # 行内链接拆出来的多余空格
        if not t:
            continue
        kind = 'h' if el.name in ('h2', 'h3') else ('q' if el.name == 'blockquote' else 'p')
        paras.append({'k': kind, 't': t})
    # 卫报正文末尾那行「X is released on …」留着，页脚那些「Explore more」之类的不要
    meta['paras'] = paras
    return meta


# ───────────────────────────── 页面 ─────────────────────────────

CSS = '''
:root{
 color-scheme:light;
 --bg:color-mix(in srgb,__ACCENT__ 6%,#fbfaf6);--accent:__INK_ACCENT__;--ink:#1d2129;--muted:#6b7280;
 --surface:#fffefb;--line:color-mix(in srgb,var(--accent) 24%,transparent);
 --shadow:0 10px 28px rgba(20,24,31,.12);--hl-mix:62%;--noted:#1f9a55;
 --pen-blue:__PEN_BLUE__;--pen-pink:__PEN_PINK__;--pen-purple:__PEN_PURPLE__;--pen-yellow:__PEN_YELLOW__;--pen-orange:__PEN_ORANGE__;--pen-sam:__PEN_SAM__;
}
:root[data-theme="dark"]{
 color-scheme:dark;
 --bg:__BG__;--accent:__ACCENT__;--ink:__TEXT__;--muted:__MUTED__;
 --surface:color-mix(in srgb,var(--bg) 90%,#fff);--line:color-mix(in srgb,var(--accent) 24%,transparent);
 --shadow:0 10px 28px rgba(0,0,0,.4);--hl-mix:42%;--noted:#4cc684;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font-family:"Noto Serif SC","Songti SC",serif;line-height:1.75;
 -webkit-tap-highlight-color:transparent;}
.wrap{max-width:44rem;margin:0 auto;padding:3.2rem 16px 7.5rem;}
.top{position:absolute;top:10px;right:10px;display:flex;gap:.4rem;z-index:5}
.rbtn{width:36px;height:36px;border-radius:50%;border:1px solid var(--line);background:var(--surface);color:var(--ink);
 cursor:pointer;font-size:17px;display:inline-flex;align-items:center;justify-content:center;padding:0}
.rbtn:hover{border-color:var(--accent)}
.eyebrow{font-family:"EB Garamond",Georgia,serif;font-size:.8rem;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);margin:0 0 .6rem}
.eyebrow a{color:inherit;text-decoration:none;border-bottom:1px dotted currentColor}
.art h1.p{font-weight:600;font-size:1.4em;line-height:1.3;margin:0 0 .6em;letter-spacing:.005em}
.art .p[data-k="lede"]{font-size:.95em;line-height:1.55;color:var(--muted);margin:0 0 .4em}
.by{font-family:"EB Garamond",Georgia,serif;font-size:.9rem;color:var(--muted);letter-spacing:.04em;margin:0 0 1.2rem;
 padding-bottom:1rem;border-bottom:1px solid var(--line)}
.howto{font-size:.84rem;color:var(--muted);background:var(--surface);border:1px dashed var(--line);border-radius:12px;
 padding:.7rem .9rem;margin:0 0 1.6rem;line-height:1.7}
.howto b{color:var(--ink);font-weight:500}
.howto .pen-dot{display:inline-block;width:.75em;height:.75em;border-radius:50%;vertical-align:-.05em;margin:0 .15em}
.howto .sync{display:block;margin-top:.3rem;font-size:.78rem}
.art{font-family:"EB Garamond",Georgia,serif;font-size:1.2rem;line-height:1.72}
.art .p{margin:0 0 1.1em;position:relative}
.art .p[data-k="h"]{font-weight:600;font-size:1.15em;margin-top:1.6em}
.art .p[data-k="q"]{border-left:3px solid var(--line);padding-left:1em;font-style:italic;color:var(--muted)}
.art .num{position:absolute;left:-2.4rem;top:.35em;font-size:.68rem;color:var(--muted);opacity:.55;letter-spacing:.04em;user-select:none;-webkit-user-select:none}
@media (max-width:700px){.art .num{display:none}}
mark{color:inherit;border-radius:2px;padding:.06em 0;background:color-mix(in srgb,var(--c) var(--hl-mix),transparent);
 box-decoration-break:clone;-webkit-box-decoration-break:clone;cursor:pointer;transition:background .15s}
mark.is-sam{text-decoration:underline;text-decoration-color:var(--pen-sam);text-decoration-thickness:2px;text-underline-offset:.16em;text-decoration-skip-ink:none}
mark.is-sam:not(.has-bg){background:transparent}
.pen[data-pen="sam"] i,.pop button[data-pen="sam"]{background:transparent;border:0;font-size:16px;line-height:1}
.pen[data-pen="sam"] i::before,.pop button[data-pen="sam"]::before{content:"❣️"}
.pen[data-pen="sam"].is-on{background:color-mix(in srgb,var(--pen-sam) 22%,var(--surface));border-color:var(--pen-sam)}
.pop button[data-pen="sam"].is-cur{border:2px solid var(--pen-sam);border-radius:50%}
.grp .gcopy{margin-left:auto;height:28px;padding:0 .6rem;border-radius:999px;border:1px solid var(--line);background:var(--surface);color:var(--ink);cursor:pointer;font-family:inherit;font-size:.76rem}
.row .t mark.is-sam{background:transparent}
mark.is-noted::after{content:"✓";font-size:.55em;vertical-align:super;color:var(--noted);margin-left:.1em;font-family:system-ui,sans-serif}
mark.is-focus{background:color-mix(in srgb,var(--c) 88%,transparent)}
/* 浮在选区上方的小笔盒 */
.pop{position:absolute;z-index:20;display:none;gap:.35rem;align-items:center;padding:.4rem .5rem;border-radius:999px;
 background:var(--surface);border:1px solid var(--line);box-shadow:var(--shadow);transform:translate(-50%,-100%);margin-top:-10px}
.pop.is-on{display:inline-flex}
.pop::after{content:"";position:absolute;left:50%;bottom:-6px;width:10px;height:10px;background:var(--surface);
 border-right:1px solid var(--line);border-bottom:1px solid var(--line);transform:translateX(-50%) rotate(45deg)}
.pop button{width:34px;height:34px;border-radius:50%;border:2px solid transparent;background:var(--c);cursor:pointer;padding:0;font-size:15px;
 display:inline-flex;align-items:center;justify-content:center;color:#1d2129}
.pop button.is-cur{border-color:var(--ink)}
.pop button.erase{background:transparent;border:1px solid var(--line);color:var(--ink);font-size:14px}
.pop button.ask,.bar .ask{display:none;background:transparent;border:1px solid var(--line);color:var(--ink);font-size:15px}
body.has-cmt .pop button.ask{display:inline-flex}
body.has-cmt .bar .ask{display:inline-flex;align-items:center;justify-content:center;width:36px;height:36px;border-radius:50%;padding:0;cursor:pointer}
.pop button.big{display:none;width:auto;height:38px;padding:0 1.1rem;border-radius:999px;font-family:inherit;font-size:.9rem;letter-spacing:.04em}
.pop.is-pen button[data-pen],.pop.is-pen button.erase{display:none}
.pop.is-pen button.big{display:inline-flex}
.pop button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
/* 底部笔架 */
.bar{position:fixed;left:0;right:0;bottom:0;z-index:15;display:flex;justify-content:center;pointer-events:none;
 padding:0 10px calc(10px + env(safe-area-inset-bottom))}
.bar__in{pointer-events:auto;display:flex;align-items:center;gap:.45rem;padding:.45rem .6rem;border-radius:999px;
 background:var(--surface);border:1px solid var(--line);box-shadow:var(--shadow);max-width:100%}
.pen{display:inline-flex;align-items:center;gap:.35rem;height:36px;padding:0 .7rem 0 .4rem;border-radius:999px;border:1px solid var(--line);
 background:transparent;color:var(--ink);cursor:pointer;font-family:inherit;font-size:.82rem;letter-spacing:.04em;white-space:nowrap}
.pen i{width:18px;height:18px;border-radius:50%;background:var(--c);display:inline-block;flex:none}
.pen.is-on{background:color-mix(in srgb,var(--c) 45%,var(--surface));border-color:var(--c)}
.pen .n{font-size:.72rem;color:var(--muted);min-width:1ch}
.pen.is-on .n{color:var(--ink)}
.bar .list{height:36px;padding:0 .75rem;border-radius:999px;border:1px solid var(--line);background:transparent;color:var(--ink);
 cursor:pointer;font-family:inherit;font-size:.82rem;letter-spacing:.04em;white-space:nowrap}
@media (max-width:480px){.bar__in{gap:.3rem;padding:.4rem .45rem}.pen{padding:0 .4rem 0 .3rem;gap:.25rem}.pen .lbl{display:none}.pen.is-on .lbl{display:inline}.pen .n:empty{display:none}.bar .list{padding:0 .6rem}}
.hint{position:fixed;left:50%;bottom:calc(66px + env(safe-area-inset-bottom));transform:translateX(-50%);z-index:14;
 font-size:.78rem;color:var(--muted);background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:.25rem .8rem;
 opacity:0;transition:opacity .25s;pointer-events:none;white-space:nowrap;max-width:calc(100vw - 24px);overflow:hidden;text-overflow:ellipsis}
.hint.is-on{opacity:1}
/* 清单抽屉 */
.drawer{position:fixed;inset:0;z-index:30;display:none;background:rgba(0,0,0,.35)}
.drawer.is-on{display:block}
.drawer__panel{position:absolute;left:0;right:0;bottom:0;max-height:78vh;overflow:auto;background:var(--bg);border-radius:18px 18px 0 0;
 padding:1rem 16px calc(1rem + env(safe-area-inset-bottom));box-shadow:0 -10px 30px rgba(0,0,0,.25)}
@media (min-width:700px){.drawer__panel{left:50%;right:auto;width:40rem;transform:translateX(-50%)}}
.drawer__head{display:flex;align-items:center;justify-content:space-between;gap:.6rem;margin-bottom:.6rem}
.drawer__head h2{margin:0;font-size:1rem;font-weight:500}
.drawer__head .tools{display:flex;gap:.4rem}
.drawer__head button{height:32px;padding:0 .7rem;border-radius:999px;border:1px solid var(--line);background:var(--surface);color:var(--ink);cursor:pointer;font-family:inherit;font-size:.8rem}
.grp{margin:.8rem 0 .4rem;font-size:.8rem;color:var(--muted);display:flex;align-items:center;gap:.4rem}
.grp i{width:12px;height:12px;border-radius:50%;background:var(--c);display:inline-block}
.row{display:flex;align-items:flex-start;gap:.5rem;padding:.45rem 0;border-bottom:1px solid var(--line);font-size:.92rem}
.row .t{flex:1;font-family:"EB Garamond",Georgia,serif;font-size:1.02rem;cursor:pointer}
.row .t mark{cursor:pointer}
.row .pg{font-size:.72rem;color:var(--muted);white-space:nowrap;padding-top:.25rem}
.row .ok{font-size:.72rem;color:var(--noted);white-space:nowrap;padding-top:.25rem}
.row .x{border:0;background:transparent;color:var(--muted);cursor:pointer;font-size:1rem;padding:0 .2rem;line-height:1.4}
.row .x:hover{color:#c8322b}
.empty{color:var(--muted);font-size:.9rem;padding:1rem 0}
.toast{position:fixed;left:50%;top:14px;transform:translateX(-50%);z-index:40;background:var(--ink);color:var(--bg);font-size:.82rem;
 padding:.4rem .9rem;border-radius:999px;opacity:0;transition:opacity .2s;pointer-events:none}
.toast.is-on{opacity:1}
::selection{background:color-mix(in srgb,var(--accent) 30%,transparent)}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
'''

JS = r'''
(function(){
  var SLUG = document.body.getAttribute('data-slug');
  var PENS = __PENS_JSON__, ORDER = __ORDER_JSON__;
  var art = document.getElementById('art');
  var paras = Array.prototype.slice.call(art.querySelectorAll('.p'));
  var TEXT = paras.map(function(p){ return p.getAttribute('data-t'); });
  var LOC = paras.map(function(p){ return p.getAttribute('data-loc'); });
  var H = {};            // id -> {p,s,e,color,text,ts,noted}
  var db = null, user = null, backend = 'local';
  var pen = null;        // 当前拿在手里的笔
  var pop = document.getElementById('pop'), hint = document.getElementById('hint'), toast = document.getElementById('toast');
  var LS = 'ws-article-hl:' + SLUG;

  /* ── 存取 ── */
  function localLoad(){ try{ var j = JSON.parse(localStorage.getItem(LS) || '{}'); return j && typeof j === 'object' ? j : {}; }catch(e){ return {}; } }
  function localSave(){ try{ localStorage.setItem(LS, JSON.stringify(H)); }catch(e){} }
  function save(id, rec){
    H[id] = rec; render();
    if (db) { db.collection('highlights').doc(id).set(rec).catch(function(e){ say('没存上：' + (e && e.message || e)); }); }
    else localSave();
  }
  function recolor(id, color){
    if (!H[id] || H[id].color === color) return;
    H[id] = Object.assign({}, H[id], {color: color}); render();
    if (db) db.collection('highlights').doc(id).update({color: color}).catch(function(e){ say('没存上'); });
    else localSave();
  }
  function remove(id){
    if (!H[id]) return;
    delete H[id]; render();
    if (db) db.collection('highlights').doc(id).delete().catch(function(e){ say('没删掉'); });
    else localSave();
  }
  function newId(){ return 'h' + Date.now().toString(36) + Math.random().toString(36).slice(2,6); }

  /* ── 渲染：每段按划线重排 ── */
  function esc(s){ return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
  function render(){
    var byP = {};
    Object.keys(H).forEach(function(id){ var h = H[id]; (byP[h.p] = byP[h.p] || []).push(Object.assign({id:id}, h)); });
    paras.forEach(function(el, i){
      var t = TEXT[i], hs = byP[i] || [];
      var num = el.getAttribute('data-n') ? '<span class="num">' + el.getAttribute('data-n') + '</span>' : '';
      if (!hs.length) { el.innerHTML = num + esc(t); return; }
      var cuts = {0:1}; cuts[t.length] = 1;
      hs.forEach(function(h){ cuts[Math.max(0,Math.min(t.length,h.s))] = 1; cuts[Math.max(0,Math.min(t.length,h.e))] = 1; });
      var pts = Object.keys(cuts).map(Number).sort(function(a,b){return a-b;});
      var out = '';
      for (var k = 0; k < pts.length - 1; k++){
        var a = pts[k], b = pts[k+1]; if (a === b) continue;
        var cover = hs.filter(function(h){ return h.s <= a && h.e >= b; }).sort(function(x,y){ return (x.ts||0)-(y.ts||0); });
        var seg = esc(t.slice(a,b));
        if (!cover.length) { out += seg; continue; }
        var bg = cover.filter(function(h){ return h.color !== 'sam'; }), sam = bg.length !== cover.length;
        var top = bg.length ? bg[bg.length-1] : cover[cover.length-1];
        var cls = [];
        if (sam) cls.push('is-sam'); if (bg.length) cls.push('has-bg');
        if (bg.length && bg.every(function(h){return h.noted;})) cls.push('is-noted');
        out += '<mark style="--c:var(--pen-' + top.color + ')" data-ids="' + cover.map(function(h){return h.id;}).join(' ') +
               '" class="' + cls.join(' ') + '">' + seg + '</mark>';
      }
      el.innerHTML = num + out;
    });
    counts();
  }
  function counts(){
    var c = {}, n = 0, noted = 0;
    Object.keys(H).forEach(function(id){ var h = H[id]; c[h.color] = (c[h.color]||0)+1; n++; if (h.noted) noted++; });
    ORDER.forEach(function(k){ var el = document.querySelector('.pen[data-pen="' + k + '"] .n'); if (el) el.textContent = c[k] || ''; });
    var lb = document.getElementById('list-btn');
    lb.textContent = n ? ('清单 ' + n + (noted ? ' · 已整理 ' + noted : '')) : '清单';
  }

  /* ── 选区 → 段内偏移 ── */
  function offsetsOf(range){
    // 返回 [{p, s, e}]，跨段时拆成多段
    var out = [];
    paras.forEach(function(el, i){
      var r = document.createRange(); r.selectNodeContents(el);
      if (range.compareBoundaryPoints(Range.END_TO_START, r) >= 0) return;   // 选区在这段之前结束
      if (range.compareBoundaryPoints(Range.START_TO_END, r) <= 0) return;   // 选区在这段之后开始
      var numEl = el.querySelector('.num'), nlen = numEl ? numEl.textContent.length : 0;
      var pre = document.createRange(); pre.selectNodeContents(el);
      var s = 0, e = TEXT[i].length;
      if (range.compareBoundaryPoints(Range.START_TO_START, r) > 0) { pre.setEnd(range.startContainer, range.startOffset); s = Math.max(0, pre.toString().length - nlen); }
      pre = document.createRange(); pre.selectNodeContents(el);
      if (range.compareBoundaryPoints(Range.END_TO_END, r) < 0) { pre.setEnd(range.endContainer, range.endOffset); e = Math.max(0, pre.toString().length - nlen); }
      var t = TEXT[i];
      while (s < e && /\s/.test(t[s])) s++;
      while (e > s && /\s/.test(t[e-1])) e--;
      if (e > s) out.push({p:i, s:s, e:e});
    });
    return out;
  }
  function selection(){
    var sel = window.getSelection();
    if (!sel || sel.rangeCount === 0 || sel.isCollapsed) return null;
    var r = sel.getRangeAt(0);
    if (!art.contains(r.commonAncestorContainer)) return null;
    var parts = offsetsOf(r);
    return parts.length ? {range:r, parts:parts} : null;
  }
  function apply(color){
    var s = selection(); if (!s) return;
    var group = s.parts.length > 1 ? newId() : null, now = Date.now();
    s.parts.forEach(function(pt, k){
      var rec = {p:pt.p, loc:LOC[pt.p], s:pt.s, e:pt.e, color:color, text:TEXT[pt.p].slice(pt.s, pt.e), ts: now + k, noted:false};
      if (group) rec.group = group;
      save(newId(), rec);
    });
    window.getSelection().removeAllRanges(); hidePop();
    say(PENS[color] + ' · 划好了');
  }

  /* ── 小笔盒 ── */
  var popTarget = null, popEl = null;   // 点中已有划线时记下它的 id 们、那块 <mark>
  var cmt = null;                        // Artifact 的批注（在 claude.ai 里打开才有）
  var muteSel = 0, muteText = '';        // 打开批注框之后，同一段选区别再弹笔盒（选区还在，会误弹）；选了别的照常弹
  function askAbout(target){
    if (!cmt || !target) return;
    hidePop(); muteSel = Date.now() + 4000; muteText = String(window.getSelection() || '');
    cmt.openComposer(target).catch(function(e){ var c = e && e.code; if (c === 'not_granted' || c === 'capability_disabled' || c === 'capability_removed' || c === 'unavailable') { cmt = null; document.body.classList.remove('has-cmt'); } });
  }
  function showPop(rect, ids, el){
    popTarget = ids || null; popEl = el || null;
    var cur = ids && H[ids[ids.length-1]] ? H[ids[ids.length-1]].color : null;
    Array.prototype.forEach.call(pop.querySelectorAll('button[data-pen]'), function(b){ b.classList.toggle('is-cur', b.getAttribute('data-pen') === cur); });
    pop.querySelector('.erase').style.display = ids ? '' : 'none';
    var big = pop.querySelector('.big');
    if (pen && !ids) { big.style.setProperty('--c', 'var(--pen-' + pen + ')'); big.textContent = '划上 · ' + PENS[pen]; }
    pop.classList.toggle('is-pen', !!(pen && !ids));
    pop.classList.add('is-on');
    var w = pop.offsetWidth, x = rect.left + rect.width/2 + window.scrollX, y = rect.top + window.scrollY;
    x = Math.max(w/2 + 8, Math.min(document.documentElement.clientWidth - w/2 - 8, x));
    if (rect.top < 70) { y = rect.bottom + window.scrollY + 54; }   // 顶上放不下就挂到下面
    pop.style.left = x + 'px'; pop.style.top = y + 'px';
  }
  function hidePop(){ pop.classList.remove('is-on'); popTarget = null; popEl = null; }
  pop.addEventListener('mousedown', function(e){ e.preventDefault(); });   // 别把选区点没了
  pop.addEventListener('touchstart', function(e){ e.preventDefault(); var b = e.target.closest('button'); if (b) b.click(); }, {passive:false});
  pop.addEventListener('click', function(e){
    var b = e.target.closest('button'); if (!b) return;
    if (b.classList.contains('erase')) { (popTarget||[]).forEach(remove); hidePop(); say('擦掉了'); return; }
    if (b.classList.contains('big')) { apply(pen); return; }
    if (b.classList.contains('ask')) {
      if (popEl) { askAbout({element: popEl}); return; }
      var sel = window.getSelection(); if (sel && !sel.isCollapsed) askAbout({range: sel.getRangeAt(0).cloneRange()});
      return;
    }
    var c = b.getAttribute('data-pen');
    if (popTarget) { popTarget.forEach(function(id){ recolor(id, c); }); hidePop(); say('换成' + PENS[c]); }
    else apply(c);
  });

  var TOUCH = window.matchMedia && window.matchMedia('(pointer: coarse)').matches;
  var selTimer = null, mouseDown = false;
  document.addEventListener('mousedown', function(){ mouseDown = true; });
  document.addEventListener('mouseup', function(){ mouseDown = false; setTimeout(onSel, 30); });
  document.addEventListener('selectionchange', function(){ clearTimeout(selTimer); selTimer = setTimeout(onSel, 220); });
  function onSel(){
    if (mouseDown) return;
    if (Date.now() < muteSel && String(window.getSelection() || '') === muteText) return;                              // 鼠标还按着：拖到一半，先别动
    var s = selection();
    if (!s) { if (!popTarget) hidePop(); return; }
    if (pen && !TOUCH) { apply(pen); return; }          // 电脑上拿着笔：松开鼠标就划上
    showPop(s.range.getBoundingClientRect(), null);     // 手机上拿着笔：弹一颗大的「划上」键，一点就好（拖选区手柄时不会误划）
  }
  art.addEventListener('click', function(e){
    var m = e.target.closest('mark'); if (!m) return;
    var sel = window.getSelection(); if (sel && !sel.isCollapsed) return;
    var ids = m.getAttribute('data-ids').split(' ');
    Array.prototype.forEach.call(art.querySelectorAll('mark.is-focus'), function(x){ x.classList.remove('is-focus'); });
    showPop(m.getBoundingClientRect(), ids, m);
  });
  document.getElementById('ask-btn').addEventListener('click', function(){
    var sel = window.getSelection();
    if (sel && !sel.isCollapsed && art.contains(sel.getRangeAt(0).commonAncestorContainer)) { askAbout({range: sel.getRangeAt(0).cloneRange()}); return; }
    var f = art.querySelector('mark.is-focus'); if (f) { askAbout({element: f}); return; }
    say('先选中几个字，或点一处划线，再点 💬');
  });
  document.getElementById('ask-btn').addEventListener('mousedown', function(e){ e.preventDefault(); });
  document.addEventListener('mousedown', function(e){ if (!pop.contains(e.target) && !e.target.closest('mark')) hidePop(); });
  document.addEventListener('touchstart', function(e){ if (!pop.contains(e.target) && !e.target.closest('mark')) hidePop(); }, {passive:true});

  /* ── 底部笔架 ── */
  Array.prototype.forEach.call(document.querySelectorAll('.pen'), function(b){
    b.addEventListener('click', function(){
      var c = b.getAttribute('data-pen');
      var s = selection();
      if (s) { apply(c); return; }                         // 已经选好了字：直接划
      pen = (pen === c) ? null : c;
      Array.prototype.forEach.call(document.querySelectorAll('.pen'), function(x){ x.classList.toggle('is-on', x.getAttribute('data-pen') === pen); });
      hint.textContent = pen ? ('拿着' + PENS[pen] + '笔' + (TOUCH ? '：选字后点「划上」' : '：选中就划上') + '，再点笔放下') : '';
      hint.classList.toggle('is-on', !!pen);
    });
  });

  /* ── 清单 ── */
  var drawer = document.getElementById('drawer');
  function openList(){
    var body = document.getElementById('drawer-body'), ids = Object.keys(H);
    if (!ids.length) { body.innerHTML = '<p class="empty">还一处都没划。选中几个字，挑一支笔。</p>'; drawer.classList.add('is-on'); return; }
    var html = '';
    ORDER.forEach(function(c){
      var g = ids.filter(function(id){ return H[id].color === c; }).sort(function(a,b){ return H[a].p - H[b].p || H[a].s - H[b].s; });
      if (!g.length) return;
      html += '<div class="grp" style="--c:var(--pen-' + c + ')">' + (c === 'sam' ? '❣️ ' : '<i></i>') + PENS[c] + ' · ' + g.length +
              (c === 'sam' ? '<button type="button" class="gcopy" id="copy-sam">复制 Sam 的</button>' : '') + '</div>';
      g.forEach(function(id){
        var h = H[id];
        html += '<div class="row" data-id="' + id + '"><span class="t" data-go="' + id + '"><mark style="--c:var(--pen-' + c + ')" class="' + (c === 'sam' ? 'is-sam' : '') + '">' + esc(h.text) + '</mark></span>' +
                '<span class="pg">' + (h.loc || LOC[h.p] || '') + '</span>' + (h.noted ? '<span class="ok">✓ 已整理</span>' : '') +
                '<button class="x" data-x="' + id + '" aria-label="擦掉">✕</button></div>';
      });
    });
    body.innerHTML = html; drawer.classList.add('is-on');
  }
  document.getElementById('list-btn').addEventListener('click', openList);
  document.getElementById('drawer-close').addEventListener('click', function(){ drawer.classList.remove('is-on'); });
  drawer.addEventListener('click', function(e){ if (e.target === drawer) drawer.classList.remove('is-on'); });
  document.getElementById('drawer-body').addEventListener('click', function(e){
    var x = e.target.closest('[data-x]'); if (x) { remove(x.getAttribute('data-x')); openList(); return; }
    var go = e.target.closest('[data-go]'); if (go) {
      var id = go.getAttribute('data-go'); drawer.classList.remove('is-on');
      var m = art.querySelector('mark[data-ids~="' + id + '"]');
      if (m) { m.scrollIntoView({block:'center', behavior:'smooth'}); m.classList.add('is-focus'); setTimeout(function(){ m.classList.remove('is-focus'); }, 1600); }
    }
  });
  function copyText(txt, msg){
    function done(){ say(msg); }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(txt).then(done, function(){ fallback(txt); done(); });
    else { fallback(txt); done(); }
  }
  function sorted(){ return Object.keys(H).sort(function(a,b){ return H[a].p - H[b].p || H[a].s - H[b].s; }); }
  document.getElementById('copy-btn').addEventListener('click', function(){
    var lines = sorted().filter(function(id){ return H[id].color !== 'sam'; }).map(function(id){ var h = H[id]; return '[' + PENS[h.color] + '] ' + (h.loc || LOC[h.p] || '') + '：' + h.text; });
    copyText(lines.join('\n'), '复制好了，贴给 Claude 就行');
  });
  document.getElementById('drawer-body').addEventListener('click', function(e){
    if (!e.target.closest('#copy-sam')) return;
    e.stopPropagation();
    var head = document.querySelector('#art h1.p'), title = head ? head.getAttribute('data-t') : document.title;
    var link = document.querySelector('.eyebrow a'), url = link ? link.getAttribute('href') : '';
    var lines = sorted().filter(function(id){ return H[id].color === 'sam'; }).map(function(id){ var h = H[id]; return '· ' + h.text + '（' + (h.loc || LOC[h.p] || '') + '）'; });
    copyText('来自《' + title + '》' + (url ? '\n' + url : '') + '\n\n' + lines.join('\n'), '复制好了 ❣️ 去发给小红书那边吧');
  }, true);
  function fallback(txt){ var ta = document.createElement('textarea'); ta.value = txt; document.body.appendChild(ta); ta.select(); try{ document.execCommand('copy'); }catch(e){} ta.remove(); }

  var toastT = null;
  function say(s){ toast.textContent = s; toast.classList.add('is-on'); clearTimeout(toastT); toastT = setTimeout(function(){ toast.classList.remove('is-on'); }, 1500); }

  /* ── 昼夜 ── */
  var root = document.documentElement, tb = document.getElementById('theme-btn');
  function paintTheme(){ tb.textContent = root.getAttribute('data-theme') === 'dark' ? '🌑' : '🌕'; }
  try { if (localStorage.getItem('ws-reading-theme') === 'dark') root.setAttribute('data-theme','dark'); } catch(e){}
  paintTheme();
  tb.addEventListener('click', function(){
    var d = root.getAttribute('data-theme') === 'dark';
    if (d) root.removeAttribute('data-theme'); else root.setAttribute('data-theme','dark');
    try { localStorage.setItem('ws-reading-theme', d ? 'light' : 'dark'); } catch(e){}
    paintTheme();
  });

  /* ── 接上数据库（在 claude.ai 里打开才有；没有就只存这台设备） ── */
  H = localLoad(); render();
  var syncNote = document.getElementById('sync');
  function useDb(){
    if (!window.claude || typeof window.claude.use !== 'function') return Promise.resolve(null);
    return window.claude.use('db');
  }
  if (window.claude && typeof window.claude.use === 'function') {
    window.claude.use('comments').then(function(c){ if (c) { cmt = c; document.body.classList.add('has-cmt'); } }).catch(function(){});
  }
  useDb().then(function(d){
    if (!d) { syncNote.textContent = '这次划的只存在这台设备上（在 Claude 里打开这一页，划线才会同步给 Claude）。'; return; }
    db = d; backend = 'db';
    // 本机之前划的、数据库里没有的，搬过去一次
    var local = localLoad();
    db.collection('highlights').onSnapshot(function(snap){
      var next = {};
      snap.docs.forEach(function(doc){ var x = doc.data(); if (x && typeof x.p === 'number') next[doc.id] = x; });
      if (!snap.metadata.fromCache && Object.keys(local).length) {
        var pending = local; local = {};
        Object.keys(pending).forEach(function(id){ if (!next[id]) db.collection('highlights').doc(id).set(pending[id]).catch(function(){}); });
        try { localStorage.removeItem(LS); } catch(e){}
      }
      H = next; render();
      syncNote.textContent = '划线会自动存好，手机电脑同一份；Claude 能直接读到。';
    }, function(e){ syncNote.textContent = '同步出了点问题（' + (e && e.code || '') + '），先只存在这台设备上。'; db = null; });
  }).catch(function(){ syncNote.textContent = '这次划的只存在这台设备上。'; });
})();
'''


def esc(s):
    return html.escape(str(s), quote=True)


def render(meta, pal, ink_accent, slug):
    pens = {k: c for k, _, c, _ in PENS}
    css = (CSS.replace('__ACCENT__', pal['accent']).replace('__INK_ACCENT__', ink_accent).replace('__BG__', pal['bg'])
              .replace('__TEXT__', pal['text']).replace('__MUTED__', pal['muted'])
              .replace('__PEN_BLUE__', pens['blue']).replace('__PEN_PINK__', pens['pink']).replace('__PEN_ORANGE__', pens['orange'])
              .replace('__PEN_PURPLE__', pens['purple']).replace('__PEN_YELLOW__', pens['yellow']).replace('__PEN_SAM__', pens['sam'])
)
    allp = [{'k': 't', 't': meta['title']}] + ([{'k': 'lede', 't': meta['standfirst']}] if meta.get('standfirst') else []) + meta['paras']
    paras, n = [], 0
    for i, p in enumerate(allp):
        if p['k'] in ('t', 'lede'):
            label, num = ('标题' if p['k'] == 't' else '导语'), ''
        else:
            n += 1; label, num = f'第 {n} 段', f'<span class="num">{n}</span>'
        tag = 'h1' if p['k'] == 't' else 'p'
        paras.append(f'<{tag} class="p" data-k="{p["k"]}" data-i="{i}" data-loc="{label}" data-n="{n if num else ""}" data-t="{esc(p["t"])}">{num}{esc(p["t"])}</{tag}>\n')
        if p['k'] in ('t', 'lede') and (i + 1 == len(allp) or allp[i + 1]['k'] not in ('t', 'lede')):
            paras.append('__META__')
    paras = ''.join(paras)
    legend = ' '.join(f'<span class="pen-dot" style="background:{c}"></span><b>{n}</b>＝{d}' for _, n, c, d in PENS)
    pens_html = ''.join(
        f'<button type="button" class="pen" data-pen="{k}" style="--c:var(--pen-{k})"><i></i><span class="lbl">{n}</span><span class="n"></span></button>'
        for k, n, _, _ in PENS)
    pop_html = ''.join(f'<button type="button" data-pen="{k}" style="--c:var(--pen-{k})" title="{n}" aria-label="{n}"></button>' for k, n, _, _ in PENS)
    js = (JS.replace('__PENS_JSON__', json.dumps({k: n for k, n, _, _ in PENS}, ensure_ascii=False))
            .replace('__ORDER_JSON__', json.dumps([k for k, _, _, _ in PENS])))
    by = ' · '.join(x for x in (meta.get('author'), meta.get('site'), meta.get('date')) if x)
    title = esc(meta['title'])
    meta_html = (f'<p class="by">{esc(by)}</p>\n'
                 f'<div class="howto">像读书一样划：<b>选中几个字</b>，挑一支笔；或者先在底下<b>拿起一支笔</b>，再选字。点已划的地方可以换色、擦掉。 '
                 f'{legend}<span class="sync" id="sync">正在接上……</span></div>\n')
    paras = paras.replace('__META__', meta_html)
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="冬的划线 · {esc(meta.get('site', ''))}">
{FONTS}
<style>{css}</style>
</head>
<body data-slug="{esc(slug)}">
<div class="top"><button type="button" class="rbtn" id="theme-btn" aria-label="切换昼夜">🌕</button></div>
<div class="wrap">
  <p class="eyebrow">冬的划线 · <a href="{esc(meta['url'])}" target="_blank" rel="noopener">原文 ↗</a></p>
  <div class="art" id="art">
{paras}  </div>
</div>
<div class="pop" id="pop" role="toolbar" aria-label="笔盒">{pop_html}<button type="button" class="erase" aria-label="擦掉">✕</button><button type="button" class="big">划上</button><button type="button" class="ask" aria-label="批注" title="批注">💬</button></div>
<div class="hint" id="hint"></div>
<div class="bar"><div class="bar__in">{pens_html}<button type="button" class="ask" id="ask-btn" aria-label="批注" title="批注">💬</button><button type="button" class="list" id="list-btn">清单</button></div></div>
<div class="drawer" id="drawer"><div class="drawer__panel">
  <div class="drawer__head"><h2>划过的地方</h2><div class="tools"><button type="button" id="copy-btn">复制清单</button><button type="button" id="drawer-close">收起</button></div></div>
  <div id="drawer-body"></div>
</div></div>
<div class="toast" id="toast"></div>
<script>{js}</script>
</body>
</html>
'''


def main():
    ap = argparse.ArgumentParser(description='网页文章 → 可划线阅读页')
    ap.add_argument('url', nargs='?', help='文章网址')
    ap.add_argument('--html', help='已经下载好的网页文件（抓不到时用 curl 先下下来）')
    ap.add_argument('--url', dest='url2', help='配合 --html：这篇文章的网址（页头「原文」链接用）')
    ap.add_argument('--slug', help='这篇文章的代号（默认从网址末尾取）')
    ap.add_argument('--series', default='', help='借哪个 AU 系列的配色（au_palettes.yml 的键）；默认站点金色')
    ap.add_argument('-o', '--out', required=True)
    ap.add_argument('--dump', help='把抓出来的文章 JSON 也存一份到这个路径（只放 scratchpad，别进仓库）')
    a = ap.parse_args()
    url = a.url or a.url2
    if not url:
        ap.error('要给网址')
    raw = open(a.html, encoding='utf-8').read() if a.html else fetch(url)
    meta = extract(raw, url)
    if not meta['paras']:
        sys.exit('❌ 没抓到正文')
    slug = a.slug or re.sub(r'[^a-z0-9]+', '-', url.rstrip('/').rsplit('/', 1)[-1].lower()).strip('-')[:60] or 'article'
    pal = palette(a.series)
    ink_accent = pal['accent']
    try:
        import yaml
        au = yaml.safe_load(open(os.path.join(os.path.dirname(os.path.dirname(HERE)), '_data', 'au_palettes.yml'), encoding='utf-8')) or {}
        ink_accent = (au.get(a.series) or {}).get('accent_ink') or pal['accent']
    except Exception:
        pass
    if not a.series:
        ink_accent = '#8a6d12'      # 默认金色在白纸上太浅，压深一档
    page = render(meta, pal, ink_accent, slug)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    open(a.out, 'w', encoding='utf-8').write(page)
    if a.dump:
        json.dump(meta, open(a.dump, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'✅ {a.out}（{meta["title"][:40]}… · {len(meta["paras"])} 段 · {meta.get("author") or "无署名"} · slug {slug}）')


if __name__ == '__main__':
    main()
