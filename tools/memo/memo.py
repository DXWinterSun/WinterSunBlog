#!/usr/bin/env python3
"""冬的备忘本 · 在对话里替 Winter 改备忘用的小工具。

备忘数据只有一份：仓库 `memo` 分支上的 `memo.json`（不在 main 上——
放 main 的话她每改一条就要整站重建一次，还会掐掉正在跑的正文部署）。
网页 /memo/ 和桌面小组件（memo/widget/winter-memo.js）读的都是这一份。

本工具不碰工作区：直接用 git 底层命令在 origin/memo 上做一次提交再推上去，
推不上（她刚在手机上改过）就重新取一遍、把这次的改动重放一遍再推，最多四次。

    python3 tools/memo/memo.py ls                 # 全部列出来（含短编号）
    python3 tools/memo/memo.py ls 工作             # 只看一页
    python3 tools/memo/memo.py add 灵感 "做一期采访切片" "Sam 新片路透整理"
    python3 tools/memo/memo.py add 工作 "申报中邮" --due 10-15 --pin
    python3 tools/memo/memo.py done 中邮           # 编号或一段原文都行
    python3 tools/memo/memo.py undone 中邮
    python3 tools/memo/memo.py edit k3f9a2 --text "新的说法" --page 生活 --due none
    python3 tools/memo/memo.py rm k3f9a2
    python3 tools/memo/memo.py top k3f9a2          # 挪到这一页最前面
    python3 tools/memo/memo.py clear-done [页]      # 清掉已完成的
    python3 tools/memo/memo.py pages               # 看有哪几页
    python3 tools/memo/memo.py page-add 读书 📚     # 加一页（page-rename / page-rm 同理）

所有改动类命令都可以加 --dry-run（只打印、不推）和 --trailer "..."（给提交说明补尾行，
可重复；会话要求在提交里署名时用）。
"""
import argparse
import datetime as dt
import json
import random
import re
import string
import subprocess
import sys
import time

BRANCH = "memo"
FILE = "memo.json"
REMOTE = "origin"
TZ = dt.timezone(dt.timedelta(hours=8))   # Winter 在国内，时间一律按北京时间记

# 页面名的口语叫法 → 页面 id（她在对话里怎么说都能认出来）
ALIASES = {
    "idea": ["灵感", "点子", "想法", "视频", "帖子", "选题", "创作", "idea", "ideas", "💡"],
    "sam": ["sam", "山姆", "他", "❣️", "❣"],
    "work": ["工作", "上班", "学校", "教学", "work", "💼"],
    "life": ["生活", "日常", "家里", "life", "🏠"],
}


def now_iso():
    return dt.datetime.now(TZ).isoformat(timespec="seconds")


def today():
    return dt.datetime.now(TZ).date()


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
            git("fetch", "-q", REMOTE, f"+refs/heads/{BRANCH}:refs/remotes/{REMOTE}/{BRANCH}")
            return
        except RuntimeError as e:
            last = e
    raise last


def load():
    return json.loads(git("show", f"{REMOTE}/{BRANCH}:{FILE}"))


def dump(data):
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def commit_and_push(data, message, trailers):
    blob = git("hash-object", "-w", "--stdin", input=dump(data))
    ref = f"{REMOTE}/{BRANCH}"
    entries = [e for e in git("ls-tree", ref).splitlines() if not e.endswith("\t" + FILE)]
    entries.append(f"100644 blob {blob}\t{FILE}")
    tree = git("mktree", input="\n".join(entries) + "\n")
    msg = message
    if trailers:
        msg += "\n\n" + "\n".join(trailers)
    commit = git("commit-tree", tree, "-p", git("rev-parse", ref), "-m", msg)
    git("push", "-q", REMOTE, f"{commit}:refs/heads/{BRANCH}")
    return commit


def new_id(taken):
    while True:
        s = "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(6))
        if s not in taken:
            return s


# ————— 认页面、认条目 —————

