"""Model pilot: a local LLM planner in the web sandbox, paired across five arms.

Arms (same model, prompt template, tools, budget, dedup and verifier):
  react_style      goal + tools + history; the LLM picks the probe
  memory_only      + structured ledger (hypotheses, scores, evidence, state); the LLM picks
  hesp             + EIG/cost rankings (designer table); the controller picks by EIG/cost
  hesp_llm_pred    as hesp, but P(o|h,a) comes from frozen LLM-elicited tables
  hesp_random      as hesp, but the controller picks a random legal probe
                   (separates "controller picks" from "EIG picks")

Resumable: rerun with --resume after an interruption; completed cells are kept and a
half-finished run folder is preserved as _aborted_*.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hesp.controller import Budget
from hesp.llm import DEFAULT_MODEL, LLMPlanner, OllamaClient
from hesp.predictors import FrozenPredictor
from hesp.study import run_suite
from hesp.webapp import make_web_env, web_suite
from suite_report import write_report

COMPARISONS = [("hesp", "react_style"), ("hesp", "memory_only"), ("memory_only", "react_style"),
               ("hesp", "hesp_random"), ("hesp", "hesp_llm_pred"), ("hesp_llm_pred", "memory_only"),
               ("hesp_random", "memory_only")]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output", required=True)
    parser.add_argument("--elicitation", required=True, help="elicitation.json from elicit_predictions.py")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--repeats", type=int, default=2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    elicitation_path = Path(args.elicitation)
    elicitation = json.loads(elicitation_path.read_text(encoding="utf-8"))
    if elicitation["model"]["model"] != args.model:
        raise SystemExit("Elicitation was produced by a different model")
    client = OllamaClient(args.model)
    info = client.info()
    llm_p = FrozenPredictor(elicitation["tables"], elicitation["source"])
    planner = lambda seed: LLMPlanner(client, seed=seed, temperature=args.temperature)
    arms = {
        "react_style": {"mode": "react_style", "planner": planner},
        "memory_only": {"mode": "memory_only", "planner": planner},
        "hesp": {"mode": "hesp", "planner": planner, "selector": "eig_cost"},
        "hesp_llm_pred": {"mode": "hesp", "planner": planner, "selector": "eig_cost", "predictor": llm_p},
        "hesp_random": {"mode": "hesp", "planner": planner, "selector": "random"},
    }
    budget = Budget(max_tool_calls=10, max_decisions=12, max_tool_cost=10, max_seconds=900.0)
    start = time.time()

    def progress(i, n, row):
        eta = (time.time() - start) / max(i, 1) * (n - i) / 60
        print(f"[{i}/{n}] {row['task_id']} r{row['repeat']} {row['arm']:<14} {row['status']:<26} "
              f"cost={row['tool_cost_units']} calls={row['planner_calls']} (~{eta:.0f} min left)", flush=True)

    report, rows = run_suite(
        args.output, web_suite(), arms, make_web_env, repeats=args.repeats, seed=args.seed, budget=budget,
        comparisons=COMPARISONS, resume=args.resume, progress=progress, purpose="local_llm_model_pilot",
        extra_manifest={"model": info, "temperature": args.temperature,
                        "elicitation_file": str(elicitation_path),
                        "elicitation_sha256": hashlib.sha256(elicitation_path.read_bytes()).hexdigest()})
    out = Path(args.output)
    (out / "summary.json").write_text(json.dumps({"results": rows, "research_claim_allowed": False},
                                                 ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(out / "report.md", f"Local-LLM pilot ({args.model}, web sandbox)", report, [
        "", f"Model digest: `{info['digest']}`, quantization {info['quantization']}, "
            f"temperature {args.temperature}. Tokens are server-reported by the local Ollama runtime.",
        "This is a small pilot on a hand-built sandbox (24 tasks); it is not a Web CTF benchmark."])
    print(f"done in {(time.time() - start) / 60:.1f} min")


if __name__ == "__main__":
    main()
