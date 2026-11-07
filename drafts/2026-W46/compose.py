#!/usr/bin/env python3
"""Pre-composites for W46 (whole-photo school composites, product composites/cards).
Rules from 06: school photos never cropped – blurred darkened copy as background, whole photo in a
1080x640 box with its bottom at y=1400 (reel), credit inside the photo's bottom-right corner."""
from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageFont

MEDIA = Path("/home/claude/media/media")
OUT = Path("/home/claude/renderer/assets/media/w46")
OUT.mkdir(parents=True, exist_ok=True)
FONT = "/home/claude/renderer/assets/fonts/Outfit-Medium.ttf"
SIZES = {"reel": (1080, 1920), "post": (1080, 1350), "square": (1080, 1080)}


def cover(im, W, H):
    r = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - H) // 2
    return im.crop((x, y, x + W, y + H))


def blurred_bg(im, W, H, dark=0.55, blur=40):
    bg = cover(im, W, H).filter(ImageFilter.GaussianBlur(blur))
    return ImageEnhance.Brightness(bg).enhance(dark)


def school(src, credit, name, fmt="reel"):
    W, H = SIZES[fmt]
    im = Image.open(MEDIA / src).convert("RGB")
    canvas = blurred_bg(im, W, H)
    if fmt == "reel":
        bw, bh, bottom = 1080, 640, 1400
    else:  # post 4:5
        bw, bh, bottom = 1080, 600, 1250
    r = min(bw / im.width, bh / im.height)
    ph = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    x, y = (W - ph.width) // 2, bottom - ph.height
    canvas.paste(ph, (x, y))
    d = ImageDraw.Draw(canvas)
    f = ImageFont.truetype(FONT, 20 if fmt == "reel" else 19)
    tw = d.textlength(credit, font=f)
    tx, ty = x + ph.width - tw - 14, y + ph.height - 34
    d.rectangle([tx - 8, ty - 4, tx + tw + 8, ty + 26], fill=(0, 0, 0))
    d.text((tx, ty), credit, font=f, fill=(255, 255, 255))
    out = OUT / f"{name}-{fmt}.jpg"
    canvas.save(out, quality=94)
    return out


def product(src, name, fmt="reel", center_y=None, width=1080):
    """Native product slide: blurred studio photo as background, product photo full width."""
    W, H = SIZES[fmt]
    im = Image.open(MEDIA / src).convert("RGB")
    canvas = blurred_bg(im, W, H, dark=0.92, blur=30)
    r = width / im.width
    ph = im.resize((width, round(im.height * r)), Image.LANCZOS)
    cy = center_y or round(H * 0.56)
    canvas.paste(ph, ((W - width) // 2, cy - ph.height // 2))
    out = OUT / f"{name}-{fmt}.jpg"
    canvas.save(out, quality=94)
    return out


def card(src, name, fmt="post", size=820, top=110, bg=(0xF5, 0xEC, 0xF7), radius=36):
    """Branded product card: tint background, rounded product photo near the top; text goes below."""
    W, H = SIZES[fmt]
    canvas = Image.new("RGB", (W, H), bg)
    im = cover(Image.open(MEDIA / src).convert("RGB"), size, size)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, size, size], radius=radius, fill=255)
    canvas.paste(im, ((W - size) // 2, top), mask)
    out = OUT / f"{name}-{fmt}.jpg"
    canvas.save(out, quality=94)
    return out


if __name__ == "__main__":
    S = [  # file, credit (as on W45-02), name
        ("skolor/katedralskolan-lund.jpg", "Foto: Dguendel / Wikimedia Commons, CC BY 4.0", "lund"),
        ("skolor/katedralskolan-uppsala.jpg", "Foto: Wazzaa97 / Wikimedia Commons, CC BY-SA 3.0", "uppsala"),
        ("skolor/malmo-latinskola.jpg", "Foto: jorchr / Wikimedia Commons, CC BY-SA 3.0", "malmo"),
        ("skolor/rudbeckianska-vasteras.jpg", "Foto: Christer Johansson / Wikimedia Commons, CC BY-SA 2.5", "vasteras"),
        ("skolor/katedralskolan-linkoping-1915.jpg", "Foto från 1915, okänd fotograf / Wikimedia Commons (public domain)", "linkoping"),
        ("skolor/hvitfeldtska-goteborg.jpg", "Foto: Historiker / Wikimedia Commons, CC BY-SA 3.0", "goteborg"),
    ]
    for src, cr, n in S:
        print(school(src, cr, n, "post"))
    P = {
        "herrgardsljus": "produkter/herrgardsljus/herrgardsljus-studio-01.jpg",
        "tryfflar": "produkter/havssaltstryfflar/havssaltstryfflar-studio-02.jpg",
        "olivolja": "produkter/olivolja/olivolja-studio-01.jpg",
        "mandelskorpor": "produkter/mandelskorpor/mandelskorpor-studio-01.jpg",
        "kokskit": "produkter/haxan-kokskit/haxan-kokskit-studio-01.jpg",
    }
    for n in ("herrgardsljus", "tryfflar"):
        print(product(P[n], n, "reel"))
    for n, src in P.items():
        print(card(src, n, "post"))
        print(card(src, n, "square", size=640, top=90))
