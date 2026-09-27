"""v0.8 study: clean selector decomposition and a second model family (PROTOCOL.md v0.8).

Five arms, every one scoring and selecting with the same frozen empirical_20 table:

  memory_only        the LLM picks every probe
  hesp_random_blind  the controller picks at random; the planner sees no ranking
  hesp_eigc_blind    the controller picks by EIG/cost; the planner sees no ranking
  hesp_eigc          as above, ranking shown to the planner
  hesp_eigc_guard    as above, plus the state-guarded finish (v0.6's main arm)

Primary endpoints (Bonferroni, 97.5 % intervals): P1 hesp_eigc_guard - memory_only on
Llama-3.1-8B; P2 hesp_eigc_blind - hesp_random_blind on Qwen2.5-7B.

    python scripts/run_v08_study.py --output results/v08_qwen7b --model qwen2.5-7b-instruct
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
COMPARISONS = [
    ("hesp_eigc_guard", "memory_only"),          # P1 on Llama-3.1-8B; reported for every model
    ("hesp_eigc_blind", "hesp_random_blind"),    # P2 on Qwen2.5-7B: ranking effect, planner info identical
    ("hesp_random_blind", "memory_only"),        # handing probe choice to the controller
    ("hesp_eigc", "hesp_eigc_blind"),            # showing the ranking to the planner
    ("hesp_eigc_guard", "hesp_eigc"),            # the finish guard
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
    ap.add_argument("--seed", type=int, default=2026)
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
    arms = {
        "memory_only": {**base, "mode": "memory_only"},
        "hesp_random_blind": {**base, "mode": "hesp", "selector": "random", "show_rankings": False},
        "hesp_eigc_blind": {**base, "mode": "hesp", "selector": "eig_cost", "show_rankings": False},
        "hesp_eigc": {**base, "mode": "hesp", "selector": "eig_cost"},
        "hesp_eigc_guard": {**base, "mode": "hesp", "selector": "eig_cost", "finish_guard": True},
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
                          resume=args.resume, progress=progress, workers=args.workers, purpose="v0.8_study",
                          extra_manifest={"model": client.info(), "temperature": args.temperature,
                                          "families": ["sec-triage"], "primary_family": "sec-triage",
                                          "table": {"name": TABLE, "sha256": digest}})
    write_report(Path(args.output) / "report.md", f"v0.8 · {args.model} · sec-triage", report)
    print(f"done in {(time.time() - start) / 60:.1f} min")


if __name__ == "__main__":
    main()
