---
name: multi-model-shot-prompts
description: "多模型镜头提示词适配：把一份分镜表改写成适合不同视频生成模型的提示词（中/英、首帧/首尾帧/纯文生视频、运镜词表、负面约束），模型中立、不编造价格或参数。Use when the user wants the same shot list adapted for Seedance, 可灵 Kling, Veo, Runway, Hailuo/海螺, Wan/通义万相, Sora, Pika or 'any video model', asks 怎么写视频提示词, camera movement terms, or a model returns deformed products."
---

# 多模型镜头提示词适配 · Model-Agnostic Shot Prompts

同一个镜头，不同模型「听得懂」的写法不一样。这个 skill 提供一套**通用骨架 + 适配规则**，不依赖任何一家模型的私有参数。

> Part of [ecommerce-video-skills](https://github.com/xianyu110/ecommerce-video-skills)
>
> ⚠️ 本 skill **不提供任何模型的价格、时长上限、分辨率、帧率等参数** —— 这些变化很快，请以各模型官方文档 / 控制台为准。需要时让用户确认或去官方页面查。

## 输入 Inputs

- 分镜表（可来自 `selling-point-storyboard`）
- 目标模型（可多选；不确定就用「通用」）
- 每镜的输入方式：文生视频 / 首帧图生视频 / 首尾帧
- PRODUCT LOCK（商品一致性描述，见 `image-to-video-shots`）

## 通用骨架 Universal skeleton

```text
{主体 + PRODUCT LOCK} , {主体动作} , {环境/场景} , {镜头运动} , {景别/角度} , {光线/色调} , {风格} , {节奏/时长描述}
约束：{保持商品一致} {不生成文字} {不出现其他品牌} {自然手部}
```

写作原则（对大多数模型都成立）：

1. **具体动词**：「冰块落入杯中」好于「展示保温效果」。
2. **一镜一个动作，一个运镜**：同时推+摇+环绕，模型容易崩。
3. **镜头词放在固定位置**，用通用说法（见词表）。
4. **商品描述用名词+颜色+材质**，避免形容词堆砌。
5. 图生视频时，提示词**只写变化**（动作、运镜），不要重新描述整张图，否则模型会「重画」。
6. 中文模型可直接中文；多数海外模型英文更稳。两种都给最省事。

## 运镜词表 Camera vocabulary

| 中文 | English | 适合 |
|---|---|---|
| 缓慢推近 | slow push-in / dolly in | 产品亮相、细节 |
| 缓慢拉远 | slow pull-out / dolly out | 从细节到全景、收尾 |
| 横移 | truck left / right | 场景展示 |
| 环绕 | orbit 30° around the product | 白底 360 展示 |
| 俯拍下降 | crane down / top-down descending | 平铺、开箱 |
| 跟拍 | tracking shot following the hand | 使用过程 |
| 固定机位 | locked-off static camera | 带字画面、对比 |
| 微距 | macro close-up, shallow depth of field | 材质、工艺 |
| 快速推近 | quick punch-in | 钩子、重点 |

## 适配规则 Adaptation rules

| 输入模式 | 写法 |
|---|---|
| 文生视频 | 完整骨架 + 详细 PRODUCT LOCK；更容易偏离真实商品，适合氛围镜头，不适合商品特写 |
| 首帧图生视频 | 骨架里删去场景/外观描述，只保留「动作 + 运镜 + 约束」 |
| 首尾帧 | 只描述「从首帧到尾帧发生了什么」+ 运镜 |
| 支持负面提示词 | 加 `deformed product, changed logo, warped text, extra fingers, flicker, watermark` |
| 不支持负面提示词 | 把约束写成正向句：`the product keeps exactly the same shape, colour and logo` |
| 支持参考图/主体参考 | 上传白底主图作为主体参考，提示词中写「the product from the reference」 |

## 输出格式 Output

每镜一块：

```text
### Shot 3 · 卖点：24h 保冰（首帧图生视频）
中文：冰块从上方落入瓶中，溅起细小水花；镜头缓慢推近；明亮柔和棚拍光；商品形状、颜色、Logo 保持不变，不生成文字。
English: Ice cubes drop into the bottle with a small splash; slow push-in; bright soft studio light. The product keeps exactly the same shape, colour and logo. No text.
Negative (if supported): deformed product, changed logo, warped text, flicker, watermark
Fallback: motion "zoom_in" in storyboard.json
```

## 提示词模板 Prompt template（让大模型批量改写）

```text
把下面的分镜表改写为视频生成提示词。目标模型：{通用 / 你的模型名}；输入模式：{首帧图生视频}。
规则：一镜一个动作一个运镜；图生视频只写变化；每镜输出中文、English、Negative（若支持）、Fallback motion；
不得写任何模型的价格、时长上限、分辨率等参数；PRODUCT LOCK：{…}
分镜表：{粘贴}
```

## 调用方式（可选）

很多视频模型可通过 OpenAI 兼容或聚合网关调用。本仓库脚本不绑定任何厂商；如需一站式调用视频/图像/大模型，可把网关地址配置为 `BASE_URL`（示例见 README「没有 Claude / API？」）。

## 检查清单 Checklist

- [ ] 每镜：一个动作、一个运镜、带 PRODUCT LOCK 或「只写变化」
- [ ] 中英双版本；约束同时有正向写法
- [ ] 没有写任何未经核实的模型参数/价格
- [ ] 每镜有本地 fallback motion

## 常见问题与修复 Failure fixes

| 问题 | 修复 |
|---|---|
| 模型「重画」了商品 | 图生视频时删掉外观描述，只写动作；加主体参考图 |
| 运镜没生效 | 把运镜词移到句首；只保留一个运镜 |
| 动作太夸张 | 加 `subtle, gentle, slow`；缩短描述 |
| 不同模型风格不统一 | 统一光线与色调描述，后期用同一 BGM/字幕统一 |
