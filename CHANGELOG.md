# 更新日志

## 0.8 · 2026-09-25

### 新增
- 盲控制器 arm：`controller.run(show_rankings=False)`，控制器照常选择，但规划器看不到 EIG 排序和选择器名称（修复勘误 E-4）；单元测试确认三种选择器下盲提示逐字相同。
- 第二个模型家族 Llama 3.1（8B bf16、70B AWQ，非门控镜像）；`scripts/run_v08_study.py`、`scripts/server/run_v08_all.sh`、`fetch_v08_models.sh`（先跑已有的 Qwen、同时下载 Llama）、`scripts/v08_summary.py`。
- GUIDE 回放环境 `hesp/guideapp.py` 与控制器"环境自带先验"接口（v0.7，已暂停）。测试增至 138 项。

### 实验
- v0.8：5 个模型 × 5 个 arm × 24 任务 × 3 重复 = **1800 个回合**，预先登记并冻结，源码哈希 `8c355d97`，全部通过审计，日志归档哈希已核对。
- **P2 确认**：在规划器信息完全相同时，EIG/c 排序本身提高完成率（Qwen 7B +0.306，97.5% 区间 [+0.139, +0.472]），在所有能结案的模型上为 +0.26 到 +0.35。
- **P1 未确认**：Llama-3.1-8B 在所有 arm 上从不结案（3389 次决策全是"继续查"），完成率均为 0。小模型主结论限定于 Qwen2.5 家族。
- "交出选择权"随规模反转在干净对照下复现；Llama 70B 复现 HESP 收益 +0.167。见 [RESULTS.md §12](hesp_research/docs/RESULTS.md)。
- v0.7（GUIDE 冷启动）在冻结前干跑中发现原主要终点只反映判定阈值移动（AUROC 差 −0.004），已暂停，GUIDE 测试集未读取。

### 勘误
- E-7：v0.6 的 `memory_only` 账本用了设计者（oracle）表而 HESP 用 `empirical_20`；偏向对照组，v0.6 主要终点只会被低估。v0.8 起统一。

## 0.6 · 2026-09-24

### 新增
- **非 oracle 预测表**：`hesp.predictors.EmpiricalEstimator` 与 `scripts/estimate_empirical_tables.py`，只从不含 LLM 的开发回合计数估计 P(o|h,a)；k 档嵌套抽样；冻结文件以 LF 字节写入并记录 SHA256。
- `build_catalog(oracle=False)` / 环境 `oracle=False`：从结构上保证估计器碰不到生成函数（测试在生成函数被替换为抛异常的条件下通过）。
- 每个回合记录 `claimed_hypothesis`、`claimed_evidence_ids`、`claim_citation_validity`；`hesp.analysis.security_metrics` 与 `true_cause`（漏判攻击、误升级、错因、未决、引用有效性，仅 sec-triage，描述性）。
- `scripts/run_v06_study.py`、`scripts/server/run_v06_all.sh`（带按显卡进程清理，以及"先审计、再归档、后停机"的流程）、`scripts/v06_summary.py`（v0.6 数字的唯一来源）。
- 测试增至 124 项。

### 实验
- v0.6（RQ3）：预先登记并冻结（修订 R-1 至 R-9），三档模型 × 8 arm × 24 任务 × 3 重复 = **1728 个回合**，源码哈希 `dcf1e79e`，全部通过审计，逐回合日志已归档并核对 SHA256。
- **主要终点（7B，`emp20 − memory_only`）：+0.875 [+0.736, +0.972]，成立。** 成功率上的 oracle 差距三个模型都是 0，代价是更高的探针成本；这部分差距全部来自开发数据观测不到的"未知原因"那一行（探索性、不含 LLM 的检验）。数据效率曲线在 k=5 饱和，这是靶场近乎确定性所致。见 [RESULTS.md §10](hesp_research/docs/RESULTS.md)。

