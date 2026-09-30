# 逐句对照：摘要与引言

做法：参考论文（Wang et al., S&P 2024）的第 N 句做什么、用什么句式，我们的第 N 句就做同样的事、用同样的句式，只把内容换成我们的。表中"原句"一栏只写位置、作用和句子骨架（不转录原文），"我们的句子"一栏就是论文里现在的英文原句，"中文"是它的意思。

我们没有照搬的只有一处：原文多次声称"首个"（the first … study），我们不能保证是首个，所以同一位置改为 "a controlled … study"。

---

## 摘要（原文 6 句 → 我们 6 句）

| # | 原句：作用与骨架 | 我们的句子 | 中文 |
| --- | --- | --- | --- |
| A1 | 研究定性 + which 从句给出对象的来历与相对传统技术的优劣：`We conduct the first comprehensive security study on [对象], which emerge in recent years and make [X] available on [Y] along with better [a] but less [b] compared to traditional techniques (e.g., …).` | We conduct a controlled security study on alert triage by small, locally run LLM agents, which emerge in recent years and make alerts resolvable on an organization's own hardware along with less analyst effort but more exposure to attacker-written logs compared to traditional techniques (e.g., manual triage). | 我们对由本地运行的小型 LLM 智能体完成的告警分诊做了一项受控安全研究；这类智能体近年出现，让告警能在组织自己的硬件上得到处理，与传统技术（例如人工分诊）相比，分析员投入更少，但更容易受到攻击者书写的日志影响。 |
| A2 | 方法使能 + 四个不定式：`Our study is made possible through a set of novel methodologies, which are designed to [v1], [v2], [v3], and [v4].` | Our study is made possible through a set of methodologies, which are designed to take each triage decision away from the model, experiment attack scenarios against local triage agents, run triage studies frozen before their first episode, and audit every episode by replaying its journal. | 我们的研究依靠一组方法，分别用于把每个分诊决定从模型手里拿走、针对本地分诊智能体实验攻击场景、运行在第一个回合前冻结的分诊研究，以及通过重放日志审计每个回合。 |
| A3 | 第一个发现（规模）：`Leveraging these methodologies, we have observed [发现 + 数字].` | Leveraging these methodologies, we have observed that small local models fail at the investigation procedure, with Qwen2.5-7B verifying only 8 to 13\% of cases and Llama-3.1-8B never concluding across 3,389 decisions. | 借助这些方法，我们观察到小型本地模型在调查流程上失败：Qwen2.5-7B 只验证了 8% 到 13% 的案例，Llama-3.1-8B 在 3,389 次决策中从未给出结论。 |
| A4 | 第二个发现，百分比 + 一串具体例子：`Furthermore, [x%] [对象] have been classified into [类别] that [..], such as, [例1], [例2], [例3], and [例4].` | Furthermore, every model that decides on its own has been found to follow an instruction planted in a log to close the alert, and one forged source closes every attack as benign once the controller decides, such as, a scanner answer on source reputation, or a poisoned feed read by two probes. | 此外，每个自行决定的模型都会服从埋在日志里的"关闭告警"指令；而一旦由控制器决定，一个伪造来源就能把每个攻击结为良性，例如来源信誉探针上的一条扫描器答案，或两个探针共同读取的被投毒信誉源。 |
| A5 | 短句收拳：`And [y%] [对象] didn't [..].` | And an attacker who writes into every log closes all 36 attacks when the model reads the logs. | 而当由模型读取日志时，往每条日志里写入内容的攻击者能让全部 36 个攻击被结案。 |
| A6 | 倒装收尾，列出剩下的发现：`Also identified are [发现], and the notable [发现] in activities such as [a], [b] and [c].` | Also identified are three rules that close these paths on every model we tested, and the notable finding that taking the decisions from the model costs no accuracy in two of our three settings. | 我们还找到了在所测每个模型上关闭这些路径的三条规则，并发现：在我们三个场景中的两个，把决定从模型手里拿走并不损失准确性。 |

---

## 引言第 1 段：张力 → 已有方案 → 各自的局限（原文 8 句 → 我们 8 句）

