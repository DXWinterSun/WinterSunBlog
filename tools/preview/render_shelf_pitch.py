# -*- coding: utf-8 -*-
"""藏品架卡面重做提案页：三版正面 + 两版背面，页底可点选复制。"""
import json, sys, html
sys.path.insert(0, '/Users/winterzhang/GitHub/WinterSunBlog/tools/preview')
import forks as forks_mod

E = lambda s: html.escape(s or '', quote=True)

CH = {
  'johnmoon': dict(name='John Moon', film='《致命一击》', year='2013', a='#8fa0b0', mono='J'),
  'zaphod':   dict(name='Zaphod Beeblebrox', film='《银河系漫游指南》', year='2005', a='#d4a82a', mono='Z'),
  'victor':   dict(name='Victor Mancini', film='《窒色》', year='2008', a='#d2a24a', mono='V'),
  'trent':    dict(name='Trent', film='《割草叔叔》', year='1997', a='#79a7bd', mono='T'),
  'sambell':  dict(name='Sam Bell', film='《月球》', year='2009', a='#7eb0d5', mono='S'),
  'guy':      dict(name='Guy Fleegman', film='《惊爆银河系》', year='1999', a='#43b3bf', mono='G'),
}
TYPES = {
  'disc': ('📀', '碟片'), 'ost': ('🎵', '原声带'), 'card': ('🃏', '卡牌'),
  'goods': ('🧸', '周边'), 'program': ('📔', '场刊'), 'book': ('📖', '书刊'),
}
ITEMS = [
  dict(n=86, name='《致命一击》原声带', type='ost', spec='CD · 全新', ch='johnmoon', date='2026-10-18',
       note='Atli Örvarsson 作曲，瑞典 MovieScore Media 和马耳他 Kronos 唱片合出。包裹从马耳他寄来，寄件人姓 Borg，跟唱片背面署名的出品人同姓。里面有一组《John Moon 变奏曲》，三个乐章：开枪、深夜来电、对决'),
  dict(n=85, name='《银河系漫游指南》明信片 · 荷兰版', type='card', spec='荷兰 Boomerang 免费明信片', ch='zaphod', date='2026-10-18',
       note='荷兰语写着“想看看我的飞船吗？”，底下小字：Zaphod（左）是银河系总统，Humma Kavula（右）是星际传教士……'),
  dict(n=83, name='《窒色》原著', type='book', spec='平装 · Anchor 2008 · 电影封面', ch='victor', date='2026-10-17',
       note='红底黑剪影，好漂亮呜呜呜。背面印着电影的演职员表，第一个名字就是他。舍不得看，也舍不得做标记🥺'),
  dict(n=82, name='《割草叔叔》', type='disc', spec='DVD · 澳版 · 四区 · 二手', ch='trent', date='2026-10-17',
       note='战损版🥲 南澳一家录像带出租店退下来的，碟面上还贴着店里的出租标签。一路从澳洲寄过来，盒子顶端摔裂了，碟面也有划痕。盒子是我自己用 502 粘好的，没换，换了就不是它了'),
  dict(n=31, name='《月球》', type='program', spec='场刊', ch='sambell', date='2026-07-17',
       note='第一本场刊，美到不行🥺'),
  dict(n=70, name='Funko Pop! Guy', type='goods', spec='Funko 公仔 · 1530 · 官网独家款', ch='guy', date='2026-10-09',
       note='皱着眉、八字小胡子，抱着他的外星枪。拆出来单独摆，这样才是我的 Guy。'),
]
NO_NOTE = {85}   # 让其中一张没字，看看折角怎么区分（荷兰明信片当作没写）

