#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把一篇草稿 .md 渲染成「草稿 · 待冬璇过目」预览页（用于 Artifact 交付）。

用法（在仓库根目录跑）：

    python3 tools/preview/render_draft.py 草稿.md -o 预览.html \
        --series "Zaphod AU" \
        --title  "雪的巡游" \
        --subtitle "番外 · Don't Panic, Baby Doll" \
        --mood   "缱绻 · 安放" \
        --notes  衔接说明.md

然后把生成的 .html 用 Artifact 工具发布，把链接给 Winter。

配色自动从 `_data/au_palettes.yml` 按 --series（= 章节 front matter 的
series 值）取该 AU 的 accent / bg / text / muted，所以预览页的观感和
线上阅读页一致。系列不在表里就回退到站点默认金色。

支持的 Markdown 子集（跟博客正文实际用到的一致）：
  ### 小节标题 ／ > 引用块 ／ **粗体** ／ --- 分隔线
  行尾两个空格 = 硬换行（诗式收束、多行题词靠这个）
  以 < 开头的裸 HTML 块原样透传（内嵌 SVG 插图、c-note 便条卡、c-decree 公文卡、c-comm 通讯屏等，
  后两者预览页自带简化样式，看到的效果跟线上接近）
"""
import argparse, html, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
DEFAULT = {'accent': '#c9a227', 'bg': '#12110f', 'text': '#ece7dd', 'muted': '#8f8a7e'}

OPEN_TAG = re.compile(r'<([a-zA-Z][\w-]*)(?=[\s/>])(?![^>]*/>)')
CLOSE_TAG = re.compile(r'</([a-zA-Z][\w-]*)\s*>')
# 自闭合 / 无需配对的标签（全小写，比较时统一 lower —— SVG 标签名大小写敏感，
# 漏一个就会让整块 HTML 之后的正文被当成 HTML 一起吞掉）
VOID = {'br', 'hr', 'img', 'input', 'meta', 'link', 'source', 'use', 'stop',
        'circle', 'rect', 'path', 'line', 'ellipse', 'polygon', 'polyline',
        'animate', 'animatetransform', 'animatemotion', 'set', 'feoffset',
        'fegaussianblur', 'femerge', 'femergenode', 'fecolormatrix', 'col'}


def palette(series):
    """从 _data/au_palettes.yml 取该系列配色；取不到就用默认。"""
    if not series:
        return dict(DEFAULT)
    path = os.path.join(ROOT, '_data', 'au_palettes.yml')
    try:
        import yaml
        data = yaml.safe_load(open(path, encoding='utf-8')) or {}
    except Exception as e:
        print(f'⚠️  读不到 {path}（{e}），用默认配色', file=sys.stderr)
        return dict(DEFAULT)
    entry = data.get(series)
    if not entry:
        print(f'⚠️  au_palettes.yml 里没有 "{series}"，用默认配色', file=sys.stderr)
        return dict(DEFAULT)
    return {k: entry.get(k, DEFAULT[k]) for k in DEFAULT}


def inline(s):
    s = html.escape(s)
    return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)


def join(lines):
    """段落内：行尾两个空格 = 硬换行。"""
    out = []
    for i, ln in enumerate(lines):
        out.append(inline(ln.rstrip()))
        if i < len(lines) - 1:
            out.append('<br>\n' if ln.endswith('  ') else '\n')
    return ''.join(out)


def html_depth(text):
    """算一段 HTML 的标签嵌套深度。整段一起算（不是逐行），
    这样跨行写的 <animateTransform ... /> 也能被正确认成自闭合。"""
    d = 0
    for m in OPEN_TAG.finditer(text):
        if m.group(1).lower() not in VOID:
            d += 1
    for m in CLOSE_TAG.finditer(text):
        if m.group(1).lower() not in VOID:
            d -= 1
    return d


def to_html(src):
    out, para, quote, raw = [], [], [], []

    def flush_p():
        if para:
            out.append('<p>' + join(para) + '</p>')
            para.clear()

    def flush_q():
        if quote:
            out.append('<blockquote>' + join(quote) + '</blockquote>')
            quote.clear()

    for line in src.split('\n'):
        stripped = line.strip()

        if raw:                                   # 裸 HTML 块进行中
            raw.append(line)
            if html_depth('\n'.join(raw)) <= 0 and not stripped:
                out.append('\n'.join(raw).strip()); raw.clear()
            continue

        if stripped.startswith('<'):              # 裸 HTML 块开始
            flush_p(); flush_q()
            raw.append(line)
            if html_depth(stripped) <= 0 and CLOSE_TAG.search(stripped):
                out.append('\n'.join(raw).strip()); raw.clear()
            continue

        if line.startswith('> '):
            flush_p(); quote.append(line[2:])
        elif line.startswith('### '):
            flush_p(); flush_q(); out.append('<h3>' + inline(line[4:]) + '</h3>')
        elif stripped in ('---', '***', '___'):
            flush_p(); flush_q(); out.append('<hr>')
        elif not stripped:
            flush_p(); flush_q()
        else:
            flush_q(); para.append(line)

    flush_p(); flush_q()
    if raw:
        out.append('\n'.join(raw).strip())
    return '\n'.join(out)


CSS = '''<style>
:root{--bg:__BG__;--accent:__ACCENT__;--ink:__TEXT__;--muted:__MUTED__;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
 font-family:"Songti SC","Noto Serif SC",Georgia,serif;line-height:2.05;font-size:17px;}
.wrap{max-width:44rem;margin:0 auto;padding:3.5rem 1.4rem 6rem;}
.eyebrow{font-size:.72rem;letter-spacing:.28em;color:var(--accent);text-align:center;
 margin-bottom:1.6rem;font-family:system-ui,sans-serif;}
h1{font-size:2rem;text-align:center;margin:0 0 .5rem;font-weight:600;letter-spacing:.04em;}
.sub{text-align:center;color:var(--muted);font-size:.85rem;letter-spacing:.12em;
 margin-bottom:.4rem;font-family:system-ui,sans-serif;}
.rule{width:60px;height:1px;background:var(--accent);opacity:.6;margin:2.4rem auto 2.8rem;}
h3{margin:3.2rem 0 1.4rem;font-size:1.05rem;letter-spacing:.1em;color:var(--accent);font-weight:600;}
h3::before{content:"";display:block;width:26px;height:1px;background:currentColor;
 opacity:.45;margin-bottom:.9rem;}
p{margin:0 0 1.5rem;text-align:justify;}
strong{color:#fff;font-weight:600;}
hr{border:0;border-top:1px solid var(--muted);opacity:.35;margin:2.6rem auto;width:40%;}
blockquote{margin:2.2rem 0;padding:1.1rem 0 1.1rem 1.4rem;border-left:2px solid var(--accent);
 background:linear-gradient(90deg,color-mix(in srgb,var(--accent) 9%,transparent),transparent 70%);}
blockquote p{margin:0}
/* 正文里的实物卡片组件（与博客 _sass/5-components/_extras.scss 观感对齐的简化版）*/
.c-note{position:relative;max-width:32rem;margin:2.8rem auto;padding:2.1rem 1.8rem 1.7rem;
 background:#f2eadd;color:#3b3329;border-radius:2px;transform:rotate(-.4deg);
 box-shadow:0 12px 32px rgba(0,0,0,.38);line-height:1.95;}
.c-note::before{content:"";position:absolute;top:-11px;left:50%;width:92px;height:22px;
 transform:translateX(-50%) rotate(-1.6deg);background:color-mix(in srgb,var(--accent) 42%,transparent);
 opacity:.75;box-shadow:0 1px 4px rgba(0,0,0,.18);}
.c-note__label{display:block;font-size:.68rem;letter-spacing:.2em;opacity:.5;
 margin-bottom:1rem;font-family:system-ui,sans-serif;}
.c-note__body p{margin:0 0 .5rem;text-align:left;}
.c-note__sign{display:block;text-align:right;margin-top:1.1rem;opacity:.72;}
/* c-comm —— 设备屏幕上的通讯记录（飞船通讯板 / 终端）。屏幕恒为暗，不随主题翻转。*/
.c-comm{max-width:29rem;margin:2.6rem auto;border-radius:10px;overflow:hidden;
 border:1px solid color-mix(in srgb,var(--accent) 34%,transparent);
 background:color-mix(in srgb,var(--accent) 7%,#0a0c11);
 box-shadow:0 14px 34px rgba(0,0,0,.42),0 0 22px color-mix(in srgb,var(--accent) 12%,transparent);}
.c-comm__bar{display:flex;align-items:center;gap:9px;padding:9px 14px;
 border-bottom:1px solid color-mix(in srgb,var(--accent) 22%,transparent);
 background:color-mix(in srgb,var(--accent) 12%,transparent);
 font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:10.5px;
 letter-spacing:.18em;text-transform:uppercase;color:color-mix(in srgb,var(--accent) 62%,#fff);}
.c-comm__bar::before{content:"";flex:none;width:7px;height:7px;border-radius:50%;
 background:var(--accent);box-shadow:0 0 8px var(--accent);animation:comm-pulse 2.6s ease-in-out infinite;}
.c-comm__id{flex:1 1 auto}
.c-comm__meta{flex:none;opacity:.72;letter-spacing:.12em}
.c-comm__log{counter-reset:comm;margin:0;padding:16px 16px 14px;list-style:none;
 background-image:repeating-linear-gradient(180deg,rgba(255,255,255,.028) 0,rgba(255,255,255,.028) 1px,transparent 1px,transparent 3px);}
.c-comm__log>li{position:relative;margin:0 0 9px;padding-left:42px;font-size:15px;line-height:1.82;
 text-align:left;color:color-mix(in srgb,var(--accent) 30%,#eef2f6);}
.c-comm__log>li:last-child{margin-bottom:0}
.c-comm__log>li::before{counter-increment:comm;content:counter(comm,decimal-leading-zero);
 position:absolute;left:0;top:.28em;width:30px;text-align:right;
 font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:10.5px;
 color:color-mix(in srgb,var(--accent) 52%,transparent);}
.c-comm__gap{padding-left:42px !important;margin:14px 0 !important;line-height:1 !important;
 border-top:1px dashed color-mix(in srgb,var(--accent) 26%,transparent);font-size:11px !important;
 letter-spacing:.4em;color:color-mix(in srgb,var(--accent) 42%,transparent) !important;}
.c-comm__gap::before{content:"" !important;counter-increment:none !important}
.c-comm__last{color:color-mix(in srgb,var(--accent) 22%,#fff) !important;
 text-shadow:0 0 14px color-mix(in srgb,var(--accent) 55%,transparent);}
.c-comm__wait{display:flex;align-items:center;gap:8px;padding:10px 16px 12px;
 border-top:1px solid color-mix(in srgb,var(--accent) 18%,transparent);
 font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:10.5px;
 letter-spacing:.2em;text-transform:uppercase;color:color-mix(in srgb,var(--accent) 48%,transparent);}
.c-comm__wait::before{content:"";flex:none;width:7px;height:13px;background:var(--accent);
 animation:comm-caret 1.1s steps(1,end) infinite;}
@keyframes comm-pulse{0%,100%{opacity:1}50%{opacity:.28}}
@keyframes comm-caret{0%,49%{opacity:1}50%,100%{opacity:0}}
.c-decree{position:relative;max-width:34rem;margin:2.8rem auto;padding:2.4rem 2rem 2rem;
 background:#f4efe4;color:#332c22;border:1px solid rgba(0,0,0,.14);
 box-shadow:0 12px 34px rgba(0,0,0,.38);line-height:1.9;}
.c-decree__seal{position:absolute;top:1.4rem;right:1.4rem;width:76px;height:76px;border-radius:50%;
 display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;
 border:2px solid color-mix(in srgb,var(--accent) 70%,#000);color:color-mix(in srgb,var(--accent) 70%,#000);
 font-family:system-ui,sans-serif;font-size:.5rem;letter-spacing:.08em;opacity:.8;transform:rotate(-8deg);}
.c-decree__stamp{position:absolute;top:1rem;left:1.2rem;font-size:.64rem;letter-spacing:.16em;
 opacity:.5;font-family:system-ui,sans-serif;}
.c-decree__title{margin:.4rem 0 .3rem;font-size:1.15rem;letter-spacing:.08em;}
.c-decree__subtitle{margin:0 0 1.2rem;font-size:.8rem;opacity:.6;}
.c-decree__body{margin:0 0 .8rem;text-align:justify;}
.c-decree__sign{margin-top:1.6rem;text-align:right;}
.c-decree__sign-label{display:block;font-size:.66rem;letter-spacing:.16em;opacity:.5;
 font-family:system-ui,sans-serif;}
.c-decree__signature{font-size:1.05rem;}
.foot{margin-top:4rem;padding-top:1.6rem;border-top:1px solid var(--accent);
 color:var(--muted);font-size:.82rem;line-height:1.9;font-family:system-ui,sans-serif;}
.foot b,.foot strong{color:var(--accent);font-weight:600;}
.foot p{margin:0 0 .6rem;text-align:left}
@media(max-width:480px){body{font-size:16px}.wrap{padding:2.4rem 1.1rem 4rem}h1{font-size:1.6rem}}
</style>'''


def main():
    ap = argparse.ArgumentParser(description='把草稿 .md 渲染成待过目的预览页')
    ap.add_argument('source', help='草稿 markdown 文件（只要正文，不用 front matter）')
    ap.add_argument('-o', '--out', required=True, help='输出的 .html 路径')
    ap.add_argument('--title', required=True, help='页面大标题，如「雪的巡游」')
    ap.add_argument('--series', default='', help='series_name，用于自动取该 AU 配色')
    ap.add_argument('--subtitle', default='', help='副标题，如「番外 · Don\'t Panic, Baby Doll」')
    ap.add_argument('--mood', default='', help='mood 标签，如「缱绻 · 安放」')
    ap.add_argument('--notes', default='', help='衔接说明文件（.md 或 .html），渲染在页尾')
    ap.add_argument('--eyebrow', default='草稿 · 待冬璇过目', help='顶部眉标')
    a = ap.parse_args()

    src = open(a.source, encoding='utf-8').read()
    if src.lstrip().startswith('---'):            # 容忍带 front matter 的成品
        src = src.split('---', 2)[2]

    pal = palette(a.series)
    css = CSS
    for k, v in pal.items():
        css = css.replace(f'__{k.upper()}__', v)
    body = to_html(src)

    foot = ''
    if a.notes:
        raw = open(a.notes, encoding='utf-8').read()
        foot = raw if a.notes.endswith(('.html', '.htm')) else to_html(raw)
        foot = f'<div class="foot">{foot}</div>'

    subs = ''
    if a.subtitle:
        subs += f'<div class="sub">{html.escape(a.subtitle)}</div>\n'
    if a.mood:
        subs += (f'<div class="sub" style="opacity:.7;letter-spacing:.06em">'
                 f'mood：{html.escape(a.mood)}</div>\n')

    page = (f'<title>{html.escape(a.title)}</title>\n{css}\n<div class="wrap">\n'
            f'<div class="eyebrow">{html.escape(a.eyebrow)}</div>\n'
            f'<h1>{html.escape(a.title)}</h1>\n{subs}<div class="rule"></div>\n'
            f'{body}\n{foot}\n</div>')
    open(a.out, 'w', encoding='utf-8').write(page)
    n = len(re.sub(r'<[^>]+>|\s', '', body))
    print(f'✅ {a.out}（配色：{a.series or "默认"} accent {pal["accent"]}，{n} 字）')


if __name__ == '__main__':
    main()
