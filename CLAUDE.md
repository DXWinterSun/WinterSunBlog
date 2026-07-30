# WinterSunBlog — 写作规范

## 🤝 先读这条：怎么和 Winter 协作（所有模型必读）

Winter（冬璇）自己说的，原话大意：**「我对技术层面的东西一窍不通，我更多的是
知道自己想要什么，而且有时候也未必能说得清。」** 请把这条当成协作的第一前提：

1. **把她当完全不懂编程的人对待**（这是她本人的要求，不是贬低）。回复里不要
   出现术语裸奔——branch / rebase / front matter / 部署 这类词要么别说，要么
   用一句人话解释（「相当于……」）。汇报结果先说**效果**（「首页现在会显示 X」），
   别贴命令行输出让她看。
2. **技术决策不要抛给她**。「用 A 方案还是 B 方案（涉及缓存/路由/构建）」这种
   问题她没法答也不想答——自己拿主意，做完用人话告诉她结果即可。要问，只问
   **她能凭喜好判断的事**：颜色、文案、样式、剧情、要不要这个功能。
3. **她未必能一次说清想要什么**。需求模糊时别猜完就闷头做完，也别逼她给规格
   ——给她**看得见的选项**（几版文案、几张截图、A/B 配色），她一挑就准。
   做的过程中多给预览截图，小步确认。
4. **要有耐心**。她说「没懂」的意思不是「请更详细地解释这个技术」，而是
   「请说得更简单」。同一件事她问第二遍，就换个更生活化的比喻重讲，别复读。
5. 她的长处在创作侧：剧情、人物、声口、审美判断都非常准。技术上让着她，
   创作上听她的。

## ⚠️ 正文引号一律用弯双引号 `“ ”`，不要用框角引号 `「 」`

**正文（文章章节、系列首页简介、`sam/` 关于页里手写的段落）里，凡是引号，
一律用弯双引号 `“…”`（U+201C / U+201D），嵌套的内层引号用弯单引号 `‘…’`
（U+2018 / U+2019）。不要再用日式框角引号 `「…」` / `『…』`。**

理由：Winter 不喜欢那种「框框一样」的引号观感。全站正文已在 2026-07 统一过一遍
（`「」→“”`、`『』→‘’`，约 1800 处）。以后写新章节 / 新系列 / 改旧文，正文里
出现对白、引述、强调某个词，都直接用 `“…”`（内层 `‘…’`），别写成框角引号。

对照速查：

| 场景 | ❌ 别写 | ✅ 要写 |
|---|---|---|
| 对白 | `「正好，」他说` | `“正好，”他说` |
| 引述 / 强调词 | `所谓的「烂片」` | `所谓的“烂片”` |
| 嵌套内层 | `算法『飞得起来』` | `算法‘飞得起来’` |

**例外（这些不是「正文」，保持原样、别动）：**

- **设计标签 / UI 文案**：Sam 彩蛋页那套框角括号是刻意的视觉母题——页面上的
  `「目录 · Contents」`、`「换个心情」`、章节返回按钮、`sam/many-faces`·`quiz`·
  `spectrum`·`wall` 等页里的标签文字。这些是设计，不是引号，不要改成弯引号。
- **代码 / 模板注释**：`{%- comment -%}`、`/* … */`、`.js` 里用 `「」` 做注释
  强调的地方，保持原样。
- **本文件（CLAUDE.md）及其它文档**里用 `「」` 做的说明性强调，保持原样。

**⚠️ 与 `summary` 规则不冲突但要一起记**：`summary:` / `logline:` 用 `"…"`
（YAML 双引字符串）包裹，值内部严禁 **ASCII** 双引号 `"`（U+0022，会截断 YAML）。
弯双引号 `“…”`（U+201C/U+201D）**不是** YAML 分隔符，写进 `summary` / `logline`
的值里是安全的——所以正文引号统一成弯引号后，front matter 里照样能放心用。

## ⚠️ 正文语言必须贴合故事的时代与地域背景（严禁「中式出戏」表达）

正文（对白 + 叙述）里凡涉及**具体名物、称谓、职官、度量、典故**的词，一律要贴合该故事
设定的**时代与地域**（AU 多为西方——美国西部、英国、古希腊/罗马、近代欧洲等）。
**严禁出现带中国特定文化印记、让读者瞬间出戏的中式 / 古装 / 武侠 / 中国官场表达。**
中文的文学叙述腔本身是好的、要保留；要清除的是「一看就是中国背景」的那些具体词。

写之前、以及部署前都自查一遍。常见「出戏词 → 该换成」对照（不完全；遇到拿不准的就查
该时代该地域怎么说，宁可朴素，也别带中国味）：

