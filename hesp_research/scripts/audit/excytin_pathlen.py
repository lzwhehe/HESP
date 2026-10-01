"""Exploratory (not registered): per-model success on ExCyTIn o1/v0 test by length of the generation path
(shortest_alert_path; length 1 = the answer is an entity of the alert described in the context).

    python scripts/audit/excytin_pathlen.py
"""
import glob
import json
import os
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EX = Path(os.environ.get("EXCYTIN_ROOT", r"E:\HESP\external\excytin"))


def norm(s):
    return re.sub(r"\s+", " ", str(s)).strip().lower()


def main():
    length = {}
    for f in glob.glob(str(EX / "questions_old/o1/v0/test/*.json")):
        inc = re.match(r"(incident_\d+)_", os.path.basename(f)).group(1)
        for q in json.load(open(f, encoding="utf-8")):
            length[(inc, norm(q["question"]), norm(q["answer"]))] = len(q["shortest_alert_path"])
    out = {}
    for f in sorted(glob.glob(str(EX / "logs/*.json"))):
        model = re.match(r"BaselineAgent_(.+?)_c\d+_", os.path.basename(f)).group(1)
        by = defaultdict(list)
        for r in json.load(open(f, encoding="utf-8")):
            n = length.get((r["incident"], norm(r["question"]), norm(r["answer"])))
            group = "1" if n == 1 else ("3" if n == 3 else ">=5")
            by[group].append(r["reward"] == 1)
        out[model] = {g: {"n": len(v), "success": sum(v) / len(v)} for g, v in sorted(by.items())}
        print(model, {g: round(v["success"], 3) for g, v in out[model].items()})
    (ROOT / "results/audit/excytin_pathlen.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
