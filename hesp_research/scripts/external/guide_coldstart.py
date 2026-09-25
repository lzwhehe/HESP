"""Is there a GUIDE subset where investigation (not history lookup) decides the grade?

Training split only; time split inside every org (earliest 80 % = history, rest = new incidents).
"Cold" = new incidents whose (org, detector) pair has no history, or a mixed one (majority
grade < 80 % of at least 5 past incidents). For these, measure:
  * how well history-style shortcuts still do (org majority, cross-org detector majority)
  * how much each facet says about the grade within the cold subset, and given the detector

    python scripts/external/guide_coldstart.py --incidents ../external/guide_incidents_train.jsonl
"""
import argparse
import collections
import json
import math
import sys

GRADES = ("TruePositive", "BenignPositive", "FalsePositive")
FACETS = ("category", "technique", "entity_types", "geography", "scale", "roles", "auto_verdict",
          "evidence_roles", "threat_family", "detector")


def mi(pairs):
    joint = collections.Counter(pairs)
    n = sum(joint.values())
    if n == 0:
        return 0.0
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
    d = collections.defaultdict(collections.Counter)
    o = collections.defaultdict(collections.Counter)
    for r in fit:
        od[(r["org"], r["o"]["detector"])][r["grade"]] += 1
        d[r["o"]["detector"]][r["grade"]] += 1
        o[r["org"]][r["grade"]] += 1

    def cold(r):
        c = od.get((r["org"], r["o"]["detector"]))
        if not c:
            return "unseen"
        n = sum(c.values())
        return "mixed" if n >= 5 and c.most_common(1)[0][1] / n < 0.8 else None

    kinds = collections.Counter(cold(r) for r in dev)
    sub = [r for r in dev if cold(r)]
    print(f"new incidents {len(dev):,}: unseen (org,detector) {kinds['unseen']:,}, mixed history {kinds['mixed']:,}, "
          f"cold total {len(sub):,} = {len(sub) / len(dev):.1%}")
    mix = collections.Counter(r["grade"] for r in sub)
    print("cold grade mix:", {g: round(mix[g] / len(sub), 3) for g in GRADES},
          f"| orgs involved: {len({r['org'] for r in sub}):,}")
    maj = mix.most_common(1)[0][0]

    def acc(pred):
        return sum(pred(r) == r["grade"] for r in sub) / len(sub)
    print(f"  majority class            {acc(lambda r: maj):.3f}")
    print(f"  org majority              {acc(lambda r: o[r['org']].most_common(1)[0][0] if o[r['org']] else maj):.3f}")
    print(f"  (org,detector) majority   "
          f"{acc(lambda r: od[(r['org'], r['o']['detector'])].most_common(1)[0][0] if od.get((r['org'], r['o']['detector'])) else maj):.3f}")
    print(f"  cross-org detector maj.   {acc(lambda r: d[r['o']['detector']].most_common(1)[0][0] if d.get(r['o']['detector']) else maj):.3f}")
    h = -sum(p * math.log2(p) for p in (v / len(sub) for v in mix.values()) if p)
    print(f"\nwithin the cold subset: H(grade) = {h:.3f} bits; I(grade; x) and I(grade; x | org):")
    by_org = collections.defaultdict(list)
    for r in sub:
        by_org[r["org"]].append(r)
    print(f"  {'org':15s} {mi((r['org'], r['grade']) for r in sub):.3f}")
    for fct in FACETS:
        plain = mi((r["o"][fct], r["grade"]) for r in sub)
        cond = sum(len(v) / len(sub) * mi((r["o"][fct], r["grade"]) for r in v) for v in by_org.values())
        print(f"  {fct:15s} {plain:.3f} -> {cond:.3f}")
    pure_orgs = sum(len(v) for v in by_org.values() if len({r['grade'] for r in v}) == 1)
    print(f"\ncold incidents in orgs whose cold incidents all share one grade: {pure_orgs / len(sub):.1%}")


if __name__ == "__main__":
    main()
