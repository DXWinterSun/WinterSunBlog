/* ===============================================================
   系列首页的交互（2026-10-15 改版）——只在 _layouts/series.html 里加载。
   ① 介绍两段 → 文件夹标签（点哪枚亮哪枚，下面那张纸换成那一段）
   ② 章节 → 正篇 / 番外 / 他视角三张书页，各自能合上（右边伸出书口小标签）
   ③ 页底票根：认出是哪个 Sam 角色就亮「后台电话」；「保存票根」把票画成一张图
   没有这段脚本页面照样能用：介绍上下排、章节一列票根、票根上少一格电话。
   =============================================================== */
(function () {
  'use strict';
  var ticket = document.getElementById('js-series-ticket');
  var BASE = ticket ? (ticket.getAttribute('data-base') || '') : (window.SITE_BASEURL || '');

  /* ---------- ① 文件夹标签 ---------- */
  function folderTabs() {
    var wrap = document.getElementById('js-series-intro');
    if (!wrap) return;
    var panels = Array.prototype.slice.call(wrap.querySelectorAll('.c-sam-intro'));
    if (!panels.length) return;
    var row = document.createElement('div');
    row.className = 'c-folder-tabs__row';
    row.setAttribute('role', 'tablist');
    var sheets = [], tabs = [];
    panels.forEach(function (p, i) {
      var h = p.querySelector('.c-sam-intro__heading, h2');
      var name = h ? h.textContent.trim() : ('第 ' + (i + 1) + ' 段');
      var tab = document.createElement('button');
      tab.type = 'button';
      tab.className = 'c-folder-tabs__tab';
      tab.id = 'intro-tab-' + i;
      tab.setAttribute('role', 'tab');
      tab.setAttribute('aria-controls', 'intro-sheet-' + i);
      tab.textContent = name;
      var sheet = document.createElement('div');
      sheet.className = 'c-folder-tabs__sheet';
      sheet.id = 'intro-sheet-' + i;
      sheet.setAttribute('role', 'tabpanel');
      sheet.setAttribute('aria-labelledby', tab.id);
      sheet.appendChild(p);
      tabs.push(tab); sheets.push(sheet);
      tab.addEventListener('click', function () { pick(i); });
      row.appendChild(tab);
    });
    function pick(n) {
      tabs.forEach(function (t, i) {
        t.setAttribute('aria-selected', i === n ? 'true' : 'false');
        t.tabIndex = i === n ? 0 : -1;
        sheets[i].hidden = i !== n;
      });
    }
    row.addEventListener('keydown', function (e) {
      var cur = tabs.indexOf(document.activeElement);
      if (cur < 0) return;
      var next = e.key === 'ArrowRight' ? cur + 1 : e.key === 'ArrowLeft' ? cur - 1 : -1;
      if (next < 0 || next >= tabs.length) return;
      e.preventDefault(); pick(next); tabs[next].focus();
    });
    wrap.innerHTML = '';
    var box = document.createElement('div');
    box.className = 'c-folder-tabs';
    box.appendChild(row);
    sheets.forEach(function (s) { box.appendChild(s); });
    wrap.appendChild(box);
    pick(0);
  }

  /* ---------- ② 三张书页 ---------- */
  var KINDS = [
    { key: 'main', cn: '正篇', en: 'Chapters' },
    { key: 'extra', cn: '番外', en: 'Extras' },
    { key: 'pov', cn: '他视角', en: 'His Side' }
  ];
  function bookPages() {
    var list = document.querySelector('.c-chapter-list[data-series]');
    if (!list) return;
    var cards = Array.prototype.slice.call(list.querySelectorAll('.c-chapter-card'));
    if (!cards.length) return;
    var by = {};
    cards.forEach(function (c) {
      var k = c.getAttribute('data-kind') || 'main';
      (by[k] = by[k] || []).push(c);
    });
    var present = KINDS.filter(function (k) { return by[k.key] && by[k.key].length; });
    if (!present.length) return;
    var book = document.createElement('div');
    book.className = 'c-book';
    list.parentNode.insertBefore(book, list);
    var subLists = [];
    present.forEach(function (k) {
      var page = document.createElement('section');
      page.className = 'c-book-page c-book-page--' + k.key + (present.length > 1 ? ' has-tab' : '');
      page.setAttribute('aria-label', k.cn);
      var head = document.createElement('button');
      head.type = 'button';
      head.className = 'c-book-page__head';
      head.setAttribute('aria-expanded', 'true');
      head.innerHTML = '<b>' + k.cn + '</b><em>' + k.en + ' · ' + by[k.key].length + '</em><i aria-hidden="true">−</i>';
      var body = document.createElement('div');
      body.className = 'c-book-page__body';
      var target;
      if (k.key === 'main') {
        target = list;                       // 正篇留在原来那张列表里：main.js 的「读到哪」「倒序」都认它
      } else {
        target = document.createElement('div');
        target.className = 'c-chapter-list c-chapter-list--sub';
        subLists.push(target);
      }
      by[k.key].forEach(function (c) { target.appendChild(c); });
      body.appendChild(target);
      page.appendChild(head);
      if (present.length > 1) {
        var tab = document.createElement('span');
        tab.className = 'c-book-page__tab';
        tab.setAttribute('aria-hidden', 'true');
        tab.textContent = k.cn;
        page.appendChild(tab);
      }
      page.appendChild(body);
      head.addEventListener('click', function () {
        var closed = page.classList.toggle('is-closed');
        head.setAttribute('aria-expanded', closed ? 'false' : 'true');
        head.querySelector('i').textContent = closed ? '＋' : '−';
      });
      book.appendChild(page);
    });
    // 「倒序」是 main.js 挂在正篇列表上的；番外 / 他视角那几张纸跟着一起翻
    var rev = document.getElementById('js-chapter-reverse');
    if (rev && subLists.length) {
      rev.addEventListener('click', function () {
        var on = list.classList.contains('is-reversed');
        subLists.forEach(function (l) { l.classList.toggle('is-reversed', on); });
      });
    }
  }

  /* ---------- ③ 票根：后台电话 ---------- */
  function backstagePhone() {
    var a = document.getElementById('js-ticket-phone');
    if (!a) return;
    fetch(BASE + '/sam/lines.json', { cache: 'no-cache' })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        function norm(p) {
          p = (p || '').replace(/index\.html$/, '');
          return p.slice(-1) === '/' ? p : p + '/';
        }
        var path = norm(window.location.pathname);
        var bylineEl = document.querySelector('.c-hero__byline-text');
        var bname = bylineEl ? bylineEl.textContent.split('·')[0].trim() : '';
        var hit = null;
        data.characters.forEach(function (c) {
          if (!hit && c.auLink && norm(c.auLink) === path) hit = c;
        });
        if (!hit && bname) {
          data.characters.forEach(function (c) { if (!hit && c.name === bname) hit = c; });
        }
        if (!hit) return;
        a.href = BASE + '/sam/hotline/?char=' + encodeURIComponent(hit.id);
        a.hidden = false;
      })
      .catch(function () {});
  }

  /* ---------- ③ 票根：保存成图 ---------- */
  function cssVar(el, name, fallback) {
    var v = getComputedStyle(el).getPropertyValue(name).trim();
    return v || fallback;
  }
  function luminance(hex) {
    var m = /^#?([0-9a-f]{6})$/i.exec(hex.trim());
    if (!m) return 0;
    var n = parseInt(m[1], 16);
    var r = (n >> 16) & 255, g = (n >> 8) & 255, b = n & 255;
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255;
  }
  function mix(hexA, hexB, t) {
    var a = parseInt(hexA.replace('#', ''), 16), b = parseInt(hexB.replace('#', ''), 16);
    function ch(s) { var x = (a >> s) & 255, y = (b >> s) & 255; return Math.round(x + (y - x) * t); }
    return 'rgb(' + ch(16) + ',' + ch(8) + ',' + ch(0) + ')';
  }
  function roundRect(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath();
  }
  function drawTicket(done) {
    var bg = cssVar(ticket, '--tk-bg', '#1b2238'), ac = cssVar(ticket, '--tk-accent', '#d4b46a');
    var tx = cssVar(ticket, '--tk-text', '#ece9e2'), mu = cssVar(ticket, '--tk-muted', '#9a9388');
    var who = ticket.getAttribute('data-who') || '', sub = ticket.getAttribute('data-sub') || '';
    var series = ticket.getAttribute('data-series') || '', run = ticket.getAttribute('data-run') || '';
    var eyebrow = (ticket.querySelector('.c-tk-who__e') || {}).textContent || 'Admit One';
    var swatches = Array.prototype.slice.call(ticket.querySelectorAll('.c-tk-perf__c')).map(function (s) {
      return { hex: s.getAttribute('data-hex'), cn: s.getAttribute('data-cn'), en: s.getAttribute('data-en') };
    });
    var stubs = Array.prototype.slice.call(ticket.querySelectorAll('.c-tk-stub')).filter(function (s) { return !s.hidden; })
      .map(function (s) { return { cn: s.querySelector('b').textContent, en: s.querySelector('em').textContent }; });
    var photo = document.getElementById('js-ticket-photo');

    var S = 2, W = 560 * S, pad = 20 * S;
    var photoH = photo ? Math.round(W * 7 / 16) : 0;
    var perfH = swatches.length ? 66 * S : 0;
    var H = (18 + 14 + 12 + 44 + 4 + 18 + 14) * S + photoH + perfH + (14 + 22 + 6 + 14 + 14) * S + (stubs.length ? 64 * S : 0);
    var cv = document.createElement('canvas');
    cv.width = W; cv.height = H;
    var ctx = cv.getContext('2d');
    ctx.fillStyle = mix(bg, '#ffffff', 0.07);
    roundRect(ctx, 0, 0, W, H, 14 * S); ctx.fill();

    var y = pad;
    ctx.fillStyle = mu;
    ctx.font = (10 * S) + 'px "Special Elite", "Courier New", monospace';
    ctx.textBaseline = 'top';
    drawSpaced(ctx, eyebrow.toUpperCase(), pad, y, 0.24 * 10 * S);
    y += 16 * S;
    ctx.fillStyle = ac;
    ctx.font = 'bold ' + (40 * S) + 'px Volkhov, "Noto Serif SC", serif';
    fitText(ctx, who, pad, y, W - pad * 2, 40 * S);
    y += 48 * S;
    ctx.fillStyle = tx;
    ctx.globalAlpha = 0.85;
    ctx.font = 'italic ' + (13.5 * S) + 'px "EB Garamond", "Noto Serif SC", serif';
    ctx.fillText(sub, pad, y);
    ctx.globalAlpha = 1;
    y += 28 * S;

    function rest() {
      if (swatches.length) {
        ctx.fillStyle = mix(bg, '#000000', 0.35);
        ctx.fillRect(0, y, W, perfH);
        // 齿孔
        ctx.fillStyle = 'rgba(236,233,226,.55)';
        for (var hx = 8 * S; hx < W; hx += 16 * S) {
          ctx.beginPath(); ctx.arc(hx, y + 5 * S, 2 * S, 0, Math.PI * 2); ctx.fill();
          ctx.beginPath(); ctx.arc(hx, y + perfH - 5 * S, 2 * S, 0, Math.PI * 2); ctx.fill();
        }
        var gap = 4 * S, inner = W - 12 * S, cw = (inner - gap * (swatches.length - 1)) / swatches.length;
        swatches.forEach(function (s, i) {
          var x = 6 * S + i * (cw + gap), top = y + 10 * S, h = perfH - 20 * S;
          ctx.fillStyle = s.hex; ctx.fillRect(x, top, cw, h);
          var dark = luminance(s.hex) > 0.6;
          ctx.fillStyle = dark ? '#2a2b36' : '#ece9e2';
          ctx.textAlign = 'center';
          ctx.font = '500 ' + (11 * S) + 'px "Noto Serif SC", serif';
          ctx.fillText(s.cn || '', x + cw / 2, top + h - 26 * S);
          ctx.font = 'italic ' + (9 * S) + 'px "EB Garamond", serif';
          ctx.fillText(s.en || '', x + cw / 2, top + h - 13 * S);
          ctx.textAlign = 'left';
        });
        y += perfH;
      }
      y += 14 * S;
      ctx.fillStyle = tx;
      ctx.font = 'bold ' + (18 * S) + 'px Volkhov, "Noto Serif SC", serif';
      ctx.fillText(series, pad, y);
      y += 26 * S;
      ctx.fillStyle = mu;
      ctx.font = (10.5 * S) + 'px "Special Elite", "Courier New", monospace';
      drawSpaced(ctx, run, pad, y, 0.12 * 10.5 * S);
      y += 28 * S;
      if (stubs.length) {
        // 撕票线 + 咬口
        ctx.strokeStyle = 'rgba(236,233,226,.4)'; ctx.lineWidth = 1 * S; ctx.setLineDash([4 * S, 4 * S]);
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); ctx.setLineDash([]);
        ctx.globalCompositeOperation = 'destination-out';
        ctx.beginPath(); ctx.arc(0, y, 8 * S, 0, Math.PI * 2); ctx.fill();
        ctx.beginPath(); ctx.arc(W, y, 8 * S, 0, Math.PI * 2); ctx.fill();
        ctx.globalCompositeOperation = 'source-over';
        var sw = W / stubs.length;
        stubs.forEach(function (s, i) {
          var cx = sw * i + sw / 2;
          if (i) { ctx.setLineDash([3 * S, 4 * S]); ctx.beginPath(); ctx.moveTo(sw * i, y + 10 * S); ctx.lineTo(sw * i, y + 54 * S); ctx.stroke(); ctx.setLineDash([]); }
          ctx.textAlign = 'center';
          ctx.fillStyle = tx; ctx.font = '600 ' + (13 * S) + 'px "Noto Serif SC", serif';
          ctx.fillText(s.cn, cx, y + 20 * S);
          ctx.fillStyle = mu; ctx.font = 'italic ' + (10.5 * S) + 'px "EB Garamond", serif';
          ctx.fillText(s.en, cx, y + 40 * S);
          ctx.textAlign = 'left';
        });
      }
      done(cv);
    }

    if (photo && photo.complete && photo.naturalWidth) {
      drawCover(ctx, photo, 0, y, W, photoH, cssVar(photo, '--pos', '50% 30%'));
      y += photoH; rest();
    } else if (photo) {
      photo.addEventListener('load', function () { drawCover(ctx, photo, 0, y, W, photoH, cssVar(photo, '--pos', '50% 30%')); y += photoH; rest(); }, { once: true });
      photo.addEventListener('error', function () { y += photoH; rest(); }, { once: true });
    } else { rest(); }
  }
  function drawCover(ctx, img, x, y, w, h, pos) {
    var p = pos.split(/\s+/), px = parseFloat(p[0]) / 100 || 0.5, py = parseFloat(p[1]) / 100 || 0.3;
    var iw = img.naturalWidth, ih = img.naturalHeight, scale = Math.max(w / iw, h / ih);
    var sw = w / scale, sh = h / scale;
    var sx = (iw - sw) * px, sy = (ih - sh) * py;
    try { ctx.drawImage(img, sx, sy, sw, sh, x, y, w, h); } catch (e) { /* 跨域图画不上就留底色 */ }
  }
  function drawSpaced(ctx, text, x, y, spacing) {
    for (var i = 0; i < text.length; i++) { var ch = text[i]; ctx.fillText(ch, x, y); x += ctx.measureText(ch).width + spacing; }
  }
  function fitText(ctx, text, x, y, maxW, size) {
    var font = ctx.font;
    while (ctx.measureText(text).width > maxW && size > 18) { size -= 2; ctx.font = font.replace(/\d+px/, size + 'px'); }
    ctx.fillText(text, x, y);
  }
  function saveTicket() {
    var btn = document.getElementById('js-ticket-save');
    if (!btn || !ticket) return;
    btn.addEventListener('click', function () {
      btn.disabled = true;
      var fonts = document.fonts ? Promise.all([
        document.fonts.load('bold 40px Volkhov'), document.fonts.load('italic 14px "EB Garamond"'),
        document.fonts.load('500 11px "Noto Serif SC"'), document.fonts.load('10px "Special Elite"')
      ]).catch(function () {}) : Promise.resolve();
      fonts.then(function () {
        drawTicket(function (cv) {
          btn.disabled = false;
          var url = cv.toDataURL('image/png');
          var ov = document.createElement('div');
          ov.className = 'c-tk-saved';
          ov.setAttribute('role', 'dialog');
          ov.setAttribute('aria-label', '保存票根');
          var name = ((ticket.getAttribute('data-series') || 'ticket') + ' · ' + (ticket.getAttribute('data-who') || '')).replace(/[\\/:*?"<>|]+/g, ' ').trim();
          ov.innerHTML = '<img alt="票根" src="' + url + '"><p>手机：长按图片存到相册 · 电脑：点「下载」</p>' +
            '<div class="c-tk-saved__row"><a class="is-primary" download="' + name + '.png" href="' + url + '">下载</a><button type="button">关掉</button></div>';
          ov.addEventListener('click', function (e) { if (e.target === ov || e.target.tagName === 'BUTTON') ov.remove(); });
          document.addEventListener('keydown', function esc(e) { if (e.key === 'Escape') { ov.remove(); document.removeEventListener('keydown', esc); } });
          document.body.appendChild(ov);
        });
      });
    });
  }

  function init() {
    folderTabs();
    bookPages();
    backstagePhone();
    saveTicket();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
