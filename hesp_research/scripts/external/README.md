# ExCyTIn-Bench 可行性验证脚本

这两个脚本回答"ExCyTIn-Bench 能不能接到 HESP"，结论写在
[`docs/EXTERNAL_BENCHMARKS.md`](../../docs/EXTERNAL_BENCHMARKS.md)。**它们只读外部数据，不改动本项目任何实验结果。**

## 准备（数据不入库）

```bash
mkdir -p external/excytin/{graphs,questions} && cd external/excytin
# 调查图与题目（microsoft/SecRL，MIT）
gh api repos/microsoft/SecRL/contents/secgym/qagen/graph_files_fixed/incident_5.graphml \
  --jq .content | base64 -d > graphs/incident_5.graphml
gh api repos/microsoft/SecRL/contents/secgym/questions/opus5/test/incident_5_qa_opus5_cleaned.json \
  --jq .content | base64 -d > questions/incident_5_test.json
# 日志（HuggingFace，CDLA-Permissive-2.0，1.64GB）
curl -L -o data_anonymized.tar.gz \
  https://huggingface.co/datasets/anandmudgerikar/excytin-bench/resolve/main/data_anonymized.tar.gz
tar -xzf data_anonymized.tar.gz --exclude="._*" data_anonymized/incidents/incident_5
```

## 运行

```bash
python probe_candidates.py   # 假设集合能否从调查图机械导出
python probe_coverage.py incident_5   # 答案能否被固定探针目录覆盖（需先解包该事件）
```

CSV 分隔符是 `❖`（U+2756），不是逗号。单个事件约 87MB，**不需要 Docker / MySQL**。

数据为 Microsoft 演示租户 "Alpine Ski House" 的**合成**攻击数据，其 Transparency Note 明确
"released for research purposes only"，不得用于商业或真实环境。
