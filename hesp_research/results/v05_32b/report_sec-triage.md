# v0.4 · qwen2.5-32b-instruct-awq · sec-triage

Fixture repetitions are deterministic; intervals are pipeline checks, not efficacy evidence.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| react_style | 72 | 0.597 | 5.50 | 4.86 | 5.75 | 7746 | 205 | TOOL_BUDGET_EXCEEDED:3, UNVERIFIED_CLAIM:26, VERIFIED_SIMULATION:43 |
| memory_only | 72 | 0.750 | 5.39 | 4.54 | 5.60 | 8688 | 190 | UNVERIFIED_CLAIM:18, VERIFIED_SIMULATION:54 |
| memory_guard | 72 | 0.792 | 5.49 | 4.54 | 6.18 | 9842 | 216 | DECISION_BUDGET_EXCEEDED:8, TOOL_BUDGET_EXCEEDED:2, UNVERIFIED_CLAIM:5, VERIFIED_SIMULATION:57 |
| hesp_eigc | 72 | 1.000 | 4.29 | 4.29 | 4.79 | 8135 | 166 | VERIFIED_SIMULATION:72 |
| hesp_eigc_guard | 72 | 1.000 | 4.29 | 4.29 | 4.79 | 8135 | 166 | VERIFIED_SIMULATION:72 |
| hesp_la | 72 | 0.972 | 5.58 | 5.46 | 4.88 | 8236 | 168 | UNVERIFIED_CLAIM:2, VERIFIED_SIMULATION:70 |
| hesp_la_guard | 72 | 0.972 | 5.58 | 5.46 | 4.88 | 8236 | 168 | UNVERIFIED_CLAIM:2, VERIFIED_SIMULATION:70 |
| hesp_random | 72 | 0.736 | 8.49 | 7.96 | 7.03 | 12793 | 246 | UNVERIFIED_CLAIM:19, VERIFIED_SIMULATION:53 |
| hesp_llmp | 72 | 1.000 | 8.99 | 8.99 | 8.69 | 16135 | 294 | VERIFIED_SIMULATION:72 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| hesp_la_guard_minus_memory_only | 24 | +0.222 | [+0.083, +0.375] | 8 / 0 | +0.19 | [-0.917, +1.236] |
| hesp_la_guard_minus_react_style | 24 | +0.375 | [+0.194, +0.556] | 11 / 0 | +0.08 | [-0.944, +1.069] |
| memory_only_minus_react_style | 24 | +0.153 | [+0.028, +0.306] | 4 / 0 | -0.11 | [-0.611, +0.389] |
| hesp_eigc_minus_memory_only | 24 | +0.250 | [+0.097, +0.417] | 8 / 0 | -1.10 | [-2.111, -0.222] |
| hesp_eigc_guard_minus_hesp_eigc | 24 | +0.000 | [+0.000, +0.000] | 0 / 0 | +0.00 | [+0.000, +0.000] |
| memory_guard_minus_memory_only | 24 | +0.042 | [+0.000, +0.125] | 1 / 0 | +0.10 | [-0.083, +0.333] |
| hesp_la_guard_minus_memory_guard | 24 | +0.181 | [+0.056, +0.319] | 7 / 0 | +0.10 | [-1.028, +1.111] |
| hesp_la_minus_hesp_eigc | 24 | -0.028 | [-0.083, +0.000] | 0 / 1 | +1.29 | [+0.667, +1.972] |
| hesp_eigc_minus_hesp_random | 24 | +0.264 | [+0.139, +0.403] | 11 / 0 | -4.19 | [-4.958, -3.472] |
| hesp_eigc_minus_hesp_llmp | 24 | +0.000 | [+0.000, +0.000] | 0 / 0 | -4.69 | [-5.708, -3.764] |

All failures remain in the denominator; unknown usage stays null.
