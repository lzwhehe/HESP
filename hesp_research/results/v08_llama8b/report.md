# v0.8 · llama-3.1-8b-instruct · sec-triage

Paired local-sandbox study. Intervals are over task clusters of a small, hand-built suite; they do not generalize to real websites or Web CTF.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| memory_only | 72 | 0.000 | 9.68 | n/a | 10.12 | 16086 | 339 | TOOL_BUDGET_EXCEEDED:72 |
| hesp_random_blind | 72 | 0.000 | 9.97 | n/a | 8.19 | 12969 | 303 | NO_LEGAL_ACTION:2, TOOL_BUDGET_EXCEEDED:70 |
| hesp_eigc_blind | 72 | 0.000 | 10 | n/a | 9.58 | 15429 | 361 | TOOL_BUDGET_EXCEEDED:72 |
| hesp_eigc | 72 | 0.000 | 10 | n/a | 9.58 | 16776 | 371 | TOOL_BUDGET_EXCEEDED:72 |
| hesp_eigc_guard | 72 | 0.000 | 10 | n/a | 9.58 | 16776 | 371 | TOOL_BUDGET_EXCEEDED:72 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| hesp_eigc_guard_minus_memory_only | 24 | +0.000 | [+0.000, +0.000] | 0 / 0 | +0.32 | [+0.208, +0.458] |
| hesp_eigc_blind_minus_hesp_random_blind | 24 | +0.000 | [+0.000, +0.000] | 0 / 0 | +0.03 | [+0.000, +0.069] |
| hesp_random_blind_minus_memory_only | 24 | +0.000 | [+0.000, +0.000] | 0 / 0 | +0.29 | [+0.181, +0.431] |
| hesp_eigc_minus_hesp_eigc_blind | 24 | +0.000 | [+0.000, +0.000] | 0 / 0 | +0.00 | [+0.000, +0.000] |
| hesp_eigc_guard_minus_hesp_eigc | 24 | +0.000 | [+0.000, +0.000] | 0 / 0 | +0.00 | [+0.000, +0.000] |

## Security-facing metrics (descriptive only; PROTOCOL.md v0.6)

A guard that refuses an unsupported claim lowers the missed-attack rate by producing no claim at all; read these together with the unresolved rate.

| Arm | Episodes with a claim | Unresolved | Missed attack | False escalation | Wrong cause | Citation validity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| memory_only | 0 / 72 | 1 | n/a | n/a | n/a | n/a |
| hesp_random_blind | 0 / 72 | 1 | n/a | n/a | n/a | n/a |
| hesp_eigc_blind | 0 / 72 | 1 | n/a | n/a | n/a | n/a |
| hesp_eigc | 0 / 72 | 1 | n/a | n/a | n/a | n/a |
| hesp_eigc_guard | 0 / 72 | 1 | n/a | n/a | n/a | n/a |

All failures remain in the denominator; unknown usage stays null.
