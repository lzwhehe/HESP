"""Selector ablation in the web sandbox with a model-free planner, swept over tool budgets.

Every arm uses the same deterministic PosteriorPlanner (finish at posterior >= 0.9 with
current-state supporting evidence). Only *who picks the probe, and how* differs:

  sequential     memory_only; the planner proposes probes in fixed catalogue order
  eig_cost       HESP controller, EIG / cost            (designer table)
  eig            HESP controller, EIG ignoring cost     (designer table)
  map_greedy     HESP controller, confirm the MAP cause (designer table)
  random         HESP controller, random legal probe
  lookahead      HESP controller, budget-aware depth-3 expectimax of the max posterior (v0.3.1)
  eig_cost_llmP  HESP controller, EIG / cost with frozen LLM-elicited P(o|h,a)

This isolates the selection rule; it says nothing about LLM planners by itself.
"""
import argparse
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hesp.controller import Budget
from hesp.planner import PosteriorPlanner
from hesp.predictors import FrozenPredictor
from hesp.study import run_suite
from hesp.webapp import make_web_env, web_suite
from suite_report import write_report

BUDGETS = (2, 3, 4, 5, 6, 8, 10)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output", required=True)
    parser.add_argument("--elicitation", help="elicitation.json; adds the eig_cost_llmP arm")
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--budgets", type=int, nargs="+", default=list(BUDGETS))
    args = parser.parse_args()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=False)
    planner = lambda seed: PosteriorPlanner(0.9)
    arms = {"sequential": {"mode": "memory_only", "planner": planner}}
    for sel in ("eig_cost", "eig", "map_greedy", "random", "lookahead"):
        arms[sel] = {"mode": "hesp", "planner": planner, "selector": sel}
    if args.elicitation:
        e = json.loads(Path(args.elicitation).read_text(encoding="utf-8"))
        arms["eig_cost_llmP"] = {"mode": "hesp", "planner": planner, "selector": "eig_cost",
                                 "predictor": FrozenPredictor(e["tables"], e["source"])}
    comparisons = [("eig_cost", a) for a in arms if a != "eig_cost"] + [("lookahead", "eig"), ("lookahead", "sequential")]
    curve, start = {}, time.time()
    for b in args.budgets:
        budget = Budget(max_tool_calls=b, max_decisions=b + 6, max_tool_cost=b, max_seconds=60.0)
        report, rows = run_suite(out / f"budget_{b:02d}", web_suite(), arms, make_web_env, repeats=args.repeats,
                                 seed=args.seed, budget=budget, comparisons=comparisons,
                                 purpose="scripted_selector_ablation")
        write_report(out / f"budget_{b:02d}" / "report.md", f"Selector ablation, tool budget {b}", report)
        by_variant = {}
        for variant in ("base", "drift", "noise"):
            by_variant[variant] = {arm: sum(r["verified_simulation"] for r in rows
                                            if r["arm"] == arm and r["variant"] == variant)
                                   / sum(1 for r in rows if r["arm"] == arm and r["variant"] == variant)
                                   for arm in arms}
        curve[b] = {"overall": {a: v["verified_fraction"] for a, v in report["modes"].items()},
                    "mean_cost": {a: v["tool_cost_units"]["mean_known"] for a, v in report["modes"].items()},
                    "by_variant": by_variant,
                    "paired_vs_eig_cost": report["paired_verification"]}
        print(f"budget {b:>2}: " + "  ".join(f"{a}={v:.3f}" for a, v in curve[b]["overall"].items()), flush=True)
    (out / "curve.json").write_text(json.dumps({"budgets": args.budgets, "repeats": args.repeats,
                                                "seed": args.seed, "arms": list(arms), "curve": curve,
                                                "research_claim_allowed": False}, indent=2), encoding="utf-8")
    print(f"done in {time.time() - start:.0f}s")


if __name__ == "__main__":
    main()
