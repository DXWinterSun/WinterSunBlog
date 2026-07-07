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

**summary 超字数时**：不要问用户，直接自行缩写到 35 字以内，保留核心钩子和节奏感。

**⚠️ summary 里严禁出现 ASCII 双引号 `"`（U+0022）**

`summary:` 的值用 `"..."` 包裹（YAML 双引字符串），如果内容里也有 `"` 就会
提前截断字符串，导致 Jekyll YAML 解析失败，整篇 post **从系列目录和首页彻底消失**，
不会有任何报错提示，极难排查。

常见危险写法（对白引用）：

```yaml
# ❌ 内层 ASCII 双引号，YAML 直接崩
summary: "他举杯说："Champagne？""
summary: "他低声说："小姑娘，你早该逃的。"但你一动不动。"
```

安全替代方案（任选一种）：

```yaml
# ✅ 用破折号代替引号
summary: "他举杯——Champagne？"
summary: "他低声说小姑娘你早该逃的，但你一动不动。"

# ✅ 用中文弯引号（U+201C / U+201D），YAML 不识别为分隔符
summary: "他举杯说："Champagne？""

# ✅ 改用 YAML 单引号包裹整个值（内层单引号用两个 '' 转义）
summary: '他说：''Champagne？'''
```

写完后用 Python 快速验证：
```bash
python3 -c "
import yaml, sys
fm = open(sys.argv[1]).read().split('---')[1]
yaml.safe_load(fm)
print('OK')
" _posts/<file>.md
```

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

## ⚠️ `series_title` 格式：必须用角色名，不能用剧名或背景设定

`series_title:` 的格式固定为：`"Series English Name · Character Name AU"`

✅ 正确示例：
```yaml
series_title: "The Invisible Light · Charles II AU"
series_title: "Good Enough · Justin Hammer AU"
series_title: "Before the World Broke for Us · Hector Escaton AU"
series_title: "The One Who Fell from the Sky · Charles AU"
```

❌ 错误示例（用剧名 / 背景设定代替角色名）：
```yaml
series_title: "Before the World Broke for Us · Westworld AU"   # ❌ 用了剧名
series_title: "The One Who Fell from the Sky · RAF 1940 AU"    # ❌ 用了背景
```

`series_title` 只用于前端展示（章节顶部返回链接），不参与路径生成，
但保持格式统一可以避免出现「系列说明里找不到角色名」的情况。

### 所有「展示」字段都要用「故事名 · 角色名 AU」，永远用角色名不用剧名

这条不只管 `series_title`。**凡是读者能看到的 AU 标识，一律统一成
`Story English Name · Character Name AU` 这一个格式，用角色名，绝不用剧名。**
剧名 / 背景设定只能出现在 byline 和「设定档案」里，不能当标题。

为什么用角色名：一部电影可能开好几个 AU（例如《Moon》下就有
**The Far Side** 和 **The Near Side** 两个 Sam Bell AU），用剧名会直接撞车；
全站的组织轴心（尤其 `sam_collection`）本来就是角色，不是电影。

需要同步统一的展示字段，以及各自的取值：

| 位置 | 字段 | 取值格式 | 例 |
|---|---|---|---|
| 系列首页 front matter | `title:` | `Story · Character AU` | `The Far Side · Sam Bell AU` |
| 系列首页 hero | `<h1 class="c-hero__title">` | **只写 Story**（不带 `· 角色 AU`） | `The Far Side` |
| Sam tab 卡片 | `collection_title:` | `Story · Character AU` | `The Far Side · Sam Bell AU` |
| 章节 front matter | `series_title:` | `Story · Character AU` | `The Far Side · Sam Bell AU` |
| 章节 front matter | `title:` 后缀 | `Chapter N · 中文名 — Story` | `Chapter 1 · Departure — The Far Side` |

⚠️ **内部管线字段不要动**：`series:`（章节）/ `series_name:`（系列首页）/
目录 slug 三者必须完全一致，且 `_data/au_palettes.yml` 的配色 key 就是
`series_name`。这些是不可见的内部键，哪怕值还是旧的（如 `"Sam Bell · Moon AU"`）
也**保持原样**——改它们会动到 URL、章节分组和配色，得不偿失。统一标题只改
上表那些展示字段即可。

❌ 反例（同一部电影用剧名，或光秃秃只有角色名 / 剧名）：
`Sam Bell · Moon AU`（用了剧名 Moon）、`A Single Shot AU`（纯剧名）、
`Alexios AU`（缺 Story 名）。都应改成 `Story · Character AU`。

