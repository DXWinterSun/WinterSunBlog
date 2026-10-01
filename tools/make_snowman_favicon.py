#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""画网页标签上那只小雪人 ⛄（Winter 2026-09-23 挑的图标）。

生成两个文件：
    favicon.ico            —— 16 / 32 / 48 三种尺寸打包在一个 ico 里
    images/favicon-180.png —— iPhone 加到主屏幕时那张

配色跟站点默认色「晴雪」同源（_sass/0-settings/_colors.scss）：
底是冰蓝，雪人是雪白，帽子是墨蓝，鼻子是冬阳金。

跑法：
    pip install Pillow
    python3 tools/make_snowman_favicon.py
"""

from PIL import Image, ImageDraw

# ── 晴雪配色（与 _colors.scss 同源）────────────────────────────────
ICE      = (63, 158, 203, 255)    # #3f9ecb 晴空冰蓝（底）
ICE_DEEP = (44, 128, 169, 255)    # #2c80a9 暗一档，用来描边
SNOW     = (255, 255, 255, 255)   # 雪
INK      = (20, 33, 46, 255)      # #14212e 墨蓝（帽子 / 眼睛 / 手臂）
GOLD     = (233, 180, 81, 255)    # #e9b451 冬阳（胡萝卜鼻子）

S = 512                            # 先画大的，再缩小，边缘才干净
R = S // 8                         # 圆角半径


def draw_snowman(size_hint):
    """size_hint 是最终尺寸，用来决定细节留多少——16px 上眼睛和纽扣只剩一团脏点。"""
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # 圆角方块底
    d.rounded_rectangle([0, 0, S - 1, S - 1], radius=R, fill=ICE)

    tiny = size_hint <= 20        # 极小尺寸：只留轮廓
    small = size_hint <= 36       # 小尺寸：去掉纽扣和嘴

    # 身子（下面那个大雪球）
    by, br = int(S * 0.700), int(S * 0.230)
    d.ellipse([S // 2 - br, by - br, S // 2 + br, by + br], fill=SNOW)

    # 脑袋。⚠️ 描边用【底色】而不是深色——这样两个雪球之间会被"切"出一道
    # 干净的缝，16px 的标签页上才看得出是「上下两个球」而不是一团白。
    hy, hr = int(S * 0.375), int(S * 0.150)
    ring = int(S * 0.030)
    d.ellipse([S // 2 - hr - ring, hy - hr - ring, S // 2 + hr + ring, hy + hr + ring],
              fill=ICE)
    d.ellipse([S // 2 - hr, hy - hr, S // 2 + hr, hy + hr], fill=SNOW)

    # 帽子：帽檐 + 帽顶
    brim_w, brim_h = int(S * 0.32), int(S * 0.040)
    brim_y = hy - hr - int(S * 0.015)
    d.rounded_rectangle([S // 2 - brim_w, brim_y - brim_h,
                         S // 2 + brim_w, brim_y + brim_h],
                        radius=brim_h, fill=INK)
    top_w, top_h = int(S * 0.195), int(S * 0.145)
    d.rounded_rectangle([S // 2 - top_w, brim_y - top_h,
                         S // 2 + top_w, brim_y],
                        radius=int(S * 0.02), fill=INK)

    if not tiny:
        # 手臂（两根树枝）
        arm_y = int(S * 0.645)
        d.line([S // 2 - br + 6, arm_y, S // 2 - int(S * 0.36), arm_y - int(S * 0.075)],
               fill=INK, width=int(S * 0.028))
        d.line([S // 2 + br - 6, arm_y, S // 2 + int(S * 0.36), arm_y - int(S * 0.075)],
               fill=INK, width=int(S * 0.028))

        # 眼睛
        er = int(S * 0.021)
        for ex in (S // 2 - int(S * 0.055), S // 2 + int(S * 0.055)):
            d.ellipse([ex - er, hy - int(S * 0.028) - er,
                       ex + er, hy - int(S * 0.028) + er], fill=INK)

        # 胡萝卜鼻子
        nx, ny = S // 2, hy + int(S * 0.012)
        d.polygon([(nx, ny - int(S * 0.018)), (nx + int(S * 0.10), ny + int(S * 0.005)),
                   (nx, ny + int(S * 0.028))], fill=GOLD)

    if not small:
        # 纽扣
        cr = int(S * 0.019)
        for cy in (int(S * 0.615), int(S * 0.700), int(S * 0.785)):
            d.ellipse([S // 2 - cr, cy - cr, S // 2 + cr, cy + cr], fill=ICE_DEEP)

    return img


def main():
    sizes = [16, 32, 48]
    frames = [draw_snowman(n).resize((n, n), Image.LANCZOS) for n in sizes]
    frames[0].save("favicon.ico", format="ICO",
                   sizes=[(n, n) for n in sizes],
                   append_images=frames[1:])
    draw_snowman(180).resize((180, 180), Image.LANCZOS).save(
        "images/favicon-180.png", format="PNG", optimize=True)
    print("favicon.ico + images/favicon-180.png 已重画 ⛄")


if __name__ == "__main__":
    main()
