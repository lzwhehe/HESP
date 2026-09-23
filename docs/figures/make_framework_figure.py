"""Generate the HESP framework overview figure (stdlib only).

Output: docs/assets/hesp-framework.svg. Render to PDF/PNG with
    python docs/figures/render_figures.py docs/assets/hesp-framework.svg

Numbers inside the mini-plots are illustrative and only show the *shape* of each
quantity; they are not experimental results.
"""

from pathlib import Path
import re
from xml.sax.saxutils import escape

W, H = 1800, 904
SANS = "Helvetica Neue, Helvetica, Arial, sans-serif"
MATH = "Cambria Math, STIX Two Math, Times New Roman, serif"
MONO = "Consolas, Menlo, monospace"

C = {
    "ink": "#1F2937", "sub": "#6B7280", "line": "#CBD5E1",
    "H": "#2F5D9E", "Hf": "#EEF3FB", "Ha": "#5B8BD0",
    "E": "#0F766E", "Ef": "#E8F6F3", "Ea": "#2BB3A3",
    "S": "#B45309", "Sf": "#FEF5E6", "Sa": "#F0A43A",
    "P": "#5B3F99", "Pf": "#F3EFFB", "Pa": "#8C6FD6",
    "N": "#475569", "Nf": "#F6F8FA",
    "V": "#B42318", "Vf": "#FDEEEC",
}
out = []


def add(s):
    out.append(s)


def rect(x, y, w, h, fill="none", stroke="none", sw=1.5, rx=10, dash=None, opacity=None, extra=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' fill-opacity="{opacity}"' if opacity is not None else ""
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{o} '
        f'stroke="{stroke}" stroke-width="{sw}"{d} {extra}/>')


def _markup(s):
    """Tiny TeX-like markup: a_{sub}, a^{sup}. Everything else is escaped."""
    s = escape(s)
    s = re.sub(r"_\{([^}]*)\}", r'<tspan baseline-shift="sub" font-size="68%">\1</tspan>', s)
    s = re.sub(r"\^\{([^}]*)\}", r'<tspan baseline-shift="super" font-size="68%">\1</tspan>', s)
    return s


def text(x, y, s, size=15, weight=400, anchor="start", color=None, family=SANS, style="normal"):
    add(f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
        f'font-style="{style}" text-anchor="{anchor}" fill="{color or C["ink"]}">{_markup(s)}</text>')


def math(x, y, s, size=16, color=None, anchor="start"):
    text(x, y, s, size, 400, anchor, color, MATH, "italic")


def line(x1, y1, x2, y2, color, sw=1.5, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}"{d}/>')


def arrow(d, key, sw=2.2, dash=None):
    ds = f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<path d="{d}" fill="none" stroke="{C[key]}" stroke-width="{sw}" stroke-linecap="round" '
        f'stroke-linejoin="round"{ds} marker-end="url(#arr-{key})"/>')


def pill(x, y, label, key, size=12.5, mono=False, fill="#FFFFFF", h=24):
    w = len(label) * (size * 0.58 if mono else size * 0.56) + 18
    rect(x, y, w, h, fill, C[key], 1.2, h / 2)
    text(x + w / 2, y + h / 2 + size * 0.36, label, size, 500, "middle", C[key], MONO if mono else SANS)
    return w


def pill_flow(x0, y0, labels, key, xmax, size=12, gap=6, h=22):
    x, y = x0, y0
    for label in labels:
        w = len(label) * size * 0.56 + 16
        if x + w > xmax:
            x, y = x0, y + h + 6
        pill(x, y, label, key, size, h=h)
        x += w + gap


def badge(cx, cy, n, key, r=13):
    add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{C[key]}"/>')
    text(cx, cy + 5, str(n), 14, 700, "middle", "#FFFFFF")


