"""v0.9 study: who probes x who stops (PROTOCOL.md v0.9).

Five arms, every one scoring and selecting with the same frozen empirical_20 table; no ranking
is shown to the planner. "autostop" = the controller concludes by itself once the current-state
leader reaches 0.8 with supporting current-state evidence (the planner may still finish first).

  memory_only                  the LLM probes, the LLM stops
  memory_only_autostop         the LLM probes, the controller may stop
  hesp_eigc_blind              the controller probes by EIG/cost, the LLM stops
  hesp_eigc_blind_autostop     the controller probes by EIG/cost, the controller may stop
  hesp_random_blind_autostop   the controller probes at random, the controller may stop

Primary endpoints (Llama-3.1-8B, Bonferroni, 97.5 % intervals):
  P1 hesp_eigc_blind_autostop - hesp_eigc_blind
  P2 hesp_eigc_blind_autostop - memory_only_autostop

    python scripts/run_v09_study.py --output results/v09_llama8b --model llama-3.1-8b-instruct
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hesp.controller import Budget
from hesp.llm import LLMPlanner, OllamaClient, OpenAICompatClient
from hesp.predictors import FrozenPredictor
from hesp.secapp import make_sec_env, sec_suite
from hesp.study import run_suite
from suite_report import write_report

TABLE = "empirical_20"
AUTO_FINISH = 0.8   # the state-guarded finish threshold used since v0.4, not tuned for v0.9
COMPARISONS = [
    ("hesp_eigc_blind_autostop", "hesp_eigc_blind"),             # P1: controller stop, controller probes
    ("hesp_eigc_blind_autostop", "memory_only_autostop"),        # P2: who probes, once stopping is supplied
    ("memory_only_autostop", "memory_only"),                     # controller stop, LLM probes
    ("hesp_eigc_blind_autostop", "hesp_random_blind_autostop"),  # ranking effect under controller stop
    ("hesp_eigc_blind", "memory_only"),                          # replicates the earlier no-stop-help contrast
]


def load_table(table_dir):
    index = json.loads((table_dir / "index.json").read_text(encoding="utf-8"))
    path = table_dir / index[TABLE]["file"]
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != index[TABLE]["sha256"]:
        raise SystemExit(f"{TABLE}: SHA256 mismatch against index.json -- table changed after freezing")
    return json.loads(path.read_text(encoding="utf-8"))["tables"], digest


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--output", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--backend", choices=("vllm", "ollama"), default="vllm")
    ap.add_argument("--base-url", default="http://127.0.0.1:8000/v1")
    ap.add_argument("--tables", default=str(Path(__file__).resolve().parents[1] / "results/v06_tables"))
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--seed", type=int, default=2027)
    ap.add_argument("--temperature", type=float, default=0.2)
    ap.add_argument("--workers", type=int, default=32)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--task-stride", type=int, default=1, help="smoke tests only")
    args = ap.parse_args()
    tables, digest = load_table(Path(args.tables))
    predictor = FrozenPredictor(tables, TABLE)
    client = (OllamaClient(args.model) if args.backend == "ollama"
              else OpenAICompatClient(args.model, args.base_url))
    planner = lambda seed: LLMPlanner(client, seed=seed, temperature=args.temperature)
    base = {"planner": planner, "predictor": predictor}
    blind = {**base, "mode": "hesp", "show_rankings": False}
    arms = {
        "memory_only": {**base, "mode": "memory_only"},
        "memory_only_autostop": {**base, "mode": "memory_only", "auto_finish": AUTO_FINISH},
        "hesp_eigc_blind": {**blind, "selector": "eig_cost"},
        "hesp_eigc_blind_autostop": {**blind, "selector": "eig_cost", "auto_finish": AUTO_FINISH},
        "hesp_random_blind_autostop": {**blind, "selector": "random", "auto_finish": AUTO_FINISH},
    }
    tasks = sec_suite()[::args.task_stride]
    budget = Budget(max_tool_calls=10, max_decisions=12, max_tool_cost=10, max_seconds=900.0)
    start = time.time()

    def progress(i, n, row):
        if i % 20 == 0 or i == n:
            print(f"[{i}/{n}] {row['task_id']} {row['arm']} {row['status']} "
                  f"(~{(time.time() - start) / i * (n - i) / 60:.0f} min left)", flush=True)
    report, _ = run_suite(Path(args.output), tasks, arms, lambda task, seed: make_sec_env(task, seed),
                          repeats=args.repeats, seed=args.seed, budget=budget, comparisons=COMPARISONS,
                          resume=args.resume, progress=progress, workers=args.workers, purpose="v0.9_study",
                          extra_manifest={"model": client.info(), "temperature": args.temperature,
                                          "families": ["sec-triage"], "primary_family": "sec-triage",
                                          "table": {"name": TABLE, "sha256": digest}})
    write_report(Path(args.output) / "report.md", f"v0.9 · {args.model} · sec-triage", report)
    print(f"done in {(time.time() - start) / 60:.1f} min")


if __name__ == "__main__":
    main()
