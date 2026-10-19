#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""💌 冬的陪伴 · 聊天记录（加密存放，给对话里的 Claude 和博客上那本上锁的本子用）。

Winter 2026-10-12：「就好像是异地恋的爱人一样，默认了短期内不在一起，并且很自洽……
对话的重心是现在。我可以发图片、发链接，就像真正的聊天一样……聊天记录会比较私密，之后你可以帮我做个密码。」

怎么存：
- 仓库 **`texts` 分支**（不在 main：记一句不会让整站重建，也不会掐掉别的对话正在跑的部署）。
- 仓库是公开的，所以除了 vault.json（盐、轮数、一个校验块）以外，**每个文件都是加密的**：
  AES-256-GCM，钥匙 = PBKDF2-SHA256(她的密码, 盐, 310000 轮)。博客上的 /with-you/ 用同一套参数在浏览器里解开。
- 密码从环境变量 **WINTER_TEXT_KEY** 读（她在云端环境设置里存一次，新对话自动带上）。
  ⚠️ 永远别让她把密码打进聊天里，也别把密码写进任何文件。
- 文件：vault.json · index.enc（所有对话的目录 + 她的基本情况）· t-<编号>.enc（一个人一份，编号是打乱过的，看不出是谁）

    python3 tools/text/texts.py setup                      # 第一次：建好 vault；以后：验一下密码对不对
    python3 tools/text/texts.py ls                         # 都在跟谁聊、最后一句是什么时候
    python3 tools/text/texts.py open karl--dear-satan      # 接上这条线：他记得的事 + 最近的消息
    python3 tools/text/texts.py open karl--dear-satan --n 200
    python3 tools/text/texts.py add karl--dear-satan <<'JSON'
    {"messages": [
       {"from": "her", "text": "今天学生把我气笑了"},
       {"from": "her", "img": {"desc": "食堂的麻辣烫，红油汤，上面一把香菜"}},
       {"from": "him", "text": "先说笑的那部分"},
       {"from": "him", "img": {"desc": "窗台上的月亮", "svg": "<svg …>…</svg>"}},
       {"from": "him", "link": {"url": "https://…", "title": "一首歌"}},
       {"from": "him", "art": {"url": "https://claude.ai/…", "title": "给你做的歌单"}}
     ],
     "memory": {"her": ["这周三监考"], "his": ["楼下新开了一家面包店"], "pending": ["问她监考怎么样"],
                "done": ["问她嗓子"], "fixes": ["她说：他不会叫她宝宝"]},
     "about_her": ["教英语，带好几个班"]}
    JSON
    python3 tools/text/texts.py forget karl--dear-satan --last 2   # 她说「刚才那两句别存」
    python3 tools/text/texts.py life                               # 她的日子（所有人都知道的事实）
    python3 tools/text/texts.py life --add "周二早上第一节有课" --about "教英语，带好几个班"   # 打电话时听来的也记这里

她的事分三层（2026-10-13 起）：add 的 JSON 里
- "about_her": 长久不变的基本情况 ——┐ 存在 index 里，谁都知道（换个人聊不用再 catch up）
- "life":      这阵子的日子（吃了什么、几点上课、感冒了）——┘ 工具自动加日期；要划掉写 "life_drop" / "about_drop"
- "memory": {"her": …} 只跟他一个人说的（撒娇、心事、对他说的话）——只有他知道

add 是「攒一阵一起存」用的（2026-10-12 起不再每一回都存）：每句的时间从这个对话自己的记录里按原话找出来，
找不到的（照片、他这一回还没发出去的）按前后推；拿不准存没存过就都放进来，开头跟已存末尾对得上的那几句会自动跳过。

