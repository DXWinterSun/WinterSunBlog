---
name: winter-memo
description: Winter 的「冬的备忘本」——分页的备忘（💡灵感 / ❣️Sam / 💼工作 / 🏠生活），网页 /memo/ 上能改，iPhone 桌面上有同步的 Scriptable 小组件，对话里也能直接替她记、替她划掉。当 Winter 说「记一下」「帮我记」「加到备忘」「备忘本」「待办」「灵感」「这个想法先存着」「……做完了 / 划掉」「我备忘里有什么」「最近要做什么」，或提到桌面小组件上的备忘、想换小组件样子、加一页 / 改页名时，必须用本 skill。即使她只是随口甩来一句「明天要交课件」「突然想拍一期 XX」，没说记哪儿，只要落点是「存下来以后要看 / 要做」，就按本 skill 记进备忘本，记完告诉她记在哪一页。注意区分：AU 连载的伏笔账、圣经用 winter-au-writing；波兰语错题用 winter-polish-notes；原著划线用 winter-reading-notes。
---

# 冬的备忘本：她说一句，就记进去；做完了，就划掉

2026-10-03 Winter 原话：**「你能不能帮我做一个类似于记事本的功能？……我自己可以编辑，然后也可以直接在
对话里告诉你，然后你帮我填进去的一个备忘录，最好可以给我做成一个同步的桌面小组件……有一些可能是我当下
有灵感的关于我想做的视频呀，帖子之类的主题，跟 Sam 有关的东西等等，然后也可能是我最近要做的，比如说
工作上的事情，生活上的事情，我觉得他们分开会比较好。」**

所以：**她说「记一下 X」，直接记，不用问「要不要记」；只在真分不清放哪一页时问一句（给选项）。**

## 东西都在哪

| 东西 | 位置 | 备注 |
|---|---|---|
| 数据（唯一一份） | 仓库 **`memo` 分支**上的 `memo.json` | ⚠️ 不在 main 上，别往 main 里放备忘 |
| 改数据的工具 | main 上的 `tools/memo/memo.py` | 不碰工作区，自己取最新、提交、推 `memo` 分支，推不上会重放重试 |
| 编辑网页 | `memo/index.html` → https://dxwintersun.github.io/WinterSunBlog/memo/ | 钥匙存她手机本地（先找 `ws-memo-key`，没有就借藏品架那把 `ws-sam-shelf-key`） |
| 桌面小组件 | `memo/widget/winter-memo.js`（Scriptable） | 安装说明页 `/memo/widget/`；读 GitHub API 上 memo 分支那份 |
| 小组件模拟器 | `tools/widget-sim/`（`sim.js` + `shot.js` + `compose.py`） | 改小组件样子时用它出效果图给她看 |

**为什么放 `memo` 分支**：放 main 的话她每改一条都会触发一次整站重建（四分钟），还会掐掉正在跑的正文部署。
memo 分支不触发 Pages 构建，网页和小组件直接从 GitHub API 读，改完一分钟内就到。

⚠️ 仓库是公开的，`memo` 分支谁特意去翻都看得见（网页本身要钥匙才打开）。这件事 2026-10-03 已经跟她说过。
真正私密的东西（密码、身份证号、银行卡）**别往里记**，她要记的话提醒一句。

## 对话里怎么改（照抄就行）

先拉最新的工具（main 上）：`git fetch origin main && git checkout origin/main -- tools/memo/memo.py`（工作区就在 main 上时不用）。

