"""HESP project overview ("Measured Elimination"; philosophy in hesp-overview-philosophy.md).

One plate, three acts: the problem (small local LLMs fail on procedure), the controller
(one real episode drawn as hypothesis elimination), and what the pre-registered studies found.
Episode data come from the archived journal of the stopping study; every other number from
hesp_research/results/*_summary.json. Fonts (OFL) are embedded from docs/figures/fonts.

    python docs/figures/make_overview_figure.py --check
    python docs/figures/render_figures.py docs/assets/hesp-overview.svg
"""
import argparse
import base64
import json
import math
from pathlib import Path
import sys
import tarfile
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RESULTS = ROOT / "hesp_research" / "results"
OUT = ROOT / "docs" / "assets" / "hesp-overview.svg"
W, H = 2400, 1500

PAPER, INK, INK2, MUTED, FAINT, RULE = "#FBFAF7", "#111827", "#374151", "#6B7280", "#C9CDD4", "#D9D6CE"
BLUE, BLUE_TINT, AMBER, AMBER_TINT = "#1D3FA8", "#E8EDFA", "#B45309", "#FBF1E4"
SERIF, SANS, MONO = "HSerif", "HSans", "HMono"

EPISODE = ("v09_llama8b", "run0087_sec-base-02_0_hesp_eigc_blind_autostop")
HYP = [("credential_stuffing", "credential stuffing"), ("sqli_probe", "SQL injection"),
       ("misconfig_exposed_admin", "exposed admin panel"), ("authorized_scan", "authorized scan"),
       ("false_positive_monitor", "monitoring false positive"), ("insider_exfil", "insider exfiltration"),
       ("vuln_component", "vulnerable component"), ("dns_c2", "DNS command-and-control"), ("other", "other")]
PROBE_NAMES = {"source_ips": "source IPs", "access_pattern": "HTTP pattern", "admin_exposure": "admin config",
               "auth_log": "auth log", "dns_logs": "DNS log", "user_activity": "egress", "change_ticket": "change ticket",
               "component_versions": "inventory", "threat_intel": "threat intel", "runbook": "runbook"}
OUTCOME_NAMES = {"normal": "normal", "exposed_no_auth": "exposed, no auth"}


class Plate:
    def __init__(self):
        self.parts = []

    def add(self, s):
        self.parts.append(s)

    def text(self, x, y, s, fit, family=SANS, size=24, weight=400, color=INK, anchor="start", style="normal",
             spacing=0):
        ls = f' letter-spacing="{spacing}"' if spacing else ""
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
                 f'font-style="{style}" fill="{color}" text-anchor="{anchor}"{ls} '
                 f'data-fit="{fit[0]:.1f},{fit[1]:.1f}">{escape(s)}</text>')

    def line(self, x1, y1, x2, y2, color=RULE, sw=1.5, dash=None, arrow=None):
        dd = f' stroke-dasharray="{dash}"' if dash else ""
        mk = f' marker-end="url(#{arrow})"' if arrow else ""
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" '
                 f'stroke-width="{sw}" stroke-linecap="round"{dd}{mk}/>')

    def circle(self, x, y, r, fill="none", stroke=None, sw=1.5):
        st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        self.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="{fill}"{st}/>')

    def rect(self, x, y, w, h, fill, stroke="none", sw=0, rx=0):
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" '
                 f'stroke="{stroke}" stroke-width="{sw}"/>')


def fonts_css():
    faces = [(SERIF, "InstrumentSerif-Regular.ttf", 400, "normal"), (SERIF, "InstrumentSerif-Italic.ttf", 400, "italic"),
             (SANS, "InstrumentSans-Regular.ttf", 400, "normal"), (SANS, "InstrumentSans-Bold.ttf", 700, "normal"),
             (MONO, "GeistMono-Regular.ttf", 400, "normal"), (MONO, "GeistMono-Bold.ttf", 700, "normal")]
    css = []
    for fam, f, wt, st in faces:
        b64 = base64.b64encode((HERE / "fonts" / f).read_bytes()).decode()
        css.append(f"@font-face{{font-family:'{fam}';src:url(data:font/ttf;base64,{b64}) format('truetype');"
                   f"font-weight:{wt};font-style:{st};}}")
    return "".join(css)


