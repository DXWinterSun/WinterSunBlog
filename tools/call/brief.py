#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""☎ 打给他 · 接通前把这个人的资料一次备齐（给对话里的 Claude 看，不给读者看）。

Winter 2026-10-12：「博客上不能做成那种和角色对话的，但我们可以在 Claude Code 的对话里实现吧……
code 的好处就是可以对齐 AU 和画册的人物设定，并且还能有真实的感觉，不会生硬。」

所以这个工具只做一件事：她说「打给 X」，就把站里关于 X 的东西从各处捡齐——
画册那一页、五句台词、热线里的声口、AU 系列首页的设定、圣经里的人物 / 称呼 / 红线、
你们俩走到了哪一章、上次通话留下的几句——拼成一份「接通前的资料」。
怎么用这份资料去当好他，写在 .claude/skills/winter-call/SKILL.md。

    python3 tools/call/brief.py --list                # 能打给谁（有 AU 的 / 只在画册的 / 别的演员的 AU）
    python3 tools/call/brief.py gary                  # 找人；名字、片名、中文片名、系列名都认
    python3 tools/call/brief.py bill --au eyes-on-me  # 一个人有两个 AU 时指定是哪一个
    python3 tools/call/brief.py bill --au none        # 不要 AU，只要电影里 / 画册里的他
    python3 tools/call/brief.py --id garyguitar       # 重名时按编号直接认（列表里 --id 后面那个）
    python3 tools/call/brief.py gary --upto 12        # 回到第 12 章那时候的他（之后的事他还不知道）

