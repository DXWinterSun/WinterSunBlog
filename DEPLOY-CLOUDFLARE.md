# 「Sam 测试」的 Cloudflare 部署（干净域名，不暴露 GitHub）

Sam 角色测试单独部署在 Cloudflare 上，对外只有 Worker 网址
`wandering-river-bd34.rz6zpmnzj4.workers.dev`，链接里不含 `github.io`，
也追溯不到 GitHub 仓库。

## 这套东西是怎么运作的

- 公开出去的**只有 Sam 测试这一个页面**，是一个完全独立的静态页。
- 构建脚本 `tools/build_public.py` 从完整版 `sam/quiz/index.html` 生成精简副本
  放进 `public/`，过程中自动：
  - 去掉指向**不公开内容**的链接（返回 Sam 主页、8 个 AU 故事、「不止一面」档案页）；
  - 图标路径改成根路径；
  - 修掉会泄露 github 地址的 `og:url`。
- **原文件一个字不动**，github.io 完整版照常工作。
- **自动同步**：每次 push 到 `main` 且改动了测试页/脚本/配置时，
  GitHub Actions（`.github/workflows/deploy-public.yml`）自动重新生成并部署到
  同一个 Worker，网址不变。**平时更新内容什么都不用手动做。**

## 仓库里已配好的文件（了解即可）

| 文件 | 作用 |
|---|---|
| `tools/build_public.py` | 生成公开版 `public/`（去外链、防泄露）；顶部 `SITE_URL` 是对外网址 |
| `wrangler.toml` | 指定部署到哪个 Worker（`name`）、哪个账号（`account_id`）、传哪个目录 |
| `.github/workflows/deploy-public.yml` | push 后自动构建 + 部署 |
| `package.json` / `package-lock.json` | 固定 wrangler 版本 |

---

## 一次性设置：一个 API 令牌（让自动部署有权限）

自动部署需要一把「钥匙」让 GitHub 有权限往你的 Cloudflare 推。**只配一次，永久有效。**

### 1. 在 Cloudflare 生成 API 令牌
- 登录 https://dash.cloudflare.com/ → 右上角头像 → **My Profile**
  → 左侧 **API Tokens** → **Create Token**。
- 选模板 **Edit Cloudflare Workers**（编辑 Workers）→ 一路 Continue / 确认创建。
- 复制生成的那串 token（**只显示这一次**，务必存好）。

### 2. 把令牌填进 GitHub
- 打开 GitHub 仓库 → **Settings** → **Secrets and variables** → **Actions**
  → **New repository secret**。
- Name（名字，必须完全一致）：`CLOUDFLARE_API_TOKEN`
- Secret（值）：第 1 步复制的 token → **Add secret**。

### 3. 触发一次，验证
- 去 GitHub 仓库 **Actions** 页 → 选 “Deploy Sam quiz to Cloudflare”
  → **Run workflow** 手动跑一次（或随便改下测试页再 push）。
- 跑绿后，去 `wandering-river-bd34.rz6zpmnzj4.workers.dev` 看更新是否生效。

> 配好之前，这个工作流每次会自动**跳过部署、显示绿色**，不会报红。

配好后就彻底自动了：**改测试 → push 到 main → 自动上线，不用再碰 Cloudflare。**

---

## 账号 ID / 网址等信息

- Cloudflare Account ID：`8cf56c71ed9797a5e930bea0537727b1`（写在 `wrangler.toml` 里；
  不是机密，dashboard 网址里就有。换账号才需要改。）
- 对外网址：`https://wandering-river-bd34.rz6zpmnzj4.workers.dev`

## 关于域名

免费的 `…workers.dev` 已经够用、不暴露 GitHub。以后想要自有域名，
在 Worker 的 **Settings → Domains & Routes** 里绑定，再把 `tools/build_public.py`
的 `SITE_URL` 和 `wrangler.toml` 里相关项更新即可（告诉 Claude 帮你改）。

## 以后想公开更多内容

改 `tools/build_public.py`（`ASSETS` 控制复制哪些静态文件，`transform()`
控制页面怎么处理）。告诉 Claude 想加什么即可——部署管线本身不用再动。
