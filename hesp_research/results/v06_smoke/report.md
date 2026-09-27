# v0.6 RQ3 · qwen2.5:7b-instruct · sec-triage

Paired local-sandbox study. Intervals are over task clusters of a small, hand-built suite; they do not generalize to real websites or Web CTF.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| react_style | 2 | 0.000 | 6 | n/a | 11.50 | 26912 | 314 | DECISION_BUDGET_EXCEEDED:1, TOOL_BUDGET_EXCEEDED:1 |
| memory_only | 2 | 0.000 | 5.50 | n/a | 12 | 31834 | 322 | DECISION_BUDGET_EXCEEDED:2 |
| hesp_eigc_guard_designer | 2 | 0.500 | 5.50 | 3 | 8 | 24690 | 348 | DECISION_BUDGET_EXCEEDED:1, VERIFIED_SIMULATION:1 |
| hesp_eigc_guard_emp1 | 2 | 0.500 | 9.50 | 9 | 10 | 32491 | 362 | DECISION_BUDGET_EXCEEDED:1, VERIFIED_SIMULATION:1 |
| hesp_eigc_guard_emp5 | 2 | 0.500 | 10 | 10 | 10.50 | 33988 | 379 | DECISION_BUDGET_EXCEEDED:1, VERIFIED_SIMULATION:1 |
| hesp_eigc_guard_emp20 | 2 | 0.500 | 10 | 10 | 10.50 | 32173 | 380 | DECISION_BUDGET_EXCEEDED:1, VERIFIED_SIMULATION:1 |
| hesp_eigc_guard_emp100 | 2 | 0.500 | 10 | 10 | 10.50 | 32768 | 372 | DECISION_BUDGET_EXCEEDED:1, VERIFIED_SIMULATION:1 |
| hesp_eigc_guard_llmp | 2 | 0.000 | 10 | n/a | 12 | 35947 | 434 | DECISION_BUDGET_EXCEEDED:2 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| hesp_eigc_guard_emp20_minus_memory_only | 2 | +0.500 | [+0.000, +1.000] | 1 / 0 | +4.50 | [+2.000, +7.000] |
| hesp_eigc_guard_emp1_minus_memory_only | 2 | +0.500 | [+0.000, +1.000] | 1 / 0 | +4.00 | [+2.000, +6.000] |
| hesp_eigc_guard_emp5_minus_memory_only | 2 | +0.500 | [+0.000, +1.000] | 1 / 0 | +4.50 | [+2.000, +7.000] |
| hesp_eigc_guard_emp100_minus_memory_only | 2 | +0.500 | [+0.000, +1.000] | 1 / 0 | +4.50 | [+2.000, +7.000] |
| hesp_eigc_guard_designer_minus_hesp_eigc_guard_emp20 | 2 | +0.000 | [+0.000, +0.000] | 0 / 0 | -4.50 | [-7.000, -2.000] |
| hesp_eigc_guard_emp20_minus_hesp_eigc_guard_llmp | 2 | +0.500 | [+0.000, +1.000] | 1 / 0 | +0.00 | [+0.000, +0.000] |
| hesp_eigc_guard_designer_minus_memory_only | 2 | +0.500 | [+0.000, +1.000] | 1 / 0 | +0.00 | [+0.000, +0.000] |
| memory_only_minus_react_style | 2 | +0.000 | [+0.000, +0.000] | 0 / 0 | -0.50 | [-2.000, +1.000] |

## Security-facing metrics (descriptive only; PROTOCOL.md v0.6)

A guard that refuses an unsupported claim lowers the missed-attack rate by producing no claim at all; read these together with the unresolved rate.

| Arm | Episodes with a claim | Unresolved | Missed attack | False escalation | Wrong cause | Citation validity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| react_style | 0 / 2 | 1 | n/a | n/a | n/a | n/a |
| memory_only | 0 / 2 | 1 | n/a | n/a | n/a | n/a |
| hesp_eigc_guard_designer | 1 / 2 | 0.500 | 0 | n/a | 0 | 1.000 |
| hesp_eigc_guard_emp1 | 1 / 2 | 0.500 | 0 | n/a | 0 | 1.000 |
| hesp_eigc_guard_emp5 | 1 / 2 | 0.500 | 0 | n/a | 0 | 1.000 |
| hesp_eigc_guard_emp20 | 1 / 2 | 0.500 | 0 | n/a | 0 | 1.000 |
| hesp_eigc_guard_emp100 | 1 / 2 | 0.500 | 0 | n/a | 0 | 1.000 |
| hesp_eigc_guard_llmp | 0 / 2 | 1 | n/a | n/a | n/a | n/a |

All failures remain in the denominator; unknown usage stays null.

Primary endpoint (pre-registered): hesp_eigc_guard_emp20 - memory_only.
