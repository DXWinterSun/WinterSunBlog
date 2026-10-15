/* =========================================================
   宝丽来背面批注 · Polaroid back-of-photo private notes
   右键(电脑)/长按(手机)照片 / 票根 → 翻开写字 → 自动保存(本机)
   解锁一次后长期保持；日后升级云端只需替换 Store 这一层。

   2026-10-15 整体改版（Winter 在方案页上挑的）：
   · 左下角那颗长条浮标 + 叠在上面的三张日记卡 → 一枚「钢笔」小圆钮（.pol-pin），
     点开一张小册子（.pol-pop）：所有背面的总账 / 底片匣 / 封存 / 去书桌；文章页里多一行「写在这一篇的背面」
     （原来右下角那支浮笔并进来了）。没解锁时点开是访客那张拍立得 + 验笔迹。
   · 三种背面统一成一张米色相纸：拍立得＝黑色相纸条，票根＝系列色票头＋撕线（印 Admit One 和票号），
     日记＝日期条。日记那排五十四个色点拿掉了。
   · 票根背面顶上一条「胶片齿孔格」：这个系列的章节票号，写过字 / 划过线的亮着，点一格整张背面
     换成那一章；最左边「系列」那格回系列自己的背面。章节资料从 /backs-map.json 取（构建时生成）。
   · 书桌上多了一本「冬的背面」（/notes/backs/）：三本日记、全部背面的总账、底片匣都在那本里；
     数据仍只在本机 localStorage，页面只是把它摊开。
   ========================================================= */
