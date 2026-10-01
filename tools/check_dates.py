#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文章日期校验 —— 部署前跑一次，拦住「乱标日期」这个痼疾。

    python3 tools/check_dates.py                 # 扫全部 _posts
    python3 tools/check_dates.py _posts/xxx.md   # 只查这几篇

规矩（2026-09-18 Winter 定，全站通用）：
  · `date:` = 这一章「真正上线」的那天（就是你推上 main 的那天），不预排未来日期，
    也不为了「看起来一天一更」往前倒着填。一天发三章就是三章同一天，这才是真实的时间轴。
  · 文件名开头的日期必须和 `date:` 同一天。
  · 改一篇旧文的日期时，把旧网址写进 `redirect_from:`（旧链接照样能打开）。

检查项：
  ❌ date 在今天之后（未来日期）
  ❌ 文件名日期 ≠ date
  ⚠️ date 只有年月日、没有时间（同一天多章时顺序会乱；建议 `YYYY-MM-DD HH:MM:SS +0800`）
有 ❌ 时退出码为 1。
"""
import sys, os, re, glob, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TZ = datetime.timezone(datetime.timedelta(hours=8))
today = datetime.datetime.now(TZ).strftime('%Y-%m-%d')

files = sys.argv[1:] or sorted(glob.glob(os.path.join(ROOT, '_posts', '*.md')))
errors = warns = 0
for f in files:
    text = open(f, encoding='utf-8').read()
    m = re.match(r'^﻿?---\s*\n(.*?)\n---\s*(\n|$)', text, re.S)
    if not m:
        continue
    fm = m.group(1)
    if re.search(r'^published:\s*false', fm, re.M):
        continue
    name = os.path.basename(f)
    fname_date = name[:10]
    dm = re.search(r'^date:\s*"?(\d{4}-\d{2}-\d{2})(.*)$', fm, re.M)
    if not dm:
        print(f'❌ {name}: 没有 date 字段'); errors += 1; continue
    day, rest = dm.group(1), dm.group(2).strip().strip('"')
    if day > today:
        print(f'❌ {name}: date 在未来（{day}，今天 {today}）—— 写真正上线的那天'); errors += 1
    if day != fname_date:
        print(f'❌ {name}: 文件名日期 {fname_date} ≠ date {day}'); errors += 1
    if not rest:
        print(f'⚠️  {name}: date 没带时间，同一天多章时顺序会乱'); warns += 1

print(f'检查 {len(files)} 篇：{errors} 个错误，{warns} 个提醒')
sys.exit(1 if errors else 0)
