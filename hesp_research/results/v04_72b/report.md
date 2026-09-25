# v0.4 · qwen2.5-72b-instruct-awq · all families

Paired local-sandbox study. Intervals are over task clusters of a small, hand-built suite; they do not generalize to real websites or Web CTF.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| react_style | 144 | 0.778 | 4.01 | 3.66 | 4.69 | 5826 | 162 | UNVERIFIED_CLAIM:32, VERIFIED_SIMULATION:112 |
| memory_only | 144 | 0.812 | 4.14 | 3.80 | 5.06 | 7482 | 172 | UNVERIFIED_CLAIM:27, VERIFIED_SIMULATION:117 |
| memory_guard | 144 | 0.896 | 4.44 | 4.03 | 5.69 | 9047 | 216 | DECISION_BUDGET_EXCEEDED:9, TOOL_BUDGET_EXCEEDED:1, UNVERIFIED_CLAIM:5, VERIFIED_SIMULATION:129 |
| hesp_eigc | 144 | 0.861 | 3.21 | 3.08 | 3 | 4604 | 103 | UNVERIFIED_CLAIM:20, VERIFIED_SIMULATION:124 |
| hesp_eigc_guard | 144 | 0.903 | 3.33 | 3.22 | 3.97 | 6334 | 144 | DECISION_BUDGET_EXCEEDED:13, UNVERIFIED_CLAIM:1, VERIFIED_SIMULATION:130 |
| hesp_la | 144 | 0.931 | 4.03 | 3.87 | 2.67 | 4051 | 93 | UNVERIFIED_CLAIM:10, VERIFIED_SIMULATION:134 |
| hesp_la_guard | 144 | 0.951 | 4.12 | 4.01 | 3.18 | 4959 | 114 | DECISION_BUDGET_EXCEEDED:6, TOOL_BUDGET_EXCEEDED:1, VERIFIED_SIMULATION:137 |
| hesp_random | 144 | 0.882 | 5.08 | 4.98 | 4.82 | 7818 | 160 | UNVERIFIED_CLAIM:17, VERIFIED_SIMULATION:127 |
| hesp_llmp | 144 | 0.896 | 4 | 3.87 | 3.34 | 5156 | 114 | UNVERIFIED_CLAIM:15, VERIFIED_SIMULATION:129 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| hesp_la_guard_minus_memory_only | 48 | +0.139 | [+0.056, +0.236] | 9 / 1 | -0.02 | [-0.681, +0.632] |
| hesp_la_guard_minus_react_style | 48 | +0.174 | [+0.090, +0.271] | 14 / 1 | +0.10 | [-0.535, +0.736] |
| memory_only_minus_react_style | 48 | +0.035 | [-0.035, +0.104] | 6 / 2 | +0.12 | [-0.076, +0.354] |
| hesp_eigc_minus_memory_only | 48 | +0.049 | [-0.056, +0.146] | 7 / 3 | -0.93 | [-1.444, -0.444] |
| hesp_eigc_guard_minus_hesp_eigc | 48 | +0.042 | [+0.000, +0.104] | 2 / 0 | +0.12 | [+0.000, +0.312] |
| memory_guard_minus_memory_only | 48 | +0.083 | [+0.021, +0.153] | 6 / 0 | +0.31 | [+0.090, +0.549] |
| hesp_la_guard_minus_memory_guard | 48 | +0.056 | [+0.000, +0.118] | 7 / 3 | -0.33 | [-1.028, +0.319] |
| hesp_la_minus_hesp_eigc | 48 | +0.069 | [-0.021, +0.174] | 7 / 4 | +0.83 | [+0.299, +1.347] |
| hesp_eigc_minus_hesp_random | 48 | -0.021 | [-0.132, +0.076] | 11 / 7 | -1.87 | [-2.389, -1.306] |
| hesp_eigc_minus_hesp_llmp | 48 | -0.035 | [-0.132, +0.049] | 5 / 5 | -0.79 | [-1.472, -0.083] |

All failures remain in the denominator; unknown usage stays null.

Primary family (pre-registered): upload-diag; see report_upload-diag.md.
