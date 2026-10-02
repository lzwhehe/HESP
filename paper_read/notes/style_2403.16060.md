# 写作剖析：Wang et al., *Port Forwarding Services Are Forwarding Security Risks*（IEEE S&P 2024，arXiv:2403.16060）

说明：为尊重版权，下文不整句转录原文。每个长句只给出位置、**句子骨架**（用 `[ ]` 表示可替换成分）、它在段落里承担的功能、用到的句法手段，以及可以借用的短语。原句请对照 arXiv PDF 阅读。位置记为 `§节 ¶段 S句`。

---

## 0. 全文结构总览

| 位置 | 内容 | 作用 |
| --- | --- | --- |
| 题目 | 一个完整的陈述句，而且是双关（Forwarding … Forwarding） | 题目本身就是结论 |
| 摘要 | 6 句：定性+首创 → 方法 → 4 个带数字的发现 | 没有背景铺垫，第一句就是"我们做了什么" |
| §1 引言 | 张力 → 旧方案及其局限 → 新事物出现 → 未知 → 本文 → 方法 → 4 个发现 → 贡献 | 每个发现一段，每段第一句就是结论 |
| §2 背景 | 带粗体小标题的定义段 | 定义 + 选择研究对象的理由 |
| §3 方法 | 三个模块 + 伦理 + 局限 | 伦理和局限放在**方法**里，而不是结尾 |
| §4–§6 发现 | 每节开头说"本节揭示什么"，结尾有 **Summary.** | 结论先行，细节在后 |
| §7 讨论 | 粗体小标题：披露、改进方向、缓解方案、建议、数据发布 | 每个小标题一个问题 |
| §8 相关工作 | 按主题分组，最近的一组放第一，组尾一句定位 | "Very few works … To the best of our knowledge …" |
| §9 结论 | 4 句：做了什么 → 靠什么做到 → 发现了什么 → 呼吁 | 与摘要呼应 |

**全文最核心的三个习惯：**
1. **结论先行**：段首句就是这段的结论；节首句就是这节要揭示什么；Summary 段放在细节之前。
2. **"困难 → 观察 → 做法 → 结果"微结构**：几乎每个方法段都按这个顺序写。
3. **一个名词短语承载整条信息，靠 which / e.g. / 括号数字挂在后面**：长句不是靠从句套从句，而是一个主干加若干"挂件"。

---

## 1. 题目

- 骨架：`[对象] Are [动词-ing] Security Risks`
- 分析：题目是一个判断句，读者看题目就知道结论。它用同一个动词做双关（服务在"转发端口"，也在"转发风险"），好记。
- 可借用：用一个完整判断句当题目，而不是"系统名：副标题"。

---

## 2. 摘要（6 句）

**S1**
- 骨架：`We conduct the first comprehensive security study on [对象] ([缩写]), which [出现时间] and [做什么] along with [优点] compared to [传统技术] (e.g., [例子]).`
- 功能：一句话同时完成三件事——我们做了什么（首个全面安全研究）、对象是什么（which 从句给定义）、为什么值得研究（它比旧方案更好用，所以在普及）。
- 句法：主句很短；定义、价值、对比全挂在 which 从句上；括号里的 e.g. 给具体例子。
- 可借用：`We conduct the first … study on …, which …`；用 which 从句代替单独的背景句。

**S2**
- 骨架：`Our study is made possible through a set of novel methodologies, which are designed to [动词1], [动词2], [动词3], and [动词4].`
- 功能：交代方法。四个不定式正好对应后文的四个方法模块/四节结果，是全文的目录。
- 句法：被动 "is made possible through" 把功劳归到方法上；平行不定式列表。
- 可借用：`… is made possible through …, which are designed to …, …, and …`

**S3**
- 骨架：`Leveraging these methodologies, we have observed [发现1：规模 + 数字].`
- 功能：方法 → 结果的过渡；第一个发现讲"规模"。
- 句法：分词短语开头承上启下；现在完成时表示"研究已得出"。
- 可借用：`Leveraging …, we have observed …`

**S4**
- 骨架：`Furthermore, [X%] [对象] have been classified into [类别] that serve [关键用途], such as, [具体例子1], [例子2], [例子3], and [例子4].`
- 功能：第二个发现，用百分比 + 四个具体到让人紧张的例子（工控、物联网、代码仓库……）把风险落地。
- 可借用：数字后面立刻跟具体例子，让抽象比例变得可感。

