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

## Sam tab 的 The Collection（AU 系列卡片）

`/sam/`（`sam/index.html`）里「The Collection」区块的 AU 系列卡片是
**动态生成**的：模板遍历 `site.pages`，挑出 front matter 里写了
`sam_collection: true` 的 `series/*/index.html`，按 `collection_order`
升序排列。所以**新增一个 Sam 的 AU 系列时不用动 `sam/index.html`**，
只要在该系列的 `index.html` front matter 里加上这几个字段即可：

```yaml
sam_collection: true            # 出现在 Sam tab 的开关
collection_order: 6             # 排序，数字越小越靠前
collection_eyebrow: "AU Story · Series"   # 卡片小标签（oneshot 用 "AU Story · Oneshot"）
collection_title: "标题 · 角色 AU"         # 卡片标题
collection_desc: "一两句简介，钩子即可。"   # 卡片描述
```

**关键规则：`sam_collection` 只给 Sam Rockwell 本人演过的角色。**
这是一个**显式 opt-in 开关**——不加就不会出现，所以不可能把别人的
角色误收进来。判断标准是「这个角色是不是 Sam 本人演的」，而不是
「这篇 AU 在不在 `series/` 目录里」。例如：

- ✅ Sam Bell（Moon）、John Moon（A Single Shot）、Eric Knox
  (Charlie's Angels)、Zaphod（银河系漫游指南）、Justin Hammer
  (Iron Man 2) —— 都是 Sam 的角色，已加 flag。
- ❌ Leonard Shelby（《记忆碎片》）是 **Guy Pearce** 的角色，不是
  Sam。所以 `series/you-are-my-fact/` **故意不加** `sam_collection`，
  不进 Sam tab。（该文 front matter 里已留注释说明。）

不确定某个角色是不是 Sam 演的，就先问用户，别擅自加 flag。

## ⚠️ `series:` 字段必须用英文（ASCII）

**绝对不能用中文做 `series:` 的值。**

`index.html` 用 `series_name | slugify` 生成系列卡片的链接，Jekyll 的
`slugify` 会把所有 CJK 字符丢掉，导致链接变成 `/series//`，卡片在
首页完全不出现。

规则：
- 章节 front matter 的 `series:` → 必须是英文，例如 `"Tuning the Devil"`
- 系列首页的 `series_name:` → 必须跟上面完全一致（也是英文）
- 系列目录 slug（`series/tuning-the-devil/`）→ 就是英文 `series:` 值的
  slugify 结果，三者要能对上

中文只能出现在 `title:`、`series_title:`、`collection_title:`、hero HTML
等**纯展示**字段里，不参与 Jekyll 路径生成的地方随便用。

## ⚠️ 系列首页 hero 标题必须用英文

`series/*/index.html` 里 `<h1 class="c-hero__title">` 必须写英文标题
（和 `series_name` / 系列目录 slug 保持一致），中文只能出现在副标题、
byline、lede 引语等展示位置。例如：

```html
<h1 class="c-hero__title">Tuning the Devil</h1>  <!-- ✅ 英文 -->
<h1 class="c-hero__title">为他调音</h1>           <!-- ❌ 中文 -->
```

## ⚠️ 设定总览的内容直接写进系列首页，不要单独建章节 post

设定总览（世界观、人物、信物、基调）的内容全部写在
`series/*/index.html` 的 `<article class="c-sam-intro">` 区块里，
**不要**单独建一篇带 `series:` 字段的 post 来当"Chapter 0"。

原因：`_layouts/series.html` 会把所有带 `series:` 的 post 全部列进章节
目录和配图卡片，把设定总览混进去显示和语义都不对。

正确做法（参考 `you-are-my-fact` / `sam-bell-moon-au`）：
- 第一个 `c-sam-intro`：「关于这个系列」，2-4 段概述世界观与核心冲突
- 第二个 `c-sam-intro`（可选）：「设定档案」，人物简介 + 信物 + 关系动力学
- 内容直接写 HTML，不用 Markdown，不用单独的 post
- 如果确实需要一篇可访问的设定文档，建普通 post 但**不加** `series:` 字段，
  用 `is_overview: true` 标记，不会出现在章节列表

## AU 系列的「目录 + 章节导航」（模板自动渲染，别手写）

为了让长系列好读，章节列表和上下文导航全部由模板统一生成，**新系列、
新章节会自动继承，不需要每篇手动加**。三个部分：

1. **系列首页的「目录 + 配图卡片」** —— 由 `_layouts/series.html` 渲染。
   每个 `series/*/index.html` 只负责写 hero + 简介，**章节区块不要手写**。
   只要 front matter 里有这两行就会自动出现（含顶部纯文字「目录 ·
   Contents」快速跳转 + 下方配图卡片，按 `series_order` 排序）：

   ```yaml
   layout: series
   series_name: "Good Enough"   # 必须跟各章 front matter 的 series 字段【完全一致】
   # series_status: ongoing      # 可选，默认 ongoing，显示在 Chapters 计数旁
   ```

   ⚠️ `series_name` 写错（跟 `series:` 对不上）→ 目录会是空的。之前
   Zaphod / Knox 就因为 index 里写的字符串和章节的 `series` 不一致，
   首页章节列表一直是空的；现已统一用 `series_name` 修好。

2. **章节顶部 / 底部的「返回系列目录」** —— 由 `_layouts/post.html` 渲染。
   任何带 `series` 字段的文章，顶部会出现一个返回链接（显示完整
   `series_title`），底部章节导航里也有一个圆角「返回《系列名》目录」
   按钮，都跳到 `…/series/<slug>/#chapters`。所以**章节 front matter 里
   `series` / `series_title` / `series_order` 必须齐全**（现有 49 章都齐）。

3. 这套东西的样式在 `_sass/5-components/_extras.scss`
   （`c-series-toc` / `c-chapter-return` / `c-chapter-nav__back`）。

一句话：**开新系列 = 复制一个 `series/*/index.html`，改 hero/简介，设好
`layout: series` 和 `series_name` 即可；章节照常写齐 `series*` 字段。
目录和返回按钮都会自己长出来。**

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
