#!/usr/bin/env python3
"""PIL product cards for short videos — end cards, selling-point cards, or a full demo set
when you have no footage yet.  Text is rendered locally, so Chinese is always crisp.

  python make_cards.py --image white-bg.webp --name "AURA 保温杯" \
      --points "24h 保冰|竹木盖防漏|运动 · 通勤 · 露营" --cta "点击下方小黄车" -o end.png
  python make_cards.py --name "示例商品" --points "卖点一|卖点二" -o card.png   # no image -> placeholder product

Options: --size 1080x1920  --theme sage|night|peach|mono  --font /path/to/CJK.ttf
"""
import argparse, glob, os
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

THEMES = {  # top, bottom, accent, text
    "sage": ((232, 240, 230), (196, 214, 196), (64, 104, 78), (24, 40, 30)),
    "night": ((14, 18, 32), (34, 44, 74), (250, 204, 21), (241, 245, 249)),
    "peach": ((255, 240, 228), (255, 206, 180), (232, 84, 60), (60, 30, 20)),
    "mono": ((248, 248, 248), (222, 222, 222), (20, 20, 20), (20, 20, 20)),
}
FONT_GLOBS = ["/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", "/usr/share/fonts/**/NotoSansCJK*Bold*",
              "/usr/share/fonts/**/SourceHanSans*Bold*", "/System/Library/Fonts/PingFang.ttc",
              "C:/Windows/Fonts/msyhbd.ttc", "/usr/share/fonts/**/wqy-zenhei.ttc"]


def find_font(user=None):
    if user:
        return user
    for g in FONT_GLOBS:
        hits = glob.glob(g, recursive=True)
        if hits:
            return hits[0]
    raise SystemExit("No CJK font found; pass --font /path/to/font.ttf")


def font(path, size):
    idx = 2 if path.endswith("NotoSansCJK-Bold.ttc") else 0  # index 2 = SC in Noto CJK collections
    return ImageFont.truetype(path, size, index=idx)


def gradient(w, h, c1, c2):
    g = Image.new("RGB", (1, h))
    for y in range(h):
        k = y / (h - 1)
        g.putpixel((0, y), tuple(int(c1[i] * (1 - k) + c2[i] * k) for i in range(3)))
    return g.resize((w, h))


def center(d, y, text, f, fill, w):
    b = d.textbbox((0, 0), text, font=f)
    d.text(((w - (b[2] - b[0])) / 2 - b[0], y), text, font=f, fill=fill)
    return b[3] - b[1]


def card(name, points, cta=None, image=None, size=(1080, 1920), theme="sage", fontpath=None, kicker=None):
    w, h = size; top, bot, acc, txt = THEMES[theme]
    fp = find_font(fontpath)
    img = gradient(w, h, top, bot); d = ImageDraw.Draw(img)
    # product panel
    pw = int(w * 0.54); ph = pw
    px, py = (w - pw) // 2, int(h * 0.10)
    sh = Image.new("RGBA", (pw + 160, ph + 160), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([80, 100, pw + 80, ph + 100], 48, fill=(0, 0, 0, 90))
    img.paste(sh.filter(ImageFilter.GaussianBlur(30)), (px - 80, py - 80), sh.filter(ImageFilter.GaussianBlur(30)))
    panel = Image.new("RGB", (pw, ph), (255, 255, 255))
    if image:
        prod = Image.open(image).convert("RGB")
        prod = ImageOps.contain(prod, (int(pw * 0.92), int(ph * 0.92)), Image.LANCZOS)
        panel.paste(prod, ((pw - prod.width) // 2, (ph - prod.height) // 2))
    else:  # placeholder bottle silhouette
        pd = ImageDraw.Draw(panel)
        pd.rounded_rectangle([pw * .38, ph * .22, pw * .62, ph * .86], 40, fill=acc)
        pd.rounded_rectangle([pw * .40, ph * .12, pw * .60, ph * .24], 18, fill=(196, 160, 110))
    m = Image.new("L", (pw, ph), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, pw - 1, ph - 1], 48, fill=255)
    img.paste(panel, (px, py), m)
    y = py + ph + int(h * 0.035)
    if kicker:
        y += center(d, y, kicker, font(fp, int(h * 0.02)), acc, w) + int(h * 0.015)
    y += center(d, y, name, font(fp, int(h * 0.045)), txt, w) + int(h * 0.03)
    fpnt = font(fp, int(h * 0.024))
    for p in points:
        b = d.textbbox((0, 0), p, font=fpnt); tw = b[2] - b[0]
        x = (w - tw) / 2 + 22
        d.ellipse([x - 44, y + 19, x - 22, y + 41], fill=acc)
        d.text((x, y - b[1] // 2), p, font=fpnt, fill=txt)
        y += int(h * 0.040)
    if cta:
        fc = font(fp, int(h * 0.026)); b = d.textbbox((0, 0), cta, font=fc)
        bw, bh = b[2] - b[0] + 120, int(h * 0.055)
        bx, by = (w - bw) // 2, int(h * 0.865) - bh
        d.rounded_rectangle([bx, by, bx + bw, by + bh], bh // 2, fill=acc)
        d.text(((w - (b[2] - b[0])) / 2 - b[0], by + (bh - (b[3] - b[1])) / 2 - b[1]), cta, font=fc,
               fill=(255, 255, 255) if theme != "night" else (14, 18, 32))
    return img


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", required=True)
    ap.add_argument("--points", default="", help="selling points separated by |")
    ap.add_argument("--cta"); ap.add_argument("--kicker"); ap.add_argument("--image")
    ap.add_argument("--size", default="1080x1920"); ap.add_argument("--theme", default="sage", choices=THEMES)
    ap.add_argument("--font"); ap.add_argument("-o", "--out", default="card.png")
    a = ap.parse_args()
    w, h = map(int, a.size.lower().split("x"))
    pts = [p.strip() for p in a.points.split("|") if p.strip()]
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    card(a.name, pts, a.cta, a.image, (w, h), a.theme, a.font, a.kicker).save(a.out)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
