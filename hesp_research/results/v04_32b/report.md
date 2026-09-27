# v0.4 · qwen2.5-32b-instruct-awq · all families

Paired local-sandbox study. Intervals are over task clusters of a small, hand-built suite; they do not generalize to real websites or Web CTF.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| react_style | 144 | 0.778 | 4.71 | 4.71 | 5.10 | 6279 | 164 | TOOL_BUDGET_EXCEEDED:3, UNVERIFIED_CLAIM:29, VERIFIED_SIMULATION:112 |
| memory_only | 144 | 0.917 | 4.43 | 4.21 | 5.12 | 7468 | 165 | UNVERIFIED_CLAIM:12, VERIFIED_SIMULATION:132 |
| memory_guard | 144 | 0.951 | 4.56 | 4.40 | 5.36 | 7895 | 176 | DECISION_BUDGET_EXCEEDED:4, UNVERIFIED_CLAIM:3, VERIFIED_SIMULATION:137 |
| hesp_eigc | 144 | 0.819 | 3.73 | 3.70 | 3.35 | 5172 | 117 | UNVERIFIED_CLAIM:26, VERIFIED_SIMULATION:118 |
| hesp_eigc_guard | 144 | 0.986 | 4.52 | 4.44 | 4.29 | 6871 | 152 | DECISION_BUDGET_EXCEEDED:1, UNVERIFIED_CLAIM:1, VERIFIED_SIMULATION:142 |
| hesp_la | 144 | 0.896 | 4.66 | 4.46 | 2.91 | 4439 | 103 | UNVERIFIED_CLAIM:15, VERIFIED_SIMULATION:129 |
| hesp_la_guard | 144 | 0.958 | 4.97 | 4.78 | 3.39 | 5310 | 123 | DECISION_BUDGET_EXCEEDED:2, STOPPED_UNRESOLVED:1, UNVERIFIED_CLAIM:3, VERIFIED_SIMULATION:138 |
| hesp_random | 144 | 0.896 | 5.47 | 5.31 | 5.10 | 8338 | 166 | UNVERIFIED_CLAIM:15, VERIFIED_SIMULATION:129 |
| hesp_llmp | 144 | 0.868 | 5.35 | 5.35 | 5.35 | 8769 | 174 | UNVERIFIED_CLAIM:19, VERIFIED_SIMULATION:125 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| hesp_la_guard_minus_memory_only | 48 | +0.042 | [-0.042, +0.125] | 7 / 4 | +0.53 | [-0.000, +1.076] |
| hesp_la_guard_minus_react_style | 48 | +0.181 | [+0.062, +0.299] | 14 / 3 | +0.26 | [-0.417, +0.924] |
| memory_only_minus_react_style | 48 | +0.139 | [+0.062, +0.229] | 12 / 1 | -0.28 | [-0.694, +0.125] |
| hesp_eigc_minus_memory_only | 48 | -0.097 | [-0.215, +0.007] | 4 / 8 | -0.70 | [-1.285, -0.167] |
| hesp_eigc_guard_minus_hesp_eigc | 48 | +0.167 | [+0.076, +0.271] | 9 / 0 | +0.79 | [+0.361, +1.306] |
| memory_guard_minus_memory_only | 48 | +0.035 | [+0.007, +0.062] | 5 / 0 | +0.13 | [+0.014, +0.264] |
| hesp_la_guard_minus_memory_guard | 48 | +0.007 | [-0.062, +0.076] | 4 / 4 | +0.40 | [-0.194, +0.993] |
| hesp_la_minus_hesp_eigc | 48 | +0.076 | [-0.035, +0.194] | 9 / 5 | +0.93 | [+0.368, +1.535] |
| hesp_eigc_minus_hesp_random | 48 | -0.076 | [-0.188, +0.021] | 9 / 9 | -1.74 | [-2.257, -1.208] |
| hesp_eigc_minus_hesp_llmp | 48 | -0.049 | [-0.160, +0.056] | 5 / 7 | -1.62 | [-2.285, -0.931] |

All failures remain in the denominator; unknown usage stays null.

Primary family (pre-registered): upload-diag; see report_upload-diag.md.
