#!/usr/bin/env python3
"""封面与标题 A/B：pick the sharpest candidate frames from a video, render several title
variants on them, and export cover files + one comparison sheet.

  python cover_ab.py out/video.mp4 --images build/still00.png build/still04.png --titles "..."   # clean stills, no burned subs
  python cover_ab.py out/video.mp4 --titles "冰水撑不到中午？|24 小时还有冰|通勤包里不漏水" \
      --ratio 3:4 --outdir out/covers
Prefer clean stills (--images): frames from the final video already carry subtitles.
Outputs cover_A.jpg, cover_B.jpg ... and ab_sheet.jpg (label each variant when you post the test).
"""
import argparse, glob, os, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

FONT_GLOBS = ["/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc", "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
              "/usr/share/fonts/**/NotoSansCJK*Bold*", "/System/Library/Fonts/PingFang.ttc", "C:/Windows/Fonts/msyhbd.ttc"]
STYLES = [  # text fill, stroke, band
    ((255, 221, 0), (0, 0, 0), None),
    ((255, 255, 255), (220, 30, 60), None),
    ((20, 20, 20), None, (255, 221, 0)),
    ((255, 255, 255), (0, 0, 0), (0, 0, 0, 140)),
]


def find_font(user=None):
    if user:
        return user
    for g in FONT_GLOBS:
        h = glob.glob(g, recursive=True)
        if h:
            return h[0]
    raise SystemExit("no CJK font; pass --font")


def sharpness(im):
    g = np.asarray(im.convert("L"), dtype=np.float32)
    lap = g[1:-1, 1:-1] * 4 - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:]
    return float(lap.var())


def candidates(video, n=12, keep=4, tmpdir="build/cover_frames"):
    os.makedirs(tmpdir, exist_ok=True)
    d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video]))
    frames = []
    for i in range(n):
        t = d * (i + 0.5) / n; f = os.path.join(tmpdir, f"c{i:02d}.png")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.2f}", "-i", video, "-frames:v", "1", f], check=True)
        im = Image.open(f).convert("RGB"); frames.append((sharpness(im), t, im))
    frames.sort(key=lambda x: -x[0])
    return frames[:keep]


def wrap(d, text, font, maxw):
    """Greedy CJK-aware wrap; pull one char back if the last line would be a single orphan."""
    lines, cur = [], ""
    for ch in text:
        if d.textlength(cur + ch, font=font) > maxw and cur and ch not in "，。！？、：；）」』!?,.":
            lines.append(cur); cur = ch
        else:
            cur += ch
    if cur:
        lines.append(cur)
    # Avoid a lonely last character (e.g. "…找到" / "了") when the previous line can spare one.
    if len(lines) >= 2 and len(lines[-1]) == 1 and len(lines[-2]) >= 3:
        lines[-1] = lines[-2][-1] + lines[-1]
        lines[-2] = lines[-2][:-1]
    return lines


def render(frame, title, ratio, style, fontpath, w=1080):
    """Draw a multi-line title on a cover frame.

    Line height uses real font metrics (+ stroke + gap) so wrapped CJK lines
    never overlap. The text block is vertically centered in the upper third;
    solid / translucent bands size themselves to the actual line count.
    """
    rw, rh = map(int, ratio.split(":")); h = int(w * rh / rw)
    im = ImageOps.fit(frame, (w, h), Image.LANCZOS, centering=(0.5, 0.4)).convert("RGBA")
    fill, stroke, band = STYLES[style % len(STYLES)]
    size = int(w * 0.11)
    f = ImageFont.truetype(fontpath, size, index=2 if fontpath.endswith(".ttc") else 0)
    probe = ImageDraw.Draw(Image.new("RGBA", (w, h)))
    lines = wrap(probe, title, f, w * 0.86) or [title]
    stroke_w = int(size * 0.08) if stroke else 0
    ascent, descent = f.getmetrics()
    # Ink height of one line (glyph box + stroke). Old bug: lh = 1.18*size < ascent+descent → 叠字.
    ink = ascent + descent + 2 * stroke_w
    gap = max(int(size * 0.28), int(ink * 0.18))  # clear air between lines
    lh = ink + gap
    # Height of the drawn block: (n-1) steps of lh, plus the last line's ink
    block_h = ink + lh * (len(lines) - 1) if lines else ink
    # Vertically center the title block in the upper third of the cover
    upper = int(h * 0.42)
    y0 = max(int(h * 0.04), (upper - block_h) // 2)
    pad_y = max(int(size * 0.28), stroke_w + int(size * 0.12))
    if band:
        overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        top = max(0, y0 - pad_y)
        bot = min(h, y0 + block_h + pad_y)
        od.rectangle([0, top, w, bot], fill=band)
        im = Image.alpha_composite(im, overlay)
    d = ImageDraw.Draw(im)
    for i, ln in enumerate(lines):
        tw = d.textlength(ln, font=f)
        d.text(((w - tw) / 2, y0 + i * lh), ln, font=f, fill=fill,
               stroke_width=stroke_w, stroke_fill=stroke)
    return im.convert("RGB")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video"); ap.add_argument("--titles", required=True, help="variants separated by |")
    ap.add_argument("--ratio", default="3:4"); ap.add_argument("--outdir", default="out/covers")
    ap.add_argument("--frame-time", type=float, help="force a frame time instead of auto-picking")
    ap.add_argument("--images", nargs="+", help="use clean stills (e.g. build/still*.png, product photos) instead of video frames")
    ap.add_argument("--font")
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True); fp = find_font(a.font)
    titles = [t.strip() for t in a.titles.split("|") if t.strip()]
    if a.images:
        frames = sorted(((sharpness(Image.open(p).convert("RGB")), 0.0, Image.open(p).convert("RGB")) for p in a.images),
                        key=lambda x: -x[0])
    elif a.frame_time is not None:
        f = os.path.join(a.outdir, "_frame.png")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(a.frame_time), "-i", a.video, "-frames:v", "1", f], check=True)
        frames = [(0, a.frame_time, Image.open(f).convert("RGB"))]
    else:
        frames = candidates(a.video)
    outs = []
    for i, t in enumerate(titles):
        label = chr(65 + i)
        _, ft, fr = frames[i % len(frames)]
        im = render(fr, t, a.ratio, i, fp)
        p = os.path.join(a.outdir, f"cover_{label}.jpg"); im.save(p, quality=92); outs.append((label, t, ft, im))
        print(f"cover_{label}.jpg  frame@{ft:.1f}s  {t}")
    tw = 360; th = int(tw * outs[0][3].height / outs[0][3].width); gap = 16
    sheet = Image.new("RGB", (len(outs) * (tw + gap) + gap, th + 2 * gap + 50), (245, 245, 245))
    d = ImageDraw.Draw(sheet); lf = ImageFont.truetype(fp, 30, index=2 if fp.endswith(".ttc") else 0)
    for k, (label, t, _, im) in enumerate(outs):
        x = gap + k * (tw + gap); sheet.paste(im.resize((tw, th)), (x, gap))
        d.text((x, gap + th + 8), f"{label}", font=lf, fill=(30, 30, 30))
    sheet.save(os.path.join(a.outdir, "ab_sheet.jpg"), quality=90)
    print("sheet ->", os.path.join(a.outdir, "ab_sheet.jpg"))


if __name__ == "__main__":
    main()
