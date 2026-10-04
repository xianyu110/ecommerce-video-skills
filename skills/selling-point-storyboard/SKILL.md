---
name: selling-point-storyboard
description: "卖点分镜表：把商品卖点拆成 15–60 秒带货短视频的逐镜分镜表（时间码、画面、台词、字幕、花字、素材来源、运镜），并直接输出可渲染的 storyboard.json。Use when the user wants a storyboard, 分镜, 分镜脚本, shot list, 带货视频脚本, video script from selling points, or needs to plan a product video before generating or editing."
---

# 卖点分镜表 · Selling-Point Storyboard

从「卖点清单」到「能直接渲染的分镜表」。输出两份：人看的 Markdown 表格 + 机器跑的 `storyboard.json`（给 `ffmpeg-auto-assemble`）。

> Part of [ecommerce-video-skills](https://github.com/xianyu110/ecommerce-video-skills)

## 输入 Inputs

- 商品信息与 **真实** 卖点（3 个最好，最多 5 个）
- 时长目标：15s（种草/主图视频）· 30s（标准带货）· 60s（测评/讲解）
- 现有素材：商品图、场景图、实拍视频（文件名列出来）
- 平台 + 画幅；配音语言与音色偏好

## 结构公式 Structure

| 时长 | 结构（镜数） |
|---|---|
| 15s | 钩子(1) → 产品亮相(1) → 卖点×2–3(2–3) → 行动号召(1)，共 5–6 镜 |
| 30s | 钩子 → 痛点放大 → 产品亮相 → 卖点×3（每个「说 + 证明」）→ 使用场景 → 行动号召，8–10 镜 |
| 60s | 钩子 → 我的经历 → 开箱 → 卖点×3–4 演示 → 对比 → 缺点/适合谁 → 行动号召，14–18 镜 |

规则：**一镜一信息**；每个卖点都要配「证明画面」（演示、细节、对比），光说不演不算卖点。

## 步骤 Steps

1. 卖点排序：按「用户最在意 × 画面最好证明」排序，最强的放第 2–3 镜。
2. 每镜写：时间、画面（用哪张素材/要拍什么）、台词（每镜 ≤ 2 句，中文 4–5 字/秒）、字幕（关键词用 `**加粗**` 标高亮）、花字（可选）、运镜。
3. 时长核算：台词字数 ÷ 4.5 ≈ 秒数；总时长超了就删台词，不要加快语速超过 +20%。
4. 缺素材的镜头标记 `TODO`，并给出拍摄/生成建议（可交给 `image-to-video-shots` 或姊妹仓库 [ecommerce-image-skills](https://github.com/xianyu110/ecommerce-image-skills) 出图）。
5. 输出 Markdown 表 + `storyboard.json`。

## 分镜表模板

| # | 时间 | 画面 / 素材 | 台词（配音） | 字幕（**高亮**） | 花字 | 运镜 |
|---|---|---|---|---|---|---|
| 1 | 0–3s | lifestyle.webp 户外手拿杯 | 夏天带冰水出门，不到中午就变温了？ | 冰水不到中午就**变温**了？ | 冰水撑不到中午？ | punch |
| 2 | 3–5s | white-bg.webp 白底亮相 | 换这只保温杯试试。 | 换这只保温杯试试 | — | zoom_in |
| … | | | | | | |

## storyboard.json 模板

```json
{
  "voice": "zh-CN-YunxiNeural", "rate": "+10%", "bgm": "auto", "tag": "品牌名 · 型号",
  "shots": [
    {"image": "assets/scene.jpg", "motion": "punch", "line": "钩子台词", "sub": "钩子**关键词**", "title": "花字"},
    {"image": "assets/main.jpg", "motion": "zoom_in", "line": "产品亮相台词"},
    {"image": "assets/detail.jpg", "motion": "pan_down", "fit": "blur", "line": "卖点一台词", "sub": "卖点一|**证明**"},
    {"video": "clips/demo.mp4", "start": 3.0, "line": "卖点二演示台词"},
    {"image": "assets/end-card.png", "min": 3.0, "line": "行动号召台词", "sub": "", "cta": "点击下方链接 ›"}
  ]
}
```

字段说明见 `ffmpeg-auto-assemble`。渲染：`python skills/ffmpeg-auto-assemble/scripts/assemble.py storyboard.json -o out/video.mp4`。

## 提示词模板 Prompt template

```text
你是电商短视频编导。根据以下信息写一份 {15} 秒竖屏带货分镜表。
商品：{…}；目标人群：{…}；平台：{…}
真实卖点（不得编造数据、认证、价格）：{…}
可用素材文件：{lifestyle.webp, white-bg.webp, …}
要求：一镜一信息；每个卖点配证明画面；台词每镜 ≤ 2 句，总字数 ≤ {时长×4.5}；
关键词用 **加粗**；最后一镜是行动号召。
先输出 Markdown 分镜表，再输出符合下面 schema 的 storyboard.json：{粘贴上方模板}
```

## 检查清单 Checklist

- [ ] 第 1 镜是钩子（见 `hook-3s-script`），最后 1 镜是行动号召
- [ ] 总台词字数 ≈ 时长 × 4.5（中文）/ × 2.5 词（英文）
- [ ] 每个卖点都有证明画面；没有编造的数据、认证、价格
- [ ] 每镜素材都存在或标了 TODO
- [ ] JSON 能通过 `python -m json.tool storyboard.json`

## 常见问题与修复 Failure fixes

| 问题 | 修复 |
|---|---|
| 成片超时 | 删台词而不是加速；合并信息相近的镜头 |
| 卖点像念说明书 | 每个卖点改成「场景 + 结果」：「放包里一下午，本子还是干的」 |
| 素材不够 | 同一张图用不同 `motion` / `fit` 做两镜；或生成场景图 |
| 字幕挡商品 | 卖点镜头用 `"fit": "blur"`，商品放在上半屏 |
