"""Figures for the preprint (paper/), sized for a 6.5 in text width (1426 px, 1 pt = 3.048 px).

  fig-architecture   controller architecture (topology from hesp/controller.py)
  fig-decomposition  decomposition study: taking the choice away vs the EIG/cost ranking
  fig-probe-stop     stopping study: who selects probes x who may stop, plus the LLM-free run

Every value comes from hesp_research/results/{v08_summary,v09_summary,v09_llm_free_reference}.json,
which the summary scripts generate from the raw outcome files. Standard-library SVG, Times New
Roman. Render with render_figures.py; ``--check`` measures every label in headless Chrome.

    python docs/figures/make_paper_figures.py --check
    python docs/figures/render_figures.py docs/assets/fig-architecture.svg docs/assets/fig-decomposition.svg docs/assets/fig-probe-stop.svg
"""
import argparse
import json
from pathlib import Path
import sys
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "hesp_research" / "results"
ASSETS = ROOT / "docs" / "assets"
FONT = "'Times New Roman', Times, serif"
W = 1426

INK, INK2, MUTED, GRID, AXIS = "#111827", "#374151", "#6B7280", "#E5E7EB", "#9CA3AF"
HESP, HESP_LIGHT, HESP_TINT = "#1D4ED8", "#93C5FD", "#EFF6FF"
LLM, LLM_TINT = "#4B5563", "#F3F4F6"
AMBER, AMBER_TINT = "#B45309", "#FFFBEB"
TITLE, LABEL, TICK, NOTE = 29, 25, 23, 22
MODELS = [("qwen7b", "Qwen 7B"), ("qwen32b", "Qwen 32B"), ("qwen72b", "Qwen 72B"),
          ("llama8b", "Llama 8B"), ("llama70b", "Llama 70B")]


class Canvas:
    def __init__(self, w, h):
        self.w, self.h, self.parts = w, h, []

    def add(self, s):
        self.parts.append(s)

    def text(self, x, y, s, fit, size=LABEL, weight=400, anchor="start", color=INK, style="normal", rotate=None):
        rot = f' transform="rotate({rotate} {x} {y})"' if rotate else ""
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" '
                 f'font-style="{style}" fill="{color}" text-anchor="{anchor}" '
                 f'data-fit="{fit[0]:.1f},{fit[1]:.1f}"{rot}>{escape(s)}</text>')

    def line(self, x1, y1, x2, y2, color=AXIS, sw=1.5, dash=None, cap="butt", arrow=None):
        dd = f' stroke-dasharray="{dash}"' if dash else ""
        mk = f' marker-end="url(#{arrow})"' if arrow else ""
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" '
                 f'stroke-width="{sw}" stroke-linecap="{cap}"{dd}{mk}/>')

    def path(self, d, color=AXIS, sw=1.5, dash=None, arrow=None, fill="none"):
        dd = f' stroke-dasharray="{dash}"' if dash else ""
        mk = f' marker-end="url(#{arrow})"' if arrow else ""
        self.add(f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{sw}"{dd}{mk}/>')

    def rect(self, x, y, w, h, fill, stroke="none", sw=0, rx=0, dash=None):
        dd = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w, 0):.1f}" height="{max(h, 0):.1f}" rx="{rx}" '
                 f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{dd}/>')

    def marker(self, kind, x, y, r, fill, stroke=None, sw=2.5):
        st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        if kind == "circle":
            self.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}"{st}/>')
        elif kind == "square":
            self.add(f'<rect x="{x - r * 0.9:.1f}" y="{y - r * 0.9:.1f}" width="{r * 1.8:.1f}" '
                     f'height="{r * 1.8:.1f}" fill="{fill}"{st}/>')
        else:
            self.add(f'<path d="M{x:.1f},{y - r * 1.15:.1f} L{x + r * 1.05:.1f},{y + r * 0.8:.1f} '
                     f'L{x - r * 1.05:.1f},{y + r * 0.8:.1f} Z" fill="{fill}"{st}/>')

    def svg(self, defs=""):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" '
                f'height="{self.h}"><defs>{defs}</defs><rect width="{self.w}" height="{self.h}" fill="#FFFFFF"/>'
                + "\n".join(self.parts) + "</svg>\n")


