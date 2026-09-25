"""LLM-free feasibility pilot for HESP on GUIDE (real analyst-graded incidents).

Question: on real, noisy incidents, does choosing the next facet by expected information gain
per unit cost reach a correct triage verdict faster than random or fixed-order lookup?

Uses the TRAINING split only, re-split by organisation (80 % fit / 20 % dev, disjoint orgs).
P(o | grade, probe) is counted on the fit orgs; policies are scored on a random sample of dev
incidents. The GUIDE test split is not read.

Detector outcome = how that detector's fit-org incidents were graded (majority grade when it
covers >= 60 % of at least 20 incidents, "mixed", or "little_history") -- the analyst's
"what did we decide last time this fired" lookup.

    python scripts/external/guide_pilot.py --incidents ../external/guide_incidents_train.jsonl
"""
import argparse
import collections
import hashlib
import json
import math
from pathlib import Path
import random
import sys
import time

GRADES = ("TruePositive", "BenignPositive", "FalsePositive")
COST = {"category": 1, "technique": 1, "entity_types": 1, "evidence_roles": 1, "scale": 1, "detector": 2,
        "auto_verdict": 2, "roles": 1, "threat_family": 1, "geography": 1}
FIXED_ORDER = ["category", "entity_types", "technique", "evidence_roles", "scale", "roles", "threat_family",
               "geography", "detector", "auto_verdict"]          # a plausible playbook: cheap facets first
TOP_OUTCOMES = 60


def org_split(org, dev_share=0.2):
    return "dev" if int(hashlib.sha256(f"guide|{org}".encode()).hexdigest(), 16) % 1000 < dev_share * 1000 \
        else "fit"


def entropy(p):
    return -sum(v * math.log2(v) for v in p.values() if v > 0)


def posterior(prior, likes):
    z = sum(prior[h] * likes[h] for h in GRADES)
    return {h: prior[h] * likes[h] / z for h in GRADES}


class Model:
    """P(o | h, probe) counted on fit incidents with add-one smoothing; unseen outcomes share mass."""

    def __init__(self, fit):
        self.prior = {h: 0.0 for h in GRADES}
        counts = {p: collections.defaultdict(collections.Counter) for p in COST}
        for r in fit:
            self.prior[r["grade"]] += 1
            for p in COST:
                counts[p][r["o"][p]][r["grade"]] += 1
        n = sum(self.prior.values())
        self.prior = {h: v / n for h, v in self.prior.items()}
        self.table = {}
        for p, by_o in counts.items():
            outs = sorted(by_o, key=lambda o: -sum(by_o[o].values()))[:TOP_OUTCOMES]
            tot = {h: sum(by_o[o][h] for o in by_o) for h in GRADES}
            k = len(outs) + 1                                   # + "other"
            rows = {}
            for h in GRADES:
                row = {o: (by_o[o][h] + 1) / (tot[h] + k) for o in outs}
                row["other"] = 1 - sum(row.values())
                rows[h] = row
            self.table[p] = rows

    def outcome(self, probe, value):
        return value if value in self.table[probe][GRADES[0]] else "other"

    def eig(self, post, probe):
        rows = self.table[probe]
        h0 = entropy(post)
        exp = 0.0
        for o in rows[GRADES[0]]:
            po = sum(post[h] * rows[h][o] for h in GRADES)
            if po > 0:
                exp += po * entropy({h: post[h] * rows[h][o] / po for h in GRADES})
        return h0 - exp


def detector_history(fit):
    by = collections.defaultdict(collections.Counter)
    for r in fit:
        by[r["o"]["detector"]][r["grade"]] += 1
    hist = {}
    for d, c in by.items():
        n = sum(c.values())
        g, k = c.most_common(1)[0]
        hist[d] = "little_history" if n < 20 else (f"mostly_{g}" if k / n >= 0.6 else "mixed")
    return hist