### 勘误
- E-6：运行时生成的安全指标把 drift 结论与初始原因比较，结果有误；第一次更正又一律改用 `drift_to`，仍然不对。最终按"结案时实际生效的原因"判定，并加入"通过验证的结论必须等于真因"这条不变式（1728 行全部成立）。运行时的 `report.md` 保留不改，更正后的数字见 `results/v06_summary.md`。

## 0.5 · 2026-09-24

### 新增
- `hesp/secapp.py`:防御向安全告警分诊任务族 sec-triage(8 类隐藏原因 × base/drift/noise;蓝队分析员诊断告警真实性质,全程只读,不发攻击载荷)。接入 CLI(`--env sec`)。
- `scripts/run_v04_study.py` 增加 `--backend {vllm,ollama}`、`--arms`、`--variants` 子集选项;`scripts/server/run_v05_all.sh`;`fig-v05-sec` 图。
- 测试增至 107 项。

### 实验
- v0.5 主研究:三档模型 × 9 arm × 24 任务 × 3 重复 = 1944 个回合,预先登记,源码哈希 `5a5fccd2`。预先登记的主要终点(EIG/cost + 守卫 − Memory-only):7B **+0.8889** [+0.7500, +1.0000]、32B **+0.2500** [+0.0972, +0.4167]、72B +0.1111 [**0.0000**, +0.2361]——**7B 与 32B 的区间不含 0,72B 包含 0**。见 [RESULTS.md §8](hesp_research/docs/RESULTS.md)。
- v0.5 前先做了本地 7B 小验证(`results/v05_sec_local_pilot`)。

### 勘误（2026-09-24，见 [RESULTS.md §9](hesp_research/docs/RESULTS.md)）
- **更正**:本条目原写"三个模型区间都不含 0",经从 `outcomes.jsonl` 复算,72B 的下界恰好为 0。7B / 32B 不受影响。
- v0.5 的逐回合事件日志未随仓库保存(GPU 实例已释放);汇总可复算,原始事件不可第三方复查。
- v0.5 的 manifest 沿用了 v0.4 的 `purpose` / `primary_family` 字段,预登记的主要比较未进入自动分析文件。
- `hesp_random` / `hesp_la` 仍能看到 EIG/cost 排序,且提示词曾错误声称"控制器执行排名第一的探针"。提示词已修正(v0.5 运行之后)。

### 修复
- `hesp/llm.py`:控制器排序段落改为陈述真实的选择策略,不再声称总是执行排名第一的探针。
- `scripts/run_v04_study.py`:新增 `--purpose` / `--primary-family`;`COMPARISONS` 加入 `hesp_eigc_guard − memory_only`。
- 新增 `scripts/v05_summary.py`:v0.5 主要终点表的唯一生成入口,不再手工填写。

## 0.4 · 2026-09-23

### 新增

- `hesp/sandbox.py`：通用的仅回环地址诊断靶场基类。web-diag 迁移到基类上后，360 个脚本回合逐一复现、结果完全一致。
- `hesp/uploadapp.py`：留出任务族 upload-diag，与 web-diag 的结构不同（最优首探针是成本为 2 的 dry-run；只靠排除法不能通过验证）。
- 状态守卫 finish：要求引用当前状态版本下被采用、且支持该假设的证据，并且得分 ≥ 0.8；否则拒绝，并把原因作为工具反馈返回。
- 预算感知 lookahead 选择器（3 层期望最大后验搜索）。
- vLLM / OpenAI 兼容客户端；`run_suite` 支持线程池并发执行。
- `scripts/run_v04_study.py`、`scripts/server/run_v04_all.sh`、`scripts/v04_summary.py`；图 `fig-v04-models`。
- 测试增加到 97 项。

### 实验

- v0.4 主研究：Qwen2.5 7B / 32B-AWQ / 72B-AWQ × 9 个 arm × 48 个任务 × 3 次重复，共 3888 个回合，预先登记，全部通过审计。见 [RESULTS.md](hesp_research/docs/RESULTS.md)。
- 选择规则消融增加 lookahead（v0.3.1，5880 个回合）。

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
