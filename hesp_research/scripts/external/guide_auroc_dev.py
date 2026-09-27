"""Operating-point-free check on development data: does evidence integration rank true
positives better than history? (Train-internal split only; used to choose the v0.7 endpoint.)

Scores for "is this a true positive":
  history  : TP share of the (org, detector) history, smoothed toward the org prior (alpha = 20)
  hesp@k   : posterior P(TP) after EIG/cost probing with budget k, starting from the org prior
AUROC is computed on cold-start incidents; the interval resamples organisations.

    python scripts/external/guide_auroc_dev.py --history H.jsonl --test T.jsonl
"""
import argparse
import collections
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hesp.guideapp import GRADES, PROBES, PRIOR_ALPHA, GuideModel, load_incidents   # noqa: E402
from run_v07_guide_confirm import eig, update   # noqa: E402


def auroc(pairs):
    """pairs: (score, is_positive). Mann-Whitney with average ranks for ties."""
    pairs = sorted(pairs)
    ranks, i = [], 0
    while i < len(pairs):
        j = i
        while j < len(pairs) and pairs[j][0] == pairs[i][0]:
            j += 1
        ranks += [(i + j + 1) / 2] * (j - i)
        i = j
    pos = sum(y for _, y in pairs)
    neg = len(pairs) - pos
    rsum = sum(r for r, (_, y) in zip(ranks, pairs) if y)
    return (rsum - pos * (pos + 1) / 2) / (pos * neg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--history", required=True)
    ap.add_argument("--test", required=True)
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    model = GuideModel(load_incidents(args.history))
    cold = [r for r in load_incidents(args.test) if model.cold_kind(r)]
    for r in cold:
        prior = model.org_prior(r["org"])
        c = model.org_detector.get((r["org"], r["o"]["detector"]), collections.Counter())
        n = sum(c.values())
        r["s"] = {"history": (c["TruePositive"] + PRIOR_ALPHA * prior["TruePositive"]) / (n + PRIOR_ALPHA),
                  "prior": prior["TruePositive"]}
        for b in (2, 4, 6):
            post, left, spent = dict(prior), list(PROBES), 0
            while True:
                legal = [p for p in left if spent + PROBES[p][0] <= b]
                if not legal:
                    break
                p = max(legal, key=lambda q: (eig(model, post, q) / PROBES[q][0], q))
                post = update(post, model.tables[p], model.outcome(r, p))
                left.remove(p)
                spent += PROBES[p][0]
            r["s"][f"hesp@{b}"] = post["TruePositive"]
    names = list(cold[0]["s"])
    point = {n: auroc([(r["s"][n], r["grade"] == "TruePositive") for r in cold]) for n in names}
    by_org = collections.defaultdict(list)
    for r in cold:
        by_org[r["org"]].append(r)
    orgs, rng, draws = sorted(by_org), random.Random(2026), collections.defaultdict(list)
    for _ in range(300):
        smp = [r for o in rng.choices(orgs, k=len(orgs)) for r in by_org[o]]
        if not any(r["grade"] == "TruePositive" for r in smp):
            continue
        a = {n: auroc([(r["s"][n], r["grade"] == "TruePositive") for r in smp]) for n in names}
        for n in names:
            draws[n].append(a[n])
            draws[n + " - history"].append(a[n] - a["history"])
    print(f"cold incidents {len(cold):,}; TP share {sum(r['grade'] == 'TruePositive' for r in cold) / len(cold):.3f}")
    for n in names:
        print(f"AUROC {n:10s} {point[n]:.3f}")
    for n in names:
        if n == "history":
            continue
        v = sorted(draws[n + ' - history'])
        print(f"  {n} - history: {point[n] - point['history']:+.3f}  org-cluster 95% "
              f"[{v[int(0.025 * (len(v) - 1))]:+.3f}, {v[int(0.975 * (len(v) - 1))]:+.3f}]  ({len(v)} resamples)")


if __name__ == "__main__":
    main()
