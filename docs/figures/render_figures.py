"""Render SVG figures to PDF (vector) and PNG (2x) with a local headless Chrome/Edge.

Usage: python docs/figures/render_figures.py docs/assets/hesp-framework.svg [...]
"""

import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

CANDIDATES = [
    os.environ.get("CHROME_PATH", ""),
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "google-chrome", "chromium", "chromium-browser", "msedge",
]


def browser():
    for c in CANDIDATES:
        if c and (Path(c).exists() or shutil.which(c)):
            return c if Path(c).exists() else shutil.which(c)
    raise SystemExit("No Chrome/Edge found; set CHROME_PATH")


def render(svg_path, scale=2):
    svg_path = Path(svg_path).resolve()
    svg = svg_path.read_text(encoding="utf-8")
    w, h = (int(float(v)) for v in re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg).groups())
    exe = browser()
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "page.html"
        page.write_text(
            "<!doctype html><html><head><meta charset='utf-8'><style>"
            f"@page{{size:{w}px {h}px;margin:0}}html,body{{margin:0;padding:0;background:#fff}}"
            f"svg{{display:block;width:{w}px;height:{h}px}}</style></head><body>{svg}</body></html>",
            encoding="utf-8")
        common = [exe, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
                  f"--user-data-dir={Path(tmp) / 'profile'}"]
        pdf = svg_path.with_suffix(".pdf")
        png = svg_path.with_suffix(".png")
        subprocess.run(common + ["--no-pdf-header-footer", f"--print-to-pdf={pdf}", page.as_uri()],
                       check=True, capture_output=True, timeout=120)
        subprocess.run(common + [f"--window-size={w},{h}", f"--force-device-scale-factor={scale}",
                                 f"--screenshot={png}", page.as_uri()],
                       check=True, capture_output=True, timeout=120)
    print(pdf)
    print(png)


CHECK_JS = """
<script>
const bad = [];
document.querySelectorAll('text[data-fit]').forEach(t => {
  const [a, z] = t.dataset.fit.split(',').map(Number);
  const b = t.getBBox();
  if (b.x < a - 4 || b.x + b.width > z + 4)
    bad.push(t.textContent.trim() + ' | ' + b.x.toFixed(1) + '..' + (b.x + b.width).toFixed(1) + ' not in ' + a + '..' + z);
});
document.body.setAttribute('data-overflow', JSON.stringify(bad));
</script>"""


def check_fit(svg_path):
    """Measure every <text data-fit="x0,x1"> in headless Chrome (the renderer used for the
    PDF/PNG) and return the ones whose rendered box leaves its allowed span."""
    import json
    svg = Path(svg_path).read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "check.html"
        page.write_text(f"<!doctype html><html><head><meta charset='utf-8'></head><body>{svg}{CHECK_JS}</body></html>",
                        encoding="utf-8")
        dom = subprocess.run([browser(), "--headless=new", "--disable-gpu", "--no-sandbox",
                              f"--user-data-dir={Path(tmp) / 'profile'}", "--virtual-time-budget=3000",
                              "--dump-dom", page.as_uri()], capture_output=True, timeout=120).stdout
    match = re.search(rb'data-overflow="([^"]*)"', dom)
    if not match:
        raise SystemExit("render check failed: Chrome returned no measurement")
    return json.loads(match.group(1).decode("utf-8").replace("&quot;", '"').replace("&amp;", "&"))


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        render(arg)
