"""Feasibility check 1: can the HESP hypothesis set be derived mechanically from
ExCyTIn's published investigation graph, without inventing anything?

Rule under test: for a question whose answer is entity node e, the candidate set is
every entity node in the same incident with the same (node_type, identifier_fields).
"""
import json
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET

NS = {"g": "http://graphml.graphdrawing.org/xmlns"}
INCIDENTS = ["incident_5", "incident_34", "incident_38", "incident_39", "incident_55", "incident_134", "incident_166", "incident_322"]


def load_graph(path):
    graph = ET.parse(path).getroot().find("g:graph", NS)
    nodes = {}
    for n in graph.findall("g:node", NS):
        d = {dd.get("key"): dd.text for dd in n.findall("g:data", NS)}
        nodes[n.get("id")] = {"kind": d.get("d1"), "type": d.get("d5"),
                              "field": d.get("d6"), "value": d.get("d7"), "name": d.get("d2")}
    return nodes


def main():
    stats = Counter()
    sizes = []
    for inc in INCIDENTS:
        nodes = load_graph(Path("graphs") / f"{inc}.graphml")
        entities = {k: v for k, v in nodes.items() if v["kind"] == "entity"}
        buckets = {}
        for k, v in entities.items():
            buckets.setdefault((v["type"], v["field"]), []).append(k)
        for split in ("test", "train"):
            path = Path("questions") / f"{inc}_{split}.json"
            if not path.exists():
                continue
            for q in json.loads(path.read_text(encoding="utf-8")):
                stats["questions"] += 1
                ends = [str(e) for e in q["end_entities"]]
                # 1. does the recorded answer match one of the end-entity node values?
                vals = [entities[e]["value"] for e in ends if e in entities]
                hit = any(v and v.strip().lower() == q["answer"].strip().lower() for v in vals)
                stats["answer_matches_end_entity" if hit else "answer_NOT_in_end_entities"] += 1
                # 2. how large is the mechanically derived candidate set?
                for e in ends:
                    if e not in entities:
                        stats["end_entity_missing_from_graph"] += 1
                        continue
                    key = (entities[e]["type"], entities[e]["field"])
                    sizes.append(len(buckets[key]))
        print(f"{inc}: {len(entities)} entity nodes, "
              f"{len(buckets)} (type, field) buckets, "
              f"bucket sizes {sorted(Counter(len(v) for v in buckets.values()).items())}")
    print()
    for k, v in stats.most_common():
        print(f"  {k:34s} {v}")
    if sizes:
        sizes.sort()
        print(f"\n  candidate-set size: min {sizes[0]}, median {sizes[len(sizes)//2]}, max {sizes[-1]}")
        print(f"  share of questions whose candidate set is a single entity (useless): "
              f"{sum(s == 1 for s in sizes) / len(sizes):.1%}")


if __name__ == "__main__":
    main()
