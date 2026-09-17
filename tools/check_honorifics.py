#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_honorifics.py —— 按「谁在说话」查人称／称呼，不是按字查。

为什么有这个脚本（2026-09-16）：
  I Kissed the Stones 写到 Ch18/Ch19 时，连着出过三次同一类错——
    ① 父亲对女儿说「您」（应当是「你」）；
    ② Lorenzo（她一块儿长大的玩伴）对她说「您」（应当是「你」）；
    ③ 她自己的台词里出现「您父亲」（她只会说「我父亲」）——说话人串了；
    ④ 叙述里冒出「我父亲」「我们站着」（第二人称叙述里漏进第一人称）。
  而 check_desino.py 不管人称，`grep 你` 又看不出是谁在说，
  所以每次「验过了」验的都不是出问题的那一项。这个脚本专治这一类。

用法：
  python3 tools/check_honorifics.py .claude/bibles/i-kissed-the-stones-revised/ch19.md
  python3 tools/check_honorifics.py _posts/2026-10-*.md
  python3 tools/check_honorifics.py --list <文件>     # 列出全部带你/您的对白供人工过一遍
  python3 tools/check_honorifics.py --series slow-hands <文件>   # 换系列的规则表

退出码：发现 ERROR → 1；只有 REVIEW / 无问题 → 0。

