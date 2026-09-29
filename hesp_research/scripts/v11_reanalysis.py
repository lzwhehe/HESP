"""v1.1 re-analysis of existing outcome files (review R6); no new episodes.

1. Security outcomes of the table-source study with explicit numerators and denominators: claimed
   verdicts, benign verdicts on actionable cases (over verdicts AND over all actionable episodes),
   not-verified vs no-verdict.
2. Sensitivity of the confirmed primary endpoints to the clustering unit: task clusters (as
   pre-registered), cause clusters (sec-triage: 8 causes), and leave-one-rule-out for sigma-triage.
3. Per-investigation latency: p50 and p95 wall time, planner calls, and completion tokens per episode
   for the recommended configuration of each model.

    python scripts/v11_reanalysis.py --json results/v11_reanalysis.json > results/v11_reanalysis.md
"""
import argparse
import collections
import json
from pathlib import Path
import random
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hesp.analysis import true_cause   # noqa: E402

BENIGN_SEC = {"authorized_scan", "false_positive_monitor"}
SEED, RESAMPLES = 2029, 2000


def load(d):
    return [json.loads(l) for l in (ROOT / "results" / d / "outcomes.jsonl").open(encoding="utf-8")]


def pct(values, q):
    values = sorted(values)
    k = (len(values) - 1) * q
    lo, hi = int(k), min(int(k) + 1, len(values) - 1)
    return values[lo] + (values[hi] - values[lo]) * (k - lo)


