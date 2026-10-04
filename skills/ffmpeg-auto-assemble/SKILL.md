---
name: ffmpeg-auto-assemble
description: "ffmpeg 自动拼接成片：一条命令把 storyboard.json（商品图/视频片段 + 口播稿）渲染成带配音、字幕花字、转场、BGM 自动闪避、响度标准化的 9:16 MP4，纯本地运行。Use when the user wants to assemble/edit/render a product video, 自动剪辑, 一键成片, 拼接视频, 图片转视频, Ken Burns, add BGM/subtitles/voice-over with ffmpeg, or batch-produce short videos without an editor."
---

# ffmpeg 自动拼接成片 · Auto-assemble with ffmpeg

`storyboard.json` → 配音（edge-tts）→ 每镜 Ken Burns / 视频裁切 → xfade 转场 → ASS 字幕花字 → BGM 闪避混音 → 两遍 loudnorm（-14 LUFS）→ `out/video.mp4` + `.srt`。

> Part of [ecommerce-video-skills](https://github.com/xianyu110/ecommerce-video-skills) · 脚本都在本目录 `scripts/`：`assemble.py`（主程序）· `tts_edge.py` · `make_subs.py` · `make_bgm.py`（免版权合成 BGM）· `make_cards.py`（PIL 商品卡/结尾卡）

## 输入 Inputs

- `storyboard.json`（可由 `selling-point-storyboard` 生成），素材路径相对于该文件
- 环境：Python 3.9+，`pip install pillow numpy edge-tts`，ffmpeg（含 libass），CJK 字体

## 快速开始 Quick start

```bash
pip install pillow numpy edge-tts
python scripts/assemble.py examples/aura-bottle/storyboard.json -o out/aura.mp4       # 仓库自带示例，约 30 秒渲染完
python scripts/assemble.py storyboard.json --tts none -o out/preview.mp4             # 离线预览（无配音，按字数估时）
python scripts/assemble.py storyboard.json --size 1080x1080 -o out/main-1x1.mp4      # 主图视频 1:1
python scripts/assemble.py storyboard.json --bgm music.mp3                           # 用你有版权的音乐
```

## storyboard 字段 Fields

| 字段 | 说明 |
|---|---|
| 顶层 `voice` / `rate` / `pitch` | edge-tts 音色、语速（如 `+10%`）、音调 |
| 顶层 `bgm` | `"auto"`（内置合成，免版权）/ 音乐文件路径 / `null` |
| 顶层 `tag` | 全程左上角贴纸（品牌/型号/「演示」） |
| `image` 或 `video` (+`start`) | 素材；视频从 `start` 秒截取本镜时长 |
| `line` | 配音文本；镜头时长 = 配音 + 0.15s 前导 + `pad` |
| `sub` | 字幕（默认同 `line`）；`""` 表示本镜不出字幕；`**高亮**`、`|` 分段 |
| `title` / `cta` | 花字 / 行动号召按钮 |
| `motion` | `zoom_in` `zoom_out` `pan_left` `pan_right` `pan_up` `pan_down` `punch` `static` |
| `fit` | `auto`（比例接近则裁满，否则模糊填充）/ `cover` / `blur` |
| `transition` | 进入下一镜的 xfade 名：`fade` `slideleft` `slideup` `smoothleft` `circleopen` `wipeleft` … |
| `min` / `duration` / `pad` | 最短时长 / 固定时长 / 句后留白（秒） |

## 步骤 Steps

1. 检查素材都存在、比例合适（商品图 ≥ 1000px）；缺结尾卡就用 `make_cards.py` 生成：
   `python scripts/make_cards.py --image main.png --name "商品名" --points "卖点一|卖点二|卖点三" -o assets/end-card.png`
2. 先 `--tts none` 跑一遍看画面节奏，再正式渲染。
3. 渲染后抽帧检查：`ffmpeg -ss 3 -i out/video.mp4 -frames:v 1 check.png`
4. 交给 `platform-spec-export` 导出各平台版本；用 `cover-title-ab` 做封面。

## 流水线细节 How it works

- **Ken Burns**：逐帧 `scale(eval=frame)+crop`，比 `zoompan` 抖动小；`punch` = 0.35 秒快速推近（钩子专用）。
- **转场**：每镜多渲染半个转场长度，xfade 居中在镜头分界，**配音起点不被转场吃掉**。
- **混音**：配音按镜头起点放置；BGM 默认 -20 dB，有人声时再压 10 dB（平滑闪避）；先压缩/限幅再两遍 loudnorm 到约 -14 LUFS、TP -1.5 dB。
- **字幕**：用真实配音时长生成 `build/timing.json` → `make_subs.py` → libass 烧录，同时导出 `.srt`。

## 检查清单 Checklist

- [ ] 成片时长、分辨率、帧率正确（`ffprobe out/video.mp4`）
- [ ] 抽 3 帧：字幕不压商品、不进底部 UI 区
- [ ] 听一遍：配音清楚、BGM 不抢、开头无爆音
- [ ] BGM 有商用授权（`auto` 合成音乐可放心用）
- [ ] 素材（图片/视频/字体）有使用授权

## 常见问题与修复 Failure fixes

| 问题 | 修复 |
|---|---|
| `ffmpeg failed` | 看脚本打印的 stderr 末尾；常见是路径错误或 ffmpeg 缺 libass/libx264 |
| 画面边缘糊 | 素材分辨率太低；换 ≥1080px 图片或减小 `motion` 幅度（改 `static`） |
| 商品被裁掉 | 该镜设 `"fit": "blur"` |
| 转场处声音被切 | 不会发生（配音按镜头起点对齐）；若自定义了 `duration` 过短，加长即可 |
| 渲染慢 | 预设已用 `veryfast` 中间文件；最终编码可把 `-preset medium` 改为 `fast` |
| 想要 1:1 / 16:9 | `--size 1080x1080` / `--size 1920x1080`，字幕字号自动按比例 |

参考与致谢：思路受 [MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo)（MIT）「脚本→配音→字幕→合成」流水线启发，本实现为独立编写的纯 ffmpeg 版本，未复制其代码。
