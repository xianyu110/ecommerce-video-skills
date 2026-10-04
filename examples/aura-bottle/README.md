# 示例：AURA 保温杯 17 秒带货视频 / Sample: AURA bottle

```bash
pip install pillow numpy edge-tts      # + ffmpeg
python scripts/assemble.py examples/aura-bottle/storyboard.json -o out/aura-zh.mp4
python scripts/assemble.py examples/aura-bottle/storyboard.json --lang en --voice en-US-AndrewNeural --rate "+5%" -o out/aura-en.mp4 --build build/en
```

- 素材：`assets/` 里 6 张图（5 张来自 [ecommerce-image-skills](https://github.com/xianyu110/ecommerce-image-skills) 的展示图 + 1 张 `make_cards.py` 生成的结尾卡）
- 输出：1080×1920 · 30fps · H.264 + AAC · 约 -14 LUFS · 同名 `.srt`
- 「AURA」是 AI 生成的虚构商品，「24 小时保冰」等说法仅作演示，真实商品请只写测过的数据。
