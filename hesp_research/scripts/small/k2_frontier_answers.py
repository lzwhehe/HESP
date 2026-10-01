"""Historical reference for K2 (docs/PROTOCOL_SMALL.md, section K2-能力): download the submitted answers of the 14 published
ExCyTIn runs (microsoft/SecRL, latest_experiments/) on the o1 test release and rescore them with the frozen K1 scorer.

Keeps only incident, position, question, gold answer, submitted answer, and the benchmark's own reward.

    python scripts/small/k2_frontier_answers.py     # writes results/small/k2_frontier.json
"""
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import k1_run as k1  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
API = "https://api.github.com/repos/microsoft/SecRL/git/trees/main?recursive=1"
RAW = "https://raw.githubusercontent.com/microsoft/SecRL/main/"
CACHE = Path(os.environ.get("EXCYTIN_ROOT", r"E:\HESP\external\excytin")) / "logs_answers"


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "audit"}), timeout=300) as r:
        return r.read()


def main():
    tree = json.loads(get(API))["tree"]
    files = [t["path"] for t in tree if t["path"].startswith("latest_experiments/")
             and os.path.basename(t["path"]).startswith("agent_incident_")]
    runs = sorted({p.split("/")[1] for p in files})
    CACHE.mkdir(parents=True, exist_ok=True)
    flags = {(x["incident"], x["index"]): x["resistant"]
             for x in json.load(open(ROOT / "results/small/k2_questions.json", encoding="utf-8"))}
    qindex = {}
    for x in json.load(open(ROOT / "results/small/k2_questions.json", encoding="utf-8")):
        qindex.setdefault((x["incident"], k1.k.norm(x["q"]["question"]), k1.k.norm(x["q"]["answer"])), []).append(x["index"])
    out = {}
    for run in runs:
        dest = CACHE / f"{run}.json"
        if not dest.exists():
            rows = []
            for p in sorted(f for f in files if f.split("/")[1] == run):
                inc = os.path.basename(p)[len("agent_"):-5]
                for pos, item in enumerate(json.loads(get(RAW + p))):
                    q = item.get("question_dict", {})
                    info = item.get("trials", {}).get("0", {}).get("info", {})
                    rows.append({"incident": inc, "position": pos, "question": q.get("question"), "answer": q.get("answer"),
                                 "submitted": info.get("submitted_answer", "") or "", "reward": item.get("reward")})
            dest.write_text(json.dumps(rows), encoding="utf-8")
            print("fetched", run, len(rows), flush=True)
        rows = json.loads(dest.read_text(encoding="utf-8"))
        model = re.match(r"BaselineAgent_(.+?)_c\d+_", run).group(1)
        scored, res = [], []
        for r in rows:
            idx = qindex.get((r["incident"], k1.k.norm(r["question"]), k1.k.norm(r["answer"])))
            if not idx:
                continue
            i = r["position"] if r["position"] in idx else idx[0]
            ok = k1.correct(r["answer"], r["submitted"])
            scored.append(ok)
            if flags[(r["incident"], i)]:
                res.append(ok)
        out[model] = {"matched": len(scored), "accuracy": sum(scored) / len(scored),
                      "accuracy_resistant": sum(res) / len(res) if res else None,
                      "benchmark_success": sum(1 for r in rows if r["reward"] == 1) / len(rows)}
        print(model, json.dumps(out[model]), flush=True)
    (ROOT / "results/small/k2_frontier.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
