# Selector ablation, tool budget 8

Paired local-sandbox study. Intervals are over task clusters of a small, hand-built suite; they do not generalize to real websites or Web CTF.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| sequential | 120 | 1.000 | 3.53 | 3.53 | 4.53 | 0 | 0 | VERIFIED_SIMULATION:120 |
| eig_cost | 120 | 0.983 | 3.84 | 3.77 | 3.29 | 0 | 0 | STOPPED_UNRESOLVED:2, VERIFIED_SIMULATION:118 |
| eig | 120 | 0.958 | 3.58 | 3.38 | 2.42 | 0 | 0 | STOPPED_UNRESOLVED:5, VERIFIED_SIMULATION:115 |
| map_greedy | 120 | 0.975 | 3.61 | 3.50 | 3.94 | 0 | 0 | STOPPED_UNRESOLVED:3, VERIFIED_SIMULATION:117 |
| random | 120 | 0.892 | 4.83 | 4.45 | 5.12 | 0 | 0 | STOPPED_UNRESOLVED:13, VERIFIED_SIMULATION:107 |
| lookahead | 120 | 0.950 | 3.54 | 3.31 | 2.46 | 0 | 0 | STOPPED_UNRESOLVED:6, VERIFIED_SIMULATION:114 |
| eig_cost_llmP | 120 | 0.592 | 6.77 | 5.92 | 4.98 | 0 | 0 | STOPPED_UNRESOLVED:49, VERIFIED_SIMULATION:71 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| eig_cost_minus_sequential | 24 | -0.017 | [-0.042, +0.000] | 0 / 2 | +0.31 | [-0.875, +1.425] |
| eig_cost_minus_eig | 24 | +0.025 | [-0.017, +0.083] | 2 / 1 | +0.27 | [-0.742, +1.250] |
| eig_cost_minus_map_greedy | 24 | +0.008 | [-0.025, +0.050] | 1 / 1 | +0.23 | [-0.367, +0.808] |
| eig_cost_minus_random | 24 | +0.092 | [+0.025, +0.158] | 8 / 1 | -0.99 | [-1.983, -0.058] |
| eig_cost_minus_lookahead | 24 | +0.033 | [-0.017, +0.092] | 3 / 1 | +0.30 | [-0.667, +1.258] |
| eig_cost_minus_eig_cost_llmP | 24 | +0.392 | [+0.233, +0.567] | 16 / 1 | -2.92 | [-3.950, -1.942] |
| lookahead_minus_eig | 24 | -0.008 | [-0.025, +0.000] | 0 / 1 | -0.03 | [-0.125, +0.050] |
| lookahead_minus_sequential | 24 | -0.050 | [-0.108, -0.008] | 0 / 4 | +0.01 | [-0.867, +0.817] |

All failures remain in the denominator; unknown usage stays null.
