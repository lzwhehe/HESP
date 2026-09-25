"""v0.7 part B: local LLM planner on a sample of GUIDE cold-start test incidents (PROTOCOL.md v0.7).

300 cold-start test incidents (seed 2026) x 3 arms x 1 repeat, local Ollama qwen2.5:7b-instruct.
Per-incident outputs carry GUIDE grades, so they are written outside the repository (the licence is
not yet confirmed); only aggregate summaries are committed.

  memory_only       the LLM picks every facet
  hesp_eigc         the controller picks by EIG/cost; the LLM proposes and concludes
  hesp_eigc_guard   as above, verdict released only at posterior >= 0.8 (else escalated)

    python scripts/run_v07_guide_llm.py --history ../external/guide_incidents_train.jsonl \
        --test ../external/guide_incidents_test.jsonl --output ../external/v07/llm_7b
"""
import argparse
import json
from pathlib import Path
import random
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hesp.controller import Budget
from hesp.guideapp import GuideModel, GuideTriageEnvironment, load_incidents
from hesp.llm import LLMPlanner, OllamaClient, OpenAICompatClient
from hesp.study import run_suite

SEED, SAMPLE = 2026, 300


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--history", required=True)
    ap.add_argument("--test", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--model", default="qwen2.5:7b-instruct")
    ap.add_argument("--backend", choices=("ollama", "vllm"), default="ollama")
    ap.add_argument("--base-url", default="http://127.0.0.1:8000/v1")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--sample", type=int, default=SAMPLE)
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    model = GuideModel(load_incidents(args.history))
    cold = sorted((r for r in load_incidents(args.test) if model.cold_kind(r)),
                  key=lambda r: (r["org"], r["incident"]))
    sample = random.Random(SEED).sample(cold, min(args.sample, len(cold)))
    by_id = {f"guide-{r['org']}-{r['incident']}": r for r in sample}
    tasks = [{"task_id": tid, "family": "guide", "variant": model.cold_kind(r), "cause": r["grade"],
              "drift_to": None, "org": r["org"]} for tid, r in by_id.items()]
    client = (OllamaClient(args.model) if args.backend == "ollama"
              else OpenAICompatClient(args.model, args.base_url))
    planner = lambda seed: LLMPlanner(client, seed=seed, temperature=0.2)
    arms = {"memory_only": {"mode": "memory_only", "planner": planner},
            "hesp_eigc": {"mode": "hesp", "planner": planner, "selector": "eig_cost"},
            "hesp_eigc_guard": {"mode": "hesp", "planner": planner, "selector": "eig_cost", "finish_guard": True}}
    budget = Budget(max_tool_calls=4, max_decisions=8, max_tool_cost=4, max_seconds=600.0)
    start = time.time()

    def progress(i, n, row):
        if i % 20 == 0 or i == n:
            print(f"[{i}/{n}] {row['arm']} {row['status']} (~{(time.time() - start) / i * (n - i) / 60:.0f} min left)",
                  flush=True)
    report, _ = run_suite(Path(args.output), tasks, arms, lambda task, seed: GuideTriageEnvironment(by_id[task["task_id"]], model),
                          repeats=1, seed=SEED, budget=budget,
                          comparisons=[("hesp_eigc", "memory_only"), ("hesp_eigc_guard", "hesp_eigc")],
                          resume=args.resume, progress=progress, workers=args.workers, purpose="v0.7_guide_llm",
                          extra_manifest={"model": args.model, "backend": args.backend, "sample": len(sample),
                                          "n_cold": len(cold)})
    print(json.dumps({a: v["verified_fraction"] for a, v in report["modes"].items()}, indent=1))
    print(f"done in {(time.time() - start) / 60:.1f} min")


if __name__ == "__main__":
    main()
