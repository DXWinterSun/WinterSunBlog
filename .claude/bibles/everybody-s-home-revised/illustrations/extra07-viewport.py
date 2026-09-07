#!/usr/bin/env python3
"""《The Third Cup》舷窗一幕的插画 SVG —— 只画窗，不画人。"""
import random

random.seed(20260821)

W, H = 1000, 620
CX, CY, R = 500, 300, 268


def stars(n, rmin, rmax, omin, omax):
    out = []
    for _ in range(n):
        while True:
            x = random.uniform(CX - R, CX + R)
            y = random.uniform(CY - R, CY + R)
            if (x - CX) ** 2 + (y - CY) ** 2 < (R - 8) ** 2:
                break
        r = random.uniform(rmin, rmax)
        o = random.uniform(omin, omax)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="#eaf2ff" opacity="{o:.2f}"/>')
    return "\n      ".join(out)


def tinted(n):
    """几颗带色温的星，让星空不至于死白。"""
    out = []
    for _ in range(n):
        while True:
            x = random.uniform(CX - R, CX + R)
            y = random.uniform(CY - R, CY + R)
            if (x - CX) ** 2 + (y - CY) ** 2 < (R - 14) ** 2:
                break
        c = random.choice(["#ffd9b0", "#ffc9a0", "#bcd4ff", "#a8c6ff", "#ffe7c8"])
        r = random.uniform(1.0, 2.0)
        o = random.uniform(.45, .9)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="{c}" opacity="{o:.2f}"/>')
    return "\n      ".join(out)


def bright(x, y, s, o):
    return (f'<g opacity="{o}">'
            f'<circle cx="{x}" cy="{y}" r="{s*0.9:.2f}" fill="#ffffff"/>'
            f'<circle cx="{x}" cy="{y}" r="{s*3.2:.2f}" fill="#cfe3ff" opacity="0.16"/>'
            f'<path d="M{x-s*6:.1f} {y} H{x+s*6:.1f} M{x} {y-s*6:.1f} V{y+s*6:.1f}" '
            f'stroke="#dceaff" stroke-width="{s*0.45:.2f}" stroke-linecap="round" opacity="0.6"/>'
            f'<path d="M{x-s*3:.1f} {y-s*3:.1f} L{x+s*3:.1f} {y+s*3:.1f} '
            f'M{x-s*3:.1f} {y+s*3:.1f} L{x+s*3:.1f} {y-s*3:.1f}" '
            f'stroke="#dceaff" stroke-width="{s*0.22:.2f}" stroke-linecap="round" opacity="0.3"/>'
            f'</g>')


brights = "\n      ".join([
    bright(360, 158, 2.8, .95),
    bright(602, 392, 2.1, .8),
    bright(428, 404, 1.8, .72),
    bright(548, 128, 1.6, .68),
    bright(300, 322, 1.5, .62),
    bright(688, 262, 1.5, .6),
    bright(468, 246, 1.2, .5),
])

EX, EY, ER = 648, 200, 30

