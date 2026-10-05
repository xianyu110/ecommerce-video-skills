#!/usr/bin/env python3
"""One-command e-commerce short video: storyboard.json -> voice-over -> Ken Burns shots ->
transitions -> subtitles/花字 -> BGM with ducking -> loudness-normalised 9:16 MP4.

  python assemble.py examples/aura-bottle/storyboard.json -o out/aura.mp4
  python assemble.py storyboard.json --tts none        # offline preview, silent timing estimate
  python assemble.py storyboard.json --size 1080x1080  # square (e.g. 主图视频 1:1)
  python assemble.py storyboard.json --lang en --voice en-US-AndrewNeural   # localised version (line_en, sub_en ...)

Storyboard (paths are relative to the storyboard file):
{
  "voice": "zh-CN-YunxiNeural", "rate": "+8%", "bgm": "auto" | "music.mp3" | null,
  "tag": "AURA 保温杯",                       # optional sticker shown the whole video
  "shots": [
    {"image": "assets/lifestyle.webp",        # or "video": "clip.mp4", "start": 12.5
     "line": "夏天带冰水出门，不到中午就变温？",   # voice-over text (TTS)
     "sub": "冰水不到中午就**变温**？",          # optional subtitle (defaults to line); **kw** = highlight, | = break
     "title": "冰水撑不到中午？",                # optional big 花字 for this shot
     "cta": "点击下方小黄车",                    # optional CTA button text
     "motion": "punch",                       # zoom_in | zoom_out | pan_left | pan_right | pan_up | pan_down | punch | static
     "fit": "auto",                           # auto | cover | blur  (blur = blurred fill for non-9:16 images)
     "transition": "fade",                    # xfade name into the NEXT shot (fade, slideleft, smoothup, circleopen ...)
     "min": 2.0, "pad": 0.25}                 # min shot length / silence after the line (s)
  ]
}
Requires: ffmpeg (with libass), pip install pillow numpy edge-tts
"""
import argparse, json, os, shutil, subprocess, sys, wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_subs  # noqa: E402
from make_bgm import make_bgm, SR  # noqa: E402

LEAD = 0.15     # silence before each line inside its shot
XF = 0.30       # transition length


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(" ".join(cmd) + "\n" + r.stderr[-3000:])
        raise SystemExit(f"ffmpeg failed (exit {r.returncode})")


# ---------------------------------------------------------------- stills
def cover(im, w, h):
    return ImageOps.fit(im, (w, h), Image.LANCZOS, centering=(0.5, 0.45))