CSS = r"""
:root{--bg:#eff6fb;--paper:#fff;--ink:#14212e;--text:#14212e;--soft:#3a4c60;--muted:#7c8fa2;--faint:#a8b9c8;
  --accent:#2c80a9;--gold:#c1892f;--line:rgba(20,33,46,.14);
  --serif:'Playfair Display','Noto Serif SC','Songti SC',serif;
  --cn:'Noto Serif SC','Songti SC',serif;--tw:'Special Elite','Courier New',monospace;--hand:'Ma Shan Zheng','Noto Serif SC',cursive;}
*{box-sizing:border-box}
html{background:var(--bg)}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--cn);font-size:16px;line-height:1.85;-webkit-font-smoothing:antialiased;
  background-image:radial-gradient(rgba(20,33,46,.07) 1px,transparent 1px);background-size:18px 18px;}
.wrap{max-width:46rem;margin:0 auto;padding-block:0 7rem;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
header.top{padding:3rem 0 1.4rem}
.kicker{font-family:var(--tw);font-size:.7rem;letter-spacing:.22em;text-transform:uppercase;color:var(--accent);margin:0 0 .8rem}
h1{font-family:var(--serif);font-weight:700;font-size:clamp(1.8rem,6.6vw,2.6rem);line-height:1.15;margin:0;text-wrap:balance}
h1 em{font-style:italic;color:var(--accent)}
.lede{margin:1rem 0 0;color:var(--soft);font-size:.98rem}
section.blk{margin-top:3.2rem}
.blk>h2{font-family:var(--serif);font-size:1.25rem;font-weight:700;margin:0 0 .3rem;display:flex;gap:.6rem;align-items:baseline}
.blk>h2 small{font-family:var(--tw);font-size:.68rem;letter-spacing:.2em;color:var(--accent);text-transform:uppercase;font-weight:400}
.blk>p.note{margin:0 0 1.2rem;color:var(--muted);font-size:.9rem}
ul.fixed{margin:.4rem 0 0;padding-left:1.2em;color:var(--soft);font-size:.95rem}
ul.fixed li{margin:.25em 0}
ul.fixed b{color:var(--ink);font-weight:600}
.opt{margin-top:2.4rem;padding-top:1.4rem;border-top:1px dashed var(--line)}
.opt__h{display:flex;align-items:baseline;gap:.7rem;margin:0 0 .25rem}
.opt__k{font-family:var(--tw);font-size:1.1rem;color:#fff;background:var(--accent);width:1.9em;height:1.9em;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;flex:none;font-size:.9rem}
.opt__name{font-family:var(--serif);font-size:1.15rem;font-weight:700}
.opt__rec{font-family:var(--tw);font-size:.62rem;letter-spacing:.15em;color:var(--gold);border:1px solid var(--gold);border-radius:999px;padding:.1em .6em;margin-left:.2rem}
.opt__why{margin:0 0 1.1rem;color:var(--soft);font-size:.92rem}
.opt__why b{font-weight:600;color:var(--ink)}
.cap{margin:.9rem 0 0;color:var(--muted);font-size:.82rem;font-family:var(--tw);letter-spacing:.06em}

/* —— 卡片公共底子（糖纸粗描边 + 硬影，跟现在一样，不动） —— */
.grid{display:grid;gap:12px;row-gap:24px}
.card{--edge:color-mix(in srgb,var(--a) 42%,var(--ink));--shade:color-mix(in srgb,var(--a) 72%,var(--ink));
  position:relative;border:2px solid var(--edge);border-radius:12px;box-shadow:4px 4px 0 var(--shade);
  background:linear-gradient(160deg,color-mix(in srgb,var(--a) 22%,#fff),#fff 72%);overflow:hidden;text-align:left}
.card::after{/* 架板 */content:"";position:absolute;}
.shelf{position:relative}
.shelf::after{content:"";position:absolute;left:-6px;right:-6px;bottom:-13px;height:12px;border-radius:0 0 4px 4px;
  background:repeating-linear-gradient(97deg,rgba(20,33,46,.05) 0 3px,transparent 3px 9px,rgba(20,33,46,.08) 9px 11px,transparent 11px 21px),
  linear-gradient(180deg,color-mix(in srgb,var(--accent) 34%,var(--bg)) 0 2px,color-mix(in srgb,var(--accent) 22%,var(--bg)) 2px 62%,color-mix(in srgb,var(--ink) 34%,var(--bg)) 62% 100%);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.22),inset 0 -1px 0 rgba(0,0,0,.35),0 4px 9px rgba(0,0,0,.22)}
.shelf>.card{height:100%}
/* 折角：有字的卡右下角折起来一角，露出背面的纸 */
.dog{position:absolute;right:-2px;bottom:-2px;width:26px;height:26px;z-index:3;
  background:linear-gradient(225deg,var(--bg) 0 50%,color-mix(in srgb,var(--a) 40%,#fff) 50% 52%,#fff 52%);
  border-top-left-radius:3px;box-shadow:-2px -2px 4px rgba(20,33,46,.16);}
.dog::before{content:"";position:absolute;left:0;top:0;width:100%;height:100%;
  background:linear-gradient(225deg,transparent 0 50%,var(--edge) 50% calc(50% + 1.5px),transparent calc(50% + 1.5px))}
.tw{font-family:var(--tw)}
.who{display:inline-flex;align-items:center;gap:6px;font-size:12.5px;color:var(--ink);letter-spacing:.3px}
.who i{width:10px;height:10px;border-radius:50%;background:var(--a);flex:none;border:1px solid rgba(20,33,46,.25)}
.badge{font-size:13px}

/* 媒介记号（三版共用的那几笔） */
.m-spine{position:absolute;left:0;top:0;bottom:0;width:14px;border-right:2px solid var(--edge);
  background:repeating-linear-gradient(180deg,rgba(20,33,46,.10) 0 2px,transparent 2px 7px),linear-gradient(180deg,color-mix(in srgb,var(--a) 55%,transparent),color-mix(in srgb,var(--a) 22%,transparent))}
.m-disc{position:absolute;right:-30px;bottom:-30px;width:96px;height:96px;border-radius:50%;border:2px solid var(--edge);
  background:repeating-radial-gradient(circle,rgba(20,33,46,.13) 0 1px,transparent 1px 5px),radial-gradient(circle,color-mix(in srgb,var(--a) 60%,transparent) 0 14%,color-mix(in srgb,var(--a) 18%,transparent) 15%)}
.m-disc::after{content:"";position:absolute;left:50%;top:50%;width:11px;height:11px;margin:-5.5px 0 0 -5.5px;border-radius:50%;background:#fff;border:1px solid var(--edge)}
.m-frame{position:absolute;inset:5px;border-radius:9px;border:1px solid rgba(20,33,46,.3);pointer-events:none}
.m-holo{position:absolute;top:-34px;right:-34px;width:96px;height:96px;border-radius:50%;opacity:.32;filter:blur(3px);
  background:conic-gradient(from 200deg,#ff9db0,#ffe08a,#a8e6cf,#a0c4ff,#d3b4ff,#ff9db0)}
.m-pages{position:absolute;right:0;top:0;bottom:0;width:10px;border-left:1px solid rgba(20,33,46,.22);
  background:repeating-linear-gradient(90deg,rgba(20,33,46,.16) 0 1px,transparent 1px 3px)}
.m-bind{position:absolute;left:0;top:0;bottom:0;width:11px;border-right:1px solid rgba(20,33,46,.26);
  background:linear-gradient(90deg,color-mix(in srgb,var(--a) 38%,transparent) 0 4px,transparent 4px 7px,color-mix(in srgb,var(--a) 22%,transparent) 7px 11px)}
.m-stripe{position:absolute;left:0;right:0;bottom:0;height:9px;border-top:2px solid var(--edge);
  background:repeating-linear-gradient(45deg,color-mix(in srgb,var(--a) 70%,transparent) 0 7px,transparent 7px 14px)}

/* ———————— A 展签 ———————— */
.A{grid-template-columns:repeat(auto-fill,minmax(min(215px,100%),1fr))}
.A .card{min-height:168px;padding:13px 15px 12px;display:flex;flex-direction:column}
.A .card.t-disc{padding-left:27px}.A .card.t-book,.A .card.t-program{padding-left:23px;padding-right:19px}
.A .top{display:flex;align-items:center;gap:7px;font-family:var(--tw);font-size:11px;letter-spacing:2px;text-transform:uppercase;color:color-mix(in srgb,var(--a) 62%,var(--ink))}
.A .top .em{font-size:17px;letter-spacing:0}
.A .top .badge{margin-left:auto}
.A .title{font-family:var(--serif);font-weight:600;font-size:16px;line-height:1.42;margin:9px 0 12px;color:var(--ink)}
.A .rule{height:1px;background:var(--line);margin:auto 0 8px}
.A .spec{font-family:var(--tw);font-size:11px;letter-spacing:1.2px;color:var(--soft);line-height:1.8;margin:0}
.A .foot{display:flex;flex-direction:column;align-items:flex-start;gap:1px;margin-top:5px;padding-right:18px}
.A .date{font-family:var(--tw);font-size:10.5px;letter-spacing:1.5px;color:var(--muted);white-space:nowrap}

/* ———————— B 封面 ———————— */
.B{grid-template-columns:repeat(auto-fill,minmax(min(200px,100%),1fr))}
.B .card{aspect-ratio:4/5;padding:0;background:linear-gradient(165deg,color-mix(in srgb,var(--a) 62%,#fff),color-mix(in srgb,var(--a) 28%,#fff) 70%,color-mix(in srgb,var(--a) 40%,#fff))}
.B .mono{position:absolute;left:50%;top:44%;transform:translate(-50%,-50%);font-family:var(--serif);font-style:italic;font-weight:700;
  font-size:150px;line-height:1;color:color-mix(in srgb,var(--a) 70%,var(--ink));opacity:.16;pointer-events:none;user-select:none}
.B .inner{position:absolute;inset:0;display:flex;flex-direction:column;padding:13px 14px 0}
.B .t-disc .inner{padding-left:26px}.B .t-book .inner,.B .t-program .inner{padding-left:24px;padding-right:18px}
.B .sticker{align-self:flex-start;transform:rotate(-3deg);background:#fff;border:1px dashed color-mix(in srgb,var(--a) 60%,var(--ink));
  font-family:var(--tw);font-size:10px;letter-spacing:1px;color:var(--soft);padding:3px 8px;border-radius:3px;box-shadow:1px 1px 0 rgba(20,33,46,.18);max-width:92%;line-height:1.5}
.B .title{font-family:var(--serif);font-weight:700;font-size:18px;line-height:1.35;color:var(--ink);margin:auto 0;text-align:center;padding:0 4px;
  text-shadow:0 1px 0 rgba(255,255,255,.6)}
.B .t-book .title{border-top:1px solid color-mix(in srgb,var(--a) 70%,var(--ink));border-bottom:1px solid color-mix(in srgb,var(--a) 70%,var(--ink));padding:10px 4px;
  box-shadow:0 3px 0 -2px color-mix(in srgb,var(--a) 70%,var(--ink)),0 -3px 0 -2px color-mix(in srgb,var(--a) 70%,var(--ink))}
.B .band{margin:0 -14px;padding:7px 14px 8px;background:color-mix(in srgb,var(--a) 78%,var(--ink));color:#fff;display:flex;align-items:center;gap:8px;
  font-size:12px;letter-spacing:.4px}
.B .t-disc .band{margin-left:-26px;padding-left:26px}.B .t-book .band,.B .t-program .band{margin-left:-24px;margin-right:-18px;padding-left:24px}
.B .band .em{font-size:15px}.B .band .yr{margin-left:auto;font-family:var(--tw);font-size:10.5px;opacity:.85;letter-spacing:1.5px;padding-right:14px}
.B .m-spine{width:16px}
.B .m-spine span{position:absolute;left:0;top:10px;width:16px;writing-mode:vertical-rl;font-family:var(--tw);font-size:9px;letter-spacing:2px;color:var(--ink);opacity:.7}
.B .m-disc{right:-38px;bottom:34px;width:110px;height:110px}
.B .staple{position:absolute;left:5px;width:3px;height:14px;background:var(--ink);opacity:.55;border-radius:1px}
.B .t-goods{clip-path:polygon(0 18px,18px 0,calc(100% - 18px) 0,100% 18px,100% 100%,0 100%)}
.B .hole{position:absolute;left:50%;top:9px;width:11px;height:11px;margin-left:-5.5px;border-radius:50%;background:var(--bg);border:2px solid var(--edge);box-shadow:inset 0 0 0 2px #fff}
.B .t-goods .inner{padding-top:26px}

/* ———————— C 集卡册 ———————— */
.C{grid-template-columns:repeat(auto-fill,minmax(min(160px,100%),1fr));gap:10px;row-gap:22px}
.C .card{aspect-ratio:5/7;display:flex;flex-direction:column;padding:0;border-radius:12px}
.C .win{position:relative;flex:0 0 57%;background:linear-gradient(160deg,color-mix(in srgb,var(--a) 62%,#fff),color-mix(in srgb,var(--a) 34%,#fff));
  border-bottom:2px solid var(--edge);display:flex;align-items:center;justify-content:center;overflow:hidden}
.C .win::before{content:"";position:absolute;inset:0;background:repeating-linear-gradient(45deg,rgba(255,255,255,.14) 0 6px,transparent 6px 12px),repeating-linear-gradient(-45deg,rgba(255,255,255,.1) 0 6px,transparent 6px 12px)}
.C .win .em{font-size:46px;line-height:1;position:relative;filter:drop-shadow(2px 3px 0 rgba(20,33,46,.18))}
.C .win .no{position:absolute;left:9px;top:7px;font-family:var(--tw);font-size:10px;letter-spacing:1.5px;color:var(--ink);opacity:.7}
.C .win .ty{position:absolute;right:9px;top:7px;font-family:var(--tw);font-size:10px;letter-spacing:2px;color:var(--ink);opacity:.7}
.C .win .badge{position:absolute;right:8px;bottom:6px}
.C .plate{flex:1;padding:8px 10px 8px;display:flex;flex-direction:column;background:#fff}
.C .title{font-family:var(--serif);font-weight:600;font-size:13px;line-height:1.4;margin:0 0 4px;color:var(--ink);display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.C .spec{font-family:var(--tw);font-size:9.5px;letter-spacing:.8px;color:var(--muted);line-height:1.6;margin:0;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.C .who{margin-top:auto;font-size:11px;padding-right:16px}
.C .who i{width:8px;height:8px}
.C .t-card .win .m-holo{top:-30px;right:-30px}

/* ———————— 背面两版 ———————— */
.backs{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(250px,100%),1fr));gap:22px;row-gap:28px}
.back{min-height:300px;display:flex;flex-direction:column;padding:14px 16px 13px}
.back .lab{font-family:var(--tw);font-size:11px;letter-spacing:2px;text-transform:uppercase;color:var(--muted);margin:0 0 8px;display:flex;justify-content:space-between}
.back .lab b{font-weight:400;color:color-mix(in srgb,var(--a) 62%,var(--ink))}
.back .note{flex:1;margin:0;font-size:13.5px;line-height:1.9;color:var(--soft)}
.back .meta{margin-top:10px;font-family:var(--tw);font-size:10.5px;letter-spacing:.4px;line-height:1.8;color:var(--muted)}
.back .code{display:block;height:15px;margin-top:8px;width:60%;opacity:.5;
  background:repeating-linear-gradient(90deg,rgba(20,33,46,.75) 0 1px,transparent 1px 3px,rgba(20,33,46,.75) 3px 5px,transparent 5px 6px,rgba(20,33,46,.75) 6px 8px,transparent 8px 11px)}
.back.hand{background:#fffdf6;background-image:repeating-linear-gradient(180deg,transparent 0 27px,rgba(44,128,169,.22) 27px 28px);background-position:0 46px;padding-top:46px}
.back.hand .tape{position:absolute;left:50%;top:-8px;width:84px;height:24px;margin-left:-42px;transform:rotate(-2deg);
  background:color-mix(in srgb,var(--a) 45%,#fff);opacity:.85;border-left:1px dashed rgba(255,255,255,.8);border-right:1px dashed rgba(255,255,255,.8)}
.back.hand .lab{position:absolute;left:16px;top:14px;right:16px}
.back.hand .note{font-family:var(--hand);font-size:19px;line-height:28px;color:#243445;margin-top:-1px}
.back.hand .stamp{align-self:flex-end;margin-top:10px;transform:rotate(-6deg);border:2px solid color-mix(in srgb,var(--a) 70%,var(--ink));color:color-mix(in srgb,var(--a) 70%,var(--ink));
  border-radius:4px;padding:1px 8px;font-family:var(--tw);font-size:10.5px;letter-spacing:2px;opacity:.75}
.turn{position:absolute;right:7px;bottom:7px;width:24px;height:24px;border-radius:50%;border:2px solid var(--edge);background:color-mix(in srgb,var(--a) 22%,#fff);
  display:flex;align-items:center;justify-content:center;font-size:12px;color:var(--ink);opacity:.75;z-index:4}
@media(max-width:620px){
  .A{grid-template-columns:repeat(2,1fr);gap:9px;row-gap:22px}
  .A .card{padding:11px 11px 10px;min-height:150px}.A .card.t-disc{padding-left:24px}.A .card.t-book,.A .card.t-program{padding-left:20px;padding-right:16px}
  .A .title{font-size:14.5px}
  .B{grid-template-columns:repeat(2,1fr);gap:9px;row-gap:22px}.B .title{font-size:16px}.B .mono{font-size:120px}.B .band{font-size:11.5px;padding-top:6px;padding-bottom:7px}.B .band .ty{display:none}.B .m-disc{right:-46px;bottom:42px;width:100px;height:100px}.B .t-ost .title{padding-right:30px}
  .C{grid-template-columns:repeat(2,1fr);gap:9px;row-gap:22px}
}
"""

