# 真实日志案例：伪装成 Windows 系统任务的远程计划任务

**性质：定性案例说明，不是统计检验。** 这里没有估计任何似然，也不报告成功率。所有观测值均由 [`otrf_case_study.py`](../scripts/external/otrf_case_study.py) 直接从原始日志提取，原始输出见 [`case_study_otrf_raw.md`](case_study_otrf_raw.md)。数据来自 OTRF Security-Datasets 的录制 SDWIN-201219070027（MIT）。该录制的说明文件引用了微软对 Solorigate 攻击的分析；数据集标注为 T1053.005（计划任务），描述为"攻击者用 schtasks 远程创建计划任务"。为什么它不能作为基准，见 [`EXTERNAL_BENCHMARKS.md`](EXTERNAL_BENCHMARKS.md) 末节。

## 告警

主机 `WORKSTATION6` 上出现一条 Security 4698 事件：新建计划任务
`\Microsoft\Windows\SoftwareProtectionPlatform\EventCacheManager`。

只看告警，这个任务名和 Windows 自带的软件保护平台任务放在同一个目录下，命名风格也一致。在同一批 27 份录制中，这个目录下的真实系统任务（`SvcRestartTask`）确实会定期出现。只看名称的分析员，或者前面提到的那条"一眼规则"（`otrf_alert_audit.py`），都会把它判为正常。

## 竞争的解释

| 编号 | 解释 | 预期的证据 |
| --- | --- | --- |
| H1 | Windows 自身维护任务 | 由机器账户（`主机名$`）创建，多数在 SYSTEM 会话中 |
| H2 | 用户态应用的更新任务（如 OneDrive） | 由登录用户在本机会话中创建，位于应用自己的路径下 |
| H3 | 本机上的持久化（恶意程序或本地用户） | 由本机会话创建，动作指向非系统程序 |
| H4 | 从另一台主机远程创建（横向移动），并伪装成系统任务 | 由域用户经网络登录创建，来源为另一台主机 |
| other | 以上都不是 | — |

## 逐步调查（每一步都是对已录日志的只读查询）

1. **查创建者**（4698 的 `SubjectUserName`）：`THESHIRE\pgustavo`，是普通域用户，不是机器账户。
   对照组里，`\Microsoft\Windows\` 下其余 17 个新建或更新事件全部由机器账户（`WORKSTATION5$`、`WORKSTATION6$`、`MORDORDC$`）完成。**这一条证据与 H1 相矛盾。**
2. **查登录会话**（按 4698 的 `SubjectLogonId` 找对应的 4624）：**网络登录（类型 3，Kerberos），来源 172.18.39.5**。任务不是在本机会话里创建的，**这与 H2、H3 相矛盾，支持 H4。**
   对照组中由用户创建的两个正常任务都是 OneDrive 更新任务，位于应用自己的路径下，而且是在用户早已开始的本机会话中创建的。
3. **查任务动作**（4698 的 `TaskContent`）：`cmd.exe /C notepad.exe`，以 `S-1-5-18`（SYSTEM）身份运行，作者是 `THESHIRE\pgustavo`。系统目录下的任务却由普通用户署名、以最高权限启动命令行，**进一步支持 H4。**
4. **查来源主机**：172.18.39.5 对应 `WORKSTATION5`。那台主机的 Sysmon 进程日志里有一条 `schtasks /create /F /tn \Microsoft\Windows\SoftwareProtectionPlatform\EventCacheManager /tr "cmd.exe /C …notepad.exe" /s …`，**直接印证了 H4。**

标注核对：数据集元数据写明这是远程创建计划任务，与 H4 一致。在录制时间内，任务尚未被触发执行（没有 notepad.exe 的进程记录）。

## 这个案例说明什么、不说明什么

- **说明了：** 在真实日志上，"告警文字给出的直觉"和"调查得到的结论"可能恰好相反。区分它们的是几个成本很低的查询（创建者、登录会话），而不是告警本身。HESP 的结构能直接表达这种情况：竞争解释、按信息量选择查询、只在证据充分时结案、结论必须引用真实观测。
- **没有说明：** HESP 在真实数据上比其他方法更准确。在这批数据里，只查"创建者"一步就能分开所有样本，没有体现查询顺序的余地；而这样的伪装样本在 27 份录制中只有 1 个场景（新建和修改各一份录制）。统计意义上的证据仍然只来自受控靶场（v0.5–v0.9）。
- **对论文的用途：** 作为方法部分的动机示例和讨论部分的真实案例，并与三个公开数据集的负面测量放在一起，说明为什么公开数据集难以检验调查型方法。
