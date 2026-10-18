# Only I Know · Jason Dixon AU（从头重写）—— 系列圣经 v2（开坑中）

> **2026-10-18 推倒重写。** Winter 在重看《Three Billboards Outside Ebbing, Missouri》，原话：
> 「我想重新写三块广告牌的 au 了🥺 我重看电影呢，想起来我们一直没怎么写。」
> 旧版只有 4 章（2026-06 发布，停更，series_status: hiatus）：你是警局前台、官衔比他高半级，他叫你 pretty、说「顺路」。
>
> ⛔ **铁律（照 Gary 那次重写的做法）：一切以电影原片为准。** 旧版的设定不继承，除非 Winter 在提案页上挑回来
> （提案页初见 A「警局的夜班电话」就是旧版那个位置）。
> 唯一保留：封面 `images/3-billboards-au.JPG`、画册 Dixon 本色配色（`_data/au_palettes.yml` 的 "Only I Know" 条目，mf_id: dixon）。
> 旧四章：新版第一章上线那天撤下，原样存进 `only-i-know-v1-archived-chapters/`，不删（同 `slow-hands-v1-archived-chapters/`）。
> 系列名等故事定了再挑；Only I Know 可以留。

---

## 一、现在走到哪

- [x] **素材**（2026-10-18）：电影台词逐句对过（字幕整理稿，来源见素材档案），配乐场次核过 →
      `only-i-know-revised/dixon-素材档案.md`（片中事实、台词、谁叫他什么、两处存疑）。
- [x] **开坑提案已发**（2026-10-18）：https://claude.ai/artifact/DZEnNrmnXSFLVNXXdpcnW3
      数据 `.claude/pitches/only-i-know-rewrite.json`，生成 `python3 tools/preview/render_pitch.py`（这次给提案页加了「想补充的话」框）。
      五道岔路：
      1. 初见：A 警局的夜班电话（旧版位置）/ B 对街那扇窗（Red 广告公司文员，他来赔窗户）/ **C 三楼最里头那间病房（我推荐）**：夜班护士，他缠满纱布，求你帮他给死去的警长回信；你先认识他，最后才知道他的名声
      2. 跟电影：**A 贴着电影走、全在镜头外（推荐）** / B 从你出现起可以拐弯 / C 电影全部结束以后才开始
      3. 味道（可多选）：糙里带甜 / **一封信那么慢（推荐）** / 炽恋 / 小镇的怅惘
      4. 他叫你：**ma'am（推荐）** / 叫你的姓 / 叫你 Winter 还拿季节开玩笑
      5. 你姓：Rainey（雨）/ Ashby（灰）/ Gentry（南方老姓）
      她重看后在批注里确认：他打了 Pamela、着火那晚戴着耳机；还补了「他养乌龟，坐沙发上喂它」（已进素材档案、母题、病房样章）。
- [x] **她挑完了**（2026-10-18）：姓 **Gentry**；身份回到旧版那个「署里的妈」，**这回就是电影里 Cedric（警佐）的位置**；
      她嫌提案页样章里的你「太严肃了，少了点宠溺和无可奈何」；警长**不给你留信**——「我们的默契已经不需要了，比较心碎但也比较像他」。
      跟电影 / 味道 / 他叫你，她没点，按她这几句话定：贴着电影走；糙里带甜 ＋ 一封信那么慢；他叫你 Sarge（原片他就这么叫 Cedric）。
- [x] **第一章《让他当最后一个知道的》草稿已发**（2026-10-18，待她过目）：https://claude.ai/artifact/EgBUvsfwB9eQiP27goJ7hH
      正文 `only-i-know-revised/ch1.md`，说明＋往后路线 `ch1-notes.md`，第二章岔路 `ch2-forks.json`
      （那天夜里他去哪儿 / 你什么时候发觉不只是心疼 / 第一声 Jason 在什么时候）。
      生成：`python3 tools/preview/render_draft.py .claude/bibles/only-i-know-revised/ch1.md -o <scratchpad>/dixon-ch1.html --series "Only I Know" --title "The Last to Know" --subtitle "第一章 · 让他当最后一个知道的" --kicker "Only I Know · Jason Dixon AU（重写）" --mood "絮语 · 怅惘" --notes .claude/bibles/only-i-know-revised/ch1-notes.md --forks .claude/bibles/only-i-know-revised/ch2-forks.json`

## 二、设定（2026-10-18 定）

- **你：Winter Gentry，Ebbing 警局警佐（Sergeant）**——电影里 Cedric Connolly 的位置，Cedric 这个人在这一版不存在，他的台词归你。
  坐镇前台，管整栋楼的日常；比 Dixon 早进署好几年（他警校念了六年），年纪跟他差不多，「妈」是署里的玩笑，不是年纪。
- **署里的「爸妈」**：那帮人私下管你和 Willoughby 叫爸妈，你俩说话叫「爸妈开会」。跟 Willoughby 是同事间的默契与亲近，**不是暧昧**（他有 Anne 和两个女儿）。
  ⭐ **警长不给你留信**（她定的）：他给 Anne、Mildred、Dixon 都留了，唯独没有你——默契不用写。第一章埋了他当面那句「那天就归你管了」，这就是你的信。
