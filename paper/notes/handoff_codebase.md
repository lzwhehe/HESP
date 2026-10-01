# 项目接手文档：本地小模型安全调查实验框架

> 本文件说明代码、环境、接口、数据格式和实验规矩，供接手的人或模型在现有框架上开展新实验。
> **具体任务目标由项目负责人在下面第 0 节填写。**

## 0. 本次任务（由负责人填写）

（在这里用一两段话写清楚：要实现什么、为什么、交付什么、验收标准。）

---

## 1. 项目当前状态

- 研究问题：在固定工具与预算下，外置结构能否提升本地 7B/8B 模型在安全调查任务（ExCyTIn-Bench）上的可靠性；量化其相对强提示基线、已有结构和确定性控制器的增益。
- 立项书：`paper/notes/proposal_small_models.md`
- 预注册协议与全部结果记录：`hesp_research/docs/PROTOCOL_SMALL.md`（K0 → K1 → K2-能力，按时间顺序追加，不删改历史）。
- 已完成：K1 筛选实验（Qwen2.5-7B，ExCyTIn 训练集 80 题，四个条件）。结果和诊断见协议文件"K1 结果"一节，逐题数据在 `hesp_research/results/small/k1/`。
- 进行中：K2-能力（o1 测试集 589 题，三个模型，条件不变）。

## 2. 仓库结构（与本实验相关的部分）

```
hesp_research/
  docs/PROTOCOL_SMALL.md            预注册协议 + 运行记录 + 结果（唯一权威记录）
  scripts/small/
    k0_build_db.py                  从 ExCyTIn 公开 CSV 建每个事件一个 SQLite 库
    k0_run.py                       环境（Env）、工具函数、LLM 客户端、动作解析（被 k1_run 复用）
    k1_run.py                       四个条件 C1–C4 的运行器，冻结评分器 correct()
    k1_sample.py                    K1 抽样（训练集，种子 2042）
    k1_analysis.py                  按事件重抽的配对比较、判读、人工核对抽样
    k2_frontier_answers.py          下载 14 次前沿运行的公开答案并用同一评分器重新计分
    run_k2.sh                       GPU 主机上的批量运行脚本（启动/停止 vLLM、可续跑）
  results/small/                    样本、题目文件、各实验输出（JSONL）与分析结果
  results/audit/excytin_flags.csv   每道题的捷径标记（named / adjacent / 查表是否答对 / 抗已测捷径）
external/excytin/                   ExCyTIn 数据（不入库）：questions/、questions_old/、graphs/、data_anonymized/
paper/notes/                        立项书、本文件等
```

## 3. 计算环境

- GPU 主机：`ubuntu@150.65.181.211`（只用 SSH 密钥登录；H100 vGPU 20 GB）。**端口 31002 属于其他工作，不要碰。**
- 模型目录：`~/models/{Qwen2.5-7B-Instruct, Llama-3.1-8B-Instruct, phi-4}`
- vLLM：`~/hesp-venv/bin/vllm`（0.11.0）。在 20 GB 显存上需要 `--quantization fp8 --gpu-memory-utilization 0.85 --max-num-seqs 16`；phi-4 用 `--max-model-len 16384`，其余 32768。服务地址 `http://127.0.0.1:8000`。
- 工作目录：`~/k0/`（脚本、题目文件、`db/` 下 8 个 SQLite 库，共约 3.7 GB）。
- **注意**：用 `pkill -f "<字符串>"` 远程停进程时，它会匹配到 SSH 命令自身并断开会话；请用 `ps -eo pid,args | grep "[v]llm serve"` 取进程号再 `kill`（见 `run_k2.sh` 的 `stopserve`）。
- **实验结束必须关闭 vLLM**，并确认 `nvidia-smi` 显存回到 0。
- 不使用任何付费 API。

## 4. 数据

- 题目来源：ExCyTIn-Bench（`microsoft/SecRL`）。
  - 开发集：`opus5` 训练集 418 题（`external/excytin/questions/<incident>_train.json`）。
  - 评测集：`o1/v0` 测试集 589 题（`external/excytin/questions_old/o1/v0/test/`），即原论文成绩所用版本。该题集已在我们的基准审计中被读取过，需在论文中披露。**不得在任何测试集上开发或调参。**
- 题目 JSON 字段：`context, question, answer, solution, start_alert, end_alert, start_entities, end_entities, shortest_alert_path`。`end_alert` 是图节点编号；图节点的 `entry` 字段里有对应的 `SystemAlertId`（`external/excytin/graphs/<incident>.graphml`）。
- 题目文件格式（喂给运行器）：JSON 列表，每项 `{"incident", "index", "resistant", "q": <题目字典>}`。例：`results/small/k2_questions.json`。
- 日志库：每个事件一个 SQLite 文件，表名与 ExCyTIn 的 MySQL 库一致（约 40–100 张表），所有列为 `TEXT COLLATE NOCASE`。**原始库只读；任何改动都必须由脚本从原始库复制出新库后再改。**

## 5. 环境接口（`k0_run.py`）

