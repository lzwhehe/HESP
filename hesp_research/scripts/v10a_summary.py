"""Regenerate every v1.0 part A number from results/v10a_*/outcomes.jsonl (PROTOCOL.md v1.0).

Primary endpoints (Qwen2.5-7B; 98.33 % intervals, Bonferroni over PA1, PA2, PC), bootstrapped over
RULES (12 clusters: every task of a rule is resampled together, which is more conservative than
task clusters):
  PA1 hesp_eigc_blind_autostop - hesp_random_blind_autostop
  PA2 hesp_eigc_blind_autostop - memory_only
Everything else is exploratory with 95 % intervals. Never retype these numbers by hand.

    python scripts/v10a_summary.py --json results/v10a_summary.json > results/v10a_summary.md
"""
import argparse
import collections
import json
from pathlib import Path
import random
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
MODELS = [("qwen7b", "Qwen2.5-7B"), ("llama8b", "Llama-3.1-8B"), ("qwen32b", "Qwen2.5-32B-AWQ"),
          ("qwen72b", "Qwen2.5-72B-AWQ"), ("llama70b", "Llama-3.1-70B-AWQ")]
ARMS = ["memory_only", "memory_only_autostop", "hesp_eigc_blind", "hesp_eigc_blind_autostop",
        "hesp_random_blind_autostop"]
TERMS = [("hesp_eigc_blind_autostop", "hesp_random_blind_autostop", "PA1 ranking under controller stop"),
         ("hesp_eigc_blind_autostop", "memory_only", "PA2 full effect"),
         ("hesp_eigc_blind_autostop", "hesp_eigc_blind", "controller stop (controller probes)"),
         ("hesp_eigc_blind_autostop", "memory_only_autostop", "who probes, stop supplied"),
         ("memory_only_autostop", "memory_only", "controller stop (LLM probes)")]
PRIMARY = {("qwen7b", TERMS[0][0], TERMS[0][1]), ("qwen7b", TERMS[1][0], TERMS[1][1])}
SEED, RESAMPLES = 2028, 2000


def paired_by_rule(rows, a, b, level):
    """Mean per-task difference in verified completion; percentile bootstrap over rules."""
    cells = {(r["task_id"], r["repeat"], r["arm"]): r for r in rows}
    per_task = collections.defaultdict(list)
    rule_of = {}
    for (task, rep, arm), r in cells.items():
        if arm == a and (task, rep, b) in cells:
            per_task[task].append(int(r["verified_simulation"]) - int(cells[task, rep, b]["verified_simulation"]))
            rule_of[task] = r["rule"]
    by_rule = collections.defaultdict(list)
    for task, v in per_task.items():
        by_rule[rule_of[task]].append(statistics.mean(v))
    rules = sorted(by_rule)
    point = statistics.mean(d for r in rules for d in by_rule[r])
    rng = random.Random(SEED)
    draws = []
    for _ in range(RESAMPLES):
        pick = rng.choices(rules, k=len(rules))
        draws.append(statistics.mean(d for r in pick for d in by_rule[r]))
    draws.sort()
    tail = (1 - level) / 2
    return {"difference": point, "ci": [draws[int((RESAMPLES - 1) * tail)], draws[int((RESAMPLES - 1) * (1 - tail))]],
            "level": level, "rules": len(rules), "tasks": len(per_task),
            "tasks_better": sum(statistics.mean(v) > 0 for v in per_task.values()),
            "tasks_worse": sum(statistics.mean(v) < 0 for v in per_task.values())}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--results", default=str(ROOT / "results"))
    ap.add_argument("--json")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    data, L = {}, ["# v1.0 part A - external sigma-triage family", ""]
    for key, label in MODELS:
        path = Path(args.results) / f"v10a_{key}" / "outcomes.jsonl"
        if not path.exists():
            continue
        rows = [json.loads(line) for line in path.open(encoding="utf-8")]
        bad = [r for r in rows if r["verified_simulation"] and r["claimed_hypothesis"] != r["cause"]]
        if bad:
            raise SystemExit(f"{key}: {len(bad)} verified rows disagree with the task cause")
        by_arm = collections.defaultdict(list)
        for r in rows:
            by_arm[r["arm"]].append(r)

        def rate(rs, f):
            return statistics.mean(f(r) for r in rs) if rs else None
        data[key] = {
            "label": label, "episodes": len(rows), "source_hashes": sorted({r["source_sha256"][:8] for r in rows}),
            "verified": {a: rate(by_arm[a], lambda r: r["verified_simulation"]) for a in ARMS},
            "tool_cost": {a: rate(by_arm[a], lambda r: r["tool_cost_units"]) for a in ARMS},
            # benign causes are every cause except "attack"; a missed attack is a benign verdict on an attack task
            "missed_attack": {a: rate([r for r in by_arm[a] if r["cause"] == "attack"],
                                      lambda r: (r["claimed_hypothesis"] or "").startswith("benign_")) for a in ARMS},
            "wrong_cause": {a: rate(by_arm[a], lambda r: r["claimed_hypothesis"] not in (None, "other", r["cause"]))
                            for a in ARMS},
            "finished_by": {a: dict(collections.Counter(str(r.get("finished_by")) for r in by_arm[a])) for a in ARMS},
            "terms": {f"{a} - {b}": {**paired_by_rule(rows, a, b, 1 - 0.05 / 3 if (key, a, b) in PRIMARY else 0.95),
                                     "name": name} for a, b, name in TERMS},
        }
    if "qwen7b" in data:
        L += ["## Primary endpoints (Qwen2.5-7B; 98.33 % rule-cluster intervals)", ""]
        for a, b, name in TERMS[:2]:
            t = data["qwen7b"]["terms"][f"{a} - {b}"]
            L.append(f"- {name}: {a} - {b} = {t['difference']:+.3f} [{t['ci'][0]:+.3f}, {t['ci'][1]:+.3f}] "
                     f"({t['rules']} rules, {t['tasks']} tasks; {t['tasks_better']} better, {t['tasks_worse']} worse) -> "
                     f"{'CONFIRMED' if t['ci'][0] > 0 else 'not confirmed'}")
        L.append("")
    for key, d in data.items():
        L += [f"## {d['label']} ({d['episodes']} episodes, source {', '.join(d['source_hashes'])})", "",
              "| Arm | Verified | Cost | Missed attack | Wrong cause | Finished by |", "| --- | ---: | ---: | ---: | ---: | --- |"]
        for a in ARMS:
            if d["verified"][a] is None:
                continue
            L.append(f"| {a} | {d['verified'][a]:.3f} | {d['tool_cost'][a]:.2f} | {d['missed_attack'][a]:.3f} | "
                     f"{d['wrong_cause'][a]:.3f} | {d['finished_by'][a]} |")
        L += ["", "| Contrast | Difference | Interval |", "| --- | ---: | --- |"]
        for name, t in d["terms"].items():
            L.append(f"| {name} | {t['difference']:+.3f} | [{t['ci'][0]:+.3f}, {t['ci'][1]:+.3f}] ({t['level']:.2%}) |")
        L.append("")
    print("\n".join(L))
    if args.json:
        Path(args.json).write_text(json.dumps(data, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
