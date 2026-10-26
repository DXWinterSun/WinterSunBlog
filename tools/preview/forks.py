# -*- coding: utf-8 -*-
"""章节预览页底下的「下一章岔路」——点选、拼成一句话、一键复制。

Winter 2026-10-11 定的交付方式：「你每次都说让我挑岔路，为什么不直接做在这个最新章节底下？
我可以点击选择复制给你的形式，不然我还得找。」所以岔路不再写在聊天里，而是跟着最新一章的
预览页一起发：她读完往下一拉就能点，点完页底那条栏会拼出一句话，「复制」贴回聊天。

render_draft.py 用 --forks <岔路.json> 调它。JSON 结构：

    {
      "title":  "第三章的岔路",                 // 这一块的标题（可省）
      "note":   "点一个就行……",                 // 标题下一句说明（可省）
      "prefix": "第三章：",                     // 复制出去那句话的开头（可省）
      "forks": [
        {"id": "why", "q": "你那天为什么在他公司待了一整天？", "short": "待一整天",
         "hint": "一句补充说明（可省）", "multi": false,
         "options": [
           {"id": "a", "name": "开新戏前对合同", "short": "对合同",
            "hook": "选项下面的一两句描述（可省）", "rec": true}
         ]}
      ]
    }

- 选项字母 A/B/C 按顺序自动编；"multi": true 这一道可以多选。
- 页尾自带一个「想补充的话」输入框，写了就一起拼进复制的那句话（她常常挑完还要加一句）。
- 字符串里可以写 <b> <i> 这类行内 HTML（内容是自己写的，不转义）；short 会转义。
- 选过的会记在她本机浏览器里（换设备不跟着走，只是图个方便）。
"""
import html
import json

E = lambda s: html.escape(s or '', quote=True)

