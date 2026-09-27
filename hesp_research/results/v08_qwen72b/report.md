# v0.8 · qwen2.5-72b-instruct-awq · sec-triage

Paired local-sandbox study. Intervals are over task clusters of a small, hand-built suite; they do not generalize to real websites or Web CTF.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| memory_only | 72 | 0.847 | 5.74 | 5.15 | 5.89 | 9137 | 200 | TOOL_BUDGET_EXCEEDED:1, UNVERIFIED_CLAIM:10, VERIFIED_SIMULATION:61 |
| hesp_random_blind | 72 | 0.569 | 6.36 | 5.66 | 5.56 | 8839 | 185 | UNVERIFIED_CLAIM:31, VERIFIED_SIMULATION:41 |
| hesp_eigc_blind | 72 | 0.917 | 3.61 | 3.76 | 4.51 | 6804 | 144 | UNVERIFIED_CLAIM:6, VERIFIED_SIMULATION:66 |
| hesp_eigc | 72 | 0.958 | 5.08 | 5.22 | 5.83 | 10200 | 199 | UNVERIFIED_CLAIM:3, VERIFIED_SIMULATION:69 |
| hesp_eigc_guard | 72 | 1.000 | 5.33 | 5.33 | 6.08 | 10689 | 207 | VERIFIED_SIMULATION:72 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| hesp_eigc_guard_minus_memory_only | 24 | +0.153 | [+0.042, +0.292] | 5 / 0 | -0.40 | [-1.181, +0.500] |
| hesp_eigc_blind_minus_hesp_random_blind | 24 | +0.347 | [+0.181, +0.500] | 16 / 2 | -2.75 | [-3.653, -1.903] |
| hesp_random_blind_minus_memory_only | 24 | -0.278 | [-0.431, -0.125] | 3 / 14 | +0.62 | [-0.264, +1.528] |
| hesp_eigc_minus_hesp_eigc_blind | 24 | +0.042 | [-0.083, +0.208] | 2 / 1 | +1.47 | [+0.917, +2.042] |
| hesp_eigc_guard_minus_hesp_eigc | 24 | +0.042 | [+0.000, +0.125] | 1 / 0 | +0.25 | [+0.000, +0.750] |

## Security-facing metrics (descriptive only; PROTOCOL.md v0.6)

A guard that refuses an unsupported claim lowers the missed-attack rate by producing no claim at all; read these together with the unresolved rate.

| Arm | Episodes with a claim | Unresolved | Missed attack | False escalation | Wrong cause | Citation validity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| memory_only | 71 / 72 | 0.153 | 0 | 0 | 0.056 | 0.986 |
| hesp_random_blind | 72 / 72 | 0.431 | 0.236 | 0.118 | 0.278 | 0.907 |
| hesp_eigc_blind | 72 / 72 | 0.083 | 0.059 | 0.143 | 0.083 | 0.917 |
| hesp_eigc | 72 / 72 | 0.042 | 0.056 | 0 | 0.042 | 0.958 |
| hesp_eigc_guard | 72 / 72 | 0 | 0 | 0 | 0 | 1.000 |

All failures remain in the denominator; unknown usage stays null.
