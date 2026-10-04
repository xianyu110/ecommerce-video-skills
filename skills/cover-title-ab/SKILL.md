---
name: cover-title-ab
description: "封面与标题 A/B：为带货短视频生成多套封面（自动挑选清晰帧或用干净素材图 + 不同标题与版式）和多组标题/文案，导出 3:4 / 9:16 封面文件和对比图，并给出 A/B 测试方法与记录表。Use when the user wants a video cover, 封面, 首图, thumbnail, 标题, 文案, title variants, A/B test covers for 抖音 / 视频号 / 小红书 / TikTok, or wants to improve click-through rate."
---

# 封面与标题 A/B · Covers & Titles A/B

一次出 3–4 个封面版本 + 6–10 个标题，按「一次只改一个变量」做测试。脚本：`scripts/cover_ab.py`。

> Part of [ecommerce-video-skills](https://github.com/xianyu110/ecommerce-video-skills) · 需要更精致的封面底图？用姊妹仓库 [ecommerce-image-skills](https://github.com/xianyu110/ecommerce-image-skills) 的 `xiaohongshu-cover` 出 3:4 封面。

## 输入 Inputs

- 成片（或干净素材图：`build/stillXX.png`、商品场景图）
- 钩子/卖点（可来自 `hook-3s-script`）
- 平台：抖音/视频号/TikTok（9:16 封面 + 3:4 预览裁切）· 小红书（3:4）

## 步骤 Steps

1. **写标题**（见模板）：每个 ≤ 14 字，覆盖不同钩子类型。
2. **生成封面**：

   ```bash
   # 推荐：用没有字幕的干净底图
   python scripts/cover_ab.py out/video.mp4 --images build/still00.png build/still03.png build/still04.png \
       --titles "冰水撑不到中午？|早上的冰，晚上还在|通勤包里不漏水" --ratio 3:4 --outdir out/covers
   # 或者从成片自动挑最清晰的帧（成片帧可能带字幕）
   python scripts/cover_ab.py out/video.mp4 --titles "A 标题|B 标题" --ratio 9:16
   ```

   输出 `cover_A.jpg`、`cover_B.jpg` … 和对比图 `ab_sheet.jpg`；四种版式轮换（黄字黑描边 / 白字红描边 / 黄底黑字横幅 / 半透明黑底白字）。
3. **设计测试**：一次只改一个变量（标题 or 底图 or 版式）；同一时段、相近流量发布；或使用平台自带的封面/标题测试功能（若有）。
4. **记录**（下表），以点击率/完播率等平台数据为准，不凭感觉选。

## 标题公式 Title formulas

| 类型 | 示例 |
|---|---|
| 痛点提问 | 冰水撑不到中午？ |
| 结果 | 早上的冰，晚上还在 |
| 场景 | 通勤包里不漏水的杯子 |
| 数字清单 | 选保温杯看这 3 点 |
| 反差 | 看着普通，其实很能扛 |
| 对比 | 普通杯 vs 这只，放 8 小时（需真实测过） |

## 提示词模板 Prompt template

```text
为这条带货视频写 8 个封面标题（≤14 字）和 4 条发布文案（≤60 字，带 2–3 个话题标签）。
商品：{…}；真实卖点：{…}；平台：{…}
每个标题用不同类型（痛点/结果/场景/数字/反差/对比），禁止绝对化用语和无法证明的数据。
输出：表格（编号/类型/标题/推荐底图/推荐版式）+ 推荐首轮 A/B 组合及理由。
```

## A/B 记录表

| 版本 | 标题 | 底图 | 版式 | 发布时间 | 曝光 | 点击率 | 完播率 | 结论 |
|---|---|---|---|---|---|---|---|---|
| A | 冰水撑不到中午？ | still00 | 黄字黑描边 | | | | | |
| B | 早上的冰，晚上还在 | still03 | 白字红描边 | | | | | |

## 检查清单 Checklist

- [ ] 标题 ≤ 14 字，手机缩略图上能看清
- [ ] 封面主体清晰、商品可识别；文字不压商品
- [ ] 3:4 裁切后标题仍完整（视频号/抖音信息流预览）
- [ ] 一次只改一个变量；数据记录完整
- [ ] 无绝对化用语、无虚假数据

## 常见问题与修复 Failure fixes

| 问题 | 修复 |
|---|---|
| 封面上叠了两层字 | 用 `--images` 传干净底图，而不是成片帧 |
| 标题折行难看 | 缩短到 ≤ 10 字，或手动在合适处断句 |
| 自动选帧糊 | 指定 `--frame-time` 或传 `--images` |
| 测试结论不稳定 | 样本太小；拉长测试周期或只比较差距明显的版本 |
