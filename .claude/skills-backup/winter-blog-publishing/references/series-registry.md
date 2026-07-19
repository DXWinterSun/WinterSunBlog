# 已知 AU 系列登记（备忘）

> **真源永远是线上仓库**。本表只是备忘，用来少跑几次「拉文件查当前值」。任何要写进 front matter 的 `series` / `series_name` / `image` / `series_order` / `collection_order`，**最终都以拉取到的当前线上文件为准**——尤其 `series_order`（接上一章 +1）和 `collection_order`（现有最大值 +1）这类需要「当前值」的字段。
>
> 用到某个系列、而下面信息不全或拿不准时：先拉线上文件确认，**确认后顺手把结果补登记到本表**。

## 一、已确认（封面 ↔ 英文 series_name）

这三组来自最新发布规范，可直接使用：

| 中文名 | 英文 `series` / `series_name` | 封面 `image` |
|---|---|---|
| 你是我的事实 | `You Are My Fact` | `leonard-shelby-au.jpg` |
| —（Wild Bill Wharton AU） | `Tuning the Devil` | `william-wharton-au.jpeg` |
| 足够好 | `Good Enough` | `justin-hammer-au.webp` |

> 封面扩展名三种都出现过（`.jpg` / `.jpeg` / `.webp`），**不能靠猜**——`image:` 字段大小写和扩展名必须和 `images/` 目录里的实际文件一字不差。

## 二、其它已知 AU（线索，数值待核对线上）

下面是 Winter 已在写或写过的 AU 角色 / 系列，**仅作线索**帮你快速回忆「画册里大概有哪些」。它们的**英文 `series_name`、封面文件名、`series_order` 进度、`collection_order`、是否 `sam_collection`，一律以线上文件为准**，不要直接照抄：

- Leonard Shelby（《记忆碎片 / Memento》线）——除已确认的《你是我的事实》外，另有更暗黑的一条《The One Who Remembers》。
- Justin Hammer（《钢铁侠 2 / Iron Man 2》）——《足够好》（已确认）。
- Jason Dixon（《三块广告牌 / Three Billboards》）——Dixon AU，女主设定名 Winter Calloway。
- Krzysztof "Kris" Wilk（《去爱那个人 / Somebody to Love》）——波兰语元素，画册里已有对应角色卡。
- Eric Bowen、Billy Bickle（《七个神经病 / Seven Psychopaths》）、Guy Fleegman / Guy Hale（《银河访客 / Galaxy Quest》）、Francis Munch（《先生你哪位 / Mr. Right》）、Wayne（《游手好闲 / Loitering with Intent》）、Craig（《迟来的青春 / Laggies》）、Stoppard（《一场偷天换日 / See How They Run》）。

> 这些条目可能不全或已变动（记忆有滞后）。**用哪个就先拉哪个的线上文件确认**，确认后把准确的英文名 / 封面 / 当前序号补到上面「已确认」表里，让本表逐渐长成可靠的真备忘。

## 三、`sam_collection` 提示

只有 Sam Rockwell 本人演的角色对应的系列才加 `sam_collection: true`。上面的角色绝大多数是 Sam 演的；但具体某个系列首页是否已挂 `sam_collection`、`collection_order` 排到几，**必须看线上文件**，不要凭本表推断。

## 四、登记新系列时，填这一行

每新建 / 确认一个系列，按下表往「已确认」表补一行：

```
| 中文名 | `English Series Name` | `cover-file.ext` |
```

若它是 Sam 角色且进画册，额外记下它的 `collection_order`（写进本节备注，便于下次 +1）。
