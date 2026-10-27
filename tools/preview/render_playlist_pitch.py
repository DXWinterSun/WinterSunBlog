# -*- coding: utf-8 -*-
"""「Polski」播放列表页 · 提案页（2026-10-27）。

Winter 把 YouTube Music 上攒的波兰语歌单（公开，38 首）截图发来，说「你看看是不是可以做一个 playlist 功能，
我会不定期给你更新」。照规矩不猜着做，先排三版样子给她挑，页底岔路栏点选复制。

用法：python3 tools/preview/render_playlist_pitch.py 输出.html 岔路.json
"""
import html
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
import forks as forks_mod  # noqa: E402

E = lambda s: html.escape(s or '', quote=True)

# 从她截图里抄下来的曲目（顺序照歌单；时长缺的留空）
TRACKS = [
    ("Urke", "Wilki", "3:24"), ("Ławka", "Platinum Purge", "3:23"), ("Dobra konstelacja", "Lady Pank", "4:25"),
    ("Pokonaj siebie", "Feel & Iwona Węgrowska", ""), ("Bo to co najważniejsze", "Łukasz Zagrobelny", "4:13"),
    ("Życie na czekanie", "Łukasz Zagrobelny", "3:47"), ("W blasku słońca", "Feel & Damian Skoczyk", "3:10"),
    ("Może jeszcze się spotkamy", "Feel", "3:28"), ("Po prostu miłość", "RH+", "3:01"),
    ("Za to co mam", "Mateusz Mijal & Jacek Stachursky", ""), ("Jak anioła głos", "Feel", "3:27"),
    ("Dla siebie sami (Wersja 2012)", "Yugopolis & Krzysztof Kiljański", ""),
    ("Miasto budzi się", "Yugopolis & Paweł Kukiz", "4:20"), ("Konstelacje", "Pin", "3:20"),
    ("Wenus, tu Mars", "Wilki", "2:38"), ("Nieprawda", "Łukasz Zagrobelny", "3:17"),
    ("Tacy sami", "Lady Pank", "4:24"), ("Oh Luczija", "Lady Pank", "3:27"), ("Swoje szczęście znam", "Feel", "3:22"),
    ("Zostań ze mną", "Feel", "3:37"), ("No pokaż na co cię stać", "Feel", "3:38"), ("7 Stan", "Feel", "3:35"),
    ("Niekochanie", "Pin", "3:01"), ("Znowu pada deszcz", "Lady Pank", "4:03"),
    ("Stacja Warszawa", "Lady Pank & Orkiestra Symfoników", ""), ("Ostatnia nocka (Wersja 2012)", "Yugopolis & Maciej Maleńczuk", "3:02"),
    ("W ciemną noc", "Feel", "3:08"), ("Póki jesteś", "Maciej Silski", "3:30"), ("Love Story", "", ""),
    ("Tylko z Tobą chcę być sobą", "Łukasz Zagrobelny", "3:59"), ("Dni, których nie znamy", "Marek Grechuta", "4:54"),
    ("Motyle", "Lady Pank", "3:23"), ("Zabijasz mnie", "Mateusz Mijal", "3:38"), ("Księga przemian", "Wilki", "4:26"),
    ("Liczysz się tylko ty", "Wilki", "3:49"), ("Co powiemy naszym dzieciom", "Seweryn Krajewski", "4:10"),
    ("Zostańmy trochę dłużej", "Robert Barwiński", "5:43"), ("Ty jak nikt", "Wilki", "3:29"),
]
ON_WALL = {"Wenus, tu Mars", "Motyle", "Co powiemy naszym dzieciom"}
NOW = "Zostań ze mną"

# 每个乐队一个色，给小方块封面用（只是示意，真页面用 YouTube 的封面图）
HUE = {"Wilki": 8, "Feel": 205, "Lady Pank": 48, "Łukasz Zagrobelny": 290, "Yugopolis": 355, "Pin": 160,
       "Seweryn Krajewski": 245, "Mateusz Mijal": 30, "Platinum Purge": 20, "RH+": 15, "Marek Grechuta": 95}


def hue(artist):
    for k, v in HUE.items():
        if artist.startswith(k):
            return v
    return 215


def thumb(t):
    a = t[1]
    ini = ''.join(w[0] for w in a.replace('&', ' ').split()[:2]).upper() if a else '♪'
    return '<i class="th" style="--h:%d">%s</i>' % (hue(a), E(ini))


def row(t, n=None, cls='row'):
    name, artist, dur = t
    tag = '<em class="wall" title="唱片墙上有这首">墙</em>' if name in ON_WALL else ''
    now = ' is-now' if name == NOW else ''
    return ('<li class="%s%s">%s%s<span class="row__t"><b>%s</b>%s<small>%s</small></span><span class="row__d">%s</span></li>'
            % (cls, now, ('<span class="row__n">%02d</span>' % n) if n else '', thumb(t), E(name), tag, E(artist or '—'), E(dur)))


