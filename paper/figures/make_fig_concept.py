"""Figure 1, concept version: what HESP contains, drawn with shapes rather than words.

An investigation loop (racetrack) around the local LLM, with four stations named by the acronym:
Hypotheses (belief as dot sizes), Evidence (probe chosen by information gain), State (posterior
crossing the stopping threshold), Planning (the journal every step is written to). An alert enters
on the left; a verified verdict leaves on the right. Sized for a 7 in (504 pt) full-width figure.

    python paper/figures/make_fig_concept.py --check
"""
import argparse
import math
from pathlib import Path
import sys
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "docs" / "figures"))
OUT = HERE / "fig_concept.svg"

S = 3.0
W_PT, H_PT = 504, 206
FONT = "Helvetica, Arial, sans-serif"
INK, GRAY, MID, LIGHT, FAINT = "#1F2937", "#6B7280", "#9CA3AF", "#D1D5DB", "#EEF1F5"
BLUE, BLUE_BG, AMBER, GREEN = "#2563EB", "#E8EDF2", "#D97706", "#059669"


def P(v):
    return f"{v * S:.1f}"


class Fig:
    def __init__(self):
        self.parts = []

    def add(self, s):
        self.parts.append(s)

    def circle(self, x, y, r, fill="none", stroke=None, sw=0.8, dash=None):
        st = f' stroke="{stroke}" stroke-width="{sw * S:.2f}"' if stroke else ""
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<circle cx="{P(x)}" cy="{P(y)}" r="{P(r)}" fill="{fill}"{st}{d}/>')

    def rect(self, x, y, w, h, fill="none", stroke=None, sw=0.8, rx=0, dash=None, shadow=False):
        st = f' stroke="{stroke}" stroke-width="{sw * S:.2f}"' if stroke else ""
        d = f' stroke-dasharray="{dash}"' if dash else ""
        sh = ' filter="url(#shadow)"' if shadow else ""
        self.add(f'<rect x="{P(x)}" y="{P(y)}" width="{P(w)}" height="{P(h)}" rx="{P(rx)}" fill="{fill}"{st}{d}{sh}/>')

    def line(self, x1, y1, x2, y2, color=GRAY, sw=0.8, dash=None, cap="round"):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<line x1="{P(x1)}" y1="{P(y1)}" x2="{P(x2)}" y2="{P(y2)}" stroke="{color}" '
                 f'stroke-width="{sw * S:.2f}" stroke-linecap="{cap}"{d}/>')

    def path(self, d, color=GRAY, sw=0.8, fill="none", dash=None, marker=None):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        mk = f' marker-end="url(#{marker})"' if marker else ""
        self.add(f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{sw * S:.2f}" '
                 f'stroke-linecap="round" stroke-linejoin="round"{da}{mk}/>')

    def text(self, x, y, s, size, fit, weight=400, color=INK, anchor="middle", italic=False):
        it = ' font-style="italic"' if italic else ""
        self.add(f'<text x="{P(x)}" y="{P(y)}" font-family="{FONT}" font-size="{P(size)}" font-weight="{weight}"{it} '
                 f'fill="{color}" text-anchor="{anchor}" data-fit="{P(fit[0])},{P(fit[1])}">{escape(s)}</text>')


def pts(*xy):
    return " ".join(f"{P(x)},{P(y)}" for x, y in xy)


# ------------------------------------------------------------------ glyphs
def station(f, cx, cy, letter, word, color=BLUE):
    f.circle(cx, cy, 25, "#FFFFFF", None)
    f.add(f'<circle cx="{P(cx)}" cy="{P(cy)}" r="{P(25)}" fill="#FFFFFF" filter="url(#shadow)"/>')
    f.circle(cx, cy, 25, "none", color, 0.9)
    return cx, cy


