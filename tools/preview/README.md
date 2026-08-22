# 草稿预览页生成器（Artifact 交付用）

Winter 看章节草稿的固定方式（2026-08-17 起，所有 AU 通用）：**不要把整章贴进聊天框**，
排成一张可预览的网页，用 Artifact 工具发布，聊天里只给链接 + 几句设计说明。
她点头后才落盘 `_posts/`；有修改就改完重发**同一个文件路径**，链接不变，她刷新即看新版。

这个目录就是那张网页的**唯一样板**。以前只把模板放在会话的 scratchpad 里，
而 scratchpad 每个对话各自独立、会话结束就没了，导致别的对话根本找不到样板——
所以它现在住在仓库里。

## 用法

```bash
python3 tools/preview/render_draft.py 草稿.md -o /tmp/.../预览.html \
    --series   "Zaphod AU" \
    --title    "雪的巡游" \
    --subtitle "番外 · Don't Panic, Baby Doll" \
    --mood     "缱绻 · 安放" \
    --notes    衔接说明.md
```

然后 `Artifact(file_path="/tmp/.../预览.html", favicon="❄️", description="...")`，
把返回的链接给 Winter。

| 参数 | 说明 |
|---|---|
| `source` | 草稿 markdown。带不带 front matter 都行（带的话自动剥掉） |
| `-o` | 输出 html 路径。**改稿后用同一个路径重新生成 + 重新发布，链接不变** |
| `--title` | 页面大标题，用中文章节名 |
| `--series` | 章节 front matter 的 `series` 值。据此从 `_data/au_palettes.yml` 自动取该 AU 的配色，预览观感就和线上阅读页一致。留空 / 查不到 → 站点默认金色 |
| `--subtitle` | 副标题，一般写「Chapter N · 系列展示名」或「番外 · 系列展示名」 |
| `--mood` | mood 标签，如 `炽恋 · 缱绻` |
| `--notes` | 页尾「衔接说明」文件（`.md` 或 `.html`）：这章回收了哪个伏笔、埋了什么新钩子、拟好的 summary、mood。方便她判断连贯性 |
| `--eyebrow` | 顶部眉标，默认「草稿 · 待冬璇过目」 |

## 支持的 Markdown 子集

跟博客正文实际用到的一致，别的语法一律不支持（也用不上）：

- `### 小节标题`
- `> 引用块`（文首题词、文末收束引语）
- `**粗体**`
- `---` 分隔线
- **行尾两个空格 = 硬换行**——多行诗式收束、多行题词靠这个，漏了各行会连成一团
- 以 `<` 开头的裸 HTML 块**原样透传**：内嵌 SVG 插图、`c-note` 便条卡、`c-decree` 公文卡等

## 已知的坑（改脚本前先看）

- **SVG 标签名大小写敏感**：`animateTransform` / `clipPath` / `linearGradient`…
  判断自闭合标签时统一 `.lower()` 再比，漏一个就会让那块 HTML 之后的正文
  全被当成 HTML 一起吞掉（2026-08 踩过）。
- **标签可能跨行写**：所以嵌套深度是把整块缓冲区合起来算，不是逐行累加。
- 页面是自包含的（CSS 内联、无外部请求），符合 Artifact 的要求。

## 自检

改完脚本随便挑一篇发布过的成品跑一遍，图 / 段落 / 引用块 / 硬换行的数量对得上就行：

```bash
python3 tools/preview/render_draft.py _posts/2026-10-02-zaphod-au-extra-a-tour-of-snow.md \
    -o /tmp/t.html --series "Zaphod AU" --title "雪的巡游"
# 期望：7 张内嵌图、5 个小节、3 个引用块、5 处硬换行
```
