"""Exploratory (not registered): how do agents behave on ExCyTIn questions that one alert-table lookup answers?

For a few runs in latest_experiments/, downloads the agent logs, and for each o1/v0 test question records: success,
whether an answer was submitted, the number of SQL actions, whether any query touched SecurityAlert, and, for wrong
answers, whether the submitted value is an entity of the end alert in the incident graph. Writes
results/audit/excytin_traces.json.

    python scripts/audit/excytin_traces.py
"""
import json
import os
import re
import sys
import urllib.request
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import excytin_shortcut as ex  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
RAW = "https://raw.githubusercontent.com/microsoft/SecRL/main/latest_experiments/"
RUNS = ["BaselineAgent_claude-opus-4.5_c310_alert_level_t0_s25_trial1", "BaselineAgent_o3_c106_alert_level_t0_s25_trial1",
        "BaselineAgent_gpt-5_c121_alert_level_t0_s25_trial1"]
INCS = ["incident_5", "incident_34", "incident_38", "incident_39", "incident_55", "incident_134", "incident_166", "incident_322"]


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "audit"}), timeout=300) as r:
        return json.loads(r.read())


def main():
    base = json.loads((ROOT / "results/audit/excytin_o1v0_test.json").read_text(encoding="utf-8"))["rows"]
    flags = {(r["incident"], r["index"]): r for r in base}
    qdir = Path(os.environ.get("EXCYTIN_ROOT", r"E:\HESP\external\excytin")) / "questions_old/o1/v0/test"
    out = {}
    for run in RUNS:
        model = re.match(r"BaselineAgent_(.+?)_c\d+_", run).group(1)
        rows = []
        for inc in INCS:
            nodes, adj = ex.load_graph(os.path.join(ex.ROOT, "graphs", f"{inc}.graphml"))
            qs = json.load(open(next(qdir.glob(f"{inc}_*.json")), encoding="utf-8"))
            index = defaultdict(list)
            for k, q in enumerate(qs):
                index[(ex.norm(q["question"]), ex.norm(q["answer"]))].append(k)
            for pos, item in enumerate(get(RAW + f"{run}/agent_{inc}.json")):
                q = item["question_dict"]
                ks = index.get((ex.norm(q["question"]), ex.norm(q["answer"])), [])
                if not ks:
                    continue
                k = pos if pos in ks else ks[0]
                t = item["trials"]["0"]
                acts = [m["content"] for m in t["messages"] if m.get("role") == "assistant"]
                sql = [a for a in acts if "execute[" in a]
                sub = ex.norm(t["info"].get("submitted_answer", "") or "")
                end_vals = {ex.norm(nodes[m].get("value", "") or nodes[m].get("name", ""))
                            for m in adj.get(str(qs[k]["end_alert"]), set())}
                rows.append({"incident": inc, "index": k, "success": item["reward"] == 1,
                             "table": flags[(inc, k)]["table_correct"], "named": flags[(inc, k)]["named"],
                             "submitted": t["info"].get("submit") in (True, "True") and bool(sub), "sql_steps": len(sql),
                             "touched_alert_table": any("securityalert" in a.lower() for a in sql),
                             "wrong_value_is_end_alert_entity": bool(sub) and item["reward"] != 1 and any(
                                 v and (v == sub or v in sub) for v in end_vals)})
        def agg(sel):
            n = len(sel)
            fail = [r for r in sel if not r["success"]]
            return {"n": n, "success": sum(r["success"] for r in sel) / n,
                    "mean_sql_steps": sum(r["sql_steps"] for r in sel) / n,
                    "touched_alert_table": sum(r["touched_alert_table"] for r in sel) / n,
                    "failures": len(fail), "failures_no_answer": sum(not r["submitted"] for r in fail),
                    "failures_value_from_end_alert": sum(r["wrong_value_is_end_alert_entity"] for r in fail)}
        out[model] = {"all": agg(rows), "table_solvable": agg([r for r in rows if r["table"]]),
                      "other": agg([r for r in rows if not r["table"]])}
        print(model, json.dumps(out[model]))
    (ROOT / "results/audit/excytin_traces.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
