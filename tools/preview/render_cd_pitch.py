# -*- coding: utf-8 -*-
"""「CD 收藏馆」提案页（2026-11-04）。

Winter：「眼下我在想能不能做一个 cd 收藏馆，我回去把我的 cd 都拍给你你帮我记一下，拿不准的你可以问我。
买的不少所以有时候搞不清楚」。照规矩不猜着做：先排三版样子给她挑（书脊柜 / 封面墙 / 收藏簿），
再挑名字、记哪些、怎么排、从哪儿进。页底岔路栏点选复制。

用法：python3 tools/preview/render_cd_pitch.py 输出.html tools/preview/cd-pitch-forks.json
"""
import html
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import forks as forks_mod  # noqa: E402

E = lambda s: html.escape(s or '', quote=True)

# 示意用的几张（她提过的 / 正在买的；真页面按她拍来的照片一张张记）
CDS = [
    dict(a="Goo Goo Dolls", t="Dizzy Up the Girl", y=1998, h=18, ver="美版 · 1 CD · 带小册子", frm="二手店", when="2019", st="", note="Iris 在第 11 首。"),
    dict(a="Goo Goo Dolls", t="Over My Head", y=2006, h=42, ver="单曲 · 英版", frm="eBay", when="2021", st="盒子裂了", note="盒子裂了，但是内容是好的。"),
    dict(a="Goo Goo Dolls", t="Let Love In", y=2006, h=28, ver="美版", frm="", when="", st="", note=""),
    dict(a="Lady Pank", t="Teraz", y=2004, h=205, ver="波兰版 · BMG · 剃须刀片封面", frm="eBay · 波兰直邮", when="2026-11（在路上）", st="全新", note="录音室版的 Stacja Warszawa 只在这张上。"),
    dict(a="Lady Pank", t="45", y=2025, h=215, ver="波兰版 · 四十五周年", frm="eBay", when="想买", st="全新", note="Motyle · Moje życie。"),
    dict(a="Feel", t="Feel", y=2007, h=350, ver="波兰版", frm="", when="", st="", note=""),
    dict(a="Myslovitz", t="Miłość w czasach popkultury", y=1999, h=95, ver="波兰版", frm="", when="", st="", note=""),
]


def spine(c, i):
    return ('<button class="sp" style="--h:%d;--i:%d" type="button"><span>%s</span><b>%s</b><i>%d</i></button>'
            % (c['h'], i, E(c['a']), E(c['t']), c['y']))


def cover(c):
    ini = ''.join(w[0] for w in c['t'].split()[:2]).upper()
    return '<div class="cv" style="--h:%d"><span>%s</span></div>' % (c['h'], E(ini))


