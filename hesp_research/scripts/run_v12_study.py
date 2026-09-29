"""v1.2 part C, LLM runs (PROTOCOL.md v1.2 C).

--part dev   prompt selection on DEVELOPMENT seeds (7000; sec-triage 24 tasks x 1): react_style and
             memory_only, each with the four system-prompt variants (v1, finish_example, explicit_rule,
             clear_finish). The selection rule is fixed in the protocol and applied by
             scripts/v12_select_prompt.py; nothing from the test seeds is used.
--part fair  test (seed 2032; sec-triage 24 tasks x 2): react_style, memory_only, hesp_guard (LLM stops),
             hesp_guard_confirmstop, each with v1 and with the selected variant (--variant).
--part raw   raw-log observations (seed 2033; sec-triage base+noise 16 tasks x 3): the LLM-free controller
             (EIG/cost, confirm stop, never-finishing planner) with three parsers x three log conditions:
             structured (the fixed classifier on the JSON response; reference), rule (regex written for the
             documented log format), llm (the served model as parser); conditions documented, drifted, injected.
             Per-observation parse records are written next to each run directory.

    python scripts/run_v12_study.py --part fair --variant clear_finish --output results/v12c_fair_qwen7b --model qwen2.5-7b-instruct
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from hesp.audit import audit_run                                     # noqa: E402
from hesp.controller import Budget, run, source_hash                 # noqa: E402
from hesp.llm import LLMPlanner, OpenAICompatClient                  # noqa: E402
from hesp.planner import NeverFinishPlanner                          # noqa: E402
from hesp.study import cell_seed, run_suite                          # noqa: E402
from hesp.selectors import Selector                                  # noqa: E402
from run_v11_study import family                                     # noqa: E402
from suite_report import write_report                                # noqa: E402
from v10b_mismatch import TargetPredictor                            # noqa: E402

STOP = 0.8
BUDGET = Budget(max_tool_calls=10, max_decisions=12, max_tool_cost=10, max_seconds=900.0)
VARIANTS = ("v1", "finish_example", "explicit_rule", "clear_finish")


def llm_parts(args, client, factory, tables, digest, suite):
    predictor = TargetPredictor(tables, "empirical_20")

    def planner(variant):
        return lambda seed: LLMPlanner(client, seed=seed, temperature=args.temperature, prompt_variant=variant)
    guard = {"mode": "hesp", "selector": "eig_cost", "show_rankings": False, "finish_guard": True, "predictor": predictor}
    arms = {}
    if args.part == "dev":
        for v in VARIANTS:
            arms[f"react_style_{v}"] = {"mode": "react_style", "planner": planner(v), "predictor": predictor, "prompt_variant": v}
            arms[f"memory_only_{v}"] = {"mode": "memory_only", "planner": planner(v), "predictor": predictor, "prompt_variant": v}
        tasks, seed, repeats = suite(("base", "drift", "noise"))[::args.task_stride], 7000, 1
    else:
        if args.variant not in VARIANTS or args.variant == "v1":
            raise SystemExit("--variant must be the selected non-default variant")
        for v in ("v1", args.variant):
            arms[f"react_style_{v}"] = {"mode": "react_style", "planner": planner(v), "predictor": predictor, "prompt_variant": v}
            arms[f"memory_only_{v}"] = {"mode": "memory_only", "planner": planner(v), "predictor": predictor, "prompt_variant": v}
            arms[f"hesp_guard_{v}"] = {**guard, "planner": planner(v), "prompt_variant": v}
            arms[f"hesp_guard_confirmstop_{v}"] = {**guard, "planner": planner(v), "prompt_variant": v,
                                                   "auto_finish": STOP, "stop_rule": "confirm"}
        tasks, seed, repeats = suite(("base", "drift", "noise"))[::args.task_stride], 2032, 2
    start = time.time()

    def progress(i, n, row):
        if i % 50 == 0 or i == n:
            print(f"[{i}/{n}] {row['task_id']} {row['arm']} {row['status']} "
                  f"(~{(time.time() - start) / i * (n - i) / 60:.0f} min left)", flush=True)
    report, _ = run_suite(Path(args.output), tasks, arms, factory, repeats=repeats, seed=seed, budget=BUDGET,
                          comparisons=[], resume=args.resume, progress=progress, workers=args.workers,
                          purpose=f"v1.2_{args.part}", extra_manifest={
                              "model": client.info(), "temperature": args.temperature, "part": args.part,
                              "variant": args.variant, "table": {"name": "empirical_20", "sha256": digest}})
    write_report(Path(args.output) / "report.md", f"v1.2 {args.part} · {args.model}", report)
    print(f"done in {(time.time() - start) / 60:.1f} min")


def raw_part(args, client, tables):
    from hesp.rawlog import LLMParser, RuleParser, make_raw_env_class
    from hesp.secapp import make_sec_env, sec_suite
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=args.resume)
    tasks = sec_suite(("base", "noise"))[::args.task_stride]
    parsers = {"rule": RuleParser(), "llm": LLMParser(client)}
    jobs = []
    for parser_name in ("structured", "rule", "llm"):
        for condition in ("documented", "drifted", "injected"):
            if parser_name == "structured" and condition != "documented":
                continue
            for t in tasks:
                for rep in range(3):
                    jobs.append((parser_name, condition, t, rep))
    src = source_hash()

    def one(i_job):
        i, (parser_name, condition, t, rep) = i_job
        name = f"run{i:04d}_{t['task_id']}_{rep}_{parser_name}_{condition}"
        rdir = out / name
        if (rdir / "result.json").exists():
            return json.loads((rdir / "row.json").read_text(encoding="utf-8"))
        seed = cell_seed(2033, t["task_id"], rep)
        if parser_name == "structured":
            env = make_sec_env(t, seed)
        else:
            cls = make_raw_env_class(parsers[parser_name], condition)
            env = cls(t["cause"], t["variant"], seed)
        with env:
            r = run(env, NeverFinishPlanner(), "hesp", rdir, BUDGET, predictor=TargetPredictor(tables, "empirical_20"),
                    selector=Selector("eig_cost", seed), show_rankings=False, auto_finish=STOP, stop_rule="confirm",
                    arm=f"{parser_name}_{condition}", metadata={"task": t, "repeat": rep})
            parse_log = getattr(env, "parse_log", [])
        (rdir / "parse_log.json").write_text(json.dumps(parse_log), encoding="utf-8")
        audit = audit_run(rdir)
        row = {"run_directory": name, "task_id": t["task_id"], "cause": t["cause"], "variant": t["variant"],
               "repeat": rep, "parser": parser_name, "condition": condition, "arm": f"{parser_name}_{condition}",
               "audit_passed": audit["passed"], "parse_log": parse_log, **r}
        (rdir / "row.json").write_text(json.dumps(row), encoding="utf-8")
        return row
    start = time.time()
    with ThreadPoolExecutor(args.workers) as pool:
        rows = list(pool.map(one, enumerate(jobs)))
    with open(out / "outcomes.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    (out / "manifest.json").write_text(json.dumps({"part": "raw", "seed": 2033, "source_sha256": src,
                                                   "model": client.info(), "episodes": len(rows)}, indent=2), encoding="utf-8")
    print(f"{len(rows)} episodes, audits passed {sum(r['audit_passed'] for r in rows)}, done in {(time.time() - start) / 60:.1f} min")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--part", choices=("dev", "fair", "raw"), required=True)
    ap.add_argument("--variant", default=None)
    ap.add_argument("--output", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--base-url", default="http://127.0.0.1:8000/v1")
    ap.add_argument("--temperature", type=float, default=0.2)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--task-stride", type=int, default=1, help="smoke tests only")
    args = ap.parse_args()
    client = OpenAICompatClient(args.model, args.base_url)
    factory, tables, digest, suite = family("sec")
    if args.part == "raw":
        raw_part(args, client, tables)
    else:
        llm_parts(args, client, factory, tables, digest, suite)


if __name__ == "__main__":
    main()
