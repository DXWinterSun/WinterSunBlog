// ============================================================
//  冬的备忘本 · Scriptable 桌面小组件
//  读 GitHub 上 memo 分支的那份 memo.json：网页上改、或在对话里让
//  Claude 改，小组件下次刷新就跟着变（什么时候刷新由 iPhone 决定，
//  一般十几分钟到半小时；点开小组件去备忘本里看，永远是最新的）。
//
//  这个小组件显示哪几页，由小组件的「参数」决定
//  （长按小组件 → 编辑小组件 → Parameter）：
//    （空着）      → 总览：每页一行
//    生活所迫       → 只显示这一页（填页名就行，「生活」「喜欢」「日更」这种简称也认）
//    生活所迫,日更   → 中号、大号里并排显示这两页
//  想「翻页」：几个同样大小的小组件叠成一摞（拖一个到另一个上面松手），
//  每个填一页，往上一滑就是下一页。
//  样式（便笺 / 提醒 / 晴雪）跟 Claude 说一声就换，不用改这里。备忘本网页只看不改。
// ============================================================

const API = "https://api.github.com/repos/DXWinterSun/WinterSunBlog/contents/memo.json?ref=memo";
const EDIT_URL = "https://dxwintersun.github.io/WinterSunBlog/memo/";

// ── 三套样子 ────────────────────────────────────────────────
// 每个颜色都是「白天 / 夜里」一对，手机切深色模式时自动换。
function dyn(light, dark) { return Color.dynamic(new Color(light), new Color(dark)); }

const STYLES = {
  // 便笺：暖米色的纸，顶上一道这一页的颜色（像撕下来的便签本），一行一道横线
  paper: {
    bg: dyn("#FBF7EF", "#2A251F"),
    ink: dyn("#3A2F27", "#F0E7D9"),
    sub: dyn("#A08F7C", "#9F927F"),
    rule: dyn("#ECE3D3", "#3A332C"),
    band: true, rules: true, dot: "page",
    title: (s) => Font.semiboldSystemFont(s),
    count: (s) => new Font("Georgia", s),
    item: (s) => Font.systemFont(s),
    rows: { small: 4, medium: 4, large: 11, cell: 5 },
  },
  // 提醒：跟系统「提醒事项」小组件一个样——白底、彩色标题、灰色空心圈
  native: {
    bg: dyn("#FFFFFF", "#1C1C1E"),
    ink: dyn("#000000", "#FFFFFF"),
    sub: dyn("#8E8E93", "#8E8E93"),
    rule: dyn("#E5E5EA", "#38383A"),
    band: false, rules: false, dot: "ring", titleInColor: true,
    title: (s) => Font.semiboldSystemFont(s + 2),
    count: (s) => Font.boldSystemFont(s + 2),
    item: (s) => Font.systemFont(s + 1.5),
    rows: { small: 3, medium: 3, large: 9, cell: 4 },
  },
  // 晴雪：博客的冬天配色——雪地淡蓝、深海军蓝的字、冰蓝的圈
  snow: {
    bg: dyn("#EAF3FA", "#13202B"),
    ink: dyn("#14212E", "#E9F1F7"),
    sub: dyn("#7C8FA2", "#7D8FA0"),
    rule: dyn("#D3E3EF", "#243443"),
    ice: dyn("#3F9ECB", "#63B6DE"),
    gold: dyn("#D9A441", "#EEC070"),
    band: false, rules: false, dot: "ice", flake: true,
    title: (s) => Font.semiboldSystemFont(s),
    count: (s) => new Font("Georgia", s),
    item: (s) => Font.systemFont(s),
    rows: { small: 4, medium: 4, large: 11, cell: 5 },
  },
};

const RED = dyn("#D9534F", "#FF6B61");