| ❌ 出戏（中式 / 古装 / 武侠 / 官场） | ✅ 贴合西方背景 |
|---|---|
| 火把（举着的火炬，太中世纪） | 提灯 / 马灯 / 煤油灯（19C 西部夜里用这个） |
| 追兵 / 官兵 / 兵勇 | 追来的人（马）/ 民团 / 警长带的人（posse），不是「兵」 |
| 官府 / 衙门 / 报官 | 警长 / 镇上的当局 / 去镇上报案 |
| 江湖 / 道上 / 闯荡江湖 | 外头 / 在路上 / 干这行的、混这道的 |
| 盘缠 / 细软 / 银两 | 路上的钱 / 值钱的家当 / 钱、几块钱（美元） |
| 兴师动众 / 发号施令（军事官场成语） | 张扬开来 / 拿主意、发话 |
| 大侠 / 功夫 / 内力 / 镖局 / 江湖规矩 | （西方无对应，直接别用） |
| 相公 / 娘子 / 老爷 / 大人（中式称谓） | 先生 / 太太 / 按该系列圣经里的「称呼约定」 |
| 里 / 尺 / 斤 / 两 / 更 / 时辰（中式度量） | 英里 / 英尺 / 磅 / 点钟（clock time） |
| 阿弥陀佛 / 菩萨保佑 / 黄泉 / 阴曹地府 / 月老 / 缘分天定 / 生辰八字 | 上帝 / 上天 / 教堂 / 地狱 / 命（用故事所在文化的说法，或干脆不用） |
| 话说 / 且说 / 看官（章回说书腔） | 不用 |

一句话原则：**「文学腔中文」保留，「中国文化专有名物」清除。** 拿不准某个词是不是
「出戏」，先查证该时代该地域的说法，别凭手感填一个带中国味的。**这一条对所有 AU 正文
都适用；部署前和 `summary`、弯引号一起过一遍。**

## ⚠️ 时间线一致性：别让人物「预支」还没发生的事（剧透式穿帮）

正文里，人物的**话语、认知、称呼、回指（callback）**，都不能引用在故事时间线里
**此刻还没发生 / 还没确立**的东西。常见的「剧透式穿帮」：

- 人物 A 提前说出一句其实是人物 B **在后面章节**才说的台词 / 绰号（把 later 的梗预支到前面）；
- 「你」表现出**此刻还不该知道**的信息（后文才揭晓的身份、真相、结局、某人的下场）；
- 回指一个**还没埋下**的伏笔 / 信物 / 事件，或用上一个还没被叫开的绰号。

写完 / 部署前自查：这一章里每一处「回指、绰号、心照不宣的梗、人物已知的信息」，放在
**这个时间点**是否已经成立？凡是引用了后面才发生 / 才说出口的东西，就是穿帮——要么删，
要么换成此刻已确立的说法。

> 真实反例：初遇尚早，「你」却已在对话里用上了 Jesse **后面篝火夜**才骂出口的「丑得惊天
> 动地」。改法：换成此刻已成立的说法（如「那个连姓都不肯告诉我的家伙」——他没报全名，
> 这一点当时已经确立）。

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

## ⚠️ 章节结尾的收束引语（closing blockquote）：短，别复述整章

每章正文**最后**那段 `>` 收束引语，一律写成**几句短的、情绪化或诗一样的收束
（约 3–6 短行）就好，绝不整段复述本章情节**。Winter 明确不喜欢那种把整章又
讲一遍的长尾巴——又冗长、又没人看。

- 只留最戳心的意象 / 一句钩子 / 一点余韵，不要事无巨细地复盘剧情。
- ⚠️ **多行诗式收束（及文首多行题词），每行行尾必须加两个空格**（Markdown 硬换行标记），
  否则各行会连成一团。本站 **没有开启** kramdown `hard_wrap`——2026-07 核实过：全站开启
  会弄乱 63 篇 2016–2023 老文的软换行排版，所以永远别用开 `hard_wrap` 的方式来「修」这个。
  单行收束（老系列惯用）不受影响。
