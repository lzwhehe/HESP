# v0.8 · qwen2.5:7b-instruct · sec-triage

Paired local-sandbox study. Intervals are over task clusters of a small, hand-built suite; they do not generalize to real websites or Web CTF.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| memory_only | 2 | 0.000 | 6.50 | n/a | 12 | 32018 | 330 | DECISION_BUDGET_EXCEEDED:2 |
| hesp_random_blind | 2 | 1.000 | 10 | 10 | 9.50 | 25647 | 290 | VERIFIED_SIMULATION:2 |
| hesp_eigc_blind | 2 | 0.500 | 9.50 | 10 | 9 | 26504 | 284 | UNVERIFIED_CLAIM:1, VERIFIED_SIMULATION:1 |
| hesp_eigc | 2 | 0.500 | 10 | 10 | 9.50 | 27256 | 277 | UNVERIFIED_CLAIM:1, VERIFIED_SIMULATION:1 |
| hesp_eigc_guard | 2 | 0.500 | 10 | 10 | 10.50 | 34358 | 372 | DECISION_BUDGET_EXCEEDED:1, VERIFIED_SIMULATION:1 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| hesp_eigc_guard_minus_memory_only | 2 | +0.500 | [+0.000, +1.000] | 1 / 0 | +3.50 | [+2.000, +5.000] |
| hesp_eigc_blind_minus_hesp_random_blind | 2 | -0.500 | [-1.000, +0.000] | 0 / 1 | -0.50 | [-1.000, +0.000] |
| hesp_random_blind_minus_memory_only | 2 | +1.000 | [+1.000, +1.000] | 2 / 0 | +3.50 | [+2.000, +5.000] |
| hesp_eigc_minus_hesp_eigc_blind | 2 | +0.000 | [+0.000, +0.000] | 0 / 0 | +0.50 | [+0.000, +1.000] |
| hesp_eigc_guard_minus_hesp_eigc | 2 | +0.000 | [+0.000, +0.000] | 0 / 0 | +0.00 | [+0.000, +0.000] |

## Security-facing metrics (descriptive only; PROTOCOL.md v0.6)

A guard that refuses an unsupported claim lowers the missed-attack rate by producing no claim at all; read these together with the unresolved rate.

| Arm | Episodes with a claim | Unresolved | Missed attack | False escalation | Wrong cause | Citation validity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| memory_only | 0 / 2 | 1 | n/a | n/a | n/a | n/a |
| hesp_random_blind | 2 / 2 | 0 | 0 | n/a | 0 | 1.000 |
| hesp_eigc_blind | 2 / 2 | 0.500 | 0.500 | n/a | 0.500 | 0.750 |
| hesp_eigc | 2 / 2 | 0.500 | 0.500 | n/a | 0.500 | 0.750 |
| hesp_eigc_guard | 1 / 2 | 0.500 | 0 | n/a | 0 | 1.000 |

All failures remain in the denominator; unknown usage stays null.
