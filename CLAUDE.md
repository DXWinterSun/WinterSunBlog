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

## 图片工作流（封面图）

- **默认前提**：用户上传的图片文件统一传到 `main` 分支（通过 GitHub
  网页上传）。当用户说「我上传了图片 / 在 image 文件夹上传了」，先
  `git fetch origin main`，再去 `origin/main` 的 `images/` 目录里找；
  当前工作分支上没有是正常的，用
  `git checkout origin/main -- images/<文件名>` 取到工作分支即可。
- 用户会在对话里直接给出「图片 → 文章 / 系列」的对应要求。据此把
  `image: <文件名>` 写进对应文章的 front matter（放在 `date:` 行之后；
  系列文章按惯例**每一章都加**同一张封面）。
- 文章配图通过模板渲染成 `background-image`，格式无关；`.webp`、
  `.jpg`、`.png` 都能正常显示。**文件名大小写 / 扩展名必须与实际文件
  完全一致**（GitHub Pages 区分大小写）。
- 系列与角色 AU 的对应：「You Are My Fact」= Leonard Shelby AU
  (`leonard-shelby-au.jpg`)；「Good Enough」= Justin Hammer AU
  (`justin-hammer-au.webp`)。其余对应见各文 `series_title` 字段。
- 站点从 `main` 部署：front matter 改动必须并入 `main` 才会在线上生效，
  仅在工作分支上不够。