**S5**
- 骨架：`And [Y%] [对象] didn't enforce any [防护].`
- 功能：长句之后的短句收拳，制造冲击。
- 注意：句首 And、缩写 didn't 在正式论文里偏口语，我们模仿"长句后接短句"的节奏即可，不模仿 And 开头。

**S6**
- 骨架：`Also identified are [发现3], and [发现4] in activities such as [a], [b] and [c].`
- 功能：把剩下两个发现塞进一句。
- 句法：分词前置倒装（Also identified are …）让句子在一串 "we have …" 之后换个节奏。
- 可借用：倒装句偶尔用一次即可。

**摘要的整体规律**：没有"背景—空白—方法"的铺垫段，第一句就是研究本身；没有形容词式的自夸，每个发现都带数字；不写缓解方案，只写发现。

---

## 3. 引言

### ¶1：张力 + 旧方案的局限

**S1** 骨架：`The increasing scarcity of [资源] leads to a tension between [目标A] and [代价B].`
- 功能：用"张力"开篇，而不是"X 很重要"。张力天然引出"于是人们想办法"。
- 可借用：`… leads to a tension between … and …`

**S2** 骨架：`To address this tension, various techniques have been explored so as to [目的] [限定：that are either … or …].`
- 功能：承接张力，引出已有方案。"so as to"表目的。

**S3** 骨架：`Two typical examples of such solutions are [A] [引用] and [B] [引用].`
- 功能：点名两个代表方案，后面分别批评。

**S4** 骨架：`[A] aim to [机制] so that [效果].` —— 一句话说清旧方案的原理，给后面的批评做靶子。

**S5** 骨架：`In addition to being [缺点形容词1] and [形容词2], [A] either require [代价1], or rely on [外部依赖] (e.g., [例子]) to [目的].`
- 功能：局限一。先用 "In addition to being …" 顺手带出两个次要缺点，再用 either/or 给出两个主要缺点。一句装四个缺点，但读起来不乱，因为主干只有 "[A] either require … or rely on …"。

**S6** 骨架：`Also, their effectiveness varies a lot across [维度], which is further undermined by [趋势] [引用].`
- 功能：局限二；which 从句加一个"更糟的是"。
- 可借用：`…, which is further undermined by …`

**S7–S8** 骨架：`Furthermore, for [情形], [B] has been adopted to [目的]. However, the latency incurred by [步骤1] and [步骤2] can still undermine [性质].`
- 功能：第二个旧方案，同样"先说作用，再用 However 说局限"。

### ¶2：新事物出现，并逐条回应旧局限

**S1** 骨架：`As an alternative solution to address these limitations, [新事物] emerge in recent years, which avoid [局限1], get rid of [局限2], and provide [优点].`
- 功能：**镜像**：which 从句里的三个动词逐一回应 ¶1 列出的局限。读者自然明白新事物为什么流行。
- 可借用：先列旧局限，再用一个 which 从句逐条"消掉"。

**S2** 骨架：`Representative [X] include [A][引], [B][引], and [C][引].`

**S3** 骨架：`At a high level, to [任务], a [组件] will be installed in [位置] (e.g., [例子]) to proactively [动作] with [另一组件].`
- 功能："At a high level"声明这是简化的机制描述，给不熟悉的读者一张地图。

**S4–S5** 骨架：`Also, each [单元] will be automatically assigned with [标识] … Once setup, [请求] will be forwarded by [A], via [B], to [C], and vice versa.`
- 功能：按数据流顺序讲机制，"by … via … to …"一口气走完整条路径。

### ¶3：未知 + 本文

**S1** 骨架：`However, given the emergence and increasing adoption of [X] [引], little is known about how [X] works from [视角] and to what extent [底层机制] are vulnerable to [攻击].`
- 功能：**空白句**。先承认它在普及（given …），再说"几乎不知道"两件事；两件事都用 wh- 从句写成研究问题。
- 可借用：`However, given …, little is known about how … and to what extent …`

**S2** 骨架：`It is also unclear what kinds of [..], whether [..], and to what extent [..].`
- 功能：再抛三个研究问题。三个 wh-/whether 从句平行。
- 注意：原文此处写成 "unclear regarding what"，是语病，模仿时去掉 regarding。

