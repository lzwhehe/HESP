"""Regenerate every v0.6 (RQ3) number reported in RESULTS.md from the raw outcomes.

Single source of truth for the v0.6 tables -- never retype them by hand (errata E-1).

The per-run report.md / analysis.json files were produced by the frozen code and are kept
unchanged. Their security-metric block contains a known bug (drift verdicts were scored
against the initial cause); this script recomputes those metrics with the corrected
``hesp.analysis.true_cause``. Verification rates and paired intervals are unaffected.

Also runs two post-hoc, clearly exploratory analyses:
  * which final causes the self-elicited table can close under the guard
  * the LLM-free "other"-row check: is the whole oracle gap due to the one row that
    development data can never observe (PROTOCOL.md R-6)?

    python scripts/v06_summary.py                  # Markdown to stdout
    python scripts/v06_summary.py --json results/v06_summary.json
"""
import argparse
import collections
import copy
import json
from pathlib import Path
import statistics
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hesp.analysis import security_metrics, summarize, true_cause
from hesp.controller import Budget, run
from hesp.planner import PosteriorPlanner
from hesp.predictors import FrozenPredictor
from hesp.secapp import SecTriageEnvironment, make_sec_env, sec_suite
from hesp.selectors import Selector
from hesp.study import cell_seed

MODELS = [("7b", "Qwen2.5-7B"), ("32b", "Qwen2.5-32B-AWQ"), ("72b", "Qwen2.5-72B-AWQ")]
ARMS = ["react_style", "memory_only", "hesp_eigc_guard_designer", "hesp_eigc_guard_emp1",
        "hesp_eigc_guard_emp5", "hesp_eigc_guard_emp20", "hesp_eigc_guard_emp100", "hesp_eigc_guard_llmp"]
PRIMARY = ("hesp_eigc_guard_emp20", "memory_only")
COMPARISONS = [PRIMARY,
               ("hesp_eigc_guard_emp1", "memory_only"),
               ("hesp_eigc_guard_emp5", "memory_only"),
               ("hesp_eigc_guard_emp100", "memory_only"),
               ("hesp_eigc_guard_designer", "hesp_eigc_guard_emp20"),
               ("hesp_eigc_guard_emp20", "hesp_eigc_guard_llmp"),
               ("hesp_eigc_guard_designer", "memory_only"),
               ("memory_only", "react_style")]
SEED = 2026


def short(arm):
    return arm.replace("hesp_eigc_guard_", "")


def ci(v):
    lo, hi = v["cluster_bootstrap_percentile_95"]
    return f"[{lo:+.3f}, {hi:+.3f}]"


def fmt(x, d=3):
    return "n/a" if x is None else f"{x:.{d}f}"


def load(results, model):
    with (results / f"v06_{model}" / "outcomes.jsonl").open(encoding="utf-8") as stream:
        rows = [json.loads(line) for line in stream]
    # The security metrics are only meaningful if true_cause agrees with the verifier.
    bad = [(r["task_id"], r["arm"]) for r in rows
           if r["verified_simulation"] and r["claimed_hypothesis"] != true_cause(r)]
    if bad:
        raise SystemExit(f"{model}: true_cause disagrees with the verifier on {len(bad)} rows, e.g. {bad[:3]}")
    return rows


def llmp_by_final_cause(rows):
    """Under the guard, which final causes can the model's own elicited table close?"""
    by = collections.defaultdict(list)
    for r in rows:
        if r["arm"] == "hesp_eigc_guard_llmp":
            by[true_cause(r)].append(r["verified_simulation"])
    return {c: statistics.mean(v) for c, v in sorted(by.items())}


