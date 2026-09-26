# 读书笔记网页生成器

Winter 读英文原著时拍来带高亮的书页，Claude 整理成笔记，排成一张能逐条批注的 Artifact 网页。
**完整工作法（读照片、写笔记、回批注、放博客）在 `.claude/skills/winter-reading-notes/SKILL.md`**，
这里只记怎么跑脚本。

```bash
python3 tools/reading/render_notes.py _data/reading/a-single-shot.yml -o <scratchpad>/a-single-shot-notes.html
```

| 文件 | 作用 |
|---|---|
| `render_notes.py` | 读笔记数据 → 生成网页。配色复用 `tools/preview/render_draft.py` 的 `palette()` |
| `demo.yml` | 页面上的固定说明文字 + 数据里还没有笔记时显示的「先挑详略」样板卡 |
| `_data/reading/<slug>.yml` | 每本书一份笔记数据（唯一真源），`book.artifact` 记着那张网页的链接 |

- 一本书一张页、一个链接：新的一批往 `batches` 末尾追加，重新生成，发布到同一个链接。
- 第一次发布带 `capabilities: {"comments": {"composer_only": true}}`，卡片上的「批注」按钮才打得开批注框。
- 行内记号只有两个：`==高亮==`、`**粗体**`；其余一律当纯文本转义。
- 笔记编号重复时脚本直接报错退出（批注锚在卡片 id 上，重号会串）。

自检：随手写一个带两批、各字段都填了的临时数据文件跑一遍，数一下 `class="card"` 的个数、
`<mark>` 是否包对了位置、目录是否出现（两批以上才有）。