## ⚠️ 系列首页 byline 格式统一为「角色 · 作品出处 · 演员 · 状态」

`c-hero__byline-text` 的固定格式是四段：

```
角色名 · 作品出处 · 演员 · 状态
```

```html
<!-- Sam Rockwell 的角色 -->
<span class="c-hero__byline-text">Justin Hammer · Iron Man 2 · Sam Rockwell · ongoing</span>

<!-- BayBay（Mathew Baynton）的角色 -->
<span class="c-hero__byline-text">Charles II · Horrible Histories · BayBay · ongoing</span>

<!-- 其他演员的角色 -->
<span class="c-hero__byline-text">Hector Escaton · Westworld · Rodrigo Santoro · ongoing</span>
```

四段规则：
- **作品出处**：角色真正的出处作品（电影 / 剧集 / 游戏），**不是**这个 AU 的
  时代设定。时代 / 世界观（如「1660 复辟」「古希腊」「Rome 219 AD」）交给
  `logline` 卡片和「设定档案」承载，**不写进 byline**。历史向的 BayBay 角色，
  出处一律是他演的那部作品（多为 `Horrible Histories`）。
- **演员**：真人演员名，每个系列都要有。已知的：`Sam Rockwell`、`Guy Pearce`
  （Leonard Shelby / Memento，不是 Sam）、`Rodrigo Santoro`（Hector）、
  `BayBay`（即 Mathew Baynton，站内用昵称）。游戏角色（如 Alexios / Assassin's
  Creed Odyssey）没有真人演员，可省略演员段。不确定演员是谁 → 先问用户再写。
- **状态**：`ongoing` / `complete` / `oneshot`。
- `设定档案` 里角色名后面也加演员名：`<strong>Hector Escaton（Rodrigo Santoro）</strong>`。

## ⚠️ byline 里的「作品出处」必须是完整、准确的官方全名

出处作品名**必须核对成完整官方全名**，不能想当然用通称或简称。写新系列、
或顺手经过旧系列时都核一遍。

常见坑（都是被截短的）：

| ❌ 简称 / 通称 | ✅ 官方全名 |
|---|---|
| Three Billboards | Three Billboards Outside Ebbing, Missouri |
| Hitchhiker's Guide | The Hitchhiker's Guide to the Galaxy |

规则：
- 出处拿不准时**先查证再写**，别凭印象填一个短的，也别用这个 AU 的时代设定顶替。
- 极少数**纯原创、无任何出处作品**的 AU 才可以在 byline 用「设定 / 时代」占位；
  但只要角色有出处（哪怕只是客串一两分钟、如 Kris / Somebody to Love (1994)），
  就写那部作品。
- 出处只出现在 byline / 设定档案，**不进标题**（标题用角色名，见上文）。

## 系列「基调」卡片（`logline` 字段）

每个系列首页 front matter 都应有一个 `logline:` 字段——一句偏**客观、官方**的
「基调 + 讲什么」简介，1–2 句。模板（`_layouts/series.html`）会自动把它渲染成
封面图下方、章节目录上方的一张「基调 · Tone」卡片，样式随该系列 AU 配色自动明暗翻转，
**新系列写了就有，无需手动改模板**。

```yaml
logline: "一篇温暖治愈、慢热向的救赎故事。全镇都认定 Jason Dixon 是个莽撞暴躁的失败警察，只有你陪着他一点点卸下盔甲，找回那个连他自己都快忘了的、干净又柔软的人。"
```

**它和 hero 里那句 `c-hero__lede` 引言功能不同，别写重、别混淆：**

| | `c-hero__lede`（图上方） | `logline`（图下方卡片） |
|---|---|---|
| 功能 | 情绪钩子 | 官方简介 |
| 语气 | 感性、诗意、第二人称 | 客观、克制、点明基调 |
| 内容 | 一句戳心的画面 / 悬念 | 先说基调（温馨 / 暗涌 / 救赎…），再一句梗概 |
| 人称 | 常用「你 / 他」直接呼唤 | 描述性，像内容简介 |

写法要点：
1. **先点基调**（卡片标签就叫「基调」）：温馨治愈 / 暗涌 / 救赎向 / 科幻群像 / 轻喜…
2. 再用一句话说清「讲的是谁、什么故事」。
3. ⚠️ **同 summary，`logline` 值用 `"..."` 包裹，内部严禁 ASCII 双引号 `"`**
   （会截断 YAML、整篇 post 消失）。要引用就用中文「」或《》。
