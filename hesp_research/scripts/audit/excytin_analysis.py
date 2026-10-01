"""Analysis of the ExCyTIn shortcut audit (pre-registered in docs/PROTOCOL_AUDIT.md).

Reads results/audit/excytin_<split>.json and results/audit/excytin_reported_table2.json; writes
results/audit/excytin_<split>_analysis.json with incident-clustered bootstrap intervals (2,000 resamples, seed 2040)
for named / adjacent / graph / table rates, and per-model Spearman correlations between the reported per-incident
reward and the per-incident named rate (H3), with a sign test.
"""
import argparse
import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KEYS = ("named", "adjacent", "graph_correct", "table_correct")


def cluster_ci(per, key, seed=2040, b=2000):
    incs = sorted(per)
    rng = random.Random(seed)
    draws = []
    for _ in range(b):
        s = [rng.choice(incs) for _ in incs]
        num = sum(per[i][key] for i in s)
        den = sum(per[i]["n"] for i in s)
        draws.append(num / den)
    draws.sort()
    return [draws[int(0.025 * (b - 1))], draws[int(0.975 * (b - 1))]]


def ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(xs):
        j = i
        while j + 1 < len(xs) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(a, b):
    ra, rb = ranks(a), ranks(b)
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    cov = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    va = math.sqrt(sum((x - ma) ** 2 for x in ra))
    vb = math.sqrt(sum((y - mb) ** 2 for y in rb))
    return cov / (va * vb) if va and vb else 0.0


def sign_test_p(pos, n):
    """One-sided P(X >= pos) for X ~ Binomial(n, 0.5)."""
    return sum(math.comb(n, k) for k in range(pos, n + 1)) / 2 ** n


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--split", default="test")
    args = ap.parse_args()
    d = json.loads((ROOT / f"results/audit/excytin_{args.split}.json").read_text(encoding="utf-8"))["summary"]
    per = d["per_incident"]
    out = {"split": args.split, "questions": d["questions"], "rates": {}}
    for k in KEYS:
        out["rates"][k] = {"count": d[k], "rate": d[k] / d["questions"], "ci95_incident_cluster": cluster_ci(per, k)}
    rep = json.loads((ROOT / "results/audit/excytin_reported_table2.json").read_text(encoding="utf-8"))
    named = [per[i]["named"] / per[i]["n"] for i in rep["incidents"]]
    graph = [per[i]["graph_correct"] / per[i]["n"] for i in rep["incidents"]]
    out["per_incident"] = {i: {"named_rate": n_, "graph_rate": g_} for i, n_, g_ in zip(rep["incidents"], named, graph)}
    corr = {m: spearman(v[:8], named) for m, v in rep["models"].items()}
    pos = sum(1 for c in corr.values() if c > 0)
    out["h3"] = {"spearman_by_model": corr, "positive": pos, "models": len(corr),
                 "sign_test_one_sided_p": sign_test_p(pos, len(corr)),
                 "median": sorted(corr.values())[len(corr) // 2]}
    out["reported_average_reward"] = {m: v[8] for m, v in rep["models"].items()}
    path = ROOT / f"results/audit/excytin_{args.split}_analysis.json"
    path.write_text(json.dumps(out, indent=1), encoding="utf-8")
    for k, v in out["rates"].items():
        print(f"{k}: {v['count']}/{d['questions']} = {v['rate']:.3f}  CI {v['ci95_incident_cluster'][0]:.3f}-{v['ci95_incident_cluster'][1]:.3f}")
    print(f"H3: {pos}/{len(corr)} models positive, median rho {out['h3']['median']:.2f}, sign-test p {out['h3']['sign_test_one_sided_p']:.4f}")


if __name__ == "__main__":
    main()
