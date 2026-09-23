#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
色卡全站同步校验 —— Many Faces 画册是唯一「真源」。

Sam 每个角色的配色（bg / accent / text / muted + 四个中英色名）在全站有 5 份拷贝，
它们必须始终一致。一旦有人改了画册里某个角色的色卡，其余各处都要一起改，
否则某个彩蛋 / 系列就会显示旧色。本脚本就是那道防线：

  真源：  sam/many-faces/index.html   （const characters 数组，每个角色全字段）
  拷贝：  sam/quiz/index.html         （const CHARS，4 色）
          sam/spectrum/index.html     （const CHARS，4 色）
          _data/sam_themes.yml        （换个心情选色器，4 色 + 4 色名，按 anchor 对应）
          sam/lines.json              （characters[] + pool[]，4 色，wall/today/widget/projector 共用）
          _data/au_palettes.yml        （AU 系列专属主题，仅带 mf_id 的条目）

⚠️ au_palettes 的 text / muted 是「各系列为阅读主题单独微调」的，历来就与画册不同，
   不算 desync —— 本脚本对 au_palettes 只校验 accent / bg / 四个色名（不校验 text/muted）。
   accent_ink 是 accent 手动暗一档派生的，也不校验。

用法：  python3 tools/check_palette_sync.py
返回：  全部一致 → exit 0；发现 desync → 打印差异并 exit 1。
"""
import re, json, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def read(p): return open(os.path.join(ROOT, p), encoding="utf-8").read()

COLOR = ["bg", "accent", "text", "muted"]

# ── 真源：画册 many-faces ────────────────────────────────────────────────
def _field(block, key):
    m = re.search(r'\b' + key + r'\s*:\s*"([^"]*)"', block)
    return m.group(1).strip() if m else None

def parse_many_faces():
    text = read("sam/many-faces/index.html")
    chars = {}
    for m in re.finditer(r'\bid:\s*"([^"]+)"', text):
        cid = m.group(1)
        block = text[m.start():m.start() + 3000]
        pm = re.search(r'profile\s*:\s*\{[^}]*\}', block)
        if pm:
            block = block[:pm.end() + 2]
        rec = {k: _field(block, k) for k in COLOR}
        rec.update({
            "bgNameEn": _field(block, "bgNameEn"), "bgNameCn": _field(block, "bgNameCn"),
            "accentNameEn": _field(block, "accentNameEn"), "accentNameCn": _field(block, "accentNameCn"),
            "textNameEn": _field(block, "textNameEn"), "textNameCn": _field(block, "textNameCn"),
            "mutedNameEn": _field(block, "mutedNameEn"), "mutedNameCn": _field(block, "mutedNameCn"),
        })
        if rec["bg"] and rec["accent"]:
            chars[cid] = rec
    return chars

# ── 拷贝：quiz / spectrum 的 CHARS（4 色，id 可能带别名）────────────────────
# many-faces id  ->  quiz/spectrum id
JS_ALIAS = {"sam": "sambell", "john": "johnmoon", "hendrix": "klenz"}

def parse_js_chars(path):
    text = read(path)
    chars = {}
    pat = re.compile(
        r'\{[^{]*?id:\s*"([^"]+)"[^{]*?bg:\s*"([^"]+)"[^{]*?accent:\s*"([^"]+)"'
        r'[^{]*?text:\s*"([^"]+)"[^{]*?muted:\s*"([^"]+)"')
    for m in pat.finditer(text):
        chars[m.group(1)] = {"bg": m.group(2), "accent": m.group(3),
                             "text": m.group(4), "muted": m.group(5)}
    return chars

# ── 拷贝：sam_themes.yml（按 anchor 对应画册 id）────────────────────────────
def parse_sam_themes():
    import yaml
    out = {}
    for t in yaml.safe_load(read("_data/sam_themes.yml")):
        out[t["anchor"]] = t
    return out

# ── 拷贝：lines.json（characters + pool）────────────────────────────────────
def parse_lines():
    return json.loads(read("sam/lines.json"))

# ── 拷贝：au_palettes.yml（仅 mf_id 条目，只比 accent/bg/色名）───────────────
def parse_au():
    import yaml
    return yaml.safe_load(read("_data/au_palettes.yml"))


# ── 「他的 AU 在哪」链路：auLink 四处同步 ──────────────────────────────────
# 画册 many-faces 里给某个角色写了 auLink/auLinks，就等于宣布「他有 AU」。
# 这个事实还要在三处拷贝里同样成立，否则那里就当他没有 AU：
#   sam/quiz、sam/spectrum  → 结果页少一个「去读他的 AU」
#   sam/lines.json          → 热线通讯录、系列页「打给他」、放映室、台词墙全认不出他
# （2026-09 真的翻过车：Gary O'Hara / Jerry / Billy Bickle / Eddie 四个人
#   画册里明明挂着 AU，lines.json 里却是空的。）
def mf_au_ids(text):
    ids = [(m.start(), m.group(1)) for m in re.finditer(r'^\s+id:\s*"([^"]+)"', text, re.M)]
    out = set()
    for m in re.finditer(r'^\s+auLinks?:', text, re.M):
        before = [i for p, i in ids if p < m.start()]
        if before:
            out.add(before[-1])
    return out

def js_au_ids(text):
    out = set()
    for m in re.finditer(r'\bid:\s*"([^"]+)"', text):
        block = text[m.start():m.start() + 3000]
        nxt = block.find('id:"', 5)
        if nxt < 0:
            nxt = block.find('id: "', 5)
        if nxt > 0:
            block = block[:nxt]
        am = re.search(r'auLink\s*:\s*("([^"]*)"|null)', block)
        if am and am.group(2):
            out.add(m.group(1))
    return out


def main():
    mf = parse_many_faces()
    issues = []

    def cmp_color(label, cid, ref, other):
        for k in COLOR:
            if ref.get(k) and other.get(k) and ref[k].lower() != other[k].lower():
                issues.append(f"[{label}] {cid} {k}: 画册={ref[k]} vs {other[k]}")

    # quiz / spectrum
    for label, path in [("quiz", "sam/quiz/index.html"), ("spectrum", "sam/spectrum/index.html")]:
        src = parse_js_chars(path)
        for cid, ref in mf.items():
            sid = JS_ALIAS.get(cid, cid)
            if sid not in src:
                issues.append(f"[{label}] 缺少角色 id={sid}（画册 {cid}）")
                continue
            cmp_color(label, cid, ref, src[sid])

    # sam_themes.yml (4 色 + 4 色名)
    themes = parse_sam_themes()
    for cid, ref in mf.items():
        t = themes.get(cid)
        if not t:
            issues.append(f"[sam_themes] 缺少 anchor={cid}")
            continue
        cmp_color("sam_themes", cid, ref, t)
        for f, mfk in [("cn", "accentNameCn"), ("en", "accentNameEn"),
                       ("bg_cn", "bgNameCn"), ("bg_en", "bgNameEn"),
                       ("text_cn", "textNameCn"), ("text_en", "textNameEn"),
                       ("muted_cn", "mutedNameCn"), ("muted_en", "mutedNameEn")]:
            if ref.get(mfk) and t.get(f) and ref[mfk] != t[f]:
                issues.append(f"[sam_themes] {cid} {f}: 画册={ref[mfk]} vs {t[f]}")
        # 四色八名标准（2026-07 起）：画册与选色器都必须有 text/muted 名字
        for mfk in ["textNameCn", "textNameEn", "mutedNameCn", "mutedNameEn"]:
            if not ref.get(mfk):
                issues.append(f"[many-faces] {cid} 缺 {mfk}（四色八名标准）")
        for f in ["text_cn", "text_en", "muted_cn", "muted_en"]:
            if not t.get(f):
                issues.append(f"[sam_themes] {cid} 缺 {f}（四色八名标准）")

    # lines.json characters + pool
    lines = parse_lines()
    alias = lines["meta"].get("mf_alias", {})   # charId -> 画册 id
    by_id = {c["id"]: c for c in lines["characters"]}
    for lid, c in by_id.items():
        mfid = alias.get(lid, lid)
        ref = mf.get(mfid)
        if not ref:
            issues.append(f"[lines.characters] id={lid} 在画册无对应({mfid})")
            continue
        cmp_color("lines.characters", lid, ref, c)
    for i, p in enumerate(lines["pool"]):
        c = by_id.get(p["charId"])
        if not c:
            issues.append(f"[lines.pool] pool[{i}] charId={p['charId']} 无对应角色")
            continue
        for k in COLOR:
            if p.get(k) and c.get(k) and p[k].lower() != c[k].lower():
                issues.append(f"[lines.pool] pool[{i}] {p['charId']} {k}: {p[k]} ≠ characters {c[k]}")

    # ── auLink 四处同步（画册为真源）────────────────────────────────────
    mf_au = mf_au_ids(read("sam/many-faces/index.html"))
    for label, path in [("quiz", "sam/quiz/index.html"), ("spectrum", "sam/spectrum/index.html")]:
        have = js_au_ids(read(path))
        for cid in mf_au:
            sid = JS_ALIAS.get(cid, cid)
            if sid not in have:
                issues.append(f"[auLink/{label}] {sid} 画册里有 AU，这里却没写 auLink")
    lines_au = {c["id"] for c in lines["characters"] if c.get("auLink")}
    for cid in mf_au:
        lid = {v: k for k, v in alias.items()}.get(cid, cid)
        if lid not in by_id:
            lid = cid
        if lid not in lines_au:
            issues.append(f"[auLink/lines.json] {lid} 画册里有 AU，lines.json 里却是空的 —— "
                          f"热线 / 系列页「打给他」会认不出他")
    for i, p in enumerate(lines["pool"]):
        c = by_id.get(p["charId"])
        if c and (p.get("auLink") or None) != (c.get("auLink") or None):
            issues.append(f"[auLink/lines.pool] pool[{i}] {p['charId']} 与 characters 不一致")

    # au_palettes.yml —— 只校验带 mf_id 的条目的 accent / bg / 四个色名
    au = parse_au()
    for series, v in au.items():
        if not isinstance(v, dict):
            continue
        mfid = v.get("mf_id")
        if not mfid:
            continue
        ref = mf.get(mfid)
        if not ref:
            issues.append(f"[au_palettes] '{series}' mf_id={mfid} 在画册无对应")
            continue
        for f, mfk in [("accent", "accent"), ("bg", "bg"),
                       ("accent_cn", "accentNameCn"), ("accent_en", "accentNameEn"),
                       ("bg_cn", "bgNameCn"), ("bg_en", "bgNameEn"),
                       # text/muted 的「色值」各系列可微调，但「名字」必须与画册一致
                       ("text_cn", "textNameCn"), ("text_en", "textNameEn"),
                       ("muted_cn", "mutedNameCn"), ("muted_en", "mutedNameEn")]:
            a, b = v.get(f), ref.get(mfk)
            if a and b and str(a).lower() != str(b).lower():
                issues.append(f"[au_palettes] '{series}' {f}: 画册={b} vs {a}")

    # ── 「穿上他的颜色」链路 ────────────────────────────────────────────
    # _includes/au-palette-strip.html 会用 mf_id 反查 sam_themes 里
    # anchor == mf_id 的那条，拿它的 id 挂成 data-au-theme。反查得到 → 选色器
    # 认成「预设色卡」，「当前」行显示角色名；反查不到 → 退成「直接上色」，
    # 显示成「AU 专属配色」，看着就不像画册角色（Francis Flute 就这么翻的车）。
    themes_by_anchor = {(t.get("anchor") or t["id"]): t["id"] for t in
                        __import__("yaml").safe_load(read("_data/sam_themes.yml"))}
    strip = read("_includes/au-palette-strip.html")
    if "p.theme_id" in strip:
        issues.append("[au-strip] 又出现手写 theme_id —— 该字段已废弃，改由 mf_id 反查 sam_themes 推导")
    for series, v in au.items():
        if not isinstance(v, dict):
            continue
        if v.get("theme_id"):
            issues.append(f"[au_palettes] '{series}' 还留着 theme_id —— 已废弃，删掉即可（由 mf_id 自动推导）")
        mfid = v.get("mf_id")
        if mfid and mfid not in themes_by_anchor:
            issues.append(f"[穿上他的颜色] '{series}' mf_id={mfid} 在 sam_themes 里查不到 anchor，"
                          f"按钮会退成「AU 专属配色」")

    # Sam 本人演的角色，系列色卡却没写 mf_id → 「穿上他的颜色」不会认成画册色卡。
    # 少数系列是有意独立设计的（见下表），其余都该补上 mf_id。
    AU_NO_MF_OK = {
        "Sanguis Benedicta",   # Wild Bill 血族哥特，有意独立配色，不跟画册同源
        "Wholly Known",        # Eddie Carbone（舞台剧），画册里没有这个角色
    }
    import glob as _glob
    for f in sorted(_glob.glob(os.path.join(ROOT, "series/*/index.html"))):
        src = open(f, encoding="utf-8").read()
        parts = src.split("---")
        if len(parts) < 3:
            continue
        try:
            fm = __import__("yaml").safe_load(parts[1]) or {}
        except Exception:
            continue
        if not fm.get("sam_collection"):
            continue
        key = fm.get("series_name")
        if key in AU_NO_MF_OK:
            continue
        v = au.get(key)
        if not isinstance(v, dict):
            issues.append(f"[穿上他的颜色] Sam 角色系列 '{key}' 在 au_palettes 里没有条目（会回退站点默认金色）")
        elif not v.get("mf_id"):
            issues.append(f"[穿上他的颜色] Sam 角色系列 '{key}' 缺 mf_id —— "
                          f"「穿上他的颜色」会显示成「AU 专属配色」，且没有「在 Many Faces 里找他」链接")

    if issues:
        print(f"✗ 发现 {len(issues)} 处色卡未同步（画册为真源）：\n")
        for i in issues:
            print("  " + i)
        print("\n改法：以画册 sam/many-faces/index.html 为准，把上述各处改回一致。")
        print("au_palettes 的 text/muted 不在校验范围（各系列有意微调）。")
        return 1

    print(f"✓ 色卡全站同步：{len(mf)} 个角色 × (quiz / spectrum / sam_themes / lines.json / au_palettes) 全部一致。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
