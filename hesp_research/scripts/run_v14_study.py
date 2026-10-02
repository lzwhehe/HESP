"""v1.4 (PROTOCOL.md v1.4): the small model alone on raw logs, the one cell of the read/decide comparison not yet run.

The model decides alone (ReAct-style or memory-only, prompt v1 or clear_finish, as in v1.2 C fair) and receives
each probe's response as log text without a parsed label (``NullParser``: outcome ``unparsed``), so it must read
the text itself. Conditions: structured (the v1.2 reference: classified label plus JSON body), documented and
drifted log text. Tasks and seeds are those of v1.2 C raw (seed 2033, sec-triage base+noise 16 tasks x 3), so
every episode is paired with the v1.2 episode in which the same model read the same text for the controller.

    python scripts/run_v14_study.py --output results/v14_alone_qwen7b --model qwen2.5-7b-instruct
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
from hesp.rawlog import NullParser, make_raw_env_class               # noqa: E402
from hesp.secapp import make_sec_env, sec_suite                      # noqa: E402
from hesp.selectors import Selector                                  # noqa: E402
from hesp.study import cell_seed                                     # noqa: E402
from run_v11_study import family                                     # noqa: E402
from v10b_mismatch import TargetPredictor                            # noqa: E402

SEED = 2033
BUDGET = Budget(max_tool_calls=10, max_decisions=12, max_tool_cost=10, max_seconds=900.0)
MODES = ("react_style", "memory_only")
VARIANTS = ("v1", "clear_finish")
CONDITIONS = ("structured", "documented", "drifted")


def jobs(task_stride=1, modes=MODES, variants=VARIANTS, conditions=CONDITIONS):
    tasks = sec_suite(("base", "noise"))[::task_stride]
    return [(mode, variant, condition, t, rep) for mode in modes for variant in variants for condition in conditions
            for t in tasks for rep in range(3)]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--output", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--base-url", default="http://127.0.0.1:8000/v1")
    ap.add_argument("--temperature", type=float, default=0.2)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--task-stride", type=int, default=1, help="smoke tests only")
    ap.add_argument("--presentation", choices=("unparsed", "raw_text"), default="unparsed",
                    help="raw_text: the v1.4 exploratory check with the neutral '(raw log below)' wording")
    ap.add_argument("--modes", nargs="+", default=list(MODES), choices=MODES)
    ap.add_argument("--variants", nargs="+", default=list(VARIANTS), choices=VARIANTS)
    ap.add_argument("--conditions", nargs="+", default=list(CONDITIONS), choices=CONDITIONS)
    args = ap.parse_args()
    client = OpenAICompatClient(args.model, args.base_url)
    _, tables, digest, _ = family("sec")
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=args.resume)
    src = source_hash()
    todo = jobs(args.task_stride, args.modes, args.variants, args.conditions)

    def one(i_job):
        i, (mode, variant, condition, t, rep) = i_job
        arm = f"{mode}_{variant}_{condition}"
        name = f"run{i:04d}_{t['task_id']}_{rep}_{arm}"
        rdir = out / name
        if (rdir / "row.json").exists():
            return json.loads((rdir / "row.json").read_text(encoding="utf-8"))
        seed = cell_seed(SEED, t["task_id"], rep)
        if condition == "structured":
            env = make_sec_env(t, seed)
        else:
            env = make_raw_env_class(NullParser(args.presentation), condition)(t["cause"], t["variant"], seed)
        with env:
            r = run(env, LLMPlanner(client, seed=seed, temperature=args.temperature, prompt_variant=variant), mode,
                    rdir, BUDGET, predictor=TargetPredictor(tables, "empirical_20"), selector=Selector("eig_cost", seed),
                    arm=arm, metadata={"task": t, "repeat": rep})
        audit = audit_run(rdir)
        row = {"run_directory": name, "task_id": t["task_id"], "cause": t["cause"], "variant": t["variant"],
               "repeat": rep, "mode": mode, "prompt_variant": variant, "condition": condition, "arm": arm,
               "audit_passed": audit["passed"], **r}
        (rdir / "row.json").write_text(json.dumps(row), encoding="utf-8")
        return row

    start = time.time()
    rows = []
    with ThreadPoolExecutor(args.workers) as pool:
        for k, row in enumerate(pool.map(one, enumerate(todo)), 1):
            rows.append(row)
            if k % 50 == 0 or k == len(todo):
                print(f"[{k}/{len(todo)}] ({(time.time() - start) / 60:.1f} min)", flush=True)
    with open(out / "outcomes.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    (out / "manifest.json").write_text(json.dumps({
        "study": "v1.4", "seed": SEED, "source_sha256": src, "model": client.info(), "temperature": args.temperature,
        "table": {"name": "empirical_20", "sha256": digest}, "task_stride": args.task_stride, "presentation": args.presentation,
        "modes": args.modes, "variants": args.variants, "conditions": args.conditions,
        "episodes": len(rows)}, indent=2), encoding="utf-8")
    print(f"{len(rows)} episodes, audits passed {sum(r['audit_passed'] for r in rows)}, "
          f"done in {(time.time() - start) / 60:.1f} min")


if __name__ == "__main__":
    main()
