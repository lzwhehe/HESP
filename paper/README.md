# 预印本草稿

排版为 USENIX 双栏会议格式（`usenix-2020-09.sty`，来自 systems-paper-writing 技能自带模板的简化版；正式投稿前应换成 USENIX 官网的正式样式文件）。

- `main.tex` + `sections/*.tex`：正文（英文）。`refs.bib`：参考文献，其中 9 条已对照原始来源核对（见文件开头注释），经典文献尚未逐页核对。
- `tables/*.tex`：由 `python paper/make_tables.py` 从 `hesp_research/results/*_summary.json` 生成，不要手改。
- 图：图 1 是 TikZ 源文件 `figures/fig_overview.tex`，由 `python paper/figures/make_fig_overview.py` 从归档日志生成；其余图引用 `docs/assets/` 下的 PDF。`figures/pdf2png.ps1` 用 Windows 自带的 PDF 引擎把任意一页渲染成 PNG，便于检查排版。

编译（本机用免安装的 Tectonic 0.17.0，放在 `E:/tools/tectonic/`；首次编译会自动下载宏包）：

```bash
cd paper && /e/tools/tectonic/tectonic.exe -X compile main.tex --outdir build
```

也可以用 `latexmk -pdf main.tex` 或上传到 Overleaf。`build/` 不入库。`arxiv_abstract.txt` 是提交 arXiv 时用的短摘要（arXiv 限 1920 字符）。