**S3** 骨架：`Also, considering several [事件] [引], it is [important] to comprehensively profile [..] and its [影响].`
- 注意：原文用 "interesting"，在安全论文里偏弱，建议换成 important / necessary。

**S4** 骨架：`In this paper, we report the first [类型] study on [X], which has answered these research questions with [方法], [发现], [攻击], as well as [缓解].`
- 功能：**主旨句**，收束整段；which 从句列出论文会交付的四类东西，是全文预告。
- 可借用：`In this paper, we …, which has answered these questions with …, …, as well as …`

### ¶4–¶5：研究对象与方法

**¶4 S1** 骨架：`In our study, we target two representative [X], namely, [A] and [B], both of which are among the most adopted [X] along with rich [功能].`
- 功能：界定范围，并在 both of which 从句里给出选择理由。

**¶4 S2** 骨架：`And our study is made possible through a set of novel methodologies.` —— 引出方法段（同摘要 S2）。

**¶5 S1** 骨架：`First of all, a [测试床] has been built up, to [目的1], and [目的2].`

**¶5 S2** 骨架：`In the design of this [测试床], [对象] are [处理] via both [A] and [B].`

**¶5 S3** 骨架：`In addition, to [目标], a [采集器] has been designed wherein [机制1], and [机制2] in an efficient and distributed manner.`
- 句法：目的状语前置 "to [目标]"，再给出做法；wherein 引出内部机制。

**¶5 S4–S5** 骨架：`Given the [规模] captured through this [采集器], it is challenging to [任务]. To conquer this challenge, a [分类器] is further developed, which takes [输入] as the input, and outputs [输出].`
- 功能：**困难 → 做法**的微结构：先用 Given 交代规模，再说难，再说为此做了什么，最后用 "takes … as the input, and outputs …" 说清楚接口。
- 可借用：`Given …, it is challenging to … To conquer this challenge, … is developed, which takes … and outputs …`

### ¶6：过渡到发现

**S1** 骨架：`Leveraging these methodologies, our study has distilled a set of novel findings and observations, which are summarized as below.`

### ¶7–¶10：四个发现，每段一个

**¶7（发现1：规模）**
- S1 骨架：`First of all, [X] have been adopted to [做什么] [规模], distributed globally.` —— 段首句就是结论。
- S2 骨架：`Leveraging the [采集器], we carried out [采集] across [时长] between [日期] and [日期], through which, [N] have been observed, and [M] were found to be [状态].` —— 时间范围 + 两个数字。
- S3 骨架：`Also, among [子集], [N] have [属性] identified (§4.2), which includes [a] and [b], which suggests these [X] are widely distributed across [国家数] and [ISP 数].` —— 两个 which 串联：数字 → 数字 → 含义。括号节号指向证据位置。

**¶8（发现2：暴露的是关键系统）**
- S1 骨架：`Furthermore, [X%] turn out to be [类别] that are used to either [A] or [B], and [这样做] may incur non-negligible security risks.` —— "turn out to be"把结果放在句末重音位置。
- S2 骨架：`Such [X] include [类1] (a%), [类2] (b%), …, and even [类n] (n%).` —— 列表中每项带百分比；"and even"把最惊人的放最后。
- S3 骨架：`What is even more worrying is that, among such [X], [a%] failed to [..], [b%] [..], and only [c%] [..].` —— 递进 + 三个并列数字。
- 可借用：`What is even more worrying is that …`（全文只用一次，效果才强）。

**¶9（发现3：协议攻击）**
- S1 骨架：`Besides, we have identified two types of attacks in [..], which have been demonstrated through attack experiments on our [测试床].`
- S2 骨架：`One attack exists in [平面] which allows attackers on [位置] to perform [攻击] and [后果].`
- S3 骨架：`Another attack targets [平面], which allows an attacker to use [组件] as a stepping stone to [后果].`
- S4 骨架：`We have responsibly disclosed [..] to [..], which in turn has acknowledged [..].`
- 功能：One … / Another … 的对称结构；每个攻击都写"在哪里、谁能打、打了会怎样"。

**¶10（发现4：滥用）**
- S1 骨架：`Also, [X] are being abused to a concerning extent and in various malicious activities, particularly, [a], [b], and [c] (e.g., [例子]).`
- S2 骨架：`As a result, [n%] [..] have been detected as [..] while over [m%] [..].`
- S3 骨架：`Also, such [现象] incurs a non-negligible challenge for existing defense systems, particularly considering that [原因].` —— 发现段以"对防御方意味着什么"收尾。

