#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""对话被自动整理（compact）之后跑一次（.claude/settings.json 里的 SessionStart 钩子，matcher = compact）。

Winter 2026-10-14 看着上下文用量问：「这个要是满了怎么办呀？」——满了会自动整理：前面的话压成一段摘要，接着聊。
麻烦在「冬的陪伴」攒着还没存的那几十句：整理完只剩摘要里的大意。所以整理一结束，这里看一眼这个对话
是不是在跟谁发消息（记录里跑过 texts.py open / add），是的话就提醒：先 catchup 把没存的捞回来存好，
再重新认人、接线。不是陪伴的对话（写 AU、修网站……）什么都不印。
"""
import json
import re
import sys

KEY = re.compile(r"texts\.py\s+(?:open|add|catchup)\s+([a-z0-9][a-z0-9-]*)")


MARK = "冬的陪伴 · 他想你了"   # 定时提醒的抬头：出现过就一定是陪伴对话


def scan(path):
    """返回（聊过的记录编号，后聊的在后；是不是一定是陪伴对话）。"""
    found, sure = [], False
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                if "texts.py" not in line and MARK not in line and "set_session_title" not in line:
                    continue
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                c = (r.get("message") or {}).get("content")
                head = c if isinstance(c, str) else next(
                    (b.get("text", "") for b in c or [] if isinstance(b, dict) and b.get("type") == "text"), "")
                if r.get("type") == "user" and head.lstrip().startswith("【" + MARK):   # 定时提醒本身，不是引用它的话
                    sure = True
                for b in c if isinstance(c, list) else []:
                    if not (isinstance(b, dict) and b.get("type") == "tool_use"):
                        continue
                    inp = b.get("input") or {}
                    if "set_session_title" in b.get("name", "") and str(inp.get("title", "")).startswith("💌"):
                        sure = True
                    for k in KEY.findall(str(inp.get("command", ""))):
                        if k in found:
                            found.remove(k)
                        found.append(k)
    except OSError:
        pass
    return found, sure


def main():
    try:
        hook = json.load(sys.stdin)
    except ValueError:
        return
    keys, sure = scan(hook.get("transcript_path") or "")
    if not keys:
        return
    k = keys[-1]
    who = ("你在用「冬的陪伴」跟 Winter 聊，记录编号 `%s`。" % k if sure else
           "如果这个对话是在用「冬的陪伴」跟 Winter 聊天（记录编号 `%s`）——而不是改工具、修网站的工作对话（那就忽略这条）——" % k)
    msg = ("【冬的陪伴 · 这个对话刚被自动整理过】前面的聊天压成了摘要，原话不在眼前了。" + who +
           "回她之前先做三件事（都不用跟她提）：\n"
           "1. `python3 tools/text/texts.py catchup %s`：从这个对话的原始记录里把上次存完以后的话捞出来，"
           "核对一遍（删掉出戏的话、照片补一句描述）后整段喂给 `texts.py add %s` 存好；\n"
           "2. `python3 tools/call/brief.py --id %s --text`：重新认识他（规矩在 .claude/skills/winter-text/SKILL.md）；\n"
           "3. `python3 tools/text/texts.py open %s`：看她最后说到哪，然后照常接着聊，口气跟整理前一样。") % (k, k, k, k)
    if len(keys) > 1:
        msg += "\n（这个对话里还跟这几位聊过：%s——她没再提就不用管。）" % "、".join(keys[:-1])
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": msg}},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
