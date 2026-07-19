#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WinterSunBlog 文章 front matter 校验脚本
========================================

用法：
    python3 check_post.py 路径/到/文章.md

作用：
    对一篇 A 类文章（_posts/ 下的 .md）做发布前检查，逐项打印 ✅ / ⚠️ / ❌。
    有 ❌（硬错误）时退出码为 1，方便判断「能不能交付」。⚠️ 是提醒，不阻断。

────────────────────────────────────────────────────────────────────────
博客规范变了就改下面这块「可调项」（其余逻辑一般不用动）：
"""

# tags 新格式：[角色名, 演员名, "AU", 系列英文名, mood1, mood2]（前 4 身份 + 1–2 mood）
# ALLOWED_TAGS = 9 个 mood 白名单（应与博客 _data/moods.yml 的 cn 值保持一致）
ALLOWED_TAGS = ["炽恋", "悸动", "缱绻", "思念", "安放", "怅惘", "暗涌", "怀旧", "絮语"]
MOOD_MIN, MOOD_MAX = 1, 2          # 末尾 mood 的数量范围

# summary 字符数硬上限（含标点，按 len() 计）
SUMMARY_MAX = 35

# series_status 合法取值
VALID_STATUS = ["ongoing", "complete"]

# categories 必须等于
REQUIRED_CATEGORIES = ["AU Story"]

# 必填字段
REQUIRED_FIELDS = [
    "layout", "title", "date", "image", "tags", "categories",
    "series", "series_title", "series_order", "series_status",
    "series_type", "chapter_type", "summary",
]
# ────────────────────────────────────────────────────────────────────────

import sys
import os
import re
import datetime

GREEN, RED, YELLOW, RESET = "\033[92m", "\033[91m", "\033[93m", "\033[0m"

errors = 0   # ❌ 计数
warns = 0    # ⚠️ 计数


def ok(msg):
    print(f"{GREEN}✅{RESET} {msg}")


def bad(msg):
    global errors
    errors += 1
    print(f"{RED}❌{RESET} {msg}")


def warn(msg):
    global warns
    warns += 1
    print(f"{YELLOW}⚠️{RESET}  {msg}")


def split_front_matter(text):
    """从文件文本里分出 front matter 原文。返回 (fm_text, ok_bool)。"""
    # 允许文件开头有 BOM / 空白行
    stripped = text.lstrip("\ufeff")
    if not stripped.startswith("---"):
        return None, False
    # 匹配第一对 --- ... ---
    m = re.match(r"^---\s*\n(.*?)\n---\s*(\n|$)", stripped, re.DOTALL)
    if not m:
        return None, False
    return m.group(1), True


def parse_yaml(fm_text):
    """优先用 pyyaml；没装就用内置的简易解析器（够应付扁平 front matter）。"""
    try:
        import yaml
        return yaml.safe_load(fm_text)
    except ImportError:
        warn("未安装 pyyaml，改用内置简易解析器（建议 pip install pyyaml --break-system-packages 获得更准确的解析）")
        return _simple_parse(fm_text)


def _simple_parse(fm_text):
    data = {}
    for line in fm_text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        # 去掉行内注释（# 前需有空白，避免误伤 #2 这类）
        val = re.sub(r"\s+#.*$", "", val).strip()
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            items = [x.strip().strip('"').strip("'") for x in inner.split(",")] if inner else []
            data[key] = [x for x in items if x != ""]
        elif (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            data[key] = val[1:-1]
        elif re.fullmatch(r"-?\d+", val):
            data[key] = int(val)
        else:
            data[key] = val
    return data


def to_date_str(v):
    """把 date 值统一成 'YYYY-MM-DD' 字符串。pyyaml 会把它解析成 date 对象。"""
    if isinstance(v, (datetime.date, datetime.datetime)):
        return v.strftime("%Y-%m-%d")
    return str(v).strip()


def check_tags(tags, series_name):
    """校验章节 tags 新格式：[角色名, 演员名, "AU", 系列英文名, mood1, mood2]
    （前 4 身份 + 末尾 1–2 个 mood）。返回错误信息列表（空 = 通过）。
    规则与线上部署侧 check_tags.py 完全一致。"""
    errs = []
    if not isinstance(tags, list):
        return ["必须是列表"]

    n = len(tags)
    lo, hi = 4 + MOOD_MIN, 4 + MOOD_MAX
    if not (lo <= n <= hi):
        errs.append(f"应为 {lo}-{hi} 个（前 4 身份 + 末尾 {MOOD_MIN}-{MOOD_MAX} mood），实际 {n} 个")

    identity, moods = tags[:4], tags[4:]

    for i, label in ((0, "角色名"), (1, "演员名")):
        if i >= len(identity) or not str(identity[i]).strip():
            errs.append(f"第 {i + 1} 位（{label}）缺失或为空")

    if len(identity) < 3 or identity[2] != "AU":
        got = identity[2] if len(identity) > 2 else "（缺）"
        errs.append(f'第 3 位应为字面量 "AU"，实际 "{got}"')

    if len(identity) < 4:
        errs.append("第 4 位（系列英文名）缺失")
    elif series_name and identity[3] != series_name:
        errs.append(f'第 4 位应 = series（"{series_name}"），实际 "{identity[3]}"')

    if not (MOOD_MIN <= len(moods) <= MOOD_MAX):
        errs.append(f"末尾 mood 应为 {MOOD_MIN}-{MOOD_MAX} 个，实际 {len(moods)} 个")
    for m in moods:
        if m not in ALLOWED_TAGS:
            errs.append(f'非法 mood "{m}"（须来自 {len(ALLOWED_TAGS)} 个白名单）')

    return errs


def check(path):
    if not os.path.isfile(path):
        bad(f"文件不存在：{path}")
        return

    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    print(f"\n检查文件：{path}\n" + "─" * 56)

    # 1) 分离 front matter
    fm_text, found = split_front_matter(text)
    if not found:
        bad("没找到 front matter（文件最开头要有一对 --- 包起来的部分）")
        return
    ok("找到 front matter")

    # 2) 解析
    try:
        data = parse_yaml(fm_text)
    except Exception as e:
        bad(f"front matter 解析失败：{e}")
        return
    if not isinstance(data, dict):
        bad("front matter 解析结果不是键值对，检查缩进 / 格式")
        return
    ok("front matter 解析成功")

    # 3) 必填字段
    missing = [k for k in REQUIRED_FIELDS if k not in data or data.get(k) in (None, "", [])]
    if missing:
        bad(f"缺少 / 为空的必填字段：{', '.join(missing)}")
    else:
        ok("必填字段齐全")

    # 4) layout
    if data.get("layout") and data.get("layout") != "post":
        warn(f"layout 通常是 post，当前为「{data.get('layout')}」")

    # 5) summary 字数
    summary = data.get("summary")
    if isinstance(summary, str):
        n = len(summary)
        if n <= SUMMARY_MAX:
            ok(f"summary 长度 {n} 字（≤ {SUMMARY_MAX}）")
        else:
            bad(f"summary 长度 {n} 字，超过上限 {SUMMARY_MAX}（首页卡片会被截成半句，需缩写）")
    elif "summary" in REQUIRED_FIELDS:
        # 缺失已在必填检查里报过
        pass

    # 6) tags（新格式：前 4 身份 + 1–2 mood）
    tags = data.get("tags")
    if tags is not None:
        tag_errs = check_tags(tags, data.get("series", ""))
        if tag_errs:
            for e in tag_errs:
                bad(f"tags：{e}")
        else:
            ok(f"tags 合法：{tags}")

    # 7) series 纯 ASCII
    series = data.get("series")
    if isinstance(series, str) and series:
        if series.isascii():
            ok(f"series 为纯英文：\"{series}\"")
        else:
            non_ascii = [ch for ch in series if not ch.isascii()]
            bad(f"series 含非 ASCII 字符 {non_ascii}：「{series}」——会导致系列链接断裂，必须改成纯英文")

    # 8) series_order 整数
    so = data.get("series_order")
    if so is not None:
        if isinstance(so, bool) or not isinstance(so, int):
            bad(f"series_order 必须是整数，当前为：{so!r}")
        elif so < 1:
            bad(f"series_order 应从 1 开始，当前为 {so}")
        else:
            ok(f"series_order = {so}（续写时记得 = 上一章 + 1，以线上为准）")

    # 9) series_status
    st = data.get("series_status")
    if st is not None and st not in VALID_STATUS:
        bad(f"series_status 应为 {VALID_STATUS} 之一，当前为「{st}」")
    elif st in VALID_STATUS:
        ok(f"series_status = {st}")

    # 10) categories
    cats = data.get("categories")
    if cats is not None and cats != REQUIRED_CATEGORIES:
        warn(f"categories 通常应为 {REQUIRED_CATEGORIES}，当前为：{cats}")
    elif cats == REQUIRED_CATEGORIES:
        ok(f"categories = {cats}")

    # 11) date 格式 + 与文件名一致
    raw_date = data.get("date")
    if raw_date is not None:
        ds = to_date_str(raw_date)
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", ds):
            ok(f"date 格式正确：{ds}")
        else:
            bad(f"date 应为 YYYY-MM-DD，当前为「{ds}」")

        # 从文件名提取日期比对
        base = os.path.basename(path)
        m = re.match(r"(\d{4}-\d{2}-\d{2})-", base)
        if m:
            if m.group(1) == ds:
                ok("文件名日期与 date 字段一致")
            else:
                warn(f"文件名日期（{m.group(1)}）与 date 字段（{ds}）不一致")
        else:
            warn(f"文件名建议以日期开头：YYYY-MM-DD-series-slug-chapter-N-title.md（当前：{base}）")

    # 收尾
    print("─" * 56)
    if errors == 0 and warns == 0:
        print(f"{GREEN}全部通过 ✅ 可以交付。{RESET}\n")
    elif errors == 0:
        print(f"{GREEN}无硬错误，可交付{RESET}；另有 {warns} 条提醒（⚠️），自行斟酌。\n")
    else:
        print(f"{RED}有 {errors} 处硬错误（❌）需先修正{RESET}，另有 {warns} 条提醒（⚠️）。\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法：python3 check_post.py 路径/到/文章.md")
        sys.exit(2)
    check(sys.argv[1])
    sys.exit(1 if errors else 0)