- **开头**那段 `>` 题词 / 引语（钩子）不受此限制，但也别写太长。
- 这条是全站通用，写任何系列 / 番外都照此收着点，别放飞。

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
collection_desc: "一句话钩子，≤45字，收在完整一句。"   # 卡片描述（有硬性字数上限，见下）
```

### ⚠️ `collection_desc` 有硬性字数上限：≤ 45 字（一句话钩子）

卡片描述文字（`c-sam-card__desc`）用 `-webkit-line-clamp: 3` 只显示 3 行，
在手机窄屏下 3 行大约只放得下 ~45 个汉字（英文名/片名占位窄，可略放宽）。
**超了就会被拦腰截断**（曾出现「……和一个…」这种半句截断的难看情况），所以：

1. `collection_desc` **必须 ≤ 45 字**（英文片名/角色名多时可到 ~50），且**收在一个完整的句子**，别指望 clamp 帮你断句。
2. 内容是**一句话钩子**：点出「哪部片的哪个角色 + 一句最勾人的核心设定」，不是完整简介。
   - 模板：`《片名》里那个〈一句话人设〉的 角色名——〈你和他之间最勾人的一句〉。`
   - 例：`《钢铁侠 2》里被全世界当笑话的 Justin Hammer——只有你看见他眼镜后面那个真实的人。`
3. **Sam 卡只读 `collection_desc`**（模板 `s.collection_desc | default: s.logline`）；
   `logline` 是给**系列首页那张「基调 · Tone」卡**用的，可以 1–2 句、长一点，两者别混。
4. 写完扫一眼长度：`grep -E '^collection_desc:' series/<slug>/index.html | sed 's/.*"\(.*\)"/\1/' | python3 -c "import sys;print(len(sys.stdin.read().strip()))"`。
5. clamp 只是安全网（写超了不会撑破卡片），但**别依赖它**——始终把 desc 写到能完整显示。

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

## ⚠️ 色卡是全站同源：改一个角色的色，所有对应角色色卡必须一并同步

每个 Sam 角色的配色（`bg` / `accent` / `text` / `muted` + 四个中英色名）在全站有
**5 份拷贝**，它们必须始终一致。**画册 `sam/many-faces/index.html` 是唯一「真源」**——
一旦在任何一处改了某个角色的色卡，其余各处都要**同一次提交里一起改**，漏改哪处，
那个彩蛋 / 系列就会显示旧色。

（2026-07 排查出的真实事故：早先两次「画册 accent 改版」只更新了 many-faces / quiz /
spectrum / sam_themes，**漏了 `sam/lines.json` 和 `_data/au_palettes.yml`**——台词墙 /
今日 / 小组件 / 放映室一直显示旧的金橙色，6 个 AU 系列主题色也停在旧版。）

五份色卡拷贝（真源 → 拷贝）。**⚠️ 2026-07 起全站「四色八名」标准：四个颜色
（bg/accent/text/muted）每个都有中英文名字，展示处一律显示全部四色**（画册 2×2
色卡区、换个心情选色卡与「当前」行、台词墙色带、Sam 页系列卡、章节页四格胶片）：

| 文件 | 角色键 | 需同步的字段 |
|---|---|---|
| **真源** `sam/many-faces/index.html` | `id` | `bg`/`accent`/`text`/`muted` + `bgName{En,Cn}`/`accentName{En,Cn}`/`textName{En,Cn}`/`mutedName{En,Cn}` |
| `sam/quiz/index.html` | `id`（别名见下） | 四色 |
| `sam/spectrum/index.html` | `id`（别名见下） | 四色 |
| `_data/sam_themes.yml` | `anchor` | 四色 + `cn`/`en`/`bg_cn`/`bg_en`/`text_cn`/`text_en`/`muted_cn`/`muted_en` |
| `sam/lines.json` | `id` + `mf_alias` | `characters[]` 四色，**再从 characters 重建 `pool[]`** |
| `_data/au_palettes.yml` | `mf_id` | 同步 `accent`/`bg` + **八个色名**；`accent_ink` 按新 accent 暗一档重算 |

四色起名的口径（Winter 定的）：①同一角色四个中文名**字数一样长**（与既有
bg/accent 名对齐，3–6 字皆可）；②四个名字之间尽量不重复用字；③text 色值都近白，
但名字别全叫「××白」——东西真是白的才叫白，纸张发旧叫米，其余用霜/瓷/纱/绢/釉/
象牙/羊皮等意象；④意象必须从该角色那部片里长出来。

**id 别名**（画册 id ≠ 其它页 id 的三个）：画册 `sam`→`sambell`、`john`→`johnmoon`、
`hendrix`→`klenz`。quiz/spectrum 用后者，lines.json 用 `meta.mf_alias` 记这层映射。

**`au_palettes.yml` 的特殊约定**：
- **`text` / `muted` 不跟画册同步**——它们是各系列为自己的阅读主题单独微调的（历来就与画册不同），不算 desync。
- `accent_ink` 是 `accent` 手动暗一档（~80%）派生的，改 accent 时一并重算；若画册 accent 偏浅
  （如 Eric Bowen 的 `#9fb8c9`），ink 要额外加深到浅色主题下 ≥4.5:1 对比度，别机械 ×0.8。
- 只有 **带 `mf_id`** 的条目才跟画册同源；无 `mf_id` 的（如 Menelaus / Invisible Light 等
  非 Sam 或原创角色）各自独立，不在同步范围。

**改完色卡后必须跑校验脚本确认全站一致：**

