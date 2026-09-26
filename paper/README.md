# 预印本草稿

- `main.tex` + `sections/*.tex`：正文（英文）。`refs.bib`：参考文献，**提交前必须逐条核对**，标 `VERIFY` 的条目尤其要查。
- `tables/*.tex`：由 `python paper/make_tables.py` 从 `hesp_research/results/*_summary.json` 生成，不要手改。
- 图：直接引用 `docs/assets/` 下的 PDF。

编译（本机用免安装的 Tectonic 0.17.0，放在 `E:	ools	ectonic\`；首次编译会自动下载宏包）：

```bash
cd paper && /e/tools/tectonic/tectonic.exe -X compile main.tex --outdir build
```

也可以用 `latexmk -pdf main.tex` 或上传到 Overleaf。`build/` 不入库。`arxiv_abstract.txt` 是提交 arXiv 时用的短摘要（arXiv 限 1920 字符）。
