# -*- coding: utf-8 -*-
"""番外 35「“都可以”不是一种饮料」里那张会动的小手绘：他三只手编的那条歪辫子。

用法：python3 make_braid.py > braid.html   （输出整块 <div class="c-braid-figure">…</div>，原样贴进正文）

画的是正文里写的样子：银白三股辫，三股各带一点不同的光（银 / 冰蓝 / 被暖黄恒星照到的那一点暖）；
手劲没准——左边那几瓣胖、右边那几瓣瘦，松紧不一；半截处莫名其妙拐个弯；末梢支棱一小撮蓬松的毛。
动效：整条辫子轻轻晃，一道光从上往下扫过，三股轮流微微亮一下，末梢那撮毛晃，几粒小星闪。
SVG 里所有 id 用 br35 前缀，别跟同一页别的图撞。
"""
import math, random

random.seed(35)
W, H = 300, 360
TOP = (150.0, 52.0)


def center(t):
    """辫子中线，t 从 0（发根）到 1（末梢）。半截处往右拐个弯，再往回收一点。"""
    y = TOP[1] + t * 248
    bend = 42 / (1 + math.exp(-(t - 0.5) * 13))           # 拐弯
    back = -9 / (1 + math.exp(-(t - 0.85) * 18))           # 末梢往回收一点
    x = TOP[0] - 14 + bend + back + 2.5 * math.sin(t * 7)  # 编得不直
    return x, y


def tangent(t):
    a, b = center(max(0, t - 0.004)), center(min(1, t + 0.004))
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy)
    return dx / n, dy / n


STRANDS = [  # (亮, 中, 暗, 光晕色)
    ("#f6f8fb", "#c9d2dc", "#5f6b7a", "#eef4ff"),   # 银
    ("#e6f4fd", "#b6cfe0", "#4d6a85", "#9fd4ff"),   # 冰蓝
    ("#fbf2e2", "#d8cdb9", "#7a6a52", "#f3c96a"),   # 被恒星照暖的那一股
]

# 每一瓣：位置 t、左右、胖瘦——手劲没准，所以间距和大小都不齐
lobes = []
t = 0.0
i = 0
while t < 0.93:
    side = -1 if i % 2 == 0 else 1
    width = (1.0 - 0.38 * t)                               # 往下越编越细
    width *= 1.18 if side < 0 else 0.86                    # 左胖右瘦
    width *= random.uniform(0.9, 1.12)
    lobes.append((t, side, width, i % 3))
    t += random.uniform(0.050, 0.068)                      # 这一下松，那一下紧
    i += 1
END_T = t


