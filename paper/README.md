# 预印本草稿

- `main.tex` + `sections/*.tex`：正文（英文）。`refs.bib`：参考文献，**提交前必须逐条核对**，标 `VERIFY` 的条目尤其要查。
- `tables/*.tex`：由 `python paper/make_tables.py` 从 `hesp_research/results/*_summary.json` 生成，不要手改。
- 图：直接引用 `docs/assets/` 下的 PDF。

编译（需要 LaTeX 环境）：

```bash
cd paper && latexmk -pdf main.tex
```
