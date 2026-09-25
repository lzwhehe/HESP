"""Regenerate every v0.8 number from results/v08_*/outcomes.jsonl (PROTOCOL.md v0.8).

Primary endpoints use 97.5 % task-cluster bootstrap intervals (Bonferroni over two);
everything else is exploratory with 95 % intervals. Never retype these numbers by hand.

    python scripts/v08_summary.py --json results/v08_summary.json > results/v08_summary.md
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
from hesp.analysis import security_metrics, true_cause   # noqa: E402

MODELS = [("qwen7b", "Qwen2.5-7B"), ("qwen32b", "Qwen2.5-32B-AWQ"), ("qwen72b", "Qwen2.5-72B-AWQ"),
          ("llama8b", "Llama-3.1-8B"), ("llama70b", "Llama-3.1-70B-AWQ")]
ARMS = ["memory_only", "hesp_random_blind", "hesp_eigc_blind", "hesp_eigc", "hesp_eigc_guard"]
TERMS = [("hesp_eigc_guard", "memory_only", "HESP vs Memory-only"),
         ("hesp_random_blind", "memory_only", "hand probe choice to controller"),
         ("hesp_eigc_blind", "hesp_random_blind", "EIG/c ranking itself"),
         ("hesp_eigc", "hesp_eigc_blind", "show ranking to planner"),
         ("hesp_eigc_guard", "hesp_eigc", "finish guard")]
PRIMARY = {("llama8b", "hesp_eigc_guard", "memory_only"): "P1", ("qwen7b", "hesp_eigc_blind", "hesp_random_blind"): "P2"}
SEED, RESAMPLES = 2026, 2000


def paired(rows, a, b, level):
    """Mean per-task difference in verified completion and its percentile task-cluster interval."""
    cells = {(r["task_id"], r["repeat"], r["arm"]): r for r in rows}
    per_task = collections.defaultdict(list)
    for (task, rep, arm) in cells:
        if arm == a and (task, rep, b) in cells:
            per_task[task].append(int(cells[(task, rep, a)]["verified_simulation"])
                                  - int(cells[(task, rep, b)]["verified_simulation"]))
    diffs = [statistics.mean(v) for _, v in sorted(per_task.items())]
    rng = random.Random(SEED)
    draws = sorted(statistics.mean(rng.choices(diffs, k=len(diffs))) for _ in range(RESAMPLES))
    tail = (1 - level) / 2
    lo, hi = draws[int((RESAMPLES - 1) * tail)], draws[int((RESAMPLES - 1) * (1 - tail))]
    return {"difference": statistics.mean(diffs), "ci": [lo, hi], "level": level, "tasks": len(diffs),
            "better": sum(d > 0 for d in diffs), "worse": sum(d < 0 for d in diffs)}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--results", default=str(ROOT / "results"))
    ap.add_argument("--json")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    data, L = {}, []
    for key, label in MODELS:
        path = Path(args.results) / f"v08_{key}" / "outcomes.jsonl"
        if not path.exists():
            continue
        with path.open(encoding="utf-8") as f:
            rows = [json.loads(line) for line in f]
        bad = [r for r in rows if r["verified_simulation"] and r["claimed_hypothesis"] != true_cause(r)]
        if bad:
            raise SystemExit(f"{key}: {len(bad)} verified rows disagree with true_cause")
        by_arm = collections.defaultdict(list)
        for r in rows:
            by_arm[r["arm"]].append(r)
        data[key] = {
            "label": label, "episodes": len(rows), "source_hashes": sorted({r["source_sha256"][:8] for r in rows}),
            "verified": {a: statistics.mean(r["verified_simulation"] for r in by_arm[a]) for a in ARMS if by_arm[a]},
            "tool_cost": {a: statistics.mean(r["tool_cost_units"] for r in by_arm[a]) for a in ARMS if by_arm[a]},
            "terms": {f"{a} - {b}": {**paired(rows, a, b, 0.975 if (key, a, b) in PRIMARY else 0.95), "name": name}
                      for a, b, name in TERMS},
            "security": {a: security_metrics(by_arm[a]) for a in ARMS if by_arm[a]},
        }
    L += ["### Primary endpoints (97.5 % task-cluster intervals, Bonferroni over two)", "",
          "| Endpoint | Model | Comparison | Δ verified | 97.5 % interval | tasks better / worse | confirmed |",
          "| --- | --- | --- | ---: | --- | ---: | --- |"]
    for (key, a, b), tag in PRIMARY.items():
        if key in data:
            t = data[key]["terms"][f"{a} - {b}"]
            L.append(f"| {tag} | {data[key]['label']} | {a} − {b} | {t['difference']:+.3f} | "
                     f"[{t['ci'][0]:+.3f}, {t['ci'][1]:+.3f}] | {t['better']} / {t['worse']} | "
                     f"{'yes' if t['ci'][0] > 0 else 'no'} |")
    L += ["", "### Verified completion by arm", "", "| Arm | " + " | ".join(d["label"] for d in data.values()) + " |",
          "| --- |" + " ---: |" * len(data)]
    for a in ARMS:
        L.append(f"| {a} | " + " | ".join(f"{d['verified'].get(a, float('nan')):.3f}" for d in data.values()) + " |")
    L += ["", "### Mean probe cost by arm", "", "| Arm | " + " | ".join(d["label"] for d in data.values()) + " |",
          "| --- |" + " ---: |" * len(data)]
    for a in ARMS:
        L.append(f"| {a} | " + " | ".join(f"{d['tool_cost'].get(a, float('nan')):.2f}" for d in data.values()) + " |")
    L += ["", "### Decomposition (Δ verified; 95 % intervals except the two primary cells, which are 97.5 %)", "",
          "| Term | " + " | ".join(d["label"] for d in data.values()) + " |", "| --- |" + " --- |" * len(data)]
    for a, b, name in TERMS:
        cells = []
        for d in data.values():
            t = d["terms"][f"{a} - {b}"]
            cells.append(f"{t['difference']:+.3f} [{t['ci'][0]:+.3f}, {t['ci'][1]:+.3f}]")
        L.append(f"| {name} | " + " | ".join(cells) + " |")
    L += ["", "### Security-facing metrics (descriptive): missed attack / false escalation / unresolved", "",
          "| Arm | " + " | ".join(d["label"] for d in data.values()) + " |", "| --- |" + " --- |" * len(data)]
    fmt = lambda x: "n/a" if x is None else f"{x:.2f}"
    for a in ARMS:
        cells = [f"{fmt(s['missed_attack_rate'])} / {fmt(s['false_escalation_rate'])} / {fmt(s['unresolved_rate'])}"
                 for s in (d["security"].get(a) for d in data.values()) if s]
        L.append(f"| {a} | " + " | ".join(cells) + " |")
    print("\n".join(L))
    if args.json:
        Path(args.json).write_bytes((json.dumps(data, indent=1) + "\n").encode("utf-8"))


if __name__ == "__main__":
    main()