# ------------------------------------------------------------------ data
def episode():
    run, name = EPISODE
    with tarfile.open(RESULTS / run / "runs_archive.tar.gz") as tf:
        lines = tf.extractfile(f"{name}/events.jsonl").read().decode("utf-8").splitlines()
    events = [json.loads(line) for line in lines]
    prior = json.loads(next(e for e in events if e["kind"] == "evidence_update")
                       ["evidence"]["before"].__repr__().replace("'", '"'))
    steps = [("prior", None, prior)]
    obs = None
    for e in events:
        if e["kind"] == "observation":
            obs = e["observation"]
        elif e["kind"] == "evidence_update":
            steps.append((obs["action_id"], obs["outcome"], e["evidence"]["after"]))
    verdict = next(e for e in events if e["kind"] == "independent_verification")
    return steps, verdict


def numbers():
    v6 = json.loads((RESULTS / "v06_summary.json").read_text(encoding="utf-8"))
    v8 = json.loads((RESULTS / "v08_summary.json").read_text(encoding="utf-8"))
    v9 = json.loads((RESULTS / "v09_summary.json").read_text(encoding="utf-8"))
    ref = json.loads((RESULTS / "v09_llm_free_reference.json").read_text(encoding="utf-8"))
    l8 = [json.loads(x) for x in (RESULTS / "v08_llama8b" / "outcomes.jsonl").read_text(encoding="utf-8").splitlines()]
    q7 = [json.loads(x) for x in (RESULTS / "v09_qwen7b" / "outcomes.jsonl").read_text(encoding="utf-8").splitlines()]
    q7 = [r for r in q7 if r["arm"] == "memory_only"]
    concl = [k for k in v8 if k != "llama8b"]
    rank = [v8[k]["terms"]["hesp_eigc_blind - hesp_random_blind"]["difference"] for k in concl]
    return {
        "q7_alone": v9["qwen7b"]["verified"]["memory_only"],
        "q7_claims": sum(r["claimed_hypothesis"] is not None for r in q7), "q7_n": len(q7),
        "q7_calls": sum(r["tool_calls"] for r in q7) / len(q7),
        "l8_decisions": sum(r["planner_calls"] for r in l8),
        "l8_verdicts": sum(r["claimed_hypothesis"] is not None for r in l8),
        "q7_elicited": v6["7b"]["verified"]["hesp_eigc_guard_llmp"],
        "q7_mem": v6["7b"]["verified"]["memory_only"], "q7_hesp": v6["7b"]["verified"]["hesp_eigc_guard_emp20"],
        "rank_lo": min(rank), "rank_hi": max(rank),
        "take_7b": v8["qwen7b"]["terms"]["hesp_random_blind - memory_only"]["difference"],
        "take_72b": v8["qwen72b"]["terms"]["hesp_random_blind - memory_only"]["difference"],
        "l8_before": v9["llama8b"]["verified"]["hesp_eigc_blind"], "l8_after": v9["llama8b"]["verified"]["hesp_eigc_blind_autostop"],
        "no_llm": ref["verified"]["controller_eigc_autostop"],
        "best_llm": max(v9[k]["verified"]["hesp_eigc_blind"] for k in v9),
        "episodes": 1944 + 1728 + sum(v8[k]["episodes"] for k in v8) + sum(v9[k]["episodes"] for k in v9),
    }


