# v1.0 part A · llama-3.1-8b-instruct · sigma-triage

Paired local-sandbox study. Intervals are over task clusters of a small, hand-built suite; they do not generalize to real websites or Web CTF.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| memory_only | 152 | 0.000 | 9.88 | n/a | 9.40 | 14450 | 329 | TOOL_BUDGET_EXCEEDED:152 |
| memory_only_autostop | 152 | 0.921 | 2.89 | 2.84 | 2.61 | 3409 | 94 | UNVERIFIED_CLAIM:12, VERIFIED_SIMULATION:140 |
| hesp_eigc_blind | 152 | 0.007 | 9.78 | 10 | 9.16 | 14246 | 346 | NO_LEGAL_ACTION:33, TOOL_BUDGET_EXCEEDED:118, VERIFIED_SIMULATION:1 |
| hesp_eigc_blind_autostop | 152 | 1.000 | 2.20 | 2.20 | 2.20 | 2873 | 83 | VERIFIED_SIMULATION:152 |
| hesp_random_blind_autostop | 152 | 0.895 | 4.27 | 4.15 | 2.79 | 3743 | 105 | TOOL_BUDGET_EXCEEDED:1, UNVERIFIED_CLAIM:15, VERIFIED_SIMULATION:136 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| hesp_eigc_blind_autostop_minus_hesp_random_blind_autostop | 76 | +0.105 | [+0.059, +0.164] | 14 / 0 | -2.07 | [-2.368, -1.789] |
| hesp_eigc_blind_autostop_minus_memory_only | 76 | +1.000 | [+1.000, +1.000] | 76 / 0 | -7.68 | [-7.796, -7.546] |
| hesp_eigc_blind_autostop_minus_hesp_eigc_blind | 76 | +0.993 | [+0.980, +1.000] | 76 / 0 | -7.59 | [-7.717, -7.447] |
| hesp_eigc_blind_autostop_minus_memory_only_autostop | 76 | +0.079 | [+0.033, +0.145] | 8 / 0 | -0.69 | [-0.987, -0.454] |
| memory_only_autostop_minus_memory_only | 76 | +0.921 | [+0.855, +0.967] | 72 / 0 | -6.99 | [-7.257, -6.671] |

All failures remain in the denominator; unknown usage stays null.
