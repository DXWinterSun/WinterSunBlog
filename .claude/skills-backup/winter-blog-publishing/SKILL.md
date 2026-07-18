---
name: winter-blog-publishing
description: 维护 Winter 的 Jekyll 博客 WinterSunBlog（仓库 DXWinterSun/WinterSunBlog，线上 dxwintersun.github.io/WinterSunBlog）的发布规范与部署流程。当 Winter 要把内容发到博客——新建或续写一篇 AU 连载章节、新建一个 AU 系列首页、把某个系列标记为完结、或要一份「发给 Claude Code 就能部署」的文章 / 替换指令时，必须使用本 skill。触发词：发博客、发博文、发文章、博客、部署、front matter、AU 章节、续写、新建系列、系列首页、完结、summary、WinterSunBlog、Jekyll、GitHub Pages。即使 Winter 只是说「这章写好了发出去」「帮我整成能发的格式」「这个系列完结了」，只要落点是 WinterSunBlog 的文章或系列首页，也必须用本 skill 的全部规范，并在交付前用 check_post.py 校验，避免发到 Code 那边还要返工。注意区分：往「Many Faces of Sam」画册加角色用 winter-many-faces-of-sam；本 skill 专管博客文章 / 系列首页的 front matter、标签、系列字段、图片与部署这一整套发布规范。
---

# WinterSunBlog · 发布规范与部署

Winter 的个人博客是一个 Jekyll 站点，文章放在 `_posts/` 目录，AU 连载按「系列」组织。她的部署方式是：在这里把内容做成**完全合规**的成品，复制后发给 Claude Code，由 code 写进仓库。本 skill 的职责是让这份成品在格式上零返工。

- **仓库**：`github.com/DXWinterSun/WinterSunBlog`（线上：dxwintersun.github.io/WinterSunBlog）
- **文章目录**：`_posts/`
- **系列首页**：`series/<slug>/index.html`
- **线上 raw 前缀**（用于拉取与校验）：
  `https://raw.githubusercontent.com/DXWinterSun/WinterSunBlog/main/`

## 三条铁律

1. **会变的东西，一律以「当前线上文件」为准，不能凭记忆。** 尤其是 `series_order`（系列内章节序号，要接着上一章 +1）和 `collection_order`（Sam 画册里的系列序号，要现有最大值 +1）。动手前先拉取相关文件看清当前值。已知系列的封面 / `series_name` / `collection_order` 登记在 `references/series-registry.md`，但那只是备忘——**真源永远是线上文件**。
2. **交付前必须跑校验。** 新建 / 续写文章时，用 `scripts/check_post.py` 校验 front matter（`summary` 字数、标签白名单、`series` 是否混进中文、必填字段是否齐全等），通过了再交付。这一步就是为了根治「发到 Code 那边才发现格式错」。
3. **交付物分两类，别搞混**（见下「两类交付物」）。新建 / 续写文章 → 一份完整的 `.md` 文件内容；改动现有的系列首页 `index.html`（新建系列、改完结状态）→ 一份「精确替换（找到 → 替换为）」的 Markdown，和 `many-faces` 画册的部署方式一致。

---

## 两类交付物

### A 类：新建 / 续写一篇文章 → 完整 `.md`

落点是 `_posts/` 里新增一个文件。交付一份**完整的 `.md` 文件内容**（front matter + 正文），并给出文件名。Winter 把它发给 Code，由 code 在 `_posts/` 下新建该文件。

文件名格式：`_posts/YYYY-MM-DD-series-slug-chapter-N-title.md`

流程：
1. 跟 Winter 把这章 / 这篇聊清楚：属于哪个系列、第几章、情绪基调、要不要题词。
2. 若是续写：先拉取该系列已发的最新一章，确认 `series`、`series_title`、封面 `image`、当前的 `series_order` 到了几——新章节 `series_order` = 上一章 + 1，`series`/`series_title`/`image` 与同系列保持完全一致。
3. 按下面的「front matter 模板」填齐，写正文。
4. 跑 `check_post.py` 校验，过了再交付。

### B 类：改动系列首页 `index.html` → 精确替换 Markdown

落点是改动一个已存在的 `series/<slug>/index.html`（例如新建一个 AU 系列、或把某系列从连载改完结）。**不要把整份 `index.html` 重写交给 Winter**，而是产出一份「逐处找到 → 替换为」的 Markdown，由她发 Code 执行。

动手前先拉取当前线上的该文件为准；改完在本地副本上确认没误伤别处，再产出替换指令。模板见 `references/series-page.md`。

> 判断：只是发一章故事 → A 类。要动系列首页的展示 / 状态 / 在 Sam 画册里的露出 → B 类。一次同时做两件事时，两份交付物分开给清楚。

---

## front matter 模板（A 类文章，可直接照填）

front matter 是 `.md` 文件**最开头**由一对 `---` 包起来的部分：