def module(x, y, w, h, key, n, title, note=None):
    rect(x, y, w, h, C[key + "f"], C[key], 1.6, 12)
    badge(x + 22, y + 24, n, key)
    text(x + 42, y + 30, title, 17, 700, color=C[key])
    if note:
        text(x + w - 14, y + 29, note, 12.5, 400, "end", C["sub"], style="italic")


# ---------------------------------------------------------------- icons
def icon_lock(x, y, color):
    add(f'<g transform="translate({x},{y})"><path d="M-7 -2 v-5 a7 7 0 0 1 14 0 v5" fill="none" '
        f'stroke="{color}" stroke-width="2.2"/><rect x="-10" y="-2" width="20" height="15" rx="3" '
        f'fill="{color}"/><circle cx="0" cy="5" r="2.3" fill="#FFFFFF"/></g>')


def icon_doc(x, y, color):
    add(f'<g transform="translate({x},{y})"><path d="M0 0 h14 l6 6 v20 h-20 z" fill="#FFFFFF" '
        f'stroke="{color}" stroke-width="1.8"/><path d="M14 0 v6 h6" fill="none" stroke="{color}" '
        f'stroke-width="1.8"/><path d="M4 12 h12 M4 16 h12 M4 20 h8" stroke="{color}" stroke-width="1.4"/></g>')


def icon_server(x, y, color):
    add(f'<g transform="translate({x},{y})">' + "".join(
        f'<rect x="0" y="{i * 9}" width="24" height="7" rx="2" fill="#FFFFFF" stroke="{color}" stroke-width="1.6"/>'
        f'<circle cx="19" cy="{i * 9 + 3.5}" r="1.5" fill="{color}"/>' for i in range(3)) + '</g>')


def icon_llm(x, y, color):
    add(f'<g transform="translate({x},{y})"><path d="M0 4 a4 4 0 0 1 4 -4 h22 a4 4 0 0 1 4 4 v13 '
        f'a4 4 0 0 1 -4 4 h-14 l-6 6 v-6 h-2 a4 4 0 0 1 -4 -4 z" fill="#FFFFFF" stroke="{color}" '
        f'stroke-width="1.8"/><path d="M15 4.5 l1.8 4.2 4.2 1.8 -4.2 1.8 -1.8 4.2 -1.8 -4.2 -4.2 -1.8 '
        f'4.2 -1.8z" fill="{color}"/></g>')


def icon_journal(x, y, color):
    add(f'<g transform="translate({x},{y})"><rect x="0" y="0" width="20" height="25" rx="2" fill="#FFFFFF" '
        f'stroke="{color}" stroke-width="1.8"/><path d="M4 7 h12 M4 12 h12 M4 17 h7" stroke="{color}" '
        f'stroke-width="1.4"/><circle cx="18" cy="21" r="6" fill="{color}"/><path d="M15.2 21 l2 2 '
        f'3.6 -3.8" stroke="#FFF" stroke-width="1.6" fill="none"/></g>')


def icon_bolt(x, y, color, s=1.0):
    add(f'<path transform="translate({x},{y}) scale({s})" d="M8 0 L0 13 H6 L4 24 L13 9 H7 L9 0 Z" fill="{color}"/>')


def icon_shield(x, y, color):
    add(f'<g transform="translate({x},{y})"><path d="M11 0 L22 4 V11 C22 18 17 23 11 26 C5 23 0 18 '
        f'0 11 V4 Z" fill="#FFFFFF" stroke="{color}" stroke-width="1.8"/><path d="M6 13 l3.5 3.5 7 -7" '
        f'stroke="{color}" stroke-width="2" fill="none"/></g>')


# ---------------------------------------------------------------- canvas
add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
    f'aria-labelledby="t d">')
add('<title id="t">HESP framework overview</title>')
add('<desc id="d">(a) The HESP decision loop: hypotheses, pre-registered predictions, diagnostic '
    'selection, execution, evidence ledger and state monitor around an LLM planner. (b) The authorized '
    'local sandbox with a hidden independent verifier. (c) Controlled three-arm evaluation and audit.</desc>')
