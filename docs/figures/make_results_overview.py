"""HESP results overview: four panels, each answering one reviewer question.

Output: docs/assets/hesp-results-overview.svg (render PDF/PNG with render_figures.py).

  (a) Does HESP make local planners finish investigations, and how does that change with
      scale?                                              v0.6, emp20 table (non-oracle)
  (b) Where does the gain come from: taking probe choice away from the planner, or the
      EIG/cost ranking?                                   v0.5 decomposition
  (c) Does it need the designer's near-oracle table?      v0.6 table sources
  (d) When an investigation does not verify, how does it end?   v0.6 outcomes

Every value and interval is computed here from results/*/outcomes.jsonl with the repo's
own paired task-cluster bootstrap (hesp.analysis.summarize, 2000 resamples, seed 2026).
Standard-library SVG, Times New Roman, sized for a 7.0 in full-width float
(1536 px canvas, 1 pt = 3.048 px). ``--check`` measures all text in headless Chrome.
"""
import argparse
import collections
import json
from pathlib import Path
import sys
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "hesp_research" / "results"
sys.path.insert(0, str(ROOT / "hesp_research"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from hesp.analysis import BENIGN_CAUSES, summarize, true_cause   # noqa: E402

OUT = ROOT / "docs" / "assets" / "hesp-results-overview.svg"
W, H = 1536, 1096
FONT = "'Times New Roman', Times, serif"
MODELS = [("7b", "7B"), ("32b", "32B"), ("72b", "72B")]
SEED = 2026

# colour roles (ccfa_ink): HESP blue throughout; baselines neutral; outcome semantics separate
INK, INK2, MUTED, GRID, AXIS = "#111827", "#374151", "#6B7280", "#E5E7EB", "#9CA3AF"
HESP, MEMORY, REACT = "#1D4ED8", "#4B5563", "#9CA3AF"
AMBER = "#B45309"
OK, MISSED, WRONG, UNSUPPORTED, NONE = "#1D4ED8", "#BE123C", "#F4A3A8", "#E9C46A", "#E5E7EB"
MODEL_SHADE = {"7b": "#111827", "32b": "#6B7280", "72b": "#B6BDC8"}
MODEL_MARK = {"7b": "circle", "32b": "square", "72b": "triangle"}
# type scale at 7.0 in
TITLE, LABEL, TICK, NOTE = 29, 25, 23, 22


# ---------------------------------------------------------------- data
def load(name):
    with (RESULTS / name / "outcomes.jsonl").open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream]


def paired(rows, arms, comparisons):
    return summarize(rows, seed=SEED, arms=arms, comparisons=comparisons)


V06_ARMS = ["react_style", "memory_only", "hesp_eigc_guard_designer", "hesp_eigc_guard_emp1",
            "hesp_eigc_guard_emp5", "hesp_eigc_guard_emp20", "hesp_eigc_guard_emp100", "hesp_eigc_guard_llmp"]
V05_ARMS = ["react_style", "memory_only", "memory_guard", "hesp_eigc", "hesp_eigc_guard", "hesp_la",
            "hesp_la_guard", "hesp_random", "hesp_llmp"]
SOURCES = [("hesp_eigc_guard_designer", "oracle"), ("hesp_eigc_guard_emp1", "1"),
           ("hesp_eigc_guard_emp5", "5"), ("hesp_eigc_guard_emp20", "20"),
           ("hesp_eigc_guard_emp100", "100"), ("hesp_eigc_guard_llmp", "LLM")]
OUTCOMES = [("verified", "verified", OK), ("missed", "attack judged benign", MISSED),
            ("wrong", "other wrong cause", WRONG), ("unsupported", "right cause, unverified", UNSUPPORTED),
            ("none", "no verdict", NONE)]


def outcome(r):
    if r["verified_simulation"]:
        return "verified"
    h, t = r["claimed_hypothesis"], true_cause(r)
    if h is None:
        return "none"
    if h == t:
        return "unsupported"
    if t not in BENIGN_CAUSES and h in BENIGN_CAUSES:
        return "missed"
    return "wrong"


def gather():
    d = {"v06": {}, "v05": {}}
    for key, _ in MODELS:
        rows = load(f"v06_{key}")
        s = paired(rows, V06_ARMS, [("hesp_eigc_guard_emp20", "memory_only")])
        comp = {arm: collections.Counter(outcome(r) for r in rows if r["arm"] == arm)
                for arm in ("react_style", "memory_only", "hesp_eigc_guard_emp20")}
        d["v06"][key] = {"verified": {a: s["modes"][a]["verified_fraction"] for a in V06_ARMS},
                         "cost": {a: s["modes"][a]["tool_cost_units"]["mean_known"] for a in V06_ARMS},
                         "delta": s["paired_verification"]["hesp_eigc_guard_emp20_minus_memory_only"],
                         "composition": comp, "n": sum(comp["memory_only"].values())}
        v5 = paired(load(f"v05_{key}"), V05_ARMS, [("hesp_random", "memory_only"), ("hesp_eigc", "hesp_random")])
        d["v05"][key] = {"take_choice": v5["paired_verification"]["hesp_random_minus_memory_only"],
                         "add_ranking": v5["paired_verification"]["hesp_eigc_minus_hesp_random"]}
    return d


# ---------------------------------------------------------------- svg primitives
parts = []


def add(s):
    parts.append(s)


def text(x, y, s, fit, size=LABEL, weight=400, anchor="start", color=INK, style="normal", raw=False, rotate=None):
    body = s if raw else escape(s)
    rot = f' transform="rotate({rotate} {x} {y})"' if rotate else ""
    add(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" '
        f'font-style="{style}" fill="{color}" text-anchor="{anchor}" data-fit="{fit[0]:.1f},{fit[1]:.1f}"{rot}>'
        f'{body}</text>')


def line(x1, y1, x2, y2, color=AXIS, sw=1.5, dash=None, cap="butt"):
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{sw}" '
        f'stroke-linecap="{cap}"{dd}/>')


