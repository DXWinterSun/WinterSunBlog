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

  // ── Theme definitions — Many Faces of Sam ────────────────────────────────
  // Each theme carries two named colors:
  //   accent / cn / en  → the character's signature highlight color
  //   bg / bg_cn / bg_en → the deep ground color (what the whole card sits on)

  var THEMES = [
    { id:'gary',     name:'Gary',        cn:'天际铜金',     en:'Skyline Brass',        bg_cn:'顶楼黑檀',     bg_en:'Penthouse Ebony',    accent:'#cba14c', bg:'#14110d', text:'#ede2d0', muted:'#8a7558' },
    { id:'kris',     name:'Kris',        cn:'余烬绯红',     en:'Ember Cardinal',       bg_cn:'华沙墨蓝',     bg_en:'Warsaw Indigo',      accent:'#bc4d3a', bg:'#11161c', text:'#ece0d2', muted:'#62768d' },
    { id:'matty',    name:'Matty',       cn:'旧电话亭琥珀', en:'Old Phonebooth Amber', bg_cn:'凌晨地铁月台', bg_en:'Pre-Dawn Subway',    accent:'#d49850', bg:'#171d24', text:'#ebe0cc', muted:'#7d7264' },
    { id:'buck',     name:'Buck',        cn:'林间苔绿',     en:'Forest Moss',          bg_cn:'月光银白',     bg_en:'Moonlight Silver',   accent:'#b8c878', bg:'#1a2418', text:'#e8eed8', muted:'#7a8868' },
    { id:'trent',    name:'Trent',       cn:'天蓝卡车',     en:'Pickup Sky',           bg_cn:'新刈草青',     bg_en:'Mown Lawn',          accent:'#79a7bd', bg:'#141c12', text:'#dce5ea', muted:'#7a7654' },
    { id:'samuel',   name:'Samuel',      cn:'舞台背心红',   en:'Stage Vest',           bg_cn:'格纹芥末棕',   bg_en:'Plaid Mustard',      accent:'#c5402f', bg:'#211a0f', text:'#f0e2d4', muted:'#a08770' },
    { id:'jerry',    name:'Jerry',       cn:'蓬乱金长发',   en:'Blond Mane',           bg_cn:'深夜快餐棕',   bg_en:'Late-Night Diner',   accent:'#d7a83c', bg:'#20120c', text:'#f0e0d0', muted:'#a07060' },
    { id:'wildbill', name:'Wild Bill',   cn:'锯末粗木',     en:'Sawdust Timber',       bg_cn:'炉膛夜黑',     bg_en:'Forge Soot',         accent:'#b0803e', bg:'#1b1510', text:'#ece0d0', muted:'#93826a' },
    { id:'guy',      name:'Guy',         cn:'控制台青',     en:'Console Teal',         bg_cn:'深空黛黑',     bg_en:'Deep-Space Black',   accent:'#43b3bf', bg:'#0f161a', text:'#dfe7ea', muted:'#738088' },
    { id:'knox',     name:'Knox',        cn:'红镜红',       en:'Crimson Lens',         bg_cn:'可乐棕',       bg_en:'Cola Noir',          accent:'#d94040', bg:'#1b1310', text:'#ede0e0', muted:'#8d6e62' },
    { id:'pero',     name:'Pero',        cn:'拳击台暖灯橘', en:'Ring Lamp Amber',      bg_cn:'科林伍德暮色', bg_en:'Collinwood Dusk',    accent:'#d49858', bg:'#1a1612', text:'#ede0cc', muted:'#8a7458' },
    { id:'chuck',    name:'Chuck',       cn:'镁光节目粉',   en:'Limelight Pink',       bg_cn:'午夜情报蓝',   bg_en:'Midnight Spy',       accent:'#de6e8e', bg:'#15182a', text:'#ede4d0', muted:'#8088a0' },
    { id:'mercer',   name:'Mercer',      cn:'擦燃焰橘',     en:'Strike Flare',         bg_cn:'焦黑火柴',     bg_en:'Burnt Matchstick',   accent:'#e08a2e', bg:'#1a1410', text:'#ede0e6', muted:'#8d7462' },
    { id:'crocker',  name:'Crocker',     cn:'夜会香槟金',   en:'Club Champagne',       bg_cn:'黑貂皮大氅',   bg_en:'Mink Black',         accent:'#d8b25a', bg:'#161214', text:'#f0e3dc', muted:'#8d6278' },
    { id:'zaphod',   name:'Zaphod',      cn:'总统鬃金',     en:"President's Mane",     bg_cn:'黑甲漆夜',     bg_en:'Lacquer Black',      accent:'#d4a82a', bg:'#0b0a12', text:'#e8e4d0', muted:'#8a7a48' },
    { id:'brad',     name:'Brad',        cn:'网球荧光黄',   en:'Tennis Ball',          bg_cn:'曼哈顿冬夜',   bg_en:'Manhattan Slate',    accent:'#c9d84e', bg:'#1c2230', text:'#e8eadc', muted:'#7a8590' },
    { id:'glenn',    name:'Glenn',       cn:'初雪微光白',   en:'First Snow',           bg_cn:'寒冬冷蓝灰',   bg_en:'Winter Steel',       accent:'#b8d0e0', bg:'#1c2030', text:'#dce4ea', muted:'#7a8090' },
    { id:'reston',   name:'Reston',      cn:'钨丝暖灯金',   en:'Tungsten Glow',        bg_cn:'深夜手稿棕',   bg_en:'Manuscript Brown',   accent:'#d89858', bg:'#1f1814', text:'#ebe0cc', muted:'#8a7458' },
    { id:'victor',   name:'Victor',      cn:'殖民地铜金',   en:'Colonial Gilt',        bg_cn:'旧绒布酒红',   bg_en:'Velvet Wine',        accent:'#d2a24a', bg:'#2a1820', text:'#f0e0d4', muted:'#9a7868' },
    { id:'sambell',  name:'Sam Bell',    cn:'基地微光',     en:'Sarang Glow',          bg_cn:'月球蔚蓝',     bg_en:'Lunar Blue',         accent:'#7eb0d5', bg:'#162038', text:'#e8eef5', muted:'#6a85a3' },
    { id:'goode',    name:'Goode',       cn:'圣诞帽红',     en:'Santa Hat',            bg_cn:'鼓皮深棕',     bg_en:'Drumskin Brown',     accent:'#cc4436', bg:'#211910', text:'#ede4d4', muted:'#9a7e58' },
    { id:'hammer',   name:'Hammer',      cn:'电光钴蓝',     en:'Spotlight Sapphire',   bg_cn:'落幕玄黑',     bg_en:'After-Curtain Onyx', accent:'#4a87ee', bg:'#13151c', text:'#e7eaf2', muted:'#7c8aa6' },
    { id:'kenny',    name:'Kenny',       cn:'铁窗微光',     en:'Barred Light',         bg_cn:'囚室灰墙',     bg_en:'Cell Concrete',      accent:'#d08a45', bg:'#1c1e1f', text:'#f0e0d4', muted:'#627f8d' },
    { id:'billy',    name:'Billy',       cn:'方块J红',      en:'Diamond Jack',         bg_cn:'沙漠焦土',     bg_en:'Scorched Desert',    accent:'#d63a33', bg:'#281208', text:'#f5e6d0', muted:'#b07840' },
    { id:'owen',     name:'Owen',        cn:'滑梯翠蓝',     en:'Waterslide Aqua',      bg_cn:'氯味深池',     bg_en:'Chlorine Deep',      accent:'#35bfc9', bg:'#15282e', text:'#dce9ea', muted:'#75899a' },
    { id:'johnmoon', name:'John Moon',   cn:'孤枪冷雾蓝',   en:'Lone Mist',            bg_cn:'西弗州山夜',   bg_en:'Appalachian Dusk',   accent:'#8fa0b0', bg:'#14181f', text:'#dce3ea', muted:'#62728d' },
    { id:'varney',   name:'Varney',      cn:'处方白大褂',   en:'Lab Coat',             bg_cn:'药瓶琥珀棕',   bg_en:'Pill-Bottle Brown',  accent:'#e6ecea', bg:'#1e1408', text:'#dceae5', muted:'#8d7a62' },
    { id:'wayne',    name:'Wayne',       cn:'夏末琥珀',     en:'Late Summer Amber',    bg_cn:'退伍橄榄',     bg_en:'Old Olive',          accent:'#c8a050', bg:'#1e2418', text:'#e8e4d0', muted:'#8a7a48' },
    { id:'craig',    name:'Craig',       cn:'威士忌金',     en:'Whisky Gold',          bg_cn:'陈年皮革',     bg_en:'Aged Leather',       accent:'#c89060', bg:'#241a14', text:'#ede0d0', muted:'#a07858' },
    { id:'munch',    name:'Munch',       cn:'丑角红鼻头',   en:'Clown Nose',           bg_cn:'小熊软糖绿',   bg_en:'Gummy Bear Green',   accent:'#e23b2e', bg:'#14241a', text:'#eed9d8', muted:'#628d72' },
    { id:'dixon',    name:'Dixon',       cn:'重生焰橘',     en:'Reborn Flame',         bg_cn:'焦烬玫瑰',     bg_en:'Charred Rose',       accent:'#e2622a', bg:'#241015', text:'#f5e6d3', muted:'#8d626d' },
    { id:'eddie',    name:'Eddie',       cn:'蓝蜥宝石',     en:'Iguana Jewel',         bg_cn:'酒馆烟灰',     bg_en:'Tavern Smoke',       accent:'#2e9fd4', bg:'#1a1f24', text:'#dce5ea', muted:'#7a8088' },
    { id:'bush',     name:'G.W. Bush',   cn:'德州牛仔金',   en:'Texan Tan',            bg_cn:'总统西装夜',   bg_en:'Suit Navy',          accent:'#c98a3e', bg:'#16181e', text:'#f1e3cb', muted:'#626d8d' },
    { id:'klenz',    name:'Klenzendorf', cn:'夸张军装红',   en:'Glam Tunic',           bg_cn:'登台华服绿',   bg_en:'Costume Green',      accent:'#d34338', bg:'#14241c', text:'#ede8d8', muted:'#8b7d4d' },
    { id:'bryant',   name:'Bryant',      cn:'红土暖橘',     en:'Georgia Clay',         bg_cn:'档案橡木',     bg_en:'Archive Oak',        accent:'#c8783c', bg:'#1c1410', text:'#ede0d0', muted:'#8a6848' },
    { id:'mrwolf',   name:'Mr. Wolf',    cn:'磁石黄金',     en:'Magnet Gold',          bg_cn:'狼影灰蓝',     bg_en:'Wolf Shadow',        accent:'#dfb23c', bg:'#14161d', text:'#ede6d8', muted:'#7a7d8a' },
    { id:'stoppard', name:'Stoppard',    cn:'旧照片暖褐',   en:'Old Photograph',       bg_cn:'伦敦午夜蓝',   bg_en:'London Midnight',    accent:'#c7995a', bg:'#1a1f2c', text:'#ebe2d4', muted:'#7c8090' },
    { id:'wilde',    name:'Wilde',       cn:'弹壳余温金',   en:'Casing Gold',          bg_cn:'午夜枪管蓝',   bg_en:'Gunmetal Blue',      accent:'#cda24f', bg:'#15192a', text:'#ebe2d0', muted:'#7a7e90' },
    { id:'future',   name:'The Future',  cn:'故障玫红',     en:'Glitch Magenta',       bg_cn:'荧光夜紫',     bg_en:'Neon Violet',        accent:'#d460a0', bg:'#1a0e2a', text:'#ede0ec', muted:'#8868a0' },
  ];

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
            '<span class="c-palette-card__char">' + t.name + '</span>' +
          '</span>' +
          '<span class="c-palette-card__perfs">' + PERFS + '</span>' +
        '</button>';
    });

    overlay.innerHTML =
      '<div class="c-palette-modal" role="dialog" aria-label="配色主题 · 换个心情">' +
        '<div class="c-palette-modal__header">' +
          '<span class="c-palette-modal__title">' +
            '换个心情 · ' +
            '<a class="c-palette-modal__gallery-link" href="' + galleryHref + '" target="_blank" rel="noopener">Many Faces ↗</a>' +
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
