/* 📻 冬的电台 · 一首歌一张卡（2026-10-27）
   Winter：「是不是可以做类似于 AU 的票根分享功能的歌曲分享保存图」。
   节目单每一行右边一颗小相机，点了用 canvas 画一张收音机样子的卡：顶上红白细边、刻度盘（指针停在这首歌的乐队）、
   封面、歌名 / 英文小注 / 乐队 / 时长，底下 POLSKI FM · 冬的电台。弹出来的浮层复用票根那套 .c-tk-saved
   （手机长按存相册、电脑点下载）。封面来自 YouTube（i.ytimg.com 允许跨域画进画布）；画不上就退回色块首字母。
   只在 /radio/ 页加载。 */
(function () {
  'use strict';
  var root = document.getElementById('js-radio');
  if (!root) return;
  var W = 1080, H = 1350;
  var CREAM = '#f1e8d2', DIM = '#b9b09a', RED = '#d4213d', GOLD = '#e2b45a';

  function rr(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath();
  }
  function fit(ctx, text, font, maxW, minPx) {
    var m = /(\d+)px/.exec(font), size = m ? +m[1] : 40;
    ctx.font = font;
    while (ctx.measureText(text).width > maxW && size > minPx) { size -= 2; ctx.font = font.replace(/\d+px/, size + 'px'); }
    return size;
  }
  function hue(s) { var h = 0; for (var i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) % 360; return h; }

  function rowData(row) {
    var q = function (sel) { var el = row.querySelector(sel); return el ? el.textContent.trim() : ''; };
    var img = row.querySelector('img.c-radio__th');
    return {
      title: q('.c-radio__t b'),
      gloss: q('.c-radio__gloss'),
      who: q('.c-radio__who'),
      dur: q('.c-radio__dur'),
      band: row.getAttribute('data-band') || '',
      bandName: row.getAttribute('data-band-name') || '',
      wall: !!row.querySelector('.c-radio__wall'),
      thumb: img ? img.getAttribute('src') : '',
      n: q('.c-radio__n')
    };
  }
  function dialTicks() {
    return [].slice.call(root.querySelectorAll('#js-radio-dial button')).map(function (b) {
      return { band: b.getAttribute('data-band'), name: (b.querySelector('span') || b).textContent.trim() };
    });
  }

  function draw(d, done) {
    var cv = document.createElement('canvas');
    cv.width = W; cv.height = H;
    var ctx = cv.getContext('2d');

    // 面板
    var g = ctx.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, '#2a2f3a'); g.addColorStop(1, '#141821');
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    // 红白细边
    ctx.fillStyle = '#ffffff'; ctx.fillRect(0, 0, W / 2, 14);
    ctx.fillStyle = RED; ctx.fillRect(W / 2, 0, W / 2, 14);

    // 刻度盘
    var ticks = dialTicks();
    if (!ticks.length) ticks = [{ band: 'all', name: '全部' }, { band: d.band, name: d.bandName }];
    var isOther = !ticks.some(function (t) { return t.band === d.band; });
    var cur = ticks.findIndex(function (t) { return t.band === d.band || (isOther && t.band === 'other'); });
    if (cur < 0) cur = 0;
    var dx = 70, dy = 70, dw = W - 140, dh = 118;
    ctx.save();
    rr(ctx, dx, dy, dw, dh, 10);
    ctx.fillStyle = 'rgba(255,255,255,0.05)'; ctx.fill();
    ctx.strokeStyle = 'rgba(255,255,255,0.18)'; ctx.lineWidth = 2; ctx.stroke();
    ctx.clip();
    // 细刻度
    ctx.strokeStyle = 'rgba(255,255,255,0.16)'; ctx.lineWidth = 2;
    for (var x = dx + 18; x < dx + dw; x += 22) { ctx.beginPath(); ctx.moveTo(x, dy); ctx.lineTo(x, dy + 16); ctx.stroke(); }
    // 指针（先画，台名压在它上面）
    var slot = dw / ticks.length;
    var nx = dx + slot * (cur + .5);
    ctx.shadowColor = RED; ctx.shadowBlur = 18;
    ctx.fillStyle = RED; ctx.fillRect(nx - 2, dy, 4, dh);
    ctx.shadowBlur = 0;
    // 台名
    ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
    ticks.forEach(function (t, i) {
      var cx = dx + slot * (i + .5);
      ctx.strokeStyle = 'rgba(255,255,255,0.5)'; ctx.beginPath(); ctx.moveTo(cx, dy); ctx.lineTo(cx, dy + 26); ctx.stroke();
      var on = i === cur;
      ctx.fillStyle = on ? '#ffffff' : DIM;
      var f = (on ? '600 ' : '400 ') + '24px "EB Garamond", "Noto Serif SC", Georgia, serif';
      var size = fit(ctx, t.name, f, slot - 14, 14);
      if (on) { ctx.shadowColor = 'rgba(20,24,33,0.95)'; ctx.shadowBlur = 10; ctx.fillText(t.name, cx, dy + 76); ctx.fillText(t.name, cx, dy + 76); }
      else ctx.fillText(t.name, cx, dy + 76);
      ctx.shadowBlur = 0;
    });
    ctx.restore();

    // 封面
    var cs = 620, cxp = (W - cs) / 2, cyp = 240;
    function afterCover() {
      // 歌名
      ctx.textAlign = 'center';
      ctx.fillStyle = CREAM;
      var y = cyp + cs + 96;
      var ts = fit(ctx, d.title, '600 64px "EB Garamond", "Noto Serif SC", Georgia, serif', W - 160, 34);
      ctx.fillText(d.title, W / 2, y);
      y += Math.round(ts * .75) + 14;
      if (d.gloss) {
        fit(ctx, d.gloss, 'italic 400 36px "EB Garamond", Georgia, serif', W - 200, 22);
        ctx.fillStyle = '#e6c88f';
        ctx.fillText(d.gloss, W / 2, y);
        y += 46;
      }
      ctx.fillStyle = DIM;
      var line = d.who + (d.dur ? '  ·  ' + d.dur : '');
      fit(ctx, line, '400 32px "EB Garamond", "Noto Serif SC", Georgia, serif', W - 200, 20);
      ctx.fillText(line, W / 2, y + 10);
      if (d.wall) {
        // 「墙」小标：唱片墙上有这首
        var tx = W / 2, ty = y + 62;
        ctx.font = '400 20px "Noto Serif SC", "EB Garamond", serif';
        ctx.strokeStyle = GOLD; ctx.lineWidth = 2; rr(ctx, tx - 92, ty - 20, 184, 36, 4); ctx.stroke();
        ctx.fillStyle = GOLD; ctx.fillText('唱片墙上有这首', tx, ty + 6);
      }
      // 底栏
      ctx.strokeStyle = 'rgba(255,255,255,0.14)'; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.moveTo(70, H - 150); ctx.lineTo(W - 70, H - 150); ctx.stroke();
      ctx.textAlign = 'left'; ctx.fillStyle = CREAM;
      ctx.font = '400 40px "EB Garamond", Georgia, serif';
      spaced(ctx, 'POLSKI FM', 70, H - 86, 10);
      ctx.fillStyle = DIM; ctx.font = '400 24px "Noto Serif SC", "EB Garamond", serif';
      ctx.fillText('冬的电台 · 听不懂也好听', 70, H - 48);
      ctx.textAlign = 'right';
      ctx.fillStyle = RED; ctx.beginPath(); ctx.arc(W - 70 - 184, H - 94, 7, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = CREAM; ctx.font = '400 24px "EB Garamond", Georgia, serif';
      spaced(ctx, 'ON AIR', W - 70, H - 86, 5);
      ctx.fillStyle = DIM; ctx.font = '400 20px "EB Garamond", Georgia, serif';
      ctx.fillText('dxwintersun.github.io/WinterSunBlog/radio', W - 70, H - 48);
      done(cv);
    }
    function blankCover() {
      var h = hue(d.band || d.who);
      var gg = ctx.createLinearGradient(cxp, cyp, cxp + cs, cyp + cs);
      gg.addColorStop(0, 'hsl(' + h + ' 45% 48%)'); gg.addColorStop(1, 'hsl(' + ((h + 30) % 360) + ' 55% 32%)');
      ctx.save(); rr(ctx, cxp, cyp, cs, cs, 18); ctx.fillStyle = gg; ctx.fill(); ctx.restore();
      ctx.fillStyle = 'rgba(255,255,255,0.9)'; ctx.textAlign = 'center';
      ctx.font = '400 150px "EB Garamond", Georgia, serif';
      ctx.fillText((d.bandName || d.who || '♪').slice(0, 2).toUpperCase(), W / 2, cyp + cs / 2 + 52);
      afterCover();
    }
    ctx.save();
    ctx.shadowColor = 'rgba(0,0,0,0.55)'; ctx.shadowBlur = 40; ctx.shadowOffsetY = 18;
    rr(ctx, cxp, cyp, cs, cs, 18); ctx.fillStyle = '#0f1218'; ctx.fill();
    ctx.restore();
    if (!d.thumb) { blankCover(); return; }
    // YouTube 的缩略图：16:9 的（mqdefault / maxresdefault）方形专辑图正好占中间一个正方形；
    // 4:3 的（hqdefault）还多两道黑边，中间那块只有 宽×9/16 那么高。先试高清，没有就退回列表那张。
    var tries = [d.thumb.replace(/\/(mq|hq|sd)default\.jpg/, '/maxresdefault.jpg'), d.thumb];
    (function load(i) {
      if (i >= tries.length) { blankCover(); return; }
      var img = new Image();
      img.crossOrigin = 'anonymous';
      img.onload = function () {
        var w = img.naturalWidth, h = img.naturalHeight;
        if (w < 200) { load(i + 1); return; }               // 没有高清图时 YouTube 给一张 120×90 的占位
        try {
          var s = (w / h > 1.5) ? h : Math.round(w * 9 / 16);
          var sx = (w - s) / 2, sy = (h - s) / 2;
          ctx.save(); rr(ctx, cxp, cyp, cs, cs, 18); ctx.clip();
          ctx.drawImage(img, sx, sy, s, s, cxp, cyp, cs, cs);
          ctx.restore();
          afterCover();
        } catch (e) { blankCover(); }
      };
      img.onerror = function () { load(i + 1); };
      img.src = tries[i];
    })(0);
  }
  // 拉开字距画一行字（canvas 没有 letter-spacing 的老浏览器也行）
  function spaced(ctx, text, x, y, gap) {
    var align = ctx.textAlign, total = 0, i;
    for (i = 0; i < text.length; i++) total += ctx.measureText(text[i]).width + (i < text.length - 1 ? gap : 0);
    var cx = align === 'right' ? x - total : align === 'center' ? x - total / 2 : x;
    ctx.textAlign = 'left';
    for (i = 0; i < text.length; i++) { ctx.fillText(text[i], cx, y); cx += ctx.measureText(text[i]).width + gap; }
    ctx.textAlign = align;
  }

  function show(cv, d) {
    var url = cv.toDataURL('image/png');
    var ov = document.createElement('div');
    ov.className = 'c-tk-saved';
    ov.setAttribute('role', 'dialog');
    ov.setAttribute('aria-label', '这首歌的卡片');
    var name = ('Polski FM · ' + d.title + (d.who ? ' · ' + d.who : '')).replace(/[\\/:*?"<>|]+/g, ' ').trim();
    ov.innerHTML = '<img alt="歌曲卡片" src="' + url + '"><p>手机：长按图片存到相册 · 电脑：点「下载」</p>' +
      '<div class="c-tk-saved__row"><a class="is-primary" download="' + name + '.png" href="' + url + '">下载</a><button type="button">关掉</button></div>';
    ov.addEventListener('click', function (e) { if (e.target === ov || e.target.tagName === 'BUTTON') ov.remove(); });
    document.addEventListener('keydown', function esc(e) { if (e.key === 'Escape') { ov.remove(); document.removeEventListener('keydown', esc); } });
    document.body.appendChild(ov);
  }

  function make(row, cb) {
    var d = rowData(row);
    var fonts = document.fonts ? Promise.all([
      document.fonts.load('600 64px "EB Garamond"'), document.fonts.load('italic 36px "EB Garamond"'),
      document.fonts.load('400 24px "Noto Serif SC"')
    ]).catch(function () {}) : Promise.resolve();
    fonts.then(function () { draw(d, function (cv) { cb(cv, d); }); });
  }

  root.addEventListener('click', function (e) {
    var btn = e.target.closest && e.target.closest('.c-radio__save');
    if (!btn) return;
    e.preventDefault();
    var row = btn.closest('.c-radio__row');
    if (!row) return;
    btn.disabled = true;
    make(row, function (cv, d) { btn.disabled = false; show(cv, d); });
  });
  // 给自检用：window.__radioCard(0, function(dataUrl){})
  window.__radioCard = function (i, cb) {
    var row = root.querySelectorAll('.c-radio__row')[i || 0];
    make(row, function (cv) { cb(cv.toDataURL('image/png')); });
  };
})();
