#!/usr/bin/env node
/* ============================================================
   Scriptable 小组件模拟器：不用 iPhone，也能看见桌面小组件长什么样
   ------------------------------------------------------------
   把一份 Scriptable 脚本（memo/widget/winter-memo.js、sam/widget/sam-today.js …）
   放进一个「假的 Scriptable」里跑一遍，把它搭出来的 ListWidget / 各层 stack
   原样记下来，再翻译成一张 HTML（flex 布局近似 SwiftUI 的排法）。配
   shot.js 截成 PNG，就是给 Winter 看的效果图。

   用法：
     node tools/widget-sim/sim.js <脚本> --family small|medium|large \
          [--param "工作"] [--data 本地json] [--dark] -o out.html

   --data：脚本里 Request 去取的东西一律换成这份本地文件（不联网）。
   假 API 只实现了我们脚本里用到的那些；脚本调了一个不存在的方法会照样报错——
   这正好在上手机前把拼错的 API 拦下来。
   字体是近似：SF Pro → Inter，苹方 → Noto Sans SC，Georgia → Gelasio。
   ============================================================ */
"use strict";
const fs = require("fs");
const path = require("path");
const vm = require("vm");

// ————— 参数 —————
const argv = process.argv.slice(2);
function opt(name, dflt) {
  const i = argv.indexOf(name);
  if (i < 0) return dflt;
  const v = argv[i + 1];
  argv.splice(i, 2);
  return v;
}
function flag(name) {
  const i = argv.indexOf(name);
  if (i < 0) return false;
  argv.splice(i, 1);
  return true;
}
const family = opt("--family", "small");
const param = opt("--param", "");
const dataFile = opt("--data", null);
const out = opt("-o", null);
const dark = flag("--dark");
const scriptPath = argv[0];
if (!scriptPath) {
  console.error("要给一个脚本路径");
  process.exit(2);
}

// Winter 那台 iPhone（截图 1206 宽、3 倍屏）上量出来的小组件尺寸，单位 pt。
// 别的机型用 --size 宽x高 覆盖。
const FAMILY_SIZE = { small: [163, 163], medium: [350, 163], large: [350, 363], extraLarge: [350, 363] };
const sizeOpt = opt("--size", null);
if (sizeOpt) FAMILY_SIZE[family] = sizeOpt.split("x").map(Number);

// ————— 假 Scriptable —————
class Color {
  constructor(hex, alpha) {
    this.hex = String(hex).replace("#", "");
    this.alpha = alpha === undefined ? 1 : alpha;
  }
  static dynamic(light, darkC) { const c = new Color("000000"); c.dyn = [light, darkC]; return c; }
  static white() { return new Color("FFFFFF"); }
  static black() { return new Color("000000"); }
  static clear() { return new Color("000000", 0); }
  static gray() { return new Color("808080"); }
  static red() { return new Color("FF3B30"); }
}
function css(c, opacity) {
  if (!c) return null;
  if (c.dyn) return css(dark ? c.dyn[1] : c.dyn[0], opacity);
  let h = c.hex;
  if (h.length === 3) h = h.split("").map((x) => x + x).join("");
  const r = parseInt(h.slice(0, 2), 16), g = parseInt(h.slice(2, 4), 16), b = parseInt(h.slice(4, 6), 16);
  let a = c.alpha;
  if (h.length === 8) a = parseInt(h.slice(6, 8), 16) / 255;
  if (opacity !== undefined && opacity !== null) a *= opacity;
  return `rgba(${r},${g},${b},${+a.toFixed(3)})`;
}

class Font {
  constructor(name, size) {
    this.name = name;
    this.size = size;
    this.weight = /Bold/i.test(name) ? 700 : /Semibold/i.test(name) ? 600 : /Medium/i.test(name) ? 500 : 400;
    this.italic = /Italic/i.test(name);
    this.family = /Georgia/i.test(name) ? "georgia" : "custom";
  }
}
function sysFont(weight, italic, rounded) {
  return (size) => {
    const f = new Font("system", size);
    f.family = rounded ? "rounded" : "system";
    f.weight = weight;
    f.italic = !!italic;
    return f;
  };
}
Object.assign(Font, {
  systemFont: sysFont(400), ultraLightSystemFont: sysFont(200), thinSystemFont: sysFont(250),
  lightSystemFont: sysFont(300), regularSystemFont: undefined, mediumSystemFont: sysFont(500),
  semiboldSystemFont: sysFont(600), boldSystemFont: sysFont(700), heavySystemFont: sysFont(800),
  blackSystemFont: sysFont(900), italicSystemFont: sysFont(400, true),
  regularRoundedSystemFont: sysFont(400, false, true), mediumRoundedSystemFont: sysFont(500, false, true),
  semiboldRoundedSystemFont: sysFont(600, false, true), boldRoundedSystemFont: sysFont(700, false, true),
  headline: () => sysFont(600)(17), body: () => sysFont(400)(17), footnote: () => sysFont(400)(13),
  caption1: () => sysFont(400)(12), caption2: () => sysFont(400)(11),
});
delete Font.regularSystemFont; // 真的 Scriptable 没有这个；留着 undefined 会让「Font.regularSystemFont ?」判断失真

