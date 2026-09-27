# v0.4 · qwen2.5-7b-instruct · all families

Paired local-sandbox study. Intervals are over task clusters of a small, hand-built suite; they do not generalize to real websites or Web CTF.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| react_style | 72 | 0.028 | 9.24 | 8 | 10.88 | 15315 | 318 | DECISION_BUDGET_EXCEEDED:26, TOOL_BUDGET_EXCEEDED:44, VERIFIED_SIMULATION:2 |
| memory_only | 72 | 0.111 | 9.42 | 7.88 | 10.22 | 16977 | 301 | DECISION_BUDGET_EXCEEDED:14, TOOL_BUDGET_EXCEEDED:50, VERIFIED_SIMULATION:8 |
| memory_guard | 72 | 0.111 | 9.36 | 7.88 | 10.26 | 17066 | 303 | DECISION_BUDGET_EXCEEDED:13, TOOL_BUDGET_EXCEEDED:51, VERIFIED_SIMULATION:8 |
| hesp_eigc | 72 | 0.958 | 5.75 | 5.83 | 5.79 | 10030 | 185 | UNVERIFIED_CLAIM:3, VERIFIED_SIMULATION:69 |
| hesp_eigc_guard | 72 | 1.000 | 5.75 | 5.75 | 5.92 | 10271 | 191 | VERIFIED_SIMULATION:72 |
| hesp_la | 72 | 0.889 | 6.71 | 6.61 | 5.71 | 9892 | 189 | UNVERIFIED_CLAIM:8, VERIFIED_SIMULATION:64 |
| hesp_la_guard | 72 | 0.889 | 6.71 | 6.61 | 6.28 | 11049 | 219 | DECISION_BUDGET_EXCEEDED:8, VERIFIED_SIMULATION:64 |
| hesp_random | 72 | 0.667 | 9.28 | 9.08 | 7.60 | 13817 | 243 | UNVERIFIED_CLAIM:24, VERIFIED_SIMULATION:48 |
| hesp_llmp | 72 | 0.417 | 9.96 | 9.97 | 8.22 | 14733 | 258 | UNVERIFIED_CLAIM:42, VERIFIED_SIMULATION:30 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| hesp_la_guard_minus_memory_only | 24 | +0.778 | [+0.583, +0.931] | 20 / 1 | -2.71 | [-3.556, -1.931] |
| hesp_la_guard_minus_react_style | 24 | +0.861 | [+0.681, +1.000] | 22 / 1 | -2.53 | [-3.528, -1.556] |
| memory_only_minus_react_style | 24 | +0.083 | [+0.000, +0.208] | 2 / 0 | +0.18 | [-0.250, +0.556] |
| hesp_eigc_minus_memory_only | 24 | +0.847 | [+0.667, +1.000] | 21 / 1 | -3.67 | [-4.625, -2.792] |
| hesp_eigc_guard_minus_hesp_eigc | 24 | +0.042 | [+0.000, +0.125] | 1 / 0 | +0.00 | [+0.000, +0.000] |
| memory_guard_minus_memory_only | 24 | +0.000 | [+0.000, +0.000] | 0 / 0 | -0.06 | [-0.111, -0.014] |
| hesp_la_guard_minus_memory_guard | 24 | +0.778 | [+0.583, +0.931] | 20 / 1 | -2.65 | [-3.500, -1.861] |
| hesp_la_minus_hesp_eigc | 24 | -0.069 | [-0.181, +0.000] | 0 / 2 | +0.96 | [+0.250, +1.722] |
| hesp_eigc_minus_hesp_random | 24 | +0.292 | [+0.153, +0.444] | 13 / 1 | -3.53 | [-4.333, -2.750] |
| hesp_eigc_minus_hesp_llmp | 24 | +0.542 | [+0.292, +0.750] | 14 / 1 | -4.21 | [-5.181, -3.278] |

All failures remain in the denominator; unknown usage stays null.

Primary family (pre-registered): upload-diag; see report_upload-diag.md.
