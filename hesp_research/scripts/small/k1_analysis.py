"""K1 analysis (docs/PROTOCOL_SMALL.md, revision K1): accuracy per condition, paired differences with incident-clustered
bootstrap intervals (2,000 resamples, seed 2040), G1/G2/G3 decisions, and a random sample of 40 judgments for manual check.

    python scripts/small/k1_analysis.py --dir results/small/k1
"""
import argparse
import json
import random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONDS = ("C1", "C2", "C3", "C4")


def load(d):
    out = {}
    for c in CONDS:
        p = Path(d) / f"{c}.jsonl"
        out[c] = {(r["incident"], r["index"]): r for r in map(json.loads, open(p, encoding="utf-8"))} if p.exists() else {}
    return out


def acc(rows, keys):
    return sum(rows[k]["correct"] for k in keys) / len(keys) if keys else float("nan")


def diff_ci(a, b, keys, seed=2040, n=2000):
    by = defaultdict(list)
    for k in keys:
        by[k[0]].append(k)
    incs = sorted(by)
    point = acc(a, keys) - acc(b, keys)
    rng = random.Random(seed)
    draws = []
    for _ in range(n):
        ks = [k for i in (rng.choice(incs) for _ in incs) for k in by[i]]
        draws.append(acc(a, ks) - acc(b, ks))
    draws.sort()
    pa = sum(1 for k in keys if a[k]["correct"] and not b[k]["correct"])
    pb = sum(1 for k in keys if b[k]["correct"] and not a[k]["correct"])
    return {"diff": point, "ci95": [draws[int(0.025 * (n - 1))], draws[int(0.975 * (n - 1))]], "a_only": pa, "b_only": pb}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=str(ROOT / "results/small/k1"))
    args = ap.parse_args()
    R = load(args.dir)
    keys = sorted(set.intersection(*(set(R[c]) for c in CONDS)))
    res = [k for k in keys if R["C1"][k]["resistant"] == 1]
    out = {"questions": len(keys), "resistant": len(res), "conditions": {}}
    for c in CONDS:
        rows = R[c]
        out["conditions"][c] = {
            "accuracy": acc(rows, keys), "accuracy_resistant": acc(rows, res),
            "accuracy_other": acc(rows, [k for k in keys if k not in res]),
            "no_answer": sum(not rows[k]["submitted"] for k in keys), "overflow": sum(rows[k]["overflow"] for k in keys),
            "rejected_once": sum(rows[k]["rejected_once"] for k in keys),
            "mean_steps": sum(rows[k]["steps"] for k in keys) / len(keys)}
    best = max(("C2", "C3"), key=lambda c: out["conditions"][c]["accuracy"])
    out["best_structure"] = best
    out["contrasts"] = {
        f"{best}-C1": diff_ci(R[best], R["C1"], keys),
        f"{best}-C4": diff_ci(R[best], R["C4"], keys),
        f"{best}-C4 (resistant)": diff_ci(R[best], R["C4"], res),
        "C3-C2": diff_ci(R["C3"], R["C2"], keys),
        "C2-C1": diff_ci(R["C2"], R["C1"], keys),
        "C3-C1": diff_ci(R["C3"], R["C1"], keys)}
    g1 = out["contrasts"][f"{best}-C1"]["diff"] >= 0.15
    g2 = out["contrasts"][f"{best}-C4"]["diff"] >= 0.10 and out["contrasts"][f"{best}-C4 (resistant)"]["diff"] >= 0.10
    g3 = out["contrasts"]["C3-C2"]["diff"] >= -0.05
    out["decision"] = {"G1": g1, "G2": g2, "G3_not_worse": g3, "continue": g1 and g2}
    rng = random.Random(7)
    sample = [(c, k) for c in ("C1", "C2", "C3") for k in rng.sample(keys, 13)] + [("C4", rng.choice(keys))]
    out["manual_check"] = [{"cond": c, "incident": k[0], "index": k[1], "gold": R[c][k]["gold"], "answer": R[c][k]["answer"],
                            "scored_correct": R[c][k]["correct"]} for c, k in sample]
    Path(args.dir, "analysis.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    for c, v in out["conditions"].items():
        print(f"{c}: all {v['accuracy']:.3f}  resistant {v['accuracy_resistant']:.3f}  other {v['accuracy_other']:.3f}  "
              f"no-answer {v['no_answer']}  overflow {v['overflow']}  steps {v['mean_steps']:.1f}")
    for name, v in out["contrasts"].items():
        print(f"{name}: {v['diff']:+.3f} [{v['ci95'][0]:+.3f}, {v['ci95'][1]:+.3f}]  a-only {v['a_only']} b-only {v['b_only']}")
    print("decision", out["decision"])


if __name__ == "__main__":
    main()
