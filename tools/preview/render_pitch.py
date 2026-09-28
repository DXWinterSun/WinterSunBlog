#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新 AU「开坑提案」页生成器

开新坑时，Winter 要的不是一份设定文档，是**一眼能挑的选项**（CLAUDE.md 协作第 3 条）。
这张页就干这个：先摆原片里查证过的东西、已经定死不用挑的东西，然后几道岔路，
每道 2–3 个选项做成可点的卡片——开篇方向那一道要附一小段**样章**，让她读到手感再挑。
页底一条选择栏会把她点的拼成一句话，点「复制」贴回聊天就行。

    python3 tools/preview/render_pitch.py .claude/pitches/<slug>.json -o /tmp/.../提案.html

JSON 结构（样板见 .claude/pitches/）：
  meta:    title（网页标签名）/ kicker / h1 / sub / lede / bg,accent,text,muted / next / summary_prefix
  facts:   {title, note, items[]}               原片里查证过的东西
  settled: {title, note, items[{k, v}]}         已定、不用挑（可以改）
  motifs:  {title, note, items[]}               每章带一两样的复现母题
  forks:   [{id, q, hint, options[{id, name, hook, lines[{k,v}], sample, rec}]}]
           sample 用空行分段；rec=true 显示「我推荐」小牌

字符串里可以直接写 <b> <i> 这类行内 HTML（内容是自己写的，不转义）。
单一深色设计（跟路线图页一致），不跟随读者的明暗主题；配色取该角色画册四色。
"""
import json, argparse, html

E = lambda s: html.escape(s or '', quote=True)


def mix(hex_a, hex_b, t):
    a = [int(hex_a[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(hex_b[i:i + 2], 16) for i in (1, 3, 5)]
    return '#%02x%02x%02x' % tuple(round(x + (y - x) * t) for x, y in zip(a, b))


CSS = """
:root{
  --bg:%(bg)s; --accent:%(accent)s; --text:%(text)s; --muted:%(muted)s;
  --panel:%(panel)s; --panel2:%(panel2)s; --line:%(line)s; --dim:%(dim)s;
  color-scheme:dark;
  --serif:"EB Garamond","Noto Serif SC",Georgia,"Songti SC",serif;
  --cn:"Noto Serif SC","Songti SC","Source Han Serif SC",serif;
  --mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace;
}
html{background:var(--bg);}
body{background:var(--bg);color:var(--text);font-family:var(--cn);line-height:1.8;
  -webkit-font-smoothing:antialiased;font-size:16px;}
.wrap{max-width:46rem;margin:0 auto;padding-inline:16px;padding-block:0 7rem;position:relative;}
.moon{position:absolute;inset:0 0 auto 0;height:26rem;pointer-events:none;
  background:radial-gradient(22rem 16rem at 78%% 2.5rem, color-mix(in srgb,var(--text) 10%%,transparent), transparent 70%%);}

header.top{padding-block:3rem 0;position:relative;}
.kicker{font-family:var(--mono);font-size:.66rem;letter-spacing:.24em;text-transform:uppercase;
  color:var(--accent);margin:0 0 1rem;display:flex;gap:.6rem;align-items:center;flex-wrap:wrap;}
.kicker i{display:inline-block;width:.45rem;height:.45rem;border-radius:50%%;background:var(--accent);
  box-shadow:0 0 .6rem var(--accent);font-style:normal;}
h1{font-family:var(--serif);font-weight:500;font-size:clamp(2.1rem,8vw,3.4rem);line-height:1.05;
  margin:0;letter-spacing:.005em;text-wrap:balance;}
h1 em{font-style:italic;color:var(--accent);}
.sub{margin:.7rem 0 0;font-family:var(--mono);font-size:.72rem;letter-spacing:.12em;color:var(--muted);}
.lede{margin:1.6rem 0 0;font-size:1.02rem;max-width:34em;}
.lede b{color:var(--accent);font-weight:600;}

section{margin-top:3.2rem;}
.sec-h{display:flex;align-items:baseline;gap:.8rem;margin:0 0 .35rem;}
.sec-h h2{margin:0;font-size:1.25rem;font-weight:600;letter-spacing:.02em;}
.sec-h .tag{font-family:var(--mono);font-size:.6rem;letter-spacing:.16em;text-transform:uppercase;
  color:var(--muted);}
