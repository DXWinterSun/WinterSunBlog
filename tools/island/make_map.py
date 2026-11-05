#!/usr/bin/env python3
"""冬的岛屿 · 底图生成器（2026-11-05 第三批小家时画的大图，1600 × 1100）。

    python3 tools/island/make_map.py          # 重新生成 _includes/island-map.html

为什么用脚本：岛上有几十棵松树、橄榄树、仙人掌、羊，一棵棵手写坐标太累，也不好改。
这里每个区域一段，改哪一块就改哪一段，跑一下就重画。树的位置用固定的随机种子撒，所以每次结果一样。
颜色写死（这张图当一幅画，不随「换个心情」变）。房子不画在这里，由岛图页按 _data/island.yml 叠上去。

区域（跟 _data/island.yml 的 region、写小家时的 zone 对应）：
  北边的雪山与雪原（Five & Six 在山顶）· 西北的松林 · 东北的英格兰高地 · 西边的红岩荒原 · 西南的海滩（Leonard）
  中间的小镇和住宅区 · 南边夏天的河（Trent 的拖车、水上乐园、球场）· 河口（Rob 的 El Rancho）
  东边的沙滩和悬崖（Zaphod 的飞船）· 东南的地中海海岸
"""
import random
from pathlib import Path

W, H = 1600, 1100
OUT = Path(__file__).resolve().parents[2] / "_includes" / "island-map.html"

ISLE = ("M300 118 C390 66 520 58 630 78 C720 46 840 40 940 66 C1050 46 1160 68 1250 108 "
        "C1350 140 1430 204 1468 292 C1506 376 1478 444 1506 522 C1534 604 1514 684 1484 764 "
        "C1452 852 1398 932 1318 982 C1236 1032 1146 1022 1058 1042 C976 1060 896 1050 816 1052 "
        "C728 1060 640 1042 558 1032 C458 1020 358 998 280 950 C198 898 128 842 108 762 "
        "C88 682 120 620 100 548 C82 470 112 400 120 330 C130 248 200 170 300 118 Z")

RIVER = ("M770 352 C760 410 700 440 690 500 C680 560 640 600 640 670 "
         "C640 740 690 790 750 850 C800 900 842 960 858 1050")


def scatter(seed, box, n, avoid=(), gap=26):
    """在 box=(x0,y0,x1,y1) 里撒 n 个点，彼此至少隔 gap，并避开 avoid 里的圆 (cx,cy,r)。"""
    rnd = random.Random(seed)
    pts, tries = [], 0
    x0, y0, x1, y1 = box
    while len(pts) < n and tries < n * 400:
        tries += 1
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if any((x - cx) ** 2 + (y - cy) ** 2 < r * r for cx, cy, r in avoid):
            continue
        if any((x - px) ** 2 + (y - py) ** 2 < gap * gap for px, py in pts):
            continue
        pts.append((round(x), round(y)))
    return sorted(pts, key=lambda p: p[1])  # 靠后的画在前面的上面


def uses(sym, pts, w, h, jitter=0.18, seed=1):
    rnd = random.Random(seed)
    out = []
    for x, y in pts:
        k = 1 + rnd.uniform(-jitter, jitter)
        ww, hh = round(w * k, 1), round(h * k, 1)
        out.append(f'<use href="#{sym}" x="{x - ww / 2:.1f}" y="{y - hh:.1f}" width="{ww}" height="{hh}"/>')
    return "".join(out)


# 房子在哪儿：读 _data/island.yml（x / y 是百分比），树就不会长在房子上。
# 加了新住户、挪了房子以后，重跑一遍这个脚本，树会自己让开。下面那串是还空着的预留地，也先别种树。
import yaml
_ISLE = yaml.safe_load((Path(__file__).resolve().parents[2] / "_data" / "island.yml").read_text(encoding="utf-8"))
HOUSES = [(r["x"] * W / 100, r["y"] * H / 100) for r in _ISLE["residents"]] + [
    (800, 150), (580, 405), (700, 425), (930, 420), (1050, 405), (560, 300), (1065, 300), (680, 240), (925, 235),
    (240, 205), (370, 190), (480, 260), (200, 320), (460, 370), (320, 400), (200, 430),
    (1110, 200), (1230, 175), (1340, 240), (1130, 310), (1250, 300), (1400, 330), (1180, 420), (1310, 440),
    (150, 640), (270, 620), (400, 590), (200, 730), (330, 720), (460, 690), (240, 500), (430, 500),
    (180, 810), (260, 880), (340, 940),
    (850, 540), (750, 600), (960, 600), (750, 500), (960, 500), (850, 640), (1060, 560), (950, 690),
    (560, 480), (545, 620), (1080, 470), (1090, 660), (1170, 560), (860, 450),
    (700, 770), (560, 840), (640, 900), (980, 800), (1000, 900), (880, 820), (760, 950), (500, 760),
    (930, 1005), (1460, 600), (1340, 470), (1450, 470), (1300, 560), (1390, 650), (1300, 670), (1430, 730),
    (1150, 760), (1270, 780), (1390, 800), (1120, 880), (1240, 880), (1360, 900), (1200, 970),
]
HOUSE_AVOID = [(x, y - 14, 40) for x, y in HOUSES]


