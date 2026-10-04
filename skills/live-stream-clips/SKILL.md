---
name: live-stream-clips
description: "直播切片：从电商直播录屏中找出高光片段（按时间戳 / 按字幕关键词 / 按停顿自动提议），批量导出 9:16 竖屏切片，自动模糊填充横屏画面、烧录标题与字幕、响度标准化，并给切片写标题与开头钩子。Use when the user has a livestream recording and wants 直播切片, 切片, highlights, clips, 高光片段, repurpose a live stream into short videos for 抖音 / 视频号 / TikTok."
---

# 直播切片 · Live-Stream Clips

几小时直播 → 一批 15–60 秒竖屏切片。选段可以靠人、靠字幕关键词、或靠停顿自动提议；导出统一交给 `scripts/live_clip.py`。

> Part of [ecommerce-video-skills](https://github.com/xianyu110/ecommerce-video-skills)
>
> 只切你自己的直播，或已获得主播/品牌授权的直播。

## 输入 Inputs

- 直播录像（mp4/flv/mov，横屏竖屏都行）
- 可选：字幕/转写 SRT（平台导出或用任意 ASR 工具生成）
- 目标：每条时长、数量、要突出的商品或话题

## 三种选段方式

```bash
# A. 已有时间戳（人工或 agent 读转写后挑选）
#    cuts.csv:  start,end,title
#               00:12:05,00:12:40,冰块放一晚还在？现场演示
python scripts/live_clip.py live.mp4 --cuts cuts.csv --outdir out/clips

# B. 按字幕关键词找片段（每个命中点向前 30% / 向后 70% 取 --window 秒，重叠自动合并）
python scripts/live_clip.py live.mp4 --srt live.srt --keywords "演示,对比,上链接,库存" --window 30 --burn-subs

# C. 没有字幕：在停顿处切分，输出候选 CSV 再人工/agent 挑选
python scripts/live_clip.py live.mp4 --propose 30 > proposals.csv
```

## 步骤 Steps

1. **先读转写**（有 SRT 时）：让 agent 标出「演示、对比、用户提问被解答、福利说明」等高光点，写进 `cuts.csv`。
2. **每条切片要能独立看懂**：开头 3 秒必须有钩子——从「问题/演示开始」切入，而不是从主播寒暄切入。
3. **起止点微调**：起点落在句子开头、终点落在句子结束后 0.3 秒。
4. **导出**：横屏自动转 9:16（模糊背景 + 居中画面），可烧标题（`title` 列）和字幕（`--burn-subs`）。
5. **写切片标题**：用 `hook-3s-script` 的钩子类型给每条写 2 个标题，交给 `cover-title-ab`。

## 高光信号 What makes a good clip

| 信号 | 例子 |
|---|---|
| 现场演示 | 倒水、摔、对比测试 |
| 问答 | 「有人问能不能放洗碗机…」 |
| 情绪峰值 | 惊讶、笑场、观众刷屏 |
| 规则说明 | 赠品、售后、发货（注意：价格/优惠信息以当前实际为准，过期切片要下架或剪掉） |

## 提示词模板 Prompt template

```text
下面是直播转写（SRT）。请找出 {8} 个适合做 {20–40} 秒竖屏切片的片段：
每段必须能独立看懂、开头 3 秒有钩子（问题/演示/结果），避免寒暄和长时间沉默；
输出 CSV：start,end,title（title ≤ 14 字，不使用绝对化用语，不承诺具体价格）。
转写：{粘贴 SRT}
```

## 检查清单 Checklist

- [ ] 每条切片开头 3 秒有钩子、结尾不断句
- [ ] 标题与字幕不在底部 UI 区；横屏画面完整可见
- [ ] 切片里出现的价格/优惠/库存信息仍然有效，否则剪掉
- [ ] 有直播内容的使用授权

## 常见问题与修复 Failure fixes

| 问题 | 修复 |
|---|---|
| `--propose` 只返回一段 | 背景音乐盖住了停顿；改用 SRT 关键词法，或调低 `silencedetect` 的 `noise` 阈值 |
| 字幕与画面不同步 | 确认 SRT 时间轴对应原始录像；脚本使用 `-copyts` 保持源时间轴 |
| 标题含冒号/引号报错 | 脚本已替换为全角符号 |
| 切点在半句话 | 用 SRT cue 的起止时间作为切点 |