.sec-note{margin:0 0 1.1rem;color:var(--muted);font-size:.92rem;}

.facts{list-style:none;margin:0;padding:0;display:grid;gap:.1rem;
  border-top:1px solid var(--line);}
.facts li{padding:.7rem 0 .7rem 1.3rem;border-bottom:1px solid var(--line);position:relative;font-size:.96rem;}
.facts li::before{content:"";position:absolute;left:.2rem;top:1.28rem;width:.4rem;height:.4rem;
  border:1px solid var(--accent);transform:rotate(45deg);}
.facts b,.settled b,.motifs b{color:var(--accent);font-weight:600;}

.settled{display:grid;grid-template-columns:1fr;gap:0;margin:0;border-top:1px solid var(--line);}
.settled div{display:grid;grid-template-columns:6.2rem 1fr;gap:1rem;padding:.75rem 0;
  border-bottom:1px solid var(--line);}
.settled dt{font-family:var(--mono);font-size:.7rem;letter-spacing:.1em;color:var(--muted);padding-top:.3rem;}
.settled dd{margin:0;font-size:.96rem;}
.swatch{display:inline-flex;align-items:center;gap:.35rem;margin:.15rem .7rem .15rem 0;font-size:.86rem;white-space:nowrap;}
.swatch i{width:.9rem;height:.9rem;border-radius:2px;border:1px solid var(--line);display:inline-block;}
.en{font-family:var(--serif);font-style:italic;font-size:1.06em;}

.motifs{list-style:none;margin:0;padding:0;display:grid;gap:.6rem;grid-template-columns:1fr;}
@media (min-width:36rem){.motifs{grid-template-columns:1fr 1fr;}}
.motifs li{background:var(--panel);border-radius:3px;padding:.75rem .9rem;font-size:.93rem;}

.fork{margin-top:3.2rem;}
.fork__q{display:grid;grid-template-columns:auto 1fr;gap:.8rem;align-items:baseline;
  border-top:2px solid var(--accent);padding-top:1rem;}
.fork__n{font-family:var(--mono);font-size:.7rem;letter-spacing:.12em;color:var(--bg);
  background:var(--accent);border-radius:2px;padding:.16rem .45rem;white-space:nowrap;}
.fork__q h2{margin:0;font-size:1.3rem;font-weight:600;text-wrap:balance;}
.fork__hint{margin:.5rem 0 1.2rem;color:var(--muted);font-size:.92rem;}
.opts{display:grid;gap:.9rem;}
.opts--grid{grid-template-columns:repeat(auto-fit,minmax(13rem,1fr));}
.opt{position:relative;display:block;cursor:pointer;background:var(--panel);
  border:1px solid var(--line);border-radius:4px;padding:1rem 1.05rem 1.05rem;
  transition:border-color .15s, background .15s;}
.opt:hover{border-color:color-mix(in srgb,var(--accent) 45%%,var(--line));}
.opt input{position:absolute;opacity:0;pointer-events:none;}
.opt:has(input:focus-visible){outline:2px solid var(--accent);outline-offset:3px;}
.opt:has(input:checked){border-color:var(--accent);background:var(--panel2);}
.opt__head{display:flex;align-items:center;gap:.6rem;flex-wrap:wrap;}
.opt__k{font-family:var(--mono);font-size:.72rem;width:1.55rem;height:1.55rem;border-radius:50%%;
  display:inline-grid;place-items:center;border:1px solid var(--accent);color:var(--accent);flex:none;}
.opt:has(input:checked) .opt__k{background:var(--accent);color:var(--bg);}
.opt__name{font-size:1.08rem;font-weight:600;margin:0;}
.rec{font-family:var(--mono);font-size:.58rem;letter-spacing:.12em;color:var(--bg);background:var(--accent);
  border-radius:2px;padding:.1rem .35rem;}
