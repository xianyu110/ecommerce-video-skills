---
name: platform-spec-export
description: "TikTok Shop / 抖音 / 视频号 / 小红书 / 淘宝主图视频 / Amazon 规格导出：把一条母版视频一键转成各平台推荐画幅与编码（9:16、3:4、1:1、16:9，模糊填充或智能裁切），输出规格报告，并可叠加 UI 安全区预览。Use when the user asks for export settings, 导出规格, 尺寸, 分辨率, 画幅, 上传要求, re-encode for TikTok Shop / Douyin / WeChat Channels / Xiaohongshu / Taobao / Amazon, or safe zones."
---

# 平台规格导出 · Platform Spec Export

一条母版（建议 1080×1920、30fps）→ 多平台文件 + `export_report.json`。脚本：`scripts/export_platform.py`。

> Part of [ecommerce-video-skills](https://github.com/xianyu110/ecommerce-video-skills)
>
> ⚠️ 平台规则经常变。下表是**稳妥的推荐编码**，不是官方上限；时长、文件大小、是否允许外链/价格信息等，上传前请在各平台官方上传页/商家后台确认。

## 预设 Presets

| `--platform` | 输出 | 用途 / 需确认 |
|---|---|---|
| `douyin` | 1080×1920 · 30fps | 抖音信息流/商品视频；上限以创作者中心为准 |
| `tiktok` | 1080×1920 · 30fps | TikTok 信息流 |
| `tiktok-shop` | 1080×1920 · 30fps | TikTok Shop 商品/联盟视频；以 Seller Center 为准 |
| `channels` | 1080×1920 · 30fps | 视频号；信息流预览可能裁切，主体和标题放中部 |
| `xiaohongshu` | 1080×1440（3:4） | 小红书信息流最占屏 |
| `taobao-main` | 1080×1080（1:1） | 淘宝/天猫主图视频（3:4 用 `taobao-3x4`）；以千牛后台为准 |
| `amazon` | 1920×1080（16:9） | Amazon 商品视频；以 Seller Central 为准 |
| `square` | 1080×1080 | Shopee / Lazada / 通用信息流 |

编码统一：H.264 High、yuv420p、CRF 20 + 码率上限、AAC 160k 48 kHz、`+faststart`（边下边播）。

## 步骤 Steps

```bash
python scripts/export_platform.py out/master.mp4 --platform douyin tiktok-shop channels xiaohongshu taobao-main amazon
python scripts/export_platform.py out/master.mp4 --platform all --outdir out/export
python scripts/export_platform.py out/master.mp4 --platform xiaohongshu --mode crop --focus-y 0.4   # 裁切而非模糊填充
python scripts/export_platform.py out/master.mp4 --safe-preview out/safe.png                    # 安全区叠加图
```

1. 母版先按 9:16 做好（字幕已在安全区内）。
2. 选择转换方式：`blur`（默认，保留完整画面，上下/左右模糊填充）或 `crop`（填满画面，会裁掉边缘 → 检查字幕和商品）。
3. 读 `export_report.json`：分辨率、时长、大小、注意事项。
4. 9:16 → 16:9 时字幕会变小，重要平台建议用 `assemble.py --size 1920x1080` **重新渲染**而不是转码。

## 安全区 Safe zones

`--safe-preview` 在一帧上叠加三块经验区域（顶部状态栏 ~9%、右侧按钮栏 ~15% 宽、底部文案/商品卡 ~22%）。这些是经验值，**最终以真机预览为准**。

## 提示词模板 Prompt template

```text
我有一条 {时长} 秒、{分辨率} 的带货母版视频，要发到 {平台列表}。
请给出：每个平台用哪个 --platform 预设、用 blur 还是 crop、需要去官方后台确认的事项（不要编造具体上限数字）。
```

## 检查清单 Checklist

- [ ] 每个导出文件都能本地播放，音画同步
- [ ] crop 模式下字幕/商品没被裁
- [ ] 视频号/小红书封面另做 3:4（见 `cover-title-ab`）
- [ ] 已在官方后台确认时长与大小限制

## 常见问题与修复 Failure fixes

| 问题 | 修复 |
|---|---|
| 上传后糊 | 平台二压；保证源 1080p、码率不要过低，避免大面积细噪点/渐变 |
| 上传失败：文件太大 | 降低 `maxrate`（如 `8M`）或缩短时长 |
| 横版字幕太小 | 用 `assemble.py --size 1920x1080` 重新渲染 |
| 黑边 | 用默认 `blur` 模式或 `crop` |
