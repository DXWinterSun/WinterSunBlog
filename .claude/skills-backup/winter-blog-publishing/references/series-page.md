# 系列首页（建 / 改 series/<slug>/index.html）

这是「B 类任务」。落点是一个系列首页文件 `series/<slug>/index.html`。本文件管两件事：**① 系列首页里的内容怎么写**（Hero + 设定总览 + 设定档案）；**② 怎么拉取、校验、产出精确替换交付给 Code**。交付物是「精确替换（找到 → 替换为）」的 Markdown，**不要把整份文件重写交给 Winter**。

## ⚠ 写在最前：系列首页的内容是 HTML，不是 Markdown

和 `_posts/` 文章正文（Markdown）**正好相反**——系列首页 `index.html` 里的设定区块（`<article class="c-sam-intro">`）和 Hero 区块**全部写 HTML**。另外：

- **不要单独建 post** 来放世界观 / 人物 / 设定（别建「Chapter 0」式 post，会混进章节列表）。
- **不要手写章节目录**——模板会自动生成。
- 语气与正文一致：中文、沉浸式，不是「简介型」介绍。
- 新建系列首页时，**先拉一个现成的同类系列首页当样板**（见下「四」），照它的整体骨架改文案，不要凭空捏结构。

---

## 一、Hero 区块

同一个 `index.html` 文件顶部的 Hero。模板（照填）：

```html
<section class="c-hero">
  <div class="c-hero__eyebrow">AU Story · Series</div>  <!-- 单篇用 Oneshot -->
  <h1 class="c-hero__title">English Title</h1>          <!-- 必须英文 -->
  {% include au-palette-strip.html %}
  <div class="c-hero__byline">
    <span class="c-hero__byline-rule"></span>
    <span class="c-hero__byline-text">角色名 · 影片名 · ongoing</span>
    <span class="c-hero__byline-rule"></span>
  </div>
  <p class="c-hero__lede">
    <span class="c-hero__quote">&ldquo;</span>
    一句中文引言，10-25字，是整个系列最核心的一句话。
    <span class="c-hero__quote c-hero__quote--end">&rdquo;</span>
  </p>
</section>
```

规则：
- `<h1 class="c-hero__title">` **必须是英文，绝不能写中文**（影响 Jekyll 路径生成，写中文会断链）。
- `c-hero__lede` 是整个系列的「灵魂句」，要压得住，**10-25 字**。
- `{% include au-palette-strip.html %}` 这行**原样复制，不要改动**。
- `c-hero__byline-text` 形如「角色名 · 影片名 · ongoing」；完结后改成 complete / 已完结（与 `series_status` 一致）。

---

## 二、设定总览（`<article class="c-sam-intro">` 区块）

设定写在 `c-sam-intro` 区块里，全 HTML。通常一到两个区块：第一个必须，第二个可选。

### 第一区块（必须）：关于这个系列

```html
<article class="c-sam-intro">
  <h2 class="c-sam-intro__heading">关于这个系列</h2>
  <p>第一段：时间/地点/世界观设定，2-3句。</p>
  <p>第二段：「你」的身份处境，以及与 AU 角色的关系起点。</p>
  <p>第三段（可选）：核心冲突或故事走向，不剧透结局。</p>
  <p class="c-sam-intro__closing">收尾一句话：核心张力或基调，是整个系列的「钩子」。</p>
</article>
```

写作要求：
- **2-4 段，总字数 200-350 字**。
- 最后一段**必须**用 `<p class="c-sam-intro__closing">`，是全区块的落点。
- 沉浸式中文，语气与正文一致，**不剧透具体章节情节**——只交代世界观和关系起点。

### 第二区块（可选）：设定档案

```html
<article class="c-sam-intro">
  <h2 class="c-sam-intro__heading">设定档案</h2>
  <p><strong>你｜身份标签</strong>　外貌/处境描述。性格特征。在这段关系里的位置。</p>
  <p><strong>角色名｜身份标签</strong>　外貌特征。性格。与「你」的关系动力学。</p>
  <p><strong>信物/背景设定（可选）</strong>　道具、地点、或贯穿全文的意象，说明其象征意义。</p>
  <p class="c-sam-intro__closing">用一句话写出两人之间的核心张力或终局暗示。</p>
</article>
```

写作要求：
- 每个条目格式：`<strong>名称｜标签</strong>　正文`——注意是**全角竖线「｜」**，`</strong>` 之后接**一个全角空格「　」**再跟正文。
- 每个条目 **50-100 字**，信息密度高，不要流水账。
- 「**你**」和「**AU 角色**」两条**必须有**；信物 / 背景条目可有可无。
- 最后同样用 `<p class="c-sam-intro__closing">`。
- AU 角色若是 Sam Rockwell 演的，眼睛默认榛色（除非该片另有设定）。