找到不止一个人 → 列出候选、退出码 2；一个人有好几个 AU 又没指定 → 列出来、退出码 3。
两种情况都去问 Winter「是哪一个」，别替她挑。她定过的叫法（calls.py alias，「以后 Gary 就是弹吉他那个」）先认。
"""
import argparse
import datetime as dt
import glob
import html
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TZ = dt.timezone(dt.timedelta(hours=8))   # Winter 在国内，一律按北京时间


def rp(*p):
    return os.path.join(ROOT, *p)


def read(path):
    with io.open(path, encoding="utf-8") as f:
        return f.read()


# 系列目录名 ≠ 圣经文件名的那几个（其余同名）
BIBLE_FOR = {
    "wholly-known": "eddie-carbone-au",
    "everything-in-transit": "glory-daze",
    "i-never-looked-away": "lawn-dogs-au",
    "the-serbian-tornado": "pero-mahlovic-au",
    "the-saloon-nobody-dares": "samuel-doc-au",
}

DIMS = [("guile", "狡黠", "算计与机锋"), ("forbear", "隐忍", "沉默里扛住的"),
        ("chaos", "疯狂", "失控与不管不顾"), ("raw", "璞真", "笨拙的真心"),
        ("romance", "浪漫", "对你的那点软"), ("grace", "优雅", "骨子里的教养")]

BUCKET_CN = {"greet": "打招呼", "miss": "说想他", "tired": "说累", "sleepless": "睡不着",
             "night": "道晚安", "love": "表白撒娇", "meet": "说要去见他", "praise": "夸他",
             "tease": "闹他", "daily": "日常"}

# 圣经里值得在接通前就读的小节（按标题关键词认）
BIBLE_KEYS = ["他 ·", "他·", "### 他", "人物", "内核", "称呼", "声口", "关系", "动力",
              "你 ·", "### 你", "红线", "已确立", "床上", "母题"]


# ───────────────────────── 读数据 ─────────────────────────

def strip_tags(s):
    s = re.sub(r"<br\s*/?>", "\n", s)
    s = re.sub(r"</p>|</li>|</h\d>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n\n", s)
    return s.strip()


def front_matter(text):
    m = re.match(r"---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        return {}, text
    fm = {}
    for line in m.group(1).splitlines():
        mm = re.match(r"^([A-Za-z_]+):\s*(.*?)\s*$", line)
        if not mm:
            continue
        v = mm.group(2)
        v = re.sub(r"\s+#.*$", "", v) if not v.startswith(("\"", "'")) else v
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            v = v[1:-1]
        fm[mm.group(1)] = v
    return fm, text[m.end():]


def load_lines():
    d = json.loads(read(rp("sam/lines.json")))
    return d["characters"], d["meta"].get("mf_alias", {})


def load_replies():
    try:
        return json.loads(read(rp("sam/hotline-replies.json")))
    except Exception:
        return {"chars": {}}


def js_str(block, key):
    m = re.search(r"\b%s:\s*\"((?:[^\"\\]|\\.)*)\"" % key, block)
    return m.group(1).replace('\\"', '"') if m else ""


def load_faces():
    """画册（真源）里每个人的那一页。"""
    src = read(rp("sam/many-faces/index.html"))
    start = src.index("const characters = [")
    body = src[start:]
    marks = [m.start() for m in re.finditer(r"\{\s*\n\s*id:\s*\"", body)]
    out = {}
    for i, a in enumerate(marks):
        b = marks[i + 1] if i + 1 < len(marks) else len(body)
        blk = body[a:b]
        cid = js_str(blk, "id")
        if not cid:
            continue
        desc = re.search(r"\bdesc:\s*`(.*?)`", blk, re.S)
        ins = re.search(r"inscription:\s*\{(.*?)\}", blk, re.S)
        prof = re.search(r"profile:\s*\{(.*?)\}", blk, re.S)
        links = re.findall(r"href:\s*\"([^\"]+)\"(?:[^}]*?label:\s*\"((?:[^\"\\]|\\.)*)\")?", blk)
        out[cid] = {
            "id": cid,
            "name": js_str(blk, "name"),
            "film": js_str(blk, "film"),
            "filmCN": js_str(blk, "filmCN"),
            "year": js_str(blk, "year"),
            "tagline": js_str(blk, "tagline"),
            "desc": desc.group(1).strip() if desc else "",
            "inscription": {k: js_str(ins.group(1), k) for k in ("label", "line", "gloss")} if ins else {},
            "profile": dict((k, int(v)) for k, v in re.findall(r"(\w+):\s*(\d+)", prof.group(1))) if prof else {},
            "au_hrefs": [h for h, _ in links],
        }
    return out


def load_series():
    out = {}
    for f in sorted(glob.glob(rp("series/*/index.html"))):
        slug = os.path.basename(os.path.dirname(f))
        text = read(f)
        fm, body = front_matter(text)
        if fm.get("layout") != "series":
            continue
        by = re.search(r'c-hero__byline-text">\s*(.*?)\s*<', text, re.S)
        byline = strip_tags(by.group(1)) if by else ""
        parts = [p.strip() for p in byline.split("·")]
        comments = re.findall(r"\{%-?\s*comment\s*-?%\}(.*?)\{%-?\s*endcomment\s*-?%\}", text, re.S)
        intros = []
        for art in re.findall(r'<article class="c-sam-intro">(.*?)</article>', text, re.S):
            h = re.search(r"<h2[^>]*>(.*?)</h2>", art, re.S)
            intros.append((strip_tags(h.group(1)) if h else "", strip_tags(re.sub(r"<h2.*?</h2>", "", art, flags=re.S))))
        lede = re.search(r'<p class="c-hero__lede[^>]*>(.*?)</p>', text, re.S)
        out[slug] = {
            "slug": slug,
            "name": fm.get("series_name", ""),
            "title": fm.get("title", ""),
            "status": (fm.get("series_status") or "ongoing").split()[0],
            "logline": fm.get("logline", ""),
            "lede": re.sub(r"\s+", "", strip_tags(lede.group(1))) if lede else "",
            "byline": byline,
            "who": parts[0] if parts else "",
            "source": parts[1] if len(parts) > 1 else "",
            "actor": parts[2] if len(parts) > 3 else "",
            "comments": [c.strip() for c in comments if c.strip()],
            "intros": intros,
            "sam": fm.get("sam_collection") == "true",
        }
    return out


def load_posts():
    by = {}
    for f in glob.glob(rp("_posts/*.md")):
        text = read(f)
        fm, body = front_matter(text)
        s = fm.get("series")
        if not s:
            continue
        try:
            order = float(fm.get("series_order") or 0)
        except ValueError:
            order = 0
        ct = fm.get("chapter_type", "")
        kind = fm.get("chapter_kind") or ("" if re.match(r"(Chapter|Episode)\s*\d", ct) else "extra")
        num = re.search(r"(?:Chapter|Episode)\s*(\d+)", ct)
        by.setdefault(s, []).append({
            "path": os.path.relpath(f, ROOT), "title": fm.get("title", ""), "date": fm.get("date", "")[:10],
            "order": order, "kind": kind, "num": int(num.group(1)) if num else None,
            "summary": fm.get("summary", ""), "tags": fm.get("tags", ""), "body": body,
            "story_time": fm.get("story_time", ""),
        })
    for s in by:
        by[s].sort(key=lambda p: (p["order"], p["date"]))
    return by


# ───────────────────────── 认人 ─────────────────────────

def norm(s):
    s = html.unescape(s or "").lower()
    s = re.sub(r"[《》“”\"'‘’·.,()（）\-_/!?！？]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def build_people():
    chars, alias = load_lines()
    faces = load_faces()
    series = load_series()
    replies = load_replies().get("chars", {})
    people = []
    used = set()
    for c in chars:
        mf = alias.get(c["id"], c["id"])
        face = faces.get(mf, {})
        hrefs = face.get("au_hrefs") or ([c["auLink"]] if c.get("auLink") else [])
        aus = []
        for h in hrefs:
            m = re.search(r"/series/([^/]+)/", h or "")
            if m and m.group(1) in series and m.group(1) not in aus:
                aus.append(m.group(1))
        used.update(aus)
        people.append({"id": c["id"], "name": c["name"], "film": c.get("film", ""), "filmCN": c.get("filmCN", ""),
                       "year": c.get("year", ""), "actor": "Sam Rockwell", "lines": c, "face": face,
                       "reply": replies.get(c["id"]), "aus": aus})
    # 不在画册里的 AU（别的演员 / 画册还没收的）：按系列首页 byline 的角色名立一个人
    for slug, s in series.items():
        if slug in used:
            continue
        who = s["who"]
        hit = next((p for p in people if not p["lines"] and norm(p["name"]) == norm(who)), None)
        if hit:
            hit["aus"].append(slug)
            continue
        people.append({"id": slug, "name": who, "film": s["source"], "filmCN": "", "year": "",
                       "actor": s["actor"], "lines": None, "face": {}, "reply": None, "aus": [slug]})
    return people, series


def keys_of(p, series):
    ks = [p["id"], p["name"], p["film"], p["filmCN"], p["face"].get("name", "")]
    for a in p["aus"]:
        s = series[a]
        ks += [a, s["name"], s["title"], s["who"]]
    return [norm(k) for k in ks if k]


def find(people, series, q):
    """先认全名 / 片名 / 系列名一字不差的；再认名字里某个词打头的；最后才是随便哪儿包含。"""
    nq = norm(q)
    exact, word, part = [], [], []
    for p in people:
        ks = keys_of(p, series)
        names = [norm(p["name"]), norm(p["face"].get("name", ""))] + [norm(series[a]["who"]) for a in p["aus"]]
        if nq in ks or any(nq == w for k in names for w in k.split()):
            exact.append(p)
        elif any(w.startswith(nq) for k in names for w in k.split()):
            word.append(p)
        elif any(nq in k for k in ks):
            part.append(p)
    return exact or word or part


def pick_au(p, series, want):
    if want is None:
        return p["aus"][0] if len(p["aus"]) == 1 else ("?" if p["aus"] else None)
    if norm(want) in ("none", "画册", "电影", "原片"):
        return None
    nw = norm(want)
    for a in p["aus"]:
        s = series[a]
        if nw in (norm(a), norm(s["name"])) or nw in norm(s["name"]) or nw in norm(a):
            return a
    return "?"


# ───────────────────────── 圣经 ─────────────────────────

def bible_path(slug):
    b = BIBLE_FOR.get(slug, slug)
    p = rp(".claude/bibles/%s.md" % b)
    return (p if os.path.exists(p) else None), b


def sections(text):
    """[(level, heading, start_line, body)]"""
    lines = text.splitlines()
    heads = [(i, len(m.group(1)), m.group(2).strip()) for i, l in enumerate(lines)
             for m in [re.match(r"^(#{2,4})\s+(.*)", l)] if m]
    out = []
    for n, (i, lv, h) in enumerate(heads):
        j = len(lines)
        for i2, lv2, _ in heads[n + 1:]:
            if lv2 <= lv:
                j = i2
                break
        out.append((lv, h, i + 1, "\n".join(lines[i + 1:j]).strip()))
    return out


def clip(s, n):
    s = s.strip()
    return s if len(s) <= n else s[:n].rstrip() + "\n……（下略，要看全文去圣经里读这一节）"


# ───────────────────────── 拼资料 ─────────────────────────

def now_line():
    t = dt.datetime.now(TZ)
    wd = "一二三四五六日"[t.weekday()]
    h = t.hour
    part = ("深夜" if h < 5 else "清早" if h < 8 else "上午" if h < 11 else "中午" if h < 13 else
            "下午" if h < 18 else "傍晚" if h < 20 else "晚上" if h < 23 else "深夜")
    return "%s 周%s %s（%s）" % (t.strftime("%Y-%m-%d"), wd, t.strftime("%H:%M"), part)


def his_texts(chapters):
    """正文里他真发过的消息、写过的字条——这才是他「发给她一个人」时的嗓子，比小说叙述准。"""
    chats, comms, notes = [], [], []
    for c in chapters:
        b = c["body"]
        for m in re.findall(r'<div class="c-chat__msg c-chat__msg--in[^"]*">(.*?)</div>', b, re.S):
            chats.append(strip_tags(m))
        for log in re.findall(r'<ol class="c-comm__log">(.*?)</ol>', b, re.S):
            for cls, m in re.findall(r'<li([^>]*)>(.*?)</li>', log, re.S):
                if "c-comm__gap" not in cls:
                    comms.append(strip_tags(m))
        for blk in re.findall(r'<div class="c-note"[^>]*>(.*?)(?=<div class="c-note"|\Z)', b, re.S):
            m = re.match(r'(.*?)<span class="c-note__sign[^"]*">(.*?)</span>\s*</div>', blk, re.S)
            if not m:
                continue   # 没署名的字条（或者这张卡在署名之前就结束了）：分不清是谁写的，不要
            body, sign = m.group(1), m.group(2)
            if "\n\n" in re.sub(r"<[^>]+>", "", body).strip() and "</div>" in body and body.count("</div>") > 1:
                continue   # 署名前已经有卡片结束过一次 = 抓到了卡片外面的叙述
            sign = strip_tags(sign)
            if re.search(r"W\.|Winter|你|妈|Mom|Ma\b", sign):
                continue   # 她写的、家里人写的，不是他
            body = re.sub(r'<span class="c-note__label">.*?</span>', "", body, flags=re.S)
            notes.append((strip_tags(body), sign))
    return chats[-40:], comms[-25:], notes[-6:]


def call_key(pid, au):
    return pid + ("--" + au if au else "")


_CALLS = None


def calls_data():
    """calls 分支上的 calls.json（通话记录 + 她定的叫法），一次接通只取一回。"""
    global _CALLS
    if _CALLS is None:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import calls
        _CALLS = calls.load_quiet()
    return _CALLS


def call_log(key):
    """上次通话留下的几句（由 calls.py 记）。"""
    import calls
    e = calls_data().get("calls", {}).get(key)
    return calls.render(e, recent=6) if e else None


def alias_of(q):
    """她定过的叫法（「以后说 Gary 就是 Interoffice 那个」「教练」），由 calls.py alias 记。"""
    for k, v in calls_data().get("aliases", {}).items():
        if norm(k) == norm(q):
            return v
    return None


def blurb(p, series):
    """重名时给她挑的那一句：画册的一句话，没有就用系列基调。"""
    t = p["face"].get("tagline") or (series[p["aus"][0]]["logline"] if p["aus"] else "")
    return t if len(t) <= 40 else t[:40] + "……"


def brief(p, series, posts, au, upto, out, text_mode=False):
    w = out.append
    face, ln = p["face"], p["lines"]
    w("# ☎ 接通前的资料 · %s" % p["name"])
    w("")
    if text_mode:
        w("> 💌 这是「冬的陪伴」要的资料：只为**认识他这个人**——性子、称呼、说话的样子、红线。"
          "你们是异地的恋人、只能发消息，他过的是他自己平常的日子；下面的剧情和大场面一概**不接、不演、不提**。"
          "他发短讯的真嗓子看「正文里他真发过的消息」那一节。")
    else:
        w("> ⚠️ 下面有很多抒情的段落和大场面——那是让你**认识他**的，不是让你照着写的。"
          "这一通：故事之后的平常日子，一行一条、平常说话、不写旁白。他发消息的真嗓子看「正文里他真发过的消息」那一节。")
    w("")
    w("- 现在：北京时间 %s" % now_line())
    film = " · ".join(x for x in [p["film"], p["filmCN"], p["year"]] if x)
    w("- 出处：%s%s" % (film, ("　演员：" + p["actor"]) if p["actor"] else ""))
    if au:
        s = series[au]
        w("- 这一通打给的是：**%s**（%s）" % (s["title"], s["status"]))
    elif p["aus"]:
        w("- 这一通打给的是：**电影 / 画册里的他**（不带 AU 剧情）")
    w("")

    if face:
        w("## 画册里的他（他和「你」的关系底色）")
        w("")
        if face.get("tagline"):
            w("> " + face["tagline"])
            w("")
        ins = face.get("inscription") or {}
        if ins.get("line"):
            w("题词：%s —— %s（%s）" % (ins.get("label", ""), ins["line"], ins.get("gloss", "")))
            w("")
        if face.get("desc"):
            w(face["desc"])
            w("")
        if face.get("profile"):
            w("六维（1–10）：" + "　".join("%s %s" % (cn, face["profile"].get(k, "?")) for k, cn, _ in DIMS))
            w("")

    if ln:
        w("## 他的五句台词（锚句在前；当声口参考，别背诵）")
        w("")
        for q in ln.get("quotes", []):
            w("- [%s] %s —— %s" % (q.get("kind", ""), q.get("line", ""), q.get("lineCN", "")))
        w("")

    rep = p["reply"]
    home = re.search(r"/series/([^/]+)/", (ln or {}).get("auLink") or "")
    if rep and "aus" not in rep and au and home and home.group(1) != au:
        w("（热线里写好的那套回复是 %s 的他，不是这一通的 AU——称呼和处境都不一样，别照搬。）" % series[home.group(1)]["name"])
        w("")
        rep = None
    if not rep and ln:
        w("（热线里还没给他写回复库——声口全看圣经和正文。）")
        w("")
    if rep:
        reg = rep.get("register", "")
        pet = rep.get("pet", "")
        block = rep
        if "aus" in rep:
            block = next((x for x in rep["aus"] if au and (x.get("key") in au or au in x.get("key", ""))), rep["aus"][0])
            reg = block.get("register", reg)
            pet = block.get("pet", pet)
        bk = block.get("buckets", block)
        w("## 热线里写好的他（声口样本）")
        w("")
        w("（早先写的，里面提到的处境——在哪上班、谁还在——可能已经变了，跟此刻对不上的别用。）")
        w("")
        if isinstance(pet, dict):
            pet = " / ".join(x for x in (pet.get("en"), pet.get("cn")) if x)
        w("声口档：%s　称呼你：%s" % (reg or "—", pet or "（热线里没写——以圣经的称呼为准）"))
        w("")
        for b, cn in BUCKET_CN.items():
            for x in (bk.get(b) or [])[:1]:
                w("- 你%s → %s（%s）" % (cn, x.get("line", ""), x.get("cn", "")))
        w("")

    if au:
        s = series[au]
        w("## AU：%s" % s["title"])
        w("")
        w("byline：%s" % s["byline"])
        if s["logline"]:
            w("基调：%s" % s["logline"])
        if s["lede"]:
            w("引言：%s" % s["lede"])
        w("")
        for h, t in s["intros"]:
            w("### %s" % h)
            w("")
            w(t)
            w("")
        for c in s["comments"]:
            if any(k in c for k in ("称呼", "声口", "母题", "红线", "你」", "你 =")):
                w("```")
                w(c)
                w("```")
                w("")

        bp, bslug = bible_path(au)
        if bp:
            text = read(bp)
            secs = sections(text)
            w("## 圣经摘录（%s · 共 %d 行）" % (os.path.relpath(bp, ROOT), len(text.splitlines())))
            w("")
            if upto:
                w("⚠️ 圣经写的是全系列。这一通只到第 %d 章，圣经里第 %d 章之后才发生 / 才揭晓的事，一个字都不能用。" % (upto, upto))
                w("")
            if len(text) <= 60000:
                w("⭐ 这本圣经不长（%d 字）：接通前**整本读一遍**（Read 这个文件），下面只是先垫个底。" % len(text))
            else:
                w("⭐ 这本圣经很长（%d 字）：下面这些节读全（没印完的照行号 sed），再读「伏笔账」和流水最后一段。" % len(text))
            w("⚠️ 圣经开头写的多是**开篇时**的他（年龄、年份、称呼）；此刻的状态以最新一章为准，伏笔账里标了已回收的就是已经发生了。")
            main_nums = [c["num"] for c in posts.get(series[au]["name"], []) if c["num"] is not None and not c["kind"]]
            flow_text = "\n".join(b for _, h, _, b in secs if "流水" in h) or text
            nums = [int(a or b) for a, b in re.findall(r"Ch\.?\s*(\d{1,3})|第\s*(\d{1,3})\s*章", flow_text)]
            if flow_text is not text:   # 流水里「14. **标题**」这种编号也算
                nums += [int(n) for n in re.findall(r"^\s*[-*]?\s*(\d{1,3})[\.、]\s", flow_text, re.M)]
            if main_nums and nums and not upto and max(nums) < max(main_nums):
                w("⚠️ 圣经的章节流水最多记到第 %d 章，正篇已经到第 %d 章——**圣经可能没跟上**：至少把最近两三章正篇读全，"
                  "再扫一眼下面「你们走到哪了」每章那一句。" % (max(nums), max(main_nums)))
            w("")
            budget = 16000
            lines_total = len(text.splitlines())
            covered = -1
            for n, (lv, h, line, body) in enumerate(secs):
                if line <= covered:
                    continue   # 上一节已经整节印过（含这个子节）
                if lv > 3 or not any(k in h for k in BIBLE_KEYS) or "流水" in h:
                    continue
                if budget <= 0:
                    break
                end = next((l2 - 1 for lv2, _, l2, _ in secs[n + 1:] if lv2 <= lv), lines_total)
                piece = body if len(body) <= 3500 else body[:3500].rstrip() + "\n……（没印完：这一节是第 %d–%d 行）" % (line, end)
                w("### %s（第 %d–%d 行）" % (h, line, end))
                w("")
                w(piece)
                w("")
                budget -= len(piece)
                covered = end
            w("圣经全部小节（要细看某节：`sed -n '起,止p' %s`）：" % os.path.relpath(bp, ROOT))
            w("")
            for lv, h, line, _ in secs:
                if lv <= 3:
                    w("%s- 第 %d 行 · %s" % ("  " * (lv - 2), line, h))
            w("")
            flow = [x for x in secs if "流水" in x[1]]
            if flow and not upto:
                lv, h, line, body = flow[-1]
                w("### %s（最后一段，第 %d 行起）" % (h, line))
                w("")
                tail = body[-2500:]
                w(("……" if len(body) > 2500 else "") + tail)
                w("")
        else:
            w("## 圣经：这个系列还没有圣经（.claude/bibles/%s.md 不存在），以系列首页和正文为准。" % bslug)
            w("")

        ch = posts.get(s["name"], [])
        if upto:
            # 第 N 章（含它之前的番外）为止；之后的一概不算
            stop = max([c["order"] for c in ch if c["num"] is not None and c["num"] <= upto] or [0])
            ch = [c for c in ch if c["order"] <= stop]
        main = [c for c in ch if not c["kind"]]
        w("## 你们走到哪了（%s 共 %d 篇%s）" % (s["name"], len(ch), ("，只算到第 %d 章" % upto) if upto else ""))
        w("")
        if upto:
            w("⚠️ 这一通回到第 %d 章那时候：之后发生的事他一概不知道，也不许漏嘴。" % upto)
            w("")
        w("（按系列顺序；番外是按上线先后插进来的，**它在故事里发生在哪儿看 story_time 或正文**，别把番外当成最新状态。）")
        w("")
        for i, c in enumerate(ch):
            tag = {"extra": "番外", "pov": "他视角"}.get(c["kind"], "")
            title = re.sub(r"\s+—\s+%s\s*$" % re.escape(s["name"]), "", c["title"])
            extra = "".join(x for x in [("〔%s〕" % tag) if tag else "", ("〔故事里：%s〕" % c["story_time"]) if c["story_time"] else ""])
            path = ("　`%s`" % c["path"]) if i >= len(ch) - 4 else ""
            w("- %s%s —— %s%s" % (title, extra, c["summary"], path))
        w("")
        chats, comms, notes = his_texts(ch)
        w("## 正文里他真发过的消息 / 写过的字条（⭐ 他「发给她一个人」时的嗓子，比小说叙述准）")
        w("")
        if chats:
            w("手机消息（他发的，按先后）：")
            w("")
            w("\n".join("- " + x for x in chats))
            w("")
        if comms:
            w("通讯板 / 屏幕上的消息（多半是他发的，拿不准看那一章）：")
            w("")
            w("\n".join("- " + x for x in comms))
            w("")
        for body, sign in notes:
            w("字条（署名 %s）：" % sign)
            w("")
            w(clip(body, 600))
            w("")
        if not (chats or comms or notes):
            w("（正文里没有他发消息、写字条的记录。声口只能从对白里学——但对白是小说的节奏，发消息要更短、更平。）")
            w("")

        last = main[-1] if main else (ch[-1] if ch else None)
        if last and not text_mode:
            body = strip_tags(re.sub(r"\{%.*?%\}", "", last["body"]))
            w("### 最新一章正篇的结尾（%s）" % last["title"])
            w("")
            w("（读它是为了看你们的关系走到哪、学他怎么说话。这一通默认在**故事之后的平常日子**：这一场里的伤、架、险都已经过去，"
              "他不会接着演这一场，也不会主动提——除非她说「接着最新一章那一刻」。）")
            w("")
            w(("……" if len(body) > 1800 else "") + body[-1800:])
            w("")
    elif p["aus"]:
        w("## 他有 AU，但这一通不带 AU 剧情")
        w("")
        w("他有：" + "、".join(series[a]["title"] for a in p["aus"]) + "。这一通只按电影和画册里的他来。")
        w("")

    key = call_key(p["id"], au)
    if text_mode:
        w("## 记录编号：`%s`（下一步：`python3 tools/text/texts.py open %s`）" % (key, key))
        return out
    log = call_log(key)
    w("## 上次通话（记录编号 `%s`）" % key)
    w("")
    w(log if log else "（还没有记录——这是第一通。）")
    w("")
    w("挂断后记一笔：`python3 tools/call/calls.py add %s --who \"%s\" --mode <电话/消息/见面/通讯板> --note \"……\" --trailer \"<会话要求的署名行>\"`"
      % (key, p["name"] + (" · " + series[au]["name"] if au else "")))
    w("她说「这不像他」：`python3 tools/call/calls.py fix %s \"……\"`" % key)
    return out


def listing(people, series):
    with_au = [p for p in people if p["lines"] and p["aus"]]
    face_only = [p for p in people if p["lines"] and not p["aus"]]
    others = [p for p in people if not p["lines"]]

    def row(p):
        film = p["filmCN"] or p["film"]
        aus = " / ".join(series[a]["name"] for a in p["aus"])
        return "- %s（%s%s）%s" % (p["name"], film, (" " + p["year"]) if p["year"] else "",
                                  ("　→ " + aus) if aus else "")
    print("## 有 AU 的（%d 人；有两个 AU 的要问她打给哪一个）" % len(with_au))
    for p in sorted(with_au, key=lambda p: p["year"]):
        print(row(p))
    print("\n## 只在画册里的（%d 人；按电影和画册的他来）" % len(face_only))
    for p in sorted(face_only, key=lambda p: p["year"]):
        print(row(p))
    print("\n## 别的演员的 AU / 画册没收的（%d 人）" % len(others))
    for p in others:
        print(row(p) + ("　· " + p["actor"] if p["actor"] else ""))


def main():
    ap = argparse.ArgumentParser(description="打给他：接通前的资料")
    ap.add_argument("who", nargs="*", help="名字 / 片名 / 中文片名 / 系列名（几个词不用加引号）")
    ap.add_argument("--au", nargs="+", help="有好几个 AU 时指定哪一个（系列名或目录名）；none = 不带 AU")
    ap.add_argument("--upto", type=int, help="回到第 N 章那时候（之后的事他还不知道）")
    ap.add_argument("--list", action="store_true", help="列出能打给谁")
    ap.add_argument("--id", help="按编号直接认人（重名时列表里给的那个；也可以直接给记录编号 karl--dear-satan）")
    ap.add_argument("--text", action="store_true", help="给「冬的陪伴」用：只要认识他的部分，不给剧情结尾、不带通话记录")
    a = ap.parse_args()

    people, series = build_people()
    if a.list or (not a.who and not a.id):
        listing(people, series)
        return 0
    a.who = " ".join(a.who)
    a.au = " ".join(a.au) if a.au else None
    if a.id and "--" in a.id:   # 直接给了记录编号（karl--dear-satan）
        a.id, _, k_au = a.id.partition("--")
        a.au = a.au or k_au
    al = None if a.id else alias_of(a.who)
    if al:
        a.id = al["id"]
        if not a.au and al.get("au"):
            a.au = al["au"]
    if a.id:
        hits = [p for p in people if p["id"] == a.id]
    else:
        hits = find(people, series, a.who)
    if not hits:
        print("没认出「%s」是谁。跑 `--list` 看看全部名单，或者换个叫法（英文名 / 片名）。" % a.who)
        return 1
    if len(hits) > 1:
        print("「%s」能对上好几个人，用一句话问 Winter 是哪一个（她要是说「以后 %s 就是他」，用 calls.py alias 记下来）：" % (a.who, a.who))
        for p in hits:
            aus = " / ".join(series[x]["name"] for x in p["aus"])
            print("- %s（%s %s）%s —— %s　→ `--id %s`" % (p["name"], p["filmCN"] or p["film"], p["year"],
                                                  ("AU：" + aus) if aus else "", blurb(p, series), p["id"]))
        return 2
    p = hits[0]
    if not a.au:   # 她直接报的是故事名（「Eyes on Me」「打给 Sanguis 那个」）→ 就是那个 AU
        nq = norm(a.who)
        a.au = next((x for x in p["aus"] if norm(series[x]["name"]) in nq or norm(x) in nq), None)
    au = pick_au(p, series, a.au)
    if au == "?":
        print("%s 有 %d 个 AU，问 Winter 打给哪一个他（也可以都不要，只要电影里的他）：" % (p["name"], len(p["aus"])))
        for x in p["aus"]:
            s = series[x]
            print("- %s（%s）—— %s　→ `--au %s`" % (s["title"], s["status"], s["logline"][:60], x))
        print("- 电影 / 画册里的他　→ `--au none`")
        return 3
    print("\n".join(brief(p, series, load_posts(), au, a.upto, [], text_mode=a.text)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
