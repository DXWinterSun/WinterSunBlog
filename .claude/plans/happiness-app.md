# Happiness · 一日三事 iPhone 应用（2026-09-30 起）

Winter 想把博客左下角「记忆碎片」那叠拍立得里的**第一张（每天三件幸运小事 · fortunes）**
做成一个**真正能上架 App Store 的 iPhone 应用**，名字叫 **Happiness**。其它两张
（吐槽窗 windows、写给自己的信 toself）以后再考虑做成附带功能。

## 分工

- **云端对话（本仓库）**＝教练：写操作指南、回答她的问题、做博客上的隐私说明 / 支持页。
  云端对话碰不到她的 Mac。
- **她 Mac 上的本地对话**（Claude 桌面应用 → Code → Local，文件夹 `~/Documents/Happiness`）
  ＝施工队：建 Xcode 项目、写代码、开模拟器、上传。那边的说明存在它自己文件夹的 `CLAUDE.md`。
- 操作指南页（Artifact）：https://claude.ai/artifact/6oEr9oguMXo8WyzcBNQkK9
  源文件 `.claude/plans/happiness-guide.html`（改完从别的对话发布时传 `url`，链接不变）。
  里面的「开工口令」就是交给本地对话的完整说明，改功能要同步改这里。

## 已查清的事实（别再重查）

| 事 | 结论 | 来源 |
|---|---|---|
| 用 Jack 的开发者账号 | **个人账号**不能把别人加成能签名的开发者（只能加进 App Store Connect，看内容、当内部测试员）。所以签名那一步要 **Jack 本人在她 Mac 的 Xcode 里登录一次**（设置 → 账户 → ＋，手机收验证码）。公司账号则可以邀请她用自己的 Apple ID。 | developer.apple.com/help/account/access/roles/ |
| 商店「开发者」一栏 | 个人账号显示 **Jack 的真实姓名**。已告诉 Winter。 | 同上 |
| 名字 | 主屏幕图标下的名字不必唯一 → 就叫 **Happiness**。商店列表名（≤30 字）**全商店唯一**，Happiness 这种常见词基本肯定被占，要带尾巴（第④阶段再让她挑）。 | developer.apple.com/app-store/product-page |
| 装到她手机上试用 | 走 **TestFlight**（不用插线、不用开开发者模式）：Jack 在 App Store Connect「用户和访问」里加她的 Apple ID → 她当内部测试员。 | |
| 歌词 | 博客卡片上 The Fray「Happiness throws a shower of sparks」**不印进应用**（上架应用印歌词有版权风险，审核可能拒）。 | |
| 同类应用 | 商店里「三件好事」日记很多（Three Good Things、Delightful…），审核有「太简陋」被拒的风险（准则 4.2），第一版要做得完整精致。 | |

## 四个阶段

1. **装好工具**：Xcode（App Store）＋ Claude 桌面应用。——她自己做
2. **开工看样子**：本地对话建项目，模拟器里看「今天」页、挑样式。——不需要 Jack
3. **装到她手机上**：Jack 登录一次 → 上传 TestFlight → 她手机上试用。——需要 Jack 十分钟
4. **提交上架**：商店名、截图、介绍、隐私说明（云端做博客页 `/happiness/privacy/`、`/happiness/support/`）、
   年龄分级、免费、App 隐私选「不收集数据」→ 提交审核。

## 第一版功能（交给本地对话的「开工口令」里写的就是这些）

1. 「今天」页：三行，编号 一 / 二 / 三，自动保存；日期写成 `Tuesday · 30 September 2026`。
2. 往前翻日子，不能翻到未来。
3. 回看所有日子（日历 / 一叠拍立得，做两版让她挑）。
4. 读入博客「底片匣」导出的 json（只读 `journals.fortunes`，旧版 `lucky` 也认；同一天留 `ts` 更新的）。
5. 导出备份文件。
6. 只存在手机里：不注册、不登录、不联网、不收集数据。
- SwiftUI，iOS 17+，只做 iPhone 竖屏；字体 Caveat ＋ 马善政（OFL，打包进应用）。
- 占位 Bundle ID：`com.wintersun.happiness`（Jack 登录后再定）。
- 以后再说：吐槽窗、给自己的信、每日提醒、面容锁、iCloud 同步、GitHub 备份。

博客导出格式（`js/polaroid-notes.js` 的 `exportNotes()`）：

```json
{ "app": "wiw-polaroid-notes", "v": 3, "exported": 0,
  "journals": { "fortunes": { "2026-09-30": { "items": ["", "", ""], "ts": 1790000000000 } } } }
```

## 进度

- 2026-09-30：Winter 拍板做正式上架版；指南页发布；等她装 Xcode、开本地对话。
