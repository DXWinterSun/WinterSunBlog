---
name: winter-au-illustration-prompt
description: 维护 Winter 给博客 AU 连载章节（以及其它 Sam Rockwell 同人需求）写「AI 作图 prompt」的整套规范——她在 Gemini 等工具里生成插画，Claude 负责产出可直接粘贴的 prompt（不是图本身）。当 Winter 想给某个 AU 系列/章节配图、说「配图 / 作图 / 画一张 / 写个 prompt / 给我作图指令 / 章节插画 / 博客配图 / Gemini 画 / 生图」，或在调一张已经生成的图（脸不像、手画反、被拒绝、画面文字不对、冷暖不对）时，必须使用本 skill。即使 Winter 只是描述一个想画的画面、还没明说「写成 prompt」，只要落点是给她的同人/AU 配图，也应使用本 skill 的全部规范。本 skill 固化了：复古水彩默认画风、人物块+风格块+场景块的锁定模板、第一视角（手绘里 Winter 画成长发女生）、用「画面方位」根治左右手画反、私密室内被安全过滤拒绝时的改写阶梯、画面内指定文字（如波兰语）的写法、横屏 16:9、以及打包成可粘贴 markdown 文件主动交付的流程。
---

# AU 配图 · 作图 Prompt 规范

Winter 在 Gemini（或类似工具）里生成插画，**Claude 的产出物是「可直接粘贴的 prompt」，不是图**。主要用途：给她 WinterSunBlog 上的 AU 连载章节配图（每章一张专属图），偶尔也给其它 Sam Rockwell 同人图写 prompt。

最终交付物：**一份 markdown 文件**，每章/每张一条**完整自包含、可直接粘贴**的 prompt，用 `present_files` **主动**递给她（对齐她博客交付的习惯，不用等她开口要）。

## 总流程

1. 搞清楚要配图的是哪个系列 / 哪几章。需要章节内容时，**先去拉取博客系列页或章节正文**，按真实剧情挑每章最适合入画的「那一个瞬间」，别凭记忆瞎猜。系列页一般在 `https://dxwintersun.github.io/WinterSunBlog/series/<slug>/`，可直接 `web_fetch`。
2. 给每章提一个**入画方案**（一句话：画面是什么、为什么贴这章），让 Winter 过目调整后再动手写 prompt。
3. 选定画风 → 锁定人物块/风格块 → 逐章只换场景块，写出整套 prompt。
4. 打包成 markdown 文件，主动 `present_files`。
5. 她生成后把图发来，按下面各节的要点**逐张微调那一条 prompt**（脸、手、过审、文字、冷暖）。

## 默认画风：复古水彩 / 绘本

写实人脸在 AI 生图里最不稳、最容易崩（五官扭曲、神情怪）。**默认走复古水彩 / 绘本插画风**——稳、好看、氛围足，是和 Winter 验证过的首选。风格块（锁定，整套一字不差复用）：

> Retro watercolor and gouache illustration, soft color washes, gentle paper-grain texture, hand-painted storybook feel, slightly faded vintage palette. Horizontal 16:9 landscape.

可选画风（Winter 想换时再用，整套统一、别混）：厚涂 / 图像小说（氛围浓、偏写实比例）、日系赛璐璐（线条干净、人物最稳）、美式老卡通（黑白橡皮管，极稳但偏喜剧，不适合言情）。

## 锁定模板：人物块 + 风格块 + 场景块

一个系列的多张图要像「同一个人、同一个世界」，靠的是**锁定**：

- **人物块**和**风格块**整套**一字不差地复用**；
- 每章**只换场景块**（地点、动作、光线、氛围、配色）；
- 每条 prompt 都把三块**焊在一起、自包含**，让 Winter 一条一粘即可，不用自己拼；
- 系列内让**配色在两三种基调间来回摆**（如 The Cardinal 的余烬绯红 ↔ 华沙墨蓝），中间穿插冷晨光、暖金等，十张挂一排才有情绪起伏。

**Kris 人物块（已验证，可直接复用）**：

> a young man in his mid-twenties resembling actor Sam Rockwell in the mid-1990s: boyish face, tousled sandy-brown wavy hair, hazel eyes, a slightly crooked smile, lean build, a simple dark shirt with rolled-up sleeves, a small silver cross at his throat（受伤章节再加：, his injured left hand wrapped in a white bandage）

要点：

- **写上演员名**（"resembling actor Sam Rockwell in the mid-1990s"）+ 详细五官，Gemini 反而画得更像，别因为「真人名怕被拒」就删——Winter 的实测是带名更像、也能出。
- 眼睛**默认榛色 hazel**（Winter 所有 Sam 角色通则）。
- 给别的 Sam 角色配图时，把人物块换成**对应片中年代**的外形描述，眼睛仍 hazel。

## 第一视角与「你」

- AU 配图**默认第一视角**：镜头 = Winter 的眼睛，画面里**不出现她本人**（最多出现她自己的手）。代入感最强，prompt 里写 "First-person POV ... as if seen through the viewer's own eyes (the viewer is not visible)"。
- **手绘风里若必须让「你」入画**（比如改成「他的视角望着你」那种构图），直接把 Winter 画成一个**长发年轻女生**就行——她本人确认过这样可以，不必纠结露不露脸。其余情况仍守「不出现你本人」的默认。

## 左右手铁律：用「画面方位」，不要用身体左右

AI 对身体「左/右」经常分不清，**人物面对镜头时画面还会镜像**——他自己的左手落在**画面右侧**。只写 `left hand` 有一半概率画反。根治办法：

