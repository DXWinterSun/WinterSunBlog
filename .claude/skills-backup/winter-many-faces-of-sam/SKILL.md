---
name: winter-many-faces-of-sam
description: 维护 Winter 的「Many Faces of Sam」角色画册（网页位于仓库 DXWinterSun/WinterSunBlog 的 sam/many-faces/index.html）。当 Winter 想往画册里新增或修改一个 Sam Rockwell 角色、提到「加进画册 / 加个角色 / 画廊 / many faces / 人物卡 / 这个画册」，或想得到一份「发给 Claude Code 就能部署到网页」的 Markdown 时，必须使用本 skill。即使 Winter 只是在描述一个新角色的设定想法、还没明说「做成画册条目」，只要落点是这个画册，也应使用本 skill 中的全部规范。本 skill 同时规定了角色卡的数据结构、第二人称文案口吻、六维雷达校准、配色命名，以及「先在本地按线上文件验证、再产出精确替换指令」的部署流程。
---

# Many Faces of Sam · 画册维护

这是 Winter 的私人项目：一个用 React（Babel in-browser）写成的单文件画册，收录 Sam Rockwell 演过的角色，每个角色一张沉浸式卡片，并配一张六维雷达图。所有卡片文案都以第二人称「你」写成，这个「你」指 Winter 本人。

- **目标文件**：`sam/many-faces/index.html`
- **仓库**：`github.com/DXWinterSun/WinterSunBlog`（线上：dxwintersun.github.io/WinterSunBlog）
- **线上 raw 地址**（用于拉取与校验）：
  `https://raw.githubusercontent.com/DXWinterSun/WinterSunBlog/main/sam/many-faces/index.html`

## 三条铁律

1. **永远不要把整份 `index.html` 重写后交给 Winter。** 她的部署方式是：你产出一份「精确替换（找到→替换为）」的 Markdown，她复制后发给 Claude Code，由 code 改她的仓库。最终交付物永远是这份 Markdown，不是整份文件。
2. **动手前先拉取「当前线上文件」并以它为准。** 这份文件会在不同对话之间被改动（例如某个角色被扩写、加了新字段）。绝不能凭上一次的记忆写替换指令。
3. **交付前必须本地验证**：把改动套到线上文件的副本上，跑通「数据解析 + JSX 编译」，并确认没有误伤其它角色。细节见 `references/deploy-workflow.md`。

## 总流程

1. 跟 Winter 把这个角色聊清楚：他是 Sam 哪部片里的角色、年份、中文译名、性格基调、和「你」的关系走向、有没有专属的小细节（爱称、习惯、某句话）。
2. 拉取当前线上文件，**读几条已有角色**，感受文案口吻、配色取值、六维分布，让新角色在整组里坐得自然。
3. 起草这个角色的卡片数据对象（字段见 `references/character-schema.md`）与文案。中文译名拿不准就先查（豆瓣/通用译名），查不到就拟一个忠实译名并跟 Winter 确认。
4. 想清楚要不要给他「特别」标记（见下「特别标记」一节）。
5. 把改动套到线上文件副本上，按 `references/deploy-workflow.md` 校验。
6. 产出部署 Markdown，交给 Winter 发 code。

## 文案的口吻与硬规范

`tagline` 和 `desc` 都是沉浸式第二人称「你」，这个「你」=Winter 本人。

- **不出现任何原片女主角的名字**（例如写 Krzysztof 时不要提 Mercedes）。
- **不出现 Winter 自己的名字。**
- **氛围优先于剧情还原**：写的是「爱上他这个版本」的感觉，不是剧情复述。
- `desc` 一般 2–4 段，**收尾用一句「你们的爱是……」**作总括（这是画册的统一收束句式）。
- `tagline` 是一句戏内的钩子，短而有画面。
- **Sam Rockwell 角色的眼睛默认榛色（hazel）**，除非该片明确另有设定。
- 影片标注：`filmCN` 用《中文译名》。

## 六维雷达（简）

六个维度（雷达标签顺序固定）：狡黠 guile / 隐忍 forbear / 疯狂 chaos / 璞真 raw / 浪漫 romance / 优雅 grace，取值 0–10 整数。
**相对整组校准**：先看几条已有角色的数值再给新角色打分，让他在群像里的位置合理（例如 Matty raw 9、Buck raw 10 是「野」的极端；Gary grace 6 是「体面打磨」的那一类）。各维度含义见 `references/character-schema.md`。

## 配色

每条有 `bg`（深背景）/`accent`（标志色）/`text`（浅文字）/`muted`（次要灰），外加 `bgNameEn`/`bgNameCn`/`accentNameEn`/`accentNameCn` 四个配色名。配色名走「意象+颜色」的路子（如「黄昏铜 / Dusk Bronze」「月光银 / Moonlight Silver」）。**两个配色名之间不要重复同一个词**（Krzysztof 那次就因为 "Cardinal" 出现两次而改了背景名）。

## 排序与插入位置

`characters` 数组按 `year` **从小到大**排列。新角色插在「第一个年份 ≥ 它的角色」之前（即按时间顺序就位）。页脚的年份范围与目录序号都是自动计算的，**不需要改任何计数或范围**。

## 「特别」标记的处理哲学（突出但不突兀）

当某个角色对 Winter 而言不止是一个普通电影角色（例如：从一个几乎没名字的龙套扩写出来的、或格外私人的），用画册**本来就有的视觉语言**去标记他，而不是发明突兀的新 UI——这样「认得出是同一套设计」，又只属于他。可用的可选字段：

- `namePostfix`：大标题后的小灰字（标他原本的身份）。
- `roleNote`：目录那行片名后追加「· 内容」（标龙套角色名）。
- `inscription`：一块独有的「── 标签 ──」小区块（放一句只属于他的话，例如他母语里的一句）。
- `auLink`：若他有专门的连载页，挂「AU · STORY · 进入系列 ↗」。

**已实现的范例：Krzysztof "Kris" Wilk**（Sam 在《去爱那个人 / Somebody to Love》1994 里那个连名字都没有的「Polish Guy」扩写而来）——用了 `namePostfix:"Polish Guy"` + `roleNote:"Polish Guy"` + 一块波兰语 `inscription`。完整对象见 `references/character-schema.md`。

> 注意：`namePostfix` 已被 Sam Bell（Moon）用来显示 "(pl.)"。所以目录里的「· 角色名」**必须**走独立字段 `roleNote`，不能复用 `namePostfix`，否则会误改 Sam Bell。任何要在渲染里基于某个可选字段做判断的改动，**先 grep 线上文件**看有没有别的角色已经在用它。

## 参考文件

- `references/character-schema.md` —— 完整字段表（必填+可选）、六维含义与校准、配色约定、Krzysztof 完整范例对象。
- `references/deploy-workflow.md` —— 拉取与校验的具体命令、部署 Markdown 的模板、各可选字段对应的渲染片段（JSX）。

新增角色通常只是往数组里插一条数据；只有当 Winter 想要某种**全新的呈现效果**（新的卡片元素）时，才需要照 `deploy-workflow.md` 里的渲染片段去加对应的渲染分支。
