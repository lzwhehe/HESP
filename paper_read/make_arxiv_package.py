"""Build the arXiv v2 upload package from paper_read/ (English manuscript only).

Writes paper_read/arxiv/hesp_v2_arxiv.zip: main.tex, IEEEtran.cls, the sections and tables it inputs, the figures it
includes, refs.bib, and the compiled main.bbl, flat with graphicspath{figures/}. The package is then unpacked into a
fresh directory and compiled there, so a missing file fails the build here rather than on arXiv.

    python paper_read/make_arxiv_package.py
"""
import re
import shutil
import subprocess
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "arxiv"
STAGE = OUT / "source"
TECTONIC = r"E:\归档\tools\tectonic\tectonic.exe"
INPUT = re.compile(r"\\input\{([^}]+)\}")
GRAPHIC = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")


def strip_comments(text):
    """Drop full-line comments (internal notes) but keep the source otherwise unchanged."""
    return "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("%") or l.startswith("%%")) + "\n"


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (STAGE / "figures").mkdir(parents=True)
    todo, seen, graphics = ["main.tex"], set(), set()
    while todo:
        rel = todo.pop()
        name = rel if rel.endswith(".tex") else rel + ".tex"
        if name in seen:
            continue
        seen.add(name)
        text = (HERE / name).read_text(encoding="utf-8")
        todo += INPUT.findall(text)
        graphics |= set(GRAPHIC.findall(text))
        if name == "main.tex":
            text = text.replace(r"\graphicspath{{figures/}{assets/}}", r"\graphicspath{{figures/}}")
        dest = STAGE / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(strip_comments(text) if name.startswith(("sections", "main")) else text, encoding="utf-8")
    for g in sorted(graphics):
        src = next(p for p in (HERE / "figures" / g, HERE / "assets" / g) if p.exists())
        shutil.copy2(src, STAGE / "figures" / g)
    for f in ("IEEEtran.cls", "refs.bib"):
        shutil.copy2(HERE / f, STAGE / f)
    build = OUT / "build"
    build.mkdir()
    subprocess.run([TECTONIC, "-X", "compile", "main.tex", "--outdir", str(build), "--keep-intermediates"],
                   cwd=STAGE, check=True, capture_output=True)
    shutil.copy2(build / "main.bbl", STAGE / "main.bbl")
    zpath = OUT / "hesp_v2_arxiv.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(STAGE.rglob("*")):
            if p.is_file():
                z.write(p, str(p.relative_to(STAGE)).replace("\\", "/"))
    check = OUT / "check"
    with zipfile.ZipFile(zpath) as z:
        z.extractall(check)
    (OUT / "check_build").mkdir()
    subprocess.run([TECTONIC, "-X", "compile", "main.tex", "--outdir", str(OUT / "check_build")], cwd=check,
                   check=True, capture_output=True)
    shutil.copy2(OUT / "check_build" / "main.pdf", OUT / "hesp_v2.pdf")
    with zipfile.ZipFile(zpath) as z:
        names = z.namelist()
    print(f"{len(names)} files, {zpath.stat().st_size / 1e6:.2f} MB: {zpath}")
    print("figures:", sorted(graphics))
    print("pdf compiled from the unpacked zip:", OUT / "hesp_v2.pdf")


if __name__ == "__main__":
    main()
