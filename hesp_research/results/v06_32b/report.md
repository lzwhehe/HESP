# v0.6 RQ3 · qwen2.5-32b-instruct-awq · sec-triage

Paired local-sandbox study. Intervals are over task clusters of a small, hand-built suite; they do not generalize to real websites or Web CTF.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| react_style | 72 | 0.611 | 5.50 | 4.82 | 5.75 | 7746 | 205 | TOOL_BUDGET_EXCEEDED:3, UNVERIFIED_CLAIM:25, VERIFIED_SIMULATION:44 |
| memory_only | 72 | 0.750 | 5.39 | 4.54 | 5.60 | 8688 | 190 | UNVERIFIED_CLAIM:18, VERIFIED_SIMULATION:54 |
| hesp_eigc_guard_designer | 72 | 1.000 | 3.67 | 3.67 | 4.42 | 7498 | 153 | VERIFIED_SIMULATION:72 |
| hesp_eigc_guard_emp1 | 72 | 0.986 | 6.40 | 6.37 | 6.97 | 12574 | 237 | DECISION_BUDGET_EXCEEDED:1, VERIFIED_SIMULATION:71 |
| hesp_eigc_guard_emp5 | 72 | 1.000 | 6.11 | 6.11 | 6.79 | 12218 | 230 | VERIFIED_SIMULATION:72 |
| hesp_eigc_guard_emp20 | 72 | 1.000 | 6.11 | 6.11 | 6.79 | 12218 | 230 | VERIFIED_SIMULATION:72 |
| hesp_eigc_guard_emp100 | 72 | 1.000 | 6.11 | 6.11 | 6.79 | 12218 | 230 | VERIFIED_SIMULATION:72 |
| hesp_eigc_guard_llmp | 72 | 0.375 | 9.01 | 7.37 | 10.33 | 19676 | 367 | DECISION_BUDGET_EXCEEDED:45, VERIFIED_SIMULATION:27 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| hesp_eigc_guard_emp20_minus_memory_only | 24 | +0.250 | [+0.097, +0.417] | 8 / 0 | +0.72 | [-0.222, +1.681] |
| hesp_eigc_guard_emp1_minus_memory_only | 24 | +0.236 | [+0.069, +0.417] | 8 / 1 | +1.01 | [-0.097, +2.194] |
| hesp_eigc_guard_emp5_minus_memory_only | 24 | +0.250 | [+0.097, +0.417] | 8 / 0 | +0.72 | [-0.222, +1.681] |
| hesp_eigc_guard_emp100_minus_memory_only | 24 | +0.250 | [+0.097, +0.417] | 8 / 0 | +0.72 | [-0.222, +1.681] |
| hesp_eigc_guard_designer_minus_hesp_eigc_guard_emp20 | 24 | +0.000 | [+0.000, +0.000] | 0 / 0 | -2.44 | [-3.472, -1.472] |
| hesp_eigc_guard_emp20_minus_hesp_eigc_guard_llmp | 24 | +0.625 | [+0.417, +0.833] | 15 / 0 | -2.90 | [-3.708, -2.167] |
| hesp_eigc_guard_designer_minus_memory_only | 24 | +0.250 | [+0.097, +0.417] | 8 / 0 | -1.72 | [-2.569, -1.042] |
| memory_only_minus_react_style | 24 | +0.139 | [+0.028, +0.278] | 4 / 0 | -0.11 | [-0.611, +0.389] |

## Security-facing metrics (descriptive only; PROTOCOL.md v0.6)

A guard that refuses an unsupported claim lowers the missed-attack rate by producing no claim at all; read these together with the unresolved rate.

| Arm | Episodes with a claim | Unresolved | Missed attack | False escalation | Wrong cause | Citation validity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| react_style | 69 / 72 | 0.389 | 0.216 | 0.167 | 0.391 | 0.778 |
| memory_only | 72 / 72 | 0.250 | 0.093 | 0.333 | 0.333 | 0.940 |
| hesp_eigc_guard_designer | 72 / 72 | 0 | 0.111 | 0.167 | 0.292 | 1.000 |
| hesp_eigc_guard_emp1 | 71 / 72 | 0.014 | 0.113 | 0.333 | 0.338 | 1.000 |
| hesp_eigc_guard_emp5 | 72 / 72 | 0 | 0.111 | 0.333 | 0.333 | 1.000 |
| hesp_eigc_guard_emp20 | 72 / 72 | 0 | 0.111 | 0.333 | 0.333 | 1.000 |
| hesp_eigc_guard_emp100 | 72 / 72 | 0 | 0.111 | 0.333 | 0.333 | 1.000 |
| hesp_eigc_guard_llmp | 27 / 72 | 0.625 | 0.400 | 0 | 0.333 | 1.000 |

All failures remain in the denominator; unknown usage stays null.

Primary endpoint (pre-registered): hesp_eigc_guard_emp20 - memory_only.