def blur_fit(im, w, h):
    bg = cover(im, w, h).filter(ImageFilter.GaussianBlur(40))
    bg = Image.blend(bg, Image.new("RGB", (w, h), (0, 0, 0)), 0.25)
    r = min(w * 0.92 / im.width, h * 0.72 / im.height)
    fg = im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)
    x, y = (w - fg.width) // 2, int(h * 0.40 - fg.height / 2)
    y = max(int(h * 0.08), y)
    sh = Image.new("RGBA", (fg.width + 120, fg.height + 120), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([60, 75, fg.width + 60, fg.height + 75], 28, fill=(0, 0, 0, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(24))
    bg.paste(sh, (x - 60, y - 60), sh)
    mask = Image.new("L", fg.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, fg.width - 1, fg.height - 1], 28, fill=255)
    bg.paste(fg, (x, y), mask)
    return bg


def make_still(path, w, h, fit, out):
    im = Image.open(path).convert("RGB")
    if fit == "auto":
        fit = "cover" if abs((im.width / im.height) / (w / h) - 1) < 0.25 else "blur"
    (cover(im, w, h) if fit == "cover" else blur_fit(im, w, h)).save(out)


# ---------------------------------------------------------------- motion
def motion_vf(motion, w, h, d, fps, z=0.10):
    """Smooth sub-pixel-ish Ken Burns using per-frame scale + crop."""
    p = f"(t/{d:.3f})"
    zoom = {
        "zoom_in": f"(1+{z}*{p})",
        "zoom_out": f"(1+{z}*(1-{p}))",
        "punch": f"(1+0.14*(1-pow(1-min(t/0.35,1),3))+0.03*{p})",
        "static": "1",
    }.get(motion, f"(1+{z})")
    cx, cy = "(iw-ow)/2", "(ih-oh)/2"
    if motion == "pan_left":
        cx = f"(iw-ow)*(1-{p})"
    elif motion == "pan_right":
        cx = f"(iw-ow)*{p}"
    elif motion == "pan_up":
        cy = f"(ih-oh)*(1-{p})"
    elif motion == "pan_down":
        cy = f"(ih-oh)*{p}"
    return (f"scale=w='2*ceil({w}*{zoom}/2)':h='2*ceil({h}*{zoom}/2)':eval=frame:flags=bicubic,"
            f"crop={w}:{h}:'{cx}':'{cy}',fps={fps},format=yuv420p,setsar=1")


def render_shot(shot, base, i, w, h, fps, dur, build):
    out = os.path.join(build, f"shot{i:02d}.mp4")
    enc = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-pix_fmt", "yuv420p", "-an"]
    if shot.get("video"):
        src = os.path.join(base, shot["video"])
        vf = (f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps={fps},format=yuv420p,setsar=1"
              if shot.get("fit", "cover") != "blur" else
              f"split[a][b];[a]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},boxblur=30[bg];"
              # contain-fit the foreground (portrait clips on a landscape canvas fit by height, not width)
              f"[b]scale={w}:{h}:force_original_aspect_ratio=decrease:force_divisible_by=2[fg];"
              f"[bg][fg]overlay=(W-w)/2:(H-h)*{0.4 if h > w else 0.5},fps={fps},format=yuv420p,setsar=1")
        run(["ffmpeg", "-y", "-v", "error", "-ss", str(shot.get("start", 0)), "-t", f"{dur:.3f}", "-i", src,
             "-vf", vf, *enc, "-t", f"{dur:.3f}", out])
        return out
    still = os.path.join(build, f"still{i:02d}.png")
    make_still(os.path.join(base, shot["image"]), w, h, shot.get("fit", "auto"), still)
    run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-framerate", str(fps), "-t", f"{dur:.3f}", "-i", still,
         "-vf", motion_vf(shot.get("motion", "zoom_in"), w, h, dur, fps), *enc, "-t", f"{dur:.3f}", out])
    return out


def concat(clips, durs, transitions, fps, out):
    """xfade chain. clip k (except last) is XF longer than its slot so slot starts stay exact."""
    if len(clips) == 1:
        shutil.copy(clips[0], out); return
    inputs, fc, prev, off = [], [], "[0:v]", 0.0
    for c in clips:
        inputs += ["-i", c]
    for k in range(1, len(clips)):
        off += durs[k - 1]
        tr = transitions[k - 1] or "fade"
        lab = f"[x{k}]"
        fc.append(f"{prev}[{k}:v]xfade=transition={tr}:duration={XF}:offset={off - XF / 2:.3f}{lab}")
        prev = lab
    run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(fc), "-map", prev,
         "-r", str(fps), "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-pix_fmt", "yuv420p", out])


# ---------------------------------------------------------------- audio
def read_audio(path):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", path, "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"])
    return np.frombuffer(raw, np.int16).astype(np.float64) / 32768.0


