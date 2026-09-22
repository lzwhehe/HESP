# 贡献与复现

欢迎改进可追溯性、正确性与研究方法。请先阅读 [研究协议](hesp_research/docs/PROTOCOL.md)，区分软件测试与真实模型效果。

## 本地开发

Python 3.10+，目前仅使用标准库。

```bash
git clone https://github.com/lzwhehe/HESP.git
cd HESP
git switch -c codex/your-change
cd hesp_research
python -m unittest discover -s tests -v
python scripts/run_study.py --output runs/check --repeats 2 --seed 42
```

每次实验使用新的输出目录。`runs/` 为本地临时结果，`results/` 为明确保留的验证记录。不要覆盖历史记录。

## 提交变更

1. 在 Issue 中描述具体问题、研究假设或复现步骤。
2. 对数值、状态、预算、协议和统计行为的变更增加必要测试。
3. 在 PR 中说明行为变化、验证结果及对已有实验的影响。
4. 检查 CI；涉及研究结果的变更须链接配置、日志和源码版本。

## 研究记录

- 不把模拟完成率写成真实任务成功率。
- 不删除失败运行；缺失 Token 或费用保持未知。
- 只记录简短的公开决策理由、可检验预测和证据引用。
- 不提交密钥、真实账户信息或生产数据。
- 真实模型和外部任务的执行须先确定预算与授权范围。

项目尚未声明开源许可证；仓库可见性不等于授予复用或再分发许可。