// ── 取数据：先看本机缓存，过了一分钟再去 GitHub 拿 ─────────────
// 叠在一摞里的几个小组件常常同时刷新，一分钟内共用同一份，免得一下请求好几次；
// 没网的时候就显示上一次存下的，右上角挂一个小小的「没连上」。
const fm = FileManager.local();
const DIR = fm.joinPath(fm.documentsDirectory(), "winter-memo");
const CACHE = fm.joinPath(DIR, "memo.json");
const META = fm.joinPath(DIR, "meta.json");

function readJSON(path) {
  try { return fm.fileExists(path) ? JSON.parse(fm.readString(path)) : null; } catch (e) { return null; }
}
function header(res, name) {
  const h = (res && res.headers) || {};
  for (const k in h) if (k.toLowerCase() === name) return h[k];
  return null;
}

async function loadMemo() {
  if (!fm.fileExists(DIR)) fm.createDirectory(DIR, true);
  const meta = readJSON(META) || {};
  const cached = readJSON(CACHE);
  if (cached && meta.at && Date.now() - meta.at < 60 * 1000) return { data: cached, stale: false };
  try {
    const req = new Request(API);
    req.timeoutInterval = 12;
    req.headers = { "Accept": "application/vnd.github.raw", "X-GitHub-Api-Version": "2022-11-28" };
    if (cached && meta.etag) req.headers["If-None-Match"] = meta.etag;
    const text = await req.loadString();
    const code = req.response ? req.response.statusCode : 0;
    if (code === 304 && cached) {
      fm.writeString(META, JSON.stringify({ etag: meta.etag, at: Date.now() }));
      return { data: cached, stale: false };
    }
    if (code >= 200 && code < 300) {
      const data = JSON.parse(text);
      fm.writeString(CACHE, text);
      fm.writeString(META, JSON.stringify({ etag: header(req.response, "etag"), at: Date.now() }));
      return { data: data, stale: false };
    }
    throw new Error("HTTP " + code);
  } catch (e) {
    if (cached) return { data: cached, stale: true };
    return { data: null, stale: true };
  }
}

// ── 整理：哪几页、每页哪些条目 ─────────────────────────────────
const ALIASES = {
  chore: ["生活所迫", "生活", "琐事", "工作", "chore"],
  love: ["喜欢的事", "喜欢", "sam", "山姆", "灵感", "项目", "love"],
  daily: ["日更", "日更素材", "素材", "近期", "daily"],
};

function findPage(pages, word) {
  const w = String(word).trim().toLowerCase();
  if (!w) return null;
  for (const p of pages) {
    if (w === p.id.toLowerCase() || w === p.name.toLowerCase() || w === (p.emoji || "")) return p;
  }
  for (const id in ALIASES) {
    if (ALIASES[id].indexOf(w) >= 0) {
      const p = pages.find((x) => x.id === id);
      if (p) return p;
    }
  }
  return pages.find((p) => p.name.toLowerCase().indexOf(w) >= 0) || null;
}

function chosenPages(data) {
  const pages = (data.settings && data.settings.pages) || [];
  const raw = (typeof args !== "undefined" && args.widgetParameter) || "";
  const picked = [];
  String(raw).split(/[,，、;；\s]+/).forEach((w) => {
    const p = findPage(pages, w);
    if (p && picked.indexOf(p) < 0) picked.push(p);
  });
  return picked.length ? picked : pages.slice();
}

function openItems(data, pageId) {
  return (data.items || [])
    .filter((i) => i.page === pageId && !i.done)
    .sort((a, b) => {
      const pa = a.pin ? 0 : 1, pb = b.pin ? 0 : 1;
      if (pa !== pb) return pa - pb;
      if ((a.order || 0) !== (b.order || 0)) return (a.order || 0) - (b.order || 0);
      return String(a.created || "").localeCompare(String(b.created || ""));
    });
}

// 到期日：今天 / 明天 / 过期用红字，其余写成 10/15
function dueLabel(due) {
  if (!due) return null;
  const m = String(due).match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (!m) return null;
  const d = new Date(+m[1], +m[2] - 1, +m[3]);
  const now = new Date();
  const t = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const diff = Math.round((d - t) / 86400000);
  if (diff === 0) return { text: "今天", hot: true };
  if (diff === 1) return { text: "明天", hot: false, soon: true };
  return { text: (+m[2]) + "/" + (+m[3]), hot: diff < 0 };
}

