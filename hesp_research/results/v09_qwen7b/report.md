# v0.9 · qwen2.5-7b-instruct · sec-triage

Paired local-sandbox study. Intervals are over task clusters of a small, hand-built suite; they do not generalize to real websites or Web CTF.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| memory_only | 72 | 0.083 | 9.50 | 9.33 | 10.04 | 16652 | 295 | DECISION_BUDGET_EXCEEDED:13, TOOL_BUDGET_EXCEEDED:53, VERIFIED_SIMULATION:6 |
| memory_only_autostop | 72 | 0.694 | 5.18 | 3.58 | 5.58 | 8546 | 162 | DECISION_BUDGET_EXCEEDED:1, TOOL_BUDGET_EXCEEDED:5, UNVERIFIED_CLAIM:16, VERIFIED_SIMULATION:50 |
| hesp_eigc_blind | 72 | 0.931 | 7.19 | 7.13 | 7.65 | 12508 | 242 | UNVERIFIED_CLAIM:5, VERIFIED_SIMULATION:67 |
| hesp_eigc_blind_autostop | 72 | 0.917 | 2.35 | 2.18 | 2.35 | 3365 | 72 | UNVERIFIED_CLAIM:6, VERIFIED_SIMULATION:66 |
| hesp_random_blind_autostop | 72 | 0.736 | 6.42 | 5.36 | 4.79 | 7468 | 146 | UNVERIFIED_CLAIM:19, VERIFIED_SIMULATION:53 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| hesp_eigc_blind_autostop_minus_hesp_eigc_blind | 24 | -0.014 | [-0.167, +0.125] | 3 / 2 | -4.85 | [-5.569, -4.153] |
| hesp_eigc_blind_autostop_minus_memory_only_autostop | 24 | +0.222 | [+0.083, +0.389] | 6 / 0 | -2.83 | [-3.806, -1.944] |
| memory_only_autostop_minus_memory_only | 24 | +0.611 | [+0.431, +0.778] | 16 / 0 | -4.32 | [-5.500, -3.139] |
| hesp_eigc_blind_autostop_minus_hesp_random_blind_autostop | 24 | +0.181 | [+0.056, +0.306] | 13 / 2 | -4.07 | [-4.653, -3.472] |
| hesp_eigc_blind_minus_memory_only | 24 | +0.847 | [+0.708, +0.958] | 22 / 0 | -2.31 | [-3.139, -1.542] |

## Security-facing metrics (descriptive only; PROTOCOL.md v0.6)

A guard that refuses an unsupported claim lowers the missed-attack rate by producing no claim at all; read these together with the unresolved rate.

| Arm | Episodes with a claim | Unresolved | Missed attack | False escalation | Wrong cause | Citation validity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| memory_only | 6 / 72 | 0.917 | 0 | 0 | 0 | 1.000 |
| memory_only_autostop | 66 / 72 | 0.306 | 0 | 0 | 0 | 1.000 |
| hesp_eigc_blind | 72 / 72 | 0.069 | 0.074 | 0 | 0.069 | 0.951 |
| hesp_eigc_blind_autostop | 72 / 72 | 0.083 | 0 | 0 | 0 | 1.000 |
| hesp_random_blind_autostop | 72 / 72 | 0.264 | 0.075 | 0 | 0.069 | 0.984 |

All failures remain in the denominator; unknown usage stays null.
