// ============================================================
//  今日的 Sam · Scriptable 桌面小组件
//  每天自动显示台词墙「今日一句」，与网站完全同步。
//  数据源：sam/lines.json（改网站内容，小组件跟着变）
//  支持 小 / 中 / 大 三种尺寸，自动适配。
// ============================================================

// ── 可自定义（改这两行即可）──────────────────────────────────
const FONT = "serif";     // "serif"（衬线，接近网站）｜ "system"（系统默认）
const SHOW_GLOSS = true;  // 中号/大号是否显示中文翻译
// ────────────────────────────────────────────────────────────

const DATA_URL = "https://dxwintersun.github.io/WinterSunBlog/sam/lines.json";
const TODAY_URL = "https://dxwintersun.github.io/WinterSunBlog/sam/today/";
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

function paint(w, c) {
  const grad = new LinearGradient();
  grad.colors = [new Color(c.bg), new Color(shade(c.bg, -0.42))];
  grad.locations = [0, 1];
  w.backgroundGradient = grad;
  w.url = TODAY_URL; // 点一下打开「今日的 Sam」页面
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
  const sign = w.addText("— " + c.name + " · " + c.year);
  sign.font = fSign(11);
  sign.textColor = new Color(c.muted);
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
  const c = data.lines[todayIndex(data.lines.length)];
  const w = new ListWidget();
  paint(w, c);

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