4. 不确定基调时可参考该系列的 `collection_desc` 和「关于这个系列」正文。

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

## 章节 `tags` 字段：mood 标签必须加

每篇章节 post 的 `tags:` 里必须包含 **1–2 个 mood 标签**，反映该章的情绪基调。
Mood 标签写在人物 / 系列标签之后，例如：

```yaml
tags: [Charles II, BayBay, AU, The Invisible Light, 暗涌, 悸动]
```

**可用的 mood 标签（共 9 个）：**

| 标签 | 情绪 | 适用场景 |
|------|------|----------|
| 缱绻 | 缠绵温柔，难舍难分 | 亲密日常、深情守候、温存时刻 |
| 思念 | 想念、惦记、距离感 | 分离、缺席、无法抵达 |
| 安放 | 安心落定，有所归处 | 关系确立、和解、平静结局 |
| 悸动 | 心跳加速，初见之感 | 初遇、第一次、被看见 |
| 暗涌 | 压抑的暗流，危险张力 | 禁忌、权力差、沉默的占有 |
| 炽恋 | 炽烈的爱欲与占有 | 激烈、失控、亲吻、占有欲爆发 |
| 絮语 | 轻声细语，日常絮叨 | 轻快番外、日常互动、温馨小片段 |
| 怅惘 | 怅然若失，带一点悲 | 遗憾、错过、未说出口 |
| 怀旧 | 回忆与留恋 | 回忆杀、过去时光 |

**选 mood 标签的原则：**
- 选 1-2 个最贴近该章「主要情绪」的标签
- 长系列里情绪会随剧情演变，每章单独判断，不要全系列用同一对
- Oneshot / Extra / 轻松番外一般选 `缱绻` + `絮语` 或 `悸动` + `缱绻`

**不要忘加！** 每次写新章节或 oneshot，生成 front matter 的同时就把 mood 标签加好。

---

## 新 AU 系列开坑 checklist

### 1. 创建系列首页 `series/<英文slug>/index.html`

复制任意一个现有系列的 index.html，改以下内容：

**Front matter 必填：**
```yaml
layout: series
title: "English Title · Character AU"      # 英文
permalink: /series/english-slug/           # 英文，与目录名一致
nav_active: "AU Story"
series_name: "English Title"              # 必须与章节的 series: 字段完全一致
logline: "先点基调（温馨/暗涌/救赎…），再一句梗概。客观官方，别和 hero 情感引言写重。内部严禁 ASCII 双引号。"
```

**Hero 里那句 `c-hero__lede` 情感引言、byline 片名要用官方全名**——详见前文
「`logline` 字段」「byline 里的片名」两节。

**若角色是 Sam Rockwell 本人演的，加：**
```yaml
sam_collection: true
collection_order: N           # 查现有最大值 +1
collection_eyebrow: "AU Story · Series"
collection_title: "English Title · Character AU"
collection_desc: "一两句钩子简介。"
```

**Hero 区块：**
- `<h1 class="c-hero__title">` → 必须是**英文**
- byline / lede 引语可以用中文

**内容区块（`c-sam-intro`）：**
- 第一个 article：`关于这个系列`，2-4 段，概述世界观与核心冲突
- 第二个 article（可选）：`设定档案`，人物 / 信物 / 关系动力学
- 全部写 HTML，**不是 Markdown**，不要用单独的 post

### 2. 章节 post front matter 完整模板

文件名格式：`_posts/YYYY-MM-DD-series-slug-chapter-N-title.md`

```yaml
---
layout: post
title: "Chapter N · 章节中文标题 — Series English Name"
categories: ["AU Story"]
date: YYYY-MM-DD
image: cover-image.jpg          # 可选，封面图文件名（大小写必须与实际文件一致）
series: "English Title"         # 必须与系列首页 series_name 完全一致，必须是英文
series_title: "English Title · Character AU"   # 用于顶部返回链接显示
series_order: N                 # 整数，章节排序（1 开始）
series_type: "Series"           # 固定值
chapter_type: "Chapter N"       # 显示在卡片眉头，如 "Chapter 1" / "Extra"
summary: "≤35字的钩子引言。"    # 必须 ≤35 汉字含标点
tags: [标签1, 标签2]
---
```

### 3. 新系列配色——先查画册

新建系列首页前，先查 `_data/sam_themes.yml`，看这个角色是否已有色卡。

```bash
grep -A 10 "id: <角色关键词>" _data/sam_themes.yml
```