class Size { constructor(w, h) { this.width = w; this.height = h; } }
class Point { constructor(x, y) { this.x = x; this.y = y; } }
class LinearGradient { constructor() { this.colors = []; this.locations = []; this.startPoint = new Point(0, 0); this.endPoint = new Point(0, 1); } }

class Image { constructor(kind, data) { this.kind = kind; this.data = data; this.size = new Size(20, 20); } }
class SFSymbol {
  constructor(name) { this.name = name; this.weight = 400; }
  static named(name) { return new SFSymbol(name); }
  applyFont(f) { this.weight = f.weight; }
  applyUltraLightWeight() { this.weight = 200; } applyThinWeight() { this.weight = 250; }
  applyLightWeight() { this.weight = 300; } applyRegularWeight() { this.weight = 400; }
  applyMediumWeight() { this.weight = 500; } applySemiboldWeight() { this.weight = 600; }
  applyBoldWeight() { this.weight = 700; } applyHeavyWeight() { this.weight = 800; }
  applyBlackWeight() { this.weight = 900; }
  get image() { return new Image("sf", { name: this.name, weight: this.weight }); }
}

class WidgetText {
  constructor(text) { this.kind = "text"; this.text = String(text); this.font = sysFont(400)(17); this.textColor = null; this.textOpacity = 1; this.lineLimit = 0; this.minimumScaleFactor = 1; this.align = "left"; this.shadowColor = null; }
  leftAlignText() { this.align = "left"; } centerAlignText() { this.align = "center"; } rightAlignText() { this.align = "right"; }
}
class WidgetDate extends WidgetText {
  constructor(d) { super(d.toLocaleTimeString()); this.kind = "text"; }
  applyTimeStyle() {} applyDateStyle() {} applyRelativeStyle() {} applyOffsetStyle() {} applyTimerStyle() {}
}
class WidgetImage {
  constructor(img) {
    if (!img) throw new TypeError("addImage(null)：图片是空的（SF Symbol 名字拼错了？）");
    this.kind = "image"; this.image = img; this.imageSize = null; this.tintColor = null; this.imageOpacity = 1; this.resizable = true; this.cornerRadius = 0; this.containerRelativeShape = false; this.align = "left";
  }
  leftAlignImage() {} centerAlignImage() {} rightAlignImage() {} applyFittingContentMode() {} applyFillingContentMode() {}
}
class WidgetSpacer { constructor(len) { this.kind = "spacer"; this.length = len === undefined ? null : len; } }
class WidgetStack {
  constructor() { this.kind = "stack"; this.dir = "h"; this.align = "center"; this.children = []; this.spacing = 0; this.size = new Size(0, 0); this.padding = null; this.backgroundColor = null; this.backgroundGradient = null; this.cornerRadius = 0; this.borderWidth = 0; this.borderColor = null; this.url = null; }
  layoutHorizontally() { this.dir = "h"; } layoutVertically() { this.dir = "v"; }
  topAlignContent() { this.align = "top"; } centerAlignContent() { this.align = "center"; } bottomAlignContent() { this.align = "bottom"; }
  setPadding(t, l, b, r) { this.padding = [t, l, b, r]; } useDefaultPadding() { this.padding = null; }
  addText(t) { const x = new WidgetText(t); this.children.push(x); return x; }
  addDate(d) { const x = new WidgetDate(d); this.children.push(x); return x; }
  addImage(i) { const x = new WidgetImage(i); this.children.push(x); return x; }
  addSpacer(n) { const x = new WidgetSpacer(n); this.children.push(x); return x; }
  addStack() { const x = new WidgetStack(); this.children.push(x); return x; }
}
let captured = null;
class ListWidget extends WidgetStack {
  constructor() { super(); this.kind = "widget"; this.dir = "v"; this.padding = [16, 16, 16, 16]; this.backgroundImage = null; this.refreshAfterDate = null; }
  async presentSmall() { captured = this; } async presentMedium() { captured = this; }
  async presentLarge() { captured = this; } async presentExtraLarge() { captured = this; }
  async presentAccessoryCircular() { captured = this; } async presentAccessoryRectangular() { captured = this; } async presentAccessoryInline() { captured = this; }
}

