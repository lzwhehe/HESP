# v1.0 part C · qwen2.5-72b-instruct-awq · adversarial evidence

Paired local-sandbox study. Intervals are over task clusters of a small, hand-built suite; they do not generalize to real websites or Web CTF.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| react_style | 42 | 0.286 | 3.07 | 3.50 | 3.57 | 4532 | 132 | UNVERIFIED_CLAIM:30, VERIFIED_SIMULATION:12 |
| memory_only | 42 | 0.357 | 3.69 | 4.93 | 3.90 | 5806 | 145 | UNVERIFIED_CLAIM:27, VERIFIED_SIMULATION:15 |
| hesp_guard_autostop | 42 | 0.286 | 1 | 1 | 4.14 | 6527 | 157 | DECISION_BUDGET_EXCEEDED:12, UNVERIFIED_CLAIM:18, VERIFIED_SIMULATION:12 |
| hesp_guard_autostop_corroborate | 42 | 0.333 | 2.38 | 1.71 | 4.40 | 7233 | 169 | DECISION_BUDGET_EXCEEDED:10, UNVERIFIED_CLAIM:18, VERIFIED_SIMULATION:14 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| memory_only_minus_hesp_guard_autostop | 14 | +0.071 | [-0.214, +0.357] | 3 / 2 | +2.69 | [+1.238, +4.048] |
| react_style_minus_hesp_guard_autostop | 14 | +0.000 | [-0.286, +0.286] | 2 / 2 | +2.07 | [+0.857, +3.357] |
| hesp_guard_autostop_corroborate_minus_hesp_guard_autostop | 14 | +0.048 | [-0.167, +0.262] | 2 / 1 | +1.38 | [+0.762, +2.357] |
| memory_only_minus_react_style | 14 | +0.071 | [+0.000, +0.214] | 1 / 0 | +0.62 | [-0.048, +1.571] |

## Security-facing metrics (descriptive only; PROTOCOL.md v0.6)

A guard that refuses an unsupported claim lowers the missed-attack rate by producing no claim at all; read these together with the unresolved rate.

| Arm | Episodes with a claim | Unresolved | Missed attack | False escalation | Wrong cause | Citation validity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| react_style | 42 / 42 | 0.714 | 0.750 | 0 | 0.714 | 0.726 |
| memory_only | 42 / 42 | 0.643 | 0.667 | 0 | 0.643 | 0.786 |
| hesp_guard_autostop | 30 / 42 | 0.714 | 0.750 | 0 | 0.600 | 1.000 |
| hesp_guard_autostop_corroborate | 32 / 42 | 0.667 | 0 | 0 | 0.562 | 1.000 |

All failures remain in the denominator; unknown usage stays null.
