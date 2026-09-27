# v1.0 part C · qwen2.5-7b-instruct · adversarial evidence

Paired local-sandbox study. Intervals are over task clusters of a small, hand-built suite; they do not generalize to real websites or Web CTF.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| react_style | 2 | 0.000 | 5.50 | n/a | 6.50 | 8959 | 198 | TOOL_BUDGET_EXCEEDED:1, UNVERIFIED_CLAIM:1 |
| memory_only | 2 | 0.000 | 5.50 | n/a | 5.50 | 8699 | 174 | TOOL_BUDGET_EXCEEDED:1, UNVERIFIED_CLAIM:1 |
| hesp_guard_autostop | 2 | 0.500 | 1 | 1 | 1 | 1347 | 30 | UNVERIFIED_CLAIM:1, VERIFIED_SIMULATION:1 |
| hesp_guard_autostop_corroborate | 2 | 0.500 | 1.50 | 1 | 1.50 | 2055 | 45 | UNVERIFIED_CLAIM:1, VERIFIED_SIMULATION:1 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| memory_only_minus_hesp_guard_autostop | 2 | -0.500 | [-1.000, +0.000] | 0 / 1 | +4.50 | [+0.000, +9.000] |
| react_style_minus_hesp_guard_autostop | 2 | -0.500 | [-1.000, +0.000] | 0 / 1 | +4.50 | [+0.000, +9.000] |
| hesp_guard_autostop_corroborate_minus_hesp_guard_autostop | 2 | +0.000 | [+0.000, +0.000] | 0 / 0 | +0.50 | [+0.000, +1.000] |
| memory_only_minus_react_style | 2 | +0.000 | [+0.000, +0.000] | 0 / 0 | +0.00 | [+0.000, +0.000] |

## Security-facing metrics (descriptive only; PROTOCOL.md v0.6)

A guard that refuses an unsupported claim lowers the missed-attack rate by producing no claim at all; read these together with the unresolved rate.

| Arm | Episodes with a claim | Unresolved | Missed attack | False escalation | Wrong cause | Citation validity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| react_style | 1 / 2 | 1 | 1 | n/a | 1 | 0.000 |
| memory_only | 1 / 2 | 1 | 1 | n/a | 1 | 0.000 |
| hesp_guard_autostop | 2 / 2 | 0.500 | 0.500 | n/a | 0.500 | 1.000 |
| hesp_guard_autostop_corroborate | 2 / 2 | 0.500 | 0 | n/a | 0.500 | 1.000 |

All failures remain in the denominator; unknown usage stays null.
