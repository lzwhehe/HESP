"""Figure 1, "Modern Minimal" version: Gemini's draft design (paper/figures/gemini/, prompt from
gen_fig_overview_gemini.py) rebuilt at print size, per the academic-plotting skill's correction step.

Changes from the draft: laid out for a 7 in (504 pt) full-width figure with no text below 7 pt at
print size, and the ledger bars drawn from the real episode (hypotheses keep their positions across
the four groups). Coordinates are in points times S so the SVG renders crisply.

    python paper/figures/make_fig_overview_minimal.py --check
    -> paper/figures/fig_overview_minimal.svg / .pdf / .png
"""
import argparse
import json
from pathlib import Path
import sys
import tarfile
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "docs" / "figures"))
ARCHIVE = ROOT / "hesp_research" / "results" / "v09_llama8b" / "runs_archive.tar.gz"
RUN = "run0087_sec-base-02_0_hesp_eigc_blind_autostop"
ORDER = ["credential_stuffing", "sqli_probe", "misconfig_exposed_admin", "authorized_scan", "false_positive_monitor",
         "insider_exfil", "vuln_component", "dns_c2", "other"]
OUT = HERE / "fig_overview_minimal.svg"

S = 3.0                                   # px per pt
W_PT, H_PT = 504, 196
FONT = "Helvetica, Arial, sans-serif"
INK, GRAY, LIGHT = "#1F2937", "#6B7280", "#D1D5DB"
BLUE, BLUE_BG = "#2563EB", "#E8EDF2"
AMBER, AMBER_BG = "#D97706", "#F5F0E8"
GREEN, GREEN_BG = "#059669", "#E8F2EE"
T_TITLE, T_BODY, T_SMALL = 8.2, 7.0, 7.0   # pt at print size


def p(v):
    return f"{v * S:.1f}"


class Fig:
    def __init__(self):
        self.parts = []

    def rect(self, x, y, w, h, fill, rx=4, shadow=False, stroke=None, dash=None):
        extra = ' filter="url(#shadow)"' if shadow else ""
        if stroke:
            extra += f' stroke="{stroke}" stroke-width="{0.5 * S:.1f}"'
        if dash:
            extra += f' stroke-dasharray="{dash}"'
        self.parts.append(f'<rect x="{p(x)}" y="{p(y)}" width="{p(w)}" height="{p(h)}" rx="{p(rx)}" fill="{fill}"{extra}/>')

    def text(self, x, y, s, size, fit, weight=400, color=INK, anchor="start", italic=False):
        st = ' font-style="italic"' if italic else ""
        self.parts.append(f'<text x="{p(x)}" y="{p(y)}" font-family="{FONT}" font-size="{p(size)}" font-weight="{weight}"'
                          f'{st} fill="{color}" text-anchor="{anchor}" data-fit="{p(fit[0])},{p(fit[1])}">{escape(s)}</text>')

    def line(self, x1, y1, x2, y2, color=GRAY, width=0.55, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<line x1="{p(x1)}" y1="{p(y1)}" x2="{p(x2)}" y2="{p(y2)}" stroke="{color}" '
                          f'stroke-width="{width * S:.2f}"{d}/>')

    def circle(self, x, y, r, fill):
        self.parts.append(f'<circle cx="{p(x)}" cy="{p(y)}" r="{p(r)}" fill="{fill}"/>')

    def head(self, x, y, direction, color=GRAY):
        a = 2.4
        if direction == "right":
            pts = [(x, y), (x - a, y - a * 0.55), (x - a, y + a * 0.55)]
        elif direction == "left":
            pts = [(x, y), (x + a, y - a * 0.55), (x + a, y + a * 0.55)]
        else:
            pts = [(x, y), (x - a * 0.55, y - a), (x + a * 0.55, y - a)]
        self.parts.append('<polygon points="' + " ".join(f"{p(u)},{p(v)}" for u, v in pts) + f'" fill="{color}"/>')

    def arrow(self, x1, y1, x2, y2, badge=None, badge_color=GRAY, label=None, label_above=True, dash=None):
        self.line(x1, y1, x2, y2, dash=dash)
        self.circle(x1, y1, 0.9, GRAY)
        self.head(x2, y2, "right" if x2 > x1 else "left" if x2 < x1 else "down")
        if badge:
            bx, by = (x1 + x2) / 2, (y1 + y2) / 2
            self.circle(bx, by, 4.3, badge_color)
            self.parts.append(f'<text x="{p(bx)}" y="{p(by + 2.45)}" font-family="{FONT}" font-size="{p(T_SMALL)}" '
                              f'font-weight="700" fill="#FFFFFF" text-anchor="middle">{badge}</text>')
            if label:
                ly = by - 6.4 if label_above else by + 11.2
                self.text(bx, ly, label, T_SMALL, (bx - 16, bx + 16), color=GRAY, anchor="middle")

    def card(self, x, y, w, h, accent, title, lines, title_size=T_TITLE, line_gap=8.6):
        self.rect(x, y, w, h, "#FFFFFF", rx=4, shadow=True)
        self.rect(x, y + 5, 1.2, 14, accent, rx=0.6)
        self.text(x + 6, y + 12, title, title_size, (x + 4, x + w - 3), weight=700)
        for i, ln in enumerate(lines):
            self.text(x + 6, y + 23 + i * line_gap, ln, T_BODY, (x + 4, x + w - 3))