def arrow_defs(*colors):
    return "".join(f'<marker id="a{c[1:]}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
                   f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>' for c in colors)


def load(name):
    return json.loads((RESULTS / name).read_text(encoding="utf-8"))


# ------------------------------------------------------------------ decomposition study
def fig_decomposition():
    s = load("v08_summary.json")
    c = Canvas(W, 470)
    panels = [("hesp_random_blind - memory_only", "Taking the choice away", "random controller selection − model's own choices"),
              ("hesp_eigc_blind - hesp_random_blind", "Ranking", "EIG/cost − random selection, identical planner prompt")]
    lo, hi = -0.5, 0.75
    top, row = 118, 58
    label_w = 170
    gap = 90
    pw = (W - 24 - 40 - label_w - gap) / 2
    for i, (term, title, sub) in enumerate(panels):
        x0 = 24 + label_w + i * (pw + gap)
        x1 = x0 + pw
        X = lambda v, x0=x0: x0 + (v - lo) / (hi - lo) * pw
        c.text(x0, 34, title, (x0, x1), TITLE, 700)
        c.text(x0, 66, sub, (x0, x1), NOTE, color=MUTED)
        y_end = top + row * (len(MODELS) - 1) + 30
        for t in (-0.5, -0.25, 0, 0.25, 0.5, 0.75):
            c.line(X(t), top - 28, X(t), y_end, AXIS if t == 0 else GRID, 1.8 if t == 0 else 1.2)
            c.text(X(t), y_end + 30, f"{t:+.2f}".replace("+0.00", "0").replace("-", "−"), (X(t) - 40, X(t) + 40), TICK,
                   anchor="middle", color=MUTED)
        for j, (key, lab) in enumerate(MODELS):
            y = top + j * row
            if i == 0:
                c.text(24 + label_w - 16, y + 8, lab, (24, 24 + label_w - 12), LABEL, anchor="end")
            d = s[key]["terms"][term]
            v, (a, b) = d["difference"], d["ci"]
            primary = key == "qwen7b" and i == 1
            if key == "llama8b":
                c.text(X(0) + 16, y + 8, "never concludes: 0 in every arm", (X(0), x1), NOTE, style="italic",
                       color=MUTED)
                c.marker("circle", X(0), y, 7, "#FFFFFF", MUTED, 2.5)
                continue
            color = HESP if b < 0 or a > 0 else MUTED
            color = AMBER if b < 0 else color
            c.line(X(a), y, X(b), y, color, 5, cap="round")
            c.marker("circle", X(v), y, 13 if primary else 9, "#FFFFFF" if primary else color, color if primary else None, 5)
            txt = f"{v:+.2f}".replace("-", "−")
            tx = X(max(b, v)) + 16
            c.text(tx, y + 8, txt, (tx, min(x1 + gap - 6, W - 8)), NOTE, 700 if primary else 400, color=color)
    c.text(24 + label_w, 470 - 12, "Difference in verified completion (72 paired episodes; bars are task-cluster bootstrap intervals)",
           (24 + label_w, W - 24), NOTE, color=INK2)
    return c.svg()


# ------------------------------------------------------------------ stopping study
def fig_probe_stop():
    s = load("v09_summary.json")
    ref = load("v09_llm_free_reference.json")
    c = Canvas(W, 560)
    series = [("memory_only", "memory_only_autostop", "model selects probes", LLM, "#FFFFFF", "circle"),
              ("hesp_eigc_blind", "hesp_eigc_blind_autostop", "controller selects (EIG/cost)", HESP, HESP, "circle"),
              (None, "hesp_random_blind_autostop", "controller selects (random)", HESP_LIGHT, HESP_LIGHT, "triangle")]
    panels = [(0, "The model decides when to stop"), (1, "The controller may also stop")]
    y0, y1 = 110, 430
    left, gap = 118, 60
    pw = (W - left - 24 - gap) / 2
    Y = lambda v: y1 - v * (y1 - y0)
    for pi, title in panels:
        x0 = left + pi * (pw + gap)
        x1 = x0 + pw
        c.text(x0, 40, title, (x0, x1), TITLE, 700)
        for t in (0, 0.25, 0.5, 0.75, 1.0):
            c.line(x0, Y(t), x1, Y(t), GRID if t else AXIS, 1.2 if t else 1.8)
            if pi == 0:
                c.text(x0 - 12, Y(t) + 8, f"{t:g}", (x0 - 70, x0 - 6), TICK, anchor="end", color=MUTED)
        if pi == 1:
            r = ref["verified"]["controller_eigc_autostop"]
            c.line(x0, Y(r), x1, Y(r), AMBER, 2.5, dash="10 7")
            c.text(x1, Y(r) - 12, f"no LLM, controller only: {r:.3f}", (x0 + pw * 0.35, x1 + 4), NOTE, 700,
                   anchor="end", color=AMBER)
        step = pw / len(MODELS)
        for j, (key, lab) in enumerate(MODELS):
            cx = x0 + step * (j + 0.5)
            c.text(cx, y1 + 36, lab, (cx - step / 2 + 2, cx + step / 2 - 2), TICK, anchor="middle")
            present = [sr for sr in series if sr[pi] is not None]
            offs = [(-18, 18)[k] if len(present) == 2 else (-26, 0, 26)[k] for k in range(len(present))]
            for (arms0, arms1, _, stroke, fill, shape), dx in zip(present, offs):
                arm = (arms0, arms1)[pi]
                v = s[key]["verified"][arm]
                c.marker(shape, cx + dx, Y(v), 10, fill, stroke, 3)
    c.text(24, (y0 + y1) / 2, "Verified completion", (24 - 300, 24 + 300), LABEL, anchor="middle", color=INK2,
           rotate=-90)
    lx = left
    for k, (_, _, name, stroke, fill, shape) in enumerate(series):
        x = lx + k * 400
        c.marker(shape, x + 10, 522, 10, fill, stroke, 3)
        c.text(x + 32, 530, name, (x + 28, x + 396), LABEL)
    return c.svg()


# ------------------------------------------------------------------ architecture
def box(c, x, y, w, h, title, lines, stroke, tint, title_color=None, dash=None, size=LABEL):
    c.rect(x, y, w, h, tint, stroke, 2.5, 14, dash)
    c.text(x + 18, y + 38, title, (x + 12, x + w - 12), TITLE, 700, color=title_color or stroke)
    for i, ln in enumerate(lines):
        c.text(x + 18, y + 78 + i * 32, ln, (x + 12, x + w - 12), size, color=INK2)


def fig_architecture():
    c = Canvas(W, 700)
    # planner
    box(c, 24, 180, 294, 216, "Planner (local LLM)",
        ["reads task, history,", "ledger, budgets", "returns one decision:", "action · finish · stop"], LLM, LLM_TINT)
    # controller frame
    cx0, cy0, cx1, cy1 = 400, 24, 1070, 560
    c.rect(cx0, cy0, cx1 - cx0, cy1 - cy0, HESP_TINT, HESP, 3, 18)
    c.text(cx0 + 22, cy0 + 44, "Controller", (cx0 + 12, cx1 - 12), TITLE + 2, 700, color=HESP)
    c.text(cx0 + 200, cy0 + 44, "owns state, selection, and acceptance", (cx0 + 190, cx1 - 12), NOTE,
           style="italic", color=HESP)
    inner = [(cx0 + 24, 90, "Hypothesis ledger", ["posterior p(h) over causes + other", "support / against per observation",
                                                  "reset on a new state version"]),
             (cx0 + 24, 262, "Probe selection", ["EIG(a) / cost(a) over legal probes",
                                                 "untried, affordable, prerequisites met", "tables P(o | h, a), frozen"]),
             (cx0 + 24, 434, "Acceptance and stop", ["finish accepted only with current", "supporting evidence and p ≥ 0.8"])]
    for x, y, title, lines in inner:
        h = 150 if len(lines) == 3 else 112
        c.rect(x, y, cx1 - cx0 - 48, h, "#FFFFFF", HESP, 1.8, 10)
        c.text(x + 16, y + 34, title, (x + 10, cx1 - 34), LABEL + 1, 700, color=INK)
        for i, ln in enumerate(lines):
            c.text(x + 16, y + 68 + i * 30, ln, (x + 10, cx1 - 34), NOTE, color=INK2)
    c.text(cx0 + 24 + 390, 434 + 34, "controller may also stop", (cx0 + 24 + 380, cx1 - 34), NOTE, 700, color=AMBER)
    # probes
    box(c, 1140, 150, 262, 262, "Read-only probes",
        ["auth · HTTP · sources", "admin config · egress", "DNS · inventory", "change tickets", "threat intel · runbook"],
        INK2, "#FFFFFF", INK, size=NOTE)
    # verifier and journal
    box(c, 1140, 510, 262, 150, "Verifier", ["cause in effect, and", "a unique signature cited"], AMBER, AMBER_TINT, size=NOTE)
    c.rect(400, 600, 670, 70, "#FFFFFF", MUTED, 2, 12, dash="8 6")
    c.text(420, 645, "Journal + audit: every prediction written before its observation",
           (410, 1060), NOTE, 700, color=INK2)
    # alert
    c.rect(24, 60, 280, 70, "#FFFFFF", INK, 2, 12)
    c.text(44, 104, "Alert (one case)", (34, 294), LABEL, 700)
    arrows = arrow_defs(INK2, HESP, AMBER, MUTED, LLM)
    c.line(164, 130, 164, 176, INK2, 2.5, arrow="a374151")
    # planner <-> controller
    c.line(398, 250, 322, 250, HESP, 3, arrow="a1D4ED8")
    c.text(357, 236, "request", (318, 398), NOTE, anchor="middle", color=HESP)
    c.line(318, 360, 394, 360, LLM, 3, arrow="a4B5563")
    c.text(359, 394, "decision", (320, 400), NOTE, anchor="middle", color=LLM)
    # controller -> probes -> ledger
    c.line(1070, 300, 1136, 300, HESP, 3, arrow="a1D4ED8")
    c.text(1076, 288, "run", (1072, 1136), NOTE, color=HESP)
    c.path("M1140,190 C1100,190 1100,150 1074,150", INK2, 3, arrow="a374151")
    c.text(1078, 128, "outcome", (1074, 1150), NOTE, color=INK2)
    # verdict -> verifier
    c.path("M1070,500 C1110,500 1100,560 1136,560", AMBER, 3, arrow="aB45309")
    c.text(1132, 600, "verdict", (1060, 1138), NOTE, anchor="end", color=AMBER)
    c.line(735, 560, 735, 596, MUTED, 2.2, dash="6 5", arrow="a6B7280")
    return c.svg(arrows)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    outs = {"fig-architecture": fig_architecture(), "fig-decomposition": fig_decomposition(),
            "fig-probe-stop": fig_probe_stop()}
    paths = []
    for name, svg in outs.items():
        p = ASSETS / f"{name}.svg"
        p.write_bytes(svg.encode("utf-8"))
        paths.append(p)
        print(p)
    if args.check:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from render_figures import check_fit
        total = 0
        for p in paths:
            bad = check_fit(p)
            total += len(bad)
            for b in bad:
                print(f"OVERFLOW {p.name}: {b}")
        print(f"text fit: {total} overflow(s)")
        if total:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
