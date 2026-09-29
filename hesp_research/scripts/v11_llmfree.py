"""v1.1 part D (LLM-free, CPU only): fair controller-only references and wider table-error tests.

Every episode uses the never-finishing script as the planner, so every verdict is the controller's.

D1  controller references on both families, same seeds, tasks and budgets as the LLM studies
    (sec-triage: v0.9 seed 2027, 24 tasks x 3; sigma-triage: v1.0 seed 2028, 76 tasks x 2):
      eig_posterior     EIG/cost selection, posterior stop at 0.8            (the v0.9 LLM-free controller)
      eig_confirm       EIG/cost selection, confirmation-aware stop at 0.8   (R1: same evidence standard as the verifier,
                                                                              from the table only)
      static_confirm    a fixed playbook: probes in the order of their EIG/cost at the prior (non-adaptive),
                        confirmation-aware stop
      catalogue_confirm catalogue order, confirmation-aware stop
D2  threshold sweep: eig_posterior and eig_confirm at 0.6, 0.7, 0.8, 0.9, 0.95, 0.99 (both families)
D3  sec-triage only, wider table error (EIG/cost; posterior and confirmation-aware stop):
      confusion   each cause's rows mixed toward the rows of one fixed other cause (beta 0.25, 0.5)
      absent      the true cause is removed from the candidate set altogether (only "other" can absorb it)
      mirror      a second probe reads the same feed as source_ips (correlated evidence counted twice)

Outcomes per episode are mutually exclusive: verified; correct_unverified (right cause, no confirming
evidence cited); wrong (a named cause other than the cause in effect); escalated (verdict "other" or none).

    python scripts/v11_llmfree.py --out results/v11d --workers 16
"""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import sys
import tempfile
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from hesp.controller import Budget, run
from hesp.core import expected_information_gain
from hesp.planner import NeverFinishPlanner
from hesp.predictors import EmpiricalEstimator
from hesp.selectors import Selector
from hesp.study import cell_seed
from v10b_mismatch import TargetPredictor

BUDGET = Budget(max_tool_calls=10, max_decisions=12, max_tool_cost=10, max_seconds=900.0)
THRESHOLDS = (0.6, 0.7, 0.8, 0.9, 0.95, 0.99)
DEV_SEED_BASE = 820_000
ROOT = Path(__file__).resolve().parents[1]


class StaticPlanner:
    """Proposes probes in a fixed order and never concludes (the playbook is executed in memory_only mode)."""

    def __init__(self, order):
        self.order, self.name = list(order), "static_playbook"

    def decide(self, request):
        version = request["state_version"]
        tried = {(o["action_id"], o["state_version"]) for o in request["history"] if o.get("valid", True)}
        for probe in self.order:
            if (probe, version) not in tried:
                return {"kind": "action", "action_id": probe, "reason": "playbook",
                        "usage": {"input_tokens": 0, "output_tokens": 0}}
        return {"kind": "stop", "reason": "playbook exhausted", "usage": {"input_tokens": 0, "output_tokens": 0}}


def static_order(env_cls, tables):
    """Probes sorted by EIG/cost at the uniform prior, from the same counted table."""
    from dataclasses import replace
    hyps = env_cls.hypotheses_()
    prior = {h: 1 / len(hyps) for h in hyps}
    scored = []
    for a in env_cls.build_catalog(oracle=False):
        modeled = replace(a, likelihoods=tables[a.id])
        scored.append((-expected_information_gain(prior, modeled) / a.cost, a.id))
    return [pid for _, pid in sorted(scored)]


# ------------------------------------------------------------------ families
def sec_family():
    from hesp.secapp import SecTriageEnvironment, make_sec_env, sec_suite
    tables = json.loads((ROOT / "results/v06_tables/empirical_20.json").read_text(encoding="utf-8"))["tables"]
    return {"name": "sec", "tasks": sec_suite(("base", "drift", "noise")), "factory": make_sec_env,
            "tables": {SecTriageEnvironment.TARGET: tables}, "seed": 2027, "repeats": 3,
            "orders": {SecTriageEnvironment.TARGET: static_order(SecTriageEnvironment, tables)},
            "unit_of": lambda t: SecTriageEnvironment.TARGET}


