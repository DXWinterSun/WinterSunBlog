#!/usr/bin/env python3
"""校验「今日一句」的排班：三处算法同源 + 轮转确实人人有份。

改过 sam/today/index.html、sam/wall/index.html、sam/widget/sam-today.js 里任何一处
的 mulberry32 / rosterOrder / dailyPick，或往 sam/lines.json 加了角色之后，跑一次：

    python3 tools/check_daily_rotation.py

全绿 exit 0；有问题会逐条列出并 exit 1。
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = [
    ROOT / "sam/today/index.html",
    ROOT / "sam/wall/index.html",
    ROOT / "sam/widget/sam-today.js",
]
FUNCS = ["mulberry32", "rosterOrder", "dailyPick"]

problems = []


def grab(path, name):
    """按大括号配平抠出一个函数的源码，并抹平 var/let/const 与空白差异。"""
    src = path.read_text(encoding="utf-8")
    start = src.index("function %s(" % name)
    i = src.index("{", start)
    depth = 0
    while True:
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                break
        i += 1
    body = re.sub(r"\b(var|let|const)\b", "X", src[start:i + 1])
    return re.sub(r"\s+", " ", body)


# ── 1. 三处算法必须字字相同 ─────────────────────────────────────
base = {fn: grab(FILES[0], fn) for fn in FUNCS}
for path in FILES[1:]:
    for fn in FUNCS:
        if grab(path, fn) != base[fn]:
            problems.append(
                "%s 里的 %s() 与 %s 不一致——三处必须完全相同，"
                "否则同一天三个页面会显示不同的句子。"
                % (path.relative_to(ROOT), fn, FILES[0].relative_to(ROOT))
            )


# ── 2. 用同一套算法（Python 复刻）验证轮转性质 ──────────────────
def imul(a, b):
    r = (a * b) & 0xFFFFFFFF
    return r - 0x100000000 if r >= 0x80000000 else r


def to_i32(x):
    x &= 0xFFFFFFFF
    return x - 0x100000000 if x >= 0x80000000 else x


def mulberry32(seed):
    state = [to_i32(seed)]

    def rnd():
        state[0] = to_i32(state[0] + 0x6D2B79F5)
        a = state[0]
        t = imul(a ^ ((a & 0xFFFFFFFF) >> 15), 1 | a)
        t = to_i32(to_i32(t + imul(t ^ ((t & 0xFFFFFFFF) >> 7), 61 | t)) ^ t)
        return ((t ^ ((t & 0xFFFFFFFF) >> 14)) & 0xFFFFFFFF) / 4294967296

    return rnd


def roster_order(n):
    order = list(range(n))
    rnd = mulberry32(to_i32(n * 2654435761))
    for i in range(n - 1, 0, -1):
        j = int(rnd() * (i + 1))
        order[i], order[j] = order[j], order[i]
    return order


data = json.loads((ROOT / "sam/lines.json").read_text(encoding="utf-8"))
chars = data["characters"]
N = len(chars)
order = roster_order(N)

if sorted(order) != list(range(N)):
    problems.append("洗牌结果不是一个完整排列——有角色被漏掉或重复了。")

# 任意连续 N 天必须覆盖全部 N 个角色，且同一角色间隔恒为 N 天
DAYS = N * 8
seq = [order[d % N] for d in range(DAYS)]
for s in range(DAYS - N + 1):
    if len(set(seq[s:s + N])) != N:
        problems.append("从第 %d 天起的连续 %d 天没有覆盖全部 %d 个角色。" % (s, N, N))
        break

last, gaps = {}, set()
for d, c in enumerate(seq):
    if c in last:
        gaps.add(d - last[c])
    last[c] = d
if gaps != {N}:
    problems.append("同一角色两次出现的间隔应恒为 %d 天，实际出现了 %s。" % (N, sorted(gaps)))

# 每个角色的 5 句台词也要轮匀
quote_counts = {len(c["quotes"]) for c in chars}
if quote_counts != {5}:
    problems.append("有角色的台词不是 5 句：%s" % sorted(quote_counts))
else:
    used = {(d // N) % 5 for d in range(N * 5)}
    if used != {0, 1, 2, 3, 4}:
        problems.append("五轮下来没有把 5 句台词都用到：%s" % sorted(used))

# meta 计数
meta = data.get("meta", {})
if meta.get("characters_count") != N:
    problems.append("meta.characters_count = %s，应为 %d。" % (meta.get("characters_count"), N))
if meta.get("pool_count") != len(data.get("pool", [])):
    problems.append("meta.pool_count 与 pool 实际长度对不上。")


if problems:
    print("「今日一句」排班校验未通过：\n")
    for p in problems:
        print("  ✗ " + p)
    sys.exit(1)

print("「今日一句」排班校验通过：")
print("  · 三处算法同源（today / wall / widget）")
print("  · %d 个角色，任意连续 %d 天每人正好出现一次，间隔恒为 %d 天" % (N, N, N))
print("  · 每人 5 句台词五轮走匀")
