# Contributing / 贡献指南

感谢愿意改进 ecommerce-video-skills！Thanks for helping out.

## 欢迎的 PR / Welcome
- 新的平台导出规格（`scripts/export_platform.py`），**请附平台官方说明链接**
- 更好的钩子 / 分镜 / 评测模板（`skills/*/SKILL.md`）
- 渲染脚本的 bug 修复（附复现用的 storyboard.json 和 ffmpeg 版本）
- 新语言 / 新市场的配音音色（`multilingual-dubbing`）

## 规则 / Rules
1. 每个 skill 自包含：`skills/<name>/SKILL.md` + 需要的 `scripts/`。
2. 改了根目录 `scripts/` 后运行 `python tools/sync_scripts.py`，把脚本同步进各 skill。
3. 改渲染相关代码后，至少跑一次示例：
   `python scripts/assemble.py examples/aura-bottle/storyboard.json -o out/aura.mp4`
4. 不写未经验证的卖点、模型价格或参数；不复制其他项目的文本或代码（见 `docs/credits.md`）。
5. 一个 PR 只做一件事，标题用 `feat:` / `fix:` / `docs:` 前缀。

## Issue
报 bug 请用 Bug 模板，附：命令、storyboard.json（可删减）、`ffmpeg -version` 首行、报错输出。
