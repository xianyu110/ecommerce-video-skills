---
name: multilingual-dubbing
description: "多语言本地化配音：把中文带货视频本地化为英语、日语、韩语、东南亚语（印尼/泰/越/马来/菲律宾）、西语等版本——本地化改写口播（不是直译）、选对 edge-tts 音色、生成对应字幕与花字，并用同一份 storyboard 一键渲染多语言成片。Use when the user wants dubbing, 多语言, 本地化, 翻译配音, 出海, localize a product video for TikTok Shop US/UK/SEA, English voice-over, or multiple language versions of one video."
---

# 多语言本地化配音 · Multilingual Dubbing

一份 `storyboard.json`，加上 `line_en` / `sub_en` / `title_en` / `cta_en` / `tag_en` 这类字段，就能用 `--lang en` 渲染出英文版。画面、节奏、转场全部复用；镜头时长按新语言的配音自动重算。

> Part of [ecommerce-video-skills](https://github.com/xianyu110/ecommerce-video-skills) · 脚本：`scripts/assemble.py --lang <code>`（内含 `tts_edge.py`、`make_subs.py`）

## 输入 Inputs

- 已完成的中文 `storyboard.json`
- 目标市场（不只是语言）：US / UK / ID / TH / VN / MY / PH / JP / KR / MX …
- 当地可用的卖点表述与合规要求（如需）

## 步骤 Steps

1. **本地化改写，不直译**：保留卖点，换成当地说法和场景（中文「通勤」→ 美国「commute / road trip」；东南亚强调「hot weather / ice」）。
2. **长度对齐**：英文语速约 2.5 词/秒；每句词数 ≈ 原镜头秒数 × 2.5，超长就删。
3. **写字段**：每镜加 `line_xx`（配音）、`sub_xx`（字幕，可用 `**高亮**` 与 `|`）、可选 `title_xx`、`cta_xx`；顶层加 `tag_xx`。缺失的字段回退到中文原字段（`sub_xx` 写 `""` 表示不出字幕）。
4. **选音色**：

   | 市场 | 音色示例（`--voice`） |
   |---|---|
   | 美国 | `en-US-AndrewNeural`（男）· `en-US-AvaNeural`（女）· `en-US-EmmaNeural` |
   | 英国 | `en-GB-SoniaNeural` |
   | 印尼 | `id-ID-GadisNeural` |
   | 泰国 | `th-TH-PremwadeeNeural` |
   | 越南 | `vi-VN-HoaiMyNeural` |
   | 马来西亚 | `ms-MY-YasminNeural` |
   | 菲律宾 | `fil-PH-BlessicaNeural` |
   | 日本 / 韩国 | `ja-JP-NanamiNeural` / `ko-KR-SunHiNeural` |
   | 墨西哥 / 巴西 | `es-MX-DaliaNeural` / `pt-BR-FranciscaNeural` |

   全部音色：`python scripts/tts_edge.py --list en-` / `--list id-ID` …

5. **渲染**：

   ```bash
   python scripts/assemble.py storyboard.json --lang en --voice en-US-AndrewNeural --rate "+5%" -o out/video-en.mp4 --build build/en
   python scripts/assemble.py storyboard.json --lang th --voice th-TH-PremwadeeNeural --font "Noto Sans Thai" -o out/video-th.mp4 --build build/th
   ```

   每种语言用独立 `--build` 目录。泰语/阿拉伯语等需安装对应字体并用 `--font` 指定（CJK 字体不含这些字形）。
6. **母语者过一遍**：至少检查钩子句、CTA 和品牌名读音。

## 字段示例

```json
{"image": "assets/infographic.webp", "fit": "blur",
 "line": "早上装满冰块，到晚上冰块还在。", "sub": "早上装满冰块|到晚上**冰块还在**", "title": "24h 保冰",
 "line_en": "Fill it with ice in the morning, it's still there at night.",
 "sub_en": "Ice in the morning|**still there at night**", "title_en": "Ice for 24h"}
```

仓库示例 `examples/aura-bottle/storyboard.json` 已包含完整英文字段。

## 提示词模板 Prompt template

```text
把这份中文带货 storyboard 本地化为 {美国英语}，面向 {TikTok Shop US} 用户：
- 不直译，用当地常见说法和场景；保留所有卖点，不新增数据或承诺
- 每句词数 ≤ 原镜头秒数 × 2.5；字幕可用 | 分段、**加粗** 1 个关键词
- 为每个 shot 输出 line_en / sub_en（以及原本有 title/cta 的 title_en / cta_en），顶层输出 tag_en
- 品牌名保持原拼写；单位换算为当地习惯（如 oz / °F），但数值必须与原文等价
storyboard：{粘贴}
```

## 检查清单 Checklist

- [ ] 改写而非直译；单位/习惯已本地化且数值等价
- [ ] 每镜配音时长与画面匹配（看 `build/<lang>/timing.json`）
- [ ] 字体覆盖目标语言字形
- [ ] 母语者检查钩子、CTA、品牌读音
- [ ] 当地平台对 AI 配音/广告标注的要求已确认

## 常见问题与修复 Failure fixes

| 问题 | 修复 |
|---|---|
| 字幕显示方框 | 安装目标语言字体并 `--font` 指定 |
| 某镜太长/太短 | 删减或补充该镜 `line_xx`；或设 `min` |
| 品牌名读错 | `line_xx` 写音译拼读，`sub_xx` 保留正确拼写 |
| 花字仍是中文 | 补 `title_xx` / `cta_xx` / `tag_xx` |