def medium(t, extra=''):
    if t == 'disc': return '<i class="m-spine">%s</i>' % extra
    if t == 'ost': return '<i class="m-disc"></i>'
    if t == 'card': return '<i class="m-frame"></i><i class="m-holo"></i>'
    if t in ('book', 'program'): return '<i class="m-pages"></i><i class="m-bind"></i>'
    if t == 'goods': return '<i class="m-stripe"></i>'
    return ''

def dog(it):
    return '' if it['n'] in NO_NOTE else '<i class="dog" title="背面有字"></i>'

def who(it, cls='who'):
    c = CH[it['ch']]
    return '<span class="%s"><i></i>%s · %s</span>' % (cls, E(c['name']), c['year'])

def cardA(it):
    em, lab = TYPES[it['type']]
    return ('<div class="shelf"><div class="card t-%s" style="--a:%s">%s'
            '<div class="top"><span class="em">%s</span>%s<span class="badge">%s</span></div>'
            '<p class="title">%s</p><div class="rule"></div><p class="spec">%s</p>'
            '<div class="foot">%s<span class="date">%s</span></div>%s</div></div>'
            % (it['type'], CH[it['ch']]['a'], medium(it['type']), em, lab,
               '📡' if it.get('nas') else '', E(it['name']), E(it['spec']), who(it), it['date'], dog(it)))