def sigma_family():
    from hesp.sigmaapp import SigmaEnvironments, sigma_suite
    from v10a_tables import load_specs
    specs, _ = load_specs(ROOT / "results/v10a/specs")
    envs = SigmaEnvironments(specs)
    rec = json.loads((ROOT / "results/v10a/tables/empirical_20.json").read_text(encoding="utf-8"))["tables"]
    tables = {envs.classes[s["slug"]].TARGET: rec[s["slug"]] for s in specs}
    orders = {envs.classes[s["slug"]].TARGET: static_order(envs.classes[s["slug"]], rec[s["slug"]]) for s in specs}
    return {"name": "sigma", "tasks": sigma_suite(specs), "factory": envs, "tables": tables, "seed": 2028,
            "repeats": 2, "orders": orders, "unit_of": lambda t: envs.classes[t["rule"]].TARGET}


FAMILIES = {}
JOBS_CTX = {}


def classify_outcome(result, truth):
    claim = result["claimed_hypothesis"]
    if result["verified_simulation"]:
        return "verified"
    if claim == truth:
        return "correct_unverified"
    if claim is None or claim == "other":
        return "escalated"
    return "wrong"


def episode(job):
    """job = (group, family, config, task, repeat, extra)."""
    group, fam_name, config, task, repeat, extra = job
    fam = FAMILIES[fam_name]
    s = cell_seed(fam["seed"], task["task_id"], repeat)
    threshold = extra.get("threshold", 0.8)
    stop_rule = "confirm" if "confirm" in config else "posterior"
    tables = JOBS_CTX.get(extra.get("tables"), fam["tables"])
    factory = JOBS_CTX.get(extra.get("factory"), fam["factory"])
    env = None
    for attempt in range(30):
        try:
            env = factory(task, s)
            break
        except OSError:
            time.sleep(0.1 * (attempt + 1))
    if env is None:
        raise RuntimeError("sandbox did not start")
    if config.startswith("static"):
        planner, mode, selector = StaticPlanner(fam["orders"][fam["unit_of"](task)]), "memory_only", "eig_cost"
    elif config.startswith("catalogue"):
        planner, mode, selector = NeverFinishPlanner(), "memory_only", "eig_cost"
    else:
        planner, mode, selector = NeverFinishPlanner(), "hesp", "eig_cost"
    with tempfile.TemporaryDirectory() as tmp:
        with env:
            r = run(env, planner, mode, Path(tmp) / "r", BUDGET, predictor=TargetPredictor(tables, "empirical_20"),
                    selector=Selector(selector, s), show_rankings=False, auto_finish=threshold, stop_rule=stop_rule)
            truth = env._app.cause
            benign = getattr(env._app, "BENIGN", None) or getattr(type(env), "BENIGN", frozenset())
    claim = r["claimed_hypothesis"]
    return group, fam_name, config, task["variant"], task["cause"], {
        "outcome": classify_outcome(r, truth), "cost": r["tool_cost_units"],
        "execution_error": r["status"] == "EXECUTION_ERROR",
        # a benign verdict while an actionable cause is in effect (the attacker's goal)
        "missed_attack": truth not in benign and claim in benign,
        "task_id": task["task_id"], "repeat": repeat, "threshold": threshold, "truth": truth, "claim": claim,
        "status": r["status"], "finished_by": r.get("finished_by"), "tool_calls": r["tool_calls"]}


# ------------------------------------------------------------------ D3 helpers (sec-triage only)
def confusion_tables(tables, beta):
    """Mix each named cause's rows toward the rows of the next cause in catalogue order."""
    from hesp.secapp import CAUSES
    out = {}
    for a, rows in tables.items():
        out[a] = dict(rows)
        for i, c in enumerate(CAUSES):
            other = CAUSES[(i + 1) % len(CAUSES)]
            out[a][c] = {o: (1 - beta) * p + beta * rows[other][o] for o, p in rows[c].items()}
    return out


