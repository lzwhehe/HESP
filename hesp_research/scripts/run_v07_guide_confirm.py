"""v0.7 part A: LLM-free confirmation on GUIDE cold-start test incidents (PROTOCOL.md v0.7).

History = the GUIDE training split; evaluation = cold-start incidents of the official test split.
Primary endpoint: TP recall of hesp_eigc@4 minus history, 95 % organisation-cluster bootstrap
(2000 resamples, seed 2026). Key secondary: macro-F1 difference, non-inferiority margin -0.02.

    python scripts/run_v07_guide_confirm.py --history ../external/guide_incidents_train.jsonl \
        --test ../external/guide_incidents_test.jsonl --out results/v07_guide_confirm
"""
import argparse
import collections
import hashlib
import json
import math
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hesp.controller import source_hash
from hesp.guideapp import GRADES, PROBES, GuideModel, load_incidents

SEED, RESAMPLES, BUDGET = 2026, 2000, 4
FIXED_ORDER = ["category", "entity_types", "technique", "evidence_roles", "scale", "roles", "threat_family",
               "geography", "detector", "auto_verdict"]      # the development pilot's playbook order


def entropy(p):
    return -sum(v * math.log2(v) for v in p.values() if v > 0)


def update(post, row, o):
    z = sum(post[h] * row[h][o] for h in GRADES)
    return {h: post[h] * row[h][o] / z for h in GRADES}


def eig(model, post, probe):
    rows = model.tables[probe]
    exp = 0.0
    for o in rows[GRADES[0]]:
        po = sum(post[h] * rows[h][o] for h in GRADES)
        if po > 0:
            exp += po * entropy({h: post[h] * rows[h][o] / po for h in GRADES})
    return entropy(post) - exp


def triage(model, incident, policy, budget, rng):
    post, left, spent = model.org_prior(incident["org"]), list(PROBES), 0
    while True:
        legal = [p for p in left if spent + PROBES[p][0] <= budget]
        if not legal:
            break
        if policy == "eig_cost":
            p = max(legal, key=lambda q: (eig(model, post, q) / PROBES[q][0], q))
        elif policy == "fixed":
            p = next(q for q in FIXED_ORDER if q in legal)
        else:
            p = rng.choice(sorted(legal))
        post = update(post, model.tables[p], model.outcome(incident, p))
        left.remove(p)
        spent += PROBES[p][0]
    return max(GRADES, key=lambda h: post[h]), spent


def confusion(pairs):
    """3x3 counts indexed [true][predicted] in GRADES order."""
    c = [[0] * 3 for _ in GRADES]
    for g, p in pairs:
        c[GRADES.index(g)][GRADES.index(p)] += 1
    return c


def metrics_from(c):
    n = sum(map(sum, c))
    f1 = []
    for i in range(3):
        tp, pp, ap = c[i][i], sum(c[j][i] for j in range(3)), sum(c[i])
        f1.append(0.0 if tp == 0 else 2 * tp / (pp + ap))
    tp_row = c[0]
    non_tp_pred_tp = c[1][0] + c[2][0]
    return {"accuracy": sum(c[i][i] for i in range(3)) / n, "macro_f1": sum(f1) / 3,
            "tp_recall": tp_row[0] / max(sum(tp_row), 1),
            "false_escalation": non_tp_pred_tp / max(sum(c[1]) + sum(c[2]), 1)}


def metrics(pairs):
    """pairs: list of (grade, prediction)."""
    return metrics_from(confusion(pairs))