svg = f'''<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="飞船客舱的圆形舷窗，窗外是满天星斗和远处一颗蓝色的地球">
  <defs>
    <radialGradient id="space" cx="54%" cy="40%" r="76%">
      <stop offset="0%" stop-color="#18274a"/>
      <stop offset="52%" stop-color="#0b1327"/>
      <stop offset="100%" stop-color="#04070e"/>
    </radialGradient>
    <radialGradient id="milky" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#b6d4ee" stop-opacity="0.26"/>
      <stop offset="55%" stop-color="#7eb0d5" stop-opacity="0.10"/>
      <stop offset="100%" stop-color="#7eb0d5" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="milky2" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#e0d0f0" stop-opacity="0.16"/>
      <stop offset="100%" stop-color="#e0d0f0" stop-opacity="0"/>
    </radialGradient>
    <filter id="soft" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="30"/>
    </filter>
    <filter id="soft2" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="14"/>
    </filter>
    <radialGradient id="earth" cx="32%" cy="30%" r="80%">
      <stop offset="0%" stop-color="#a8dcf6"/>
      <stop offset="40%" stop-color="#4390cd"/>
      <stop offset="80%" stop-color="#1d4a7e"/>
      <stop offset="100%" stop-color="#0b1e3a"/>
    </radialGradient>
    <radialGradient id="earthglow" cx="50%" cy="50%" r="50%">
      <stop offset="48%" stop-color="#7eb0d5" stop-opacity="0.38"/>
      <stop offset="100%" stop-color="#7eb0d5" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="frame" x1="0.1" y1="0" x2="0.9" y2="1">
      <stop offset="0%" stop-color="#4b5f7e"/>
      <stop offset="30%" stop-color="#28344b"/>
      <stop offset="62%" stop-color="#1a2334"/>
      <stop offset="100%" stop-color="#54688a"/>
    </linearGradient>
    <linearGradient id="frameIn" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#0a1120"/>
      <stop offset="100%" stop-color="#2a3852"/>
    </linearGradient>
    <linearGradient id="mat" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#16223c"/>
      <stop offset="100%" stop-color="#070b14"/>
    </linearGradient>
    <radialGradient id="lamp" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#ffcb92" stop-opacity="0.34"/>
      <stop offset="100%" stop-color="#ffcb92" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="glass" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#cfe6ff" stop-opacity="0.16"/>
      <stop offset="45%" stop-color="#cfe6ff" stop-opacity="0.02"/>
      <stop offset="100%" stop-color="#cfe6ff" stop-opacity="0"/>
    </linearGradient>
    <radialGradient id="vig" cx="50%" cy="48%" r="62%">
      <stop offset="0%" stop-color="#04070e" stop-opacity="0"/>
      <stop offset="70%" stop-color="#04070e" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="#04070e" stop-opacity="0.72"/>
    </radialGradient>
    <clipPath id="port"><circle cx="{CX}" cy="{CY}" r="{R}"/></clipPath>
  </defs>

  <!-- 舱壁 -->
  <rect width="{W}" height="{H}" fill="#070b14"/>
  <rect x="-200" y="-100" width="1000" height="900" fill="url(#lamp)" opacity="0.95"/>
  <rect x="400" y="200" width="900" height="800" fill="url(#lamp)" opacity="0.35"/>

  <!-- 舱壁上的一点结构线 -->
  <g stroke="#1d2b44" stroke-width="1.2" opacity="0.55" fill="none">
    <path d="M0 96 H188"/>
    <path d="M812 96 H1000"/>
    <path d="M0 512 H150"/>
    <path d="M850 512 H1000"/>
  </g>

  <!-- 舷窗 -->
  <g clip-path="url(#port)">
    <circle cx="{CX}" cy="{CY}" r="{R}" fill="url(#space)"/>
    <ellipse cx="{CX-40}" cy="{CY+30}" rx="{R*1.25:.0f}" ry="{R*0.30:.0f}"
             fill="url(#milky)" filter="url(#soft)" transform="rotate(-28 {CX-40} {CY+30})"/>
    <ellipse cx="{CX+70}" cy="{CY-90}" rx="{R*0.55:.0f}" ry="{R*0.30:.0f}"
             fill="url(#milky2)" filter="url(#soft)" transform="rotate(-40 {CX+70} {CY-90})"/>
    <g>
      {stars(230, 0.4, 1.4, .22, .8)}
    </g>
    <g>
      {stars(40, 1.4, 2.2, .5, 1)}
    </g>
    <g>
      {tinted(22)}
    </g>
    {brights}

    <!-- 地球 -->
    <circle cx="{EX}" cy="{EY}" r="{ER*2.6:.0f}" fill="url(#earthglow)"/>
    <circle cx="{EX}" cy="{EY}" r="{ER}" fill="url(#earth)"/>
    <g clip-path="none">
      <path d="M{EX-19} {EY-16} q10 -7 20 -2 q8 4 3 10 q-7 9 -18 7 q-10 -2 -5 -15 Z" fill="#7fb08a" opacity="0.48"/>
      <path d="M{EX+5} {EY+10} q11 -4 15 4 q4 8 -6 10 q-12 2 -13 -7 q-1 -6 4 -7 Z" fill="#7fb08a" opacity="0.4"/>
      <path d="M{EX-24} {EY+8} q7 -3 11 3 q3 6 -4 8 q-8 1 -9 -5 Z" fill="#7fb08a" opacity="0.3"/>
      <ellipse cx="{EX-10}" cy="{EY+9}" rx="16" ry="7" fill="#eaf4ff" opacity="0.30" transform="rotate(-18 {EX-10} {EY+9})"/>
      <ellipse cx="{EX+10}" cy="{EY-10}" rx="12" ry="5" fill="#eaf4ff" opacity="0.26" transform="rotate(14 {EX+10} {EY-10})"/>
      <ellipse cx="{EX+2}" cy="{EY+20}" rx="13" ry="5" fill="#eaf4ff" opacity="0.2" transform="rotate(-6 {EX+2} {EY+20})"/>
    </g>
    <circle cx="{EX}" cy="{EY}" r="{ER}" fill="none" stroke="#c8e6f8" stroke-width="0.9" opacity="0.55"/>
    <circle cx="{EX}" cy="{EY}" r="{ER+2.5}" fill="none" stroke="#8fc4e6" stroke-width="2.4" opacity="0.22" filter="url(#soft2)"/>

    <!-- 玻璃上的一层斜反光 -->
    <path d="M{CX-R} {CY-30} L{CX-30} {CY-R} L{CX+70} {CY-R} L{CX-R} {CY+160} Z"
          fill="url(#glass)" opacity="0.85" filter="url(#soft)"/>
    <!-- 内层暖光在玻璃上的一点回照 -->
    <ellipse cx="{CX-170}" cy="{CY+150}" rx="150" ry="80"
             fill="#ffcb92" opacity="0.05" filter="url(#soft)" transform="rotate(-24 {CX-170} {CY+150})"/>
  </g>

  <!-- 窗框 -->
  <circle cx="{CX}" cy="{CY}" r="{R+2}" fill="none" stroke="url(#frameIn)" stroke-width="6" opacity="0.95"/>
  <circle cx="{CX}" cy="{CY}" r="{R+13}" fill="none" stroke="url(#frame)" stroke-width="22"/>
  <circle cx="{CX}" cy="{CY}" r="{R+24.5}" fill="none" stroke="#0a1120" stroke-width="3" opacity="0.9"/>
  <circle cx="{CX}" cy="{CY}" r="{R+31}" fill="none" stroke="#111a2c" stroke-width="10" opacity="0.75"/>
  <circle cx="{CX}" cy="{CY}" r="{R+5}" fill="none" stroke="#8fbfe0" stroke-width="1" opacity="0.18"/>

  <!-- 窗框上的螺栓 -->
  <g opacity="0.9">
'''

