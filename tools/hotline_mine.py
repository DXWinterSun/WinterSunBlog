#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深夜热线 · 从各 AU 正文里「筛」他说过的话 → sam/hotline-mined.json

用法：python3 tools/hotline_mine.py          （重新生成；新章节上线后再跑一遍即可）
     python3 tools/hotline_mine.py --sample 30   （随机抽 30 句看看筛得准不准）

规则（Winter 2026-09-02 要「从他们的 AU 里筛一筛」）：
- 只取弯双引号 “…” 里的对白；靠引号前后的「他 / 角色名 / 你 + 说话动词」判定说话人，
  判不出的一律不要（宁缺毋滥）。
- 跳过题词（> 引语）、HTML 卡片（c-note / c-decree…）、标题、表格。
- 跳过带「炽恋」标签的章节，再过一遍露骨词表——热线是深夜谈心，不是那种深夜。
- 4–60 字；去重；按关键词分到情境桶（night / miss / tired / love / …，其余 daily）。
- 每句带出处：系列英文名 + 章号（页面上显示成小戳「Wintergreen · Ch.7」）。
"""
import json, re, glob, io, sys, random, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def rp(*p): return os.path.join(ROOT, *p)

LINES = json.load(io.open(rp('sam/lines.json'), encoding='utf-8'))
REPLIES = json.load(io.open(rp('sam/hotline-replies.json'), encoding='utf-8'))
NAME = {c['id']: c['name'] for c in LINES['characters']}

# 角色 → 系列（series_name）。有两个 AU 的角色按 au key 分开存。
# 大多数能按系列首页 byline 的角色名自动对上；对不上的（byline 用全名）在这里点名。
MANUAL = {
  'rob': 'Everything in Transit', 'doug': 'Better Living Through You',
  'wildbill': 'Tuning the Devil', 'garyguitar': 'Slow Hands',
  'sambell': "Everybody's Home", 'dixon': 'Only I Know',
  'eric': 'Knox AU', 'bowen': 'This House Is Clean',
  'greaves': {'eyes-on-me': 'Eyes on Me', 'no-one-walks-off': 'No One Walks Off'},
  'jim': {'some-steps': 'Some Steps Only We Know', 'the-one-i-kept': 'The One I Kept'},
}

def series_table():
    out = {}
    for f in glob.glob(rp('series/*/index.html')):
        s = io.open(f, encoding='utf-8').read()
        sn = re.search(r'^series_name:\s*"([^"]*)"', s, re.M)
        by = re.search(r'c-hero__byline-text">([^<]*)<', s)
        if sn and by:
            out[sn.group(1)] = by.group(1).split('·')[0].strip()
    return out

def targets():
    """返回 [(charId, auKey|None, series_name)]"""
    tbl = series_table()
    res = []
    for cid in REPLIES['chars']:
        m = MANUAL.get(cid)
        if isinstance(m, dict):
            for k, sn in m.items(): res.append((cid, k, sn))
            continue
        if isinstance(m, str):
            res.append((cid, None, m)); continue
        nm = NAME.get(cid, '')
        hit = [sn for sn, who in tbl.items() if who == nm or (nm and nm.split()[0] in who.split())]
        if len(hit) == 1: res.append((cid, None, hit[0]))
        else: print('!! 对不上系列:', cid, nm, hit, file=sys.stderr)
    return res

def front_matter(s):
    m = re.match(r'---\s*\n(.*?)\n---\s*\n', s, re.S)
    return (m.group(1), s[m.end():]) if m else ('', s)

def fm_get(fm, key):
    m = re.search(r'^' + key + r':\s*"?([^"\n]*)"?\s*$', fm, re.M)
    return m.group(1).strip() if m else ''

EXPLICIT = re.compile(r'操|干你|干我|进来|进去|插|碰你|摸你|摸我|咬你|湿|硬了|舔|吸|射|阴|乳|奶子|屁股|坐上来|坐下去|腿打开|张开|daddy|Daddy|高潮|下面|摸下|脱|内裤|裸|勃|阴茎|穴|骑|顶|抽|喘|呻吟|做爱|上床|睡你|睡我|要你|要我|吃了你|吃掉你')
SPEECH_HIS = None  # 按角色动态建

def speaker(before, after, his_re):
    """返回 'his' / 'hers' / None"""
    a = re.sub(r'^[，。、！？…—\s]*', '', after)[:16]
    if his_re.match(a): return 'his'
    if re.match(r'你', a): return 'hers'
    # 引号前：取最后一个小句（到 。！？； 为止）
    clause = re.split(r'[。！？；]', before)[-1]
    clause = clause[-40:]
    m = re.search(r'你|他|' + his_re.pattern.strip('^()'), clause)
    if not m: return None
    tok = m.group(0)
    if tok == '你': return 'hers'
    return 'his'

BUCKET_RULES = [
  ('night',     r'晚安|去睡|睡吧|睡觉|该睡|闭眼'),
  ('sleepless', r'睡不着|几点了|半夜|这么晚|还不睡|凌晨'),
  ('tired',     r'累|哭|难过|委屈|别怕|不怕|没事的|没事了|我在这|我在呢|扛|撑'),
  ('miss',      r'想你|想念|见不到|等你|回来'),
  ('love',      r'爱你|喜欢你|亲|抱|吻|宝贝|我的人|你是我的|只有你|就你'),
  ('meet',      r'来找|见面|过来|到我这|跟我走|带你'),
  ('praise',    r'好看|漂亮|聪明|厉害'),
  ('tease',     r'笨|傻|讨厌|欠揍|闭嘴|少来|别闹'),
  ('greet',     r'^在吗|你来了|回来了|早$|早啊|早安'),
]
def bucket_of(cn):
    for b, r in BUCKET_RULES:
        if re.search(r, cn): return b
    return 'daily'

PETS = set(['baby doll', 'Ocean', 'kotku', 'sweetheart', 'princess', 'sugar', 'Nickel', 'Crowe', 'Hart', 'Miss Hart', 'love', 'ma\'am', 'angel', 'kid'])
CONTEXT = re.compile(r'那天|那次|那回|那件事|这件事|这事|刚才|上回|上次|前几天|昨天|今早|方才|那小子|那个人|那家伙|这位|那位|他们|她们|你们|咱们')
def standalone(cn, names):
    """能不能脱离上下文、单独当一句「他对你说的话」"""
    n = len(re.sub(r'[^一-鿿A-Za-z0-9]', '', cn))
    if n < 5 or len(cn) > 45: return False
    if not re.search(r'[。！？…]$', cn): return False           # 半截句子（以逗号 / 破折号收尾）不要
    if re.search(r'[—–]$|——\s*$', cn): return False
    if EXPLICIT.search(cn): return False
    if re.search(r'第[一二三四五六七八九十\d]+章|上一章|这一章', cn): return False
    if re.search(r'[他她]', cn): return False                   # 在说第三个人 → 是剧情，不是对你说的
    if CONTEXT.search(cn): return False
    # 带大写拉丁词（人名 / 地名）的多半是剧情专名；只放行称呼与他自己的名字
    for w in re.findall(r'[A-Z][A-Za-z\'\.]+', cn):
        if w not in PETS and w not in names and w.lower() not in ('i', 'ok', 'okay'): return False
    # 要么是对你 / 关于我说的，要么本身就落在某个情境桶里
    if bucket_of(cn) != 'daily' or re.search(r'你|咱|您', cn): return True
    return bool(re.search(r'我', cn)) and n >= 8            # 只有「我」的叙述句要长一点才站得住
    return True

def mine_series(cid, sn):
    his_name = NAME.get(cid, '')
    names = [n.strip('"“”') for n in re.split(r'[\s"]+', his_name) if n and len(n) > 1]
    his_re = re.compile(r'^(他|' + '|'.join(re.escape(n) for n in names) + ')')
    out, seen = [], set()
    for f in sorted(glob.glob(rp('_posts/*.md'))):
        s = io.open(f, encoding='utf-8').read()
        fm, body = front_matter(s)
        if fm_get(fm, 'series') != sn: continue
        if '炽恋' in fm_get(fm, 'tags'): continue
        if fm_get(fm, 'is_overview') == 'true': continue
        order = fm_get(fm, 'series_order')
        title = fm_get(fm, 'title').split(' — ')[0]
        # 去掉 HTML 块（卡片 / 插图）与题词
        body = re.sub(r'<div[\s\S]*?</div>', '', body)
        body = re.sub(r'<[^>]+>', '', body)
        for para in body.split('\n'):
            p = para.strip()
            if not p or p[0] in '>#|<-*!' or p.startswith('{%'): continue
            ms = list(re.finditer(r'“([^“”]{2,120})”|"([^"“”]{2,120})"', p))
            for i, m in enumerate(ms):
                before = p[(ms[i-1].end() if i else 0):m.start()]
                after = p[m.end():(ms[i+1].start() if i+1 < len(ms) else len(p))]
                if speaker(before, after, his_re) != 'his': continue
                cn = (m.group(1) or m.group(2) or '').strip()
                cn = re.sub(r'^[…—\s]+', '', cn)
                if not standalone(cn, names): continue
                key = re.sub(r'[^一-鿿]', '', cn)
                if key in seen: continue
                seen.add(key)
                out.append({'cn': cn, 'b': bucket_of(cn), 'ch': int(order) if order.isdigit() else 0,
                            'title': title, 'series': sn})
    return out

def main():
    sample = int(sys.argv[sys.argv.index('--sample') + 1]) if '--sample' in sys.argv else 0
    data = {'meta': {'note': '由 tools/hotline_mine.py 从各 AU 正文自动筛出的「他说过的话」（中文正文即译文，无英文原句）。'
                              '每句带 series / ch / title 出处，b = 情境桶。新章节上线后重跑脚本即可，不要手改。'},
            'chars': {}}
    total = 0
    for cid, k, sn in targets():
        lines = mine_series(cid, sn)
        slot = data['chars'].setdefault(cid, {})
        slot[k or 'default'] = lines
        total += len(lines)
        print('%-12s %-18s %-32s %4d 句' % (cid, k or '', sn, len(lines)))
    data['meta']['count'] = total
    io.open(rp('sam/hotline-mined.json'), 'w', encoding='utf-8').write(json.dumps(data, ensure_ascii=False, indent=1) + '\n')
    print('合计', total, '句 → sam/hotline-mined.json')
    if sample:
        pool = [(cid, k, l) for cid, d in data['chars'].items() for k, ls in d.items() for l in ls]
        for cid, k, l in random.sample(pool, min(sample, len(pool))):
            print('  [%s%s · %s Ch.%s · %s] %s' % (cid, '@' + k if k != 'default' else '', l['series'], l['ch'], l['b'], l['cn']))

if __name__ == '__main__':
    main()
