#!/usr/bin/env python3
"""Render Pero's DVD source archive. Edit dvd-glossary.json, then rerun this file."""
from pathlib import Path
from html import escape as e
import json
ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / 'sam/pero/archive'
data = json.loads((DEST / 'dvd-glossary.json').read_text())
pages = {p['key']: p for p in data['pages']}
photos = []
for p in data['pages']:
    photos.append({'file':p['source_filename'], 'caption':p.get('title', 'ANTWERP / KUPUCHNIK')})
    if p.get('duplicate_source_filename'):
        photos.append({'file':p['duplicate_source_filename'], 'caption':'KRAZNER · 重复截图（菜单选中状态不同）'})

def photo(file, caption):
    n = next(i for i,p in enumerate(photos) if p['file']==file)
    return f'''<figure class="source-photo"><a class="photo-link" href="images/{e(file)}" data-photo="{n}" aria-label="放大：{e(caption)}"><img src="images/{e(file)}" alt="{e(caption)} · DVD 原始截图" width="852" height="480" loading="lazy"><span>查看原图 ↗</span></a><figcaption>{e(caption)}</figcaption></figure>'''

def page_block(p, section=None):
    if section is None:
        title=p.get('title', 'ANTWERP / KUPUCHNIK')
        original=p.get('text',[])
        translated=p['translation']
    else:
        title=p['sections'][section]['title']
        original=[p['sections'][section]['text']]
        translated=[p['translation'][section]]
    paragraphs=''.join('<p>'+e(s)+'</p>' for s in original)
    chinese=''.join('<p>'+e(s)+'</p>' for s in translated)
    uncertainty=f'<p class="source-note">转录说明：{e(p["uncertainty"])}</p>' if p.get('uncertainty') else ''
    spell=''
    if p['key']=='mullinski_continued': spell='<p class="source-note">原图拼作 TROLLY，按原样保留。以上涉及 Eliot Ness 的叙述仅为 DVD 中的词源故事，不作为已核实的历史记载。</p>'
    if p['key']=='antwerp_kupuchnik' and section==0: spell='<p class="source-note">原图用词为 COMPLIMENT，按原样保留；中文按此处“配套之物”的语境翻译。</p>'
    return f'''<div class="source-page"><div class="source-copy"><p class="page-label">{e(title)} · DVD 页面</p><div class="original" lang="en"><h4>英文原文 <span>DVD SOURCE</span></h4>{paragraphs}</div><div class="translation" lang="zh-CN"><h4>中文译文 <span>整理翻译</span></h4>{chinese}</div>{uncertainty}{spell}</div>{photo(p['source_filename'],title)}</div>'''

nav=''.join(f'<a href="#{t["id"]}"><span>{i+1:02}</span> {t["name"]}</a>' for i,t in enumerate(data['terms']))
entries=[]
for i,t in enumerate(data['terms']):
    blocks=''.join(page_block(pages[key],t.get('section')) for key in t['pages'])
    extra=''
    if t['id']=='krazner':
        p=pages['krazner']
        extra=f'<details class="duplicate"><summary>另存：Krazner 同页重复截图</summary><p>两张正文相同，保留菜单选中状态不同的第二张，便于对照。</p>{photo(p["duplicate_source_filename"], "KRAZNER · 第二张截图")}</details>'
    if t['id']=='antwerp': extra='<p class="source-note">Antwerp 与下方 Kupuchnik 出自同一张 DVD 页面，分别归入各自词条。</p>'
    entries.append(f'''<article class="entry" id="{t['id']}"><header class="entry-head"><span class="entry-number">{i+1:02}</span><div><p class="eyebrow">COLLINWOODISMS</p><h2>{t['name']}</h2><p class="meaning">{t['meaning']}<span>中文释义</span></p></div><a class="back-top" href="#terms" aria-label="返回词条目录">↑ 目录</a></header>{blocks}{extra}</article>''')
