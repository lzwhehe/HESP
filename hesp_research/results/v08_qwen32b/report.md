# v0.8 · qwen2.5-32b-instruct-awq · sec-triage

Paired local-sandbox study. Intervals are over task clusters of a small, hand-built suite; they do not generalize to real websites or Web CTF.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| memory_only | 72 | 0.875 | 5.44 | 5.03 | 5.67 | 8766 | 192 | UNVERIFIED_CLAIM:9, VERIFIED_SIMULATION:63 |
| hesp_random_blind | 72 | 0.653 | 8.10 | 7.74 | 6.69 | 11143 | 237 | UNVERIFIED_CLAIM:25, VERIFIED_SIMULATION:47 |
| hesp_eigc_blind | 72 | 1.000 | 5.57 | 5.57 | 6.24 | 10032 | 212 | VERIFIED_SIMULATION:72 |
| hesp_eigc | 72 | 1.000 | 6.11 | 6.11 | 6.79 | 12218 | 230 | VERIFIED_SIMULATION:72 |
| hesp_eigc_guard | 72 | 1.000 | 6.11 | 6.11 | 6.79 | 12218 | 230 | VERIFIED_SIMULATION:72 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| hesp_eigc_guard_minus_memory_only | 24 | +0.125 | [+0.028, +0.250] | 5 / 0 | +0.67 | [-0.111, +1.528] |
| hesp_eigc_blind_minus_hesp_random_blind | 24 | +0.347 | [+0.222, +0.486] | 15 / 0 | -2.53 | [-3.250, -1.806] |
| hesp_random_blind_minus_memory_only | 24 | -0.222 | [-0.375, -0.083] | 4 / 13 | +2.65 | [+2.097, +3.181] |
| hesp_eigc_minus_hesp_eigc_blind | 24 | +0.000 | [+0.000, +0.000] | 0 / 0 | +0.54 | [+0.264, +0.833] |
| hesp_eigc_guard_minus_hesp_eigc | 24 | +0.000 | [+0.000, +0.000] | 0 / 0 | +0.00 | [+0.000, +0.000] |

## Security-facing metrics (descriptive only; PROTOCOL.md v0.6)

A guard that refuses an unsupported claim lowers the missed-attack rate by producing no claim at all; read these together with the unresolved rate.

| Arm | Episodes with a claim | Unresolved | Missed attack | False escalation | Wrong cause | Citation validity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| memory_only | 72 / 72 | 0.125 | 0.019 | 0 | 0.069 | 0.972 |
| hesp_random_blind | 72 / 72 | 0.347 | 0.259 | 0.056 | 0.236 | 0.907 |
| hesp_eigc_blind | 72 / 72 | 0 | 0 | 0 | 0 | 1.000 |
| hesp_eigc | 72 / 72 | 0 | 0 | 0 | 0 | 1.000 |
| hesp_eigc_guard | 72 / 72 | 0 | 0 | 0 | 0 | 1.000 |

All failures remain in the denominator; unknown usage stays null.
