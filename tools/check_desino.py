#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_desino.py —— AU 正文「中式出戏表达」扫描器
用法：python3 tools/check_desino.py _posts/某章.md [更多文件...]

三档结果：
  ❌ HIGH  几乎必错（筷子/夹菜/衙门/江湖……），部署前必须处理
  ⚠️ WARN  看语境（大人/师父/饺子/户口……），人工判断
  🗣 LANG  语言穿帮嫌疑（英文/英语/中文……），逐处回答「此刻真的在切换语言吗」
  📖 META  正文 cue 章节（上一章/第 N 章……），题词引语行（> 开头）与「下一章：」预告行不查

规则维护：出戏词清单见下方 HIGH_WORDS / WARN_WORDS，规范真源是 CLAUDE.md
「严禁中式出戏表达」一节；发现新漏网词就往清单里加一行。
exit code：有 HIGH 命中 → 1，否则 0。
"""
import re
import sys

# ---- 几乎必错（命中即改）----
HIGH_WORDS = [
    # 餐桌·饮食（最易手滑的重灾区）
    ("筷子", "刀·叉·勺"), ("夹菜", "替某人盛/递过盘子/切一块"), ("夹给", "盛给/递给"),
    ("扒饭", "大口吃"), ("端起碗", "端起盘子/杯子"), ("布菜", "上菜/分餐"),
    # 器物·居家·衣着·身势
    ("灶台", "炉灶/灶头(stove)"), ("土炕", "床/壁炉边"), ("火炕", "床/壁炉边"),
    ("蒲扇", "扇子/纸扇"), ("长衫", "衬衫外套/大衣"), ("马褂", "外套/马甲"),
    ("抱拳", "握手/点头致意"), ("作揖", "握手/欠身"), ("磕头", "跪下/鞠躬"), ("叩首", "跪拜/鞠躬"),
    # 官府·武侠·江湖
    ("衙门", "警局/法院/当局"), ("官府", "当局/政府"), ("报官", "报警/报案"),
    ("捕快", "警察/警长的人"), ("县令", "镇长/法官"), ("官兵", "士兵/警队"), ("兵勇", "士兵"),
    ("江湖", "外头/在路上/干这行的"), ("镖局", "（无对应，重写）"), ("大侠", "（无对应，重写）"),
    ("武功", "身手"), ("内力", "（无对应，重写）"), ("轻功", "身手"),
    # 称谓
    ("相公", "先生/丈夫"), ("娘子", "太太/妻子"), ("姨娘", "（按该文化重写）"), ("丫鬟", "女仆/侍女"),
    # 钱物·度量·计时
    ("盘缠", "路上的钱"), ("细软", "值钱的家当"), ("银两", "钱/美元"), ("纹银", "钱"), ("铜板", "硬币/零钱"),
    ("时辰", "点钟/小时"), ("一炷香", "几分钟/一刻钟"), ("半炷香", "几分钟"),
    # 宗教·命理
    ("阿弥陀佛", "上帝啊/天哪"), ("菩萨", "上帝/上天"), ("黄泉", "地狱/九泉→重写"),
    ("阴曹", "地狱"), ("阎王", "死神/地狱"), ("月老", "丘比特/命运"), ("生辰八字", "（无对应，删）"),
    ("缘分天定", "命中注定"), ("冲喜", "（无对应，删）"),
    # 说书腔
    ("话说，", "（删）"), ("且说", "（删）"), ("看官", "（删）"), ("列位看官", "（删）"),
]

# ---- 看语境（人工判断）----
WARN_WORDS = [
    ("大人", "若是官场称谓(X大人)→先生/阁下；若是「成年人」义→通常没问题"),
    ("老爷", "先生/主人(sir)；旧宅仆役语境或可保留西式对应"),
    ("小姐", "女士/小姐(Miss)——西式 Miss 义可留，青楼义必改"),
    ("师父", "老师/师傅(mentor/coach)——武侠义必改"),
    ("哥哥", "英语背景兄弟直呼其名居多；「哥」作亲昵称呼酌情"),
    ("姐姐", "同上——英语没有「叫姐姐」的敬称用法"),
    ("饺子", "现代世界观可作为普通食物保留；历史向 AU 建议换本地食物"),
    ("户口", "出生登记/户籍记录(registry)——中国专有制度词，酌情"),
    ("鞭炮", "礼炮/烟花——鞭炮偏中式年俗"),
    ("红包", "礼金/信封装的现金"), ("压岁钱", "节日零花钱"),
    ("坐月子", "产后休养"), ("风水", "运势/格局——玄学义必改"),
    ("转世", "重生/来世——佛教义酌情"), ("投胎", "重生——同上"),
    ("尊老", "长者优先/尊重长辈(respect your elders)"),
    ("兴师动众", "张扬开来/大动干戈"), ("发号施令", "拿主意/发话"),
]

# 度量单位（带数字/汉字数量词才算命中，降低误报）
UNIT_PATTERNS = [
    (r"[0-9一二两三四五六七八九十百千]+\s*里[地路]?(?![面头边程])", "英里/公里"),
    (r"[0-9一二两三四五六七八九十百千]+\s*[斤两](?![只个人样件])", "磅/盎司"),
    (r"[0-9一二两三四五六七八九十]+\s*丈", "英尺/米"),
    (r"[一二三四五]更[天时]?", "后半夜/凌晨 X 点"),
]

# 语言穿帮嫌疑
LANG_PATTERN = re.compile(r"英文|英语|中文|汉语|普通话")

# 正文 cue 章节（元指涉）
META_PATTERN = re.compile(r"上一章|这一章|前文所述|第[一二三四五六七八九十百0-9]+章")


# 已知误报豁免：词 → 命中行若同时含这些子串则跳过
FALSE_POSITIVE = {
    "娘子": ["新娘子", "新娘"],
    "老爷": ["老爷车", "老爷子"],
    "小姐": ["小姐姐"],
}


def _false_positive(word: str, line: str) -> bool:
    for ctx in FALSE_POSITIVE.get(word, []):
        if ctx in line:
            return True
    return False


def split_body(text: str) -> list:
    """去掉 front matter，返回 (行号, 行内容) 列表。"""
    lines = text.splitlines()
    body_start = 0
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                body_start = i + 1
                break
    return [(i + 1, lines[i]) for i in range(body_start, len(lines))]


def check_file(path: str) -> int:
    try:
        text = open(path, encoding="utf-8").read()
    except OSError as e:
        print(f"  读不到文件：{e}")
        return 0

    body = split_body(text)
    high, warn, lang, meta = [], [], [], []

    for lineno, line in body:
        for word, fix in HIGH_WORDS:
            if word in line and not _false_positive(word, line):
                high.append((lineno, word, fix, line.strip()))
        for word, fix in WARN_WORDS:
            if word in line:
                warn.append((lineno, word, fix, line.strip()))
        for pat, fix in UNIT_PATTERNS:
            if re.search(pat, line):
                high.append((lineno, "中式度量", fix, line.strip()))
        if LANG_PATTERN.search(line):
            lang.append((lineno, line.strip()))
        # 题词/引语行与「下一章」预告行属于面向读者的导航文本，不算正文元指涉
        stripped = line.lstrip()
        if not stripped.startswith(">") and not stripped.startswith("下一章"):
            if META_PATTERN.search(line):
                meta.append((lineno, line.strip()))

    print(f"\n检查：{path}")
    print("─" * 56)
    if not (high or warn or lang or meta):
        print("  ✅ 全部干净")
        return 0

    def show(items, icon, label):
        if not items:
            return
        print(f"  {icon} {label}（{len(items)} 处）")
        for it in items:
            if len(it) == 4:
                lineno, word, fix, ctx = it
                print(f"     L{lineno} 「{word}」→ 建议：{fix}")
            else:
                lineno, ctx = it
                print(f"     L{lineno}")
            print(f"        {ctx[:60]}")

    show(high, "❌", "HIGH · 几乎必错")
    show(warn, "⚠️", "WARN · 看语境")
    show(lang, "🗣", "LANG · 语言穿帮嫌疑（此刻真的在切换语言吗？）")
    show(meta, "📖", "META · 正文 cue 章节")
    return 1 if high else 0


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    bad = 0
    for path in sys.argv[1:]:
        bad |= check_file(path)
    sys.exit(bad)


if __name__ == "__main__":
    main()
