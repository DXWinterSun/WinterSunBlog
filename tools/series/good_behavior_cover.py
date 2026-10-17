"""Good Behavior 系列封面（images/good-behavior.svg）的生成脚本。

2026-10-17 画的：塔顶那间屋——空铁椅、扶手上绕着铁链、座上那顶骷髅手骨大檐帽、地上红绒球、
窗台上的小钥匙和搪瓷杯、头顶一盏红灯。照血族线封面那样画成静物，不画人。
改图就改这里再跑：python3 tools/series/good_behavior_cover.py images/good-behavior.svg
"""
import math, random, sys
random.seed(7)
W,H=900,540
o=[]
A=o.append

def chain(pts, step=11, rx=6.2, ry=3.4, color="#9aa1a8", hi="#e3dfd6", width=2.1):
    """links along a polyline/curve (list of points), alternating face/edge"""
    # resample
    seg=[]
    for i in range(len(pts)-1):
        (x1,y1),(x2,y2)=pts[i],pts[i+1]
        seg.append((x1,y1,x2,y2,math.hypot(x2-x1,y2-y1)))
    total=sum(s[4] for s in seg); d=0; k=0; out=[]
    while d<total:
        acc=0
        for (x1,y1,x2,y2,L) in seg:
            if acc+L>=d:
                t=(d-acc)/L if L else 0
                x=x1+(x2-x1)*t; y=y1+(y2-y1)*t
                ang=math.degrees(math.atan2(y2-y1,x2-x1))
                out.append((x,y,ang)); break
            acc+=L
        d+=step
    for i,(x,y,ang) in enumerate(out):
        if i%2==0:
            A(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx}" ry="{ry}" transform="rotate({ang:.1f} {x:.1f} {y:.1f})" fill="none" stroke="{color}" stroke-width="{width}"/>')
            A(f'<path d="M{x-rx*0.6:.1f} {y-ry*0.55:.1f} q {rx*0.5:.1f} -1.2 {rx:.1f} 0" transform="rotate({ang:.1f} {x:.1f} {y:.1f})" fill="none" stroke="{hi}" stroke-width="0.9" opacity="0.7"/>')
        else:
            A(f'<rect x="{x-rx:.1f}" y="{y-1.3:.1f}" width="{2*rx:.1f}" height="2.6" rx="1.3" transform="rotate({ang:.1f} {x:.1f} {y:.1f})" fill="{color}"/>')

def qcurve(p0,p1,p2,n=24):
    return [((1-t)**2*p0[0]+2*(1-t)*t*p1[0]+t*t*p2[0],(1-t)**2*p0[1]+2*(1-t)*t*p1[1]+t*t*p2[1]) for t in [i/n for i in range(n+1)]]