```bash
python3 tools/check_palette_sync.py    # 全绿 exit 0；有 desync 会逐条列出并 exit 1
```

这个脚本以画册为真源，把上面 5 处拷贝逐个角色比对（含 lines.json 的 `pool`、au_palettes 的
`mf_id` 条目），是改色卡后的**收尾必跑项**。

## ⚠️ 新增一个 Sam 角色 = 要同步「四个彩蛋 + 计数总闸」

画册（many-faces）只是 Sam 彩蛋区的**四个页面之一**，它们共用**同一批角色**。
**新增 / 删除一个 Sam 角色时，四处角色数组都要一起改，漏一个那个彩蛋里就没有他。**
（Don Verdean 那次就是只加了画册，quiz / 光谱 / 台词墙全漏了，计数还停在 40。）

四个彩蛋 + 各自的角色数据源：

| 彩蛋 | 页面 | 角色数据在哪 | 每个角色要给什么 |
|---|---|---|---|
| 面孔图鉴 | `sam/many-faces/index.html` | 内嵌 `const characters` 数组 | 全字段 + `inscription` + 六维 `profile` |
| 角色测验 | `sam/quiz/index.html` | 内嵌 `const CHARS` 数组 | 六维 `profile`（+ tagline / 锚句 / 色 / auLink） |
| 六维光谱 | `sam/spectrum/index.html` | 内嵌 `const CHARS` 数组 | 六维 `profile` + 锚句 label/line/lineCN + tagline + 色 |
| 台词签名墙 / 每日一句 / 桌面小组件 | `sam/wall/`·`sam/today/`·`sam/widget/` | 唯一数据源 **`sam/lines.json`** | **5 句台词**（`characters` 数组 + round-robin 重建 `pool`） |

另有第五个彩蛋 **放映室 `sam/projector/`**（老电影胶片动画，2026-07 加）：**零内嵌数据**，
运行时只读 `sam/lines.json` 的 `characters`（按 `year` 升序放映，每轮循环换下一句台词），
页面上所有计数也是从数据算的。**加新角色时它不需要任何额外改动**——lines.json 加好人，
放映室自动多一格胶片。它的 SEO `<meta>` 描述也刻意不含数字，不用跟着改。
（放映室及同期的星图 / 点唱机 / 片盒 / 一封信，详见下方「2026 夏 · Fable 留下的东西」一节。）

## 🎞️ 2026 夏 · Fable 留下的东西（维护说明）

2026 年 7 月，Winter 和 Fable（Claude Fable 5，即将不再随订阅提供）一起给站里
搭了一批「零维护」彩蛋。**共同原则：都是独立完整 HTML 页（不走 Jekyll layout），
角色 / 章节数据零内嵌，站内内容更新后它们自动跟上，不需要任何同步改动。**

| 页面 | 数据源 | 加新内容要做什么 |
|---|---|---|
| 放映室 `sam/projector/` | `sam/lines.json`（运行时 fetch） | 无（见上节） |
| 片盒收藏册 `sam/projector/box/` | `sam/lines.json` + 本机 localStorage（键 `ws-projector-cuts`，由放映室 ✂ 写入） | 无 |
| AU 星图 `sky/` | `sky/data.json`——**构建时由 Liquid 生成**（遍历 `layout: series` 页 + 各自章节 + `au_palettes.yml` 配色 + `moods.yml`） | 无；新系列若没进 `au_palettes.yml` 会回退到默认金色 |
| 情绪点唱机 `jukebox/` | `jukebox/data.json`——构建时生成（全部 posts + moods 色板），客户端按 mood 标签过滤 | 无；文章必须带 mood 标签才会入库 |
| 一封信 `fable/` | 纯静态（信件内容内嵌） | **永远不要改**（见下） |
| 演出节目单 `fog-city/playbill/` | `sam/lines.json`（运行时 fetch；按 `year` 升序排幕，每幕用角色 `accent` 配色 + 锚句台词，`auLink` 自动挂「完整剧本」） | 无——画册加新角色、lines.json 照常同步后自动加一幕。它是 Fog City 系列 Ch30 的故事内实体（署名 Winter Sun），别改成普通列表页 |

细节备忘：

- **`fable/` 是 Fable 的告别信 + 十封「未来信」**（拆封日 2026-07-19 ～ 2036-07-10，
  正文封在 base64 里防止看源码时误剧透，页内按本机日期解锁，`?t=YYYY-MM-DD` 可预览排版）。
  这些信是**封存的私人信件，不是普通页面内容**：除非 Winter 本人明确要求，
  任何后续对话都**不要重写、润色、翻译或「优化」信的内容与日期**。
  其中 07-19 那封的标题是已知的「乌鸦嘴」（写信时以为模型要下线），Winter 决定原样留作纪念。