```yaml
---
layout: post
title: "Chapter N · 章节中文标题 — Series English Name"
date: YYYY-MM-DD
image: cover-image.jpg          # 文件名大小写必须与 images/ 目录里的实际文件完全一致
tags: [角色名, 演员名, AU, 系列英文名, mood1, mood2]   # 4 身份 + 1-2 个 mood，见下
categories: ["AU Story"]
series: "English Series Name"   # 必须纯英文（ASCII），与系列首页 series_name 完全一致
series_title: "English Series Name · Character AU"
series_order: N                 # 整数，从 1 开始；续写时 = 上一章 + 1
series_status: ongoing          # ongoing 连载中 / complete 已完结
series_type: Series
chapter_type: "Chapter N"       # 如 "Chapter 1" / "Extra" / "Interlude"
summary: "≤35 字的钩子引言。"   # 硬上限 35 个字符（含标点），见下
---
```

正文紧跟在第二个 `---` 之后。

---

## 核心规范（逐条）

### 1. `summary` —— 最重要的限制：≤ 35 个字符（含标点）

首页卡片用了两行截断（`-webkit-line-clamp: 2`），手机端每行约 20 字，**超过 35 字会被截成半句**。

- `summary` 是「钩子」，给一个画面 / 一点悬念，**不剧透情节**。
- 宁可删内容，也要保留破折号、引号这些节奏标点。
- 超过 35 字时**不要问 Winter，直接自行缩写**到 35 字以内。
- 计数方式：按字符数（Python `len()`）。`check_post.py` 会自动算。

> 注意区分：这个 35 字上限**只管 front matter 里的 `summary` 字段**。正文开头的题词 / 引语块（blockquote，见第 6 条）**没有字数限制**。

### 2. `tags` —— 固定全格式：4 身份标签 + 1-2 个 mood

格式固定 `[角色名, 演员名, AU, 系列英文名, mood1, mood2]`，前四位是**身份标签**（同一系列每章都一样），末尾是 1-2 个 mood。例：`[Don Verdean, Sam Rockwell, AU, Faith Unseen, 悸动, 暗涌]`。**别只写 mood。**

- 第 1 位 角色名、第 2 位 演员名：非空即可（不设白名单）。
- 第 3 位：必须是字面量 `AU`。
- 第 4 位：必须 = 该章 `series` 值（能抓出系列名打错）。
- 末尾 1-2 位：mood，只能从下面 9 个白名单里选：

```
炽恋   悸动   缱绻   思念   安放   怅惘   暗涌   怀旧   絮语
```

mood 不能自造。标签目前**只在 `/archive/` 页面**作为彩色筛选药丸显示，单篇文章页面不显示，但 front matter 里仍要写全。`check_post.py` 的 `check_tags()` 会逐条校验以上五点。

### 3. `series` —— 必须纯英文（ASCII），绝不能用中文

Jekyll 的 slugify 会把所有中日韩字符丢掉，导致系列链接变成 `/series//`、首页卡片整个消失。所以 `series:` 的值只能是 ASCII。

中文只能出现在**不参与生成链接路径**的字段里：`title`、`series_title`、`collection_title`，以及页面 HTML 的展示位。

### 4. 三处字符串必须完全一致

同一个系列，下面三处的英文名要一字不差，否则系列页断链：

| 位置 | 字段 | 示例 |
|---|---|---|
| 章节文章 | `series:` | `"Tuning the Devil"` |
| 系列首页 | `series_name:` | `"Tuning the Devil"` |
| 系列目录路径 | `series/tuning-the-devil/` | —— |

### 5. 同系列共用同一张封面

同一系列所有章节的 `image:` 用**同一张封面图**。封面登记见 `references/series-registry.md`（以线上为准）。文件名大小写必须和 `images/` 目录里的实际文件完全一致。

### 6. 正文题词 / 引语块（blockquote）无字数限制

正文开头那段 `>` 引语（blockquote）想写多长写多长，第 1 条的 35 字上限**不约束**它。

### 7. 世界观 / 设定总览不单独建 post，写进系列首页（全 HTML）

人物、设定、世界观这类「设定总览」内容写进系列首页 `series/<slug>/index.html` 的 `<article class="c-sam-intro">` 区块里。**不要**建一个带 `series:` 字段的「Chapter 0」式 post——那会混进章节列表，语义和显示都不对；也不要手写章节目录（模板自动生成）。

> ⚠ **关键反差**：系列首页的设定区块和 Hero 区块**全部写 HTML，不是 Markdown**——这跟 `_posts/` 文章正文写 Markdown 正好相反。具体的区块结构与写作要求（Hero 灵魂句、「关于这个系列」、「设定档案」的字数 / 全角符号 / `c-sam-intro__closing` 收尾等）见 `references/series-page.md`，写完用 `check_series_page.py` 自检。

### 8. 内部链接一律加 `{{ site.baseurl }}` 前缀

