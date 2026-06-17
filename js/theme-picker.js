(function () {
  'use strict';

  var STORAGE_KEY = 'wiw-palette';

  // ── Color utilities ──────────────────────────────────────────────────────

  function hexToRgb(hex) {
    return parseInt(hex.slice(1,3),16)+', '+parseInt(hex.slice(3,5),16)+', '+parseInt(hex.slice(5,7),16);
  }

  function hslToHex(h, s, l) {
    s /= 100; l /= 100;
    var a = s * Math.min(l, 1 - l);
    function f(n) {
      var k = (n + h / 30) % 12;
      var c = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1);
      return Math.round(255 * c).toString(16).padStart(2, '0');
    }
    return '#' + f(0) + f(8) + f(4);
  }

  // ── Theme definitions ────────────────────────────────────────────────────
  // Each theme has light + dark variants covering all CSS custom properties.

  var THEMES = [
    {
      id: 'rose', name: '冬日玫瑰', mood: '暖 · 默认',
      light: {
        bg:'#f7f3ec', bgSoft:'#fbf8f1', paper:'#ffffff',
        ink:'#1f1d1a', inkSoft:'#3d3833', muted:'#8a8074', mutedSoft:'#b6ac9d',
        line:'#e6dfd2', lineStrong:'#cfc6b4',
        accent:'#b85c5c', accentSoft:'#d3938b', accentDark:'#9c4848',
        statusRed:'#c0594a', statusGreen:'#6b8a5b'
      },
      dark: {
        bg:'#1a1815', bgSoft:'#211f1a', paper:'#24211d',
        ink:'#efe8da', inkSoft:'#c8c0b1', muted:'#948a7c', mutedSoft:'#6e665b',
        line:'#322e28', lineStrong:'#4a443c',
        accent:'#d97978', accentSoft:'#b06564', accentDark:'#f08e8d',
        statusRed:'#d97978', statusGreen:'#84a06f'
      }
    },
    {
      id: 'rain', name: '烟雨青瓦', mood: '凉 · 沉静',
      light: {
        bg:'#edf1f6', bgSoft:'#f2f5f9', paper:'#ffffff',
        ink:'#1a2028', inkSoft:'#2c3848', muted:'#6a7888', mutedSoft:'#9aa8b8',
        line:'#ccd4e0', lineStrong:'#b4c0d0',
        accent:'#4e7296', accentSoft:'#7a98b8', accentDark:'#365678',
        statusRed:'#b05050', statusGreen:'#5a8450'
      },
      dark: {
        bg:'#141820', bgSoft:'#1a2028', paper:'#1e242e',
        ink:'#dce8f4', inkSoft:'#a8b8cc', muted:'#6878a0', mutedSoft:'#4a5878',
        line:'#242c3c', lineStrong:'#344460',
        accent:'#7898c0', accentSoft:'#5878a0', accentDark:'#96b4d8',
        statusRed:'#c06868', statusGreen:'#6a9460'
      }
    },
    {
      id: 'amber', name: '暮色琥珀', mood: '暖 · 活泼',
      light: {
        bg:'#fdf5e8', bgSoft:'#fef9f0', paper:'#ffffff',
        ink:'#241a10', inkSoft:'#483420', muted:'#988060', mutedSoft:'#c4aa88',
        line:'#eaddc4', lineStrong:'#d8c8a8',
        accent:'#c07828', accentSoft:'#d89a58', accentDark:'#985a18',
        statusRed:'#c04a3a', statusGreen:'#6a8848'
      },
      dark: {
        bg:'#1e1710', bgSoft:'#261e14', paper:'#2a2018',
        ink:'#f0e4cc', inkSoft:'#d0b898', muted:'#a08858', mutedSoft:'#706040',
        line:'#382c1c', lineStrong:'#504030',
        accent:'#d89050', accentSoft:'#a87038', accentDark:'#f0a870',
        statusRed:'#d06050', statusGreen:'#80a060'
      }
    },
    {
      id: 'moss', name: '竹影苔痕', mood: '自然 · 宁静',
      light: {
        bg:'#eff4ec', bgSoft:'#f4f8f2', paper:'#ffffff',
        ink:'#1a2018', inkSoft:'#2e3c2c', muted:'#6a8060', mutedSoft:'#a0b498',
        line:'#d0e0c8', lineStrong:'#b8ccac',
        accent:'#5a7c48', accentSoft:'#88a870', accentDark:'#446038',
        statusRed:'#b05044', statusGreen:'#4a7a44'
      },
      dark: {
        bg:'#151a12', bgSoft:'#1c2218', paper:'#202818',
        ink:'#e0edd8', inkSoft:'#b0c8a8', muted:'#789068', mutedSoft:'#506848',
        line:'#283020', lineStrong:'#384830',
        accent:'#88a868', accentSoft:'#688050', accentDark:'#a8c880',
        statusRed:'#c06858', statusGreen:'#70a060'
      }
    },
    {
      id: 'moonlit', name: '月光书房', mood: '冷 · 专注',
      light: {
        bg:'#f0f2f8', bgSoft:'#f5f6fa', paper:'#ffffff',
        ink:'#181c2c', inkSoft:'#2c3448', muted:'#6870a0', mutedSoft:'#9aa4c8',
        line:'#ccd0e4', lineStrong:'#b4bcdc',
        accent:'#4a608c', accentSoft:'#7a90b8', accentDark:'#344870',
        statusRed:'#a85060', statusGreen:'#5a806a'
      },
      dark: {
        bg:'#14161e', bgSoft:'#1a1c28', paper:'#1e2230',
        ink:'#dce0f4', inkSoft:'#a8b0cc', muted:'#6070a8', mutedSoft:'#404c78',
        line:'#222840', lineStrong:'#303c58',
        accent:'#8090c8', accentSoft:'#5a6aa8', accentDark:'#a0b0e4',
        statusRed:'#c06878', statusGreen:'#6a8c7a'
      }
    },
    {
      id: 'lilac', name: '丁香晚霞', mood: '温柔 · 浪漫',
      light: {
        bg:'#f4f0f8', bgSoft:'#f8f5fc', paper:'#ffffff',
        ink:'#1e1828', inkSoft:'#382c48', muted:'#8070a0', mutedSoft:'#b4a4cc',
        line:'#e0d4f0', lineStrong:'#ccc0e0',
        accent:'#8860ac', accentSoft:'#b090d4', accentDark:'#6c4890',
        statusRed:'#b05878', statusGreen:'#6a8864'
      },
      dark: {
        bg:'#1a1620', bgSoft:'#211c28', paper:'#262030',
        ink:'#eee8f8', inkSoft:'#c8b8e0', muted:'#9880c0', mutedSoft:'#685888',
        line:'#2c2438', lineStrong:'#403450',
        accent:'#aa88d8', accentSoft:'#8868b8', accentDark:'#c4a4f0',
        statusRed:'#d07888', statusGreen:'#80a078'
      }
    },
    {
      id: 'vermilion', name: '朱砂流丹', mood: '热烈 · 张扬',
      light: {
        bg:'#fef2ef', bgSoft:'#fff5f3', paper:'#ffffff',
        ink:'#241410', inkSoft:'#4a2820', muted:'#a06858', mutedSoft:'#c8a090',
        line:'#f0d8d0', lineStrong:'#e0c0b4',
        accent:'#c44030', accentSoft:'#e07860', accentDark:'#a82818',
        statusRed:'#c44030', statusGreen:'#5a8050'
      },
      dark: {
        bg:'#201410', bgSoft:'#281a14', paper:'#2c1e18',
        ink:'#f4e4dc', inkSoft:'#d0b0a0', muted:'#b07860', mutedSoft:'#784c3c',
        line:'#3c2018', lineStrong:'#542c20',
        accent:'#e06050', accentSoft:'#b84030', accentDark:'#f87868',
        statusRed:'#e06050', statusGreen:'#789060'
      }
    },
    {
      id: 'mono', name: '墨分五彩', mood: '极简 · 克制',
      light: {
        bg:'#f8f8f6', bgSoft:'#fafaf8', paper:'#ffffff',
        ink:'#1a1a18', inkSoft:'#363632', muted:'#888880', mutedSoft:'#b8b8b0',
        line:'#e4e4e0', lineStrong:'#d0d0c8',
        accent:'#484840', accentSoft:'#7a7a70', accentDark:'#282820',
        statusRed:'#a85048', statusGreen:'#5a7850'
      },
      dark: {
        bg:'#1a1a18', bgSoft:'#222220', paper:'#282826',
        ink:'#ecece8', inkSoft:'#c0c0b8', muted:'#909088', mutedSoft:'#606058',
        line:'#2e2e2c', lineStrong:'#404040',
        accent:'#a8a8a0', accentSoft:'#808078', accentDark:'#d0d0c8',
        statusRed:'#c06858', statusGreen:'#70906a'
      }
    }
  ];

  var ALL_VARS = [
    '--c-bg','--c-bg-soft','--c-paper',
    '--c-ink','--c-ink-soft','--c-muted','--c-muted-soft',
    '--c-line','--c-line-strong',
    '--c-accent','--c-accent-soft','--c-accent-dark',
    '--c-status-red','--c-status-green',
    '--rgb-accent','--rgb-bg','--rgb-paper','--rgb-shadow','--rgb-line-warm'
  ];

  // ── Apply helpers ─────────────────────────────────────────────────────────

  function buildVars(p, dark) {
    return {
      '--c-bg': p.bg, '--c-bg-soft': p.bgSoft, '--c-paper': p.paper,
      '--c-ink': p.ink, '--c-ink-soft': p.inkSoft,
      '--c-muted': p.muted, '--c-muted-soft': p.mutedSoft,
      '--c-line': p.line, '--c-line-strong': p.lineStrong,
      '--c-accent': p.accent, '--c-accent-soft': p.accentSoft, '--c-accent-dark': p.accentDark,
      '--c-status-red': p.statusRed, '--c-status-green': p.statusGreen,
      '--rgb-accent': hexToRgb(p.accent),
      '--rgb-bg': hexToRgb(p.bg),
      '--rgb-paper': hexToRgb(p.paper),
      '--rgb-shadow': dark ? '0, 0, 0' : hexToRgb(p.ink),
      '--rgb-line-warm': hexToRgb(p.line)
    };
  }

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

  // ── State ─────────────────────────────────────────────────────────────────

  var currentState = null;

  function saveState(state) {
    currentState = state;
    try { localStorage.setItem(STORAGE_KEY, state ? JSON.stringify(state) : ''); } catch (e) {}
  }

  function applyState(state) {
    if (!state) { clearVars(); return; }
    var dark = isDark();
    if (state.type === 'preset') {
      var t = THEMES.filter(function (x) { return x.id === state.id; })[0];
      if (!t) { clearVars(); return; }
      applyVars(buildVars(dark ? t.dark : t.light, dark));
    } else if (state.type === 'custom') {
      applyCustomHue(state.hue, false);
    }
  }

  function applyCustomHue(hue, save) {
    var dark = isDark();
    var s = dark ? 58 : 52;
    var l = dark ? 65 : 46;
    var accent    = hslToHex(hue, s, l);
    var accentSoft = dark
      ? hslToHex(hue, Math.max(0, s - 12), Math.max(5, l - 14))
      : hslToHex(hue, Math.max(0, s - 10), Math.min(95, l + 13));
    var accentDark = dark
      ? hslToHex(hue, Math.min(100, s + 5), Math.min(95, l + 15))
      : hslToHex(hue, Math.min(100, s + 5), Math.max(5, l - 10));

    clearVars();
    var root = document.documentElement;
    root.style.setProperty('--c-accent', accent);
    root.style.setProperty('--c-accent-soft', accentSoft);
    root.style.setProperty('--c-accent-dark', accentDark);
    root.style.setProperty('--rgb-accent', hexToRgb(accent));
    root.style.setProperty('--c-status-red', accent);

    if (save !== false) saveState({ type: 'custom', hue: hue });
  }

  // ── Dark mode observation ─────────────────────────────────────────────────

  // Re-apply theme when light/dark mode switches
  var observer = new MutationObserver(function (mutations) {
    mutations.forEach(function (m) {
      if (m.attributeName === 'data-theme') {
        applyState(currentState);
        if (hueSliderEl) updateHuePreview(parseInt(hueSliderEl.value, 10));
      }
    });
  });
  observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });

  if (window.matchMedia) {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function () {
      if (!document.documentElement.getAttribute('data-theme')) {
        applyState(currentState);
        if (hueSliderEl) updateHuePreview(parseInt(hueSliderEl.value, 10));
      }
    });
  }

  var hueSliderEl = null; // set after UI build

  // ── UI ────────────────────────────────────────────────────────────────────
  // The trigger button lives in header.html; we only build the panel here.

  function buildUI() {
    var trigger = document.getElementById('js-palette-trigger');

    var panel = document.createElement('div');
    panel.className = 'c-palette-panel';
    panel.id = 'js-palette-panel';
    panel.setAttribute('role', 'dialog');
    panel.setAttribute('aria-label', '配色主题');
    panel.setAttribute('aria-hidden', 'true');

    var grid = '';
    THEMES.forEach(function (t) {
      grid += '<button class="c-palette-swatch" data-theme-id="' + t.id + '" title="' + t.mood + '" aria-label="' + t.name + '">' +
        '<span class="c-palette-swatch__chip" style="--sw-bg:' + t.light.bg + ';--sw-ac:' + t.light.accent + '"></span>' +
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
          '<p class="c-palette-section__label">心情主题</p>' +
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
    var dark = isDark();
    el.style.backgroundColor = 'hsl(' + hue + ',' + (dark ? 58 : 52) + '%,' + (dark ? 65 : 46) + '%)';
  }

  function updateSwatchStates() {
    document.querySelectorAll('[data-theme-id]').forEach(function (sw) {
      var active = !!(currentState && currentState.type === 'preset' && currentState.id === sw.getAttribute('data-theme-id'));
      sw.classList.toggle('is-active', active);
    });
  }

  function initEvents(trigger, panel) {
    var open = false;

    function openPanel() {
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

    trigger.addEventListener('click', function (e) {
      e.stopPropagation();
      open ? closePanel() : openPanel();
    });

    document.getElementById('js-palette-close').addEventListener('click', closePanel);

    document.addEventListener('click', function (e) {
      if (open && !panel.contains(e.target) && e.target !== trigger) closePanel();
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && open) closePanel();
    });

    document.getElementById('js-palette-grid').addEventListener('click', function (e) {
      var btn = e.target.closest('[data-theme-id]');
      if (!btn) return;
      var state = { type: 'preset', id: btn.getAttribute('data-theme-id') };
      applyState(state);
      saveState(state);
      updateSwatchStates();
      var slider = document.getElementById('js-palette-hue');
      if (slider) { slider.value = 0; updateHuePreview(0); }
    });

    var hueSlider = document.getElementById('js-palette-hue');
    hueSliderEl = hueSlider;

    if (currentState && currentState.type === 'custom') {
      hueSlider.value = currentState.hue;
    }
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