function pageUrl(p) { return EDIT_URL + (p ? "#" + encodeURIComponent(p.id) : ""); }
function oneLine(s) { return String(s || "").replace(/\s+/g, " ").trim(); }

// ── 画的小零件 ─────────────────────────────────────────────────
function symbol(name, size, weightFont) {
  const s = SFSymbol.named(name);
  if (!s) return null;
  if (weightFont) s.applyFont(weightFont);
  return s.image;
}

function addLine(parent, st) {
  const l = parent.addStack();
  l.size = new Size(0, 0.5);
  l.backgroundColor = st.rule;
  l.addSpacer();
}

function addDot(row, st, page, item, size) {
  const color = new Color(page.color || "#8C7BB8");
  let img;
  if (item.pin) {
    img = row.addImage(symbol("star.fill", size, Font.systemFont(size)));
    img.tintColor = st.gold || color;
  } else if (st.dot === "ring") {
    img = row.addImage(symbol("circle", size, Font.lightSystemFont(size)));
    img.tintColor = dyn("#C7C7CC", "#48484A");
  } else if (st.dot === "ice") {
    img = row.addImage(symbol("circle", size, Font.systemFont(size)));
    img.tintColor = st.ice;
  } else {
    img = row.addImage(symbol("circle", size, Font.mediumSystemFont(size)));
    img.tintColor = color;
  }
  img.imageSize = new Size(size, size);
}

function addHeader(parent, st, page, count, f, opts) {
  const h = parent.addStack();
  h.layoutHorizontally();
  h.centerAlignContent();
  if (st.flake) {
    const s = h.addImage(symbol("snowflake", f.title, Font.systemFont(f.title)));
    s.imageSize = new Size(f.title - 1, f.title - 1);
    s.tintColor = st.ice;
    h.addSpacer(4);
  }
  const name = h.addText((st.flake ? "" : (page.emoji || "") + " ") + page.name);
  name.font = st.title(f.title);
  name.textColor = st.titleInColor ? new Color(page.color || "#8C7BB8") : st.ink;
  name.lineLimit = 1;
  h.addSpacer();
  if (opts && opts.stale) {
    const w = h.addImage(symbol("wifi.slash", 9, Font.systemFont(9)));
    w.imageSize = new Size(10, 10);
    w.tintColor = st.sub;
    h.addSpacer(5);
  }
  const n = h.addText(String(count));
  n.font = st.count(f.count);
  n.textColor = st.titleInColor ? st.ink : (st.ice || new Color(page.color || "#8C7BB8"));
  return h;
}

function addItemRow(parent, st, page, item, f, showDue) {
  const r = parent.addStack();
  r.layoutHorizontally();
  r.centerAlignContent();
  addDot(r, st, page, item, f.dot);
  r.addSpacer(f.gap);
  const t = r.addText(oneLine(item.text));
  t.font = st.item(f.item);
  t.textColor = st.ink;
  t.lineLimit = 1;
  t.minimumScaleFactor = 0.85;   // 长一点的先缩小一丁点，实在放不下再截成「…」
  r.addSpacer();
  // 小号放不下日期，只把今天到期 / 已经过期的红字露出来
  const lab = dueLabel(item.due);
  const due = (showDue === true || (showDue === "hot" && lab && lab.hot)) ? lab : null;
  if (due) {
    r.addSpacer(4);
    const d = r.addText(due.text);
    d.font = Font.mediumSystemFont(f.item - 2.5);
    d.textColor = due.hot ? RED : (due.soon ? new Color(page.color || "#8C7BB8") : st.sub);
    d.lineLimit = 1;
  }
}