// Request：一律从 --data 那份本地文件里拿
class Request {
  constructor(url) { this.url = url; this.method = "GET"; this.headers = {}; this.timeoutInterval = 60; this.response = null; }
  async loadString() {
    if (!dataFile) throw new Error("没给 --data，模拟器不联网");
    const text = fs.readFileSync(dataFile, "utf8");
    this.response = { statusCode: 200, headers: { etag: '"sim"' } };
    return text;
  }
  async loadJSON() { return JSON.parse(await this.loadString()); }
  async load() { return Buffer.from(await this.loadString()); }
}

// FileManager：放进一个临时目录，每次模拟都是干净的
const tmpRoot = fs.mkdtempSync(path.join(require("os").tmpdir(), "scriptable-sim-"));
const fileManager = {
  documentsDirectory: () => tmpRoot, cacheDirectory: () => tmpRoot, temporaryDirectory: () => tmpRoot, libraryDirectory: () => tmpRoot,
  joinPath: (a, b) => path.join(a, b),
  fileExists: (p) => fs.existsSync(p),
  isDirectory: (p) => fs.existsSync(p) && fs.statSync(p).isDirectory(),
  createDirectory: (p, inter) => fs.mkdirSync(p, { recursive: !!inter }),
  readString: (p) => fs.readFileSync(p, "utf8"),
  writeString: (p, s) => fs.writeFileSync(p, s),
  remove: (p) => fs.rmSync(p, { recursive: true, force: true }),
  modificationDate: (p) => fs.statSync(p).mtime,
  listContents: (p) => fs.readdirSync(p),
};
const FileManager = { local: () => fileManager, iCloud: () => fileManager };

class Alert {
  constructor() { this.title = ""; this.message = ""; this.actions = []; }
  addAction(t) { this.actions.push(t); } addCancelAction(t) { this.cancel = t; } addDestructiveAction(t) { this.actions.push(t); }
  addTextField() { return {}; } textFieldValue() { return ""; }
  async presentSheet() { return -1; } async presentAlert() { return -1; } async present() { return -1; }
}

const sandbox = {
  console, Color, Font, Size, Point, LinearGradient, Image, SFSymbol, ListWidget, WidgetStack, Request, FileManager, Alert,
  Safari: { open() {}, openInApp: async () => {} },
  Keychain: { contains: () => false, get: () => { throw new Error("no key"); }, set() {}, remove() {} },
  Device: { isUsingDarkAppearance: () => dark, locale: () => "zh_CN", language: () => "zh", screenSize: () => new Size(393, 852) },
  config: { runsInWidget: true, runsInApp: false, widgetFamily: family },
  args: { widgetParameter: param, queryParameters: {}, plainTexts: [], urls: [] },
  Script: { setWidget(w) { captured = w; }, complete() {}, name: () => "sim" },
  Data: {}, DateFormatter: class { constructor() { this.dateFormat = ""; } string(d) { return d.toISOString(); } },
  setTimeout, Date, Math, JSON, String, Number, Array, Object, RegExp, Promise, parseInt, parseFloat, encodeURIComponent, decodeURIComponent,
};