def run_policy(model, r, policy, budget, rng, stop_at=None):
    post, left, spent, used = dict(model.prior), [p for p in COST], 0, []
    while True:
        if stop_at is not None and max(post.values()) >= stop_at:
            break
        legal = [p for p in left if spent + COST[p] <= budget]
        if not legal:
            break
        if policy == "eig_cost":
            p = max(legal, key=lambda q: (model.eig(post, q) / COST[q], q))
        elif policy == "random":
            p = rng.choice(legal)
        else:
            p = next(q for q in FIXED_ORDER if q in legal)
        o = model.outcome(p, r["o"][p])
        post = posterior(post, {h: model.table[p][h][o] for h in GRADES})
        left.remove(p)
        spent += COST[p]
        used.append(p)
    return post, spent, used


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--incidents", required=True)
    parser.add_argument("--dev-sample", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--json")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    t0 = time.time()
    with open(args.incidents, encoding="utf-8") as f:
        rows = [json.loads(line) for line in f]
    fit = [r for r in rows if org_split(r["org"]) == "fit"]
    dev = [r for r in rows if org_split(r["org"]) == "dev"]
    hist = detector_history(fit)
    for r in rows:
        r["o"]["detector"] = hist.get(r["o"]["detector"], "unseen_detector")
    model = Model(fit)
    rng = random.Random(args.seed)
    sample = rng.sample(dev, min(args.dev_sample, len(dev)))
    fit_orgs, dev_orgs = {r["org"] for r in fit}, {r["org"] for r in dev}
    print(f"fit: {len(fit):,} incidents / {len(fit_orgs):,} orgs | dev: {len(dev):,} / {len(dev_orgs):,} orgs "
          f"| org overlap {len(fit_orgs & dev_orgs)} | scored sample {len(sample):,}")
    print("prior:", {h: round(v, 3) for h, v in model.prior.items()},
          "| dev grade mix:", dict(collections.Counter(r["grade"] for r in sample)))
    base = collections.Counter(r["grade"] for r in fit).most_common(1)[0][0]
    print(f"majority-class accuracy on dev sample: "
          f"{sum(r['grade'] == base for r in sample) / len(sample):.3f}")
    print("\nsingle-probe EIG at the prior (bits) / cost:")
    for p in sorted(COST, key=lambda q: -model.eig(model.prior, q) / COST[q]):
        print(f"  {p:15s} {model.eig(model.prior, p):.3f} / {COST[p]}")

    results = {}
    budgets = (1, 2, 3, 4, 6, 8, sum(COST.values()))
    print(f"\n{'budget':>6s} {'policy':>9s} {'acc':>6s} {'macroF1':>8s} {'TP recall':>9s} {'TP->BP/FP':>9s} {'cost':>5s}")
    for b in budgets:
        for policy in ("eig_cost", "fixed", "random"):
            conf = collections.Counter()
            cost = 0
            for r in sample:
                post, spent, _ = run_policy(model, r, policy, b, rng)
                conf[(r["grade"], max(post, key=post.get))] += 1
                cost += spent
            acc = sum(v for (t, p), v in conf.items() if t == p) / len(sample)
            f1s = []
            for h in GRADES:
                tp = conf[(h, h)]
                prec = tp / max(sum(v for (t, p), v in conf.items() if p == h), 1)
                rec = tp / max(sum(v for (t, p), v in conf.items() if t == h), 1)
                f1s.append(0 if tp == 0 else 2 * prec * rec / (prec + rec))
            n_tp = sum(v for (t, p), v in conf.items() if t == "TruePositive")
            tp_rec = conf[("TruePositive", "TruePositive")] / max(n_tp, 1)
            results[f"{policy}@{b}"] = {"accuracy": acc, "macro_f1": sum(f1s) / 3, "tp_recall": tp_rec,
                                        "mean_cost": cost / len(sample)}
            print(f"{b:6d} {policy:>9s} {acc:6.3f} {sum(f1s) / 3:8.3f} {tp_rec:9.3f} {1 - tp_rec:9.3f} "
                  f"{cost / len(sample):5.2f}")
        print()

    print("guarded stop (verdict only when max posterior >= 0.8), budget = all probes:")
    for policy in ("eig_cost", "fixed", "random"):
        decided = correct = cost = 0
        for r in sample:
            post, spent, _ = run_policy(model, r, policy, sum(COST.values()), rng, stop_at=0.8)
            cost += spent
            if max(post.values()) >= 0.8:
                decided += 1
                correct += max(post, key=post.get) == r["grade"]
        results[f"{policy}@guard0.8"] = {"decided": decided / len(sample), "accuracy_decided": correct / max(decided, 1),
                                         "mean_cost": cost / len(sample)}
        print(f"  {policy:9s} decided {decided / len(sample):.3f}  accuracy on decided {correct / max(decided, 1):.3f}"
              f"  mean cost {cost / len(sample):.2f}")
    print(f"\n({time.time() - t0:.0f}s)")
    if args.json:
        Path(args.json).write_text(json.dumps(results, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