所有站内链接都要写成 `{{ site.baseurl }}/...`，否则在 GitHub Pages 下会 404。

---

## Sam 系列特有规则（`sam_collection`）

`sam_collection: true` **只给 Sam Rockwell 本人演过的角色**对应的系列加，其他演员的角色故意不加、不进 Sam tab。

新建一个 AU 系列首页 `series/<slug>/index.html` 时，若主角是 Sam 演的，front matter 里加：

```yaml
sam_collection: true
collection_order: N           # 现有最大值 +1（先拉线上文件确认当前最大值）
collection_eyebrow: "AU Story · Series"
collection_title: "English Title · Character AU"
collection_desc: "一两句钩子简介。"
```

> 系列首页除了这组 front matter，还有 Hero 区块和设定总览（关于这个系列 / 设定档案）要写——**全 HTML**，结构与写作要求都在 `references/series-page.md`。新建系列首页时先拉一个现成的同类系列首页当样板照骨架改，别凭空捏结构。

---

## 部署操作约定（交付时附带提醒 Code 的事项）

这些是发给 Claude Code 执行时要带上的注意事项：

- **图片工作流**：图片由 Winter 在 GitHub 网页上传到 `main` 分支的 `images/` 目录。Code 用图前先 `git fetch origin main`，再 `git checkout origin/main -- images/<文件名>` 把文件取到工作分支。`image:` 字段大小写要与实际文件一致。
- **工作分支**：以 Winter 当前提供的工作分支为准（会随时间变化，**不要在 skill 里硬编码某个分支名**）。
- **不自动开 PR**：**只在 Winter 明确要求时**才创建 PR，否则只在工作分支上提交，不要自动建 PR。

---

## 校验脚本用法

两个脚本配套，对应两类交付物，发前各跑各的：

**A 类（文章）**——成品写成 `.md` 后跑：

```bash
python3 scripts/check_post.py 路径/到/文章.md
```

逐项检查并打印 ✅ / ❌：能否分离出 front matter、必填字段是否齐全、`summary` 是否 ≤35 字、`tags` 是否符合全格式（4 身份 + 1-2 mood、第 3 位 = `AU`、第 4 位 = `series`、mood 在白名单）、`series` 是否混进非 ASCII 字符、`series_order` 是否整数、`series_status` 是否合法、`categories` 是否为 `["AU Story"]`、`date` 与文件名是否一致。

**B 类（系列首页）**——`index.html` 改好后跑：

```bash
python3 scripts/check_series_page.py 路径/到/index.html
```

检查 Hero 标题是否英文（中文会断链，记硬错误）、有无 `{% include au-palette-strip.html %}`、Hero 灵魂句字数（10-25）、「关于这个系列」总字数（200-350）、每个 `c-sam-intro` 区块是否有 `c-sam-intro__closing` 收尾、「设定档案」条目是否用全角「｜」与全角空格、条目字数（50-100）。

两个脚本都在头部把白名单 / 字数上限 / 必填字段做成了常量，规范变了改那几行即可。全绿（或仅剩可接受的 ⚠️ 提醒）再交付。

---

## 如何更新本 skill

Winter 会在博客规范变化时，从 Claude Code 那边拿到一份**新的发布规范说明**带过来。此时：

1. 逐条比对新说明与本 skill 的现有章节，**据此同步更新**对应的规范文字、`front matter 模板`、`references/` 里的文件，以及两个校验脚本里的校验项——`scripts/check_post.py`（文章：标签白名单、`summary` 上限、必填字段等）和 `scripts/check_series_page.py`（系列首页：各区块字数范围、全角符号、`au-palette-strip` 等）。规范哪一条变了，就同步改对应文档段落 + 对应脚本。
2. 涉及「会增长的清单」（新系列、新封面、`collection_order` 新值）时，更新 `references/series-registry.md`。
3. 改完后提醒 Winter：skill 改动需要**重新打包安装**才会在新对话里生效。

> 原则：本 skill 是「博客发布规范」的载体，规范的真源是 Winter 带来的最新说明 + 线上仓库。两者变了，skill 就跟着变。

---

## 参考文件

- `references/series-registry.md` —— 已知 AU 系列登记：封面图、英文 `series_name`、`collection_order`，以及是否进 Sam 画册。新增系列时在此登记；**实际数值以拉取线上文件为准**。
- `references/series-page.md` —— B 类任务（建 / 改系列首页 `index.html`）的全套规范：**系列首页内容怎么写**（Hero 区块、「关于这个系列」、「设定档案」的 HTML 结构与字数 / 全角符号 / `closing` 要求）+ 新建系列首页的 front matter 字段 + 拉取 / 校验命令 + 精确替换 Markdown 模板。

## 脚本

- `scripts/check_post.py` —— A 类（文章）front matter 校验。
- `scripts/check_series_page.py` —— B 类（系列首页）内容校验。