**如果找到了**：直接用他的 `accent`、`bg`、`accent_cn`、`accent_en`、
`bg_cn`、`bg_en` 六个字段，复制到 `_data/au_palettes.yml` 的新条目里。
`accent_ink` 取 `accent` 值的 ~80%（手动暗一档），`text` 和 `muted`
照抄 sam_themes 里同一条目的值。键名用 `series_name`（英文，与 front
matter 完全一致）。条目末尾注明来源，例：
`# Jason Dixon · 色卡同源 sam_themes.yml id: dixon`

**如果没有**：告知用户，等他提供配色或手动新建条目，不要自己编颜色。

### 4. 三处必须完全一致的字符串

| 位置 | 字段 | 示例值 |
|---|---|---|
| 章节 post | `series:` | `"Tuning the Devil"` |
| 系列首页 | `series_name:` | `"Tuning the Devil"` |
| 系列目录名 | `series/<slug>/` | `series/tuning-the-devil/` |

任意一处对不上 → 章节列表为空或卡片不出现。

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

## ⚠️ 文中出现「文件 / 卡片 / 字条」→ 一律做成卡片组件

**硬性约定：只要正文里复现了一件「可以拿在手里读」的东西——公文、声明、
批复、证书、判决、通知、菜单、节目单、契约、录取通知，或是信件、明信片、
字条、便签、情书、便利贴、餐巾纸上的字、刻下的一行字——就不要用裸的
`**加粗**` / `> 引用` 呈现，改用下面两个卡片组件之一。** 新文章写到这类内容
时直接就用；发现旧文章里有，也顺手改过来。

样式在 `_sass/5-components/_extras.scss`，两个组件都用 AU 色卡令牌
（`$accent`/`$paper`/`$ink`…），**自动跟随该系列配色明暗翻转**，无系列的
文章则用站点默认色。直接在正文里写裸 HTML（kramdown 支持，参考已有的
`buzzfeed-56-things` 一文），前后留空行即可。

### 1. `c-decree`——正式 / 官方文件（圆形钢印 + 编号）

适用：公文、声明、批复、判决、通缉、证书、榜文等「盖章」气质的东西。

```html
<div class="c-decree" role="group" aria-label="官方声明">
  <div class="c-decree__seal" aria-hidden="true">
    <span class="c-decree__seal-top">机构英文名</span>
    <span class="c-decree__seal-star">★</span>
    <span class="c-decree__seal-bot">已 · 批</span>
  </div>
  <div class="c-decree__stamp">No. 001</div>        <!-- 左上角小钢印，可选 -->
  <h3 class="c-decree__title">官方声明</h3>
  <p class="c-decree__subtitle">副标题，可选</p>       <!-- 可选 -->
  <p class="c-decree__body">正文第一段。</p>
  <p class="c-decree__body">正文第二段。</p>
  <div class="c-decree__sign">
    <span class="c-decree__sign-label">落款</span>
    <span class="c-decree__signature c-decree__signature--cn">签名</span>
  </div>
</div>
```

签名是英文名就去掉 `--cn`（用花体），中文名保留 `--cn`（衬线，不斜）。

### 2. `c-note`——手写便条 / 信件 / 卡片 / 明信片（暖纸 + 和纸胶带）

适用：字条、便签、情书、书信、明信片背面、餐巾纸上的字、任何手写的东西。
比 `c-decree` 柔和，没有钢印。

```html
<div class="c-note" role="group" aria-label="便利贴">
  <span class="c-note__label">明信片 · 背面</span>    <!-- 眉标，可选 -->
  <div class="c-note__body">
    <p>第一行。</p>
    <p>第二行。</p>
  </div>
  <span class="c-note__sign">— 署名</span>            <!-- 可选；中文署名加 c-note__sign--cn -->
</div>
```

### 判断 formal 还是 note

- 有机构 / 盖章 / 官腔气质 → `c-decree`（哪怕是恶搞的「管理层批复」）。
- 私人手写、便条、信、明信片、贺卡 → `c-note`。
- 拿不准就问用户，或选更贴合语气的那个。

### 不要过度套用

只有「被复现出来、当作一件实物去读」的文本才套卡片。**下面这些不套**：
普通对白、歌词、每篇文首的 `> "..."` 双语题记、文末的回环式题记 / 尾声引语、
只在叙述里被转述而没有逐字复现的信件、环境里的门牌 / 标语一类背景文字。
拿不准时，宁可不套。