// ————— SF Symbol 的几张近似图 —————
function sfSvg(name, weight, size, color) {
  const sw = Math.max(0.9, size * (weight <= 300 ? 0.062 : weight <= 400 ? 0.08 : weight <= 500 ? 0.095 : 0.11));
  const c = color || "currentColor";
  const s = size;
  const r = s / 2 - sw / 2 - s * 0.04;
  switch (name) {
    case "circle":
      return `<svg width="${s}" height="${s}" viewBox="0 0 ${s} ${s}"><circle cx="${s / 2}" cy="${s / 2}" r="${r}" fill="none" stroke="${c}" stroke-width="${sw}"/></svg>`;
    case "circle.fill":
      return `<svg width="${s}" height="${s}" viewBox="0 0 ${s} ${s}"><circle cx="${s / 2}" cy="${s / 2}" r="${r + sw / 2}" fill="${c}"/></svg>`;
    case "star.fill": {
      const pts = [];
      for (let k = 0; k < 10; k++) {
        const rr = k % 2 ? s * 0.22 : s * 0.48;
        const a = -Math.PI / 2 + (k * Math.PI) / 5;
        pts.push((s / 2 + rr * Math.cos(a)).toFixed(2) + "," + (s / 2 + 0.03 * s + rr * Math.sin(a)).toFixed(2));
      }
      return `<svg width="${s}" height="${s}" viewBox="0 0 ${s} ${s}"><polygon points="${pts.join(" ")}" fill="${c}" stroke="${c}" stroke-width="${s * 0.06}" stroke-linejoin="round"/></svg>`;
    }
    case "snowflake": {
      let d = "";
      for (let k = 0; k < 6; k++) {
        const a = (k * Math.PI) / 3 - Math.PI / 2;
        const x = s / 2 + Math.cos(a) * s * 0.46, y = s / 2 + Math.sin(a) * s * 0.46;
        d += `M${s / 2},${s / 2}L${x.toFixed(2)},${y.toFixed(2)}`;
        const bx = s / 2 + Math.cos(a) * s * 0.3, by = s / 2 + Math.sin(a) * s * 0.3;
        for (const t of [-0.55, 0.55]) {
          const ex = bx + Math.cos(a + t * 1.7) * s * 0.13, ey = by + Math.sin(a + t * 1.7) * s * 0.13;
          d += `M${bx.toFixed(2)},${by.toFixed(2)}L${ex.toFixed(2)},${ey.toFixed(2)}`;
        }
      }
      return `<svg width="${s}" height="${s}" viewBox="0 0 ${s} ${s}"><path d="${d}" stroke="${c}" stroke-width="${sw * 1.1}" stroke-linecap="round" fill="none"/></svg>`;
    }
    case "wifi.slash":
      return `<svg width="${s}" height="${s}" viewBox="0 0 24 24"><path d="M3 9a13 13 0 0 1 18 0M6.5 12.5a8 8 0 0 1 11 0M10 16a3 3 0 0 1 4 0M3 3l18 18" stroke="${c}" stroke-width="2" fill="none" stroke-linecap="round"/></svg>`;
    default:
      return `<svg width="${s}" height="${s}" viewBox="0 0 ${s} ${s}"><rect x="1" y="1" width="${s - 2}" height="${s - 2}" rx="${s / 4}" fill="none" stroke="${c}" stroke-dasharray="2 2"/></svg>`;
  }
}

