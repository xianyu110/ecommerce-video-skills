#!/usr/bin/env python3
"""AI voice-over with edge-tts (free Microsoft Edge online voices).

Usage:
  python tts_edge.py "夏天带冰水出门，不到中午就变温？" -o out/l00.wav
  python tts_edge.py --storyboard storyboard.json --outdir build/tts   # one wav per shot line
  python tts_edge.py --list zh-CN                                       # list voices for a locale

Each line is synthesised to mp3, leading/trailing silence trimmed, converted to
48 kHz mono WAV, and its duration written to <outdir>/durations.json.
Results are cached by (text, voice, rate, pitch) so re-runs are instant.

Needs: pip install edge-tts ; ffmpeg on PATH ; network access to the Edge TTS service.
"""
import argparse, asyncio, hashlib, json, os, subprocess, sys

DEFAULT_VOICE = "zh-CN-YunxiNeural"
TRIM = ("silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
        "silenceremove=start_periods=1:start_threshold=-45dB,areverse")


def probe_duration(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                   "-of", "csv=p=0", path])
    return float(out.strip())


async def _synth(text, voice, rate, pitch, mp3):
    import edge_tts  # imported lazily so --help works without it
    await edge_tts.Communicate(text, voice, rate=rate, pitch=pitch).save(mp3)


def synth_line(text, out_wav, voice=DEFAULT_VOICE, rate="+0%", pitch="+0Hz", retries=3):
    """Synthesise one line to a trimmed 48 kHz mono wav. Returns duration in seconds."""
    os.makedirs(os.path.dirname(os.path.abspath(out_wav)), exist_ok=True)
    key = hashlib.sha1(f"{text}|{voice}|{rate}|{pitch}".encode()).hexdigest()[:12]
    stamp = out_wav + ".key"
    if os.path.exists(out_wav) and os.path.exists(stamp) and open(stamp).read() == key:
        return probe_duration(out_wav)
    mp3 = out_wav[:-4] + ".mp3"
    last = None
    for attempt in range(retries):
        try:
            asyncio.run(_synth(text, voice, rate, pitch, mp3))
            if os.path.getsize(mp3) > 0:
                break
        except Exception as e:  # network hiccups are common; retry
            last = e
    else:
        raise RuntimeError(f"edge-tts failed for {text!r}: {last}")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", mp3, "-af", TRIM, "-ar", "48000", "-ac", "1", out_wav],
                   check=True)
    open(stamp, "w").write(key)
    return probe_duration(out_wav)


def synth_storyboard(sb, outdir, voice=None, rate=None, field="line"):
    voice = voice or sb.get("voice", DEFAULT_VOICE)
    rate = rate or sb.get("rate", "+0%")
    durs = []
    for i, shot in enumerate(sb["shots"]):
        text = shot[field] if field in shot else shot.get("line")
        if not text:
            durs.append(0.0)
            continue
        d = synth_line(text, os.path.join(outdir, f"l{i:02d}.wav"), shot.get("voice", voice),
                       shot.get("rate", rate), shot.get("pitch", sb.get("pitch", "+0Hz")))
        durs.append(round(d, 3))
        print(f"  tts {i:02d} {d:5.2f}s  {text}")
    json.dump(durs, open(os.path.join(outdir, "durations.json"), "w"))
    return durs


async def _list(prefix):
    import edge_tts
    for v in await edge_tts.list_voices():
        if v["ShortName"].startswith(prefix):
            print(f'{v["ShortName"]:<34} {v["Gender"]:<7} {", ".join(v.get("VoiceTag", {}).get("VoicePersonalities", []))}')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("text", nargs="?")
    ap.add_argument("-o", "--out", default="out/voice.wav")
    ap.add_argument("--storyboard")
    ap.add_argument("--outdir", default="build/tts")
    ap.add_argument("--field", default="line", help="storyboard field to read (e.g. line_en)")
    ap.add_argument("--voice")
    ap.add_argument("--rate", help='e.g. "+10%%"')
    ap.add_argument("--pitch", default="+0Hz")
    ap.add_argument("--list", metavar="LOCALE", help="list voices whose name starts with LOCALE, e.g. zh-CN, en-US, ja-JP")
    a = ap.parse_args()
    if a.list is not None:
        asyncio.run(_list(a.list)); return
    if a.storyboard:
        sb = json.load(open(a.storyboard, encoding="utf-8"))
        durs = synth_storyboard(sb, a.outdir, a.voice, a.rate, a.field)
        print(f"total voice {sum(durs):.2f}s -> {a.outdir}/durations.json")
    elif a.text:
        d = synth_line(a.text, a.out, a.voice or DEFAULT_VOICE, a.rate or "+0%", a.pitch)
        print(f"{a.out} {d:.2f}s")
    else:
        ap.print_help(); sys.exit(1)


if __name__ == "__main__":
    main()
