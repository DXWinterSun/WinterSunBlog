#!/usr/bin/env python3
"""把模拟出来的小组件 PNG 贴到 Winter 发来的桌面截图上，做「换上之后」的效果图。

    python3 tools/widget-sim/compose.py 桌面截图.png 输出.png \\
        --put 小组件.png 638 871          # 左上角坐标（截图像素）
        [--label Scriptable 1395]        # 把小组件下面那行 app 名换掉（y = 名字那行的中线）
        [--dots 4 0]                     # 在右边画叠放的翻页小圆点：共几页、当前第几页
        [--clear 630 865 1135 1366]      # 先抹掉原来那个小组件（上下插值补背景）
        [--fill 270 760 870]             # 把 y 从 760 到 870 那条缝用左右两边的背景补上（拿掉大组件时用）

--put 可以给好几次。坐标都是截图原尺寸的像素（3 倍屏：1 pt = 3 px）。
"""
import argparse
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT_CANDIDATES = [
    "/root/.fonts/Inter%5Bopsz,wght%5D.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def font(size):
    for f in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            pass
    return ImageFont.load_default()


def inpaint_rows(im, y0, y1, x0=0, x1=None):
    """y0..y1 之间的每一列，用上下两行的颜色线性插值补平（盖掉原来的字）。"""
    x1 = im.width if x1 is None else x1
    px = im.load()
    for x in range(x0, x1):
        a, b = px[x, y0 - 1], px[x, y1 + 1]
        n = y1 - y0 + 2
        for k, y in enumerate(range(y0, y1 + 1), 1):
            t = k / n
            px[x, y] = tuple(round(a[i] * (1 - t) + b[i] * t) for i in range(3)) + (255,)


def inpaint_cols(im, y0, y1, xl, xr):
    """y0..y1 这几行，用左边 xl 处、右边 xr 处的颜色横向插值补平。"""
    px = im.load()
    for y in range(y0, y1 + 1):
        a, b = px[xl, y], px[xr, y]
        for x in range(im.width):
            t = min(max((x - xl) / (xr - xl), 0), 1)
            px[x, y] = tuple(round(a[i] * (1 - t) + b[i] * t) for i in range(3)) + (255,)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("out")
    ap.add_argument("--put", nargs=3, action="append", default=[], metavar=("PNG", "X", "Y"))
    ap.add_argument("--label", nargs=2, action="append", default=[], metavar=("TEXT", "Y"))
    ap.add_argument("--dots", nargs=2, type=int, metavar=("N", "CUR"))
    ap.add_argument("--clear", nargs=4, type=int, action="append", default=[], metavar=("X0", "Y0", "X1", "Y1"),
                    help="先把这块（原来那个小组件）用上下的背景补平，免得新组件圆角外露出旧的白边")
    ap.add_argument("--fill", nargs=3, type=int, action="append", default=[], metavar=("Y0", "Y1", "_"))
    ap.add_argument("--scale", type=float, default=1.0, help="输出时缩放")
    a = ap.parse_args()

    im = Image.open(a.base).convert("RGBA")
    for x0, y0, x1, y1 in a.clear:
        inpaint_rows(im, y0, y1, x0, x1)
    for y0, y1, _ in a.fill:
        inpaint_cols(im, y0, y1, 40, im.width - 41)
    placed = []
    for path, x, y in a.put:
        w = Image.open(path).convert("RGBA")
        x, y = int(x), int(y)
        im.alpha_composite(w, (x, y))
        placed.append((x, y, w.width, w.height))
    for text, ly in a.label:
        ly = int(ly)
        x, y, w, h = placed[-1]
        inpaint_rows(im, ly - 24, ly + 24, x, x + w)
        d = ImageDraw.Draw(im)
        f = font(36)
        tw = d.textlength(text, font=f)
        shadow = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(shadow).text((x + w / 2 - tw / 2, ly - 21), text, font=f, fill=(0, 0, 0, 90))
        im.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(3)))
        d.text((x + w / 2 - tw / 2, ly - 22), text, font=f, fill=(255, 255, 255, 255))
    if a.dots:
        n, cur = a.dots
        x, y, w, h = placed[-1]
        d = ImageDraw.Draw(im)
        cx = x + w + 30
        gap = 22
        top = y + h / 2 - (n - 1) * gap / 2
        for k in range(n):
            r = 7 if k == cur else 6
            fill = (255, 255, 255, 240) if k == cur else (255, 255, 255, 120)
            d.ellipse((cx - r, top + k * gap - r, cx + r, top + k * gap + r), fill=fill)
    if a.scale != 1:
        im = im.resize((round(im.width * a.scale), round(im.height * a.scale)), Image.LANCZOS)
    im.convert("RGB").save(a.out, quality=92)


if __name__ == "__main__":
    main()
