"""v1.0 part B: how the controller degrades when its prediction tables are wrong (PROTOCOL.md v1.0).

LLM-free and CPU-only. The planner never concludes (``NeverFinishPlanner``), so every verdict is
the controller's own: the controller stop (threshold 0.8) decides when to conclude, and the
selector decides what to probe. Three selectors are compared: EIG/cost, random, and the fixed
catalogue order (``memory_only`` mode, in which the never-finishing planner's own proposal - the
next untried probe - is executed).

Mismatch conditions
  M0 matched      tables counted from base+noise development runs (k=20; the frozen empirical_20)
  M1 shift        tables counted from base runs only (k=20); evaluated on every variant
  M2 perturbed    every row mixed with a random Dirichlet(1) row: (1-lam) p + lam q
  M3 missing      one cause absent from the development data (its row is uniform); evaluated only
                  on tasks whose true cause is that cause
  M4 scarce       k in {1, 5}, base runs only

Outcomes per episode: verified, wrong (a verdict naming a named cause other than the cause in
effect), escalated (a verdict of ``other``, or no verdict), probe cost.

    python scripts/v10b_mismatch.py --family sec --out results/v10b_sec
"""
import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
import random
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hesp.controller import Budget, run
from hesp.planner import NeverFinishPlanner
from hesp.predictors import EmpiricalEstimator, FrozenPredictor
from hesp.selectors import Selector
from hesp.study import cell_seed

DEV_SEED_BASE = 810_000          # disjoint from v0.6 (900000+) and v0.9 development (700000+)
EVAL_SEED = 2028
LAMBDAS = (0.1, 0.25, 0.5, 0.75)
PERTURB_SEEDS = 20
SELECTORS = {"eig_cost": ("hesp", "eig_cost"), "random": ("hesp", "random"), "catalogue": ("memory_only", "eig_cost")}


def family(name):
    if name == "sec":
        from hesp.secapp import SecTriageEnvironment, make_sec_env, sec_suite
        return SecTriageEnvironment, sec_suite(("base", "noise", "drift")), make_sec_env
    raise SystemExit(f"unknown family {name}")


def count_tables(env_cls, variants, k, omit=None, eps=0.01):
    """Counted tables from LLM-free development runs; never calls the generative model."""
    est = EmpiricalEstimator(eps=eps)
    for i in range(1, k + 1):
        for ci, cause in enumerate(env_cls.CAUSES):
            if cause == omit:
                continue
            for vi, variant in enumerate(variants):
                seed = DEV_SEED_BASE + (ci * 10 + vi) * 1000 + i
                with env_cls(cause, variant, seed=seed, oracle=False) as env:
                    for action in env.catalog():
                        obs = env.execute(action)
                        if obs.valid:
                            est.observe(action.id, cause, obs.outcome)
    return est.tables(env_cls.build_catalog(oracle=False), env_cls.hypotheses_())


def perturb(tables, lam, seed):
    rng = random.Random(seed)
    out = {}
    for a, rows in tables.items():
        out[a] = {}
        for h, row in rows.items():
            draws = {o: rng.gammavariate(1.0, 1.0) for o in row}
            z = sum(draws.values())
            out[a][h] = {o: (1 - lam) * p + lam * draws[o] / z for o, p in row.items()}
    return out


def episode(task, repeat, env_factory, tables, source, selector_name, tmp):
    mode, sel = SELECTORS[selector_name]
    s = cell_seed(EVAL_SEED, task["task_id"], repeat)
    budget = Budget(max_tool_calls=10, max_decisions=12, max_tool_cost=10, max_seconds=900.0)
    with env_factory(task, s) as env:
        r = run(env, NeverFinishPlanner(), mode, Path(tmp) / f"{task['task_id']}_{repeat}_{selector_name}_{source}",
                budget, predictor=FrozenPredictor(tables, source), selector=Selector(sel, s),
                show_rankings=False, auto_finish=0.8)
        truth = env._app.cause
    claim = r["claimed_hypothesis"]
    return {"verified": r["verified_simulation"], "cost": r["tool_cost_units"],
            "wrong": claim is not None and claim != "other" and claim != truth,
            "escalated": claim is None or claim == "other"}