.opt__hook{margin:.55rem 0 0;font-size:.96rem;}
.opt__lines{margin:.7rem 0 0;display:grid;gap:.3rem;}
.opt__lines div{display:grid;grid-template-columns:4.2rem 1fr;gap:.6rem;font-size:.88rem;color:var(--muted);}
.opt__lines dt{font-family:var(--mono);font-size:.66rem;letter-spacing:.08em;padding-top:.22rem;color:var(--accent);}
.opt__lines dd{margin:0;}
.sample{margin:1rem 0 0;padding:1rem 1.05rem;border-left:2px solid var(--accent);
  background:color-mix(in srgb,var(--bg) 55%%,var(--panel));font-size:.95rem;line-height:1.95;}
.sample__label{display:block;font-family:var(--mono);font-size:.6rem;letter-spacing:.2em;color:var(--muted);
  margin-bottom:.4rem;text-transform:uppercase;}
.sample p{margin:0;}
.sample p+p{margin-top:.75em;}

.next{margin-top:3.6rem;padding-top:1.2rem;border-top:1px solid var(--line);color:var(--muted);font-size:.93rem;}
.next b{color:var(--text);}

.bar{position:fixed;left:0;right:0;bottom:0;z-index:5;
  padding:.7rem 16px calc(.7rem + env(safe-area-inset-bottom, 0px));
  background:color-mix(in srgb,var(--bg) 88%%,transparent);backdrop-filter:blur(8px);
  -webkit-backdrop-filter:blur(8px);border-top:1px solid var(--line);}
