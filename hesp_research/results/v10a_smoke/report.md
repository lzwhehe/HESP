# v1.0 part A · qwen2.5-7b-instruct · sigma-triage

Paired local-sandbox study. Intervals are over task clusters of a small, hand-built suite; they do not generalize to real websites or Web CTF.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| memory_only | 4 | 1.000 | 4.25 | 4.25 | 4.75 | 7858 | 193 | VERIFIED_SIMULATION:4 |
| memory_only_autostop | 4 | 1.000 | 2.25 | 2.25 | 2.25 | 3038 | 73 | VERIFIED_SIMULATION:4 |
| hesp_eigc_blind | 4 | 1.000 | 2.75 | 2.75 | 3.75 | 5905 | 150 | VERIFIED_SIMULATION:4 |
| hesp_eigc_blind_autostop | 4 | 1.000 | 1.75 | 1.75 | 2 | 2735 | 62 | VERIFIED_SIMULATION:4 |
| hesp_random_blind_autostop | 4 | 1.000 | 3 | 3 | 2.25 | 3102 | 75 | VERIFIED_SIMULATION:4 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| hesp_eigc_blind_autostop_minus_hesp_random_blind_autostop | 4 | +0.000 | [+0.000, +0.000] | 0 / 0 | -1.25 | [-3.000, +0.500] |
| hesp_eigc_blind_autostop_minus_memory_only | 4 | +0.000 | [+0.000, +0.000] | 0 / 0 | -2.50 | [-4.000, -1.000] |
| hesp_eigc_blind_autostop_minus_hesp_eigc_blind | 4 | +0.000 | [+0.000, +0.000] | 0 / 0 | -1.00 | [-2.250, +0.000] |
| hesp_eigc_blind_autostop_minus_memory_only_autostop | 4 | +0.000 | [+0.000, +0.000] | 0 / 0 | -0.50 | [-1.000, +0.000] |
| memory_only_autostop_minus_memory_only | 4 | +0.000 | [+0.000, +0.000] | 0 / 0 | -2.00 | [-4.000, +0.000] |

All failures remain in the denominator; unknown usage stays null.
