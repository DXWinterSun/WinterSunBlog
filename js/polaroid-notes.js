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
  // 拍立得背面黑条上印着的一句话（仪式感所在，想换就改这里）：
  var NOTE_TAGLINE = "趁我还记得，把它写在背面。";
  var NOTE_TAGLINE_EN = "While it's still mine to remember.";
  // 左下角浮标上的导语（钢笔旁的小字）：
  var LOCK_LABEL = "记忆碎片";
  var LOCK_LABEL_EN = "Memento";
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
      lockEl.innerHTML = brand + '<span class="pol-lock-state">笔迹已验</span><button class="pol-lk-btn" type="button" data-act="box">底片匣</button><button class="pol-lk-btn pol-lk-seal" type="button" data-act="lock">封存</button>';
    } else {
      lockEl.innerHTML = brand + '<button class="pol-lk-btn pol-lk-open" type="button">' + (hasPass() ? "Leo 的笔迹" : "留下笔迹") + "</button>";
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
    lockEl.innerHTML = '<input class="pol-pw" type="password" placeholder="' + (setting ? "写下一个密码……" : "写下你的密码……") + '"><button class="pol-go" type="button">' + (setting ? "印记" : "验明") + "</button>";
    var pw = lockEl.querySelector(".pol-pw"); pw.focus();
    function submit() {
      var v = pw.value.trim(); if (!v) return;
      if (setting) {
        localStorage.setItem(LS_PASS_DEV, hash(v));
        localStorage.setItem(LS_UNLOCK, "1"); unlocked = true; renderLock();
      } else {
        if (hash(v) === passHash()) { localStorage.setItem(LS_UNLOCK, "1"); unlocked = true; renderLock(); }
        else { pw.value = ""; pw.placeholder = "笔迹有误，再试……"; }
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
      '<div class="pol-box-head"><span>底片匣</span><button class="pol-box-x" type="button" aria-label="关闭">×</button></div>' +
      '<p class="pol-box-count"></p>' +
      '<button class="pol-box-btn" type="button" data-act="export"><b>取出底片</b><small>打包下载，带去手机 / 新设备冲印</small></button>' +
      '<button class="pol-box-btn" type="button" data-act="import"><b>装入底片</b><small>选一个之前取出的文件，恢复相片</small></button>' +
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

  /* ========== 启动 ========== */
  function init() { buildLock(); markDogears(); attachCards(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