# ------------------------------------------------------------------ acts
def act_header(p, x, x1, y, index, kicker, title):
    p.text(x, y, f"{index}", (x, x + 60), MONO, 22, 700, BLUE)
    p.text(x + 44, y, kicker.upper(), (x + 40, x1), MONO, 20, 400, MUTED, spacing=3)
    p.text(x, y + 56, title, (x, x1), SERIF, 40, 400, INK)


def fmt(v, d=3):
    return f"{v:.{d}f}"


def act_problem(p, n, x, x1, y):
    act_header(p, x, x1, y, "01", "the problem", "Small models fail on procedure")
    p.text(x, y + 98, "7B and 8B open-weight models, investigating alone", (x, x1), SANS, 22, color=MUTED)
    rows = [
        (fmt(n["q7_alone"]), "Qwen2.5-7B: share verified",
         f"probes until the budget runs out; a verdict in {n['q7_claims']} of {n['q7_n']} cases", "repeat"),
        (f"{n['l8_verdicts']} / {n['l8_decisions']:,}", "Llama-3.1-8B: verdicts / decisions",
         "always asks for one more probe, even at p > 0.999", "never"),
        (fmt(n["q7_elicited"]), "Qwen2.5-7B with its own tables",
         "cannot write calibrated probe-outcome likelihoods", "flat"),
    ]
    ry = y + 190
    for big, unit, note, glyph in rows:
        p.text(x, ry + 44, big, (x, x1), MONO, 52, 700, AMBER)
        p.text(x, ry + 84, unit, (x, x1), SANS, 24, 700, INK)
        p.text(x, ry + 118, note, (x, x1), SANS, 21, color=INK2)
        gx, gy = x, ry + 162
        if glyph == "repeat":      # about seven distinct probes, then the budget is gone
            k = round(n["q7_calls"])
            for i in range(k):
                p.circle(gx + 10 + i * 30, gy, 9, AMBER, AMBER, 2)
            p.circle(gx + 10 + k * 30, gy, 9, "none", FAINT, 2)
            p.text(gx + 30 * k + 36, gy + 7, f"{n['q7_calls']:.1f} probes, budget spent", (gx + 30 * k + 30, x1), SANS, 19,
                   style="italic", color=MUTED)
        elif glyph == "never":     # probes forever, no verdict
            for i in range(12):
                p.line(gx + 4 + i * 22, gy - 12, gx + 4 + i * 22, gy + 12, AMBER, 3)
            p.circle(gx + 282, gy, 11, "none", FAINT, 2, )
            p.text(gx + 306, gy + 7, "no verdict", (gx + 300, x1), SANS, 19, style="italic", color=MUTED)
        else:                      # a flat, uninformative table
            for i in range(9):
                for j in range(2):
                    p.rect(gx + i * 30, gy - 16 + j * 18, 26, 14, "#E7E3DA")
            p.text(gx + 282, gy + 7, "flat likelihoods", (gx + 276, x1), SANS, 19, style="italic", color=MUTED)
        ry += 282


