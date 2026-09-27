"""HESP framework figure: the method shown as two real investigations, side by side.

Output: docs/assets/hesp-framework.svg (render PDF/PNG with render_figures.py).

The same alert (sec-triage task sec-base-00, hidden cause credential_stuffing), the same
local Qwen2.5-7B planner, the same probes, budget and verifier -- one run where the planner
chooses every probe (Memory-only) and one where the HESP controller chooses and the planner
only concludes. Rows are decision steps. Everything is read from the v0.6 per-episode
journals inside results/v06_7b/runs_archive.tar.gz (repeat 0 of both arms), and the
72-episode totals from results/v06_7b/outcomes.jsonl; nothing is typed in by hand.

Design: 7.0 in full-width float on a 1536 px canvas (1 pt = 3.048 px); Times New Roman,
Consolas for probe and outcome identifiers. ``--check`` measures every text element in
headless Chrome and fails on overflow.
"""
import argparse
import json
from pathlib import Path
import sys
import tarfile
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "hesp_research" / "results" / "v06_7b"
sys.path.insert(0, str(ROOT / "hesp_research"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from hesp.secapp import HYPOTHESES, SecTriageEnvironment   # noqa: E402

OUT = ROOT / "docs" / "assets" / "hesp-framework.svg"
TASK, REPEAT = "sec-base-00", 0
ARMS = ("memory_only", "hesp_eigc_guard_emp20")
W = 1536
SERIF = "'Times New Roman', Times, serif"
MONO = "Consolas, 'DejaVu Sans Mono', monospace"
INK, INK2, MUTED, RULE, TRACK = "#111827", "#374151", "#6B7280", "#D1D5DB", "#EEF0F3"
BLUE, BLUE_TINT = "#1D4ED8", "#EEF3FD"
RED, RED_TINT = "#BE123C", "#FDF2F4"
GREEN, GREEN_TINT = "#047857", "#ECFDF5"
TITLE, LABEL, SMALL, CODE = 29, 25, 23, 22


# ---------------------------------------------------------------- data
def journal(arm):
    with tarfile.open(RUN / "runs_archive.tar.gz") as tar:
        name = next(m.name for m in tar.getmembers()
                    if m.name.endswith("events.jsonl") and f"_{TASK}_{REPEAT}_{arm}/" in m.name)
        return [json.loads(line) for line in tar.extractfile(name).read().decode("utf-8").splitlines()]


def steps(events, cause):
    """One record per planner decision: what was proposed, what ran, what came back."""
    out, cur, spent, belief, status = [], None, 0, None, None
    for e in events:
        k = e["kind"]
        if k == "planner_request":
            ranks = e["request"].get("action_rankings")
            cur = {"ranks": {r["action_id"]: r["score"] for r in ranks} if ranks is not None else None,
                   "no_legal": ranks == [], "belief_before": belief}
            out.append(cur)
        elif k == "planner_decision":
            d = e["decision"]
            cur["kind"], cur["proposed"] = d["kind"], d.get("action_id") or d.get("hypothesis")
            cur["cited"] = d.get("evidence_ids")
        elif k == "action_blocked":
            cur["blocked"] = e["reason"]
        elif k == "prediction_registered":
            cur["ran"], cur["cost"] = e["action"]["id"], e["action"]["cost"]
            spent += e["action"]["cost"]
            cur["spent"] = spent
        elif k == "observation":
            cur["obs"], cur["outcome"] = e["observation"]["id"], e["observation"]["outcome"]
        elif k == "evidence_update":
            belief = e["evidence"]["after"][cause]
            cur["belief"] = belief
        elif k == "independent_verification":
            cur["verified"] = e["passed"]
        elif k == "run_finished":
            status = e["result"]["status"]
    for s in out:
        s.setdefault("belief", s["belief_before"])
    return out, status


def gather():
    with (RUN / "outcomes.jsonl").open(encoding="utf-8") as stream:
        rows = [json.loads(line) for line in stream]
    cause = next(r for r in rows if r["task_id"] == TASK)["cause"]
    runs = {}
    for arm in ARMS:
        s, status = steps(journal(arm), cause)
        runs[arm] = {"steps": s, "status": status,
                     "verified_total": sum(r["verified_simulation"] for r in rows if r["arm"] == arm),
                     "n": sum(1 for r in rows if r["arm"] == arm)}
    return cause, runs


# ---------------------------------------------------------------- svg primitives
parts = []


def add(s):
    parts.append(s)


def text(x, y, s, fit, size=LABEL, weight=400, anchor="start", color=INK, family=SERIF, style="normal", raw=False):
    body = s if raw else escape(s)
    add(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
        f'font-style="{style}" fill="{color}" text-anchor="{anchor}" data-fit="{fit[0]:.1f},{fit[1]:.1f}">{body}</text>')


def rect(x, y, w, h, fill, stroke="none", sw=0, rx=0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w, 0):.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" '
        f'stroke="{stroke}" stroke-width="{sw}"{d}/>')


def line(x1, y1, x2, y2, color, sw=1.5, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{sw}"{d}/>')


def check(x, y, color, s=1.0):
    add(f'<path d="M{x:.1f},{y:.1f} l{7 * s:.1f},{8 * s:.1f} l{14 * s:.1f},{-17 * s:.1f}" fill="none" '
        f'stroke="{color}" stroke-width="{3 * s:.1f}" stroke-linecap="round" stroke-linejoin="round"/>')


def belief_txt(p):
    return "≈1" if p >= 0.995 else f"{p:.2f}"[1:]


# ---------------------------------------------------------------- figure
def build(cause, runs):
    step_count = max(len(runs[a]["steps"]) for a in ARMS)
    ROW = 48
    Y_ROWS = 336
    H = Y_ROWS + step_count * ROW + 172
    add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
    add(f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>')

    L0, L1 = 48, 740          # Memory-only column
    S0, S1 = 740, 796         # step spine
    R0, R1 = 796, 1488        # HESP column

    # ---- shared setting (identical for both runs)
    case = SecTriageEnvironment.STATE_FIELDS["case"]
    add(f'<text x="48" y="64" font-family="{SERIF}" font-size="{TITLE}" fill="{INK}" data-fit="48,1488">'
        f'<tspan font-weight="700">Alert {escape(case)}</tspan>'
        f'<tspan fill="{INK2}" font-size="{LABEL}">   spike in authentication failures and 4xx/5xx errors '
        f'on the web tier, last hour</tspan></text>')
    add(f'<text x="48" y="102" font-family="{SERIF}" font-size="{SMALL}" fill="{INK2}" data-fit="48,1488">'
        f'{len(HYPOTHESES) - 1} candidate causes + other; hidden true cause '
        f'<tspan font-family="{MONO}" font-size="{CODE}" fill="{RED}">{escape(cause)}</tspan></text>')
    text(48, 132, "Both runs: the same Qwen2.5-7B planner, read-only probes, budget (10 cost units, 12 decisions) "
         "and independent verifier", (48, 1488), SMALL, color=INK2)
    line(48, 156, 1488, 156, RULE, 1.2)

    # ---- column headers
    text(L0, 202, "The planner chooses every probe", (L0, L1), TITLE, 700, color=INK)
    text(L0, 236, "Memory-only: π reads the evidence ledger and", (L0, L1), SMALL, color=INK2)
    text(L0, 264, "picks the next probe itself.", (L0, L1), SMALL, color=INK2)
    text(R0, 202, "The controller chooses, the planner concludes", (R0, R1), TITLE, 700, color=BLUE)
    add(f'<text x="{R0}" y="236" font-family="{SERIF}" font-size="{SMALL}" fill="{INK2}" data-fit="{R0},{R1}">'
        f'HESP: probes are picked by argmax EIG/<tspan font-style="italic">c</tspan> over legal, unseen probes;</text>')
    text(R0, 264, "π proposes and concludes; a guard and the verifier check the verdict.", (R0, R1), SMALL,
         color=INK2)

    # sub-column anchors (same offsets in both columns)
    def cols(c0):
        return {"chip": c0 + 4, "eig": c0 + 446, "cost": c0 + 506, "spent": c0 + 548, "used_r": c0 + 604,
                "bar": c0 + 614, "bar_w": 50, "val": c0 + 692}
    for c0, c1, hesp in ((L0, L1, False), (R0, R1, True)):
        k = cols(c0)
        y = Y_ROWS - 26
        text(k["chip"], y, "probe → observed outcome", (c0, k["eig"] - 8), SMALL - 1, color=MUTED, style="italic")
        if hesp:
            text(k["eig"], y, "EIG/c", (k["eig"] - 6, k["cost"] - 4), SMALL - 1, color=BLUE, style="italic")
        text(k["cost"], y, "cost", (k["cost"] - 4, k["spent"] - 2), SMALL - 1, color=MUTED, style="italic")
        text(k["used_r"], y, "used", (k["spent"] - 4, k["bar"] - 2), SMALL - 1, anchor="end", color=MUTED,
             style="italic")
        add(f'<text x="{k["val"]}" y="{y}" font-family="{SERIF}" font-size="{SMALL - 1}" fill="{MUTED}" '
            f'font-style="italic" text-anchor="end" data-fit="{k["bar"] - 4},{c1 + 4}">'
            f'p(<tspan font-family="{MONO}" font-size="{CODE - 4}" font-style="normal">h</tspan>*)</text>')
        line(c0, Y_ROWS - 14, c1, Y_ROWS - 14, RULE, 1.2)
    text((S0 + S1) / 2, Y_ROWS - 26, "step", (S0 - 4, S1 + 4), SMALL - 1, anchor="middle", color=MUTED,
         style="italic")

    # ---- decision rows
    for i in range(step_count):
        y = Y_ROWS + i * ROW
        if i % 2 == 0:
            rect(L0, y, R1 - L0, ROW, "#F9FAFB")
        text((S0 + S1) / 2, y + 32, str(i + 1), (S0, S1), SMALL, anchor="middle", color=MUTED)

    for arm, c0, c1, hesp in ((ARMS[0], L0, L1, False), (ARMS[1], R0, R1, True)):
        k = cols(c0)
        cited_ids = {c for s in runs[arm]["steps"] if s.get("kind") == "finish" for c in (s.get("cited") or [])}
        for i, s in enumerate(runs[arm]["steps"]):
            y = Y_ROWS + i * ROW
            base = y + 32
            if s.get("kind") == "finish":
                ok = s.get("verified")
                w = len("finish") * 12.2 + 20
                rect(k["chip"], y + 7, w, ROW - 14, GREEN_TINT if ok else RED_TINT, GREEN if ok else RED, 1.5, 4)
                text(k["chip"] + 10, base, "finish", (k["chip"] + 4, k["chip"] + w), CODE, 700,
                     family=MONO, color=GREEN if ok else RED)
                ox = k["chip"] + w + 10
                add(f'<text x="{ox:.1f}" y="{base}" font-family="{SERIF}" font-size="{SMALL}" fill="{INK2}" '
                    f'data-fit="{ox - 2:.1f},{k["eig"] - 6}">→ <tspan font-family="{MONO}" font-size="{CODE}" '
                    f'font-weight="700" fill="{GREEN if ok else RED}">{escape(s["proposed"])}</tspan> '
                    f'<tspan font-style="italic">with</tspan> <tspan font-style="italic" fill="{GREEN}">E</tspan></text>')
                if hesp and s.get("no_legal"):
                    text(k["eig"] + 50, base, "none", (k["eig"] - 4, k["cost"] + 30), SMALL - 1, anchor="end",
                         color=BLUE, style="italic")
            elif s.get("blocked"):
                w = len(s["proposed"]) * 12.2 + 20
                rect(k["chip"], y + 7, w, ROW - 14, RED_TINT, RED, 1.4, 4, dash="5 3")
                text(k["chip"] + 10, base, s["proposed"], (k["chip"] + 4, k["chip"] + w), CODE, family=MONO,
                     color=RED)
                line(k["chip"] + 8, base - 7, k["chip"] + w - 8, base - 7, RED, 1.6)
                text(k["chip"] + w + 12, base, "repeat, blocked", (k["chip"] + w + 8, k["eig"] - 6), SMALL - 1,
                     color=RED, style="italic")
            elif s.get("ran"):
                w = len(s["ran"]) * 12.2 + 20
                rect(k["chip"], y + 7, w, ROW - 14, BLUE_TINT if hesp else "#FFFFFF", BLUE if hesp else INK2, 1.4, 4)
                text(k["chip"] + 10, base, s["ran"], (k["chip"] + 4, k["chip"] + w), CODE, family=MONO,
                     color=BLUE if hesp else INK)
                ox = k["chip"] + w + 10
                arrow_out = f'→ <tspan font-family="{MONO}" font-size="{CODE}">{escape(s["outcome"])}</tspan>'
                add(f'<text x="{ox:.1f}" y="{base}" font-family="{SERIF}" font-size="{SMALL}" fill="{INK2}" '
                    f'data-fit="{ox - 2:.1f},{(k["eig"] if hesp else k["cost"]) - 6}">{arrow_out}</text>')
                if s.get("obs") in cited_ids:
                    ex = ox + 34 + len(s["outcome"]) * 12.2
                    text(ex, base, "E", (ex - 2, k["eig"] - 6), SMALL, 700, color=GREEN, style="italic")
                if hesp and s["proposed"] and s["proposed"] != s["ran"]:
                    # the planner asked for something else; the controller ran the EIG/c choice
                    ax = ox + 34 + len(s["outcome"]) * 12.2
                    add(f'<text x="{ax:.1f}" y="{base}" font-family="{SERIF}" font-size="{SMALL - 1}" '
                        f'fill="{MUTED}" font-style="italic" data-fit="{ax - 2:.1f},{k["eig"] - 6}">π: '
                        f'<tspan font-family="{MONO}" font-style="normal" font-size="{CODE - 1}" '
                        f'text-decoration="line-through">{escape(s["proposed"])}</tspan></text>')
                if hesp and s["ranks"] is not None:
                    text(k["eig"] + 50, base, f"{s['ranks'][s['ran']]:.2f}", (k["eig"] - 4, k["cost"] - 4),
                         SMALL - 1, anchor="end", color=BLUE)
                for p in range(s["cost"]):
                    rect(k["cost"] + p * 13, y + 17, 9, 14, INK2, rx=1)
                text(k["used_r"], base, f"{s['spent']}/10", (k["spent"] - 4, k["bar"] - 2), SMALL - 1,
                     anchor="end", color=RED if s["spent"] >= 10 else MUTED)
            else:   # a probe the controller refused because the budget was spent
                w = len(s["proposed"]) * 12.2 + 20
                rect(k["chip"], y + 7, w, ROW - 14, "#FFFFFF", RED, 1.4, 4, dash="5 3")
                text(k["chip"] + 10, base, s["proposed"], (k["chip"] + 4, k["chip"] + w), CODE, family=MONO, color=RED)
                text(k["chip"] + w + 12, base, "refused: budget spent", (k["chip"] + w + 8, k["eig"] - 6),
                     SMALL - 1, color=RED, style="italic")
            b = s.get("belief")
            if b is not None:
                rect(k["bar"], y + 17, k["bar_w"], 14, TRACK, rx=2)
                rect(k["bar"], y + 17, k["bar_w"] * b, 14, BLUE if hesp else INK2, rx=2)
                text(k["val"], base, belief_txt(b), (k["bar"] + k["bar_w"] + 2, c1 + 4), SMALL - 1, anchor="end",
                     color=INK)

    # ---- how each run ends
    yb = Y_ROWS + step_count * ROW + 22
    for arm, c0, c1, hesp in ((ARMS[0], L0, L1, False), (ARMS[1], R0, R1, True)):
        r = runs[arm]
        ok = r["status"] == "VERIFIED_SIMULATION"
        rect(c0, yb, c1 - c0, 118, GREEN_TINT if ok else "#F3F4F6", GREEN if ok else "#9CA3AF", 1.5, 6)
        if ok:
            check(c0 + 20, yb + 36, GREEN)
            text(c0 + 52, yb + 44, "Verdict passes the guard and the verifier", (c0 + 48, c1 - 12), LABEL, 700,
                 color=GREEN)
        else:
            text(c0 + 20, yb + 44, "No verdict: budget spent, no conclusion", (c0 + 16, c1 - 12), LABEL, 700,
                 color=INK2)
        text(c0 + 20, yb + 78, f"Qwen2.5-7B over all 24 alerts × 3 repeats: {r['verified_total']}/{r['n']} "
             f"verified", (c0 + 16, c1 - 12), SMALL, color=INK2)
        if not ok:
            first = next(i for i, s in enumerate(r["steps"]) if (s.get("belief") or 0) > 0.9)
            text(c0 + 20, yb + 106, f"p(h*) passed .9 at step {first + 1}; "
                 f"{sum(1 for s in r['steps'] if s.get('blocked'))} steps lost to repeats",
                 (c0 + 16, c1 - 12), SMALL - 1, color=MUTED, style="italic")
        else:
            text(c0 + 20, yb + 106, "no legal probe left → π concludes and the check passes",
                 (c0 + 16, c1 - 12), SMALL - 1, color=MUTED, style="italic")
    add("</svg>")
    return H


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    cause, runs = gather()
    build(cause, runs)
    OUT.write_bytes(("\n".join(parts) + "\n").encode("utf-8"))
    print(OUT)
    for arm in ARMS:
        r = runs[arm]
        print(arm, r["status"], "steps", len(r["steps"]), f"| {r['verified_total']}/{r['n']} verified")
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