CSS = '''
.forks{--f-ink:var(--ink,var(--text));--f-line:color-mix(in srgb,var(--muted) 35%,transparent);
 --f-panel:color-mix(in srgb,var(--f-ink) 5%,var(--bg));
 margin-top:4.2rem;padding-top:1.6rem;border-top:2px solid var(--accent);
 font-family:"Noto Serif SC","Songti SC",Georgia,serif;}
.forks__h{margin:0;font-size:1.3rem;font-weight:600;color:var(--accent);letter-spacing:.02em;}
.forks__note{margin:.4rem 0 0;color:var(--muted);font-size:.9rem;line-height:1.8;}
.fk{margin-top:2.2rem;}
.fk__q{display:grid;grid-template-columns:auto 1fr;gap:.7rem;align-items:baseline;}
.fk__n{font-family:"EB Garamond",Georgia,serif;font-size:.78rem;letter-spacing:.1em;color:var(--bg);
 background:var(--accent);border-radius:2px;padding:.05rem .45rem;white-space:nowrap;}
.fk__q h3{margin:0;font-size:1.08rem;font-weight:600;line-height:1.6;text-wrap:balance;color:var(--f-ink);}
.fk__hint{margin:.35rem 0 0;color:var(--muted);font-size:.88rem;line-height:1.7;}
.fk__opts{display:grid;gap:.7rem;margin-top:.9rem;}
.fk__opt{position:relative;display:block;cursor:pointer;background:var(--f-panel);
 border:1px solid var(--f-line);border-radius:4px;padding:.8rem .95rem .85rem;line-height:1.75;
 transition:border-color .15s,background .15s;}
.fk__opt:hover{border-color:color-mix(in srgb,var(--accent) 50%,var(--f-line));}
.fk__opt input{position:absolute;opacity:0;pointer-events:none;}
.fk__opt:has(input:focus-visible){outline:2px solid var(--accent);outline-offset:3px;}
.fk__opt:has(input:checked){border-color:var(--accent);
 background:color-mix(in srgb,var(--accent) 13%,var(--bg));}
.fk__top{display:flex;align-items:center;gap:.55rem;flex-wrap:wrap;}
.fk__k{font-family:"EB Garamond",Georgia,serif;font-size:.8rem;width:1.45rem;height:1.45rem;border-radius:50%;
 display:inline-grid;place-items:center;border:1px solid var(--accent);color:var(--accent);flex:none;}
.fk__opt:has(input:checked) .fk__k{background:var(--accent);color:var(--bg);}
.fk__opt:has(input[type=checkbox]) .fk__k{border-radius:3px;}
.fk__name{font-weight:600;font-size:1rem;color:var(--f-ink);}
.fk__rec{font-family:"EB Garamond",Georgia,serif;font-size:.7rem;letter-spacing:.1em;color:var(--bg);
 background:var(--accent);border-radius:2px;padding:0 .35rem;}
.fk__hook{margin:.3rem 0 0;font-size:.92rem;color:var(--muted);}
.fk__more{display:block;margin-top:2.2rem;}
.fk__more span{display:block;font-size:.9rem;color:var(--muted);margin-bottom:.45rem;}
.fk__more textarea{width:100%;min-height:4.6rem;resize:vertical;font:inherit;font-size:.95rem;line-height:1.7;
 color:var(--f-ink);background:var(--f-panel);border:1px solid var(--f-line);border-radius:4px;padding:.6rem .75rem;}
.fk__more textarea:focus{outline:2px solid var(--accent);outline-offset:2px;}
.fkbar{position:fixed;left:0;right:0;bottom:0;z-index:5;
 padding:.65rem 16px calc(.65rem + env(safe-area-inset-bottom,0px));
 background:color-mix(in srgb,var(--bg) 90%,transparent);backdrop-filter:blur(8px);
 -webkit-backdrop-filter:blur(8px);border-top:1px solid var(--f-line,rgba(127,127,127,.3));}
.fkbar__in{max-width:44rem;margin:0 auto;display:flex;gap:.8rem;align-items:center;}
.fkbar__txt{flex:1;min-width:0;font-size:.85rem;line-height:1.5;color:var(--ink,var(--text));
 font-family:"Noto Serif SC","Songti SC",Georgia,serif;}
.fkbar__txt small{display:block;font-size:.7rem;letter-spacing:.1em;color:var(--muted);}
.fkbar__txt span{display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.fkbar button{flex:none;font:inherit;font-size:.88rem;font-weight:600;color:var(--bg);background:var(--accent);
 border:0;border-radius:3px;padding:.55rem 1rem;cursor:pointer;}
.fkbar button:focus-visible{outline:2px solid var(--ink,var(--text));outline-offset:2px;}
.forks-pad{height:5.5rem;}
@media (prefers-reduced-motion:reduce){.fk__opt{transition:none;}}
'''