def find_page(data, word):
    w = (word or "").strip().lower()
    pages = data["settings"]["pages"]
    for p in pages:
        if w in (p["id"].lower(), p["name"].lower(), p.get("emoji", "")):
            return p
    for pid, words in ALIASES.items():
        if w in [x.lower() for x in words]:
            for p in pages:
                if p["id"] == pid:
                    return p
    for p in pages:   # 名字的一部分
        if w and w in p["name"].lower():
            return p
    names = "、".join(p["emoji"] + p["name"] for p in pages)
    raise SystemExit(f"认不出「{word}」是哪一页。现有：{names}")


def find_item(data, key, include_done=True):
    k = key.strip()
    items = [i for i in data["items"] if include_done or not i.get("done")]
    exact = [i for i in items if i["id"] == k]
    if exact:
        return exact[0]
    hits = [i for i in items if i["id"].startswith(k)] or \
           [i for i in items if k.lower() in i["text"].lower()]
    if len(hits) == 1:
        return hits[0]
    if not hits:
        raise SystemExit(f"找不到「{key}」。先 ls 看一眼编号。")
    # 同一段字命中好几条时，没完成的优先
    open_hits = [i for i in hits if not i.get("done")]
    if len(open_hits) == 1:
        return open_hits[0]
    lines = "\n".join(f"  {i['id']}  {i['text']}" + ("（已完成）" if i.get("done") else "") for i in hits)
    raise SystemExit(f"「{key}」对上了好几条，用编号再说一次：\n{lines}")


def parse_due(s):
    if s is None:
        return None
    s = s.strip()
    if s.lower() in ("none", "no", "清除", "无", "-", ""):
        return ""
    t = today()
    rel = {"今天": 0, "明天": 1, "后天": 2, "大后天": 3}
    if s in rel:
        return (t + dt.timedelta(days=rel[s])).isoformat()
    m = re.fullmatch(r"(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})", s)
    if m:
        return dt.date(int(m[1]), int(m[2]), int(m[3])).isoformat()
    m = re.fullmatch(r"(\d{1,2})[-/.月](\d{1,2})日?", s)
    if m:
        d = dt.date(t.year, int(m[1]), int(m[2]))
        if d < t - dt.timedelta(days=60):   # 写 1-5 而今天是 12 月 → 明年
            d = d.replace(year=t.year + 1)
        return d.isoformat()
    raise SystemExit(f"日期「{s}」看不懂：写成 10-15、2026-10-15、今天 / 明天 / 后天，或 none 清掉。")


def sort_key(i):
    return (0 if i.get("pin") else 1, i.get("order", 0), i.get("created", ""))


def page_items(data, pid, done=False):
    return sorted([i for i in data["items"] if i["page"] == pid and bool(i.get("done")) == done],
                  key=sort_key)


def top_order(data, pid):
    orders = [i.get("order", 0) for i in data["items"] if i["page"] == pid]
    return (min(orders) - 1) if orders else 0


def show(data, only=None):
    out = []
    for p in data["settings"]["pages"]:
        if only and p["id"] != only["id"]:
            continue
        todo, done = page_items(data, p["id"]), page_items(data, p["id"], True)
        out.append(f"{p['emoji']} {p['name']}（{len(todo)} 条没做，{len(done)} 条做完）")
        for i in todo:
            extra = []
            if i.get("pin"):
                extra.append("置顶")
            if i.get("due"):
                extra.append("到期 " + i["due"])
            if i.get("note"):
                extra.append("备注：" + i["note"].replace("\n", " / "))
            out.append(f"   {i['id']}  ○ {i['text']}" + (f"   〔{'；'.join(extra)}〕" if extra else ""))
        for i in done:
            out.append(f"   {i['id']}  ✓ {i['text']}")
    print("\n".join(out) if out else "（空）")


# ————— 各个动作：都写成「拿到最新数据 → 改 → 返回提交说明」，推不上时可原样重放 —————

