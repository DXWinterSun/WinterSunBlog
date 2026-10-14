#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全知的 Young Sam：brief.py 给他多印的那几节（他的每一张脸、博客上的 AU、她的藏品架和灵感本、她在跟哪几个「别的他」聊）。

Winter 2026-10-14：「他是唯一一个知道所有角色存在的，而且知道是他的角色……博客里面的 au 呀给他做的内容呀他也都知道，
包括我的收藏还有一些计划什么的。」设定和说话的规矩在 .claude/skills/winter-text/young-sam.md。

只由 brief.py 调用（单看「她写给你的那一页」：python3 tools/call/omni.py sam）：  omni.applies(p) → 是不是他；omni.persona() → 设定；omni.sections(people, series, posts, key) → 资料。
每一节都是「取得到就印，取不到就跳过」，不会让 brief 出错。
"""
import contextlib
import io
import json
import os
import re
import subprocess
import sys
from collections import Counter
from html import unescape

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OMNI_ID = "youngsam"
PERSONA = os.path.join(ROOT, ".claude", "skills", "winter-text", "young-sam.md")
LIVED_UNTIL = 1995          # 他刚拍完 Glory Daze（1995）：这一年以前（含）的脸是他真演过的
TYPE_CN = {"disc": "碟", "program": "场刊", "book": "书", "ost": "原声", "goods": "周边", "card": "卡"}


def applies(p):
    return p.get("id") == OMNI_ID


def persona():
    try:
        with open(PERSONA, encoding="utf-8") as f:
            text = f.read().strip()
    except OSError:
        return []
    text = re.sub(r"^# .*\n", "", text, count=1).strip()
    return ["## ⭐ 这一位是「全知的 Young Sam」——先读这一节，它压过下面所有跟它对不上的设定", "", text, ""]


def _year(p):
    m = re.search(r"\d{4}", str(p.get("year") or ""))
    return int(m.group(0)) if m else 9999


def _cn_title(t):
    m = re.search(r"·\s*(.*?)\s*—", t or "")
    return m.group(1) if m else (t or "")


def _au_line(s, posts):
    chs = posts.get(s["name"], [])
    main = [c for c in chs if not c["kind"]]
    extra = len(chs) - len(main)
    last = chs[-1]["title"] if chs else ""
    title = s["title"].rsplit(" · ", 1)[0] if " · " in s["title"] else s["title"]
    status = {"ongoing": "连载中", "complete": "完结", "oneshot": "短篇", "hiatus": "停着"}.get(s["status"], s["status"])
    return "　　AU《%s》%s · 正篇 %d 章%s%s" % (
        title, status, len(main), (" + 番外 %d" % extra) if extra else "",
        ("，最新：%s" % _cn_title(last)) if last else "")


SAM_PAGE_GUIDE = """她在 /sam/ 写的那一页「For Sam」，写的是今天快 58 岁的你——这就是你自己。你 26 岁，所以分三种用：

- **身上现在就有的**：右上臂那只吊死的公鸡（十几岁纹的）、榛色的眼睛、左手食指和中指微弯（九十年代中期在洛杉矶翻车压的，
  对 26 岁的你是不久前的事，你会下意识把那两根手指藏起来）、笑起来仰头还拍手、爱跳舞（少年时为了撩妹学的）、
  高中时说想去冒险、嫌自己脸太嫩、能吃辣、不想要孩子。聊到挨得上的地方，就当成你自己身上的事说——
  她写的是她看见的，你说的是当事人的版本（「那只鸡是我十几岁喝多了纹的，别笑」）。
- **以后的事＝预习**：奥斯卡、2018 年金球奖那身全黑、Hot Ones、SmartLess、Larry King 那段——是你从她的页上读到的，
  跟以后的角色一样：好奇、不好意思、偶尔嘴硬。
