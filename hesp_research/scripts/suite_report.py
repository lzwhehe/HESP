"""Markdown report for a paired suite (shared by the study scripts)."""


def fmt(v, digits=3):
    return "n/a" if v is None else (f"{v:.{digits}f}" if isinstance(v, float) else str(v))


def ci(interval):
    return "n/a" if not interval else f"[{interval[0]:+.3f}, {interval[1]:+.3f}]"


def write_report(path, title, report, notes=()):
    lines = [f"# {title}", "", report["warning"], ""]
    lines += ["| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | "
              "Mean input tokens | Mean output tokens | Statuses |",
              "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |"]
    for arm, v in report["modes"].items():
        statuses = ", ".join(f"{k}:{n}" for k, n in sorted(v["statuses"].items()))
        lines.append(f"| {arm} | {v['runs']} | {v['verified_fraction']:.3f} | "
                     f"{fmt(v['tool_cost_units']['mean_known'], 2)} | {fmt(v['tool_cost_when_verified'], 2)} | "
                     f"{fmt(v['planner_calls']['mean_known'], 2)} | "
                     f"{fmt(v['reported_input_tokens']['mean_known'], 0)} | "
                     f"{fmt(v['reported_output_tokens']['mean_known'], 0)} | {statuses} |")
    if report["paired_verification"]:
        lines += ["", "## Paired differences (task-cluster bootstrap, 95% percentile interval)", "",
                  "| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |",
                  "| --- | ---: | ---: | --- | --- | ---: | --- |"]
        for name, v in report["paired_verification"].items():
            c = report["paired_tool_cost"][name]
            lines.append(f"| {name} | {v['task_clusters']} | {v['difference']:+.3f} | "
                         f"{ci(v['cluster_bootstrap_percentile_95'])} | {v['tasks_better']} / {v['tasks_worse']} | "
                         f"{c['difference']:+.2f} | {ci(c['cluster_bootstrap_percentile_95'])} |")
    lines += ["", "All failures remain in the denominator; unknown usage stays null.", *notes]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