bolts = []
import math
for i in range(16):
    a = math.radians(i * 22.5 - 90)
    bx = CX + (R + 13) * math.cos(a)
    by = CY + (R + 13) * math.sin(a)
    lit = 0.9 if math.cos(a - math.radians(-135)) > 0.2 else 0.45
    bolts.append(
        f'    <circle cx="{bx:.1f}" cy="{by:.1f}" r="4.2" fill="#6d87a8" opacity="{lit}"/>'
        f'<circle cx="{bx-1:.1f}" cy="{by-1:.1f}" r="1.6" fill="#c3d6ec" opacity="{lit*0.7:.2f}"/>'
    )
svg += "\n".join(bolts) + '''
  </g>

  <!-- 四周的压暗，让窗浮出来 -->
  <rect width="{W}" height="{H}" fill="url(#vig)"/>

  <!-- 悬浮的微尘 -->
  <g fill="#cfe3f5">
    <circle cx="248" cy="470" r="1.6" opacity="0.34"/>
    <circle cx="742" cy="418" r="1.3" opacity="0.28"/>
    <circle cx="612" cy="506" r="1.9" opacity="0.3"/>
    <circle cx="352" cy="392" r="1.1" opacity="0.22"/>
    <circle cx="856" cy="486" r="1.5" opacity="0.26"/>
    <circle cx="130" cy="426" r="1.2" opacity="0.2"/>
    <circle cx="470" cy="540" r="1.4" opacity="0.24"/>
  </g>
</svg>
'''

open("viewport.svg", "w", encoding="utf-8").write(svg)
print("wrote viewport.svg", len(svg), "chars")