- ⭐ **你的口气：宠他，又拿他没办法**（她点名要的「宠溺和无可奈何」「天然的怜爱」）。别写成冷静严肃的上司。
  他捅娄子你骂，骂完替他收拾；被他绕进去你想板脸板不住；嘴上「别犯浑」，脚已经追出去了。右手边第二个抽屉是给他备的。
- **称呼**：他叫你 **Sarge**（原片他就这么叫警佐）；Willoughby 叫你 Winter；Red 叫你 Winter，你回他「别叫我 Winter」（原片「别叫我 Cedric」）；
  他妈叫你「Gentry 家的姑娘」。你叫他 **Dixon**；只有警长和他妈叫他 Jason。**你第一次叫他 Jason 留着当大事**（第二章岔路第三道问她什么时候）。
- **贴着电影走**：电影里的事一件不改，你们的事在镜头外。片尾他照样上 Mildred 的车去爱达荷；之后的事空着。
- **不洗白**：刑讯传闻、种族歧视、扔 Red、打 Pamela 都发生过。但 Cedric 那句「他刑讯过一个在押的人，Bill」不给你（你是宠他的人，太硬），由 Red 当街那句带出来，你听见、不接、不提。

## 三、我从片子里读出来的他（提案页上给她看过，她没改就照这个写）

- 三十好几还跟妈住、警校念了六年、全镇都看不上；真拿他当回事的只有 Willoughby，而他在故事一开头就快死了。
- 笨的坏：偏见从他妈那儿原样搬来，连“进步”也只是把脏字换成“有色人种”。**片子里他干过的事一件不洗白**——不替他辩解，只写他往好里走。
- 抬杠，以为自己机灵（“我是问你是不是白痴”，现学 Mildred 广告牌那招）。
- 一封信就信了：爱 → 平静 → 想事情，他真去学；狠起来也像孩子（为 DNA 让人把自己揍到满脸血）。
- 会道歉，笨笨的、不找借口。
- 没人爱过：他妈笑他没相好，警长说他缺的是爱。

## 四、母题候选（提案页列过，挑完岔路再定）

那封信（“Jason, Willoughby here.”）· Dixon / Jason · 丢了又找着的警徽 · 耳机和《Chiquitita》 ·
“The Dixon residence.” · 他妈（沙发、电视、Donald Sutherland 的头发、“我知道！”）· 一杯橙汁一根吸管 ·
纱布和新长的皮 · 那只乌龟（他坐沙发上喂它）· 对街那扇窗和钉上的板子 · “你能做的就是尽力，我妈说的。” · 夹在案卷里的漫画 · “我是问你是不是。”

## 五、章节流水

| 章 | 篇名 | 干了什么 | 状态 |
|---|---|---|---|
| 1 | 让他当最后一个知道的（The Last to Know） | 复活节夜他先打给你；第二天他头一回早到，你给他重扣扣子；你去 Red 那儿（《好人难寻》、Pamela）；“我是问你是不是白痴”把你绕进去，警长“他把你绕进去了，Winter！”；他听说 Red 对你说脏话冲出去，Main Street，“你现在就喝了？”；警长关门咳血：“那就让他当最后一个知道的”“那天就归你管了”；夜里拼 ramifications、警探梦、“他大概觉得我是个笑话”；他妈来电、乌龟；他问警长是不是病了，你说“感冒”，他信了。summary：全镇都知道的事，你和警长说好，让他当最后一个知道的。mood：絮语 · 怅惘 | 草稿待过目 |

往后路线（贴着电影）见 `only-i-know-revised/ch1-notes.md` 末尾：第 2 章酒吧里 Red 说漏 → 第 3 章 Mildred 上电视、Denise、咳血 → 第 4 章 Chiquitita 那个早上、你对外头说“做个好警察”时他走过了街、三封信没有你 → 第 5 章窗户、Pamela、交枪 → 第 6 章是你叫他夜里回来拿信、火 → 第 7 章病房、橙汁 → 第 8 章他学平静、去他家 → 第 9 章爱达荷那个男人、浴室门外 → 第 10 章 DNA、警徽、上车。

## 六、PINNED / DEFERRED

**PINNED（已埋，待回收）**
- Ch1「那就让他当最后一个知道的」→ Ch2 他从 Red 嘴里知道；Ch4 他又是最后一个（耳机、《Chiquitita》）。
- Ch1 你说“感冒”骗了他 → 他知道你骗了他（Ch2）。
- Ch1「他大概觉得我是个笑话」→ 警长的信“I know you don't think I think that, but I do”（Ch6）。
- Ch1「那天就归你管了」→ Ch4 三封信没有你；你想起这句，就是你的信。
- Ch1 右手边第二个抽屉 → 以后里面多出一样东西（未定：烧焦的什么？他找着的警徽？等写到再定）。
- Ch1 Red 手里的《好人难寻》 ↔ 警长“他是个好人。打心底里”。
- Ch1 “从窗户扔出去”（你随口一句）→ Ch5 他真把 Red 扔出了窗。

**DEFERRED（压着，到点再放）**
- 你第一次叫他 Jason：第二章岔路问她（推荐：叫他夜里回来拿信的那通电话——原片警佐正是在那通电话里叫的 Jason，那一夜警局着火）。
