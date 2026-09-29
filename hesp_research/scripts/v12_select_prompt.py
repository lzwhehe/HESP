"""Apply the pre-registered prompt-selection rule of PROTOCOL.md v1.2 C to the development runs.

Rule (fixed before any C episode): among the non-default variants (explicit_rule, finish_example, clear_finish),
choose the one with the highest mean verified completion over the four development cells
{react_style, memory_only} x {Qwen2.5-7B, Llama-3.1-8B}; ties go to the variant listed first. The development
runs use seed 7000 and never the test seeds.

    python scripts/v12_select_prompt.py results/v12c_dev_qwen7b results/v12c_dev_llama8b
"""
import json
from pathlib import Path
import statistics
import sys

CANDIDATES = ("explicit_rule", "finish_example", "clear_finish")


def main():
    cells = {}
    for d in sys.argv[1:]:
        rows = [json.loads(line) for line in (Path(d) / "outcomes.jsonl").open(encoding="utf-8")]
        for r in rows:
            cells.setdefault((Path(d).name, r["arm"]), []).append(float(bool(r["verified_simulation"])))
    table = {k: statistics.mean(v) for k, v in cells.items()}
    scores = {}
    for v in ("v1",) + CANDIDATES:
        vals = [table[(m, f"{mode}_{v}")] for m in {k[0] for k in table} for mode in ("react_style", "memory_only")]
        scores[v] = statistics.mean(vals)
    chosen = max(CANDIDATES, key=lambda v: (scores[v], -CANDIDATES.index(v)))
    print(json.dumps({"cells": {f"{m}|{a}": round(x, 3) for (m, a), x in sorted(table.items())},
                      "mean_by_variant": {k: round(v, 3) for k, v in scores.items()}, "selected": chosen}, indent=2))


if __name__ == "__main__":
    main()