function addEmpty(parent, st, page, f, big) {
  const e = parent.addStack();
  e.layoutVertically();
  const a = e.addText(big ? "这一页还空着" : "还空着");
  a.font = Font.mediumSystemFont(big ? f.item : f.item - 1);
  a.textColor = st.sub;
  if (big) {
    e.addSpacer(3);
    const b = e.addText("想到什么就记一笔");
    b.font = Font.systemFont(f.item - 2);
    b.textColor = st.sub;
    b.textOpacity = 0.8;
    b.lineLimit = 1;
  }
}

// 一页：抬头 + 若干行。宽的格子里条目多了就分两栏。
function addPageBlock(parent, st, data, page, f, maxRows, opts) {
  const items = openItems(data, page.id);
  addHeader(parent, st, page, items.length, f, opts);
  parent.addSpacer(f.afterHeader);
  if (st.rules) { addLine(parent, st); parent.addSpacer(f.ruleGap); }
  if (!items.length) {
    addEmpty(parent, st, page, f, opts && opts.bigEmpty);
    return;
  }
  const cols = (opts && opts.twoCols && items.length > maxRows) ? 2 : 1;
  const shown = items.slice(0, maxRows * cols);
  if (cols === 1) {
    addRows(parent, st, page, shown, f, opts);
  } else {
    const grid = parent.addStack();
    grid.layoutHorizontally();
    grid.topAlignContent();
    const left = grid.addStack(); left.layoutVertically();
    grid.addSpacer(14);
    const right = grid.addStack(); right.layoutVertically();
    addRows(left, st, page, shown.slice(0, maxRows), f, opts);
    addRows(right, st, page, shown.slice(maxRows), f, opts);
  }
}

function addRows(parent, st, page, items, f, opts) {
  items.forEach((it, k) => {
    if (k > 0) {
      if (st.rules) { parent.addSpacer(f.ruleGap); addLine(parent, st); parent.addSpacer(f.ruleGap); }
      else parent.addSpacer(f.rowGap);
    }
    addItemRow(parent, st, page, it, f, opts && opts.due);
  });
}

// 便笺顶上那一道色条
function addBand(w, st, page) {
  if (!st.band) return;
  const b = w.addStack();
  b.size = new Size(0, 6);
  b.backgroundColor = new Color((page && page.color) || "#C9B48C");
  b.addSpacer();
}

function body(w, st, pad) {
  const s = w.addStack();
  s.layoutVertically();
  s.setPadding(pad[0], pad[1], pad[2], pad[3]);
  return s;
}

// ── 各种尺寸 ───────────────────────────────────────────────────
const SIZES = {
  small:  { title: 14, count: 21, item: 13, dot: 11, gap: 7, rowGap: 7, ruleGap: 4, afterHeader: 7 },
  medium: { title: 14, count: 21, item: 13, dot: 11, gap: 7, rowGap: 7, ruleGap: 4, afterHeader: 7 },
  large:  { title: 15, count: 22, item: 14, dot: 12, gap: 8, rowGap: 8, ruleGap: 4.5, afterHeader: 8 },
  cell:   { title: 13, count: 17, item: 12.5, dot: 10, gap: 6, rowGap: 6, ruleGap: 3.5, afterHeader: 6 },
};
function sizeFor(st, key) {
  const f = Object.assign({}, SIZES[key]);
  if (st.dot === "ring") { f.dot += 6; f.rowGap += 2; f.gap += 2; }
  return f;
}

