"""RQ4 feasibility pilot: can IoC-pivot probes tell the answer entity from its distractors?

Design under test (not yet pre-registered; development data only):
  * hypotheses H   = graph entities of the answer's (node_type, identifier_field) in the incident
  * probe a = T    = "rows of log table T that mention any context entity" (a SOC pivot)
  * outcome o      = which candidates co-occur in those rows: exactly one / several / none

The probe family is usable only if the true answer co-occurs far more often than a distractor
(q_T >> f_T) for some tables. This script measures q_T, f_T and the unique-identification rate
per table on the **train** questions only -- the 599 test questions are not read.

Data: ExCyTIn-Bench (microsoft/SecRL, MIT; logs CDLA-Permissive-2.0, synthetic demo tenant).
Expects external/excytin/{graphs,questions,data_anonymized/incidents/...} as set up by
scripts/external/README.md.

    python scripts/external/excytin_pivot_pilot.py --root ../external/excytin
"""
import argparse
import collections
import csv
import json
from pathlib import Path
import re
import sys
import time
import xml.etree.ElementTree as ET

NS = {"g": "http://graphml.graphdrawing.org/xmlns"}
DELIM = "❖"
INCIDENTS = ["incident_5", "incident_34", "incident_38", "incident_39", "incident_55",
             "incident_134", "incident_166", "incident_322"]
MIN_ATOM = 6          # shorter atoms (bare PIDs, "cmd", ...) match unrelated rows
csv.field_size_limit(10 ** 9)


def norm(s):
    return re.sub(r"[\s`'\"\\]+", "", (s or "").lower())


def atoms_of(value):
    """Matchable fragments of an entity value; composite process values are split on '__'."""
    out = []
    for part in (value or "").split("__"):
        a = norm(part)
        if len(a) >= MIN_ATOM and not (a.isdigit() and len(a) < 8):
            out.append(a)
    return out


def load_graph(root, inc):
    g = ET.parse(root / "graphs" / f"{inc}.graphml").getroot().find("g:graph", NS)
    ents = {}
    for n in g.findall("g:node", NS):
        d = {dd.get("key"): dd.text for dd in n.findall("g:data", NS)}
        if d.get("d1") == "entity":
            ents[n.get("id")] = {"type": d.get("d5"), "field": d.get("d6"), "value": d.get("d7"),
                                 "atoms": atoms_of(d.get("d7"))}
    return ents


def index_tables(root, inc, ents):
    """table -> list of frozensets of entity ids mentioned together in one row."""
    atoms = [(a, eid) for eid, e in ents.items() for a in e["atoms"]]
    out = {}
    for path in sorted((root / "data_anonymized" / "incidents" / inc).glob("*.csv")):
        rows = []
        with path.open(encoding="utf-8", errors="replace", newline="") as f:
            next(f, None)                                  # header
            for line in f:
                low = norm(line)
                hit = frozenset(eid for a, eid in atoms if a in low)
                if hit:
                    rows.append(hit)
        out[path.stem] = rows
    return out


def linked(answer, value):
    a = norm(answer)
    parts = [norm(p) for p in (value or "").split("__") if p.strip()]
    return bool(parts) and all(p in a for p in parts)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", required=True)
    parser.add_argument("--split", default="train", choices=["train"], help="design data only")
    parser.add_argument("--json")
    args = parser.parse_args()
    root = Path(args.root)
    stats = collections.defaultdict(lambda: collections.Counter())
    per_q = []
    t0 = time.time()
    for inc in INCIDENTS:
        ents = load_graph(root, inc)
        qs = json.loads((root / "questions" / f"{inc}_{args.split}.json").read_text(encoding="utf-8"))
        tables = index_tables(root, inc, ents)
        buckets = collections.defaultdict(list)
        for eid, e in ents.items():
            buckets[(e["type"], e["field"])].append(eid)
        kept = 0
        for q in qs:
            ends = [str(e) for e in q["end_entities"] if str(e) in ents]
            ans = next((e for e in ends if linked(q["answer"], ents[e]["value"])), None)
            if ans is None or not ents[ans]["atoms"]:
                stats["_"]["skip_unlinked"] += 1
                continue
            cands = set(buckets[(ents[ans]["type"], ents[ans]["field"])])
            ctx = {str(e) for e in q["start_entities"] if str(e) in ents} - cands
            if len(cands) < 2:
                stats["_"]["skip_singleton"] += 1
                continue
            if not ctx:
                stats["_"]["skip_no_context"] += 1
                continue
            kept += 1
            distractors = cands - {ans}
            row = {"incident": inc, "n_candidates": len(cands), "tables": {}}
            for table, rows in tables.items():
                seen = set()
                for r in rows:
                    if r & ctx:
                        seen |= r & cands
                s = stats[table]
                s["questions"] += 1
                s["answer_hit"] += ans in seen
                s["distractor_slots"] += len(distractors)
                s["distractor_hit"] += len(seen & distractors)
                s["unique"] += seen == {ans}
                s["none"] += not seen
                row["tables"][table] = {"answer": ans in seen, "distractors": len(seen & distractors)}
            per_q.append(row)
        print(f"{inc}: {len(qs)} train questions, {kept} usable, {len(ents)} entities, "
              f"{sum(len(v) for v in tables.values())} matching rows  ({time.time() - t0:.0f}s)", flush=True)

    usable = len(per_q)
    print(f"\nusable train questions: {usable}   skipped: {dict(stats['_'])}")
    print(f"\n{'table':38s} {'q=P(ans)':>9s} {'f=P(dist)':>10s} {'q/f':>6s} {'unique':>7s} {'none':>6s}")
    rows = []
    for table, s in stats.items():
        if table == "_" or not s["questions"]:
            continue
        q = s["answer_hit"] / s["questions"]
        f = s["distractor_hit"] / max(s["distractor_slots"], 1)
        rows.append((q - f, table, q, f, s["unique"] / s["questions"], s["none"] / s["questions"]))
    for _, table, q, f, u, n in sorted(rows, reverse=True):
        ratio = f"{q / f:.1f}" if f > 0 else "inf" if q > 0 else "-"
        print(f"{table:38s} {q:9.3f} {f:10.3f} {ratio:>6s} {u:7.3f} {n:6.3f}")
    solvable = sum(any(v["answer"] for v in r["tables"].values()) for r in per_q)
    uniq = sum(any(v["answer"] and v["distractors"] == 0 for v in r["tables"].values()) for r in per_q)
    print(f"\nanswer reachable by at least one one-hop pivot: {solvable}/{usable} = {solvable / usable:.1%}")
    print(f"answer uniquely identified by at least one table:  {uniq}/{usable} = {uniq / usable:.1%}")
    if args.json:
        Path(args.json).write_text(json.dumps({"usable": usable, "per_question": per_q}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
