"""Paired task-cluster summaries. Fixture/scripted results never establish efficacy."""

from collections import Counter, defaultdict
import random
import statistics

from .controller import MODES

METRICS = ("tool_calls", "tool_cost_units", "planner_calls", "wall_seconds",
           "reported_input_tokens", "reported_output_tokens")


def arm_of(row):
    return row.get("arm") or row["mode"]


def _bootstrap(values, samples, seed):
    if len(values) < 2:
        return None
    rng = random.Random(seed)
    draws = sorted(statistics.mean(rng.choices(values, k=len(values))) for _ in range(samples))
    return [draws[int((samples - 1) * .025)], draws[int((samples - 1) * .975)]]


def summarize(rows, bootstrap_samples=2000, seed=42, arms=None, comparisons=None):
    """Summarize a complete paired study.

    ``arms`` defaults to the three modes; ``comparisons`` is a list of (treatment, baseline)
    pairs. Differences are computed per task (mean over repeats), so each task cluster has
    equal weight, and intervals are percentile bootstraps over task clusters.
    """
    if not rows:
        raise ValueError("Cannot analyze an empty study")
    if isinstance(bootstrap_samples, bool) or not isinstance(bootstrap_samples, int) or bootstrap_samples < 1:
        raise ValueError("bootstrap_samples must be a positive integer")
    arms = tuple(arms or MODES)
    if comparisons is None:
        comparisons = [("hesp", "react_style"), ("hesp", "memory_only")] if set(MODES) <= set(arms) else []
    cells = {}
    groups = defaultdict(list)
    for row in rows:
        key = (row["task_id"], row["repeat"], arm_of(row))
        if key in cells or key[2] not in arms:
            raise ValueError("Duplicate study cell or unknown arm")
        if type(row["verified_simulation"]) is not bool:
            raise ValueError("Verification outcome must be boolean")
        cells[key] = row
        groups[key[2]].append(row)
    pairs = {(task, repeat) for task, repeat, _ in cells}
    if any((task, repeat, arm) not in cells for task, repeat in pairs for arm in arms):
        raise ValueError("Incomplete paired study; restore missing outcomes before analysis")
    summaries = {}
    for arm in arms:
        values = groups[arm]
        summaries[arm] = {
            "runs": len(values),
            "verified_fraction": statistics.mean(r["verified_simulation"] for r in values),
            "statuses": dict(Counter(r["status"] for r in values)),
        }
        for metric in METRICS:
            known = [r[metric] for r in values if r.get(metric) is not None]
            summaries[arm][metric] = {"mean_known": statistics.mean(known) if known else None,
                                      "unknown_runs": len(values) - len(known)}
        solved = [r["tool_cost_units"] for r in values if r["verified_simulation"]]
        summaries[arm]["tool_cost_when_verified"] = statistics.mean(solved) if solved else None
    paired, paired_cost = {}, {}
    for treatment, baseline in comparisons:
        per_task, per_task_cost = defaultdict(list), defaultdict(list)
        for task, repeat in sorted(pairs):
            t, b = cells[task, repeat, treatment], cells[task, repeat, baseline]
            per_task[task].append(int(t["verified_simulation"]) - int(b["verified_simulation"]))
            per_task_cost[task].append(t["tool_cost_units"] - b["tool_cost_units"])
        differences = [statistics.mean(per_task[t]) for t in sorted(per_task)]
        cost_diffs = [statistics.mean(per_task_cost[t]) for t in sorted(per_task_cost)]
        name = f"{treatment}_minus_{baseline}"
        paired[name] = {"task_clusters": len(differences), "difference": statistics.mean(differences),
                        "cluster_bootstrap_percentile_95": _bootstrap(differences, bootstrap_samples, seed),
                        "tasks_better": sum(d > 0 for d in differences),
                        "tasks_worse": sum(d < 0 for d in differences)}
        paired_cost[name] = {"task_clusters": len(cost_diffs), "difference": statistics.mean(cost_diffs),
                             "cluster_bootstrap_percentile_95": _bootstrap(cost_diffs, bootstrap_samples, seed)}
    return {
        "purpose": "synthetic_software_validation_only", "research_claim_allowed": False,
        "warning": "Fixture repetitions are deterministic; intervals are pipeline checks, not efficacy evidence.",
        "bootstrap_samples": bootstrap_samples, "bootstrap_seed": seed, "arms": list(arms),
        "modes": summaries, "paired_verification": paired, "paired_tool_cost": paired_cost,
    }
