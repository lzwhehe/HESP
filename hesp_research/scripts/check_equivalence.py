"""Behavioural fingerprint of the controller on LLM-free episodes.

Runs every sec-triage task (base/drift/noise) under scripted planners and the arm
configurations used by earlier studies, then hashes the per-episode results with the
volatile fields removed. Run it before and after a change to ``hesp/``: equal digests mean
the existing arms behave identically (PROTOCOL.md: implementation checks before freezing).

    python scripts/check_equivalence.py --tables results/v06_tables
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hesp.controller import Budget, run
from hesp.planner import NeverFinishPlanner, PosteriorPlanner
from hesp.predictors import FrozenPredictor
from hesp.secapp import make_sec_env, sec_suite
from hesp.selectors import Selector
from hesp.study import cell_seed

VOLATILE = {"wall_seconds", "source_sha256", "finished_by"}
CONFIGS = {
    "memory_only": {"mode": "memory_only"},
    "memory_only_autostop": {"mode": "memory_only", "auto_finish": 0.8},
    "hesp_eigc_guard": {"mode": "hesp", "selector": "eig_cost", "finish_guard": True},
    "hesp_eigc_blind": {"mode": "hesp", "selector": "eig_cost", "show_rankings": False},
    "hesp_eigc_blind_autostop": {"mode": "hesp", "selector": "eig_cost", "show_rankings": False,
                                 "auto_finish": 0.8},
    "hesp_random_blind_autostop": {"mode": "hesp", "selector": "random", "show_rankings": False,
                                   "auto_finish": 0.8},
}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tables", default=str(Path(__file__).resolve().parents[1] / "results/v06_tables"))
    ap.add_argument("--seed", type=int, default=700000)
    args = ap.parse_args()
    tables = json.loads((Path(args.tables) / "empirical_20.json").read_text(encoding="utf-8"))["tables"]
    predictor = FrozenPredictor(tables, "empirical_20")
    budget = Budget(max_tool_calls=10, max_decisions=12, max_tool_cost=10, max_seconds=900.0)
    planners = {"posterior": lambda: PosteriorPlanner(0.9), "never": NeverFinishPlanner}
    digest, n = hashlib.sha256(), 0
    with tempfile.TemporaryDirectory() as tmp:
        for task in sec_suite():
            for pname, make_planner in planners.items():
                for cname, cfg in CONFIGS.items():
                    s = cell_seed(args.seed, task["task_id"], 0)
                    with make_sec_env(task, s) as env:
                        result = run(env, make_planner(), cfg["mode"], Path(tmp) / f"{task['task_id']}_{pname}_{cname}",
                                     budget, predictor=predictor, selector=Selector(cfg.get("selector", "eig_cost"), s),
                                     finish_guard=cfg.get("finish_guard", False),
                                     show_rankings=cfg.get("show_rankings", True), auto_finish=cfg.get("auto_finish"))
                    row = {k: v for k, v in result.items() if k not in VOLATILE}
                    digest.update(json.dumps([task["task_id"], pname, cname, row], sort_keys=True).encode())
                    n += 1
    print(f"{n} episodes, digest {digest.hexdigest()}")


if __name__ == "__main__":
    main()