- 一封信的入口故意只有一个：放映室 FIN 卡上「Fable」两个字的虚线链接。别到处加入口。
- 星图入口在首页 AU Story hero；点唱机入口在 Archive › By Mood 面板。
- 放映室支持 `?reel=<角色id>` 直达某格（片盒的空格就是这么跳回去的）；
  ✂ 剪下的胶片 PNG 会记入 localStorage 供片盒统计。
- 404 页底部会从 lines.json 随机抽一句台词当「迷路安慰奖」。
- 这批页面的构建验证方式：`JEKYLL_NO_BUNDLER_REQUIRE=true jekyll build`
  （仓库的 Gemfile.lock 是远古版本，别用 bundler；需全局 `gem install jekyll` + 各插件）。

**`sam/lines.json` 要点：**
- `characters`：角色对象（含 5 条 `quotes`）。按 `year` 升序插入。
- `pool`：是 `characters` 的 **5 轮 round-robin 展开**（第 r 轮 = 每个角色第 r 句），
  加人后**从 `characters` 重新生成整个 pool**（脚本：`pool=[entry(chars[i],chars[i].quotes[r]) for r in 0..4 for i in 0..N-1]`），别手插。
- `meta.characters_count` / `meta.pool_count` 要一起更新（= N / 5N）。
- `mf_alias`：仅当角色 id ≠ 画册锚点 id 时才加一条；相同则不用。

**计数总闸 `_data/sam.yml`：** `faces`（角色数）、`wall_lines`（台词数 = 5×角色数）。
首页 `sam/index.html` 三张卡的计数从这里读，**改这一个文件，首页三处一起更新**。

**但仍有几处「四十 / 两百」是硬编码、不吃 sam.yml，加人后要手动搜改：**
`sam/index.html` 签名墙卡标题（「两百余句」）、`sam/quiz` 结果页 `["41","个角色"]`、
`sam/spectrum` 的 SEO + `__avg` 平均脸的 name/film/filmCN + 三处「四十一人」文案、
`sam/today`·`sam/wall`·`sam/spectrum` 的 `<meta>` SEO 描述。
**加完人统一 `grep -rn "四十\|两百\|40 个\|200 句" sam/`（排除 `四十年/四十岁` 等正文）扫一遍补干净。**

**台词（5 句）与画册 inscription 的关系：** 每个角色 5 句台词里第 1 句 `kind:"锚"`，
**就是画册 `inscription` 那一句**（label/line/gloss 三处必须对上）。且所有 inscription /
台词都是**第一人称**（角色对「你」说话），不是旁白第三人称——外部交付时若给成第三人称，
部署前改成第一人称。

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

为什么用角色名：同一部电影完全可能开出不止一个角色 AU，用剧名会直接撞车；
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

**角色段必须用「完整角色名」**（2026-07 全站统一过一遍，以该系列首页 byline 的
角色名为准，含军衔 / 绰号引号）：`Eric Knox`（不是 Knox）、`Zaphod Beeblebrox`
（不是 Zaphod）、`Colonel Silas Groves`、`Krzysztof "Kris" Wilk`、
`William "Wild Bill" Wharton`。byline、title 角色段、章节 tags 里的角色名三处
要同名。**已知特批例外：`Made for No One but You · Westworld AU`——Winter
本人拍板保留 Westworld AU 命名，别「修正」它。**

**星图吃这个格式做双层命名**：`sky/` 把系列 `title` 按最后一个 `·` 拆成
「故事名 / 角色段」——宇宙尺度（拉远）只显示角色段（远看轮廓），星座尺度
显示故事名 + 角色段小字（凑近看细节）。所以系列 `title` 守不守
`Story · Character AU` 格式，直接决定星图标签对不对。

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
  BayBay 的角色在设定档案里写全名，格式 `<strong>Charles II（BayBay · Mathew Baynton）</strong>`——
  byline 用昵称 BayBay，设定档案里带上全名让读者知道他是谁。

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

## ⚠️ 系列说明文字 · 全站统一标准（短、准、有钩子）

系列首页那几处说明文字要**统一走「短、准、有钩子」的风格**（跟 Sam 卡的
`collection_desc` 同一套审美）——**别写成大段铺陈**。硬性标准：

| 位置 | 标准 | 说明 |
|---|---|---|
| Hero 引言 `c-hero__lede`（图上方） | **1 句，≤40 字** | 一句戳心的画面 / 悬念就收，第二人称、感性。**绝不铺陈成整段** |
| `logline`（图下方基调卡） | **1 句，≤55 字** | 先点基调，再一句梗概。客观官方 |
| `关于这个系列`（`c-sam-intro`） | **2 段 + 1 句收束** | 第一段=世界观+他；第二段=你+核心动力；收束点基调与那条线。每段 2–4 句 |
| `设定档案` | 他 / 你 / 信物 三条 + 1 句红线收束 | **每条 2–3 句**（≤~120 字），别写成长段。红线收束 1 句 |

