# v0.4 · qwen2.5-72b-instruct-awq · sec-triage

Fixture repetitions are deterministic; intervals are pipeline checks, not efficacy evidence.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| react_style | 72 | 0.597 | 5.81 | 5.91 | 5.99 | 7920 | 212 | UNVERIFIED_CLAIM:29, VERIFIED_SIMULATION:43 |
| memory_only | 72 | 0.889 | 5.75 | 5.34 | 5.86 | 9136 | 200 | TOOL_BUDGET_EXCEEDED:1, UNVERIFIED_CLAIM:7, VERIFIED_SIMULATION:64 |
| memory_guard | 72 | 0.889 | 5.71 | 5.30 | 5.94 | 9305 | 203 | TOOL_BUDGET_EXCEEDED:8, VERIFIED_SIMULATION:64 |
| hesp_eigc | 72 | 1.000 | 4.57 | 4.57 | 4.93 | 8353 | 174 | VERIFIED_SIMULATION:72 |
| hesp_eigc_guard | 72 | 1.000 | 4.62 | 4.62 | 4.99 | 8454 | 175 | VERIFIED_SIMULATION:72 |
| hesp_la | 72 | 0.958 | 6.53 | 6.41 | 5.56 | 9483 | 194 | UNVERIFIED_CLAIM:3, VERIFIED_SIMULATION:69 |
| hesp_la_guard | 72 | 0.958 | 6.53 | 6.41 | 5.57 | 9510 | 194 | UNVERIFIED_CLAIM:3, VERIFIED_SIMULATION:69 |
| hesp_random | 72 | 0.736 | 8.83 | 8.42 | 7.29 | 13095 | 252 | UNVERIFIED_CLAIM:19, VERIFIED_SIMULATION:53 |
| hesp_llmp | 72 | 0.986 | 7.96 | 7.93 | 7.71 | 13841 | 263 | UNVERIFIED_CLAIM:1, VERIFIED_SIMULATION:71 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| hesp_la_guard_minus_memory_only | 24 | +0.069 | [+0.000, +0.181] | 2 / 0 | +0.78 | [-0.208, +1.708] |
| hesp_la_guard_minus_react_style | 24 | +0.361 | [+0.194, +0.556] | 11 / 1 | +0.72 | [-0.278, +1.694] |
| memory_only_minus_react_style | 24 | +0.292 | [+0.097, +0.500] | 10 / 1 | -0.06 | [-0.722, +0.569] |
| hesp_eigc_minus_memory_only | 24 | +0.111 | [+0.000, +0.236] | 3 / 0 | -1.18 | [-2.167, -0.375] |
| hesp_eigc_guard_minus_hesp_eigc | 24 | +0.000 | [+0.000, +0.000] | 0 / 0 | +0.06 | [+0.000, +0.167] |
| memory_guard_minus_memory_only | 24 | +0.000 | [+0.000, +0.000] | 0 / 0 | -0.04 | [-0.125, +0.000] |
| hesp_la_guard_minus_memory_guard | 24 | +0.069 | [+0.000, +0.181] | 2 / 0 | +0.82 | [-0.167, +1.750] |
| hesp_la_minus_hesp_eigc | 24 | -0.042 | [-0.097, +0.000] | 0 / 2 | +1.96 | [+1.319, +2.611] |
| hesp_eigc_minus_hesp_random | 24 | +0.264 | [+0.139, +0.403] | 11 / 0 | -4.26 | [-4.986, -3.542] |
| hesp_eigc_minus_hesp_llmp | 24 | +0.014 | [+0.000, +0.042] | 1 / 0 | -3.39 | [-4.264, -2.597] |

All failures remain in the denominator; unknown usage stays null.