def act_controller(p, steps, verdict, x, x1, y):
    act_header(p, x, x1, y, "02", "the controller", "Hypotheses eliminated, probe by probe")
    # the loop, drawn as a quiet band
    by = y + 128
    nodes = [(x, 250, "Local LLM planner", "proposes, finishes, abstains", INK2, "#F1EFEA"),
             (x + 320, 300, "Controller", "ledger · EIG/cost · stop rule", BLUE, BLUE_TINT),
             (x + 690, 190, "Probes", "10 read-only views", INK2, "#F1EFEA")]
    for nx, nw, title, sub, col, tint in nodes:
        p.rect(nx, by, nw, 84, tint, col, 2, 42)
        p.text(nx + nw / 2, by + 36, title, (nx + 10, nx + nw - 10), SANS, 22, 700, col, anchor="middle")
        p.text(nx + nw / 2, by + 64, sub, (nx + 10, nx + nw - 10), SANS, 17, color=INK2, anchor="middle")
    p.line(x + 316, by + 30, x + 256, by + 30, BLUE, 2.5, arrow="mb")
    p.line(x + 254, by + 56, x + 314, by + 56, INK2, 2.5, arrow="mg")
    p.line(x + 624, by + 30, x + 684, by + 30, BLUE, 2.5, arrow="mb")
    p.line(x + 686, by + 56, x + 626, by + 56, INK2, 2.5, arrow="mg")
    # the matrix: rows = hypotheses, columns = steps, circle area = posterior
    top = by + 190
    label_x1 = x + 300
    col_x = [label_x1 + 60 + i * 150 for i in range(len(steps))]
    row_h = 58
    rmax = 34
    for i, (probe, outcome, _) in enumerate(steps):
        cx = col_x[i]
        p.text(cx, top - 62, f"{i}", (cx - 40, cx + 40), MONO, 22, 700, BLUE if i else MUTED, anchor="middle")
        if probe == "prior":
            p.text(cx, top - 32, "prior", (cx - 80, cx + 80), SANS, 19, color=MUTED, anchor="middle")
        else:
            p.text(cx, top - 32, PROBE_NAMES.get(probe, probe), (cx - 88, cx + 88), SANS, 19, 700, INK2, anchor="middle")
            p.text(cx, top - 8, f"→ {OUTCOME_NAMES.get(outcome, outcome)}", (cx - 88, cx + 88), SANS, 18,
                   color=MUTED, anchor="middle")
    for j, (key, label) in enumerate(HYP):
        ry = top + 40 + j * row_h
        winner = key == verdict["hypothesis"]
        p.text(label_x1, ry + 7, label, (x, label_x1 + 4), SANS, 21, 700 if winner else 400,
               BLUE if winner else INK2, anchor="end")
        p.line(label_x1 + 18, ry, col_x[-1] + rmax, ry, "#ECE9E2", 1)
        for i, (_, _, scores) in enumerate(steps):
            v = scores[key]
            cx = col_x[i]
            if v < 0.0015:
                p.circle(cx, ry, 5, "none", FAINT, 1.5)
            else:
                r = max(rmax * math.sqrt(v), 2.2)
                p.circle(cx, ry, r, BLUE if winner and i else (INK if i else "#9CA3AF"))
    last = steps[-1][2][verdict["hypothesis"]]
    vy = top + 40 + len(HYP) * row_h + 10
    p.text(col_x[-1], vy + 10, f"p = {last:.3f}", (col_x[-1] - 120, col_x[-1] + 120), MONO, 22, 700, BLUE,
           anchor="middle")
    p.text(x, vy + 70, "The controller stops and cites evidence; the verifier confirms "
           "“exposed admin panel”.", (x, x1), SANS, 21, color=INK2)
    p.text(x, vy + 104, "Real episode sec-base-02, stopping study. Circle area = posterior; rings = eliminated.", (x, x1), SANS, 19, style="italic", color=MUTED)


