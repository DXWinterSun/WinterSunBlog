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
                       ("bg_cn", "bgNameCn"), ("bg_en", "bgNameEn")]:
            if ref.get(mfk) and t.get(f) and ref[mfk] != t[f]:
                issues.append(f"[sam_themes] {cid} {f}: 画册={ref[mfk]} vs {t[f]}")

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
                       ("bg_cn", "bgNameCn"), ("bg_en", "bgNameEn")]:
            a, b = v.get(f), ref.get(mfk)
            if a and b and str(a).lower() != str(b).lower():
                issues.append(f"[au_palettes] '{series}' {f}: 画册={b} vs {a}")

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