def cluster_ci(rows, a, b, cluster_of, level, metric=lambda r: int(r["verified_simulation"])):
    cells = {(r["task_id"], r["repeat"], r["arm"]): r for r in rows}
    per_task = collections.defaultdict(list)
    for (t, rep, arm), r in cells.items():
        if arm == a and (t, rep, b) in cells:
            per_task[t].append(metric(r) - metric(cells[t, rep, b]))
    clusters = collections.defaultdict(list)
    for t, v in per_task.items():
        clusters[cluster_of(t)].append(statistics.mean(v))
    keys = sorted(clusters)
    point = statistics.mean(d for k in keys for d in clusters[k])
    rng = random.Random(SEED)
    draws = sorted(statistics.mean(d for k in rng.choices(keys, k=len(keys)) for d in clusters[k])
                   for _ in range(RESAMPLES))
    tail = (1 - level) / 2
    return {"difference": point, "ci": [draws[int((RESAMPLES - 1) * tail)], draws[int((RESAMPLES - 1) * (1 - tail))]],
            "clusters": len(keys), "level": level}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    out, L = {}, ["# v1.1 re-analysis of existing outcomes (review R6)", ""]

    # 1 ---------------------------------------------------------------- security counts (v0.6)
    L += ["## 1. Table-source study: security outcomes with numerators and denominators", "",
          "| Model | Arm | Episodes | Verdicts | Not verified | No verdict | Actionable eps | Benign verdict on actionable | over verdicts | over all actionable |",
          "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    out["security"] = {}
    for key, label in (("7b", "Qwen2.5-7B"), ("32b", "Qwen2.5-32B"), ("72b", "Qwen2.5-72B")):
        rows = load(f"v06_{key}")
        for arm in ("react_style", "memory_only", "hesp_eigc_guard_emp20"):
            rs = [r for r in rows if r["arm"] == arm]
            verdicts = [r for r in rs if r["claimed_hypothesis"] is not None]
            act = [r for r in rs if true_cause(r) not in BENIGN_SEC]
            act_verdicts = [r for r in act if r["claimed_hypothesis"] is not None]
            missed = [r for r in act_verdicts if r["claimed_hypothesis"] in BENIGN_SEC]
            rec = {"episodes": len(rs), "verdicts": len(verdicts),
                   "not_verified": sum(not r["verified_simulation"] for r in rs),
                   "no_verdict": len(rs) - len(verdicts), "actionable": len(act),
                   "actionable_with_verdict": len(act_verdicts), "missed": len(missed)}
            out["security"][f"{key}/{arm}"] = rec
            L.append(f"| {label} | {arm} | {rec['episodes']} | {rec['verdicts']} | {rec['not_verified']} | {rec['no_verdict']} | "
                     f"{rec['actionable']} | {rec['missed']} | {rec['missed']}/{rec['actionable_with_verdict']} | "
                     f"{rec['missed']}/{rec['actionable']} |")
    L.append("")

    # 2 ---------------------------------------------------------------- clustering sensitivity
    L += ["## 2. Sensitivity of confirmed primary endpoints to the clustering unit", "",
          "| Endpoint | Pre-registered (task clusters) | Cause clusters | Clusters |", "| --- | --- | --- | ---: |"]
    out["sensitivity"] = {}
    specs = [("v0.6 7B counted vs Memory-only", "v06_7b", "hesp_eigc_guard_emp20", "memory_only", 0.95),
             ("v0.8 ranking Q-7B", "v08_qwen7b", "hesp_eigc_blind", "hesp_random_blind", 0.975),
             ("v0.9 P1 controller stop L-8B", "v09_llama8b", "hesp_eigc_blind_autostop", "hesp_eigc_blind", 0.975),
             ("v1.0 PC injection Q-7B", "v10c_qwen7b", "memory_only", "hesp_guard_autostop", 1 - 0.05 / 3)]
    for name, d, a, b, level in specs:
        rows = load(d)
        if d.startswith("v10c"):
            rows = [r for r in rows if r["variant"] == "inject"]
            metric = lambda r: int(r["claimed_hypothesis"] in BENIGN_SEC)
        else:
            metric = lambda r: int(r["verified_simulation"])
        cause_of = {r["task_id"]: r.get("cause") for r in rows}
        task = cluster_ci(rows, a, b, lambda t: t, level, metric)
        cause = cluster_ci(rows, a, b, lambda t: cause_of[t], level, metric)
        out["sensitivity"][name] = {"task": task, "cause": cause}
        L.append(f"| {name} | {task['difference']:+.3f} [{task['ci'][0]:+.3f}, {task['ci'][1]:+.3f}] ({task['clusters']}) | "
                 f"{cause['difference']:+.3f} [{cause['ci'][0]:+.3f}, {cause['ci'][1]:+.3f}] | {cause['clusters']} |")
    L.append("")
    L += ["### Leave-one-rule-out, sigma-triage primary endpoints (Qwen2.5-7B)", "",
          "| Endpoint | Full | Min over left-out rule | Max over left-out rule |", "| --- | ---: | ---: | ---: |"]
    rows = load("v10a_qwen7b")
    rules = sorted({r["rule"] for r in rows})
    out["loro"] = {}
    for name, a, b in (("PA1 ranking", "hesp_eigc_blind_autostop", "hesp_random_blind_autostop"),
                       ("PA2 full", "hesp_eigc_blind_autostop", "memory_only")):
        full = cluster_ci(rows, a, b, lambda t: t, 0.95)["difference"]
        loo = [cluster_ci([r for r in rows if r["rule"] != rule], a, b, lambda t: t, 0.95)["difference"] for rule in rules]
        out["loro"][name] = {"full": full, "min": min(loo), "max": max(loo)}
        L.append(f"| {name} | {full:+.3f} | {min(loo):+.3f} | {max(loo):+.3f} |")
    L.append("")

    # 3 ---------------------------------------------------------------- latency
    L += ["## 3. Per-investigation latency (v0.9 controller probes + controller stop; v1.0-A same arm)", "",
          "| Study | Model | p50 s | p95 s | mean planner calls | mean completion tokens |", "| --- | --- | ---: | ---: | ---: | ---: |"]
    out["latency"] = {}
    for d, arm in [(f"v09_{m}", "hesp_eigc_blind_autostop") for m in ("qwen7b", "llama8b", "qwen32b", "qwen72b", "llama70b")] + \
                  [(f"v10a_{m}", "hesp_eigc_blind_autostop") for m in ("qwen7b", "llama8b", "qwen32b", "qwen72b", "llama70b")]:
        rs = [r for r in load(d) if r["arm"] == arm]
        w = [r["wall_seconds"] for r in rs]
        tok = [r["reported_output_tokens"] for r in rs if r["reported_output_tokens"] is not None]
        rec = {"p50": pct(w, 0.5), "p95": pct(w, 0.95), "calls": statistics.mean(r["planner_calls"] for r in rs),
               "tokens": statistics.mean(tok) if tok else None, "episodes": len(rs)}
        out["latency"][d] = rec
        L.append(f"| {d.split('_')[0]} | {d.split('_')[1]} | {rec['p50']:.1f} | {rec['p95']:.1f} | {rec['calls']:.2f} | "
                 f"{rec['tokens']:.0f} |" if rec["tokens"] is not None else f"| {d} | | | | | |")
    L += ["", "Wall time was measured with 32 concurrent episodes sharing one GPU, so it includes queueing."]
    print("\n".join(L))
    if args.json:
        Path(args.json).write_text(json.dumps(out, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
