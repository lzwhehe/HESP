"""Aggregate the v0.4 study across models: tables (Markdown + JSON) for the report.

Reads results/v04_<key>/analysis_by_family.json and results/v04_<key>_elicitation.json.
Descriptive aggregation only; the pre-registered primary endpoint is reported per model.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "results"
MODELS = [("7b", "Qwen2.5-7B"), ("32b", "Qwen2.5-32B-AWQ"), ("72b", "Qwen2.5-72B-AWQ")]
ARMS = ["react_style", "memory_only", "memory_guard", "hesp_eigc", "hesp_eigc_guard", "hesp_la",
        "hesp_la_guard", "hesp_random", "hesp_llmp"]
FAMILIES = [("upload-diag", "held-out, primary"), ("web-diag", "development")]
KEY_COMPARISONS = ["hesp_la_guard_minus_memory_only", "hesp_eigc_minus_memory_only", "memory_only_minus_react_style",
                   "memory_guard_minus_memory_only", "hesp_eigc_guard_minus_hesp_eigc", "hesp_la_minus_hesp_eigc",
                   "hesp_eigc_minus_hesp_random", "hesp_eigc_minus_hesp_llmp"]


def ci(v):
    i = v["cluster_bootstrap_percentile_95"]
    return f"{v['difference']:+.3f} [{i[0]:+.2f}, {i[1]:+.2f}]" if i else f"{v['difference']:+.3f}"


def main():
    present = [(k, n) for k, n in MODELS if (ROOT / f"v04_{k}" / "analysis_by_family.json").exists()]
    data = {k: json.loads((ROOT / f"v04_{k}" / "analysis_by_family.json").read_text(encoding="utf-8"))
            for k, _ in present}
    elic = {k: json.loads((ROOT / f"v04_{k}_elicitation.json").read_text(encoding="utf-8")) for k, _ in present}
    out = {"models": [n for _, n in present], "families": {}}
    lines = ["# v0.4 results across models", "",
             "Verified completion rate per arm (72 episodes per cell: 24 tasks x 3 repeats). "
             "Differences are paired per task, 95% task-cluster bootstrap intervals.", ""]
    for fam, role in FAMILIES:
        out["families"][fam] = {}
        lines += [f"## {fam} ({role})", "", "| Arm | " + " | ".join(n for _, n in present) + " |",
                  "| --- |" + " ---: |" * len(present)]
        for arm in ARMS:
            vals = [data[k][fam]["modes"][arm]["verified_fraction"] for k, _ in present]
            out["families"][fam][arm] = dict(zip([n for _, n in present], vals))
            best = max(vals)
            lines.append(f"| {arm} | " + " | ".join(f"**{v:.3f}**" if v == best else f"{v:.3f}" for v in vals) + " |")
        lines += ["", "| Comparison | " + " | ".join(n for _, n in present) + " |", "| --- |" + " --- |" * len(present)]
        for comp in KEY_COMPARISONS:
            lines.append(f"| {comp}{' (primary)' if comp == KEY_COMPARISONS[0] and fam == 'upload-diag' else ''} | "
                         + " | ".join(ci(data[k][fam]["paired_verification"][comp]) for k, _ in present) + " |")
        lines += ["", "| Mean tool cost | " + " | ".join(n for _, n in present) + " |", "| --- |" + " ---: |" * len(present)]
        for arm in ARMS:
            lines.append(f"| {arm} | " + " | ".join(f"{data[k][fam]['modes'][arm]['tool_cost_units']['mean_known']:.2f}"
                                                   for k, _ in present) + " |")
        lines.append("")
    lines += ["## Self-elicited predictive tables vs the sandbox generator (base variant)", "",
              "| Model | family | KL (bits) | Brier | argmax agreement | fallback rows |", "| --- | --- | ---: | ---: | ---: | ---: |"]
    out["calibration"] = {}
    for k, n in present:
        for fam, _ in FAMILIES:
            c = elic[k]["families"][fam]["calibration_vs_true_model"]["base"]["llm"]
            out["calibration"].setdefault(n, {})[fam] = c
            ids = set(elic[k]["families"][fam]["tables"])
            fallback = sum(r["uniform_fallback"] for r in elic[k]["records"] if r["action_id"] in ids)
            c = {**c, "uniform_fallback_rows": fallback}
            out["calibration"][n][fam] = c
            lines.append(f"| {n} | {fam} | {c['kl_bits']:.2f} | {c['expected_brier']:.3f} | "
                         f"{c['argmax_agreement']:.2f} | {fallback} |")
    (ROOT / "v04_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (ROOT / "v04_summary.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
