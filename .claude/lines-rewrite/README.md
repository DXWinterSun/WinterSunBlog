# 台词改稿工作区

Winter 2026-09-22 在桌面小组件上看见 Wayne 那句挂着光秃秃的 `YES`，说「整个台词库我感觉都可以
过一遍」。2026-09-23 先做了一次全库体检（54 人 × 5 句 = 270 条），按「原著厚不厚 / 有没有 AU」
分成四象限，挑出分数最低的 8 位先动刀。**这个目录放的就是还没上线的改稿。**

| 文件 | 是什么 |
|---|---|
| `batch1.json` | 第一批 8 人 × 5 句的改稿（含预览页的全部文案与要问 Winter 的岔路） |
| `audit-rows.json` | 那次全库体检的评分数据（54 人：原著厚薄 / AU 章数 / 语料条数 / 五句里有几句真属于他 / 一句诊断） |

## 怎么用

```bash
# 生成给 Winter 过目的新旧对照页，再用 Artifact 工具发布，聊天里只给链接
python3 tools/preview/render_lines_diff.py .claude/lines-rewrite/batch1.json -o /tmp/.../稿.html
```

改稿 JSON 的字段说明写在 `tools/preview/render_lines_diff.py` 的文件头里。

## 判据（Winter 定的那把尺子，跟章节名同一把）

> **移植测试**：把这句话放到别的角色身上还成立吗？成立 → 太泛，重写。

合格的句子长在**他自己的东西**上：一件道具、一个动作、一句原片台词，或他 AU 正文里已有的那件事。
`你是唯一看见我的人` / `你留下了` / `我想变好` 这一类谁都能说，一律作废。

## ⚠️ 她点头之后，落盘要做的事

1. 写进 `sam/lines.json` 的 `characters[].quotes`，**再从 characters 整个重建 `pool`**
   （5 轮 round-robin，别手改 pool）。
2. **改了第 1 句（锚句）的**，画册 `sam/many-faces/index.html` 的 `inscription`、
   `sam/spectrum/index.html`、`sam/quiz/index.html` 三处的 label/line/lineCN 要一起改。
   第 2–5 句只动 lines.json 一个文件。
3. 查 label：全站唯一、同一个角色的 5 条之间不互相包含（命令见 CLAUDE.md 那一节）。
4. 跑 `python3 tools/check_palette_sync.py` 和 `python3 tools/check_daily_rotation.py`。
5. ⚠️ `.claude/` 下的改动不单独推 `main`，攒着跟台词一起走。

## Winter 给过的两条判断（照着办，别推翻）

- **2026-09-23｜「有点克制了，但确实更细节更贴合角色了」** → 方向（摆具体的东西、不说通用情话）
  留着，尺度放开：**每人挑一句，在那件东西后面把话真的说出来**（改稿里标 `"warm": true`）。
  放多少看各人性子：Buck / Samuel / Eddie 藏不住，放到底；Trent 隐忍是他六维最高的一项，
  他的「放开」是把说不出口本身说出口（那三个字圣经里压着，别提前给）；Jim Reston 仍然不说
  「我爱你」——「我不说，我证明」本来就是他的声口。
- **2026-09-23｜Brad Cairn 不是一个只会疲惫的人**（Winter 原话）：「他确实是扛着生活的重压，
  但他有 Sam 式的活力，他打网球，他在上下班路上戴耳机听歌（那个年代还是有线耳机），他会开玩笑，
  会和最爱的金毛狗狗一起玩……**他的悲剧源于不幸和不可抗力，这才是最戳的**。」
  → 他的五句已按这条整块重写（活力在前、不可抗力在后），体检里「原著薄」的判定也一并订正为「中」。
  ⚠️ 写他别再往「疲惫的爸爸」一个方向写。

## 还欠着的

- 第 2 批：体检里 B 组那 15 位（原著厚、还没写 AU）——每人从各自电影里挑一件**只有他有的东西**，
  替掉最泛的那一句，每人只动一句。
- 之后每开一个新 AU，回来把那个人的五句重写一遍——那时候材料最足。
- Gary / Jerry / Billy Bickle / Eddie 四位的热线聊天回复库（`sam/hotline-replies.json`）还没写，
  所以他们的 AU 正文也还没被 `tools/hotline_mine.py` 收进语料。
