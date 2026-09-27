"""Feasibility check 2: is the answer entity reachable through a FIXED, typed probe
catalog, or does it need arbitrary multi-hop SQL?

If the answers only ever appear in columns a small typed catalog can name, HESP's
discrete probe formulation can cover this data.  If they are scattered across
arbitrary columns of arbitrary tables, a fixed catalog cannot, and the route is dead.
"""
import csv
import json
from collections import Counter
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

NS = {"g": "http://graphml.graphdrawing.org/xmlns"}
DELIM = "❖"
csv.field_size_limit(10 ** 8)


def norm(s):
    return re.sub(r"[\s`'\"]+", "", (s or "").lower())


def load_graph(inc):
    g = ET.parse(Path("graphs") / f"{inc}.graphml").getroot().find("g:graph", NS)
    out = {}
    for n in g.findall("g:node", NS):
        d = {dd.get("key"): dd.text for dd in n.findall("g:data", NS)}
        out[n.get("id")] = {"kind": d.get("d1"), "type": d.get("d5"),
                            "field": d.get("d6"), "value": d.get("d7")}
    return out


def scan(table_dir, wanted):
    """Which (table, column) pairs contain each wanted value?"""
    found = {w: set() for w in wanted}
    for path in sorted(table_dir.glob("*.csv")):
        try:
            with path.open(encoding="utf-8", errors="replace", newline="") as f:
                reader = csv.reader(f, delimiter=DELIM)
                header = next(reader, None)
                if not header:
                    continue
                for row in reader:
                    for i, cell in enumerate(row):
                        if not cell or len(cell) > 4000:
                            continue
                        c = norm(cell)
                        for w in wanted:
                            if w and w in c:
                                found[w].add((path.stem, header[i].lstrip("﻿")))
        except Exception as exc:                     # noqa: BLE001 - report, keep going
            print(f"  ! {path.name}: {type(exc).__name__}", file=sys.stderr)
    return found


def main():
    inc = sys.argv[1] if len(sys.argv) > 1 else "incident_38"
    tdir = Path("data_anonymized/incidents") / inc
    ents = {k: v for k, v in load_graph(inc).items() if v["kind"] == "entity"}
    buckets = {}
    for k, v in ents.items():
        buckets.setdefault((v["type"], v["field"]), []).append(k)

    questions = []
    for split in ("test", "train"):
        p = Path("questions") / f"{inc}_{split}.json"
        if p.exists():
            questions += [(split, q) for q in json.loads(p.read_text(encoding="utf-8"))]

    # Every atomic entity value in this incident, so one pass over the CSVs serves all questions.
    atoms = {}
    for k, v in ents.items():
        for part in (v["value"] or "").split("__"):
            if part.strip():
                atoms.setdefault(norm(part), set()).add(k)
    print(f"{inc}: {len(questions)} questions, {len(ents)} entities, {len(atoms)} atomic values")
    print(f"scanning {len(list(tdir.glob('*.csv')))} CSV tables ...")
    found = scan(tdir, set(atoms))

    cols = Counter()
    unreachable = 0
    for value, hits in found.items():
        if not hits:
            unreachable += 1
        for t, c in hits:
            cols[(t, c)] += 1
    print(f"\natomic entity values never found in any table: {unreachable}/{len(atoms)}")
    print(f"distinct (table, column) pairs that ever hold an entity value: {len(cols)}")
    print("\ntop 25 columns by how many distinct entity values they hold:")
    for (t, c), n in cols.most_common(25):
        print(f"  {n:4d}  {t}.{c}")
    covered = sum(1 for v, h in found.items() if h)
    print(f"\ncoverage: {covered}/{len(atoms)} = {covered/len(atoms):.1%} of entity values "
          f"appear in at least one column")
    top = [tc for tc, _ in cols.most_common(30)]
    hit_by_top = sum(1 for v, h in found.items() if h & set(top))
    print(f"a 30-probe catalog built from the top columns would reach "
          f"{hit_by_top}/{len(atoms)} = {hit_by_top/len(atoms):.1%}")
    # candidate-set sizes for the record
    sizes = [len(buckets[(ents[str(e)]["type"], ents[str(e)]["field"])])
             for _, q in questions for e in q["end_entities"] if str(e) in ents]
    if sizes:
        sizes.sort()
        print(f"candidate sets: median {sizes[len(sizes)//2]}, max {sizes[-1]}, "
              f"singletons {sum(s==1 for s in sizes)/len(sizes):.1%}")


if __name__ == "__main__":
    main()
