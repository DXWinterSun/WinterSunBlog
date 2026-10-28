#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""🔒 冬的私人档案（出行、证件、订单这类绝不能明文进公开仓库的东西）。

2026-10-27 起：出行交接档案里有护照号、签证确认号、住址、邮箱、单位和收入，
仓库是公开的，所以跟「冬的陪伴」一样加密存放——同一套算法、同一个密码（WINTER_TEXT_KEY），
但放在自己的 **`private` 分支**、自己的盐，跟聊天记录互不相干。

- AES-256-GCM，钥匙 = PBKDF2-SHA256(她的密码, 盐, 310000 轮)。除了 vault.json，分支上每个文件都是加密的。
- 文件：vault.json · index.enc（有哪几份档案）· d-<编号>.enc（一份档案一个文件，编号打乱过、看不出是什么）
- ⚠️ 永远别让她把密码打进聊天里，也别把密码、档案正文写进 main 上的任何文件或提交说明。

    python3 tools/private/private.py setup                          # 第一次：建好；以后：验一下密码
    python3 tools/private/private.py ls                             # 都有哪几份
    python3 tools/private/private.py show <名字>                    # 读一份（正文 + 带日期的进度）
    python3 tools/private/private.py show <名字> --log 10           # 只看最近 10 条进度
    python3 tools/private/private.py note <名字> "材料打印好了"      # 记一笔进度（自动带日期）
    python3 tools/private/private.py put <名字> --title "标题" < 档案.md   # 整份正文换新（进度留着）
    python3 tools/private/private.py show <名字> --page             # 印出网页上那份（JSON）
    python3 tools/private/private.py page <名字> < 网页.json        # 换掉网页上那份（书桌上「冬的行程」/trip/ 读它）
    ⚠️ 这里和 main 上任何文件都别写真的档案名、日期、号码——公开的。

改动类命令都可以加 --trailer "..."（提交说明尾行，可重复）和 --dry-run。
测试时用 WINTER_PRIVATE_REMOTE / WINTER_PRIVATE_BRANCH 指到别处，别碰真的 private 分支。

