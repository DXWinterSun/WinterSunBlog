(function () {
  'use strict';

  var STORAGE_KEY = 'wiw-palette';

  // ── Color utilities ──────────────────────────────────────────────────────

  function hexToRgb(hex) {
    return parseInt(hex.slice(1,3),16)+', '+parseInt(hex.slice(3,5),16)+', '+parseInt(hex.slice(5,7),16);
  }

  // Mirrors CSS color-mix(in srgb, hex1 pct%, hex2)
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

  // ── Theme definitions — Many Faces of Sam ────────────────────────────────
  // accent/bg/text/muted pulled directly from the gallery's palette data.

  var THEMES = [
    { id:'gary',     name:'Gary',       accent:'#cba14c', bg:'#14110d', text:'#ede2d0', muted:'#8a7558' },
    { id:'kris',     name:'Kris',       accent:'#bc4d3a', bg:'#11161c', text:'#ece0d2', muted:'#62768d' },
    { id:'matty',    name:'Matty',      accent:'#d49850', bg:'#171d24', text:'#ebe0cc', muted:'#7d7264' },
    { id:'buck',     name:'Buck',       accent:'#b8c878', bg:'#1a2418', text:'#e8eed8', muted:'#7a8868' },
    { id:'trent',    name:'Trent',      accent:'#79a7bd', bg:'#141c12', text:'#dce5ea', muted:'#7a7654' },
    { id:'samuel',   name:'Samuel',     accent:'#c5402f', bg:'#211a0f', text:'#f0e2d4', muted:'#a08770' },
    { id:'jerry',    name:'Jerry',      accent:'#d7a83c', bg:'#20120c', text:'#f0e0d0', muted:'#a07060' },
    { id:'wildbill', name:'Wild Bill',  accent:'#b0803e', bg:'#1b1510', text:'#ece0d0', muted:'#93826a' },
    { id:'guy',      name:'Guy',        accent:'#43b3bf', bg:'#0f161a', text:'#dfe7ea', muted:'#738088' },
    { id:'knox',     name:'Knox',       accent:'#d94040', bg:'#1b1310', text:'#ede0e0', muted:'#8d6e62' },
    { id:'pero',     name:'Pero',       accent:'#d49858', bg:'#1a1612', text:'#ede0cc', muted:'#8a7458' },
    { id:'chuck',    name:'Chuck',      accent:'#de6e8e', bg:'#15182a', text:'#ede4d0', muted:'#8088a0' },
    { id:'mercer',   name:'Mercer',     accent:'#e08a2e', bg:'#1a1410', text:'#ede0e6', muted:'#8d7462' },
    { id:'crocker',  name:'Crocker',    accent:'#d8b25a', bg:'#161214', text:'#f0e3dc', muted:'#8d6278' },
    { id:'zaphod',   name:'Zaphod',     accent:'#d4a82a', bg:'#0b0a12', text:'#e8e4d0', muted:'#8a7a48' },
    { id:'brad',     name:'Brad',       accent:'#c9d84e', bg:'#1c2230', text:'#e8eadc', muted:'#7a8590' },
    { id:'glenn',    name:'Glenn',      accent:'#b8d0e0', bg:'#1c2030', text:'#dce4ea', muted:'#7a8090' },
    { id:'reston',   name:'Reston',     accent:'#d89858', bg:'#1f1814', text:'#ebe0cc', muted:'#8a7458' },
    { id:'victor',   name:'Victor',     accent:'#d2a24a', bg:'#2a1820', text:'#f0e0d4', muted:'#9a7868' },
    { id:'sambell',  name:'Sam Bell',   accent:'#7eb0d5', bg:'#162038', text:'#e8eef5', muted:'#6a85a3' },
    { id:'goode',    name:'Goode',      accent:'#cc4436', bg:'#211910', text:'#ede4d4', muted:'#9a7e58' },
    { id:'hammer',   name:'Hammer',     accent:'#4a87ee', bg:'#13151c', text:'#e7eaf2', muted:'#7c8aa6' },
    { id:'kenny',    name:'Kenny',      accent:'#d08a45', bg:'#1c1e1f', text:'#f0e0d4', muted:'#627f8d' },
    { id:'billy',    name:'Billy',      accent:'#d63a33', bg:'#281208', text:'#f5e6d0', muted:'#b07840' },
    { id:'owen',     name:'Owen',       accent:'#35bfc9', bg:'#15282e', text:'#dce9ea', muted:'#75899a' },
    { id:'johnmoon', name:'J. Moon',    accent:'#8fa0b0', bg:'#14181f', text:'#dce3ea', muted:'#62728d' },
    { id:'varney',   name:'Varney',     accent:'#e6ecea', bg:'#1e1408', text:'#dceae5', muted:'#8d7a62' },
    { id:'wayne',    name:'Wayne',      accent:'#c8a050', bg:'#1e2418', text:'#e8e4d0', muted:'#8a7a48' },
    { id:'craig',    name:'Craig',      accent:'#c89060', bg:'#241a14', text:'#ede0d0', muted:'#a07858' },
    { id:'munch',    name:'Munch',      accent:'#e23b2e', bg:'#14241a', text:'#eed9d8', muted:'#628d72' },
    { id:'dixon',    name:'Dixon',      accent:'#e2622a', bg:'#241015', text:'#f5e6d3', muted:'#8d626d' },
    { id:'eddie',    name:'Eddie',      accent:'#2e9fd4', bg:'#1a1f24', text:'#dce5ea', muted:'#7a8088' },
    { id:'bush',     name:'G.W. Bush',  accent:'#c98a3e', bg:'#16181e', text:'#f1e3cb', muted:'#626d8d' },
    { id:'klenz',    name:'Klenz.',     accent:'#d34338', bg:'#14241c', text:'#ede8d8', muted:'#8b7d4d' },
    { id:'bryant',   name:'Bryant',     accent:'#c8783c', bg:'#1c1410', text:'#ede0d0', muted:'#8a6848' },
    { id:'mrwolf',   name:'Mr. Wolf',   accent:'#dfb23c', bg:'#14161d', text:'#ede6d8', muted:'#7a7d8a' },
    { id:'stoppard', name:'Stoppard',   accent:'#c7995a', bg:'#1a1f2c', text:'#ebe2d4', muted:'#7c8090' },
    { id:'wilde',    name:'Wilde',      accent:'#cda24f', bg:'#15192a', text:'#ebe2d0', muted:'#7a7e90' },
    { id:'future',   name:'Future',     accent:'#d460a0', bg:'#1a0e2a', text:'#ede0ec', muted:'#8868a0' },
  ];

  // ── Color derivation — mirrors au-palette-style.html exactly ─────────────
  // Light: accent-tinted warm cream base (via colorMix)
  // Dark:  character's own deep bg + full-saturation accent

  var LB   = '#f6f2ea';   // light base bg
  var LBS  = '#faf6ef';   // light base bg-soft
  var LP   = '#fdfbf6';   // light paper
  var DTINT = '#1a1614';  // dark tint for lightening accent on light bg

  function lightVars(p) {
    var bg     = colorMix(p.accent, 18, LB);
    var bgSoft = colorMix(p.accent, 12, LBS);
    var paper  = colorMix(p.accent,  7, LP);
    var accent = colorMix(p.accent, 70, DTINT);  // color-mix(accent, #1a1614 30%)
    var acSoft = colorMix(p.accent, 78, DTINT);  // color-mix(accent, #1a1614 22%)
    var acDark = colorMix(p.accent, 58, '#000000'); // color-mix(accent, #000 42%)
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
    // Neutral dark bg for custom hue in dark mode (the default dark)
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

  // ── UI ────────────────────────────────────────────────────────────────────
  // Trigger lives in header.html; we only build the panel here.

  function buildUI() {
    var trigger = document.getElementById('js-palette-trigger');

    var panel = document.createElement('div');
    panel.className = 'c-palette-panel';
    panel.id = 'js-palette-panel';
    panel.setAttribute('role', 'dialog');
    panel.setAttribute('aria-label', '配色主题');
    panel.setAttribute('aria-hidden', 'true');

    // Swatch grid — dark bg + accent chip so it reads like the gallery
    var grid = '';
    THEMES.forEach(function (t) {
      grid += '<button class="c-palette-swatch" data-theme-id="' + t.id + '" aria-label="' + t.name + '">' +
        '<span class="c-palette-swatch__chip" style="--sw-bg:' + t.bg + ';--sw-ac:' + t.accent + '"></span>' +
        '<span class="c-palette-swatch__name">' + t.name + '</span>' +
        '</button>';
    });

    panel.innerHTML =
      '<div class="c-palette-panel__inner">' +
        '<div class="c-palette-panel__header">' +
          '<span class="c-palette-panel__title">换个心情</span>' +
          '<button class="c-palette-panel__close" id="js-palette-close" aria-label="关闭">✕</button>' +
        '</div>' +
        '<section class="c-palette-section">' +
          '<p class="c-palette-section__label">Many Faces · 角色配色</p>' +
          '<div class="c-palette-grid" id="js-palette-grid">' + grid + '</div>' +
        '</section>' +
        '<section class="c-palette-section">' +
          '<p class="c-palette-section__label">自定义强调色</p>' +
          '<div class="c-palette-custom">' +
            '<input type="range" class="c-palette-hue" id="js-palette-hue" min="0" max="359" value="0" aria-label="色相">' +
            '<div class="c-palette-custom__preview" id="js-palette-preview"></div>' +
          '</div>' +
          '<p class="c-palette-section__hint">仅调整强调色，背景保持中性</p>' +
        '</section>' +
        '<button class="c-palette-panel__reset" id="js-palette-reset">还原默认配色</button>' +
      '</div>';

    document.body.appendChild(panel);
    return { trigger: trigger, panel: panel };
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

  function initEvents(trigger, panel) {
    var open = false;

    function openPanel()  {
      open = true;
      panel.classList.add('is-open');
      panel.setAttribute('aria-hidden', 'false');
      trigger.setAttribute('aria-expanded', 'true');
      updateSwatchStates();
    }
    function closePanel() {
      open = false;
      panel.classList.remove('is-open');
      panel.setAttribute('aria-hidden', 'true');
      trigger.setAttribute('aria-expanded', 'false');
    }

    trigger.addEventListener('click', function (e) { e.stopPropagation(); open ? closePanel() : openPanel(); });
    document.getElementById('js-palette-close').addEventListener('click', closePanel);
    document.addEventListener('click', function (e) {
      if (open && !panel.contains(e.target) && e.target !== trigger) closePanel();
    });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && open) closePanel(); });

    document.getElementById('js-palette-grid').addEventListener('click', function (e) {
      var btn = e.target.closest('[data-theme-id]');
      if (!btn) return;
      var state = { type: 'preset', id: btn.getAttribute('data-theme-id') };
      applyState(state);
      saveState(state);
      updateSwatchStates();
      var sl = document.getElementById('js-palette-hue');
      if (sl) { sl.value = 0; updateHuePreview(0); }
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

    document.getElementById('js-palette-reset').addEventListener('click', function () {
      clearVars();
      saveState(null);
      updateSwatchStates();
      hueSlider.value = 0;
      updateHuePreview(0);
    });
  }

  // ── Init ──────────────────────────────────────────────────────────────────

  function init() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      if (raw) { currentState = JSON.parse(raw); applyState(currentState); }
    } catch (e) {}

    var ui = buildUI();
    initEvents(ui.trigger, ui.panel);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