def rect(x, y, w, h, fill, stroke="none", sw=0, rx=0):
    add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w, 0):.1f}" height="{max(h, 0):.1f}" rx="{rx}" fill="{fill}" '
        f'stroke="{stroke}" stroke-width="{sw}"/>')


def marker(kind, x, y, r, fill, stroke=None, sw=2):
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    if kind == "circle":
        add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}"{st}/>')
    elif kind == "square":
        add(f'<rect x="{x - r * 0.9:.1f}" y="{y - r * 0.9:.1f}" width="{r * 1.8:.1f}" height="{r * 1.8:.1f}" '
            f'fill="{fill}"{st}/>')
    else:
        add(f'<path d="M{x:.1f},{y - r * 1.1:.1f} L{x + r:.1f},{y + r * 0.8:.1f} L{x - r:.1f},{y + r * 0.8:.1f} Z" '
            f'fill="{fill}"{st}/>')


def panel_title(x, y, letter, title, x1):
    add(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{TITLE}" fill="{INK}" '
        f'data-fit="{x},{x1}"><tspan font-weight="700">({letter})</tspan> {escape(title)}</text>')


def y_axis(x, y0, y1, lo, hi, ticks, fmt, fit_x0, label=None, grid_to=None):
    for t in ticks:
        y = y1 - (t - lo) / (hi - lo) * (y1 - y0)
        if grid_to:
            line(x, y, grid_to, y, GRID, 1.2)
        text(x - 10, y + 8, fmt(t), (fit_x0, x - 4), TICK, anchor="end", color=MUTED)
    line(x, y0, x, y1, AXIS, 1.5)
    if label:
        text(fit_x0 + 2, (y0 + y1) / 2, label, (fit_x0 - 400, fit_x0 + 400), LABEL, anchor="middle",
             color=INK2, rotate=-90)


def ci_text(v):
    lo, hi = v["cluster_bootstrap_percentile_95"]
    return f"[{lo:+.2f}, {hi:+.2f}]".replace("+0.00", "0.00").replace("-0.00", "0.00")


