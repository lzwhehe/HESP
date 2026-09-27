# 四大安全会议论文的形态与画图模式（调研小结，2026-09-27）

调研对象：USENIX Security、NDSS、ACM CCS、IEEE S&P 的 21 篇论文（优先选 LLM 安全、LLM agent、告警与攻击调查、安全领域机器学习方法论），加上作者提供的 5 张 overview 参考图（PromptThief、Causal Analyst、NetMasquerade、WebSpotter，以及一个基于规划 LLM 的 agent 系统）。通过 arXiv HTML 版读取章节结构与图注；会议归属以论文自述或 arXiv 的 comments/journal-ref 为准。

| 论文 | 会议 |
| --- | --- |
| PentestGPT | USENIX Sec '24 |
| Formalizing and Benchmarking Prompt Injection | USENIX Sec '24 |
| StruQ | USENIX Sec '25 |
| LLMmap | USENIX Sec '25 |
| "Do Anything Now"（越狱提示词） | CCS '24 |
| PLeak | CCS '24 |
| JudgeDeceiver（LLM-as-a-Judge 注入） | CCS '24 |
| SecAlign | CCS '25 |
| Progent | CCS（论文自述） |
| SVEN | CCS '23 |
| LLMs Cannot Reliably Identify Vulnerabilities | S&P '24 |
| Kairos | S&P '24 |
| IsolateGPT | NDSS '25 |
| NodLink | NDSS '24 |
| NoDoze（告警疲劳分诊） | NDSS '19 |
| Dos and Don'ts of ML in Computer Security | USENIX Sec '22 |
| MAGIC、OMNISEC、PoisonedRAG、CodeBreaker、LLMs for Code Analysis、ChatGPT for Vulnerability Management | 同领域；会议归属未逐一核实，只用于归纳写法 |

## 一、论文形态

1. **引言固定五段式**：领域和重要性 → 现有方法的具体不足（Kairos 列出四个维度，SVEN 列出三个挑战）→ 一句显式的核心观点，常写成"Our key insight/idea is …"（IsolateGPT、PoisonedRAG、Progent）→ 系统名和一段概述 → 评估的关键数字 → **编号贡献 3–5 条** → 开源链接。
2. **单独的威胁模型一节**（21 篇中至少 10 篇）：攻击者目标、背景知识、能力、信任关系、范围（明确写出哪些在范围内、哪些不在）。常放在第 3 节，紧跟背景之后。
3. **背景之后常有"动机示例 / Motivating Example"小节**（Kairos §II-B、MAGIC §2.1、IsolateGPT §II），用一个具体案例讲清问题。
4. **系统论文的核心结构**：Overview（配总览图）→ Design Details（逐个模块）→ Implementation（语言、代码行数）。
5. **评估用显式的研究问题组织**：PentestGPT RQ1–6、Kairos Q1–5、NodLink RQ1–6、PLeak RQ1–5、OMNISEC RQ1–4。常见的研究问题依次是：效果、与基线比较、消融、参数敏感性、效率或开销、真实案例。
6. **经验研究会用编号的"发现"框**（PentestGPT 的 Finding 1–5），把结论单独框出来。
7. **收尾顺序**：Discussion / Limitations → Related Work（按方法分组）→ Conclusion。USENIX '25 起要求单独的 "Ethics Considerations" 与 "Open Science" 两节（StruQ、LLMmap、Progent 都有），涉及负责任披露时要写明（DAN、PLeak）。

## 二、画图模式

1. **图 1 几乎都是动机示例或问题示意，而不是系统架构**：JudgeDeceiver 对比有无攻击，Progent 用贯穿全文的运行示例，DAN 和 CodeBreaker 用具体例子，StruQ 和 SecAlign 对比方法前后。
2. **图 2 是总览或流水线图，放在 Overview 一节开头**：
   - 用虚线框把流程分成几个阶段，每个阶段用黑底白字的编号标出（❶❷❸ 或 1.1、2.2），标题用粗体或斜体；
   - 框里画**具体的东西**：一行彩色小方块代表特征或分数向量、填了数字的小表格、文件、服务器和脑子图标、圆角灰框表示模型；
   - 关键输出用**红色**，其余是柔和的浅蓝、浅黄、浅橙、浅绿，配细黑箭头。
3. **执行流程并排对比图**：IsolateGPT 图 5–8、PentestGPT 图 7（GPT-4 与 PentestGPT 并排，每一步用 ❶–❻ 编号）。同一个输入，用两种方法处理，一步步画出来。
4. **结果图**：每个模型或方法一组的柱状图，参数敏感性用折线图，另有热力图、ROC 曲线、"效用–安全"散点图。主要结果多用表格。
5. **案例研究**：NodLink 画了 7 个真实攻击案例图，Kairos 画了攻击摘要图。

## 三、本文据此做的修改

| 模式 | 本文的做法 |
| --- | --- |
| 图 1 = 动机示例 | 同一条告警、同一个 Llama-3.1-8B，"谁选探针 × 谁决定停止"四种组合的真实执行轨迹 |
| 图 2 = 总览流水线 | ❶ 假设账本 → ❷ 按信息增益/成本选探针 → ❸ 证据规则与停止，框内是同一回合的真实数据 |
| 引言 | 加一句显式的 "Our key insight is …"；编号贡献，每条对应到章节 |
| 单独的威胁模型一节 | 问题形式化、系统模型、攻击者、信任假设、范围 |
| Overview → Design → Implementation | 拆出单独的 Overview 一节 |
| 评估用 RQ 组织，结论用编号发现框 | RQ1–RQ4，每个 RQ 末尾一个 Finding 框 |
| Ethics / Open Science | 已有，保留 |
