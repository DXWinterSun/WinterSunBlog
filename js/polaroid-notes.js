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
      lockEl.innerHTML = '<span class="pol-lock-state">🔓 已解锁</span><button class="pol-lk-btn" type="button" data-act="box">📦 收纳盒</button><button class="pol-lk-btn" type="button" data-act="lock">锁定</button>';
    } else {
      lockEl.innerHTML = '<button class="pol-lk-btn pol-lk-open" type="button">🔒 ' + (hasPass() ? "解锁" : "设密码") + "</button>";
    }
    var openBtn = lockEl.querySelector(".pol-lk-open");
    if (openBtn) openBtn.addEventListener("click", showPwInput);
    var lockBtn = lockEl.querySelector('[data-act="lock"]');
    if (lockBtn) lockBtn.addEventListener("click", function () { localStorage.removeItem(LS_UNLOCK); unlocked = false; if (boxEl) boxEl.classList.remove("open"); renderLock(); });
    var boxBtn = lockEl.querySelector('[data-act="box"]');
    if (boxBtn) boxBtn.addEventListener("click", toggleBox);
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

  /* ========== 收纳盒：导出 / 导入（设备间搬家）========== */
  function pad(n) { return n < 10 ? "0" + n : "" + n; }
  function noteCount() {
    var a = Store.all(), c = 0;
    for (var k in a) if (a.hasOwnProperty(k) && a[k].text && a[k].text.trim()) c++;
    return c;
  }
  function exportNotes() {
    var data = { app: "wiw-polaroid-notes", v: 1, exported: Date.now(), notes: Store.all() };
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
      '<div class="pol-box-head"><span>📦 收纳盒</span><button class="pol-box-x" type="button" aria-label="关闭">×</button></div>' +
      '<p class="pol-box-count"></p>' +
      '<button class="pol-box-btn" type="button" data-act="export"><b>导出备份</b><small>打包下载成一个文件，带去手机 / 新设备</small></button>' +
      '<button class="pol-box-btn" type="button" data-act="import"><b>导入备份</b><small>选一个之前导出的文件，恢复批注</small></button>' +
      '<input class="pol-box-file" type="file" accept="application/json,.json" hidden>' +
      '<p class="pol-box-msg"></p>';
    document.body.appendChild(boxEl);
    boxCount = boxEl.querySelector(".pol-box-count");
    boxMsg = boxEl.querySelector(".pol-box-msg");
    boxFile = boxEl.querySelector(".pol-box-file");
    boxEl.querySelector(".pol-box-x").addEventListener("click", function () { boxEl.classList.remove("open"); });
    boxEl.querySelector('[data-act="export"]').addEventListener("click", function () {
      if (noteCount() === 0) { setMsg("这台设备上还没有批注，没什么可导出的。"); return; }
      exportNotes(); setMsg("已导出 ✓ 文件已下载；到新设备点「导入备份」选它即可。");
    });
    boxEl.querySelector('[data-act="import"]').addEventListener("click", function () { boxFile.click(); });
    boxFile.addEventListener("change", function () {
      var f = boxFile.files && boxFile.files[0]; if (!f) return;
      importNotes(f, function (err, r) {
        boxFile.value = "";
        if (err) { setMsg("导入失败：" + (err.message || "文件读不出来")); return; }
        markDogears(); refreshBox();
        setMsg("导入完成 ✓ 新增 " + r.added + " 张，更新 " + r.updated + " 张。");
      });
    });
  }
  function setMsg(t) { if (boxMsg) { boxMsg.textContent = t; boxMsg.classList.add("show"); } }
  function refreshBox() { if (boxCount) boxCount.textContent = "这台设备上有 " + noteCount() + " 张批注相片"; }
  function toggleBox() {
    if (!boxEl) buildBox();
    var open = boxEl.classList.toggle("open");
    if (open) { refreshBox(); if (boxMsg) boxMsg.classList.remove("show"); }
  }

  /* ========== 启动 ========== */
  function init() { buildLock(); markDogears(); attachCards(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
