/* =============================================================
   下雪 ❄ —— Winter 2026-09-23 拍板的规格
   -------------------------------------------------------------
   · 只在「标题那块」（每个 .c-hero）里下，正文一片雪都没有——
     字上面飘东西会看不下去。
   · 是个开关：点标题区的空白处，或点右上角那朵小雪花，雪就停；
     再点一下继续下。选择记在本机（localStorage: wiw-snow），
     下次进来还是这个样子。
   · 系统里开了「减少动画」就只静静落一层，不飘。
   · 顺带管页脚 / 404 页那个小雪人：戳一下他会抖、帽子会飞起来。
   ============================================================= */
(function () {
  'use strict';

  var KEY = 'wiw-snow';
  var reduce = !!(window.matchMedia &&
                  window.matchMedia('(prefers-reduced-motion: reduce)').matches);

  var snowing = true;
  try { snowing = localStorage.getItem(KEY) !== 'off'; } catch (e) {}

  var scenes = [];   // { hero, canvas, ctx, w, h, flakes, dpr }
  var raf = null;

  // ── 一片雪 ──────────────────────────────────────────────────
  function makeFlake(w, h, fromTop) {
    return {
      x: Math.random() * w,
      y: fromTop ? -Math.random() * h * 0.3 : Math.random() * h,
      r: 0.9 + Math.random() * 2.2,
      fall: 0.16 + Math.random() * 0.5,
      drift: Math.random() * Math.PI * 2,
      sway: 0.2 + Math.random() * 0.8,
      alpha: 0.35 + Math.random() * 0.5
    };
  }

  function density(w, h) {
    // 「偶尔飘几片」那一档：一个 1180×320 的标题区大约 27 片。
    return Math.max(8, Math.min(90, Math.round(w * h / 14000)));
  }

  // 标题区再高（404 页、系列首页那种），雪也只落在最上面这一带，
  // 免得飘到正文上——Winter：「正文不要飘雪」。
  var BAND = 420;

  function measure(sc) {
    var r = sc.hero.getBoundingClientRect();
    if (!r.width || !r.height) return false;
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    sc.w = r.width;
    sc.h = Math.min(r.height, BAND);
    sc.canvas.style.height = sc.h + 'px';
    sc.dpr = dpr;
    sc.canvas.width  = Math.round(sc.w * dpr);
    sc.canvas.height = Math.round(sc.h * dpr);
    sc.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    var want = density(sc.w, sc.h);
    while (sc.flakes.length < want) sc.flakes.push(makeFlake(sc.w, sc.h, false));
    if (sc.flakes.length > want) sc.flakes.length = want;
    return true;
  }

  // 雪的颜色跟着当前配色走：浅色主题下用主色（站点默认是淡淡的冰蓝，
  // AU 系列页则是那个系列自己的颜色），暗色主题下用接近白的雪色。
  //
  // ⚠️ 不能直接去读 --rgb-accent：AU 系列页（_includes/au-palette-style.html）
  // 只改了 --c-accent，没有对应的 rgb 三元组，读出来永远是站点默认的蓝，
  // 于是粉色的系列页上会飘蓝雪。改成「量」开关按钮真正渲染出来的颜色——
  // 不管底下写的是 hex 还是 color-mix()，getComputedStyle 都会还原成 rgb()。
  var probe = null;
  function flakeColor() {
    var dt = document.documentElement.getAttribute('data-theme');
    var dark = dt === 'dark' ||
      (!dt && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
    if (dark) return 'rgb(233, 241, 247)';
    if (probe) {
      var c = getComputedStyle(probe).color;
      if (c && c.indexOf('rgb') === 0) return c;
    }
    return 'rgb(44, 128, 169)';
  }

  function withAlpha(rgb, a) {
    var m = rgb.match(/rgba?\(([^)]+)\)/);
    if (!m) return rgb;
    var parts = m[1].split(',');
    return 'rgba(' + parts[0] + ',' + parts[1] + ',' + parts[2] + ',' + a.toFixed(3) + ')';
  }

  var COLOR = 'rgb(44, 128, 169)';

  function paint(sc) {
    var ctx = sc.ctx;
    ctx.clearRect(0, 0, sc.w, sc.h);
    if (!snowing) return;
    for (var i = 0; i < sc.flakes.length; i++) {
      var f = sc.flakes[i];
      ctx.beginPath();
      ctx.arc(f.x, f.y, f.r, 0, Math.PI * 2);
      ctx.fillStyle = withAlpha(COLOR, f.alpha);
      ctx.fill();
    }
  }

  function live(sc) {
    return sc.hero.offsetParent !== null && sc.hero.offsetHeight > 0;
  }

  function tick() {
    raf = null;
    if (!snowing) return;
    var any = false;
    for (var s = 0; s < scenes.length; s++) {
      var sc = scenes[s];
      if (!live(sc)) continue;
      any = true;
      if (!sc.w || !sc.h) { if (!measure(sc)) continue; }
      for (var i = 0; i < sc.flakes.length; i++) {
        var f = sc.flakes[i];
        f.drift += 0.009;
        f.y += f.fall;
        f.x += Math.sin(f.drift) * f.sway * 0.55;
        if (f.y - f.r > sc.h) { f.y = -f.r; f.x = Math.random() * sc.w; }
        if (f.x < -8) f.x = sc.w + 8;
        if (f.x > sc.w + 8) f.x = -8;
      }
      paint(sc);
    }
    if (any || scenes.length) raf = requestAnimationFrame(tick);
  }

  function start() {
    if (reduce) { scenes.forEach(function (sc) { if (live(sc)) { measure(sc); paint(sc); } }); return; }
    if (!raf) raf = requestAnimationFrame(tick);
  }

  function stop() {
    if (raf) { cancelAnimationFrame(raf); raf = null; }
    scenes.forEach(function (sc) { sc.ctx.clearRect(0, 0, sc.w || 0, sc.h || 0); });
  }

  function setSnowing(next) {
    snowing = next;
    try { localStorage.setItem(KEY, next ? 'on' : 'off'); } catch (e) {}
    document.documentElement.setAttribute('data-snow', next ? 'on' : 'off');
    scenes.forEach(function (sc) {
      sc.toggle.setAttribute('aria-pressed', next ? 'true' : 'false');
      sc.toggle.setAttribute('title', next ? '让雪停下来' : '让它再下起来');
      sc.toggle.setAttribute('aria-label', next ? '让雪停下来' : '让它再下起来');
    });
    if (next) start(); else stop();
  }

  // ── 装进每一个标题区 ────────────────────────────────────────
  function build() {
    var heroes = document.querySelectorAll('.c-hero');
    if (!heroes.length) return;

    Array.prototype.forEach.call(heroes, function (hero) {
      if (hero.getAttribute('data-snow-ready')) return;
      hero.setAttribute('data-snow-ready', '1');

      var canvas = document.createElement('canvas');
      canvas.className = 'c-snow';
      canvas.setAttribute('aria-hidden', 'true');
      hero.insertBefore(canvas, hero.firstChild);

      var toggle = document.createElement('button');
      toggle.type = 'button';
      toggle.className = 'c-snow-toggle';
      toggle.innerHTML =
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" ' +
        'stroke-linecap="round" aria-hidden="true" focusable="false">' +
        '<path d="M12 2v20M3.5 7l17 10M20.5 7l-17 10M12 6.4l-2.6-2.6M12 6.4l2.6-2.6' +
        'M12 17.6l-2.6 2.6M12 17.6l2.6 2.6M7.2 9.1l-3.5.5M7.2 14.9l-3.5-.5' +
        'M16.8 9.1l3.5.5M16.8 14.9l3.5-.5"/></svg>';
      hero.appendChild(toggle);

      var sc = {
        hero: hero, canvas: canvas, ctx: canvas.getContext('2d'),
        toggle: toggle, w: 0, h: 0, dpr: 1, flakes: []
      };
      scenes.push(sc);
      if (!probe) { probe = toggle; COLOR = flakeColor(); }

      toggle.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        setSnowing(!snowing);
      });

      // 点标题区的空白处也能让雪停——但不能抢走链接和按钮的点击。
      hero.addEventListener('click', function (e) {
        if (e.target.closest('a, button, input, select, textarea, [role="button"]')) return;
        if (window.getSelection && String(window.getSelection())) return; // 正在选字
        setSnowing(!snowing);
      });
    });

    var resizeTimer = null;
    window.addEventListener('resize', function () {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(function () {
        scenes.forEach(function (sc) { if (live(sc)) measure(sc); });
        if (reduce) scenes.forEach(function (sc) { if (live(sc)) paint(sc); });
      }, 180);
    });

    // 首页切换标签会换一个标题区出来，新露面的那个要量一遍尺寸。
    new MutationObserver(function () {
      scenes.forEach(function (sc) { if (live(sc) && !sc.w) measure(sc); });
      if (reduce) scenes.forEach(function (sc) { if (live(sc)) paint(sc); });
    }).observe(document.documentElement, {
      attributes: true, attributeFilter: ['data-hero-active']
    });

    // 换了昼夜或换了心情色，雪的颜色也跟着换。
    new MutationObserver(function () {
      COLOR = flakeColor();
    }).observe(document.documentElement, {
      attributes: true, attributeFilter: ['data-theme', 'style']
    });

    setSnowing(snowing);
  }

  // ── 戳雪人 ⛄ ───────────────────────────────────────────────
  function snowmen() {
    Array.prototype.forEach.call(document.querySelectorAll('.c-snowman'), function (man) {
      man.addEventListener('click', function () {
        man.classList.remove('is-poked');
        void man.offsetWidth;          // 强制重排，连着戳才每次都动
        man.classList.add('is-poked');
      });
      man.addEventListener('animationend', function () {
        man.classList.remove('is-poked');
      });
    });
  }

  function init() { build(); snowmen(); }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
