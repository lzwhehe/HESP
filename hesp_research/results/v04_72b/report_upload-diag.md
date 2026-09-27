# v0.4 · qwen2.5-72b-instruct-awq · upload-diag

Fixture repetitions are deterministic; intervals are pipeline checks, not efficacy evidence.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| react_style | 72 | 0.806 | 4.25 | 3.81 | 5.21 | 6761 | 180 | UNVERIFIED_CLAIM:14, VERIFIED_SIMULATION:58 |
| memory_only | 72 | 0.819 | 4.21 | 3.83 | 5.18 | 7981 | 178 | UNVERIFIED_CLAIM:13, VERIFIED_SIMULATION:59 |
| memory_guard | 72 | 0.847 | 4.44 | 3.93 | 6.01 | 10347 | 249 | DECISION_BUDGET_EXCEEDED:7, UNVERIFIED_CLAIM:4, VERIFIED_SIMULATION:61 |
| hesp_eigc | 72 | 0.917 | 3.06 | 3.06 | 2.94 | 4530 | 101 | UNVERIFIED_CLAIM:6, VERIFIED_SIMULATION:66 |
| hesp_eigc_guard | 72 | 1.000 | 3.31 | 3.31 | 3.24 | 5030 | 113 | VERIFIED_SIMULATION:72 |
| hesp_la | 72 | 0.889 | 4.43 | 4.23 | 2.85 | 4363 | 97 | UNVERIFIED_CLAIM:8, VERIFIED_SIMULATION:64 |
| hesp_la_guard | 72 | 0.931 | 4.60 | 4.49 | 3.72 | 5935 | 132 | DECISION_BUDGET_EXCEEDED:5, VERIFIED_SIMULATION:67 |
| hesp_random | 72 | 0.889 | 5.25 | 5 | 4.74 | 7804 | 150 | UNVERIFIED_CLAIM:8, VERIFIED_SIMULATION:64 |
| hesp_llmp | 72 | 0.833 | 4.03 | 3.65 | 2.76 | 4213 | 96 | UNVERIFIED_CLAIM:12, VERIFIED_SIMULATION:60 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| hesp_la_guard_minus_memory_only | 24 | +0.111 | [+0.028, +0.222] | 4 / 0 | +0.39 | [-0.625, +1.458] |
| hesp_la_guard_minus_react_style | 24 | +0.125 | [+0.028, +0.250] | 4 / 0 | +0.35 | [-0.667, +1.431] |
| memory_only_minus_react_style | 24 | +0.014 | [+0.000, +0.042] | 1 / 0 | -0.04 | [-0.208, +0.125] |
| hesp_eigc_minus_memory_only | 24 | +0.097 | [+0.000, +0.222] | 3 / 0 | -1.15 | [-1.917, -0.431] |
| hesp_eigc_guard_minus_hesp_eigc | 24 | +0.083 | [+0.000, +0.208] | 2 / 0 | +0.25 | [+0.000, +0.625] |
| memory_guard_minus_memory_only | 24 | +0.028 | [+0.000, +0.069] | 2 / 0 | +0.24 | [+0.000, +0.569] |
| hesp_la_guard_minus_memory_guard | 24 | +0.083 | [+0.000, +0.181] | 4 / 1 | +0.15 | [-0.764, +1.069] |
| hesp_la_minus_hesp_eigc | 24 | -0.028 | [-0.139, +0.069] | 1 / 2 | +1.38 | [+0.792, +2.000] |
| hesp_eigc_minus_hesp_random | 24 | +0.028 | [-0.125, +0.153] | 7 / 2 | -2.19 | [-2.806, -1.556] |
| hesp_eigc_minus_hesp_llmp | 24 | +0.083 | [+0.014, +0.181] | 4 / 0 | -0.97 | [-1.583, -0.444] |

All failures remain in the denominator; unknown usage stays null.
