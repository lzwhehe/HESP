# arXiv 2609.33446 v2 上传说明

## 文件
- `hesp_v2_arxiv_source.tar.gz`：上传用的源码包（扁平结构，含 `main.bbl`，pdfLaTeX 可编译）。
- `hesp_v2.pdf`：本地编译结果，供核对（16 页）。
- `paper/arxiv_abstract.txt`：粘贴到 arXiv 表单 Abstract 栏的纯文本摘要（1,786 字符）。
- `make_arxiv_package.py`：重新生成以上文件的脚本。

## 操作步骤（在 arXiv 网站上由作者本人完成）
1. 登录 arXiv → Your articles → 找到 2609.33446 → **Replace**。
2. 上传 `hesp_v2_arxiv_source.tar.gz`，确认 arXiv 编译出的 PDF 与 `hesp_v2.pdf` 一致。
3. Abstract 栏粘贴 `paper/arxiv_abstract.txt` 的内容。
4. Comments 栏填写：

```
v2: corrects a false statement about access to the ExCyTIn-Bench test split (erratum E-8), and states in the abstract, introduction and conclusion that an LLM-free controller already reaches 0.917 and that the gains come from moving the procedure out of the model; the limitations now name the environment properties behind this. No experiment or number changed. 16 pages, 5 figures. Code and data: https://github.com/lzwhehe/HESP
```

5. 标题与作者不变。提交后检查新版本页面。

## v2 相对 v1 的全部改动（不删任何实验、不改任何数字）
| 位置 | 改动 |
| --- | --- |
| 摘要 | 主张改为"小模型不应掌控调查流程"；明确写出无 LLM 控制器达到 0.917、环境中每个原因都有独特的离散观测、模型的可测贡献仅限于等待确认证据；说明在原始日志等模糊观测下尚未检验 |
| 引言第 5 段 | 补充：收益来自把流程从模型中拿走，并说明环境的三个性质 |
| 贡献第 4 条 | 由"控制器不需要预言表"改为：无 LLM 控制器与五个模型中四个持平；计数表与生成器表一致是因为二者同源，只说明表不必手写，不说明能迁移到真实数据 |
| 讨论·局限 | 新增三点：几乎每个原因都有概率为 1 的独特观测；日志解析由固定规则完成；计数表、验证器签名与生成器同源；并列入 v1 的测试集表述错误 |
| 结果 §5 公开数据 | 更正"未读取任何测试集"：ExCyTIn 的 599 道测试题曾被可行性脚本读取；GUIDE 测试集确未读取 |
| 伦理 | 同上更正 |
| 附录·勘误 | 新增 E-8 |
| 结论 | 重写：结论落在"控制权"而非"能力"；说明模型在模糊原始日志上的价值未被检验 |
