# Scriptable 小组件模拟器

不用 iPhone，也能看见桌面小组件长什么样——给 Winter 出效果图、改小组件之前先自查都用它。

| 文件 | 干什么 |
|---|---|
| `sim.js` | 把一份 Scriptable 脚本放进「假 Scriptable」里跑，记下它搭的 ListWidget / stack 树，翻成一张 HTML（flex 近似 SwiftUI 的排法） |
| `shot.js` | 把那张 HTML 截成透明圆角的 PNG |
| `compose.py` | 把 PNG 贴到她发来的桌面截图上（可抹掉原来的小组件、换掉下面的 app 名、画叠放的翻页小圆点） |

```bash
export NODE_PATH=/opt/node22/lib/node_modules          # 全局装的 playwright
node tools/widget-sim/sim.js sam/widget/sam-today.js --family medium --data sam/lines.json -o /tmp/q.html
node tools/widget-sim/shot.js /tmp/q.html /tmp/q.png 3
```

- `--data`：脚本里所有 `Request` 一律换成这份本地文件（模拟器不联网）。
- `--param`：小组件的 Parameter。`--dark`：深色模式。`--size 宽x高`：别的机型。
- 默认尺寸是在 Winter 那台 iPhone 上量的（截图 1206 宽、3 倍屏）：小 163、中 350×163、大 350×363（pt）。
- 字体是近似：SF Pro → Inter，苹方 → Noto Sans SC，Georgia → Gelasio。容器里没有就先装：
  ```bash
  mkdir -p ~/.fonts && cd ~/.fonts
  for f in notosanssc/NotoSansSC%5Bwght%5D.ttf gelasio/Gelasio%5Bwght%5D.ttf gelasio/Gelasio-Italic%5Bwght%5D.ttf inter/Inter%5Bopsz,wght%5D.ttf; do
    curl -sSLO "https://raw.githubusercontent.com/google/fonts/main/ofl/$f"; done; fc-cache -f
  ```
- 假 API 只实现了用得到的那些。**脚本调了 Scriptable 里不存在的方法，模拟器照样报错**——这正好在上手机前
  把拼错的 API 拦下来。真机上要用新的 API，先在 `sim.js` 里照官方文档补上。
- 2026-10-03 校过一次：拿 `sam-today.js` 的大号跟她真机截图并排比，排版、换行、字号几乎一致，
  只有行距真机略紧（已把行高调到 1.2）。