def summarize(rows):
    n = len(rows)
    return {"episodes": n, **{k: sum(r[k] for r in rows) / n for k in ("verified", "wrong", "escalated", "cost")}}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--family", default="sec")
    ap.add_argument("--out", required=True)
    ap.add_argument("--matched-tables", default=str(Path(__file__).resolve().parents[1] / "results/v06_tables/empirical_20.json"))
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--quick", action="store_true", help="smoke test: one lambda, two seeds, one repeat")
    args = ap.parse_args()
    env_cls, tasks, env_factory = family(args.family)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    repeats = 1 if args.quick else args.repeats
    lambdas = LAMBDAS[:1] if args.quick else LAMBDAS
    pseeds = 2 if args.quick else PERTURB_SEEDS
    matched = json.loads(Path(args.matched_tables).read_text(encoding="utf-8"))["tables"]
    conditions = {"M0_matched": (matched, tasks),
                  "M1_base_only": (count_tables(env_cls, ("base",), 20), tasks)}
    for k in (1, 5):
        conditions[f"M4_k{k}_base_only"] = (count_tables(env_cls, ("base",), k), tasks)
    results = defaultdict(dict)
    with tempfile.TemporaryDirectory() as tmp:
        for cname, (tables, ctasks) in conditions.items():
            for sel in SELECTORS:
                rows = [episode(t, r, env_factory, tables, cname, sel, tmp) for t in ctasks for r in range(repeats)]
                results[cname][sel] = summarize(rows)
                if cname == "M1_base_only":
                    for v in ("base", "noise", "drift"):
                        vr = [row for row, (t, r) in zip(rows, [(t, r) for t in ctasks for r in range(repeats)])
                              if t["variant"] == v]
                        results[f"M1_base_only[{v}]"][sel] = summarize(vr)
            print(cname, {s: round(results[cname][s]["verified"], 3) for s in SELECTORS}, flush=True)
        for lam in lambdas:
            cname = f"M2_lambda{lam}"
            for sel in SELECTORS:
                rows = []
                for ps in range(pseeds):
                    tables = perturb(matched, lam, 5000 + ps)
                    rows += [episode(t, r, env_factory, tables, f"{cname}_{ps}", sel, tmp) for t in tasks for r in range(repeats)]
                results[cname][sel] = summarize(rows)
            print(cname, {s: round(results[cname][s]["verified"], 3) for s in SELECTORS}, flush=True)
        for cause in env_cls.CAUSES:
            cname = f"M3_missing[{cause}]"
            tables = count_tables(env_cls, ("base", "noise"), 20, omit=cause)
            ctasks = [t for t in tasks if t["cause"] == cause and t["variant"] != "drift"]
            for sel in SELECTORS:
                rows = [episode(t, r, env_factory, tables, cname, sel, tmp) for t in ctasks for r in range(repeats)]
                results[cname][sel] = summarize(rows)
        m3 = [results[f"M3_missing[{c}]"] for c in env_cls.CAUSES]
        results["M3_missing[mean]"] = {s: {k: sum(m[s][k] for m in m3) / len(m3)
                                           for k in ("verified", "wrong", "escalated", "cost")} for s in SELECTORS}
        print("M3 mean", {s: round(results["M3_missing[mean]"][s]["verified"], 3) for s in SELECTORS}, flush=True)
    record = {"schema": "hesp.v10b.v1", "family": args.family, "eval_seed": EVAL_SEED, "dev_seed_base": DEV_SEED_BASE,
              "repeats": repeats, "lambdas": list(lambdas), "perturb_seeds": pseeds, "quick": args.quick,
              "results": results}
    (out / "summary.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    lines = [f"# v1.0 part B - table mismatch ({args.family})", "",
             "| Condition | Selector | Verified | Wrong | Escalated | Cost |", "| --- | --- | ---: | ---: | ---: | ---: |"]
    for cname, per in results.items():
        for sel, m in per.items():
            lines.append(f"| {cname} | {sel} | {m['verified']:.3f} | {m['wrong']:.3f} | {m['escalated']:.3f} | {m['cost']:.2f} |")
    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
