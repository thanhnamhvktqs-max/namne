# -*- coding: utf-8 -*-
"""Trich va chuan bi hinh anh tu bo slide goc.

    python prep_assets.py <slide_goc.pptx> <thu_muc_ra>

- Lay anh goc (logo, anh san pham, mach, CAD, giao dien, do thi theo thoi gian)
- Tach nen trang cua anh render CAD (to loang tu bien, khong lam thung chi tiet bac)
- Phong to anh nho (anh chup gimbal, mach that, giao dien) bang Lanczos + lam net nhe
"""
import os
import sys
import zipfile
from collections import deque

from PIL import Image, ImageFilter

MEDIA = {
    "logo": "image4.png",
    "gimbal_photo": "image9.jpg",
    "gimbal_illus": "image10.png",
    "stm32": "image16.png",
    "icm20948": "image17.png",
    "ms3506": "image18.png",
    "usbttl": "image19.jpeg",
    "sch_mcu": "image20.png",
    "sch_rs485": "image21.png",
    "sch_power": "image22.png",
    "pcb_layout": "image23.png",
    "pcb_3d": "image24.png",
    "pcb_real": "image25.jpeg",
    "cad_2d": "image26.png",
    "cad_exploded": "image58.png",
    "cad_render": "image28.png",
    "gui": "image37.jpeg",
    "fig_model": "image36.png",
    "fig_step": "image39.png",
    "fig_kp": "image38.png",
    "fig_limit": "image40.png",
    "fig_stop": "image41.png",
    "fig_shaping": "image42.png",
}


def remove_white_bg(im, tol=18, feather=1.2):
    """To loang tu bien anh: diem gan trang lien thong voi bien -> trong suot."""
    im = im.convert("RGBA")
    w, h = im.size
    px = im.load()
    mask = Image.new("L", (w, h), 255)
    mp = mask.load()
    seen = bytearray(w * h)
    dq = deque()

    def near_white(p):
        r, g, b, a = p
        return a < 10 or (r > 255 - tol and g > 255 - tol and b > 255 - tol)

    for x in range(w):
        for y in (0, h - 1):
            dq.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            dq.append((x, y))
    while dq:
        x, y = dq.popleft()
        i = y * w + x
        if seen[i]:
            continue
        seen[i] = 1
        if not near_white(px[x, y]):
            continue
        mp[x, y] = 0
        if x > 0:
            dq.append((x - 1, y))
        if x < w - 1:
            dq.append((x + 1, y))
        if y > 0:
            dq.append((x, y - 1))
        if y < h - 1:
            dq.append((x, y + 1))
    mask = mask.filter(ImageFilter.GaussianBlur(feather))
    im.putalpha(mask)
    return im


def upscale(im, factor, sharpen=True):
    im = im.resize((int(im.size[0] * factor), int(im.size[1] * factor)), Image.LANCZOS)
    if sharpen:
        im = im.filter(ImageFilter.UnsharpMask(radius=1.6, percent=60, threshold=2))
    return im


def main(src, out):
    os.makedirs(out, exist_ok=True)
    z = zipfile.ZipFile(src)
    raw = {}
    for key, fn in MEDIA.items():
        data = z.read("ppt/media/" + fn)
        ext = os.path.splitext(fn)[1]
        p = os.path.join(out, key + "_raw" + ext)
        with open(p, "wb") as f:
            f.write(data)
        raw[key] = p

    def save(key, im, fmt="PNG", **kw):
        p = os.path.join(out, key + (".png" if fmt == "PNG" else ".jpg"))
        if fmt == "JPEG":
            im = im.convert("RGB")
        im.save(p, fmt, **kw)
        return p

    # anh dung nguyen ban
    for key in ["logo", "stm32", "icm20948", "ms3506", "sch_mcu", "sch_rs485", "sch_power",
                "pcb_layout", "pcb_3d", "cad_2d", "cad_exploded", "fig_model", "fig_step",
                "fig_kp", "fig_limit", "fig_stop", "fig_shaping"]:
        save(key, Image.open(raw[key]).convert("RGBA" if key == "logo" else "RGB"))
    # tach nen anh render CAD va anh linh kien nen trang
    save("cad_render_cut", remove_white_bg(Image.open(raw["cad_render"])))
    save("cad_render", Image.open(raw["cad_render"]).convert("RGB"))
    # phong to anh nho
    save("gimbal_photo", upscale(Image.open(raw["gimbal_photo"]).convert("RGB"), 2.0), "JPEG", quality=93)
    save("pcb_real", upscale(Image.open(raw["pcb_real"]).convert("RGB"), 2.0), "JPEG", quality=93)
    save("usbttl", upscale(Image.open(raw["usbttl"]).convert("RGB"), 1.5), "JPEG", quality=92)
    save("gui", upscale(Image.open(raw["gui"]).convert("RGB"), 1.5, sharpen=False), "JPEG", quality=94)
    ill = Image.open(raw["gimbal_illus"]).convert("RGB")
    ill = ill.crop((0, 70, ill.size[0], ill.size[1]))  # bo dai "Chuoi dong hoc" (ve lai ban dia)
    save("gimbal_illus", upscale(ill, 1.5))
    for p in raw.values():
        os.remove(p)
    print("ok", sorted(os.listdir(out)))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
