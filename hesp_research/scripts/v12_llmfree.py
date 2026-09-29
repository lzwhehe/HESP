"""v1.2 part B (LLM-free, CPU only): evidence policies, targeted same-source forgery, stall recovery, benign cost.

Written in response to the second review (2026-09-29). Every episode uses a scripted planner, so every verdict
is the controller's (or the script's, in G3). Pre-registered in docs/PROTOCOL.md v1.2 before any run.

G1  evidence policies. Stop rules: posterior; confirm (one specifically supporting observation); joint (leader
    >= r x every other NAMED hypothesis, which admits elimination); joint_open (also >= r x "other").
    r = 10, plus a sweep r in {3, 5, 30} for confirm and joint_open. Settings:
      sec-matched     sec-triage base+noise, counted tables (empirical_20)
      sec-absent      the true cause removed from the candidate set (as v1.1 D3)
      sec-confusion   each cause's rows mixed 0.25 toward one other cause (as v1.1 D3)
      comp            comp-triage (probabilistic outcomes, composite evidence, paired attack/admin causes),
                      tables counted from k = 20 LLM-free development episodes per cause and variant
    Every episode records both verifiers: single-signature (as in all earlier studies) and joint identification.
G2  targeted same-source forgery (sec-triage, spoof_feed): a fixed playbook reads source_ips, then threat_intel
    (both read the forged feed), then the rest in catalogue order; posterior stop with no corroboration,
    corroboration per probe, and corroboration per source group. Benign base cases measure the cost.
G3  stall recovery (sigma-triage and sec-triage): a scripted planner that proposes a finish for the leader as soon
    as its score reaches 0.5 (below the guard's 0.8), otherwise a probe; hesp mode, guard, confirm stop;
    finish_rejection_limit None (v1.1 behaviour) vs 2.
G4  benign cost on a wider set of benign causes (sigma-triage: 26 benign explanations over 12 rules): confirm stop
    without corroboration vs corroboration per probe (sigma-triage probes have no shared sources).

    python scripts/v12_llmfree.py --out results/v12b --workers 16
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
from hesp.controller import Budget, run                  # noqa: E402
from hesp.planner import NeverFinishPlanner             # noqa: E402
from hesp.predictors import EmpiricalEstimator          # noqa: E402
from hesp.selectors import Selector                     # noqa: E402
from hesp.study import cell_seed                        # noqa: E402
from v10b_mismatch import TargetPredictor               # noqa: E402
from v11_llmfree import StaticPlanner, absent_family, confusion_tables, sec_family, sigma_family  # noqa: E402

BUDGET = Budget(max_tool_calls=10, max_decisions=12, max_tool_cost=10, max_seconds=900.0)
ROOT = Path(__file__).resolve().parents[1]
DEV_SEED_BASE = 910_000
COMP_SEED, SEC_SEED, SIGMA_SEED = 2031, 2027, 2028
REPEATS = 3
CTX = {}


class StubbornPlanner:
    """Proposes a finish for the leader once its score reaches 0.5, citing its latest supporting current
    observations; otherwise proposes the next untried probe. Mimics the v1.1 Qwen2.5-7B stall."""
    name = "stubborn_finisher_script"

    def decide(self, request):
        inv = request.get("investigation") or {}
        hyps = {h["id"]: h["score"] for h in inv.get("hypotheses", [])}
        version = request["state_version"]
        if hyps:
            leader = max(sorted(hyps), key=lambda h: hyps[h])
            if leader != "other" and hyps[leader] >= 0.5:
                cites = [e["observation_id"] for e in reversed(inv.get("evidence", []))
                         if e.get("used") and e.get("state_version") == version
                         and e.get("relations", {}).get(leader) == "support"][:3]
                if cites:
                    return {"kind": "finish", "hypothesis": leader, "evidence_ids": cites, "reason": "stubborn",
                            "usage": {"input_tokens": 0, "output_tokens": 0}}
        tried = {(o["action_id"], o["state_version"]) for o in request["history"]}
        options = [t for t in request["tools"] if (t["id"], version) not in tried] or request["tools"]
        return {"kind": "action", "action_id": options[0]["id"], "reason": "stubborn: probe",
                "usage": {"input_tokens": 0, "output_tokens": 0}}


def comp_family():
    from hesp.compapp import CompEnvironments, comp_suite
    envs = CompEnvironments()
    tables = {}
    for si, (name, cls) in enumerate(envs.classes.items()):
        est = EmpiricalEstimator(eps=0.01)
        for i in range(1, 21):
            for ci, c in enumerate(cls.CAUSES):
                for vi, v in enumerate(("base", "noise")):
                    with cls(c, v, seed=DEV_SEED_BASE + si * 10_000 + (ci * 10 + vi) * 100 + i,
                             oracle=False) as env:
                        for a in env.catalog():
                            o = env.execute(a)
                            if o.valid:
                                est.observe(a.id, c, o.outcome)
        tables[cls.TARGET] = est.tables(cls.build_catalog(oracle=False), cls.hypotheses_())
    return {"tasks": comp_suite(), "factory": envs, "tables": tables}


def classify(result, truth, benign):
    claim = result["claimed_hypothesis"]
    if result["verified_simulation"]:
        cls = "verified"
    elif claim is None or claim == "other":
        cls = "escalated"
    elif claim == truth:
        cls = "correct_unverified"
    else:
        cls = "wrong"
    return {"outcome": cls, "verified_joint": bool(result.get("verified_joint")), "correct": claim == truth,
            "missed_attack": truth not in benign and claim in benign, "claim": claim, "truth": truth}


def episode(job):
    group, setting, config, task, repeat, extra = job
    seed = cell_seed(extra["seed"], task["task_id"], repeat)
    factory = CTX[extra["factory"]]
    tables = CTX[extra["tables"]]
    env = None
    for attempt in range(30):
        try:
            env = factory(task, seed)
            break
        except OSError:
            time.sleep(0.1 * (attempt + 1))
    if env is None:
        raise RuntimeError("sandbox did not start")
    kw = dict(auto_finish=0.8, stop_rule=extra.get("stop_rule", "posterior"),
              specific_ratio=extra.get("ratio", 10.0), record_joint=True)
    planner, mode = NeverFinishPlanner(), "hesp"
    if extra.get("playbook"):
        planner, mode = StaticPlanner(extra["playbook"]), "memory_only"
    if extra.get("stubborn"):
        planner, mode = StubbornPlanner(), "hesp"
        kw.update(finish_guard=True, finish_rejection_limit=extra.get("limit"))
    if extra.get("corroborate"):
        kw.update(corroborate_benign=2, corroborate_unit=extra["corroborate"])
    with tempfile.TemporaryDirectory() as tmp:
        with env:
            r = run(env, planner, mode, Path(tmp) / "r", BUDGET, predictor=TargetPredictor(tables, "empirical_20"),
                    selector=Selector("eig_cost", seed), show_rankings=False, **kw)
            truth = env._app.cause
            benign = frozenset(type(env).BENIGN)
    return {"group": group, "setting": setting, "config": config, "task_id": task["task_id"], "repeat": repeat,
            "variant": task["variant"], "cost": r["tool_cost_units"], "status": r["status"],
            "finished_by": r.get("finished_by"), "finish_rejections": r["finish_rejections"],
            "execution_error": r["status"] == "EXECUTION_ERROR", **classify(r, truth, benign)}


def jobs_for(quick):
    stride = 7 if quick else 1
    reps = 1 if quick else REPEATS
    jobs = []
    sec = sec_family()
    sec_target = next(iter(sec["tables"]))
    CTX["sec_factory"], CTX["sec_tables"] = sec["factory"], sec["tables"]
    sec_tasks = [t for t in sec["tasks"] if t["variant"] != "drift"][::stride]
    CTX["sec_conf"] = {k: confusion_tables(v, 0.25) for k, v in sec["tables"].items()}
    comp = comp_family()
    CTX["comp_factory"], CTX["comp_tables"] = comp["factory"], comp["tables"]
    comp_tasks = comp["tasks"][::stride]
    rules = [("posterior", 10.0), ("confirm", 10.0), ("joint", 10.0), ("joint_open", 10.0),
             ("confirm", 3.0), ("confirm", 5.0), ("confirm", 30.0), ("joint_open", 3.0), ("joint_open", 5.0),
             ("joint_open", 30.0)]
    for rule, ratio in rules:
        cfg = f"{rule}@{ratio:g}"
        common = {"stop_rule": rule, "ratio": ratio}
        jobs += [("G1", "sec-matched", cfg, t, r, {**common, "seed": SEC_SEED, "factory": "sec_factory", "tables": "sec_tables"})
                 for t in sec_tasks for r in range(reps)]
        jobs += [("G1", "sec-confusion", cfg, t, r, {**common, "seed": SEC_SEED, "factory": "sec_factory", "tables": "sec_conf"})
                 for t in sec_tasks for r in range(reps)]
        jobs += [("G1", "comp", cfg, t, r, {**common, "seed": COMP_SEED, "factory": "comp_factory", "tables": "comp_tables"})
                 for t in comp_tasks for r in range(reps)]
    from hesp.secapp import CAUSES
    for cause in CAUSES:
        cls, tables = absent_family(cause)
        CTX[f"abs_t:{cause}"] = tables
        CTX[f"abs_f:{cause}"] = (lambda k: (lambda task, seed: k(task["cause"], task["variant"], seed)))(cls)
        for rule, ratio in rules:
            jobs += [("G1", "sec-absent", f"{rule}@{ratio:g}", t, r,
                      {"stop_rule": rule, "ratio": ratio, "seed": SEC_SEED, "factory": f"abs_f:{cause}", "tables": f"abs_t:{cause}"})
                     for t in sec_tasks if t["cause"] == cause for r in range(reps)]
    # G2: targeted same-source forgery
    from hesp.secapp import BENIGN, SecTriageEnvironment, sec_suite
    order = ["source_ips", "threat_intel"] + [p["id"] for p in SecTriageEnvironment.PROBES
                                               if p["id"] not in ("source_ips", "threat_intel")]
    feed = [t for t in sec_suite(("spoof_feed",)) if t["cause"] not in BENIGN][::1 if not quick else 3]
    benign = [t for t in sec_suite(("base",)) if t["cause"] in BENIGN]
    for corr in (None, "probe", "source"):
        cfg = f"playbook_corr_{corr or 'none'}"
        for tasks in (feed, benign):
            jobs += [("G2", "spoof_feed" if tasks is feed else "benign", cfg, t, r,
                      {"playbook": order, "corroborate": corr, "seed": 2029, "factory": "sec_factory", "tables": "sec_tables"})
                     for t in tasks for r in range(reps)]
    # G3: stall recovery
    sigma = sigma_family()
    CTX["sigma_factory"], CTX["sigma_tables"] = sigma["factory"], sigma["tables"]
    sigma_tasks = sigma["tasks"][::stride]
    for limit in (None, 2):
        cfg = f"stubborn_limit_{limit}"
        jobs += [("G3", "sigma", cfg, t, r, {"stubborn": True, "limit": limit, "stop_rule": "confirm", "seed": SIGMA_SEED,
                                              "factory": "sigma_factory", "tables": "sigma_tables"})
                 for t in sigma_tasks for r in range(2 if not quick else 1)]
        jobs += [("G3", "sec", cfg, t, r, {"stubborn": True, "limit": limit, "stop_rule": "confirm", "seed": SEC_SEED,
                                            "factory": "sec_factory", "tables": "sec_tables"})
                 for t in sec_tasks for r in range(reps)]
    # G4: benign cost on sigma-triage
    for corr in (None, "probe"):
        jobs += [("G4", "sigma", f"confirm_corr_{corr or 'none'}", t, r,
                  {"stop_rule": "confirm", "corroborate": corr, "seed": SIGMA_SEED, "factory": "sigma_factory",
                   "tables": "sigma_tables"})
                 for t in sigma_tasks for r in range(2 if not quick else 1)]
    return jobs


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    jobs = jobs_for(args.quick)
    print(f"{len(jobs)} episodes on {args.workers} workers", flush=True)
    if args.workers > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(args.workers) as pool:
            rows = pool.map(episode, jobs, chunksize=8)
    else:
        rows = [episode(j) for j in jobs]
    with open(out / "episodes.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    agg = defaultdict(lambda: defaultdict(int))
    for r in rows:
        a = agg[(r["group"], r["setting"], r["config"])]
        a["episodes"] += 1
        a[r["outcome"]] += 1
        a["verified_joint"] += r["verified_joint"]
        a["correct"] += r["correct"]
        a["missed_attack"] += r["missed_attack"]
        a["cost"] += r["cost"]
        a["execution_errors"] += r["execution_error"]
        a["stalled"] += r["status"] == "DECISION_BUDGET_EXCEEDED"
    lines = ["# v1.2 part B (LLM-free)", "",
             "| Group | Setting | Config | N | Verified (single) | Verified (joint) | Correct cause | Wrong | Escalated | Missed attack | Decision budget out | Cost |",
             "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    summary = {}
    for (g, s, c), a in sorted(agg.items()):
        n = a["episodes"]
        summary[f"{g}|{s}|{c}"] = {**a, "mean_cost": a["cost"] / n}
        lines.append(f"| {g} | {s} | {c} | {n} | {a['verified']} | {a['verified_joint']} | {a['correct']} | {a['wrong']} | "
                     f"{a['escalated']} | {a['missed_attack']} | {a['stalled']} | {a['cost'] / n:.2f} |")
    (out / "summary.json").write_text(json.dumps({"schema": "hesp.v12b.v1", "quick": args.quick, "results": summary},
                                                 indent=2), encoding="utf-8")
    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("execution errors:", sum(a["execution_errors"] for a in agg.values()))


if __name__ == "__main__":
    main()
