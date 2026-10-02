"""v1.4 summary (PROTOCOL.md v1.4): the small model deciding alone, on structured observations and on raw logs, next to
the paired v1.2 C raw episodes in which the same model only read the logs and the controller decided.

Primary endpoint per model (97.5 %, clusters = the 16 tasks, 2,000 resamples, seed 2030): on drifted logs, verified
completion of "model reads, controller decides" (v1.2 C raw, llm_drifted) minus that of the strongest model-alone
configuration of v1.2 C fair (memory_only, clear_finish), paired by (task, repeat).

    python scripts/v14_summary.py            # writes results/v14_summary.{json,md}
"""
import collections
import json
from pathlib import Path
import random
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hesp.secapp import BENIGN  # noqa: E402

MODELS = [("qwen7b", "Qwen2.5-7B"), ("llama8b", "Llama-3.1-8B")]
ALONE = [f"{m}_{v}" for m in ("react_style", "memory_only") for v in ("v1", "clear_finish")]
CONDITIONS = ("structured", "documented", "drifted")
PRIMARY_ALONE = "memory_only_clear_finish_drifted"
RESAMPLES = 2000


def load(path):
    return [json.loads(line) for line in path.open(encoding="utf-8")] if path.exists() else None


def cell(rs):
    return {"episodes": len(rs),
            "verified": sum(bool(r["verified_simulation"]) for r in rs),
            "named_cause": sum(r["claimed_hypothesis"] not in (None, "other") for r in rs),
            "wrong_cause": sum(r["claimed_hypothesis"] not in (None, "other") and r["claimed_hypothesis"] != r["cause"]
                               for r in rs),
            "missed_attack": sum(r["cause"] not in BENIGN and r["claimed_hypothesis"] in BENIGN for r in rs),
            "no_verdict": sum(r["claimed_hypothesis"] in (None, "other") for r in rs),
            "planner_error": sum(r["status"] == "PLANNER_ERROR" for r in rs),
            "mean_tool_calls": round(statistics.mean(r["tool_calls"] for r in rs), 2),
            "audits_passed": sum(bool(r.get("audit_passed", True)) for r in rs)}


def primary(together, alone, level=0.975, seed=2030):
    a = {(r["task_id"], r["repeat"]): float(bool(r["verified_simulation"])) for r in together}
    b = {(r["task_id"], r["repeat"]): float(bool(r["verified_simulation"])) for r in alone}
    per = collections.defaultdict(list)
    for k in sorted(a.keys() & b.keys()):
        per[k[0]].append(a[k] - b[k])
    diffs = [statistics.mean(v) for _, v in sorted(per.items())]
    rng = random.Random(seed)
    draws = sorted(statistics.mean(rng.choices(diffs, k=len(diffs))) for _ in range(RESAMPLES))
    tail = (1 - level) / 2
    return {"difference": statistics.mean(diffs),
            "ci": [draws[int((RESAMPLES - 1) * tail)], draws[int((RESAMPLES - 1) * (1 - tail))]],
            "level": level, "tasks": len(diffs), "pairs": sum(len(v) for v in per.values())}


def main():
    res = ROOT / "results"
    summary, md = {}, ["# v1.4: the small model deciding alone on raw logs", "",
                       "Verified / episodes; wrong = a named cause other than the true one; missed = attack called benign; "
                       "no verdict = no finish or `other`. Reference rows are the paired v1.2 C raw episodes "
                       "(same tasks, seeds, and log text; the model only reads, the controller decides).", ""]
    for key, label in MODELS:
        rows = load(res / f"v14_alone_{key}" / "outcomes.jsonl")
        ref = load(res / f"v12c_raw_{key}" / "outcomes.jsonl")
        if rows is None or ref is None:
            continue
        by = collections.defaultdict(list)
        for r in rows:
            by[r["arm"]].append(r)
        cells = {f"{a}_{c}": cell(by[f"{a}_{c}"]) for a in ALONE for c in CONDITIONS if by.get(f"{a}_{c}")}
        refs = {f"controller_{p}_{c}": cell([r for r in ref if r["parser"] == p and r["condition"] == c])
                for p, c in (("structured", "documented"), ("rule", "drifted"), ("llm", "drifted"))}
        prim = primary([r for r in ref if r["parser"] == "llm" and r["condition"] == "drifted"], by[PRIMARY_ALONE])
        summary[key] = {"model": label, "alone": cells, "reference": refs, "primary": prim}
        md += [f"## {label}", "", "| configuration | verified | wrong | missed | no verdict | probes |",
               "|---|---|---|---|---|---|"]
        for name, c in list(cells.items()) + list(refs.items()):
            md.append(f"| {name} | {c['verified']}/{c['episodes']} | {c['wrong_cause']} | {c['missed_attack']} | "
                      f"{c['no_verdict']} | {c['mean_tool_calls']} |")
        md += ["", f"Primary (97.5 %): controller with {label} reading drifted logs minus {label} alone "
                   f"({PRIMARY_ALONE}): **{prim['difference']:+.3f} [{prim['ci'][0]:+.3f}, {prim['ci'][1]:+.3f}]** "
                   f"({prim['tasks']} tasks, {prim['pairs']} pairs)", ""]
    (res / "v14_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (res / "v14_summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