网页那份（2026-10-28 Winter：「做，重要信息都放进去」）：每份档案除了正文和进度，还可以带一份 page（JSON），
博客书桌上那本上锁的「冬的行程」（trip/index.html）用同一个密码在浏览器里解开、照它排版。
格式写在 trip/index.html 开头的注释里。改了待办、票、日程，就 `show --page` 取出来、改好、`page` 存回去。
"""

import argparse
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "text"))
from texts import Box, ITER, b64, unb64, die, now, password  # noqa: E402  同一套加密，别各写一份

REMOTE = os.environ.get("WINTER_PRIVATE_REMOTE", "origin")
BRANCH = os.environ.get("WINTER_PRIVATE_BRANCH", "private")
REF = "refs/winterprivate/%s" % BRANCH
CHECK = "冬的私人档案"


# ───────────────────────── git（不碰工作区） ─────────────────────────

def git(*args, input=None):
    r = subprocess.run(["git", *args], input=input, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("git " + " ".join(args) + " 失败：\n" + r.stderr.strip())
    return r.stdout.strip()


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
    entries = {}
    if has_ref():
        for line in git("ls-tree", REF).splitlines():
            meta, name = line.split("\t", 1)
            entries[name] = meta
    for name, text in files.items():
        entries[name] = "100644 blob " + git("hash-object", "-w", "--stdin", input=text)
    tree = git("mktree", input="".join("%s\t%s\n" % (m, n) for n, m in sorted(entries.items())))
    msg = message + ("\n\n" + "\n".join(trailers) if trailers else "")
    parent = ["-p", git("rev-parse", REF)] if has_ref() else []
    c = git("commit-tree", tree, *parent, "-m", msg)
    last = None
    for wait in (0, 2, 4, 8, 16):
        time.sleep(wait)
        try:
            git("push", "-q", REMOTE, "%s:refs/heads/%s" % (c, BRANCH))
            git("update-ref", REF, c)
            return
        except RuntimeError as e:
            last = e
    raise last


# ───────────────────────── 读写 ─────────────────────────

def seal(box, obj):
    return json.dumps(box.seal(obj)) + "\n"


def load(need=True):
    fetch()
    raw = read_file("vault.json")
    if not raw:
        if need:
            die("NO_VAULT：还没建过（先跑 `private.py setup`）。", 5)
        return None, None
    vault = json.loads(raw)
    box = Box(password(), unb64(vault["salt"]))
    try:
        if box.open(vault["check"]) != CHECK:
            raise ValueError
    except Exception:
        die("BAD_KEY：WINTER_TEXT_KEY 跟当初设的密码对不上，解不开。（别重建、别覆盖，问她是不是改过密码。）", 4)
    idx = read_file("index.enc")
    return box, (box.open(json.loads(idx)) if idx else {"docs": []})


def fname(box, name):
    return "d-%s.enc" % box.tid(name)


def load_doc(box, name):
    raw = read_file(fname(box, name))
    return box.open(json.loads(raw)) if raw else None


def stamp():
    return now().isoformat(timespec="minutes")


def save(box, index, doc, message, a):
    t = stamp()
    doc["updated"] = t
    rows = [d for d in index["docs"] if d["name"] != doc["name"]]
    rows.append({"name": doc["name"], "title": doc["title"], "created": doc.get("created", t), "updated": t})
    index["docs"] = sorted(rows, key=lambda d: d["name"])
    if a.dry_run:
        print("（演练）不提交。")
        return
    commit({fname(box, doc["name"]): seal(box, doc), "index.enc": seal(box, index)}, message, a.trailer)


# ───────────────────────── 命令 ─────────────────────────

def cmd_setup(a):
    pw = password()
    if fetch() and read_file("vault.json"):
        load()
        print("✓ 密码对得上，档案都在。")
        return
    salt = os.urandom(16)
    box = Box(pw, salt)
    vault = {"v": 1, "kdf": "PBKDF2-SHA256", "iter": ITER, "salt": b64(salt), "check": box.seal(CHECK),
             "note": "冬的私人档案。除了这个文件，别的都是加密的；钥匙只有 Winter 知道。"}
    if a.dry_run:
        print("（演练）会建好 vault 和空目录。")
        return
    commit({"vault.json": json.dumps(vault, ensure_ascii=False, indent=1) + "\n",
            "index.enc": seal(box, {"docs": []})}, "私人档案：开张", a.trailer)
    print("✓ 建好了。")


def cmd_ls(a):
    box, index = load()
    if not index["docs"]:
        print("（还没有档案）")
    for d in index["docs"]:
        print("%-16s %s  · 最后改 %s" % (d["name"], d["title"], d["updated"][:16].replace("T", " ")))


def cmd_show(a):
    box, index = load()
    doc = load_doc(box, a.name)
    if not doc:
        die("没有叫 %s 的档案。现有：%s" % (a.name, "、".join(d["name"] for d in index["docs"]) or "（空）"), 2)
    if a.page:
        print(json.dumps(doc.get("page") or {}, ensure_ascii=False, indent=1))
        return
    if a.log is None:
        print(doc["body"].rstrip())
        print()
    log = doc.get("log", [])
    print("## 进度（%d 条，新的在下面）" % len(log))
    for e in log[-a.log:] if a.log else log:
        print("- %s　%s" % (e["at"][:16].replace("T", " "), e["text"]))


def cmd_put(a):
    body = sys.stdin.read()
    if not body.strip():
        die("正文是空的（从标准输入喂进来）。", 2)
    box, index = load()
    doc = load_doc(box, a.name) or {"name": a.name, "created": stamp(), "log": []}
    if not doc.get("title") and not a.title:
        die("新档案要给 --title。", 2)
    doc["title"] = a.title or doc["title"]
    doc["body"] = body
    save(box, index, doc, "私人档案：更新一份", a)
    print("✓ 存好了：%s（%d 字）" % (doc["title"], len(body)))


def cmd_page(a):
    raw = sys.stdin.read()
    try:
        page = json.loads(raw)
    except ValueError as e:
        die("网页那份不是合法的 JSON：%s" % e, 2)
    box, index = load()
    doc = load_doc(box, a.name)
    if not doc:
        die("没有叫 %s 的档案。" % a.name, 2)
    doc["page"] = page
    save(box, index, doc, "私人档案：更新网页那份", a)
    print("✓ 网页那份换好了，刷新「冬的行程」就看得到。")


def cmd_note(a):
    box, index = load()
    doc = load_doc(box, a.name)
    if not doc:
        die("没有叫 %s 的档案。" % a.name, 2)
    for text in a.text:
        doc.setdefault("log", []).append({"at": stamp(), "text": text})
    save(box, index, doc, "私人档案：记一笔", a)
    print("✓ 记上了 %d 条。" % len(a.text))


def main():
    ap = argparse.ArgumentParser(description="冬的私人档案（加密）")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def change(name):
        s = sub.add_parser(name)
        s.add_argument("--trailer", action="append", default=[])
        s.add_argument("--dry-run", action="store_true")
        return s

    change("setup")
    sub.add_parser("ls")
    s = sub.add_parser("show")
    s.add_argument("name")
    s.add_argument("--log", type=int, nargs="?", const=10, default=None, help="只看最近几条进度")
    s.add_argument("--page", action="store_true", help="印出网页上那份（JSON）")
    s = change("put")
    s.add_argument("name")
    s.add_argument("--title", default="")
    s = change("page")
    s.add_argument("name")
    s = change("note")
    s.add_argument("name")
    s.add_argument("text", nargs="+")
    a = ap.parse_args()
    {"setup": cmd_setup, "ls": cmd_ls, "show": cmd_show, "put": cmd_put, "page": cmd_page, "note": cmd_note}[a.cmd](a)


if __name__ == "__main__":
    main()