// 总览：每页一行——图标、（宽的时候带页名）、头一两条、条数
function addOverview(parent, st, data, pages, f, stale, wide) {
  const h = parent.addStack();
  h.layoutHorizontally();
  h.centerAlignContent();
  const title = h.addText("冬的备忘");
  title.font = st.title(f.title - 1);
  title.textColor = st.ink;
  h.addSpacer();
  if (stale) {
    const w = h.addImage(symbol("wifi.slash", 9, Font.systemFont(9)));
    w.imageSize = new Size(10, 10);
    w.tintColor = st.sub;
    h.addSpacer(5);
  }
  const fl = h.addImage(symbol("snowflake", 11, Font.systemFont(11)));
  fl.imageSize = new Size(11, 11);
  fl.tintColor = st.ice || st.sub;
  parent.addSpacer(f.afterHeader);
  if (st.rules) { addLine(parent, st); parent.addSpacer(f.ruleGap + 1); }
  pages.slice(0, wide ? 6 : 5).forEach((p, k) => {
    if (k > 0) {
      if (st.rules && wide) { parent.addSpacer(f.ruleGap); addLine(parent, st); parent.addSpacer(f.ruleGap); }
      else parent.addSpacer(st.dot === "ring" ? 8 : 7);
    }
    const items = openItems(data, p.id);
    const color = new Color(p.color || "#8C7BB8");
    const r = parent.addStack();
    r.layoutHorizontally();
    r.centerAlignContent();
    r.url = pageUrl(p);
    const e = r.addText(p.emoji || "•");
    e.font = Font.systemFont(f.item - 1);
    r.addSpacer(6);
    if (wide) {
      const nm = r.addStack();
      nm.size = new Size(36, 0);
      const nt = nm.addText(p.name);
      nt.font = st.title(f.item - 0.5);
      nt.textColor = st.titleInColor ? color : st.ink;
      nt.lineLimit = 1;
      nm.addSpacer();
      r.addSpacer(6);
    }
    const first = items.slice(0, wide ? 2 : 1).map((i) => oneLine(i.text)).join("  ·  ");
    const t = r.addText(items.length ? first : (wide ? "还空着" : p.name + " · 还空着"));
    t.font = st.item(f.item - 0.5);
    t.textColor = items.length ? st.ink : st.sub;
    t.lineLimit = 1;
    r.addSpacer();
    r.addSpacer(4);
    const n = r.addText(String(items.length));
    n.font = st.count(f.item);
    n.textColor = st.titleInColor ? st.ink : color;
  });
}

function buildSmall(w, st, data, pages, stale) {
  const f = sizeFor(st, "small");
  if (pages.length === 1) {
    const p = pages[0];
    w.url = pageUrl(p);
    addBand(w, st, p);
    const b = body(w, st, st.band ? [10, 14, 12, 14] : [14, 15, 13, 15]);
    addPageBlock(b, st, data, p, f, st.rows.small, { stale: stale, bigEmpty: true, due: "hot" });
    b.addSpacer();
  } else {
    w.url = pageUrl(null);
    addBand(w, st, { color: "#C9B48C" });
    const b = body(w, st, st.band ? [10, 14, 12, 14] : [14, 15, 13, 15]);
    addOverview(b, st, data, pages, f, stale);
    b.addSpacer();
  }
}

function buildMedium(w, st, data, pages, stale) {
  if (pages.length === 1) {
    const p = pages[0];
    w.url = pageUrl(p);
    addBand(w, st, p);
    const b = body(w, st, st.band ? [10, 16, 12, 16] : [14, 16, 13, 16]);
    addPageBlock(b, st, data, p, sizeFor(st, "medium"), st.rows.medium, { stale: stale, due: true, twoCols: true, bigEmpty: true });
    b.addSpacer();
    return;
  }
  addBand(w, st, { color: "#C9B48C" });
  const b = body(w, st, st.band ? [10, 15, 12, 15] : [13, 15, 12, 15]);
  w.url = pageUrl(null);
  if (pages.length === 2) {
    columns(b, st, data, pages, sizeFor(st, "medium"), st.rows.medium - (st.rules ? 1 : 0), stale, true);
  } else {
    // 三页以上：一页一行，每行带头两条
    addOverview(b, st, data, pages, sizeFor(st, "medium"), stale, true);
  }
  b.addSpacer();
}

