# sec-triage 本地小验证(2026-09-24)

**这不是正式研究,只是"看看效果"的小规模验证。** 规模极小(每格 n=8,单次重复,仅 base 变体,仅 4 个 arm),不能用于任何效果或显著性结论。

- 模型:`qwen2.5:7b-instruct`(Q4_K_M,本地 Ollama + Vulkan),温度 0.2。
- 规模:sec-triage 族 8 个 base 任务 × 4 个 arm × 1 次 = 32 个回合;全部通过审计,源码哈希 `5a5fccd2`。
- 预测抽取:7B 对 sec-triage 的自生成预测表 KL=1.20 比特(设计者表 0.008),argmax 一致率 0.59。

| Arm | 成功率 | 平均工具成本 | 结局 |
| --- | ---: | ---: | --- |
| A · react_style | 0/8 | 7.62 | 6 循环、2 超预算 |
| B · memory_only | 0/8 | 7.38 | 8 循环 |
| C · hesp_eigc_guard | 8/8 | 4.50 | 全部一次成功 |
| C · hesp_random | 5/8 | 8.88 | 部分成功但浪费 |

**观察(仅供参考,需正式实验确认):** 在这个更难的安全分诊任务上,7B 自己查会陷入"探测→再确认同一探测(被拦截)→始终不下结论"的死循环,决策预算耗尽 → 0/8。HESP 由控制器代选探测、模型只判断何时收尾,绕开了这个死循环 → 8/8,成本还只有一半多。这与 v0.3/v0.4 中"弱模型收益最大、且省成本"的结论方向一致。

复现:
```
python scripts/run_v04_study.py --output runs/v05_sec_local --model qwen2.5:7b-instruct \
  --backend ollama --families sec-triage --variants base \
  --arms react_style memory_only hesp_eigc_guard hesp_random --repeats 1 --seed 2026
```
