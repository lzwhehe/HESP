"""Result figures for HESP v0.3 (stdlib only; render with render_figures.py).

Fig. 2  selector ablation: verified rate vs tool budget (scripted planner, web sandbox)
Fig. 3  local-LLM pilot: verified rate (task-cluster bootstrap CI), tool cost, failure modes
Fig. 4  calibration of pre-registered predictions: KL(true || predicted) per probe x cause

Categorical colours: validated reference palette slots 1-6 (light mode). Every series
also has its own marker shape and a direct label, so identity never relies on colour.
"""

from collections import defaultdict
import json
import math
from pathlib import Path
import random
import statistics
import sys
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "hesp_research" / "results"
ASSETS = ROOT / "docs" / "assets"
SANS = "Helvetica Neue, Helvetica, Arial, sans-serif"
MONO = "Consolas, Menlo, monospace"
INK, SUB, MUTED, GRID, SURF = "#1F2937", "#52514E", "#8A8984", "#E7E6E2", "#FFFFFF"
SLOTS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7"]
MARKERS = ["circle", "square", "diamond", "triangle", "tri_down", "cross", "ring"]


class Canvas:
    def __init__(self, w, h, title):
        self.w, self.h, self.parts = w, h, []
        self.add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
                 f'role="img"><title>{escape(title)}</title><rect width="{w}" height="{h}" fill="{SURF}"/>')

    def add(self, s):
        self.parts.append(s)

    def text(self, x, y, s, size=13, weight=400, anchor="start", color=INK, family=SANS, rotate=None, style="normal"):
        rot = f' transform="rotate({rotate} {x} {y})"' if rotate else ""
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
                 f'font-style="{style}" text-anchor="{anchor}" fill="{color}"{rot}>{escape(str(s))}</text>')

    def line(self, x1, y1, x2, y2, color=GRID, sw=1, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{sw}"{d}/>')

    def rect(self, x, y, w, h, fill, rx=0, stroke="none", sw=0, opacity=1):
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w, 0):.1f}" height="{max(h, 0):.1f}" rx="{rx}" '
                 f'fill="{fill}" fill-opacity="{opacity}" stroke="{stroke}" stroke-width="{sw}"/>')

    def marker(self, kind, x, y, color, r=5):
        ring = f'stroke="{SURF}" stroke-width="2" paint-order="stroke"'
        if kind == "circle":
            self.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}" {ring}/>')
        elif kind == "square":
            self.add(f'<rect x="{x - r:.1f}" y="{y - r:.1f}" width="{2 * r}" height="{2 * r}" rx="1.5" fill="{color}" {ring}/>')
        elif kind == "diamond":
            self.add(f'<path d="M{x} {y - r * 1.3} L{x + r * 1.3} {y} L{x} {y + r * 1.3} L{x - r * 1.3} {y} Z" fill="{color}" {ring}/>')
        elif kind == "triangle":
            self.add(f'<path d="M{x} {y - r * 1.25} L{x + r * 1.2} {y + r} L{x - r * 1.2} {y + r} Z" fill="{color}" {ring}/>')
        elif kind == "tri_down":
            self.add(f'<path d="M{x} {y + r * 1.25} L{x + r * 1.2} {y - r} L{x - r * 1.2} {y - r} Z" fill="{color}" {ring}/>')
        elif kind == "ring":
            self.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{SURF}" stroke="{color}" stroke-width="2.4"/>')
        else:
            self.add(f'<path d="M{x - r} {y - r} L{x + r} {y + r} M{x + r} {y - r} L{x - r} {y + r}" stroke="{color}" stroke-width="2.6" stroke-linecap="round"/>')

    def save(self, name):
        path = ASSETS / name
        path.write_text("\n".join(self.parts + ["</svg>"]), encoding="utf-8")
        print(path)


def axes(c, x0, y0, w, h, yticks, ylab, fmt=lambda v: f"{v:.1f}", xlab=None, xticks=None, xmap=None):
    """Recessive grid + axes; returns y-mapper."""
    lo, hi = yticks[0], yticks[-1]
    ymap = lambda v: y0 + h - (v - lo) / (hi - lo) * h
    for t in yticks:
        c.line(x0, ymap(t), x0 + w, ymap(t), GRID, 1)
        c.text(x0 - 8, ymap(t) + 4, fmt(t), 11.5, 400, "end", SUB)
    c.line(x0, y0 + h, x0 + w, y0 + h, "#BDBBB5", 1.2)
    if xticks and xmap:
        for t in xticks:
            c.line(xmap(t), y0 + h, xmap(t), y0 + h + 4, "#BDBBB5", 1.2)
            c.text(xmap(t), y0 + h + 18, t, 11.5, 400, "middle", SUB)
    if xlab:
        c.text(x0 + w / 2, y0 + h + 38, xlab, 12.5, 500, "middle", SUB)
    c.text(x0 - 44, y0 + h / 2, ylab, 12.5, 500, "middle", SUB, rotate=-90)
    return ymap


