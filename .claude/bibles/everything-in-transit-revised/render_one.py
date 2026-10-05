# 重新生成改版预览页的某一章（带上一章/下一章导航）：python3 .claude/bibles/everything-in-transit-revised/render_one.py N ；输出目录 O 按需改
import sys,subprocess,yaml,re
n=int(sys.argv[1]);D='.claude/bibles/everything-in-transit-revised';O='/tmp/claude-0/-home-user-WinterSunBlog/97bc39de-a1ae-5be8-99d9-9178a5410199/scratchpad/eit-read'
fm=yaml.safe_load(open(f'{D}/ch{n}.md').read().split('---')[1]);cn=re.search(r'· (.*?) —',fm['title']).group(1)
subprocess.run(['python3','tools/preview/render_draft.py',f'{D}/ch{n}.md','-o',f'{O}/ch{n}.html','--series','Everything in Transit','--title',cn,'--subtitle',f'Chapter {n}','--kicker','Everything in Transit · Rob Cove AU','--mood',' · '.join(fm['tags'][4:]),'--eyebrow','改版稿 / 待冬璇过目','--notes',f'{D}/ch{n}-notes.md'],check=True,capture_output=True)
h=open(f'{O}/ch{n}.html').read()
prev=f'<a href="ch{n-1}.html">← 第 {n-1} 章</a>' if n>1 else '<span></span>'
nxt=f'<a href="ch{n+1}.html">第 {n+1} 章 →</a>' if n<32 else '<span></span>'
nav=f'<nav class="eitnav">{prev}<a href="./">全部章节</a>{nxt}</nav>'
css='<style>.eitnav{position:relative;z-index:2;display:flex;justify-content:space-between;gap:12px;max-width:44rem;margin:0 auto;padding:14px 1.4rem;font-family:"EB Garamond",Georgia,serif;font-size:15px;letter-spacing:.04em}.eitnav a{color:var(--accent);text-decoration:none;border-bottom:1px dashed color-mix(in srgb,var(--accent) 50%,transparent)}</style>'
h='<!doctype html>\n<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'+h.replace('<style>',css+'<style>',1)
h=h.replace('<div class="wrap">',nav+'<div class="wrap">',1)+nav
open(f'{O}/ch{n}.html','w').write(h)
