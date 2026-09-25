# v0.4 · qwen2.5-32b-instruct-awq · upload-diag

Fixture repetitions are deterministic; intervals are pipeline checks, not efficacy evidence.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| react_style | 72 | 0.875 | 5.38 | 5.24 | 5.75 | 7294 | 180 | TOOL_BUDGET_EXCEEDED:3, UNVERIFIED_CLAIM:6, VERIFIED_SIMULATION:63 |
| memory_only | 72 | 0.944 | 5.19 | 4.97 | 5.82 | 8775 | 185 | UNVERIFIED_CLAIM:4, VERIFIED_SIMULATION:68 |
| memory_guard | 72 | 0.958 | 5.21 | 5.04 | 5.85 | 8831 | 186 | UNVERIFIED_CLAIM:3, VERIFIED_SIMULATION:69 |
| hesp_eigc | 72 | 0.875 | 3.60 | 3.68 | 3.44 | 5353 | 120 | UNVERIFIED_CLAIM:9, VERIFIED_SIMULATION:63 |
| hesp_eigc_guard | 72 | 1.000 | 4.18 | 4.18 | 4.15 | 6627 | 146 | VERIFIED_SIMULATION:72 |
| hesp_la | 72 | 0.819 | 5.68 | 5.54 | 3.32 | 5140 | 116 | UNVERIFIED_CLAIM:13, VERIFIED_SIMULATION:59 |
| hesp_la_guard | 72 | 0.944 | 6.21 | 6.04 | 4.11 | 6531 | 147 | DECISION_BUDGET_EXCEEDED:1, UNVERIFIED_CLAIM:3, VERIFIED_SIMULATION:68 |
| hesp_random | 72 | 0.889 | 5.69 | 5.50 | 5.06 | 8393 | 162 | UNVERIFIED_CLAIM:8, VERIFIED_SIMULATION:64 |
| hesp_llmp | 72 | 0.806 | 5.61 | 5.64 | 5.29 | 8800 | 171 | UNVERIFIED_CLAIM:14, VERIFIED_SIMULATION:58 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| hesp_la_guard_minus_memory_only | 24 | +0.000 | [-0.125, +0.125] | 2 / 2 | +1.01 | [+0.125, +1.861] |
| hesp_la_guard_minus_react_style | 24 | +0.069 | [-0.083, +0.222] | 4 / 2 | +0.83 | [-0.194, +1.889] |
| memory_only_minus_react_style | 24 | +0.069 | [+0.000, +0.167] | 3 / 0 | -0.18 | [-0.542, +0.222] |
| hesp_eigc_minus_memory_only | 24 | -0.069 | [-0.236, +0.097] | 2 / 3 | -1.60 | [-2.486, -0.778] |
| hesp_eigc_guard_minus_hesp_eigc | 24 | +0.125 | [+0.000, +0.250] | 3 / 0 | +0.58 | [+0.000, +1.292] |
| memory_guard_minus_memory_only | 24 | +0.014 | [+0.000, +0.042] | 1 / 0 | +0.01 | [+0.000, +0.042] |
| hesp_la_guard_minus_memory_guard | 24 | -0.014 | [-0.139, +0.111] | 1 / 2 | +1.00 | [+0.125, +1.833] |
| hesp_la_minus_hesp_eigc | 24 | -0.056 | [-0.194, +0.069] | 2 / 3 | +2.08 | [+1.417, +2.750] |
| hesp_eigc_minus_hesp_random | 24 | -0.014 | [-0.153, +0.111] | 5 / 3 | -2.10 | [-2.778, -1.444] |
| hesp_eigc_minus_hesp_llmp | 24 | +0.069 | [-0.069, +0.222] | 4 / 1 | -2.01 | [-2.986, -1.069] |

All failures remain in the denominator; unknown usage stays null.
