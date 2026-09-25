# v0.4 · qwen2.5-32b-instruct-awq · web-diag

Fixture repetitions are deterministic; intervals are pipeline checks, not efficacy evidence.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| react_style | 72 | 0.681 | 4.04 | 4.04 | 4.46 | 5264 | 148 | UNVERIFIED_CLAIM:23, VERIFIED_SIMULATION:49 |
| memory_only | 72 | 0.889 | 3.67 | 3.41 | 4.42 | 6162 | 145 | UNVERIFIED_CLAIM:8, VERIFIED_SIMULATION:64 |
| memory_guard | 72 | 0.944 | 3.92 | 3.75 | 4.88 | 6959 | 167 | DECISION_BUDGET_EXCEEDED:4, VERIFIED_SIMULATION:68 |
| hesp_eigc | 72 | 0.764 | 3.86 | 3.73 | 3.25 | 4991 | 113 | UNVERIFIED_CLAIM:17, VERIFIED_SIMULATION:55 |
| hesp_eigc_guard | 72 | 0.972 | 4.86 | 4.71 | 4.43 | 7115 | 158 | DECISION_BUDGET_EXCEEDED:1, UNVERIFIED_CLAIM:1, VERIFIED_SIMULATION:70 |
| hesp_la | 72 | 0.972 | 3.64 | 3.54 | 2.50 | 3739 | 91 | UNVERIFIED_CLAIM:2, VERIFIED_SIMULATION:70 |
| hesp_la_guard | 72 | 0.972 | 3.72 | 3.54 | 2.67 | 4089 | 99 | DECISION_BUDGET_EXCEEDED:1, STOPPED_UNRESOLVED:1, VERIFIED_SIMULATION:70 |
| hesp_random | 72 | 0.903 | 5.24 | 5.12 | 5.15 | 8282 | 169 | UNVERIFIED_CLAIM:7, VERIFIED_SIMULATION:65 |
| hesp_llmp | 72 | 0.931 | 5.10 | 5.10 | 5.40 | 8738 | 177 | UNVERIFIED_CLAIM:5, VERIFIED_SIMULATION:67 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| hesp_la_guard_minus_memory_only | 24 | +0.083 | [-0.014, +0.194] | 5 / 2 | +0.06 | [-0.597, +0.736] |
| hesp_la_guard_minus_react_style | 24 | +0.292 | [+0.125, +0.472] | 10 / 1 | -0.32 | [-1.083, +0.472] |
| memory_only_minus_react_style | 24 | +0.208 | [+0.069, +0.361] | 9 / 1 | -0.38 | [-1.125, +0.389] |
| hesp_eigc_minus_memory_only | 24 | -0.125 | [-0.278, +0.000] | 2 / 5 | +0.19 | [-0.292, +0.722] |
| hesp_eigc_guard_minus_hesp_eigc | 24 | +0.208 | [+0.069, +0.375] | 6 / 0 | +1.00 | [+0.347, +1.778] |
| memory_guard_minus_memory_only | 24 | +0.056 | [+0.014, +0.111] | 4 / 0 | +0.25 | [+0.014, +0.542] |
| hesp_la_guard_minus_memory_guard | 24 | +0.028 | [-0.042, +0.111] | 3 / 2 | -0.19 | [-1.014, +0.597] |
| hesp_la_minus_hesp_eigc | 24 | +0.208 | [+0.056, +0.389] | 7 / 2 | -0.22 | [-0.889, +0.417] |
| hesp_eigc_minus_hesp_random | 24 | -0.139 | [-0.319, +0.014] | 4 / 6 | -1.38 | [-2.111, -0.667] |
| hesp_eigc_minus_hesp_llmp | 24 | -0.167 | [-0.319, -0.028] | 1 / 6 | -1.24 | [-2.167, -0.319] |

All failures remain in the denominator; unknown usage stays null.
