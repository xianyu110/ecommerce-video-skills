---
name: subtitles-and-text-effects
description: "字幕与花字：为带货短视频生成 ASS/SRT 字幕与花字（大标题弹出、关键词高亮、贴纸标签、行动号召按钮），自动避开平台底部/右侧 UI 安全区，并用 ffmpeg/libass 烧录。Use when the user wants subtitles, captions, 字幕, 花字, 大字报, keyword highlight, burned-in captions, SRT/ASS files, or text overlays that don't get covered by TikTok/抖音 UI."
---

# 字幕与花字 · Subtitles & Text Effects

一份 ASS 同时放四种样式：**Sub**（底部字幕）· **Hook**（弹出式大花字）· **Tag**（左上角贴纸）· **CTA**（行动号召按钮）。脚本：`scripts/make_subs.py`。

> Part of [ecommerce-video-skills](https://github.com/xianyu110/ecommerce-video-skills)

## 输入 Inputs

- 时间轴 JSON（`ffmpeg-auto-assemble` 自动生成 `build/timing.json`），或自己写：

```json
{"size": [1080, 1920], "cues": [
  {"start": 0.10, "end": 2.70, "text": "冰水撑不到中午？", "style": "Hook"},
  {"start": 0.15, "end": 2.60, "text": "冰水不到中午就**变温**了？", "style": "Sub"},
  {"start": 0.00, "end": 17.0, "text": "AURA 保温杯", "style": "Tag"},
  {"start": 14.2, "end": 17.0, "text": "点击下方链接 ›", "style": "CTA"}]}
```

## 标记语法 Markup

| 写法 | 效果 |
|---|---|
| `**关键词**` | 关键词换成高亮色（默认暖黄） |
| `早上装满冰块|到晚上冰块还在` | Sub：拆成两段按字数分配时间依次出现；其他样式：换行 |

## 步骤 Steps

1. 每条字幕 ≤ 14 个汉字（1080 宽 ≈ 一行），超过用 `|` 拆。
2. 每条只高亮 1 个关键词；花字 ≤ 10 字，只在钩子和关键卖点用。
3. 生成：`python scripts/make_subs.py build/timing.json -o build/subs.ass --srt build/subs.srt`
4. 烧录：`ffmpeg -i in.mp4 -vf "ass=build/subs.ass" -c:a copy out.mp4`
5. 平台若支持上传字幕文件（如 YouTube / 部分广告平台），同时交付 `.srt`。

## 安全区 Safe zones（经验值，以真机为准）

- 底部约 20%：标题文案、商品卡、购物车 → 字幕 `MarginV` 默认 26% 高度
- 右侧约 15%：点赞/评论/分享按钮 → 左右边距 70px，重要信息别贴右边
- 顶部约 8%：状态栏/搜索 → Hook 放在 13% 高度处
- 用 `python skills/platform-spec-export/scripts/export_platform.py video.mp4 --safe-preview safe.png`（在仓库根目录运行） 叠加检查

## 样式定制

编辑 `make_subs.py` 里的 `header()`：字号按画面高度比例计算（9:16 / 1:1 / 16:9 都适用），颜色为 ASS `&HAABBGGRR`。字体自动探测（Noto Sans CJK SC / 思源黑体 / 苹方 / 微软雅黑），也可 `--font "思源黑体 CN"`。

## 提示词模板 Prompt template

```text
把这段口播稿拆成短视频字幕：每条 ≤14 字，超过用 | 分段；每条最多 1 个关键词用 **加粗**；
另外为钩子镜头和最强卖点各写 1 条 ≤10 字的花字。输出 JSON cues（start/end 先留空）。口播稿：{…}
```

## 检查清单 Checklist

- [ ] 字幕不压商品主体、不进底部 20% / 右侧按钮区
- [ ] 每屏最多 2 行；关键词高亮 ≤ 1 个
- [ ] 错别字/品牌拼写检查；数字与配音一致
- [ ] 中文字体已安装（否则会出现方框）

## 常见问题与修复 Failure fixes

| 问题 | 修复 |
|---|---|
| 中文显示成方框 | 安装 CJK 字体（`apt install fonts-noto-cjk`）或 `--font` 指定已安装字体 |
| `No such filter: 'ass'` | ffmpeg 未编译 libass，换官方/发行版完整版 ffmpeg |
| 路径含冒号报错（Windows） | 用相对路径或把 `C:` 写成 `C\:`；脚本已自动转义 |
| 字幕和声音不同步 | 用真实配音时长生成 timing（`assemble.py` 已自动处理） |
| 字幕太小 | 调 `header()` 中 `sub = round(h * 0.037)` 的系数 |