⚠️ 规则表在下面 SERIES 里，新系列照抄一份改即可。
"""
import re
import sys
import glob

# ───────────────────────── 规则表（每个系列一份） ─────────────────────────
# speakers: 说话人 → 归一化的角色 key
#   attribution 的写法按正文实际用的提示语来配（“…”X说 / X说，“…”）
# rules:
#   forbid_in_quote: 这个角色的对白里不许出现的词
#   allow_if_quote_has: 命中 forbid 但对白里同时有这些词 → 放行（多为「转述对别人说的话」）
SERIES = {
    "i-kissed-the-stones": {
        "title": "I Kissed the Stones · Francis Flute AU",
        # 说话人识别：正则 → 角色 key
        "attrib": [
            (r"你$|^你", "她"),
            (r"Emilia", "Emilia"),
            (r"你父亲说", "父亲"),
            (r"Lorenzo\s*说", "Lorenzo"),
            (r"Chiara\s*说", "Chiara"),
            (r"神父说", "神父"),
            (r"Baldi\s*说", "Baldi"),
            (r"Baldi\s*太太说", "Baldi太太"),
            (r"Vannucci\s*太太说", "Vannucci太太"),
            (r"Snug\s*说", "Snug"),
            (r"Bottom\s*说", "Bottom"),
            (r"Quince\s*说", "Quince"),
            (r"母亲说", "母亲"),
            (r"Nella\s*说", "Nella"),
            (r"他说", "他?"),          # 歧义：多半是 Flute，也可能是父亲/Lorenzo → 只列不判
            (r"她说", "她?"),
        ],
        "rules": {
            # ⭐⭐⭐ 第②把锁：他对她永远「您」，一个「你」都不许有（到结局才开）
            "他": {
                "forbid": ["你"],
                "allow_if_quote_has": ["他说你", "你看吧"],   # 他转述别人说的话
                "why": "第②把锁：Flute 对她一律「您」，⚠️ 到结局才第一次说「你」",
            },
            "Emilia": {
                "forbid": ["你"],
                "why": "Emilia 是九岁的学生，那个年代孩子对先生用敬称 → 「您」",
            },
            # 她的台词：绝不会把自己的爹妈叫成「您父亲／您母亲」
            "她": {
                "forbid": ["您父亲", "您母亲", "您妈", "您爹"],
                "why": "她自己的爹妈，她只会说「我父亲／我母亲」——出现「您父亲」＝说话人串了",
            },
            # 父亲 → 女儿：用「你」（考据：19C 意大利父母对子女用 tu）
            "父亲": {
                "forbid": ["您"],
                "allow_if_quote_has": ["先生"],
                "allow_if_near": ["神父"],   # 他对神父说话才用「您」
                "why": "父亲对女儿一律「你」；只有他对神父说话才用「您」",
            },
            # Lorenzo：与她一块儿长大、同一个阶层 → 「你」
            "Lorenzo": {
                "forbid": ["您"],
                "allow_if_quote_has": ["先生", "您女儿"],  # 他转述自己对她父亲说的话
                "why": "Lorenzo 是一块儿长大的玩伴、同阶层 → 对她用「你」（Ch9/Ch11 已定）",
            },
            "Chiara": {
                "forbid": ["您"],
                "why": "Chiara 同上，闺中玩伴 → 「你」",
            },
        },
        # ⚠️ 已人工核过、确实不是 Flute 的「他」（分场里没提名字，脚本解析不出来）
        #    ——每加一条都要写清真正的说话人，别拿它当消错工具
        "ambiguous_ok": [
            "你对我好，一直都好。你什么礼都不缺，什么话都听完。",        # Ch11 Lorenzo
            "可是你看我的时候是空的。",                                  # Ch11 Lorenzo（同段）
            "你母亲每个礼拜四还让人把那间屋子的琴擦一遍。",              # Ch18 父亲
            "你那位。",                                                  # Ch19 Lorenzo
            # Ch11 园子里那一整场（她跟 Lorenzo 谈「我不愿意」）通篇只写「他」，
            # 这六句全是 Lorenzo 说的：
            "你不用对不住。",
            "你又没有骗我。",
            "那对你不好。",
            "镇上会说你。",
            "可要是那个人真的值得你走这一步",
            "——你叫他小心点。",
        ],
        # 叙述（引号外）里不许出现的第一人称
        "narration_forbid": ["我父亲", "我母亲", "我们站", "我旁边", "我家里那"],
        "narration_why": "本系列是第二人称叙述（你），叙述里不该有「我」的所有格",
        # 只列出来人工过一遍的（歧义说话人）
        "review_keys": ["他?", "她?", None],
    },
}

QUOTE_RE = re.compile(r"“([^”]*)”")

# 引号边界上的提示语：”X说 / X说，“
ATTR_AFTER = re.compile(r"”\s*([^，。！？“”]{0,10}?)(说|问|答|喊|念)")
ATTR_BEFORE = re.compile(r"([^，。！？“”]{0,10}?)(说|问|答|喊|念)[，：]?\s*“")

# 提示语碎片 → 角色
def norm(frag, cfg):
    for pat, key in cfg["attrib"]:
        if re.search(pat, frag):
            return key
    if frag.strip() in ("他", "他又", "他小声", "他重复了一遍"):
        return "他?"
    if frag.strip() in ("她", "她又"):
        return "她?"
    return None


# 一章里除 Flute 之外的男性说话人（用来判断「他」是不是 Flute）
OTHER_MEN = ("父亲", "Lorenzo", "Bottom", "Quince", "Snug", "Snout", "Starveling",
             "Bardi", "Baldi", "神父", "Don Pietro", "管事", "铁匠", "那个人")


MALE_KEYS = ("父亲", "Lorenzo", "Bottom", "Quince", "Snug", "Snout",
             "Bardi", "Baldi", "神父", "Starveling")


def resolve(line, lines, idx, cfg, scene_male):
    """返回 (角色, 是否为推断)。scene_male = 本场里最近一个有名有姓的男性说话人。"""
    frags = [m.group(1) for m in ATTR_AFTER.finditer(line)] + \
            [m.group(1) for m in ATTR_BEFORE.finditer(line)]
    for fr in frags:
        k = norm(fr, cfg)
        if k and k not in ("他?", "她?"):
            return k, False
    for fr in frags:
        k = norm(fr, cfg)
        if k == "他?":
            # 本场里出现过别的男人 → 歧义，只列不判；否则「他」就是 Flute
            return (("他?", True) if scene_male else ("他", False))
        if k == "她?":
            return "她?", True
    return None, True


def check_file(path, cfg, list_mode=False):
    errors, reviews = [], []
    text = open(path, encoding="utf-8").read()
    lines = text.split("\n")
    in_html = False
    scene_male = None
    for i, line in enumerate(lines, 1):
        if re.match(r"^-{3,}\s*$", line):
            scene_male = None          # 分场，重置「本场出现过哪个男人」
        # 本场里只要（叙述或提示语里）出现过别的男人，「他」就算歧义
        for _m in ("父亲", "Lorenzo", "Bottom", "Quince", "Snug", "Snout",
                   "Bardi", "Baldi", "神父", "Don Pietro", "Starveling",
                   "铁匠", "管钟"):
            if _m in line:
                scene_male = _m
                break
        if re.match(r"\s*<div", line):
            in_html = True
        if in_html:
            if "</div>" in line and not re.search(r"<div", line):
                in_html = False
            continue

        quotes = QUOTE_RE.findall(line)

        # ① 叙述（挖掉引号内容）里的第一人称
        bare = QUOTE_RE.sub("", line)
        if not bare.lstrip().startswith(">"):
            for w in cfg.get("narration_forbid", []):
                if w in bare:
                    errors.append((i, "叙述第一人称", w, bare.strip()[:70],
                                   cfg.get("narration_why", "")))
        if not quotes:
            continue

        spk, guessed = resolve(line, lines, i - 1, cfg, scene_male)
        rule = cfg["rules"].get(spk)
        near = "".join(lines[max(0, i - 4): i + 3])

        for q in quotes:
            if rule:
                allow = any(a in q for a in rule.get("allow_if_quote_has", []))
                if not allow:
                    for ctxw in rule.get("allow_if_near", []):
                        if ctxw in near:
                            allow = True
                            break
                if not allow and any(q.startswith(x[:14]) for x in cfg.get("ambiguous_ok", [])):
                    allow = True
                if not allow:
                    for w in rule["forbid"]:
                        if w in q:
                            errors.append((i, f"{spk} 的对白", w, q[:70], rule["why"]))
                            break
            if ("您" in q or "你" in q) and (list_mode or spk is None or guessed):
                reviews.append((i, (spk or "？") + ("（推断）" if guessed else ""), q[:70]))
    return errors, reviews


def main():
    args = sys.argv[1:]
    series = "i-kissed-the-stones"
    list_mode = False
    files = []
    it = iter(range(len(args)))
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--series":
            series = args[i + 1]; i += 2; continue
        if a in ("--list", "-l"):
            list_mode = True; i += 1; continue
        files.extend(glob.glob(a) or [a]); i += 1

    files = [f for f in files if not f.endswith("-notes.md")]

    if series not in SERIES:
        print(f"没有 {series} 的规则表，照 SERIES 里现成的抄一份。")
        return 2
    cfg = SERIES[series]
    if not files:
        print(__doc__)
        return 2

    bad = 0
    for path in sorted(files):
        errors, reviews = check_file(path, cfg, list_mode)
        head = f"检查：{path}"
        print(f"\n{head}\n" + "─" * 56)
        if errors:
            bad += len(errors)
            print(f"  ❌ ERROR（{len(errors)} 处）")
            for ln, who, word, ctx, why in errors:
                print(f"     L{ln} [{who}] 出现「{word}」")
                print(f"        {ctx}")
                print(f"        → {why}")
        if reviews:
            print(f"  👀 人工过一遍（{len(reviews)} 处，说话人有歧义或 --list）")
            for ln, who, q in reviews:
                print(f"     L{ln} [{who}] {q}")
        if not errors and not reviews:
            print("  ✅ 没有发现人称问题")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