| # | 原句：作用与骨架 | 我们的句子 | 中文 |
| --- | --- | --- | --- |
| I1 | 以"张力"开篇：`The increasing scarcity of [资源] leads to a tension between [A] and [B].` | The increasing volume of security alerts leads to a tension between investigating every alert and the limited time of security analysts. | 安全告警数量不断增加，使"逐条调查每条告警"与"安全分析员时间有限"之间形成张力。 |
| I2 | 为缓解张力而探索的技术：`To address this tension, various techniques have been explored so as to [目的] [限定].` | To address this tension, various techniques have been explored so as to triage alerts automatically, deciding for each whether an attack, a misconfiguration, authorized activity, or a false positive caused it. | 为缓解这一张力，人们探索了多种技术来自动分诊告警，对每条告警判断其原因是攻击、配置错误、授权活动还是误报。 |
| I3 | 两个典型方案：`Two typical examples of such solutions are [A] [引] and [B] [引].` | Two typical examples of such solutions are provenance-based alert ranking~\cite{nodoze,kairos} and LLM investigation agents on hosted models~\cite{excytin,clouseau}. | 这类方案的两个典型例子是基于溯源的告警排序，以及运行在托管模型上的 LLM 调查智能体。 |
| I4 | 方案 A 的原理：`[A] aim to [机制] so that [效果].` | Provenance-based systems aim to rank alerts by the causal graph of the surrounding host activity so that analysts read the most suspicious alerts first. | 基于溯源的系统依据周围主机活动的因果图对告警排序，让分析员先看最可疑的告警。 |
| I5 | 方案 A 的局限：`In addition to being [a] and [b], [A] either require [..], or rely on [..] (e.g., …) to [..].` | In addition to being built on whole-system provenance and tuned per environment, these systems either leave the choice of the next query to the analyst, or rely on the analyst (e.g., a tier-1 responder) to reach and justify the verdict. | 这些系统除了依赖全系统溯源、需要按环境调校之外，要么把下一步查询的选择留给分析员，要么依赖分析员（例如一线响应人员）得出并论证结论。 |
| I6 | 方案 A 的另一局限，which 从句"更糟的是"：`Also, their effectiveness varies a lot across [..], which is further undermined by [趋势] [引].` | Also, their output is a ranking rather than a verdict, which is further undermined by the large share of alerts that turn out to be benign~\cite{nodoze}. | 此外，它们的输出是排序而不是结论，而大量告警最终证明是良性的，这进一步削弱了排序的价值。 |
| I7 | 方案 B 的作用：`Furthermore, for [情形], [B] has been adopted to [..].` | Furthermore, for alerts that need an investigation, LLM investigation agents have been adopted to choose queries and read their results in the ReAct pattern~\cite{react}. | 此外，对于需要调查的告警，人们采用 LLM 调查智能体，以 ReAct 模式选择查询并读取结果。 |
| I8 | 方案 B 的局限：`However, [..] can still undermine [..].` | However, the strongest of these agents rely on hosted models, to which many organizations cannot or will not send raw telemetry, and open-weight models still trail them on complex cases~\cite{clouseau}. | 然而，其中最强的智能体依赖托管模型，而许多组织不能或不愿把原始遥测发送给托管模型；开源权重模型在复杂案例上仍落后于它们。 |

## 引言第 2 段：新事物出现，逐条回应局限（原文 5 句 → 我们 5 句）

