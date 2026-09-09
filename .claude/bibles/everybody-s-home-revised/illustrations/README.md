# 手绘插图的生成脚本

这个系列里几张 SVG 插图**不是外部素材，是脚本画出来的**。SVG 成品已经内嵌在各自
那篇 `_posts/` 正文里（所以画面本身丢不了），可**生成脚本**要是只留在会话临时目录，
下次 Winter 说「这张图某处改一下」就没得改了——所以放在这儿。

| 脚本 | 属于哪篇 | 画的是什么 |
|---|---|---|
| `extra07-viewport.py` | 番外七《The Third Cup》 | 飞船客舱那扇圆舷窗：满天星斗 ＋ 远处一颗蓝色的地球。**只画窗、不画人**（Winter 定：人不好画就别硬凑） |
| `extra13-rings.py` | 番外十三《Next of Kin》 | 深色绒布上四枚戒指。**她的两枚叠起来是满月，他们各自那枚是半月**（一上弦、一下弦）；内圈刻 `SAM BELL · SARANG` |

## 怎么用

```bash
python3 extra13-rings.py          # 在当前目录生成 rings.svg
```

看效果（容器里没装 Playwright 的 python 包，直接用那个 Chromium）：

```bash
cat > /tmp/c.html <<'H'
<html><body style="margin:0;background:#000"><img src="rings.svg" style="width:1000px;display:block"></body></html>
H
/opt/pw-browsers/chromium-1194/chrome-linux/chrome --headless --disable-gpu --no-sandbox \
  --hide-scrollbars --window-size=1000,622 --screenshot=out.png "file:///tmp/c.html"
```

改完把新的 SVG 换进对应那篇正文里的 `<figure>` 块即可（正文里的 `<svg>` 开标签上
多挂了一段内联样式：`display:block;width:100%;height:auto;…`，替换时记得带上）。

## 画这类图的两条经验（都是 Winter 当场否掉换来的）

1. **人形能不画就不画。** 三个人躺着看舷窗那版试过三种画法，都像一堆黑色的团。
   她的原话：「人不好画的话就只画舷窗之类的制造氛围感吧，不然要卡死了。」
2. **形状要靠「明暗」而不是「缺口」来表达。** 戒指上的半月，第一版是把圆切掉一半，
   看着像「被咬了一口的圆」；改成**月相**（整颗都是圆的，一半亮一半暗）立刻就对了。