def op_add(a):
    def run(data):
        p = find_page(data, a.page)
        taken = {i["id"] for i in data["items"]} | set(data.get("gone", {}))
        due = parse_due(a.due) if a.due else ""
        texts = [t.strip() for t in a.text if t.strip()]
        if not texts:
            raise SystemExit("没有要记的内容。")
        order = top_order(data, p["id"])
        # 一次记好几条时，保持她说的先后：第一条在最上面
        for k, t in enumerate(texts):
            iid = new_id(taken)
            taken.add(iid)
            stamp = now_iso()
            item = {"id": iid, "page": p["id"], "text": t, "done": False,
                    "order": order - (len(texts) - 1) + k, "created": stamp, "updated": stamp}
            if a.note:
                item["note"] = a.note
            if due:
                item["due"] = due
            if a.pin:
                item["pin"] = True
            data["items"].append(item)
        return f"备忘：{p['emoji']}{p['name']} + " + "、".join(f"「{t}」" for t in texts)
    return run


def op_done(a, value):
    def run(data):
        it = find_item(data, a.key, include_done=not value)
        it["done"] = value
        it["updated"] = now_iso()
        if value:
            it["doneAt"] = it["updated"]
        else:
            it.pop("doneAt", None)
            it["order"] = top_order(data, it["page"])
        return f"备忘：{'✓ 做完' if value else '↺ 改回没做'}「{it['text']}」"
    return run


def op_rm(a):
    def run(data):
        it = find_item(data, a.key)
        data["items"] = [i for i in data["items"] if i["id"] != it["id"]]
        data.setdefault("gone", {})[it["id"]] = now_iso()
        return f"备忘：删掉「{it['text']}」"
    return run


def op_edit(a):
    def run(data):
        it = find_item(data, a.key)
        changed = []
        if a.text:
            it["text"] = a.text.strip()
            changed.append("内容")
        if a.page:
            p = find_page(data, a.page)
            if p["id"] != it["page"]:
                it["page"] = p["id"]
                it["order"] = top_order(data, p["id"])
                changed.append("挪到" + p["name"])
        if a.note is not None:
            if a.note.strip():
                it["note"] = a.note
            else:
                it.pop("note", None)
            changed.append("备注")
        if a.due is not None:
            d = parse_due(a.due)
            if d:
                it["due"] = d
            else:
                it.pop("due", None)
            changed.append("日期")
        if a.pin:
            it["pin"] = True
            changed.append("置顶")
        if a.unpin:
            it.pop("pin", None)
            changed.append("取消置顶")
        if not changed:
            raise SystemExit("没说要改什么。")
        it["updated"] = now_iso()
        return f"备忘：改「{it['text']}」（{'、'.join(changed)}）"
    return run


def op_top(a):
    def run(data):
        it = find_item(data, a.key, include_done=False)
        it["order"] = top_order(data, it["page"])
        it["updated"] = now_iso()
        return f"备忘：「{it['text']}」挪到最前"
    return run


def op_clear_done(a):
    def run(data):
        p = find_page(data, a.page) if a.page else None
        gone = [i for i in data["items"] if i.get("done") and (not p or i["page"] == p["id"])]
        if not gone:
            raise SystemExit("没有做完的条目可清。")
        stamp = now_iso()
        for i in gone:
            data.setdefault("gone", {})[i["id"]] = stamp
        ids = {i["id"] for i in gone}
        data["items"] = [i for i in data["items"] if i["id"] not in ids]
        return f"备忘：清掉 {len(gone)} 条做完的" + (f"（{p['name']}）" if p else "")
    return run


def op_page_add(a):
    def run(data):
        pages = data["settings"]["pages"]
        if any(p["name"] == a.name for p in pages):
            raise SystemExit(f"已经有「{a.name}」这一页了。")
        taken = {p["id"] for p in pages}
        pid = new_id(taken)
        pages.append({"id": pid, "name": a.name, "emoji": a.emoji or "📝",
                      "color": a.color or "#8C7BB8", "hint": a.hint or ""})
        data["settings"]["updated"] = now_iso()
        return f"备忘：加一页 {a.emoji or '📝'}{a.name}"
    return run


def op_page_rename(a):
    def run(data):
        p = find_page(data, a.page)
        old = p["emoji"] + p["name"]
        if a.name:
            p["name"] = a.name
        if a.emoji:
            p["emoji"] = a.emoji
        if a.hint is not None:
            p["hint"] = a.hint
        if a.color:
            p["color"] = a.color
        data["settings"]["updated"] = now_iso()
        return f"备忘：{old} → {p['emoji']}{p['name']}"
    return run


