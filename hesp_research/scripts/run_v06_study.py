"""v0.6 study (RQ3): does HESP survive without the near-oracle predictive table?

Pre-registered in docs/PROTOCOL.md (v0.6 section). The single independent variable is
where P(o|h,a) comes from; everything else -- model, prompt template, tools, budget,
exact dedup, verifier, finish guard -- is held fixed across the HESP arms.

  react_style                goal + tools + history; the LLM picks probes
  memory_only                + structured ledger; the LLM picks probes   (primary baseline)
  hesp_eigc_guard_designer   EIG/cost + guard, designer (near-oracle) table  -- upper bound
  hesp_eigc_guard_emp{k}     EIG/cost + guard, table counted from k dev episodes
  hesp_eigc_guard_llmp       EIG/cost + guard, the model's own elicited table -- lower bound

Primary endpoint: hesp_eigc_guard_emp20 - memory_only on sec-triage.

Empirical tables must already exist (scripts/estimate_empirical_tables.py); their SHA256
values are checked against index.json and written into the manifest before any episode.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hesp.analysis import summarize
from hesp.controller import Budget
from hesp.llm import LLMPlanner, OllamaClient, OpenAICompatClient
from hesp.predictors import FrozenPredictor, calibration
from hesp.secapp import SecTriageEnvironment, make_sec_env, sec_suite
from hesp.study import run_suite, write_json
from run_v04_study import elicit
from suite_report import write_report

FAMILY = "sec-triage"
K_LEVELS = (1, 5, 20, 100)
PRIMARY = ("hesp_eigc_guard_emp20", "memory_only")
COMPARISONS = [
    PRIMARY,                                                          # primary endpoint
    ("hesp_eigc_guard_emp1", "memory_only"),                          # data-efficiency curve
    ("hesp_eigc_guard_emp5", "memory_only"),
    ("hesp_eigc_guard_emp100", "memory_only"),
    ("hesp_eigc_guard_designer", "hesp_eigc_guard_emp20"),            # oracle gap
    ("hesp_eigc_guard_emp20", "hesp_eigc_guard_llmp"),                # vs the elicited lower bound
    ("hesp_eigc_guard_designer", "memory_only"),                      # anchor to v0.5's endpoint
    ("memory_only", "react_style"),
]


def load_tables(table_dir):
    """Load every empirical_k table and verify it matches the frozen index."""
    index = json.loads((table_dir / "index.json").read_text(encoding="utf-8"))
    tables, frozen = {}, {}
    for k in K_LEVELS:
        name = f"empirical_{k}"
        path = table_dir / index[name]["file"]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != index[name]["sha256"]:
            raise SystemExit(f"{name}: SHA256 mismatch against index.json -- table changed after freezing")
        record = json.loads(path.read_text(encoding="utf-8"))
        tables[k] = record["tables"]
        frozen[name] = {"file": path.name, "sha256": digest, "dev_episodes": record["dev_episodes"],
                        "cell_coverage": record["cell_coverage"],
                        "skipped_invalid_observations": record["skipped_invalid_observations"]}
    return tables, frozen


def table_calibration(tables):
    """Calibration of each empirical table against the generator, per variant (reporting only)."""
    env = SecTriageEnvironment
    ids = [p["id"] for p in env.PROBES]
    out = {}
    for k, t in tables.items():
        out[f"empirical_{k}"] = {
            variant: calibration(t, (lambda lag: (lambda a, h: env.true_outcome_distribution(a, h, lag)))(spec["lag"]),
                                 env.hypotheses_(), ids)
            for variant, spec in env.VARIANTS.items()}
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model", default="qwen2.5:7b-instruct")
    parser.add_argument("--backend", choices=("ollama", "vllm"), default="ollama")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000/v1")
    parser.add_argument("--tables", default=str(Path(__file__).resolve().parents[1] / "results/v06_tables"))
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--task-stride", type=int, default=1, help="smoke tests only: keep every k-th task")
    args = parser.parse_args()
    out = Path(args.output)

    tables, frozen = load_tables(Path(args.tables))
    client = (OllamaClient(args.model) if args.backend == "ollama"
              else OpenAICompatClient(args.model, args.base_url))
    elicitation, epath = elicit(client, out, args.seed, [FAMILY])
    llm_tables = elicitation["families"][FAMILY]["tables"]

    planner = lambda seed: LLMPlanner(client, seed=seed, temperature=args.temperature)
    guard = {"mode": "hesp", "planner": planner, "selector": "eig_cost", "finish_guard": True}
    arms = {
        "react_style": {"mode": "react_style", "planner": planner},
        "memory_only": {"mode": "memory_only", "planner": planner},
        "hesp_eigc_guard_designer": dict(guard),                    # predictor=None -> designer table
        **{f"hesp_eigc_guard_emp{k}": {**guard, "predictor": FrozenPredictor(tables[k], f"empirical_{k}")}
           for k in K_LEVELS},
        "hesp_eigc_guard_llmp": {**guard, "predictor": FrozenPredictor(llm_tables, elicitation["source"])},
    }
    tasks = sec_suite()[::args.task_stride]
    budget = Budget(max_tool_calls=10, max_decisions=12, max_tool_cost=10, max_seconds=900.0)
    start = time.time()

    def progress(i, n, row):
        if i % 10 == 0 or i == n:
            rate = (time.time() - start) / max(i, 1)
            print(f"[{i}/{n}] last={row['task_id']} {row['arm']} {row['status']} "
                  f"(~{rate * (n - i) / 60:.0f} min left)", flush=True)

    report, rows = run_suite(
        out, tasks, arms, lambda task, seed: make_sec_env(task, seed), repeats=args.repeats,
        seed=args.seed, budget=budget, comparisons=COMPARISONS, resume=args.resume,
        progress=progress, workers=args.workers, purpose="v0.6_rq3_study",
        extra_manifest={"model": elicitation["model"], "temperature": args.temperature,
                        "families": [FAMILY], "primary_family": FAMILY,
                        "primary_endpoint": f"{PRIMARY[0]}_minus_{PRIMARY[1]}",
                        "empirical_tables": frozen,
                        "elicitation_file": epath.name,
                        "elicitation_sha256": hashlib.sha256(epath.read_bytes()).hexdigest()})
    write_json(out / "table_calibration.json", table_calibration(tables))
    write_report(out / "report.md", f"v0.6 RQ3 · {args.model} · {FAMILY}", report,
                 ["", f"Primary endpoint (pre-registered): {PRIMARY[0]} - {PRIMARY[1]}."])
    print(f"done in {(time.time() - start) / 60:.1f} min")


if __name__ == "__main__":
    main()
