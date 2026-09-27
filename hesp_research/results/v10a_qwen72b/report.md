# v1.0 part A · qwen2.5-72b-instruct-awq · sigma-triage

Paired local-sandbox study. Intervals are over task clusters of a small, hand-built suite; they do not generalize to real websites or Web CTF.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| memory_only | 152 | 0.895 | 4.51 | 4.33 | 4.88 | 7700 | 205 | TOOL_BUDGET_EXCEEDED:2, UNVERIFIED_CLAIM:14, VERIFIED_SIMULATION:136 |
| memory_only_autostop | 152 | 0.914 | 2.49 | 2.30 | 2.41 | 3393 | 85 | UNVERIFIED_CLAIM:13, VERIFIED_SIMULATION:139 |
| hesp_eigc_blind | 152 | 0.974 | 3.02 | 2.92 | 4.01 | 6115 | 162 | UNVERIFIED_CLAIM:4, VERIFIED_SIMULATION:148 |
| hesp_eigc_blind_autostop | 152 | 1.000 | 2.17 | 2.17 | 2.20 | 3037 | 72 | VERIFIED_SIMULATION:152 |
| hesp_random_blind_autostop | 152 | 0.770 | 3.55 | 3.37 | 2.62 | 3689 | 89 | UNVERIFIED_CLAIM:35, VERIFIED_SIMULATION:117 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| hesp_eigc_blind_autostop_minus_hesp_random_blind_autostop | 76 | +0.230 | [+0.158, +0.309] | 29 / 0 | -1.38 | [-1.638, -1.138] |
| hesp_eigc_blind_autostop_minus_memory_only | 76 | +0.105 | [+0.046, +0.178] | 10 / 0 | -2.34 | [-2.658, -2.046] |
| hesp_eigc_blind_autostop_minus_hesp_eigc_blind | 76 | +0.026 | [+0.000, +0.066] | 2 / 0 | -0.85 | [-1.132, -0.612] |
| hesp_eigc_blind_autostop_minus_memory_only_autostop | 76 | +0.086 | [+0.026, +0.158] | 7 / 0 | -0.32 | [-0.526, -0.158] |
| memory_only_autostop_minus_memory_only | 76 | +0.020 | [+0.000, +0.046] | 3 / 0 | -2.02 | [-2.375, -1.691] |

All failures remain in the denominator; unknown usage stays null.
