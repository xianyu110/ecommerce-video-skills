#!/usr/bin/env python3
"""直播切片 / live-stream clipper.

Three ways to choose segments, then every clip is exported as a 9:16 MP4 (blur-fill if the
source is landscape) with an optional title burned on top and subtitles if an SRT is given.

  # 1) you (or the agent) already picked timestamps
  python live_clip.py live.mp4 --cuts cuts.csv --outdir out/clips      # csv: start,end,title  (hh:mm:ss or seconds)
  # 2) find moments in a transcript (SRT from your ASR tool / platform export)
  python live_clip.py live.mp4 --srt live.srt --keywords "上链接,库存,演示,对比" --window 25 --outdir out/clips
  # 3) no transcript: propose segments split at pauses (silencedetect)
  python live_clip.py live.mp4 --propose 30 > proposals.csv

Only clip streams you own or have permission to repost.
"""
import argparse, csv, os, re, subprocess, sys


def secs(x):
    x = str(x).strip()
    if re.fullmatch(r"[\d.]+", x):
        return float(x)
    parts = [float(p) for p in x.replace(",", ".").split(":")]
    while len(parts) < 3:
        parts.insert(0, 0.0)
    return parts[0] * 3600 + parts[1] * 60 + parts[2]


def hms(t):
    h, r = divmod(t, 3600); m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{s:06.3f}"


def duration(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]))


def read_srt(path):
    txt = open(path, encoding="utf-8-sig").read()
    cues = []
    for block in re.split(r"\n\s*\n", txt.strip()):
        m = re.search(r"(\d+:\d+:\d+[,.]\d+)\s*-->\s*(\d+:\d+:\d+[,.]\d+)\s*\n(.*)", block, re.S)
        if m:
            cues.append((secs(m.group(1)), secs(m.group(2)), m.group(3).replace("\n", " ").strip()))
    return cues


def keyword_segments(cues, keywords, window, total):
    hits = []
    for st, en, text in cues:
        k = next((k for k in keywords if k in text), None)
        if k:
            a = max(0.0, st - window * 0.3); b = min(total, a + window)
            if hits and a < hits[-1][1]:            # merge overlapping windows
                hits[-1] = (hits[-1][0], max(hits[-1][1], b), hits[-1][2]); continue
            hits.append((a, b, text[:16]))
    return hits


def propose(path, target):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "silencedetect=noise=-35dB:d=0.6", "-f", "null", "-"],
                       capture_output=True, text=True)
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    total = duration(path); segs, a = [], 0.0
    for e in ends + [total]:
        if e - a >= target:
            segs.append((a, e)); a = e
    return segs


def export_clip(src, a, b, title, out, w=1080, h=1920, srt=None, font="Noto Sans CJK SC"):
    vf = (f"split[x][y];[x]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},boxblur=30:2,"
          f"eq=brightness=-0.08[bg];[y]scale={w}:{h}:force_original_aspect_ratio=decrease[fg];"
          f"[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1")
    if srt:
        esc = srt.replace("\\", "/").replace(":", "\\:")
        vf += f",subtitles='{esc}':force_style='FontName={font},Fontsize=13,Bold=1,Outline=2,MarginV=70'"
    if title:
        t = title.replace("'", "’").replace(":", "：")
        vf += (f",drawtext=font='{font}':text='{t}':fontsize={int(h * 0.05)}:fontcolor=yellow:borderw=8:"
               f"bordercolor=black:x=(w-text_w)/2:y=h*0.11")
    # -ss before -i is fast; with -copyts subtitles stay in sync with the source timeline
    cmd = ["ffmpeg", "-y", "-v", "error", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-copyts", "-i", src, "-vf", vf,
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
           "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-movflags", "+faststart", "-output_ts_offset", "0",
           "-avoid_negative_ts", "make_zero", out]
    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--cuts"); ap.add_argument("--srt"); ap.add_argument("--keywords")
    ap.add_argument("--window", type=float, default=25.0)
    ap.add_argument("--propose", type=float, metavar="SECONDS")
    ap.add_argument("--outdir", default="out/clips")
    ap.add_argument("--size", default="1080x1920")
    ap.add_argument("--burn-subs", action="store_true", help="burn --srt subtitles into each clip")
    a = ap.parse_args()
    total = duration(a.video)
    if a.propose:
        wr = csv.writer(sys.stdout); wr.writerow(["start", "end", "title"])
        for s, e in propose(a.video, a.propose):
            wr.writerow([hms(s), hms(e), ""])
        return
    if a.cuts:
        rows = list(csv.DictReader(open(a.cuts, encoding="utf-8-sig")))
        segs = [(secs(r["start"]), secs(r["end"]), r.get("title", "")) for r in rows]
    elif a.srt and a.keywords:
        segs = keyword_segments(read_srt(a.srt), [k.strip() for k in a.keywords.split(",") if k.strip()], a.window, total)
    else:
        raise SystemExit("give --cuts, or --srt + --keywords, or --propose N")
    os.makedirs(a.outdir, exist_ok=True)
    w, h = map(int, a.size.split("x"))
    for i, (s, e, title) in enumerate(segs, 1):
        out = os.path.join(a.outdir, f"clip_{i:02d}.mp4")
        export_clip(a.video, s, e, title, out, w, h, a.srt if a.burn_subs else None)
        print(f"{out}  {hms(s)} -> {hms(e)}  {title}")


if __name__ == "__main__":
    main()