# --------------------------------------------------------------------- Fig. 2
ABL_LABELS = {"sequential": "sequential (B)", "eig_cost": "EIG / cost (C)", "eig": "EIG only",
              "map_greedy": "MAP-greedy", "random": "random legal", "eig_cost_llmP": "EIG / cost, LLM-P",
              "lookahead": "lookahead (budget-aware)"}


def fig_ablation():
    folder = RES / "web_ablation_v031" if (RES / "web_ablation_v031").exists() else RES / "web_ablation_v03"
    data = json.loads((folder / "curve.json").read_text(encoding="utf-8"))
    budgets, arms, curve = data["budgets"], data["arms"], data["curve"]
    # Colour follows the entity (fixed slot per arm), never its rank or presence.
    order = ["eig_cost", "sequential", "eig", "map_greedy", "random", "eig_cost_llmP", "lookahead"]
    color = {a: SLOTS[i] for i, a in enumerate(order)}
    mark = {a: MARKERS[i] for i, a in enumerate(order)}
    arms = [a for a in order if a in arms]
    c = Canvas(1480, 430, "Selector ablation: verified rate versus tool budget")
    panels = [("overall", "All 24 tasks"), ("base", "base"), ("drift", "drift (state change)"), ("noise", "noise (503s, audit lag)")]
    pw, ph, gap, top = 300, 260, 60, 92
    # legend row
    lx = 70
    for a in arms:
        c.line(lx, 30, lx + 26, 30, color[a], 2.4)
        c.marker(mark[a], lx + 13, 30, color[a], 4.5)
        c.text(lx + 34, 34.5, ABL_LABELS[a], 12.5, 600 if a in ("eig_cost", "lookahead") else 400, color=INK)
        lx += 40 + len(ABL_LABELS[a]) * 6.9
    c.text(70, 62, f"Model-free planner (finish at posterior ≥ 0.9); only the probe-selection rule differs.  "
                   f"{data['repeats']} seeded repeats per task; failures stay in the denominator.", 12, 400, color=SUB, style="italic")
    for pi, (key, title) in enumerate(panels):
        x0 = 76 + pi * (pw + gap)
        xmap = lambda b, x0=x0: x0 + (budgets.index(b) / (len(budgets) - 1)) * pw
        ymap = axes(c, x0, top, pw, ph, [0, .25, .5, .75, 1.0], "verified rate" if pi == 0 else "",
                    fmt=lambda v: f"{v:.2f}", xlab="tool-cost budget", xticks=budgets, xmap=xmap)
        c.text(x0, top - 12, f"({'abcd'[pi]}) {title}", 13.5, 700)
        for a in arms:
            vals = [(curve[str(b)]["overall"][a] if key == "overall" else curve[str(b)]["by_variant"][key][a])
                    for b in budgets]
            pts = " ".join(f"{xmap(b):.1f},{ymap(v):.1f}" for b, v in zip(budgets, vals))
            sw = 2.6 if a in ("eig_cost", "lookahead") else 1.8
            c.add(f'<polyline points="{pts}" fill="none" stroke="{color[a]}" stroke-width="{sw}" '
                  f'stroke-linejoin="round" stroke-linecap="round"/>')
            for b, v in zip(budgets, vals):
                c.marker(mark[a], xmap(b), ymap(v), color[a], 4.2)
    c.save("fig-ablation-budget.svg")


# --------------------------------------------------------------------- Fig. 3
PILOT_LABELS = {"react_style": "A · ReAct-style", "memory_only": "B · Memory-only", "hesp": "C · HESP (EIG/c)",
                "hesp_llm_pred": "C · HESP, LLM-P", "hesp_random": "C · random picks"}


def cluster_ci(rows, arm, key=lambda r: float(r["verified_simulation"]), samples=4000, seed=7):
    per = defaultdict(list)
    for r in rows:
        if r["arm"] == arm:
            per[r["task_id"]].append(key(r))
    means = [statistics.mean(v) for v in per.values()]
    rng = random.Random(seed)
    draws = sorted(statistics.mean(rng.choices(means, k=len(means))) for _ in range(samples))
    return statistics.mean(means), draws[int(.025 * (samples - 1))], draws[int(.975 * (samples - 1))]