# ---------------------------------------------------------------- panels
def panel_a(d, x0, y0, x1, y1):
    """Verified completion per model: ReAct, Memory-only, HESP; memory -> HESP delta with CI."""
    panel_title(x0, y0 + 26, "a", "Verified completion", x1)
    px0, px1, py0, py1 = x0 + 92, x1 - 150, y0 + 70, y1 - 118
    fmt = lambda t: f"{t:.1f}"
    y_axis(px0, py0, py1, 0, 1, [0, 0.25, 0.5, 0.75, 1.0], lambda t: f"{t:g}", x0 + 30, "Fraction of 72 episodes",
           grid_to=px1)
    Y = lambda v: py1 - v * (py1 - py0)
    xs = {k: px0 + (px1 - px0) * f for (k, _), f in zip(MODELS, (0.2, 0.52, 0.84))}
    for key, lab in MODELS:
        x = xs[key]
        text(x, py1 + 34, lab, (x - 40, x + 40), LABEL, 700, anchor="middle")
        v = d["v06"][key]["verified"]
        m, h, r = v["memory_only"], v["hesp_eigc_guard_emp20"], v["react_style"]
        line(x, Y(m), x, Y(h), HESP, 4, cap="round")
        marker("circle", x, Y(r), 9, "#FFFFFF", REACT, 2.5)
        marker("circle", x, Y(m), 9, MEMORY)
        marker("circle", x, Y(h), 11, HESP)
        delta = d["v06"][key]["delta"]
        half = (xs["32b"] - xs["7b"]) / 2
        text(x, py1 + 72, f"+{delta['difference']:.2f}", (x - half, x + half), LABEL, 700, anchor="middle",
             color=HESP)
        text(x, py1 + 98, ci_text(delta), (x - half, x + half), NOTE, anchor="middle", color=HESP)
    text(px0 - 10, py1 + 72, "Δ", (x0, px0 - 4), LABEL, 700, anchor="end", color=HESP)
    # direct labels at the right of the last group
    lx = xs["72b"] + 26
    v72 = d["v06"]["72b"]["verified"]
    text(lx, Y(v72["hesp_eigc_guard_emp20"]) + 8, "HESP", (lx, x1), LABEL, 700, color=HESP)
    text(lx, Y(v72["memory_only"]) + 14, "Memory-only", (lx, x1), LABEL, color=MEMORY)
    text(lx, Y(v72["react_style"]) + 8, "ReAct", (lx, x1), LABEL, color=MUTED)


def panel_b(d, x0, y0, x1, y1):
    """Delta ladder: taking probe choice from the planner vs adding the EIG/cost ranking."""
    panel_title(x0, y0 + 26, "b", "Where the gain comes from", x1)
    px0, px1, py0, py1 = x0 + 92, x1 - 24, y0 + 118, y1 - 60
    lo, hi = -0.4, 0.8
    X = lambda v: px0 + (v - lo) / (hi - lo) * (px1 - px0)
    for t in (-0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8):
        line(X(t), py0 - 10, X(t), py1, GRID if t else AXIS, 1.2 if t else 1.8)
        text(X(t), py1 + 30, f"{t:+.1f}".replace("+0.0", "0"), (X(t) - 34, X(t) + 34), TICK, anchor="middle",
             color=MUTED)
    text((px0 + px1) / 2, py1 + 62, "Δ verified completion (95% task-cluster interval)",
         (px0 - 40, px1 + 20), LABEL, anchor="middle", color=INK2)
    # legend as direct labels above the ladder
    marker("circle", px0 + 10, y0 + 62, 8, AMBER)
    text(px0 + 26, y0 + 70, "controller picks at random − Memory-only", (px0 + 20, px1), NOTE, color=AMBER)
    marker("circle", px0 + 10, y0 + 92, 8, HESP)
    text(px0 + 26, y0 + 100, "EIG/c ranking − controller picks at random", (px0 + 20, px1), NOTE, color=HESP)
    band = (py1 - py0) / len(MODELS)
    for k, (key, lab) in enumerate(MODELS):
        cy = py0 + band * (k + 0.5)
        text(px0 - 14, cy + 8, lab, (x0, px0 - 8), LABEL, 700, anchor="end")
        for dy, name, color in ((-17, "take_choice", AMBER), (17, "add_ranking", HESP)):
            v = d["v05"][key][name]
            lo_, hi_ = v["cluster_bootstrap_percentile_95"]
            line(X(lo_), cy + dy, X(hi_), cy + dy, color, 3, cap="round")
            marker("circle", X(v["difference"]), cy + dy, 9, color)
            txt = f"{v['difference']:+.2f}"
            right = X(hi_) + 12
            if right + 60 < px1:
                text(right, cy + dy + 8, txt, (right - 2, px1), NOTE, color=color)
            else:
                text(X(lo_) - 12, cy + dy + 8, txt, (px0, X(lo_) - 4), NOTE, anchor="end", color=color)


