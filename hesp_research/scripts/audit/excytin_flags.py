"""Write the per-question shortcut flags for every audited ExCyTIn question set (released with the paper).

Columns: question_set, incident, index (position in the set's file), named, adjacent, graph_lookup_correct,
table_lookup_correct, shortcut_resistant (not named and neither lookup correct).

    python scripts/audit/excytin_flags.py      # writes results/audit/excytin_flags.csv
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SETS = [("opus5_train", "excytin_train.json"), ("opus5_test", "excytin_test.json"),
        ("o1_v0_test", "excytin_o1v0_test.json"), ("o1_v1_test", "excytin_o1v1_test.json")]


def main():
    out = ROOT / "results/audit/excytin_flags.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["question_set", "incident", "index", "named", "adjacent", "graph_lookup_correct",
                    "table_lookup_correct", "shortcut_resistant"])
        counts = {}
        for name, fn in SETS:
            rows = json.loads((ROOT / "results/audit" / fn).read_text(encoding="utf-8"))["rows"]
            for r in rows:
                res = not r["named"] and not r["graph_correct"] and not r["table_correct"]
                w.writerow([name, r["incident"], r["index"], int(r["named"]), int(r["adjacent"]),
                            int(r["graph_correct"]), int(r["table_correct"]), int(res)])
                counts[name] = counts.get(name, 0) + res
    print(out, "shortcut-resistant per set:", counts)


if __name__ == "__main__":
    main()
