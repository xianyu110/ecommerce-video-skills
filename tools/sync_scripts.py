#!/usr/bin/env python3
"""Maintainers: copy canonical scripts/ into each skill so every skill folder is self-contained.
Run from the repo root after editing anything in scripts/:  python tools/sync_scripts.py"""
import os, shutil

MAP = {
    "ai-voiceover-edge-tts": ["tts_edge.py"],
    "subtitles-and-text-effects": ["make_subs.py"],
    "ffmpeg-auto-assemble": ["assemble.py", "tts_edge.py", "make_subs.py", "make_bgm.py", "make_cards.py"],
    "multilingual-dubbing": ["assemble.py", "tts_edge.py", "make_subs.py", "make_bgm.py"],
    "platform-spec-export": ["export_platform.py"],
    "live-stream-clips": ["live_clip.py"],
    "cover-title-ab": ["cover_ab.py"],
    "unboxing-comparison-review": ["make_cards.py"],
    "image-to-video-shots": ["assemble.py", "tts_edge.py", "make_subs.py", "make_bgm.py"],
}
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for skill, files in MAP.items():
    dst = os.path.join(root, "skills", skill, "scripts"); os.makedirs(dst, exist_ok=True)
    for f in files:
        shutil.copy2(os.path.join(root, "scripts", f), os.path.join(dst, f))
    print(f"{skill:<30} {', '.join(files)}")
