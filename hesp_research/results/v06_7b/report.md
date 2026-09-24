# v0.6 RQ3 · qwen2.5-7b-instruct · sec-triage

Paired local-sandbox study. Intervals are over task clusters of a small, hand-built suite; they do not generalize to real websites or Web CTF.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| react_style | 72 | 0.028 | 9.14 | 8 | 10.82 | 15239 | 316 | DECISION_BUDGET_EXCEEDED:26, TOOL_BUDGET_EXCEEDED:43, UNVERIFIED_CLAIM:1, VERIFIED_SIMULATION:2 |
| memory_only | 72 | 0.125 | 9.44 | 8.11 | 10.28 | 17091 | 304 | DECISION_BUDGET_EXCEEDED:15, TOOL_BUDGET_EXCEEDED:48, VERIFIED_SIMULATION:9 |
| hesp_eigc_guard_designer | 72 | 1.000 | 7.07 | 7.07 | 6.81 | 12421 | 224 | VERIFIED_SIMULATION:72 |
| hesp_eigc_guard_emp1 | 72 | 0.986 | 9.44 | 9.44 | 9.19 | 17021 | 275 | DECISION_BUDGET_EXCEEDED:1, VERIFIED_SIMULATION:71 |
| hesp_eigc_guard_emp5 | 72 | 1.000 | 9.40 | 9.40 | 9.15 | 16938 | 273 | VERIFIED_SIMULATION:72 |
| hesp_eigc_guard_emp20 | 72 | 1.000 | 9.40 | 9.40 | 9.15 | 16938 | 273 | VERIFIED_SIMULATION:72 |
| hesp_eigc_guard_emp100 | 72 | 1.000 | 9.40 | 9.40 | 9.15 | 16938 | 273 | VERIFIED_SIMULATION:72 |
| hesp_eigc_guard_llmp | 72 | 0.069 | 10 | 10 | 11.17 | 21036 | 393 | DECISION_BUDGET_EXCEEDED:49, TOOL_BUDGET_EXCEEDED:14, UNVERIFIED_CLAIM:4, VERIFIED_SIMULATION:5 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| hesp_eigc_guard_emp20_minus_memory_only | 24 | +0.875 | [+0.736, +0.972] | 22 / 0 | -0.04 | [-0.694, +0.542] |
| hesp_eigc_guard_emp1_minus_memory_only | 24 | +0.861 | [+0.722, +0.958] | 22 / 0 | -0.00 | [-0.639, +0.556] |
| hesp_eigc_guard_emp5_minus_memory_only | 24 | +0.875 | [+0.736, +0.972] | 22 / 0 | -0.04 | [-0.694, +0.542] |
| hesp_eigc_guard_emp100_minus_memory_only | 24 | +0.875 | [+0.736, +0.972] | 22 / 0 | -0.04 | [-0.694, +0.542] |
| hesp_eigc_guard_designer_minus_hesp_eigc_guard_emp20 | 24 | +0.000 | [+0.000, +0.000] | 0 / 0 | -2.33 | [-3.139, -1.583] |
| hesp_eigc_guard_emp20_minus_hesp_eigc_guard_llmp | 24 | +0.931 | [+0.819, +1.000] | 23 / 0 | -0.60 | [-1.139, -0.167] |
| hesp_eigc_guard_designer_minus_memory_only | 24 | +0.875 | [+0.736, +0.972] | 22 / 0 | -2.38 | [-3.181, -1.653] |
| memory_only_minus_react_style | 24 | +0.097 | [+0.000, +0.222] | 3 / 0 | +0.31 | [-0.194, +0.792] |

## Security-facing metrics (descriptive only; PROTOCOL.md v0.6)

A guard that refuses an unsupported claim lowers the missed-attack rate by producing no claim at all; read these together with the unresolved rate.

| Arm | Episodes with a claim | Unresolved | Missed attack | False escalation | Wrong cause | Citation validity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| react_style | 3 / 72 | 0.972 | 1 | n/a | 1 | 1.000 |
| memory_only | 9 / 72 | 0.875 | 0.222 | n/a | 0.333 | 1.000 |
| hesp_eigc_guard_designer | 72 / 72 | 0 | 0.111 | 0.333 | 0.333 | 1.000 |
| hesp_eigc_guard_emp1 | 71 / 72 | 0.014 | 0.113 | 0.333 | 0.338 | 1.000 |
| hesp_eigc_guard_emp5 | 72 / 72 | 0 | 0.111 | 0.333 | 0.333 | 1.000 |
| hesp_eigc_guard_emp20 | 72 / 72 | 0 | 0.111 | 0.333 | 0.333 | 1.000 |
| hesp_eigc_guard_emp100 | 72 / 72 | 0 | 0.111 | 0.333 | 0.333 | 1.000 |
| hesp_eigc_guard_llmp | 9 / 72 | 0.931 | 1 | 0 | 0.333 | 1.000 |

All failures remain in the denominator; unknown usage stays null.

Primary endpoint (pre-registered): hesp_eigc_guard_emp20 - memory_only.
