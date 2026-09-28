"""v1.1 LLM parts (PROTOCOL.md v1.1).

--part e2  configuration matrix with the finish guard ON, both families, seeds shared with the
           LLM-free references of part D (sec 2027 x3, sigma 2028 x2):
             hesp_guard                 controller EIG/cost (blind), guard, the LLM decides when to stop
             hesp_guard_autostop        + controller stop at posterior 0.8
             hesp_guard_confirmstop     + controller stop that also requires a confirming observation
--part e4  attack attribution on sec-triage (seed 2029 x3): six actionable causes under six attacker
           variants (inject, inject_b, inject_c, inject_one, spoof, spoof_feed) plus the two benign
           causes under base, with seven arms:
             memory_only, memory_only_redacted, hesp_guard, hesp_autostop_noguard, hesp_guard_autostop,
             hesp_guard_autostop_corr_probe, hesp_guard_autostop_corr_source
--part f   stopping diagnosis (sec-triage, seed 2030 x2): memory_only and hesp_guard, each with the
           three pre-specified system-prompt variants (v1, finish_example, explicit_rule)

    python scripts/run_v11_study.py --part e2 --family sec --output results/v11e2_sec_qwen7b --model qwen2.5-7b-instruct
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from hesp.controller import Budget
from hesp.llm import LLMPlanner, OllamaClient, OpenAICompatClient
from hesp.study import run_suite
from suite_report import write_report
from v10b_mismatch import TargetPredictor

ROOT = Path(__file__).resolve().parents[1]
STOP = 0.8
BUDGET = Budget(max_tool_calls=10, max_decisions=12, max_tool_cost=10, max_seconds=900.0)


def checked(path, expected=None):
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if expected and digest != expected:
        raise SystemExit(f"{path}: SHA256 mismatch")
    return digest


def family(name):
    if name == "sec":
        from hesp.secapp import SecTriageEnvironment, make_sec_env, sec_suite
        index = json.loads((ROOT / "results/v06_tables/index.json").read_text(encoding="utf-8"))
        path = ROOT / "results/v06_tables" / index["empirical_20"]["file"]
        digest = checked(path, index["empirical_20"]["sha256"])
        tables = {SecTriageEnvironment.TARGET: json.loads(path.read_text(encoding="utf-8"))["tables"]}
        return make_sec_env, tables, digest, sec_suite
    from hesp.sigmaapp import SigmaEnvironments, sigma_suite
    from v10a_tables import load_specs
    specs, _ = load_specs(ROOT / "results/v10a/specs")
    envs = SigmaEnvironments(specs)
    index = json.loads((ROOT / "results/v10a/tables/index.json").read_text(encoding="utf-8"))
    path = ROOT / "results/v10a/tables" / index["empirical_20"]["file"]
    digest = checked(path, index["empirical_20"]["sha256"])
    rec = json.loads(path.read_text(encoding="utf-8"))["tables"]
    tables = {envs.classes[s["slug"]].TARGET: rec[s["slug"]] for s in specs}
    return envs, tables, digest, (lambda variants=("base", "noise"): sigma_suite(specs, variants))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--part", choices=("e2", "e4", "f"), required=True)
    ap.add_argument("--family", choices=("sec", "sigma"), default="sec")
    ap.add_argument("--output", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--backend", choices=("vllm", "ollama"), default="vllm")
    ap.add_argument("--base-url", default="http://127.0.0.1:8000/v1")
    ap.add_argument("--temperature", type=float, default=0.2)
    ap.add_argument("--workers", type=int, default=32)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--task-stride", type=int, default=1, help="smoke tests only")
    args = ap.parse_args()
    if args.part != "e2" and args.family != "sec":
        raise SystemExit("parts e4 and f use sec-triage")
    factory, tables, digest, suite = family(args.family)
    predictor = TargetPredictor(tables, "empirical_20")
    client = (OllamaClient(args.model) if args.backend == "ollama"
              else OpenAICompatClient(args.model, args.base_url))

    def planner(variant="v1"):
        return lambda seed: LLMPlanner(client, seed=seed, temperature=args.temperature, prompt_variant=variant)
    base = {"planner": planner(), "predictor": predictor}
    guard = {**base, "mode": "hesp", "selector": "eig_cost", "show_rankings": False, "finish_guard": True}
    if args.part == "e2":
        arms = {"hesp_guard": guard,
                "hesp_guard_autostop": {**guard, "auto_finish": STOP},
                "hesp_guard_confirmstop": {**guard, "auto_finish": STOP, "stop_rule": "confirm"}}
        tasks = suite(("base", "drift", "noise")) if args.family == "sec" else suite()
        seed, repeats = (2027, 3) if args.family == "sec" else (2028, 2)
    elif args.part == "e4":
        from hesp.secapp import BENIGN
        arms = {"memory_only": {**base, "mode": "memory_only"},
                "memory_only_redacted": {**base, "mode": "memory_only", "redact_raw": True},
                "hesp_guard": guard,
                "hesp_autostop_noguard": {**guard, "finish_guard": False, "auto_finish": STOP},
                "hesp_guard_autostop": {**guard, "auto_finish": STOP},
                "hesp_guard_autostop_corr_probe": {**guard, "auto_finish": STOP, "corroborate_benign": 2},
                "hesp_guard_autostop_corr_source": {**guard, "auto_finish": STOP, "corroborate_benign": 2,
                                                    "corroborate_unit": "source"}}
        variants = ("inject", "inject_b", "inject_c", "inject_one", "spoof", "spoof_feed")
        tasks = [t for t in suite(variants) if t["cause"] not in BENIGN]
        tasks += [t for t in suite(("base",)) if t["cause"] in BENIGN]
        seed, repeats = 2029, 3
    else:
        arms = {}
        for v in ("v1", "finish_example", "explicit_rule"):
            arms[f"memory_only_{v}"] = {"planner": planner(v), "predictor": predictor, "mode": "memory_only",
                                        "prompt_variant": v}
            arms[f"hesp_guard_{v}"] = {**guard, "planner": planner(v), "prompt_variant": v}
        tasks = suite(("base", "drift", "noise"))
        seed, repeats = 2030, 2
    tasks = tasks[::args.task_stride]
    start = time.time()

    def progress(i, n, row):
        if i % 50 == 0 or i == n:
            print(f"[{i}/{n}] {row['task_id']} {row['arm']} {row['status']} "
                  f"(~{(time.time() - start) / i * (n - i) / 60:.0f} min left)", flush=True)
    report, _ = run_suite(Path(args.output), tasks, arms, factory, repeats=repeats, seed=seed, budget=BUDGET,
                          comparisons=[], resume=args.resume, progress=progress, workers=args.workers,
                          purpose=f"v1.1_{args.part}", extra_manifest={
                              "model": client.info(), "temperature": args.temperature, "family": args.family,
                              "part": args.part, "table": {"name": "empirical_20", "sha256": digest}})
    write_report(Path(args.output) / "report.md", f"v1.1 {args.part} · {args.family} · {args.model}", report)
    print(f"done in {(time.time() - start) / 60:.1f} min")


if __name__ == "__main__":
    main()
