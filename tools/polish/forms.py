#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查一个波兰语词的全部变格 / 变位——写笔记前核对词形用（她很看重准确，别凭印象写词尾）。

    python3 tools/polish/forms.py kawa        # 原形
    python3 tools/polish/forms.py kawy        # 变过的样子也行，会先找回原形
    python3 tools/polish/forms.py piję pić    # 一次查几个

数据是站里「波兰语变格」小工具（polski.html）用的那份 polish-data.json：
约 6000 个常用词，来源 SGJP / Morfeusz2 与维基词典。查不到的词去维基词典核对
（https://en.wiktionary.org/wiki/<词>#Polish 的 Declension / Conjugation 表）。
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CASES = {'Nominative': '主格', 'Genitive': '生格', 'Dative': '与格', 'Accusative': '宾格',
         'Instrumental': '工具格', 'Locative': '方位格', 'Vocative': '呼格'}
TITLES = {'Declension': '变格', 'Present': '现在时', 'Past': '过去时', 'Future': '将来时', 'Imperative': '命令式'}


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    d = json.load(open(os.path.join(ROOT, 'polish-data.json'), encoding='utf-8'))
    lemmas, forms = d['lemmas'], d['forms']
    for w in sys.argv[1:]:
        k = w.lower()
        hits = [k] if k in lemmas else as_list(forms.get(k))
        if not hits:
            print(f'✗ {w}：离线词库里没有，去维基词典核对。\n')
            continue
        if k not in lemmas:
            print(f'· {w} 是 {"、".join(hits)} 变出来的样子')
        for lm in hits:
            e = lemmas.get(lm)
            if not e:
                continue
            print(f'■ {e["word"]}  {e.get("pos", "")} {e.get("extra", "")}'.rstrip())
            for t in e.get('tables') or []:
                cols = [c for c in t.get('columns') or [] if c]
                print(f'  【{TITLES.get(t["title"], t["title"])}】' + (f'  {" / ".join(cols)}' if cols else ''))
                for r in t.get('rows') or []:
                    print(f'    {CASES.get(r["label"], r["label"]):<8} ' + ' / '.join(r.get('forms') or []))
        print()


def as_list(v):
    return [] if not v else v if isinstance(v, list) else [v]


if __name__ == '__main__':
    main()