> 提示：写完用 `scripts/check_series_page.py` 自检字数、全角符号、closing 标签、hero 标题是否英文（见下「四」）。

---

## 三、新建系列首页的 front matter 字段

这份规范明确的字段如下；**其余结构照样板系列首页复刻**。

```yaml
series_name: "English Series Name"   # 纯英文 ASCII，与各章节 series 完全一致，否则断链
# 若主角是 Sam Rockwell 演的，加下面这组：
sam_collection: true
collection_order: N                  # 现有最大值 +1（先拉线上确认当前最大值）
collection_eyebrow: "AU Story · Series"
collection_title: "English Title · Character AU"
collection_desc: "一两句钩子简介。"
```

- `series_name` 等参与路径的字段只能 ASCII；`collection_title` 这类含中文的字段不参与路径，可放中文。
- `sam_collection: true` **只给 Sam Rockwell 本人演的角色**对应的系列加。

---

## 四、拉取并校验（动手前必做）

系列首页会随时间改动，务必以**当前线上**为准。

```bash
cd /home/claude
# 拉取要改的系列首页（<slug> 换成实际系列目录名）
curl -sL "https://raw.githubusercontent.com/DXWinterSun/WinterSunBlog/main/series/<slug>/index.html" -o live.html
cp live.html test.html

# 新建系列首页时：再拉一个同类现有系列首页当样板，照它的骨架写
curl -sL "https://raw.githubusercontent.com/DXWinterSun/WinterSunBlog/main/series/good-enough/index.html" -o sample.html
```

把改动用 `str_replace` 套到 `test.html`，然后：
- 跑内容自检：`python3 scripts/check_series_page.py test.html`（查 hero 标题是否英文、有无 au-palette-strip、lede 字数、「关于这个系列」字数、closing 标签、全角符号）；
- 核对 front matter 仍合法、`series_name` 与各章节 `series` 一致；
- 确认没误删 / 误改无关内容；若文件含内联 `<script>`，确认还能正常解析、不白屏。

---

## 五、部署 Markdown 模板

逐处给「找到 / 替换为」，提醒按原样匹配空白缩进，末尾附自检清单。

### 场景 ①：新建系列首页

````markdown
# 部署任务：新建系列首页 <英文系列名>
**新建文件**：`series/<slug>/index.html`
（<slug> 与 series_name 的小写连字符形式对应，且与各章节 series 字段一致。整文件新建，内容如下。）

```html
<完整的 index.html 内容——基于样板系列首页改写而成>
```

## 配套提醒
- 各章节文章里的 `series:` 必须等于本页 `series_name:`（<英文系列名>），一字不差。
- 若挂了 sam_collection，确认 collection_order 是现有最大值 +1，未与别的系列撞号。

## 完成后自检
- 系列页 /series/<slug>/ 能打开、卡片正常、不白屏。
- （若进 Sam 画册）画册里新系列露出、序号正确。
````

### 场景 ②：把系列标记完结

完结状态在**每章 front matter 的 `series_status`**（`ongoing` → `complete`）；Hero 的 byline 与系列首页若有状态展示位也一并改。

````markdown
# 部署任务：把 <英文系列名> 标记为完结

## 改动（章节 front matter）
对该系列**所有章节**的 `.md`：
**找到：** `series_status: ongoing`
**替换为：** `series_status: complete`
（或只在 Winter 指定的范围内改——按她的说法来）

## 改动（系列首页 Hero byline / 状态位）
**找到：** `series/<slug>/index.html` 里 `c-hero__byline-text` 中的「ongoing」（及其它状态文案）
**替换为：** 「complete」/「已完结」等对应文案

## 完成后自检
- 系列首页与归档页状态显示为「已完结」。
- 没有遗漏的章节仍写着 ongoing。
````

> 完结到底是「改全系列每章」还是「只改首页状态」，**以 Winter 的明确说法为准**；拿不准先确认范围再产出替换指令。

---

## 六、与 A 类的衔接

- 发一章故事 = A 类（产出完整 `.md`，跑 `check_post.py`）。
- 建 / 改系列首页（含写设定总览、改状态、画册露出）= B 类（本文件，写 HTML，跑 `check_series_page.py`）。
- 「建系列首页 + 同时发第一章」「写完结篇 + 标系列完结」这类组合：A 类成品 + B 类替换指令**两份分开给清楚**。