CSS = '''
:root{--bg:#eef3f8;--paper:#f8fafc;--ink:#1c2a44;--muted:#5d6b85;--accent:#3f73a8;--gold:#d9a441;--line:#c9d6e4;
 --disp:"EB Garamond",Georgia,"Noto Serif SC",serif;--body:"Noto Serif SC","Songti SC",Georgia,serif;--mono:"Special Elite","Courier New",monospace;}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#0f1727;--paper:#182236;--ink:#e6edf6;--muted:#93a3bd;--accent:#7fb0e6;--gold:#e2b45a;--line:#2b3a55;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#0f1727;--paper:#182236;--ink:#e6edf6;--muted:#93a3bd;--accent:#7fb0e6;--gold:#e2b45a;--line:#2b3a55;color-scheme:dark}
body{background:var(--bg);color:var(--ink);font-family:var(--body);line-height:1.8;font-size:16px;margin:0;}
.wrap{max-width:46rem;margin:0 auto;padding-block:2rem 7rem;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));}
.wrap,.wrap *{box-sizing:border-box;}
.kicker{font-family:var(--disp);letter-spacing:.14em;text-transform:uppercase;font-size:.78rem;color:var(--accent);margin:0 0 .4rem;}
h1{font-family:var(--disp);font-weight:600;font-size:2rem;line-height:1.2;margin:0 0 .8rem;text-wrap:balance;}
h1 em{font-style:italic;color:var(--accent);}
.lede{color:var(--muted);margin:0;font-size:.98rem;}
.blk{margin-top:3rem;}
.blk h2{font-family:var(--disp);font-weight:600;font-size:1.35rem;margin:0 0 .3rem;display:flex;gap:.6rem;align-items:baseline;}
.blk h2 small{font-size:.72rem;letter-spacing:.12em;text-transform:uppercase;color:var(--accent);}
.note{color:var(--muted);font-size:.9rem;margin:0 0 1.2rem;}
.opt{margin-top:1.6rem;}
.opt__h{display:flex;align-items:center;gap:.6rem;margin-bottom:.4rem;}
.opt__k{font-family:var(--disp);width:1.6rem;height:1.6rem;border-radius:50%;border:1px solid var(--accent);color:var(--accent);display:inline-grid;place-items:center;font-size:.85rem;}
.opt__name{font-weight:600;}
.opt__rec{font-size:.72rem;letter-spacing:.08em;color:var(--bg);background:var(--accent);border-radius:2px;padding:.05rem .45rem;}
.opt__why{margin:0 0 .9rem;font-size:.93rem;}
.cap{color:var(--muted);font-size:.85rem;margin:.6rem 0 0;}
.how{display:grid;gap:.6rem;margin:1rem 0 0;padding:0;list-style:none;}
.how li{display:grid;grid-template-columns:1.6rem 1fr;gap:.5rem;font-size:.93rem;}
.how li b{font-family:var(--disp);color:var(--accent);font-weight:600;}
.mk{background:var(--paper);border:1px solid var(--line);border-radius:10px;padding:1rem;max-width:min(30rem,100%);min-width:0;}

/* 封面小方块（示意；真页面用专辑图） */
.cv{aspect-ratio:1;border-radius:3px;display:grid;place-items:center;color:#fff;font-family:var(--disp);font-weight:600;letter-spacing:.06em;
 background:linear-gradient(135deg,hsl(var(--h) 42% 50%),hsl(calc(var(--h) + 35) 50% 30%));box-shadow:inset 0 0 0 1px rgba(255,255,255,.15);}

/* ---- A 书脊柜 ---- */
.rack{background:linear-gradient(180deg,#8a6a4a,#6e5238);border-radius:8px;padding:.9rem .8rem .5rem;position:relative;}
.rack__row{display:flex;gap:2px;align-items:flex-end;height:12.5rem;padding:0 .3rem;}
.rack__board{height:.55rem;margin:0 -.8rem;background:linear-gradient(180deg,#a7845f,#5b4129);box-shadow:0 3px 6px rgba(0,0,0,.35);}
.rack__label{font-family:var(--mono);font-size:.62rem;letter-spacing:.14em;color:#f1e4cf;opacity:.85;margin:.35rem 0 .2rem .3rem;}
.sp{flex:1 1 0;min-width:0;height:100%;border:0;border-radius:2px 2px 0 0;cursor:pointer;position:relative;padding:0;
 background:linear-gradient(90deg,hsl(var(--h) 38% 34%),hsl(var(--h) 42% 48%) 50%,hsl(var(--h) 38% 30%));box-shadow:inset 1px 0 0 rgba(255,255,255,.25),inset -1px 0 0 rgba(0,0,0,.3);
 writing-mode:vertical-rl;transform:rotate(180deg);color:#fff;font-family:var(--disp);font-size:.7rem;letter-spacing:.06em;line-height:1;display:flex;gap:.35rem;align-items:center;justify-content:flex-start;padding:.5rem .1rem;}
.sp span{opacity:.8;font-size:.62rem;}
.sp b{font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex:1;min-width:0;}
.sp i{font-style:normal;font-size:.6rem;opacity:.8;}
.sp.is-out{flex:0 0 5.4rem;background:#111;transform:none;writing-mode:horizontal-tb;align-items:stretch;padding:.3rem;border-radius:3px;}
.sp.is-out>span,.sp.is-out>b,.sp.is-out>i{display:none;}
.sp.is-out .cv{width:100%;height:auto;font-size:.9rem;}
.pull{background:var(--paper);border:1px solid var(--line);border-radius:8px;padding:.7rem .8rem;margin-top:.9rem;display:grid;grid-template-columns:4.2rem 1fr;gap:.7rem;align-items:start;font-size:.82rem;line-height:1.55;}
.pull h4{margin:0;font-family:var(--disp);font-size:1rem;}
.pull p{margin:.1rem 0 0;color:var(--muted);}
.pull p b{color:var(--ink);font-weight:600;}

/* ---- B 封面墙 ---- */
.wall{display:grid;grid-template-columns:repeat(3,1fr);gap:.8rem .6rem;}
.jc{position:relative;min-width:0;}
.jc .case{position:relative;aspect-ratio:1;border-radius:2px;background:#0b0b0b;padding:3px 3px 3px 9px;}
.jc .case::before{content:"";position:absolute;left:0;top:0;bottom:0;width:7px;background:linear-gradient(90deg,#000,#2a2a2a 60%,#000);border-radius:2px 0 0 2px;}
.jc .case::after{content:"";position:absolute;inset:0;border-radius:2px;background:linear-gradient(115deg,rgba(255,255,255,.28),transparent 35%,transparent 70%,rgba(255,255,255,.1));pointer-events:none;}
.jc .cv{position:absolute;inset:3px 3px 3px 9px;aspect-ratio:auto;border-radius:1px;}
.tag{margin:.3rem 0 0 .4rem;display:inline-block;background:#fff8e6;color:#2a241a;border:1px solid #d9cba3;border-radius:2px;padding:.1rem .4rem .15rem;font-family:var(--mono);font-size:.56rem;line-height:1.45;position:relative;max-width:100%;}
.tag::before{content:"";position:absolute;left:-.4rem;top:-.35rem;width:.5rem;height:.5rem;border-radius:50%;border:1px solid #d9cba3;background:var(--paper);}
.tag b{display:block;font-size:.62rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.tag.is-new::after{content:"NEW";position:absolute;right:-.3rem;top:-.5rem;background:#d4213d;color:#fff;font-size:.5rem;padding:0 .25rem;border-radius:2px;letter-spacing:.08em;}

/* ---- C 收藏簿 ---- */
.book{background:#fbf7ee;color:#2a241a;border:1px solid #e2d8c2;border-radius:6px;padding:1rem;position:relative;}
.book::before{content:"";position:absolute;left:1.6rem;top:0;bottom:0;border-left:1px solid #e9b4b4;}
.book__pg{display:grid;grid-template-columns:5.2rem 1fr;gap:.9rem;padding:.6rem 0 .8rem 1.2rem;border-bottom:1px dashed #d8ccb0;}
.book__pg:last-child{border-bottom:0;}
.book__pg h4{margin:0;font-family:var(--disp);font-size:1.05rem;line-height:1.2;}
.book__pg h4 small{display:block;font-size:.75rem;color:#7a6f57;font-weight:400;margin-top:.1rem;}
.book table{border-collapse:collapse;font-size:.72rem;margin-top:.35rem;width:100%;font-family:var(--mono);}
.book td{padding:.08rem .3rem .08rem 0;vertical-align:top;border-bottom:1px dotted #d8ccb0;}
.book td:first-child{color:#7a6f57;white-space:nowrap;width:4.2rem;}
.book .memo{font-family:"Ma Shan Zheng","Kaiti SC","STKaiti",cursive;font-size:.95rem;color:#5a4b8a;margin:.3rem 0 0;transform:rotate(-1deg);}
.book .no{position:absolute;left:.35rem;font-family:var(--mono);font-size:.6rem;color:#b5a98a;}
'''


