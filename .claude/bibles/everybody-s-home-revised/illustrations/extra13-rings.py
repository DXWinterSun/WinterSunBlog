#!/usr/bin/env python3
"""《Everybody's Home》求婚那篇的插图：四枚戒指。
她的两枚叠起来是一轮满月；他们各自那枚，是其中的一半（上弦 / 下弦）。
内圈刻字：SAM BELL · SARANG。"""
import math, random

W, H = 1000, 620

def craters(cx, cy, r, n, seed):
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        while True:
            a = rnd.uniform(0, math.tau); d = rnd.uniform(0, r * .80)
            x, y = cx + d * math.cos(a), cy + d * math.sin(a)
            if (x - cx) ** 2 + (y - cy) ** 2 < (r * .82) ** 2:
                break
        cr = rnd.uniform(r * .06, r * .18); o = rnd.uniform(.12, .28)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{cr:.1f}" fill="#8ea3bf" opacity="{o:.2f}"/>'
                   f'<circle cx="{x-cr*.2:.1f}" cy="{y-cr*.2:.1f}" r="{cr*.78:.1f}" fill="#fbfdff" opacity="{o*.55:.2f}"/>')
    return "".join(out)

def moon(cx, cy, r, phase, seed):
    """phase: 'full' 满月 / 'L' 左半亮 / 'R' 右半亮。整颗都是圆的，只是明暗不同。"""
    g = f'<circle cx="{cx}" cy="{cy+r*.16:.1f}" r="{r*1.12:.1f}" fill="#04070e" opacity=".5" filter="url(#blur)"/>'
    g += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#stone)"/>'
    g += craters(cx, cy, r, 12, seed)
    if phase != 'full':
        cid = f"dk{phase}{int(cx)}{int(cy)}"
        d = (f'M{cx} {cy-r} A{r} {r} 0 0 1 {cx} {cy+r} Z' if phase == 'L'
             else f'M{cx} {cy-r} A{r} {r} 0 0 0 {cx} {cy+r} Z')
        g += (f'<clipPath id="{cid}"><path d="{d}"/></clipPath>'
              f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#1b2740" opacity=".82" clip-path="url(#{cid})"/>'
              f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#2b3a56" stroke-width="2.6" '
              f'opacity=".5" clip-path="url(#{cid})"/>')
    g += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#cfdcec" stroke-width="1.3" opacity=".8"/>'
    g += (f'<ellipse cx="{cx-r*.34:.1f}" cy="{cy-r*.42:.1f}" rx="{r*.30:.1f}" ry="{r*.18:.1f}" '
          f'fill="#ffffff" opacity=".5" transform="rotate(-28 {cx-r*.34:.1f} {cy-r*.42:.1f})"/>')
    # 四爪
    g += "".join(
        f'<circle cx="{cx+r*0.96*math.cos(math.radians(a)):.1f}" cy="{cy+r*0.96*math.sin(math.radians(a)):.1f}" '
        f'r="{r*.11:.1f}" fill="url(#metal)" stroke="#0a1120" stroke-width=".8" opacity=".95"/>'
        for a in (40, 140, 220, 320))
    return g

def band(cx, cy, R, w):
    return (f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="url(#metal)" stroke-width="{w}"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{R+w/2:.1f}" fill="none" stroke="#0a1120" stroke-width="1.2" opacity=".6"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{R-w/2:.1f}" fill="none" stroke="#0a1120" stroke-width="1.2" opacity=".5"/>'
            f'<path d="M{cx-R*.78:.1f} {cy-R*.62:.1f} A{R} {R} 0 0 1 {cx+R*.26:.1f} {cy-R*.97:.1f}" '
            f'fill="none" stroke="#ffffff" stroke-width="{w*.30:.1f}" stroke-linecap="round" opacity=".6"/>'
            f'<path d="M{cx+R*.74:.1f} {cy+R*.66:.1f} A{R} {R} 0 0 1 {cx+R*.18:.1f} {cy+R*.98:.1f}" '
            f'fill="none" stroke="#ffffff" stroke-width="{w*.17:.1f}" stroke-linecap="round" opacity=".28"/>')