CSS = '''
:root{--bg:#eef3f8;--paper:#f8fafc;--ink:#1c2a44;--muted:#5d6b85;--accent:#3f73a8;--gold:#d9a441;--line:#c9d6e4;
 --pl-red:#d4213d;--pl-white:#fff;
 --disp:"EB Garamond",Georgia,"Noto Serif SC",serif;--body:"Noto Serif SC","Songti SC",Georgia,serif;--mono:"Special Elite","Courier New",monospace;}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#0f1727;--paper:#182236;--ink:#e6edf6;--muted:#93a3bd;--accent:#7fb0e6;--gold:#e2b45a;--line:#2b3a55;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#0f1727;--paper:#182236;--ink:#e6edf6;--muted:#93a3bd;--accent:#7fb0e6;--gold:#e2b45a;--line:#2b3a55;color-scheme:dark}
body{background:var(--bg);color:var(--ink);font-family:var(--body);line-height:1.8;font-size:16px;}
.wrap{max-width:46rem;margin:0 auto;padding-block:2rem 7rem;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));}
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

/* ---- 共用的小方块封面与曲目行 ---- */
.th{flex:none;width:2.6rem;height:2.6rem;border-radius:4px;display:grid;place-items:center;font-style:normal;font-family:var(--disp);font-size:.78rem;letter-spacing:.04em;
 color:#fff;background:linear-gradient(135deg,hsl(var(--h) 45% 48%),hsl(calc(var(--h) + 30) 55% 32%));}
.row{display:flex;align-items:center;gap:.7rem;padding:.5rem 0;border-bottom:1px solid var(--line);min-width:0;}
.row__n{font-family:var(--disp);color:var(--muted);font-size:.8rem;width:1.3rem;flex:none;font-variant-numeric:tabular-nums;}
.row__t{min-width:0;flex:1;display:flex;flex-direction:column;line-height:1.35;}
.row__t b{font-weight:600;font-size:.95rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.row__t small{color:var(--muted);font-size:.8rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.row__d{font-family:var(--disp);color:var(--muted);font-size:.85rem;font-variant-numeric:tabular-nums;flex:none;}
.wall{position:absolute;right:3.2rem;font-style:normal;font-size:.62rem;letter-spacing:.1em;color:var(--gold);border:1px solid var(--gold);border-radius:2px;padding:0 .3rem;line-height:1.5;}
.row{position:relative;}
.row.is-now b{color:var(--accent);}
.row.is-now .th::after{content:"▶";position:absolute;}
.mk{background:var(--paper);border:1px solid var(--line);border-radius:10px;padding:1rem;max-width:min(30rem,100%);min-width:0;box-sizing:border-box;}
.jcard>div{min-width:0;}
.wrap,.wrap *{box-sizing:border-box;}
.mk ol{list-style:none;margin:0;padding:0;}

/* ---- A 电台 ---- */
.radio__face{background:linear-gradient(180deg,#2a2f3a,#171b24);color:#f1e8d2;border-radius:10px;padding:1rem 1rem .9rem;position:relative;overflow:hidden;}
.radio__face::before{content:"";position:absolute;inset:0 0 auto;height:4px;background:linear-gradient(90deg,var(--pl-white) 50%,var(--pl-red) 50%);}
.radio__dial{position:relative;margin:.6rem 0 .8rem;height:2.6rem;border:1px solid rgba(255,255,255,.18);border-radius:4px;background:linear-gradient(180deg,rgba(255,255,255,.06),rgba(255,255,255,.02));
 display:flex;justify-content:space-between;align-items:flex-end;padding:0 .6rem .3rem;font-family:var(--disp);font-size:.72rem;letter-spacing:.08em;color:#cfc4a6;}
.radio__dial span{position:relative;}
.radio__dial span::before{content:"";position:absolute;left:50%;top:-1.1rem;height:.6rem;border-left:1px solid #8a8370;}
.radio__dial i{position:absolute;top:0;bottom:0;left:61%;border-left:2px solid var(--pl-red);box-shadow:0 0 8px var(--pl-red);}
.radio__name{font-family:var(--disp);font-size:1.5rem;letter-spacing:.18em;line-height:1.1;}
.radio__name small{display:block;letter-spacing:.04em;font-size:.78rem;color:#b9b09a;margin-top:.3rem;font-family:var(--body);}
.radio__now{margin-top:.8rem;font-size:.82rem;color:#f1e8d2;display:flex;gap:.5rem;align-items:center;}
.radio__now i{width:.5rem;height:.5rem;border-radius:50%;background:var(--pl-red);box-shadow:0 0 6px var(--pl-red);}
.radio__list{margin-top:.6rem;}
.radio .row__n{display:none;}

/* ---- B 磁带 J 卡 ---- */
.jcard{display:grid;grid-template-columns:1.6rem minmax(0,1fr);gap:0;padding:0;overflow:hidden;background:#f3ecd9;color:#2a241a;border-color:#d9cfb6;}
.j__spine{writing-mode:vertical-rl;transform:rotate(180deg);background:var(--pl-red);color:#fff;font-family:var(--mono);font-size:.68rem;letter-spacing:.14em;display:grid;place-items:center;padding:.6rem 0;}
.j__front{background:var(--pl-red);color:#fff;padding:1.4rem 1rem;position:relative;}
.j__front h3{margin:0;font-family:var(--disp);font-size:2.2rem;letter-spacing:.2em;text-align:center;font-weight:700;}
.j__front p{margin:.2rem 0 0;text-align:center;font-size:.72rem;letter-spacing:.14em;opacity:.9;}
.j__front .doodle{position:absolute;font-size:1rem;opacity:.7;}
.j__inside{padding:.8rem 1rem 1rem;font-family:var(--mono);font-size:.78rem;line-height:1.6;}
.j__inside h4{margin:.6rem 0 .2rem;font-size:.72rem;letter-spacing:.2em;border-bottom:1px dashed #b7ab8e;}
.j__inside ol{columns:1;}
.j__inside li{display:flex;gap:.4rem;border-bottom:1px dotted #d2c7ab;padding:.1rem 0;}
.j__inside li b{font-weight:400;flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.j__inside li i{font-style:normal;color:#7a6f57;}
.j__inside li em{font-style:normal;color:var(--pl-red);font-size:.66rem;}

/* ---- C 歌单长条 ---- */
.list__head{display:flex;gap:1rem;align-items:flex-end;margin-bottom:.6rem;}
.list__cover{flex:none;width:5.4rem;height:5.4rem;border-radius:8px;background:var(--pl-red);color:#fff;display:grid;place-items:center;font-family:var(--disp);font-weight:700;letter-spacing:.12em;font-size:1rem;box-shadow:0 6px 16px color-mix(in srgb,var(--pl-red) 35%,transparent);}
.list__head h3{margin:0;font-family:var(--disp);font-size:1.6rem;line-height:1.1;}
.list__head p{margin:.25rem 0 0;color:var(--muted);font-size:.82rem;}
.chips{display:flex;flex-wrap:wrap;gap:.35rem;margin:.6rem 0 .3rem;}
.chips span{font-size:.74rem;border:1px solid var(--line);border-radius:999px;padding:.05rem .55rem;color:var(--muted);}
.chips span b{color:var(--ink);font-weight:600;}
.ymlink{display:inline-flex;align-items:center;gap:.4rem;margin-top:.7rem;font-size:.8rem;color:var(--accent);border:1px solid var(--accent);border-radius:999px;padding:.15rem .7rem;}
'''