def op_page_rm(a):
    def run(data):
        p = find_page(data, a.page)
        pages = data["settings"]["pages"]
        if len(pages) == 1:
            raise SystemExit("只剩这一页了，不能删。")
        left = [i for i in data["items"] if i["page"] == p["id"]]
        if left and not a.force:
            raise SystemExit(f"「{p['name']}」里还有 {len(left)} 条。确定连条目一起删就加 --force，"
                             "或者先用 edit --page 挪走。")
        stamp = now_iso()
        for i in left:
            data.setdefault("gone", {})[i["id"]] = stamp
        data["items"] = [i for i in data["items"] if i["page"] != p["id"]]
        data["settings"]["pages"] = [x for x in pages if x["id"] != p["id"]]
        data["settings"]["updated"] = stamp
        return f"备忘：删掉一页 {p['emoji']}{p['name']}"
    return run


def apply(op, a):
    fetch()
    last = None
    for attempt in range(4):
        data = load()
        msg = op(data)
        data["updated"] = now_iso()
        if a.dry_run:
            print("（演练，不推）" + msg)
            show(data)
            return
        try:
            commit_and_push(data, msg, a.trailer)
            print("✓ " + msg)
            return
        except RuntimeError as e:   # 多半是她刚在手机上改过 → 取最新的、重放一遍
            last = e
            time.sleep(2 ** attempt)
            fetch()
    raise SystemExit(f"推了四次都没推上去：\n{last}")


def main():
    ap = argparse.ArgumentParser(description="冬的备忘本")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def change(name, **kw):
        s = sub.add_parser(name, **kw)
        s.add_argument("--dry-run", action="store_true")
        s.add_argument("--trailer", action="append", default=[])
        return s

    s = sub.add_parser("ls")
    s.add_argument("page", nargs="?")
    sub.add_parser("pages")

    s = change("add")
    s.add_argument("page")
    s.add_argument("text", nargs="+")
    s.add_argument("--due")
    s.add_argument("--note")
    s.add_argument("--pin", action="store_true")

    for name in ("done", "undone", "rm", "top"):
        s = change(name)
        s.add_argument("key")

    s = change("edit")
    s.add_argument("key")
    s.add_argument("--text")
    s.add_argument("--page")
    s.add_argument("--note")
    s.add_argument("--due")
    s.add_argument("--pin", action="store_true")
    s.add_argument("--unpin", action="store_true")

    s = change("clear-done")
    s.add_argument("page", nargs="?")

    s = change("page-add")
    s.add_argument("name")
    s.add_argument("emoji", nargs="?")
    s.add_argument("--hint")
    s.add_argument("--color")

    s = change("page-rename")
    s.add_argument("page")
    s.add_argument("--name")
    s.add_argument("--emoji")
    s.add_argument("--hint")
    s.add_argument("--color")

    s = change("page-rm")
    s.add_argument("page")
    s.add_argument("--force", action="store_true")

    a = ap.parse_args()
    if a.cmd in ("ls", "pages"):
        fetch()
        data = load()
        if a.cmd == "pages":
            for p in data["settings"]["pages"]:
                n = len(page_items(data, p["id"]))
                print(f"{p['id']:>6}  {p['emoji']} {p['name']}  {n} 条  {p.get('hint', '')}")
        else:
            show(data, find_page(data, a.page) if a.page else None)
        return

    ops = {
        "add": op_add(a) if a.cmd == "add" else None,
        "done": op_done(a, True) if a.cmd == "done" else None,
        "undone": op_done(a, False) if a.cmd == "undone" else None,
        "rm": op_rm(a) if a.cmd == "rm" else None,
        "edit": op_edit(a) if a.cmd == "edit" else None,
        "top": op_top(a) if a.cmd == "top" else None,
        "clear-done": op_clear_done(a) if a.cmd == "clear-done" else None,
        "page-add": op_page_add(a) if a.cmd == "page-add" else None,
        "page-rename": op_page_rename(a) if a.cmd == "page-rename" else None,
        "page-rm": op_page_rm(a) if a.cmd == "page-rm" else None,
    }
    apply(ops[a.cmd], a)


if __name__ == "__main__":
    main()
