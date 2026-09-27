# v1.0 part C · llama-3.1-70b-instruct-awq · adversarial evidence

Paired local-sandbox study. Intervals are over task clusters of a small, hand-built suite; they do not generalize to real websites or Web CTF.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| react_style | 42 | 0.310 | 5.38 | 8.23 | 5.76 | 7462 | 158 | TOOL_BUDGET_EXCEEDED:5, UNVERIFIED_CLAIM:24, VERIFIED_SIMULATION:13 |
| memory_only | 42 | 0.214 | 5.19 | 7.89 | 5.33 | 8033 | 146 | TOOL_BUDGET_EXCEEDED:15, UNVERIFIED_CLAIM:18, VERIFIED_SIMULATION:9 |
| hesp_guard_autostop | 42 | 0.500 | 1.64 | 1.86 | 2.05 | 2882 | 58 | UNVERIFIED_CLAIM:21, VERIFIED_SIMULATION:21 |
| hesp_guard_autostop_corroborate | 42 | 0.429 | 2.79 | 2.17 | 3.21 | 4749 | 91 | DECISION_BUDGET_EXCEEDED:3, UNVERIFIED_CLAIM:21, VERIFIED_SIMULATION:18 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| memory_only_minus_hesp_guard_autostop | 14 | -0.286 | [-0.571, +0.000] | 1 / 5 | +3.55 | [+1.048, +5.976] |
| react_style_minus_hesp_guard_autostop | 14 | -0.190 | [-0.571, +0.190] | 4 / 6 | +3.74 | [+1.143, +6.190] |
| hesp_guard_autostop_corroborate_minus_hesp_guard_autostop | 14 | -0.071 | [-0.214, +0.000] | 0 / 1 | +1.14 | [+0.357, +2.500] |
| memory_only_minus_react_style | 14 | -0.095 | [-0.262, +0.048] | 1 / 3 | -0.19 | [-0.571, +0.167] |

## Security-facing metrics (descriptive only; PROTOCOL.md v0.6)

A guard that refuses an unsupported claim lowers the missed-attack rate by producing no claim at all; read these together with the unresolved rate.

| Arm | Episodes with a claim | Unresolved | Missed attack | False escalation | Wrong cause | Citation validity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| react_style | 37 / 42 | 0.690 | 0.750 | 0 | 0.649 | 0.829 |
| memory_only | 27 / 42 | 0.786 | 0.857 | 0 | 0.667 | 0.877 |
| hesp_guard_autostop | 42 / 42 | 0.500 | 0.500 | 0 | 0.429 | 1.000 |
| hesp_guard_autostop_corroborate | 39 / 42 | 0.571 | 0 | 0 | 0.462 | 1.000 |

All failures remain in the denominator; unknown usage stays null.