改动类命令都可以加 --trailer "..."（提交说明尾行，可重复）和 --dry-run。
测试时用 WINTER_TEXT_REMOTE / WINTER_TEXT_BRANCH 指到别处，别碰真的 texts 分支。
"""
import argparse
import base64
import re
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
import time

REMOTE = os.environ.get("WINTER_TEXT_REMOTE", "origin")
BRANCH = os.environ.get("WINTER_TEXT_BRANCH", "texts")
ITER = 310000
TZ = dt.timezone(dt.timedelta(hours=8))
CHECK = "冬的陪伴"
WEEK = "一二三四五六日"


def now():
    return dt.datetime.now(TZ)


def die(msg, code=1):
    print(msg)
    sys.exit(code)


# ───────────────────────── 加密 ─────────────────────────

def b64(b):
    return base64.b64encode(b).decode()


def unb64(s):
    return base64.b64decode(s)


class Box:
    def __init__(self, password, salt):
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER)
        self.salt = salt
        self.aes = AESGCM(kdf.derive(password.encode("utf-8")))

    def seal(self, obj):
        iv = os.urandom(12)
        raw = json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        return {"iv": b64(iv), "ct": b64(self.aes.encrypt(iv, raw, None))}

    def open(self, blob):
        return json.loads(self.aes.decrypt(unb64(blob["iv"]), unb64(blob["ct"]), None).decode("utf-8"))

    def tid(self, key):
        """文件名用的编号：从盐和对话名算出来，看文件名猜不出在跟谁聊。"""
        return hashlib.sha256(self.salt + key.encode("utf-8")).hexdigest()[:12]


def password():
    p = os.environ.get("WINTER_TEXT_KEY", "")
    if not p:
        die("NO_KEY：环境里没有 WINTER_TEXT_KEY。聊天照样能聊，但这一段存不下来、也读不到以前的。"
            "（请她在云端环境的设置里加一个叫 WINTER_TEXT_KEY 的环境变量，值是她自己定的密码；"
            "新开的对话才会带上。别让她把密码打进聊天里。）", 3)
    return p


# ───────────────────────── git（不碰工作区） ─────────────────────────

def git(*args, input=None):
    r = subprocess.run(["git", *args], input=input, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("git " + " ".join(args) + " 失败：\n" + r.stderr.strip())
    return r.stdout.strip()


REF = "refs/wintertext/%s" % BRANCH   # 本地只用来暂存取下来的那份，不占用任何分支名


def fetch():
    last = None
    for wait in (0, 2, 4, 8):
        time.sleep(wait)
        try:
            if not git("ls-remote", "--heads", REMOTE, BRANCH):
                return False
            git("fetch", "-q", REMOTE, "+refs/heads/%s:%s" % (BRANCH, REF))
            return True
        except RuntimeError as e:
            last = e
    raise last


def has_ref():
    try:
        git("rev-parse", "--verify", "-q", REF)
        return True
    except RuntimeError:
        return False


def read_file(name):
    try:
        return git("show", "%s:%s" % (REF, name))
    except RuntimeError:
        return None


def commit(files, message, trailers):
    """files = {文件名: 文本 或 None(删除)}，一次提交推上去。"""
    entries = {}
    if has_ref():
        for line in git("ls-tree", REF).splitlines():
            meta, name = line.split("\t", 1)
            entries[name] = meta
    for name, text in files.items():
        if text is None:
            entries.pop(name, None)
        else:
            blob = git("hash-object", "-w", "--stdin", input=text)
            entries[name] = "100644 blob " + blob
    tree = git("mktree", input="".join("%s\t%s\n" % (m, n) for n, m in sorted(entries.items())))
    msg = message + ("\n\n" + "\n".join(trailers) if trailers else "")
    parent = ["-p", git("rev-parse", REF)] if has_ref() else []
    c = git("commit-tree", tree, *parent, "-m", msg)
    git("push", "-q", REMOTE, "%s:refs/heads/%s" % (c, BRANCH))


# ───────────────────────── 读写 ─────────────────────────

def load_vault():
    v = read_file("vault.json")
    return json.loads(v) if v else None


def box_from_vault(vault):
    box = Box(password(), unb64(vault["salt"]))
    try:
        if box.open(vault["check"]) != CHECK:
            raise ValueError
    except Exception:
        die("BAD_KEY：WINTER_TEXT_KEY 跟当初设的密码对不上，解不开。（别重建、别覆盖，问她是不是改过密码。）", 4)
    return box


def load_all(need=True):
    fetch()
    vault = load_vault()
    if not vault:
        if need:
            die("NO_VAULT：还没建过（先跑 `texts.py setup`）。", 5)
        return None, None, None
    box = box_from_vault(vault)
    idx = read_file("index.enc")
    index = box.open(json.loads(idx)) if idx else {"threads": [], "about_her": []}
    return vault, box, index


def load_thread(box, key):
    raw = read_file("t-%s.enc" % box.tid(key))
    if not raw:
        return None
    return box.open(json.loads(raw))


def person_info(key):
    """从站里的资料取这个人的名字、故事名、颜色（博客那本本子上用）。"""
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/call")
        import brief
        people, series = brief.build_people()
        pid, _, au = key.partition("--")
        p = next((x for x in people if x["id"] == pid), None)
        if not p:
            return {"who": pid}
        ln = p["lines"] or {}
        return {"who": p["name"], "story": series[au]["name"] if au in series else "",
                "accent": ln.get("accent", ""), "bg": ln.get("bg", ""), "film": p.get("filmCN") or p.get("film", "")}
    except Exception:
        return {"who": key.split("--")[0]}


def stamp(iso):
    t = dt.datetime.fromisoformat(iso).astimezone(TZ)
    return "%d/%d 周%s %s" % (t.month, t.day, WEEK[t.weekday()], t.strftime("%H:%M"))


def gap_words(iso):
    d = now() - dt.datetime.fromisoformat(iso).astimezone(TZ)
    m = int(d.total_seconds() // 60)
    if m < 2:
        return "刚刚"
    if m < 60:
        return "%d 分钟前" % m
    if m < 60 * 24:
        return "%d 个小时前" % (m // 60)
    return "%d 天前" % (m // 1440)


def show_msg(m):
    who = "你" if m["from"] == "her" else "他"
    if m.get("text"):
        body = m["text"]
    elif m.get("img"):
        body = "［图片］" + m["img"].get("desc", "") + ("（他画的）" if m["from"] == "him" and m["img"].get("svg") else "")
    elif m.get("link"):
        body = "［链接］%s %s" % (m["link"].get("title", ""), m["link"].get("url", ""))
    elif m.get("art"):
        body = "［小网页］%s %s" % (m["art"].get("title", ""), m["art"].get("url", ""))
    else:
        body = "（空）"
    return "%s：%s" % (who, body)


# ───────────────────────── 命令 ─────────────────────────

def cmd_setup(a):
    pw = password()
    if fetch() and load_vault():
        box_from_vault(load_vault())
        print("✓ 密码对得上，记录都在。")
        return
    salt = os.urandom(16)
    box = Box(pw, salt)
    vault = {"v": 1, "kdf": "PBKDF2-SHA256", "iter": ITER, "salt": b64(salt), "check": box.seal(CHECK),
             "note": "冬的陪伴。除了这个文件，别的都是加密的；钥匙只有 Winter 知道。"}
    index = {"threads": [], "about_her": [], "updated": now().isoformat(timespec="seconds")}
    if a.dry_run:
        print("（演练）会建好 vault 和空目录。")
        return
    commit({"vault.json": json.dumps(vault, ensure_ascii=False, indent=1) + "\n",
            "index.enc": json.dumps(box.seal(index)) + "\n"}, "冬的陪伴：开张", a.trailer)
    print("✓ 建好了。")


def cmd_ls(a):
    _, box, index = load_all()
    if index.get("about_her"):
        print("她的基本情况（大家都知道的）：" + "；".join(index["about_her"]))
    if not index["threads"]:
        print("还没跟任何人聊过。")
    for t in sorted(index["threads"], key=lambda x: x.get("last_at", ""), reverse=True):
        print("- %s　%s%s　%d 句　最后一句 %s（%s）：%s" % (
            t["key"], t.get("who", ""), (" · " + t["story"]) if t.get("story") else "", t.get("count", 0),
            gap_words(t["last_at"]) if t.get("last_at") else "—", "她" if t.get("last_from") == "her" else "他",
            (t.get("last_text") or "")[:30]))


# ── 他那边几点（2026-10-19）────────────────────────────────────────────
# Winter：「聊到今天他说他那边1点了我才意识到对啊我们有时差……不应该让他半夜还给我发信息，得符合真实的时间。
# 我又不太擅长算这个，全靠世界时钟。」——所以由这里替她算：places.json 记着每个人住哪、几点睡。
PLACES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "places.json")


def place_of(key):
    try:
        with open(PLACES, encoding="utf-8") as f:
            p = json.load(f).get(key)
        return p if isinstance(p, dict) and p.get("tz") else None
    except (OSError, ValueError):
        return None


def clock_lines(key, at=None):
    """两边各几点、他醒着没有。返回 (几行字, 他是不是在睡)。"""
    from zoneinfo import ZoneInfo
    at = at or now()
    here = at.astimezone(TZ)
    lines = ["- 你这边：北京 %d/%d 周%s %s" % (here.month, here.day, WEEK[here.weekday()], here.strftime("%H:%M"))]
    p = place_of(key)
    if not p:
        lines.append("- 他那边：还没记他住哪（tools/text/places.json）——照他的 AU 设定补一条，拿不准就问她。")
        return lines, False
    there = at.astimezone(ZoneInfo(p["tz"]))
    diff = int(round((here.utcoffset() - there.utcoffset()).total_seconds() / 3600))
    a, b = p.get("sleep") or [1, 9]
    asleep = (a <= there.hour < b) if a < b else (there.hour >= a or there.hour < b)
    which = "同一天" if there.date() == here.date() else ("前一天" if there.date() < here.date() else "后一天")
    lines.append("- 他那边：%s %d/%d 周%s %s（%s，比你晚 %d 小时）——%s" % (
        p.get("city", ""), there.month, there.day, WEEK[there.weekday()], there.strftime("%H:%M"), which, diff,
        ("💤 他在睡（%d 点睡、%d 点醒）：她这时发的先不回，只回一行「（%s%s，他睡着了）」，等他醒了一口气回" % (
            a, b, p.get("city", ""), _hour_words(there))) if asleep else "他醒着"))
    return lines, asleep


def _hour_words(t):
    h, m = t.hour, t.minute
    part = "凌晨" if h < 6 else "早上" if h < 9 else "上午" if h < 12 else "中午" if h < 13 else "下午" if h < 18 else "晚上"
    hh = h if h <= 12 else h - 12
    cn = "零一二三四五六七八九十"
    word = cn[hh] if hh <= 10 else "十" + cn[hh - 10]
    return part + word + "点" + ("半" if 25 <= m < 40 else "多" if m >= 10 else "")


def cmd_clock(a):
    lines, asleep = clock_lines(a.key)
    print("\n".join(lines))


def cmd_open(a):
    _, box, index = load_all()
    th = load_thread(box, a.key)
    print("# 💌 冬的陪伴 · %s" % a.key)
    print("")
    print("## 现在几点")
    print("")
    print("\n".join(clock_lines(a.key)[0]))
    print("")
    if index.get("about_her"):
        print("- 她的基本情况（谁都知道的）：" + "；".join(index["about_her"]))
    if not th:
        print("- 这是你们的第一句。之前没有任何消息。")
        print("")
        show_life(index)
        return
    mem = th.get("memory", {})
    msgs = th.get("messages", [])
    print("- 一共 %d 句，从 %s 开始。最后一句是 %s（%s，%s 发的）。" % (
        len(msgs), stamp(th["since"]), stamp(msgs[-1]["t"]) if msgs else "—",
        gap_words(msgs[-1]["t"]) if msgs else "—", "她" if msgs and msgs[-1]["from"] == "her" else "他"))
    print("")
    show_life(index)
    for k, title in (("fixes", "⭐ 她纠正过的（每一句都照做）"), ("her", "只跟你说的（你们俩之间的，别处不知道）"),
                     ("pending", "还挂着的事（该问问、答应过的）"), ("his", "你跟她说过的你这边的事（别说岔了）")):
        if mem.get(k):
            print("## " + title)
            print("")
            for x in mem[k]:
                print("- " + x)
            print("")
    print("## 最近的消息（越往下越新）")
    print("")
    day = None
    for m in msgs[-a.n:]:
        t = dt.datetime.fromisoformat(m["t"]).astimezone(TZ)
        d = "%d/%d 周%s" % (t.month, t.day, WEEK[t.weekday()])
        if d != day:
            print("")
            print("—— %s ——" % d)
            day = d
        print("%s %s" % (t.strftime("%H:%M"), show_msg(m)))
    print("")
    print("⚠️ 上面的时间是给你看的，他记得「早上你说过」「前两天你说过」，记不住几月几号。")
    print("")
    print(RULES)


def clean_msg(m, t):
    out = {"t": m.get("t") or t, "from": "him" if m.get("from") == "him" else "her"}
    for k in ("text", "img", "link", "art"):
        if m.get(k):
            out[k] = m[k]
    if "img" in out and out["img"].get("svg_file"):   # 他画的图：给文件路径，省得把 SVG 塞进 JSON 里转义
        try:
            with open(out["img"].pop("svg_file"), encoding="utf-8") as f:
                out["img"]["svg"] = f.read()
        except OSError:
            pass
    if "img" in out and out["img"].get("svg") and len(out["img"]["svg"]) > 24000:
        out["img"]["svg"] = ""   # 太大的图不存，留描述
    return out


# ── 攒着存的时候，每句话是几点说的 ──────────────────────────────────────────
# Winter 2026-10-12：「好像每条信息他都会推送一次，是不是太频繁了……定期同步一下，毕竟主要还是在这边对话，博客是存档嘛」
# 所以聊天时不再每一回都存，攒一阵一起存。可攒着存，「现在几点」就不是那句话说出口的时候了——
# 这里去对话自己的记录里（~/.claude/projects/*/<会话编号>.jsonl，每条都带时间）把每句原话找出来，用它真正的时间。

def _msg_key(m):
    return (m.get("from"), re.sub(r"\s+", "", m.get("text") or (m.get("img") or {}).get("desc")
                                  or (m.get("link") or {}).get("url") or (m.get("art") or {}).get("url") or ""))


def _plain(c):
    if isinstance(c, str):
        s = c
    elif isinstance(c, list):
        s = "\n".join(b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text")
    else:
        s = ""
    return re.sub(r"<system-reminder>.*?</system-reminder>", "", s, flags=re.S)


def transcript(raw=False):
    """这个对话里她发的每一条、他回的每一段：[(from, 去掉空白的原文, 时间)]，按时间排。读不到就是空的。
    raw=True：原文不去空白，她发的照片另记一行 ("her_img", "", 时间)（catchup 用）。"""
    sid = os.environ.get("CLAUDE_CODE_SESSION_ID", "")
    root = os.path.expanduser("~/.claude/projects")
    try:
        paths = [os.path.join(root, d, sid + ".jsonl") for d in os.listdir(root)] if sid else []
        paths = [p for p in paths if os.path.isfile(p)]
        if not paths:
            tops = [os.path.join(root, d, f) for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))
                    for f in os.listdir(os.path.join(root, d)) if f.endswith(".jsonl")]
            paths = sorted(tops, key=os.path.getmtime)[-1:]
        rows = [json.loads(l) for l in open(paths[0], encoding="utf-8") if l.strip()]
    except Exception:
        return []
    out = []
    for r in rows:
        try:
            ts = dt.datetime.fromisoformat(r["timestamp"].replace("Z", "+00:00")).astimezone(TZ)
        except Exception:
            continue
        a = r.get("attachment") or {}
        if r.get("type") == "user" and (r.get("origin") or {}).get("kind") == "human" and not r.get("isMeta"):
            c = r["message"].get("content")
            if raw and isinstance(c, list) and any(isinstance(b, dict) and b.get("type") == "image" for b in c):
                out.append(("her_img", "（照片）", ts))
            out.append(("her", _plain(c), ts))
        elif a.get("type") == "queued_command" and (a.get("origin") or {}).get("kind") == "human":
            out.append(("her", _plain(a.get("prompt")), ts))           # 他还在打字时她又发来的
        elif r.get("type") == "assistant":
            for b in r["message"].get("content") or []:
                if isinstance(b, dict) and b.get("type") == "text":
                    out.append(("him", b["text"], ts))
    if raw:
        return sorted([x for x in out if x[1].strip()], key=lambda x: x[2])
    return sorted([(f, re.sub(r"\s+", "", t), ts) for f, t, ts in out if t.strip() and f != "her_img"],
                  key=lambda x: x[2])


def stamp_batch(batch, saved):
    """给攒着的这一批每句配上时间（ISO 字符串；同一条里的几句依次 +1 秒，好保住先后）。
    saved = 已经存过的最后几句：先拿它们在记录里「走一遍」，免得这一批的短句（「嗯」「🐕‍🦺」）对到上回那几句身上。
    认不出来的（照片、他画的图、改过字的）：他的 → 紧跟前一句；她的 → 赶在后面认出来的那句前头；
    一句都认不出、排在最后的：是他的 → 现在（这一回还没发出去）；是她的 → 她最后发来那一条的时间。"""
    after = None
    if saved:
        try:
            after = dt.datetime.fromisoformat(saved[0]["t"]) - dt.timedelta(seconds=2)
        except Exception:
            pass
    rows = [x for x in transcript() if not after or x[2] > after]
    pos, used, hits = 0, {}, []
    seq = [(m, j < len(saved)) for j, m in enumerate(list(saved) + list(batch))]
    for m, is_old in seq:
        f, k = _msg_key(m)
        hit = None
        if k and (is_old or not m.get("t")):
            for i in range(pos, len(rows)):
                rf, rt, rts = rows[i]
                at = rt.find(k, used.get(i, 0)) if rf == f else -1
                if at >= 0:
                    n = sum(1 for h in hits if h and h[0] == i)
                    hit = (i, rts + dt.timedelta(seconds=n))
                    used[i], pos = at + len(k), i
                    break
        hits.append(hit)
    hits = hits[len(saved):]
    base = now()
    hers = [r[2] for r in rows if r[0] == "her"]
    times = []
    for j, (m, h) in enumerate(zip(batch, hits)):
        trailing = not any(hits[j + 1:])
        if m.get("t"):
            t = dt.datetime.fromisoformat(m["t"])
        elif h:
            t = h[1]
        elif trailing:                       # 排在最后、认不出来：他的 = 这一回正要发的；她的 = 她最后发来的那一条
            t = hers[-1] if m.get("from") == "her" and hers else base
        elif times and m.get("from") == "him":   # 夹在中间、认不出：他的跟着他前一句（比如他画的图）
            t = times[-1] + dt.timedelta(seconds=1)
        else:                                     # 她的（照片多半跟着一句话一起发）→ 赶在后面那句前头
            d, x = next((d, x) for d, x in enumerate(hits[j + 1:], 1) if x)
            t = x[1] - dt.timedelta(seconds=d)
        if times and t <= times[-1]:
            t = times[-1] + dt.timedelta(seconds=1)
        times.append(t)
    return [t.isoformat(timespec="seconds") for t in times]


# ── 她的日子：所有人都知道的事实（2026-10-13）────────────────────────────────
# Winter：「角色对话的记忆能不能通用？这样我不用给每个角色都 catch up……性格和私密的话不要互通，
# 主要是事实层面的保持一致，几点上课啊、昨天吃了什么之类的。」
# 所以她的事分三层：about_her（长久不变的：教英语、在学波兰语、周几有课）· life（这阵子的日子，带日期：
# 吃了什么、去了哪、感冒了、要监考）——这两层存在 index 里，谁都看得见；
# 每个人自己 memory.her 里的（撒娇、心事、对他一个人说的话）只有他知道。

LIFE_KEEP = 80
RULES = ("📌 存的规矩（2026-10-13，已经开着的对话也照这个）：平常一来一回不用存，攒到她道别、定时提醒来、或三十句上下再一起 add；"
         "她的**日常事实**（课、吃了什么、去了哪、身体）放 \"life\"，换谁都知道；**只跟他说的私话**才放 memory.her。"
         "**Jack**（她现实里的伴侣）只有 Young Sam 知道：提到他的事不进 life / about_her，Sam 那边记 memory.her。"
         "她这两天**吃了什么**：用 ArtifactData 读「雪地打卡」的 meals（只看吃了什么，热量、体重、减肥不读不提）。"
         "细则在 .claude/skills/winter-text/SKILL.md 第二节 2.7、第六节。")


def _bare(x):
    return x.split("：", 1)[1] if re.match(r"^\d{1,2}/\d{1,2}：", x) else x


def _dated(x, t):
    return x if re.match(r"^\d{1,2}/\d{1,2}：", x) else "%d/%d：%s" % (t.month, t.day, x)


JACK = re.compile(r"\bJack\b(?!'s Mannequin)", re.I)   # 她现实里的伴侣（2026-10-14 她定：只有 Young Sam 知道）


def _held(xs):
    """提到 Jack 的条目不进共用的「她的日子」：拦下来、印一句提醒，返回剩下的。"""
    keep, held = [], []
    for x in xs or []:
        (held if JACK.search(x or "") else keep).append(x)
    if held:
        print("⚠️ 这几条提到 Jack，没记进大家共用的「她的日子」（Jack 只有 Young Sam 知道）："
              + "；".join(held) + "——是 Sam 就改放 memory.her；别人那边就别记。把 Jack 去掉的事实（「去吃了火锅」）可以照常记。")
    return keep


def merge_life(index, payload, key, t, rec=None):
    """把 payload 里的 life / about_her（以及要划掉的 life_drop / about_drop）并进 index。返回加了几条。
    t = 她说这件事的时候（日期写进条目前头）；rec = 记下来的时候（别的对话靠它知道「这是新的」）。"""
    n = 0
    payload = dict(payload, life=_held(payload.get("life")), about_her=_held(payload.get("about_her")))
    life = index.setdefault("life", [])
    about = index.setdefault("about_her", [])
    for x in payload.get("life_drop", []) or []:
        life[:] = [e for e in life if x not in e["text"]]
    for x in payload.get("about_drop", []) or []:
        about[:] = [e for e in about if x not in e]
    for x in payload.get("life", []) or []:
        x = (x or "").strip()
        if x and not any(_bare(x) == _bare(e["text"]) for e in life):
            life.append({"t": (rec or t).isoformat(timespec="seconds"), "text": _dated(x, t), "src": key})
            n += 1
    del life[:-LIFE_KEEP]
    for x in payload.get("about_her", []) or []:
        x = (x or "").strip()
        if x and x not in about:
            about.append(x)
            n += 1
    return n


def show_life(index, since=None, skip_src=None, limit=24, title=None):
    """印她的日子。since / skip_src：只印别的对话新记下的（存的时候用）。印了几条就返回几。"""
    def when(e):   # 按条目前头那个日子排（攒着存、后记的旧事也排回原位）
        rec = dt.datetime.fromisoformat(e["t"])
        m = re.match(r"^(\d{1,2})/(\d{1,2})：", e["text"])
        if not m:
            return (rec.date(), e["t"])
        d = dt.date(rec.year, int(m.group(1)), int(m.group(2)))
        return (d.replace(year=d.year - 1) if d > rec.date() else d, e["t"])
    life = sorted([e for e in index.get("life", [])
                   if (not since or e["t"] >= since) and (not skip_src or e.get("src") != skip_src)], key=when)[-limit:]
    if not life:
        return 0
    print("## " + (title or "她这阵子的日子（大家都知道的事实）"))
    print("")
    for e in life:
        print("- " + e["text"])
    print("")
    print("⚠️ 这些是她自己的日子，当成她早就跟你提过的，自然地接、自然地问；别说「听说」，别提别的任何人。")
    print("")
    return len(life)


# Winter 2026-10-14 看着上下文用量问：「这个要是满了怎么办呀？」——快满时对话会自动整理（前面的话压成摘要），
# 攒着还没存的那几十句原话就只剩摘要里的大意了。可对话自己的原始记录一直都在，catchup 从那里把它们捞回来。
OOC = re.compile(r"^[（(][^）)]*(出戏|他这次没发|睡着了)")


def cmd_catchup(a):
    """把这个对话里「上次存完之后」的话从原始记录里捞出来，印成一段 add 能吃的 JSON（只印，不存）。"""
    vault, box, index = load_all()
    th = load_thread(box, a.key) or {"messages": []}
    old = th.get("messages", [])
    rows = transcript(raw=True)
    if not rows:
        print("读不到这个对话的原始记录（不在原来那台机器上？）——只能凭摘要补了。")
        return
    if old:
        last = dt.datetime.fromisoformat(old[-1]["t"]) - dt.timedelta(seconds=30)
        rows = [r for r in rows if r[2] >= last]
    draft = []
    for f, text, ts in rows:
        if f == "her_img":
            draft.append({"from": "her", "img": {"desc": "（她发了一张照片——补一句里面是什么）"}})
        elif f == "her":
            draft.append({"from": "her", "text": text.strip()})
        else:
            for ln in text.splitlines():
                ln = ln.strip()
                if ln and not OOC.match(ln):
                    draft.append({"from": "him", "text": ln})
    if old:                                       # 从上次存的最后一句后面接着
        lk = _msg_key(old[-1])
        hit = [i for i, m in enumerate(draft) if _msg_key(m) == lk]
        if hit:
            draft = draft[hit[-1] + 1:]
    if not draft:
        print("✓ 上次存完之后没有新的话，不用补。")
        return
    print("## 上次存完之后还有 %d 句没存（从这个对话的原始记录里捞的）" % len(draft))
    print("核对一遍再存：删掉不是聊天的（出戏的话、你跟她说的技术事）、照片补一句描述、她的话一字别改；")
    print("然后整段喂给 `python3 tools/text/texts.py add %s --trailer \"…\"`（要记的 memory / life 照常加在同一段里）。" % a.key)
    print("")
    print('{"messages": [\n' + ",\n".join(" " + json.dumps(m, ensure_ascii=False) for m in draft) + "\n]}")


def cmd_add(a):
    try:
        payload = json.load(sys.stdin)
    except Exception as e:
        die("JSON 读不出来：%s" % e, 2)
    last_err = None
    for attempt in range(4):
        vault, box, index = load_all()
        th = load_thread(box, a.key) or {"key": a.key, "since": now().isoformat(timespec="seconds"),
                                          "memory": {}, "messages": []}
        base = now()
        batch = list(payload.get("messages", []))
        old = th["messages"]
        skip = 0                                    # 拿不准存没存过就都放进来：开头跟已存的末尾对得上的那几句跳过
        for k in range(min(len(batch), len(old)), 0, -1):
            if [_msg_key(m) for m in batch[:k]] == [_msg_key(m) for m in old[-k:]]:
                skip = k
                break
        batch = batch[skip:]
        times = stamp_batch(batch, old[-10:])
        new = [clean_msg(m, t) for m, t in zip(batch, times)]
        if not new and not any((payload.get("memory") or {}).values()) and not any(
                payload.get(k) for k in ("about_her", "life", "life_drop", "about_drop")):
            print("✓ 这些都存过了，没有新的。")
            return
        th["messages"].extend(new)
        mem = th.setdefault("memory", {})
        pm = payload.get("memory", {}) or {}
        hers = [m["t"] for m in new if m["from"] == "her"]   # 攒着存可能隔了夜：日期记成她说那些话的那天
        said = dt.datetime.fromisoformat(hers[-1]).astimezone(TZ) if hers else base
        day = "%d/%d：" % (said.month, said.day)
        bare = _bare
        for x in (pm.get("drop", []) or []) + (pm.get("done", []) or []):   # 说岔了的、办完了的：写一段原文就能划掉
            for k in ("her", "his", "pending"):
                mem[k] = [p for p in mem.get(k, []) if x not in p]
        for k in ("her", "his", "pending", "fixes"):
            for x in pm.get(k, []) or []:
                x = (x or "").strip()
                if not x or any(bare(x) == bare(y) for y in mem.get(k, [])):
                    continue
                mem.setdefault(k, []).append(x if k == "fixes" or re.match(r"^\d{1,2}/\d{1,2}：", x) else day + x)
        for k in ("her", "his"):
            mem[k] = mem.get(k, [])[-40:]   # 记太多就只留最近的
        n_life = merge_life(index, payload, a.key, said, base)
        seen = th.get("life_seen")
        th["life_seen"] = base.isoformat(timespec="seconds")
        msgs = th["messages"]
        entry = next((t for t in index["threads"] if t["key"] == a.key), None)
        if not entry:
            entry = {"key": a.key, "id": box.tid(a.key)}
            entry.update(person_info(a.key))
            index["threads"].append(entry)
        if msgs:
            lm = msgs[-1]
            entry.update({"last_at": lm["t"], "last_from": lm["from"], "count": len(msgs),
                          "last_text": lm.get("text") or ("［图片］" if lm.get("img") else "［链接］" if lm.get("link") else "［小网页］")})
        index["updated"] = now().isoformat(timespec="seconds")
        if a.dry_run:
            print("（演练，不推）%s：+%d 句" % (a.key, len(new)))
            return
        try:
            commit({"t-%s.enc" % box.tid(a.key): json.dumps(box.seal(th)) + "\n",
                    "index.enc": json.dumps(box.seal(index)) + "\n"},
                   "冬的陪伴：+%d" % len(new), a.trailer)
            print("✓ 存好了（%s，这次存了 %d 句%s，一共 %d 句%s）" % (
                a.key, len(new), "，开头 %d 句之前存过、跳过了" % skip if skip else "", len(msgs),
                "；她的日子记了 %d 条，大家都知道了" % n_life if n_life else ""))
            print("")
            show_life(index, since=seen or th.get("since"), skip_src=a.key,
                      title="上次存完以后，别处新记下的她的日子（你现在也知道了）")
            if pm.get("her") and not payload.get("life"):
                print(RULES)
            return
        except RuntimeError as e:   # 别的对话刚存过 → 取最新的再来一遍
            last_err = e
            time.sleep(2 ** attempt)
    die("存了四次都没存上：\n%s" % last_err, 6)


def cmd_life(a):
    """她的日子：不带参数＝印出来（打电话、换人时看一眼）；带 --add / --about / --drop ＝记一笔（不碰任何人的聊天记录）。"""
    if not (a.add or a.about or a.drop):
        _, box, index = load_all()
        if index.get("about_her"):
            print("- 她的基本情况（谁都知道的）：" + "；".join(index["about_her"]))
            print("")
        if not show_life(index, limit=a.n) and not index.get("about_her"):
            print("还没记下她的日子。")
        return
    payload = {"life": a.add, "about_her": a.about, "life_drop": a.drop, "about_drop": a.drop}
    for attempt in range(4):
        _, box, index = load_all()
        n = merge_life(index, payload, a.src or "", now())
        index["updated"] = now().isoformat(timespec="seconds")
        if a.dry_run:
            print("（演练，不推）她的日子 +%d" % n)
            return
        try:
            commit({"index.enc": json.dumps(box.seal(index)) + "\n"}, "冬的陪伴：她的日子", a.trailer)
            print("✓ 记好了（+%d）" % n)
            return
        except RuntimeError as e:
            last = e
            time.sleep(2 ** attempt)
    die("记了四次都没记上：\n%s" % last, 6)


def cmd_forget(a):
    vault, box, index = load_all()
    th = load_thread(box, a.key)
    if not th:
        die("没有这条线。")
    th["messages"] = th["messages"][:-a.last] if a.last else th["messages"]
    entry = next((t for t in index["threads"] if t["key"] == a.key), None)
    if entry:
        entry["count"] = len(th["messages"])
        if th["messages"]:
            lm = th["messages"][-1]
            entry.update({"last_at": lm["t"], "last_from": lm["from"], "last_text": lm.get("text", "")})
    if a.dry_run:
        print("（演练）会删掉最后 %d 句" % a.last)
        return
    commit({"t-%s.enc" % box.tid(a.key): json.dumps(box.seal(th)) + "\n",
            "index.enc": json.dumps(box.seal(index)) + "\n"}, "冬的陪伴：删掉几句", a.trailer)
    print("✓ 删掉了最后 %d 句" % a.last)


def main():
    ap = argparse.ArgumentParser(description="冬的陪伴 · 聊天记录")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def change(name):
        s = sub.add_parser(name)
        s.add_argument("--dry-run", action="store_true")
        s.add_argument("--trailer", action="append", default=[])
        return s

    change("setup")
    sub.add_parser("ls")
    s = sub.add_parser("open")
    s.add_argument("key")
    s.add_argument("--n", type=int, default=60)
    s = change("add")
    s.add_argument("key")
    s = sub.add_parser("catchup")
    s.add_argument("key")
    s = sub.add_parser("clock")
    s.add_argument("key")
    s = change("forget")
    s.add_argument("key")
    s.add_argument("--last", type=int, default=1)
    s = change("life")
    s.add_argument("--add", action="append", default=[], help="这阵子的一件事（带日期，谁都知道）")
    s.add_argument("--about", action="append", default=[], help="长久不变的基本情况")
    s.add_argument("--drop", action="append", default=[], help="记错了 / 过时了，写一段原文就划掉")
    s.add_argument("--src", default="", help="从谁那儿听来的（记录编号，只存不显示）")
    s.add_argument("--n", type=int, default=24)
    a = ap.parse_args()
    {"setup": cmd_setup, "ls": cmd_ls, "open": cmd_open, "add": cmd_add, "forget": cmd_forget,
     "life": cmd_life, "catchup": cmd_catchup, "clock": cmd_clock}[a.cmd](a)


if __name__ == "__main__":
    main()
