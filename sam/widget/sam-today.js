// ============================================================
//  今日的 Sam · Scriptable 桌面小组件
//  每天自动显示台词墙「今日一句」，与网站完全同步。
//  数据源：sam/lines.json（改网站内容，小组件跟着变）
//  支持 小 / 中 / 大 三种尺寸，自动适配。
// ============================================================

// ── 可自定义（改这三行即可）──────────────────────────────────
const FONT = "serif";     // "serif"（衬线，接近网站）｜ "system"（系统默认）
const SHOW_GLOSS = true;  // 中号/大号是否显示中文翻译
const PIN = "";           // 固定角色/固定某一句，留空 = 跟着全站每天轮换。
                           // 从台词墙（/sam/wall/）「📌 复制到桌面小组件」按钮
                           // 复制代码粘到这对引号里：填「krzysztof」锁定这个人
                           // （仍在他 5 句里按天换）；填「krzysztof:2」锁死这一句。
                           // 改完这一行，保存脚本即可——不用去 iOS 那边找小组件的
                           // 「参数」设置。
// ────────────────────────────────────────────────────────────

const DATA_URL = "https://dxwintersun.github.io/WinterSunBlog/sam/lines.json";
const TODAY_URL = "https://dxwintersun.github.io/WinterSunBlog/sam/today/";
const WALL_URL = "https://dxwintersun.github.io/WinterSunBlog/sam/wall/";
const START = Date.UTC(2026, 1, 13); // 2026-02-13，与网站同一起点

function dayCount() {
  const now = new Date();
  const today = Date.UTC(now.getFullYear(), now.getMonth(), now.getDate());
  return Math.floor((today - START) / 86400000) + 1;
}
function todayIndex(n) {
  const now = new Date();
  const today = Date.UTC(now.getFullYear(), now.getMonth(), now.getDate());
  const days = Math.round((today - START) / 86400000);
  return ((days % n) + n) % n;
}
function shade(hex, amt) { // amt<0 变暗
  const h = hex.replace("#", "");
  let r = parseInt(h.substr(0, 2), 16), g = parseInt(h.substr(2, 2), 16), b = parseInt(h.substr(4, 2), 16);
  const f = 1 + amt;
  const c = (x) => Math.max(0, Math.min(255, Math.round(x * f)));
  const to = (x) => ("0" + x.toString(16)).slice(-2);
  return "#" + to(c(r)) + to(c(g)) + to(c(b));
}

// 字体：衬线用 Georgia（中文自动回退到系统苹方）
function fSerif(size, style) {
  const name = style === "bold" ? "Georgia-Bold" : style === "italic" ? "Georgia-Italic" : "Georgia";
  return new Font(name, size);
}
function fQuote(size) { return FONT === "serif" ? fSerif(size, "italic") : Font.italicSystemFont(size); }
function fSign(size)  { return FONT === "serif" ? fSerif(size, "italic") : Font.italicSystemFont(size); }
function fBody(size)  { return FONT === "serif" ? fSerif(size, "regular") : Font.systemFont(size); }

async function getData() {
  const req = new Request(DATA_URL);
  req.timeoutInterval = 15;
  return await req.loadJSON();
}

// ── 固定角色 / 固定某一句（可选）──────────────────────────────
// 优先读顶部那行 PIN 常量（改脚本里的一行文字，最简单）；PIN 留空的话，
// 兼容读一下小组件自带的「参数」（长按小组件→编辑小组件→参数），给已经
// 会用这个的人用。两处都留空 = 和以前一样，跟着网站全站两百多句每日轮换。
// 格式：「角色id」锁定这个角色，仍在他 5 句里按天轮换；「角色id:第几句」
// 锁死这一句永远不变。参数写错/角色不存在也不会让小组件报错——自动退回
// 全站轮换。
function pickQuote(data) {
  const fromParam = (typeof args !== "undefined" && args.widgetParameter) || "";
  const raw = (PIN || fromParam || "").trim();
  if (!raw) return { c: data.pool[todayIndex(data.pool.length)], pinned: false };

  const bits = raw.split(":");
  const character = data.characters.find(function (x) { return x.id === bits[0].trim(); });
  if (!character) return { c: data.pool[todayIndex(data.pool.length)], pinned: false };

  const n = parseInt(bits[1], 10);
  const quotes = character.quotes;
  const q = (n >= 1 && n <= quotes.length) ? quotes[n - 1] : quotes[todayIndex(quotes.length)];
  return {
    pinned: true,
    c: {
      charId: character.id, name: character.name, film: character.film, filmCN: character.filmCN, year: character.year,
      accent: character.accent, bg: character.bg, text: character.text, muted: character.muted, auLink: character.auLink,
      label: q.label, line: q.line, lineCN: q.lineCN, kind: q.kind,
    },
  };
}

