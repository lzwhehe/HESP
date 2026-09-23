# 更新日志

## 0.3 · 2026-09-23

### 新增

- **本地授权 Web 诊断靶场**（`hesp/webapp.py`）：标准库 HTTP 服务，仅监听 127.0.0.1，每回合新实例；8 种隐藏原因 × base / drift / noise 三种变体共 24 个任务；路径白名单、拒绝重定向、超时、独立验证器（需引用当前状态版本下带原因特征的观察）。
- **通用环境接口**：假设集合与探针目录由环境提供，控制器不再写死 v0.1 模拟目录。
- **可插拔预测模型与选择器**：设计者预测表 / 冻结的 LLM 预测表；`eig_cost`、`eig`、`map_greedy`、`random`，以及 v0.3.1 的预算感知前瞻选择器 `lookahead`。
- **本地 LLM 组件**（`hesp/llm.py`）：Ollama 客户端（仅回环地址、服务端 usage 含缓存 token）、三组共用模板的 LLM Planner（最多修复一次）、逐行 JSON Schema 约束的 `P(o|h,a)` 抽取；`hesp/predictors.py` 提供 KL / Brier / argmax 一致率校准指标。
- **可续跑的配对实验执行器** `run_suite`：任意 arm、按 (任务, 重复) 共享种子、manifest 与源码哈希校验、中断目录保留为 `_aborted_*`；分析增加配对成本差与每任务胜负计数。
- 脚本：`elicit_predictions.py`、`run_llm_pilot.py`、`run_web_ablation.py`、`pilot_breakdown.py`；图：框架总览图、消融曲线、LLM Pilot、预测校准（`docs/figures/`，SVG/PDF/PNG）。
- 测试从 50 项增加到 90+ 项，含假 Ollama 服务器上的 LLM 组件测试，CI 无需模型。

### 修复

- 被拦截的重复提议现在作为工具反馈返回给所有 arm 的 Planner；此前真实模型会因同一提示与种子反复生成同一被拦截动作。
- 瞬时错误（HTTP 503）不再占用去重键，允许在同一状态下重试（预算照常扣除）。
- 源码哈希对换行符归一化（v0.3.1），Windows 与 Linux 检出结果一致。

### 实验

- v0.3 LLM Pilot、脚本选择器消融、预测校准：见 [`hesp_research/docs/PILOT_V03.md`](hesp_research/docs/PILOT_V03.md)。分析口径在结果产生前登记于 `PROTOCOL.md`。

## 0.2 · 2026-09-22

### 实验与验证

- 增加可复现的随机化配对模拟执行器与冻结 manifest。
- 增加按任务聚类的配对分析，保留失败及未知用量。
- 增加预测、观察、证据、预算和结果的日志一致性审计。
- 记录 50 项软件测试与 36 次配对模拟结果。
- 配置 Linux / Windows、Python 3.10 / 3.12 的 GitHub Actions。

### 修复

- 脚本策略不再使用旧状态的匹配信号结束当前诊断。
- 外部 JSON 子进程协议明确使用 UTF-8。

### 文档

- 增加项目视觉、工作流程图、结果入口、研究路线与英文介绍。
- 增加贡献说明、Issue 和 PR 模板。

本版本仍是模拟研究原型，未执行真实模型或 Web CTF 实验。

## 0.1 · 原始导入版本

- 调查状态、候选动作、信息增益与证据账本。
- 三种对照模式、统一预算、去重和独立模拟验证。
- 外部 Planner 子进程协议。
- 原始 40 项测试与模拟套件，记录保留在 `hesp_research/results/`。
