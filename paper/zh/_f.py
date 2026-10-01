import re
p="main_zh.tex"; s=open(p,encoding="utf-8").read()
s=s.replace("\usepackage{booktabs,makecell,multirow}","\usepackage{array,booktabs,makecell,multirow}")
s=s.replace("\usepackage{tikz}\n","\usepackage{tikz}\n\usetikzlibrary{positioning}\n")
s=s.replace("\graphicspath{{../figures/}{../../docs/assets/}}","\graphicspath{{../figures/}{../../docs/assets/}}\n\input{../tables/audit_numbers}")
s=re.sub(r"\title\{.*?\}\n\n\author", lambda m: "\title{面向安全运营的 LLM 智能体基准\\真的在衡量调查能力吗？}\n\n\author", s, flags=re.S)
old="\input{sections/background}\n\input{sections/threat}\n\input{sections/approach}\n\input{sections/setup}\n\input{sections/results}\n"
assert old in s
s=s.replace(old,"\input{sections/background}\n\input{sections/method}\n\input{sections/results}\n\input{sections/scores}\n\input{sections/design}\n")
s=re.sub(r"\section\*\{数据可得性\}\n.*?\n\n", lambda m: "\section*{数据可得性}\n审计脚本、冻结的协议、我们审计过的每个 ExCyTIn 题集的逐题捷径标记、SIABench/GUIDE/OTRF 的派生结果，以及生成文中每张表、每幅图和每个数字的脚本见 \repourl{}。基准数据和智能体日志不再分发，脚本从公开来源下载或读取。\n\n", s, flags=re.S)
open(p,"w",encoding="utf-8").write(s)
