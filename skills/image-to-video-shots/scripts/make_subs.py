#!/usr/bin/env python3
"""Subtitles + 花字 (big title text) as one ASS file (+ a plain SRT).

Input: a timing JSON written by assemble.py (or your own) of the form
  {"size": [1080, 1920], "cues": [{"start": 0.3, "end": 2.4, "text": "冰水不到中午就**变温**？", "style": "Sub"}, ...]}

Text markup:
  **word**   highlight word (keyword colour)
  |          manual line break; also splits one cue into timed chunks when --chunk is on
Styles: Sub (bottom subtitle), Hook (big pop-in 花字 near top), Tag (small sticker, top-left), CTA (big bottom-centre button text)

Usage: python make_subs.py timing.json -o build/subs.ass --srt build/subs.srt [--font "Noto Sans CJK SC"]
"""
import argparse, json, re, shutil, subprocess

# ASS colours are &HAABBGGRR
WHITE, BLACK, YELLOW, CYAN = "&H00FFFFFF", "&H00000000", "&H0000DCFF", "&H00F0D322"
HL = "&H0000DCFF"  # keyword highlight (warm yellow)


def detect_font():
    if shutil.which("fc-list"):
        names = subprocess.run(["fc-list", ":lang=zh", "family"], capture_output=True, text=True).stdout
        for cand in ["Noto Sans CJK SC", "Source Han Sans SC", "PingFang SC", "Microsoft YaHei", "WenQuanYi Zen Hei"]:
            if cand in names:
                return cand
    return "Noto Sans CJK SC"


def ts(t):
    t = max(0.0, t)
    h, rem = divmod(t, 3600); m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def srt_ts(t):
    ms = int(round(max(0.0, t) * 1000))
    h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def header(w, h, font):
    sub = round(h * 0.037)    # ~71 px on 1920
    hook = round(h * 0.058)   # ~110 px
    tag = round(h * 0.022)
    cta = round(h * 0.040)
    mv_sub = round(h * 0.26)  # keep subtitles above the bottom ~22% UI area
    mv_hook = round(h * 0.13)
    return f"""[Script Info]
ScriptType: v4.00+
PlayResX: {w}
PlayResY: {h}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,{font},{sub},{WHITE},{WHITE},{BLACK},&H64000000,-1,0,0,0,100,100,1,0,1,5,2,2,70,70,{mv_sub},1
Style: Hook,{font},{hook},{YELLOW},{WHITE},{BLACK},&H96000000,-1,0,0,0,100,100,2,-2,1,9,5,8,60,60,{mv_hook},1
Style: Tag,{font},{tag},{BLACK},{WHITE},{YELLOW},&H00000000,-1,0,0,0,100,100,1,0,3,14,0,7,48,48,{round(h*0.05)},1
Style: CTA,{font},{cta},{WHITE},{WHITE},&H003C14FF,&H00000000,-1,0,0,0,100,100,2,0,3,22,0,2,60,60,{round(h*0.20)},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def markup(text, hl=HL):
    text = text.replace("{", "(").replace("}", ")")
    text = re.sub(r"\*\*(.+?)\*\*", lambda m: "{\\c" + hl + "&}" + m.group(1) + "{\\r}", text)
    return text.replace("|", "\\N")


def plain(text):
    return re.sub(r"\*\*(.+?)\*\*", r"\1", text).replace("|", "\n")


def chunk_cue(c):
    """Split 'a|b|c' Sub cues into sequential chunks timed by character count."""
    parts = [p for p in c["text"].split("|") if p.strip()]
    if c.get("style", "Sub") != "Sub" or len(parts) < 2:
        return [c]
    lens = [max(1, len(plain(p))) for p in parts]; tot = sum(lens)
    out, t = [], c["start"]
    for p, n in zip(parts, lens):
        d = (c["end"] - c["start"]) * n / tot
        out.append({**c, "start": t, "end": t + d, "text": p}); t += d
    return out


def anim(style):
    if style == "Hook":   # pop-in: 120% -> 100% with fade
        return "{\\fad(60,120)\\fscx125\\fscy125\\t(0,180,\\fscx100\\fscy100)}"
    if style == "CTA":    # gentle pulse
        return "{\\fad(100,0)\\t(0,400,\\fscx106\\fscy106)\\t(400,800,\\fscx100\\fscy100)\\t(800,1200,\\fscx106\\fscy106)\\t(1200,1600,\\fscx100\\fscy100)}"
    if style == "Tag":
        return "{\\fad(150,150)}"
    return "{\\fad(40,40)}"


def build(timing, font=None, chunk=True):
    w, h = timing.get("size", [1080, 1920])
    font = font or timing.get("font") or detect_font()
    cues = []
    for c in timing["cues"]:
        cues.extend(chunk_cue(c) if chunk else [c])
    ass = [header(w, h, font)]
    srt, n = [], 0
    for c in cues:
        st = c.get("style", "Sub")
        layer = {"Sub": 1, "Hook": 2, "Tag": 3, "CTA": 2}.get(st, 1)
        ass.append(f"Dialogue: {layer},{ts(c['start'])},{ts(c['end'])},{st},,0,0,0,,{anim(st)}{markup(c['text'])}")
        if st == "Sub":
            n += 1
            srt.append(f"{n}\n{srt_ts(c['start'])} --> {srt_ts(c['end'])}\n{plain(c['text'])}\n")
    return "\n".join(ass) + "\n", "\n".join(srt)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("timing")
    ap.add_argument("-o", "--out", default="build/subs.ass")
    ap.add_argument("--srt")
    ap.add_argument("--font")
    ap.add_argument("--no-chunk", action="store_true")
    a = ap.parse_args()
    ass, srt = build(json.load(open(a.timing, encoding="utf-8")), a.font, not a.no_chunk)
    open(a.out, "w", encoding="utf-8").write(ass)
    if a.srt:
        open(a.srt, "w", encoding="utf-8").write(srt)
    print("wrote", a.out, a.srt or "")


if __name__ == "__main__":
    main()