add('<defs>')
for k in ("ink", "H", "E", "S", "P", "N", "V", "sub"):
    add(f'<marker id="arr-{k}" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" '
        f'orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="{C[k]}"/></marker>')
add('<pattern id="hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
    f'<line x1="0" y1="0" x2="0" y2="7" stroke="{C["V"]}" stroke-opacity=".10" stroke-width="3"/></pattern>')
add('<filter id="sh" x="-5%" y="-5%" width="110%" height="120%"><feDropShadow dx="0" dy="1.5" '
    'stdDeviation="2.2" flood-color="#0f172a" flood-opacity=".12"/></filter>')
add('</defs>')
rect(0, 0, W, H, "#FFFFFF", "none", 0, 0)

PY, PH = 18, 868
LOOP_X, LOOP_W = 16, 952
ENV_X, ENV_W = 984, 372
EVAL_X, EVAL_W = 1372, 412
for x, w, tag, name in ((LOOP_X, LOOP_W, "(a)", "HESP Decision Loop"),
                        (ENV_X, ENV_W, "(b)", "Authorized Sandbox"),
                        (EVAL_X, EVAL_W, "(c)", "Controlled Evaluation & Audit")):
    rect(x, PY, w, PH, "#FBFCFD", "#D5DBE3", 1.3, 16)
    text(x + 20, PY + 34, f"{tag}  {name}", 19, 700)

# ====================================================================== (a)
MW, GAP = 288, 24
X1, X2, X3 = 36, 36 + MW + GAP, 36 + 2 * (MW + GAP)
R1Y, R1H = 70, 238
R2Y, R2H = 552, 196
HUB_W, HUB_H = 428, 128
HUB_X, HUB_Y = 492 - HUB_W // 2, 372
LEFT_SPINE = (HUB_X + X1 + MW) // 2          # overlap of module 1/6 and hub
RIGHT_SPINE = (X3 + HUB_X + HUB_W) // 2      # overlap of module 3/4 and hub

# -- (1) hypotheses
module(X1, R1Y, MW, R1H, "H", 1, "Hypotheses", "task-supplied (v0.3)")
text(X1 + 16, R1Y + 60, "competing local causes of one symptom", 12.5, 400, color=C["sub"], style="italic")
hyps = [("session expired", .08), ("owner policy", .46), ("workflow lock", .24),
        ("quota exceeded", .14), ("other / unknown", .08)]
for i, (name, p) in enumerate(hyps):
    yy = R1Y + 78 + i * 28
    top = i == 1
    text(X1 + 16, yy + 13, name, 13, 700 if top else 500)
    rect(X1 + 130, yy, 110, 17, "#FFFFFF", C["line"], 1, 3)
    rect(X1 + 130, yy, 110 * p / .5, 17, C["H"] if top else C["Ha"], "none", 0, 3, opacity=1 if top else .5)
    text(X1 + 246, yy + 13, f"{p:.2f}", 12, 500, color=C["sub"], family=MONO)
math(X1 + 130, R1Y + 226, "posterior  p_{t}(h)", 14, C["H"])

# -- (2) predictions
module(X2, R1Y, MW, R1H, "P", 2, "Pre-registered Predictions")
math(X2 + 16, R1Y + 60, "P(o | h, a),   a = GET /workflow/42", 14, C["P"])
outs = ["200", "403", "423", "401"]
mat = [[.80, .05, .05, .10], [.10, .80, .05, .05], [.05, .05, .85, .05],
       [.85, .05, .05, .05], [.40, .20, .20, .20]]
short = ["session", "owner", "workflow", "quota", "other"]
hx, hy, cw, ch = X2 + 104, R1Y + 90, 40, 24
for j, o in enumerate(outs):
    text(hx + j * cw + cw / 2, hy - 7, o, 12, 600, "middle", C["sub"], MONO)