def mock_a():
    rows = []
    rows.append('<div class="rack__label">LADY PANK · FEEL · MYSLOVITZ</div><div class="rack__row">'
                + ''.join(spine(c, i) if c['t'] != 'Teraz' else spine(c, i).replace('class="sp"', 'class="sp is-out"').replace('<span>', cover(c) + '<span>', 1)
                          for i, c in enumerate(CDS[3:7])) + '</div><div class="rack__board"></div>')
    rows.append('<div class="rack__label">GOO GOO DOLLS</div><div class="rack__row">'
                + ''.join(spine(c, i) for i, c in enumerate(CDS[0:3])) + '</div><div class="rack__board"></div>')
    c = CDS[3]
    pull = ('<div class="pull">%s<div><h4>%s <small>· %s · %d</small></h4><p>%s</p><p>%s · %s · <b>%s</b></p><p>“%s”</p></div></div>'
            % (cover(c), E(c['t']), E(c['a']), c['y'], E(c['ver']), E(c['frm']), E(c['when']), E(c['st']), E(c['note'])))
    return '<div class="mk" style="padding:.6rem"><div class="rack">%s</div>%s</div>' % (''.join(rows), pull)


def mock_b():
    def one(c):
        new = ' is-new' if c['st'] == '全新' else ''
        return ('<div class="jc"><div class="case">%s</div><div class="tag%s"><b>%s</b>%s · %d<br>%s</div></div>'
                % (cover(c), new, E(c['t']), E(c['a']), c['y'], E(c['ver'].split(' · ')[0] + (' · ' + c['st'] if c['st'] else ''))))
    return '<div class="mk"><div class="wall">%s</div></div>' % ''.join(one(c) for c in [CDS[3], CDS[4], CDS[5], CDS[0], CDS[1], CDS[6]])


