#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
封面「对脸」—— 自动找出每张图里人脸的位置，算好裁切锚点，写进 _data/image_focus.yml。

为什么要它（Winter 2026-09-19）：
    「点进去的时候，配图是方形的，需要每次都截到人的话，需要对每张图核对人的
      具体位置，这好做吗？」
    ——能，而且不用人工。这个脚本用 OpenCV 的 YuNet 人脸模型扫一遍 images/，
    把最大那张脸的中心记下来，再按「方形裁切」的真实数学算出 background-position，
    模板直接用。认不出脸的（手绘封面、风景图）留空，模板回退到原来的居中偏上。

    ⚠️ 为什么不能直接把「脸在 19%」写成 background-position: 19%：
    CSS 的百分比是「图上 19% 的点对齐容器 19% 的点」，不是「把这一点摆到正中」。
    图越宽、脸越靠边，偏差越大——Billy Bickle 那张（脸在最左边）就是这么被切掉
    半张脸的。正确解见下面的 crop_pos()。

用法：
    python3 tools/face_focus.py              # 扫描并写入 _data/image_focus.yml
    python3 tools/face_focus.py --check      # 只看有没有变化（CI 用），不写文件
    python3 tools/face_focus.py --report     # 列出没认出脸的图

手动微调：
    某张图自动裁得不好看时，在 _data/image_focus.yml 里把那一条改掉，并加一行
    `manual: true`。下次重跑脚本会原样保留这一条，不会覆盖你的手改。
