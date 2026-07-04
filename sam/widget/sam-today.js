// ============================================================
//  今日的 Sam · Scriptable 桌面小组件
//  每天自动显示台词墙「今日一句」，与网站完全同步。
//  数据源：sam/lines.json（改网站内容，小组件跟着变）
// ============================================================

const DATA_URL = "https://dxwintersun.github.io/WinterSunBlog/sam/lines.json";
const TODAY_URL = "https://dxwintersun.github.io/WinterSunBlog/sam/today/";
const START = Date.UTC(2026, 1, 13); // 2026-02-13，与网站同一起点

function todayIndex(n) {
  const now = new Date();
  const today = Date.UTC(now.getFullYear(), now.getMonth(), now.getDate());
  const days = Math.round((today - START) / 86400000);
  return ((days % n) + n) % n;
}

function shade(hex, amt) { // amt<0 变暗
  const h = hex.replace("#", "");
  let r = parseInt(h.substr(0, 2), 16),
      g = parseInt(h.substr(2, 2), 16),
      b = parseInt(h.substr(4, 2), 16);
  const f = 1 + amt;
  r = Math.max(0, Math.min(255, Math.round(r * f)));
  g = Math.max(0, Math.min(255, Math.round(g * f)));
  b = Math.max(0, Math.min(255, Math.round(b * f)));
  const to = (x) => ("0" + x.toString(16)).slice(-2);
  return "#" + to(r) + to(g) + to(b);
}

async function getData() {
  const req = new Request(DATA_URL);
  req.timeoutInterval = 15;
  return await req.loadJSON();
}

async function buildWidget() {
  const data = await getData();
  const c = data.lines[todayIndex(data.lines.length)];

  const w = new ListWidget();
  const grad = new LinearGradient();
  grad.colors = [new Color(c.bg), new Color(shade(c.bg, -0.42))];
  grad.locations = [0, 1];
  w.backgroundGradient = grad;
  w.setPadding(16, 17, 16, 17);
  w.url = TODAY_URL; // 点一下打开「今日的 Sam」页面

  const label = w.addText(c.label);
  label.font = Font.mediumSystemFont(9);
  label.textColor = new Color(c.accent);
  label.lineLimit = 1;

  w.addSpacer(7);

  const line = w.addText("“" + c.line + "”");
  line.font = Font.italicSystemFont(15);
  line.textColor = new Color(c.text);
  line.minimumScaleFactor = 0.6;

  w.addSpacer(5);

  const gloss = w.addText(c.lineCN);
  gloss.font = Font.systemFont(11);
  gloss.textColor = new Color(c.text);
  gloss.textOpacity = 0.72;
  gloss.minimumScaleFactor = 0.7;

  w.addSpacer();

  const sign = w.addText("— " + c.name + " · " + c.year);
  sign.font = Font.italicSystemFont(11);
  sign.textColor = new Color(c.muted);

  // 每 3 小时刷新一次（跨零点自动换成新的一句）
  w.refreshAfterDate = new Date(Date.now() + 3 * 3600 * 1000);
  return w;
}

const widget = await buildWidget();
if (config.runsInWidget) {
  Script.setWidget(widget);
} else {
  await widget.presentMedium();
}
Script.complete();
