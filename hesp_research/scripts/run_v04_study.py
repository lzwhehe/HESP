"""v0.4 main study: one served LLM, two task families, nine paired arms.

Families: web-diag (development family, used in v0.3) and upload-diag (held-out, primary).
Arms (same model, prompt template, tools, budget, exact dedup and verifier):

  react_style       goal + tools + history; the LLM picks probes
  memory_only       + structured ledger; the LLM picks probes
  memory_guard      memory_only + state-guarded finish          (guard without selection)
  hesp_eigc         controller picks by EIG / cost               (= v0.3 C arm)
  hesp_eigc_guard   EIG / cost + guard
  hesp_la           budget-aware lookahead selector
  hesp_la_guard     lookahead + guard                             (full v0.4 HESP)
  hesp_random       controller picks a random legal probe         (controller-pick control)
  hesp_llmp         EIG / cost with the model's own elicited P(o|h,a)

The model first elicits its predictive tables for both families (frozen before any
episode). Episodes run concurrently against a local OpenAI-compatible server (vLLM).
Resumable with --resume. Comparisons and the primary endpoint are pre-registered in
docs/PROTOCOL.md (v0.4 section).
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
from hesp.llm import LLMPlanner, LLMPredictor, OpenAICompatClient
from hesp.predictors import FrozenPredictor, calibration
from hesp.study import run_suite, write_json
from hesp.uploadapp import UploadDiagEnvironment, make_upload_env, upload_suite
from hesp.webapp import WebDiagEnvironment, make_web_env, web_suite
from suite_report import write_report

FAMILIES = {"web-diag": (WebDiagEnvironment, web_suite, make_web_env),
            "upload-diag": (UploadDiagEnvironment, upload_suite, make_upload_env)}
PRIMARY_FAMILY = "upload-diag"
COMPARISONS = [
    ("hesp_la_guard", "memory_only"),       # primary endpoint (on the held-out family)
    ("hesp_la_guard", "react_style"),
    ("memory_only", "react_style"),
    ("hesp_eigc", "memory_only"),
    ("hesp_eigc_guard", "hesp_eigc"),       # guard effect given EIG / cost
    ("memory_guard", "memory_only"),        # guard effect without controller selection
    ("hesp_la_guard", "memory_guard"),      # selection effect given the guard
    ("hesp_la", "hesp_eigc"),               # selector effect
    ("hesp_eigc", "hesp_random"),           # EIG ranking vs random controller picks
    ("hesp_eigc", "hesp_llmp"),             # designer vs self-elicited predictions
]


def elicit(client, out, seed):
    path = out.parent / f"{out.name}_elicitation.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8")), path
    predictor = LLMPredictor(client, seed=seed)
    record = {"schema": "hesp.elicitation.v2", "model": client.info(), "source": predictor.source,
              "eps_floor": predictor.eps, "families": {}}
    start = time.time()
    for name, (env_cls, _, _) in FAMILIES.items():
        tables = predictor.elicit(env_cls.build_catalog(), env_cls.DESCRIPTIONS,
                                  context=env_cls.public_task()["objective"])
        fam = {p["id"]: tables[p["id"]] for p in env_cls.PROBES}
        ids = [p["id"] for p in env_cls.PROBES]
        cal = {}
        for variant, spec in env_cls.VARIANTS.items():
            truth = (lambda lag: (lambda a, h: env_cls.true_outcome_distribution(a, h, lag)))(spec["lag"])
            cal[variant] = {"llm": calibration(fam, truth, env_cls.hypotheses_(), ids),
                            "designer_table": calibration({a.id: a.likelihoods for a in env_cls.build_catalog()},
                                                          truth, env_cls.hypotheses_(), ids)}
        record["families"][name] = {"tables": fam, "calibration_vs_true_model": cal}
    record.update({"seconds": round(time.time() - start, 1), "usage": predictor.usage,
                   "calls": len(predictor.records), "records": predictor.records,
                   "uniform_fallback_rows": sum(r["uniform_fallback"] for r in predictor.records)})
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    return record, path


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model", required=True, help="served model name")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000/v1")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--workers", type=int, default=24)
    parser.add_argument("--families", nargs="+", default=list(FAMILIES), choices=list(FAMILIES))
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--task-stride", type=int, default=1, help="smoke tests only: keep every k-th task")
    args = parser.parse_args()
    out = Path(args.output)
    client = OpenAICompatClient(args.model, args.base_url)
    elicitation, epath = elicit(client, out, args.seed)
    tables = {}
    for fam in elicitation["families"].values():
        tables.update(fam["tables"])
    llm_p = FrozenPredictor(tables, elicitation["source"])
    planner = lambda seed: LLMPlanner(client, seed=seed, temperature=args.temperature)
    arms = {
        "react_style": {"mode": "react_style", "planner": planner},
        "memory_only": {"mode": "memory_only", "planner": planner},
        "memory_guard": {"mode": "memory_only", "planner": planner, "finish_guard": True},
        "hesp_eigc": {"mode": "hesp", "planner": planner, "selector": "eig_cost"},
        "hesp_eigc_guard": {"mode": "hesp", "planner": planner, "selector": "eig_cost", "finish_guard": True},
        "hesp_la": {"mode": "hesp", "planner": planner, "selector": "lookahead"},
        "hesp_la_guard": {"mode": "hesp", "planner": planner, "selector": "lookahead", "finish_guard": True},
        "hesp_random": {"mode": "hesp", "planner": planner, "selector": "random"},
        "hesp_llmp": {"mode": "hesp", "planner": planner, "selector": "eig_cost", "predictor": llm_p},
    }
    tasks = [t for name in args.families for t in FAMILIES[name][1]()[::args.task_stride]]
    factory = lambda task, seed: FAMILIES[task["family"]][2](task, seed)
    budget = Budget(max_tool_calls=10, max_decisions=12, max_tool_cost=10, max_seconds=900.0)
    start = time.time()

    def progress(i, n, row):
        if i % 25 == 0 or i == n:
            rate = (time.time() - start) / max(i, 1)
            print(f"[{i}/{n}] last={row['task_id']} {row['arm']} {row['status']} "
                  f"(~{rate * (n - i) / 60:.0f} min left)", flush=True)

    report, rows = run_suite(
        out, tasks, arms, factory, repeats=args.repeats, seed=args.seed, budget=budget,
        comparisons=COMPARISONS, resume=args.resume, progress=progress, workers=args.workers,
        purpose="v0.4_main_study",
        extra_manifest={"model": elicitation["model"], "temperature": args.temperature,
                        "families": args.families, "primary_family": PRIMARY_FAMILY,
                        "elicitation_file": epath.name,
                        "elicitation_sha256": hashlib.sha256(epath.read_bytes()).hexdigest()})
    by_family = {}
    for name in args.families:
        subset = [r for r in rows if r["family"] == name]
        by_family[name] = summarize(subset, seed=args.seed, arms=list(arms), comparisons=COMPARISONS)
        write_report(out / f"report_{name}.md", f"v0.4 · {args.model} · {name}", by_family[name])
    write_json(out / "analysis_by_family.json", by_family)
    write_report(out / "report.md", f"v0.4 · {args.model} · all families", report,
                 ["", f"Primary family (pre-registered): {PRIMARY_FAMILY}; see report_{PRIMARY_FAMILY}.md."])
    print(f"done in {(time.time() - start) / 60:.1f} min")


if __name__ == "__main__":
    main()