def leaf(t, side, width):
    cx, cy = center(t)
    ux, uy = tangent(t)               # 沿辫子往下
    vx, vy = -uy, ux                  # 横向（朝右）
    off = side * 9.0 * width
    px, py = cx + vx * off, cy + vy * off
    # 长轴：从外上方斜着压到中间偏下
    ax, ay = (-side) * 0.78 * vx + 0.62 * ux, (-side) * 0.78 * vy + 0.62 * uy
    n = math.hypot(ax, ay); ax, ay = ax / n, ay / n
    bx, by = -ay, ax
    L, Wd = 25 * width, 11.5 * width
    pts = []
    for k in range(0, 41):
        a = -1 + k / 20 if k <= 20 else 1 - (k - 20) / 20
        sgn = 1 if k <= 20 else -1
        b = sgn * Wd * (1 - a * a) ** 0.62
        pts.append((px + ax * a * L + bx * b, py + ay * a * L + by * b))
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + "Z"
    outer = (px - ax * L, py - ay * L)
    inner = (px + ax * L, py + ay * L)
    hairs = []
    for bo in (-0.45, 0.0, 0.42):
        s = [(px + ax * a * L * 0.86 + bx * bo * Wd * (1 - a * a) ** 0.6,
              py + ay * a * L * 0.86 + by * bo * Wd * (1 - a * a) ** 0.6) for a in (-0.9, -0.3, 0.3, 0.9)]
        hairs.append("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in s))
    return d, outer, inner, hairs


out = []
P = out.append
P('<div class="c-braid-figure" role="img" aria-label="一条银白的三股辫，左边胖右边瘦，半截处拐了个弯，末梢支棱着一小撮蓬松的毛；三股各自微微发光" style="margin:2.4rem auto;max-width:260px;">')
P(f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;display:block;">')
P('  <defs>')
P('    <radialGradient id="br35sun" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#f3c96a" stop-opacity=".30"/><stop offset="1" stop-color="#f3c96a" stop-opacity="0"/></radialGradient>')
P('    <linearGradient id="br35sweep" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>')
P('    <linearGradient id="br35root" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#dfe6ee" stop-opacity="0"/><stop offset="1" stop-color="#dfe6ee" stop-opacity=".85"/></linearGradient>')
P('    <linearGradient id="br35rootink" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3b4452" stop-opacity="0"/><stop offset="1" stop-color="#3b4452" stop-opacity=".45"/></linearGradient>')
for s, (hi, mid, lo, glow) in enumerate(STRANDS):
    P(f'    <filter id="br35blur{s}" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="4"/></filter>')
shapes = []
for j, (t, side, width, s) in enumerate(lobes):
    d, outer, inner, hairs = leaf(t, side, width)
    hi, mid, lo, glow = STRANDS[s]
    P(f'    <linearGradient id="br35g{j}" gradientUnits="userSpaceOnUse" x1="{outer[0]:.1f}" y1="{outer[1]:.1f}" x2="{inner[0]:.1f}" y2="{inner[1]:.1f}">'
      f'<stop offset="0" stop-color="{lo}"/><stop offset=".3" stop-color="{mid}"/><stop offset=".62" stop-color="{hi}"/><stop offset="1" stop-color="{lo}"/></linearGradient>')
    shapes.append((j, d, hairs, s))
P('    <clipPath id="br35clip">' + "".join(f'<path d="{d}"/>' for _, d, _, _ in shapes) + '</clipPath>')
P('  </defs>')

# 背景：那颗暖黄的恒星的光 + 几粒远星
P('  <circle cx="118" cy="120" r="96" fill="url(#br35sun)"/>')
for _ in range(16):
    x, y = random.uniform(8, W - 8), random.uniform(8, H - 8)
    if abs(x - 160) < 45 and 30 < y < 310:
        continue
    o = random.uniform(.18, .45)
    P(f'  <circle cx="{x:.0f}" cy="{y:.0f}" r="{random.choice([.6, .8, 1.0])}" fill="#fff" opacity="{o:.2f}">'
      f'<animate attributeName="opacity" values="{o:.2f};{o/4:.2f};{o:.2f}" dur="{random.uniform(2.6, 5.2):.1f}s" repeatCount="indefinite"/></circle>')

# 整条辫子轻轻晃（以发根为轴）
P(f'  <g><animateTransform attributeName="transform" type="rotate" values="-1.4 {TOP[0]} {TOP[1]};1.4 {TOP[0]} {TOP[1]};-1.4 {TOP[0]} {TOP[1]}" dur="7s" repeatCount="indefinite"/>')

# 发根：一把头发收拢进辫子
for k in range(13):
    x0 = 92 + k * 9.5 + random.uniform(-2, 2)
    d = f"M{x0:.1f},4 Q{(x0 + TOP[0]) / 2 + random.uniform(-6, 6):.1f},{28 + random.uniform(-4, 4):.1f} {TOP[0] + random.uniform(-5, 5):.1f},{TOP[1] + 4:.1f}"
    sw = random.uniform(1.6, 2.6)
    P(f'    <path d="{d}" stroke="url(#br35rootink)" stroke-width="{sw + 1.2:.1f}" fill="none" stroke-linecap="round"/>')  # 衬线：浅色主题下也看得见
    P(f'    <path d="{d}" stroke="url(#br35root)" stroke-width="{sw:.1f}" fill="none" stroke-linecap="round"/>')

# 三股各自的光晕，轮流亮
for s, (hi, mid, lo, glow) in enumerate(STRANDS):
    paths = "".join(f'<path d="{d}"/>' for j, d, _, ss in shapes if ss == s)
    P(f'    <g fill="{glow}" filter="url(#br35blur{s})" opacity=".18">{paths}'
      f'<animate attributeName="opacity" values=".12;.5;.12" dur="4.5s" begin="{s * 1.5:.1f}s" repeatCount="indefinite"/></g>')

# 每一瓣 + 发丝纹路（从下往上画，上面一瓣压住下面一瓣）
for j, d, hairs, s in reversed(shapes):
    P(f'    <path d="{d}" fill="url(#br35g{j})" stroke="#2a2f3a" stroke-opacity=".35" stroke-width=".7"/>')
    P('    <path d="' + " ".join(hairs) + '" stroke="#fff" stroke-opacity=".38" stroke-width=".55" fill="none" stroke-linecap="round"/>')

# 一道光从上往下扫过
P(f'    <g clip-path="url(#br35clip)"><rect x="0" y="-140" width="{W}" height="110" fill="url(#br35sweep)">'
  f'<animate attributeName="y" values="-140;{H};{H}" keyTimes="0;.55;1" dur="5.5s" repeatCount="indefinite"/></rect></g>')

# 末梢那一小撮蓬松的毛，自己晃
ex, ey = center(END_T - 0.02)
P(f'    <g><animateTransform attributeName="transform" type="rotate" values="-5 {ex:.1f} {ey:.1f};5 {ex:.1f} {ey:.1f};-5 {ex:.1f} {ey:.1f}" dur="3.6s" repeatCount="indefinite"/>')
for k in range(22):
    ang = math.radians(90 + random.uniform(-48, 48))
    ln = random.uniform(20, 44)
    x2, y2 = ex + math.cos(ang) * ln, ey + math.sin(ang) * ln
    mx, my = ex + math.cos(ang) * ln * .5 + random.uniform(-5, 5), ey + math.sin(ang) * ln * .5
    col = STRANDS[k % 3][1]
    d = f"M{ex:.1f},{ey:.1f} Q{mx:.1f},{my:.1f} {x2:.1f},{y2:.1f}"
    sw = random.uniform(1.1, 2.0)
    P(f'      <path d="{d}" stroke="#3b4452" stroke-opacity=".5" stroke-width="{sw + 1.1:.1f}" fill="none" stroke-linecap="round"/>')  # 衬线
    P(f'      <path d="{d}" stroke="{col}" stroke-opacity="{random.uniform(.8, 1):.2f}" stroke-width="{sw:.1f}" fill="none" stroke-linecap="round"/>')
P('    </g>')
P('  </g>')

# 几粒小星沿着辫子闪
for k in range(5):
    t = 0.12 + k * 0.18 + random.uniform(-0.04, 0.04)
    x, y = center(t)
    x += random.choice([-1, 1]) * random.uniform(16, 26)
    r = random.uniform(3.2, 4.6)
    P(f'  <path d="M{x:.1f},{y - r:.1f} L{x + r * .22:.1f},{y - r * .22:.1f} L{x + r:.1f},{y:.1f} L{x + r * .22:.1f},{y + r * .22:.1f} '
      f'L{x:.1f},{y + r:.1f} L{x - r * .22:.1f},{y + r * .22:.1f} L{x - r:.1f},{y:.1f} L{x - r * .22:.1f},{y - r * .22:.1f}Z" fill="#fff" opacity="0">'
      f'<animate attributeName="opacity" values="0;.85;0;0" keyTimes="0;.15;.35;1" dur="{random.uniform(3.8, 5.6):.1f}s" begin="{k * 0.9:.1f}s" repeatCount="indefinite"/></path>')

P('</svg>')
P('<div style="text-align:center;font-size:.72rem;letter-spacing:.22em;opacity:.5;margin-top:.7rem;font-family:system-ui,sans-serif;">三只手 · 三股 · 艺术体</div>')
P('</div>')
print("\n".join(out))