def glyph_hypotheses(f, cx, cy):
    """Nine candidate causes; dot area is belief. One remains strong."""
    sizes = [0.02, 0.10, 1.00, 0.02, 0.02, 0.02, 0.18, 0.18, 0.06]
    for k, v in enumerate(sizes):
        x = cx - 9 + (k % 3) * 9
        y = cy - 9 + (k // 3) * 9
        if v < 0.05:
            f.circle(x, y, 1.6, "none", LIGHT, 0.6)
        else:
            f.circle(x, y, 1.4 + 3.2 * math.sqrt(v), BLUE if v == 1.0 else MID)


def glyph_evidence(f, cx, cy):
    """Three probes; the most informative one is picked (magnifier)."""
    for k in range(3):
        y = cy - 9 + k * 9
        chosen = k == 1
        f.rect(cx - 13, y - 3, 17, 6, "#FFFFFF" if not chosen else "#DBE6FD", BLUE if chosen else MID, 0.6, rx=1.2)
        for j in range(3):
            f.line(cx - 11 + j * 5, y, cx - 8.5 + j * 5, y, BLUE if chosen else MID, 0.6)
    f.circle(cx + 7, cy - 1, 4.2, "none", BLUE, 1.0)
    f.line(cx + 10, cy + 2, cx + 13.5, cy + 5.5, BLUE, 1.3)


def glyph_state(f, cx, cy):
    """Belief rises past the stopping threshold; a flag marks the stop."""
    base, top = cy + 12, cy - 12
    f.rect(cx - 10, top, 6, base - top, FAINT, LIGHT, 0.5, rx=1)
    f.rect(cx - 10, top + 3, 6, base - top - 3, BLUE, rx=1)
    f.line(cx - 14, top + 7, cx + 3, top + 7, INK, 0.6, dash=f"{1.2 * S:.1f},{1.0 * S:.1f}")
    f.line(cx + 6, base, cx + 6, top + 1, INK, 0.8)
    f.path(f"M{P(cx + 6)},{P(top + 1)} L{P(cx + 14)},{P(top + 4)} L{P(cx + 6)},{P(top + 7)} Z", AMBER, 0.5, fill=AMBER)


def glyph_planning(f, cx, cy):
    """A journal: every step written down and checked."""
    f.rect(cx - 10, cy - 13, 20, 26, "#FFFFFF", MID, 0.7, rx=1.5)
    for k in range(4):
        y = cy - 8 + k * 6
        f.path(f"M{P(cx - 7)},{P(y)} L{P(cx - 5.6)},{P(y + 1.4)} L{P(cx - 3)},{P(y - 1.6)}", GREEN, 0.7)
        f.line(cx - 1, y, cx + 7, y, MID, 0.6)


def glyph_llm(f, cx, cy):
    """The local model: a chip with pins."""
    f.rect(cx - 13, cy - 13, 26, 26, "#FFF7ED", AMBER, 1.0, rx=3)
    f.rect(cx - 7, cy - 7, 14, 14, "#FFFFFF", AMBER, 0.6, rx=1.5)
    for k in range(4):
        o = -9 + k * 6
        for (x1, y1, x2, y2) in ((cx + o, cy - 13, cx + o, cy - 17), (cx + o, cy + 13, cx + o, cy + 17),
                                 (cx - 13, cy + o, cx - 17, cy + o), (cx + 13, cy + o, cx + 17, cy + o)):
            f.line(x1, y1, x2, y2, AMBER, 0.8)


def glyph_alert(f, cx, cy):
    f.path(f"M{P(cx)},{P(cy - 12)} L{P(cx + 12)},{P(cy + 9)} L{P(cx - 12)},{P(cy + 9)} Z", AMBER, 1.0, fill="#FFF7ED")
    f.line(cx, cy - 4, cx, cy + 2.5, AMBER, 1.4)
    f.circle(cx, cy + 5.6, 0.9, AMBER)


def glyph_verdict(f, cx, cy):
    f.circle(cx, cy, 12, "#ECFDF5", GREEN, 1.0)
    f.path(f"M{P(cx - 5.5)},{P(cy + 0.5)} L{P(cx - 1.5)},{P(cy + 4.5)} L{P(cx + 6)},{P(cy - 4)}", GREEN, 1.6)


def build():
    f = Fig()
    cx, cy, rx, ry = 252, 101, 150, 58
    # the investigation loop
    f.add(f'<ellipse cx="{P(cx)}" cy="{P(cy)}" rx="{P(rx + 14)}" ry="{P(ry + 14)}" fill="{BLUE_BG}"/>')
    f.add(f'<ellipse cx="{P(cx)}" cy="{P(cy)}" rx="{P(rx)}" ry="{P(ry)}" fill="none" stroke="{BLUE}" '
          f'stroke-width="{1.1 * S:.1f}" stroke-dasharray="{3 * S:.1f},{2.2 * S:.1f}"/>')
    # direction of travel: small chevrons on the track
    for ang in (205, 335, 25, 155):
        a = math.radians(ang)
        x, y = cx + rx * math.cos(a), cy + ry * math.sin(a)
        tx, ty = -rx * math.sin(a), ry * math.cos(a)
        n = math.hypot(tx, ty)
        tx, ty = tx / n, ty / n
        nx, ny = -ty, tx
        tip = (x + tx * 3.2, y + ty * 3.2)
        f.path(f"M{P(tip[0] - tx * 4 + nx * 2.8)},{P(tip[1] - ty * 4 + ny * 2.8)} L{P(tip[0])},{P(tip[1])} "
               f"L{P(tip[0] - tx * 4 - nx * 2.8)},{P(tip[1] - ty * 4 - ny * 2.8)}", BLUE, 1.1)
    # four stations: H left, E top, S right, P bottom
    # label placement: below the side stations, beside the top and bottom ones
    stations = [((cx - rx, cy), "Hypotheses", glyph_hypotheses, (-12, 38, "end")),
                ((cx, cy - ry), "Evidence", glyph_evidence, (0, -30, "middle")),
                ((cx + rx, cy), "State", glyph_state, (12, 38, "start")),
                ((cx, cy + ry), "Planning", glyph_planning, (0, 38, "middle"))]
    for (sx, sy), word, glyph, (dx, dy, anchor) in stations:
        station(f, sx, sy, word[0], word)
        glyph(f, sx, sy)
        fit = {"middle": (sx - 40, sx + 40), "start": (sx + dx - 2, sx + dx + 60),
               "end": (sx + dx - 60, sx + dx + 2)}[anchor]
        f.text(sx + dx, sy + dy, word, 9.2, fit, weight=700, color=BLUE, anchor=anchor)
    # the model inside the loop, wired to what it may do
    glyph_llm(f, cx, cy)
    f.text(cx, cy + 27, "local LLM", 8, (cx - 30, cx + 30), weight=700, color=AMBER)
    f.line(cx, cy - 19, cx, cy - ry + 26, AMBER, 0.7, dash=f"{1.4 * S:.1f},{1.2 * S:.1f}")
    f.line(cx + 19, cy, cx + rx - 26, cy, AMBER, 0.7, dash=f"{1.4 * S:.1f},{1.2 * S:.1f}")
    f.text(cx + 3, cy - 30, "proposes", 7, (cx + 1, cx + 36), color=AMBER, anchor="start", italic=True)
    f.text(cx + 58, cy - 3, "may finish", 7, (cx + 36, cx + 80), color=AMBER, italic=True)
    # entry and exit
    glyph_alert(f, 18, cy)
    f.text(18, cy + 21, "alert", 8, (4, 32), weight=700, color=INK)
    f.path(f"M{P(32)},{P(cy)} L{P(cx - rx - 27)},{P(cy)}", GRAY, 0.9, marker="arr")
    glyph_verdict(f, 486, cy)
    f.text(486, cy + 21, "verdict", 8, (468, 504), weight=700, color=INK)
    f.path(f"M{P(cx + rx + 27)},{P(cy)} L{P(472)},{P(cy)}", GRAY, 0.9, marker="arr")
    defs = (f'<filter id="shadow" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="{0.4 * S:.1f}" '
            f'stdDeviation="{0.9 * S:.1f}" flood-color="#000" flood-opacity="0.10"/></filter>'
            f'<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{GRAY}"/></marker>')
    w, h = int(W_PT * S), int(H_PT * S)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}"><defs>{defs}</defs>'
            f'<rect width="{w}" height="{h}" fill="#FFFFFF"/>' + "\n".join(f.parts) + "</svg>\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    OUT.write_text(build(), encoding="utf-8")
    from render_figures import check_fit, render
    if args.check:
        bad = check_fit(OUT)
        for b in bad:
            print("OVERFLOW:", b)
        print(f"text fit: {len(bad)} overflow(s)")
    render(OUT, scale=2)


if __name__ == "__main__":
    main()
