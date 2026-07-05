# 把「Sam 测试」发布到 Cloudflare（干净域名，不暴露 GitHub）

把 **Sam 角色测试**单独部署到 Cloudflare，对外只显示你自己的域名，链接里完全
不出现 `github.io`，也追溯不到 GitHub 仓库。

## 这套东西是怎么运作的

- 公开出去的**只有 Sam 测试这一个页面**，是一个完全独立的静态页。
- 构建脚本 `tools/build_public.py` 会从完整版测试页 `sam/quiz/index.html`
  生成一个精简副本放进 `public/` 目录，过程中：
  - 去掉所有指向**不公开内容**的链接（返回 Sam 主页、8 个 AU 故事、
    「不止一面」角色档案页）——测试本身照常能做、能出结果；
  - 把图标路径改成根路径；
  - 修掉 `og:url` 里硬编码的 github.io 地址（否则分享时预览卡片会泄露）。
- **原文件 `sam/quiz/index.html` 一个字都不动**，github.io 完整版照常工作。
- Cloudflare 连着你的 GitHub 仓库，每次 push 到 `main` 就自动重新构建、上线。

## 仓库里已经配好的文件（你不用管，了解即可）

| 文件 | 作用 |
|---|---|
| `tools/build_public.py` | 生成公开版 `public/`（去外链、防泄露） |
| `wrangler.toml` | 告诉 Cloudflare「把 `public/` 目录作为静态资源托管」 |
| `package.json` / `package-lock.json` | 固定部署工具 wrangler 版本，让安装步骤稳定 |

---

## 你要做的：在 Cloudflare 后台改一个设置

你已经建好了 `winter-sam` 这个项目。之前构建失败，是因为**构建命令是空的
（Build command: None）**，我的脚本没机会运行，所以没东西可发布。补上就好：

1. 进 **Workers & Pages** → 打开 **`winter-sam`** → **Settings（设置）**。
2. 找到 **Build（构建）** 相关设置，把 **Build command（构建命令）** 填成：

   ```
   python3 tools/build_public.py
   ```

   其余保持不动：
   - **Deploy command（部署命令）**：`npx wrangler deploy`（默认就是这个，不用改）
   - **Root directory（根目录）**：`/`（默认，不用改）

3. 保存后，回到 **Deployments（部署）**，点 **Retry build（重试构建）**。

这次的顺序会是：安装 wrangler → 运行脚本生成 `public/` → 把 `public/` 上传。
一两分钟后就能在 Worker 的网址（形如 `winter-sam.<你的子域>.workers.dev`）
打开你的 Sam 测试。这个网址已经不带 github.io，可以直接分享。

> 如果还是失败：在那个构建详情页点 **Download log / Copy build log**，
> 把日志发给 Claude，能立刻定位问题。

---

## 关于域名（还没有也没关系）

先用 Cloudflare 免费给的 `…workers.dev` 网址就行，已经不暴露 GitHub。
以后想要自有域名：
- **在 Cloudflare 直接买最省事**，买完在 `winter-sam` 项目的
  **Settings → Domains & Routes / Custom domains** 里一键绑定。
- 或在别处买域名，再把 DNS 指到 Cloudflare。

买好后告诉 Claude，会帮你把 `tools/build_public.py` 里的 `SITE_URL` 改成
你的真域名（只影响分享预览里显示的网址），并教你绑定。

---

## 以后想公开更多内容

现在公开的只有 Sam 测试一个页面。想加别的，改 `tools/build_public.py`
（`ASSETS` 控制复制哪些静态文件，`transform()` 控制页面怎么处理）。
告诉 Claude 想加什么即可——**部署管线本身不用再动**。
