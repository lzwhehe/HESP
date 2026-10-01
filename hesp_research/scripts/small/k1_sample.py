"""K1 sample (docs/PROTOCOL_SMALL.md, revision K1): 40 shortcut-resistant + 40 other ExCyTIn opus5 TRAIN questions, seed 2042.

    python scripts/small/k1_sample.py      # writes results/small/k1_sample.json and k1_questions.json
"""
import csv
import json
import random
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QROOT = Path(r"E:\HESP\external\excytin\questions")


def main():
    rows = [r for r in csv.DictReader(open(ROOT / "results/audit/excytin_flags.csv", encoding="utf-8"))
            if r["question_set"] == "opus5_train"]
    key = lambda r: (r["incident"], int(r["index"]))  # noqa: E731
    res = sorted([r for r in rows if r["shortcut_resistant"] == "1"], key=key)
    oth = sorted([r for r in rows if r["shortcut_resistant"] == "0"], key=key)
    rng = random.Random(2042)
    pick = [(r, 1) for r in rng.sample(res, 40)] + [(r, 0) for r in rng.sample(oth, 40)]
    out = sorted([{"incident": r["incident"], "index": int(r["index"]), "resistant": s,
                   "table_lookup_correct": int(r["table_lookup_correct"])} for r, s in pick],
                 key=lambda x: (x["incident"], x["index"]))
    (ROOT / "results/small/k1_sample.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    cache = {}
    items = []
    for x in out:
        if x["incident"] not in cache:
            cache[x["incident"]] = json.load(open(QROOT / f"{x['incident']}_train.json", encoding="utf-8"))
        items.append({**x, "q": cache[x["incident"]][x["index"]]})
    (ROOT / "results/small/k1_questions.json").write_text(json.dumps(items), encoding="utf-8")
    print(len(out), Counter(x["incident"] for x in out), "table floor:", sum(x["table_lookup_correct"] for x in out))


if __name__ == "__main__":
    main()