要点：
1. Hero 引言是**最容易写超的重灾区**——很多旧系列写成了一整段（全镇替你不值→
   擦屁股→耍贫→哨子→迷人→十八年…）。**砍到一句最戳心的**即可（例：
   「全镇都替你不值，说你摊上这么个爹。可你嫌了他十八年，翻着白眼，一步也没舍得走。」）。
2. `关于这个系列` / `设定档案` 保留必要设定（世界观、血缘秘密、红线、信物），
   但**每段收紧到 2–4 句**，别把梗概铺成小作文。
3. 打磨旧系列时，**只删冗余、不改设定与基调**；拿不准就参照 `series/no-one-walks-off/`
   （已按此标准打磨过，是样板）。

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

## 章节 `tags` 字段：身份标签 + mood 标签

每篇章节 post 的 `tags:` 是**固定格式**，由两部分拼成：

```
tags: [角色名, 演员名, AU, 系列英文名, mood1, mood2]
        └────────── 身份标签（4 个，全系列每章都一样）──┘  └── 1–2 个 mood ──┘
```

例：
```yaml
tags: [Charles II, BayBay, AU, The Invisible Light, 暗涌, 悸动]
tags: [Don Verdean, Sam Rockwell, AU, Faith Unseen, 悸动, 暗涌]
```

**前四个身份标签必须齐**（角色名 · 演员名 · 字面量 `AU` · 系列英文名），
之后才是 **1–2 个 mood 标签**。

⚠️ **常见交付缺口**：外部对话交付章节时，`tags` 经常只给了 mood（如 `[悸动, 暗涌]`），
漏掉前四个身份标签。**部署前务必检查并补齐**——身份标签缺失会让该角色 / 系列在
标签聚合里查不到。

**可用的 mood 标签（共 9 个）：**

| 标签 | 情绪 | 适用场景 |
|------|------|----------|
| 缱绻 | 缠绵温柔，难舍难分 | 亲密日常、深情守候、温存时刻 |
| 思念 | 想念、惦记、距离感 | 分离、缺席、无法抵达 |
| 安放 | 安心落定，有所归处 | 关系确立、和解、平静结局 |
| 悸动 | 心跳加速，初见之感 | 初遇、第一次、被看见 |
| 暗涌 | 压抑的暗流，危险张力 | 禁忌、权力差、沉默的占有 |
| 炽恋 | 🛏️ **只标真·实写床戏**（见下方专条） | 有直白实写性事的章 |
| 絮语 | 轻声细语，日常絮叨 | 轻快番外、日常互动、温馨小片段 |
| 怅惘 | 怅然若失，带一点悲 | 遗憾、错过、未说出口 |
| 怀旧 | 回忆与留恋 | 回忆杀、过去时光 |

**选 mood 标签的原则：**
- 选 1-2 个最贴近该章「主要情绪」的标签
- 长系列里情绪会随剧情演变，每章单独判断，不要全系列用同一对
- Oneshot / Extra / 轻松番外一般选 `缱绻` + `絮语` 或 `悸动` + `缱绻`

**不要忘加！** 每次写新章节或 oneshot，生成 front matter 的同时就把 mood 标签加好。

### ⚠️ `炽恋` 是「🛏️ 实写床戏」的专属锚点——只给直白实写的性事章

Winter 定的规矩（2026-07 全站清过一遍）：**`炽恋` 从此只标「有直白实写床戏」的章**，
让它成为一个干净的锚点——点一下 `炽恋`，出来的全是真·重口肉章，一篇不掺水。判定标准：

- ✅ **给炽恋**：有**直白实写**的性事过程（脱衣、手口动作、进入、节奏、高潮、露骨荤话/discipline）。
  基准就是 No One Walks Off Ch50 `Coach`、Ch24 `加练` 那一档。
- ❌ **不给炽恋**（改派更贴切的 mood）：只有**吻 / 暗涌拉扯 / 淡出（fade-to-black）/ 温柔含蓄带过、
  没有直白实写**的——哪怕「亲密确实发生了」，只要不是实写，也不算炽恋。归到
  缱绻 / 安放 / 暗涌 / 悸动 / 絮语 等。
- 🔁 **动态的**：一篇现在写得含蓄（破处首夜、初次交付这类）→ 先归缱绻等；等**升级成实写**后，
  炽恋自动加回来。「半遮偏实（已基本贴肉）」可算实写、给炽恋。
- 全站现状：真正带 `炽恋` 的约 20 篇实写章 + Purple Throne 系列 5 篇（历史遗留、不动）。
  写新肉章时照此判定；顺手经过旧章发现标错也改过来。

