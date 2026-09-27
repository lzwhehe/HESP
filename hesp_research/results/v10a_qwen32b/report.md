# v1.0 part A · qwen2.5-32b-instruct-awq · sigma-triage

Paired local-sandbox study. Intervals are over task clusters of a small, hand-built suite; they do not generalize to real websites or Web CTF.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| memory_only | 152 | 0.954 | 5.36 | 5.26 | 5.39 | 8998 | 240 | TOOL_BUDGET_EXCEEDED:1, UNVERIFIED_CLAIM:6, VERIFIED_SIMULATION:145 |
| memory_only_autostop | 152 | 0.934 | 2.74 | 2.58 | 2.44 | 3348 | 82 | UNVERIFIED_CLAIM:10, VERIFIED_SIMULATION:142 |
| hesp_eigc_blind | 152 | 0.947 | 5.24 | 5.17 | 6.06 | 10569 | 271 | UNVERIFIED_CLAIM:8, VERIFIED_SIMULATION:144 |
| hesp_eigc_blind_autostop | 152 | 1.000 | 2.20 | 2.20 | 2.20 | 3037 | 73 | VERIFIED_SIMULATION:152 |
| hesp_random_blind_autostop | 152 | 0.836 | 4.07 | 3.86 | 2.75 | 3944 | 96 | UNVERIFIED_CLAIM:25, VERIFIED_SIMULATION:127 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| hesp_eigc_blind_autostop_minus_hesp_random_blind_autostop | 76 | +0.164 | [+0.105, +0.224] | 22 / 0 | -1.87 | [-2.145, -1.612] |
| hesp_eigc_blind_autostop_minus_memory_only | 76 | +0.046 | [+0.013, +0.092] | 5 / 0 | -3.16 | [-3.566, -2.796] |
| hesp_eigc_blind_autostop_minus_hesp_eigc_blind | 76 | +0.053 | [+0.013, +0.105] | 4 / 0 | -3.05 | [-3.500, -2.632] |
| hesp_eigc_blind_autostop_minus_memory_only_autostop | 76 | +0.066 | [+0.020, +0.125] | 6 / 0 | -0.54 | [-0.862, -0.296] |
| memory_only_autostop_minus_memory_only | 76 | -0.020 | [-0.059, +0.013] | 2 / 4 | -2.62 | [-3.026, -2.243] |

All failures remain in the denominator; unknown usage stays null.