"""

import os
import sys
import glob
import math

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(ROOT, "images")
OUT = os.path.join(ROOT, "_data", "image_focus.yml")
MODEL = os.path.join(ROOT, "tools", "models", "face_detection_yunet_2023mar.onnx")
EXTS = (".jpg", ".jpeg", ".png", ".webp")

# 模板里真正用到的容器形状 → 预先算好各自的 background-position
# （Liquid 算不动这种数学，所以在这里一次算完写进数据文件。）
SHAPES = {
    "sq": 1.0,          # 正方形：「那一天」页面里的系列小图
    "card": 16 / 10,    # 首页 / 相关文章卡片
    "banner": 16 / 6.5,  # 系列首页的宽封面
}


def crop_pos(fx, fy, img_w, img_h, box_ar):
    """算出 background-size: cover 时，要把脸摆到正中该用的 background-position。

    fx / fy 是脸中心在图上的位置（0–1）。box_ar 是容器的宽高比。
    推导：图按 cover 放进容器后会有一个方向溢出；设溢出方向上
    「缩放后的图长 / 容器长」= s，则百分比 p 满足
        p * (s - 1) * 容器长 = fx * s * 容器长 - 容器长 / 2
    解得 p = (fx * s - 0.5) / (s - 1)，再夹到 0–1。
    """
    img_ar = img_w / img_h
    s = img_ar / box_ar if img_ar > box_ar else box_ar / img_ar
    if s < 1.05:
        # 图和容器几乎一样的形状：几乎没东西被切掉，挪不挪都一样，居中就好
        return "50% 50%"
    if img_ar > box_ar:                      # 图更宽 → 左右溢出，只能横向挪
        s = img_ar / box_ar
        p = (fx * s - 0.5) / (s - 1)
        return "%.0f%% 50%%" % (max(0.0, min(1.0, p)) * 100)
    s = box_ar / img_ar                      # 图更高 → 上下溢出，只能纵向挪
    p = (fy * s - 0.5) / (s - 1)
    return "50%% %.0f%%" % (max(0.0, min(1.0, p)) * 100)


def load_existing():
    """读回上一次的结果，保住手改过（manual: true）的条目。"""
    if not os.path.exists(OUT):
        return {}
    try:
        import yaml
        return yaml.safe_load(open(OUT, encoding="utf-8")) or {}
    except Exception:
        return {}


def detect_all():
    import cv2
    if not os.path.exists(MODEL):
        sys.exit("[face_focus] 找不到人脸模型：%s" % MODEL)
    det = cv2.FaceDetectorYN.create(MODEL, "", (320, 320), 0.55, 0.3, 5000)
    found, missed = {}, []
    for path in sorted(glob.glob(os.path.join(IMG_DIR, "*"))):
        name = os.path.basename(path)
        if not name.lower().endswith(EXTS):
            continue
        im = cv2.imread(path)
        if im is None:
            missed.append(name)
            continue
        h, w = im.shape[:2]
        scale = 1024 / max(h, w) if max(h, w) > 1024 else 1
        small = cv2.resize(im, (int(w * scale), int(h * scale))) if scale != 1 else im
        H, W = small.shape[:2]
        det.setInputSize((W, H))
        _, faces = det.detect(small)
        if faces is None or len(faces) == 0:
            missed.append(name)
            continue
        f = max(faces, key=lambda f: f[2] * f[3])
        x, y, fw, fh = [float(v) for v in f[:4]]
        fx = (x + fw / 2) / W
        fy = (y + fh / 2) / H
        rec = {
            "x": round(fx * 100, 1),
            "y": round(fy * 100, 1),
            "w": int(w),
            "h": int(h),
            "score": round(float(f[-1]), 2),
        }
        for key, ar in SHAPES.items():
            rec[key] = crop_pos(fx, fy, w, h, ar)
        found[name] = rec
    return found, missed


def render(data):
    lines = [
        "# 封面「对脸」锚点 —— 由 tools/face_focus.py 自动生成，别手改整份文件。",
        "#",
        "# 每一条：x / y 是脸中心在图上的位置（%），w / h 是原图尺寸，",
        "# sq / card / banner 是三种容器形状下该用的 background-position（已按裁切数学算好）。",
        "# 模板用法：{{ site.data.image_focus[文件名].sq | default: '50% 30%' }}",
        "#",
        "# 想手动微调某一张：改掉它的 sq / card / banner，并加一行 manual: true，",
        "# 下次重跑脚本会原样保留这一条。没认出脸的图不在这里，模板自动回退到居中偏上。",
        "",
    ]
    for name in sorted(data):
        rec = data[name]
        lines.append('"%s":' % name.replace('"', '\\"'))
        for key in ("x", "y", "w", "h", "score", "sq", "card", "banner", "manual", "note"):
            if key not in rec:
                continue
            val = rec[key]
            if isinstance(val, str):
                lines.append('  %s: "%s"' % (key, val))
            elif isinstance(val, bool):
                lines.append("  %s: %s" % (key, "true" if val else "false"))
            else:
                lines.append("  %s: %s" % (key, val))
    return "\n".join(lines) + "\n"


def main():
    check = "--check" in sys.argv
    report = "--report" in sys.argv
    old = load_existing()
    found, missed = detect_all()
    merged = {}
    for name, rec in found.items():
        prev = old.get(name) or {}
        merged[name] = prev if prev.get("manual") else rec
    # 手改过、但这次没认出脸的，也留着
    for name, rec in (old or {}).items():
        if rec.get("manual") and name not in merged:
            merged[name] = rec

    text = render(merged)
    same = os.path.exists(OUT) and open(OUT, encoding="utf-8").read() == text
    manual = sum(1 for r in merged.values() if r.get("manual"))
    print("[face_focus] 扫了 %d 张图：%d 张认出了脸（其中 %d 张是手调的），%d 张没有（回退居中）。"
          % (len(found) + len(missed), len(merged), manual, len(missed)))
    if report:
        print("[face_focus] 没认出脸的：")
        for n in missed:
            print("   ·", n)
    if check:
        print("[face_focus] " + ("没有变化。" if same else "有变化，需要重新生成。"))
        return 0 if same else 1
    if same:
        print("[face_focus] 内容没变，不重写文件。")
        return 0
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(text)
    print("[face_focus] 已写入 %s" % os.path.relpath(OUT, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
