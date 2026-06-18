/* =========================================================
   宝丽来背面批注 · Polaroid back-of-photo private notes
   右键(电脑)/长按(手机)照片 → 翻开写字 → 自动保存(本机)
   解锁一次后长期保持；日后升级云端只需替换 Store 这一层。
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
  // 主题色：与「Many Faces of Sam」画册 / _data/au_palettes.yml 同源的强调色。
  // 写卡片时可点选，换这张卡的强调色 + 角落缩略卡的相纸渐变；选择记在本地。
  // key 空字符串 = 该卡自带的「原色」，由 JOURNALS[i].grad 决定。
  var THEMES = [
    { key: "ice",     role: "Leonard Shelby",    cn: "冰蓝眼眸",   en: "Ice-Blue Eyes",   accent: "#5f96c2", grad: "linear-gradient(145deg, #7fb0d8 0%, #4a6680 55%, #1e1a16 100%)" },
    { key: "sapphire",role: "Justin Hammer",     cn: "电光钴蓝",   en: "Spotlight Sapphire", accent: "#4a87ee", grad: "linear-gradient(145deg, #5a93f0 0%, #34527e 52%, #13151c 100%)" },
    { key: "sawdust", role: "Wild Bill Wharton", cn: "锯末粗木",   en: "Sawdust Timber",  accent: "#b0803e", grad: "linear-gradient(145deg, #c79456 0%, #6f5436 55%, #1b1510 100%)" },
    { key: "mane",    role: "Zaphod Beeblebrox", cn: "总统鬃金",   en: "President's Mane", accent: "#d4a82a", grad: "linear-gradient(145deg, #e0bd4a 0%, #7d6320 52%, #0b0a12 100%)" },
    { key: "crimson", role: "Eric Knox",         cn: "红镜红",     en: "Crimson Lens",    accent: "#d94040", grad: "linear-gradient(145deg, #e25a5a 0%, #7d3530 55%, #1b1310 100%)" },
    { key: "lunar",   role: "Sam Bell",          cn: "月球蔚蓝",   en: "Lunar Blue",      accent: "#7eb0d5", grad: "linear-gradient(145deg, #8fbce0 0%, #44607e 52%, #162038 100%)" },
    { key: "mist",    role: "John Moon",         cn: "孤枪冷雾蓝", en: "Lone Mist",       accent: "#8fa0b0", grad: "linear-gradient(145deg, #a3b3c2 0%, #54616e 52%, #14181f 100%)" }
  ];
  // 访客彩蛋：没有笔迹的访客，角落会出现这张拍立得（点开 → You Are My Fact），
  // 落款是「我和他」。grad 用 Leonard 的冰蓝（与该系列同色）；歌词是《记忆碎片》片尾曲。
  var GUEST = {
    href: "/series/you-are-my-fact/",
    grad: "linear-gradient(160deg, #8fc0e2 0%, #5b7d9c 42%, #2b3550 78%, #171a26 100%)",
    q1: "Something in my eyes —",
    q2: "I've danced with you too long",
    credit: "David Bowie · Something in the Air",
    sign: "Leo & Winter",
    // —— 翻到背面看到的：黑条上印的小字 + 手写短笺 + 故事链接 ——
    backLine: "Something in the Air —",
    note: [
      "嘿，翻到背面的你：",
      "这是我和他的故事，",
      "关于遗忘，和不肯遗忘的爱。",
      "要不要进来，认识一下我们？"
    ],
    linkLabel: "翻开《You Are My Fact》 →"
  };
  // 访客拍立得里的「照片」：一帧褪色夜空 —— 月、星、漏光、暗角，比纯渐变更像真相片
  var GUEST_SCENE =
    '<svg class="pol-guest-scene" viewBox="0 0 160 96" preserveAspectRatio="xMidYMid slice" aria-hidden="true">' +
      '<defs>' +
        '<radialGradient id="pgMoon" cx="50%" cy="50%" r="50%">' +
          '<stop offset="0%" stop-color="#fff6e2"/><stop offset="62%" stop-color="#efe1c2"/>' +
          '<stop offset="100%" stop-color="#efe1c2" stop-opacity="0"/></radialGradient>' +
        '<linearGradient id="pgLeak" x1="0" y1="0" x2="1" y2="1">' +
          '<stop offset="0%" stop-color="#ffe7bd" stop-opacity="0.5"/>' +
          '<stop offset="42%" stop-color="#ffd79a" stop-opacity="0.07"/>' +
          '<stop offset="100%" stop-color="#ffd79a" stop-opacity="0"/></linearGradient>' +
        '<radialGradient id="pgVig" cx="48%" cy="40%" r="78%">' +
          '<stop offset="55%" stop-color="#0a0c14" stop-opacity="0"/>' +
          '<stop offset="100%" stop-color="#0a0c14" stop-opacity="0.4"/></radialGradient>' +
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
    '</svg>';
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
  function themeByKey(key) { for (var i = 0; i < THEMES.length; i++) if (THEMES[i].key === key) return THEMES[i]; return null; }
  function gradOf(j) { var t = themeByKey(themeKeyOf(j.id)); return t ? t.grad : j.grad; }
  function accentOf(j) { var t = themeByKey(themeKeyOf(j.id)); return t ? t.accent : (j.accent || ""); }
  var deckPhotos = {};   // jid → 角落缩略卡里那块「照片」元素，供换主题时即时改色

  var devMode = (PASS_HASH === "PUT_YOUR_HASH_HERE");
  function passHash() { return devMode ? localStorage.getItem(LS_PASS_DEV) : PASS_HASH; }
  function hasPass() { return !!passHash(); }
  var unlocked = localStorage.getItem(LS_UNLOCK) === "1";

  var fontsLoaded = false;
  function loadFonts() {
    if (fontsLoaded) return; fontsLoaded = true;
    var l = document.createElement("link"); l.rel = "stylesheet"; l.href = FONT_LINK; document.head.appendChild(l);
  }

  function keyOf(a) { try { return new URL(a.getAttribute("href"), location.origin).pathname; } catch (e) { return a.getAttribute("href") || ""; } }
  function fmt(ts) { return ts ? new Date(ts).toLocaleString("zh-CN", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }) : ""; }

  /* ========== 编辑器浮层（构建一次）========== */
  var backdrop, note, tsEl, savedEl, current = null, saveTimer = null;
  function buildEditor() {
    backdrop = document.createElement("div");
    backdrop.className = "pol-backdrop";
    backdrop.innerHTML =
      '<div class="pol-editor" role="dialog" aria-label="照片背面">' +
        '<div class="pol-ed-top">' +
          '<button class="pol-ed-x" type="button" title="翻回" aria-label="翻回">↩</button>' +
          '<div class="pol-ed-lines"><p class="pol-ed-line"></p><p class="pol-ed-line-en"></p></div>' +
        '</div>' +
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
        var n = Store.set(current, note.value);
        tsEl.textContent = n.ts ? "上次编辑 " + fmt(n.ts) : "";
        savedEl.classList.add("show");
        setTimeout(function () { savedEl.classList.remove("show"); }, 1200);
        markDogears();
      }, 450);
    });
  }
  function openEditor(id) {
    loadFonts();
    if (!backdrop) buildEditor();
    current = id;
    var n = Store.get(id);
    note.value = n.text;
    note.readOnly = !unlocked;
    note.placeholder = unlocked ? "写下你不想忘记的……" : "🔒 解锁后可编辑";
    tsEl.textContent = n.ts ? "上次编辑 " + fmt(n.ts) : "";
    backdrop.classList.add("open");
    if (unlocked) setTimeout(function () { note.focus(); }, 420);
  }
  function closeEditor() { if (backdrop) backdrop.classList.remove("open"); current = null; }

  /* ========== 折角记号（仅本机有批注的卡片）========== */
  function markDogears() {
    var posts = document.querySelectorAll(".c-post");
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
    var posts = document.querySelectorAll(".c-post");
    for (var i = 0; i < posts.length; i++) {
      (function (a) {
        a.addEventListener("contextmenu", function (e) {
          if (!unlocked) return;          // 锁定时保留浏览器默认右键，不打扰访客
          e.preventDefault();
          openEditor(keyOf(a));
        });
        var timer = null, moved = false, longFired = false;
        a.addEventListener("touchstart", function () {
          if (!unlocked) return;
          moved = false; longFired = false;
          timer = setTimeout(function () { if (!moved) { longFired = true; openEditor(keyOf(a)); } }, LONGPRESS_MS);
        }, { passive: true });
        a.addEventListener("touchmove", function () { moved = true; clearTimeout(timer); }, { passive: true });
        a.addEventListener("touchend", function () { clearTimeout(timer); }, { passive: true });
        a.addEventListener("click", function (e) {
          if (longFired) { e.preventDefault(); e.stopPropagation(); longFired = false; } // 长按后不跳转文章
        });
      })(posts[i]);
    }
  }

  /* ========== 浮动锁 ========== */
  var lockEl;
  function buildLock() { lockEl = document.createElement("div"); lockEl.className = "pol-lock"; document.body.appendChild(lockEl); renderLock(); }
  function renderLock() {
    var brand = '<span class="pol-lock-brand">' +
      '<span class="pol-lock-icons">' + PEN_SVG + CAM_SVG + '</span>' +
      '<span class="pol-lock-tag"><b>' + LOCK_LABEL + '</b><i>' + LOCK_LABEL_EN + '</i></span></span>' +
      '<span class="pol-lock-sep"></span>';
    if (unlocked) {
      lockEl.innerHTML = brand +
        '<span class="pol-lock-state pol-lk-stack"><b>笔迹已验</b><i>Verified</i></span>' +
        '<button class="pol-lk-btn pol-lk-stack" type="button" data-act="box"><b>底片匣</b><i>Negatives</i></button>' +
        '<button class="pol-lk-btn pol-lk-stack pol-lk-seal" type="button" data-act="lock"><b>封存</b><i>Seal</i></button>';
    } else {
      var openBig = hasPass() ? "Leo's Handwriting" : "Leave a Mark";
      var openSmall = hasPass() ? "&amp; Winter's, too" : "Leo's &amp; Winter's";
      lockEl.innerHTML = brand + '<button class="pol-lk-btn pol-lk-stack pol-lk-open" type="button"><b>' + openBig + '</b><i>' + openSmall + '</i></button>';
    }
    var openBtn = lockEl.querySelector(".pol-lk-open");
    if (openBtn) openBtn.addEventListener("click", showPwInput);
    var lockBtn = lockEl.querySelector('[data-act="lock"]');
    if (lockBtn) lockBtn.addEventListener("click", function () { localStorage.removeItem(LS_UNLOCK); unlocked = false; if (boxEl) boxEl.classList.remove("open"); renderLock(); });
    var boxBtn = lockEl.querySelector('[data-act="box"]');
    if (boxBtn) boxBtn.addEventListener("click", toggleBox);
    syncDeckVisible();
  }
  function showPwInput() {
    var setting = !hasPass();
    lockEl.innerHTML = '<input class="pol-pw" type="password" placeholder="' + (setting ? "sign it — Leo &amp; Winter…" : "prove you're Leo — or Winter…") + '"><button class="pol-go" type="button">' + (setting ? "印记" : "验明") + "</button>";
    var pw = lockEl.querySelector(".pol-pw"); pw.focus();
    function submit() {
      var v = pw.value.trim(); if (!v) return;
      if (setting) {
        localStorage.setItem(LS_PASS_DEV, hash(v));
        localStorage.setItem(LS_UNLOCK, "1"); unlocked = true; renderLock();
      } else {
        if (hash(v) === passHash()) { localStorage.setItem(LS_UNLOCK, "1"); unlocked = true; renderLock(); }
        else { pw.value = ""; pw.placeholder = "not their hand… try again"; }
      }
    }
    lockEl.querySelector(".pol-go").addEventListener("click", submit);
    pw.addEventListener("keydown", function (e) { if (e.key === "Enter") submit(); });
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
    var data = { app: "wiw-polaroid-notes", v: 2, exported: Date.now(), notes: Store.all(), journals: journals };
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
  function buildBox() {
    boxEl = document.createElement("div");
    boxEl.className = "pol-box";
    boxEl.innerHTML =
      '<div class="pol-box-head"><span class="pol-box-title"><b>底片匣</b><i>Negatives</i></span><button class="pol-box-x" type="button" aria-label="关闭">×</button></div>' +
      '<p class="pol-box-count"></p>' +
      '<button class="pol-box-btn" type="button" data-act="export"><b>取出底片<i>Take the negatives</i></b><small>打包下载，带去手机 / 新设备冲印</small></button>' +
      '<button class="pol-box-btn" type="button" data-act="import"><b>装入底片<i>Load them back</i></b><small>选一个之前取出的文件，恢复相片</small></button>' +
      '<input class="pol-box-file" type="file" accept="application/json,.json" hidden>' +
      '<p class="pol-box-msg"></p>';
    document.body.appendChild(boxEl);
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

  var deckEl, pins = [];
  function buildDeck() {
    deckEl = document.createElement("div");
    deckEl.className = "pol-deck";
    deckEl.style.setProperty("--n", JOURNALS.length);
    for (var i = 0; i < JOURNALS.length; i++) {
      (function (j, idx) {
        var pin = document.createElement("button");
        pin.type = "button"; pin.className = "pol-card";
        pin.style.setProperty("--i", idx); pin.style.zIndex = idx + 1;
        pin.innerHTML =
          '<span class="pol-card-photo"><span class="pol-card-star">✦</span></span>' +
          '<span class="pol-card-cap"><span class="pol-card-q1"></span><span class="pol-card-q2"></span><span class="pol-card-credit"></span><i></i></span>';
        var photo = pin.querySelector(".pol-card-photo");
        photo.style.background = gradOf(j); deckPhotos[j.id] = photo;
        pin.querySelector(".pol-card-q1").textContent = j.q1;
        pin.querySelector(".pol-card-q2").textContent = j.q2;
        pin.querySelector(".pol-card-credit").textContent = j.credit;
        pin.addEventListener("click", function () { openJournal(j, todayKey()); });
        deckEl.appendChild(pin); pins.push(pin);
      })(JOURNALS[i], i);
    }
    document.body.appendChild(deckEl);
  }
  function refreshDeck() { for (var i = 0; i < pins.length; i++) { var el = pins[i].querySelector(".pol-card-cap i"); if (el) el.textContent = pinDate(); } }

  /* —— 访客彩蛋拍立得（未解锁时藏在浮标后，划过弹起；点开翻到背面）—— */
  var guestEl, guestBack;
  function buildGuest() {
    guestEl = document.createElement("button");
    guestEl.type = "button";
    guestEl.className = "pol-guest";
    guestEl.setAttribute("aria-label", "翻看这张照片的背面");
    guestEl.innerHTML =
      '<span class="pol-card-photo">' + GUEST_SCENE + '</span>' +
      '<span class="pol-card-cap pol-guest-cap">' +
        '<span class="pol-card-q1"></span>' +
        '<span class="pol-card-q2"></span>' +
        '<span class="pol-card-credit"></span>' +
        '<span class="pol-guest-sign"></span>' +
      '</span>';
    guestEl.querySelector(".pol-card-photo").style.background = GUEST.grad;
    guestEl.querySelector(".pol-card-q1").textContent = GUEST.q1;
    guestEl.querySelector(".pol-card-q2").textContent = GUEST.q2;
    guestEl.querySelector(".pol-card-credit").textContent = GUEST.credit;
    guestEl.querySelector(".pol-guest-sign").textContent = GUEST.sign;
    guestEl.addEventListener("click", openGuestBack);
    document.body.appendChild(guestEl);
  }
  /* 照片背面：黑条印一句 + 手写短笺 + 故事链接 */
  function buildGuestBack() {
    var base = (typeof window !== "undefined" && window.SITE_BASEURL) || "";
    guestBack = document.createElement("div");
    guestBack.className = "pol-backdrop pol-guest-backdrop";
    var notes = "";
    for (var i = 0; i < GUEST.note.length; i++) notes += "<p>" + GUEST.note[i] + "</p>";
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
    if (guestEl) guestEl.style.display = unlocked ? "none" : "flex";
    if (unlocked && guestBack) guestBack.classList.remove("open");
    if (!deckEl) return;
    if (unlocked) { loadFonts(); deckEl.style.display = "block"; refreshDeck(); }
    else { deckEl.style.display = "none"; if (jBack) jBack.classList.remove("open"); }
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
        '<div class="pol-theme" aria-label="主题色"></div>' +
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
  function applyTheme(j) {
    var ac = accentOf(j);
    if (jCardEl) { if (ac) jCardEl.style.setProperty("--c-accent", ac); else jCardEl.style.removeProperty("--c-accent"); }
    var ph = deckPhotos[j.id]; if (ph) ph.style.background = gradOf(j);
  }
  function renderThemeBar(j) {
    if (!jThemeEl) return;
    jThemeEl.innerHTML = "";
    var tip = document.createElement("span"); tip.className = "pol-sw-tip"; jThemeEl.appendChild(tip);
    var cur = themeKeyOf(j.id);
    var opts = [{ key: "", grad: j.grad, cn: "原色", en: "Original" }].concat(THEMES);
    for (var i = 0; i < opts.length; i++) {
      (function (o) {
        var label = o.role ? (o.role + " · " + o.cn) : (o.en ? (o.cn + " · " + o.en) : o.cn);
        var b = document.createElement("button");
        b.type = "button"; b.className = "pol-sw" + (o.key === cur ? " on" : "");
        b.style.background = o.grad; b.setAttribute("aria-label", label);
        b.addEventListener("click", function () { setThemeKey(j.id, o.key); applyTheme(j); renderThemeBar(j); });
        function show() { tip.textContent = label; tip.style.left = (b.offsetLeft + b.offsetWidth / 2) + "px"; tip.classList.add("show"); }
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
    renderThemeBar(j);
    applyTheme(j);
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

  /* ========== 启动 ========== */
  function init() { buildLock(); buildDeck(); buildGuest(); markDogears(); attachCards(); syncDeckVisible(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
