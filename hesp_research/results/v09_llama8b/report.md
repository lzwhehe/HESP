# v0.9 · llama-3.1-8b-instruct · sec-triage

Paired local-sandbox study. Intervals are over task clusters of a small, hand-built suite; they do not generalize to real websites or Web CTF.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| memory_only | 72 | 0.000 | 9.72 | n/a | 10.07 | 16011 | 337 | TOOL_BUDGET_EXCEEDED:72 |
| memory_only_autostop | 72 | 0.861 | 4.78 | 4.13 | 5.28 | 7699 | 180 | TOOL_BUDGET_EXCEEDED:1, UNVERIFIED_CLAIM:9, VERIFIED_SIMULATION:62 |
| hesp_eigc_blind | 72 | 0.000 | 10 | n/a | 9.57 | 15410 | 360 | TOOL_BUDGET_EXCEEDED:72 |
| hesp_eigc_blind_autostop | 72 | 0.917 | 2.35 | 2.18 | 2.35 | 3205 | 87 | UNVERIFIED_CLAIM:6, VERIFIED_SIMULATION:66 |
| hesp_random_blind_autostop | 72 | 0.750 | 6.43 | 5.44 | 4.79 | 7098 | 176 | TOOL_BUDGET_EXCEEDED:8, UNVERIFIED_CLAIM:10, VERIFIED_SIMULATION:54 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| hesp_eigc_blind_autostop_minus_hesp_eigc_blind | 24 | +0.917 | [+0.792, +1.000] | 22 / 0 | -7.65 | [-8.194, -7.125] |
| hesp_eigc_blind_autostop_minus_memory_only_autostop | 24 | +0.056 | [-0.056, +0.167] | 4 / 2 | -2.43 | [-3.333, -1.597] |
| memory_only_autostop_minus_memory_only | 24 | +0.861 | [+0.750, +0.958] | 24 / 0 | -4.94 | [-6.042, -3.819] |
| hesp_eigc_blind_autostop_minus_hesp_random_blind_autostop | 24 | +0.167 | [+0.042, +0.292] | 12 / 2 | -4.08 | [-4.653, -3.486] |
| hesp_eigc_blind_minus_memory_only | 24 | +0.000 | [+0.000, +0.000] | 0 / 0 | +0.28 | [+0.153, +0.403] |

## Security-facing metrics (descriptive only; PROTOCOL.md v0.6)

A guard that refuses an unsupported claim lowers the missed-attack rate by producing no claim at all; read these together with the unresolved rate.

| Arm | Episodes with a claim | Unresolved | Missed attack | False escalation | Wrong cause | Citation validity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| memory_only | 0 / 72 | 1 | n/a | n/a | n/a | n/a |
| memory_only_autostop | 71 / 72 | 0.139 | 0 | 0 | 0 | 1.000 |
| hesp_eigc_blind | 0 / 72 | 1 | n/a | n/a | n/a | n/a |
| hesp_eigc_blind_autostop | 72 / 72 | 0.083 | 0 | 0 | 0 | 1.000 |
| hesp_random_blind_autostop | 64 / 72 | 0.250 | 0 | 0 | 0 | 1.000 |

All failures remain in the denominator; unknown usage stays null.
