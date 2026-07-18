#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WinterSunBlog 系列首页（series/<slug>/index.html）内容自检
=========================================================

用法：
    python3 check_series_page.py 路径/到/index.html

作用：
    对一份系列首页做发布前内容检查，逐项打印 ✅ / ⚠️ / ❌。
    系列首页大多是「建议范围」，所以多为 ⚠️ 提醒；只有会断链的硬规则记 ❌。
    有 ❌ 时退出码 1。

────────────────────────────────────────────────────────────────────────
规范变了就改这块「可调项」：
"""

LEDE_MIN, LEDE_MAX = 10, 25          # Hero 灵魂句字数
ABOUT_MIN, ABOUT_MAX = 200, 350      # 「关于这个系列」区块总字数
PROFILE_ITEM_MIN, PROFILE_ITEM_MAX = 50, 100   # 「设定档案」每个条目字数
PALETTE_INCLUDE = "au-palette-strip.html"       # Hero 必须原样包含的 include
# ────────────────────────────────────────────────────────────────────────

import sys, os, re

GREEN, RED, YELLOW, RESET = "\033[92m", "\033[91m", "\033[93m", "\033[0m"
errors = 0
warns = 0


def ok(m):
    print(f"{GREEN}✅{RESET} {m}")


def bad(m):
    global errors
    errors += 1
    print(f"{RED}❌{RESET} {m}")


def warn(m):
    global warns
    warns += 1
    print(f"{YELLOW}⚠️{RESET}  {m}")


def text_only(html):
    """提取纯文本字数用：去标签、去实体、去 Liquid、去空白（含全角空格）。"""
    s = re.sub(r"<[^>]+>", "", html)
    s = re.sub(r"&[a-zA-Z]+;", "", s)
    s = re.sub(r"&#\d+;", "", s)
    s = re.sub(r"\{%.*?%\}", "", s, flags=re.DOTALL)
    s = re.sub(r"\{\{.*?\}\}", "", s, flags=re.DOTALL)
    s = re.sub(r"\s+", "", s)            # \s 在 Python3 str 下含 U+3000 全角空格
    return s


def check(path):
    if not os.path.isfile(path):
        bad(f"文件不存在：{path}")
        return
    html = open(path, "r", encoding="utf-8").read()
    print(f"\n检查文件：{path}\n" + "─" * 56)

    # 1) Hero 标题必须英文（ASCII）—— 硬规则
    m = re.search(r'<h1[^>]*class="[^"]*c-hero__title[^"]*"[^>]*>(.*?)</h1>', html, re.DOTALL)
    if not m:
        warn("没找到 <h1 class=\"c-hero__title\">，确认 Hero 区块存在")
    else:
        title = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        if not title:
            warn("Hero 标题为空")
        elif title.isascii():
            ok(f'Hero 标题为英文："{title}"')
        else:
            non = [c for c in title if not c.isascii()]
            bad(f"Hero 标题含非 ASCII 字符 {non}：「{title}」——必须英文，否则系列链接断裂")

    # 2) au-palette-strip include 必须原样存在
    if re.search(r"\{%\s*include\s+" + re.escape(PALETTE_INCLUDE) + r"\s*%\}", html):
        ok("包含 {% include au-palette-strip.html %}")
    else:
        warn(f"未找到 {{% include {PALETTE_INCLUDE} %}}（这行应原样复制）")

    # 3) Hero 灵魂句字数
    m = re.search(r'<p[^>]*class="[^"]*c-hero__lede[^"]*"[^>]*>(.*?)</p>', html, re.DOTALL)
    if m:
        # 去掉引号 span（c-hero__quote）后再数
        body = re.sub(r'<span[^>]*c-hero__quote[^>]*>.*?</span>', "", m.group(1), flags=re.DOTALL)
        n = len(text_only(body))
        if LEDE_MIN <= n <= LEDE_MAX:
            ok(f"Hero 灵魂句 {n} 字（{LEDE_MIN}-{LEDE_MAX}）")
        else:
            warn(f"Hero 灵魂句 {n} 字，建议 {LEDE_MIN}-{LEDE_MAX} 字")
    else:
        warn("没找到 <p class=\"c-hero__lede\">")

    # 4) 遍历 c-sam-intro 区块
    blocks = re.findall(r'<article[^>]*class="[^"]*c-sam-intro[^"]*"[^>]*>(.*?)</article>', html, re.DOTALL)
    if not blocks:
        warn("没找到 <article class=\"c-sam-intro\"> 区块（设定总览应至少有一个）")
    else:
        ok(f"找到 {len(blocks)} 个 c-sam-intro 区块")

    found_about = False
    for blk in blocks:
        hm = re.search(r"<h2[^>]*>(.*?)</h2>", blk, re.DOTALL)
        heading = re.sub(r"<[^>]+>", "", hm.group(1)).strip() if hm else "(无标题)"
        is_profile = "档案" in heading

        # 4a) 每个区块都要有 closing
        if "c-sam-intro__closing" not in blk:
            warn(f"区块「{heading}」缺少 <p class=\"c-sam-intro__closing\"> 收尾")
        else:
            ok(f"区块「{heading}」有 closing 收尾")

        if not is_profile:
            # 4b)「关于这个系列」类区块：总字数 + 段数
            found_about = True
            body = re.sub(r"<h2[^>]*>.*?</h2>", "", blk, flags=re.DOTALL)
            n = len(text_only(body))
            paras = re.findall(r"<p[^>]*>(.*?)</p>", blk, re.DOTALL)
            np = len(paras)
            if ABOUT_MIN <= n <= ABOUT_MAX:
                ok(f"区块「{heading}」总字数 {n}（{ABOUT_MIN}-{ABOUT_MAX}），{np} 段")
            else:
                warn(f"区块「{heading}」总字数 {n}，建议 {ABOUT_MIN}-{ABOUT_MAX} 字；当前 {np} 段（建议 2-4 段）")
        else:
            # 4c)「设定档案」：条目全角符号 + 条目字数 + 你/角色两条
            items = re.findall(r"<p[^>]*>(.*?)</p>", blk, re.DOTALL)
            items = [it for it in items if "c-sam-intro__closing" not in it and "<strong>" in it]
            if len(items) < 2:
                warn(f"设定档案条目偏少（{len(items)} 条）：「你」和「AU 角色」两条必须有")
            for it in items:
                label = re.sub(r"<[^>]+>", "", re.search(r"<strong>(.*?)</strong>", it, re.DOTALL).group(1)).strip() if "<strong>" in it else "(条目)"
                # 全角竖线
                if "｜" not in label and "|" in label:
                    warn(f"档案条目「{label}」用了半角竖线 | ，应改全角「｜」")
                # </strong> 后应紧跟全角空格 U+3000
                after = re.search(r"</strong>(.)", it)
                if after and after.group(1) != "\u3000":
                    warn(f"档案条目「{label}」的 </strong> 后应是全角空格「　」，当前为 {after.group(1)!r}")
                # 条目字数
                n = len(text_only(it))
                if not (PROFILE_ITEM_MIN <= n <= PROFILE_ITEM_MAX):
                    warn(f"档案条目「{label}」约 {n} 字，建议 {PROFILE_ITEM_MIN}-{PROFILE_ITEM_MAX} 字")

    if found_about is False and blocks:
        warn("未识别到「关于这个系列」类区块（第一区块必须有）")

    # 收尾
    print("─" * 56)
    if errors == 0 and warns == 0:
        print(f"{GREEN}全部通过 ✅{RESET}\n")
    elif errors == 0:
        print(f"{GREEN}无硬错误{RESET}；{warns} 条提醒（⚠️）自行斟酌——多为字数建议范围。\n")
    else:
        print(f"{RED}有 {errors} 处硬错误（❌）需先修正{RESET}，另有 {warns} 条提醒（⚠️）。\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法：python3 check_series_page.py 路径/到/index.html")
        sys.exit(2)
    check(sys.argv[1])
    sys.exit(1 if errors else 0)
