"""HESP framework figure (paper mechanism figure, formal-roman preset).

Output: docs/assets/hesp-framework.svg. Render to PDF/PNG with
    python docs/figures/render_figures.py docs/assets/hesp-framework.svg

Every number in the figure is computed here from the code, not typed in: the script
replays one real sec-triage episode (task sec-base-00, hidden cause credential_stuffing)
with the non-oracle table counted from 20 development episodes per (cause, variant)
(results/v06_tables/empirical_20.json), the EIG/cost selector, and the finish guard. The
posterior values, the t=0 ranking, the planner's overridden proposal, the executed probe
and its outcome all come from that episode's journal.

Design: 7.0 in final width on a 1536 px canvas (1 pt = 3.048 px); Times New Roman for text,
Consolas only for code identifiers. Blue = the HESP controller (the contribution), red =
the trust boundary the planner cannot see, neutral = the LLM planner and the inputs.
Every text element records the box it must fit in; ``--check`` measures the rendered text
in headless Chrome (the same renderer as the PDF/PNG) and fails on any overflow.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[2]
CODE = ROOT / "hesp_research"
sys.path.insert(0, str(CODE))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from hesp.controller import Budget, run                      # noqa: E402
from hesp.planner import PosteriorPlanner                    # noqa: E402
from hesp.predictors import FrozenPredictor                  # noqa: E402
from hesp.secapp import HYPOTHESES, SecTriageEnvironment, make_sec_env, sec_suite   # noqa: E402
from hesp.selectors import Selector                          # noqa: E402
from hesp.study import cell_seed                             # noqa: E402
from render_figures import browser                           # noqa: E402

OUT = ROOT / "docs" / "assets" / "hesp-framework.svg"
W, H = 1536, 752
SERIF = "'Times New Roman', Times, serif"
MONO = "Consolas, 'DejaVu Sans Mono', monospace"
# ccfa_ink roles
INK, INK2, MUTED, RULE = "#111827", "#374151", "#6B7280", "#9CA3AF"
BLUE, BLUE_TINT, BLUE_EDGE = "#1D4ED8", "#EEF3FD", "#C9D8F7"
RED, RED_TINT = "#BE123C", "#FDF2F4"
GREEN = "#059669"
# type scale at 7.0 in (pt x 3.048 px): headings 10.2 pt, labels 8.2 pt, secondary >= 7.5 pt,
# code identifiers 7.2 pt (Consolas has a larger x-height than Times at the same size)
H1, LABEL, CODE_PX = 31, 25, 22
PAD = 16

TASK_ID, REPEAT, SEED = "sec-base-00", 1, 2026
TABLE = CODE / "results" / "v06_tables" / "empirical_20.json"


# ---------------------------------------------------------------- episode replay
def replay():
    tables = json.loads(TABLE.read_text(encoding="utf-8"))["tables"]
    task = next(t for t in sec_suite() if t["task_id"] == TASK_ID)
    seed = cell_seed(SEED, TASK_ID, REPEAT)
    with tempfile.TemporaryDirectory() as tmp:
        with make_sec_env(task, seed) as env:
            result = run(env, PosteriorPlanner(), "hesp", Path(tmp) / "r", Budget(10, 12, 10, 900),
                         predictor=FrozenPredictor(tables, "empirical_20"), selector=Selector("eig_cost", seed),
                         finish_guard=True)
        with (Path(tmp) / "r" / "events.jsonl").open(encoding="utf-8") as stream:
            events = [json.loads(line) for line in stream]
    requests = [e["request"] for e in events if e["kind"] == "planner_request"]
    decisions = [e["decision"] for e in events if e["kind"] == "planner_decision"]
    executed = [e["action"]["id"] for e in events if e["kind"] == "prediction_registered"]
    observations = [e["observation"] for e in events if e["kind"] == "observation"]
    posteriors = [{h["id"]: h["score"] for h in r["investigation"]["hypotheses"]} for r in requests]
    assert result["verified_simulation"] and result["claimed_hypothesis"] == task["cause"]
    assert decisions[0]["kind"] == "action" and decisions[0]["action_id"] != executed[0], \
        "the figure shows the planner's proposal being overridden; the replay no longer shows that"
    return {"task": task, "result": result, "rank0": requests[0]["action_rankings"],
            "proposed0": decisions[0]["action_id"], "executed": executed, "obs": observations,
            "post": posteriors}


# ---------------------------------------------------------------- svg helpers
parts = []


def add(s):
    parts.append(s)


def rect(x0, y0, x1, y1, fill="#FFFFFF", stroke=RULE, sw=1.5, rx=4, dash=None, opacity=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' fill-opacity="{opacity:.3f}"' if opacity is not None else ""
    add(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="{rx}" fill="{fill}"{o} '
        f'stroke="{stroke}" stroke-width="{sw}"{d}/>')


def text(x, y, content, fit, size=LABEL, weight=400, anchor="start", color=INK, family=SERIF,
         style="normal", raw=False):
    """``fit`` = (x0, x1) that the rendered text must stay inside (checked by --check)."""
    body = content if raw else escape(content)
    add(f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
        f'font-style="{style}" fill="{color}" text-anchor="{anchor}" data-fit="{fit[0]},{fit[1]}">{body}</text>')


def i(s):
    """Italic math variable."""
    return f'<tspan font-style="italic">{escape(s)}</tspan>'


def sub(base, index, size):
    return (f'{i(base)}<tspan baseline-shift="sub" font-size="{round(size * 0.68)}">{escape(index)}</tspan>')


def path(points, color=INK2, sw=2.0, dash=None, marker="ink"):
    d = " ".join(f"{'M' if k == 0 else 'L'}{x},{y}" for k, (x, y) in enumerate(points))
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}"{dd} marker-end="url(#arrow-{marker})" '
        f'stroke-linejoin="round"/>')


def defs():
    add("<defs>")
    for name, color in (("ink", INK2), ("blue", BLUE), ("red", RED), ("green", GREEN), ("muted", MUTED)):
        add(f'<marker id="arrow-{name}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6.5" '
            f'markerHeight="6.5" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{color}"/></marker>')
    add("</defs>")


def prob(p):
    """Two decimals without the leading zero; values below .01 keep three."""
    return f"{p:.3f}"[1:] if p < 0.01 else f"{p:.2f}"[1:]


# ---------------------------------------------------------------- figure
def build(ep):
    add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
    defs()
    add(f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>')

    # anchors: three columns (inputs | HESP controller | trust boundary), three rows
    A0, A1 = 48, 368                      # inputs
    C0, C1 = 400, 1164                    # controller tint; lane C0..B0 carries the update edge
    B0, B1 = 424, 1140                    # controller boxes
    PI1, GD0 = 700, 860                   # planner right edge, guard left edge (gap holds typed edges)
    POST1, SEL0 = 842, 866                # posterior | selector
    T0, T1 = 1194, 1488                   # trust boundary
    TB0, TB1 = 1210, 1472                 # trust boxes
    R0, R1 = 48, 196                      # decision row
    L0, L1 = 232, 448                     # posterior / selector row
    P0, P1 = 472, 556                     # predictive model
    E0, E1 = 580, 690                     # evidence ledger
    GBOT = 726                            # bottom of both containers

    # containers: the controller tint wraps the loop and reaches up around the guard
    add(f'<path d="M{C0},{L0 - 12} L{GD0 - 12},{L0 - 12} L{GD0 - 12},36 L{C1},36 L{C1},{GBOT} '
        f'L{C0},{GBOT} Z" fill="{BLUE_TINT}" stroke="{BLUE_EDGE}" stroke-width="1.5"/>')
    rect(T0, 36, T1, GBOT, fill=RED_TINT, stroke=RED, sw=1.6, rx=6, dash="7 5")
    text(C0 + 14, GBOT - 12, "HESP controller", (C0, C1), LABEL, 700, color=BLUE)
    text(T0 + 16, GBOT - 12, "Hidden from π", (T0, T1), LABEL, color=RED, style="italic")

    # ---- inputs
    rect(A0, R0, A1, R1, stroke=INK2)
    fa = (A0 + PAD, A1 - PAD)
    text(A0 + PAD, R0 + 36, "Alert τ", fa, H1, 700)
    text(A1 - PAD, R0 + 36, SecTriageEnvironment.STATE_FIELDS["case"], fa, CODE_PX, family=MONO,
         color=MUTED, anchor="end")
    for k, s in enumerate(("Spike in auth failures", "and 4xx/5xx errors on", "the web tier, last hour")):
        text(A0 + PAD, R0 + 74 + k * 30, s, fa, LABEL, color=INK2)

    rect(A0, L0, A1, E1, stroke=INK2)
    add(f'<text x="{A0 + PAD}" y="{L0 + 36}" font-family="{SERIF}" font-size="{H1}" font-weight="700" fill="{INK}" '
        f'data-fit="{fa[0]},{fa[1]}">Hypotheses {i("H")}</text>')
    cause = ep["task"]["cause"]
    for k, h in enumerate(HYPOTHESES):
        strong = h == cause
        text(A0 + PAD, L0 + 78 + k * 36, h, fa, CODE_PX, 700 if strong else 400, family=MONO,
             color=INK if strong else INK2)
    text(A0 + PAD, E1 - 44, f"uniform prior 1/{len(HYPOTHESES)};", fa, LABEL - 2, color=MUTED, style="italic")
    text(A0 + PAD, E1 - 16, "other = unknown cause", fa, LABEL - 2, color=MUTED, style="italic")

    # ---- LLM planner (neutral: consulted, not the contribution)
    rect(B0, R0, PI1, R1, stroke=INK, sw=1.8)
    fp = (B0 + PAD, PI1 - PAD)
    text(B0 + PAD, R0 + 36, "LLM planner π", fp, H1, 700)
    text(B0 + PAD, R0 + 74, "Qwen2.5 7B–72B, local", fp, LABEL, color=INK2, style="italic")
    text(B0 + PAD, R0 + 104, "one decision per step", fp, LABEL - 2, color=INK2)
    add(f'<text x="{B0 + PAD}" y="{R0 + 134}" font-family="{MONO}" font-size="{CODE_PX}" fill="{INK2}" '
        f'data-fit="{fp[0]},{fp[1]}">stop <tspan font-family="{SERIF}" font-size="{LABEL - 2}">→ unresolved</tspan></text>')

    # ---- finish guard (part of the controller)
    rect(GD0, R0, B1, R1, stroke=BLUE, sw=1.8)
    fg = (GD0 + PAD, B1 - PAD)
    text(GD0 + PAD, R0 + 36, "Finish guard", fg, H1, 700, color=BLUE)
    text(GD0 + PAD, R0 + 72, "cites current-state", fg, LABEL, color=INK2)
    text(GD0 + PAD, R0 + 100, "evidence for ĥ and", fg, LABEL, color=INK2)
    add(f'<text x="{GD0 + PAD}" y="{R0 + 130}" font-family="{SERIF}" font-size="{LABEL}" fill="{INK2}" '
        f'data-fit="{fg[0]},{fg[1]}">{sub("p", "t", LABEL)}({i("ĥ")}) ≥ 0.8</text>')

    # ---- verifier (inside the trust boundary)
    rect(TB0, R0, TB1, R1, stroke=RED, sw=1.8)
    fv = (TB0 + PAD, TB1 - PAD)
    add(f'<text x="{TB0 + PAD}" y="{R0 + 36}" font-family="{SERIF}" font-size="{H1}" font-weight="700" '
        f'fill="{RED}" data-fit="{fv[0]},{fv[1]}">Verifier {i("V")}</text>')
    add(f'<text x="{TB0 + PAD}" y="{R0 + 72}" font-family="{SERIF}" font-size="{LABEL}" fill="{INK2}" '
        f'data-fit="{fv[0]},{fv[1]}">pass iff {i("ĥ")} = {i("h")}* and</text>')
    add(f'<text x="{TB0 + PAD}" y="{R0 + 100}" font-family="{SERIF}" font-size="{LABEL}" fill="{INK2}" '
        f'data-fit="{fv[0]},{fv[1]}">{i("E")} has {i("h")}*’s signature</text>')
    add(f'<path d="M{TB0 + PAD},{R0 + 122} l7,8 l14,-17" fill="none" stroke="{GREEN}" stroke-width="3" '
        f'stroke-linecap="round" stroke-linejoin="round"/>')
    text(TB0 + PAD + 30, R0 + 132, "verified", fv, LABEL, 700, color=GREEN)

    # ---- posterior (values from the replayed episode)
    rect(B0, L0, POST1, L1, stroke=BLUE)
    fq = (B0 + PAD, POST1 - PAD)
    add(f'<text x="{B0 + PAD}" y="{L0 + 36}" font-family="{SERIF}" font-size="{H1}" font-weight="700" '
        f'fill="{BLUE}" data-fit="{fq[0]},{fq[1]}">Posterior {sub("p", "t", H1)}({i("h")})</text>')
    post = ep["post"]
    others = [h for h in HYPOTHESES if h not in (cause, "other")]
    rows = [(cause, [p[cause] for p in post], True),
            ("other", [p["other"] for p in post], False),
            (f"{len(others)} other causes, max", [max(p[h] for h in others) for p in post], False)]
    cw = 50
    cx0 = POST1 - PAD - cw * len(post)
    text(cx0 - 10, L0 + 76, "t =", (cx0 - 60, cx0 - 4), LABEL - 2, anchor="end", color=MUTED, style="italic")
    for j in range(len(post)):
        text(cx0 + j * cw + cw / 2, L0 + 76, str(j), (cx0 + j * cw, cx0 + (j + 1) * cw), LABEL - 2,
             anchor="middle", color=MUTED)
    for k, (name, vals, strong) in enumerate(rows):
        y = L0 + 114 + k * 38
        code = not name[0].isdigit()
        text(B0 + PAD, y, name, (B0 + PAD, cx0 - 6), CODE_PX if code else LABEL - 2, 700 if strong else 400,
             family=MONO if code else SERIF, color=INK if strong else INK2, style="normal" if code else "italic")
        for j, v in enumerate(vals):
            x = cx0 + j * cw
            rect(x + 3, y - 23, x + cw - 3, y + 8, fill=BLUE, stroke="none", sw=0, rx=3, opacity=0.08 + 0.82 * v)
            text(x + cw / 2, y, prob(v), (x, x + cw), LABEL - 2, 700 if strong and j == len(vals) - 1 else 400,
                 anchor="middle", color="#FFFFFF" if v > 0.55 else INK)

    # ---- EIG / cost selector (ranking at t = 0, values from the replayed episode)
    rect(SEL0, L0, B1, L1, stroke=BLUE)
    fs = (SEL0 + PAD, B1 - PAD)
    text(SEL0 + PAD, L0 + 36, "Probe selector", fs, H1, 700, color=BLUE)
    add(f'<text x="{SEL0 + PAD}" y="{L0 + 70}" font-family="{SERIF}" font-size="{LABEL - 2}" fill="{INK2}" '
        f'data-fit="{fs[0]},{B1 - 80}">argmax EIG/{i("c")}</text>')
    text(B1 - PAD, L0 + 70, "t = 0", (B1 - 60, B1 - PAD), LABEL - 2, anchor="end", color=MUTED, style="italic")
    ranking = ep["rank0"]
    shown = ranking[:3]
    if ep["proposed0"] not in [r["action_id"] for r in shown]:
        shown.append(next(r for r in ranking if r["action_id"] == ep["proposed0"]))
    for k, r in enumerate(shown):
        y = L0 + 102 + k * 32
        ran = r["action_id"] == ep["executed"][0]
        proposed = r["action_id"] == ep["proposed0"]
        if ran:
            rect(SEL0 + 8, y - 23, B1 - 8, y + 8, fill=BLUE, stroke="none", sw=0, rx=3, opacity=0.14)
        if proposed:
            rect(SEL0 + 8, y - 23, B1 - 8, y + 8, fill="none", stroke=MUTED, sw=1.3, rx=3, dash="4 3")
        text(SEL0 + PAD, y, r["action_id"], (SEL0 + PAD, B1 - 84), CODE_PX, 700 if ran else 400, family=MONO,
             color=BLUE if ran else INK2)
        text(B1 - 40, y, f"{r['score']:.2f}", (B1 - 84, B1 - 38), LABEL - 2, 700 if ran else 400, anchor="end",
             color=BLUE if ran else INK2)
        if ran:
            run_y = y - 8
        if proposed:
            text(B1 - 22, y, "π", (B1 - 38, B1 - 8), LABEL - 2, anchor="middle", color=MUTED, style="italic")

    # ---- predictive model, shared by the selector and the ledger
    rect(B0, P0, B1, P1, stroke=BLUE)
    fm = (B0 + PAD, B1 - PAD)
    add(f'<text x="{B0 + PAD}" y="{P0 + 34}" font-family="{SERIF}" font-size="{H1}" font-weight="700" '
        f'fill="{BLUE}" data-fit="{fm[0]},{fm[1]}">Predictive model {i("P")}({i("o")} | {i("h")}, {i("a")})</text>')
    x = B0 + PAD
    for label, used in (("designer (oracle)", False), ("counted, k dev episodes", True), ("LLM-elicited", False)):
        w = len(label) * 10.6 + 26
        rect(x, P0 + 48, x + w, P0 + 76, stroke=BLUE if used else RULE, sw=1.8 if used else 1.2, rx=14)
        text(x + w / 2, P0 + 69, label, (x, x + w), LABEL - 3, 700 if used else 400, anchor="middle",
             color=BLUE if used else INK2)
        x += w + 12

    # ---- evidence ledger
    rect(B0, E0, B1, E1, stroke=BLUE)
    fe = (B0 + PAD, B1 - PAD)
    text(B0 + PAD, E0 + 36, "Evidence ledger", fe, H1, 700, color=BLUE)
    add(f'<text x="{B0 + 262}" y="{E0 + 36}" font-family="{SERIF}" font-size="{LABEL + 1}" fill="{INK}" '
        f'data-fit="{B0 + 262},{fe[1]}">{sub("p", "t+1", LABEL + 1)}({i("h")}) ∝ {sub("p", "t", LABEL + 1)}'
        f'({i("h")}) · {i("P")}({sub("o", "t", LABEL + 1)} | {i("h")}, {sub("a", "t", LABEL + 1)})</text>')
    text(B0 + PAD, E0 + 72, "skips duplicate, stale-state and transient observations;", fe, LABEL - 2, color=INK2)
    add(f'<text x="{B0 + PAD}" y="{E0 + 98}" font-family="{SERIF}" font-size="{LABEL - 2}" fill="{MUTED}" '
        f'font-style="italic" data-fit="{fe[0]},{fe[1]}">a change of state version {sub("s", "t", LABEL - 2)} '
        f'resets current scores, keeps history</text>')

    # ---- sandbox (inside the trust boundary)
    rect(TB0, L0, TB1, E1, stroke=RED)
    text(TB0 + PAD, L0 + 36, "Loopback app", fv, H1, 700, color=RED)
    text(TB0 + PAD, L0 + 70, "127.0.0.1, read-only", fv, LABEL - 2, color=MUTED, style="italic")
    first = ep["obs"][0]
    probe = SecTriageEnvironment.probe_by_id()[first["action_id"]]
    route = probe["path"].split("?")
    text(TB0 + PAD, L0 + 116, f"{probe['method']} {route[0]}", fv, CODE_PX, family=MONO)
    if len(route) > 1:
        text(TB0 + PAD, L0 + 144, f"    ?{route[1]}", fv, CODE_PX, family=MONO, color=INK2)
    text(TB0 + PAD, L0 + 186, "→ outcome class", fv, LABEL - 2, color=MUTED, style="italic")
    text(TB0 + PAD, L0 + 216, first["outcome"], fv, CODE_PX, 700, family=MONO)
    costs = sorted({p["cost"] for p in SecTriageEnvironment.PROBES})
    text(TB0 + PAD, L0 + 272, f"{len(SecTriageEnvironment.PROBES)} probes, cost {costs[0]}–{costs[-1]}", fv,
         LABEL - 2, color=INK2)
    text(TB0 + PAD, L0 + 302, "reset per episode", fv, LABEL - 2, color=INK2)
    add(f'<text x="{TB0 + PAD}" y="{L0 + 332}" font-family="{SERIF}" font-size="{LABEL - 2}" fill="{INK2}" '
        f'data-fit="{fv[0]},{fv[1]}">versioned state {sub("s", "t", LABEL - 2)}</text>')
    add(f'<text x="{TB0 + PAD}" y="{L0 + 380}" font-family="{SERIF}" font-size="{LABEL}" fill="{RED}" '
        f'data-fit="{fv[0]},{fv[1]}">hidden cause {i("h")}*</text>')

    # ---- typed connections
    gap = (PI1 + 4, GD0 - 4)
    path([(A1, 110), (B0, 110)])                                                    # alert -> planner
    path([(A1, 300), (B0, 300)], color=BLUE, marker="blue")                         # H -> posterior
    path([(500, L0), (500, R1)])                                                    # state -> planner
    text(512, R1 + 26, "ledger, rankings", (506, 682), LABEL - 1, color=MUTED, style="italic")
    path([(PI1, 96), (GD0, 96)], sw=2.2)                                            # finish -> guard
    text((PI1 + GD0) / 2, 84, "finish(ĥ, E)", gap, CODE_PX, anchor="middle", family=MONO)
    path([(GD0, 124), (PI1, 124)], color=MUTED, dash="5 4", marker="muted")         # rejection reason
    text((PI1 + GD0) / 2, 150, "rejection", gap, LABEL - 1, anchor="middle", color=MUTED, style="italic")
    path([(690, R1), (690, 208), (906, 208), (906, L0)], color=MUTED, dash="5 4", marker="muted")   # advisory
    text(PI1 + 8, 200, "action a", (PI1 + 4, GD0 - 4), CODE_PX, family=MONO, color=MUTED)
    path([(B1, 96), (TB0, 96)], color=GREEN, sw=2.4, marker="green")                # guard -> verifier
    path([(POST1, 340), (SEL0, 340)], color=BLUE, sw=2.6, marker="blue")            # posterior -> selector
    path([(B1 - 8, run_y), (TB0, run_y)], color=BLUE, sw=2.6, marker="blue")       # a_t leaves the executed row
    add(f'<text x="{(B1 + TB0) / 2}" y="{run_y - 10}" font-family="{SERIF}" font-size="{LABEL}" fill="{BLUE}" '
        f'text-anchor="middle" data-fit="{B1},{TB0}">{sub("a", "t", LABEL)}</text>')
    path([(TB0, 640), (B1, 640)], color=BLUE, sw=2.6, marker="blue")                # o_t -> ledger
    add(f'<text x="{(B1 + TB0) / 2}" y="630" font-family="{SERIF}" font-size="{LABEL}" fill="{BLUE}" '
        f'text-anchor="middle" data-fit="{B1},{TB0}">{sub("o", "t", LABEL)}</text>')
    path([(B0, 660), (412, 660), (412, 420), (B0, 420)], color=BLUE, sw=2.6, marker="blue")   # ledger -> posterior
    path([(1000, P0), (1000, L1)], color=BLUE, sw=1.6, marker="blue")               # P -> selector
    path([(1000, P1), (1000, E0)], color=BLUE, sw=1.6, marker="blue")               # P -> ledger
    mid = (TB0 + TB1) / 2
    path([(mid, L0), (mid, R1)], color=RED, sw=1.6, dash="3 3", marker="red")       # h* -> verifier
    add(f'<text x="{mid + 10}" y="{R1 + 26}" font-family="{SERIF}" font-size="{LABEL - 1}" fill="{RED}" '
        f'data-fit="{mid},{TB1}">{i("h")}*</text>')
    add("</svg>")


# ---------------------------------------------------------------- render QA
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
    """Measure every rendered text element in headless Chrome; return the overflowing ones."""
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


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="fail if any text overflows its box")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    ep = replay()
    build(ep)
    OUT.write_bytes(("\n".join(parts) + "\n").encode("utf-8"))
    print(OUT)
    print("replayed:", TASK_ID, "->", ep["result"]["claimed_hypothesis"],
          "| t=0 proposed", ep["proposed0"], "executed", ep["executed"][0],
          "| posterior of cause", [round(p[ep["task"]["cause"]], 3) for p in ep["post"]])
    if args.check:
        bad = check_fit(OUT)
        for b in bad:
            print("OVERFLOW:", b)
        print(f"text fit: {len(bad)} overflow(s)")
        if bad:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