def act_evidence(p, n, x, x1, y):
    act_header(p, x, x1, y, "03", "what we measured", "Four pre-registered studies")
    p.text(x, y + 98, f"5 models, 2 families, {n['episodes']:,} audited episodes", (x, x1), SANS, 22,
           color=MUTED)
    items = [
        ("No oracle needed", f"{fmt(n['q7_mem'])} → {fmt(n['q7_hesp'])}",
         ["Tables counted from LLM-free runs work", "as well as the true generator (Qwen 7B)"], BLUE),
        ("The ranking helps every model", f"+{n['rank_lo']:.2f} to +{n['rank_hi']:.2f}",
         ["EIG/cost vs random, same planner prompt;", f"taking choice away: 7B {n['take_7b']:+.2f}, 72B {n['take_72b']:+.2f}".replace("-", "−")], BLUE),
        ("What to probe ≠ when to stop", f"{fmt(n['l8_before'], 0) if n['l8_before'] == 0 else fmt(n['l8_before'])} → {fmt(n['l8_after'])}",
         ["A controller stop rescues Llama 8B;", "probe choice adds nothing detectable after"], BLUE),
        ("The controller alone comes close", f"{fmt(n['no_llm'])} vs {fmt(n['best_llm'])}",
         ["No LLM vs the best LLM configuration:", "strong models wait for confirming evidence"], INK),
        ("Public SOC data cannot test this", "3 of 3",
         ["ExCyTIn, GUIDE and OTRF: the alert names", "the answer, or labels follow policy"], AMBER),
    ]
    iy = y + 150
    for k, (title, num, lines, col) in enumerate(items):
        p.line(x + 8, iy + 10, x + 8, iy + 156, "#E5E1D8", 2)
        p.circle(x + 8, iy + 10, 7, col)
        p.text(x + 34, iy + 18, title, (x + 30, x1), SANS, 23, 700, INK)
        p.text(x + 34, iy + 64, num, (x + 30, x1), MONO, 34, 700, col)
        for m, ln in enumerate(lines):
            p.text(x + 34, iy + 98 + m * 28, ln, (x + 30, x1), SANS, 20, color=INK2)
        iy += 176


def build():
    n = numbers()
    steps, verdict = episode()
    p = Plate()
    p.rect(0, 0, W, H, PAPER)
    m = 90
    # title band
    p.text(m, 150, "HESP", (m, m + 330), SERIF, 118, 400, INK)
    p.text(m + 330, 108, "Hypotheses, Evidence, State, Planning", (m + 320, 1500), SERIF, 44, 400, INK, style="italic")
    p.text(m + 330, 150, "An external investigation procedure for small local LLMs in security alert triage",
           (m + 320, 1640), SANS, 26, color=INK2)
    for i, s in enumerate(["read-only probes", "pre-registered", "every prediction journaled"]):
        p.text(W - m, 96 + i * 32, s, (W - m - 420, W - m), MONO, 20, color=MUTED, anchor="end", spacing=1)
    p.line(m, 206, W - m, 206, INK, 2)
    # three acts on one grid
    xs = [(m, m + 620), (m + 700, m + 700 + 880), (W - m - 560, W - m)]
    act_problem(p, n, *xs[0], 270)
    act_controller(p, steps, verdict, *xs[1], 270)
    act_evidence(p, n, *xs[2], 270)
    for a, b in ((xs[0][1], xs[1][0]), (xs[1][1], xs[2][0])):
        p.line((a + b) / 2, 270, (a + b) / 2, 1290, RULE, 1.5)
    # coda
    p.line(m, 1340, W - m, 1340, INK, 2)
    p.text(m, 1428, "Put the procedure outside the model.", (m, 1100), SERIF, 54, 400, INK, style="italic")
    p.text(1120, 1404, "What remains for the model: judging when evidence suffices,", (1110, W - m), SANS, 25,
           color=INK2)
    p.text(1120, 1440, "and reading raw telemetry into the observations the controller consumes.", (1110, W - m),
           SANS, 25, color=INK2)
    defs = (f"<style>{fonts_css()}</style>"
            f'<marker id="mb" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{BLUE}"/></marker>'
            f'<marker id="mg" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{INK2}"/></marker>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            f"<defs>{defs}</defs>" + "\n".join(p.parts) + "</svg>\n"), n, steps


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    svg, n, steps = build()
    OUT.write_bytes(svg.encode("utf-8"))
    print(OUT)
    print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in n.items()})
    for probe, outcome, scores in steps:
        print(probe, outcome, {k: round(v, 3) for k, v in scores.items()})
    if args.check:
        sys.path.insert(0, str(HERE))
        from render_figures import check_fit
        bad = check_fit(OUT)
        for b in bad:
            print("OVERFLOW:", b)
        print(f"text fit: {len(bad)} overflow(s)")
        if bad:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