### 贡献列表（4 条）

- `We conduct the first extensive security study on [..].`
- `A novel methodology has been proposed and implemented to [v1], [v2], and [v3] [..].`
- `A set of novel security findings on [..] have been distilled along with supportive analysis and data points.`
- `Two attack scenarios have been identified and demonstrated for [..].`
- 分析：每条一个动词短语，各对应一节。主动与被动混用；用词偏平实，但"novel"用了三次，模仿时建议只保留一次。

---

## 4. 背景（§2）

**粗体小标题 + 定义段**，每段第一句是定义：
- 骨架：`A [X] is designed as an out-of-the-box service to help [用户] [任务].`
- 骨架：`It circumvents the necessity of [旧做法] by [技术], i.e., [解释] (e.g., [例子]).` —— i.e. 解释术语，e.g. 给实例。
- 骨架：`In the scenario of a [X], a program, namely, the [组件], is deployed to [..], and is instructed to [..].` —— "namely"引入命名术语。
- 骨架：`Figure 1 depicts how [流量] traverses [A], [B], before reaching [C], which tends to be [..].` —— 用一句话带读者走一遍图。

**选择研究对象的段落**（表 1 之后）：
- `Our study has identified [N] [X] in total and the full list can be found in Table 1.`
- `To estimate [..], we manually identified [..], and queried [..] to collect [..].`
- `As shown in Table 1, [A] and [B] have the largest [..], [n]/[m] respectively.`
- `We therefore chose [A] and [B] as the targets of our study. And we believe that many of our results on [A] and [B] are applicable to other services, e.g., [..].`
- 分析：**先给数据，再下选择，最后说外推范围**，三步一气呵成。

**第二个术语段**："[术语]. [术语] datasets store [..] that are collected from [..]. A typical [记录] consists of [a], [b], as well as [c]. In our study, we have utilized two [..], with one provided by [..] and the other sourcing from [..]. Combining both was found to lead to a higher coverage." —— 定义 → 组成 → 本文怎么用 → 为什么这样用。

---

## 5. 方法（§3）

### 节首段：模块链

- S1 骨架：`Upon the background knowledge, we present in this section the research methodology which consists of three modules: [A], [B], and [C].`
- S2 骨架：`As the first step of our study, we try to understand [..], which is made possible by [A], as elaborated in §3.1.`
- S3–S4 骨架：`Given [A 的产出], we are motivated to [下一个问题]. Therefore, [B] is designed and implemented to [..], as detailed in §3.2.`
- S5 骨架：`Given [B 的产出], [C] is built up to [..], which is presented in §3.3.`
- 分析：**每个模块都由上一个模块的产出引出**（Given … → need … → therefore …），读者看到的是一条因果链而不是一堆组件。每句都带节号。

### §3.1 测试床

- S1 骨架：`To uncover [..] and test [..], a [测试床] was built up.` —— 目的在前。
- 骨架：`Along [..], [工具][引] is enabled to capture [..], in an attempt to uncover [..], e.g., how [..].`
- 骨架：`Note that when [做实验], the [流量] was generated by our own [..] and [..] under our control. We believe there are no ethical issues as our experiments have no impact on any third parties.` —— 伦理说明就地写，不拖到最后。
- 骨架：`Empowered by this testbed, we have successfully uncovered [..]. For more details, see §4.1 for [..] and §5.2 for [..].` —— 小节以"它带来了什么、在哪里看"收尾。

### §3.2 采集器：**困难 → 观察 → 策略 → 细节 → 终止 → 数量 → 核验**

- 开头：`To get a deep understanding of [..], it is critical to know [..], especially considering that [..]. We refer to such [..] as [术语].` —— 先说为什么要做，再定义术语。
- `Unlike a typical [..], a [X] is more [..] and can [..]. In addition, [..], and no solutions exist to [..].` —— 两个特殊性 = 两个困难。
- `To address these issues, we design a [采集器] to [..]. Next, we introduce more details about this [采集器].`
- 小标题步骤里的典型句链：
  1. `However, it is non-trivial to [..], since [..].`（困难）
  2. `Our observation is that [..].`（关键观察）
  3. `Therefore, we adopted a [策略] to [..].`（做法）
  4. `Specifically, we use [..] as seed to [..]. Given these [..], we [..].`（细节）
  5. `This process continued until no more [..] could be identified.`（终止条件）
  6. `In total, we identified [N] [..].`（数量）
  7. `We double-checked [..] through [..], and have thus confirmed that [..].`（核验）