def cardB(it):
    em, lab = TYPES[it['type']]
    c = CH[it['ch']]
    t = it['type']
    med = medium(t, '<span>%s</span>' % E(it['spec'].split(' · ')[0]))
    extra = ''
    if t == 'program': extra = '<i class="staple" style="top:26%"></i><i class="staple" style="top:62%"></i>'
    if t == 'goods': extra = '<i class="hole"></i>'
    return ('<div class="shelf"><div class="card t-%s" style="--a:%s">%s%s<span class="mono">%s</span>'
            '<div class="inner"><span class="sticker">%s</span><p class="title">%s</p>'
            '<div class="band"><span class="em">%s</span><span class="ty">%s · </span>%s<span class="yr">%s</span></div></div>%s</div></div>'
            % (t, c['a'], med, extra, c['mono'], E(it['spec']), E(it['name']), em, lab, E(c['name']), c['year'], dog(it)))

def cardC(it):
    em, lab = TYPES[it['type']]
    c = CH[it['ch']]
    return ('<div class="shelf"><div class="card t-%s" style="--a:%s">'
            '<div class="win">%s<span class="no">No. %03d</span><span class="ty">%s</span><span class="em">%s</span></div>'
            '<div class="plate"><p class="title">%s</p><p class="spec">%s</p>%s</div>%s</div></div>'
            % (it['type'], c['a'], '<i class="m-holo"></i>' if it['type'] == 'card' else '', it['n'], lab, em,
               E(it['name']), E(it['spec']), who(it), dog(it)))