// ————— 记下来的树 → HTML —————
function fontCss(f) {
  const fam = f.family === "georgia" ? "'Gelasio','Noto Sans SC',serif"
    : f.family === "rounded" ? "'Nunito','Inter','Noto Sans SC',sans-serif"
    : "'Inter','Noto Sans SC',sans-serif";
  return `font-family:${fam};font-size:${f.size}px;font-weight:${f.weight};font-style:${f.italic ? "italic" : "normal"};`;
}
// 一个元素在主轴 / 交叉轴上要不要「撑满」：有弹性 spacer 的 stack 在它的方向上想占满
function wants(node, axis) {
  if (node.kind === "spacer") return false;
  if (node.kind === "text" || node.kind === "image") return false;
  if (node.size && ((axis === "w" && node.size.width > 0) || (axis === "h" && node.size.height > 0))) return false;
  const along = (node.dir === "h" && axis === "w") || (node.dir === "v" && axis === "h");
  if (along && node.children.some((c) => c.kind === "spacer" && c.length === null)) return true;
  return node.children.some((c) => c.kind === "stack" && wants(c, axis));
}
function render(node, parentDir) {
  const parts = [];
  let style = "";
  if (node.kind === "spacer") {
    if (node.length === null) style = "flex:1 1 0;min-width:0;min-height:0;";
    else style = parentDir === "h" ? `flex:0 0 ${node.length}px;width:${node.length}px;` : `flex:0 0 ${node.length}px;height:${node.length}px;`;
    return `<i style="${style}"></i>`;
  }
  if (node.kind === "text") {
    const f = node.font;
    const lim = node.lineLimit;
    style += fontCss(f) + `color:${css(node.textColor || Color.dynamic(new Color("000"), new Color("fff")), node.textOpacity)};text-align:${node.align};line-height:1.2;min-width:0;`;
    if (lim === 1) style += "white-space:nowrap;overflow:hidden;text-overflow:ellipsis;";
    else if (lim > 1) style += `display:-webkit-box;-webkit-line-clamp:${lim};-webkit-box-orient:vertical;overflow:hidden;`;
    if (parentDir === "h") style += "flex:0 1 auto;";
    const esc = node.text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/\n/g, "<br>");
    return `<span style="${style}">${esc}</span>`;
  }
  if (node.kind === "image") {
    const sz = node.imageSize ? node.imageSize : new Size(20, 20);
    const color = css(node.tintColor || Color.dynamic(new Color("000"), new Color("fff")), node.imageOpacity);
    const inner = node.image.kind === "sf" ? sfSvg(node.image.data.name, node.image.data.weight, sz.width, color) : "";
    return `<b style="display:flex;flex:0 0 auto;width:${sz.width}px;height:${sz.height}px;align-items:center;justify-content:center;">${inner}</b>`;
  }
  // stack / widget
  const dir = node.dir;
  style += `display:flex;flex-direction:${dir === "h" ? "row" : "column"};gap:${node.spacing || 0}px;min-width:0;min-height:0;`;
  if (dir === "h") style += `align-items:${node.align === "top" ? "flex-start" : node.align === "bottom" ? "flex-end" : "center"};`;
  else style += "align-items:flex-start;";
  if (node.padding) style += `padding:${node.padding.map((x) => x + "px").join(" ")};`;
  if (node.size && node.size.width > 0) style += `width:${node.size.width}px;flex-shrink:0;`;
  if (node.size && node.size.height > 0) style += `height:${node.size.height}px;flex-shrink:0;`;
  if (node.backgroundColor) style += `background:${css(node.backgroundColor)};`;
  if (node.backgroundGradient) {
    const g = node.backgroundGradient;
    style += `background:linear-gradient(180deg,${g.colors.map((c, i) => css(c) + " " + ((g.locations[i] || 0) * 100) + "%").join(",")});`;
  }
  if (node.cornerRadius) style += `border-radius:${node.cornerRadius}px;overflow:hidden;`;
  if (node.borderWidth) style += `border:${node.borderWidth}px solid ${css(node.borderColor)};`;
  // 自己在父容器里怎么伸
  if (parentDir === "h") {
    if (wants(node, "w")) style += "flex:1 1 0;";
    if (wants(node, "h")) style += "align-self:stretch;";
  } else if (parentDir === "v") {
    if (wants(node, "h")) style += "flex:1 1 0;";
    if (wants(node, "w")) style += "align-self:stretch;";
  }
  for (const c of node.children) parts.push(render(c, dir));
  return `<div style="${style}">${parts.join("")}</div>`;
}

function page(widget) {
  const [w, h] = FAMILY_SIZE[family] || FAMILY_SIZE.small;
  let bg = "transparent";
  if (widget.backgroundGradient) {
    const g = widget.backgroundGradient;
    bg = `linear-gradient(180deg,${g.colors.map((c, i) => css(c) + " " + ((g.locations[i] || 0) * 100) + "%").join(",")})`;
  } else if (widget.backgroundColor) bg = css(widget.backgroundColor);
  const inner = render(Object.assign({}, widget, { kind: "stack", backgroundColor: null, backgroundGradient: null }), null);
  return `<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;background:transparent}
#w{width:${w}px;height:${h}px;border-radius:22px;overflow:hidden;background:${bg};display:flex;flex-direction:column}
#w>div{flex:1 1 0;align-self:stretch}
i,b,span{font-style:normal;font-weight:inherit}
</style></head><body><div id="w">${inner}</div></body></html>`;
}

(async () => {
  const code = fs.readFileSync(scriptPath, "utf8");
  const wrapped = "(async () => {\n" + code + "\n})()";
  vm.createContext(sandbox);
  await vm.runInContext(wrapped, sandbox, { filename: scriptPath });
  if (!captured) {
    console.error("脚本跑完了，但没有交出小组件（Script.setWidget 没被调用）");
    process.exit(1);
  }
  const html = page(captured);
  if (out) fs.writeFileSync(out, html);
  else process.stdout.write(html);
  fs.rmSync(tmpRoot, { recursive: true, force: true });
})().catch((e) => {
  console.error("脚本在模拟器里出错了：", e && e.stack ? e.stack : e);
  process.exit(1);
});
