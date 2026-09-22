# HESP research

研究代码、协议与可追溯实验记录位于 [hesp_research](hesp_research/README.md)。

当前包含模拟诊断控制器、三组对照、随机化配对实验执行器和任务聚类统计。
原始 v0.1 记录保留在 `hesp_research/results/`；这些是软件验证，不是真实模型效果证据。

```sh
cd hesp_research
python -m unittest discover -s tests -v
python scripts/run_study.py --output runs/study --repeats 3 --seed 42
```

研究进度与尚需外部条件见 [后续工作](hesp_research/docs/CONTINUATION.md)。
