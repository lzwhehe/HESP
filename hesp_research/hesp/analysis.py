"""Paired task-cluster summaries; fixture results never establish efficacy."""

from collections import Counter, defaultdict
import random
import statistics

from .controller import MODES


def summarize(rows, bootstrap_samples=2000, seed=42):
    if not rows:
        raise ValueError("Cannot analyze an empty study")
    if isinstance(bootstrap_samples, bool) or not isinstance(bootstrap_samples, int) or bootstrap_samples < 1:
        raise ValueError("bootstrap_samples must be a positive integer")
    cells = {}
    groups = defaultdict(list)
    for row in rows:
        key = (row["task_id"], row["repeat"], row["mode"])
        if key in cells or row["mode"] not in MODES:
            raise ValueError("Duplicate study cell or unknown mode")
        if type(row["verified_simulation"]) is not bool:
            raise ValueError("Verification outcome must be boolean")
        cells[key] = row
        groups[row["mode"]].append(row)
    pairs = {(task, repeat) for task, repeat, _ in cells}
    if any((task, repeat, mode) not in cells for task, repeat in pairs for mode in MODES):
        raise ValueError("Incomplete paired study; restore missing outcomes before analysis")
    summaries = {}
    for mode in MODES:
        values = groups[mode]
        summaries[mode] = {
            "runs": len(values),
            "verified_fraction": statistics.mean(r["verified_simulation"] for r in values),
            "statuses": dict(Counter(r["status"] for r in values)),
        }
        for metric in ("tool_calls", "tool_cost_units", "planner_calls", "wall_seconds",
                       "reported_input_tokens", "reported_output_tokens"):
            known = [r[metric] for r in values if r.get(metric) is not None]
            summaries[mode][metric] = {
                "mean_known": statistics.mean(known) if known else None,
                "unknown_runs": len(values) - len(known),
            }
    comparisons = {}
    for baseline in ("react_style", "memory_only"):
        per_task = defaultdict(list)
        for task, repeat in sorted(pairs):
            per_task[task].append(int(cells[task, repeat, "hesp"]["verified_simulation"])
                                  - int(cells[task, repeat, baseline]["verified_simulation"]))
        # Each task receives equal weight, regardless of repeats.
        differences = [statistics.mean(per_task[t]) for t in sorted(per_task)]
        rng = random.Random(seed)
        interval = None
        if len(differences) > 1:
            samples = sorted(statistics.mean(rng.choices(differences, k=len(differences)))
                             for _ in range(bootstrap_samples))
            interval = [samples[int((bootstrap_samples - 1) * .025)],
                        samples[int((bootstrap_samples - 1) * .975)]]
        comparisons["hesp_minus_" + baseline] = {
            "task_clusters": len(differences), "difference": statistics.mean(differences),
            "cluster_bootstrap_percentile_95": interval,
        }
    return {
        "purpose": "synthetic_software_validation_only", "research_claim_allowed": False,
        "warning": "Fixture repetitions are deterministic; intervals are pipeline checks, not efficacy evidence.",
        "bootstrap_samples": bootstrap_samples, "bootstrap_seed": seed,
        "modes": summaries, "paired_verification": comparisons,
    }
