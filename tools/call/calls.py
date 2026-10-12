#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""☎ 打给他 · 通话记录（让他下一通还记得上一通）。

Winter 2026-10-12 选的：「记几句，下次接着问」。挂断之后由 Claude 记两三句——
她今天说了什么事、他答应了什么、她纠正过哪里不像他——下次接通，brief.py 会把这些带上。

数据只有一份：仓库 **`calls` 分支**上的 `calls.json`（跟灵感本的 memo 分支同一个道理：
不放 main，记一笔就不会触发整站重建、也不会掐掉别的对话正在跑的正文部署）。
本工具不碰工作区：用 git 底层命令在 origin/calls 上做一次提交再推上去；推不上就取最新的重放，最多四次。

⚠️ 仓库是公开的。只记「他该记得的事」，一两句话的概括，不抄原话；太私密的不记，
她说「这句别记」就不记，说「把上次的忘了」就 forget。

    python3 tools/call/calls.py ls                          # 都跟谁通过话
    python3 tools/call/calls.py show gary--interoffice      # 这个人的全部记录（brief.py 会自动带上最近几通）
    python3 tools/call/calls.py add gary--interoffice --who "Gary O'Hara · Interoffice" --mode 电话 \\
        --note "她说今天学生太吵，嗓子哑了" --note "他答应下次打来先问她嗓子"
    python3 tools/call/calls.py add gary--interoffice --update --note ……   # 还是这一通：整条换成新写的（聊得长时中途先记、挂断再更新）
    python3 tools/call/calls.py fix gary--interoffice "她说：他不会一上来就叫 sweetheart，熟了才叫名字"
    python3 tools/call/calls.py forget gary--interoffice            # 忘掉最近一通
    python3 tools/call/calls.py forget gary--interoffice --all      # 这个人的通话记录全忘（纠正过的地方保留）
    python3 tools/call/calls.py alias Gary garyguitar               # 她说「以后 Gary 就是弹吉他那个」
    python3 tools/call/calls.py alias 教练 greaves --au eyes-on-me  # 她自己的叫法，连 AU 一起定
    python3 tools/call/calls.py unalias Gary                        # 不要这个默认了，重名时再问

