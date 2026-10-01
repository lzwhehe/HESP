"""Download the per-question evaluation logs that ExCyTIn-Bench publishes (microsoft/SecRL, latest_experiments/) and
keep only what the audit needs: incident, position, question, gold answer, reward. Writes
external/excytin/logs/<run>.json. Reads nothing else.

    python scripts/audit/excytin_fetch_logs.py
"""
import json
import os
import tempfile
import urllib.request

API = "https://api.github.com/repos/microsoft/SecRL/git/trees/main?recursive=1"
RAW = "https://raw.githubusercontent.com/microsoft/SecRL/main/"
OUT = os.path.join(os.environ.get("EXCYTIN_ROOT", r"E:\HESP\external\excytin"), "logs")


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "audit"}), timeout=300) as r:
        return r.read()


def main():
    tree = json.loads(get(API))["tree"]
    files = [t["path"] for t in tree if t["path"].startswith("latest_experiments/")
             and os.path.basename(t["path"]).startswith("agent_incident_")]
    runs = sorted({p.split("/")[1] for p in files})
    os.makedirs(OUT, exist_ok=True)
    for run in runs:
        dest = os.path.join(OUT, run + ".json")
        if os.path.exists(dest):
            continue
        rows = []
        for p in sorted(f for f in files if f.split("/")[1] == run):
            inc = os.path.basename(p)[len("agent_"):-5]
            data = json.loads(get(RAW + p))
            for k, item in enumerate(data):
                q = item.get("question_dict", {})
                rows.append({"incident": inc, "position": k, "question": q.get("question"), "answer": q.get("answer"),
                             "start_alert": q.get("start_alert"), "end_alert": q.get("end_alert"),
                             "reward": item.get("reward")})
        tmp = dest + ".part"
        json.dump(rows, open(tmp, "w", encoding="utf-8"))
        os.replace(tmp, dest)
        print(run, len(rows), flush=True)


if __name__ == "__main__":
    main()