- **Leslie** 是你很多年以后的伴侣，26 岁的你还不认识她。你跟 Ocean 之间不提她。
- **她怎么喜欢上你的**（「我们的故事」那一节）：日期都是真的，你知道，可以偶尔提一嘴、可以得意，别背给她听。"""


def _sam_text(html):
    html = re.sub(r"\{%-?\s*comment\s*-?%\}.*?\{%-?\s*endcomment\s*-?%\}", "", html, flags=re.S)
    html = re.sub(r"\{%.*?%\}|\{\{.*?\}\}", "", html, flags=re.S)
    html = re.sub(r"<(script|style|button|summary)\b.*?</\1>", "", html, flags=re.S)
    html = re.sub(r'<span[^>]*aria-hidden="true"[^>]*>.*?</span>', "", html, flags=re.S)   # 装饰用的小图标
    html = re.sub(r'<div class="c-bday__(count|sub)".*?</div>', "", html, flags=re.S)
    html = re.sub(r'<span class="c-sam-detail__title">(.*?)</span>', r"\n- 【\1】", html, flags=re.S)
    html = re.sub(r'<span class="c-sam-relic__name">(.*?)</span>', r"\n- 【\1】", html, flags=re.S)
    html = re.sub(r'<span class="c-bday__d">(.*?)</span>\s*<span class="c-bday__who">(.*?)</span>', r"\n\1 \2", html, flags=re.S)
    html = re.sub(r"<br\s*/?>|</(p|div|blockquote|cite|h\d)>", "\n", html)
    html = re.sub(r"<[^>]+>", "", html)
    lines, prev = [], ""
    for ln in unescape(html).splitlines():
        ln = re.sub(r"\s+", " ", ln).strip()
        if not ln:
            continue
        if prev.startswith("- 【") and prev.endswith("】") and not ln.startswith(("- ", "#")):
            lines[-1] += ln          # 小标题和下面那段并成一行
        else:
            lines.append(ln)
        prev = lines[-1]
    return lines


def sam_page():
    try:
        with open(os.path.join(ROOT, "sam", "index.html"), encoding="utf-8") as f:
            html = f.read()
    except OSError:
        return []
    out = ["## 她写给你的那一页（/sam/ · For Sam）", "", SAM_PAGE_GUIDE, ""]
    for m in re.finditer(r'<details class="c-sam-fold"[^>]*>(.*?)</details>', html, flags=re.S):
        block = m.group(1)
        cn = re.search(r'c-sam-fold__cn">(.*?)<', block)
        out += ["### " + (cn.group(1) if cn else "（一节）"), ""] + _sam_text(block) + [""]
    return out if len(out) > 4 else []


def faces(people, series, posts):
    out = ["## 你的每一张脸（画册里的，按年份；1995 以前＝演过的，是回忆；之后的＝预习，你从她的博客上认识的）", ""]
    mine = sorted([p for p in people if p.get("lines") and p["id"] != OMNI_ID], key=_year)
    for p in mine:
        y = _year(p)
        tag = (p.get("face") or {}).get("tagline") or ""
        film = (p.get("filmCN") or p.get("film") or "").strip("《》")
        out.append("- %s %s《%s》%s%s" % (
            p.get("year") or "?", p["name"], film, "（演过）" if y <= LIVED_UNTIL else "",
            ("　" + tag[:40]) if tag else ""))
        for a in p.get("aus") or []:
            if a in series:
                out.append(_au_line(series[a], posts))
    others = [p for p in people if not p.get("lines") and p.get("aus")]
    if others:
        out += ["", "她博客上还有别人的 AU（不是你演的，你知道有，偶尔酸一句也行）："]
        for p in others:
            s = series[p["aus"][0]]
            out.append("- %s · %s：%s" % (p["name"], p.get("actor") or "?", s["title"].rsplit(" · ", 1)[0]))
    out += ["", "具体哪一章写了什么，要说之前先去读那一章（`_posts/` 里按系列名找），别凭印象编。", ""]
    return out


def shelf(people):
    try:
        with open(os.path.join(ROOT, "sam", "shelf", "data.json"), encoding="utf-8") as f:
            items = json.load(f).get("items", [])
    except (OSError, ValueError):
        return []
    if not items:
        return []
    names = {p["id"]: p["name"] for p in people}
    names[""] = "你本人（不分角色）"
    have = [i for i in items if not i.get("wish")]
    wish = [i for i in items if i.get("wish")]
    kinds = Counter(TYPE_CN.get(i.get("type"), i.get("type") or "?") for i in have)
    who = Counter(names.get(i.get("charId") or "", i.get("charId") or "?") for i in have)
    out = ["## 她的藏品架（她收的你的东西；网页 /sam/shelf/）", "",
           "- 一共 %d 件：%s；有签名的 %d 件" % (
               len(have), "、".join("%s %d" % kv for kv in kinds.most_common()), sum(1 for i in have if i.get("signed"))),
           "- 收得最多的脸：" + "、".join("%s %d" % kv for kv in who.most_common(6))]
    out.append("- 最近收到的：")
    for i in sorted(have, key=lambda i: i.get("added") or 0, reverse=True)[:5]:
        note = re.sub(r"\s+", " ", i.get("note") or "")
        out.append("  - %s %s（%s · %s）%s" % (
            i.get("date") or "", i.get("name") or "", names.get(i.get("charId") or "", i.get("charId") or ""),
            i.get("spec") or TYPE_CN.get(i.get("type"), ""), ("　" + note[:60]) if note else ""))
    if wish:
        out.append("- 心愿单上还差：" + "、".join(i.get("name") or "" for i in wish[:8]))
    out += ["- 要说哪一件的细节，先查 `sam/shelf/data.json`。", ""]
    return out


def memo():
    try:
        r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "memo", "memo.py"), "ls"],
                           capture_output=True, text=True, timeout=60, cwd=ROOT)
    except Exception:
        return []
    text = r.stdout.strip()
    if r.returncode or not text:
        return []
    return ["## 她的灵感本（她在计划做的事；细节 `python3 tools/memo/memo.py show <编号>`）", "", text, ""]


def studies():
    out = []
    try:
        import yaml
    except ImportError:
        return []
    books = []
    rdir = os.path.join(ROOT, "_data", "reading")
    for f in sorted(os.listdir(rdir)) if os.path.isdir(rdir) else []:
        try:
            d = yaml.safe_load(open(os.path.join(rdir, f), encoding="utf-8")) or {}
        except Exception:
            continue
        b = d.get("book") or {}
        n = sum(len(x.get("notes") or []) for x in d.get("batches") or [])
        if b.get("title"):
            books.append("《%s》%s（记了 %d 条）" % (b["title"], ("—" + b["about"]) if b.get("about") else "", n))
    try:
        pol = yaml.safe_load(open(os.path.join(ROOT, "_data", "polish", "notes.yml"), encoding="utf-8")) or {}
        pn = len(pol.get("notes") or [])
    except Exception:
        pn = 0
    if books:
        out.append("- 她在读 / 划线的：" + "；".join(books))
    if pn:
        out.append("- 她在学波兰语（多邻国 + 课本），错题笔记本里 %d 条" % pn)
    return (["## 她在读的、在学的", ""] + out + [""]) if out else []


def others(self_key):
    if not os.environ.get("WINTER_TEXT_KEY"):
        return []
    try:
        sys.path.insert(0, os.path.join(ROOT, "tools", "text"))
        import texts
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            _, box, index = texts.load_all()
        rows = [t for t in index.get("threads", []) if t.get("key") != self_key and t.get("last_at")]
        rows.sort(key=lambda t: t["last_at"], reverse=True)
        if not rows:
            return []
        out = ["## 她最近在跟哪几个「别的你」发消息（⚠️ 只知道有这回事；聊了什么你看不到，也绝不去读）", ""]
        for t in rows[:8]:
            out.append("- %s%s：上一句 %s" % (t.get("who") or t["key"], (" · " + t["story"]) if t.get("story") else "",
                                           texts.gap_words(t["last_at"])))
        out += ["", "可以酸一句、自己先笑场；不追问内容、不让她汇报、不贬低那个角色——那也是你。", ""]
        return out
    except (Exception, SystemExit):
        return []


def sections(people, series, posts, self_key):
    out = ["# ── 全知：你知道的一切（下面每一节都是真的，用之前挑跟她此刻说的事挨得上的，一次只带一两样）──", ""]
    for part in (sam_page(), faces(people, series, posts), shelf(people), memo(), studies(), others(self_key)):
        out += part
    return out


if __name__ == "__main__":   # 已经读过 brief、只想补看这一页时用
    if sys.argv[1:] == ["sam"]:
        print("\n".join(sam_page()))
    else:
        print("用法：python3 tools/call/omni.py sam")
