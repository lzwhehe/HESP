"""LLM-free reference rows for v0.9 on the evaluation seeds (post hoc, exploratory; not pre-registered).

Replaces the LLM with ``NeverFinishPlanner`` (always proposes the next untried probe in
catalogue order, never finishes or stops) under the frozen v0.9 budget, table, seed and
task schedule, so the rows are directly comparable with results/v09_*:

  fixed_order_autostop        catalogue-order probing, controller stop
  controller_eigc_autostop    EIG/cost probing, controller stop (the controller alone)
  controller_random_autostop  random probing, controller stop

    python scripts/v09_llm_free_reference.py   # writes results/v09_llm_free_reference.json
"""
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hesp.controller import Budget  # noqa: E402
from hesp.planner import NeverFinishPlanner  # noqa: E402
from hesp.predictors import FrozenPredictor  # noqa: E402
from hesp.secapp import make_sec_env, sec_suite  # noqa: E402
from hesp.study import run_suite  # noqa: E402

sys.path.insert(0, str(ROOT / "scripts"))
from run_v09_study import AUTO_FINISH, load_table  # noqa: E402


def main():
    tables, digest = load_table(ROOT / "results/v06_tables")
    predictor = FrozenPredictor(tables, "empirical_20")
    base = {"planner": lambda seed: NeverFinishPlanner(), "predictor": predictor, "auto_finish": AUTO_FINISH}
    arms = {
        "fixed_order_autostop": {**base, "mode": "memory_only"},
        "controller_eigc_autostop": {**base, "mode": "hesp", "selector": "eig_cost", "show_rankings": False},
        "controller_random_autostop": {**base, "mode": "hesp", "selector": "random", "show_rankings": False},
    }
    budget = Budget(max_tool_calls=10, max_decisions=12, max_tool_cost=10, max_seconds=900.0)
    with tempfile.TemporaryDirectory() as root:
        report, rows = run_suite(Path(root) / "ref", sec_suite(), arms, lambda t, s: make_sec_env(t, s),
                                 repeats=3, seed=2027, budget=budget, workers=8, purpose="v0.9_llm_free_reference",
                                 comparisons=[("controller_eigc_autostop", "fixed_order_autostop"),
                                              ("controller_eigc_autostop", "controller_random_autostop")],
                                 extra_manifest={"table": {"name": "empirical_20", "sha256": digest}})
    out = {"note": "post hoc, exploratory; LLM replaced by NeverFinishPlanner; seed 2027, same tasks and budget as v0.9",
           "source_sha256": rows[0]["source_sha256"][:8], "episodes": len(rows),
           "verified": {a: sum(r["verified_simulation"] for r in rows if r["arm"] == a) / 72 for a in arms},
           "tool_cost": {a: sum(r["tool_cost_units"] for r in rows if r["arm"] == a) / 72 for a in arms},
           "comparisons": report.get("comparisons")}
    (ROOT / "results/v09_llm_free_reference.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("source_sha256", "episodes", "verified", "tool_cost")}, indent=1))


if __name__ == "__main__":
    main()