def build():
    s = []
    a = s.append
    a("""{%- comment -%}
  🏝️ 冬的岛屿的底图（2026-11-03 第一版；2026-11-05 全岛的人都住进来以后，按 tools/island/make_map.py 画成大图）。
  她挑的「冬天的水彩雪岛」。坐标是 1600 × 1100；房子不画在这里，由 _pages/island/index.html 按 _data/island.yml 的 x / y（百分比）叠上去。
  ⚠️ 别手改这个文件：改 tools/island/make_map.py，再跑一遍。颜色写死，当一幅画。
{%- endcomment -%}
""")
    a(f'<svg class="c-isle__paint" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" '
      'aria-label="冬的岛屿：北边雪山，西北松林，东北英格兰高地，西边红岩荒原，中间小镇，南边夏天的河，东边悬崖和沙滩，东南地中海海岸" '
      'preserveAspectRatio="xMidYMid slice">')
    a("""<defs>
<radialGradient id="isle-sea" cx="50%" cy="50%" r="72%"><stop offset="0" stop-color="#e6f3f9"/><stop offset=".55" stop-color="#c8e4f1"/><stop offset="1" stop-color="#97c6df"/></radialGradient>
<linearGradient id="isle-land" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e6edf2"/><stop offset=".3" stop-color="#eef2f0"/><stop offset=".6" stop-color="#e9efdd"/><stop offset="1" stop-color="#d8e7c4"/></linearGradient>
<filter id="isle-wc" x="-6%" y="-6%" width="112%" height="112%"><feTurbulence type="fractalNoise" baseFrequency=".016" numOctaves="3" seed="11" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="18" xChannelSelector="R" yChannelSelector="G" result="d"/><feGaussianBlur in="d" stdDeviation=".9"/></filter>
<filter id="isle-wc-soft" x="-15%" y="-15%" width="130%" height="130%"><feTurbulence type="fractalNoise" baseFrequency=".024" numOctaves="2" seed="4" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="14" result="d"/><feGaussianBlur in="d" stdDeviation="3.4"/></filter>
<filter id="isle-blur" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="12"/></filter>
<filter id="isle-grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" seed="3"/><feColorMatrix values="0 0 0 0 .35  0 0 0 0 .42  0 0 0 0 .5  0 0 0 .07 0"/></filter>
""")
    a(f'<path id="isle-shape" d="{ISLE}"/>')
    a("""<symbol id="isle-pine" viewBox="0 0 20 28"><path d="M10 1 L18 22 H2 Z" fill="#5f8c8c"/><path d="M10 1 L14.5 12 L11.5 10.5 L10 13 L8.5 10.5 L5.5 12 Z" fill="#ffffff"/><rect x="9" y="22" width="2" height="5" fill="#7b6a58"/></symbol>
<symbol id="isle-fir" viewBox="0 0 20 30"><path d="M10 1 L16 12 H13 L18 21 H2 L7 12 H4 Z" fill="#4f7d77"/><path d="M10 1 L13 7 L10 6 L7 7 Z" fill="#ffffff"/><rect x="9" y="21" width="2" height="7" fill="#6e5d4b"/></symbol>
<symbol id="isle-tree" viewBox="0 0 20 26"><circle cx="10" cy="10" r="9" fill="#9cc79a"/><circle cx="7" cy="8" r="4" fill="#b7d8ad"/><rect x="9" y="17" width="2" height="8" fill="#8a7559"/></symbol>
<symbol id="isle-olive" viewBox="0 0 22 24"><ellipse cx="11" cy="9" rx="10" ry="7.5" fill="#aab58c"/><ellipse cx="8" cy="7" rx="4.5" ry="3" fill="#c3cba6"/><path d="M11 15 C10 18 12 20 10 23" stroke="#8a7559" stroke-width="2" fill="none"/></symbol>
<symbol id="isle-palm" viewBox="0 0 24 30"><path d="M13 29 C12 22 14 15 12 9" stroke="#a5835c" stroke-width="2.2" fill="none"/><path d="M12 9 C7 5 3 7 1 10 M12 9 C16 4 21 5 23 8 M12 9 C9 3 12 1 15 1 M12 9 C16 9 19 12 20 15 M12 9 C8 9 5 12 4 15" stroke="#7fb27a" stroke-width="2.4" fill="none" stroke-linecap="round"/></symbol>
<symbol id="isle-cactus" viewBox="0 0 16 22"><path d="M8 21 V4" stroke="#7fa66a" stroke-width="4" stroke-linecap="round"/><path d="M8 13 H4 V9 M8 11 H12 V7" stroke="#7fa66a" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/></symbol>
<symbol id="isle-sheep" viewBox="0 0 14 10"><ellipse cx="7" cy="5" rx="5.5" ry="3.8" fill="#ffffff" stroke="#c7c2b5" stroke-width=".6"/><circle cx="12" cy="4" r="1.8" fill="#4a4a48"/><path d="M4 8 v2 M9 8 v2" stroke="#4a4a48" stroke-width=".9"/></symbol>
</defs>""")

    # 海
    a(f'<rect width="{W}" height="{H}" fill="url(#isle-sea)"/>')
    waves = [(90, 160), (1460, 90), (80, 1010), (1500, 1010), (40, 520), (1560, 420), (620, 1080), (1120, 1070), (1560, 200), (40, 300)]
    a('<g stroke="#ffffff" stroke-width="2.2" stroke-linecap="round" fill="none" opacity=".55">'
      + "".join(f'<path d="M{x} {y} q14 -8 28 0 q14 8 28 0"/>' for x, y in waves) + "</g>")
    a('<use href="#isle-shape" fill="none" stroke="#e2f2f8" stroke-width="60" filter="url(#isle-blur)" opacity=".9"/>')

    # 岛和沙滩
    a('<g filter="url(#isle-wc)">')
    a('<use href="#isle-shape" fill="url(#isle-land)" stroke="#86b6cd" stroke-width="3.5" stroke-opacity=".7"/>')
    a('<path d="M1470 448 C1494 510 1486 560 1500 620 C1508 670 1494 720 1478 766 C1478 712 1484 670 1478 624 C1470 566 1478 510 1450 462 Z" fill="#f1e2bf"/>')
    a('<path d="M116 736 C130 800 170 860 236 910 C268 934 300 950 336 964 C292 930 252 898 214 860 C178 820 150 782 140 740 Z" fill="#f1e2bf"/>')
    a('<path d="M748 1042 C820 1030 904 1028 990 1038 C934 1054 840 1058 748 1042 Z" fill="#f1e2bf"/>')
    a("</g>")

    # 各区的底色
    a('<g filter="url(#isle-wc-soft)">')
    a('<ellipse cx="800" cy="290" rx="380" ry="190" fill="#f7fafc" opacity=".95"/>')          # 雪原
    a('<ellipse cx="320" cy="300" rx="220" ry="170" fill="#d5e4df" opacity=".7"/>')            # 松林
    a('<ellipse cx="1260" cy="300" rx="220" ry="160" fill="#d9e7c6" opacity=".85"/>')          # 高地
    a('<ellipse cx="1180" cy="230" rx="110" ry="60" fill="#cfe0b8" opacity=".7"/>')
    a('<ellipse cx="290" cy="620" rx="200" ry="150" fill="#f0d6b4" opacity=".85"/>')           # 荒原
    a('<ellipse cx="200" cy="700" rx="90" ry="60" fill="#ecc9a0" opacity=".6"/>')
    a('<ellipse cx="860" cy="565" rx="250" ry="130" fill="#f2ede3" opacity=".8"/>')            # 小镇
    a('<ellipse cx="760" cy="860" rx="320" ry="130" fill="#c9e0b4" opacity=".65"/>')           # 南边的夏天
    a('<ellipse cx="540" cy="800" rx="130" ry="80" fill="#cfe4ba" opacity=".55"/>')
    a('<ellipse cx="1260" cy="860" rx="210" ry="120" fill="#efe9da" opacity=".9"/>')           # 地中海
    a('<ellipse cx="1380" cy="560" rx="120" ry="150" fill="#e8eadf" opacity=".6"/>')           # 东边
    a("</g>")

    # ── 北边：雪山（Five & Six 在最高那座的山顶）和雪原上一面冰湖
    a('<g filter="url(#isle-wc)">')
    a('<g stroke="#9fb4c6" stroke-width="2" stroke-linejoin="round">')
    a('<path d="M520 356 L596 270 L668 356 Z" fill="#cbd7e2"/><path d="M944 356 L1024 262 L1100 356 Z" fill="#cbd7e2"/>')
    a('<path d="M616 344 L700 214 L784 344 Z" fill="#c2d0dc"/><path d="M832 344 L920 200 L1008 344 Z" fill="#c2d0dc"/>')
    a('<path d="M690 352 L800 150 L912 352 Z" fill="#b2c3d3"/>')
    a("</g>")
    a('<path d="M770 206 L800 150 L832 208 L818 200 L802 220 L786 200 Z" fill="#ffffff"/>')
    a('<path d="M684 238 L700 214 L717 241 L708 236 L700 247 L692 236 Z" fill="#ffffff"/>')
    a('<path d="M903 228 L920 200 L938 230 L929 225 L920 237 L911 225 Z" fill="#ffffff"/>')
    a('<path d="M584 284 L596 270 L609 287 L602 283 L596 291 L590 283 Z" fill="#ffffff"/>')
    a('<path d="M1012 276 L1024 262 L1037 279 L1030 275 L1024 283 L1018 275 Z" fill="#ffffff"/>')
    a('<ellipse cx="820" cy="396" rx="78" ry="22" fill="#d3e9f4" stroke="#ffffff" stroke-width="3"/>')
    a("</g>")
    a('<g stroke="#ffffff" stroke-width="1.6" stroke-linecap="round" opacity=".9"><path d="M770 392 l30 -6 M818 402 l26 -5 M846 390 l18 -3"/></g>')
    # 雪原上的小雪人
    a('<g transform="translate(760 458)"><circle cy="-6" r="7" fill="#ffffff" stroke="#b9cbd8"/><circle cy="-17" r="5" fill="#ffffff" stroke="#b9cbd8"/><path d="M0 -17 l5 1.4 l-5 1" fill="#e3954a"/><rect x="-4.5" y="-26" width="9" height="4" fill="#34495e"/><rect x="-3" y="-30" width="6" height="5" fill="#34495e"/></g>')

    # ── 西北：松林和林中的湖
    a('<g filter="url(#isle-wc)"><ellipse cx="330" cy="300" rx="64" ry="30" fill="#bcdcec" stroke="#ffffff" stroke-width="3"/></g>')
    a('<path d="M300 298 l22 -4 M336 306 l18 -3" stroke="#ffffff" stroke-width="1.6" stroke-linecap="round"/>')
    pines = scatter(7, (150, 150, 560, 470), 58, avoid=[(330, 300, 80)] + HOUSE_AVOID, gap=24)
    a("<g>" + uses("isle-fir", pines[::2], 17, 25, seed=7) + uses("isle-pine", pines[1::2], 16, 22, seed=8) + "</g>")
    snowpines = scatter(17, (540, 190, 1100, 470), 26, avoid=[(800, 280, 230), (820, 396, 90)] + HOUSE_AVOID, gap=30)
    a("<g>" + uses("isle-pine", snowpines, 15, 21, seed=18) + "</g>")

    # ── 东北：英格兰高地（缓坡、石头矮墙、羊、一条小跑道停着一架双翼机）
    a('<g fill="#cfe0b8" opacity=".9" filter="url(#isle-wc-soft)"><path d="M1090 260 C1150 220 1220 230 1260 260 Z"/><path d="M1240 360 C1300 320 1380 330 1430 370 Z"/><path d="M1130 410 C1180 380 1240 386 1270 412 Z"/></g>')
    a('<g fill="none" stroke="#a9a596" stroke-width="2" stroke-dasharray="3 3" stroke-linecap="round" opacity=".85">'
      '<path d="M1080 250 C1160 270 1240 250 1310 280 C1360 300 1400 290 1440 300"/>'
      '<path d="M1180 140 C1190 200 1170 260 1200 330 C1220 380 1210 430 1230 470"/>'
      '<path d="M1290 160 C1300 210 1290 260 1320 300"/></g>')
    a('<g transform="rotate(-10 1300 382)"><rect x="1222" y="372" width="156" height="20" rx="3" fill="#d2cec4"/>'
      '<path d="M1232 382 h136" stroke="#ffffff" stroke-width="2" stroke-dasharray="10 8"/></g>')
    a('<g transform="translate(1268 360) rotate(-10)"><path d="M0 0 h26 l4 -3 h-4 Z" fill="#9aa48a" stroke="#5b6450" stroke-width=".8"/>'
      '<rect x="7" y="-7" width="14" height="2.4" fill="#9aa48a" stroke="#5b6450" stroke-width=".6"/>'
      '<rect x="7" y="3" width="14" height="2.4" fill="#9aa48a" stroke="#5b6450" stroke-width=".6"/>'
      '<path d="M10 -5 v8 M18 -5 v8" stroke="#5b6450" stroke-width=".7"/><circle cx="-1" cy="0" r="2" fill="#5b6450"/></g>')
    sheep = scatter(23, (1090, 190, 1420, 460), 9, avoid=HOUSE_AVOID + [(1300, 382, 90)], gap=40)
    a("<g>" + uses("isle-sheep", sheep, 13, 9, jitter=.05, seed=23) + "</g>")
    hl_trees = scatter(29, (1080, 150, 1440, 470), 12, avoid=HOUSE_AVOID + [(1300, 382, 90)], gap=40)
    a("<g>" + uses("isle-tree", hl_trees, 15, 20, seed=29) + "</g>")

    # ── 西边：红岩荒原（平顶山、仙人掌、土路、一条铁道）
    a('<g filter="url(#isle-wc)">'
      '<path d="M128 606 L150 552 L232 552 L254 606 Z" fill="#d99a70"/><path d="M150 552 L232 552 L236 562 L146 562 Z" fill="#e9b88e"/>'
      '<path d="M300 560 L322 506 L404 506 L428 560 Z" fill="#d18f66"/><path d="M322 506 L404 506 L408 516 L318 516 Z" fill="#e6b087"/>'
      '<path d="M354 676 L366 640 L398 640 L410 676 Z" fill="#d99a70"/>'
      '</g>')
    a('<g fill="none" stroke-linecap="round"><path d="M112 712 C220 694 330 684 440 656 C500 640 540 612 590 588" stroke="#9b7b55" stroke-width="7" stroke-dasharray="1.6 6"/>'
      '<path d="M112 709 C220 691 330 681 440 653 C500 637 540 609 590 585" stroke="#6f5f4e" stroke-width="1.3"/>'
      '<path d="M112 715 C220 697 330 687 440 659 C500 643 540 615 590 591" stroke="#6f5f4e" stroke-width="1.3"/></g>')
    cacti = scatter(31, (120, 470, 500, 780), 16, avoid=HOUSE_AVOID + [(190, 580, 60), (364, 534, 64)], gap=36)
    a("<g>" + uses("isle-cactus", cacti, 11, 15, seed=31) + "</g>")

    # ── 西南的海滩：几棵棕榈
    palms = [(170, 760), (300, 900), (226, 846)]
    a("<g>" + uses("isle-palm", palms, 20, 26, seed=37) + "</g>")

    # ── 河：从雪山脚下一路流过小镇，到南边河口
    a('<g filter="url(#isle-wc)" fill="none" stroke-linecap="round">'
      f'<path d="{RIVER}" stroke="#8cc3df" stroke-width="15"/><path d="{RIVER}" stroke="#cde7f3" stroke-width="5"/></g>')
    # 小镇的桥、Trent 那座单车道的小桥
    a('<g transform="rotate(-62 668 560)"><rect x="646" y="554" width="44" height="12" rx="2" fill="#b9a68a"/><path d="M648 557 h40 M648 563 h40" stroke="#8a7458" stroke-width="1"/></g>')
    a('<g transform="rotate(42 700 794)"><rect x="678" y="788" width="44" height="11" rx="2" fill="#b08b62"/><path d="M680 791 h40 M680 796 h40" stroke="#8a6a46" stroke-width="1"/></g>')

    a('<g transform="rotate(-48 805 905)"><rect x="781" y="898" width="48" height="13" rx="1" fill="#8e9aa6"/><path d="M783 898 l8 -6 l8 6 l8 -6 l8 6 l8 -6 l8 6" stroke="#5f6c78" stroke-width="1.4" fill="none"/></g>')
    a('<g filter="url(#isle-wc)"><ellipse cx="306" cy="214" rx="28" ry="12" fill="#bcdcec" stroke="#ffffff" stroke-width="2"/></g>')

    # ── 路：小镇往四面八方
    a('<g fill="none" stroke="#bfa47c" stroke-width="3.2" stroke-linecap="round" stroke-dasharray="1 8" opacity=".9">'
      '<path d="M560 560 C640 548 760 556 850 560 C940 564 1000 556 1100 570 C1200 586 1290 600 1420 606"/>'
      '<path d="M560 560 C470 580 400 612 300 650 C230 676 170 690 120 700"/>'
      '<path d="M900 520 C980 470 1060 400 1150 350 C1200 320 1240 300 1280 290"/>'
      '<path d="M920 620 C990 700 1080 760 1180 820 C1240 856 1300 900 1330 960"/>'
      '<path d="M850 560 C860 640 880 720 900 800 C916 870 920 940 930 1000"/>'
      '<path d="M760 470 C700 420 600 380 480 340"/>'
      '<path d="M830 450 C820 420 810 400 806 380"/></g>')
    # 小镇的石板广场
    a('<g fill="#ece2cf" stroke="#d6c8ae" stroke-width="1.2" opacity=".9"><rect x="792" y="518" width="116" height="78" rx="10"/></g>')
    a('<g fill="#e3d8c4" opacity=".7"><rect x="720" y="482" width="60" height="26" rx="5"/><rect x="920" y="482" width="64" height="26" rx="5"/>'
      '<rect x="716" y="616" width="66" height="26" rx="5"/><rect x="922" y="616" width="66" height="26" rx="5"/></g>')
    # 广场上的喷泉
    a('<g transform="translate(850 572)"><ellipse rx="16" ry="7" fill="#bfe1f1" stroke="#9fb6c6"/><path d="M0 -2 v-9 M0 -11 q-5 2 -7 7 M0 -11 q5 2 7 7" stroke="#8cc3df" stroke-width="1.6" fill="none" stroke-linecap="round"/></g>')
    town_trees = scatter(41, (520, 430, 1200, 720), 22, avoid=HOUSE_AVOID + [(850, 560, 90), (680, 560, 50)], gap=44)
    a("<g>" + uses("isle-tree", town_trees, 14, 18, seed=41) + "</g>")

    # ── 南边夏天的河：水上乐园（滑梯）、球场
    a('<g filter="url(#isle-wc)"><path d="M520 892 C520 868 546 860 572 862 C604 864 622 880 614 902 C606 922 566 926 540 918 C522 912 520 902 520 892 Z" fill="#9fd8ef" stroke="#ffffff" stroke-width="3"/></g>')
    a('<path d="M600 862 C626 840 604 818 628 800" stroke="#f2a07a" stroke-width="4.5" fill="none" stroke-linecap="round"/>'
      '<path d="M626 800 v-14 h8 v26" stroke="#8a7458" stroke-width="1.5" fill="none"/>'
      '<g fill="#f2c46b"><circle cx="546" cy="884" r="3"/><circle cx="586" cy="900" r="3"/></g>')
    a('<g transform="rotate(-6 1010 860)"><rect x="950" y="830" width="120" height="66" rx="3" fill="#b4d89a" stroke="#ffffff" stroke-width="2"/>'
      '<path d="M1010 830 v66" stroke="#ffffff" stroke-width="1.6"/><circle cx="1010" cy="863" r="10" fill="none" stroke="#ffffff" stroke-width="1.6"/>'
      '<rect x="950" y="851" width="12" height="24" fill="none" stroke="#ffffff" stroke-width="1.4"/><rect x="1058" y="851" width="12" height="24" fill="none" stroke="#ffffff" stroke-width="1.4"/></g>')
    s_trees = scatter(43, (430, 730, 1090, 1010), 30, avoid=HOUSE_AVOID + [(566, 890, 66), (1010, 862, 80)], gap=34)
    a("<g>" + uses("isle-tree", s_trees, 15, 20, seed=43) + "</g>")

    # ── 东边：悬崖和沙滩上的棕榈
    a('<g filter="url(#isle-wc)"><path d="M1420 330 C1450 360 1470 400 1478 440 L1448 452 C1440 410 1420 380 1398 356 Z" fill="#c9bcab"/>'
      '<path d="M1402 354 C1424 380 1440 410 1448 452" stroke="#9c8e7c" stroke-width="2" fill="none"/></g>')
    a("<g>" + uses("isle-palm", [(1478, 520), (1490, 690), (1440, 760)], 20, 26, seed=47) + "</g>")

    # ── 东南：地中海海岸（白色石灰岩崖、橄榄树、一个小港口）
    a('<g filter="url(#isle-wc)"><path d="M1380 830 C1420 860 1430 900 1400 940 C1370 972 1330 988 1300 990 L1292 970 C1330 960 1366 936 1378 900 C1388 870 1376 850 1360 838 Z" fill="#f6f2e9" stroke="#d6c9b2" stroke-width="2"/></g>')
    olives = scatter(53, (1080, 720, 1440, 1000), 20, avoid=HOUSE_AVOID + [(1370, 900, 50)], gap=38)
    a("<g>" + uses("isle-olive", olives, 16, 17, seed=53) + "</g>")
    a('<g><rect x="1238" y="992" width="12" height="70" rx="2" fill="#c9b08c"/><path d="M1240 1004 h8 M1240 1018 h8 M1240 1032 h8 M1240 1046 h8" stroke="#a08a68" stroke-width="1.2"/></g>')
    a('<g transform="translate(1266 1030)"><path d="M0 16 h30 l-5 7 h-20 Z" fill="#3f7fa8"/><path d="M15 0 v16" stroke="#6b5640" stroke-width="1.3"/><path d="M16 2 L28 14 H16 Z" fill="#ffffff" stroke="#9fb6c6" stroke-width=".8"/><path d="M14 4 L6 14 H14 Z" fill="#e86f5a"/></g>')

    # ── 码头：抖出来的人从这里上岸
    a('<g><rect x="654" y="1020" width="13" height="66" rx="2" fill="#a88560"/><path d="M656 1030 h9 M656 1044 h9 M656 1058 h9 M656 1072 h9" stroke="#866646" stroke-width="1.2"/>'
      '<text x="676" y="1080" class="c-isle__lbl">码头</text></g>')
    # 西边海上一只小帆船
    a('<g transform="translate(36 860)"><path d="M0 18 h34 l-6 8 h-22 Z" fill="#b08b62"/><path d="M17 0 v18" stroke="#6b5640" stroke-width="1.4"/><path d="M18 2 L32 16 H18 Z" fill="#ffffff" stroke="#9fb6c6" stroke-width=".8"/></g>')

    # ── 各区的名字（小字，房子尽量不压上去）
    zones = [
        (300, 118, "西北的松林"), (1010, 132, "北边的雪山"), (1300, 150, "英格兰高地"),
        (215, 722, "红岩荒原"), (176, 978, "西边的海滩"), (850, 628, "小镇"), (800, 1000, "夏天的河"),
        (1395, 968, "地中海海岸"), (1520, 650, "东边的沙滩"),
    ]
    a('<g class="c-isle__zones">' + "".join(
        f'<text x="{x}" y="{y}" text-anchor="middle" class="c-isle__zone">{t}</text>' for x, y, t in zones if t) + "</g>")

    # 指南针
    a('<g transform="translate(1530 1030)"><circle r="34" fill="#f7f4ec" opacity=".85" stroke="#8fb4c9" stroke-width="1.5"/>'
      '<path d="M0 -27 L7 0 L0 27 L-7 0 Z" fill="#c9d6e1"/><path d="M0 -27 L7 0 L-7 0 Z" fill="#d79a4a"/>'
      '<text y="-38" text-anchor="middle" class="c-isle__lbl">北</text></g>')
    # 角上的名牌
    a('<g transform="translate(36 30)"><rect width="250" height="70" rx="7" fill="#fbf8f1" opacity=".92" stroke="#bcd3e0"/>'
      '<text x="20" y="34" class="c-isle__ttl">冬的岛屿</text><text x="20" y="56" class="c-isle__sub">WINTER\'S ISLAND · 面积：无限</text></g>')
    # 纸纹
    a(f'<rect width="{W}" height="{H}" filter="url(#isle-grain)"/>')
    a("</svg>")
    return "\n".join(s) + "\n"


if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    print(f"✓ 写好了 {OUT.relative_to(OUT.parents[1])}（{OUT.stat().st_size // 1024} KB）")