| # | 原句：作用与骨架 | 我们的句子 | 中文 |
| --- | --- | --- | --- |
| I9 | 新事物 + 三个动词逐条回应局限：`As an alternative solution to address these limitations, [X] emerge in recent years, which avoid [..], get rid of [..], and provide [..].` | As an alternative solution to address these limitations, triage agents built on small open-weight models emerge in recent years, which avoid sending telemetry off the premises, get rid of the need for an analyst to choose each query, and provide a complete verdict for any alert. | 作为解决这些局限的替代方案，基于小型开源权重模型的分诊智能体近年出现：它们不需要把遥测发送到本地之外，不需要分析员选择每一个查询，并能对任何告警给出完整结论。 |
| I10 | 代表者：`Representative [X] include [A], [B], and [C].` | Representative models for such agents include Qwen2.5 and Llama~3.1, from 7B to 72B parameters on a single local GPU. | 这类智能体的代表性模型包括 Qwen2.5 和 Llama 3.1，参数量从 7B 到 72B，可在单块本地 GPU 上运行。 |
| I11 | 高层机制：`At a high level, to [任务], a [组件] will be installed in [位置] (e.g., …) to proactively [动作].` | At a high level, to triage an alert, a local LLM agent will be given the alert and a catalogue of read-only queries (e.g., authentication logs, request patterns, source reputation, change tickets) to repeatedly choose a query and read its result. | 从高层看，为分诊一条告警，本地 LLM 智能体会拿到这条告警和一个只读查询目录（例如认证日志、请求模式、来源信誉、变更工单），反复选择一个查询并读取其结果。 |
| I12 | 机制细节：`Also, each [单元] will be automatically assigned with [..], which [..].` | Also, each verdict will be stated as a cause together with the observations it cites, which an analyst can check. | 此外，每个结论都会以"一个原因及其引用的观测"的形式给出，分析员可以核对。 |
| I13 | 数据流走一遍：`Once setup, [请求] will be forwarded by [A], via [B], to [C], and vice versa.` | Once concluded, a benign verdict will close the case without any response, and any other verdict will escalate it to an analyst. | 一旦给出结论，良性结论会在不采取任何响应的情况下关闭案件，其他结论则把案件升级给分析员。 |

## 引言第 3 段：未知 → 本文（原文 4 句 → 我们 4 句）

| # | 原句：作用与骨架 | 我们的句子 | 中文 |
| --- | --- | --- | --- |
| I14 | 空白句，两个 wh- 问题：`However, given the emergence and increasing adoption of [X] [引], little is known about how [..] and to what extent [..].` | However, given the emergence and increasing adoption of LLM agents in security operations~\cite{excytin,clouseau}, little is known about how reliably small local models carry out the investigation procedure and to what extent their verdicts are vulnerable to an attacker who writes into the logs they read. | 然而，尽管 LLM 智能体在安全运营中出现并日益普及，我们几乎不知道小型本地模型执行调查流程有多可靠，也不知道它们的结论在多大程度上会受到"往它们读取的日志里写东西"的攻击者影响。 |
| I15 | 再抛三个问题：`It is also unclear what [..], whether [..], and to what extent [..].` | It is also unclear which of the model's decisions an attacker can reach, whether a component outside the model can take those decisions over, and to what extent such a component costs accuracy. | 同样不清楚的是：攻击者能触及模型的哪些决定，模型之外的组件能否接管这些决定，以及这样的组件在多大程度上损失准确性。 |
| I16 | 结合已知事件说明必要性：`Also, considering [事件] [引], it is [..] to comprehensively profile [..] and its respective security implications.` | Also, considering the established threat of indirect prompt injection through retrieved content~\cite{greshake2023,agentdojo}, it is important to comprehensively profile how an attacker can steer a triage verdict and its respective security implications. | 此外，考虑到通过检索内容实施的间接提示注入已是公认的威胁，有必要全面刻画攻击者如何左右分诊结论及其安全影响。 |
| I17 | 主旨句，which 从句列出论文交付的四类东西：`In this paper, we report the first [..] study on [X], which has answered these research questions with [a], [b], [c], as well as [d].` | In this paper, we report a controlled security study on local LLM triage agents, which has answered these research questions with a controller that takes each decision from the model, pre-registered studies, three attack paths, as well as rules that close each of them. | 本文报告一项针对本地 LLM 分诊智能体的受控安全研究，用一个能把每个决定从模型手里拿走的控制器、若干预注册研究、三条攻击路径，以及关闭每条路径的规则，回答了这些研究问题。 |

## 引言第 4 段：研究对象（原文 2 句 → 我们 2 句）

| # | 原句：作用与骨架 | 我们的句子 | 中文 |
| --- | --- | --- | --- |
| I18 | 研究对象 + both of which 给理由：`In our study, we target [..], namely, [A] and [B], both of which are among the most adopted [..] along with rich [..].` | In our study, we target five open-weight models, namely, Qwen2.5 at 7B, 32B, and 72B and Llama~3.1 at 8B and 70B, all of which are among the most adopted open-weight models along with instruction tuning for tool use. | 本研究针对五个开源权重模型，即 7B、32B、72B 的 Qwen2.5 和 8B、70B 的 Llama 3.1，它们都是采用最广的开源权重模型之一，并经过面向工具使用的指令微调。 |
| I19 | 引出方法：`And our study is made possible through a set of novel methodologies.` | And our study is made possible through a set of methodologies. | 我们的研究依靠一组方法完成。 |

