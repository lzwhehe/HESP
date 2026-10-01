"""Addendum A of docs/PROTOCOL_AUDIT.md: per-question model results on ExCyTIn (o1/v0 test, the release behind the
reported scores) split by shortcut availability.

Inputs: external/excytin/logs/*.json (from excytin_fetch_logs.py), results/audit/excytin_o1v0_test.json (frozen
baselines on that release) and the o1/v0 test questions. Success = reward == 1.

    python scripts/audit/excytin_logs.py
"""
import glob
import json
import os
import random
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EX = Path(os.environ.get("EXCYTIN_ROOT", r"E:\HESP\external\excytin"))
QDIR = EX / "questions_old" / "o1" / "v0" / "test"
SEED, B = 2040, 2000


def norm(s):
    return re.sub(r"\s+", " ", str(s)).strip().lower()


def model_name(run):
    m = re.match(r"BaselineAgent_(.+?)_c\d+_", run)
    return m.group(1) if m else run


def diff_ci(rows, key):
    """Success(key) - success(not key); incident-clustered bootstrap."""
    by = defaultdict(list)
    for r in rows:
        by[r["incident"]].append(r)
    incs = sorted(by)

    def d(sample):
        a = [r["success"] for r in sample if r[key]]
        b = [r["success"] for r in sample if not r[key]]
        return (sum(a) / len(a) - sum(b) / len(b)) if a and b else None

    point = d(rows)
    rng = random.Random(SEED)
    draws = []
    for _ in range(B):
        s = [r for i in (rng.choice(incs) for _ in incs) for r in by[i]]
        v = d(s)
        if v is not None:
            draws.append(v)
    draws.sort()
    return point, [draws[int(0.025 * (len(draws) - 1))], draws[int(0.975 * (len(draws) - 1))]]


def kendall(a, b):
    n, c, dcount = len(a), 0, 0
    for i in range(n):
        for j in range(i + 1, n):
            s = (a[i] - a[j]) * (b[i] - b[j])
            c += s > 0
            dcount += s < 0
    return (c - dcount) / (n * (n - 1) / 2)


def main():
    base = json.loads((ROOT / "results/audit/excytin_o1v0_test.json").read_text(encoding="utf-8"))["rows"]
    qs = {}
    for f in glob.glob(str(QDIR / "*.json")):
        inc = re.match(r"(incident_\d+)_", os.path.basename(f)).group(1)
        for k, item in enumerate(json.load(open(f, encoding="utf-8"))):
            qs[(inc, k)] = item
    flags = {(r["incident"], r["index"]): r for r in base}
    key_of = defaultdict(list)
    for (inc, k), item in qs.items():
        key_of[(inc, norm(item["question"]), norm(item["answer"]))].append(k)

    out = {"models": {}, "unmatched": {}}
    for f in sorted(glob.glob(str(EX / "logs" / "*.json"))):
        run = os.path.basename(f)[:-5]
        logs = json.load(open(f, encoding="utf-8"))
        rows, miss = [], 0
        for L in logs:
            ks = key_of.get((L["incident"], norm(L["question"]), norm(L["answer"])))
            if not ks:
                miss += 1
                continue
            k = L["position"] if L["position"] in ks else ks[0]
            fl = flags[(L["incident"], k)]
            rows.append({"incident": L["incident"], "index": k, "success": L["reward"] == 1, "reward": L["reward"],
                         "named": fl["named"], "table": fl["table_correct"], "graph": fl["graph_correct"],
                         "resistant": not fl["named"] and not fl["graph_correct"] and not fl["table_correct"]})
        out["unmatched"][run] = miss
        n = len(rows)
        succ = sum(r["success"] for r in rows)
        res = [r for r in rows if r["resistant"]]
        dn, cin = diff_ci(rows, "named")
        dt, cit = diff_ci(rows, "table")
        out["models"][model_name(run)] = {
            "run": run, "matched": n, "success": succ / n, "mean_reward": sum(r["reward"] for r in rows) / n,
            "success_named": sum(r["success"] for r in rows if r["named"]) / max(1, sum(r["named"] for r in rows)),
            "success_not_named": sum(r["success"] for r in rows if not r["named"]) / max(1, sum(not r["named"] for r in rows)),
            "diff_named": dn, "ci_named": cin,
            "success_table": sum(r["success"] for r in rows if r["table"]) / max(1, sum(r["table"] for r in rows)),
            "success_not_table": sum(r["success"] for r in rows if not r["table"]) / max(1, sum(not r["table"] for r in rows)),
            "diff_table": dt, "ci_table": cit,
            "resistant_n": len(res), "success_resistant": sum(r["success"] for r in res) / max(1, len(res)),
            "share_successes_table_solvable": sum(r["success"] and r["table"] for r in rows) / max(1, succ),
        }
    ms = out["models"]
    names = list(ms)
    from math import comb
    for key in ("named", "table"):
        pos = sum(1 for m in names if ms[m][f"diff_{key}"] > 0)
        out[f"A{2 if key == 'named' else 3}"] = {
            "positive": pos, "models": len(names),
            "sign_test_one_sided_p": sum(comb(len(names), k) for k in range(pos, len(names) + 1)) / 2 ** len(names),
            "ci_excludes_zero": sum(1 for m in names if ms[m][f"ci_{key}"][0] > 0)}
    full = [ms[m]["success"] for m in names]
    sub = [ms[m]["success_resistant"] for m in names]
    rank_full = {m: i + 1 for i, m in enumerate(sorted(names, key=lambda m: -ms[m]["success"]))}
    rank_sub = {m: i + 1 for i, m in enumerate(sorted(names, key=lambda m: -ms[m]["success_resistant"]))}
    out["A4"] = {"kendall_tau": kendall(full, sub), "rank_full": rank_full, "rank_resistant": rank_sub,
                 "resistant_n": ms[names[0]]["resistant_n"] if names else 0}
    path = ROOT / "results/audit/excytin_logs_analysis.json"
    path.write_text(json.dumps(out, indent=1), encoding="utf-8")
    for m in sorted(names, key=lambda m: -ms[m]["success"]):
        v = ms[m]
        print(f"{m:38s} n={v['matched']} succ={v['success']:.3f} named {v['success_named']:.3f}/{v['success_not_named']:.3f} "
              f"d={v['diff_named']:+.3f} [{v['ci_named'][0]:+.2f},{v['ci_named'][1]:+.2f}] | table d={v['diff_table']:+.3f} "
              f"| resistant {v['success_resistant']:.3f} (rank {rank_full[m]}->{rank_sub[m]}) | share {v['share_successes_table_solvable']:.2f}")
    print("A2", out["A2"], "A3", out["A3"], "A4 tau", round(out["A4"]["kendall_tau"], 3), "unmatched", out["unmatched"])


if __name__ == "__main__":
    main()
