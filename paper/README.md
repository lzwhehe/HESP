# 预印本草稿

排版为 ACSAC 要求的 IEEEtran compsoc 会议格式（`\documentclass[conference,compsoc]{IEEEtran}`），章节结构逐节模仿 ACSAC 2025 的 Clouseau，对照表见 `VENUE_PATTERNS.md` 第四节。附录 A 的 prompt 原文由 `python paper/make_prompt_appendix.py` 从归档日志生成。

- `main.tex` + `sections/*.tex`：正文（英文）。`refs.bib`：参考文献，其中 9 条已对照原始来源核对（见文件开头注释），经典文献尚未逐页核对。
- `tables/*.tex`：由 `python paper/make_tables.py` 从 `hesp_research/results/*_summary.json` 生成，不要手改。
- 图：图 1（总览）由 `python paper/figures/make_fig_pipeline.py` 生成，图 2（同一告警的四种配置）由 `python paper/figures/make_fig_motivating.py` 生成，两者都直接读取归档日志；其余图引用 `docs/assets/` 下的 PDF。`figures/pdf2png.ps1` 用 Windows 自带的 PDF 引擎把任意一页渲染成 PNG，便于检查排版。

编译（本机用免安装的 Tectonic 0.17.0，放在 `E:/tools/tectonic/`；首次编译会自动下载宏包）：

```bash
cd paper && /e/tools/tectonic/tectonic.exe -X compile main.tex --outdir build
```

也可以用 `latexmk -pdf main.tex` 或上传到 Overleaf。`build/` 不入库。`arxiv_abstract.txt` 是提交 arXiv 时用的短摘要（arXiv 限 1920 字符）。