- **改说「画面的哪一边」**（the LEFT / RIGHT side of the image），别说身体左右；
- **给两只手各派明确、不同的活**，逼模型正确分配；
- **把镜像逻辑点破**：如「he faces us, so the bandaged hand on the RIGHT side of the frame is his own left hand」；
- 再加一句**否定**：「Do NOT place the bandage on the left side of the image.」
- **这条同样管 Winter 自己的手**（如握笔的手应在**画面右侧** = 她的右手）。
- 整套里把伤手 / 纱布**固定在画面同一侧**（默认画面右侧），十张更统一。

验证过的写法（贴进 prompt）：

> HAND PLACEMENT — follow the on-screen sides exactly: [好手在做什么] on the LEFT side of the image; the hand on the RIGHT side of the image is wrapped in a white bandage (his injured hand). He faces us, so the bandaged hand on the RIGHT side of the frame is his own left hand. Do NOT place the bandage on the left side of the image.

（人物侧身/背身/远景时左右不像正对那么死板，可不强行钉方位。）

## 过审：私密室内 + 人 + 言情，容易被拒

Gemini 安全过滤对「**私密室内场景 + 一个人 + 第一视角 + 言情/亲密氛围**」很敏感，会误判成暧昧内容而拒绝。公共/室外场景、纯物件场景几乎不会被拒。**改写阶梯**（从轻到重，按需往下走）：

1. **洗掉触发词**：`bed` / `bedding` / `lying in bed` / `intimate` / `tender` / `reaching toward you` → 换 cozy / warm / soft / fond / gentle；卧室写成 "dim room"、深夜亲密写成 "evening lamplight"。
2. **改构图，绕开「一个人正对你」**：
   - **陪读 / 并肩侧脸**：他坐你身边、你转头看他**侧脸**（three-quarter profile）——读起来是「陪伴」而非「对峙」，过审且更有温度；
   - **换成他的视角**：镜头 = 他在门口/桌边看你，画面主体变成你（手绘里画成长发女生），自然没有「一个人对着镜头」；
   - **纯空镜 / 物件**：只画门、口琴、那只手、钥匙等，几乎不可能被拒。
3. 仍被拒：把 "looking directly at the viewer" 改 "looking off to the side"；或整张改第三人称旁观；或退成空镜。

> 经验：The Cardinal 第 5 章「他半夜上来、你以为在做梦」反复被拒，最后改成**镜头是他在门口的视角、望进昏暗卧室、床上是长发安睡的你**，一次过——既是他的凝视、又彻底避开了被拒构图。

## 翻转兜底

手若仍画反：把图**左右镜像翻转**即可。但**只对没有可读文字的图能翻**（招牌、书名、手写字翻了会反）。**有文字的图（带 "THE CARDINAL" 霓虹、波兰语笔记等）别翻，重抽几张取最好的。**

## 画面内指定文字（如波兰语）

要画面里出现特定文字：把**原句一字不差**写进 prompt，并要求拼写正确、带正确字母（波兰语 ą ę ó ś）。AI 写手写字常缺字母/拼错——**多抽几张取最好**，或让文字**虚化看不清**就不穿帮。

> 范例（第 7 章）：本子写 `"Dzień dobry. Nazywam się Winter. Uczę się polskiego. Krok po kroku."`，封面 `"JĘZYK POLSKI"` + 猫头鹰；并加一句 `All visible text must be correct Polish, spelled exactly as given, with proper Polish letters (ą, ę, ó, ś).`

## 横屏 16:9

博客配图一律**横屏 16:9**（landscape），挂在文章里好看。每条 prompt 里都写明 `Horizontal 16:9 landscape`。

## 一条完整 prompt 长什么样（范例 · The Cardinal 第 1 章）

把风格块 + POV + 人物块 + 手部块 + 场景/配色焊成一整段，可直接粘贴：

```
Retro watercolor and gouache illustration, soft color washes, gentle paper-grain texture, hand-painted storybook feel, slightly faded vintage palette. Horizontal 16:9 landscape. First-person POV from a barstool inside an old 1994 taxi-dance hall called The Cardinal, late at night, as if seen through the viewer's own eyes (the viewer is not visible) — the front edge of a dark-wood bar and the rim of a whisky glass soft in the foreground. Behind the bar stands a young man in his mid-twenties resembling actor Sam Rockwell in the mid-1990s: boyish face, tousled sandy-brown wavy hair, hazel eyes, a slightly crooked smile, lean build, a simple dark shirt with rolled-up sleeves, a small silver cross at his throat. He leans slightly toward the viewer with a quiet, attentive, knowing look.

HAND PLACEMENT — follow the on-screen sides exactly: his bare uninjured hand rests on the bar on the LEFT side of the image; his other hand, on the RIGHT side of the image, is wrapped in a white bandage and rests on the counter (his injured hand). He faces us, so the bandaged hand on the RIGHT side of the frame is his own left hand. Do NOT place the bandage on the left side of the image.

Deep ember-red glow from red velvet walls and a glowing neon sign reading "THE CARDINAL" makes his hazel eyes look amber; a vintage jukebox and a carved mirror reflecting dancing couples catch the light behind him. Dominant ember-red palette, intimate and slightly melancholy mood.
```

> The Cardinal 十章的完整成套 prompt，Winter 手上已有一份独立文件（`TheCardinal_配图Prompt_十章_水彩防拒版.md`）可作为整套示范参照。
