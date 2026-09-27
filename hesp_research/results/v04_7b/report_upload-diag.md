# v0.4 · qwen2.5-7b-instruct · upload-diag

Fixture repetitions are deterministic; intervals are pipeline checks, not efficacy evidence.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| react_style | 72 | 0.194 | 1.25 | 1.71 | 2.12 | 3419 | 92 | UNVERIFIED_CLAIM:58, VERIFIED_SIMULATION:14 |
| memory_only | 72 | 0.236 | 1 | 1 | 2 | 4804 | 112 | UNVERIFIED_CLAIM:55, VERIFIED_SIMULATION:17 |
| memory_guard | 72 | 0.236 | 1.03 | 1 | 9.56 | 16950 | 413 | DECISION_BUDGET_EXCEEDED:54, PLANNER_ERROR:1, VERIFIED_SIMULATION:17 |
| hesp_eigc | 72 | 1.000 | 3.35 | 3.35 | 3.15 | 4884 | 102 | VERIFIED_SIMULATION:72 |
| hesp_eigc_guard | 72 | 1.000 | 3.35 | 3.35 | 3.15 | 4884 | 103 | VERIFIED_SIMULATION:72 |
| hesp_la | 72 | 0.875 | 4.40 | 4.13 | 2.82 | 4313 | 93 | UNVERIFIED_CLAIM:9, VERIFIED_SIMULATION:63 |
| hesp_la_guard | 72 | 0.861 | 4.40 | 4.08 | 4.01 | 6482 | 145 | DECISION_BUDGET_EXCEEDED:10, VERIFIED_SIMULATION:62 |
| hesp_random | 72 | 0.847 | 6.43 | 6.20 | 5.49 | 9118 | 168 | UNVERIFIED_CLAIM:11, VERIFIED_SIMULATION:61 |
| hesp_llmp | 72 | 0.792 | 5.40 | 4.93 | 3.21 | 4935 | 104 | UNVERIFIED_CLAIM:15, VERIFIED_SIMULATION:57 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| hesp_la_guard_minus_memory_only | 24 | +0.625 | [+0.444, +0.792] | 17 / 0 | +3.40 | [+2.500, +4.361] |
| hesp_la_guard_minus_react_style | 24 | +0.667 | [+0.486, +0.833] | 18 / 0 | +3.15 | [+2.125, +4.222] |
| memory_only_minus_react_style | 24 | +0.042 | [+0.000, +0.125] | 1 / 0 | -0.25 | [-0.500, +0.000] |
| hesp_eigc_minus_memory_only | 24 | +0.764 | [+0.583, +0.917] | 19 / 0 | +2.35 | [+1.806, +2.958] |
| hesp_eigc_guard_minus_hesp_eigc | 24 | +0.000 | [+0.000, +0.000] | 0 / 0 | +0.00 | [+0.000, +0.000] |
| memory_guard_minus_memory_only | 24 | +0.000 | [+0.000, +0.000] | 0 / 0 | +0.03 | [+0.000, +0.083] |
| hesp_la_guard_minus_memory_guard | 24 | +0.625 | [+0.444, +0.792] | 17 / 0 | +3.38 | [+2.486, +4.319] |
| hesp_la_minus_hesp_eigc | 24 | -0.125 | [-0.250, -0.028] | 0 / 5 | +1.06 | [+0.583, +1.611] |
| hesp_eigc_minus_hesp_random | 24 | +0.153 | [+0.083, +0.236] | 10 / 0 | -3.08 | [-3.750, -2.389] |
| hesp_eigc_minus_hesp_llmp | 24 | +0.208 | [+0.083, +0.347] | 9 / 0 | -2.06 | [-2.861, -1.333] |

All failures remain in the denominator; unknown usage stays null.
