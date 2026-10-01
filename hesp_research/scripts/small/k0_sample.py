"""K0 sample (docs/PROTOCOL_SMALL.md): 25 shortcut-resistant + 25 other ExCyTIn opus5 TRAIN questions, seed 2041.

    python scripts/small/k0_sample.py      # writes results/small/k0_sample.json
"""
import csv
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    rows = [r for r in csv.DictReader(open(ROOT / "results/audit/excytin_flags.csv", encoding="utf-8"))
            if r["question_set"] == "opus5_train"]
    rng = random.Random(2041)
    res = sorted([r for r in rows if r["shortcut_resistant"] == "1"], key=lambda r: (r["incident"], int(r["index"])))
    oth = sorted([r for r in rows if r["shortcut_resistant"] == "0"], key=lambda r: (r["incident"], int(r["index"])))
    pick = [(r, 1) for r in rng.sample(res, 25)] + [(r, 0) for r in rng.sample(oth, 25)]
    out = [{"incident": r["incident"], "index": int(r["index"]), "resistant": s,
            "table_lookup_correct": int(r["table_lookup_correct"])} for r, s in pick]
    out.sort(key=lambda x: (x["incident"], x["index"]))
    path = ROOT / "results/small/k0_sample.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=1), encoding="utf-8")
    from collections import Counter
    print(len(out), Counter(x["incident"] for x in out), "table floor on sample:", sum(x["table_lookup_correct"] for x in out))


if __name__ == "__main__":
    main()