改动类命令都可以加 --dry-run（只打印、不推）和 --trailer "..."（给提交说明补尾行，可重复）。
"""
import argparse
import datetime as dt
import json
import subprocess
import sys
import time

BRANCH = "calls"
FILE = "calls.json"
REMOTE = "origin"
TZ = dt.timezone(dt.timedelta(hours=8))   # 一律按北京时间
README = ("☎ 打给他 · 通话记录。只由 tools/call/calls.py 改，别手改。"
          "calls 的每个键 = 角色 id（有 AU 的再接 --系列目录名）；log = 一通一条，notes 是他该记得的事；"
          "fixes = Winter 纠正过的「这不像他」，每一通都要遵守。aliases = 她定的叫法（「Gary」默认是谁、「教练」是谁）。")


def now():
    return dt.datetime.now(TZ)


def git(*args, input=None):
    r = subprocess.run(["git", *args], input=input, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("git " + " ".join(args) + " 失败：\n" + r.stderr.strip())
    return r.stdout.strip()


def fetch():
    """取 origin/calls。分支还不存在 → False（第一次记的时候会建）。"""
    last = None
    for wait in (0, 2, 4, 8):
        time.sleep(wait)
        try:
            if not git("ls-remote", "--heads", REMOTE, BRANCH):
                return False
            git("fetch", "-q", REMOTE, f"+refs/heads/{BRANCH}:refs/remotes/{REMOTE}/{BRANCH}")
            return True
        except RuntimeError as e:
            last = e
    raise last


def has_ref():
    try:
        git("rev-parse", "--verify", "-q", f"{REMOTE}/{BRANCH}")
        return True
    except RuntimeError:
        return False


def load():
    if not has_ref():
        return {"_readme": README, "calls": {}}
    return json.loads(git("show", f"{REMOTE}/{BRANCH}:{FILE}"))


def load_quiet():
    """给 brief.py 用：取不到（没网 / 还没有分支）就当没有记录，绝不让接通卡住。"""
    try:
        fetch()
    except Exception:
        pass
    try:
        return load()
    except Exception:
        return {"_readme": README, "calls": {}}


def dump(data):
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def commit_and_push(data, message, trailers):
    blob = git("hash-object", "-w", "--stdin", input=dump(data))
    ref = f"{REMOTE}/{BRANCH}"
    exists = has_ref()
    entries = [e for e in git("ls-tree", ref).splitlines() if not e.endswith("\t" + FILE)] if exists else []
    entries.append(f"100644 blob {blob}\t{FILE}")
    tree = git("mktree", input="\n".join(entries) + "\n")
    msg = message + ("\n\n" + "\n".join(trailers) if trailers else "")
    parent = ["-p", git("rev-parse", ref)] if exists else []
    commit = git("commit-tree", tree, *parent, "-m", msg)
    git("push", "-q", REMOTE, f"{commit}:refs/heads/{BRANCH}")
    return commit


def ago(iso):
    try:
        t = dt.datetime.fromisoformat(iso)
    except ValueError:
        return iso
    d = (now().date() - t.astimezone(TZ).date()).days
    h = t.astimezone(TZ).hour
    part = "深夜" if h < 5 or h >= 23 else "早上" if h < 11 else "中午" if h < 13 else "下午" if h < 18 else "晚上"
    when = "今天" if d == 0 else "昨天" if d == 1 else "前天" if d == 2 else ("%d 天前" % d if d < 14 else
           "%d 个星期前" % (d // 7) if d < 60 else "好几个月前")
    return "%s%s" % (when, part)


def render(entry, recent=None):
    """给 brief.py 和 show 用的文字。recent = 只看最近几通。"""
    out = []
    fixes = entry.get("fixes", [])
    if fixes:
        out.append("⭐ 她纠正过的（每一通都照做）：")
        out += ["- " + f["text"] for f in fixes]
        out.append("")
    log = entry.get("log", [])
    if log:
        shown = log[-recent:] if recent else log
        if recent and len(log) > recent:
            out.append("（一共 %d 通，下面是最近 %d 通；更早的：`python3 tools/call/calls.py show <编号>`）" % (len(log), recent))
        for c in reversed(shown):
            head = "- " + ago(c["at"]) + ("（%s）" % c["mode"] if c.get("mode") else "")
            out.append(head + "：" + "；".join(c.get("notes", [])))
        out.append("")
        out.append("⚠️ 他只记得「上回 / 前几天你说过」，记不住是几月几号；越早的越模糊。")
    return "\n".join(out).strip()


def main():
    ap = argparse.ArgumentParser(description="打给他 · 通话记录")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def change(name):
        s = sub.add_parser(name)
        s.add_argument("key")
        s.add_argument("--dry-run", action="store_true")
        s.add_argument("--trailer", action="append", default=[])
        return s

    sub.add_parser("ls")
    s = sub.add_parser("show")
    s.add_argument("key")
    s = change("add")
    s.add_argument("--who", default="")
    s.add_argument("--mode", default="")
    s.add_argument("--note", action="append", required=True)
    s.add_argument("--update", action="store_true", help="还是同一通（六小时内）：把这一通的记录整条换成新的")
    s = change("fix")
    s.add_argument("text")
    s = change("forget")
    s.add_argument("--all", action="store_true")
    s = change("alias")
    s.add_argument("target", help="角色编号（brief.py 重名列表里 --id 后面那个）")
    s.add_argument("--au", default="", help="连哪个 AU 一起定（系列目录名）")
    s = change("unalias")
    a = ap.parse_args()

    if a.cmd in ("ls", "show"):
        data = load_quiet()
        calls = data.get("calls", {})
        if a.cmd == "ls":
            for k, v in data.get("aliases", {}).items():
                print("叫法：「%s」→ %s%s" % (k, v["id"], (" · " + v["au"]) if v.get("au") else ""))
            if not calls:
                print("还没有任何通话记录。")
            for k, e in sorted(calls.items(), key=lambda kv: (kv[1].get("log") or [{"at": ""}])[-1]["at"], reverse=True):
                last = (e.get("log") or [{}])[-1]
                print("- %s　%s　%d 通，上一通 %s" % (k, e.get("who", ""), len(e.get("log", [])),
                                                ago(last["at"]) if last.get("at") else "—"))
            return 0
        e = calls.get(a.key)
        print(render(e) if e else "（%s 还没有通话记录）" % a.key)
        return 0

    def op(data):
        if a.cmd == "alias":
            data.setdefault("aliases", {})[a.key] = {"id": a.target, "au": a.au, "at": now().isoformat(timespec="minutes")}
            return "通话记录：以后说「%s」就是 %s" % (a.key, a.target + (" · " + a.au if a.au else ""))
        if a.cmd == "unalias":
            data.setdefault("aliases", {}).pop(a.key, None)
            return "通话记录：「%s」不再默认是谁" % a.key
        e = data["calls"].setdefault(a.key, {"who": "", "log": [], "fixes": []})
        if a.cmd == "add":
            if a.who:
                e["who"] = a.who
            entry = {"at": now().isoformat(timespec="minutes"), "mode": a.mode,
                     "notes": [n.strip() for n in a.note if n.strip()]}
            if a.update and e["log"]:
                started = dt.datetime.fromisoformat(e["log"][-1]["at"])
                if now() - started < dt.timedelta(hours=6):   # 还是这一通：整条换成新的，开始时间不变
                    entry["at"] = e["log"][-1]["at"]
                    e["log"][-1] = entry
                    return "通话记录：%s 更新这一通" % a.key
            e["log"].append(entry)
            return "通话记录：%s 记一通" % a.key
        if a.cmd == "fix":
            e.setdefault("fixes", []).append({"at": now().isoformat(timespec="minutes"), "text": a.text.strip()})
            return "通话记录：%s 记一条纠正" % a.key
        if a.cmd == "forget":
            if a.all:
                e["log"] = []
                return "通话记录：%s 全部忘掉（纠正保留）" % a.key
            if e["log"]:
                e["log"].pop()
            return "通话记录：%s 忘掉最近一通" % a.key

    fetch()
    last = None
    for attempt in range(4):
        data = load()
        data["_readme"] = README
        msg = op(data)
        if a.dry_run:
            print("（演练，不推）" + msg)
            if a.key in data["calls"]:
                print(render(data["calls"][a.key]))
            return 0
        try:
            commit_and_push(data, msg, a.trailer)
            print("✓ " + msg)
            return 0
        except RuntimeError as err:
            last = err
            time.sleep(2 ** attempt)
            fetch()
    raise SystemExit("推了四次都没推上去：\n%s" % last)


if __name__ == "__main__":
    sys.exit(main())
