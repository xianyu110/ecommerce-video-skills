#!/usr/bin/env python3
"""Re-encode one master video into platform-ready files + a spec report.

  python export_platform.py out/master.mp4 --platform douyin tiktok channels xiaohongshu taobao-main amazon
  python export_platform.py out/master.mp4 --platform all --outdir out/export
  python export_platform.py out/master.mp4 --safe-preview out/safe.png   # overlay typical UI zones on a frame

Presets are conservative *recommended* encodes (H.264 High + AAC 48 kHz, faststart).  Platform limits
change often — the `note` field says what to double-check in the official upload page / seller centre.
Ratio conversion: --mode blur (blurred fill, keeps the whole frame) or --mode crop (centre crop, --focus-y).
"""
import argparse, json, os, subprocess

PRESETS = {
    "douyin":      dict(size=(1080, 1920), fps=30, maxrate="12M", note="抖音：竖版 9:16 推荐；时长/大小上限以创作者中心上传页为准"),
    "tiktok":      dict(size=(1080, 1920), fps=30, maxrate="12M", note="TikTok: 9:16 recommended; check current length/size limits in the upload page"),
    "tiktok-shop": dict(size=(1080, 1920), fps=30, maxrate="12M", note="TikTok Shop 商品/联盟视频：9:16 为主；商品视频规格以 Seller Center 为准"),
    "channels":    dict(size=(1080, 1920), fps=30, maxrate="10M", note="视频号：竖版可发 9:16，信息流预览可能裁切显示，主体与标题放画面中部"),
    "xiaohongshu": dict(size=(1080, 1440), fps=30, maxrate="10M", note="小红书：3:4 在信息流最占屏；9:16 也可，封面建议 3:4"),
    "taobao-main": dict(size=(1080, 1080), fps=30, maxrate="8M", note="淘宝/天猫主图视频：1:1 或 3:4 常用，时长建议短（以千牛后台要求为准）"),
    "taobao-3x4":  dict(size=(1080, 1440), fps=30, maxrate="8M", note="淘宝 3:4 主图视频版本"),
    "amazon":      dict(size=(1920, 1080), fps=30, maxrate="12M", note="Amazon listing video: 16:9 landscape common; check Seller Central video guidelines"),
    "square":      dict(size=(1080, 1080), fps=30, maxrate="8M", note="Generic 1:1 (Shopee/Lazada/feeds)"),
}


def probe(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries",
                                   "stream=codec_type,width,height,r_frame_rate:format=duration,size",
                                   "-of", "json", path])
    j = json.loads(out); v = next(s for s in j["streams"] if s["codec_type"] == "video")
    return dict(w=v["width"], h=v["height"], fps=v["r_frame_rate"], duration=float(j["format"]["duration"]),
                size_mb=round(int(j["format"]["size"]) / 1e6, 2), audio=any(s["codec_type"] == "audio" for s in j["streams"]))


def vf_for(src, w, h, mode, focus_y):
    if abs(src["w"] / src["h"] - w / h) < 0.01:
        return f"scale={w}:{h}:flags=lanczos,setsar=1"
    if mode == "crop":
        return (f"scale={w}:{h}:force_original_aspect_ratio=increase:flags=lanczos,"
                f"crop={w}:{h}:(iw-ow)/2:(ih-oh)*{focus_y},setsar=1")
    return (f"split[a][b];[a]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},boxblur=40:2,"
            f"eq=brightness=-0.06[bg];[b]scale={w}:{h}:force_original_aspect_ratio=decrease:flags=lanczos[fg];"
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1")


def export(src_path, name, p, outdir, mode, focus_y):
    src = probe(src_path); w, h = p["size"]
    out = os.path.join(outdir, f"{os.path.splitext(os.path.basename(src_path))[0]}_{name}.mp4")
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", src_path, "-vf", vf_for(src, w, h, mode, focus_y), "-r", str(p["fps"]),
           "-c:v", "libx264", "-profile:v", "high", "-preset", "medium", "-crf", "20", "-maxrate", p["maxrate"],
           "-bufsize", p["maxrate"].replace("M", "") + "M", "-pix_fmt", "yuv420p", "-movflags", "+faststart"]
    cmd += ["-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2"] if src["audio"] else ["-an"]
    subprocess.run(cmd + [out], check=True)
    info = probe(out)
    return dict(platform=name, file=out, **info, note=p["note"])


def safe_preview(src_path, out, t=1.0):
    """Overlay empirical UI zones (top status bar, right action rail, bottom caption/cart area)."""
    from PIL import Image, ImageDraw
    tmp = out + ".frame.png"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(t), "-i", src_path, "-frames:v", "1", tmp], check=True)
    im = Image.open(tmp).convert("RGBA"); w, h = im.size
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    zones = [((0, 0, w, int(h * 0.09)), "top bar"), ((int(w * 0.85), int(h * 0.35), w, int(h * 0.80)), "action rail"),
             ((0, int(h * 0.78), w, h), "caption / product card / cart")]
    for box, label in zones:
        d.rectangle(box, fill=(255, 0, 80, 90), outline=(255, 0, 80, 220), width=4)
        d.text((box[0] + 16, box[1] + 12), label, fill=(255, 255, 255, 255))
    Image.alpha_composite(im, ov).convert("RGB").save(out); os.remove(tmp)
    print("safe-zone preview ->", out, "(empirical zones; verify on a real phone)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--platform", nargs="+", default=["douyin"], help=f"any of: {', '.join(PRESETS)} or all")
    ap.add_argument("--outdir", default="out/export")
    ap.add_argument("--mode", choices=["blur", "crop"], default="blur")
    ap.add_argument("--focus-y", type=float, default=0.45, help="crop mode: 0=top 0.5=centre 1=bottom")
    ap.add_argument("--safe-preview", metavar="PNG")
    a = ap.parse_args()
    if a.safe_preview:
        safe_preview(a.video, a.safe_preview); return
    os.makedirs(a.outdir, exist_ok=True)
    names = list(PRESETS) if a.platform == ["all"] else a.platform
    report = []
    for n in names:
        if n not in PRESETS:
            raise SystemExit(f"unknown platform {n}; choose from {list(PRESETS)}")
        r = export(a.video, n, PRESETS[n], a.outdir, a.mode, a.focus_y); report.append(r)
        print(f"{n:<12} {r['w']}x{r['h']} {r['duration']:.1f}s {r['size_mb']}MB  -> {r['file']}\n             {r['note']}")
    json.dump(report, open(os.path.join(a.outdir, "export_report.json"), "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
