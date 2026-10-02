"""How much the counted sec-triage tables depend on the amount of development data (for the limitations).

Compares the empirical tables counted from k = 1, 5, 20, 100 development episodes per (cause, variant) cell by cell
with the k = 100 table; writes results/table_determinism.json.

    python scripts/table_determinism.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "results/v06_tables"


def load(k):
    return json.loads((TABLES / f"empirical_{k}.json").read_text(encoding="utf-8"))["tables"]


def main():
    ref = load(100)
    cells = [(a, h) for a in ref for h in ref[a]]
    out = {"cells": len(cells), "probes": len(ref), "compared_with": "empirical_100", "by_k": {}}
    for k in (1, 5, 20):
        t = load(k)
        differ = [(a, h) for a, h in cells if any(abs(t[a][h][o] - ref[a][h][o]) > 1e-9 for o in ref[a][h])]
        out["by_k"][k] = {"differing_cells": len(differ), "differing_probes": sorted({a for a, _ in differ})}
    (ROOT / "results/table_determinism.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