- 设计权衡句：`However, [步骤] can be costly in terms of [..]. Thus, we designed a prior step to [..]. Through this check, we can significantly lower the workload of [..] by [96%].` —— 每个额外步骤都给出量化收益。
- 限制式设计的理由：`Note that our [工具] only [..] due to several factors. On one hand, [实用理由]. On the other hand, [伦理理由].`
- 实现段：`Our [工具] is implemented in [语言] using several libraries, in particular [..]. In terms of deployment, [..]. In total, we have captured [N] [..] for [M] [..].`

### §3.3 分类器

- 开头：`Once [..] have been captured, we move on to [..], in an attempt to understand [..].`
- 范围声明：`One thing to note, rather than serving as a generic [..], this [..] is tailored for [..].` —— 把局限写成设计选择。
- 标注：`To create the groundtruth, two members of the research team independently labeled [..]. During [..], the two labelers periodically synced with each other to resolve [..].`
- 迭代扩充：`As the sample volume for some categories is still too small to [..], we moved forward to [..] and used [..] to [..].`
- 边界案例：`Some [..] sit on the borderline between [A] and [B], for which we take a conservative strategy and tend to label such cases as [B].` —— 主动说明保守取向。
- 需求 → 选型：`There are two critical issues to consider when [..]. [问题1]. Therefore, [需求1]. In addition, [问题2]. To meet these requirements, [方案].`
- 结果 + 误差分析：`As a result, our model has achieved [..]. … We then further looked into the false classifications and found that [..], probably because [..]. We leave it as our future work to explore [..].`

### §3.4 伦理

- `We take ethics seriously and have carefully designed our methods to avoid [..].`
- `Specifically, we first attempted to [..], but later found that this is not feasible due to [..]. Instead, we [..] and adopted the best ethical practices established by previous studies [引].`
- `As a result, when [..], our [工具] only [..] rather than [..]. We design [..] in this manner according to the observation that [..].`
- 分析：**先表态，再讲过程，再讲具体约束，每条约束都给理由**。

### §3.5 局限：每条局限后面紧跟缓解或指向

- `Several limitations exist in our methodology.`
- `First of all, our study focuses on [..], and our findings on [..] may not be applicable to [..], e.g., [..].`
- `Besides, our [工具] can only capture [..] if [..]. Therefore, the coverage of [..] is constrained by [..].`
- `Also, as [..] are known to bias towards [..], our [工具] inherits this limitation, i.e., [..].`
- `However, our [工具] is designed in a manner that [..] can be seamlessly replaced or complemented by [..], so as to mitigate this limitation.`
- `Fortunately, by integrating [..], we are still able to [..] (see §6).`
- 分析：局限 → 后果 → 缓解（However/Fortunately）。不是一串"我们没做到"，每条都告诉读者影响多大、怎么补。

---

## 6. 发现（§4–§6）

### 节首句：本节揭示什么 + 为什么要先揭示

- `In this section, we reveal for the first time [A], together with a comprehensive measurement for [B]. The distilled knowledge serves as a basis for reasoning about and evaluating [后续问题].`
- `Previous studies [引] have revealed some separate incidents where [..]. However, no studies have systematically profiled [..]. In this section, we move one step further and provide a comprehensive analysis of the extent to which [..].` —— 节级别的"空白 → 本节"。

### 小节首句：承上 + 本小节焦点

- `Upon the knowledge distilled on [..], we then move on to profile [..] with a focus on their [a], [b], and [c].`
- `As detailed in §3.1, we selected [..], [..], and analyzed [..]. Through these steps, we are able to uncover their [a], [b], and [c], as detailed below.`

### 指标段（粗体小标题：Scale / Evolution / Lifetime / Usage / Origins / Categories）

