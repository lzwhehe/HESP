# v0.4 · qwen2.5-72b-instruct-awq · web-diag

Fixture repetitions are deterministic; intervals are pipeline checks, not efficacy evidence.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| react_style | 72 | 0.750 | 3.78 | 3.50 | 4.17 | 4890 | 145 | UNVERIFIED_CLAIM:18, VERIFIED_SIMULATION:54 |
| memory_only | 72 | 0.806 | 4.07 | 3.78 | 4.93 | 6982 | 165 | UNVERIFIED_CLAIM:14, VERIFIED_SIMULATION:58 |
| memory_guard | 72 | 0.944 | 4.44 | 4.12 | 5.36 | 7747 | 182 | DECISION_BUDGET_EXCEEDED:2, TOOL_BUDGET_EXCEEDED:1, UNVERIFIED_CLAIM:1, VERIFIED_SIMULATION:68 |
| hesp_eigc | 72 | 0.806 | 3.36 | 3.10 | 3.06 | 4678 | 105 | UNVERIFIED_CLAIM:14, VERIFIED_SIMULATION:58 |
| hesp_eigc_guard | 72 | 0.806 | 3.36 | 3.10 | 4.69 | 7638 | 175 | DECISION_BUDGET_EXCEEDED:13, UNVERIFIED_CLAIM:1, VERIFIED_SIMULATION:58 |
| hesp_la | 72 | 0.972 | 3.64 | 3.54 | 2.50 | 3739 | 90 | UNVERIFIED_CLAIM:2, VERIFIED_SIMULATION:70 |
| hesp_la_guard | 72 | 0.972 | 3.64 | 3.54 | 2.64 | 3983 | 95 | DECISION_BUDGET_EXCEEDED:1, TOOL_BUDGET_EXCEEDED:1, VERIFIED_SIMULATION:70 |
| hesp_random | 72 | 0.875 | 4.90 | 4.95 | 4.90 | 7832 | 170 | UNVERIFIED_CLAIM:9, VERIFIED_SIMULATION:63 |
| hesp_llmp | 72 | 0.958 | 3.97 | 4.06 | 3.92 | 6098 | 131 | UNVERIFIED_CLAIM:3, VERIFIED_SIMULATION:69 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| hesp_la_guard_minus_memory_only | 24 | +0.167 | [+0.042, +0.333] | 5 / 1 | -0.43 | [-1.222, +0.306] |
| hesp_la_guard_minus_react_style | 24 | +0.222 | [+0.083, +0.361] | 10 / 1 | -0.14 | [-0.847, +0.528] |
| memory_only_minus_react_style | 24 | +0.056 | [-0.083, +0.181] | 5 / 2 | +0.29 | [-0.083, +0.736] |
| hesp_eigc_minus_memory_only | 24 | -0.000 | [-0.167, +0.153] | 4 / 3 | -0.71 | [-1.417, -0.069] |
| hesp_eigc_guard_minus_hesp_eigc | 24 | +0.000 | [+0.000, +0.000] | 0 / 0 | +0.00 | [+0.000, +0.000] |
| memory_guard_minus_memory_only | 24 | +0.139 | [+0.028, +0.278] | 4 / 0 | +0.38 | [+0.069, +0.792] |
| hesp_la_guard_minus_memory_guard | 24 | +0.028 | [-0.042, +0.111] | 3 / 2 | -0.81 | [-1.806, +0.069] |
| hesp_la_minus_hesp_eigc | 24 | +0.167 | [+0.014, +0.333] | 6 / 2 | +0.28 | [-0.486, +1.097] |
| hesp_eigc_minus_hesp_random | 24 | -0.069 | [-0.222, +0.069] | 4 / 5 | -1.54 | [-2.444, -0.722] |
| hesp_eigc_minus_hesp_llmp | 24 | -0.153 | [-0.306, -0.014] | 1 / 5 | -0.61 | [-1.889, +0.611] |

All failures remain in the denominator; unknown usage stays null.
