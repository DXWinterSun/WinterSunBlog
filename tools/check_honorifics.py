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
            (r"你(说|问|喊)", "她"),
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
            # 她的台词：绝不会把自己的爹妈叫成「您父亲／您母亲」
            "她": {
                "forbid": ["您父亲", "您母亲", "您妈", "您爹"],
                "why": "她自己的爹妈，她只会说「我父亲／我母亲」——出现「您父亲」＝说话人串了",
            },
            # 父亲 → 女儿：用「你」（考据：19C 意大利父母对子女用 tu）
            "父亲": {
                "forbid": ["您"],
                "allow_if_quote_has": ["先生", "神父"],   # 他对神父说话才用「您」
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
        # 叙述（引号外）里不许出现的第一人称
        "narration_forbid": ["我父亲", "我母亲", "我们站", "我旁边", "我家里那"],
        "narration_why": "本系列是第二人称叙述（你），叙述里不该有「我」的所有格",
        # 只列出来人工过一遍的（歧义说话人）
        "review_keys": ["他?", "她?", None],
    },
}

QUOTE_RE = re.compile(r"“([^”]*)”")
CJK_CURLY_BAD = "「』』"


def speaker_of(line, attrib):
    for pat, key in attrib:
        if re.search(pat, line):
            return key
    return None


def check_file(path, cfg, list_mode=False):
    errors, reviews = [], []
    text = open(path, encoding="utf-8").read()
    in_html = False
    for i, line in enumerate(text.split("\n"), 1):
        # 跳过内嵌 HTML 卡片（c-note / c-decree / c-comm）
        if re.match(r"\s*<div", line):
            in_html = True
        if in_html:
            if "</div>" in line and not re.search(r"<div", line):
                in_html = False
            continue

        quotes = QUOTE_RE.findall(line)

        # ① 叙述（把引号内容挖掉之后）里的第一人称
        bare = QUOTE_RE.sub("", line)
        if not bare.lstrip().startswith(">"):
            for w in cfg.get("narration_forbid", []):
                if w in bare:
                    errors.append((i, "叙述第一人称", w, bare.strip()[:70],
                                   cfg.get("narration_why", "")))

        if not quotes:
            continue
        spk = speaker_of(line, cfg["attrib"])
        rule = cfg["rules"].get(spk)

        near = "".join(text.split("\n")[max(0, i - 3): i + 2])
        for q in quotes:
            if rule:
                allow = any(a in q for a in rule.get("allow_if_quote_has", []))
                if not allow and "神父" in rule.get("allow_if_quote_has", []) and "神父" in near:
                    allow = True
                for w in rule["forbid"]:
                    if w in q and not allow:
                        errors.append((i, f"{spk} 的对白", w, q[:70], rule["why"]))
                        break
            if list_mode and ("您" in q or "你" in q):
                reviews.append((i, spk or "（没有提示语）", q[:70]))
            elif not rule and spk in cfg.get("review_keys", []) and ("您" in q or "你" in q):
                reviews.append((i, spk or "（没有提示语）", q[:70]))
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