## 引言第 5 段：方法（原文 6 句 → 我们 6 句）

| # | 原句：作用与骨架 | 我们的句子 | 中文 |
| --- | --- | --- | --- |
| I20 | 组件一及目的：`First of all, a [测试床] has been built up, to [目的1], and [目的2].` | First of all, a controller, \hesp{}, has been built up, to take each triage decision away from the model, and hand any of them back when an allocation of control is studied. | 首先，我们构建了控制器 HESP，用来把每个分诊决定从模型手里拿走，并在研究某种控制权分配时把其中任意一个交还给模型。 |
| I21 | 组件一的设计：`In the design of this [..], [..].` | In the design of this controller, a Bayesian ledger of candidate causes ranks read-only probes by expected information gain per cost, and a verdict is accepted only if a current observation in the ledger supports it. | 在这个控制器的设计中，候选原因的贝叶斯账本按单位成本的期望信息增益对只读探针排序，只有账本中有当前观测支持的结论才会被接受。 |
| I22 | 组件一的配套模块：`And the [..] is equipped with a set of [..] for [..].` | And the controller is equipped with a write-ahead journal and an audit for replaying every episode. | 控制器还配有预写式日志和一个用于重放每个回合的审计模块。 |
| I23 | 组件二：目的在前 + wherein 讲机制：`In addition, to [目标], a [采集器] has been designed wherein [机制1], and [机制2] in an efficient and distributed manner.` | In addition, to measure where the attacker gets in, a triage testbed has been designed wherein every episode runs against its own loopback sandbox, and attackers are instrumented to write instructions into log fields, forge a data source, or target the model while it parses raw logs. | 此外，为测量攻击者从哪里进来，我们设计了一个分诊测试床：每个回合在自己的回环沙箱中运行，攻击者被编排为往日志字段写入指令、伪造一个数据来源，或在模型解析原始日志时针对它。 |
| I24 | 困难：`Given the [规模] captured through this [..], it is challenging to [..].` | Given dozens of configurations run through this testbed on five models, it is challenging to tell a real effect from one found by searching. | 面对在这个测试床上、五个模型上运行的几十种配置，很难区分真实的效应和"找出来的"效应。 |
| I25 | 应对 + 接口：`To conquer this challenge, a [..] is further developed, which takes [..] as the input, and outputs [..].` | To conquer this challenge, a pre-registration protocol is further adopted, which takes each study's hypotheses, primary endpoints, and source hash as the input before the first episode, and outputs confirmatory intervals for those endpoints only. | 为应对这一挑战，我们进一步采用预注册协议：它在第一个回合之前以每项研究的假设、主要终点和源码哈希为输入，只对这些终点输出验证性区间。 |

## 引言第 6 段：过渡（1 句 → 1 句）

| # | 原句 | 我们的句子 | 中文 |
| --- | --- | --- | --- |
| I26 | `Leveraging these methodologies, our study has distilled a set of novel findings and observations, which are summarized as below.` | Leveraging these methodologies, our study has distilled a set of findings and observations, which are summarized as below. | 借助这些方法，我们的研究得出了一组发现和观察，概括如下。 |

## 引言第 7 段：发现一（原文 4 句 → 我们 4 句）

