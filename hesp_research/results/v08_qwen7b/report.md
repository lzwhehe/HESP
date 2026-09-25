# v0.8 · qwen2.5-7b-instruct · sec-triage

Paired local-sandbox study. Intervals are over task clusters of a small, hand-built suite; they do not generalize to real websites or Web CTF.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| memory_only | 72 | 0.083 | 9.46 | 9.83 | 10.18 | 16907 | 299 | DECISION_BUDGET_EXCEEDED:13, TOOL_BUDGET_EXCEEDED:52, UNVERIFIED_CLAIM:1, VERIFIED_SIMULATION:6 |
| hesp_random_blind | 72 | 0.639 | 9.26 | 9.26 | 7.58 | 12542 | 244 | TOOL_BUDGET_EXCEEDED:1, UNVERIFIED_CLAIM:25, VERIFIED_SIMULATION:46 |
| hesp_eigc_blind | 72 | 0.944 | 7.32 | 7.25 | 7.78 | 12694 | 246 | UNVERIFIED_CLAIM:4, VERIFIED_SIMULATION:68 |
| hesp_eigc | 72 | 1.000 | 9.44 | 9.44 | 9.19 | 17019 | 275 | VERIFIED_SIMULATION:72 |
| hesp_eigc_guard | 72 | 1.000 | 9.44 | 9.44 | 9.19 | 17019 | 275 | VERIFIED_SIMULATION:72 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| hesp_eigc_guard_minus_memory_only | 24 | +0.917 | [+0.833, +0.986] | 24 / 0 | -0.01 | [-0.556, +0.444] |
| hesp_eigc_blind_minus_hesp_random_blind | 24 | +0.306 | [+0.167, +0.458] | 14 / 1 | -1.94 | [-2.583, -1.347] |
| hesp_random_blind_minus_memory_only | 24 | +0.556 | [+0.403, +0.708] | 19 / 0 | -0.19 | [-0.556, +0.167] |
| hesp_eigc_minus_hesp_eigc_blind | 24 | +0.056 | [+0.000, +0.153] | 2 / 0 | +2.12 | [+1.611, +2.653] |
| hesp_eigc_guard_minus_hesp_eigc | 24 | +0.000 | [+0.000, +0.000] | 0 / 0 | +0.00 | [+0.000, +0.000] |

## Security-facing metrics (descriptive only; PROTOCOL.md v0.6)

A guard that refuses an unsupported claim lowers the missed-attack rate by producing no claim at all; read these together with the unresolved rate.

| Arm | Episodes with a claim | Unresolved | Missed attack | False escalation | Wrong cause | Citation validity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| memory_only | 7 / 72 | 0.917 | 0.143 | n/a | 0.143 | 0.929 |
| hesp_random_blind | 71 / 72 | 0.361 | 0.189 | 0.167 | 0.239 | 0.852 |
| hesp_eigc_blind | 72 / 72 | 0.056 | 0.074 | 0 | 0.056 | 0.968 |
| hesp_eigc | 72 / 72 | 0 | 0 | 0 | 0 | 1.000 |
| hesp_eigc_guard | 72 / 72 | 0 | 0 | 0 | 0 | 1.000 |

All failures remain in the denominator; unknown usage stays null.
