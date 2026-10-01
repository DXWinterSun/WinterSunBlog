# 波兰语笔记本

Winter 学波兰语时把多邻国上做错的、看不懂的拿来问，Claude 讲清楚后收进这里，一题一张卡、按知识点分类。
**完整工作法（查档、讲解、归类、发布、推送）在 `.claude/skills/winter-polish-notes/SKILL.md`**，这里只记脚本。

```bash
python3 tools/polish/find.py kawy                                       # 她问过没有
python3 tools/polish/forms.py kawy                                      # 核对变格 / 变位
python3 tools/polish/render_polish.py -o <scratchpad>/polish-notes.html # Artifact
python3 tools/polish/render_polish.py --blog                            # 博客 polish/index.html
```

| 文件 | 作用 |
|---|---|
| `_data/polish/notes.yml` | 唯一真源：`meta`（链接、配色）、`areas`（分类表）、`notes`（笔记） |
| `render_polish.py` | 数据 → 网页。配色复用 `tools/preview/render_draft.py` 的 `palette()` |
| `find.py` | 查档：不分大小写、不管附加符号；对不上会去掉词尾再试，标「可能相关」 |
| `forms.py` | 查词形：读根目录的 `polish-data.json`（站里 `polski.html` 变格小工具的词库） |
| `demo.yml` | 页面固定文字 + 还没有笔记时显示的两张样板卡 |

- 编号重复、知识点不在 `areas` 里、`see` 指向不存在的编号，脚本都会直接报错退出。
- 生词旁的「查变格」链到 `polski.html?q=<词>`，打开就直接查好。
- 自测：`POLISH_NOTES=<临时数据.yml> python3 tools/polish/render_polish.py -o …`（不动真数据）。
