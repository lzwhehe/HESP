# v0.4 · qwen2.5-7b-instruct · web-diag

Fixture repetitions are deterministic; intervals are pipeline checks, not efficacy evidence.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| react_style | 72 | 0.444 | 2.79 | 2.66 | 3.76 | 4627 | 139 | UNVERIFIED_CLAIM:40, VERIFIED_SIMULATION:32 |
| memory_only | 72 | 0.639 | 3.53 | 3.57 | 3.94 | 5466 | 133 | UNVERIFIED_CLAIM:26, VERIFIED_SIMULATION:46 |
| memory_guard | 72 | 0.750 | 4.18 | 4.02 | 6.57 | 9999 | 258 | DECISION_BUDGET_EXCEEDED:18, VERIFIED_SIMULATION:54 |
| hesp_eigc | 72 | 0.750 | 4.01 | 3.80 | 3.40 | 5258 | 110 | UNVERIFIED_CLAIM:18, VERIFIED_SIMULATION:54 |
| hesp_eigc_guard | 72 | 0.819 | 4.24 | 4.10 | 5.14 | 8395 | 183 | DECISION_BUDGET_EXCEEDED:13, VERIFIED_SIMULATION:59 |
| hesp_la | 72 | 0.958 | 4.04 | 3.78 | 2.88 | 4401 | 96 | UNVERIFIED_CLAIM:3, VERIFIED_SIMULATION:69 |
| hesp_la_guard | 72 | 0.972 | 4.04 | 3.87 | 3.03 | 4682 | 105 | DECISION_BUDGET_EXCEEDED:2, VERIFIED_SIMULATION:70 |
| hesp_random | 72 | 0.889 | 5.61 | 5.34 | 5.42 | 8698 | 177 | UNVERIFIED_CLAIM:8, VERIFIED_SIMULATION:64 |
| hesp_llmp | 72 | 1.000 | 4.08 | 4.08 | 2.92 | 4470 | 100 | VERIFIED_SIMULATION:72 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| hesp_la_guard_minus_memory_only | 24 | +0.333 | [+0.167, +0.500] | 11 / 0 | +0.51 | [-0.139, +1.153] |
| hesp_la_guard_minus_react_style | 24 | +0.528 | [+0.333, +0.722] | 14 / 0 | +1.25 | [+0.722, +1.847] |
| memory_only_minus_react_style | 24 | +0.194 | [+0.069, +0.333] | 8 / 1 | +0.74 | [+0.194, +1.292] |
| hesp_eigc_minus_memory_only | 24 | +0.111 | [-0.083, +0.292] | 8 / 2 | +0.49 | [-0.125, +1.153] |
| hesp_eigc_guard_minus_hesp_eigc | 24 | +0.069 | [+0.000, +0.181] | 2 / 0 | +0.22 | [+0.000, +0.556] |
| memory_guard_minus_memory_only | 24 | +0.111 | [+0.028, +0.194] | 6 / 0 | +0.65 | [+0.208, +1.208] |
| hesp_la_guard_minus_memory_guard | 24 | +0.222 | [+0.097, +0.347] | 11 / 1 | -0.14 | [-0.875, +0.597] |
| hesp_la_minus_hesp_eigc | 24 | +0.208 | [+0.056, +0.389] | 7 / 2 | +0.03 | [-0.722, +0.750] |
| hesp_eigc_minus_hesp_random | 24 | -0.139 | [-0.319, +0.028] | 5 / 6 | -1.60 | [-2.153, -1.083] |
| hesp_eigc_minus_hesp_llmp | 24 | -0.250 | [-0.417, -0.097] | 0 / 8 | -0.07 | [-0.819, +0.708] |

All failures remain in the denominator; unknown usage stays null.
