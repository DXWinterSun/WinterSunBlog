# 雪地打卡（加密）

在仓库根目录运行 `python3 tools/snow/snow.py summary` 检查数量。使用既有
`WINTER_TEXT_KEY` 和 `tools/private/private.py` 的既有 vault，不创建或重置 vault。
结构化历史存为 private 分支的一份加密档案；main 只保留通用程序与上锁网页。
不得提交原始历史、照片、密码或私密对话。不读取其他私人档案。

首次导入：`python3 tools/snow/snow.py import < /安全位置/history.json`。
已有档案拒绝重复导入。更新前在内存读取现有档案，保留全部其他字段。

饮食通过 stdin 传入 JSON：`python3 tools/snow/snow.py meal`。
格式为 `{ "id": "稳定且唯一的记录ID", "data": { "date": "YYYY-MM-DD",
"meal": "午餐", "what": "实际吃掉的内容", "kcal": 350,
"kcalRange": [290,410], "at": null } }`（示例为虚构数据）。
修正份量必须沿用原 ID，替换原记录，不能再加一条。计划吃的先不记，
照片给合理估算范围；不能把原设置的 kcal 当作当前目标。每日按上海时区累计。
体重用 `weight` 命令，结构相同，data 用 date / kg / note / at；同日覆盖。
写入后自动从远程读回核验，失败不能声称已保存。

网页 `/snow/` 在浏览器内解密，仅用于查看；不保存密码、派生密钥或明文到浏览器存储。
锁定/刷新后需重新解锁。通过对话更新，网页不直接写 GitHub，不索取 GitHub 令牌。
若发生 Git 非快进冲突，停止并重新读取、合并再提交；不得强推。
