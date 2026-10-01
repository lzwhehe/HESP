"""Build the arXiv v2 upload package for 2609.33446 from arxiv_v2/paper.

Writes arxiv_v2/paper/arxiv_abstract.txt (plain-text abstract for the arXiv form) and
arxiv_v2/hesp_v2_arxiv_source.tar.gz (flat source: main.tex with graphicspath{figures/}, sections, tables,
the figures that are used, refs.bib and the compiled .bbl).

    python arxiv_v2/make_arxiv_package.py
"""
import re
import shutil
import subprocess
import tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER = HERE / "paper"
STAGE = HERE / "upload"
TECTONIC = r"E:\tools\tectonic\tectonic.exe"


def abstract():
    t = (PAPER / "sections/abstract.tex").read_text(encoding="utf-8")
    t = re.sub(r"\\(begin|end)\{abstract\}", "", t).strip()
    t = t.replace("\\hesp{}", "HESP").replace("{,}", ",").replace("$+0.26$", "+0.26").replace("$+0.35$", "+0.35")
    t = t.replace("We release all code, protocols, and episode journals.",
                  "We release all code, protocols, and episode journals at https://github.com/lzwhehe/HESP.")
    assert "\\" not in t and "$" not in t, t
    (PAPER / "arxiv_abstract.txt").write_text(t + "\n", encoding="utf-8")
    return t


def main():
    t = abstract()
    print("abstract characters:", len(t), "(arXiv limit 1920)")
    if STAGE.exists():
        shutil.rmtree(STAGE)
    (STAGE / "figures").mkdir(parents=True)
    for d in ("sections", "tables"):
        shutil.copytree(PAPER / d, STAGE / d)
    used = set()
    for tex in [PAPER / "main.tex", *sorted((PAPER / "sections").glob("*.tex"))]:
        used |= set(re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", tex.read_text(encoding="utf-8")))
    for name in sorted(used):
        src = next(p for p in (PAPER / "figures" / name, HERE / "docs/assets" / name) if p.exists())
        shutil.copy2(src, STAGE / "figures" / name)
    main_tex = (PAPER / "main.tex").read_text(encoding="utf-8").replace(
        "\\graphicspath{{figures/}{../docs/assets/}}", "\\graphicspath{{figures/}}")
    (STAGE / "main.tex").write_text(main_tex, encoding="utf-8")
    shutil.copy2(PAPER / "refs.bib", STAGE / "refs.bib")
    for cls in PAPER.glob("*.cls"):
        shutil.copy2(cls, STAGE / cls.name)
    build = HERE / "build_pkg"
    build.mkdir(exist_ok=True)
    subprocess.run([TECTONIC, "-X", "compile", "main.tex", "--outdir", str(build), "--keep-intermediates"],
                   cwd=STAGE, check=True, capture_output=True)
    shutil.copy2(build / "main.bbl", STAGE / "main.bbl")
    shutil.copy2(build / "main.pdf", HERE / "hesp_v2.pdf")
    out = HERE / "hesp_v2_arxiv_source.tar.gz"
    with tarfile.open(out, "w:gz") as tar:
        for p in sorted(STAGE.rglob("*")):
            if p.is_file():
                tar.add(p, arcname=str(p.relative_to(STAGE)).replace("\\", "/"))
    print("figures:", sorted(used))
    print("package:", out, "pdf:", HERE / "hesp_v2.pdf")


if __name__ == "__main__":
    main()