menu=''.join(f'<article class="menu-page"><h3>{e(pages[key]["title"])}</h3>{page_block(pages[key])}</article>' for key in ['main_menu','special_features'])
html='''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Collinwood 术语档案 · Pero Mahlovic · Winter Sun</title>
<meta name="description" content="《欢迎来到科林伍德》DVD Definitions and Etymologies：五个术语的英文原文、中文译文与十张原始截图。">
<meta name="theme-color" content="#1a1612">
<link rel="icon" type="image/png" href="/WinterSunBlog/images/heading-normal.png">
<link rel="canonical" href="https://dxwintersun.github.io/WinterSunBlog/sam/pero/archive/">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Noto+Serif+SC:wght@400;500;600&family=Special+Elite&display=swap" rel="stylesheet">
<style>
:root{color-scheme:dark;--bg:#1a1612;--ink:#ede0cc;--accent:#b8703a;--muted:#baaa93;--line:#5c4532;--paper:#231d17;--soft:#30251c}*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:24px}body{margin:0;background:var(--bg);color:var(--ink);font-family:'Noto Serif SC',Georgia,serif;font-size:16px;line-height:1.9}a{color:inherit;text-underline-offset:5px}a:focus-visible,button:focus-visible,summary:focus-visible{outline:2px solid #e6ac79;outline-offset:5px}button{font:inherit}button,a,summary{-webkit-tap-highlight-color:transparent}img{display:block;max-width:100%;height:auto}.wrap{width:min(1120px,calc(100% - 64px));margin:auto}.topbar{display:flex;justify-content:space-between;gap:20px;padding:22px 0;border-bottom:1px solid var(--line);font-size:.8rem;letter-spacing:.07em}.topbar a{text-decoration:none}.topbar a:hover{color:#e6ac79}.topbar .brand{font-family:Georgia,serif;font-style:italic}.hero{display:grid;grid-template-columns:1.1fr 1fr;gap:56px;align-items:center;padding:68px 0 60px}.eyebrow{font-family:'Special Elite',monospace;font-size:.72rem;letter-spacing:.18em;color:#d9a477;margin:0 0 10px}.hero h1{font-size:clamp(2rem,4.5vw,3.5rem);line-height:1.3;font-weight:500;letter-spacing:.02em;margin:0 0 20px}.hero h1 em{font-family:'Cormorant Garamond',Georgia,serif;display:block;font-size:1.3em;line-height:1.1;font-weight:500;color:#e1b185}.intro{max-width:35em;color:var(--muted);font-size:.95rem}.stamp{font-family:'Special Elite',monospace;color:#dfac80;font-size:.7rem;letter-spacing:.1em;border:1px solid var(--line);display:inline-block;padding:5px 12px;margin-top:18px}.hero-photo{transform:rotate(-3deg);padding:9px;background:#d7c4a6;box-shadow:7px 10px 0 #0e0c0a;position:relative}.hero-photo:before{content:'';position:absolute;width:100px;height:25px;background:#c2a16bba;top:-12px;left:36%;transform:rotate(3deg)}.hero-photo figcaption{color:#534334;font-size:.7rem;font-family:monospace;text-align:center;letter-spacing:.08em;padding-top:8px}.hero-photo figure{margin:0}.archive-note{border:1px solid var(--line);border-left:3px solid var(--accent);padding:22px 26px;background:var(--paper);margin-bottom:30px}.archive-note p{margin:0;font-size:.86rem;color:var(--muted)}.archive-note strong{color:var(--ink);font-weight:500}.term-index{padding:6px 0 30px;border-bottom:1px solid var(--line);margin-bottom:60px}.term-index h2{font-size:.8rem;letter-spacing:.15em;font-weight:400;color:var(--muted)}.term-links{display:flex;flex-wrap:wrap;gap:10px}.term-links a{border:1px solid var(--line);padding:8px 15px;text-decoration:none;font-family:Georgia,serif;font-size:1rem;transition:background .2s}.term-links a:hover{background:var(--soft)}.term-links span{font: .68rem monospace;color:#d9a477;margin-right:7px}.term-index .extras{margin:18px 0 0;display:flex;gap:22px;flex-wrap:wrap;font-size:.8rem;color:var(--muted)}.entry{margin-bottom:70px;scroll-margin-top:24px}.entry-head{display:flex;gap:20px;align-items:flex-start;border-bottom:1px solid var(--line);padding-bottom:24px;margin-bottom:28px}.entry-number{font:2.1rem 'Cormorant Garamond',Georgia,serif;color:#d9a477;line-height:1.4;border-bottom:2px solid var(--accent)}.entry-head .eyebrow{font-size:.62rem;margin-bottom:0}.entry h2{font-family:'Cormorant Garamond',Georgia,serif;line-height:1.15;font-size:2.8rem;font-weight:500;margin:0 0 10px}.meaning{margin:0;font-size:.98rem}.meaning span{font-size:.64rem;color:var(--muted);display:inline-block;margin-left:14px;vertical-align:middle;border:1px solid var(--line);padding:0 6px}.back-top{margin-left:auto;white-space:nowrap;font-size:.7rem;color:var(--muted);text-decoration:none}.source-page{display:grid;grid-template-columns:minmax(0,1.28fr) minmax(0,1fr);gap:40px;padding:0 0 34px;margin-bottom:26px;border-bottom:1px dashed var(--line)}.source-page:last-child{margin-bottom:0;padding-bottom:0;border-bottom:0}.page-label{font-family:monospace;color:var(--muted);font-size:.66rem;letter-spacing:.07em;margin:0 0 20px}h4{font-size:.73rem;font-weight:500;color:#e1b185;margin:0 0 12px}h4 span{font: .6rem monospace;letter-spacing:.1em;color:var(--muted);margin-left:10px}.original p{font-family:Georgia,'Times New Roman',serif;white-space:pre-line;font-size:.87rem;line-height:1.7;letter-spacing:.018em;margin:0 0 15px;overflow-wrap:break-word}.translation{border-left:2px solid var(--line);padding-left:17px;margin-top:24px}.translation p{font-size:.92rem;line-height:1.95;margin:0 0 14px}.source-photo{margin:0;align-self:start;min-width:0}.photo-link{display:block;border:1px solid var(--line);padding:6px;background:var(--paper);position:relative}.photo-link img{width:100%}.photo-link span{position:absolute;bottom:10px;right:10px;font-size:.6rem;line-height:1.7;background:#16120fea;padding:2px 8px;color:#f5e3ca}.source-photo figcaption{color:var(--muted);font-size:.64rem;font-family:monospace;line-height:1.6;margin-top:9px;letter-spacing:.03em}.source-note{color:var(--muted);font-size:.75rem;line-height:1.85;margin:20px 0}.duplicate{margin:20px 0;padding:14px 18px;background:var(--paper);border:1px solid var(--line)}summary{cursor:pointer;font-size:.82rem}.duplicate p{font-size:.78rem;color:var(--muted)}.duplicate .source-photo{max-width:500px;margin-top:20px}.menus{border-top:1px solid var(--line);padding:36px 0}.menus>h2{font-size:1.4rem;font-weight:500;margin:0}.menus>p{color:var(--muted);font-size:.85rem;margin:8px 0 30px}.menu-page{margin:35px 0}.menu-page>h3{font:1.5rem 'Cormorant Garamond',Georgia,serif;margin:0 0 18px}.provenance{padding:25px;border:1px solid var(--line);background:var(--paper);margin-bottom:50px}.provenance h2{font-size:1rem;margin:0 0 12px;font-weight:500}.provenance p{font-size:.8rem;color:var(--muted);margin:8px 0}.footer{display:flex;justify-content:space-between;gap:20px;border-top:1px solid var(--line);padding:25px 0 40px;font-size:.75rem;color:var(--muted)}dialog{background:#15120f;color:var(--ink);border:1px solid var(--line);padding:18px;width:min(1050px,calc(100% - 24px));max-height:95vh;max-height:95dvh;overflow:auto}dialog::backdrop{background:#090807e8}.viewer-top{display:flex;align-items:center;justify-content:space-between;gap:16px;font-size:.8rem;margin-bottom:16px}dialog button{color:var(--ink);border:1px solid var(--line);background:var(--paper);padding:7px 14px;cursor:pointer;min-height:44px}dialog img{width:100%;max-height:72vh;object-fit:contain;background:#0a0807}.viewer-controls{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-top:16px;font-size:.8rem}.viewer-controls a{color:var(--muted)}.viewer-controls button:disabled{opacity:.3;cursor:default}.skip{position:absolute;top:-100px;left:16px;background:var(--ink);color:var(--bg);padding:10px;z-index:2}.skip:focus{top:10px}@media(max-width:760px){.wrap{width:calc(100% - 32px)}.topbar{font-size:.72rem;padding:16px 0}.hero{grid-template-columns:1fr;gap:36px;padding:42px 0 38px}.hero-photo{max-width:520px;margin:0 9px}.hero h1{font-size:2.25rem}.intro{font-size:.9rem}.stamp{margin-top:8px}.archive-note{padding:18px}.term-index{margin-bottom:38px}.term-links{gap:8px}.term-links a{padding:8px 12px}.source-page{grid-template-columns:1fr;gap:24px}.source-photo{width:100%;max-width:600px}.entry{margin-bottom:52px}.entry-head{gap:15px}.entry h2{font-size:2.5rem}.meaning{font-size:.88rem}.meaning span{font-size:.58rem;margin-left:8px}.original p{font-size:.82rem}.translation{padding-left:13px}.translation p{font-size:.94rem}.back-top{font-size:.65rem}.entry-number{font-size:1.8rem}.provenance{padding:20px}.footer{flex-wrap:wrap}.viewer-top{font-size:.68rem}.viewer-controls{font-size:.7rem}.viewer-controls button{padding:7px 10px}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}*{transition:none!important}}
</style>
</head><body>
<a class="skip" href="#terms">跳到词条目录</a><div class="wrap">
<nav class="topbar" aria-label="返回导航"><a href="/WinterSunBlog/sam/many-faces/#pero">← Pero Mahlovic · 角色画册</a><a class="brand" href="/WinterSunBlog/sam/">Winter Sun / Sam</a></nav>
<main><header class="hero"><div><p class="eyebrow">PERO MAHLOVIC · SOURCE ARCHIVE / 001</p><h1><em>Collinwood</em>术语档案</h1><p class="intro">《欢迎来到科林伍德》DVD 特别收录中的<br lang="en">Definitions and Etymologies。<br>把这条街的黑话，连同它们的来历，一页页存好。</p><span class="stamp">5 TERMS · 7 PAGES · 10 CAPTURES</span></div><div class="hero-photo"><figure><img src="images/E__WELCOME_TO_COLLINWOOD_20261107_183921.764.jpg" alt="DVD Definitions and Etymologies 中的 Bellini 页面" width="852" height="480"><figcaption>WELCOME TO COLLINWOOD · DVD EXTRA</figcaption></figure></div></header>
<aside class="archive-note" aria-label="来源说明"><p><strong>原片资料，与 AU 分开收存。</strong> 英文是 DVD 页面原文；中文是整理译文。词源轶事保留 DVD 的叙述方式，<strong>不当作已核实的历史事实</strong>，也不自动变成 Pero 的 AU 设定。全部原图可点开放大。</p></aside>
<nav class="term-index" id="terms" aria-label="术语目录"><h2>词条目录 / DEFINITIONS &amp; ETYMOLOGIES</h2><div class="term-links">__NAV__</div><p class="extras"><a href="#dvd-menus">DVD 菜单留档 ↓</a><a href="#record">来源与转录说明 ↓</a><a href="dvd-transcription.txt" download>下载英文转录 ↓</a></p></nav>
__ENTRIES__
<section class="menus" id="dvd-menus"><h2>DVD 菜单留档</h2><p>原盘入口：主菜单 → Special Features → Definitions and Etymologies。</p>__MENU__</section>
<section class="provenance" id="record"><h2>这份档案收了什么</h2><p>来源：Winter 提供的《Welcome to Collinwood》DVD 截图。2026 年 11 月 7 日归档。DVD 的具体发行版本、地区及发行商信息未从这些画面确认。</p><p>共 10 张原图：7 张不同的术语页、1 张 Krazner 重复截图、2 张菜单。Antwerp 和 Kupuchnik 共用最后一张术语页。页面按 DVD 导航推定的阅读顺序排列。</p><p>英文保留原图的拼写、用词与断行，撇号统一为排印形式。TROLLY、COMPLIMENT 按原样保留；CO 后的句点无法辨明，已在对应页面说明。菜单中的导航标签、页脚文字另见完整转录。</p><p>中文释义与译文为本档案整理内容，不是 DVD 自带中文，也不是独立史料核验。原图与文字供对照阅读。</p><p><a href="dvd-transcription.txt" download>英文完整转录（TXT）</a> · <a href="dvd-glossary.json" download>结构化档案（JSON）</a></p></section>
</main><footer class="footer"><a href="/WinterSunBlog/sam/many-faces/#pero">← 回 Pero 的角色页</a><a href="#terms">回到词条目录 ↑</a><span>Winter Sun · Collinwood Archive</span></footer>
</div>
<dialog id="image-viewer" aria-labelledby="viewer-caption"><div class="viewer-top"><span id="viewer-caption"></span><button type="button" id="viewer-close" aria-label="关闭原图">关闭 ×</button></div><img id="viewer-image" alt=""><div class="viewer-controls"><button type="button" id="viewer-prev" aria-label="上一张截图">← 上一张</button><a id="viewer-original" target="_blank" rel="noopener">打开原文件 ↗</a><button type="button" id="viewer-next" aria-label="下一张截图">下一张 →</button></div></dialog>
<script>
(function(){'use strict';
var photos=__PHOTOS__,current=0,viewer=document.getElementById('image-viewer');
if(!viewer.showModal)return;
var caption=document.getElementById('viewer-caption'),img=document.getElementById('viewer-image'),prev=document.getElementById('viewer-prev'),next=document.getElementById('viewer-next'),original=document.getElementById('viewer-original');
function show(n){current=n;var p=photos[n];img.src='images/'+p.file;img.alt=p.caption+' · DVD 原始截图';caption.textContent=(n+1)+' / '+photos.length+' · '+p.caption;original.href=img.src;prev.disabled=n===0;next.disabled=n===photos.length-1;}
document.querySelectorAll('[data-photo]').forEach(function(a){a.addEventListener('click',function(event){if(event.ctrlKey||event.metaKey||event.shiftKey||event.altKey)return;event.preventDefault();show(Number(a.dataset.photo));viewer.showModal();});});
document.getElementById('viewer-close').addEventListener('click',function(){viewer.close();});
prev.addEventListener('click',function(){if(current>0)show(current-1);});next.addEventListener('click',function(){if(current<photos.length-1)show(current+1);});
viewer.addEventListener('keydown',function(event){if(event.key==='ArrowLeft'&&current>0){event.preventDefault();show(current-1);}if(event.key==='ArrowRight'&&current<photos.length-1){event.preventDefault();show(current+1);}});
viewer.addEventListener('click',function(event){if(event.target===viewer){var box=viewer.getBoundingClientRect();if(event.clientX<box.left||event.clientX>box.right||event.clientY<box.top||event.clientY>box.bottom)viewer.close();}});
})();
</script></body></html>
'''
html=html.replace('__NAV__',nav).replace('__ENTRIES__','\n'.join(entries)).replace('__MENU__',menu).replace('__PHOTOS__',json.dumps(photos,ensure_ascii=False))
(DEST/'index.html').write_text(html)
# Plain English source copy: preserve all source text and navigation, without private file IDs.
lines=['Welcome to Collinwood DVD — Definitions and Etymologies','SOURCE: Ten DVD screenshots supplied by Winter. Archived 2026-11-07.','English is transcribed from the screenshots; narrative claims are DVD text, not independently verified history.','Seven distinct glossary pages, one duplicate glossary screenshot, and two menus. Apostrophe typography normalized.','']
for p in data['pages']:
    lines += [p.get('heading',''),p.get('title','ANTWERP / KUPUCHNIK'),'SCREENSHOT: '+p['source_filename']]
    lines += p.get('text',[])
    for s in p.get('sections',[]): lines += [s['title'],s['text']]
    if p.get('duplicate_source_filename'): lines += ['DUPLICATE SCREENSHOT: '+p['duplicate_source_filename']]
    if p.get('navigation'): lines += ['Navigation: '+', '.join(p['navigation'])]
    if p.get('footer'): lines += ['Footer: '+p['footer']]
    if p.get('uncertainty'): lines += ['TRANSCRIPTION NOTE: A full stop after CO is not confidently distinguishable; transcribed CO,.']
    lines += ['','']
(DEST/'dvd-transcription.txt').write_text('\n\n'.join(lines))
print('Rendered archive: 5 terms, 7 glossary pages, 10 source images.')
