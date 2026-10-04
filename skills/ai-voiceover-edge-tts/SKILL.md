---
name: ai-voiceover-edge-tts
description: "AI 口播配音：用免费的 edge-tts（微软 Edge 在线语音）为带货短视频逐句生成配音，自动去首尾静音、统计每句时长、缓存复用，可选音色/语速/音调，并给出口播稿改写规则。Use when the user needs a voice-over, 配音, 口播, 旁白, TTS, text-to-speech, AI 主播声音, or wants to turn a script into audio for 抖音 / TikTok / 视频号 videos."
---

# AI 口播配音 · Voice-over with edge-tts

逐句合成 → 去静音 → 48 kHz WAV → `durations.json`。后续的字幕、镜头时长都按真实配音时长对齐，不再「声画对不上」。

> Part of [ecommerce-video-skills](https://github.com/xianyu110/ecommerce-video-skills) · 脚本：`scripts/tts_edge.py`（仅依赖 `edge-tts` + ffmpeg）

## 输入 Inputs

- 口播稿（一句一行，或 `storyboard.json` 的 `line` 字段）
- 语言 / 音色偏好（男/女、活泼/沉稳）、语速
- 环境：`pip install edge-tts`，ffmpeg，能访问微软 TTS 服务的网络

## 步骤 Steps

1. **改写成「好读」的口播稿**（见规则），每句 8–20 字。
2. **选音色**（`python scripts/tts_edge.py --list zh-CN` 查看全部）：

   | 场景 | 推荐音色 |
   |---|---|
   | 活力种草（男） | `zh-CN-YunxiNeural` |
   | 亲切种草（女） | `zh-CN-XiaoxiaoNeural` / `zh-CN-XiaoyiNeural` |
   | 激情促销 | `zh-CN-YunjianNeural` |
   | 专业讲解 | `zh-CN-YunyangNeural` |
   | 台湾 / 香港 | `zh-TW-HsiaoChenNeural` / `zh-HK-HiuMaanNeural` |
   | English | `en-US-AndrewNeural` · `en-US-AvaNeural` · `en-US-EmmaNeural` |

3. **合成**：

   ```bash
   pip install edge-tts
   # 单句试听
   python scripts/tts_edge.py "夏天带冰水出门，不到中午就变温了？" --voice zh-CN-YunxiNeural --rate "+10%" -o out/hook.wav
   # 整个分镜（每镜一句 → build/tts/l00.wav … + durations.json）
   python scripts/tts_edge.py --storyboard storyboard.json --outdir build/tts
   ```

4. **试听 2 句再批量**：语速 `+5%`～`+15%` 最像带货口播；超过 `+20%` 会显得赶。
5. 交给 `ffmpeg-auto-assemble`（它会自动调用本脚本）或自己的剪辑软件。

## 口播稿改写规则 Script rules

- 数字写成「读法」：`2核8G` → `两核八G`；`24h` → `二十四小时`；型号字母之间加空格 `A I`。字幕可以保留原写法（`sub` 字段）。
- 一句只说一件事；逗号就是换气点，句末用句号/问号让语调落下来。
- 去掉书面词：「此款产品具有…」→「这只杯子…」。
- 英文品牌名若读错，用拼读或谐音写进 `line`，`sub` 保留正确拼写。

## 提示词模板 Prompt template

```text
把下面的带货文案改写成适合 TTS 朗读的口播稿：每句 8–20 字、一句一件事、口语化；
数字和字母写成读法；另外输出一列「字幕版」保留原始写法并用 **加粗** 标 1 个关键词。
不要添加原文没有的卖点或数据。原文：{…}
```

## 检查清单 Checklist

- [ ] 先试听 2 句确认音色/语速
- [ ] 数字、英文、品牌名读音正确
- [ ] `durations.json` 已生成，总时长符合目标
- [ ] 商用前确认所在平台与地区对 AI 配音的标注要求（如需标注「AI 生成」）

## 常见问题与修复 Failure fixes

| 问题 | 修复 |
|---|---|
| `edge-tts failed` / 超时 | 网络问题，脚本已重试 3 次；换网络或稍后再试；离线时用 `assemble.py --tts none` 先预览画面 |
| 读音错误 | 在 `line` 里写谐音/拼读，`sub` 保留原文 |
| 句子之间停顿太长 | 已自动去首尾静音；调 storyboard 的 `pad`（默认 0.25s） |
| 声音太平 | 换 `YunjianNeural`/`XiaoyiNeural`；`--pitch "+5Hz"`；句尾用问号/感叹号 |
| 需要真人感 | edge-tts 是合成音；高要求场景改用真人录音，流水线照样可用（把录音放进 `build/tts/lXX.wav`） |

> edge-tts 由社区维护（[rany2/edge-tts](https://github.com/rany2/edge-tts)，LGPL-3.0），调用的是微软在线服务；本仓库只把它当依赖安装，不包含其代码。