def cluster_bootstrap(by_org, comparisons):
    """95 % percentile intervals of metric(a) - metric(b), resampling organisations.

    Per-organisation confusion matrices are summed per resample, which is exactly the
    incident-level metric on the resampled set of organisations."""
    rng = random.Random(SEED)
    orgs = sorted(by_org)
    names = sorted({x for a, b, _ in comparisons for x in (a, b)})
    per = {o: {n: confusion([(r["grade"], r["pred"][n]) for r in by_org[o]]) for n in names} for o in orgs}
    draws = {k: [] for k in comparisons}
    for _ in range(RESAMPLES):
        tot = {n: [[0] * 3 for _ in GRADES] for n in names}
        for o in rng.choices(orgs, k=len(orgs)):
            for n in names:
                m = per[o][n]
                t = tot[n]
                for i in range(3):
                    for j in range(3):
                        t[i][j] += m[i][j]
        mets = {n: metrics_from(tot[n]) for n in names}
        for a, b, m in comparisons:
            draws[(a, b, m)].append(mets[a][m] - mets[b][m])
    out = {}
    for k, v in draws.items():
        v.sort()
        out[k] = [v[int((RESAMPLES - 1) * 0.025)], v[int((RESAMPLES - 1) * 0.975)]]
    return out


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--history", required=True)
    ap.add_argument("--test", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    model = GuideModel(load_incidents(args.history))
    test = load_incidents(args.test)
    cold = [r for r in test if model.cold_kind(r)]
    rng = random.Random(SEED)
    policies = {"history": None, "prior_only": ("eig_cost", 0), "hesp_eigc@4": ("eig_cost", 4),
                "fixed@4": ("fixed", 4), "random@4": ("random", 4), "hesp_eigc@2": ("eig_cost", 2),
                "hesp_eigc@6": ("eig_cost", 6), "all_probes": ("eig_cost", sum(c for c, _ in PROBES.values()))}
    for r in cold:
        r["pred"], r["cold"] = {}, model.cold_kind(r)
        for name, spec in policies.items():
            r["pred"][name] = model.history_verdict(r) if spec is None else triage(model, r, *spec, rng)[0]
    by_org = collections.defaultdict(list)
    for r in cold:
        by_org[r["org"]].append(r)

    summary = {"n_test_incidents": len(test), "n_cold": len(cold), "n_orgs": len(by_org),
               "cold_kinds": dict(collections.Counter(r["cold"] for r in cold)),
               "grade_mix": dict(collections.Counter(r["grade"] for r in cold)),
               "source_sha256": source_hash(),
               "inputs_sha256": {"history": sha(args.history), "test": sha(args.test)},
               "policies": {n: metrics([(r["grade"], r["pred"][n]) for r in cold]) for n in policies},
               "by_cold_kind": {k: {n: metrics([(r["grade"], r["pred"][n]) for r in cold if r["cold"] == k])
                                    for n in ("history", "hesp_eigc@4")} for k in ("unseen", "mixed")}}
    comps = [(a, b, m) for (a, b), mets in {
        ("hesp_eigc@4", "history"): ("tp_recall", "macro_f1", "accuracy", "false_escalation"),
        ("hesp_eigc@4", "fixed@4"): ("tp_recall", "macro_f1", "accuracy"),
        ("hesp_eigc@4", "random@4"): ("tp_recall", "macro_f1", "accuracy")}.items() for m in mets]
    cis = cluster_bootstrap(by_org, comps)
    d = {f"{a} - {b} | {m}": {"difference": summary["policies"][a][m] - summary["policies"][b][m],
                              "ci95": cis[(a, b, m)]} for a, b, m in comps}
    summary["paired"] = d
    prim = d["hesp_eigc@4 - history | tp_recall"]
    sec = d["hesp_eigc@4 - history | macro_f1"]
    summary["primary_confirmed"] = prim["ci95"][0] > 0
    summary["macro_f1_noninferior"] = sec["ci95"][0] > -0.02
    (out / "summary.json").write_bytes((json.dumps(summary, indent=1) + "\n").encode("utf-8"))
    with open(out / "predictions.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for r in cold:
            f.write(json.dumps({"org": r["org"], "incident": r["incident"], "grade": r["grade"], "cold": r["cold"],
                                "pred": r["pred"]}) + "\n")

    print(f"cold test incidents {len(cold):,} of {len(test):,} | orgs {len(by_org):,} | kinds {summary['cold_kinds']}")
    print(f"grade mix {summary['grade_mix']}\n")
    print(f"{'policy':14s} {'acc':>6s} {'macroF1':>8s} {'TP recall':>9s} {'false esc.':>10s}")
    for n, m in summary["policies"].items():
        print(f"{n:14s} {m['accuracy']:6.3f} {m['macro_f1']:8.3f} {m['tp_recall']:9.3f} {m['false_escalation']:10.3f}")
    print()
    for k, v in d.items():
        print(f"{k:45s} {v['difference']:+.3f}  [{v['ci95'][0]:+.3f}, {v['ci95'][1]:+.3f}]")
    print(f"\nPRIMARY (TP recall, hesp_eigc@4 - history) confirmed: {summary['primary_confirmed']}")
    print(f"macro-F1 non-inferior (lower bound > -0.02): {summary['macro_f1_noninferior']}")


if __name__ == "__main__":
    main()