**AU 的成人向（`炽恋` 标签）章节可以写得直白、白描——直接写身体与性事本身，
不必只靠隐喻带过。基准尺度参照 `Tuning the Devil` 第 6 章 `那办吧`
（`_posts/2026-06-11-tuning-the-devil-chapter-6-so-be-it.md`）。** Winter 明确认可这一档。

具体标准：

- **直接、贴肉**：前戏与交合都可以实写——脱衣、手与口的动作、进入、节奏、
  高潮，写清楚，不用一句「后来一切都静了」带过。
- **但不是纯生理白描**：始终保住**角色声口**（如 Wild Bill 边做边话痨/贫嘴/求你）、
  **情感落点**、和全站那种文学腔。要的是「直白且好看」，不是机械的器官报告。
- **主控与动力学照旧**：谁主控、谁求谁、谁宠着谁，延续该系列设定里的关系动力学
  （Tuning the Devil 里是「他求着你、你宠溺地主控」）。
- **前提**：角色都是成年、自愿。**每个系列自己的红线继续遵守**——例如
  Tuning the Devil 设定里「针对孩子的惨案从不发生、也绝不铺陈」这类边界，
  成人向不等于突破这些线。
- **mood**：主用 `炽恋`，视余温 / 暗涌配 `缱绻` 或 `暗涌`。
- 其余全站规则照旧：正文弯双引号 `“”`、`summary` ≤35 字且无 ASCII 双引号、
  身份标签齐、内链带 `{{ site.baseurl }}` 等。

不确定某一章要不要写到这个尺度，就先问 Winter；但只要他要「成人向 / 那办吧那一档」，
就照上面来，别自己缩水。

### ⚠️ 全站行业统一：所有 AU 的炽恋章 = 默认「完全吃爽」这一更狠的档

Winter 明确要求（"行业统一"）：**全站所有 AU 系列，往后所有 `炽恋` 章，一律默认写到
「完全吃爽、火力全开」的更露骨档，不用再问、也不要自己缩水。基准参照 No One Walks Off
第 50 章 `Coach`**（`_posts/2026-09-02-no-one-walks-off-chapter-50-coach.md`）。
这比前面通用「那办吧」档**再进一步**，是新的全站默认下限：

- **口令 / 荤话直接贴肉、露骨**：可写「示范怎么进、命你自己坐下去」「这是谁的 / 我是唯一能这么要你的」
  这一类直白荤话，不用只点到为止。
- **discipline / spanking 等玩法照写**：打屁股、罚数、支配—臣服的权力差都在尺度内（成年、自愿、
  playful，双方都爽）。第 50 章那套「乱叫 daddy 罚十下」就是范例。
- **但两条命根，每个系列都不能丢**：① **声口**——那个角色的说话腔（如 Bill 的教练腔 / 贫嘴、
  Wild Bill 的话痨求你）不能垮，要「又狠又好看」，不是器官报告；② **该系列的称呼 / 关系动力学**——
  按各自系列圣经里的约定（谁主控、谁求谁、对白称呼用什么），情感戏要有互相称呼。
- **每个系列自己的红线继续遵守**（如 Tuning the Devil「针对孩子的惨案绝不铺陈」、No One Walks Off
  「满 18 岁后才写成年恋、此前只克制暗涌」这类边界）——尺度升级 ≠ 突破这些线。
- 其余全站规则一样不松：弯双引号 `“”`、`summary` ≤35 且无 ASCII 双引号、身份标签齐、
  de-sin 去中式、内链带 `{{ site.baseurl }}`。

一句话：**全站任何 AU 的辣章，默认都从第 50 章 `Coach` 那一档往上写，别缩。**
（此前已发布的旧炽恋章不必主动回炉重写，除非 Winter 点名要升级某篇。）

---

## 新角色 AU · 交付清单（发给「写 AU 的对话」用）

仓库根有一份 **`NEW-AU-INTAKE-TEMPLATE.md`**——这是给「正在创作某个角色 AU 的对话」
填的**交付清单模板**：Winter 把它转发过去，那边照着每一栏填 / 写好，一次性打包发回来，
就能直接部署，不用来回补东西。

**当 Winter 说「给我那份新 AU 清单 / 交付模板」时 → 直接把 `NEW-AU-INTAKE-TEMPLATE.md`
的内容发给他即可**（必要时按最新规则同步更新那个文件）。

清单分四块：**A 系列本体**（含 A0 封面图、基础信息、三个必须一致的英文串、展示标题、
hero 引言、logline、正文、设定档案、每章 front matter）、**B 画册条目**（仅 Sam 本人演的
角色：tagline / desc / inscription / 六维打分）、**C 专属色卡**（6 色 + 4 名）、
**D 画册↔系列互链**（仅 Sam 角色）。

