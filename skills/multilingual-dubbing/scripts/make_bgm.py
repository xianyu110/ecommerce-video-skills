#!/usr/bin/env python3
"""Generate a royalty-free, upbeat background bed (pure numpy synthesis) so demos never
depend on copyrighted music.  For real campaigns use music you have rights to
(e.g. the platform's commercial music library).

Usage: python make_bgm.py 18 -o build/bgm.wav [--bpm 112] [--key 0]
"""
import argparse, wave
import numpy as np

SR = 48000


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def make_bgm(seconds, bpm=112, key=0, seed=7):
    n = int(seconds * SR); t = np.arange(n) / SR
    beat = 60.0 / bpm; bar = beat * 4
    prog = [[60, 64, 67], [57, 60, 64], [53, 57, 60], [55, 59, 62]]  # I vi IV V
    out = np.zeros(n)
    for b in range(int(seconds / bar) + 1):
        a = int(b * bar * SR)
        if a >= n:
            break
        chord = [m + key for m in prog[b % 4]]
        # soft pad, one chord per bar
        L = min(n - a, int(bar * SR) + SR // 4); tt = np.arange(L) / SR
        env = np.minimum(1, tt / 0.08) * np.exp(-tt * 0.6)
        for m in chord:
            f = midi(m - 12)
            out[a:a + L] += env * (np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(2 * np.pi * 2 * f * tt)) * 0.10
        # plucked 8th-note arpeggio
        for j in range(8):
            s = a + int(j * beat / 2 * SR)
            if s >= n:
                break
            L = min(n - s, int(0.35 * SR)); tt = np.arange(L) / SR
            f = midi(chord[[0, 1, 2, 1][j % 4]] + (12 if j in (3, 7) else 0))
            out[s:s + L] += np.sin(2 * np.pi * f * tt) * np.exp(-tt * 9) * 0.09
    # kick on every beat, hat on off-beats
    rng = np.random.default_rng(seed)
    for k in range(int(seconds / beat) + 1):
        s = int(k * beat * SR)
        if s >= n:
            break
        L = min(n - s, int(0.18 * SR)); tt = np.arange(L) / SR
        out[s:s + L] += np.sin(2 * np.pi * (50 + 70 * np.exp(-tt * 35)) * tt) * np.exp(-tt * 18) * 0.35
        h = s + int(beat / 2 * SR)
        if h < n:
            L = min(n - h, int(0.05 * SR))
            out[h:h + L] += rng.standard_normal(L) * np.exp(-np.arange(L) / SR * 80) * 0.04
    fade = np.minimum(1, t / 0.6) * np.minimum(1, np.maximum(0, (seconds - t) / 1.2))
    out *= fade
    return out / (np.max(np.abs(out)) + 1e-9) * 0.9


def write_wav(path, x):
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("seconds", type=float)
    ap.add_argument("-o", "--out", default="build/bgm.wav")
    ap.add_argument("--bpm", type=float, default=112)
    ap.add_argument("--key", type=int, default=0, help="semitone transpose")
    a = ap.parse_args()
    write_wav(a.out, make_bgm(a.seconds, a.bpm, a.key))
    print("wrote", a.out)
