# viral-remake-demo · 虚构爆款拆解 → AURA 复刻

演示 `viral-remake` skill：假设一条抖音爆款带货视频（**虚构**，无真实链接），拆 8 维后换成 AURA 保温杯，输出可渲染 `storyboard.json`。

> 「24h 保冰」「不漏水」等卖点仅作演示，未测数据不能用于真实投放。素材复用 `../aura-bottle/assets/`。

## 虚构源视频（口述结构）

- 平台：抖音 · 约 15s · 品类：保温杯
- 钩子：痛点提问「夏天冰水是不是不到午就温了？」
- 5-beat：Hook 吐槽 → Problem 普通杯失败 → Solution 亮相 → Proof 倒冰+拧盖 → CTA 点链接
- 不可复用：原片「月销 10 万」、具名竞品对比、原配乐与原花字文案

## 选用角度

**A 保守同构** — 保留 5-beat 与证明类型，全部台词/花字重写，卖点改为演示用 AURA 卖点。

渲染：

```bash
# 在仓库根目录；storyboard 里的 assets 指向 ../aura-bottle/assets
python scripts/assemble.py examples/viral-remake-demo/storyboard.json -o out/viral-remake-demo.mp4
```
