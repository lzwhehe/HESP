"""Aggregate GUIDE evidence rows into one record per incident, with discrete probe outcomes.

Each probe is one facet an L1 analyst can look up for an incident. Outcomes are discretised
here once, so every later study reads the same definitions. Columns that are produced by
triage or remediation (ActionGrouped, ActionGranular) are never read; the grade is kept only
as the label.

    python scripts/external/guide_build_incidents.py --csv ../external/GUIDE_Train.csv \
        --out ../external/guide_incidents_train.jsonl
"""
import argparse
import collections
import csv
import json
from pathlib import Path
import sys
import time

# Probe definitions: id -> (cost, description). Outcomes are computed in `outcomes()` below.
PROBES = {
    "category":       (1, "MITRE tactic category of the incident's alerts (majority)"),
    "technique":      (1, "whether the alerts carry a MITRE technique, and the most common one"),
    "entity_types":   (1, "the two most frequent evidence entity types"),
    "evidence_roles": (1, "share of evidence marked Impacted vs Related"),
    "scale":          (1, "number of alerts and of evidence rows"),
    "detector":       (2, "the alert detector (history of its grades is learned from training data)"),
    "auto_verdict":   (2, "automated-investigation verdict / suspicion level, if any"),
    "roles":          (1, "strongest entity role annotation (Compromised, Attacker, ...)"),
    "threat_family":  (1, "whether a malware / threat family is named"),
    "geography":      (1, "number of distinct countries among the evidence"),
}
LEAKY = ("ActionGrouped", "ActionGranular")           # remediation after triage: never read
TOP_TECH = 40                                         # techniques kept by name; the rest -> "other"


def bucket(n, edges):
    for e in edges:
        if n <= e:
            return f"<={e}"
    return f">{edges[-1]}"


def outcomes(s):
    cats = s["cats"].most_common()
    ents = [e for e, _ in s["ents"].most_common(2)]
    tech = s["tech"].most_common(1)
    imp = s["impacted"] / max(s["evidence"], 1)
    verdict = ("Malicious" if s["verdict"]["Malicious"] else "Suspicious" if s["verdict"]["Suspicious"]
               else "NoThreatsFound" if s["verdict"]["NoThreatsFound"] else "none")
    role_rank = ("Compromised", "Attacker", "Suspicious", "PolicyViolator", "Destination", "Source", "Contextual")
    role = next((r for r in role_rank if s["roles"][r]), "none")
    return {
        "category": cats[0][0],
        "technique": tech[0][0] if tech else "none",
        "entity_types": "+".join(sorted(ents)),
        "evidence_roles": "all_related" if imp == 0 else "all_impacted" if imp == 1 else
                          ("mostly_impacted" if imp >= 0.5 else "mostly_related"),
        "scale": f"alerts{bucket(s['alerts_n'], (1, 3, 10))}_ev{bucket(s['evidence'], (2, 5, 15, 50))}",
        "detector": s["detector"].most_common(1)[0][0],
        "auto_verdict": verdict,
        "roles": role,
        "threat_family": "named" if s["families"] else "none",
        "geography": bucket(len(s["countries"]), (1, 2, 4)),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--csv", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    t0 = time.time()
    inc = {}
    tech_count = collections.Counter()
    with open(args.csv, encoding="utf-8", newline="") as f:
        for i, r in enumerate(csv.DictReader(f), 1):
            key = (r["OrgId"], r["IncidentId"])
            s = inc.get(key)
            if s is None:
                s = inc[key] = {"grade": r["IncidentGrade"], "alerts": set(), "evidence": 0, "impacted": 0,
                                "cats": collections.Counter(), "ents": collections.Counter(),
                                "tech": collections.Counter(), "detector": collections.Counter(),
                                "verdict": collections.Counter(), "roles": collections.Counter(),
                                "families": 0, "countries": set(), "first_ts": r["Timestamp"]}
            s["alerts"].add(r["AlertId"])
            s["evidence"] += 1
            s["impacted"] += r["EvidenceRole"] == "Impacted"
            s["cats"][r["Category"]] += 1
            s["ents"][r["EntityType"]] += 1
            for t in filter(None, r["MitreTechniques"].split(";")):
                s["tech"][t] += 1
                tech_count[t] += 1
            s["detector"][r["DetectorId"]] += 1
            s["verdict"][r["LastVerdict"] or r["SuspicionLevel"]] += 1
            if r["Roles"]:
                s["roles"][r["Roles"]] += 1
            s["families"] += bool(r["ThreatFamily"])
            s["countries"].add(r["CountryCode"])
            s["first_ts"] = min(s["first_ts"], r["Timestamp"])
            if i % 2_000_000 == 0:
                print(f"  {i:,} rows ({time.time() - t0:.0f}s)", flush=True)
    keep = {t for t, _ in tech_count.most_common(TOP_TECH)}
    n = 0
    with open(args.out, "w", encoding="utf-8", newline="\n") as out:
        for (org, iid), s in inc.items():
            if s["grade"] not in ("TruePositive", "BenignPositive", "FalsePositive"):
                continue
            s["alerts_n"] = len(s["alerts"])
            s["tech"] = collections.Counter({(t if t in keep else "other"): c for t, c in s["tech"].items()})
            out.write(json.dumps({"org": org, "incident": iid, "grade": s["grade"], "first_ts": s["first_ts"],
                                  "o": outcomes(s)}) + "\n")
            n += 1
    print(f"{n:,} graded incidents written to {args.out} ({time.time() - t0:.0f}s)")
    print("probes:", json.dumps(PROBES))


if __name__ == "__main__":
    main()