JS = '''
(function(){
  var KEY = %(key)s, PREFIX = %(prefix)s;
  var forks = [].slice.call(document.querySelectorAll('.fk'));
  var more = document.getElementById('fk-more');
  var bar = document.getElementById('fkbar'), txt = document.getElementById('fkbar-txt'),
      cnt = document.getElementById('fkbar-cnt'), btn = document.getElementById('fkbar-copy');
  function picks(){
    var out = [];
    forks.forEach(function(f){
      var cs = [].slice.call(f.querySelectorAll('input:checked'));
      if (cs.length) out.push(f.getAttribute('data-short') + ' ' + cs.map(function(c){
        return c.getAttribute('data-k') + '（' + c.getAttribute('data-short') + '）';
      }).join('＋'));
    });
    return out;
  }
  function line(){
    var p = picks(), m = (more.value || '').trim();
    var s = PREFIX + (p.length ? p.join('；') : '');
    if (m) s += (p.length ? '。补充：' : '补充：') + m;
    return s;
  }
  function paint(){
    var p = picks(), m = (more.value || '').trim();
    bar.hidden = !(p.length || m);
    cnt.textContent = '已挑 ' + p.length + ' / ' + forks.length + (m ? ' · 带补充' : '');
    txt.textContent = line();
    try {
      var s = {more: more.value};
      forks.forEach(function(f){
        s[f.id] = [].slice.call(f.querySelectorAll('input:checked')).map(function(c){ return c.id; });
      });
      localStorage.setItem(KEY, JSON.stringify(s));
    } catch(e) {}
  }
  try {
    var s = JSON.parse(localStorage.getItem(KEY) || '{}');
    if (s.more) more.value = s.more;
    forks.forEach(function(f){
      (s[f.id] || []).forEach(function(id){ var el = document.getElementById(id); if (el) el.checked = true; });
    });
  } catch(e) {}
  document.addEventListener('change', paint);
  more.addEventListener('input', paint);
  btn.addEventListener('click', function(){
    var t = line();
    function done(){ btn.textContent = '已复制'; setTimeout(function(){ btn.textContent = '复制'; }, 1600); }
    function fallback(){
      var r = document.createRange(); r.selectNodeContents(txt);
      var sel = getSelection(); sel.removeAllRanges(); sel.addRange(r);
      btn.textContent = '已选中，长按复制';
    }
    try { navigator.clipboard.writeText(t).then(done, fallback); } catch(e) { fallback(); }
  });
  paint();
})();
'''


def render(path, page_key):
    """读岔路 JSON，返回 (css, 区块 html, 页底栏 + 脚本 html)。"""
    d = json.load(open(path, encoding='utf-8'))
    blocks = []
    for n, f in enumerate(d['forks'], 1):
        kind = 'checkbox' if f.get('multi') else 'radio'
        opts = []
        for i, o in enumerate(f['options']):
            oid = 'fk-%s-%s' % (f['id'], o['id'])
            k = chr(65 + i)
            opts.append(
                '<label class="fk__opt" for="%s"><input type="%s" name="fk-%s" id="%s" data-k="%s" data-short="%s">'
                '<span class="fk__top"><span class="fk__k">%s</span><span class="fk__name">%s</span>%s</span>%s</label>'
                % (oid, kind, f['id'], oid, k, E(o.get('short', o['name'])), k, o['name'],
                   '<span class="fk__rec">我推荐</span>' if o.get('rec') else '',
                   '<p class="fk__hook">%s</p>' % o['hook'] if o.get('hook') else ''))
        blocks.append(
            '<div class="fk" id="fk-%s" data-short="%s"><div class="fk__q"><span class="fk__n">%s</span><h3>%s</h3></div>%s'
            '<div class="fk__opts" role="group">%s</div></div>'
            % (f['id'], E(f.get('short', '')), ('岔路 %d · 可多选' % n) if f.get('multi') else ('岔路 %d' % n),
               f['q'], '<p class="fk__hint">%s</p>' % f['hint'] if f.get('hint') else '', ''.join(opts)))
    section = (
        '<section class="forks" aria-labelledby="forks-h"><h2 class="forks__h" id="forks-h">%s</h2>'
        '<p class="forks__note">%s</p>%s'
        '<label class="fk__more" for="fk-more"><span>想补充的话（可不填，会一起复制）</span>'
        '<textarea id="fk-more" rows="3"></textarea></label><div class="forks-pad"></div></section>'
        % (d.get('title', '下一章的岔路'),
           d.get('note', '每一道点一个，页底会拼成一句话，点「复制」贴回聊天就行。'), ''.join(blocks)))
    tail = (
        '<div class="fkbar" id="fkbar" hidden><div class="fkbar__in"><div class="fkbar__txt"><small id="fkbar-cnt"></small>'
        '<span id="fkbar-txt"></span></div><button type="button" id="fkbar-copy">复制</button></div></div>'
        '<script>%s</script>' % (JS % {'key': json.dumps('forks-' + page_key),
                                       'prefix': json.dumps(d.get('prefix', ''))}))
    return CSS, section, tail, len(d['forks'])