def fig_pilot():
    base = RES / "llm_pilot_v03"
    rows = [json.loads(l) for l in (base / "outcomes.jsonl").read_text(encoding="utf-8").splitlines()]
    manifest = json.loads((base / "manifest.json").read_text(encoding="utf-8"))
    arms = [a for a in PILOT_LABELS if a in {r["arm"] for r in rows}]
    color = {a: SLOTS[i] for i, a in enumerate(["hesp", "memory_only", "react_style", "hesp_llm_pred", "hesp_random"])}
    mark = {a: MARKERS[i] for i, a in enumerate(["hesp", "memory_only", "react_style", "hesp_llm_pred", "hesp_random"])}
    c = Canvas(1480, 470, "Local-LLM pilot results")
    model = manifest["model"]
    c.text(40, 30, f"Planner: {model['model']} ({model['parameter_size']}, {model['quantization']}), local, T = "
                   f"{manifest['temperature']}.  24 sandbox tasks × {manifest['repeats']} repeats × {len(arms)} arms, "
                   f"paired and shuffled.  Whiskers: 95% bootstrap over task clusters.", 12.5, 400, color=SUB, style="italic")
    rowh, top, lab_w = 58, 110, 150

    def dot_panel(x0, title, key, lo, hi, ticks, fmt, xlab):
        w = 250
        xmap = lambda v: x0 + lab_w + (v - lo) / (hi - lo) * w
        c.text(x0, top - 40, title, 13.5, 700)
        for t in ticks:
            c.line(xmap(t), top - 16, xmap(t), top + rowh * len(arms) - 16, GRID, 1)
            c.text(xmap(t), top + rowh * len(arms) + 4, fmt(t), 11.5, 400, "middle", SUB)
        c.text(x0 + lab_w + w / 2, top + rowh * len(arms) + 26, xlab, 12.5, 500, "middle", SUB)
        for i, a in enumerate(arms):
            y = top + i * rowh + 8
            c.text(x0 + lab_w - 12, y + 4.5, PILOT_LABELS[a], 12.5, 600 if a == "hesp" else 400, "end", INK)
            m, l, h = cluster_ci(rows, a, key)
            c.line(xmap(l), y, xmap(h), y, color[a], 2.2)
            c.line(xmap(l), y - 5, xmap(l), y + 5, color[a], 2.2)
            c.line(xmap(h), y - 5, xmap(h), y + 5, color[a], 2.2)
            c.marker(mark[a], xmap(m), y, color[a], 6)
            c.text(xmap(m), y - 11, fmt(m) if not isinstance(fmt(m), str) else fmt(m), 11.5, 600, "middle", INK)

    dot_panel(30, "(a) Verified completion", lambda r: float(r["verified_simulation"]), 0, 1,
              [0, .25, .5, .75, 1], lambda v: f"{v:.2f}", "verified rate")
    dot_panel(510, "(b) Tool cost per episode", lambda r: float(r["tool_cost_units"]), 0, 10,
              [0, 2.5, 5, 7.5, 10], lambda v: f"{v:.1f}", "cost units (budget 10)")
    # (c) failure modes: stacked horizontal bars of status shares
    x0, w = 990, 300
    c.text(x0, top - 40, "(c) Episode outcome", 13.5, 700)
    # Neutral ramp for outcome types so no series colour is reused with a different meaning;
    # only the "wrong claim" failure gets an accent.
    statuses = [("VERIFIED_SIMULATION", "verified", "#374151"), ("UNVERIFIED_CLAIM", "wrong claim", "#e34948"),
                ("DECISION_BUDGET_EXCEEDED", "decision budget (loops)", "#9CA3AF"),
                ("TOOL_BUDGET_EXCEEDED", "tool budget", "#C9CDD3"), ("OTHER", "other stop / error", "#E5E7EB")]
    for i, a in enumerate(arms):
        y = top + i * rowh
        c.text(x0 + lab_w - 12, y + 12.5, PILOT_LABELS[a], 12.5, 600 if a == "hesp" else 400, "end", INK)
        mine = [r for r in rows if r["arm"] == a]
        xx = x0 + lab_w
        for code, _, col in statuses:
            n = sum(1 for r in mine if (r["status"] == code) or (code == "OTHER" and r["status"] not in
                                                                   {s[0] for s in statuses}))
            seg = w * n / len(mine)
            if seg > 0:
                c.rect(xx, y, seg - 2, 17, col, 3)
                if seg > 26:
                    c.text(xx + seg / 2 - 1, y + 12.5, n, 11, 700, "middle", "#FFFFFF" if col in ("#374151", "#e34948") else INK)
            xx += seg
    lx, ly = x0 + lab_w, top + rowh * len(arms) + 6
    for i, (_, name, col) in enumerate(statuses):
        xx, yy = lx + (i % 2) * 170, ly + (i // 2) * 20
        c.rect(xx, yy - 10, 12, 12, col, 2)
        c.text(xx + 18, yy, name, 11.5, 400, color=SUB)
    c.save("fig-llm-pilot.svg")


# --------------------------------------------------------------------- Fig. 4
def fig_calibration():
    sys.path.insert(0, str(ROOT / "hesp_research"))
    from hesp.webapp import HYPOTHESES, PROBES, catalog, true_outcome_distribution
    e = json.loads((RES / "elicitation_v03" / "elicitation.json").read_text(encoding="utf-8"))
    tables = {"Designer table": {a.id: a.likelihoods for a in catalog()}, f"LLM-elicited ({e['model']['model']})": e["tables"]}
    probes = [p["id"] for p in PROBES]
    c = Canvas(1100, 560, "Calibration of pre-registered predictions")
    cell, x_start, top = 36, 160, 100
    ramp = ["#F3F7FC", "#D5E3F6", "#A9C6EE", "#6FA1E2", "#2a78d6", "#1B4F91"]   # single-hue sequential
    edges = [0.05, 0.25, 1, 2, 4]

    def shade(v):
        for i, e_ in enumerate(edges):
            if v < e_:
                return ramp[i]
        return ramp[-1]

    for ti, (name, tab) in enumerate(tables.items()):
        x0 = x_start + ti * (cell * len(probes) + 90)
        kl_all = []
        c.text(x0, top - 50, f"({'ab'[ti]}) {name}", 13.5, 700)
        for j, p in enumerate(probes):
            c.text(x0 + j * cell + cell / 2, top - 10, p.replace("_", " ")[:9], 10.5, 500, "start", SUB, MONO, rotate=-35)
        for i, h in enumerate(HYPOTHESES):
            if ti == 0:
                c.text(x0 - 10, top + i * cell + cell / 2 + 4, h.replace("_", " "), 12, 400, "end", INK)
            for j, p in enumerate(probes):
                q = true_outcome_distribution(p, h, 0.10)
                pr = tab[p][h]
                kl = sum(qo * math.log2(qo / max(pr.get(o, 0), 1e-12)) for o, qo in q.items() if qo > 0)
                kl_all.append(kl)
                c.rect(x0 + j * cell + 1, top + i * cell + 1, cell - 2, cell - 2, shade(kl), 3)
                if kl >= 1:
                    c.text(x0 + j * cell + cell / 2, top + i * cell + cell / 2 + 4, f"{kl:.1f}", 10, 600, "middle",
                           "#FFFFFF" if kl >= 2 else INK)
        cal = e["calibration_vs_true_model"]["base"]["designer_table" if ti == 0 else "llm"]
        c.text(x0, top + len(HYPOTHESES) * cell + 24,
               f"mean KL {cal['kl_bits']:.2f} bits · Brier {cal['expected_brier']:.3f} · "
               f"argmax agreement {cal['argmax_agreement']:.2f}", 12.5, 600, color=INK)
    # legend for the ramp
    lx, ly = x_start, top + len(HYPOTHESES) * cell + 52
    c.text(lx, ly + 11, "KL(true ‖ predicted), bits:", 12, 500, color=SUB)
    labels = ["<0.05", "0.05–0.25", "0.25–1", "1–2", "2–4", "≥4"]
    for i, (col, lab) in enumerate(zip(ramp, labels)):
        xx = lx + 175 + i * 96
        c.rect(xx, ly, 22, 14, col, 2, "#D5D3CC", .8)
        c.text(xx + 28, ly + 11.5, lab, 11.5, 400, color=SUB)
    c.text(lx, ly + 36, "Rows: true cause h. Columns: probe a. Truth = sandbox generator (base variant). "
                        f"LLM rows elicited one call per (h, a), schema-constrained, T = 0, ε = {e['eps_floor']}.",
           12, 400, color=SUB, style="italic")
    c.save("fig-calibration.svg")


if __name__ == "__main__":
    which = set(sys.argv[1:]) or {"ablation", "pilot", "calibration"}
    if "ablation" in which:
        fig_ablation()
    if "calibration" in which:
        fig_calibration()
    if "pilot" in which:
        fig_pilot()