- 定义指标：`Here, we define two metrics to profile this question. The first is [指标] as [公式], i.e., [解释]. However, [它漏掉了什么]. We therefore define another metric, namely [指标2], as [..].` —— 第二个指标由第一个指标的缺陷引出。
- 读图：`[图] presents how [..]. For both [..], we can see that [现象1], while [现象2], which means that [解释].`
- 如实交代数据异常：`We can also see a sudden increase in [..], due to [原因]. Some data points look abnormally lower than others, which is due to [原因].`
- 结果放句尾：`Therefore, the [数据] enable us to measure the extent of [..], which turns out to be low. Specifically, only [n (x%)] [..], and only [..], while none of [..].`
- 解释数字：`This implies that [..] due to various factors, e.g., when [..].`

### Summary 段（放在细节之前）

- `Summary. As summarized in Table 6, a non-negligible portion of [..] fail to [..], therefore, leading to concerning risks in terms of [..]. Below, we provide category-wise results in terms of [..].`
- `Summary. We can conclude with high confidence that [..]. Also, [..], which renders many existing defensive mechanisms less effective, e.g., [..].`
- 分析：**Summary 先给结论，再展开细节**（倒金字塔），或者在节末用 "We can conclude with high confidence that" 收束。

### 类别段

- `In total, [n] [A] were classified as [类], compared to [m] for [B]. Through manual labeling of a sampled set of [k] cases, we have grouped them into [j] subcategories.`
- `Despite their critical roles, [x%] fail to enable any [..], which allows an unauthorized party to not only [..], but also [..].` —— Despite 让反差更强；not only … but also … 递进后果。
- `We need to stress that the fraction of [..] should be considered as a lower-bound estimate, as [..].` —— 如实说明测量是下界，并给原因。
- `One thing to recap, all [..] results are learned through passively [..], which involve no [..].` —— 再次提醒伦理约束。

### 攻击段（§5.2）

- 开头：`We have also identified [..] in [..], which incur non-negligible security risks to both [..] and [..].`
- 机制：`Further analysis revealed that [..]. And the [机制] can be easily [..] without the need of [..], as it only [..]. This allows any [..] to perform [..].`
- 演示：`We have demonstrated this attack on our [测试床]. In these experiments, we [..], so that [..].`
- 现实性：`One thing to note is that it is not necessary for a real-world attacker to [..], as long as he controls [..].`
- 升级：`What is even worse, when [..], [..] is adopted, which allows [..] without the need of [..].`
- 攻击门槛：`Also regarding the attacking bar, the attacker doesn't have to be [..]. Instead, [..] can serve as the attacking vantage points.`
- 分析：**机制 → 演示 → 现实可行性 → 更坏情况 → 攻击门槛**。每个攻击都回答"真实攻击者能不能做到"。

---

## 7. 讨论（§7）

粗体小标题各管一个问题：Responsible disclosure / 方法的改进方向 / 缓解方案 / 给管理员的建议 / 新变化是否影响结论 / 代码与数据发布。

**缓解方案段的句链**
1. 重述问题：`As revealed above, [..]. Also, it is unclear whether [..], since no mechanisms have been implemented by [..]. This allows the attacker with [..] to [..].`
2. 提出方案：`To address these issues, we propose a mitigation technique through [..], which once deployed, can prevent [..] even if [..].`
3. 实现：`This is achieved by utilizing [..], which tend to be increasingly available in [..] [引].`
4. 流程：`The [过程] is triggered every time when [..]. During [..], [..]. Then, no matter whether [..], [..].`
5. 威胁分析：`Assuming a remote attacker has [..], as long as [..], this mitigation can prevent [..]. However, the [机制] cannot prevent [..], e.g., [..]. Also, this defense assumes [..], which we consider as reasonable.`
6. 代价：`Also, we expect the modifications to both [..] and [..] should be minor, as [..].`
- 分析：**问题 → 方案 → 实现 → 流程 → 能防什么、不能防什么 → 部署代价**。对自己提出的防御也写清边界。

**建议段**：`As observed in our study, [..]. [角色] should be aware of this type of threat and implement [..] accordingly. Specifically, [..] is strongly recommended, and [..].`

**变化段**：`We notice that [变化], which we believe doesn't invalidate any of our key results. Also, our [工具] can be easily adapted to such updates by just [..].`

---

## 8. 相关工作（§8）