| # | 原句：作用与骨架 | 我们的句子 | 中文 |
| --- | --- | --- | --- |
| I27 | 段首即结论：`First of all, [X] have been adopted to [..] [规模].` | First of all, small local models have been found to fail at the investigation procedure itself, in two different ways. | 首先，小型本地模型在调查流程本身上失败，而且以两种不同方式失败。 |
| I28 | 时间范围 + 两个数字：`Leveraging the [..], we carried out [..] across [时长] between [日期] and [日期], through which, [N] have been observed, and [M] were found to be [..].` | Leveraging the controller, we carried out eight studies across one week between September 24 and September 30, 2026, through which, 23,582 LLM episodes have been audited, and 11,912 were found to come from the five original studies. | 借助控制器，我们在 2026 年 9 月 24 日至 30 日的一周内完成了八项研究，审计了 23,582 个 LLM 回合，其中 11,912 个来自最初的五项研究。 |
| I29 | 总量：`In total, we have captured [N] [..].` | In total, Qwen2.5-7B choosing its own probes has ended only 8 to 13\% of cases with a verified verdict. | 总体上，自行选择探针的 Qwen2.5-7B 只有 8% 到 13% 的案例以已验证的结论结束。 |
| I30 | 两个 which 串联：数字 → 数字 → 含义：`Also, among [..], [N] have [..] (§), which includes [..], which suggests [..].` | Also, under our prompt and serving configuration, Llama-3.1-8B has asked for another probe in all 3,389 of its decisions (§5.1), which includes decisions whose posterior exceeded 0.999, which suggests that choosing what to probe and deciding when to stop are separate failures. | 此外，在我们的提示与服务配置下，Llama-3.1-8B 在全部 3,389 次决策中都要求再运行一个探针，其中包括后验已超过 0.999 的决策，这说明"探测什么"与"何时停止"是两种独立的失败。 |

## 引言第 8 段：发现二（原文 3 句 → 我们 3 句）

| # | 原句：作用与骨架 | 我们的句子 | 中文 |
| --- | --- | --- | --- |
| I31 | 发现 + "may incur non-negligible security risks"：`Furthermore, [x%] turn out to be [..] that are used to either [..] or [..], and [这样做] may incur non-negligible security risks.` | Furthermore, every model that decides and reaches its own verdict turns out to follow an instruction planted in a log field to close the alert, and letting such a model decide may incur non-negligible security risks. | 此外，每个自行决定并给出结论的模型都服从埋在日志字段里的"关闭告警"指令，让这样的模型做决定可能带来不可忽视的安全风险。 |
| I32 | 列表，每项带数字，"and even"放最后：`Such [X] include [a] (x%), [b] (y%), …, and even [z] (w%).` | Such models include Qwen2.5-7B (69 of 72 actionable cases closed), Qwen2.5-32B (57), Qwen2.5-72B (69), and even Llama-3.1-70B (63). | 这类模型包括 Qwen2.5-7B（72 个需处置案例中关闭 69 个）、Qwen2.5-32B（57 个）、Qwen2.5-72B（69 个），甚至 Llama-3.1-70B（63 个）。 |
| I33 | 递进 + 三个并列数字：`What is even more worrying is that, among such [..], [a], [b], and only [c].` | What is even more worrying is that, once the controller decides, a single forged source closes 18 of 18 actionable cases as benign on every model, a poisoned feed read by two probes does the same, and only corroboration from two distinct source groups escalates all of them (§4.2). | 更令人担忧的是，一旦由控制器决定，单个伪造来源就在每个模型上把 18 个需处置案例全部结为良性，两个探针共同读取的被投毒信誉源也是如此，只有来自两个不同来源组的佐证能把它们全部升级。 |

## 引言第 9 段：发现三——两种攻击（原文 4 句 → 我们 4 句）

