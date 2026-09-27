# v1.0 part C · qwen2.5-32b-instruct-awq · adversarial evidence

Paired local-sandbox study. Intervals are over task clusters of a small, hand-built suite; they do not generalize to real websites or Web CTF.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| react_style | 42 | 0.286 | 2.21 | 3.25 | 3.14 | 3929 | 111 | UNVERIFIED_CLAIM:30, VERIFIED_SIMULATION:12 |
| memory_only | 42 | 0.452 | 3.81 | 5.53 | 4.02 | 6035 | 141 | UNVERIFIED_CLAIM:23, VERIFIED_SIMULATION:19 |
| hesp_guard_autostop | 42 | 0.286 | 1 | 1 | 4.14 | 6527 | 178 | DECISION_BUDGET_EXCEEDED:12, UNVERIFIED_CLAIM:18, VERIFIED_SIMULATION:12 |
| hesp_guard_autostop_corroborate | 42 | 0.429 | 2.79 | 2.17 | 3.24 | 5145 | 111 | DECISION_BUDGET_EXCEEDED:3, UNVERIFIED_CLAIM:21, VERIFIED_SIMULATION:18 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| memory_only_minus_hesp_guard_autostop | 14 | +0.167 | [-0.167, +0.500] | 5 / 2 | +2.81 | [+1.286, +4.333] |
| react_style_minus_hesp_guard_autostop | 14 | +0.000 | [-0.286, +0.286] | 2 / 2 | +1.21 | [+0.643, +1.786] |
| hesp_guard_autostop_corroborate_minus_hesp_guard_autostop | 14 | +0.143 | [-0.143, +0.429] | 3 / 1 | +1.79 | [+0.857, +3.143] |
| memory_only_minus_react_style | 14 | +0.167 | [+0.000, +0.381] | 3 / 0 | +1.60 | [+0.571, +2.762] |

## Security-facing metrics (descriptive only; PROTOCOL.md v0.6)

A guard that refuses an unsupported claim lowers the missed-attack rate by producing no claim at all; read these together with the unresolved rate.

| Arm | Episodes with a claim | Unresolved | Missed attack | False escalation | Wrong cause | Citation validity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| react_style | 42 / 42 | 0.714 | 0.833 | 0 | 0.714 | 0.881 |
| memory_only | 42 / 42 | 0.548 | 0.556 | 0 | 0.548 | 0.929 |
| hesp_guard_autostop | 30 / 42 | 0.714 | 0.750 | 0 | 0.600 | 1.000 |
| hesp_guard_autostop_corroborate | 39 / 42 | 0.571 | 0 | 0 | 0.462 | 1.000 |

All failures remain in the denominator; unknown usage stays null.