for i, row in enumerate(mat):
    text(hx - 10, hy + i * ch + 17, short[i], 12.5, 500, "end")
    for j, v in enumerate(row):
        add(f'<rect x="{hx + j * cw + 1}" y="{hy + i * ch + 1}" width="{cw - 2}" height="{ch - 2}" rx="3" '
            f'fill="{C["P"]}" fill-opacity="{0.06 + 0.9 * v:.2f}"/>')
        text(hx + j * cw + cw / 2, hy + i * ch + 16.5, f"{v:.2f}".lstrip("0"), 11, 500, "middle",
             "#FFFFFF" if v > .5 else C["ink"], MONO)
text(X2 + 16, R1Y + 226, "logged before execution · source:", 12, 400, color=C["sub"], style="italic")
text(X2 + MW - 14, R1Y + 226, "LLM | table", 12, 700, "end", C["P"], MONO)

# -- (3) selector
module(X3, R1Y, MW, R1H, "P", 3, "Diagnostic Selector")
math(X3 + 16, R1Y + 60, "legal probes ranked by  EIG(a) / c(a)", 14, C["P"])
rank = [("/workflow/42", 1.00, 1, "sel"), ("/documents/42", .71, 1, ""), ("/audit", .55, 3, ""),
        ("/whoami", .38, 1, ""), ("/quota", 0, 1, "dup"), ("/help", 0.02, 1, "")]
for i, (name, v, cost, flag) in enumerate(rank):
    yy = R1Y + 76 + i * 23
    text(X3 + 16, yy + 13, name, 12.5, 700 if flag == "sel" else 400,
         C["sub"] if flag == "dup" else C["ink"], MONO)
    if flag == "dup":
        line(X3 + 16, yy + 8.5, X3 + 16 + len(name) * 7.2, yy + 8.5, C["V"], 1.4)
        text(X3 + 128, yy + 13, "duplicate · blocked", 12, 600, color=C["V"])
        continue
    bw = 96 * v + 3
    rect(X3 + 128, yy + 2, bw, 14, C["P"] if flag == "sel" else C["Pa"], "none", 0, 3,
         opacity=1 if flag == "sel" else .45)
    text(X3 + 134 + bw, yy + 13.5, f"c={cost}", 11.5, 500, color=C["sub"], family=MONO)
text(X3 + 16, R1Y + 226, "filters: scope · prerequisites · dedup · budget", 12, 400, color=C["sub"], style="italic")

# -- hub: LLM planner
rect(HUB_X, HUB_Y, HUB_W, HUB_H, "#FFFFFF", C["ink"], 2, 16, extra='filter="url(#sh)"')
icon_llm(HUB_X + 18, HUB_Y + 16, C["ink"])
text(HUB_X + 58, HUB_Y + 35, "LLM Planner  π", 18, 700)
text(HUB_X + HUB_W - 16, HUB_Y + 34, "Qwen2.5-7B · local", 12, 500, "end", C["sub"], style="italic")
text(HUB_X + 18, HUB_Y + 66, "reads the investigation state; returns one JSON decision", 13, 400, color=C["sub"])
px = HUB_X + 18
for label, key in (("action a", "P"), ("finish(ĥ, E)", "E"), ("stop", "N")):
    px += pill(px, HUB_Y + 82, label, key, 13, mono=True) + 10
text(HUB_X + HUB_W - 16, HUB_Y + 99, "usage logged", 12, 500, "end", C["sub"], style="italic")

