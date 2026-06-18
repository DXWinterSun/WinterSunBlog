(function () {
  'use strict';

  var STORAGE_KEY = 'wiw-palette';
  var FAV_KEY     = 'wiw-palette-favs';
  var MAX_FAVS    = 5;

  // ── Color utilities ──────────────────────────────────────────────────────

  function hexToRgb(hex) {
    return parseInt(hex.slice(1,3),16)+', '+parseInt(hex.slice(3,5),16)+', '+parseInt(hex.slice(5,7),16);
  }

  function colorMix(hex1, pct, hex2) {
    var p=pct/100, q=1-p;
    var r1=parseInt(hex1.slice(1,3),16), g1=parseInt(hex1.slice(3,5),16), b1=parseInt(hex1.slice(5,7),16);
    var r2=parseInt(hex2.slice(1,3),16), g2=parseInt(hex2.slice(3,5),16), b2=parseInt(hex2.slice(5,7),16);
    function m(a,b){return Math.round(a*p+b*q).toString(16).padStart(2,'0');}
    return '#'+m(r1,r2)+m(g1,g2)+m(b1,b2);
  }

  function hslToHex(h, s, l) {
    s/=100; l/=100;
    var a=s*Math.min(l,1-l);
    function f(n){var k=(n+h/30)%12,c=l-a*Math.max(Math.min(k-3,9-k,1),-1);return Math.round(255*c).toString(16).padStart(2,'0');}
    return '#'+f(0)+f(8)+f(4);
  }

  // ── Theme definitions — loaded from _data/sam_themes.yml via sam-themes-data.js
  var THEMES = window.__SAM_THEMES || [];

  // ── Color derivation — mirrors au-palette-style.html exactly ─────────────

  var LB   = '#f6f2ea';
  var LBS  = '#faf6ef';
  var LP   = '#fdfbf6';
  var DTINT = '#1a1614';

  function lightVars(p) {
    var bg     = colorMix(p.accent, 30, LB);
    var bgSoft = colorMix(p.accent, 20, LBS);
    var paper  = colorMix(p.accent, 13, LP);
    var accent = colorMix(p.accent, 70, DTINT);
    var acSoft = colorMix(p.accent, 78, DTINT);
    var acDark = colorMix(p.accent, 58, '#000000');
    return {
      '--c-bg': bg, '--c-bg-soft': bgSoft, '--c-paper': paper,
      '--c-ink': '#2b2620', '--c-ink-soft': '#4a443c',
      '--c-muted': '#847a6d', '--c-muted-soft': '#a59a8a',
      '--c-line': 'rgba(0,0,0,.10)', '--c-line-strong': 'rgba(0,0,0,.16)',
      '--c-accent': accent, '--c-accent-soft': acSoft, '--c-accent-dark': acDark,
      '--c-status-red': '#c0594a', '--c-status-green': '#6b8a5b',
      '--rgb-accent': hexToRgb(accent),
      '--rgb-bg': hexToRgb(bg),
      '--rgb-paper': hexToRgb(paper),
      '--rgb-shadow': '43, 38, 32',
      '--rgb-line-warm': hexToRgb(colorMix(p.accent, 14, '#d4c4b0'))
    };
  }

  function darkVars(p) {
    return {
      '--c-bg': p.bg, '--c-bg-soft': p.bg, '--c-paper': p.bg,
      '--c-ink': p.text, '--c-ink-soft': p.text,
      '--c-muted': p.muted, '--c-muted-soft': p.muted,
      '--c-line': 'rgba(255,255,255,.10)', '--c-line-strong': 'rgba(255,255,255,.20)',
      '--c-accent': p.accent, '--c-accent-soft': p.accent, '--c-accent-dark': p.accent,
      '--c-status-red': '#c06868', '--c-status-green': '#6a9460',
      '--rgb-accent': hexToRgb(p.accent),
      '--rgb-bg': hexToRgb(p.bg),
      '--rgb-paper': hexToRgb(p.bg),
      '--rgb-shadow': '0, 0, 0',
      '--rgb-line-warm': hexToRgb(p.bg)
    };
  }

  var ALL_VARS = [
    '--c-bg','--c-bg-soft','--c-paper',
    '--c-ink','--c-ink-soft','--c-muted','--c-muted-soft',
    '--c-line','--c-line-strong',
    '--c-accent','--c-accent-soft','--c-accent-dark',
    '--c-status-red','--c-status-green',
    '--rgb-accent','--rgb-bg','--rgb-paper','--rgb-shadow','--rgb-line-warm'
  ];

  // ── Apply helpers ─────────────────────────────────────────────────────────

  function applyVars(vars) {
    var root = document.documentElement;
    for (var k in vars) root.style.setProperty(k, vars[k]);
  }

  function clearVars() {
    var root = document.documentElement;
    ALL_VARS.forEach(function (k) { root.style.removeProperty(k); });
  }

  function isDark() {
    var dt = document.documentElement.getAttribute('data-theme');
    if (dt === 'dark') return true;
    if (dt === 'light') return false;
    return !!(window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
  }

  function buildVars(p) {
    return isDark() ? darkVars(p) : lightVars(p);
  }

  // ── State ─────────────────────────────────────────────────────────────────

  var currentState = null;

  function saveState(state) {
    currentState = state;
    try { localStorage.setItem(STORAGE_KEY, state ? JSON.stringify(state) : ''); } catch (e) {}
  }

  function applyState(state) {
    if (!state) { clearVars(); return; }
    if (state.type === 'preset') {
      var t = THEMES.filter(function (x) { return x.id === state.id; })[0];
      if (!t) { clearVars(); return; }
      applyVars(buildVars(t));
    } else if (state.type === 'custom') {
      applyCustomHue(state.hue, false);
    }
  }

  function applyCustomHue(hue, save) {
    var s = isDark() ? 62 : 58;
    var l = isDark() ? 65 : 47;
    var fakeTheme = {
      accent: hslToHex(hue, s, l),
      bg: '#1a1815', text: '#efe8da', muted: '#948a7c'
    };
    clearVars();
    applyVars(buildVars(fakeTheme));
    if (save !== false) saveState({ type: 'custom', hue: hue });
  }

  // ── Dark mode observation ─────────────────────────────────────────────────

  var hueSliderEl = null;

  function onModeChange() {
    applyState(currentState);
    if (hueSliderEl) updateHuePreview(parseInt(hueSliderEl.value, 10));
  }

  new MutationObserver(function (ms) {
    ms.forEach(function (m) { if (m.attributeName === 'data-theme') onModeChange(); });
  }).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });

  if (window.matchMedia) {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function () {
      if (!document.documentElement.getAttribute('data-theme')) onModeChange();
    });
  }

  // ── Favorites ─────────────────────────────────────────────────────────────

  function loadFavs() {
    try { return JSON.parse(localStorage.getItem(FAV_KEY) || '[]'); } catch (e) { return []; }
  }

  function saveFavs(favs) {
    try { localStorage.setItem(FAV_KEY, JSON.stringify(favs)); } catch (e) {}
  }

  function addFav(hue) {
    var s = isDark() ? 62 : 58, l = isDark() ? 65 : 47;
    var hex = hslToHex(hue, s, l);
    var favs = loadFavs().filter(function (f) { return f.hue !== hue; });
    favs.unshift({ hue: hue, hex: hex });
    if (favs.length > MAX_FAVS) favs = favs.slice(0, MAX_FAVS);
    saveFavs(favs);
    renderFavs();
  }

  function renderFavs() {
    var container = document.getElementById('js-palette-favs');
    if (!container) return;
    var favs = loadFavs();
    container.innerHTML = favs.map(function (f) {
      return '<button class="c-palette-fav" data-hue="' + f.hue + '" title="应用此色" style="background:' + f.hex + '"></button>';
    }).join('');
    container.querySelectorAll('.c-palette-fav').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var hue = parseInt(this.getAttribute('data-hue'), 10);
        applyCustomHue(hue, true);
        var sl = document.getElementById('js-palette-hue');
        if (sl) { sl.value = hue; updateHuePreview(hue); }
        updateSwatchStates();
      });
    });
  }

  // ── Heartbeat animation on the trigger button ────────────────────────────

  function heartbeat() {
    var trigger = document.getElementById('js-palette-trigger');
    if (!trigger) return;
    trigger.classList.remove('is-beating');
    void trigger.offsetWidth; // force reflow so animation restarts
    trigger.classList.add('is-beating');
    trigger.addEventListener('animationend', function onEnd() {
      trigger.classList.remove('is-beating');
      trigger.removeEventListener('animationend', onEnd);
    });
  }

  // ── UI ────────────────────────────────────────────────────────────────────

  var PERFS = '<i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i>';

  function buildUI() {
    var trigger  = document.getElementById('js-palette-trigger');
    var baseurl  = trigger ? (trigger.getAttribute('data-baseurl') || '') : '';
    var galleryHref = baseurl + '/sam/many-faces/';

    var overlay = document.createElement('div');
    overlay.className = 'c-palette-overlay';
    overlay.id = 'js-palette-overlay';
    overlay.setAttribute('aria-hidden', 'true');

    var cards = '';
    THEMES.forEach(function (t) {
      var charHref = baseurl + '/sam/many-faces/#' + (t.anchor || t.id);
      cards +=
        '<button class="c-palette-card" data-theme-id="' + t.id + '" aria-label="' + t.cn + ' · ' + t.name + '"' +
          ' style="--card-bg:' + t.bg + ';--card-ac:' + t.accent + '">' +
          '<span class="c-palette-card__perfs">' + PERFS + '</span>' +
          '<span class="c-palette-card__body">' +
            '<span class="c-palette-card__dot"></span>' +
            '<span class="c-palette-card__cn">' + t.cn + '</span>' +
            '<span class="c-palette-card__en">' + t.en + '</span>' +
            '<span class="c-palette-card__sep"></span>' +
            '<span class="c-palette-card__bg-cn">' + t.bg_cn + '</span>' +
            '<span class="c-palette-card__bg-en">' + t.bg_en + '</span>' +
            '<a class="c-palette-card__char" href="' + charHref + '" target="_blank" rel="noopener" tabindex="-1">' + t.name + '</a>' +
          '</span>' +
          '<span class="c-palette-card__perfs">' + PERFS + '</span>' +
        '</button>';
    });

    overlay.innerHTML =
      '<div class="c-palette-modal" role="dialog" aria-label="配色主题 · 换个心情">' +
        '<div class="c-palette-modal__header">' +
          '<span class="c-palette-modal__title">' +
            '换个心情' +
            '<span class="c-palette-modal__subtitle">他走过银幕，停在你面前 · <a class="c-palette-modal__gallery-link" href="' + galleryHref + '" target="_blank" rel="noopener">Many Faces ↗</a></span>' +
          '</span>' +
          '<button class="c-palette-modal__close" id="js-palette-close" aria-label="关闭">✕</button>' +
        '</div>' +
        '<div class="c-palette-modal__body">' +
          '<div class="c-palette-cards" id="js-palette-grid">' + cards + '</div>' +
        '</div>' +
        '<div class="c-palette-modal__footer">' +
          '<div class="c-palette-footer__left">' +
            '<span class="c-palette-footer__label">随心染色</span>' +
            '<div class="c-palette-favs" id="js-palette-favs"></div>' +
          '</div>' +
          '<input type="range" class="c-palette-hue" id="js-palette-hue" min="0" max="359" value="0" aria-label="自定义色相">' +
          '<div class="c-palette-custom__preview" id="js-palette-preview"></div>' +
          '<button class="c-palette-panel__save" id="js-palette-save" title="把这一刻的颜色藏起来" aria-label="收藏此色">♡</button>' +
          '<button class="c-palette-panel__reset" id="js-palette-reset">还原默认</button>' +
        '</div>' +
      '</div>';

    document.body.appendChild(overlay);
    return { trigger: trigger, overlay: overlay };
  }

  function updateHuePreview(hue) {
    var el = document.getElementById('js-palette-preview');
    if (!el) return;
    var s = isDark() ? 62 : 58, l = isDark() ? 65 : 47;
    el.style.backgroundColor = 'hsl(' + hue + ',' + s + '%,' + l + '%)';
  }

  function updateSwatchStates() {
    document.querySelectorAll('[data-theme-id]').forEach(function (sw) {
      var active = !!(currentState && currentState.type === 'preset' && currentState.id === sw.getAttribute('data-theme-id'));
      sw.classList.toggle('is-active', active);
    });
  }

  function initEvents(trigger, overlay) {
    var open = false;

    function openOverlay() {
      open = true;
      overlay.classList.add('is-open');
      overlay.setAttribute('aria-hidden', 'false');
      trigger.setAttribute('aria-expanded', 'true');
      document.body.style.overflow = 'hidden';
      updateSwatchStates();
      renderFavs();
    }
    function closeOverlay() {
      open = false;
      overlay.classList.remove('is-open');
      overlay.setAttribute('aria-hidden', 'true');
      trigger.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
    }

    trigger.addEventListener('click', function (e) { e.stopPropagation(); open ? closeOverlay() : openOverlay(); });
    document.getElementById('js-palette-close').addEventListener('click', closeOverlay);
    overlay.addEventListener('click', function (e) { if (e.target === overlay) closeOverlay(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && open) closeOverlay(); });

    document.getElementById('js-palette-grid').addEventListener('click', function (e) {
      var btn = e.target.closest('[data-theme-id]');
      if (!btn) return;
      var state = { type: 'preset', id: btn.getAttribute('data-theme-id') };
      applyState(state);
      saveState(state);
      updateSwatchStates();
      var sl = document.getElementById('js-palette-hue');
      if (sl) { sl.value = 0; updateHuePreview(0); }
      heartbeat();
    });

    var hueSlider = document.getElementById('js-palette-hue');
    hueSliderEl = hueSlider;

    if (currentState && currentState.type === 'custom') hueSlider.value = currentState.hue;
    updateHuePreview(parseInt(hueSlider.value, 10));

    hueSlider.addEventListener('input', function () {
      var hue = parseInt(this.value, 10);
      updateHuePreview(hue);
      applyCustomHue(hue, true);
      updateSwatchStates();
    });

    document.getElementById('js-palette-save').addEventListener('click', function () {
      var hue = parseInt(hueSlider.value, 10);
      addFav(hue);
      var btn = this;
      btn.textContent = '♥';
      btn.classList.add('is-saved');
      setTimeout(function () { btn.textContent = '♡'; btn.classList.remove('is-saved'); }, 1200);
    });

    document.getElementById('js-palette-reset').addEventListener('click', function () {
      clearVars();
      saveState(null);
      updateSwatchStates();
      hueSlider.value = 0;
      updateHuePreview(0);
    });

    document.addEventListener('click', function (e) {
      var btn = e.target.closest('[data-au-theme]');
      if (!btn) return;
      var id = btn.getAttribute('data-au-theme');
      var state = { type: 'preset', id: id };
      applyState(state);
      saveState(state);
      updateSwatchStates();
      heartbeat();
    });
  }

  // ── Init ──────────────────────────────────────────────────────────────────

  function init() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      if (raw) { currentState = JSON.parse(raw); applyState(currentState); }
    } catch (e) {}

    var ui = buildUI();
    initEvents(ui.trigger, ui.overlay);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