- 最近的一组放第一：`Security studies on [X]. Very few works study [..]. As detailed in [引], [..]. However, no details were provided regarding [..]. Furthermore, when studying [..], [作者] et al. [引] discovered [..].`
- 定位句：`To the best of our knowledge, our study is the first work that has systematically [..]. For the first time, we have [v1], [v2], [v3], and [v4].` —— 四个动词回扣四个发现。
- 其他组：`A long line of works have studied [..], especially [a], [b], and [c]. Regarding [a], [作者] et al. [引] evaluated [..] along with [..] discovered, e.g., [..].` —— 每篇工作一句：谁、做了什么、发现了什么。
- 组尾定位：`Moving forward, in this study, we have applied [..] to [..], along with [..].` —— 每组最后一句说明本文和这组的关系。

---

## 9. 结论（§9）

- S1 骨架：`In this study, we have conducted the first of its kind [..] study on [..].`
- S2 骨架：`This is made possible through designing and implementing a novel methodology, to [v1], [v2], as well as [v3].`
- S3 骨架：`As a result, multiple security findings have been distilled.`
- S4 骨架：`Particularly, [发现1]; [发现2], and [发现3].` —— 分号串起三个发现。
- S5 骨架：`To conclude, [总判断], to address which, more research and engineering efforts should be invested.`
- 分析：与摘要逐句呼应（做了什么 → 靠什么 → 发现什么）；最后一句是对领域的呼吁。

---

## 10. 用词表

| 用途 | 表达 |
| --- | --- |
| 方法使能 | made possible through / by；leveraging；empowered by；upon |
| 目的 | so as to；in an attempt to；to [动词]（句首） |
| 困难 | it is challenging / non-trivial to …；to conquer this challenge |
| 推进 | we move on to；we then move on to profile … with a focus on …；we move one step further |
| 结果 | turns out to be；we have observed；has been distilled；as a result |
| 强调 | what is even more worrying is that；what is even worse；despite their critical roles |
| 如实 | should be considered as a lower-bound estimate；one thing to note；we need to stress that |
| 交叉引用 | as detailed in §；as elaborated in §；see §… for … |
| 收束 | Summary.；we can conclude with high confidence that；to conclude |

## 11. 不建议模仿的地方

- 语病："As the result"（应为 As a result）；"unclear regarding what"；"an user"；"can be easily adapt"。
- 主观形容词："interesting findings"、"inspiring findings"、多次"novel"。
- 句首 And / Also / Besides 连用：原文几乎每段都这样起句，读多了很单调；保留"一段一个过渡词"即可。
- "non-negligible" 全文出现十余次；一个强调词用多了就没有强调作用。

---

## 12. 映射到我们的论文

| 他们 | 我们 |
| --- | --- |
| 判断句题目 | 用一个判断句当题目（例如"Local LLM Triage Agents Let Attackers Close Their Own Alerts"），系统名放到正文 |
| 摘要：研究 → 方法 → 4 个带数字的发现 | 摘要：研究 → 靠什么做到（控制器 + 攻击测试床 + 预注册）→ 4 个发现（流程失败、注入、伪造来源、读取通道）→ 控制器不损失准确性 |
| ¶1 张力 | "自动化分诊 vs. 遥测不能出网" 的张力 |
| ¶2 新事物 + 镜像 | 本地 LLM 智能体出现，它们逐条解决人工与规则方案的局限 |
| ¶3 空白：little is known about how … and to what extent … | 几乎不知道攻击者从哪里进来、在多大程度上能让告警被关闭；也不清楚哪些决定该交给模型 |
| ¶5 方法：测试床 / 采集器 / 分类器 + 困难→做法 | HESP 控制器 / 带攻击者的分诊测试床 / 预注册研究流程，各配一个困难→做法 |
| ¶7–¶10 四个发现，每段一个，段首即结论 | 发现1：小模型的流程失败；发现2：注入与守卫；发现3：伪造来源与来源组佐证；发现4：读取通道与读取器信任；再加一句"拿走决定不损失准确性" |
| §3 方法内含伦理与局限 | 把伦理与局限放进方法/评测设置 |
| 结果节首句 + Summary 段 | 每个结果小节先给 Summary，再给细节 |
| 讨论：缓解方案写清能防什么不能防什么 | 部署建议和每条规则的边界 |
| 相关工作：最近的一组放第一，组尾定位 | "LLM 调查智能体"一组放第一，组尾一句"To the best of our knowledge …" |
| 结论 5 句与摘要呼应 | 同 |