```bash
python3 tools/memo/memo.py ls                       # 看全部（含 6 位编号）——动手前先看一眼
python3 tools/memo/memo.py add 灵感 "剪一期采访切片"   # 一次可以给好几条
python3 tools/memo/memo.py add 工作 "交 Unit 5 课件" --due 10-15 --note "要带听力答案"
python3 tools/memo/memo.py done 课件                 # 编号、或原文里的一段都行
python3 tools/memo/memo.py undone 课件
python3 tools/memo/memo.py edit k3f9a2 --page 生活 --due none --pin
python3 tools/memo/memo.py rm k3f9a2
python3 tools/memo/memo.py top k3f9a2                # 挪到这一页最前面
python3 tools/memo/memo.py clear-done 工作           # 清掉做完的（不可恢复，先问她）
python3 tools/memo/memo.py pages                     # 看有哪几页
python3 tools/memo/memo.py page-add 读书 📚 --hint "想读的书"
python3 tools/memo/memo.py page-rename 生活 --name 日常 --emoji 🌿
```

- 页面名认口语：灵感 / 点子 / 视频 / 帖子 → 💡灵感；Sam / 山姆 → ❣️Sam；工作 / 上班 / 学校 / 教学 → 💼工作；
  生活 / 日常 / 家里 → 🏠生活。她新加的页按名字认。
- 日期：`10-15`、`2026-10-15`、`今天 / 明天 / 后天`，`none` 清掉。她说「下周五」之类，自己算成日期再填。
- 每个改动都加 `--trailer` 把会话要求的署名行带上（会话提示里给的那两行，原样一行一个 `--trailer`）。
- 想先看效果不推：加 `--dry-run`。

## 记的时候怎么判断

1. **放哪一页**：她说了就照说的；没说就按内容判——想拍的视频 / 想发的帖子 / 选题 → 灵感；
   跟 Sam 本人、他的片子、他的 AU、画册、藏品有关 → Sam；上课、课件、学生、单位、申报 → 工作；
   取快递、买东西、看病、家里的事 → 生活。**真两可时**给她两个选项挑，别闷头猜。
2. **一条写短**：桌面小号一行只放得下七八个字。长的拆成「标题 + 备注」：标题进正文，细节进 `--note`
   （网页上看得见，小组件上不显示）。例：她说「我想做一期 Sam 讲第一次试镜的采访切片，最好三分钟以内
   配中英字幕」→ `add 灵感 "采访切片：第一次试镜" --note "三分钟以内，配中英字幕"`。
3. **用她的说法**，别改写成书面语；别替她加她没说的事。
4. **到期日**只在她提到时间时才填。
5. 她说「X 做完了」→ `done`，不是 `rm`（做完的留在网页的「做完的」里，她自己清）。说「删掉 / 不要了」才 `rm`。

## 回她的话怎么说

用人话说结果，别贴命令输出：

> 记好了：💼 工作 多了一条「交 Unit 5 课件」，10 月 15 号，备注写了要带听力答案。
> 桌面上那块等它自己刷新（十几分钟内），点开就能看到。

她问「我备忘里有什么 / 最近要做什么」→ `ls` 之后按页用几行话列给她（只列没做完的；有到期的标出来）。

## 改小组件的样子

样子在数据里（`settings.style`：`paper` 便笺 / `native` 提醒 / `snow` 晴雪），她在网页⚙设置里自己能换。
要改脚本本身的画法：改 `memo/widget/winter-memo.js` → 用模拟器出图给她看（下面）→ 她点头再推 main
（脚本改了，她得在 Scriptable 里重新粘一次代码，说明页的代码块会自动更新）。

```bash
export NODE_PATH=/opt/node22/lib/node_modules     # 全局装的 playwright
git show origin/memo:memo.json > /tmp/m.json
node tools/widget-sim/sim.js memo/widget/winter-memo.js --family small --param 工作 --data /tmp/m.json -o /tmp/w.html
node tools/widget-sim/shot.js /tmp/w.html /tmp/w.png 3
# 贴到她发来的桌面截图上（坐标是截图像素；她那台 iPhone 1206 宽、3 倍屏，右侧中间那格小组件在 638,871）
python3 tools/widget-sim/compose.py 桌面.png 效果.jpg --clear 636 869 1129 1362 --put /tmp/w.png 638 871 --label Scriptable 1404 --dots 4 0
```
