"""Diagnose the GUIDE pilot's failure: organisation label policy vs. correlated facets.

Training split only.
  1. How concentrated are incidents in a few organisations, and how different are their grade mixes?
  2. How predictable is the grade from (org, detector) history alone, learned on each org's own
     earlier incidents (time split inside every org)?
  3. How redundant are the facets: I(grade; facet | detector) vs I(grade; facet).

    python scripts/external/guide_diagnose.py --incidents ../external/guide_incidents_train.jsonl
"""
import argparse
import collections
import json
import math
import sys

GRADES = ("TruePositive", "BenignPositive", "FalsePositive")


def mi(pairs):
    """I(grade; x) in bits from an iterable of (x, grade)."""
    joint = collections.Counter(pairs)
    n = sum(joint.values())
    px, pg = collections.Counter(), collections.Counter()
    for (x, g), k in joint.items():
        px[x] += k
        pg[g] += k
    return sum(k / n * math.log2(k * n / (px[x] * pg[g])) for (x, g), k in joint.items())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--incidents", required=True)
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    with open(args.incidents, encoding="utf-8") as f:
        rows = [json.loads(line) for line in f]

    # 1. organisation concentration and label-policy spread
    by_org = collections.defaultdict(collections.Counter)
    for r in rows:
        by_org[r["org"]][r["grade"]] += 1
    sizes = sorted(((sum(c.values()), o) for o, c in by_org.items()), reverse=True)
    n = len(rows)
    print(f"{n:,} incidents in {len(by_org):,} orgs; top-1 org {sizes[0][0] / n:.1%}, top-10 "
          f"{sum(s for s, _ in sizes[:10]) / n:.1%}, top-100 {sum(s for s, _ in sizes[:100]) / n:.1%}")
    print("largest orgs and their grade mix:")
    for s, o in sizes[:8]:
        c = by_org[o]
        print(f"  org {o:>6s} {s:>7,}  " + "  ".join(f"{g[:2]} {c[g] / s:.2f}" for g in GRADES))
    big = [o for s, o in sizes if s >= 200]
    bp = sorted(by_org[o]["BenignPositive"] / sum(by_org[o].values()) for o in big)
    print(f"orgs with >=200 incidents: {len(big)}; their BP share p10/p50/p90 = "
          f"{bp[len(bp) // 10]:.2f}/{bp[len(bp) // 2]:.2f}/{bp[9 * len(bp) // 10]:.2f}")
    print(f"I(grade; org) = {mi((r['org'], r['grade']) for r in rows):.3f} bits   "
          f"H(grade) = {-sum(p * math.log2(p) for p in (v / n for v in collections.Counter(r['grade'] for r in rows).values())):.3f}")

    # 2. history within each org: earliest 80 % of each org's incidents -> later 20 %
    per_org = collections.defaultdict(list)
    for r in rows:
        per_org[r["org"]].append(r)
    fit, dev = [], []
    for lst in per_org.values():
        lst.sort(key=lambda r: r["first_ts"])
        cut = int(len(lst) * 0.8)
        fit += lst[:cut]
        dev += lst[cut:]
    hist_od = collections.defaultdict(collections.Counter)
    hist_d = collections.defaultdict(collections.Counter)
    hist_o = collections.defaultdict(collections.Counter)
    for r in fit:
        hist_od[(r["org"], r["o"]["detector"])][r["grade"]] += 1
        hist_d[r["o"]["detector"]][r["grade"]] += 1
        hist_o[r["org"]][r["grade"]] += 1
    glob = collections.Counter(r["grade"] for r in fit).most_common(1)[0][0]

    def predict(r, level):
        for key, table in (((r["org"], r["o"]["detector"]), hist_od), (r["o"]["detector"], hist_d),
                           (r["org"], hist_o))[:level]:
            if table.get(key):
                return table[key].most_common(1)[0][0]
        return glob
    print(f"\ntime split inside each org: fit {len(fit):,}, dev {len(dev):,}")
    for name, lvl in (("global majority", 0), ("org+detector history", 1), ("+ detector history", 2),
                      ("+ org history", 3)):
        acc = sum(predict(r, lvl) == r["grade"] for r in dev) / len(dev)
        tp = [r for r in dev if r["grade"] == "TruePositive"]
        rec = sum(predict(r, lvl) == "TruePositive" for r in tp) / len(tp)
        print(f"  {name:22s} accuracy {acc:.3f}   TP recall {rec:.3f}")
    cov = sum(bool(hist_od.get((r["org"], r["o"]["detector"]))) for r in dev) / len(dev)
    print(f"  dev incidents whose (org, detector) was seen in the org's past: {cov:.1%}")

    # 3. facet redundancy given the detector
    print("\nI(grade; facet) vs I(grade; facet | detector), bits (fit part):")
    by_det = collections.defaultdict(list)
    for r in fit:
        by_det[r["o"]["detector"]].append(r)
    for facet in ("category", "technique", "entity_types", "geography", "scale", "roles", "auto_verdict",
                  "evidence_roles"):
        plain = mi((r["o"][facet], r["grade"]) for r in fit)
        cond = sum(len(v) / len(fit) * mi((r["o"][facet], r["grade"]) for r in v) for v in by_det.values())
        print(f"  {facet:15s} {plain:.3f} -> {cond:.3f}")
    print(f"  detector        {mi((r['o']['detector'], r['grade']) for r in fit):.3f}")


if __name__ == "__main__":
    main()