# -- (6) state monitor, (5) ledger, (4) execute   [bottom row, right-to-left flow]
module(X1, R2Y, MW, R2H, "S", 6, "State Monitor")
icon_bolt(X1 + 18, R2Y + 44, C["Sa"])
math(X1 + 40, R2Y + 62, "v_{t} ≠ v_{t−1}", 17, C["S"])
text(X1 + 118, R2Y + 61, "login · role switch · edit", 12.5, 500, color=C["S"])
tx0, ty0 = X1 + 24, R2Y + 84
line(tx0, ty0 + 10, tx0 + 240, ty0 + 10, C["S"], 1.6)
for i, (xx, lab) in enumerate(((0, "v=1"), (80, "v=1"), (160, "v=2"), (236, "v=2"))):
    add(f'<circle cx="{tx0 + xx}" cy="{ty0 + 10}" r="5" fill="{"#FFFFFF" if i < 2 else C["S"]}" '
        f'stroke="{C["S"]}" stroke-width="1.6"/>')
    text(tx0 + xx, ty0 + 32, lab, 11, 500, "middle", C["sub"], MONO)
icon_bolt(tx0 + 114, ty0 - 2, C["Sa"], .9)
text(X1 + 16, R2Y + 150, "reset current scores, keep history,", 12.5, 400)
text(X1 + 16, R2Y + 168, "emit a replan signal to π", 12.5, 400)
text(X1 + 16, R2Y + 186, "old-state evidence cannot be cited", 12.5, 400, color=C["sub"], style="italic")

module(X2, R2Y, MW, R2H, "E", 5, "Evidence Ledger")
math(X2 + 16, R2Y + 64, "p_{t+1}(h) ∝ p_{t}(h) · P(o_{t} | h, a_{t})", 17, C["E"])
text(X2 + 16, R2Y + 92, "update skipped, uncertainty kept, if:", 12.5, 500)
pill_flow(X2 + 16, R2Y + 102, ["duplicate", "stale state", "invalid", "unmodeled o", "model conflict"],
          "E", X2 + MW - 10, 11.5)
text(X2 + 16, R2Y + 184, "each entry: before · after · provenance", 12, 400, color=C["sub"], style="italic")

module(X3, R2Y, MW, R2H, "N", 4, "Register → Execute")
icon_journal(X3 + 16, R2Y + 46, C["N"])
text(X3 + 46, R2Y + 58, "prediction_registered", 12.5, 700, color=C["N"], family=MONO)
text(X3 + 46, R2Y + 76, "durable before the tool call", 12.5, 400, color=C["sub"])
rect(X3 + 16, R2Y + 92, MW - 32, 88, "#FFFFFF", C["line"], 1, 8)
math(X3 + 28, R2Y + 116, "o_{t}", 15)
text(X3 + 48, R2Y + 115, "= 423 {\"state\":\"locked\"}", 12.5, 400, family=MONO)
text(X3 + 28, R2Y + 140, "raw response + provenance", 12.5, 400, color=C["sub"])
text(X3 + 28, R2Y + 162, "→ outcome class o ∈ 𝒪(a)", 12.5, 400, color=C["sub"])

# -- loop arrows (no crossings)
arrow(f"M{X1 + MW} {R1Y + 120} H{X2 - 4}", "H")                         # 1 -> 2
arrow(f"M{X2 + MW} {R1Y + 120} H{X3 - 4}", "P")                         # 2 -> 3
arrow(f"M{RIGHT_SPINE} {R1Y + R1H} V{HUB_Y - 4}", "P")                  # 3 -> hub
text(RIGHT_SPINE + 10, R1Y + R1H + 36, "rankings", 12.5, 700, color=C["P"])
text(RIGHT_SPINE + 10, R1Y + R1H + 52, "(HESP arm only)", 12, 500, color=C["P"], style="italic")
arrow(f"M{RIGHT_SPINE} {HUB_Y + HUB_H} V{R2Y - 4}", "N")                # hub -> 4
text(RIGHT_SPINE + 10, HUB_Y + HUB_H + 30, "chosen a", 12.5, 700, color=C["N"], family=MONO)
arrow(f"M{X3} {R2Y + 110} H{X2 + MW + 4}", "E")                         # 4 -> 5
arrow(f"M{X2} {R2Y + 110} H{X1 + MW + 4}", "S")                         # 5 -> 6
arrow(f"M{LEFT_SPINE} {R2Y} V{HUB_Y + HUB_H + 4}", "S")                 # 6 -> hub
text(LEFT_SPINE - 10, HUB_Y + HUB_H + 26, "investigation state", 12.5, 700, "end", C["S"])
math(LEFT_SPINE - 10, HUB_Y + HUB_H + 44, "(H, E, s_{t})", 14, C["S"], "end")
arrow(f"M{LEFT_SPINE} {HUB_Y} V{R1Y + R1H + 4}", "H")                   # hub -> 1
text(LEFT_SPINE - 10, R1Y + R1H + 36, "replan signal", 12.5, 700, "end", C["H"])
text(LEFT_SPINE - 10, R1Y + R1H + 52, "H expansion: future work", 12, 500, "end", C["H"], style="italic")

