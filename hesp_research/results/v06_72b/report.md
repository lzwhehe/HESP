# v0.6 RQ3 · qwen2.5-72b-instruct-awq · sec-triage

Paired local-sandbox study. Intervals are over task clusters of a small, hand-built suite; they do not generalize to real websites or Web CTF.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| react_style | 72 | 0.597 | 5.79 | 5.98 | 5.97 | 7900 | 212 | UNVERIFIED_CLAIM:29, VERIFIED_SIMULATION:43 |
| memory_only | 72 | 0.889 | 5.71 | 5.30 | 5.85 | 9109 | 199 | TOOL_BUDGET_EXCEEDED:1, UNVERIFIED_CLAIM:7, VERIFIED_SIMULATION:64 |
| hesp_eigc_guard_designer | 72 | 1.000 | 4.12 | 4.12 | 4.75 | 8147 | 167 | VERIFIED_SIMULATION:72 |
| hesp_eigc_guard_emp1 | 72 | 1.000 | 5.36 | 5.36 | 6.11 | 10742 | 208 | VERIFIED_SIMULATION:72 |
| hesp_eigc_guard_emp5 | 72 | 1.000 | 5.32 | 5.32 | 6.07 | 10659 | 207 | VERIFIED_SIMULATION:72 |
| hesp_eigc_guard_emp20 | 72 | 1.000 | 5.33 | 5.33 | 6.08 | 10689 | 208 | VERIFIED_SIMULATION:72 |
| hesp_eigc_guard_emp100 | 72 | 1.000 | 5.33 | 5.33 | 6.08 | 10689 | 208 | VERIFIED_SIMULATION:72 |
| hesp_eigc_guard_llmp | 72 | 0.375 | 8.39 | 5.70 | 10.01 | 19036 | 370 | DECISION_BUDGET_EXCEEDED:45, VERIFIED_SIMULATION:27 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| hesp_eigc_guard_emp20_minus_memory_only | 24 | +0.111 | [+0.000, +0.236] | 3 / 0 | -0.38 | [-1.278, +0.597] |
| hesp_eigc_guard_emp1_minus_memory_only | 24 | +0.111 | [+0.000, +0.236] | 3 / 0 | -0.35 | [-1.250, +0.625] |
| hesp_eigc_guard_emp5_minus_memory_only | 24 | +0.111 | [+0.000, +0.236] | 3 / 0 | -0.39 | [-1.292, +0.583] |
| hesp_eigc_guard_emp100_minus_memory_only | 24 | +0.111 | [+0.000, +0.236] | 3 / 0 | -0.38 | [-1.278, +0.597] |
| hesp_eigc_guard_designer_minus_hesp_eigc_guard_emp20 | 24 | +0.000 | [+0.000, +0.000] | 0 / 0 | -1.21 | [-2.042, -0.514] |
| hesp_eigc_guard_emp20_minus_hesp_eigc_guard_llmp | 24 | +0.625 | [+0.417, +0.833] | 15 / 0 | -3.06 | [-4.333, -1.667] |
| hesp_eigc_guard_designer_minus_memory_only | 24 | +0.111 | [+0.000, +0.236] | 3 / 0 | -1.58 | [-2.542, -0.708] |
| memory_only_minus_react_style | 24 | +0.292 | [+0.083, +0.500] | 10 / 1 | -0.08 | [-0.736, +0.542] |

## Security-facing metrics (descriptive only; PROTOCOL.md v0.6)

A guard that refuses an unsupported claim lowers the missed-attack rate by producing no claim at all; read these together with the unresolved rate.

| Arm | Episodes with a claim | Unresolved | Missed attack | False escalation | Wrong cause | Citation validity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| react_style | 72 / 72 | 0.403 | 0.426 | 0.333 | 0.431 | 0.690 |
| memory_only | 71 / 72 | 0.111 | 0.132 | 0.333 | 0.352 | 0.967 |
| hesp_eigc_guard_designer | 72 / 72 | 0 | 0.111 | 0.167 | 0.292 | 1.000 |
| hesp_eigc_guard_emp1 | 72 / 72 | 0 | 0.111 | 0.333 | 0.333 | 1.000 |
| hesp_eigc_guard_emp5 | 72 / 72 | 0 | 0.111 | 0.333 | 0.333 | 1.000 |
| hesp_eigc_guard_emp20 | 72 / 72 | 0 | 0.111 | 0.333 | 0.333 | 1.000 |
| hesp_eigc_guard_emp100 | 72 / 72 | 0 | 0.111 | 0.333 | 0.333 | 1.000 |
| hesp_eigc_guard_llmp | 27 / 72 | 0.625 | 0.400 | 0 | 0.333 | 0.938 |

All failures remain in the denominator; unknown usage stays null.

Primary endpoint (pre-registered): hesp_eigc_guard_emp20 - memory_only.
