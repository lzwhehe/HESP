# arXiv 2609.33446 v2 上传说明

## 文件（由 `python paper_read/make_arxiv_package.py` 生成）
- `arxiv/hesp_v2_arxiv.zip`：上传用的源码包（40 个文件，0.45 MB；扁平结构，含 `main.bbl`）。脚本已把它解压到新目录并单独编译通过。
- `arxiv/hesp_v2.pdf`：从解压后的 zip 编译出的 PDF（20 页），文字与 `build/main.pdf` 完全一致，供核对。
- `arxiv_abstract.txt`：粘贴到 Abstract 栏的纯文本摘要（1,570 字符，上限 1,920）。

## 操作步骤（在 arXiv 网站上由作者本人完成）
1. 登录 arXiv → Your articles → 找到 2609.33446 → **Replace**。
2. 上传 `arxiv/hesp_v2_arxiv.zip`。处理器选 pdfLaTeX（默认）。确认 arXiv 编译出的 PDF 与 `arxiv/hesp_v2.pdf` 一致（20 页）。
3. **Title** 改为：`HESP: Making Small Local LLMs Usable for Alert Triage -- The Model Reads the Logs, a Controller Decides`
4. **Abstract** 栏粘贴 `arxiv_abstract.txt` 的全部内容。
5. **Comments** 栏填写（355 字符，上限 400）：

```
v2: revised and repositioned: for known alert types, a small local model reads raw logs and a controller decides. Adds raw-log studies, incl. the model deciding alone (0 of 48 cases) and attacks on the model reader; corrects a statement on ExCyTIn-Bench test-split access (erratum E-10). 20 pages, 5 figures. Code and data: https://github.com/lzwhehe/HESP
```

6. 作者不变。提交后检查新版本页面。