# -- equation + legend strip
EQ_Y = 770
rect(X1, EQ_Y, X3 + MW - X1, 44, "#FFFFFF", "#D5DBE3", 1.1, 10)
math(X1 + 28, EQ_Y + 29, "EIG(a) = H[p_{t}] − 𝔼_{o | a} H[p_{t}(· | o, a)]", 18)
math(X3 + MW - 28, EQ_Y + 29, "a* = argmax_{a ∈ 𝒜(s_t) ∖ seen}  EIG(a) / c(a)", 18, anchor="end")
LG_Y = 842
text(X1 + 4, LG_Y, "Colours:", 12.5, 700, color=C["sub"])
lx = X1 + 70
for label, key in (("Hypotheses", "H"), ("Planning", "P"), ("Evidence", "E"), ("State", "S"),
                   ("Execution", "N"), ("Hidden oracle", "V")):
    rect(lx, LG_Y - 11, 14, 14, C[key + "f"], C[key], 1.5, 3)
    text(lx + 20, LG_Y, label, 12.5, 500, color=C["sub"])
    lx += len(label) * 7 + 44
text(X3 + MW, LG_Y, "mini-plot values are illustrative", 12, 400, "end", C["sub"], style="italic")

# ====================================================================== (b)
ex, ew = ENV_X + 20, ENV_W - 40
# public task
rect(ex, 70, ew, 104, "#FFFFFF", C["N"], 1.4, 12, extra='filter="url(#sh)"')
icon_doc(ex + 16, 84, C["N"])
text(ex + 48, 100, "Public task  τ", 16, 700, color=C["N"])
text(ex + 48, 120, "“Saving document #42 fails.”", 13.5, 400, style="italic")
text(ex + 16, 148, "Diagnose the cause; cite observations.", 13, 400, color=C["sub"])
text(ex + 16, 165, "No answer or write-up reaches π.", 13, 400, color=C["sub"])

# business state
rect(ex, 188, ew, 96, C["Sf"], C["S"], 1.4, 12)
text(ex + 16, 212, "Business state  s_{t}", 16, 700, color=C["S"])
px = ex + 16
for label in ("role=editor", "page=doc", "v=2"):
    px += pill(px, 226, label, "S", 12, mono=True) + 8
text(ex + 16, 274, "versioned; advances on login / role / edits", 12.5, 400, color=C["sub"], style="italic")

# hidden oracle region, aligned with the planner hub
VY = HUB_Y - 22
rect(ex - 6, VY, ew + 12, 170, "url(#hatch)", C["V"], 1.4, 14, dash="7 5")
text(ex + ew, VY - 8, "hidden from π", 12, 700, "end", C["V"])
rect(ex + 10, VY + 16, ew - 20, 138, "#FFFFFF", C["V"], 1.4, 12, extra='filter="url(#sh)"')
icon_lock(ex + 36, VY + 46, C["V"])
text(ex + 58, VY + 48, "Hidden cause  h*", 16, 700, color=C["V"])
text(ex + 58, VY + 72, "Independent verifier  V(ĥ, E)", 15, 600, color=C["V"])
text(ex + 26, VY + 104, "passes iff ĥ = h* and a cited", 13, 400)
text(ex + 26, VY + 122, "observation from the current state", 13, 400)
text(ex + 26, VY + 140, "carries the cause's signature", 13, 400)