def ring(cx, cy, R, w, phase, seed, double=False, engrave=None):
    g = f'<ellipse cx="{cx+8}" cy="{cy+15}" rx="{R+w}" ry="{R*.92:.1f}" fill="#03060d" opacity=".52" filter="url(#blur)"/>'
    if double:
        g += band(cx, cy, R - w * .60, w * .88)
        g += band(cx, cy, R + w * .60, w * .88)
        g += f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="#46566e" stroke-width="1.6" opacity=".9"/>'
        inner = R - w * 1.10
    else:
        g += band(cx, cy, R, w)
        inner = R - w * .55
    # 内壁（俯视时看见的是对侧内壁，所以只在下半圈显出来）
    iw = inner - 9
    g += (f'<circle cx="{cx}" cy="{cy}" r="{iw:.1f}" fill="none" stroke="url(#wall)" stroke-width="17"/>')
    if engrave:
        eid = f"eng{int(cx)}"
        g += (f'<path id="{eid}" d="M{cx-iw:.1f} {cy} A{iw:.1f} {iw:.1f} 0 0 0 {cx+iw:.1f} {cy}" fill="none"/>'
              f'<text font-family="Georgia,serif" font-size="{w*.62:.1f}" letter-spacing="{w*.16:.1f}" '
              f'fill="#eef4fb" opacity=".82" font-weight="600">'
              f'<textPath href="#{eid}" startOffset="50%" text-anchor="middle">{engrave}</textPath></text>')
    g += moon(cx, cy - R - (w * .55 if not double else w * .55), R * 0.40, phase, seed)
    return g

svg = f'''<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="四枚戒指摊在深色绒布上。中间那对叠在一起，宝石是一轮满月；两侧各一枚，宝石各是半轮月亮。内圈刻着 SAM BELL · SARANG">
  <defs>
    <radialGradient id="cloth" cx="36%" cy="30%" r="82%">
      <stop offset="0%" stop-color="#22314f"/>
      <stop offset="55%" stop-color="#151f36"/>
      <stop offset="100%" stop-color="#080c16"/>
    </radialGradient>
    <linearGradient id="metal" x1="0.1" y1="0" x2="0.9" y2="1">
      <stop offset="0%" stop-color="#f4f8fc"/><stop offset="20%" stop-color="#bcc9d9"/>
      <stop offset="45%" stop-color="#7d8ca1"/><stop offset="66%" stop-color="#e3eaf3"/>
      <stop offset="100%" stop-color="#8b9aaf"/>
    </linearGradient>
    <linearGradient id="wall" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#3a4counterfeit" stop-opacity="0"/>
      <stop offset="42%" stop-color="#39465c" stop-opacity="0"/>
      <stop offset="72%" stop-color="#5e6f88" stop-opacity=".85"/>
      <stop offset="100%" stop-color="#8fa0b8" stop-opacity=".95"/>
    </linearGradient>
    <radialGradient id="stone" cx="34%" cy="28%" r="82%">
      <stop offset="0%" stop-color="#ffffff"/><stop offset="42%" stop-color="#e6eef7"/>
      <stop offset="78%" stop-color="#bbc9dd"/><stop offset="100%" stop-color="#94a6bf"/>
    </radialGradient>
    <filter id="blur" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="9"/></filter>
    <radialGradient id="vig" cx="46%" cy="44%" r="70%">
      <stop offset="0%" stop-color="#04070e" stop-opacity="0"/>
      <stop offset="70%" stop-color="#04070e" stop-opacity="0.14"/>
      <stop offset="100%" stop-color="#04070e" stop-opacity="0.68"/>
    </radialGradient>
  </defs>

  <rect width="{W}" height="{H}" fill="url(#cloth)"/>
  <g opacity=".012">
    {''.join(f'<path d="M{-320+i*46} {H} L{i*46} 0" stroke="#cfe0f5" stroke-width="20"/>' for i in range(34))}
  </g>
  <ellipse cx="300" cy="150" rx="520" ry="330" fill="#8fb4dd" opacity=".055"
           transform="rotate(-24 300 150)" filter="url(#blur)"/>

  <!-- 他的：上弦（右半亮） -->
  {ring(766, 172, 72, 15, 'R', 7)}
  <!-- 他的：下弦（左半亮） -->
  {ring(806, 424, 72, 15, 'L', 6)}

  <!-- 她的：两枚叠在一起，合成满月 -->
  {ring(330, 322, 128, 26, 'full', 5, double=True, engrave='SAM BELL &#183; SARANG')}

  <rect width="{W}" height="{H}" fill="url(#vig)"/>
</svg>
'''
svg = svg.replace('<stop offset="0%" stop-color="#3a4counterfeit" stop-opacity="0"/>\n      ', '')
open("rings.svg", "w", encoding="utf-8").write(svg)
print("wrote rings.svg", len(svg), "chars")
