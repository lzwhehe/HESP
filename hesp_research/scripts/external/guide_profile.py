"""Profile the GUIDE training split to decide whether and how it can host a HESP environment.

Reads only GUIDE_Train.csv (design data). The test split is never read here.

Answers, per incident (OrgId, IncidentId) -- the unit HESP would triage:
  * how grades are distributed, and whether a grade is constant within an incident
  * how many alerts / evidence rows / distinct categories an incident carries
  * which columns are post-triage artefacts that would leak the label
    (their association with the grade is measured, not assumed)

    python scripts/external/guide_profile.py --csv ../external/GUIDE_Train.csv --json ../external/guide_profile.json
"""
import argparse
import collections
import csv
import json
import math
from pathlib import Path
import sys
import time

GRADES = ("TruePositive", "BenignPositive", "FalsePositive")
# categorical columns worth profiling as potential probe facets or leak sources
FACETS = ("Category", "EntityType", "EvidenceRole", "SuspicionLevel", "LastVerdict", "ActionGrouped",
          "ActionGranular", "ThreatFamily", "AntispamDirection", "OSFamily", "ResourceType", "Roles")


def mutual_information(table):
    """I(grade; value) in bits from a {value: Counter(grade)} contingency table."""
    n = sum(sum(c.values()) for c in table.values())
    if n == 0:
        return 0.0
    pg = collections.Counter()
    for c in table.values():
        pg.update(c)
    mi = 0.0
    for c in table.values():
        nv = sum(c.values())
        for g, k in c.items():
            if k:
                mi += k / n * math.log2(k * n / (nv * pg[g]))
    return mi


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--csv", required=True)
    parser.add_argument("--json")
    parser.add_argument("--limit", type=int, default=0, help="rows to read (0 = all)")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    t0 = time.time()

    rows = 0
    empty = collections.Counter()
    header = None
    inc = {}                                    # (org, incident) -> summary
    facet_by_grade = {f: collections.defaultdict(collections.Counter) for f in FACETS}
    detectors, titles, orgs = set(), set(), set()
    with open(args.csv, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames
        for r in reader:
            rows += 1
            for k, v in r.items():
                if v == "":
                    empty[k] += 1
            key = (r["OrgId"], r["IncidentId"])
            s = inc.get(key)
            if s is None:
                s = inc[key] = {"grades": set(), "alerts": set(), "evidence": 0, "cats": set(), "ents": set()}
            g = r["IncidentGrade"]
            s["grades"].add(g)
            s["alerts"].add(r["AlertId"])
            s["evidence"] += 1
            s["cats"].add(r["Category"])
            s["ents"].add(r["EntityType"])
            detectors.add(r["DetectorId"])
            titles.add(r["AlertTitle"])
            orgs.add(r["OrgId"])
            for fcol in FACETS:
                facet_by_grade[fcol][r[fcol] or "<empty>"][g or "<none>"] += 1
            if args.limit and rows >= args.limit:
                break
            if rows % 2_000_000 == 0:
                print(f"  {rows:,} rows, {len(inc):,} incidents ({time.time() - t0:.0f}s)", flush=True)

    grade_mixed = sum(1 for s in inc.values() if len(s["grades"]) > 1)
    grade_missing = sum(1 for s in inc.values() if s["grades"] <= {""})
    inc_grade = collections.Counter(next(iter(s["grades"])) for s in inc.values() if len(s["grades"]) == 1)

    def dist(values):
        v = sorted(values)
        q = lambda p: v[min(len(v) - 1, int(p * len(v)))]
        return {"median": q(0.5), "p75": q(0.75), "p90": q(0.9), "p99": q(0.99), "max": v[-1],
                "share_eq_1": sum(x == 1 for x in v) / len(v)}

    out = {
        "rows": rows, "columns": header, "incidents": len(inc), "orgs": len(orgs),
        "detectors": len(detectors), "alert_titles": len(titles),
        "empty_share": {k: empty[k] / rows for k in header},
        "incidents_with_mixed_grade": grade_mixed, "incidents_without_grade": grade_missing,
        "incident_grade": dict(inc_grade),
        "alerts_per_incident": dist([len(s["alerts"]) for s in inc.values()]),
        "evidence_per_incident": dist([s["evidence"] for s in inc.values()]),
        "categories_per_incident": dist([len(s["cats"]) for s in inc.values()]),
        "entity_types_per_incident": dist([len(s["ents"]) for s in inc.values()]),
        "facets": {},
    }
    for fcol, table in facet_by_grade.items():
        top = sorted(table.items(), key=lambda kv: -sum(kv[1].values()))[:8]
        out["facets"][fcol] = {
            "values": len(table),
            "mi_bits_row_level": mutual_information(table),
            "top": [{"value": v, "n": sum(c.values()),
                     **{g: round(c[g] / max(sum(c.values()), 1), 3) for g in GRADES}} for v, c in top],
        }

    print(f"\nrows {rows:,} | incidents {len(inc):,} | orgs {len(orgs):,} | detectors {len(detectors):,} "
          f"| alert titles {len(titles):,}   ({time.time() - t0:.0f}s)")
    print(f"incident grade: {dict(inc_grade)} | mixed-grade incidents {grade_mixed:,} | no grade {grade_missing:,}")
    for k in ("alerts_per_incident", "evidence_per_incident", "categories_per_incident", "entity_types_per_incident"):
        print(f"{k:28s} {out[k]}")
    print("\ncolumn empty share:")
    for k in header:
        print(f"  {k:20s} {out['empty_share'][k]:.3f}")
    print("\nfacet -> grade (row level; MI in bits; row-level grade shares for the most common values):")
    for fcol, d in sorted(out["facets"].items(), key=lambda kv: -kv[1]["mi_bits_row_level"]):
        print(f"\n  {fcol}: {d['values']} values, I(grade; {fcol}) = {d['mi_bits_row_level']:.3f} bits")
        for t in d["top"]:
            print(f"    {str(t['value'])[:28]:28s} n={t['n']:>9,}  TP {t['TruePositive']:.2f}  "
                  f"BP {t['BenignPositive']:.2f}  FP {t['FalsePositive']:.2f}")
    if args.json:
        Path(args.json).write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
