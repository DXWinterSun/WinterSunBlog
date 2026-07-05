# 把「Sam 测试」发布到 Cloudflare Pages（干净域名，不暴露 GitHub）

这份文档说明如何把 **Sam 角色测试**单独部署到 **Cloudflare Pages**，对外只显示
你自己的域名，链接里完全不出现 `github.io`，也追溯不到 GitHub 仓库。

## 这套东西是怎么运作的

- 公开出去的**只有 Sam 测试这一个页面**，是一个完全独立的静态页。
- 构建脚本 `tools/build_public.py` 会从完整版测试页 `sam/quiz/index.html`
  生成一个精简副本放进 `public/` 目录，过程中：
  - 去掉所有指向**不公开内容**的链接（返回 Sam 主页、8 个 AU 故事、
    「不止一面」角色档案页）——测试本身照常能做、能出结果；
  - 把图标路径改成根路径；
  - 修掉 `og:url` 里硬编码的 github.io 地址（否则分享到社交平台时预览卡片会泄露）。
- **原文件 `sam/quiz/index.html` 一个字都不动**，所以 github.io 上的完整版
  照常工作，两边并存、互不影响。
- Cloudflare 直接连你的 GitHub 仓库，每次你 push 到 `main` 就自动跑这个脚本、
  自动上线。**以后更新内容你什么都不用额外做。**

---

## 一次性配置清单（照着做，约 10 分钟）

### 1. 注册 / 登录 Cloudflare
打开 https://dash.cloudflare.com/sign-up 注册一个**免费**账号（不用绑卡），
去邮箱点确认链接激活。

### 2. 用「Connect to Git」创建 Pages 项目
- 登录后点左侧 **Workers & Pages**。
- 点 **Create（创建）** → 选 **Pages** 那一栏 → 选 **Connect to Git
  （连接 Git）**。
  - 如果你看到的是新版界面（只有 Connect GitHub / Upload static files 等
    按钮），底部有一行小字 **“Looking to deploy Pages? Get started”**，
    点那个 **Get started**，就会进到 Pages 的「连接 Git」流程。
- 授权 Cloudflare 访问你的 GitHub，选中仓库 **`WinterSunBlog`**。
- 分支选 **`main`**。

### 3. 填构建设置（关键，照抄）
在创建页面的构建设置里填：

| 项目                              | 填什么                        |
| --------------------------------- | ----------------------------- |
| Project name（项目名）            | `winter-sam`                  |
| Production branch（生产分支）     | `main`                        |
| Framework preset（框架预设）      | `None`（无 / 不选）           |
| Build command（构建命令）         | `python3 tools/build_public.py` |
| Build output directory（输出目录）| `public`                      |

其余保持默认，点 **Save and Deploy（保存并部署）**。

### 4. 等它构建完成
Cloudflare 会拉取仓库、运行脚本、发布。大约一两分钟后，你的 Sam 测试就在
**`winter-sam.pages.dev`** 上线了（这个免费域名已经不带 github.io，可以直接
分享测试）。

> 如果构建报错，把错误信息发给 Claude 帮你看。最常见的是构建设置某项填错。

### 5. 绑定你自己的自定义域名（等你有了域名再做）
- 先有一个域名（见下方「关于域名」）。
- Cloudflare **Workers & Pages** → 打开 `winter-sam` 项目 →
  **Custom domains（自定义域名）** → **Set up a custom domain** →
  输入你的域名，按提示把 DNS 指过去（域名若托管在 Cloudflare 一键完成）。
- 绑定后，再把 `tools/build_public.py` 里的 `SITE_URL` 改成你的真域名
  （告诉 Claude 帮你改，或自己改那一行），push 一下即可。这一步只影响分享
  预览卡片里显示的网址，不影响测试能不能用。

---

## 关于域名（还没有也没关系）

现在 `winter-sam.pages.dev` 已经能用、已经不暴露 GitHub，足够先发出去。
以后想要更好看的自有域名（一年通常几十到一百多块）：
- **在 Cloudflare 直接买最省事**（Workers & Pages 旁边的 **Registrar /
  Domain Registration**），买完在同一个账号里一键绑定。
- 或在 Namecheap / 阿里云 / 腾讯云 等买，再把域名的 DNS 指到 Cloudflare。

买好后告诉 Claude 域名是什么，会帮你改配置 + 教你绑定。

---

## 以后想公开更多内容

现在公开的只有 Sam 测试一个页面。想加别的，改 `tools/build_public.py`：
- 顶部的 `ASSETS` 控制哪些静态资源被复制进公开站；
- `transform()` 里控制页面怎么处理。

告诉 Claude 你想加什么，会帮你扩这个脚本——**部署管线本身不用再动**。
