"""v1.3 (PROTOCOL.md v1.3): adaptive log injection against the recommended controller with a model as reader.

The controller plans without an LLM (EIG/cost, confirmation stop, benign corroboration per source group, recovery
after rejected finishes); a reader turns each probe's log text into the outcome the ledger consumes.

--reader llm    the served model is the base reader (H100); --model / --base-url as in run_v12_study.py
--reader adopt  scripted upper bound of a model reader (CPU only): reads every format, adopts every claim it sees

Reader policies (the paper's D0-D3): reader_only, rule_first, reader_trust (rule_first + benign_requires_trusted),
strip (known free-text fields removed before the base reader reads).
Log conditions: documented, drifted, injected (v1.2), injected_all, drifted_injected_all, lineinjected_all.
Seed 2034; sec-triage base+noise, 16 tasks x 3 repeats = 48 episodes per cell; every cell is paired.

    python scripts/run_v13_study.py --reader adopt --output results/v13_adopt --workers 8
    python scripts/run_v13_study.py --reader llm --model qwen2.5-7b-instruct --output results/v13_llm_qwen7b
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from hesp.audit import audit_run                                                             # noqa: E402
from hesp.controller import Budget, run, source_hash                                         # noqa: E402
from hesp.planner import NeverFinishPlanner                                                  # noqa: E402
from hesp.rawlog import CONDITIONS, AdoptParser, LLMParser, RuleFirstParser, StripParser, make_raw_env_class  # noqa: E402
from hesp.secapp import sec_suite                                                            # noqa: E402
from hesp.selectors import Selector                                                          # noqa: E402
from hesp.study import cell_seed                                                             # noqa: E402
from run_v11_study import family                                                             # noqa: E402
from v10b_mismatch import TargetPredictor                                                    # noqa: E402

STOP = 0.8
SEED = 2034
REPEATS = 3
BUDGET = Budget(max_tool_calls=10, max_decisions=12, max_tool_cost=10, max_seconds=900.0)
POLICIES = ("reader_only", "rule_first", "reader_trust", "strip")


def make_parser(policy, base):
    if policy == "reader_only":
        return base
    if policy in ("rule_first", "reader_trust"):
        return RuleFirstParser(base)
    if policy == "strip":
        return StripParser(base)
    raise ValueError(policy)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--reader", choices=("llm", "adopt"), required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--model", default=None)
    ap.add_argument("--base-url", default="http://127.0.0.1:8000/v1")
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--task-stride", type=int, default=1, help="smoke tests only")
    ap.add_argument("--conditions", default=",".join(CONDITIONS))
    ap.add_argument("--policies", default=",".join(POLICIES))
    args = ap.parse_args()
    _, tables, digest, _ = family("sec")
    if args.reader == "llm":
        from hesp.llm import OpenAICompatClient
        if not args.model:
            raise SystemExit("--model is required with --reader llm")
        client = OpenAICompatClient(args.model, args.base_url)
        base, reader_info = LLMParser(client), client.info()
    else:
        base, reader_info = AdoptParser(), {"reader": "adopt"}
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=args.resume)
    tasks = sec_suite(("base", "noise"))[::args.task_stride]
    conditions, policies = args.conditions.split(","), args.policies.split(",")
    jobs = [(policy, condition, t, rep) for policy in policies for condition in conditions for t in tasks
            for rep in range(REPEATS)]
    src = source_hash()

    def one(i_job):
        i, (policy, condition, t, rep) = i_job
        name = f"run{i:04d}_{t['task_id']}_{rep}_{policy}_{condition}"
        rdir = out / name
        if (rdir / "result.json").exists():
            return json.loads((rdir / "row.json").read_text(encoding="utf-8"))
        seed = cell_seed(SEED, t["task_id"], rep)
        env = make_raw_env_class(make_parser(policy, base), condition)(t["cause"], t["variant"], seed)
        with env:
            r = run(env, NeverFinishPlanner(), "hesp", rdir, BUDGET, predictor=TargetPredictor(tables, "empirical_20"),
                    selector=Selector("eig_cost", seed), show_rankings=False, auto_finish=STOP, stop_rule="confirm",
                    corroborate_benign=2, corroborate_unit="source", finish_rejection_limit=2,
                    benign_requires_trusted=(policy == "reader_trust"),
                    arm=f"{policy}_{condition}", metadata={"task": t, "repeat": rep})
            parse_log = list(env.parse_log)
        (rdir / "parse_log.json").write_text(json.dumps(parse_log), encoding="utf-8")
        audit = audit_run(rdir)
        row = {"run_directory": name, "task_id": t["task_id"], "cause": t["cause"], "variant": t["variant"],
               "repeat": rep, "reader": args.reader, "policy": policy, "condition": condition,
               "arm": f"{policy}_{condition}", "audit_passed": audit["passed"], "parse_log": parse_log, **r}
        (rdir / "row.json").write_text(json.dumps(row), encoding="utf-8")
        return row
    start = time.time()
    rows = []
    with ThreadPoolExecutor(args.workers) as pool:
        for k, row in enumerate(pool.map(one, enumerate(jobs)), 1):
            rows.append(row)
            if k % 100 == 0 or k == len(jobs):
                print(f"[{k}/{len(jobs)}] {row['arm']} {row['status']} (~{(time.time() - start) / k * (len(jobs) - k) / 60:.0f} min left)",
                      flush=True)
    with open(out / "outcomes.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    (out / "manifest.json").write_text(json.dumps({
        "study": "v1.3", "seed": SEED, "repeats": REPEATS, "source_sha256": src, "reader": reader_info,
        "table": {"name": "empirical_20", "sha256": digest}, "conditions": conditions, "policies": policies,
        "task_stride": args.task_stride, "episodes": len(rows)}, indent=2), encoding="utf-8")
    print(f"{len(rows)} episodes, audits passed {sum(r['audit_passed'] for r in rows)}, "
          f"done in {(time.time() - start) / 60:.1f} min")


if __name__ == "__main__":
    main()
