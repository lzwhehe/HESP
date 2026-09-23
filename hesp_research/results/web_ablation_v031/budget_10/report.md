# Selector ablation, tool budget 10

Paired local-sandbox study. Intervals are over task clusters of a small, hand-built suite; they do not generalize to real websites or Web CTF.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| sequential | 120 | 1.000 | 3.53 | 3.53 | 4.53 | 0 | 0 | VERIFIED_SIMULATION:120 |
| eig_cost | 120 | 1.000 | 3.86 | 3.86 | 3.31 | 0 | 0 | VERIFIED_SIMULATION:120 |
| eig | 120 | 0.992 | 3.62 | 3.57 | 2.48 | 0 | 0 | STOPPED_UNRESOLVED:1, VERIFIED_SIMULATION:119 |
| map_greedy | 120 | 1.000 | 3.67 | 3.67 | 3.97 | 0 | 0 | VERIFIED_SIMULATION:120 |
| random | 120 | 0.942 | 5.12 | 4.82 | 5.24 | 0 | 0 | STOPPED_UNRESOLVED:7, VERIFIED_SIMULATION:113 |
| lookahead | 120 | 0.992 | 3.62 | 3.57 | 2.48 | 0 | 0 | STOPPED_UNRESOLVED:1, VERIFIED_SIMULATION:119 |
| eig_cost_llmP | 120 | 0.725 | 7.55 | 6.62 | 5.77 | 0 | 0 | STOPPED_UNRESOLVED:33, VERIFIED_SIMULATION:87 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| eig_cost_minus_sequential | 24 | +0.000 | [+0.000, +0.000] | 0 / 0 | +0.33 | [-0.867, +1.450] |
| eig_cost_minus_eig | 24 | +0.008 | [+0.000, +0.025] | 1 / 0 | +0.23 | [-0.792, +1.217] |
| eig_cost_minus_map_greedy | 24 | +0.000 | [+0.000, +0.000] | 0 / 0 | +0.19 | [-0.425, +0.800] |
| eig_cost_minus_random | 24 | +0.058 | [+0.017, +0.100] | 6 / 0 | -1.27 | [-2.308, -0.317] |
| eig_cost_minus_lookahead | 24 | +0.008 | [+0.000, +0.025] | 1 / 0 | +0.23 | [-0.792, +1.217] |
| eig_cost_minus_eig_cost_llmP | 24 | +0.275 | [+0.142, +0.417] | 14 / 0 | -3.69 | [-4.867, -2.592] |
| lookahead_minus_eig | 24 | +0.000 | [+0.000, +0.000] | 0 / 0 | +0.00 | [+0.000, +0.000] |
| lookahead_minus_sequential | 24 | -0.008 | [-0.025, +0.000] | 0 / 1 | +0.09 | [-0.800, +0.908] |

All failures remain in the denominator; unknown usage stays null.