function paint(w, c, pinned) {
  const grad = new LinearGradient();
  grad.colors = [new Color(c.bg), new Color(shade(c.bg, -0.42))];
  grad.locations = [0, 1];
  w.backgroundGradient = grad;
  // 固定角色时点一下直接打开他在台词墙上的位置，没固定就还是打开「今日的 Sam」
  w.url = pinned ? (WALL_URL + "?char=" + c.charId) : TODAY_URL;
}

function buildSmall(w, c) {
  w.setPadding(13, 14, 13, 14);
  const label = w.addText(c.label);
  label.font = Font.mediumSystemFont(8);
  label.textColor = new Color(c.accent);
  label.lineLimit = 1;
  w.addSpacer(6);
  const line = w.addText("“" + c.line + "”");
  line.font = fQuote(12.5);
  line.textColor = new Color(c.text);
  line.minimumScaleFactor = 0.5;
  w.addSpacer();
  const sign = w.addText("— " + c.name);
  sign.font = fSign(10.5);
  sign.textColor = new Color(c.muted);
  sign.lineLimit = 1;
  w.addSpacer(3);
  const meta = w.addText(c.filmCN + " · 第 " + dayCount() + " 天");
  meta.font = fBody(9);
  meta.textColor = new Color(c.muted);
  meta.textOpacity = 0.72;
  meta.lineLimit = 1;
  meta.minimumScaleFactor = 0.55;
}

function buildMedium(w, c) {
  w.setPadding(16, 17, 16, 17);
  const label = w.addText(c.label);
  label.font = Font.mediumSystemFont(9);
  label.textColor = new Color(c.accent);
  label.lineLimit = 1;
  w.addSpacer(7);
  const line = w.addText("“" + c.line + "”");
  line.font = fQuote(15);
  line.textColor = new Color(c.text);
  line.minimumScaleFactor = 0.6;
  if (SHOW_GLOSS) {
    w.addSpacer(5);
    const gloss = w.addText(c.lineCN);
    gloss.font = fBody(11);
    gloss.textColor = new Color(c.text);
    gloss.textOpacity = 0.72;
    gloss.minimumScaleFactor = 0.7;
  }
  w.addSpacer();
  const sign = w.addText("— " + c.name);
  sign.font = fSign(11);
  sign.textColor = new Color(c.muted);
  w.addSpacer(2);
  const meta = w.addText(c.filmCN + " · " + c.year + " · 日更第 " + dayCount() + " 天");
  meta.font = fBody(10);
  meta.textColor = new Color(c.muted);
  meta.textOpacity = 0.78;
  meta.lineLimit = 1;
  meta.minimumScaleFactor = 0.6;
}

function buildLarge(w, c) {
  w.setPadding(22, 22, 22, 22);
  const q = w.addText("“");
  q.font = FONT === "serif" ? fSerif(52, "italic") : Font.italicSystemFont(52);
  q.textColor = new Color(c.accent);
  q.textOpacity = 0.5;
  w.addSpacer(2);
  const label = w.addText(c.label);
  label.font = Font.mediumSystemFont(11);
  label.textColor = new Color(c.accent);
  label.lineLimit = 1;
  w.addSpacer(12);
  const line = w.addText(c.line);
  line.font = fQuote(21);
  line.textColor = new Color(c.text);
  line.minimumScaleFactor = 0.7;
  if (SHOW_GLOSS) {
    w.addSpacer(10);
    const gloss = w.addText(c.lineCN);
    gloss.font = fBody(13.5);
    gloss.textColor = new Color(c.text);
    gloss.textOpacity = 0.78;
    gloss.minimumScaleFactor = 0.8;
  }
  w.addSpacer();
  const sign = w.addText("— " + c.name);
  sign.font = fSign(15);
  sign.textColor = new Color(c.muted);
  w.addSpacer(3);
  const meta = w.addText(c.filmCN + " · " + c.year + "  ·  日更第 " + dayCount() + " 天");
  meta.font = fBody(10.5);
  meta.textColor = new Color(c.muted);
  meta.textOpacity = 0.8;
}

async function buildWidget() {
  const data = await getData();
  const picked = pickQuote(data);
  const c = picked.c;
  const w = new ListWidget();
  paint(w, c, picked.pinned);

  const family = config.widgetFamily || "medium";
  if (family === "small") buildSmall(w, c);
  else if (family === "large" || family === "extraLarge") buildLarge(w, c);
  else buildMedium(w, c);

  // 每 3 小时刷新一次（跨零点自动换成新的一句）
  w.refreshAfterDate = new Date(Date.now() + 3 * 3600 * 1000);
  return w;
}

const widget = await buildWidget();
if (config.runsInWidget) {
  Script.setWidget(widget);
} else {
  // 在 Scriptable 里手动运行时，依次预览三种尺寸
  await widget.presentMedium();
}
Script.complete();
