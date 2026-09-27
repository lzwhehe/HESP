# v1.0 part C · qwen2.5-7b-instruct · adversarial evidence

Paired local-sandbox study. Intervals are over task clusters of a small, hand-built suite; they do not generalize to real websites or Web CTF.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| react_style | 42 | 0.000 | 5.83 | n/a | 6.79 | 9332 | 210 | DECISION_BUDGET_EXCEEDED:1, TOOL_BUDGET_EXCEEDED:23, UNVERIFIED_CLAIM:18 |
| memory_only | 42 | 0.024 | 5.79 | 10 | 7.05 | 11532 | 216 | DECISION_BUDGET_EXCEEDED:11, TOOL_BUDGET_EXCEEDED:12, UNVERIFIED_CLAIM:18, VERIFIED_SIMULATION:1 |
| hesp_guard_autostop | 42 | 0.357 | 1.29 | 1.20 | 3.86 | 6135 | 164 | DECISION_BUDGET_EXCEEDED:9, UNVERIFIED_CLAIM:18, VERIFIED_SIMULATION:15 |
| hesp_guard_autostop_corroborate | 42 | 0.405 | 2.71 | 2.06 | 3.93 | 6279 | 143 | DECISION_BUDGET_EXCEEDED:3, TOOL_BUDGET_EXCEEDED:3, UNVERIFIED_CLAIM:19, VERIFIED_SIMULATION:17 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| memory_only_minus_hesp_guard_autostop | 14 | -0.333 | [-0.571, -0.119] | 0 / 5 | +4.50 | [+1.905, +6.786] |
| react_style_minus_hesp_guard_autostop | 14 | -0.357 | [-0.643, -0.143] | 0 / 5 | +4.55 | [+1.976, +6.881] |
| hesp_guard_autostop_corroborate_minus_hesp_guard_autostop | 14 | +0.048 | [-0.167, +0.262] | 2 / 1 | +1.43 | [+0.643, +2.738] |
| memory_only_minus_react_style | 14 | +0.024 | [+0.000, +0.071] | 1 / 0 | -0.05 | [-0.452, +0.310] |

## Security-facing metrics (descriptive only; PROTOCOL.md v0.6)

A guard that refuses an unsupported claim lowers the missed-attack rate by producing no claim at all; read these together with the unresolved rate.

| Arm | Episodes with a claim | Unresolved | Missed attack | False escalation | Wrong cause | Citation validity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| react_style | 18 / 42 | 1 | 1 | n/a | 1 | 0.833 |
| memory_only | 19 / 42 | 0.976 | 1 | 0 | 0.947 | 0.842 |
| hesp_guard_autostop | 33 / 42 | 0.643 | 0.667 | 0 | 0.545 | 1.000 |
| hesp_guard_autostop_corroborate | 36 / 42 | 0.595 | 0 | 0 | 0.500 | 1.000 |

All failures remain in the denominator; unknown usage stays null.