# local web app, aligned with (4)
WY = 560
rect(ex, WY, ew, 196, "#FFFFFF", C["N"], 1.4, 12, extra='filter="url(#sh)"')
icon_server(ex + 16, WY + 14, C["N"])
text(ex + 50, WY + 31, "Local web app", 16, 700, color=C["N"])
text(ex + ew - 14, WY + 31, "127.0.0.1", 12, 500, "end", C["sub"], MONO)
eps = ["GET  /whoami", "GET  /documents/42", "POST /documents/42/save", "GET  /workflow/42",
       "GET  /audit?doc=42", "POST /login"]
for i, e in enumerate(eps):
    yy = WY + 58 + i * 21
    rect(ex + 14, yy - 15, ew - 28, 20, "#F4F6F9" if i % 2 == 0 else "#FFFFFF", "none", 0, 4)
    text(ex + 22, yy, e, 12.5, 400, family=MONO)
text(ex + 16, WY + 186, "fresh instance per episode · reset", 12, 400, color=C["sub"], style="italic")

# guardrails
GY = 772
rect(ex, GY, ew, 98, "#FFFFFF", C["N"], 1.4, 12)
icon_shield(ex + 16, GY + 12, C["N"])
text(ex + 48, GY + 30, "Guardrails · shared by all arms", 14.5, 700, color=C["N"])
pill_flow(ex + 16, GY + 44, ["path allowlist", "no redirects", "timeout", "tool budget", "exact dedup"],
          "N", ex + ew - 8, 11.5)

# loop <-> sandbox arrows (short and horizontal)
arrow(f"M{X3 + MW} {R2Y + 62} H{ex - 4}", "N")
text((X3 + MW + ex) / 2, R2Y + 54, "a", 13, 700, "middle", C["N"], MONO)
arrow(f"M{ex} {R2Y + 150} H{X3 + MW + 4}", "E", dash="6 4")
math((X3 + MW + ex) / 2, R2Y + 142, "o_{t}", 15, C["E"], "middle")
arrow(f"M{HUB_X + HUB_W} {HUB_Y + 94} H{ex + 6}", "V")
text(X3 + MW - 8, HUB_Y + 86, "finish(ĥ, E)", 13, 700, "end", C["V"], MONO)
text(X3 + MW - 8, HUB_Y + 116, "→ independent check", 12, 500, "end", C["V"], style="italic")

# ====================================================================== (c)
cx = EVAL_X + 20
text(cx, 82, "Same model, tools, budget, dedup and verifier", 13.5, 600, color=C["sub"])
cols = ["goal +\nhistory", "H, E, s\nledger", "EIG / c\nrankings", "picks\naction"]
arms = [("A", "ReAct-style", "N", [1, 0, 0, "π"]),
        ("B", "Memory-only", "E", [1, 1, 0, "π"]),
        ("C", "HESP", "P", [1, 1, 1, "ctrl"])]
mx, my, colw, rowh = cx + 128, 96, 60, 52
for j, col in enumerate(cols):
    for k, part in enumerate(col.split("\n")):
        text(mx + j * colw + colw / 2, my + 14 + k * 15, part, 12, 600, "middle", C["sub"])
