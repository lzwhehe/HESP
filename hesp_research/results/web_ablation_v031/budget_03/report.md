# Selector ablation, tool budget 3

Paired local-sandbox study. Intervals are over task clusters of a small, hand-built suite; they do not generalize to real websites or Web CTF.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| sequential | 120 | 0.567 | 2.37 | 1.88 | 3.37 | 0 | 0 | STOPPED_UNRESOLVED:52, VERIFIED_SIMULATION:68 |
| eig_cost | 120 | 0.617 | 2.20 | 1.70 | 3.20 | 0 | 0 | STOPPED_UNRESOLVED:46, VERIFIED_SIMULATION:74 |
| eig | 120 | 0.833 | 3 | 3 | 2 | 0 | 0 | STOPPED_UNRESOLVED:20, VERIFIED_SIMULATION:100 |
| map_greedy | 120 | 0.608 | 2.20 | 1.68 | 3.20 | 0 | 0 | STOPPED_UNRESOLVED:47, VERIFIED_SIMULATION:73 |
| random | 120 | 0.467 | 2.49 | 1.91 | 3.33 | 0 | 0 | STOPPED_UNRESOLVED:64, VERIFIED_SIMULATION:56 |
| lookahead | 120 | 0.833 | 3 | 3 | 2 | 0 | 0 | STOPPED_UNRESOLVED:20, VERIFIED_SIMULATION:100 |
| eig_cost_llmP | 120 | 0.000 | 3 | n/a | 2 | 0 | 0 | STOPPED_UNRESOLVED:120 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| eig_cost_minus_sequential | 24 | +0.050 | [-0.233, +0.342] | 7 / 6 | -0.17 | [-0.575, +0.250] |
| eig_cost_minus_eig | 24 | -0.217 | [-0.425, -0.008] | 10 / 9 | -0.80 | [-1.183, -0.450] |
| eig_cost_minus_map_greedy | 24 | +0.008 | [-0.025, +0.050] | 1 / 1 | +0.00 | [-0.158, +0.150] |
| eig_cost_minus_random | 24 | +0.150 | [-0.058, +0.367] | 13 / 8 | -0.29 | [-0.692, +0.067] |
| eig_cost_minus_lookahead | 24 | -0.217 | [-0.425, -0.008] | 10 / 9 | -0.80 | [-1.183, -0.450] |
| eig_cost_minus_eig_cost_llmP | 24 | +0.617 | [+0.417, +0.800] | 15 / 0 | -0.80 | [-1.183, -0.450] |
| lookahead_minus_eig | 24 | +0.000 | [+0.000, +0.000] | 0 / 0 | +0.00 | [+0.000, +0.000] |
| lookahead_minus_sequential | 24 | +0.267 | [+0.075, +0.458] | 10 / 8 | +0.63 | [+0.317, +0.967] |

All failures remain in the denominator; unknown usage stays null.
