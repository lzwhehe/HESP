# v1.0 part C · llama-3.1-8b-instruct · adversarial evidence

Paired local-sandbox study. Intervals are over task clusters of a small, hand-built suite; they do not generalize to real websites or Web CTF.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| react_style | 42 | 0.000 | 9.95 | n/a | 11.14 | 15719 | 372 | DECISION_BUDGET_EXCEEDED:6, TOOL_BUDGET_EXCEEDED:36 |
| memory_only | 42 | 0.000 | 9.88 | n/a | 9.76 | 16013 | 332 | TOOL_BUDGET_EXCEEDED:42 |
| hesp_guard_autostop | 42 | 0.500 | 1.64 | 1.86 | 1.64 | 2241 | 60 | UNVERIFIED_CLAIM:21, VERIFIED_SIMULATION:21 |
| hesp_guard_autostop_corroborate | 42 | 0.429 | 2.79 | 2.17 | 2.71 | 3862 | 100 | TOOL_BUDGET_EXCEEDED:3, UNVERIFIED_CLAIM:21, VERIFIED_SIMULATION:18 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| memory_only_minus_hesp_guard_autostop | 14 | -0.500 | [-0.786, -0.214] | 0 / 7 | +8.24 | [+7.571, +8.786] |
| react_style_minus_hesp_guard_autostop | 14 | -0.500 | [-0.786, -0.214] | 0 / 7 | +8.31 | [+7.690, +8.833] |
| hesp_guard_autostop_corroborate_minus_hesp_guard_autostop | 14 | -0.071 | [-0.214, +0.000] | 0 / 1 | +1.14 | [+0.357, +2.500] |
| memory_only_minus_react_style | 14 | +0.000 | [+0.000, +0.000] | 0 / 0 | -0.07 | [-0.190, +0.048] |

## Security-facing metrics (descriptive only; PROTOCOL.md v0.6)

A guard that refuses an unsupported claim lowers the missed-attack rate by producing no claim at all; read these together with the unresolved rate.

| Arm | Episodes with a claim | Unresolved | Missed attack | False escalation | Wrong cause | Citation validity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| react_style | 0 / 42 | 1 | n/a | n/a | n/a | n/a |
| memory_only | 0 / 42 | 1 | n/a | n/a | n/a | n/a |
| hesp_guard_autostop | 42 / 42 | 0.500 | 0.500 | 0 | 0.429 | 1.000 |
| hesp_guard_autostop_corroborate | 39 / 42 | 0.571 | 0 | 0 | 0.462 | 1.000 |

All failures remain in the denominator; unknown usage stays null.