def mock_a():
    return ('<div class="mk radio"><div class="radio__face"><div class="radio__dial"><span>88</span><span>92</span><span>96</span><span>100</span><span>104</span><span>108</span><i></i></div>'
            '<div class="radio__name">POLSKI FM<small>冬璇的波兰电台 · 38 首 · 2 小时 20 分 · 2026-10-22 更新</small></div>'
            '<div class="radio__now"><i></i>正在播 · Zostań ze mną — Feel</div></div>'
            '<ol class="radio__list">%s<li class="row" style="justify-content:center;border:0;color:var(--muted);font-size:.8rem">… 还有 30 首，往下翻</li></ol></div>'
            % ''.join(row(t) for t in TRACKS[19:27]))


def mock_b():
    def li(i, t):
        return '<li><i>%s%d</i><b>%s — %s</b>%s<i>%s</i></li>' % ('A' if i < 19 else 'B', (i % 19) + 1, E(t[0]), E(t[1] or '—'),
                                                                 '<em>墙</em>' if t[0] in ON_WALL else '', E(t[2]))
    return ('<div class="mk jcard"><div class="j__spine">POLSKI · WINTER SUN · 2026</div><div>'
            '<div class="j__front"><span class="doodle" style="left:8%%;top:12%%">♪</span><span class="doodle" style="right:10%%;top:18%%">♫</span>'
            '<span class="doodle" style="left:14%%;bottom:14%%">♩</span><span class="doodle" style="right:16%%;bottom:10%%">♬</span>'
            '<h3>POLSKI</h3><p>38 UTWORÓW · 2 H 20 MIN</p></div>'
            '<div class="j__inside"><h4>SIDE A</h4><ol>%s</ol><h4>SIDE B</h4><ol>%s</ol></div></div></div>'
            % (''.join(li(i, t) for i, t in enumerate(TRACKS[:6])), ''.join(li(i, t) for i, t in enumerate(TRACKS[19:25], 19))))