def panel_c(d, x0, y0, x1, y1):
    """Small multiples over the table source: verified (top) and tool cost (bottom)."""
    panel_title(x0, y0 + 26, "c", "Without the designer's table", x1)
    px0, px1 = x0 + 92, x1 - 92
    top0, top1 = y0 + 96, y0 + 236
    bot0, bot1 = y0 + 282, y1 - 110
    n = len(SOURCES)
    X = lambda i: px0 + (i + 0.5) * (px1 - px0) / n
    YT = lambda v: top1 - v * (top1 - top0)
    YB = lambda v: bot1 - v / 10 * (bot1 - bot0)
    y_axis(px0, top0, top1, 0, 1, [0, 0.5, 1.0], lambda t: f"{t:g}", x0 + 30, None, grid_to=px1)
    y_axis(px0, bot0, bot1, 0, 10, [0, 5, 10], lambda t: f"{t:g}", x0 + 30, None, grid_to=px1)
    text(x0 + 32, (top0 + top1) / 2, "Verified", (x0 - 200, x0 + 300), LABEL, anchor="middle", color=INK2,
         rotate=-90)
    text(x0 + 32, (bot0 + bot1) / 2, "Probe cost", (x0 - 200, x0 + 300), LABEL, anchor="middle", color=INK2,
         rotate=-90)
    text(px0 + 10, YB(10) - 8, "budget", (px0 + 6, px0 + 100), NOTE, color=MUTED, style="italic")
    # counted-table bracket
    bx0, bx1 = X(1) - 30, X(4) + 30
    line(bx0, bot1 + 58, bx1, bot1 + 58, INK2, 1.5)
    line(bx0, bot1 + 50, bx0, bot1 + 58, INK2, 1.5)
    line(bx1, bot1 + 50, bx1, bot1 + 58, INK2, 1.5)
    text((bx0 + bx1) / 2, bot1 + 86, "counted from k dev episodes", (bx0 - 20, bx1 + 20), NOTE, anchor="middle",
         color=INK2, style="italic")
    for i, (_, lab) in enumerate(SOURCES):
        tx = X(i)
        name = lab if lab.isalpha() else f"k={lab}"
        text(tx, bot1 + 32, name, (tx - (px1 - px0) / n / 2 - 14, tx + (px1 - px0) / n / 2 + 14), TICK,
             anchor="middle", color=INK2)
    for key, lab in reversed(MODELS):          # 7B (the primary endpoint) on top
        v, c = d["v06"][key]["verified"], d["v06"][key]["cost"]
        shade, mk = MODEL_SHADE[key], MODEL_MARK[key]
        for series, Yf in ((v, YT), (c, YB)):
            pts = [(X(i), Yf(series[arm])) for i, (arm, _) in enumerate(SOURCES)]
            add(f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" fill="none" stroke="{shade}" '
                f'stroke-width="2.2"/>')
            for a, b in pts:
                marker(mk, a, b, 7, shade, "#FFFFFF", 1.5)
    # direct model labels at the right end of the cost strip, spread to avoid collisions
    ends = sorted(((YB(d["v06"][k]["cost"]["hesp_eigc_guard_llmp"]), k, lab) for k, lab in MODELS))
    last = -1e9
    for y, key, lab in ends:
        y = max(y, last + 28)
        last = y
        marker(MODEL_MARK[key], X(n - 1) + 24, y, 7, MODEL_SHADE[key], "#FFFFFF", 1.5)
        text(X(n - 1) + 38, y + 8, lab, (X(n - 1) + 34, x1), NOTE, 700, color=INK2)


