# 致谢与许可 / Credits & Licenses

本仓库的文字、模板与脚本均为原创编写（MIT）。下列项目给了我们结构或思路上的启发——**只学习了组织方式，没有复制其文本或代码**。

| 项目 | 许可证 | 借鉴了什么 |
|---|---|---|
| [harry0703/MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) | MIT | 「文案 → 配音 → 字幕 → 素材合成」一条龙流水线的思路；本仓库为独立的纯 ffmpeg 实现 |
| [eternityspring/shuohao-skills](https://github.com/eternityspring/shuohao-skills) | Apache-2.0 | AI 视频 skill 的拆分粒度、「复制 SKILL.md 就能用」的零成本试用思路 |
| [eternityspring/reelbench-skills](https://github.com/eternityspring/reelbench-skills) | Apache-2.0 | 分镜/拉片表格化的呈现方式 |
| [kajisho5/ffmpeg-skill](https://github.com/kajisho5/ffmpeg-skill) | MIT | 把 ffmpeg 能力包装成 agent skill 的形式 |
| [cclank/lanshu-create-ai-presenter-video](https://github.com/cclank/lanshu-create-ai-presenter-video) | MIT | AI 口播视频的需求形态 |
| [anthropics/skills](https://github.com/anthropics/skills) | 见其仓库 | `SKILL.md` frontmatter（name + description）约定 |

## 运行时依赖 / Runtime dependencies

| 依赖 | 许可证 | 说明 |
|---|---|---|
| [FFmpeg](https://ffmpeg.org/legal.html) | LGPL-2.1+ / GPL（取决于编译选项，libx264 为 GPL） | 由用户自行安装，本仓库只调用命令行 |
| [edge-tts](https://github.com/rany2/edge-tts) | LGPL-3.0（`srt_composer.py` 为 MIT） | pip 依赖，调用微软在线语音服务；商用请自行评估服务条款 |
| [Pillow](https://github.com/python-pillow/Pillow) | MIT-CMU (HPND) | 图片处理 |
| [NumPy](https://github.com/numpy/numpy) | BSD-3-Clause | 音频混音 |
| Noto Sans CJK | SIL OFL 1.1 | 推荐字体（系统安装） |

## 示例素材 / Sample assets

`examples/aura-bottle/assets/` 中的商品图来自姊妹仓库 [ecommerce-image-skills](https://github.com/xianyu110/ecommerce-image-skills) 的效果展示（AI 生成的虚构商品「AURA」，MIT），`end-card.png` 由 `scripts/make_cards.py` 生成。示例 BGM 由 `scripts/make_bgm.py` 实时合成，无版权问题。
