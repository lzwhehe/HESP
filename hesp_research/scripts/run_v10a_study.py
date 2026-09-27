"""v1.0 part A: the v0.9 arms on the external sigma-triage family (PROTOCOL.md v1.0).

Five arms, as in v0.9, every one scoring and selecting with the same frozen per-rule counted tables
(empirical_20); no ranking is shown to the planner.

  memory_only                  the LLM probes, the LLM stops
  memory_only_autostop         the LLM probes, the controller may stop
  hesp_eigc_blind              the controller probes by EIG/cost, the LLM stops
  hesp_eigc_blind_autostop     the controller probes by EIG/cost, the controller may stop
  hesp_random_blind_autostop   the controller probes at random, the controller may stop

Primary endpoints (Qwen2.5-7B; 98.33 % rule-cluster intervals, see v10a_summary.py):
  PA1 hesp_eigc_blind_autostop - hesp_random_blind_autostop
  PA2 hesp_eigc_blind_autostop - memory_only

    python scripts/run_v10a_study.py --output results/v10a_qwen7b --model qwen2.5-7b-instruct
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
from hesp.sigmaapp import RuleTablePredictor, SigmaEnvironments, sigma_suite
from hesp.study import run_suite
from suite_report import write_report
from v10a_tables import load_specs

TABLE = "empirical_20"
AUTO_FINISH = 0.8
COMPARISONS = [
    ("hesp_eigc_blind_autostop", "hesp_random_blind_autostop"),   # PA1: ranking under controller stop
    ("hesp_eigc_blind_autostop", "memory_only"),                  # PA2: full effect
    ("hesp_eigc_blind_autostop", "hesp_eigc_blind"),              # controller stop, controller probes
    ("hesp_eigc_blind_autostop", "memory_only_autostop"),         # who probes, stop supplied
    ("memory_only_autostop", "memory_only"),                      # controller stop, LLM probes
]


def load_tables(table_dir):
    index = json.loads((table_dir / "index.json").read_text(encoding="utf-8"))
    path = table_dir / index[TABLE]["file"]
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != index[TABLE]["sha256"]:
        raise SystemExit(f"{TABLE}: SHA256 mismatch against index.json -- table changed after freezing")
    return json.loads(path.read_text(encoding="utf-8")), digest


def main():
    here = Path(__file__).resolve().parents[1]
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--output", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--backend", choices=("vllm", "ollama"), default="vllm")
    ap.add_argument("--base-url", default="http://127.0.0.1:8000/v1")
    ap.add_argument("--specs", default=str(here / "results/v10a/specs"))
    ap.add_argument("--tables", default=str(here / "results/v10a/tables"))
    ap.add_argument("--repeats", type=int, default=2)
    ap.add_argument("--seed", type=int, default=2028)
    ap.add_argument("--temperature", type=float, default=0.2)
    ap.add_argument("--workers", type=int, default=32)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--task-stride", type=int, default=1, help="smoke tests only")
    args = ap.parse_args()
    specs, spec_index = load_specs(args.specs)
    record, digest = load_tables(Path(args.tables))
    if record["specs_index_sha256"] != hashlib.sha256((Path(args.specs) / "index.json").read_bytes()).hexdigest():
        raise SystemExit("tables were counted from a different set of specs")
    predictor = RuleTablePredictor(record["tables"], TABLE)
    envs = SigmaEnvironments(specs)
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
    tasks = sigma_suite(specs)[::args.task_stride]
    budget = Budget(max_tool_calls=10, max_decisions=12, max_tool_cost=10, max_seconds=900.0)
    start = time.time()

    def progress(i, n, row):
        if i % 50 == 0 or i == n:
            print(f"[{i}/{n}] {row['task_id']} {row['arm']} {row['status']} "
                  f"(~{(time.time() - start) / i * (n - i) / 60:.0f} min left)", flush=True)
    report, _ = run_suite(Path(args.output), tasks, arms, envs, repeats=args.repeats, seed=args.seed,
                          budget=budget, comparisons=COMPARISONS, resume=args.resume, progress=progress,
                          workers=args.workers, purpose="v1.0_part_a",
                          extra_manifest={"model": client.info(), "temperature": args.temperature,
                                          "families": ["sigma-triage"], "primary_family": "sigma-triage",
                                          "sigma_commit": spec_index["sigma_commit"],
                                          "specs": spec_index["accepted"], "annotator": spec_index["annotator"],
                                          "table": {"name": TABLE, "sha256": digest}})
    write_report(Path(args.output) / "report.md", f"v1.0 part A · {args.model} · sigma-triage", report)
    print(f"done in {(time.time() - start) / 60:.1f} min")


if __name__ == "__main__":
    main()
