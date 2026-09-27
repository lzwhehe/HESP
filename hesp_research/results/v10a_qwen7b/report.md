# v1.0 part A · qwen2.5-7b-instruct · sigma-triage

Paired local-sandbox study. Intervals are over task clusters of a small, hand-built suite; they do not generalize to real websites or Web CTF.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| memory_only | 152 | 0.678 | 5.23 | 5.27 | 5.12 | 8691 | 214 | PLANNER_ERROR:18, TOOL_BUDGET_EXCEEDED:4, UNVERIFIED_CLAIM:27, VERIFIED_SIMULATION:103 |
| memory_only_autostop | 152 | 0.862 | 2.76 | 2.79 | 2.52 | 3471 | 80 | PLANNER_ERROR:4, UNVERIFIED_CLAIM:17, VERIFIED_SIMULATION:131 |
| hesp_eigc_blind | 152 | 0.882 | 2.98 | 2.96 | 3.97 | 6195 | 153 | PLANNER_ERROR:1, UNVERIFIED_CLAIM:17, VERIFIED_SIMULATION:134 |
| hesp_eigc_blind_autostop | 152 | 0.974 | 2.07 | 2.09 | 2.19 | 3057 | 67 | UNVERIFIED_CLAIM:4, VERIFIED_SIMULATION:148 |
| hesp_random_blind_autostop | 152 | 0.803 | 3.73 | 3.80 | 2.63 | 3739 | 83 | UNVERIFIED_CLAIM:30, VERIFIED_SIMULATION:122 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| hesp_eigc_blind_autostop_minus_hesp_random_blind_autostop | 76 | +0.171 | [+0.105, +0.237] | 24 / 2 | -1.66 | [-1.914, -1.408] |
| hesp_eigc_blind_autostop_minus_memory_only | 76 | +0.296 | [+0.191, +0.401] | 32 / 2 | -3.16 | [-3.625, -2.711] |
| hesp_eigc_blind_autostop_minus_hesp_eigc_blind | 76 | +0.092 | [+0.033, +0.158] | 8 / 0 | -0.91 | [-1.164, -0.691] |
| hesp_eigc_blind_autostop_minus_memory_only_autostop | 76 | +0.112 | [+0.033, +0.197] | 14 / 2 | -0.68 | [-0.928, -0.461] |
| memory_only_autostop_minus_memory_only | 76 | +0.184 | [+0.118, +0.257] | 22 / 0 | -2.47 | [-2.961, -2.033] |

All failures remain in the denominator; unknown usage stays null.
