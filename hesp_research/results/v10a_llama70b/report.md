# v1.0 part A · llama-3.1-70b-instruct-awq · sigma-triage

Paired local-sandbox study. Intervals are over task clusters of a small, hand-built suite; they do not generalize to real websites or Web CTF.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| memory_only | 152 | 0.783 | 7.91 | 7.50 | 7.14 | 10601 | 217 | STOPPED_UNRESOLVED:1, TOOL_BUDGET_EXCEEDED:30, UNVERIFIED_CLAIM:2, VERIFIED_SIMULATION:119 |
| memory_only_autostop | 152 | 0.941 | 2.76 | 2.58 | 2.49 | 3258 | 70 | UNVERIFIED_CLAIM:9, VERIFIED_SIMULATION:143 |
| hesp_eigc_blind | 152 | 0.954 | 8.65 | 8.59 | 8.51 | 13114 | 249 | UNVERIFIED_CLAIM:7, VERIFIED_SIMULATION:145 |
| hesp_eigc_blind_autostop | 152 | 1.000 | 2.20 | 2.20 | 2.20 | 2873 | 59 | VERIFIED_SIMULATION:152 |
| hesp_random_blind_autostop | 152 | 0.895 | 4.27 | 4.15 | 2.79 | 3743 | 74 | UNVERIFIED_CLAIM:16, VERIFIED_SIMULATION:136 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| hesp_eigc_blind_autostop_minus_hesp_random_blind_autostop | 76 | +0.105 | [+0.059, +0.164] | 14 / 0 | -2.07 | [-2.368, -1.789] |
| hesp_eigc_blind_autostop_minus_memory_only | 76 | +0.217 | [+0.138, +0.296] | 24 / 0 | -5.71 | [-6.158, -5.257] |
| hesp_eigc_blind_autostop_minus_hesp_eigc_blind | 76 | +0.046 | [+0.007, +0.099] | 4 / 0 | -6.45 | [-6.829, -6.066] |
| hesp_eigc_blind_autostop_minus_memory_only_autostop | 76 | +0.059 | [+0.013, +0.118] | 5 / 0 | -0.57 | [-0.941, -0.283] |
| memory_only_autostop_minus_memory_only | 76 | +0.158 | [+0.086, +0.230] | 19 / 1 | -5.14 | [-5.618, -4.671] |

All failures remain in the denominator; unknown usage stays null.