def mix_audio(voice_items, total, bgm, out, bgm_db=-20.0, duck_db=-10.0):
    n = int(total * SR) + 1
    voice = np.zeros(n)
    for start, path in voice_items:
        a = read_audio(path); k = int(start * SR)
        voice[k:k + len(a)] += a[:max(0, n - k)]
    if np.max(np.abs(voice)) > 0:
        voice *= 0.9 / np.max(np.abs(voice))
    music = np.zeros(n)
    if bgm == "auto":
        m = make_bgm(total + 0.1)
        music[:min(n, len(m))] = m[:n]
    elif bgm:
        m = read_audio(bgm)
        reps = int(np.ceil(n / max(1, len(m))))
        music = np.tile(m, reps)[:n]
        t = np.arange(n) / SR
        music *= np.minimum(1, t / 0.5) * np.minimum(1, np.maximum(0, (total - t) / 1.2))
    if bgm:
        music /= (np.max(np.abs(music)) + 1e-9)
        win = int(0.2 * SR)
        env = np.convolve(np.abs(voice), np.ones(win) / win, mode="same")
        g = np.where(env > 0.01, 10 ** ((bgm_db + duck_db) / 20), 10 ** (bgm_db / 20))
        g = np.convolve(g, np.ones(win) / win, mode="same")  # smooth ducking
        voice = voice + music * g
    voice *= 0.95 / (np.max(np.abs(voice)) + 1e-9)
    with wave.open(out, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((voice * 32767).astype(np.int16).tobytes())


def loudnorm_2pass(src, dst, target=-14.0, tp=-1.5, lra=11.0):
    """Two-pass EBU R128 normalisation (short-video platforms play back around -14 LUFS)."""
    pre = "acompressor=threshold=-20dB:ratio=3:attack=5:release=120:makeup=2,alimiter=limit=0.6:level=false,"
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", src, "-af",
                        pre + f"loudnorm=I={target}:TP={tp}:LRA={lra}:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    try:
        m = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
        float(m["input_i"]); float(m["input_tp"])
        if m["input_i"] in ("-inf", "inf") or float(m["input_i"]) < -70:
            raise ValueError("silent")
    except (ValueError, KeyError):  # silent track (e.g. --tts none --bgm none): nothing to normalise
        shutil.copy(src, dst); return
    af = (pre + f"loudnorm=I={target}:TP={tp}:LRA={lra}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,"
          f"aresample=48000")
    run(["ffmpeg", "-y", "-v", "error", "-i", src, "-af", af, "-ar", "48000", dst])


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("storyboard")
    ap.add_argument("-o", "--out", default="out/video.mp4")
    ap.add_argument("--build", default="build")
    ap.add_argument("--size", default="1080x1920")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--tts", choices=["edge", "none"], default="edge")
    ap.add_argument("--field", default="line", help="storyboard field used for TTS + default subtitle (e.g. line_en)")
    ap.add_argument("--sub-field", default="sub", help="subtitle field (e.g. sub_en)")
    ap.add_argument("--lang", help="localised fields: reads line_<lang>, sub_<lang>, title_<lang>, cta_<lang>, tag_<lang>")
    ap.add_argument("--voice"); ap.add_argument("--rate")
    ap.add_argument("--bgm", help='"auto", a music file, or "none" (overrides storyboard)')
    ap.add_argument("--font")
    ap.add_argument("--no-subs", action="store_true")
    a = ap.parse_args()

    if a.lang:
        a.field, a.sub_field = f"line_{a.lang}", f"sub_{a.lang}"

    def loc(d, key):  # localised value with fallback to the base field
        return d.get(f"{key}_{a.lang}", d.get(key)) if a.lang else d.get(key)

    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            raise SystemExit(f"{tool} not found on PATH")
    sb = json.load(open(a.storyboard, encoding="utf-8"))
    base = os.path.dirname(os.path.abspath(a.storyboard))
    w, h = map(int, a.size.lower().split("x"))
    os.makedirs(a.build, exist_ok=True); os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    shots = sb["shots"]

    # 1) voice-over
    ttsdir = os.path.join(a.build, "tts"); os.makedirs(ttsdir, exist_ok=True)
    print("[1/5] voice-over")
    if a.tts == "edge":
        from tts_edge import synth_storyboard
        vdur = synth_storyboard(sb, ttsdir, a.voice, a.rate, a.field)
    else:
        vdur = [len((s.get(a.field) or s.get("line") or "")) / 4.5 for s in shots]

    # 2) timeline
    durs = []
    for s, v in zip(shots, vdur):
        d = s.get("duration") or max(s.get("min", 1.6), LEAD + v + s.get("pad", 0.25))
        durs.append(round(d, 3))
    starts = list(np.cumsum([0] + durs[:-1]))
    total = float(sum(durs))
    print(f"      {len(shots)} shots, total {total:.2f}s")

    # 3) shots + transitions
    print("[2/5] rendering shots")
    clips = []
    for i, (s, d) in enumerate(zip(shots, durs)):
        extra = XF / 2 if i < len(shots) - 1 else 0
        extra += XF / 2 if i > 0 else 0
        clips.append(render_shot(s, base, i, w, h, a.fps, d + extra, a.build))
    print("[3/5] transitions")
    silent = os.path.join(a.build, "video_noaudio.mp4")
    concat(clips, durs, [s.get("transition", "fade") for s in shots], a.fps, silent)

    # 4) audio
    print("[4/5] audio mix")
    bgm = a.bgm if a.bgm is not None else sb.get("bgm", "auto")
    if bgm == "none":
        bgm = None
    if bgm and bgm != "auto":
        bgm = bgm if os.path.isabs(bgm) or os.path.exists(bgm) else os.path.join(base, bgm)
    items = [(st + LEAD, os.path.join(ttsdir, f"l{i:02d}.wav")) for i, st in enumerate(starts)
             if a.tts == "edge" and vdur[i] > 0]
    mix = os.path.join(a.build, "mix.wav")
    mix_audio(items, total, bgm, mix)
    norm = os.path.join(a.build, "mix_norm.wav")
    loudnorm_2pass(mix, norm)

    # 5) subtitles + mux
    print("[5/5] subtitles + mux")
    cues = []
    if loc(sb, "tag"):
        cues.append({"start": 0.0, "end": total, "text": loc(sb, "tag"), "style": "Tag"})
    for i, (s, st, d, v) in enumerate(zip(shots, starts, durs, vdur)):
        text = s[a.sub_field] if a.sub_field in s else (s.get(a.field) or s.get("line"))
        if text:
            cues.append({"start": st + LEAD - 0.05, "end": min(st + d, st + LEAD + v + 0.15), "text": text, "style": "Sub"})
        if loc(s, "title"):
            cues.append({"start": st + 0.05, "end": st + d - 0.05, "text": loc(s, "title"), "style": "Hook"})
        if loc(s, "cta"):
            cues.append({"start": st + 0.2, "end": st + d, "text": loc(s, "cta"), "style": "CTA"})
    timing = {"size": [w, h], "total": total, "starts": [float(x) for x in starts], "durations": durs,
              "voice": vdur, "cues": cues}
    json.dump(timing, open(os.path.join(a.build, "timing.json"), "w"), ensure_ascii=False, indent=1)
    ass, srt = make_subs.build(timing, a.font)
    assp = os.path.join(a.build, "subs.ass")
    open(assp, "w", encoding="utf-8").write(ass)
    open(os.path.splitext(a.out)[0] + ".srt", "w", encoding="utf-8").write(srt)
    vf = [] if a.no_subs else ["-vf", "ass=" + assp.replace("\\", "/").replace(":", "\\:")]
    run(["ffmpeg", "-y", "-v", "error", "-i", silent, "-i", norm, *vf,
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-r", str(a.fps),
         "-c:a", "aac", "-b:a", "160k", "-ac", "2", "-movflags", "+faststart", "-t", f"{total:.3f}", a.out])
    print(f"done -> {a.out}  ({total:.1f}s, {w}x{h})  subtitles -> {os.path.splitext(a.out)[0]}.srt")


if __name__ == "__main__":
    main()