def panel_d(d, x0, y0, x1, y1):
    """Stacked outcome composition per model and arm."""
    panel_title(x0, y0 + 26, "d", "How investigations end", x1)
    px0, px1 = x0 + 206, x1 - 24
    top = y0 + 128
    arms = [("react_style", "ReAct"), ("memory_only", "Memory-only"), ("hesp_eigc_guard_emp20", "HESP")]
    bar, gap_arm, gap_model = 26, 8, 30
    # legend (two rows, direct swatches)
    lx, ly = x0 + 8, y0 + 64
    sx, sy = lx, ly
    for k, (_, label, color) in enumerate(OUTCOMES):
        if k == 3:
            sx, sy = lx, ly + 30
        w = 26 + len(label) * 10.2
        rect(sx, sy - 16, 18, 18, color, "#9CA3AF" if color == NONE else "none", 1 if color == NONE else 0, 2)
        if color == MISSED:
            rect(sx, sy - 16, 18, 18, "url(#hatch)", rx=2)
        text(sx + 26, sy, label, (sx + 24, sx + w), NOTE - 1, color=INK2)
        sx += w + 26
    rows_h = len(MODELS) * (3 * bar + 2 * gap_arm) + (len(MODELS) - 1) * gap_model
    for t in (0, 0.5, 1.0):
        xx = px0 + t * (px1 - px0)
        line(xx, top - 8, xx, top + rows_h + 8, AXIS if t in (0, 1.0) else GRID, 1.2)
    y = top
    for key, lab in MODELS:
        comp = d["v06"][key]["composition"]
        n = d["v06"][key]["n"]
        text(x0 + 8, y + (3 * bar + 2 * gap_arm) / 2 + 9, lab, (x0, x0 + 60), LABEL, 700)
        for arm, name in arms:
            text(px0 - 12, y + bar - 6, name, (x0 + 62, px0 - 6), NOTE, 700 if arm.startswith("hesp") else 400,
                 anchor="end", color=HESP if arm.startswith("hesp") else INK2)
            x = px0
            for cat, _, color in OUTCOMES:
                cnt = comp[arm].get(cat, 0)
                w = cnt / n * (px1 - px0)
                if cnt:
                    rect(x, y, w, bar, color)
                    if cat == "missed":
                        rect(x, y, w, bar, "url(#hatch)")
                    if w > 34:
                        if cat == "missed":         # solid backing so the count stays readable over the hatch
                            rect(x + w / 2 - 19, y + 3, 38, bar - 6, MISSED, rx=3)
                        dark = color in (NONE, UNSUPPORTED, WRONG)
                        text(x + w / 2, y + bar - 6, str(cnt), (x, x + w), NOTE - 2, anchor="middle",
                             color=INK if dark else "#FFFFFF")
                x += w
            y += bar + gap_arm
        y += gap_model - gap_arm
    text(px0, y - gap_model + 40, "0", (px0 - 20, px0 + 20), TICK, anchor="middle", color=MUTED)
    text(px1, y - gap_model + 40, "72", (px1 - 30, px1 + 30), TICK, anchor="middle", color=MUTED)
    text((px0 + px1) / 2, y - gap_model + 40, "episodes", ((px0 + px1) / 2 - 80, (px0 + px1) / 2 + 80), TICK,
         anchor="middle", color=MUTED)


def build(d):
    add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
    # hatch: "attack judged benign" must stay distinct from "verified" in greyscale
    add('<defs><pattern id="hatch" patternUnits="userSpaceOnUse" width="9" height="9" '
        'patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="9" stroke="#FFFFFF" '
        'stroke-width="3.2"/></pattern></defs>')
    add(f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>')
    mid, gap = W / 2, 32
    top_h = 500
    panel_a(d, 48, 24, mid - gap, 24 + top_h)
    panel_b(d, mid + gap, 24, W - 48, 24 + top_h)
    panel_c(d, 48, 24 + top_h + 40, mid - gap, H - 24)
    panel_d(d, mid + gap, 24 + top_h + 40, W - 48, H - 24)
    add("</svg>")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    d = gather()
    build(d)
    OUT.write_bytes(("\n".join(parts) + "\n").encode("utf-8"))
    print(OUT)
    for key, lab in MODELS:
        print(lab, "emp20-memory", round(d["v06"][key]["delta"]["difference"], 3), ci_text(d["v06"][key]["delta"]),
              "| random-memory", round(d["v05"][key]["take_choice"]["difference"], 3),
              "| eigc-random", round(d["v05"][key]["add_ranking"]["difference"], 3))
    if args.check:
        from render_figures import check_fit
        bad = check_fit(OUT)
        for b in bad:
            print("OVERFLOW:", b)
        print(f"text fit: {len(bad)} overflow(s)")
        if bad:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
