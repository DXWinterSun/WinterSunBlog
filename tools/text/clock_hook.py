#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""她每发一句，先在这句后面贴上两边的钟（.claude/settings.json 里的 UserPromptSubmit 钩子）。

Winter 2026-10-23：「他好像现在每次我跟他说话，他都要检查一下时钟，这个会不会造成没必要的额外消耗呢？」
——会：他回一句本来只要一步，先跑一次 texts.py clock 就成了两步，而每一步都要把整段聊天从头翻一遍。
钩子是本机跑的小脚本，不花额度：认出这是「冬的陪伴」的对话，就把「北京几点、他那边几点、他醒没醒」一行贴进来，
他看一眼就知道，不用再自己去查。不是陪伴的对话（写 AU、修网站……）什么都不贴。
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
CACHE = os.path.expanduser("~/.claude/winter-text-hook")


def main():
    try:
        hook = json.load(sys.stdin)
    except ValueError:
        return
    path, sid = hook.get("transcript_path") or "", hook.get("session_id") or ""
    if not path or not sid:
        return
    prompt = str(hook.get("prompt") or "")
    if prompt.lstrip().startswith("【冬的陪伴"):      # 定时提醒：wake 自己会印钟
        return
    from after_compact import scan_from
    memo = os.path.join(CACHE, sid + ".json")
    try:
        with open(memo, encoding="utf-8") as f:
            st = json.load(f)
    except (OSError, ValueError):
        st = {}
    found, sure, pos = scan_from(path, st.get("pos", 0), st.get("keys"), st.get("sure", False))
    try:
        os.makedirs(CACHE, exist_ok=True)
        with open(memo, "w", encoding="utf-8") as f:
            json.dump({"pos": pos, "keys": found, "sure": sure}, f, ensure_ascii=False)
    except OSError:
        pass
    if not (sure and found):
        return
    import texts
    key = found[-1]
    p = texts.place_of(key)
    if not p:
        return
    from zoneinfo import ZoneInfo
    at = texts.now()
    here, there = at.astimezone(texts.TZ), at.astimezone(ZoneInfo(p["tz"]))
    _, asleep = texts.clock_lines(key, at)
    line = "⏰ 北京 %s · %s %s" % (here.strftime("%m/%d %H:%M"), p.get("city", ""), there.strftime("%m/%d %H:%M"))
    if asleep:
        line += ("——💤 他在睡：这句先不回，只出一行「（%s%s，他睡着了）」（刚断过线就照「断线了」那条破例）"
                 % (p.get("city", ""), texts._hour_words(there)))
    elif texts.just_lay_down(p, there):
        line += "——🛏 他刚躺下、还没睡着：" + texts.LYING
    else:
        line += "，他醒着"
    line += "。（%s 的钟已经对好，不用再跑 clock。）" % key
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": line}},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