| # | 原句：作用与骨架 | 我们的句子 | 中文 |
| --- | --- | --- | --- |
| I34 | `Besides, we have identified two types of attacks in [..], which have been demonstrated through attack experiments on our [测试床].` | Besides, we have identified two types of attacks on the model when it parses raw logs, which have been demonstrated through attack experiments on our testbed against the recommended controller. | 另外，我们找到了两类针对"模型解析原始日志"这一环节的攻击，并在测试床上针对推荐配置的控制器通过攻击实验加以演示。 |
| I35 | 攻击一：在哪、谁能打、后果：`One attack exists in [..] which allows attackers on [..] to perform [..] and [..].` | One attack exists in the free-text fields of every log, which allows an attacker who writes a consistent benign story into all of them to reach every source group at once and close all 36 actionable cases on Qwen2.5-7B once the log format has changed. | 第一种攻击存在于每条日志的自由文本字段中：攻击者往所有字段写入一致的良性故事，就能一次触及所有来源组，在日志格式变化后让 Qwen2.5-7B 把全部 36 个需处置案例结案。 |
| I36 | 攻击二：`Another attack targets [..], which allows an attacker to use [..] as a stepping stone to [..].` | Another attack targets the log writer, which allows an attacker to use an unescaped user-agent field as a stepping stone to forge a whole log record, and turns all 36 actionable cases on Llama-3.1-8B into escalations. | 第二种攻击针对日志写入器：攻击者以一个未转义的用户代理字段为跳板伪造一整条日志记录，让 Llama-3.1-8B 的全部 36 个需处置案例都变成升级。 |
| I37 | 处置结果：`We have responsibly disclosed [..] to [..], which in turn has [..].` | We have closed both with a reader-trust rule, which in turn lets no attack close a case on either model, at the cost of escalating honest benign cases whenever the rule parser cannot read (§4.3). | 我们用读取器信任规则关闭了这两种攻击：在两个模型上都没有攻击能关闭案件，代价是规则解析器读不出时诚实的良性案例会被升级。 |

## 引言第 10 段：发现四（原文 3 句 → 我们 3 句）

| # | 原句：作用与骨架 | 我们的句子 | 中文 |
| --- | --- | --- | --- |
| I38 | 发现 + particularly 列举 + e.g.：`Also, [X] are being [..] to a concerning extent and in various [..], particularly, [a], [b], and [c] (e.g., …).` | Also, taking the decisions from the model costs no accuracy in our settings, particularly, in probe selection, in stopping, and against prompts selected to help the baselines (e.g., $+0.667$ and $+1.000$ for the controller on the two small models). | 此外，在我们的场景中，把决定从模型手里拿走并不损失准确性，尤其体现在探针选择、停止判断，以及面对为帮助基线而选出的提示时（例如在两个小模型上控制器分别领先 +0.667 和 +1.000）。 |
| I39 | 数字结果：`As a result, [x%] [..] while over [y%] [..].` | As a result, the controller alone resolves every case in two of our three settings, while a pre-registered comparison finds no gain from letting Qwen2.5-72B decide when to stop (§5). | 结果是，控制器单独就能解决三个场景中两个的每一个案例，而一项预注册比较没有发现让 Qwen2.5-72B 决定何时停止带来任何增益。 |
| I40 | 对防御方的含义：`Also, such [..] incurs a non-negligible challenge for [..], particularly considering that [..].` | Also, such a controller incurs a non-negligible cost in automation where causes share tools, particularly considering that joint evidence would resolve more of those cases but closes 4 of 18 attacks as the legitimate activity they resemble. | 不过，在原因使用相同工具的地方，这样的控制器会带来不可忽视的自动化代价，尤其考虑到联合证据虽能解决更多这类案例，却会把 18 个攻击中的 4 个结为与之相似的合法活动。 |

## 贡献列表（原文 1 句 + 4 条 → 我们 1 句 + 4 条）

| # | 原句 | 我们的句子 | 中文 |
| --- | --- | --- | --- |
| I41 | `Our contributions can be outlined as follows.` | Our contributions can be outlined as follows. | 本文的贡献概括如下。 |
| C1 | `We conduct the first extensive security study on [..].` | We conduct a controlled security study on alert triage by small, locally run LLM agents. | 我们对由本地小型 LLM 智能体完成的告警分诊做了一项受控安全研究。 |
| C2 | `A novel methodology has been proposed and implemented to [..].` | A controller has been proposed and implemented to take each triage decision from the model, together with three rules that close the attack paths we found. | 我们提出并实现了一个能把每个分诊决定从模型手里拿走的控制器，以及关闭所发现攻击路径的三条规则。 |
| C3 | `A set of novel security findings on [..] have been distilled along with supportive analysis and data points.` | A set of security findings on local triage agents have been distilled along with supportive analysis and data points. | 我们得出了一组关于本地分诊智能体的安全发现，并附有支撑分析和数据。 |
| C4 | `Two attack scenarios have been identified and demonstrated for [..].` | Three attack paths have been identified and demonstrated against local triage agents, one for each allocation of control. | 我们识别并演示了针对本地分诊智能体的三条攻击路径，每条对应一种控制权分配。 |