trent = ITEMS[3]
def back1():
    return ('<div class="shelf"><div class="card back" style="--a:%s"><i class="m-spine"></i><div style="padding-left:14px;display:flex;flex-direction:column;height:100%%">'
            '<p class="lab"><b>碟片 · 背面</b><span>No. 082</span></p><p class="note">%s</p>'
            '<p class="meta">DVD · 澳版 · 四区 · 二手<br>Trent · 《割草叔叔》 · 1997<br>入手于 2026-10-17 · 还没进 NAS</p>'
            '<i class="code"></i></div><span class="turn">↻</span></div></div>' % (CH['trent']['a'], E(trent['note'])))
def back2():
    return ('<div class="shelf"><div class="card back hand" style="--a:%s"><i class="tape"></i>'
            '<p class="lab"><b>《割草叔叔》</b><span>No. 082</span></p><p class="note">%s</p>'
            '<span class="stamp">入手 2026 · 10 · 17</span><span class="turn">↻</span></div></div>' % (CH['trent']['a'], E(trent['note'])))

def main(OUT, FORKS):
    fk_css, fk_html, fk_tail, nf = forks_mod.render(FORKS, 'shelf-card-pitch-2026-10-18')
    
    page = """<title>藏品架卡面提案</title><meta name="claude:viewport-fit-sides" content="cover">
    <link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,700&family=Noto+Serif+SC:wght@400;600&family=Special+Elite&family=Ma+Shan+Zheng&display=swap" rel="stylesheet">
    <style>%s%s</style><div class="wrap">
    <header class="top"><p class="kicker">藏品架 · 卡面重做 · 2026-10-18</p>
    <h1>碎碎念翻到背面，<em>正面还给东西本身</em></h1>
    <p class="lede">现在一张卡上什么都有：名字、规格、角色、一大段话、日期，像一页说明书。你说得对，那段话该在背面。下面是三版正面、两版背面，都是用你架上真的东西画的；挑完页底复制给我就行。</p></header>
    
    <section class="blk"><h2><small>先定下的</small>三版都一样的几件事</h2>
    <ul class="fixed">
    <li><b>碎碎念一律翻到背面。</b>正面只留四样：是什么 · 叫什么 · 什么版本 · 谁的。</li>
    <li><b>有字的卡，右下角折起来一个角</b>（下面每张卡上那个小折角），一眼知道「背面有话」；没写字的卡角是平的。</li>
    <li><b>一行卡一样高。</b>正面不再随字数忽长忽短，架子才像一排架子。</li>
    <li>背面那段话<b>不再截到五行</b>，写多长看多长（卡里滚动）。翻面 ↻、编辑 ✎、点一下闪光，三件事三个地方，照旧。</li>
    <li>糖纸粗描边、硬影、一种媒介一个记号（盒脊 / 唱片 / 书口 / 虹彩角 / 贴条），都不动。</li>
    </ul></section>
    
    <section class="blk"><h2><small>岔路一</small>正面长什么样</h2>
    <p class="note">三版同样六件东西：原声带、明信片、原著、碟片、场刊、公仔。荷兰那张明信片我故意当作没写字，你看折角怎么区分。</p>
    
    <div class="opt"><div class="opt__h"><span class="opt__k">A</span><span class="opt__name">展签</span></div>
    <p class="opt__why"><b>像博物馆展柜里那张小标签。</b>最安静的一版：名字大、规格一行打字机小字、底下是谁和日期，中间一道细线。跟现在最接近，只是把药丸标签和那段话都拿掉了。</p>
    <div class="grid A">%s</div>
    <p class="cap">↑ 信息最清楚，但「东西感」最弱，更像目录。</p></div>
    
    <div class="opt"><div class="opt__h"><span class="opt__k">B</span><span class="opt__name">封面</span><span class="opt__rec">我推荐</span></div>
    <p class="opt__why"><b>卡面就是那件东西的正面。</b>整张染上他的颜色，名字像印在封面上，规格是一张斜贴的白标签，底下一道深色带写着是谁。碟片有盒脊、原声带露半张唱片、书有书名框、场刊有订书钉、公仔是一张挂牌。背景那个大写字母是他名字的首字母，淡淡压在底下。</p>
    <div class="grid B">%s</div>
    <p class="cap">↑ 最像「一件件藏品」，也最有画面；字少，远看一眼认出是什么。</p></div>
    
    <div class="opt"><div class="opt__h"><span class="opt__k">C</span><span class="opt__name">集卡册</span></div>
    <p class="opt__why"><b>像游戏厅扭蛋册里那种一张张的卡。</b>统一竖版，上半截是一块他的颜色、中间一个媒介图标、左上角编号，下半截是白色名牌：名字、规格、谁。卡牌那一类角上有虹彩。手机上两张一行，电脑上四张，像翻一本卡册。</p>
    <div class="grid C">%s</div>
    <p class="cap">↑ 最整齐、最「收集感」，但上半截只有颜色和图标，件数多了会有点一个样。</p></div>
    </section>
    
    <section class="blk"><h2><small>岔路二</small>背面怎么写</h2>
    <p class="note">同一张《割草叔叔》战损版翻过来。两版都是整段话完整显示。</p>
    <div class="backs">
    <div><div class="opt__h" style="margin-bottom:.8rem"><span class="opt__k">A</span><span class="opt__name">实物背面</span></div>%s
    <p class="cap">↑ 像碟盒背面：规格、谁、日期、条码都在，话排在上面。跟现在的背面一个路子，收拾干净了。</p></div>
    <div><div class="opt__h" style="margin-bottom:.8rem"><span class="opt__k">B</span><span class="opt__name">手写便签</span><span class="opt__rec">我推荐</span></div>%s
    <p class="cap">↑ 一张横格便签贴在背面：手写体、一条胶带、一枚入手日期的戳。碎碎念本来就是随手写的话。</p></div>
    </div></section>
    
    %s
    </div>%s""" % (
        CSS, fk_css,
        ''.join(cardA(i) for i in ITEMS), ''.join(cardB(i) for i in ITEMS), ''.join(cardC(i) for i in ITEMS),
        back1(), back2(), fk_html, fk_tail)
    open(OUT, 'w', encoding='utf-8').write(page)
    print('ok', len(page))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
