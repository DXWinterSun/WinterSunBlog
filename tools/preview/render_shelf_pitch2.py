# -*- coding: utf-8 -*-
"""藏品架卡面提案 · 第二轮（2026-10-18）：B / C 换上真正的小画精修，实物背面两版；第一轮收在页底。

    python3 shelf_pitch2.py 输出.html 岔路.json
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_shelf_pitch as r1
from shelf_art import ART, ART_CSS
import forks as forks_mod

E, CH, TYPES, ITEMS = r1.E, r1.CH, r1.TYPES, r1.ITEMS

CSS2 = r"""
/* ———————— 第二轮：小画 ———————— */
.win2{position:relative;overflow:hidden;background:color-mix(in srgb,var(--a) 26%,#fff)}
.win2 .art{position:absolute;inset:6% 10%;width:80%;height:88%}
/* B2 封面：整张一块淡色，小画占上半，名字印在画下面 */
.B2{grid-template-columns:repeat(auto-fill,minmax(min(200px,100%),1fr))}
.B2 .card{aspect-ratio:4/5;padding:0;background:color-mix(in srgb,var(--a) 24%,#fff);
  background-image:radial-gradient(rgba(255,255,255,.9) 1.1px,transparent 1.2px);background-size:22px 22px}
.B2 .frame{position:absolute;inset:6px;border:1px solid rgba(255,255,255,.7);border-radius:8px;pointer-events:none}
.B2 .inner{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;padding:12px 14px 12px}
.B2 .t-disc .inner{padding-left:26px}.B2 .t-book .inner,.B2 .t-program .inner{padding-left:24px;padding-right:18px}
.B2 .sticker{align-self:flex-start;transform:rotate(-3deg);background:#fff;border:1px dashed color-mix(in srgb,var(--a) 60%,var(--ink));
  font-family:var(--tw);font-size:10px;letter-spacing:1px;color:var(--soft);padding:3px 8px;border-radius:3px;box-shadow:1px 1px 0 rgba(20,33,46,.18);max-width:92%;line-height:1.5;position:relative;z-index:2}
.B2 .pic{width:64%;max-width:150px;aspect-ratio:1;margin:auto auto 0}
.B2 .title{font-family:var(--serif);font-weight:700;font-size:16.5px;line-height:1.35;color:var(--ink);margin:2px 0 0;text-align:center;text-wrap:balance}
.B2 .who{margin:7px 0 auto;font-size:11.5px;color:var(--soft);padding-right:14px}
.B2 .m-spine{width:16px}
.B2 .staple{position:absolute;left:5px;width:3px;height:14px;background:var(--ink);opacity:.5;border-radius:1px}
.B2 .t-goods{clip-path:polygon(0 18px,18px 0,calc(100% - 18px) 0,100% 18px,100% 100%,0 100%)}
.B2 .t-goods .frame{clip-path:polygon(0 14px,14px 0,calc(100% - 14px) 0,100% 14px,100% 100%,0 100%)}
.B2 .hole{position:absolute;left:50%;top:9px;width:11px;height:11px;margin-left:-5.5px;border-radius:50%;background:var(--bg);border:2px solid var(--edge);box-shadow:inset 0 0 0 2px #fff;z-index:3}
.B2 .t-goods .inner{padding-top:24px}
/* C2 集卡册：上面一扇窗放小画，下面白色名牌 */
.C2{grid-template-columns:repeat(auto-fill,minmax(min(160px,100%),1fr));gap:10px;row-gap:22px}
.C2 .card{aspect-ratio:5/7;display:flex;flex-direction:column;padding:0}
.C2 .win2{flex:0 0 56%;border-bottom:2px solid var(--edge)}
.C2 .win2 .no{position:absolute;left:9px;top:7px;font-family:var(--tw);font-size:10px;letter-spacing:1.5px;color:var(--ink);opacity:.65;z-index:2}
.C2 .win2 .ty{position:absolute;right:9px;top:7px;font-family:var(--tw);font-size:10px;letter-spacing:2px;color:var(--ink);opacity:.65;z-index:2}
.C2 .plate{flex:1;padding:8px 10px 8px;display:flex;flex-direction:column;background:#fff;min-width:0}
.C2 .title{font-family:var(--serif);font-weight:600;font-size:13px;line-height:1.4;margin:0 0 3px;color:var(--ink);display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.C2 .spec{font-family:var(--tw);font-size:9.5px;letter-spacing:.8px;color:var(--muted);line-height:1.6;margin:0;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.C2 .who{margin-top:auto;font-size:11px;padding-right:16px}
.C2 .who i{width:8px;height:8px}
/* 背面两版 */
.backs>div{display:flex;flex-direction:column;min-width:0}.backs .shelf{flex:none}.backs .card{height:auto}
.bk{min-height:300px;display:flex;flex-direction:column;padding:0;background:#fff}
.bk .head{display:flex;justify-content:space-between;align-items:center;padding:7px 14px;background:color-mix(in srgb,var(--a) 78%,var(--ink));color:#fff;
  font-family:var(--tw);font-size:10.5px;letter-spacing:2px;text-transform:uppercase}
.bk .body{flex:1;padding:12px 14px 10px;display:flex;flex-direction:column}
.bk .note{flex:1;margin:0;font-size:13.5px;line-height:1.9;color:var(--soft)}
.bk dl{margin:10px 0 0;padding:8px 0 0;border-top:1px solid var(--line);display:grid;grid-template-columns:auto 1fr;gap:3px 10px;
  font-family:var(--tw);font-size:10.5px;letter-spacing:.4px;color:var(--muted);line-height:1.7}
.bk dt{color:var(--ink);opacity:.75}
.bk dd{margin:0;display:flex;align-items:baseline;gap:6px;min-width:0}
.bk dd::before{content:"";flex:1;border-bottom:1px dotted rgba(20,33,46,.3);transform:translateY(-3px);min-width:10px;order:-1}
.bk dd span{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bk .foot{display:flex;align-items:flex-end;justify-content:space-between;gap:10px;margin-top:10px;padding-right:28px}
.bk .code{display:block;height:16px;width:44%;opacity:.55;
  background:repeating-linear-gradient(90deg,rgba(20,33,46,.75) 0 1px,transparent 1px 3px,rgba(20,33,46,.75) 3px 5px,transparent 5px 6px,rgba(20,33,46,.75) 6px 8px,transparent 8px 11px)}
.bk .tiny{font-family:var(--tw);font-size:9px;letter-spacing:2px;color:var(--muted)}
.bk2{min-height:300px;display:flex;flex-direction:column;padding:18px 18px 14px;background:#fffdf8}
.bk2 .q{font-family:var(--serif);font-style:italic;font-size:44px;line-height:.6;color:color-mix(in srgb,var(--a) 70%,var(--ink));opacity:.55;margin:4px 0 10px}
.bk2 .note{flex:1;margin:0;font-size:14px;line-height:1.95;color:var(--soft)}
.bk2 .line{margin-top:14px;padding-top:8px;border-top:1px solid var(--line);font-family:var(--tw);font-size:10.5px;letter-spacing:.6px;color:var(--muted);padding-right:28px;line-height:1.7}
.bk2 .line b{font-weight:400;color:var(--ink)}
details.r1{margin-top:3.4rem;border-top:1px dashed var(--line);padding-top:1.2rem}
details.r1 summary{cursor:pointer;font-family:var(--serif);font-weight:700;font-size:1.05rem;color:var(--muted)}
details.r1 summary small{font-family:var(--tw);font-size:.66rem;letter-spacing:.2em;margin-left:.6rem;font-weight:400}
details.r1 .opt{margin-top:1.6rem}
@media(max-width:620px){
  .B2{grid-template-columns:repeat(2,1fr);gap:9px;row-gap:22px}.B2 .title{font-size:14.5px}.B2 .pic{width:66%}
  .C2{grid-template-columns:repeat(2,1fr);gap:9px;row-gap:22px}
}
"""

def who(it, cls='who'):
    c = CH[it['ch']]
    return '<span class="%s"><i></i>%s · %s</span>' % (cls, E(c['name']), c['year'])

def cardB2(it):
    c = CH[it['ch']]; t = it['type']
    med = r1.medium(t, '<span>%s</span>' % E(it['spec'].split(' · ')[0])) if t == 'disc' else ('' if t == 'ost' else r1.medium(t))
    extra = ''
    if t == 'program': extra = '<i class="staple" style="top:26%"></i><i class="staple" style="top:62%"></i>'
    if t == 'goods': extra = '<i class="hole"></i>'
    return ('<div class="shelf"><div class="card t-%s" style="--a:%s">%s%s<i class="frame"></i>'
            '<div class="inner"><span class="sticker">%s</span><div class="pic">%s</div><p class="title">%s</p>%s</div>%s</div></div>'
            % (t, c['a'], med, extra, E(it['spec']), ART[t], E(it['name']), who(it), r1.dog(it)))

def cardC2(it):
    em, lab = TYPES[it['type']]; c = CH[it['ch']]
    return ('<div class="shelf"><div class="card t-%s" style="--a:%s">'
            '<div class="win2"><span class="no">No. %03d</span><span class="ty">%s</span>%s</div>'
            '<div class="plate"><p class="title">%s</p><p class="spec">%s</p>%s</div>%s</div></div>'
            % (it['type'], c['a'], it['n'], lab, ART[it['type']], E(it['name']), E(it['spec']), who(it), r1.dog(it)))

trent = ITEMS[3]
def back_a():
    return ('<div class="shelf"><div class="card bk" style="--a:%s"><div class="head"><span>碟片 · 背面</span><span>No. 082</span></div>'
            '<div class="body"><p class="note">%s</p>'
            '<dl><dt>规格</dt><dd><span>DVD · 澳版 · 四区 · 二手</span></dd><dt>谁的</dt><dd><span>Trent · 《割草叔叔》 · 1997</span></dd>'
            '<dt>入手</dt><dd><span>2026-10-17</span></dd><dt>NAS</dt><dd><span>还没进</span></dd></dl>'
            '<div class="foot"><i class="code"></i><span class="tiny">WINTER SUN · SHELF</span></div></div><span class="turn">↻</span></div></div>'
            % (CH['trent']['a'], E(trent['note'])))
def back_b():
    return ('<div class="shelf"><div class="card bk2" style="--a:%s"><div class="q">“</div><p class="note">%s</p>'
            '<p class="line"><b>Trent</b> · 《割草叔叔》1997<br>DVD · 澳版 · 四区 · 二手 · 入手 2026-10-17</p><span class="turn">↻</span></div></div>'
            % (CH['trent']['a'], E(trent['note'])))

def main(OUT, FORKS):
    fk_css, fk_html, fk_tail, nf = forks_mod.render(FORKS, 'shelf-card-pitch-r2-2026-10-18')
    page = """<meta charset="utf-8"><title>藏品架卡面提案</title><meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,700&family=Noto+Serif+SC:wght@400;600&family=Special+Elite&family=Ma+Shan+Zheng&display=swap" rel="stylesheet">
<style>%s%s%s%s</style><div class="wrap">
<header class="top"><p class="kicker">藏品架 · 卡面重做 · 第二轮 · 2026-10-18</p>
<h1>给每种东西画一张<em>小画</em></h1>
<p class="lede">上一轮 B、C 粗糙，病根是卡上没有画，只好拿一个大字母、一个 emoji 顶着。这回照 Winter's 封面和 Sam 页那套画风，给碟片、原声带、卡牌、书刊、场刊、周边各画了一张，颜色跟着每个角色走；B、C 都换上了，实物背面也重新排过。第一轮的三版收在页底，想对照可以展开。</p></header>

<section class="blk"><h2><small>岔路一</small>正面用哪一版</h2>
<p class="note">同样六件东西。荷兰明信片仍当作没写字，看折角怎么区分。</p>

<div class="opt"><div class="opt__h"><span class="opt__k">A</span><span class="opt__name">封面 · 小画版</span></div>
<p class="opt__why"><b>整张是一块他的颜色，小画在上，名字印在画下面。</b>去掉了上一轮那个大字母和底下那道深色带，加了一圈细白框像封面的边；规格还是一张斜贴的白标签。碟片有盒脊、场刊有订书钉、公仔是挂牌。</p>
<div class="grid B2">%s</div>
<p class="cap">↑ 一眼先看见画，再看见名字；整张卡都是他的颜色。</p></div>

<div class="opt"><div class="opt__h"><span class="opt__k">B</span><span class="opt__name">集卡册 · 小画版</span><span class="opt__rec">我推荐</span></div>
<p class="opt__why"><b>上面一扇窗放小画，下面白色名牌。</b>窗是他的颜色，画大一些、占满窗；名牌上名字、规格、谁，左上角编号。统一竖版，手机两张一行，电脑四张。</p>
<div class="grid C2">%s</div>
<p class="cap">↑ 最像一本卡册，画和字分开，各自都干净。</p></div>
</section>

<section class="blk"><h2><small>岔路二</small>实物背面怎么排</h2>
<p class="note">手写便签拿掉了。两版都是整段话完整显示，同一张《割草叔叔》。</p>
<div class="backs">
<div><div class="opt__h" style="margin-bottom:.8rem"><span class="opt__k">A</span><span class="opt__name">产品背面</span><span class="opt__rec">我推荐</span></div>%s
<p class="cap">↑ 顶上一道他颜色的条，话在中间，底下规格 / 谁的 / 入手 / NAS 排成一张小表，再一道条码。像真的碟盒背面。</p></div>
<div><div class="opt__h" style="margin-bottom:.8rem"><span class="opt__k">B</span><span class="opt__name">只留那段话</span></div>%s
<p class="cap">↑ 什么都不加，一个大引号起头，话排在米色纸上，最底下一行小字说清是谁、什么版本、哪天。</p></div>
</div></section>

%s

<details class="r1"><summary>第一轮的三版<small>2026-10-18 · 展开对照</small></summary>
<div class="opt"><div class="opt__h"><span class="opt__k">1</span><span class="opt__name">展签</span></div><div class="grid A">%s</div></div>
<div class="opt"><div class="opt__h"><span class="opt__k">2</span><span class="opt__name">封面 · 字母版</span></div><div class="grid B">%s</div></div>
<div class="opt"><div class="opt__h"><span class="opt__k">3</span><span class="opt__name">集卡册 · emoji 版</span></div><div class="grid C">%s</div></div>
</details>
</div>%s""" % (
        r1.CSS, ART_CSS, CSS2, fk_css,
        ''.join(cardB2(i) for i in ITEMS), ''.join(cardC2(i) for i in ITEMS),
        back_a(), back_b(), fk_html,
        ''.join(r1.cardA(i) for i in ITEMS), ''.join(r1.cardB(i) for i in ITEMS), ''.join(r1.cardC(i) for i in ITEMS),
        fk_tail)
    open(OUT, 'w', encoding='utf-8').write(page)
    print('ok', len(page))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
