#!/usr/bin/env node
/* 把 sim.js 吐出来的 HTML 截成透明底 PNG（圆角外面是透明的，方便贴到桌面截图上）。
   node tools/widget-sim/shot.js in.html out.png [倍率，默认 3]
   倍率 2.36 ≈ Winter 发来的那种 920 宽桌面截图里一个 pt 有多少像素。 */
"use strict";
const { chromium } = require("playwright");
(async () => {
  const [inp, out, scale] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ deviceScaleFactor: parseFloat(scale || "3") });
  await page.goto("file://" + require("path").resolve(inp));
  await page.evaluate(() => document.fonts.ready);
  await page.locator("#w").screenshot({ path: out, omitBackground: true });
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
