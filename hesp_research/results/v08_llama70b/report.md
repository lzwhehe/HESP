# v0.8 · llama-3.1-70b-instruct-awq · sec-triage

Paired local-sandbox study. Intervals are over task clusters of a small, hand-built suite; they do not generalize to real websites or Web CTF.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| memory_only | 72 | 0.833 | 8.64 | 8.62 | 8.06 | 12445 | 226 | TOOL_BUDGET_EXCEEDED:11, UNVERIFIED_CLAIM:1, VERIFIED_SIMULATION:60 |
| hesp_random_blind | 72 | 0.736 | 9.86 | 9.81 | 8.08 | 12759 | 221 | UNVERIFIED_CLAIM:19, VERIFIED_SIMULATION:53 |
| hesp_eigc_blind | 72 | 1.000 | 9.14 | 9.14 | 8.94 | 14240 | 243 | VERIFIED_SIMULATION:72 |
| hesp_eigc | 72 | 1.000 | 9.36 | 9.36 | 9.17 | 15974 | 261 | VERIFIED_SIMULATION:72 |
| hesp_eigc_guard | 72 | 1.000 | 9.36 | 9.36 | 9.17 | 15974 | 261 | VERIFIED_SIMULATION:72 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| hesp_eigc_guard_minus_memory_only | 24 | +0.167 | [+0.056, +0.292] | 7 / 0 | +0.72 | [+0.319, +1.264] |
| hesp_eigc_blind_minus_hesp_random_blind | 24 | +0.264 | [+0.139, +0.403] | 11 / 0 | -0.72 | [-1.375, -0.236] |
| hesp_random_blind_minus_memory_only | 24 | -0.097 | [-0.278, +0.056] | 4 / 8 | +1.22 | [+0.694, +1.861] |
| hesp_eigc_minus_hesp_eigc_blind | 24 | +0.000 | [+0.000, +0.000] | 0 / 0 | +0.22 | [+0.069, +0.431] |
| hesp_eigc_guard_minus_hesp_eigc | 24 | +0.000 | [+0.000, +0.000] | 0 / 0 | +0.00 | [+0.000, +0.000] |

## Security-facing metrics (descriptive only; PROTOCOL.md v0.6)

A guard that refuses an unsupported claim lowers the missed-attack rate by producing no claim at all; read these together with the unresolved rate.

| Arm | Episodes with a claim | Unresolved | Missed attack | False escalation | Wrong cause | Citation validity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| memory_only | 61 / 72 | 0.167 | 0.021 | 0 | 0.016 | 0.978 |
| hesp_random_blind | 72 / 72 | 0.264 | 0.259 | 0 | 0.194 | 0.968 |
| hesp_eigc_blind | 72 / 72 | 0 | 0 | 0 | 0 | 1.000 |
| hesp_eigc | 72 / 72 | 0 | 0 | 0 | 0 | 1.000 |
| hesp_eigc_guard | 72 / 72 | 0 | 0 | 0 | 0 | 1.000 |

All failures remain in the denominator; unknown usage stays null.