def other_row_check(results):
    """Post-hoc, LLM-free: swap only the unobservable 'other' row into the empirical table."""
    designer = {a.id: a.likelihoods for a in SecTriageEnvironment.build_catalog()}
    emp20 = json.loads((results / "v06_tables" / "empirical_20.json").read_text(encoding="utf-8"))["tables"]
    patched = copy.deepcopy(emp20)
    for action in patched:
        patched[action]["other"] = designer[action]["other"]
    sources = {"designer": designer, "emp20": emp20, "emp20 + designer 'other' row": patched}
    out = {}
    with tempfile.TemporaryDirectory() as root:
        for i, (name, table) in enumerate(sources.items()):
            predictor = FrozenPredictor(table, name)
            ok, cost = [], []
            for task in sec_suite():
                for repeat in (1, 2, 3):
                    s = cell_seed(SEED, task["task_id"], repeat)
                    with make_sec_env(task, s) as env:
                        r = run(env, PosteriorPlanner(), "hesp", Path(root) / f"s{i}_{task['task_id']}_{repeat}",
                                Budget(10, 12, 10, 900), predictor=predictor, selector=Selector("eig_cost", s),
                                finish_guard=True)
                    ok.append(r["verified_simulation"])
                    cost.append(r["tool_cost_units"])
            out[name] = {"verified": statistics.mean(ok), "mean_tool_cost": statistics.mean(cost)}
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--results", default=str(ROOT / "results"))
    parser.add_argument("--json")
    parser.add_argument("--skip-other-row-check", action="store_true")
    args = parser.parse_args()
    results = Path(args.results)
    sys.stdout.reconfigure(encoding="utf-8")   # Windows consoles default to GBK / cp1252

    data, L = {}, []
    for model, label in MODELS:
        rows = load(results, model)
        report = summarize(rows, seed=SEED, arms=ARMS, comparisons=COMPARISONS)
        data[model] = {
            "episodes": len(rows),
            "source_hashes": sorted({r["source_sha256"][:8] for r in rows}),
            "verified": {a: report["modes"][a]["verified_fraction"] for a in ARMS},
            "mean_tool_cost": {a: report["modes"][a]["tool_cost_units"]["mean_known"] for a in ARMS},
            "paired_verification": report["paired_verification"],
            "paired_tool_cost": report["paired_tool_cost"],
            "security_metrics_corrected": {a: security_metrics([r for r in rows if r["arm"] == a]) for a in ARMS},
            "llmp_verified_by_final_cause": llmp_by_final_cause(rows),
        }

    key = f"{PRIMARY[0]}_minus_{PRIMARY[1]}"
    L += [f"### Pre-registered primary endpoint ({key}, 7B; 32B/72B exploratory per R-9)", "",
          "| Model | delta verified | 95% cluster interval | tasks better / worse |", "| --- | ---: | --- | ---: |"]
    for model, label in MODELS:
        v = data[model]["paired_verification"][key]
        L.append(f"| {label} | {v['difference']:+.3f} | {ci(v)} | {v['tasks_better']} / {v['tasks_worse']} |")

    L += ["", "### Verified fraction by arm", "",
          "| Arm | " + " | ".join(l for _, l in MODELS) + " |", "| --- |" + " ---: |" * len(MODELS)]
    for a in ARMS:
        L.append(f"| {a} | " + " | ".join(f"{data[m]['verified'][a]:.3f}" for m, _ in MODELS) + " |")

    L += ["", "### Mean tool cost by arm", "",
          "| Arm | " + " | ".join(l for _, l in MODELS) + " |", "| --- |" + " ---: |" * len(MODELS)]
    for a in ARMS:
        L.append(f"| {a} | " + " | ".join(f"{data[m]['mean_tool_cost'][a]:.2f}" for m, _ in MODELS) + " |")

    L += ["", "### Paired comparisons (verified fraction; tool cost)", "",
          "| Comparison | " + " | ".join(l for _, l in MODELS) + " |", "| --- |" + " --- |" * len(MODELS)]
    for t, b in COMPARISONS:
        name = f"{t}_minus_{b}"
        cells = []
        for m, _ in MODELS:
            v, c = data[m]["paired_verification"][name], data[m]["paired_tool_cost"][name]
            cells.append(f"{v['difference']:+.3f} {ci(v)}; cost {c['difference']:+.2f}")
        L.append(f"| {short(t)} − {short(b)} | " + " | ".join(cells) + " |")

    L += ["", "### Security-facing metrics, corrected (descriptive only)", "",
          "Ground truth is the cause in effect at the verdict: `drift_to` only if the drift had already "
          "happened. Checked: every verified claim equals this ground truth.", ""]
    for m, label in MODELS:
        L += [f"**{label}**", "",
              "| Arm | with a claim | unresolved | missed attack | false escalation | wrong cause | citation validity |",
              "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
        for a in ARMS:
            s = data[m]["security_metrics_corrected"][a]
            L.append(f"| {short(a)} | {s['episodes_with_a_claim']}/{s['episodes']} | {fmt(s['unresolved_rate'])} | "
                     f"{fmt(s['missed_attack_rate'])} | {fmt(s['false_escalation_rate'])} | "
                     f"{fmt(s['wrong_cause_rate'])} | {fmt(s['evidence_citation_validity'])} |")
        L.append("")

    L += ["### Exploratory: self-elicited table under the guard, verified by final cause", "",
          "| Final cause | " + " | ".join(l for _, l in MODELS) + " |", "| --- |" + " ---: |" * len(MODELS)]
    for c in data["7b"]["llmp_verified_by_final_cause"]:
        L.append(f"| {c} | " + " | ".join(f"{data[m]['llmp_verified_by_final_cause'][c]:.2f}" for m, _ in MODELS) + " |")

    if not args.skip_other_row_check:
        check = other_row_check(results)
        data["other_row_check_llm_free"] = check
        L += ["", "### Exploratory, LLM-free: does the unobservable 'other' row explain the oracle gap?", "",
              "| Predictive table | verified | mean tool cost |", "| --- | ---: | ---: |"]
        for name, v in check.items():
            L.append(f"| {name} | {v['verified']:.3f} | {v['mean_tool_cost']:.2f} |")

    print("\n".join(L))
    if args.json:
        Path(args.json).write_bytes((json.dumps(data, indent=2) + "\n").encode("utf-8"))


if __name__ == "__main__":
    main()
