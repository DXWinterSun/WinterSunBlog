/* =========================================================
   宝丽来背面批注 · Polaroid back-of-photo private notes
   右键(电脑)/长按(手机)照片 → 翻开写字 → 自动保存(本机)
   解锁一次后长期保持；日后升级云端只需替换 Store 这一层。
   ========================================================= */
(function () {
  "use strict";

  /* ========== 你的配置 ========== */
  // ↓↓↓ 用文末小工具把你的密码转成哈希，替换下面这行的占位符：
  var PASS_HASH = "PUT_YOUR_HASH_HERE";
  var NOTE_FONT = "'Caveat','Ma Shan Zheng',cursive";
  var FONT_LINK = "https://fonts.googleapis.com/css2?family=Caveat:wght@500;600&family=Ma+Shan+Zheng&display=swap";
  var LONGPRESS_MS = 480;

  /* ========== 存储键 ========== */
  var LS_NOTES = "wiw-pol-notes";
  var LS_UNLOCK = "wiw-pol-unlock";
  var LS_PASS_DEV = "wiw-pol-pass-dev"; // 仅在尚未填 PASS_HASH 时作兜底

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
      '<div class="pol-editor" role="dialog" aria-label="背面批注">' +
        '<div class="pol-ed-head"><span class="pol-ed-title">背面 · 批注</span>' +
        '<button class="pol-ed-x" type="button" title="翻回" aria-label="翻回">↩</button></div>' +
        '<textarea class="pol-note" spellcheck="false"></textarea>' +
        '<div class="pol-ed-foot"><span class="pol-ts"></span><span class="pol-saved">已保存 ✓</span></div>' +
      '</div>';
    document.body.appendChild(backdrop);
    note = backdrop.querySelector(".pol-note");
    tsEl = backdrop.querySelector(".pol-ts");
    savedEl = backdrop.querySelector(".pol-saved");
    note.style.fontFamily = NOTE_FONT;
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
    note.placeholder = unlocked ? "在这里写点什么…" : "🔒 解锁后可编辑";
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
    if (unlocked) {
      lockEl.innerHTML = '<span class="pol-lock-state">🔓 已解锁</span><button class="pol-lk-btn" type="button" data-act="lock">锁定</button>';
    } else {
      lockEl.innerHTML = '<button class="pol-lk-btn pol-lk-open" type="button">🔒 ' + (hasPass() ? "解锁" : "设密码") + "</button>";
    }
    var openBtn = lockEl.querySelector(".pol-lk-open");
    if (openBtn) openBtn.addEventListener("click", showPwInput);
    var lockBtn = lockEl.querySelector('[data-act="lock"]');
    if (lockBtn) lockBtn.addEventListener("click", function () { localStorage.removeItem(LS_UNLOCK); unlocked = false; renderLock(); });
  }
  function showPwInput() {
    var setting = !hasPass();
    lockEl.innerHTML = '<input class="pol-pw" type="password" placeholder="' + (setting ? "设一个密码" : "输入密码") + '"><button class="pol-go" type="button">' + (setting ? "设定" : "解锁") + "</button>";
    var pw = lockEl.querySelector(".pol-pw"); pw.focus();
    function submit() {
      var v = pw.value.trim(); if (!v) return;
      if (setting) {
        localStorage.setItem(LS_PASS_DEV, hash(v));
        localStorage.setItem(LS_UNLOCK, "1"); unlocked = true; renderLock();
      } else {
        if (hash(v) === passHash()) { localStorage.setItem(LS_UNLOCK, "1"); unlocked = true; renderLock(); }
        else { pw.value = ""; pw.placeholder = "密码不对"; }
      }
    }
    lockEl.querySelector(".pol-go").addEventListener("click", submit);
    pw.addEventListener("keydown", function (e) { if (e.key === "Enter") submit(); });
  }

  /* ========== 启动 ========== */
  function init() { buildLock(); markDogears(); attachCards(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
