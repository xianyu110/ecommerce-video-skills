---
name: image-to-video-shots
description: "主图转视频：把一张或几张商品主图/白底图/场景图，写成可直接喂给图生视频模型的镜头提示词（运镜、主体动作、光线、时长、负面约束），并保证商品不变形。Use when the user has product images and wants a product video, 主图视频, 图生视频, image-to-video, animate a product photo, or 让主图动起来 — with any image-to-video model (Seedance / 可灵 Kling / Veo / Runway / Hailuo / Wan …) or a local Ken Burns fallback."
---

# 主图转视频 · Image → Video Shots

把静态商品图变成 3–6 秒的「会动的镜头」：每张图配一条图生视频提示词 + 一条本地兜底方案（ffmpeg Ken Burns），保证没有视频模型也能出片。

> Part of [ecommerce-video-skills](https://github.com/xianyu110/ecommerce-video-skills) · 图从哪来？用姊妹仓库 [ecommerce-image-skills](https://github.com/xianyu110/ecommerce-image-skills) 先出白底图/场景图/卖点图。

## 输入 Inputs

| 必填 | 说明 |
|---|---|
| 商品图 1–6 张 | 白底主图、场景图、细节图均可；越清晰越好（≥1000px） |
| 投放平台 | 抖音 / TikTok Shop / 视频号 / 淘宝主图视频 / Amazon（决定画幅 9:16、1:1、3:4、16:9） |
| 可选 | 卖点（最多 3 条）、目标时长、风格（清爽 / 高级 / 活力）、可用的视频模型 |

## 步骤 Steps

1. **商品一致性锁（必做）**：看图写下形状、颜色、Logo/文字、材质、配件——之后每条提示词原样带上，**禁止模型改商品**。

   ```text
   PRODUCT LOCK: tall matte sage-green bottle, natural bamboo lid with black loop,
   small white "AURA" wordmark on upper body. Keep shape, colour, logo and proportions identical in every frame.
   ```

2. **给每张图选一个镜头角色**（一张图只做一件事）：

   | 图类型 | 推荐镜头 | 动作 |
   |---|---|---|
   | 白底主图 | 缓慢推近 / 360° 环绕（模型支持时） | 产品静止，光影扫过 |
   | 场景图 | 轻微横移 / 手部入画 | 人物拿起、倒水、放进包里 |
   | 细节图 | 微距推近 | 光斑划过材质纹理 |
   | 卖点/信息图 | 静止或极慢推 | 不让文字变形（文字区域尽量不动） |

3. **写提示词**（下方模板）：主体 → 动作 → 运镜 → 光线/氛围 → 时长/画幅 → 约束。动作越小，商品越稳。
4. **每条镜头都给本地兜底**：没有视频模型 / 模型把商品变形时，用 `ffmpeg-auto-assemble` 的 `motion` 字段（`zoom_in` / `pan_left` / `punch` …）直接让静图动起来。
5. **交付**：镜头表（编号、图、提示词、兜底 motion、时长）+ 可以直接粘进 `storyboard.json` 的 shots 片段。

## 提示词模板 Prompt templates

**通用图生视频（中文）**

```text
[参考图] 作为首帧。{PRODUCT LOCK}
镜头：{缓慢推近 / 从左向右平移 / 低角度环绕 30°}，运动平稳，无抖动。
画面动作：{冰块落入杯中溅起细小水花 / 手从画面右侧入画拿起杯子 / 柔和光斑从左扫到右}。
光线：{明亮自然光 / 柔和棚拍光，浅景深}。
时长约 {4} 秒，{9:16} 竖屏。
要求：商品形状、颜色、Logo 与参考图完全一致；不新增文字；不出现其他品牌；手部自然、五指正常。
```

**English (most models parse English best)**

```text
Use the reference image as the first frame. {PRODUCT LOCK}
Camera: {slow push-in | gentle left-to-right truck | 30° low-angle orbit}, smooth, no shake.
Action: {ice cubes drop into the bottle with a small splash | a hand enters from the right and lifts the bottle | a soft light sweep across the surface}.
Lighting: {bright natural daylight | soft studio light, shallow depth of field}.
About {4} seconds, {9:16} vertical.
Keep the product's shape, colour and logo identical to the reference. No new text, no other brands, natural hands.
```

**首尾帧模式**（模型支持首帧+尾帧时）：首帧 = 白底主图，尾帧 = 场景图，提示词只写「从棚拍过渡到户外场景，商品保持不变，镜头缓慢拉远」。

**负面约束（模型支持 negative prompt 时）**：`deformed product, melting, extra logos, changed colour, warped text, extra fingers, flicker, watermark`

## 本地兜底（无模型）

```json
{"image": "assets/white-bg.webp", "motion": "zoom_in", "line": "换这只保温杯试试。"}
```

```bash
python scripts/assemble.py storyboard.json -o out/main-video.mp4 --size 1080x1080   # 本目录已附带 assemble.py
```

## 检查清单 Checklist

- [ ] 每条提示词都带 PRODUCT LOCK
- [ ] 一个镜头只有一个主要动作；商品本身动作越少越好
- [ ] 卖点图/带字图只用静止或极慢运镜
- [ ] 画幅与平台一致（主图视频常用 1:1 / 3:4，信息流 9:16）
- [ ] 不写模型不支持的参数；时长、分辨率以所用模型文档为准
- [ ] 每个镜头都有本地 motion 兜底

## 常见问题与修复 Failure fixes

| 问题 | 修复 |
|---|---|
| 商品变形 / Logo 糊掉 | 减少动作，改成「camera moves, product stays still」；或改用本地 Ken Burns |
| 手部畸形 | 去掉手部动作，或让手只出现半秒、在画面边缘 |
| 画面闪烁 | 缩短时长、降低运动幅度、关掉夸张光效 |
| 文字乱码 | 别让模型生成文字；字幕和花字交给 `subtitles-and-text-effects` 后期加 |
| 颜色漂移 | 在提示词里写出色值或颜色名，并要求 "match the reference colour exactly" |