def mock_c():
    def pg(i, c):
        rows = [('专辑', '%s（%d）' % (c['t'], c['y'])), ('乐队', c['a']), ('版本', c['ver'] or '—'),
                ('来处', ((c['frm'] + ' · ') if c['frm'] else '') + (c['when'] or '—')), ('状态', c['st'] or '—')]
        return ('<div class="book__pg"><span class="no">%03d</span>%s<div><h4>%s<small>%s · %d</small></h4><table>%s</table>%s</div></div>'
                % (i, cover(c), E(c['t']), E(c['a']), c['y'],
                   ''.join('<tr><td>%s</td><td>%s</td></tr>' % (E(k), E(v)) for k, v in rows),
                   ('<p class="memo">%s</p>' % E(c['note'])) if c['note'] else ''))
    return '<div class="mk book">%s</div>' % ''.join(pg(i + 1, c) for i, c in enumerate([CDS[1], CDS[3]]))


def main(OUT, FORKS):
    fk_css, fk_html, fk_tail, nf = forks_mod.render(FORKS, 'cd-pitch-2026-11-04')
    page = '''<meta charset="utf-8"><title>CD 收藏馆提案</title><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=Noto+Serif+SC:wght@400;600&family=Special+Elite&family=Ma+Shan+Zheng&display=swap" rel="stylesheet">
<style>%s%s</style><div class="wrap">
<header><p class="kicker">冬的唱片柜 · 新的一页 · 2026-11-04</p>
<h1>把家里的 <em>CD</em> 都记进来</h1>
<p class="lede">你回家把 CD 拍给我（正面一张，背面或书脊有字的也拍一张），我一张张认出专辑、乐队、年份、哪国版，查证了再记；认不准的拍出来问你。记好的都挂在博客一页上，以后买之前翻一眼就知道有没有。Sam 的碟还在藏品架上不动，这一页只放音乐。</p>
<ol class="how"><li><b>1</b>你拍照发我，一次几张、几十张都行，不用自己写名字。</li>
<li><b>2</b>唱片墙上已经有的专辑（比如《LP 45》）会互相连着：柜子里点它能跳去看摘录，唱片墙那边也多一枚「柜里有」的小标。</li>
<li><b>3</b>以后新到一张，拍一张发我就记上；eBay 那两张到了也是。</li></ol></header>

<section class="blk"><h2><small>岔路一</small>长什么样</h2>
<p class="note">三版都拿几张示意（有两张是你正在买的），封面小方块只是占位，真页面用专辑图。</p>

<div class="opt"><div class="opt__h"><span class="opt__k">A</span><span class="opt__name">一排排书脊的唱片柜</span><span class="opt__rec">我推荐</span></div>
<p class="opt__why"><b>像你家里那个柜子：一张张侧着立在木头架子上，只看见书脊上的乐队和专辑名，一层一个乐队。</b>点一张，它就从架子上抽出来，露出封面，底下弹出它的资料卡。一眼看过去有多少、是谁的，跟真柜子一个感觉。</p>
%s<p class="cap">↑ 最像「收藏」；书脊的颜色取封面的主色，一排排看着就是你的柜子。</p></div>

<div class="opt"><div class="opt__h"><span class="opt__k">B</span><span class="opt__name">唱片行的那面墙</span></div>
<p class="opt__why"><b>封面朝外一格一格摆满，连塑料壳左边那道黑铰链和反光都画出来。</b>每张底下挂一张小价签，写着乐队、年份、哪国版；全新的贴一枚红色 NEW。更像逛店，封面好看的一眼就看见。</p>
%s<p class="cap">↑ 最好看封面；多了以后一页会很长，按乐队分段。</p></div>

<div class="opt"><div class="opt__h"><span class="opt__k">C</span><span class="opt__name">一本收藏簿</span></div>
<p class="opt__why"><b>一张 CD 一页：左边封面，右边一张小表，版本、来处、到手日、状态一行一行，最后一行是你那句碎碎念，手写体。</b>最像账本，查东西最方便。</p>
%s<p class="cap">↑ 最清楚；缺点是不够像一个「馆」。</p></div>
</section>

%s
</div>%s''' % (CSS, fk_css, mock_a(), mock_b(), mock_c(), fk_html, fk_tail)
    open(OUT, 'w', encoding='utf-8').write(page)
    print('ok', len(page))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