(function () {
  "use strict";

  /* ========== 你的配置 ========== */
  // ↓↓↓ 用文末小工具把你的密码转成哈希，替换下面这行的占位符：
  var PASS_HASH = "2432187070";
  var HELLO_ENDPOINT = (typeof window !== "undefined" && window.HELLO_ENDPOINT) || ""; // 寄信端点（Web3Forms）
  var WEB3FORMS_KEY = (typeof window !== "undefined" && window.WEB3FORMS_KEY) || "";   // Web3Forms 免费 access key
  var NOTE_FONT = "'Caveat','Ma Shan Zheng',cursive";
  var FONT_LINK = "https://fonts.googleapis.com/css2?family=Caveat:wght@500;600&family=Ma+Shan+Zheng&display=swap";
  var LONGPRESS_MS = 480;
  // 拍立得背面黑条上印着的一句话（仪式感所在，想换就改这里）：
  var NOTE_TAGLINE = "趁我还记得，把它写在背面。";
  // 票根背面（章节卡 / 章节页）献给 Sam 的一句——正面归他，背面归她：
  var TICKET_TAGLINE = "正面是他的戏。背面归你。";
  var TICKET_TAGLINE_EN = "His show on the front. The back is yours.";
  var NOTE_TAGLINE_EN = "While it's still mine to remember.";
  // 左下角浮标上的导语（钢笔旁的小字）：
  var LOCK_LABEL = "记忆碎片";
  var LOCK_LABEL_EN = "Memento";
  // 角落里那叠小拍立得 —— 每张一个用途，平时叠着，悬停展开，点开记录。
  // kind: "three" = 每天三件（固定三行）；"free" = 每天自由写（一段，可长）。
  // ls:   各自的 localStorage 键，互不干扰；grad: 相纸里那块"照片"的渐变色。
  // q1/q2/credit: 相纸下沿的分层歌词（引子 / 主角 / 署名）。
  var JOURNALS = [
    {
      id: "fortunes", kind: "three", ls: "wiw-lucky",
      grad: "linear-gradient(145deg, #c9a16b 0%, #6b5e7a 55%, #3f4a63 100%)",
      q1: "Happiness throws", q2: "a shower of sparks", credit: "The Fray · Happiness",
      hint: "记下这一天的三件幸运小事。"
    },
    {
      id: "windows", kind: "free", ls: "wiw-windows",
      grad: "linear-gradient(145deg, #5a6b78 0%, #46505f 50%, #2c333f 100%)",
      q1: "It seems to you I'm failing,", q2: "but it seems to me I'm trying.", credit: "Guy Pearce · Dirty Windows",
      hint: "今天想吐槽 / 想记下的，都丢这儿。"
    },
    {
      id: "toself", kind: "letter", ls: "wiw-toself",
      grad: "linear-gradient(145deg, #8a7459 0%, #5b4a52 52%, #34303a 100%)",
      q1: "And I'll", q2: "meet you there someday", credit: "Augustana · Meet You There",
      hint: "存着慢慢写；封缄后，它会寄进你的邮箱。",
      subjectDefault: ""
    }
  ];
  // 主题色：直接读「Many Faces of Sam」画册的全量角色色卡（_data/sam_themes.yml，
  // 经 sam-themes-data.js 注入到 window.__SAM_THEMES）。画册新增角色 → 这里自动同步。
  // 选某个角色：把这张卡的顶栏换成该角色的深色背景 + 强调色；选「原色」则恢复默认。
  // 注：旧的手写 7 色子集已废弃，改走画册数据源。
  // 访客彩蛋：没有笔迹的访客，角落会出现这张拍立得（点开 → You Are My Fact），
  // 落款是「我和他」。grad 用 Leonard 的冰蓝（与该系列同色）；歌词是《记忆碎片》片尾曲。
  var GUEST = {
    href: "/series/you-are-my-fact/",
    grad: "linear-gradient(160deg, #8fc0e2 0%, #5b7d9c 42%, #2b3550 78%, #171a26 100%)",
    q1: "Something in my eyes —",
    q2: "I've danced with you too long",
    credit: "David Bowie · Something in the Air",
    sign: "Leo & Winter",
    // —— 翻到背面看到的：黑条上印的小字 + 手写短笺（中英对照）+ 故事链接 ——
    backLine: "Something in the Air —",
    note: [
      { zh: "嘿，翻到背面的你：", en: "Hey, you who turned me over —" },
      { zh: "这是我和他的故事，", en: "this is our story, his and mine:" },
      { zh: "关于遗忘，和不肯遗忘的爱。", en: "of forgetting, and a love that won't." },
      { zh: "要不要进来，认识一下我们？", en: "Won't you come in and meet us?" }
    ],
    linkLabel: "翻开《You Are My Fact》 →"
  };
  // 每张拍立得里的「照片」：一帧贴合这张情绪的小场景（纯 SVG，铺满相纸框）。
  // 比纯渐变更像真相片，月/星/漏光/暗角营造厚度。键 = journal id（+ guest）。
  var SCENES = {
    // fortunes · The Fray「Happiness throws a shower of sparks」—— 暖金火花雨，幸运、雀跃
    fortunes:
      '<svg class="pol-scene" viewBox="0 0 160 96" preserveAspectRatio="xMidYMid slice" aria-hidden="true">' +
        '<defs>' +
          '<radialGradient id="scFg" cx="50%" cy="16%" r="62%"><stop offset="0%" stop-color="#ffe9b0" stop-opacity="0.55"/><stop offset="100%" stop-color="#ffe9b0" stop-opacity="0"/></radialGradient>' +
          '<radialGradient id="scFv" cx="50%" cy="42%" r="80%"><stop offset="55%" stop-color="#1a1024" stop-opacity="0"/><stop offset="100%" stop-color="#1a1024" stop-opacity="0.4"/></radialGradient>' +
        '</defs>' +
        '<rect x="0" y="0" width="160" height="96" fill="url(#scFg)"/>' +
        '<g stroke="#ffd373" stroke-width="1.4" stroke-linecap="round">' +
          '<line x1="40" y1="8" x2="36" y2="20" opacity="0.85"/><line x1="66" y1="4" x2="61" y2="18" opacity="0.7"/>' +
          '<line x1="92" y1="10" x2="88" y2="24" opacity="0.8"/><line x1="116" y1="6" x2="112" y2="19" opacity="0.6"/>' +
          '<line x1="78" y1="22" x2="75" y2="33" opacity="0.5"/><line x1="52" y1="26" x2="49" y2="36" opacity="0.45"/>' +
        '</g>' +
        '<g fill="#ffe7a8">' +
          '<circle cx="36" cy="22" r="1.3" opacity="0.9"/><circle cx="61" cy="20" r="1.1" opacity="0.8"/>' +
          '<circle cx="88" cy="26" r="1.4" opacity="0.9"/><circle cx="112" cy="21" r="1" opacity="0.7"/>' +
          '<circle cx="75" cy="35" r="1" opacity="0.6"/><circle cx="128" cy="34" r="1.2" opacity="0.7"/>' +
        '</g>' +
        '<path d="M104 50 l1.8 5 5 1.8 -5 1.8 -1.8 5 -1.8 -5 -5 -1.8 5 -1.8 z" fill="#fff3d0" opacity="0.95"/>' +
        '<rect x="0" y="0" width="160" height="96" fill="url(#scFv)"/>' +
      '</svg>',
    // windows · Guy Pearce「Dirty Windows」—— 雨水顺着窗格往下淌，灰蓝、低落、隐忍
    windows:
      '<svg class="pol-scene" viewBox="0 0 160 96" preserveAspectRatio="xMidYMid slice" aria-hidden="true">' +
        '<defs>' +
          '<linearGradient id="scWs" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#cdd6dc" stop-opacity="0"/><stop offset="100%" stop-color="#cdd6dc" stop-opacity="0.4"/></linearGradient>' +
          '<radialGradient id="scWv" cx="50%" cy="45%" r="80%"><stop offset="50%" stop-color="#0e141a" stop-opacity="0"/><stop offset="100%" stop-color="#0e141a" stop-opacity="0.42"/></radialGradient>' +
        '</defs>' +
        '<g stroke="#11161c" stroke-width="3" opacity="0.18"><line x1="80" y1="0" x2="80" y2="96"/><line x1="0" y1="50" x2="160" y2="50"/></g>' +
        '<g stroke="url(#scWs)" stroke-width="1.6" stroke-linecap="round">' +
          '<line x1="24" y1="6" x2="24" y2="40"/><line x1="44" y1="20" x2="44" y2="62"/><line x1="100" y1="2" x2="100" y2="34"/>' +
          '<line x1="120" y1="26" x2="120" y2="70"/><line x1="138" y1="10" x2="138" y2="48"/><line x1="62" y1="40" x2="62" y2="82"/>' +
        '</g>' +
        '<g fill="#dfe7ec" opacity="0.6">' +
          '<circle cx="24" cy="42" r="2"/><circle cx="44" cy="64" r="2.4"/><circle cx="120" cy="72" r="2.2"/>' +
          '<circle cx="138" cy="50" r="1.8"/><circle cx="62" cy="84" r="2"/>' +
        '</g>' +
        '<rect x="0" y="0" width="160" height="96" fill="url(#scWv)"/>' +
      '</svg>',
    // toself · Augustana「Meet You There」—— 一条小路通向地平线上的光点，盼望、奔赴
    toself:
      '<svg class="pol-scene" viewBox="0 0 160 96" preserveAspectRatio="xMidYMid slice" aria-hidden="true">' +
        '<defs>' +
          '<radialGradient id="scTg" cx="50%" cy="62%" r="34%"><stop offset="0%" stop-color="#ffe6c0" stop-opacity="0.85"/><stop offset="100%" stop-color="#ffe6c0" stop-opacity="0"/></radialGradient>' +
          '<radialGradient id="scTv" cx="50%" cy="45%" r="80%"><stop offset="55%" stop-color="#140f12" stop-opacity="0"/><stop offset="100%" stop-color="#140f12" stop-opacity="0.4"/></radialGradient>' +
        '</defs>' +
        '<rect x="0" y="0" width="160" height="96" fill="url(#scTg)"/>' +
        '<path d="M64 96 L78 60 L82 60 L96 96 Z" fill="#d8c4a6" opacity="0.22"/>' +
        '<line x1="0" y1="60" x2="160" y2="60" stroke="#e9d6b8" stroke-width="1" opacity="0.35"/>' +
        '<circle cx="80" cy="60" r="5" fill="#fff1d6" opacity="0.35"/><circle cx="80" cy="60" r="2.4" fill="#fff1d6"/>' +
        '<g fill="#f3e6cf">' +
          '<circle cx="30" cy="22" r="1.1" opacity="0.8"/><circle cx="120" cy="18" r="1" opacity="0.7"/>' +
          '<circle cx="100" cy="34" r="0.8" opacity="0.55"/><circle cx="46" cy="40" r="0.8" opacity="0.5"/>' +
        '</g>' +
        '<rect x="0" y="0" width="160" height="96" fill="url(#scTv)"/>' +
      '</svg>',
    // guest · David Bowie「Something in the Air」—— 褪色夜空，月、星、漏光、暗角
    guest:
      '<svg class="pol-scene" viewBox="0 0 160 96" preserveAspectRatio="xMidYMid slice" aria-hidden="true">' +
        '<defs>' +
          '<radialGradient id="pgMoon" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#fff6e2"/><stop offset="62%" stop-color="#efe1c2"/><stop offset="100%" stop-color="#efe1c2" stop-opacity="0"/></radialGradient>' +
          '<linearGradient id="pgLeak" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#ffe7bd" stop-opacity="0.5"/><stop offset="42%" stop-color="#ffd79a" stop-opacity="0.07"/><stop offset="100%" stop-color="#ffd79a" stop-opacity="0"/></linearGradient>' +
          '<radialGradient id="pgVig" cx="48%" cy="40%" r="78%"><stop offset="55%" stop-color="#0a0c14" stop-opacity="0"/><stop offset="100%" stop-color="#0a0c14" stop-opacity="0.4"/></radialGradient>' +
        '</defs>' +
        '<rect x="84" y="-14" width="96" height="128" transform="rotate(20 132 40)" fill="url(#pgLeak)"/>' +
        '<circle cx="126" cy="25" r="15" fill="url(#pgMoon)"/>' +
        '<g fill="#fdf6e6">' +
          '<circle cx="20" cy="18" r="1.3" opacity="0.9"/><circle cx="38" cy="36" r="0.9" opacity="0.6"/>' +
          '<circle cx="58" cy="14" r="1.1" opacity="0.75"/><circle cx="80" cy="44" r="0.8" opacity="0.5"/>' +
          '<circle cx="98" cy="20" r="1" opacity="0.7"/><circle cx="30" cy="56" r="1" opacity="0.6"/>' +
          '<circle cx="14" cy="38" r="0.8" opacity="0.5"/><circle cx="110" cy="50" r="0.9" opacity="0.55"/>' +
        '</g>' +
        '<path d="M50 60 l1.7 4.6 4.6 1.7 -4.6 1.7 -1.7 4.6 -1.7 -4.6 -4.6 -1.7 4.6 -1.7 z" fill="#fff" opacity="0.92"/>' +
        '<rect x="0" y="0" width="160" height="96" fill="url(#pgVig)"/>' +
      '</svg>'
  };
  // 钢笔笔尖（SVG，缺口与气孔留成镂空，像真的笔尖）：
  var PEN_SVG = '<svg class="pol-lock-pen" viewBox="0 0 24 24" width="19" height="19" aria-hidden="true">' +
    '<path d="M12 2 C15.2 8 16.6 13.6 12 22 C7.4 13.6 8.8 8 12 2 Z" fill="#d8c6a2"/>' +
    '<line x1="12" y1="8.4" x2="12" y2="19.6" stroke="#1e1c18" stroke-width="1.3" stroke-linecap="round"/>' +
    '<circle cx="12" cy="7.4" r="1" fill="#1e1c18"/>' +
    '</svg>';
  // 拍立得小相机（经典彩虹条 + 镜头），和笔并排，是 Leo 的另一半安全感：
  var CAM_SVG = '<svg class="pol-lock-cam" viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">' +
    '<rect x="2.5" y="6.5" width="19" height="13" rx="2.2" fill="#efe8d8"/>' +
    '<rect x="7" y="3.6" width="9" height="3.5" rx="1" fill="#e0d6c1"/>' +
    '<rect x="4" y="9" width="1.4" height="8" fill="#e2574c"/>' +
    '<rect x="5.4" y="9" width="1.4" height="8" fill="#f0a13b"/>' +
    '<rect x="6.8" y="9" width="1.4" height="8" fill="#f2c94c"/>' +
    '<rect x="8.2" y="9" width="1.4" height="8" fill="#6fbf73"/>' +
    '<rect x="9.6" y="9" width="1.4" height="8" fill="#4a90d9"/>' +
    '<circle cx="15" cy="13" r="3.6" fill="#2c2b29"/>' +
    '<circle cx="15" cy="13" r="1.8" fill="#5b6a72"/>' +
    '<circle cx="14.2" cy="12.2" r="0.6" fill="#cdd6da"/>' +
    '</svg>';

  /* ========== 存储键 ========== */
  var LS_NOTES = "wiw-pol-notes";
  var LS_UNLOCK = "wiw-pol-unlock";
  var LS_PASS_DEV = "wiw-pol-pass-dev"; // 仅在尚未填 PASS_HASH 时作兜底
  // 各 journal 的存储键写在 JOURNALS 配置里（如 wiw-lucky / wiw-windows）。

  function hash(s) { var h = 5381; for (var i = 0; i < s.length; i++) h = ((h << 5) + h + s.charCodeAt(i)) >>> 0; return "" + h; }

  /* ========== 存储层（升级云端时只改这里）========== */
  var Store = {
    all: function () { try { return JSON.parse(localStorage.getItem(LS_NOTES)) || {}; } catch (e) { return {}; } },
    get: function (id) { return this.all()[id] || { text: "", ts: 0 }; },
    set: function (id, text) {
      var a = this.all(); a[id] = { text: text, ts: Date.now() };
      try { localStorage.setItem(LS_NOTES, JSON.stringify(a)); } catch (e) {}
      return a[id];
    }
  };

  /* 每个 journal 一个按日期存的存储层（互不干扰；升级云端时也只改这里）*/
  var stores = {};
  function storeOf(j) {
    if (stores[j.id]) return stores[j.id];
    var lsKey = j.ls;
    var s = {
      all: function () { try { return JSON.parse(localStorage.getItem(lsKey)) || {}; } catch (e) { return {}; } },
      get: function (day) { return this.all()[day] || null; },
      save: function (day, rec, empty) {
        var a = this.all();
        if (empty) { delete a[day]; }            // 写空了就不留这天，免得攒空壳
        else { rec.ts = Date.now(); a[day] = rec; }
        try { localStorage.setItem(lsKey, JSON.stringify(a)); } catch (e) {}
      }
    };
    stores[j.id] = s; return s;
  }
  function journalById(id) { for (var i = 0; i < JOURNALS.length; i++) if (JOURNALS[i].id === id) return JOURNALS[i]; return null; }

  /* ========== 主题色：每张卡选一个，记在本地 ========== */
  var LS_THEME = "wiw-pol-themes";
  function themeMap() { try { return JSON.parse(localStorage.getItem(LS_THEME)) || {}; } catch (e) { return {}; } }
  function themeKeyOf(jid) { return themeMap()[jid] || ""; }
  function setThemeKey(jid, key) {
    var m = themeMap(); if (key) m[jid] = key; else delete m[jid];
    try { localStorage.setItem(LS_THEME, JSON.stringify(m)); } catch (e) {}
  }
  function samThemes() { return (typeof window !== "undefined" && window.__SAM_THEMES) || []; }
  function themeById(id) { if (!id) return null; var a = samThemes(); for (var i = 0; i < a.length; i++) if (a[i].id === id) return a[i]; return null; }
  // 颜色混合（与画册 theme-picker 同款）：pct% 的 hex1 + (100-pct)% 的 hex2
  function mixHex(hex1, pct, hex2) {
    var p = pct / 100, q = 1 - p;
    function ch(h, i) { return parseInt(h.slice(i, i + 2), 16); }
    function m(a, b) { var v = Math.round(a * p + b * q).toString(16); return v.length < 2 ? "0" + v : v; }
    return "#" + m(ch(hex1, 1), ch(hex2, 1)) + m(ch(hex1, 3), ch(hex2, 3)) + m(ch(hex1, 5), ch(hex2, 5));
  }
  // 整站当前是否深色（读 <html data-theme>，未设则跟随系统）—— 与 theme-picker 一致
  function isDarkSite() {
    var dt = document.documentElement.getAttribute("data-theme");
    if (dt === "dark") return true;
    if (dt === "light") return false;
    return !!(window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches);
  }
  // 由角色色卡 p 推出这张写作卡的颜色：色源始终是该角色，明暗跟随整站
  function cardVars(p, dark) {
    if (dark) {
      return { bg: p.bg, strip: mixHex(p.bg, 72, "#000000"), stripInk: p.text,
        text: p.text, muted: p.muted, accent: p.accent, line: "rgba(255,255,255,0.12)" };
    }
    return { bg: mixHex(p.accent, 13, "#fdfbf6"), strip: mixHex(p.accent, 30, "#f3ede2"), stripInk: "#2b2620",
      text: "#2b2620", muted: "#847a6d", accent: mixHex(p.accent, 70, "#1a1614"), line: "rgba(0,0,0,0.12)" };
  }

  var devMode = (PASS_HASH === "PUT_YOUR_HASH_HERE");
  function passHash() { return devMode ? localStorage.getItem(LS_PASS_DEV) : PASS_HASH; }
  function hasPass() { return !!passHash(); }
  var unlocked = localStorage.getItem(LS_UNLOCK) === "1";

  var fontsLoaded = false;
  function loadFonts() {
    if (fontsLoaded) return; fontsLoaded = true;
    var l = document.createElement("link"); l.rel = "stylesheet"; l.href = FONT_LINK; document.head.appendChild(l);
  }

  // 批注的钥匙 = 这张卡指向的文章路径；没有链接的（系列页底那张票根）用 data-note-key（= 系列页自己的路径）
  function keyOf(a) {
    var k = a.getAttribute("data-note-key");
    if (k) return k;
    try { return new URL(a.getAttribute("href"), location.origin).pathname; } catch (e) { return a.getAttribute("href") || ""; }
  }
  function fmt(ts) { return ts ? new Date(ts).toLocaleString("zh-CN", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }) : ""; }

  /* ========== 编辑器浮层（构建一次）========== */
  var backdrop, note, tsEl, savedEl, current = null, saveTimer = null;
  function buildEditor() {
    backdrop = document.createElement("div");
    backdrop.className = "pol-backdrop";
    backdrop.innerHTML =
      '<div class="pol-editor" role="dialog" aria-label="照片背面">' +
        '<div class="pol-ed-top">' +
          '<span class="pol-ed-adm"></span>' +
          '<button class="pol-ed-x" type="button" title="翻回" aria-label="翻回">↩</button>' +
          '<div class="pol-ed-lines"><p class="pol-ed-line"></p><p class="pol-ed-line-en"></p></div>' +
        '</div>' +
        '<div class="pol-film" hidden></div>' +
        '<div class="pol-ed-chap" hidden></div>' +
        '<div class="pol-ed-write">' +
          '<textarea class="pol-note" spellcheck="false"></textarea>' +
          '<div class="pol-ed-foot"><span class="pol-ts"></span><span class="pol-saved">已保存 ✓</span></div>' +
        '</div>' +
      '</div>';
    document.body.appendChild(backdrop);
    note = backdrop.querySelector(".pol-note");
    tsEl = backdrop.querySelector(".pol-ts");
    savedEl = backdrop.querySelector(".pol-saved");
    note.style.fontFamily = NOTE_FONT;
    backdrop.querySelector(".pol-ed-line").textContent = NOTE_TAGLINE;
    backdrop.querySelector(".pol-ed-line-en").textContent = NOTE_TAGLINE_EN;
    backdrop.querySelector(".pol-ed-x").addEventListener("click", closeEditor);
    backdrop.addEventListener("click", function (e) { if (e.target === backdrop) closeEditor(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeEditor(); });
    note.addEventListener("input", function () {
      if (!unlocked || !current) return;
      clearTimeout(saveTimer);
      saveTimer = setTimeout(function () {
        saveTimer = null;
        var n = Store.set(current, note.value);
        tsEl.textContent = n.ts ? "上次编辑 " + fmt(n.ts) : "";
        savedEl.classList.add("show");
        setTimeout(function () { savedEl.classList.remove("show"); }, 1200);
        markDogears();
        var film = backdrop.querySelector(".pol-film");
        if (film && !film.hidden) { var cell = film.querySelector('.pol-film-cell[data-path="' + current.replace(/"/g, '&quot;') + '"]'); if (cell) cell.classList.toggle("is-lit", !!note.value.trim() || Marks.forPath(current).length > 0); }
      }, 450);
    });
  }
  /* 票头的颜色：系列页从页底那张票根的变量取，章节页从胶片色卡那颗按钮取，都没有就用默认的深蓝 */
  function ticketPalette() {
    var tk = document.getElementById("js-series-ticket");
    if (tk) {
      var cs = getComputedStyle(tk);
      return { bg: cs.getPropertyValue("--tk-bg").trim() || "#15213f", accent: cs.getPropertyValue("--tk-accent").trim() || "#ecc84f", text: cs.getPropertyValue("--tk-text").trim() || "#ece9e2" };
    }
    var sw = document.querySelector("[data-au-bg]");
    if (sw) return { bg: sw.getAttribute("data-au-bg") || "#15213f", accent: sw.getAttribute("data-au-accent") || "#ecc84f", text: sw.getAttribute("data-au-text") || "#ece9e2" };
    return { bg: "#15213f", accent: "#ecc84f", text: "#ece9e2" };
  }
  function openEditor(id, kind) {
    loadFonts();
    if (!backdrop) buildEditor();
    id = normPath(id);
    var ed = backdrop.querySelector(".pol-editor");
    var isTicket = kind === "ticket";
    ed.classList.toggle("pol-editor--ticket", isTicket);
    ed.setAttribute("aria-label", isTicket ? "票根背面" : "照片背面");
    if (isTicket) {
      var pal = ticketPalette();
      ed.style.setProperty("--pol-tk-bg", pal.bg); ed.style.setProperty("--pol-tk-accent", pal.accent); ed.style.setProperty("--pol-tk-text", pal.text);
    }
    backdrop.querySelector(".pol-ed-line").textContent = isTicket ? TICKET_TAGLINE : NOTE_TAGLINE;
    backdrop.querySelector(".pol-ed-line-en").textContent = isTicket ? TICKET_TAGLINE_EN : NOTE_TAGLINE_EN;
    loadNoteInto(id);
    backdrop.classList.add("open");
    var film = backdrop.querySelector(".pol-film"), chap = backdrop.querySelector(".pol-ed-chap"), adm = backdrop.querySelector(".pol-ed-adm");
    film.hidden = true; chap.hidden = true; adm.textContent = isTicket ? "Admit One" : "";
    if (isTicket) renderFilm(id);
    if (unlocked) setTimeout(function () { note.focus(); }, 420);
  }
  /* 把某一张背面的字和划线装进编辑器（翻票号时也走这里） */
  function loadNoteInto(id) {
    flushNote();
    current = id;
    var n = Store.get(id);
    note.value = n.text;
    note.readOnly = !unlocked;
    note.placeholder = unlocked ? "写下你不想忘记的……" : "🔒 解锁后可编辑";
    tsEl.textContent = n.ts ? "上次编辑 " + fmt(n.ts) : "";
    renderEditorMarks(id);
  }
  function flushNote() {
    if (!saveTimer || !current || !unlocked) return;
    clearTimeout(saveTimer); saveTimer = null;
    Store.set(current, note.value); markDogears();
  }
  function closeEditor() { flushNote(); if (backdrop) backdrop.classList.remove("open"); current = null; if (deskEl) renderDeskLedger(); }

  /* —— 票根背面顶上的胶片齿孔格：这个系列的章节票号，写过的亮着，点一格翻到那一章的背面 —— */
  function renderFilm(id) {
    var film = backdrop.querySelector(".pol-film"), chap = backdrop.querySelector(".pol-ed-chap"), adm = backdrop.querySelector(".pol-ed-adm");
    loadMap(function (map) {
      if (normPath(current) !== id) return;
      var sp = map.series && map.series[id], po = map.posts && map.posts[id];
      var sname = sp ? sp.s : (po ? po.s : null);
      if (!sname) return;
      var seriesPath = null, k;
      for (k in map.series) if (map.series.hasOwnProperty(k) && map.series[k].s === sname) { seriesPath = k; break; }
      var chaps = [];
      for (k in map.posts) if (map.posts.hasOwnProperty(k) && map.posts[k].s === sname) chaps.push({ path: k, p: map.posts[k] });
      chaps.sort(function (a, b) { var wa = a.p.k === "main" ? 0 : 1, wb = b.p.k === "main" ? 0 : 1; return wa - wb || (a.p.n || 0) - (b.p.n || 0) || (a.p.d > b.p.d ? 1 : -1); });
      var notes = Store.all(), marks = Marks.all();
      function lit(p) { var n = notes[p]; return !!((n && n.text && n.text.trim()) || (marks[p] && marks[p].length)); }
      var html = '<span class="pol-film-holes" aria-hidden="true"></span><div class="pol-film-cells">';
      if (seriesPath) html += '<button type="button" class="pol-film-cell is-series' + (seriesPath === id ? " is-on" : "") + (lit(seriesPath) ? " is-lit" : "") + '" data-path="' + esc(seriesPath) + '">系列</button>';
      for (var i = 0; i < chaps.length; i++) {
        var c = chaps[i];
        html += '<button type="button" class="pol-film-cell' + (c.path === id ? " is-on" : "") + (lit(c.path) ? " is-lit" : "") + '" data-path="' + esc(c.path) + '" title="' + esc(chapTitle(c.p.t)) + '">' + stubOf(c.p) + '</button>';
      }
      html += '</div><span class="pol-film-holes" aria-hidden="true"></span>';
      film.innerHTML = html; film.hidden = false;
      var on = film.querySelector(".pol-film-cell.is-on");
      if (on && on.scrollIntoView) { try { on.scrollIntoView({ block: "nearest", inline: "center" }); } catch (e) {} }
      var cells = film.querySelectorAll(".pol-film-cell");
      for (var j = 0; j < cells.length; j++) {
        (function (b) {
          b.addEventListener("click", function () {
            var p = b.getAttribute("data-path");
            loadNoteInto(p);
            renderFilm(p);
          });
        })(cells[j]);
      }
      // 票头：系列的背面印 Admit One · 系列名；某一章印票号 + 章名 + 去读
      if (po) {
        adm.textContent = "Admit One · " + (stubOf(po) === "EX" || stubOf(po) === "POV" || stubOf(po) === "IF" ? stubOf(po) : "No. " + stubOf(po));
        var onPage = isArticlePage() && normPath(location.pathname) === id;
        chap.innerHTML = '<b>' + esc(chapTitle(po.t)) + '</b>' + (onPage ? '<i>就是这一章</i>' : '<a href="' + esc(id) + '">去读这一章 →</a>');
        chap.hidden = false;
      } else {
        adm.textContent = "Admit One · " + (sp ? sp.t : "");
        chap.hidden = true;
      }
    });
  }

  /* ========== 折角记号（仅本机有批注的卡片）========== */
  function markDogears() {
    var posts = document.querySelectorAll(".c-post, .c-chapter-card, .c-stub-ticket");
    for (var i = 0; i < posts.length; i++) {
      var a = posts[i];
      var n = Store.get(keyOf(a));
      var has = !!(n.text && n.text.trim());
      a.classList.toggle("has-note", has);
      if (has && !a.querySelector(".pol-dogear")) {
        var d = document.createElement("span"); d.className = "pol-dogear"; a.appendChild(d);
      }
    }
  }

  /* ========== 卡片交互（仅解锁后拦截右键 / 长按）========== */
  function attachCards() {
    var posts = document.querySelectorAll(".c-post, .c-chapter-card, .c-stub-ticket");
    for (var i = 0; i < posts.length; i++) {
      (function (a) {
        var kind = (a.classList.contains("c-chapter-card") || a.classList.contains("c-stub-ticket")) ? "ticket" : "photo";
        a.addEventListener("contextmenu", function (e) {
          if (!unlocked) return;          // 锁定时保留浏览器默认右键，不打扰访客
          e.preventDefault();
          openEditor(keyOf(a), kind);
        });
        var timer = null, moved = false, longFired = false;
        a.addEventListener("touchstart", function () {
          if (!unlocked) return;
          moved = false; longFired = false;
          timer = setTimeout(function () { if (!moved) { longFired = true; openEditor(keyOf(a), kind); } }, LONGPRESS_MS);
        }, { passive: true });
        a.addEventListener("touchmove", function () { moved = true; clearTimeout(timer); }, { passive: true });
        a.addEventListener("touchend", function () { clearTimeout(timer); }, { passive: true });
        a.addEventListener("click", function (e) {
          if (longFired) { e.preventDefault(); e.stopPropagation(); longFired = false; } // 长按后不跳转文章
        });
      })(posts[i]);
    }
  }


  /* ========== 钢笔小钮 + 小册子（2026-10-15 起，取代左下角长条浮标和叠在上面的日记卡）========== */
  var BASEURL = (typeof window !== "undefined" && window.SITE_BASEURL) || "";
  var DESK_URL = BASEURL + "/notes/backs/";
  var pinEl, popEl, popOpen = false;
  var PIN_SVG = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
    '<path d="m4 20 3.5-1 10-10-2.5-2.5-10 10z"/><path d="m14 7.5 2.5 2.5"/><path d="M17 4.5 19.5 7"/></svg>';
  function buildLock() {
    pinEl = document.createElement("button");
    pinEl.type = "button";
    pinEl.className = "pol-pin";
    pinEl.title = LOCK_LABEL + " · " + LOCK_LABEL_EN;
    pinEl.setAttribute("aria-label", LOCK_LABEL);
    pinEl.setAttribute("aria-expanded", "false");
    pinEl.innerHTML = PIN_SVG;
    document.body.appendChild(pinEl);
    popEl = document.createElement("div");
    popEl.className = "pol-pop";
    popEl.setAttribute("role", "dialog");
    popEl.setAttribute("aria-label", LOCK_LABEL);
    popEl.hidden = true;
    document.body.appendChild(popEl);
    pinEl.addEventListener("click", function (e) {
      // 缩在屏幕边上时，第一下点击只负责把它叫回来
      if (pinEl.classList.contains("is-tucked")) { e.preventDefault(); pinEl.classList.remove("is-tucked"); return; }
      togglePop();
    });
    document.addEventListener("click", function (e) {
      if (!popOpen) return;
      if (popEl.contains(e.target) || pinEl.contains(e.target)) return;
      closePop();
    });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && popOpen) closePop(); });
    lockEl = pinEl;   // 老名字还有几处在用
  }
  var lockEl;
  function togglePop() { if (popOpen) closePop(); else openPop(); }
  function openPop() {
    renderLock();
    popEl.hidden = false; popOpen = true;
    pinEl.classList.add("is-open"); pinEl.setAttribute("aria-expanded", "true");
    if (boxEl) boxEl.classList.remove("open");
  }
  function closePop() {
    popEl.hidden = true; popOpen = false;
    pinEl.classList.remove("is-open"); pinEl.setAttribute("aria-expanded", "false");
  }

  /* —— 会让路（2026-10-05 Winter 挑的 B 方案）：往下滚就缩到屏幕左边只露一小截，往上滚或点那一截就回来。
        册子 / 底片匣开着、正在输密码时不躲。 —— */
  function lockAutoHide() {
    if (!pinEl) return;
    var lastY = window.pageYOffset || 0;
    function busy() {
      if (popOpen) return true;
      if (boxEl && boxEl.classList.contains("open")) return true;
      return false;
    }
    window.addEventListener("scroll", function () {
      var y = window.pageYOffset || 0;
      if (busy()) { lastY = y; return; }
      if (y > lastY + 8 && y > 64) pinEl.classList.add("is-tucked");
      else if (y < lastY - 8 || y < 48) pinEl.classList.remove("is-tucked");
      lastY = y;
    }, { passive: true });
  }

  /* 册子里的内容：解锁了＝总账 + 工具；没解锁＝访客那张拍立得 + 验笔迹 */
  function renderLock() {
    if (!popEl) return;
    var head = '<div class="pol-pop-head"><span class="pol-pop-brand">' + PEN_SVG + CAM_SVG +
      '<b>' + LOCK_LABEL + '</b><i>' + LOCK_LABEL_EN + '</i></span>' +
      (unlocked ? '<span class="pol-pop-state">笔迹已验 · Verified</span>' : '') + '</div>';
    if (!unlocked) {
      popEl.innerHTML = head +
        '<button class="pol-guest" type="button" aria-label="翻看这张照片的背面">' +
          '<span class="pol-card-photo">' + SCENES.guest + '</span>' +
          '<span class="pol-card-cap pol-guest-cap"><span class="pol-card-q1">' + GUEST.q1 + '</span><span class="pol-card-q2">' + GUEST.q2 + '</span>' +
          '<span class="pol-card-credit">' + GUEST.credit + '</span><span class="pol-guest-sign">' + GUEST.sign + '</span></span></button>' +
        '<div class="pol-pop-pw"><input class="pol-pw" type="password" placeholder="' + (hasPass() ? "prove you&#39;re Leo — or Winter…" : "sign it — Leo &amp; Winter…") + '">' +
        '<button class="pol-go" type="button">' + (hasPass() ? "验明" : "印记") + '</button></div>';
      popEl.querySelector(".pol-guest .pol-card-photo").style.background = GUEST.grad;
      popEl.querySelector(".pol-guest").addEventListener("click", function () { closePop(); openGuestBack(); });
      wirePw(popEl.querySelector(".pol-pw"), popEl.querySelector(".pol-go"));
      return;
    }
    var acts = '';
    if (isArticlePage()) acts += '<button class="pol-pop-act" type="button" data-act="here"><b>写在这一篇的背面</b><i>' + (isTicketPage() ? '票根 · Ticket' : '相纸 · Polaroid') + '</i></button>';
    var tk = document.getElementById("js-series-ticket");
    if (tk) acts += '<button class="pol-pop-act" type="button" data-act="ticket"><b>翻开这个系列的票根</b><i>Series stub</i></button>';
    popEl.innerHTML = head + acts +
      '<div class="pol-pop-sub">所有的背面 · <span class="pol-pop-count"></span></div>' +
      '<div class="pol-ledger pol-ledger--pop"><p class="pol-ledger-empty">正在翻…</p></div>' +
      '<div class="pol-pop-foot">' +
        '<button class="pol-pop-link" type="button" data-act="box">底片匣</button>' +
        '<a class="pol-pop-link" href="' + DESK_URL + '">去书桌「冬的背面」</a>' +
        '<button class="pol-pop-link pol-pop-seal" type="button" data-act="lock">封存</button>' +
      '</div>';
    popEl.querySelector('[data-act="lock"]').addEventListener("click", function () {
      localStorage.removeItem(LS_UNLOCK); unlocked = false;
      if (boxEl) boxEl.classList.remove("open");
      closePop(); syncDeckVisible(); markDogears();
    });
    popEl.querySelector('[data-act="box"]').addEventListener("click", function () { closePop(); toggleBox(); });
    var here = popEl.querySelector('[data-act="here"]');
    if (here) here.addEventListener("click", function () { closePop(); openEditor(location.pathname, isTicketPage() ? "ticket" : "photo"); });
    var tkb = popEl.querySelector('[data-act="ticket"]');
    if (tkb) tkb.addEventListener("click", function () { closePop(); openEditor(keyOf(tk), "ticket"); });
    renderLedger(popEl.querySelector(".pol-ledger"), popEl.querySelector(".pol-pop-count"), { compact: true, onPick: closePop });
  }
  function wirePw(pw, go) {
    var setting = !hasPass();
    function submit() {
      var v = pw.value.trim(); if (!v) return;
      if (setting) {
        localStorage.setItem(LS_PASS_DEV, hash(v));
        localStorage.setItem(LS_UNLOCK, "1"); unlocked = true;
      } else if (hash(v) === passHash()) {
        localStorage.setItem(LS_UNLOCK, "1"); unlocked = true;
      } else { pw.value = ""; pw.placeholder = "not their hand… try again"; return; }
      syncDeckVisible(); markDogears(); renderLock();
      if (deskEl) renderDesk();
    }
    go.addEventListener("click", submit);
    pw.addEventListener("keydown", function (e) { if (e.key === "Enter") submit(); });
    setTimeout(function () { try { pw.focus(); } catch (e) {} }, 60);
  }
  function showPwInput() { openPop(); }

  /* ========== 背面的总账：哪些票 / 照片写过字、划过线（本机），按系列分组 ========== */
  var mapCache = null, mapLoading = null;
  function loadMap(done) {
    if (mapCache) { done(mapCache); return; }
    if (mapLoading) { mapLoading.push(done); return; }
    mapLoading = [done];
    fetch(BASEURL + "/backs-map.json", { cache: "force-cache" })
      .then(function (r) { return r.json(); })
      .then(function (m) { mapCache = m || { posts: {}, series: {} }; })
      .catch(function () { mapCache = { posts: {}, series: {} }; })
      .then(function () { var q = mapLoading; mapLoading = null; for (var i = 0; i < q.length; i++) q[i](mapCache); });
  }
  function normPath(p) { p = (p || "").replace(/index\.html$/, ""); return p.slice(-1) === "/" ? p : p + "/"; }
  function chapTitle(raw) { return (raw || "").replace(/^(Chapter|Episode|Extra|Oneshot)[^·]*·\s*/i, "").replace(/\s+—.*$/, ""); }
  function stubOf(p) {
    if (!p) return "";
    if (p.k === "main" && p.n) return (p.n < 10 ? "0" : "") + p.n;
    if (p.k === "pov") return "POV";
    return p.c && /IF/.test(p.c) ? "IF" : (p.k === "main" ? "ONE" : "EX");
  }
  /* 把 notes + marks 两张表合成「一张背面一行」，再按系列分组 */
  function ledgerGroups(map) {
    var notes = Store.all(), marks = Marks.all(), keys = {}, k;
    for (k in notes) if (notes.hasOwnProperty(k) && notes[k].text && notes[k].text.trim()) keys[normPath(k)] = true;
    for (k in marks) if (marks.hasOwnProperty(k) && marks[k].length) keys[normPath(k)] = true;
    var groups = {}, order = [];
    function grp(id, title, sub) { if (!groups[id]) { groups[id] = { id: id, title: title, sub: sub, rows: [] }; order.push(id); } return groups[id]; }
    for (k in keys) {
      var n = notes[k] || notes[k.replace(/\/$/, "")] || null, mk = (marks[k] || []).length;
      var row = { path: k, note: n && n.text ? n.text.trim() : "", marks: mk, ts: n ? n.ts : 0 };
      var sp = map.series && map.series[k], po = map.posts && map.posts[k];
      if (sp) { var g1 = grp("s:" + sp.s, sp.t, sp.who); row.stub = "票"; row.title = "系列的背面"; row.kind = "ticket"; row.n = -1; g1.rows.push(row); g1.sp = sp; }
      else if (po && po.s) { var g2 = grp("s:" + po.s, po.st || po.s, ""); row.stub = stubOf(po); row.title = chapTitle(po.t); row.kind = "ticket"; row.n = po.k === "main" ? (po.n || 0) : 1000 + (po.n || 0); g2.rows.push(row); }
      else if (po) { var g3 = grp("photo", "照片", "Winter&rsquo;s"); row.stub = "照"; row.title = po.t; row.kind = "photo"; row.n = 0; g3.rows.push(row); }
      else { var g4 = grp("other", "别的背面", ""); row.stub = "·"; row.title = k; row.kind = /\/\d{4}\/\d{2}\/\d{2}\//.test(k) ? "ticket" : "photo"; row.n = 0; g4.rows.push(row); }
    }
    var out = [];
    for (var i = 0; i < order.length; i++) {
      var g = groups[order[i]];
      g.rows.sort(function (a, b) { return a.n - b.n; });
      out.push(g);
    }
    // 系列名下带系列背面的排前面；照片组放最后
    out.sort(function (a, b) { var wa = a.id === "photo" ? 2 : a.id === "other" ? 3 : 1, wb = b.id === "photo" ? 2 : b.id === "other" ? 3 : 1; return wa - wb || (b.rows.length - a.rows.length); });
    return out;
  }
  function esc(t) { return String(t == null ? "" : t).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;"); }
  function renderLedger(el, countEl, opt) {
    opt = opt || {};
    loadMap(function (map) {
      var groups = ledgerGroups(map), total = 0, html = "";
      for (var i = 0; i < groups.length; i++) {
        var g = groups[i]; total += g.rows.length;
        html += '<div class="pol-ledger-grp"><b>' + esc(g.title) + '</b>' + (g.sub ? '<em>' + g.sub + '</em>' : '') + '<small>' + g.rows.length + ' 张</small></div>';
        for (var r = 0; r < g.rows.length; r++) {
          var row = g.rows[r];
          var meta = (row.note ? "1 条" : "") + (row.note && row.marks ? " · " : "") + (row.marks ? row.marks + " 划线" : "");
          html += '<button class="pol-ledger-row" type="button" data-path="' + esc(row.path) + '" data-kind="' + row.kind + '">' +
            '<span class="pol-ledger-no' + (row.stub === "票" ? " is-series" : row.stub === "照" ? " is-photo" : "") + '">' + esc(row.stub) + '</span>' +
            '<span class="pol-ledger-t">' + esc(row.title) + (opt.compact || !row.note ? "" : '<small>' + esc(row.note.slice(0, 40)) + (row.note.length > 40 ? "…" : "") + '</small>') + '</span>' +
            '<span class="pol-ledger-m">' + meta + '</span></button>';
        }
      }
      if (!total) html = '<p class="pol-ledger-empty">还没有写过的背面。右键（电脑）或长按（手机）一张照片、一张票根，翻过去写一句。</p>';
      el.innerHTML = html;
      if (countEl) countEl.textContent = total + " 张";
      var rows = el.querySelectorAll(".pol-ledger-row");
      for (var j = 0; j < rows.length; j++) {
        (function (b) {
          b.addEventListener("click", function () {
            if (opt.onPick) opt.onPick();
            openEditor(b.getAttribute("data-path"), b.getAttribute("data-kind"));
          });
        })(rows[j]);
      }
    });
  }

  /* ========== 收纳盒：导出 / 导入（设备间搬家）========== */
  function pad(n) { return n < 10 ? "0" + n : "" + n; }
  function noteCount() {
    var a = Store.all(), c = 0;
    for (var k in a) if (a.hasOwnProperty(k) && a[k].text && a[k].text.trim()) c++;
    return c;
  }
  function exportNotes() {
    var journals = {};
    for (var i = 0; i < JOURNALS.length; i++) journals[JOURNALS[i].id] = storeOf(JOURNALS[i]).all();
    var data = { app: "wiw-polaroid-notes", v: 3, exported: Date.now(), notes: Store.all(), journals: journals, marks: Marks.all() };
    var blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    var url = URL.createObjectURL(blob);
    var d = new Date();
    var name = "polaroid-notes-" + d.getFullYear() + pad(d.getMonth() + 1) + pad(d.getDate()) + ".json";
    var a = document.createElement("a"); a.href = url; a.download = name;
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  }
  function importNotes(file, done) {
    var reader = new FileReader();
    reader.onload = function () {
      try {
        var data = JSON.parse(reader.result);
        var incoming = (data && data.notes) ? data.notes : data; // 兼容直接传相片表
        if (!incoming || typeof incoming !== "object") { done(new Error("文件格式不对")); return; }
        var cur = Store.all(), added = 0, updated = 0;
        for (var id in incoming) {
          if (!incoming.hasOwnProperty(id)) continue;
          var inc = incoming[id];
          if (!inc || typeof inc.text !== "string") continue;
          var ex = cur[id];
          if (!ex) { cur[id] = inc; added++; }
          else if ((inc.ts || 0) > (ex.ts || 0) && inc.text !== ex.text) { cur[id] = inc; updated++; }
        }
        localStorage.setItem(LS_NOTES, JSON.stringify(cur));
        // 划线合并（按 文字+指纹 去重）
        if (data && data.marks && typeof data.marks === "object") {
          var curMarks = Marks.all();
          for (var mp in data.marks) {
            if (!data.marks.hasOwnProperty(mp)) continue;
            var mine = curMarks[mp] || [], theirs = data.marks[mp] || [];
            for (var ti = 0; ti < theirs.length; ti++) {
              var tm = theirs[ti], dup = false;
              for (var mi = 0; mi < mine.length; mi++) {
                if (mine[mi].t === tm.t && mine[mi].p === tm.p && mine[mi].s === tm.s) { dup = true; break; }
              }
              if (!dup) mine.push(tm);
            }
            if (mine.length) curMarks[mp] = mine;
          }
          try { localStorage.setItem(LS_MARKS, JSON.stringify(curMarks)); } catch (e) {}
        }
        // 各 journal 也一并合并（按日期，谁更新留谁）
        var incJournals = (data && data.journals) ? data.journals
          : (data && data.lucky) ? { fortunes: data.lucky } : null;   // 兼容旧 v1 的 lucky 字段
        if (incJournals) {
          for (var jid in incJournals) {
            if (!incJournals.hasOwnProperty(jid)) continue;
            var j = journalById(jid); if (!j) continue;
            var st = storeOf(j), curMap = st.all(), inMap = incJournals[jid];
            if (!inMap || typeof inMap !== "object") continue;
            for (var day in inMap) {
              if (!inMap.hasOwnProperty(day)) continue;
              var rec = inMap[day]; if (!rec) continue;
              if (!curMap[day] || (rec.ts || 0) > (curMap[day].ts || 0)) curMap[day] = rec;
            }
            try { localStorage.setItem(j.ls, JSON.stringify(curMap)); } catch (e) {}
          }
        }
        done(null, { added: added, updated: updated });
      } catch (e) { done(e); }
    };
    reader.onerror = function () { done(reader.error || new Error("读取失败")); };
    reader.readAsText(file);
  }

  var boxEl, boxCount, boxMsg, boxFile;
  function buildBox(parent) {
    boxEl = document.createElement("div");
    boxEl.className = "pol-box" + (parent ? " is-inline open" : "");
    boxEl.innerHTML =
      '<div class="pol-box-head"><span class="pol-box-title"><b>底片匣</b><i>Negatives</i></span><button class="pol-box-x" type="button" aria-label="关闭">×</button></div>' +
      '<p class="pol-box-count"></p>' +
      '<button class="pol-box-btn" type="button" data-act="export"><b>取出底片<i>Take the negatives</i></b><small>打包下载，带去手机 / 新设备冲印</small></button>' +
      '<button class="pol-box-btn" type="button" data-act="import"><b>装入底片<i>Load them back</i></b><small>选一个之前取出的文件，恢复相片</small></button>' +
      '<input class="pol-box-file" type="file" accept="application/json,.json" hidden>' +
      '<p class="pol-box-msg"></p>';
    (parent || document.body).appendChild(boxEl);
    boxCount = boxEl.querySelector(".pol-box-count");
    boxMsg = boxEl.querySelector(".pol-box-msg");
    boxFile = boxEl.querySelector(".pol-box-file");
    boxEl.querySelector(".pol-box-x").addEventListener("click", function () { boxEl.classList.remove("open"); });
    boxEl.querySelector('[data-act="export"]').addEventListener("click", function () {
      if (noteCount() === 0) { setMsg("底片匣是空的，还没有相片可取出。"); return; }
      exportNotes(); setMsg("底片已取出 ✓ 文件已下载，带去新设备装入即可。");
    });
    boxEl.querySelector('[data-act="import"]').addEventListener("click", function () { boxFile.click(); });
    boxFile.addEventListener("change", function () {
      var f = boxFile.files && boxFile.files[0]; if (!f) return;
      importNotes(f, function (err, r) {
        boxFile.value = "";
        if (err) { setMsg("装入失败：" + (err.message || "底片读不出来")); return; }
        markDogears(); refreshBox();
        setMsg("装入完成 ✓ 新增 " + r.added + " 张，更新 " + r.updated + " 张。");
      });
    });
  }
  function setMsg(t) { if (boxMsg) { boxMsg.textContent = t; boxMsg.classList.add("show"); } }
  function refreshBox() { if (boxCount) boxCount.textContent = "这台设备上存有 " + noteCount() + " 张相片"; }
  function toggleBox() {
    if (!boxEl) buildBox();
    if (boxEl.classList.contains("is-inline")) { refreshBox(); return; }
    var open = boxEl.classList.toggle("open");
    if (open) { refreshBox(); if (boxMsg) boxMsg.classList.remove("show"); }
  }

  /* ========== 角落卡组：一叠拍立得，每张一个用途（仅解锁后可见）========== */
  var LUCKY_MARKS = ["一", "二", "三"];
  var EN_WK = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
  var EN_MON = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  function todayKey() { var d = new Date(); return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()); }
  function dayLabel(key) {
    var p = key.split("-"); var d = new Date(+p[0], +p[1] - 1, +p[2]);
    return EN_WK[d.getDay()] + " · " + (+p[2]) + " " + EN_MON[+p[1] - 1] + " " + p[0];
  }
  function pinDate() { var d = new Date(); return d.getDate() + " " + EN_MON[d.getMonth()]; }

  var deckEl = null, guestEl = null, guestBack;
  /* 照片背面：黑条印一句 + 手写短笺 + 故事链接 */
  function buildGuestBack() {
    var base = (typeof window !== "undefined" && window.SITE_BASEURL) || "";
    guestBack = document.createElement("div");
    guestBack.className = "pol-backdrop pol-guest-backdrop";
    var notes = "";
    for (var i = 0; i < GUEST.note.length; i++) notes += '<div class="pol-gb-pair"><p class="pol-gb-zh">' + GUEST.note[i].zh + '</p><p class="pol-gb-en">' + GUEST.note[i].en + "</p></div>";
    guestBack.innerHTML =
      '<div class="pol-guest-flip" role="dialog" aria-label="照片背面">' +
        '<button class="pol-ed-x pol-gb-x" type="button" title="翻回" aria-label="翻回">↩</button>' +
        '<div class="pol-gb-strip"><span>' + GUEST.backLine + '</span></div>' +
        '<div class="pol-gb-note">' + notes + '</div>' +
        '<a class="pol-gb-link" href="' + base + GUEST.href + '">' + GUEST.linkLabel + '</a>' +
      '</div>';
    document.body.appendChild(guestBack);
    guestBack.querySelector(".pol-gb-x").addEventListener("click", closeGuestBack);
    guestBack.addEventListener("click", function (e) { if (e.target === guestBack) closeGuestBack(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && guestBack.classList.contains("open")) closeGuestBack(); });
  }
  function openGuestBack() {
    loadFonts();
    if (!guestBack) buildGuestBack();
    guestBack.querySelector(".pol-gb-note").style.fontFamily = NOTE_FONT;
    guestBack.classList.add("open");
  }
  function closeGuestBack() { if (guestBack) guestBack.classList.remove("open"); }
  function syncDeckVisible() {
    if (unlocked && guestBack) guestBack.classList.remove("open");
    if (!unlocked && jBack) jBack.classList.remove("open");
    if (unlocked) loadFonts();
  }

  /* —— 共用的翻开编辑卡（按当前 journal 的 kind 重建内页）—— */
  var jBack, jCardEl, jThemeEl, jDateEl, jSavedEl, jHintEl, jBodyEl, jSendMsgEl, curJournal = null, curDay = null, jInputs = [], jSaveTimer = null;
  var letterSubj, letterRead, letterBody, whenChips = []; // 信卡专用：标题 / 写给何时 / 正文 / 时间预设按钮
  function autoGrow(t) { t.style.height = "auto"; t.style.height = Math.max(30, t.scrollHeight) + "px"; }
  function flashSaved() { if (jSavedEl) { jSavedEl.classList.add("show"); setTimeout(function () { jSavedEl.classList.remove("show"); }, 1200); } }
  function buildJournalEditor() {
    jBack = document.createElement("div");
    jBack.className = "pol-backdrop pol-lucky-backdrop";
    jBack.innerHTML =
      '<div class="pol-lucky-card" role="dialog">' +
        '<div class="pol-lucky-top">' +
          '<button class="pol-lucky-nav" type="button" data-d="-1" aria-label="前一天">‹</button>' +
          '<span class="pol-lucky-date"></span>' +
          '<button class="pol-lucky-nav" type="button" data-d="1" aria-label="后一天">›</button>' +
        '</div>' +
        '<div class="pol-lucky-body"></div>' +
        '<div class="pol-lucky-foot"><span class="pol-lucky-hint"></span>' +
          '<span class="pol-lucky-foot-r"><span class="pol-lucky-sendmsg"></span><span class="pol-saved pol-lucky-saved">已收好 ✓</span>' +
          '<button class="pol-lucky-send" type="button">封缄寄出</button>' +
          '<button class="pol-lucky-x" type="button">收起</button></span></div>' +
      '</div>';
    document.body.appendChild(jBack);
    jCardEl = jBack.querySelector(".pol-lucky-card");
    jThemeEl = jBack.querySelector(".pol-theme");
    jDateEl = jBack.querySelector(".pol-lucky-date");
    jSavedEl = jBack.querySelector(".pol-lucky-saved");
    jHintEl = jBack.querySelector(".pol-lucky-hint");
    jBodyEl = jBack.querySelector(".pol-lucky-body");
    jSendMsgEl = jBack.querySelector(".pol-lucky-sendmsg");
    var navs = jBack.querySelectorAll(".pol-lucky-nav");
    for (var i = 0; i < navs.length; i++) { (function (b) { b.addEventListener("click", function () { shiftDay(+b.getAttribute("data-d")); }); })(navs[i]); }
    jBack.querySelector(".pol-lucky-send").addEventListener("click", sendLetter);
    jBack.querySelector(".pol-lucky-x").addEventListener("click", closeJournal);
    jBack.addEventListener("click", function (e) { if (e.target === jBack) closeJournal(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && jBack.classList.contains("open")) closeJournal(); });
  }
  function makeTextarea(onInput) {
    var ta = document.createElement("textarea");
    ta.className = "pol-lucky-in"; ta.rows = 1; ta.spellcheck = false; ta.placeholder = "……";
    ta.style.fontFamily = NOTE_FONT;
    ta.addEventListener("input", function () { autoGrow(ta); onInput(); });
    return ta;
  }
  function makeInput() { return makeTextarea(scheduleJournalSave); }
  function buildBodyFor(j) {
    jBodyEl.innerHTML = ""; jInputs = []; letterSubj = letterRead = letterBody = null;
    if (j.kind === "three") {
      for (var i = 0; i < 3; i++) {
        var row = document.createElement("label"); row.className = "pol-lucky-row";
        var no = document.createElement("span"); no.className = "pol-lucky-no"; no.textContent = LUCKY_MARKS[i];
        var ta = makeInput();
        row.appendChild(no); row.appendChild(ta); jBodyEl.appendChild(row); jInputs.push(ta);
      }
    } else if (j.kind === "letter") {
      var f1 = document.createElement("label"); f1.className = "pol-letter-field";
      var l1 = document.createElement("span"); l1.className = "pol-letter-lab"; l1.textContent = "标题";
      letterSubj = document.createElement("input"); letterSubj.type = "text"; letterSubj.className = "pol-letter-in"; letterSubj.placeholder = "给这封信起个标题（可留空）…";
      letterSubj.addEventListener("input", scheduleLetterSave);
      f1.appendChild(l1); f1.appendChild(letterSubj);
      // 写给何时的自己：一排预设快捷 + 自定义日期
      var f2 = document.createElement("div"); f2.className = "pol-letter-field pol-letter-when-field";
      var l2 = document.createElement("span"); l2.className = "pol-letter-lab"; l2.textContent = "写给";
      var when = document.createElement("div"); when.className = "pol-when";
      whenChips = [];
      for (var w = 0; w < WHEN_PRESETS.length; w++) {
        (function (p) {
          var c = document.createElement("button"); c.type = "button"; c.className = "pol-when-chip";
          c.textContent = p.label; c.setAttribute("data-key", computePreset(p));
          c.addEventListener("click", function () { letterRead.value = c.getAttribute("data-key"); syncWhenChips(); scheduleLetterSave(); });
          when.appendChild(c); whenChips.push(c);
        })(WHEN_PRESETS[w]);
      }
      letterRead = document.createElement("input"); letterRead.type = "date"; letterRead.className = "pol-letter-date pol-when-date";
      letterRead.title = "或自选一个日期";
      letterRead.addEventListener("input", function () { syncWhenChips(); scheduleLetterSave(); });
      when.appendChild(letterRead);
      f2.appendChild(l2); f2.appendChild(when);
      letterBody = makeTextarea(scheduleLetterSave); letterBody.classList.add("pol-lucky-free");
      jBodyEl.appendChild(f1); jBodyEl.appendChild(f2); jBodyEl.appendChild(letterBody);
    } else {
      var free = makeInput(); free.classList.add("pol-lucky-free");
      jBodyEl.appendChild(free); jInputs.push(free);
    }
  }
  var THEME_VARS = ["--c-bg", "--c-strip", "--c-strip-ink", "--c-text", "--c-muted", "--c-accent", "--c-line"];
  function applyTheme(j) {
    if (!jCardEl) return;
    var t = themeById(themeKeyOf(j.id));
    if (!t) {
      for (var k = 0; k < THEME_VARS.length; k++) jCardEl.style.removeProperty(THEME_VARS[k]);
      jCardEl.classList.remove("is-themed"); return;
    }
    var v = cardVars(t, isDarkSite());
    jCardEl.style.setProperty("--c-bg", v.bg);
    jCardEl.style.setProperty("--c-strip", v.strip);
    jCardEl.style.setProperty("--c-strip-ink", v.stripInk);
    jCardEl.style.setProperty("--c-text", v.text);
    jCardEl.style.setProperty("--c-muted", v.muted);
    jCardEl.style.setProperty("--c-accent", v.accent);
    jCardEl.style.setProperty("--c-line", v.line);
    jCardEl.classList.add("is-themed");
  }
  function renderThemeBar(j) {
    if (!jThemeEl) return;
    jThemeEl.innerHTML = "";
    var tip = document.createElement("span"); tip.className = "pol-sw-tip"; jThemeEl.appendChild(tip);
    var cur = themeKeyOf(j.id);
    var opts = [{ id: "", original: true, label: "原色 · Original" }];
    var list = samThemes();
    for (var k = 0; k < list.length; k++) {
      var t = list[k];
      opts.push({ id: t.id, accent: t.accent, label: (t.name || "") + (t.cn ? " · " + t.cn : "") });
    }
    for (var i = 0; i < opts.length; i++) {
      (function (o) {
        var b = document.createElement("button");
        b.type = "button"; b.className = "pol-sw" + (o.original ? " pol-sw-og" : "") + (o.id === cur ? " on" : "");
        if (!o.original) b.style.background = o.accent;
        b.setAttribute("aria-label", o.label);
        b.addEventListener("click", function () { setThemeKey(j.id, o.id); applyTheme(j); renderThemeBar(j); });
        function show() { tip.textContent = o.label; tip.style.left = (b.offsetLeft + b.offsetWidth / 2) + "px"; tip.style.top = b.offsetTop + "px"; tip.classList.add("show"); }
        function hide() { tip.classList.remove("show"); }
        b.addEventListener("mouseenter", show); b.addEventListener("mouseleave", hide);
        b.addEventListener("focus", show); b.addEventListener("blur", hide);
        jThemeEl.appendChild(b);
      })(opts[i]);
    }
  }
  function loadDay(day) {
    curDay = day;
    var rec = storeOf(curJournal).get(day) || {};
    if (curJournal.kind === "three") {
      var items = rec.items || [];
      for (var i = 0; i < jInputs.length; i++) { jInputs[i].value = items[i] || ""; autoGrow(jInputs[i]); }
    } else {
      jInputs[0].value = rec.text || ""; autoGrow(jInputs[0]);
    }
    jDateEl.textContent = dayLabel(day);
  }
  function openJournal(j, day) {
    if (!unlocked) return;
    loadFonts();
    if (!jBack) buildJournalEditor();
    curJournal = j; curDay = null;
    jBack.setAttribute("data-kind", j.kind);
    jHintEl.textContent = j.hint || "";
    buildBodyFor(j);
    jBack.classList.add("open");
    if (jSendMsgEl) jSendMsgEl.classList.remove("show");
    if (j.kind === "letter") {
      jSavedEl.textContent = "已存草稿 ✓";
      jDateEl.textContent = "A letter to myself";
      loadLetter();
      setTimeout(function () { if (letterSubj) letterSubj.focus(); }, 420);
    } else {
      jSavedEl.textContent = "已收好 ✓";
      loadDay(day);
      setTimeout(function () { if (jInputs[0]) jInputs[0].focus(); }, 420);
    }
  }
  function scheduleJournalSave() { clearTimeout(jSaveTimer); jSaveTimer = setTimeout(saveJournal, 450); }
  function saveJournal() {
    if (!curJournal || !curDay) return;
    var rec, empty;
    if (curJournal.kind === "three") {
      var items = []; for (var i = 0; i < jInputs.length; i++) items.push(jInputs[i].value);
      empty = !items.join("").trim(); rec = { items: items };
    } else {
      var text = jInputs[0].value; empty = !text.trim(); rec = { text: text };
    }
    storeOf(curJournal).save(curDay, rec, empty);
    if (jSavedEl) { jSavedEl.classList.add("show"); setTimeout(function () { jSavedEl.classList.remove("show"); }, 1200); }
  }
  function shiftDay(delta) {
    if (!curDay) return;
    saveJournal();
    var p = curDay.split("-"); var d = new Date(+p[0], +p[1] - 1, +p[2]); d.setDate(d.getDate() + delta);
    var key = d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate());
    if (delta > 0 && key > todayKey()) return; // 不翻到未来
    loadDay(key);
  }
  function closeJournal() {
    if (!jBack) return;
    if (curJournal && curJournal.kind === "letter") saveLetterDraft(); else saveJournal();
    jBack.classList.remove("open");
    if (deskEl) renderDeskJournals();
  }

  /* —— 信卡：本地草稿 + 一键寄进自己的邮箱 —— */
  function cnDate(key) { var p = key.split("-"); return (+p[0]) + "年" + (+p[1]) + "月" + (+p[2]) + "日"; }
  // 「写给何时的自己」预设：点一下按今天往后推算出一个日期
  var WHEN_PRESETS = [
    { label: "一个月后", add: function (d) { d.setMonth(d.getMonth() + 1); } },
    { label: "半年后",   add: function (d) { d.setMonth(d.getMonth() + 6); } },
    { label: "一年后",   add: function (d) { d.setFullYear(d.getFullYear() + 1); } },
    { label: "三年后",   add: function (d) { d.setFullYear(d.getFullYear() + 3); } },
    { label: "十年后",   add: function (d) { d.setFullYear(d.getFullYear() + 10); } }
  ];
  function computePreset(p) { var d = new Date(); p.add(d); return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()); }
  function syncWhenChips() { for (var i = 0; i < whenChips.length; i++) whenChips[i].classList.toggle("on", !!letterRead && whenChips[i].getAttribute("data-key") === letterRead.value); }
  function letterRecord() { try { return JSON.parse(localStorage.getItem(curJournal.ls)) || {}; } catch (e) { return {}; } }
  function loadLetter() {
    var r = letterRecord();
    letterSubj.value = r.subject != null ? r.subject : (curJournal.subjectDefault || "");
    letterRead.value = r.readOn || "";
    letterBody.value = r.body || ""; autoGrow(letterBody);
    syncWhenChips();
  }
  function scheduleLetterSave() { clearTimeout(jSaveTimer); jSaveTimer = setTimeout(saveLetterDraft, 450); }
  function saveLetterDraft() {
    if (!curJournal || !letterBody) return;
    var r = { subject: letterSubj.value, readOn: letterRead.value, body: letterBody.value, ts: Date.now() };
    try {
      if (!r.subject.trim() && !r.body.trim() && !r.readOn) localStorage.removeItem(curJournal.ls);
      else localStorage.setItem(curJournal.ls, JSON.stringify(r));
    } catch (e) {}
    flashSaved();
  }
  function whoLine() { return letterRead.value ? "致 " + cnDate(letterRead.value) + " 的你" : "致未来的你"; }
  function composeSubject() {
    var title = (letterSubj.value || "").trim();
    var parts = [whoLine()];
    if (title) parts.push(title);
    parts.push("写于 " + cnDate(todayKey()));
    return parts.join(" · ");
  }
  function composeBody(body) {
    var tail = "—— 写于 " + cnDate(todayKey()) + (letterRead.value ? "，待 " + cnDate(letterRead.value) + " 再读 ——" : " ——");
    return whoLine() + "：\n\n" + body + "\n\n" + tail;
  }
  function setSendMsg(t) { if (jSendMsgEl) { jSendMsgEl.textContent = t; jSendMsgEl.classList.add("show"); } }
  function sendLetter() {
    if (!curJournal || curJournal.kind !== "letter") return;
    var body = (letterBody.value || "").trim();
    if (!body) { setSendMsg("信还是空的呢…"); return; }
    if (!HELLO_ENDPOINT || !WEB3FORMS_KEY) { setSendMsg("还没配好寄信钥匙 :("); return; }
    setSendMsg("封缄寄送中…");
    var fd = new FormData();
    fd.append("access_key", WEB3FORMS_KEY);
    fd.append("from_name", "To Myself");
    fd.append("subject", composeSubject());
    fd.append("message", composeBody(body));
    fetch(HELLO_ENDPOINT, { method: "POST", headers: { "Accept": "application/json" }, body: fd })
      .then(function (res) { return res.json().catch(function () { return { success: res.ok }; }); })
      .then(function (data) {
        if (data && data.success) {
          setSendMsg("已寄出 ✓ 去你的邮箱等它");
          try { localStorage.removeItem(curJournal.ls); } catch (e) {}
          letterSubj.value = curJournal.subjectDefault || ""; letterRead.value = ""; letterBody.value = ""; autoGrow(letterBody); syncWhenChips();
        } else { setSendMsg("没寄出去，待会儿再试…"); }
      })
      .catch(function () { setSendMsg("网络不太顺，待会儿再试…"); });
  }

  /* ========== 铅笔划线：选中正文 → 划线（本机私有），背面引用 + 跳回 ==========
     锚定方式：存「选中文字 + 前后各 20 字指纹」，载入时全文搜索定位；
     原文改动导致定位失败时，引文保留在背面并标「原文已改动」。 */
  var LS_MARKS = "wiw-pol-marks";
  var Marks = {
    all: function () { try { return JSON.parse(localStorage.getItem(LS_MARKS)) || {}; } catch (e) { return {}; } },
    forPath: function (path) { var a = this.all(); return a[path] || []; },
    save: function (path, arr) {
      var a = this.all();
      if (arr && arr.length) a[path] = arr; else delete a[path];
      try { localStorage.setItem(LS_MARKS, JSON.stringify(a)); } catch (e) {}
    }
  };
  function artContainer() { return document.querySelector(".c-article .c-wrap-content"); }
  var BLOCK_SEL = "p, li, blockquote, h1, h2, h3, h4, h5, h6";
  function blockOf(node) {
    var el = node.nodeType === 1 ? node : node.parentNode;
    while (el && el !== document.body) {
      if (el.matches && el.matches(BLOCK_SEL)) return el;
      el = el.parentNode;
    }
    return null;
  }

  /* —— 定位：在容器里按 文字+指纹 找到字符区间，映射成 DOM Range —— */
  function findMarkRange(root, m) {
    var blocks = root.querySelectorAll(BLOCK_SEL);
    var best = null, bestScore = -1;
    for (var b = 0; b < blocks.length; b++) {
      var txt = blocks[b].textContent, from = 0, idx;
      while ((idx = txt.indexOf(m.t, from)) >= 0) {
        var pre = txt.slice(Math.max(0, idx - 20), idx);
        var post = txt.slice(idx + m.t.length, idx + m.t.length + 20);
        var score = 0;
        if (m.p && pre.slice(-m.p.length) === m.p) score += 2; else if (m.p && pre.indexOf(m.p.slice(-6)) >= 0) score += 1;
        if (m.s && post.slice(0, m.s.length) === m.s) score += 2; else if (m.s && post.indexOf(m.s.slice(0, 6)) >= 0) score += 1;
        if (!m.p && !m.s) score = 1;
        if (score > bestScore) { bestScore = score; best = { block: blocks[b], start: idx, end: idx + m.t.length }; }
        from = idx + 1;
      }
    }
    if (!best) return null;
    // 字符偏移 → DOM Range
    var range = document.createRange(), walker = document.createTreeWalker(best.block, NodeFilter.SHOW_TEXT), n, pos = 0, sSet = false;
    while ((n = walker.nextNode())) {
      var len = n.nodeValue.length;
      if (!sSet && pos + len > best.start) { range.setStart(n, best.start - pos); sSet = true; }
      if (sSet && pos + len >= best.end) { range.setEnd(n, best.end - pos); return range; }
      pos += len;
    }
    return null;
  }
  /* —— 给 Range 里的每个文本节点套 <span class="pol-line"> —— */
  function paintRange(range, idx) {
    var nodes = [], walker = document.createTreeWalker(range.commonAncestorContainer.nodeType === 3 ? range.commonAncestorContainer.parentNode : range.commonAncestorContainer, NodeFilter.SHOW_TEXT), n;
    while ((n = walker.nextNode())) { if (range.intersectsNode(n)) nodes.push(n); }
    for (var i = 0; i < nodes.length; i++) {
      var node = nodes[i], s0 = 0, e0 = node.nodeValue.length;
      if (node === range.startContainer) s0 = range.startOffset;
      if (node === range.endContainer) e0 = range.endOffset;
      if (e0 <= s0) continue;
      var target = node;
      if (s0 > 0) target = target.splitText(s0);
      if (e0 - s0 < target.nodeValue.length) target.splitText(e0 - s0);
      var wrap = document.createElement("span");
      wrap.className = "pol-line";
      wrap.setAttribute("data-mark", idx);
      target.parentNode.insertBefore(wrap, target);
      wrap.appendChild(target);
    }
  }
  function unpaintAll() {
    var root = artContainer(); if (!root) return;
    var spans = root.querySelectorAll(".pol-line");
    for (var i = 0; i < spans.length; i++) {
      var sp = spans[i], parent = sp.parentNode;
      while (sp.firstChild) parent.insertBefore(sp.firstChild, sp);
      parent.removeChild(sp);
      parent.normalize();
    }
  }
  var markOrphans = {};   // idx → true（本次载入没定位到）
  function renderMarks() {
    var root = artContainer(); if (!root || !isArticlePage()) return;
    unpaintAll();
    markOrphans = {};
    var arr = Marks.forPath(location.pathname);
    for (var i = 0; i < arr.length; i++) {
      var r = findMarkRange(root, arr[i]);
      if (r) paintRange(r, i); else markOrphans[i] = true;
    }
  }
  function scrollToMark(idx) {
    var el = document.querySelector('.pol-line[data-mark="' + idx + '"]');
    if (!el) return;
    el.scrollIntoView({ block: "center", behavior: "smooth" });
    var all = document.querySelectorAll('.pol-line[data-mark="' + idx + '"]');
    for (var i = 0; i < all.length; i++) all[i].classList.add("pol-line--flash");
    setTimeout(function () {
      for (var i = 0; i < all.length; i++) all[i].classList.remove("pol-line--flash");
    }, 1800);
  }

  /* —— 选中文字后浮出的「划线」小按钮（仅文章页 + 解锁后）—— */
  var bubbleEl = null;
  function buildBubble() {
    bubbleEl = document.createElement("button");
    bubbleEl.type = "button";
    bubbleEl.className = "pol-mark-bubble";
    bubbleEl.textContent = "✏️ 划线";
    document.body.appendChild(bubbleEl);
    bubbleEl.addEventListener("mousedown", function (e) { e.preventDefault(); });
    bubbleEl.addEventListener("click", function () {
      var sel = window.getSelection();
      if (!sel || sel.isCollapsed) { hideBubble(); return; }
      var range = sel.getRangeAt(0);
      var text = range.toString().replace(/\s+/g, " ").trim();
      var block = blockOf(range.startContainer);
      if (!text || !block) { hideBubble(); return; }
      var preRange = document.createRange();
      preRange.selectNodeContents(block); preRange.setEnd(range.startContainer, range.startOffset);
      var postRange = document.createRange();
      postRange.selectNodeContents(block); postRange.setStart(range.endContainer, range.endOffset);
      var mark = { t: range.toString(), p: preRange.toString().slice(-20), s: postRange.toString().slice(0, 20), ts: Date.now() };
      var arr = Marks.forPath(location.pathname);
      arr.push(mark);
      Marks.save(location.pathname, arr);
      sel.removeAllRanges();
      hideBubble();
      renderMarks();
    });
  }
  function hideBubble() { if (bubbleEl) bubbleEl.style.display = "none"; }
  function maybeShowBubble() {
    if (!unlocked || !isArticlePage()) return;
    var sel = window.getSelection();
    if (!sel || sel.isCollapsed || !sel.rangeCount) { hideBubble(); return; }
    var range = sel.getRangeAt(0);
    var root = artContainer();
    if (!root || !root.contains(range.commonAncestorContainer)) { hideBubble(); return; }
    var text = range.toString().trim();
    if (text.length < 2 || text.length > 300) { hideBubble(); return; }
    var b1 = blockOf(range.startContainer), b2 = blockOf(range.endContainer);
    if (!b1 || b1 !== b2) { hideBubble(); return; }   // v1：一次划线不跨段
    if (!bubbleEl) buildBubble();
    var rect = range.getBoundingClientRect();
    bubbleEl.style.display = "block";
    var x = Math.min(Math.max(rect.left + rect.width / 2 - 34, 8), window.innerWidth - 84);
    var y = rect.top - 40; if (y < 8) y = rect.bottom + 10;
    bubbleEl.style.left = x + "px";
    bubbleEl.style.top = y + "px";
  }
  function attachMarking() {
    document.addEventListener("mouseup", function () { setTimeout(maybeShowBubble, 10); });
    document.addEventListener("touchend", function () { setTimeout(maybeShowBubble, 150); });
    document.addEventListener("selectionchange", function () {
      var sel = window.getSelection();
      if (!sel || sel.isCollapsed) hideBubble();
    });
    // 点已有的划线 → 翻开背面
    document.addEventListener("click", function (e) {
      var t = e.target;
      if (t && t.classList && t.classList.contains("pol-line") && unlocked) {
        e.preventDefault();
        openEditor(location.pathname, document.querySelector(".c-chapter-return") ? "ticket" : "photo");
      }
    });
  }

  /* —— 背面的划线引文列表 —— */
  var marksBox = null;
  function renderEditorMarks(id) {
    if (!backdrop) return;
    if (!marksBox) {
      marksBox = document.createElement("div");
      marksBox.className = "pol-ed-marks";
      backdrop.querySelector(".pol-editor").appendChild(marksBox);
    }
    var arr = Marks.forPath(id);
    if (!arr.length) { marksBox.style.display = "none"; return; }
    marksBox.style.display = "";
    var onPage = isArticlePage() && location.pathname === id;
    var html = '<div class="pol-ed-marks-title">✏️ 划线 · ' + arr.length + ' 条</div>';
    for (var i = 0; i < arr.length; i++) {
      var q = arr[i].t.length > 64 ? arr[i].t.slice(0, 64) + "…" : arr[i].t;
      var orphan = onPage && markOrphans[i];
      html += '<div class="pol-ed-mark' + (orphan ? ' is-orphan' : '') + '" data-i="' + i + '">' +
        '<span class="pol-ed-mark-q">' + q.replace(/</g, "&lt;") + '</span>' +
        '<span class="pol-ed-mark-acts">' +
          (orphan ? '<i class="pol-ed-mark-note">原文已改动</i>' : '<button type="button" data-act="go">跳转</button>') +
          (unlocked ? '<button type="button" data-act="del">删除</button>' : '') +
        '</span></div>';
    }
    marksBox.innerHTML = html;
    marksBox.onclick = function (e) {
      var btn = e.target.closest ? e.target.closest("button") : null;
      if (!btn) return;
      var row = btn.parentNode.parentNode, i = +row.getAttribute("data-i");
      if (btn.getAttribute("data-act") === "go") {
        if (onPage) { closeEditor(); setTimeout(function () { scrollToMark(i); }, 150); }
        else { location.href = id + "#pol-mark-" + i; }
      } else if (btn.getAttribute("data-act") === "del") {
        var arr2 = Marks.forPath(id);
        arr2.splice(i, 1);
        Marks.save(id, arr2);
        if (onPage) renderMarks();
        renderEditorMarks(id);
      }
    };
  }

  /* ========== 文章页（原来右下角那支浮笔并进了左下角的小钮）========== */
  function isArticlePage() {
    return !!document.querySelector(".c-article__header .c-article__title") &&
      /\/\d{4}\/\d{2}\/\d{2}\//.test(location.pathname);
  }
  function isTicketPage() { return !!document.querySelector(".c-chapter-return"); }
  function syncPenVisible() {}

  /* ========== 书桌上那本「冬的背面」（/notes/backs/）：三本日记 + 总账 + 底片匣 ========== */
  var deskEl = null;
  function buildDesk() {
    deskEl = document.getElementById("pol-desk");
    if (!deskEl) return;
    loadFonts();
    var tabs = deskEl.querySelectorAll(".pol-desk-tab"), panes = deskEl.querySelectorAll(".pol-desk-pane");
    function pick(name) {
      for (var i = 0; i < tabs.length; i++) tabs[i].setAttribute("aria-selected", tabs[i].getAttribute("data-tab") === name ? "true" : "false");
      for (var j = 0; j < panes.length; j++) panes[j].hidden = panes[j].getAttribute("data-pane") !== name;
      try { localStorage.setItem("wiw-pol-desk-tab", name); } catch (e) {}
    }
    for (var i = 0; i < tabs.length; i++) (function (t) { t.addEventListener("click", function () { pick(t.getAttribute("data-tab")); }); })(tabs[i]);
    var saved = null; try { saved = localStorage.getItem("wiw-pol-desk-tab"); } catch (e) {}
    pick(saved && deskEl.querySelector('.pol-desk-tab[data-tab="' + saved + '"]') ? saved : "ledger");
    renderDesk();
  }
  function renderDesk() {
    if (!deskEl) return;
    deskEl.classList.toggle("is-locked", !unlocked);
    var lockBox = deskEl.querySelector(".pol-desk-lock");
    if (lockBox) {
      if (unlocked) { lockBox.hidden = true; }
      else {
        lockBox.hidden = false;
        lockBox.innerHTML = '<p>这本本子只认你的笔迹。先验一下，再翻。</p><div class="pol-pop-pw"><input class="pol-pw" type="password" placeholder="' + (hasPass() ? "prove you&#39;re Leo — or Winter…" : "sign it — Leo &amp; Winter…") + '"><button class="pol-go" type="button">' + (hasPass() ? "验明" : "印记") + '</button></div>';
        wirePw(lockBox.querySelector(".pol-pw"), lockBox.querySelector(".pol-go"));
      }
    }
    renderDeskLedger();
    renderDeskJournals();
    var boxWrap = deskEl.querySelector(".pol-desk-box");
    if (boxWrap && !boxEl) buildBox(boxWrap);
    if (boxEl) refreshBox();
  }
  function renderDeskLedger() {
    if (!deskEl) return;
    var el = deskEl.querySelector(".pol-desk-ledger"), c = deskEl.querySelector(".pol-desk-count");
    if (!el) return;
    if (!unlocked) { el.innerHTML = ""; if (c) c.textContent = ""; return; }
    renderLedger(el, c, {});
  }
  function fmtDay(key) { var p = key.split("-"); return (+p[1]) + " 月 " + (+p[2]) + " 日"; }
  function renderDeskJournals() {
    if (!deskEl) return;
    var hosts = deskEl.querySelectorAll(".pol-desk-journal");
    for (var i = 0; i < hosts.length; i++) {
      (function (host) {
        var j = journalById(host.getAttribute("data-journal")); if (!j) return;
        var all = storeOf(j).all(), days = [];
        if (j.kind === "letter") {
          var r = all || {};
          days = (r.body || r.subject) ? ["draft"] : [];
        } else {
          for (var d in all) if (all.hasOwnProperty(d)) days.push(d);
          days.sort().reverse();
        }
        var html = '<button class="pol-jcard" type="button"><span class="pol-card-photo" style="background:' + j.grad + '">' + (SCENES[j.id] || "") + '</span>' +
          '<span class="pol-card-cap"><span class="pol-card-q1">' + esc(j.q1) + '</span><span class="pol-card-q2">' + esc(j.q2) + '</span><span class="pol-card-credit">' + esc(j.credit) + '</span><i>' + (j.kind === "letter" ? "写一封" : "今天 · " + pinDate()) + '</i></span></button>';
        html += '<div class="pol-jlist">';
        if (!unlocked) html += '<p class="pol-ledger-empty">验过笔迹才看得到。</p>';
        else if (!days.length) html += '<p class="pol-ledger-empty">' + esc(j.hint || "") + '</p>';
        else for (var k = 0; k < Math.min(days.length, 60); k++) {
          var key = days[k], rec = j.kind === "letter" ? all : all[key], text;
          if (j.kind === "three") text = (rec.items || []).filter(Boolean).join(" · ");
          else if (j.kind === "letter") text = (rec.subject ? rec.subject + " · " : "") + (rec.body || "").slice(0, 60);
          else text = (rec.text || "").replace(/\s+/g, " ");
          html += '<button class="pol-jrow" type="button" data-day="' + esc(key) + '"><b>' + (j.kind === "letter" ? "草稿" : fmtDay(key)) + '</b><span>' + esc(text.slice(0, 72)) + (text.length > 72 ? "…" : "") + '</span></button>';
        }
        html += '</div>';
        host.innerHTML = html;
        host.querySelector(".pol-jcard").addEventListener("click", function () { if (!unlocked) return; openJournal(j, todayKey()); });
        var rows = host.querySelectorAll(".pol-jrow");
        for (var m = 0; m < rows.length; m++) (function (b) { b.addEventListener("click", function () { openJournal(j, b.getAttribute("data-day") === "draft" ? todayKey() : b.getAttribute("data-day")); }); })(rows[m]);
      })(hosts[i]);
    }
  }
  /* 书桌页的本子封面：报一下这台手机上有几张背面 */
  function fillDeskCover() {
    var el = document.getElementById("js-backs-meta");
    if (!el) return;
    var n = noteCount(), mk = 0, marks = Marks.all();
    for (var k in marks) if (marks.hasOwnProperty(k)) mk += marks[k].length;
    el.innerHTML = (n || mk) ? ('<b>' + n + '</b> 张背面' + (mk ? ' · <b>' + mk + '</b> 处划线' : '') + ' · 只在这台设备上') : '🔒 只在你这台设备上';
  }

  /* ========== 启动 ========== */
  function init() {
    buildLock(); markDogears(); attachCards(); syncDeckVisible();
    lockAutoHide();
    buildDesk(); fillDeskCover();
    if (isArticlePage()) {
      renderMarks(); attachMarking();
      var hm = location.hash.match(/^#pol-mark-(\d+)$/);
      if (hm) setTimeout(function () { scrollToMark(+hm[1]); }, 400);
    }
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