- `Env(path)`：打开只读 SQLite。`Env.tables` 为表名列表。
- `Env.observe(sql) -> (obs: str, ok: bool)`：执行一条 SQL，返回与官方环境一致格式的结果字符串（行元组列表的 `str()`；超过 100,000 字符时只显示前 15 行），再截断到 6,000 字符。兼容层支持 `SHOW TABLES`、`DESCRIBE t`、`SHOW COLUMNS FROM t`、MySQL JSON 箭头运算符，以及 `CONCAT/JSON_UNQUOTE/LOCATE/SUBSTRING_INDEX/LCASE/UCASE/REGEXP`。单条查询 30 秒超时。
- 工具函数（C2/C3 可用）：
  - `find_alerts(env, keywords) -> str`：在 `SecurityAlert` 的告警名与描述中按关键词匹配，返回至多 10 行 `id=<SystemAlertId> | <AlertName> | <TimeGenerated>`。
  - `alert_entities(env, system_alert_id) -> str`：首行 `Alert: <名称> | <时间>`，其后每行 `<type>: field=value, field=value, ...`。
  - `related_alerts(env, value) -> str`：`Entities` 中包含该值的告警，格式同 `find_alerts`。
- `LLM(url, model)(messages) -> str`：OpenAI 兼容接口，温度 0，`max_tokens` 768。
- `parse(action) -> (kind, arg)`：识别 `submit[...]`、`find_alerts[...]`、`alert_entities[...]`、`related_alerts[...]`、`execute[...]`；都不匹配时 `kind="raw"`，按官方行为把整段当作 SQL 执行。

## 6. 运行器接口（`k1_run.py`）

- 命令：`python3 k1_run.py --cond C1|C2|C3|C4 --questions <题目文件> --db ~/k0/db --out <输出.jsonl> --model <served-name> --workers 12`。可续跑：已写入输出文件的题目会被跳过。
- 条件实现在 `run_llm(llm, env, q, cond)`（C1–C3）和 `run_controller(env, q)`（C4）中。每题最多 25 步；提示词常量在文件开头（`C1_PROMPT`、`k0_run.S_PROMPT`、`C3_PROMPT`）。
- **新增一个条件的做法**：新建脚本（例如 `k3_run.py`），`import k0_run as k, k1_run as k1` 复用环境、工具、`LLM`、`parse` 和评分器；在自己的 `run_*` 函数里实现新条件；`main()` 照抄 `k1_run.main()` 的结构（线程池、续跑、逐行写 JSONL）。**不要修改 `k0_run.py`、`k1_run.py` 里已用于正式实验的行为**；确需修环境错误时，在协议中记录并说明影响哪些已完成的运行。
- 输出 JSONL 每行字段：`submitted`（bool）、`answer`、`steps`、`overflow`（上下文溢出）、`rejected_once`、`traj`（每步 `action`、`kind`、截断的 `obs`）、`correct`、`cond`、`incident`、`index`、`resistant`、`gold`、`seconds`。新条件请保留这些字段，可以增加字段。

## 7. 评分

- 冻结评分器 `k1_run.correct(gold, pred)`：规范化（小写、合并空白、去引号）后相等即对；若预测包含标准答案，则要求预测中同类型候选值（IP、邮箱/UPN、SID、哈希、URL、GUID）只有一个，且长度不超过 max(3×标准答案长度, 标准答案长度+40)。**不得修改。** 新指标另写函数。
- K1 人工核对：40 个判定中 38 个一致；评分器对长句型标准答案偏严（会漏判少量语义正确的答案），没有发现误判为正确。

## 8. 统计与分析

- ExCyTIn 只有 8 个事件，同一事件的题目相关。所有区间按**事件**重抽（2,000 次，种子 2040），见 `k1_analysis.diff_ci`。
- 条件间比较一律配对（同一批题），报告差值、95% 区间、两侧独对计数。
- 分析脚本读 JSONL、写 `analysis.json`，并打印判读结果；表格和图的数字只能由脚本生成。

## 9. 实验规矩（必须遵守）

1. **先登记再运行**：在 `PROTOCOL_SMALL.md` 末尾追加新的一节，写清数据、样本、条件、指标、主要假设和判读阈值，与抽样脚本、样本文件一起提交（git commit），然后才能发出第一个模型请求。
2. **冒烟测试**只用样本以外的开发题（训练集），只查程序错误，不看成绩；发现的问题和修复写进协议的"运行前记录"。
3. 每个条件只正式运行一次。失败、溢出、未作答都计入分母。程序错误导致整组失效可修复后重跑一次，并在协议中记录。
4. 结果写进协议的"结果"一节；与预设阈值不符就如实写"不成立"，并按事先写好的规则收窄结论。
5. 开发只用训练集；测试集上只跑冻结后的系统。
6. 不提交任何凭据；外部数据（ExCyTIn 原始数据、日志）不入库。
7. 结束后关闭 GPU 主机上的服务。

## 10. 交付要求

- 代码放在 `hesp_research/scripts/small/`，新脚本开头写清用途和命令行用法。
- 若需要改动过的数据库：提供一个脚本，从 `~/k0/db/` 的原始库复制出新目录后再改；同时输出一份清单（JSON），逐条列出改动的事件、表、行（如 `SystemAlertId`）、字段、原值和新值，供分析脚本使用。
- 协议草稿：按第 9 节格式写好新一节，交给负责人审阅后再提交和运行。
- 冒烟测试记录：在 6 道样本外训练题上跑通所有新条件的输出文件。
- 一段说明：如何运行、预计耗时、已知局限。
