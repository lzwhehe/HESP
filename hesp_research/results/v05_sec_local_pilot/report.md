# v0.4 · qwen2.5:7b-instruct · all families

Paired local-sandbox study. Intervals are over task clusters of a small, hand-built suite; they do not generalize to real websites or Web CTF.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| react_style | 8 | 0.000 | 7.62 | n/a | 11.88 | 28929 | 328 | DECISION_BUDGET_EXCEEDED:6, TOOL_BUDGET_EXCEEDED:2 |
| memory_only | 8 | 0.000 | 7.38 | n/a | 12 | 32198 | 328 | DECISION_BUDGET_EXCEEDED:8 |
| hesp_eigc_guard | 8 | 1.000 | 4.50 | 4.50 | 4.75 | 12956 | 149 | VERIFIED_SIMULATION:8 |
| hesp_random | 8 | 0.625 | 8.88 | 9 | 7.25 | 20617 | 212 | UNVERIFIED_CLAIM:3, VERIFIED_SIMULATION:5 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| memory_only_minus_react_style | 8 | +0.000 | [+0.000, +0.000] | 0 / 0 | -0.25 | [-1.875, +1.250] |

All failures remain in the denominator; unknown usage stays null.

Primary family (pre-registered): upload-diag; see report_upload-diag.md.
