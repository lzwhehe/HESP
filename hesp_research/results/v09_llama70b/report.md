# v0.9 · llama-3.1-70b-instruct-awq · sec-triage

Paired local-sandbox study. Intervals are over task clusters of a small, hand-built suite; they do not generalize to real websites or Web CTF.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| memory_only | 72 | 0.889 | 8.56 | 8.52 | 7.97 | 12276 | 223 | TOOL_BUDGET_EXCEEDED:8, VERIFIED_SIMULATION:64 |
| memory_only_autostop | 72 | 0.889 | 4.42 | 3.95 | 4.18 | 5976 | 107 | TOOL_BUDGET_EXCEEDED:1, UNVERIFIED_CLAIM:7, VERIFIED_SIMULATION:64 |
| hesp_eigc_blind | 72 | 1.000 | 9.04 | 9.04 | 8.83 | 14046 | 241 | VERIFIED_SIMULATION:72 |
| hesp_eigc_blind_autostop | 72 | 0.917 | 2.35 | 2.18 | 2.35 | 3205 | 59 | UNVERIFIED_CLAIM:6, VERIFIED_SIMULATION:66 |
| hesp_random_blind_autostop | 72 | 0.750 | 6.43 | 5.44 | 4.79 | 7098 | 122 | UNVERIFIED_CLAIM:18, VERIFIED_SIMULATION:54 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| hesp_eigc_blind_autostop_minus_hesp_eigc_blind | 24 | -0.083 | [-0.208, +0.000] | 0 / 2 | -6.69 | [-7.403, -5.931] |
| hesp_eigc_blind_autostop_minus_memory_only_autostop | 24 | +0.028 | [-0.097, +0.153] | 3 / 2 | -2.07 | [-2.861, -1.361] |
| memory_only_autostop_minus_memory_only | 24 | +0.000 | [-0.139, +0.139] | 5 / 4 | -4.14 | [-5.097, -3.167] |
| hesp_eigc_blind_autostop_minus_hesp_random_blind_autostop | 24 | +0.167 | [+0.042, +0.292] | 12 / 2 | -4.08 | [-4.653, -3.486] |
| hesp_eigc_blind_minus_memory_only | 24 | +0.111 | [+0.028, +0.208] | 5 / 0 | +0.49 | [+0.125, +0.903] |

## Security-facing metrics (descriptive only; PROTOCOL.md v0.6)

A guard that refuses an unsupported claim lowers the missed-attack rate by producing no claim at all; read these together with the unresolved rate.

| Arm | Episodes with a claim | Unresolved | Missed attack | False escalation | Wrong cause | Citation validity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| memory_only | 64 / 72 | 0.111 | 0 | 0 | 0 | 0.992 |
| memory_only_autostop | 71 / 72 | 0.111 | 0 | 0 | 0 | 1.000 |
| hesp_eigc_blind | 72 / 72 | 0 | 0 | 0 | 0 | 1.000 |
| hesp_eigc_blind_autostop | 72 / 72 | 0.083 | 0 | 0 | 0 | 1.000 |
| hesp_random_blind_autostop | 72 / 72 | 0.250 | 0.094 | 0 | 0.069 | 0.986 |

All failures remain in the denominator; unknown usage stays null.