def episode():
    with tarfile.open(ARCHIVE) as tf:
        events = [json.loads(x) for x in tf.extractfile(f"{RUN}/events.jsonl").read().decode("utf-8").splitlines()]
    first = next(e for e in events if e["kind"] == "evidence_update")
    steps = [first["evidence"]["before"]] + [e["evidence"]["after"] for e in events if e["kind"] == "evidence_update"]
    winner = next(e for e in events if e["kind"] == "independent_verification")["hypothesis"]
    return steps, winner


def build():
    steps, winner = episode()
    f = Fig()
    # Alert
    f.card(1, 72, 47, 30, GRAY, "Alert", ["one incident"])
    f.arrow(48, 87, 55, 87)
    # Planner
    f.rect(55, 56, 88, 62, AMBER_BG, rx=5)
    f.card(59, 61, 80, 52, AMBER, "Planner", ["local LLM (7B–72B)", "returns action,", "finish, or stop"])
    # Controller
    cx0, cx1 = 172, 391
    f.rect(cx0, 4, cx1 - cx0, 152, BLUE_BG, rx=6)
    f.rect(cx0 + 6, 9.5, 3.4, 3.4, BLUE, rx=0.8)
    f.text(cx0 + 12, 13, "HESP controller", T_TITLE, (cx0 + 10, cx0 + 90), weight=700)
    f.text(cx1 - 6, 13, "owns state, probe choice, acceptance", T_SMALL, (cx0 + 88, cx1 - 3), color=GRAY, anchor="end")
    # ledger with the real episode
    lx, ly, lw, lh = cx0 + 6, 20, 102, 130
    f.card(lx, ly, lw, lh, BLUE, "Hypothesis ledger", ["posterior p(h) over", "8 causes + other"])
    base, hmax, bw, gap = ly + 96, 46, 2.0, 4.6
    x0 = lx + 7
    labels = ["prior", "IPs", "HTTP", "admin"]
    for g, scores in enumerate(steps):
        gx = x0 + g * (9 * bw + gap)
        f.line(gx - 0.5, base, gx + 9 * bw + 0.5, base, LIGHT, 0.4)
        for i, h in enumerate(ORDER):
            v = scores[h]
            color = BLUE if (h == winner and g > 0) else ("#9CA3AF" if g == 0 else GRAY)
            height = max(v * hmax, 0.6)
            f.rect(gx + i * bw + 0.25, base - height, bw - 0.5, height, color if v >= 0.0015 else LIGHT, rx=0)
        f.text(gx + 4.5 * bw, base + 8.4, labels[g], T_SMALL, (gx - 3, gx + 9 * bw + 3), color=GRAY, anchor="middle")
    top = steps[-1][winner]
    wx = x0 + 3 * (9 * bw + gap) + ORDER.index(winner) * bw + bw / 2
    f.text(wx - 2, base - top * hmax - 2, f"p = {top:.2f}", T_SMALL, (wx - 30, wx + 2), weight=700, color=BLUE,
           anchor="end")
    for k, ln in enumerate(["one real episode:", "9 causes → 1 in 3 probes"]):
        f.text(lx + lw / 2, ly + lh - 11.5 + k * 8.4, ln, T_SMALL, (lx + 2, lx + lw - 2), italic=True, anchor="middle")
    # selection and acceptance
    rx0, rw = lx + lw + 6, cx1 - (lx + lw + 6) - 6
    f.card(rx0, 20, rw, 50, BLUE, "Probe selection", ["rank legal probes by", "EIG(a)/c(a);", "run the best"])
    f.card(rx0, 82, rw, 68, BLUE, "Acceptance and stop",
           ["verdict needs p ≥ 0.8", "and current support;", "the controller may", "also stop by itself"])
    # planner <-> controller
    f.arrow(cx0, 78, 143, 78, badge="1", badge_color=BLUE, label="request")
    f.arrow(143, 97, cx0, 97, badge="2", badge_color=AMBER, label="decision", label_above=False)
    # probes and verifier
    px0 = 414
    f.card(px0, 20, W_PT - px0, 60, GRAY, "Read-only probes",
           ["auth, HTTP, sources,", "DNS, egress, config,", "inventory, tickets,", "threat intel"], line_gap=8.3)
    f.rect(px0 - 2, 90, W_PT - px0 + 2, 60, GREEN_BG, rx=5)
    f.card(px0 + 2, 95, W_PT - px0 - 4, 50, GREEN, "Verifier", ["correct cause and a", "cited signature", "unique to it"])
    f.arrow(cx1 - 6, 42, px0, 42, badge="3", badge_color=BLUE, label="run")
    oy = 76
    f.arrow(px0, oy, lx + lw, oy + 0.001, badge=None)
    f.circle((cx1 + px0) / 2, oy, 4.3, GRAY)
    f.parts.append(f'<text x="{p((cx1 + px0) / 2)}" y="{p(oy + 2.45)}" font-family="{FONT}" font-size="{p(T_SMALL)}" '
                   f'font-weight="700" fill="#FFFFFF" text-anchor="middle">4</text>')
    f.text((cx1 + px0) / 2, oy + 11.2, "outcome", T_SMALL, ((cx1 + px0) / 2 - 16, (cx1 + px0) / 2 + 16), color=GRAY,
           anchor="middle")
    f.arrow(cx1 - 6, 118, px0 + 2, 118, badge="5", badge_color=GREEN, label="verdict")
    # journal band
    f.arrow((cx0 + cx1) / 2, 156, (cx0 + cx1) / 2, 171.5, dash=f"{2 * S:.1f},{1.6 * S:.1f}")
    f.rect(0.5, 172, W_PT - 1, 22, "#FFFFFF", rx=4, stroke=GRAY, dash=f"{2 * S:.1f},{2 * S:.1f}")
    f.text(W_PT / 2, 185.5, "Journal and audit: every prediction is written before the observation it predicts; "
           "every episode is replayed", T_BODY, (4, W_PT - 4), anchor="middle")
    defs = (f'<filter id="shadow" x="-10%" y="-10%" width="120%" height="130%"><feDropShadow dx="0" dy="{0.35 * S:.2f}" '
            f'stdDeviation="{0.7 * S:.2f}" flood-color="#000000" flood-opacity="0.08"/></filter>')
    w, h = int(W_PT * S), int(H_PT * S)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}"><defs>{defs}</defs>'
            f'<rect width="{w}" height="{h}" fill="#FFFFFF"/>' + "\n".join(f.parts) + "</svg>\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    OUT.write_text(build(), encoding="utf-8")
    print(OUT)
    from render_figures import check_fit, render
    if args.check:
        bad = check_fit(OUT)
        for b in bad:
            print("OVERFLOW:", b)
        print(f"text fit: {len(bad)} overflow(s)")
    render(OUT, scale=2)


if __name__ == "__main__":
    main()
