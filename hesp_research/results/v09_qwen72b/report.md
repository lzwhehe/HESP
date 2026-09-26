# v0.9 · qwen2.5-72b-instruct-awq · sec-triage

Paired local-sandbox study. Intervals are over task clusters of a small, hand-built suite; they do not generalize to real websites or Web CTF.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| memory_only | 72 | 0.861 | 5.61 | 5.06 | 5.76 | 8920 | 197 | TOOL_BUDGET_EXCEEDED:1, UNVERIFIED_CLAIM:9, VERIFIED_SIMULATION:62 |
| memory_only_autostop | 72 | 0.833 | 4.11 | 3.50 | 3.94 | 5864 | 123 | UNVERIFIED_CLAIM:12, VERIFIED_SIMULATION:60 |
| hesp_eigc_blind | 72 | 0.917 | 3.57 | 3.71 | 4.47 | 6719 | 143 | UNVERIFIED_CLAIM:6, VERIFIED_SIMULATION:66 |
| hesp_eigc_blind_autostop | 72 | 0.875 | 2.31 | 2.14 | 2.35 | 3365 | 65 | UNVERIFIED_CLAIM:9, VERIFIED_SIMULATION:63 |
| hesp_random_blind_autostop | 72 | 0.694 | 5.44 | 4.30 | 4.36 | 6728 | 134 | UNVERIFIED_CLAIM:22, VERIFIED_SIMULATION:50 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| hesp_eigc_blind_autostop_minus_hesp_eigc_blind | 24 | -0.042 | [-0.167, +0.083] | 1 / 2 | -1.26 | [-1.917, -0.708] |
| hesp_eigc_blind_autostop_minus_memory_only_autostop | 24 | +0.042 | [-0.083, +0.167] | 2 / 1 | -1.81 | [-2.625, -1.069] |
| memory_only_autostop_minus_memory_only | 24 | -0.028 | [-0.125, +0.042] | 1 / 1 | -1.50 | [-2.069, -0.986] |
| hesp_eigc_blind_autostop_minus_hesp_random_blind_autostop | 24 | +0.181 | [+0.042, +0.319] | 13 / 3 | -3.14 | [-3.722, -2.569] |
| hesp_eigc_blind_minus_memory_only | 24 | +0.056 | [-0.125, +0.236] | 4 / 2 | -2.04 | [-2.833, -1.264] |

## Security-facing metrics (descriptive only; PROTOCOL.md v0.6)

A guard that refuses an unsupported claim lowers the missed-attack rate by producing no claim at all; read these together with the unresolved rate.

| Arm | Episodes with a claim | Unresolved | Missed attack | False escalation | Wrong cause | Citation validity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| memory_only | 71 / 72 | 0.139 | 0.019 | 0 | 0.056 | 0.995 |
| memory_only_autostop | 72 / 72 | 0.167 | 0 | 0 | 0.042 | 1.000 |
| hesp_eigc_blind | 72 / 72 | 0.083 | 0.059 | 0.143 | 0.083 | 0.917 |
| hesp_eigc_blind_autostop | 72 / 72 | 0.125 | 0 | 0.143 | 0.042 | 0.958 |
| hesp_random_blind_autostop | 72 / 72 | 0.306 | 0.151 | 0 | 0.153 | 0.961 |

All failures remain in the denominator; unknown usage stays null.
