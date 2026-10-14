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

## 网页文章 → 可划线的阅读页（`clone_article.py`，2026-10-14）

Winter 读网上的英文报道时也想像读书一样划线（原话：「我看见一个生词自己查的方式还是太老套了……
是不是可以你帮我做一个这个网页的文章的克隆，我在读的时候可以在上面用我习惯的颜色标注词和短语，
然后你就可以帮我做笔记了？」）。

```bash
python3 tools/reading/clone_article.py <网址> -o <scratchpad>/<slug>.html
# 抓不到（反爬 / 代理）就先 curl 下来再喂：
python3 tools/reading/clone_article.py --html 下载的.html --url <网址> --slug <slug> -o …
```

- 抓标题、导语、署名、日期、正文各段（《卫报》按它的结构找，别的网站退到 `<article>`），
  排成一页：三支笔（蓝生词 / 粉对照 / 橙好句，跟 `render_notes.py` 同色）、选中即划、点已划的换色或擦掉、
  底部「清单」（按颜色列出、可擦、可复制一份贴给 Claude）。
- **第一次发布带 `capabilities: {"db": {}}`**：划线存进这张页自己的数据库 `highlights` 集合
  （一处一条：`p` 段下标、`loc` 位置名、`s`/`e` 字符偏移、`color`、`text`、`ts`、`noted`），手机电脑同一份；
  不在 claude.ai 里打开时退回本机 `localStorage`，再在 Claude 里打开会自动搬进数据库。之后重新发布不传 capabilities。
- Claude 做笔记时：`ArtifactData list highlights` 读回来 → 按读书笔记那套写进 `_data/reading/<slug>.yml`
  （`book.page_unit: 段`，每条的 `page` 写段号，标题 / 导语写 `标题` / `导语`，`loc` 里就有）→ 整理过的那几条
  `update {noted: true}`，页上那处划线底下会多一道绿线、清单里标「✓ 已整理」。
- ⚠️ 仓库公开：文章全文只在（私密的）网页里，**不要**把抓下来的全文或 `--dump` 的 JSON 存进仓库。
