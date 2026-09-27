# v0.9 · qwen2.5-32b-instruct-awq · sec-triage

Paired local-sandbox study. Intervals are over task clusters of a small, hand-built suite; they do not generalize to real websites or Web CTF.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| memory_only | 72 | 0.903 | 5.22 | 4.89 | 5.53 | 8451 | 187 | UNVERIFIED_CLAIM:7, VERIFIED_SIMULATION:65 |
| memory_only_autostop | 72 | 0.819 | 4.06 | 3.39 | 3.90 | 5782 | 119 | UNVERIFIED_CLAIM:13, VERIFIED_SIMULATION:59 |
| hesp_eigc_blind | 72 | 1.000 | 5.49 | 5.49 | 6.15 | 9891 | 211 | VERIFIED_SIMULATION:72 |
| hesp_eigc_blind_autostop | 72 | 0.917 | 2.35 | 2.18 | 2.35 | 3365 | 68 | UNVERIFIED_CLAIM:6, VERIFIED_SIMULATION:66 |
| hesp_random_blind_autostop | 72 | 0.708 | 6.04 | 4.84 | 4.62 | 7387 | 153 | UNVERIFIED_CLAIM:21, VERIFIED_SIMULATION:51 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| hesp_eigc_blind_autostop_minus_hesp_eigc_blind | 24 | -0.083 | [-0.208, +0.000] | 0 / 2 | -3.14 | [-4.208, -2.181] |
| hesp_eigc_blind_autostop_minus_memory_only_autostop | 24 | +0.097 | [+0.000, +0.222] | 3 / 0 | -1.71 | [-2.444, -1.042] |
| memory_only_autostop_minus_memory_only | 24 | -0.083 | [-0.194, +0.000] | 0 / 3 | -1.17 | [-1.667, -0.708] |
| hesp_eigc_blind_autostop_minus_hesp_random_blind_autostop | 24 | +0.208 | [+0.069, +0.333] | 14 / 2 | -3.69 | [-4.264, -3.125] |
| hesp_eigc_blind_minus_memory_only | 24 | +0.097 | [+0.000, +0.222] | 3 / 0 | +0.26 | [-0.444, +1.111] |

## Security-facing metrics (descriptive only; PROTOCOL.md v0.6)

A guard that refuses an unsupported claim lowers the missed-attack rate by producing no claim at all; read these together with the unresolved rate.

| Arm | Episodes with a claim | Unresolved | Missed attack | False escalation | Wrong cause | Citation validity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| memory_only | 72 / 72 | 0.097 | 0 | 0 | 0.056 | 0.965 |
| memory_only_autostop | 72 / 72 | 0.181 | 0 | 0 | 0.069 | 0.986 |
| hesp_eigc_blind | 72 / 72 | 0 | 0 | 0 | 0 | 1.000 |
| hesp_eigc_blind_autostop | 72 / 72 | 0.083 | 0 | 0 | 0 | 1.000 |
| hesp_random_blind_autostop | 72 / 72 | 0.292 | 0.135 | 0 | 0.139 | 0.979 |

All failures remain in the denominator; unknown usage stays null.
