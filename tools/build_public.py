#!/usr/bin/env python3
"""
Build the public, standalone Sam quiz for Cloudflare Pages.

Takes the full quiz page (sam/quiz/index.html) and produces a clean,
self-contained copy under public/ that:

  * removes every link out to content we do NOT publish
    (the Sam hub "For Sam", the many-faces gallery, the 8 AU series stories);
  * rewrites icon paths to the site root (no /WinterSunBlog subpath);
  * fixes the og:url so shared links never leak the github.io address.

The source file is left untouched, so the full version on GitHub Pages keeps
working exactly as before. Only the derived copy in public/ is stripped down.

Run from anywhere:  python3 tools/build_public.py
Output:             public/index.html  +  public/images/…  +  public/favicon.ico

To add more pages to the public site later, extend PAGES / ASSETS below.
When you bind a custom domain, change SITE_URL to it.
"""

import os
import re
import shutil
import sys

# 对外的干净域名。绑定自定义域名后把这里换成你的域名即可。
SITE_URL = "https://winter-sam.pages.dev"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sam", "quiz", "index.html")
OUT_DIR = os.path.join(ROOT, "public")

# 测试页需要的静态资源： 源路径 -> public/ 下的目标路径
ASSETS = {
    "images/heading-normal.png": "images/heading-normal.png",
    "images/favicon-180.png": "images/favicon-180.png",
    "favicon.ico": "favicon.ico",
}


def replace_once(text, old, new, label):
    """Exact replacement that fails loudly if the anchor text is missing —
    so an upstream edit to the quiz can never silently ship a broken/leaky
    public build."""
    if old not in text:
        sys.exit(f"[build_public] ERROR: expected snippet not found: {label}\n"
                 f"  The quiz source changed. Update tools/build_public.py.")
    return text.replace(old, new, 1)


def transform(html):
    # ── 1. 修掉会泄露 github.io 的 og:url ────────────────────────────
    html = replace_once(
        html,
        '<meta property="og:url" content="https://dxwintersun.github.io/WinterSunBlog/sam/quiz/">',
        f'<meta property="og:url" content="{SITE_URL}/">',
        "og:url",
    )

    # ── 2. 图标路径去掉 /WinterSunBlog 子路径 ────────────────────────
    html = html.replace('href="/WinterSunBlog/images/', 'href="/images/')
    html = html.replace('href="/WinterSunBlog/favicon.ico"', 'href="/favicon.ico"')

    # ── 3. 顶部两处「← For Sam」返回主页链接 → 换成占位，保持排版居中 ──
    html = replace_once(
        html,
        '''        <a href="/WinterSunBlog/sam/" style={{
          color:p.muted, textDecoration:"none", fontSize:"0.72rem",
          fontFamily:"'Special Elite',monospace", letterSpacing:"0.15em", opacity:0.85
        }}>← For Sam</a>''',
        '        <span style={{width:60}}/>',
        "intro nav back-link",
    )
    html = replace_once(
        html,
        '''        <a href="/WinterSunBlog/sam/" style={{
          color:c.muted, textDecoration:"none", fontSize:"0.7rem",
          fontFamily:"'Special Elite',monospace", letterSpacing:"0.15em", opacity:0.7
        }}>← For Sam</a>''',
        '        <span style={{width:60}}/>',
        "result nav back-link",
    )

    # ── 4. 结果页「你的侧面」卡片：保留卡片内容，去掉跳转（<a> → <div>）──
    html = replace_once(
        html,
        '''              <a key={dim.key}
                href={"/WinterSunBlog/sam/many-faces/#"+fc.id}
                target="_blank" rel="noopener"
                style={{''',
        '''              <div key={dim.key}
                style={{''',
        "facet card open tag",
    )
    html = replace_once(
        html,
        '''                }}>{fc.tagline}</p>
              </a>''',
        '''                }}>{fc.tagline}</p>
              </div>''',
        "facet card close tag",
    )
    # 上面把 <a> 换成 <div>，对应的移动端 CSS 选择器也跟着改
    html = html.replace(".facet-list a {", ".facet-list > div {")

    # ── 5. 结果页两个「READ HIS STORY」按钮（指向 many-faces / AU）→ 删除 ──
    html = replace_once(
        html,
        '''          <a href={"/WinterSunBlog/sam/many-faces/#"+c.id} style={{
            border:`1px solid ${c.accent}`, color:c.accent, padding:"12px 24px",
            fontFamily:"'Special Elite',monospace", fontSize:"0.7rem",
            letterSpacing:"0.15em", textDecoration:"none", transition:"all 0.2s"
          }}
            onMouseEnter={e=>{ e.currentTarget.style.background=c.accent; e.currentTarget.style.color=c.bg; }}
            onMouseLeave={e=>{ e.currentTarget.style.background="transparent"; e.currentTarget.style.color=c.accent; }}
          >READ HIS STORY →</a>
          {c.auLink && (
            <a href={c.auLink} style={{
              border:`1px solid ${c.accent}55`, color:c.text, padding:"12px 24px",
              fontFamily:"'Special Elite',monospace", fontSize:"0.7rem",
              letterSpacing:"0.15em", textDecoration:"none", transition:"all 0.2s"
            }}
              onMouseEnter={e=>{ e.currentTarget.style.borderColor=c.accent; e.currentTarget.style.color=c.accent; }}
              onMouseLeave={e=>{ e.currentTarget.style.borderColor=c.accent+"55"; e.currentTarget.style.color=c.text; }}
            >READ HIS STORY (AU) →</a>
          )}
''',
        "",
        "result action story-buttons",
    )

    # ── 6. 数据里 8 个 AU 系列链接字符串 → 删除（页面已不再引用，避免源码里残留路径）──
    html = re.sub(r'\s*auLink:"[^"]*"', "", html)

    # ── 7. 兜底：确认没有任何会暴露来源的字符串残留 ───────────────────
    for bad in ("/WinterSunBlog", "github.io", "dxwintersun"):
        if bad in html:
            sys.exit(f"[build_public] ERROR: leak remains in output: {bad!r}. "
                     f"A link/path was missed — fix tools/build_public.py.")
    return html


def main():
    with open(SRC, encoding="utf-8") as f:
        html = f.read()

    html = transform(html)

    # 清空并重建 public/
    if os.path.isdir(OUT_DIR):
        shutil.rmtree(OUT_DIR)
    os.makedirs(OUT_DIR)

    with open(os.path.join(OUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

    for src_rel, dst_rel in ASSETS.items():
        src = os.path.join(ROOT, src_rel)
        dst = os.path.join(OUT_DIR, dst_rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)

    print("[build_public] wrote public/index.html")
    for dst_rel in ASSETS.values():
        print(f"[build_public] copied public/{dst_rel}")
    print(f"[build_public] done. public site root -> the quiz, canonical {SITE_URL}")


if __name__ == "__main__":
    main()
