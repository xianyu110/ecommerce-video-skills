#!/usr/bin/env python3
"""README/preview helpers: an optimised GIF and a frame gallery from a video.

  python preview.py out/video.mp4 --gif out/preview.gif --width 360 --fps 12 --max-mb 8
  python preview.py out/video.mp4 --gallery out/gallery.jpg --frames 6
"""
import argparse, os, subprocess


def duration(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]))


def make_gif(src, out, width=360, fps=12, max_mb=8.0):
    for w, f in [(width, fps), (int(width * .85), fps), (int(width * .75), max(8, fps - 3)), (int(width * .6), 8)]:
        vf = (f"fps={f},scale={w}:-2:flags=lanczos,split[a][b];[a]palettegen=max_colors=128:stats_mode=diff[p];"
              f"[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-vf", vf, "-loop", "0", out], check=True)
        mb = os.path.getsize(out) / 1e6
        print(f"gif {w}px {f}fps -> {mb:.2f} MB")
        if mb <= max_mb:
            return out
    print("warning: GIF still above limit")
    return out


def make_gallery(src, out, n=6, thumb_w=270, cols=None):
    from PIL import Image
    d = duration(src); cols = cols or n; tmpl = out + ".%02d.png"; ims = []
    for i in range(n):
        t = d * (i + 0.5) / n
        f = tmpl % i
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.2f}", "-i", src, "-frames:v", "1",
                        "-vf", f"scale={thumb_w}:-2", f], check=True)
        ims.append(Image.open(f).convert("RGB")); os.remove(f)
    gap = 12; rows = (n + cols - 1) // cols; tw, th = ims[0].size
    sheet = Image.new("RGB", (cols * tw + (cols + 1) * gap, rows * th + (rows + 1) * gap), (255, 255, 255))
    for i, im in enumerate(ims):
        sheet.paste(im, (gap + (i % cols) * (tw + gap), gap + (i // cols) * (th + gap)))
    sheet.save(out, quality=88)
    print("gallery ->", out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video"); ap.add_argument("--gif"); ap.add_argument("--gallery")
    ap.add_argument("--width", type=int, default=360); ap.add_argument("--fps", type=int, default=12)
    ap.add_argument("--max-mb", type=float, default=8.0); ap.add_argument("--frames", type=int, default=6)
    a = ap.parse_args()
    if a.gif:
        make_gif(a.video, a.gif, a.width, a.fps, a.max_mb)
    if a.gallery:
        make_gallery(a.video, a.gallery, a.frames)