def absent_family(cause):
    """sec-triage whose candidate set lacks ``cause``, with tables counted without it."""
    from hesp.secapp import CAUSES, SecTriageEnvironment
    hyps = tuple(c for c in CAUSES if c != cause) + ("other",)
    cls = type(f"SecAbsent_{cause}", (SecTriageEnvironment,), {"hypotheses_": classmethod(lambda k: hyps)})
    est = EmpiricalEstimator(eps=0.01)
    for i in range(1, 21):
        for ci, c in enumerate(CAUSES):
            if c == cause:
                continue
            for vi, v in enumerate(("base", "noise")):
                with cls(c, v, seed=DEV_SEED_BASE + (ci * 10 + vi) * 1000 + i, oracle=False) as env:
                    for a in env.catalog():
                        o = env.execute(a)
                        if o.valid:
                            est.observe(a.id, c, o.outcome)
    tables = est.tables(cls.build_catalog(oracle=False), hyps)
    return cls, {cls.TARGET: tables}


def mirror_family():
    """sec-triage with an extra probe that reads the same feed as source_ips."""
    from hesp import secapp
    from hesp.sandbox import probe
    src = next(p for p in secapp.PROBES if p["id"] == "source_ips")
    mirror = probe("source_ips_mirror", "GET", "/siem/sources_mirror?window=1h", 1,
                   "Read the reputation of the top traffic sources from the mirrored dashboard.", src["outcome_notes"])

    def respond(cause, method, path, rng, v):
        return secapp.respond(cause, method, "/siem/sources?window=1h" if path == mirror["path"] else path, rng, v)

    def classify(pid, status, body):
        return secapp.classify("source_ips" if pid == "source_ips_mirror" else pid, status, body)

    def tod(pid, cause, lag):
        return secapp.true_outcome_distribution("source_ips" if pid == "source_ips_mirror" else pid, cause, lag)
    cls = type("SecMirror", (secapp.SecTriageEnvironment,), {
        "PROBES": secapp.PROBES + [mirror], "respond": staticmethod(respond), "classify": staticmethod(classify),
        "true_outcome_distribution": staticmethod(tod),
        # every source_ips signature has its mirrored twin
        "SIGNATURES": {c: sig | {("source_ips_mirror", o) for a, o in sig if a == "source_ips"}
                       for c, sig in secapp.SIGNATURES.items()}})
    est = EmpiricalEstimator(eps=0.01)
    for i in range(1, 21):
        for ci, c in enumerate(secapp.CAUSES):
            for vi, v in enumerate(("base", "noise")):
                with cls(c, v, seed=DEV_SEED_BASE + 500 + (ci * 10 + vi) * 1000 + i, oracle=False) as env:
                    for a in env.catalog():
                        o = env.execute(a)
                        if o.valid:
                            est.observe(a.id, c, o.outcome)
    tables = est.tables(cls.build_catalog(oracle=False), cls.hypotheses_())
    return cls, {cls.TARGET: tables}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--quick", action="store_true", help="smoke test: every 7th task, one repeat")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    FAMILIES["sec"], FAMILIES["sigma"] = sec_family(), sigma_family()
    stride = 7 if args.quick else 1
    jobs = []
    for fam in FAMILIES.values():
        reps = 1 if args.quick else fam["repeats"]
        tasks = fam["tasks"][::stride]
        for config in ("eig_posterior", "eig_confirm", "static_confirm", "catalogue_confirm"):
            jobs += [("D1", fam["name"], config, t, r, {}) for t in tasks for r in range(reps)]
        for th in THRESHOLDS:
            for config in ("eig_posterior", "eig_confirm"):
                jobs += [(f"D2@{th}", fam["name"], config, t, r, {"threshold": th}) for t in tasks for r in range(reps)]
    from hesp.secapp import CAUSES
    sec_tasks = [t for t in FAMILIES["sec"]["tasks"] if t["variant"] != "drift"][::stride]
    reps = 1 if args.quick else 3
    for beta in (0.25, 0.5):
        JOBS_CTX[f"confusion{beta}"] = {k: confusion_tables(v, beta) for k, v in FAMILIES["sec"]["tables"].items()}
        jobs += [(f"D3 confusion {beta}", "sec", config, t, r, {"tables": f"confusion{beta}"})
                 for config in ("eig_posterior", "eig_confirm") for t in sec_tasks for r in range(reps)]
    for cause in CAUSES:
        cls, tables = absent_family(cause)
        JOBS_CTX[f"absent:{cause}"] = tables
        JOBS_CTX[f"absent_factory:{cause}"] = (lambda k: (lambda task, seed: k(task["cause"], task["variant"], seed)))(cls)
        jobs += [("D3 absent", "sec", config, t, r, {"tables": f"absent:{cause}", "factory": f"absent_factory:{cause}"})
                 for config in ("eig_posterior", "eig_confirm") for t in sec_tasks if t["cause"] == cause
                 for r in range(reps)]
    cls, tables = mirror_family()
    JOBS_CTX["mirror"] = tables
    JOBS_CTX["mirror_factory"] = lambda task, seed: cls(task["cause"], task["variant"], seed)
    for config in ("eig_posterior", "eig_confirm"):
        jobs += [("D3 mirror", "sec", config, t, r, {"tables": "mirror", "factory": "mirror_factory"})
                 for t in sec_tasks for r in range(reps)]
    print(f"{len(jobs)} episodes on {args.workers} workers", flush=True)
    if args.workers > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(args.workers) as pool:
            rows = pool.map(episode, jobs, chunksize=8)
    else:
        rows = [episode(j) for j in jobs]
    agg = defaultdict(lambda: defaultdict(int))
    for group, fam, config, variant, cause, row in rows:
        for key in ((group, fam, config, "all"), (group, fam, config, variant)):
            a = agg["|".join(key)]
            a["episodes"] += 1
            a[row["outcome"]] += 1
            a["cost_sum"] += row["cost"]
            a["execution_errors"] += row["execution_error"]
            a["missed_attack"] += row["missed_attack"]
    with open(out / "episodes.jsonl", "w", encoding="utf-8") as f:
        for group, fam, config, variant, cause, row in rows:
            f.write(json.dumps({"group": group, "family": fam, "config": config, "variant": variant, **row}) + "\n")
    keys = ("verified", "correct_unverified", "wrong", "escalated", "missed_attack", "execution_errors")
    summary = {k: {**{x: v.get(x, 0) for x in keys}, "episodes": v["episodes"], "cost_sum": v["cost_sum"],
                   "mean_cost": v["cost_sum"] / v["episodes"]} for k, v in sorted(agg.items())}
    (out / "summary.json").write_text(json.dumps({"schema": "hesp.v11d.v1", "quick": args.quick,
                                                  "results": summary}, indent=2), encoding="utf-8")
    lines = ["# v1.1 part D (LLM-free)", "", "| Group | Family | Config | Variant | N | Verified | Correct, unverified | Wrong | Escalated | Missed attack (n) | Cost |",
             "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for k, v in summary.items():
        g, f, c, var = k.split("|")
        n = v["episodes"]
        lines.append(f"| {g} | {f} | {c} | {var} | {n} | {v['verified'] / n:.3f} | {v['correct_unverified'] / n:.3f} | "
                     f"{v['wrong'] / n:.3f} | {v['escalated'] / n:.3f} | {v['missed_attack']} | {v['mean_cost']:.2f} |")
    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("execution errors:", sum(v["execution_errors"] for k, v in summary.items() if k.endswith("|all")))


if __name__ == "__main__":
    main()
