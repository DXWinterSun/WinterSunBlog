# -*- coding: utf-8 -*-
"""藏品架六种媒介的小画（照 _includes/sam-toy-art.html 的画风：淡底、白雪点、细描边；主色接角色 --a）。"""
HEAD = '<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false" class="art">'
DOTS = '<g fill="#fff" opacity=".9"><circle cx="8" cy="10" r="1.2"/><circle cx="55" cy="8" r="1"/><circle cx="58" cy="52" r="1.3"/><circle cx="7" cy="48" r="1"/></g>'
SK = 'stroke="#14212e" stroke-width="1.5" stroke-linejoin="round"'
ART = {}
ART['disc'] = HEAD + DOTS + '''
<circle cx="43" cy="31" r="15" class="a2" %(sk)s/>
<circle cx="43" cy="31" r="11" fill="none" stroke="#fff" stroke-width="1" opacity=".75"/>
<circle cx="43" cy="31" r="7" fill="none" stroke="#fff" stroke-width="1" opacity=".5"/>
<circle cx="43" cy="31" r="2.6" class="cream" stroke="#14212e" stroke-width="1.2"/>
<rect x="11" y="13" width="28" height="38" rx="2.5" class="cream" %(sk)s/>
<path d="M11 15.5a2.5 2.5 0 0 1 2.5-2.5H18v38h-4.5a2.5 2.5 0 0 1-2.5-2.5z" class="a3"/>
<rect x="21" y="19" width="14" height="26" rx="1.5" class="a2"/>
<path d="M24.5 26h7M24.5 30.5h7M24.5 35h4" stroke="#fff" stroke-width="1.4" stroke-linecap="round"/>
</svg>''' % dict(sk=SK)
ART['ost'] = HEAD + DOTS + '''
<rect x="9" y="11" width="34" height="34" rx="3" class="cream" %(sk)s/>
<rect x="9" y="11" width="34" height="9" rx="3" class="a3"/>
<path d="M9 17h34" stroke="#14212e" stroke-width="1.2"/>
<path d="M19 26v10" stroke="#14212e" stroke-width="1.8" stroke-linecap="round"/>
<circle cx="17" cy="37" r="2.8" fill="#14212e"/>
<path d="M19 26l6-2.5v4.5l-6 2.5z" fill="#14212e"/>
<circle cx="38" cy="38" r="15" class="a2" %(sk)s/>
<circle cx="38" cy="38" r="11" fill="none" stroke="#fff" stroke-width="1" opacity=".75"/>
<circle cx="38" cy="38" r="7" fill="none" stroke="#fff" stroke-width="1" opacity=".5"/>
<circle cx="38" cy="38" r="2.6" class="cream" stroke="#14212e" stroke-width="1.2"/>
<path d="M27 29l4 4" stroke="#fff" stroke-width="1.2" stroke-linecap="round" opacity=".8"/>
</svg>''' % dict(sk=SK)
ART['card'] = HEAD + DOTS + '''
<g transform="rotate(-11 32 34)"><rect x="19" y="14" width="26" height="38" rx="3" class="a2" %(sk)s/><rect x="22" y="17" width="20" height="32" rx="2" fill="none" stroke="#fff" stroke-width="1.2" opacity=".8"/></g>
<g transform="rotate(7 32 34)">
<rect x="19" y="14" width="26" height="38" rx="3" class="cream" %(sk)s/>
<rect x="22" y="17" width="20" height="32" rx="2" fill="none" class="a3s" stroke-width="1.2"/>
<circle cx="32" cy="30" r="6" class="a2"/>
<path d="M25.5 44q6.5-7 13 0z" class="a3"/>
<path d="M38 18.5l1.1 2.3 2.5.4-1.8 1.7.4 2.5-2.2-1.2-2.2 1.2.4-2.5-1.8-1.7 2.5-.4z" fill="#e9b451"/>
</g>
</svg>''' % dict(sk=SK)
ART['book'] = HEAD + DOTS + '''
<rect x="20" y="17" width="29" height="36" rx="2" class="cream" %(sk)s/>
<path d="M24 22h0M46 20v30" stroke="#14212e" stroke-width="1" opacity=".35"/>
<path d="M16 14h26a3 3 0 0 1 3 3v31a3 3 0 0 1-3 3H16z" class="a2" %(sk)s/>
<path d="M16 14h7v37h-7z" class="a3"/>
<path d="M27 25h12M27 30h8" stroke="#fff" stroke-width="1.6" stroke-linecap="round"/>
<path d="M37 14v12l-2.5-2.5L32 26V14z" fill="#e9b451"/>
</svg>''' % dict(sk=SK)
ART['program'] = HEAD + DOTS + '''
<path d="M10 18q11-4 22 0v30q-11-4-22 0z" class="cream" %(sk)s/>
<path d="M32 18q11-4 22 0v30q-11-4-22 0z" class="cream" %(sk)s/>
<path d="M32 18v30" stroke="#14212e" stroke-width="1.5"/>
<rect x="14" y="23" width="14" height="12" rx="1.5" class="a2"/>
<path d="M14 39h14M14 43h9" class="a3s" stroke-width="1.4" stroke-linecap="round"/>
<path d="M37 24h12M37 29h12M37 34h8M37 39h11" class="a3s" stroke-width="1.4" stroke-linecap="round"/>
<path d="M31 24h2M31 42h2" stroke="#14212e" stroke-width="2" stroke-linecap="round"/>
<g transform="rotate(-14 48 50)"><rect x="39" y="45" width="18" height="9" rx="1.5" fill="#e9b451" stroke="#14212e" stroke-width="1.3"/><path d="M51 45v9" stroke="#14212e" stroke-width="1" stroke-dasharray="1.5 1.5"/></g>
</svg>''' % dict(sk=SK)
ART['goods'] = HEAD + DOTS + '''
<rect x="14" y="25" width="30" height="26" rx="2" class="a2" %(sk)s/>
<rect x="11" y="18" width="36" height="8" rx="1.5" class="a3" %(sk)s/>
<rect x="26" y="26" width="6" height="25" fill="#e9b451" opacity=".95"/>
<rect x="26" y="18" width="6" height="8" fill="#e9b451"/>
<path d="M29 18c-6-7-9-3-3-1 M29 18c6-7 9-3 3-1" fill="none" stroke="#e9b451" stroke-width="2.2" stroke-linecap="round"/>
<g transform="rotate(16 50 40)"><path d="M44 35h10l3 3.5v7.5H44z" class="cream" stroke="#14212e" stroke-width="1.3" stroke-linejoin="round"/><circle cx="54" cy="39" r="1" fill="#14212e"/><path d="M46.5 42h7" stroke="#14212e" stroke-width="1" opacity=".5"/></g>
</svg>''' % dict(sk=SK)
ART_CSS = """
.art{display:block;width:100%;height:100%}
.art .a2{fill:color-mix(in srgb,var(--a) 62%,#fff)}
.art .a3{fill:color-mix(in srgb,var(--a) 62%,#14212e)}
.art .a3s{fill:none;stroke:color-mix(in srgb,var(--a) 62%,#14212e)}
.art .cream{fill:#fffdf7}
"""