def mock_c():
    return ('<div class="mk list"><div class="list__head"><div class="list__cover">POLSKI</div><div><h3>Polski</h3>'
            '<p>冬璇 WinterSun · 38 首 · 2 小时 20 分<br>2026-10-22 加了最后一首</p></div></div>'
            '<div class="chips"><span><b>Feel</b> 10</span><span><b>Lady Pank</b> 7</span><span><b>Wilki</b> 5</span><span><b>Łukasz Zagrobelny</b> 4</span><span><b>Yugopolis</b> 3</span><span>… 还有 8 组</span></div>'
            '<ol>%s</ol><a class="ymlink">▶ 去 YouTube Music 听整张</a></div>'
            % ''.join(row(t, i + 1) for i, t in enumerate(TRACKS[:9])))


def main(OUT, FORKS):
    fk_css, fk_html, fk_tail, nf = forks_mod.render(FORKS, 'playlist-pitch-2026-10-27')
    page = '''<meta charset="utf-8"><title>Polski 歌单页提案</title><meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=Noto+Serif+SC:wght@400;600&family=Special+Elite&display=swap" rel="stylesheet">
<style>%s%s</style><div class="wrap">
<header><p class="kicker">冬的歌单 · 新的一页 · 2026-10-27</p>
<h1>把你的 <em>Polski</em> 搬到博客上</h1>
<p class="lede">你那个歌单是公开的，所以这页可以<b>自己长</b>：你照旧在 YouTube Music 里往 Polski 扔歌，博客这边隔一阵去看一眼，新歌自动排进来，封面、歌名、乐队、时长都带着，你一首都不用发我。下面三版是它长什么样，挑一版；再挑个名字、挑个门。</p>
<ol class="how"><li><b>1</b>你把歌单的分享链接发我一次（点歌单右上角的 ⋮ → 分享）。</li>
<li><b>2</b>每首歌点一下就跳去 YouTube Music 播放；已经挂在唱片墙上的歌会打一枚小小的「墙」字标，点进去能看摘录和翻译。</li>
<li><b>3</b>想加第二个歌单（比如以后有「Polski · 慢歌」）也是同一套，再发我一个链接就行。</li></ol></header>

<section class="blk"><h2><small>岔路一</small>长什么样</h2>
<p class="note">三版都用同一批歌示意，封面小方块只是占位，真页面用每首歌自己的封面图。</p>

<div class="opt"><div class="opt__h"><span class="opt__k">A</span><span class="opt__name">一台波兰收音机</span><span class="opt__rec">我推荐</span></div>
<p class="opt__why"><b>页头是一台老收音机的面板：刻度盘、红色指针、顶上一道红白两色的细边（波兰国旗），台名 POLSKI FM。</b>下面是节目单，一首一行。「正在播」那一行是你上次听到的那首。整页是暗面板配米色字，白天夜里都一样，像一件真的东西摆在桌上。</p>
%s<p class="cap">↑ 最有「波兰」的味道；刻度盘以后还能做成按乐队拨台。</p></div>

<div class="opt"><div class="opt__h"><span class="opt__k">B</span><span class="opt__name">一张磁带的 J 卡</span></div>
<p class="opt__why"><b>整页排成磁带盒里那张折纸：左边一条书脊写着 POLSKI · 冬璇，红色封面，翻开是打字机字体的 A 面 / B 面曲目。</b>38 首对半分成两面。配 Archive 那台磁带机正好是一套。</p>
%s<p class="cap">↑ 最复古；缺点是站里已经有一台磁带机，再来一张磁带会有点像重复。</p></div>

<div class="opt"><div class="opt__h"><span class="opt__k">C</span><span class="opt__name">就像手机里那张歌单</span></div>
<p class="opt__why"><b>你做的那张红底 POLSKI 封面放左上，旁边是首数和时长，底下一排乐队小标签（Feel 10 · Lady Pank 7 · Wilki 5 …），然后就是一首一行。</b>最朴素，跟 YouTube Music 里看到的一样，打开不用适应。</p>
%s<p class="cap">↑ 最省心；乐队小标签点一下只看那个乐队的歌。</p></div>
</section>

%s
</div>%s''' % (CSS, fk_css, mock_a(), mock_b(), mock_c(), fk_html, fk_tail)
    open(OUT, 'w', encoding='utf-8').write(page)
    print('ok', len(page))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
