<div align="center">

# 🎬 Ecommerce Video Skills

**12 个电商短视频 Agent Skills · 一张商品图 → 带配音、字幕、BGM 的 9:16 带货视频**<br>
**12 Agent Skills for ecommerce short videos — 抖音 · TikTok Shop · 视频号 · 小红书 · 淘宝主图视频 · Amazon**

[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-12-8b5cf6)](#-skills--技能列表)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-ready-d97757)](#-安装)
[![Codex](https://img.shields.io/badge/Codex-ready-111111)](#-安装)
[![Cursor](https://img.shields.io/badge/Cursor-ready-2563eb)](#-安装)
[![ffmpeg](https://img.shields.io/badge/ffmpeg-local%20render-007808)](skills/ffmpeg-auto-assemble/SKILL.md)
[![edge-tts](https://img.shields.io/badge/edge--tts-free%20voice-0ea5e9)](skills/ai-voiceover-edge-tts/SKILL.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![姊妹仓库](https://img.shields.io/badge/%E5%A7%8A%E5%A6%B9%E4%BB%93%E5%BA%93-ecommerce--image--skills-f97316)](https://github.com/xianyu110/ecommerce-image-skills)

[中文](#-中文) · [English](#-english) · [效果 Demo](#-效果--demo) · [Skills](#-skills--技能列表) · [没有 Claude / API？](#-没有-claude--api)

<br>

<img src="https://upload.maynor1024.live/file/1791117340370_evs-aura-preview.gif" width="300" alt="ecommerce-video-skills demo: 17s 9:16 product video rendered by scripts/assemble.py">

<sub>👆 上面这条 17 秒竖屏视频（配音 + 字幕花字 + 转场 + BGM）由 <code>scripts/assemble.py</code> 在本地一条命令渲染，素材是 6 张商品图 · <a href="https://upload.maynor1024.live/file/1791117346796_evs-aura-bottle-9x16-zh.mp4">下载 MP4（中文）</a> · <a href="https://upload.maynor1024.live/file/1791117344714_evs-aura-bottle-9x16-en.mp4">MP4 (English)</a></sub>

<img src="https://upload.maynor1024.live/file/1791117345401_evs-aura-gallery.jpg" width="860" alt="frame gallery">

```bash
npx skills add xianyu110/ecommerce-video-skills
```

</div>

---

## 🇨🇳 中文

把「写脚本 → 找钩子 → 分镜 → 图生视频 → 配音 → 字幕花字 → 剪辑 → 导出 → 封面」拆成 **12 个可单独安装的 Agent Skill**。丢几张商品图给 Claude Code / Codex / Cursor，它会写钩子和分镜、出多模型镜头提示词，并且**真的在本地把视频剪出来**。

**和一堆提示词的区别：**

- 🎞 **能跑的流水线**：`storyboard.json` → edge-tts 逐句配音 → Ken Burns 镜头 → xfade 转场 → ASS 字幕/花字 → BGM 自动闪避 → 两遍响度标准化（≈ -14 LUFS）→ MP4 + SRT。纯 Python + ffmpeg，无需剪辑软件、无需 API Key。
- 🔒 **商品一致性锁**：图生视频提示词第一步先锁定形状/颜色/Logo，减少「视频很酷但商品变了」。
- 🧠 **模型中立**：同一份分镜适配 Seedance / 可灵 / Veo / Runway / 海螺 / 万相 …；**不编造任何模型的价格或参数**，每个镜头都有本地 Ken Burns 兜底。
- 📐 **平台规格 + 安全区**：抖音 / TikTok Shop / 视频号 / 小红书 / 淘宝主图视频 / Amazon 一键导出，字幕自动避开底部商品卡和右侧按钮。
- 🌏 **出海友好**：同一份 storyboard 加 `line_en` 等字段，`--lang en` 直接渲染英文版（东南亚、日韩、拉美音色已列好）。
- ⚖️ **合规意识**：钩子/评测模板内置广告法绝对化用语检查、「只写测过的数据」、公平对比规则。

### 📦 安装

```bash
npx skills add xianyu110/ecommerce-video-skills          # 一行安装（skills CLI）
# 或在 Claude Code 里：/plugin marketplace add xianyu110/ecommerce-video-skills
```

手动安装：

```bash
git clone https://github.com/xianyu110/ecommerce-video-skills.git && cd ecommerce-video-skills
mkdir -p ~/.claude/skills && cp -r skills/* ~/.claude/skills/     # Claude Code（或项目内 .claude/skills/）
mkdir -p ~/.codex/skills  && cp -r skills/* ~/.codex/skills/      # Codex
mkdir -p .cursor/skills   && cp -r skills/* .cursor/skills/       # Cursor（项目内）
pip install -r requirements.txt                                    # pillow numpy edge-tts；另需 ffmpeg（含 libass）
```

每个 skill 文件夹自带所需脚本，互不依赖，只复制需要的即可。

### ⚡ 30 秒跑通示例

```bash
python scripts/assemble.py examples/aura-bottle/storyboard.json -o out/aura.mp4                    # 中文版
python scripts/assemble.py examples/aura-bottle/storyboard.json --lang en --voice en-US-AndrewNeural -o out/aura-en.mp4 --build build/en
python scripts/export_platform.py out/aura.mp4 --platform douyin tiktok-shop channels xiaohongshu taobao-main amazon
python scripts/cover_ab.py out/aura.mp4 --images build/still00.png build/still03.png --titles "冰水撑不到中午？|早上的冰，晚上还在"
```

### 🚀 对 agent 这样说

```text
用 hook-3s-script 给这个保温杯写 8 个前三秒开场，标出推荐 Top 3
用 selling-point-storyboard 按 ./photos 里的图做一条 15 秒抖音分镜，并输出 storyboard.json
用 ffmpeg-auto-assemble 把 storyboard.json 渲染成片，然后导出抖音和小红书版本
把这条视频本地化成美国英语和印尼语版本（multilingual-dubbing）
这是 3 小时直播录像和字幕，帮我切 8 条 30 秒高光（live-stream-clips）
```

### 🧭 流水线

```text
商品图 ──► hook-3s-script ──► selling-point-storyboard ──► storyboard.json
  │                                   │
  └► image-to-video-shots ◄── multi-model-shot-prompts（可选：任意视频模型出镜头）
                                      ▼
   ai-voiceover-edge-tts ─► subtitles-and-text-effects ─► ffmpeg-auto-assemble ─► MP4 + SRT
                                                                 │
     platform-spec-export ◄──────────────────────────────────────┤
     cover-title-ab ◄────────────────────────────────────────────┤
     multilingual-dubbing（--lang en / id / th …）◄──────────────┘
   直播录像 ─► live-stream-clips ─► 9:16 切片      开箱/评测 ─► unboxing-comparison-review
```

---

## 🎞 效果 / Demo

| 中文成片（帧） | English version (frames) |
|---|---|
| <img src="https://upload.maynor1024.live/file/1791117345401_evs-aura-gallery.jpg" width="420" alt="zh frames"> | <img src="https://upload.maynor1024.live/file/1791117349101_evs-aura-gallery-en.jpg" width="420" alt="en frames"> |
| [▶ MP4 中文](https://upload.maynor1024.live/file/1791117346796_evs-aura-bottle-9x16-zh.mp4) · 仓库内 [docs/media/aura-bottle-9x16.mp4](docs/media/aura-bottle-9x16.mp4) | [▶ MP4 English](https://upload.maynor1024.live/file/1791117344714_evs-aura-bottle-9x16-en.mp4) |

**封面 A/B**（`cover-title-ab`，用干净底图 + 3 种标题/版式）：

<img src="https://upload.maynor1024.live/file/1791117343900_evs-aura-covers-ab.jpg" width="640" alt="cover A/B sheet">

> 规格：1080×1920 · 30fps · H.264 + AAC · ≈ -14 LUFS · 17.0 秒 · 配音 edge-tts `zh-CN-YunxiNeural` / `en-US-AndrewNeural` · BGM 由 `make_bgm.py` 实时合成（免版权）。<br>
> 商品「AURA」是 [ecommerce-image-skills](https://github.com/xianyu110/ecommerce-image-skills) 用 AI 生成的虚构商品，「24h 保冰」等卖点仅作演示。

---

## 🧩 Skills / 技能列表

| Skill | 中文说明 | 脚本 |
|---|---|---|
| [`image-to-video-shots`](skills/image-to-video-shots/SKILL.md) | **主图转视频**：商品图 → 图生视频镜头提示词（运镜/动作/约束）+ 商品一致性锁 + 本地 Ken Burns 兜底 | assemble.py |
| [`hook-3s-script`](skills/hook-3s-script/SKILL.md) | **3 秒钩子脚本**：9 种钩子类型一次出 6–10 版（台词+画面+花字），广告法自检 | — |
| [`selling-point-storyboard`](skills/selling-point-storyboard/SKILL.md) | **卖点分镜表**：15/30/60 秒结构公式，一镜一信息，直接输出可渲染的 storyboard.json | — |
| [`multi-model-shot-prompts`](skills/multi-model-shot-prompts/SKILL.md) | **多模型镜头提示词适配**：通用骨架 + 运镜词表 + 文生/首帧/首尾帧写法，不编造价格/参数 | — |
| [`ai-voiceover-edge-tts`](skills/ai-voiceover-edge-tts/SKILL.md) | **AI 口播配音**：edge-tts 逐句合成、去静音、时长统计、缓存；口播稿改写规则与音色推荐 | tts_edge.py |
| [`subtitles-and-text-effects`](skills/subtitles-and-text-effects/SKILL.md) | **字幕与花字**：ASS 四种样式（字幕/弹出花字/贴纸/CTA）、关键词高亮、安全区 | make_subs.py |
| [`ffmpeg-auto-assemble`](skills/ffmpeg-auto-assemble/SKILL.md) | **ffmpeg 自动拼接成片**：一条命令出片（配音、转场、字幕、BGM 闪避、响度标准化） | assemble.py 等 5 个 |
| [`platform-spec-export`](skills/platform-spec-export/SKILL.md) | **TikTok Shop / 抖音 / 视频号规格导出**：9:16 / 3:4 / 1:1 / 16:9，模糊填充或裁切，安全区预览 | export_platform.py |
| [`live-stream-clips`](skills/live-stream-clips/SKILL.md) | **直播切片**：时间戳 / 字幕关键词 / 停顿提议三种选段，批量导出竖屏切片 | live_clip.py |
| [`unboxing-comparison-review`](skills/unboxing-comparison-review/SKILL.md) | **开箱 / 对比评测模板**：结构、拍摄清单、公平对比规则、storyboard 示例 | make_cards.py |
| [`multilingual-dubbing`](skills/multilingual-dubbing/SKILL.md) | **多语言本地化配音**：本地化改写 + 各市场音色 + `--lang` 一键渲染多语言版本 | assemble.py |
| [`cover-title-ab`](skills/cover-title-ab/SKILL.md) | **封面与标题 A/B**：自动挑清晰帧/干净底图 + 多标题版式，对比图与测试记录表 | cover_ab.py |

---

## 🔑 没有 Claude / API？

这些 skill 在任何能读 `SKILL.md` 的 agent 里都能用；本地剪辑脚本**不需要任何 API Key**。如果你还没有趁手的模型/接口：

- **方法一**：`https://claude-opus.top/` —— Claude 国内镜像站，打开即用，把 SKILL.md 内容粘进对话就能按步骤出脚本、分镜和提示词。
- **方法二**：`https://tryallapi.com/register?aff=5A6A` —— 一站式 API，调视频 / 图像 / 大模型。需要在脚本或 agent 里调用模型时，推荐把 `BASE_URL=https://tryallapi.com/v1` 作为 OpenAI 兼容接口的备选地址（任何 OpenAI 兼容网关均可）。

```bash
export OPENAI_BASE_URL=https://tryallapi.com/v1   # 推荐的备选 BASE_URL
export OPENAI_API_KEY=sk-...
```

---

## 👭 姊妹仓库 / Sister repo

- **[ecommerce-image-skills](https://github.com/xianyu110/ecommerce-image-skills)** —— 12 个电商出图 Skill（白底主图、场景图、卖点图、A+、小红书封面、详情长图…）。**先出图，再用本仓库把图变成视频**：本仓库示例视频的素材就来自它。

## 🤝 Contributing

欢迎 PR：新的平台规格（附官方链接）、更好的钩子/分镜模板、更多脚本。请保持每个 skill 自包含（`skills/<name>/SKILL.md` + `scripts/`）；修改 `scripts/` 后运行 `python tools/sync_scripts.py` 同步到各 skill。

## 📜 致谢与许可

MIT © xianyu110。内容为原创编写；参考项目（MoneyPrinterTurbo · MIT、shuohao-skills · Apache-2.0、reelbench-skills · Apache-2.0、ffmpeg-skill · MIT 等）只借鉴了结构思路，未复制文本或代码，详见 [docs/credits.md](docs/credits.md)。edge-tts 为 LGPL-3.0 依赖；FFmpeg 由用户自行安装。平台规则经常变化，上传前请以各平台官方说明为准。

---

## 🇺🇸 English

Twelve installable Agent Skills that take an ecommerce product from **a few photos to a finished 9:16 short video** — hooks, storyboards, model-agnostic image-to-video prompts, free edge-tts voice-over, styled subtitles, **a working local ffmpeg render pipeline**, platform exports (TikTok Shop, Douyin, WeChat Channels, Xiaohongshu, Taobao, Amazon), live-stream clipping, unboxing/comparison templates, multilingual dubbing and cover/title A/B tests. Chinese-first, English included.

```bash
npx skills add xianyu110/ecommerce-video-skills        # or: /plugin marketplace add xianyu110/ecommerce-video-skills
pip install -r requirements.txt                          # + ffmpeg with libass
python scripts/assemble.py examples/aura-bottle/storyboard.json --lang en --voice en-US-AndrewNeural -o out/aura-en.mp4
```

- **Real pipeline, no API key**: storyboard.json → per-line edge-tts → Ken Burns shots → xfade → ASS captions & pop-up titles → ducked BGM → two-pass loudnorm (≈ -14 LUFS) → MP4 + SRT.
- **Model-agnostic prompts**: one shot list adapted for any image-to-video model, with a product-identity lock and a local fallback for every shot. No invented prices or model limits.
- **Localisation**: add `line_en` / `sub_en` / `title_en` fields and render with `--lang en`; voices listed for US/UK/SEA/JP/KR/LATAM.
- Skills: `image-to-video-shots` · `hook-3s-script` · `selling-point-storyboard` · `multi-model-shot-prompts` · `ai-voiceover-edge-tts` · `subtitles-and-text-effects` · `ffmpeg-auto-assemble` · `platform-spec-export` · `live-stream-clips` · `unboxing-comparison-review` · `multilingual-dubbing` · `cover-title-ab` (see the table above).
- No model access? Use `https://claude-opus.top/` (Claude mirror for mainland China) or `https://tryallapi.com/register?aff=5A6A` (one API for video / image / LLMs; recommended fallback `BASE_URL=https://tryallapi.com/v1`).
- Images first? See the sister repo **[ecommerce-image-skills](https://github.com/xianyu110/ecommerce-image-skills)**.

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=xianyu110/ecommerce-video-skills&type=Date)](https://star-history.com/#xianyu110/ecommerce-video-skills&Date)

---

<div align="center">

我是 MaynorAI 团队，分享 AI 编程、AI SaaS 工具出海、一人团队搭建经验。

</div>
