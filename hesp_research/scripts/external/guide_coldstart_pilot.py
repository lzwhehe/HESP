"""LLM-free predictive test of HESP on GUIDE's cold-start incidents (training split only).

Time split inside every organisation: earliest 80 % = history, latest 20 % = new incidents.
Cold = new incidents whose (org, detector) pair has no history, or a mixed one (majority
< 80 % of >= 5 past incidents) -- the alerts where "what did we decide last time" does not help.

HESP mapping:
  prior   p0(h)       = the organisation's own historical grade mix (its labelling policy),
                        smoothed toward the global mix
  P(o | h, probe)     = counted on all organisations' history-period incidents
  detector outcome    = cross-organisation history of that detector (majority grade / mixed /
                        little history / unseen)
Policies: EIG/cost, fixed playbook order, random; plus prior-only and history baselines.

    python scripts/external/guide_coldstart_pilot.py --incidents ../external/guide_incidents_train.jsonl
"""
import argparse
import collections
import json
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from guide_pilot import COST, GRADES, Model, posterior, run_policy   # noqa: E402

ALPHA = 20          # pseudo-counts pulling an org's prior toward the global mix


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--incidents", required=True)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--json")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    with open(args.incidents, encoding="utf-8") as f:
        rows = [json.loads(line) for line in f]
    per_org = collections.defaultdict(list)
    for r in rows:
        per_org[r["org"]].append(r)
    fit, dev = [], []
    for lst in per_org.values():
        lst.sort(key=lambda r: r["first_ts"])
        cut = int(len(lst) * 0.8)
        fit += lst[:cut]
        dev += lst[cut:]

    od = collections.defaultdict(collections.Counter)
    org_hist = collections.defaultdict(collections.Counter)
    det = collections.defaultdict(collections.Counter)
    for r in fit:
        od[(r["org"], r["o"]["detector"])][r["grade"]] += 1
        org_hist[r["org"]][r["grade"]] += 1
        det[r["o"]["detector"]][r["grade"]] += 1

    def is_cold(r):
        c = od.get((r["org"], r["o"]["detector"]))
        if not c:
            return True
        n = sum(c.values())
        return n >= 5 and c.most_common(1)[0][1] / n < 0.8
    cold = [r for r in dev if is_cold(r)]
    raw_det = {id(r): r["o"]["detector"] for r in cold}

    def det_hist(d):
        c = det.get(d)
        if not c:
            return "unseen_detector"
        n = sum(c.values())
        g, k = c.most_common(1)[0]
        return "little_history" if n < 20 else (f"mostly_{g}" if k / n >= 0.6 else "mixed")
    for r in fit + cold:
        r["o"]["detector"] = det_hist(r["o"]["detector"])
    model = Model(fit)
    glob = dict(model.prior)

    def org_prior(org):
        c = org_hist.get(org, collections.Counter())
        n = sum(c.values())
        return {h: (c[h] + ALPHA * glob[h]) / (n + ALPHA) for h in GRADES}

    def score(preds):
        acc = sum(p == r["grade"] for p, r in zip(preds, cold)) / len(cold)
        tps = [(p, r) for p, r in zip(preds, cold) if r["grade"] == "TruePositive"]
        rec = sum(p == "TruePositive" for p, _ in tps) / len(tps)
        f1 = []
        for h in GRADES:
            tp = sum(p == h and r["grade"] == h for p, r in zip(preds, cold))
            pp = sum(p == h for p in preds)
            ap_ = sum(r["grade"] == h for r in cold)
            f1.append(0 if tp == 0 else 2 * tp / (pp + ap_))
        return acc, sum(f1) / 3, rec

    print(f"cold new incidents: {len(cold):,} (of {len(dev):,}) in {len({r['org'] for r in cold}):,} orgs")
    res = {}
    base = {
        "global majority": [max(glob, key=glob.get)] * len(cold),
        "(org,detector) history": [od[(r['org'], raw_det[id(r)])].most_common(1)[0][0]
                                   if od.get((r['org'], raw_det[id(r)])) else max(org_prior(r['org']).items(),
                                                                                    key=lambda kv: kv[1])[0]
                                   for r in cold],
        "org prior only": [max(org_prior(r['org']).items(), key=lambda kv: kv[1])[0] for r in cold],
    }
    print(f"\n{'policy':30s} {'budget':>6s} {'acc':>6s} {'macroF1':>8s} {'TP recall':>9s}")
    for name, preds in base.items():
        a, f, t = score(preds)
        res[name] = {"accuracy": a, "macro_f1": f, "tp_recall": t}
        print(f"{name:30s} {'-':>6s} {a:6.3f} {f:8.3f} {t:9.3f}")
    rng = random.Random(args.seed)
    for b in (2, 4, 6, sum(COST.values())):
        for policy in ("eig_cost", "fixed", "random"):
            preds = []
            for r in cold:
                model.prior = org_prior(r["org"])
                post, _, _ = run_policy(model, r, policy, b, rng)
                preds.append(max(post, key=post.get))
            a, f, t = score(preds)
            res[f"{policy}@{b}"] = {"accuracy": a, "macro_f1": f, "tp_recall": t}
            print(f"{'org prior + ' + policy:30s} {b:6d} {a:6.3f} {f:8.3f} {t:9.3f}")
    for b in (2, 4, 6):
        for policy in ("eig_cost", "random"):
            preds = []
            for r in cold:
                model.prior = dict(glob)
                post, _, _ = run_policy(model, r, policy, b, rng)
                preds.append(max(post, key=post.get))
            a, f, t = score(preds)
            res[f"globalprior_{policy}@{b}"] = {"accuracy": a, "macro_f1": f, "tp_recall": t}
            print(f"{'global prior + ' + policy:30s} {b:6d} {a:6.3f} {f:8.3f} {t:9.3f}")
    if args.json:
        Path(args.json).write_text(json.dumps(res, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
