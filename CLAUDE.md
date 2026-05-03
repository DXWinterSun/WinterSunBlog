# WinterSunBlog — 写作规范

## 文章 `summary` 字段（front matter 里的引言）

**硬性长度限制：≤ 35 个汉字。**

理由：首页的文章卡片对 `summary` 用了 `-webkit-line-clamp: 2`，
样式定义在 `_sass/5-components/_index-post.scss`。在 390px 手机视口
下，15px 衬线字号每行只塞得下约 20 个汉字，2 行最多 ~40 字。预留
一点边距，控制在 35 字以内才能完整呈现，不会出现「他们在那张床
上看了《七个神…」这种半截截断。

写新章节 / 新文章的时候：

1. `summary:` 必须是单句、≤35 汉字（含标点）。
2. 不要为了塞字数把引号、破折号删掉——这些是节奏的一部分。宁可
   砍内容也要留标点。
3. 引言是「钩子」，不是摘要。给读者一个画面、一句话、一个悬念，
   不要剧透完整情节。
4. 章节正文里的引言段落（通常在文首 `>` 引语或本章的开场）不受这
   个限制——只有 front matter 的 `summary:` 字段需要 ≤35 字。

写完后用以下命令快速核查长度：

```bash
grep -E '^summary:' _posts/<file>.md | sed 's/^summary: *"//; s/"$//' | awk '{print length}'
```

（注意：`length` 是按 UTF-8 字节算的，1 个汉字 ≈ 3 字节，所以阈值
应该是 ~105。要精确按字符数可以用 Python：
`python3 -c "import sys; print(len(sys.argv[1]))" "<summary 内容>"`）

## 其他

- 工作分支：`claude/redesign-blog-homepage-RSiJO`（首页改版相关）。
- 只在用户明确要求时再开 PR。
- 内部链接全部要用 `{{ site.baseurl }}` 前缀，否则在 GitHub Pages
  默认 URL 下会 404。
- 修改 `js/main.js` 后记得 cache-bust 已经在 `_includes/javascripts.html`
  里通过 `?v={{ site.time | date: '%Y%m%d%H%M' }}` 自动处理，不用手动改。
