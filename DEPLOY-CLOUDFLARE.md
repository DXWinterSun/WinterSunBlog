# 把博客发布到 Cloudflare Pages（干净域名，不暴露 GitHub）

这份文档说明如何把本站点部署到 **Cloudflare Pages**，对外只显示你自己的
自定义域名，链接里完全不出现 `github.io`，也追溯不到 GitHub 仓库。

构建仍然用你已经跑通的 GitHub Pages 官方环境（稳定），构建完的静态成品由
`.github/workflows/cloudflare-pages.yml` 自动上传给 Cloudflare。github.io
上原有的站点**不受任何影响**，两边可以并存。

---

## 一次性配置清单（按顺序做，约 15 分钟）

### 1. 注册 / 登录 Cloudflare
打开 https://dash.cloudflare.com/ 注册一个免费账号。

### 2. 建一个 Pages 项目（Direct Upload 类型）
- 左侧菜单 **Workers & Pages** → **Create** → **Pages** 选项卡
  → **Upload assets（直接上传）**。
- 给项目起个名字，比如 `winter-sam`。**记住这个名字**，第 5 步要用。
- 随便传一个占位文件先把项目创建出来即可（之后由 GitHub Actions 自动覆盖）。

> 为什么选「直接上传」而不是「连接 Git」：连接 Git 会让 Cloudflare 自己跑
> Ruby 构建，本站锁的 Jekyll 版本较老容易构建失败。直接上传由 GitHub 这边
> 构建好再传，最稳。

### 3. 拿到两个密钥
需要把它们填到 GitHub 里，Actions 才有权限往 Cloudflare 上传。

- **Account ID**：在 Cloudflare 首页右侧，或任意 Pages 项目的 URL 里能看到
  一串账号 ID，复制下来。
- **API Token**：右上角头像 → **My Profile** → **API Tokens**
  → **Create Token** → 用模板 **Edit Cloudflare Workers**（或自定义一个
  拥有 `Account · Cloudflare Pages · Edit` 权限的 token）→ 创建后复制那串
  token（**只显示一次，务必存好**）。

### 4. 把两个密钥填进 GitHub 仓库
到 GitHub 仓库页 → **Settings** → **Secrets and variables** → **Actions**
→ **New repository secret**，添加两条：

| 名称（必须完全一致）      | 值                         |
| ------------------------- | -------------------------- |
| `CLOUDFLARE_API_TOKEN`    | 第 3 步的 API Token        |
| `CLOUDFLARE_ACCOUNT_ID`   | 第 3 步的 Account ID       |

### 5.（已替你填好，无需操作）
`.github/workflows/cloudflare-pages.yml` 里的项目名已填为 `winter-sam`，
对外域名先用免费的 `winter-sam.pages.dev` 占位。等你有了自定义域名，
告诉 Claude 或自己把该文件里 `winter-sam.pages.dev` 那一行换成真域名即可。

> 第 2 步在 Cloudflare 建项目时，名字务必也叫 `winter-sam`，两边要一致。

### 6. （已自动生效）
工作流已在 `main` 上。**在你完成第 2–4 步之前**，它每次运行会自动
**跳过上传、显示绿色**，不会报红。等你把密钥配好，下一次推送到 `main`
（或在 Actions 页面手动点 “Run workflow”）就会真正上传，站点随即在
`winter-sam.pages.dev` 上线。

### 7. 绑定自定义域名
- Cloudflare **Workers & Pages** → 打开你的项目 → **Custom domains**
  → **Set up a custom domain** → 输入你的域名，按提示把 DNS 记录指过去
  （如果域名本身就托管在 Cloudflare，一键完成；在别处买的按提示加 CNAME）。
- 生效后，对外分享这个自定义域名即可，链接里不含 github.io。

---

## 以后怎么更新内容

**什么都不用额外做。** 照常写文章 / 改 Sam 内容，合并进 `main`，
GitHub Actions 会自动重新构建并推到 Cloudflare，几分钟后线上更新。
github.io 那边也会照旧同步更新，两边互不干扰。

## 想控制「哪些内容对外公开」

目前是整站一起发布。若以后想只公开 Sam 部分、把个人板块挡在公开域名之外，
告诉 Claude，可以在这条工作流里加一层构建过滤（include / exclude），
不影响 github.io 的完整站点。