for i, (tag, name, key, vals) in enumerate(arms):
    yy = my + 38 + i * rowh
    rect(cx, yy, EVAL_W - 40, rowh - 8, C[key + "f"], C[key], 1.4, 10)
    add(f'<circle cx="{cx + 20}" cy="{yy + 22}" r="12" fill="{C[key]}"/>')
    text(cx + 20, yy + 27, tag, 13.5, 700, "middle", "#FFFFFF")
    text(cx + 40, yy + 27, name, 14.5, 700, color=C[key])
    for j, v in enumerate(vals):
        xx = mx + j * colw + colw / 2
        if v == 1:
            add(f'<path d="M{xx - 7} {yy + 22} l5 5 l10 -11" fill="none" stroke="{C[key]}" stroke-width="2.6" '
                f'stroke-linecap="round" stroke-linejoin="round"/>')
        elif v == 0:
            text(xx, yy + 28, "–", 16, 600, "middle", C["line"])
        else:
            text(xx, yy + 27, v, 13, 700, "middle", C[key], MONO if v == "ctrl" else MATH)

AY = 298
rect(cx, AY, EVAL_W - 40, 106, "#FFFFFF", "#D5DBE3", 1.3, 12)
text(cx + 16, AY + 26, "Selector ablations", 15, 700, color=C["P"])
text(cx + 160, AY + 26, "(C-family)", 12.5, 400, color=C["sub"], style="italic")
abl = [("EIG / c", "full"), ("EIG only", "ignore cost"), ("MAP-greedy", "test top h"),
       ("random", "legal probe"), ("oracle P", "true table"), ("LLM P", "elicited")]
for i, (a, d) in enumerate(abl):
    xx, yy = cx + 16 + (i % 2) * 180, AY + 50 + (i // 2) * 22
    add(f'<circle cx="{xx + 4}" cy="{yy - 4}" r="3.5" fill="{C["Pa"]}"/>')
    text(xx + 13, yy, a, 12.5, 700, family=MONO)
    text(xx + 13 + len(a) * 7.3 + 6, yy, d, 12, 400, color=C["sub"], style="italic")

TY = 418
rect(cx, TY, EVAL_W - 40, 118, "#FFFFFF", "#D5DBE3", 1.3, 12)
text(cx + 16, TY + 26, "Task suite", 15, 700, color=C["N"])
text(cx + 102, TY + 26, "(paired, shuffled, seeded)", 12.5, 400, color=C["sub"], style="italic")
suite = [("fixture", "synthetic, 4 causes (v0.2)"), ("web-diag", "local HTTP app, 8 causes"),
         ("+ drift", "state change mid-episode"), ("+ noise", "flaky probe outcomes")]
for i, (a, d) in enumerate(suite):
    yy = TY + 50 + i * 19
    text(cx + 16, yy, a, 12.5, 700, color=C["N"], family=MONO)
    text(cx + 100, yy, d, 12.5, 400, color=C["sub"])

PPY = 550
steps = [("events.jsonl", "append-only journal per run", "N"), ("Journal audit", "order · counters · budget", "E"),
         ("Paired analysis", "task-cluster bootstrap CIs", "P"), ("Calibration", "Brier · log-loss of P(o | h, a)", "H")]
for i, (a, d, key) in enumerate(steps):
    yy = PPY + i * 64
    rect(cx, yy, EVAL_W - 40, 50, C[key + "f"], C[key], 1.3, 10)
    text(cx + 16, yy + 22, a, 14.5, 700, color=C[key], family=MONO if i == 0 else SANS)
    text(cx + 16, yy + 40, d, 12.5, 400, color=C["sub"])
    if i < len(steps) - 1:
        arrow(f"M{cx + 186} {yy + 50} V{yy + 62}", "sub", 1.8)
text(cx, 832, "Primary: verified completion rate.", 12.5, 700)
text(cx, 850, "Secondary: tool cost, tokens (unknown ≠ 0).", 12.5, 500, color=C["sub"])
text(cx, 868, "Failures stay in the denominator.", 12.5, 500, color=C["sub"])

add('</svg>')
target = Path(__file__).resolve().parents[1] / "assets" / "hesp-framework.svg"
target.write_text("\n".join(out), encoding="utf-8")
print(target)