.bar__in{max-width:46rem;margin:0 auto;display:flex;gap:.8rem;align-items:center;}
.bar__txt{flex:1;min-width:0;font-size:.86rem;line-height:1.5;}
.bar__txt small{display:block;font-family:var(--mono);font-size:.6rem;letter-spacing:.14em;color:var(--muted);}
.bar__txt span{display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.bar button{flex:none;font:inherit;font-size:.86rem;font-weight:600;color:var(--bg);background:var(--accent);
  border:0;border-radius:3px;padding:.55rem .95rem;cursor:pointer;}
.bar button:focus-visible{outline:2px solid var(--text);outline-offset:2px;}
.bar button[disabled]{opacity:.45;cursor:default;}
@media (prefers-reduced-motion:reduce){.opt{transition:none;}}
"""

JS = """
(function(){
  var KEY = %(key)s, PREFIX = %(prefix)s;
  var forks = [].slice.call(document.querySelectorAll('.fork'));
  var txt = document.getElementById('bar-txt'), cnt = document.getElementById('bar-cnt'),
      btn = document.getElementById('bar-copy');
  function picks(){
    var out = [];
    forks.forEach(function(f){
      var c = f.querySelector('input:checked');
      if (c) out.push(f.getAttribute('data-short') + ' ' + c.getAttribute('data-short'));
    });
    return out;
  }
  function paint(){
    var p = picks();
    cnt.textContent = '已挑 ' + p.length + ' / ' + forks.length;
    txt.textContent = p.length ? p.join(' · ') : '每一栏点一个，这里会拼成一句话';
    btn.disabled = !p.length;
    try {
      var s = {};
      forks.forEach(function(f){ var c = f.querySelector('input:checked'); if (c) s[f.id] = c.id; });
      localStorage.setItem(KEY, JSON.stringify(s));
    } catch(e) {}
  }
  try {
    var s = JSON.parse(localStorage.getItem(KEY) || '{}');
    Object.keys(s).forEach(function(k){ var el = document.getElementById(s[k]); if (el) el.checked = true; });
  } catch(e) {}
  document.addEventListener('change', paint);
  btn.addEventListener('click', function(){
    var line = PREFIX + picks().join(' · ');
    function done(){ btn.textContent = '已复制'; setTimeout(function(){ btn.textContent = '复制'; }, 1600); }
    function fallback(){
      var r = document.createRange(); r.selectNodeContents(txt);
      var sel = getSelection(); sel.removeAllRanges(); sel.addRange(r);
      btn.textContent = '已选中，长按复制';
    }
    try { navigator.clipboard.writeText(line).then(done, fallback); } catch(e) { fallback(); }
  });
  paint();
})();
"""


def paras(s):
    return ''.join('<p>%s</p>' % p.strip().replace('\n', '<br>') for p in s.split('\n\n') if p.strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('data')
    ap.add_argument('-o', '--out', required=True)
    a = ap.parse_args()
    d = json.load(open(a.data, encoding='utf-8'))
    m = d['meta']
    css = CSS % {
        'bg': m['bg'], 'accent': m['accent'], 'text': m['text'], 'muted': m['muted'],
        'panel': mix(m['bg'], m['text'], .05), 'panel2': mix(m['bg'], m['accent'], .12),
        'line': mix(m['bg'], m['text'], .15), 'dim': mix(m['bg'], m['text'], .55),
    }
    out = ['<title>%s</title>' % E(m['title']),
           '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Noto+Serif+SC:wght@400;600&display=swap">',
           '<style>%s</style>' % css,
           '<div class="wrap"><div class="moon" aria-hidden="true"></div>',
           '<header class="top"><p class="kicker"><i></i>%s</p><h1>%s</h1><p class="sub">%s</p><p class="lede">%s</p></header>'
           % (m['kicker'], m['h1'], m['sub'], m['lede'])]

    def sec(key, body):
        s = d.get(key)
        if not s:
            return
        out.append('<section><div class="sec-h"><h2>%s</h2><span class="tag">%s</span></div>%s%s</section>'
                   % (s['title'], s.get('tag', ''),
                      '<p class="sec-note">%s</p>' % s['note'] if s.get('note') else '', body(s)))

    sec('facts', lambda s: '<ul class="facts">%s</ul>' % ''.join('<li>%s</li>' % i for i in s['items']))
    sec('settled', lambda s: '<dl class="settled">%s</dl>' % ''.join(
        '<div><dt>%s</dt><dd>%s</dd></div>' % (i['k'], i['v']) for i in s['items']))
    sec('motifs', lambda s: '<ul class="motifs">%s</ul>' % ''.join('<li>%s</li>' % i for i in s['items']))

    for n, f in enumerate(d['forks'], 1):
        opts = []
        for i, o in enumerate(f['options']):
            oid = '%s-%s' % (f['id'], o['id'])
            lines = ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % (l['k'], l['v']) for l in o.get('lines', []))
            sample = ('<div class="sample"><span class="sample__label">样章一小段</span>%s</div>' % paras(o['sample'])
                      if o.get('sample') else '')
            opts.append(
                '<label class="opt" for="%s"><input type="radio" name="%s" id="%s" data-short="%s">'
                '<div class="opt__head"><span class="opt__k">%s</span><h3 class="opt__name">%s</h3>%s</div>'
                '%s%s%s</label>'
                % (oid, f['id'], oid, E(o.get('short', o['name'])), chr(65 + i), o['name'],
                   '<span class="rec">我推荐</span>' if o.get('rec') else '',
                   '<p class="opt__hook">%s</p>' % o['hook'] if o.get('hook') else '',
                   '<dl class="opt__lines">%s</dl>' % lines if lines else '', sample))
        grid = ' opts--grid' if not any(o.get('sample') for o in f['options']) else ''
        out.append(
            '<section class="fork" id="%s" data-short="%s"><div class="fork__q"><span class="fork__n">岔路 %d</span>'
            '<h2>%s</h2></div><p class="fork__hint">%s</p><div class="opts%s" role="radiogroup">%s</div></section>'
            % (f['id'], E(f.get('short', '')), n, f['q'], f.get('hint', ''), grid, ''.join(opts)))

    if m.get('next'):
        out.append('<p class="next">%s</p>' % m['next'])
    out.append('</div>')
    out.append('<div class="bar"><div class="bar__in"><div class="bar__txt"><small id="bar-cnt"></small>'
               '<span id="bar-txt"></span></div><button type="button" id="bar-copy">复制</button></div></div>')
    out.append('<script>%s</script>' % (JS % {'key': json.dumps('pitch-' + m['title']),
                                               'prefix': json.dumps(m.get('summary_prefix', ''))}))
    open(a.out, 'w', encoding='utf-8').write('\n'.join(out))
    print('→ %s  （%d 道岔路）' % (a.out, len(d['forks'])))


if __name__ == '__main__':
    main()
