"""Regenerate the v0.5 primary-endpoint table from the raw outcomes.

The v0.5 tables in RESULTS.md / README.md / CHANGELOG.md were originally filled in by hand,
which is how the "all three intervals exclude 0" error got in: the 72B interval's lower bound
is exactly 0.  This script is the single source of truth for those numbers -- run it and paste
its Markdown, never retype the values.

    python scripts/v05_summary.py                 # Markdown to stdout
    python scripts/v05_summary.py --json out.json
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hesp.analysis import summarize

ARMS = ["react_style", "memory_only", "memory_guard", "hesp_eigc", "hesp_eigc_guard",
        "hesp_la", "hesp_la_guard", "hesp_random", "hesp_llmp"]
# Pre-registered primary endpoint first; the rest are exploratory decomposition.
COMPARISONS = [("hesp_eigc_guard", "memory_only"),
               ("hesp_eigc", "hesp_random"),
               ("hesp_random", "memory_only"),
               ("memory_only", "react_style")]
MODELS = [("7b", "Qwen2.5-7B"), ("32b", "Qwen2.5-32B-AWQ"), ("72b", "Qwen2.5-72B-AWQ")]
FAMILY = "sec-triage"
SEED = 2026


def analyze(results, model):
    rows = [json.loads(line) for line in (results / f"v05_{model}/outcomes.jsonl").open(encoding="utf-8")]
    rows = [r for r in rows if r.get("family") == FAMILY]
    return summarize(rows, seed=SEED, arms=ARMS, comparisons=COMPARISONS), len(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--results", default=str(Path(__file__).resolve().parents[1] / "results"))
    parser.add_argument("--json", help="also write the full numbers here")
    args = parser.parse_args()
    results = Path(args.results)
    out, lines = {}, []
    for model, label in MODELS:
        summary, n = analyze(results, model)
        out[model] = {"episodes": n, "arms": {a: summary["modes"][a]["verified_fraction"] for a in ARMS},
                      "paired_verification": summary["paired_verification"]}
    key = "hesp_eigc_guard_minus_memory_only"
    lines += [f"Pre-registered primary endpoint ({key}, {FAMILY}, 24 task clusters, "
              f"2000 bootstrap resamples, seed {SEED})", "",
              "| Model | delta verified | 95% cluster interval | tasks better / worse |",
              "| --- | ---: | --- | ---: |"]
    for model, label in MODELS:
        v = out[model]["paired_verification"][key]
        lo, hi = v["cluster_bootstrap_percentile_95"]
        lines.append(f"| {label} | {v['difference']:+.4f} | [{lo:.4f}, {hi:.4f}] | "
                     f"{v['tasks_better']} / {v['tasks_worse']} |")
    for tag, title in [("hesp_eigc_minus_hesp_random", "EIG/cost ranking vs random controller picks"),
                       ("hesp_random_minus_memory_only", "controller picking at all vs the planner picking")]:
        lines += ["", f"Exploratory: {title} ({tag})", "",
                  "| Model | delta verified | 95% cluster interval |", "| --- | ---: | --- |"]
        for model, label in MODELS:
            v = out[model]["paired_verification"][tag]
            lo, hi = v["cluster_bootstrap_percentile_95"]
            lines.append(f"| {label} | {v['difference']:+.4f} | [{lo:.4f}, {hi:.4f}] |")
    print("\n".join(lines))
    if args.json:
        Path(args.json).write_text(json.dumps(out, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