function buildLarge(w, st, data, pages, stale) {
  if (pages.length === 1) {
    const p = pages[0];
    w.url = pageUrl(p);
    addBand(w, st, p);
    const b = body(w, st, st.band ? [12, 18, 14, 18] : [17, 18, 15, 18]);
    addPageBlock(b, st, data, p, sizeFor(st, "large"), st.rows.large, { stale: stale, due: true, bigEmpty: true });
    b.addSpacer();
    return;
  }
  addBand(w, st, { color: "#C9B48C" });
  const b = body(w, st, st.band ? [12, 16, 14, 16] : [16, 16, 14, 16]);
  w.url = pageUrl(null);
  if (pages.length === 2) {
    columns(b, st, data, pages, sizeFor(st, "medium"), st.rows.large - 2, stale, true);
    b.addSpacer();
  } else {
    // 三四页：两行两列，上下两行各占一半高（格子里垫了弹性空白，SwiftUI 会平分）
    grid(b, st, data, pages.slice(0, 4), sizeFor(st, "cell"), st.rows.cell, stale);
  }
}

function columns(parent, st, data, pages, f, rows, stale, due) {
  const row = parent.addStack();
  row.layoutHorizontally();
  row.topAlignContent();
  pages.forEach((p, k) => {
    if (k > 0) row.addSpacer(16);
    const c = row.addStack();
    c.layoutVertically();
    c.url = pageUrl(p);
    addPageBlock(c, st, data, p, f, rows, { stale: stale && k === pages.length - 1, due: due });
  });
}

function grid(parent, st, data, pages, f, rows, stale) {
  for (let r = 0; r < pages.length; r += 2) {
    if (r > 0) parent.addSpacer(st.rules ? 10 : 12);
    const line = parent.addStack();
    line.layoutHorizontally();
    line.topAlignContent();
    [pages[r], pages[r + 1]].forEach((p, k) => {
      if (k > 0) line.addSpacer(14);
      const c = line.addStack();
      c.layoutVertically();
      if (p) {
        c.url = pageUrl(p);
        addPageBlock(c, st, data, p, f, rows, { stale: stale && r === 0 && k === 1 });
      }
      c.addSpacer();
    });
  }
}

function buildError(w) {
  const st = STYLES.paper;
  w.url = EDIT_URL;
  const b = body(w, st, [14, 15, 14, 15]);
  const a = b.addText("备忘本这会儿没连上");
  a.font = Font.semiboldSystemFont(13);
  a.textColor = st.ink;
  b.addSpacer(4);
  const c = b.addText("点一下去网页里看");
  c.font = Font.systemFont(11.5);
  c.textColor = st.sub;
  b.addSpacer();
}

async function buildWidget(family) {
  const got = await loadMemo();
  const w = new ListWidget();
  w.setPadding(0, 0, 0, 0);
  w.refreshAfterDate = new Date(Date.now() + 10 * 60 * 1000);
  if (!got.data) {
    w.backgroundColor = STYLES.paper.bg;
    buildError(w);
    return w;
  }
  const data = got.data;
  const st = STYLES[(data.settings && data.settings.style) || "paper"] || STYLES.paper;
  w.backgroundColor = st.bg;
  const pages = chosenPages(data);
  if (!pages.length) { buildError(w); return w; }
  if (family === "small") buildSmall(w, st, data, pages, got.stale);
  else if (family === "large" || family === "extraLarge") buildLarge(w, st, data, pages, got.stale);
  else buildMedium(w, st, data, pages, got.stale);
  return w;
}

if (config.runsInWidget) {
  Script.setWidget(await buildWidget(config.widgetFamily || "small"));
} else {
  // 在 Scriptable 里直接点运行：挑一个尺寸预览，或者打开备忘本网页
  const a = new Alert();
  a.title = "冬的备忘本";
  a.message = "预览一下桌面上的样子，或者打开备忘本看全文。";
  a.addAction("预览 · 小");
  a.addAction("预览 · 中");
  a.addAction("预览 · 大");
  a.addAction("打开备忘本");
  a.addCancelAction("算了");
  const pick = await a.presentSheet();
  if (pick === 0) await (await buildWidget("small")).presentSmall();
  else if (pick === 1) await (await buildWidget("medium")).presentMedium();
  else if (pick === 2) await (await buildWidget("large")).presentLarge();
  else if (pick === 3) Safari.open(EDIT_URL);
}
Script.complete();