A(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
A('''<defs>
<linearGradient id="gb-bg" x1="0%" y1="0%" x2="70%" y2="100%">
 <stop offset="0%" stop-color="#22262d"/><stop offset="55%" stop-color="#16181c"/><stop offset="100%" stop-color="#0c0d10"/></linearGradient>
<radialGradient id="gb-bulb" cx="50%" cy="50%" r="50%">
 <stop offset="0%" stop-color="#ff5a5f" stop-opacity="0.55"/><stop offset="30%" stop-color="#cf3a40" stop-opacity="0.22"/><stop offset="100%" stop-color="#cf3a40" stop-opacity="0"/></radialGradient>
<linearGradient id="gb-cone" x1="0%" y1="0%" x2="0%" y2="100%">
 <stop offset="0%" stop-color="#e2474d" stop-opacity="0.26"/><stop offset="100%" stop-color="#cf3a40" stop-opacity="0.05"/></linearGradient>
<radialGradient id="gb-floor" cx="50%" cy="50%" r="50%">
 <stop offset="0%" stop-color="#cf3a40" stop-opacity="0.30"/><stop offset="100%" stop-color="#cf3a40" stop-opacity="0"/></radialGradient>
<radialGradient id="gb-moon" cx="50%" cy="50%" r="50%">
 <stop offset="0%" stop-color="#e9eef3" stop-opacity="0.5"/><stop offset="40%" stop-color="#b9c4cf" stop-opacity="0.14"/><stop offset="100%" stop-color="#b9c4cf" stop-opacity="0"/></radialGradient>
<linearGradient id="gb-shaft" x1="85%" y1="10%" x2="40%" y2="95%">
 <stop offset="0%" stop-color="#dfe6ee" stop-opacity="0.16"/><stop offset="100%" stop-color="#dfe6ee" stop-opacity="0"/></linearGradient>
<linearGradient id="gb-iron" x1="0%" y1="0%" x2="100%" y2="0%">
 <stop offset="0%" stop-color="#2a2d33"/><stop offset="45%" stop-color="#5b6068"/><stop offset="60%" stop-color="#7d838b"/><stop offset="100%" stop-color="#2a2d33"/></linearGradient>
<linearGradient id="gb-ironv" x1="0%" y1="0%" x2="0%" y2="100%">
 <stop offset="0%" stop-color="#6b7078"/><stop offset="100%" stop-color="#2b2e34"/></linearGradient>
<linearGradient id="gb-patent" x1="0%" y1="0%" x2="0%" y2="100%">
 <stop offset="0%" stop-color="#2a2c31"/><stop offset="60%" stop-color="#0d0e10"/><stop offset="100%" stop-color="#050506"/></linearGradient>
<linearGradient id="gb-brass" x1="0%" y1="0%" x2="100%" y2="100%">
 <stop offset="0%" stop-color="#f3d58c"/><stop offset="50%" stop-color="#b98a3c"/><stop offset="100%" stop-color="#7a5822"/></linearGradient>
<radialGradient id="gb-ball" cx="40%" cy="35%" r="65%">
 <stop offset="0%" stop-color="#ef5d63"/><stop offset="70%" stop-color="#b52a31"/><stop offset="100%" stop-color="#6d161b"/></radialGradient>
<filter id="gb-soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="7"/></filter>
<radialGradient id="gb-vig" cx="50%" cy="52%" r="72%">
 <stop offset="55%" stop-color="#050506" stop-opacity="0"/><stop offset="100%" stop-color="#050506" stop-opacity="0.78"/></radialGradient>
<clipPath id="gb-win"><path d="M662 330 L662 150 Q722 78 782 150 L782 330 Z"/></clipPath>
</defs>''')
A(f'<rect width="{W}" height="{H}" fill="url(#gb-bg)"/>')
# stone blocks on wall
for row in range(0,9):
    y=row*54
    off=0 if row%2==0 else 60
    A(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="#2a2e35" stroke-width="1" opacity="0.35"/>')
    for x in range(-off,W,120):
        A(f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y+54}" stroke="#2a2e35" stroke-width="1" opacity="0.28"/>')
# window + moon
A('<g clip-path="url(#gb-win)"><rect x="650" y="60" width="150" height="280" fill="#1b2027"/>'
  '<circle cx="740" cy="178" r="110" fill="url(#gb-moon)"/><circle cx="740" cy="178" r="30" fill="#e8edf2"/>'
  '<circle cx="731" cy="170" r="5" fill="#cfd7df" opacity="0.6"/><circle cx="749" cy="187" r="6.5" fill="#cfd7df" opacity="0.45"/>'
  '<path d="M650 236 Q690 222 730 236 T800 232 L800 340 L650 340 Z" fill="#2a3038" opacity="0.55"/>'
  '<path d="M650 262 Q700 248 750 262 T800 258 L800 340 L650 340 Z" fill="#323943" opacity="0.5"/>'
  # distant tower silhouette in fog
  '<path d="M694 340 L694 268 Q702 260 710 268 L710 340 Z" fill="#11151a" opacity="0.5"/>')
for x in range(674,782,18):
    A(f'<line x1="{x}" y1="80" x2="{x}" y2="332" stroke="#0e1014" stroke-width="4"/>'
      f'<line x1="{x-1}" y1="80" x2="{x-1}" y2="332" stroke="#4a5058" stroke-width="0.8" opacity="0.6"/>')
A('<line x1="660" y1="236" x2="784" y2="236" stroke="#0e1014" stroke-width="4"/></g>')
A('<path d="M662 330 L662 150 Q722 78 782 150 L782 330 Z" fill="none" stroke="#33373f" stroke-width="6"/>')
# sill
A('<path d="M650 330 L796 330 L806 344 L640 344 Z" fill="#2b2f36"/><line x1="640" y1="344" x2="806" y2="344" stroke="#0e1014" stroke-width="2"/>')
# moon shaft
A('<path d="M664 150 L784 150 L560 520 L360 520 Z" fill="url(#gb-shaft)" filter="url(#gb-soft)"/>')
# enamel cup on sill
A('<path d="M752 300 L778 300 L775 330 L755 330 Z" fill="#d9d6cf"/><ellipse cx="765" cy="300" rx="13" ry="3.4" fill="#eceae4"/>'
  '<ellipse cx="765" cy="300.5" rx="10.5" ry="2.4" fill="#5a4a3b"/><path d="M778 306 q9 2 6 10 q-3 6 -8 4" fill="none" stroke="#d9d6cf" stroke-width="2.4"/>'
  '<path d="M753 320 L777 320" stroke="#3c5a7a" stroke-width="1.6" opacity="0.7"/>')
# key on sill (brass), glinting
A('<g transform="translate(704 326) rotate(-12)">'
  '<circle cx="0" cy="0" r="5.6" fill="none" stroke="url(#gb-brass)" stroke-width="2.6"/>'
  '<rect x="5" y="-1.4" width="17" height="2.8" rx="1.2" fill="url(#gb-brass)"/>'
  '<rect x="16" y="1.2" width="2.4" height="4" fill="url(#gb-brass)"/><rect x="19.6" y="1.2" width="2.2" height="3" fill="url(#gb-brass)"/></g>'
  '<g fill="#ffe7a8"><path d="M716 314 l1.2 4 l4 1.2 l-4 1.2 l-1.2 4 l-1.2 -4 l-4 -1.2 l4 -1.2 z" opacity="0.9"/></g>')
# brass rules plaque on left wall
A('<rect x="92" y="150" width="118" height="84" rx="3" fill="#6e5a2e" opacity="0.55"/>'
  '<rect x="96" y="154" width="110" height="76" rx="2" fill="none" stroke="#c9a35a" stroke-width="1" opacity="0.5"/>')
for i,(y,w) in enumerate([(170,64),(184,86),(196,80),(208,84),(220,50)]):
    A(f'<line x1="{151-w/2}" y1="{y}" x2="{151+w/2}" y2="{y}" stroke="#d8bd7a" stroke-width="{2 if i==0 else 1.2}" opacity="{0.55 if i==0 else 0.35}"/>')
A('<circle cx="100" cy="158" r="1.6" fill="#d8bd7a" opacity="0.6"/><circle cx="202" cy="158" r="1.6" fill="#d8bd7a" opacity="0.6"/>'
  '<circle cx="100" cy="226" r="1.6" fill="#d8bd7a" opacity="0.6"/><circle cx="202" cy="226" r="1.6" fill="#d8bd7a" opacity="0.6"/>')
# bulb glow + cone
A('<circle cx="390" cy="112" r="190" fill="url(#gb-bulb)"/>')
A('<path d="M380 116 L400 116 L560 492 L220 492 Z" fill="url(#gb-cone)" filter="url(#gb-soft)"/>')
A('<ellipse cx="390" cy="492" rx="210" ry="30" fill="url(#gb-floor)"/>')
# cord + bulb
A('<line x1="390" y1="0" x2="390" y2="94" stroke="#0a0b0d" stroke-width="2"/>'
  '<rect x="383" y="92" width="14" height="12" rx="2" fill="#2b2e33"/>'
  '<circle cx="390" cy="113" r="10" fill="#ff7a7e"/><circle cx="387" cy="110" r="3.5" fill="#ffd2d3" opacity="0.9"/>')
# floor line
A('<line x1="0" y1="492" x2="900" y2="492" stroke="#262a30" stroke-width="1.4"/>')
for x1,x2 in [(120,80),(300,280),(480,500),(680,720),(860,900)]:
    A(f'<line x1="{x1}" y1="492" x2="{x2}" y2="540" stroke="#262a30" stroke-width="1" opacity="0.7"/>')
# shadow of chair
A('<ellipse cx="392" cy="494" rx="110" ry="12" fill="#050506" opacity="0.55"/>')
# ── iron chair ──
I='url(#gb-iron)'; IV='url(#gb-ironv)'
# back legs
A(f'<rect x="341" y="400" width="7" height="72" fill="#25282d"/><rect x="434" y="400" width="7" height="72" fill="#25282d"/>')
# back posts
A(f'<rect x="336" y="196" width="10" height="210" rx="2" fill="{I}"/><rect x="436" y="196" width="10" height="210" rx="2" fill="{I}"/>')
A(f'<path d="M332 204 Q391 186 450 204 L450 216 Q391 198 332 216 Z" fill="{IV}"/>')
for x in (364,391,418):
    A(f'<rect x="{x-2.5}" y="210" width="5" height="160" fill="{I}" opacity="0.95"/>')
A(f'<rect x="340" y="300" width="102" height="5" fill="{IV}" opacity="0.8"/>')
# seat
A('<path d="M326 380 L456 380 L472 402 L310 402 Z" fill="#3b3f46"/><path d="M310 402 L472 402 L472 412 L310 412 Z" fill="#23262b"/>'
  '<path d="M326 380 L456 380" stroke="#8a9098" stroke-width="1.2" opacity="0.6"/>')
# front legs
A(f'<rect x="312" y="410" width="9" height="80" fill="{I}"/><rect x="461" y="410" width="9" height="80" fill="{I}"/>'
  f'<rect x="318" y="460" width="146" height="4" fill="#2b2e34"/>')
# armrests
A(f'<path d="M340 318 L300 342 L306 348 L344 326 Z" fill="{IV}"/><rect x="301" y="344" width="7" height="60" fill="{I}"/>'
  f'<path d="M442 318 L482 342 L476 348 L438 326 Z" fill="{IV}"/><rect x="474" y="344" width="7" height="60" fill="{I}"/>')
# chains wrapped on armrests + drooping between
for side in (-1,1):
    ax=391+side*70
    # wraps
    for k in range(3):
        cx=391+side*(56+k*9); cy=322+k*6+(4 if side>0 else 4)
        A(f'<ellipse cx="{cx}" cy="{cy}" rx="5.5" ry="8" fill="none" stroke="#a7adb4" stroke-width="2.2"/>')
        A(f'<path d="M{cx-3} {cy-6} q3 -2 6 0" stroke="#e7e3da" stroke-width="0.9" fill="none" opacity="0.7"/>')
# droop from left arm down to floor, pooled, across to right arm (the shackle chain)
pts=qcurve((302,348),(330,470),(372,486))+qcurve((372,486),(392,492),(414,486))[1:]+qcurve((414,486),(456,470),(480,348))[1:]
chain(pts, step=10)
# shackle cuffs resting on seat edge
for cx in (322,460):
    A(f'<ellipse cx="{cx}" cy="390" rx="11" ry="5" fill="none" stroke="#b7bcc2" stroke-width="3.6"/>'
      f'<path d="M{cx-9} 388 q9 -4 18 0" stroke="#efece5" stroke-width="1" fill="none" opacity="0.6"/>')
# ── peaked cap on seat ──
A('<g transform="translate(391 0)">'
  # crown top (wide oval)
  '<path d="M-58 352 C-62 330 -30 318 0 318 C30 318 64 328 58 352 Z" fill="url(#gb-patent)"/>'
  '<ellipse cx="0" cy="352" rx="58" ry="10" fill="#141518"/>'
  # band
  '<path d="M-44 350 L44 350 L42 370 L-42 370 Z" fill="#0b0c0e"/>'
  '<path d="M-44 352 L44 352" stroke="#cf3a40" stroke-width="2.4" opacity="0.85"/>'
  # visor
  '<path d="M-44 368 C-30 386 30 386 44 368 C30 376 -30 376 -44 368 Z" fill="#050506"/>'
  '<path d="M-36 372 C-18 382 18 382 36 372" stroke="#e9e2d6" stroke-width="1.6" fill="none" opacity="0.55"/>'
  # patent highlights on crown
  '<path d="M-40 332 C-20 322 14 321 34 328" stroke="#f1ece3" stroke-width="2.2" fill="none" opacity="0.5"/>'
  '<path d="M-30 340 C-12 334 10 334 26 338" stroke="#f1ece3" stroke-width="1" fill="none" opacity="0.3"/>'
  # badge stud
  '<circle cx="0" cy="360" r="4.5" fill="#9aa1a8"/><circle cx="-1.2" cy="358.8" r="1.6" fill="#f2efe8"/>'
  '</g>')
# skeleton hand gripping the crown (white finger bones over the top-left)
bones=[(-34,348,-52),(-24,344,-70),(-12,342,-84),(0,342,-96),(12,345,-110)]
A('<g transform="translate(391 0)" fill="#e9e4da" stroke="#9c958a" stroke-width="0.6">')
A('<path d="M-46 352 Q-38 346 -26 348 Q-16 350 -8 348 L-10 356 Q-30 360 -46 358 Z"/>')  # palm/metacarpals at band
for (x,y,ang) in bones:
    rad=math.radians(ang)
    # two phalanges per finger, curling over the crown
    x2=x+math.cos(rad)*-1*0+ (x*0)  # placeholder
for i,(x,y) in enumerate([(-40,348),(-30,346),(-20,346),(-10,347)]):
    # finger: three segments arcing up/over crown toward the right
    segs=[(x,y,x+4,y-10),(x+4,y-10,x+10,y-18),(x+10,y-18,x+17,y-22)]
    for (a,b,c,d) in segs:
        A(f'<line x1="{a}" y1="{b}" x2="{c}" y2="{d}" stroke="#e9e4da" stroke-width="3.6" stroke-linecap="round"/>')
        A(f'<circle cx="{c}" cy="{d}" r="2.2"/>')
A('<line x1="-46" y1="356" x2="-56" y2="350" stroke="#e9e4da" stroke-width="3.6" stroke-linecap="round"/><circle cx="-56" cy="350" r="2.2"/>')
A('</g>')
# ── red pom-pom ball on floor ──
bx,by=246,474
A(f'<ellipse cx="{bx+4}" cy="{by+17}" rx="20" ry="4" fill="#050506" opacity="0.6"/>')
A('<filter id="gb-fur" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="0.55"/></filter>')
A(f'<circle cx="{bx}" cy="{by}" r="16" fill="url(#gb-ball)" filter="url(#gb-soft)" opacity="0.5"/>')
A(f'<circle cx="{bx}" cy="{by}" r="15" fill="url(#gb-ball)"/>')
A('<g filter="url(#gb-fur)">')
for i in range(260):
    a=random.uniform(0,2*math.pi); r0=random.uniform(0,15); r1=min(r0+random.uniform(2,4.5),19.5)
    x0=bx+math.cos(a)*r0; y0=by+math.sin(a)*r0; x1=bx+math.cos(a+random.uniform(-.3,.3))*r1; y1=by+math.sin(a+random.uniform(-.3,.3))*r1
    shade=(math.cos(a)*-0.6+math.sin(a)*-0.8)  # light from upper-left
    col="#f07a7f" if shade>0.5 else ("#d6464c" if shade>-0.2 else ("#b02a31" if shade>-0.7 else "#7e181e"))
    A(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="{col}" stroke-width="1.1" stroke-linecap="round" opacity="0.85"/>')
A('</g>')
A(f'<ellipse cx="{bx-5}" cy="{by-6}" rx="6" ry="4" fill="#ffb3b6" opacity="0.25"/>')
# dust motes in cones
for i in range(18):
    x=random.uniform(300,620); y=random.uniform(150,470)
    A(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{random.uniform(0.9,1.8):.1f}" fill="#f1e2df" opacity="{random.uniform(0.15,0.45):.2f}"/>')
# vignette
A(f'<rect width="{W}" height="{H}" fill="url(#gb-vig)"/>')
A('</svg>')
open(sys.argv[1],'w').write('\n'.join(o))
print('ok', len('\n'.join(o)))
