"""Sensitivity of every sec-triage primary endpoint to the clustering unit and to drift (review, 2026-09-29).

The pre-registered intervals resample the 24 sec-triage tasks. Those tasks are 8 causes x 3 variants that share
one generator, so this script recomputes each primary endpoint (a) with the pre-registered task clusters, as a
check against the reported numbers, (b) with the 8 causes (6 for the adversarial endpoint) as clusters, and
(c) separately on the base, noise, and drift variants, where drift makes the cause switch after the second
probe. Exploratory; nothing here replaces a pre-registered result.

    python scripts/cause_sensitivity.py --json results/cause_sensitivity.json > results/cause_sensitivity.md
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
from hesp.secapp import BENIGN   # noqa: E402

RESAMPLES = 2000


def load(rel):
    return [json.loads(line) for line in (ROOT / "results" / rel).open(encoding="utf-8")]


def verified(r):
    return float(bool(r["verified_simulation"]))


def attack_success(r):
    return float(r["claimed_hypothesis"] in BENIGN and r["cause"] not in BENIGN)


# (label, rows loader, arm a, arm b, metric, level, variants filter); seeds per study in SEEDS
SEEDS = {"v0.9": 2027, "v1.0-C": 2028, "v1.1": 2029}   # all others: 2026

ENDPOINTS = [
    ("v0.5 Q-7B full HESP - Memory-only", lambda: load("v05_7b/outcomes.jsonl"), "hesp_eigc_guard", "memory_only", verified, 0.95, None),
    ("v0.5 Q-32B full HESP - Memory-only", lambda: load("v05_32b/outcomes.jsonl"), "hesp_eigc_guard", "memory_only", verified, 0.95, None),
    ("v0.5 Q-72B full HESP - Memory-only", lambda: load("v05_72b/outcomes.jsonl"), "hesp_eigc_guard", "memory_only", verified, 0.95, None),
    ("v0.6 Q-7B counted tables - Memory-only", lambda: load("v06_7b/outcomes.jsonl"), "hesp_eigc_guard_emp20", "memory_only", verified, 0.95, None),
    ("v0.8 Q-7B ranking (blind EIG - blind random)", lambda: load("v08_qwen7b/outcomes.jsonl"), "hesp_eigc_blind", "hesp_random_blind", verified, 0.975, None),
    ("v0.8 L-8B full HESP - Memory-only", lambda: load("v08_llama8b/outcomes.jsonl"), "hesp_eigc_guard", "memory_only", verified, 0.975, None),
    ("v0.9 L-8B controller stop", lambda: load("v09_llama8b/outcomes.jsonl"), "hesp_eigc_blind_autostop", "hesp_eigc_blind", verified, 0.975, None),
    ("v0.9 L-8B selection given stop", lambda: load("v09_llama8b/outcomes.jsonl"), "hesp_eigc_blind_autostop", "memory_only_autostop", verified, 0.975, None),
    ("v1.0-C Q-7B injection attack success (Mem. - HESP)", lambda: load("v10c_qwen7b/outcomes.jsonl"), "memory_only", "hesp_guard_autostop", attack_success, 1 - 0.05 / 3, ("inject",)),
]


def cause_of(r, causes_by_task):
    return r.get("cause") or causes_by_task[r["task_id"]]


def interval(values, level, seed):
    rng = random.Random(seed)
    draws = sorted(statistics.mean(rng.choices(values, k=len(values))) for _ in range(RESAMPLES))
    tail = (1 - level) / 2
    return [draws[int((RESAMPLES - 1) * tail)], draws[int((RESAMPLES - 1) * (1 - tail))]]


def contrast(rows, a, b, metric, level, variants=None, unit="task", seed=2026):
    cells = {(r["task_id"], r["repeat"], r["arm"]): r for r in rows}
    per = collections.defaultdict(list)
    for (task, rep, arm), r in cells.items():
        if arm != a or (task, rep, b) not in cells:
            continue
        if variants and r["variant"] not in variants:
            continue
        key = task if unit == "task" else r["cause"]
        per[key].append(metric(r) - metric(cells[task, rep, b]))
    # a cause-level mean weights every task of that cause equally, so average within tasks first
    if unit == "cause":
        per_task = collections.defaultdict(list)
        for (task, rep, arm), r in cells.items():
            if arm == a and (task, rep, b) in cells and (not variants or r["variant"] in variants):
                per_task[(r["cause"], task)].append(metric(r) - metric(cells[task, rep, b]))
        per = collections.defaultdict(list)
        for (cause, task), v in per_task.items():
            per[cause].append(statistics.mean(v))
    means = [statistics.mean(v) for _, v in sorted(per.items())]
    if not means:
        return None
    return {"difference": statistics.mean(means), "ci": interval(means, level, seed) if len(means) > 1 else None,
            "clusters": len(means), "level": level}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    out = {}
    L = ["# Clustering and drift sensitivity of the sec-triage primary endpoints (exploratory)", "",
         "| Endpoint | Task clusters (as reported) | Cause clusters | Base | Noise | Drift |",
         "| --- | --- | --- | ---: | ---: | ---: |"]

    def fmt(c):
        if c is None:
            return "--"
        if c["ci"] is None:
            return f"{c['difference']:+.3f}"
        return f"{c['difference']:+.3f} [{c['ci'][0]:+.2f}, {c['ci'][1]:+.2f}] ({c['clusters']})"
    for label, loader, a, b, metric, level, variants in ENDPOINTS:
        rows = loader()
        seed = SEEDS.get(label.split()[0], 2026)
        res = {"task": contrast(rows, a, b, metric, level, variants, "task", seed),
               "cause": contrast(rows, a, b, metric, level, variants, "cause", seed)}
        for v in ("base", "noise", "drift"):
            res[v] = contrast(rows, a, b, metric, level, (v,) if not variants else tuple(x for x in variants if x == v) or ("__none__",), "task")
        out[label] = res
        L.append(f"| {label} | {fmt(res['task'])} | {fmt(res['cause'])} | "
                 + " | ".join(f"{res[v]['difference']:+.3f}" if res[v] else "--" for v in ("base", "noise", "drift")) + " |")
    # PE1-sec: the LLM-free reference has no 'cause' column in the same file, so pair it here explicitly
    llm = [r for r in load("v11e2_sec_qwen72b/outcomes.jsonl") if r["arm"] == "hesp_guard"]
    cause_by_task = {r["task_id"]: r["cause"] for r in llm}
    ref = {}
    for line in (ROOT / "results" / "v11d" / "episodes.jsonl").open(encoding="utf-8"):
        e = json.loads(line)
        if e["group"] == "D1" and e["family"] == "sec" and e["config"] == "eig_confirm":
            ref[(e["task_id"], e["repeat"])] = float(e["outcome"] == "verified")
    rows = [dict(r, arm="llm") for r in llm] + [{"task_id": t, "repeat": rep, "arm": "ref", "variant": t.split("-")[1],
                                                 "cause": cause_by_task[t], "verified_simulation": bool(v)}
                                                for (t, rep), v in ref.items()]
    res = {"task": contrast(rows, "llm", "ref", verified, 0.975, None, "task", 2029),
           "cause": contrast(rows, "llm", "ref", verified, 0.975, None, "cause", 2029)}
    for v in ("base", "noise", "drift"):
        res[v] = contrast(rows, "llm", "ref", verified, 0.975, (v,), "task")
    out["v1.1 PE1-sec Q-72B LLM stop - LLM-free confirmation"] = res
    L.append("| v1.1 PE1-sec Q-72B LLM stop - LLM-free confirmation | " + fmt(res["task"]) + " | " + fmt(res["cause"]) + " | "
             + " | ".join(f"{res[v]['difference']:+.3f}" if res[v] else "--" for v in ("base", "noise", "drift")) + " |")
    L += ["", "Levels follow each study's protocol (95 %, 97.5 %, or 98.33 %); cause clusters average tasks within a cause first."]
    print("\n".join(L))
    if args.json:
        Path(args.json).write_text(json.dumps(out, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