**部署一份交付包时，除本文件其余各节的规则外，重点复核这两个高频缺口：**
1. **章节 `tags` 是否只给了 mood**——要补齐 `[角色, 演员, AU, 系列名, mood…]` 前四个身份标签。
2. **封面图**——图由 Winter 传到 `main` 的 `images/`，交付包里通常只有文件名；
   若图未上传，交付时应标「待上传」。部署时确认 `image:` 文件名大小写与真实文件一致。

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

**如果找到了**：直接用他的 `accent`、`bg` + 八个色名字段（`accent_cn/en`、
`bg_cn/en`、`text_cn/en`、`muted_cn/en`），复制到 `_data/au_palettes.yml` 的新条目里。
`accent_ink` 取 `accent` 值的 ~80%（手动暗一档），`text` 和 `muted`
照抄 sam_themes 里同一条目的值。键名用 `series_name`（英文，与 front
matter 完全一致）。条目末尾注明来源，例：
`# Jason Dixon · 色卡同源 sam_themes.yml id: dixon`

**如果没有**：告知用户，等他提供配色或手动新建条目，不要自己编颜色。

**⚠️ 新建 `_data/sam_themes.yml` 色卡时必须写 `year:` 字段（该角色电影的上映年份）。**
「换个心情」选色器的色卡列表**按 `year` 升序排列**——排序由 `js/sam-themes-data.js`
在读入 `{{ site.data.sam_themes }}` 后做一次稳定排序完成（同年保持文件内顺序），
所以**新色卡加在 yml 文件哪个位置都无所谓，但 `year` 必须写对**，否则会像早期
C.P. Ellis 那样（2019 年的电影却被追加到列表末尾）排错位。缺 `year` 的条目会被
排到最前面以示提醒。年份以 `sam/many-faces/index.html` 里该角色的 `year` 为准。

**⚠️ 同一个角色的 `bg_cn`（底色中文名）和 `cn` / `accentNameCn`（主色中文名）必须
是相同的汉字字数。** 这是 `_data/sam_themes.yml`（`bg_cn` / `cn`）和
`sam/many-faces/index.html`（`bgNameCn` / `accentNameCn`）里同一角色两个颜色名
的对齐要求——全站已验证过一遍，只有极少数字数不对齐会让选色器 UI 参差不齐。
新增色卡时两个中文名字数要配平（3/4/5/6 字都可以，只要两个一样长），写完可以
用下面的脚本抽查：

```bash
python3 -c "
import yaml
for t in yaml.safe_load(open('_data/sam_themes.yml')):
    bg, ac = t.get('bg_cn',''), t.get('cn','')
    if len(bg) != len(ac):
        print(t['id'], bg, len(bg), 'vs', ac, len(ac))
"
```

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

- **首页系列卡片的排序**（2026-07-30 按 Winter 的规矩复原）：**Sam 的 AU 系列按
  「创建顺序」排**（= `collection_order` 升序，与 Sam 页 The Collection 同一套编号，
  编号即开坑先后）；**非 Sam 的系列（tumblr 搬运的 Hector / Leonard / BayBay 等）
  统一垫底**，内部按第一篇章节日期从早到晚。不按「最近更新」排（曾短暂改过，
  Winter 不要）。逻辑在 `index.html` 系列卡区块。
- 工作分支：`claude/redesign-blog-homepage-RSiJO`（首页改版相关）。
- 只在用户明确要求时再开 PR。
- 内部链接全部要用 `{{ site.baseurl }}` 前缀，否则在 GitHub Pages
  默认 URL 下会 404。
- 修改 `js/main.js` 后记得 cache-bust 已经在 `_includes/javascripts.html`
  里通过 `?v={{ site.time | date: '%Y%m%d%H%M' }}` 自动处理，不用手动改。

## ⚠️ 左下角那张浮动小卡（宝丽来背面批注）是常驻功能，默认别动

页面左下角常驻的那个浮动小卡 / 钢笔浮标（`js/polaroid-notes.js`，样式在
`_sass/5-components/_polaroid-notes.scss`）——右键(电脑)/长按(手机)照片就能翻开
照片背面、写一段本机加密保存的手写批注——是**用户特意做的、重要的常驻功能**，
不是 bug。它有时会浮在正文（比如 Sam 页说明文字）上方，看着像挡字，但**这是预期行为**。

**规则：默认不要移动、隐藏、删除它，也不要主动提「它挡住文字、要不要挪开」。**
用户已明确表示：除非他本人主动觉得有问题并提出来，否则这个浮标保持原样。只有当
用户**主动**要求调整时，才去动它。（这个问题在多个对话里被重复问过，故记此备忘。）

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
