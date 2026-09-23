# Selector ablation, tool budget 4

Paired local-sandbox study. Intervals are over task clusters of a small, hand-built suite; they do not generalize to real websites or Web CTF.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| sequential | 120 | 0.692 | 2.80 | 2.27 | 3.80 | 0 | 0 | STOPPED_UNRESOLVED:37, VERIFIED_SIMULATION:83 |
| eig_cost | 120 | 0.667 | 2.89 | 2.34 | 2.71 | 0 | 0 | STOPPED_UNRESOLVED:40, VERIFIED_SIMULATION:80 |
| eig | 120 | 0.875 | 3.17 | 3.05 | 2.17 | 0 | 0 | STOPPED_UNRESOLVED:15, VERIFIED_SIMULATION:105 |
| map_greedy | 120 | 0.683 | 2.59 | 1.94 | 3.59 | 0 | 0 | STOPPED_UNRESOLVED:38, VERIFIED_SIMULATION:82 |
| random | 120 | 0.533 | 3.17 | 2.45 | 3.83 | 0 | 0 | STOPPED_UNRESOLVED:56, VERIFIED_SIMULATION:64 |
| lookahead | 120 | 0.675 | 2.95 | 2.44 | 2.65 | 0 | 0 | STOPPED_UNRESOLVED:39, VERIFIED_SIMULATION:81 |
| eig_cost_llmP | 120 | 0.175 | 4 | 4 | 3 | 0 | 0 | STOPPED_UNRESOLVED:99, VERIFIED_SIMULATION:21 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| eig_cost_minus_sequential | 24 | -0.025 | [-0.258, +0.225] | 6 / 8 | +0.09 | [-0.483, +0.658] |
| eig_cost_minus_eig | 24 | -0.208 | [-0.375, -0.050] | 3 / 7 | -0.28 | [-0.875, +0.250] |
| eig_cost_minus_map_greedy | 24 | -0.017 | [-0.192, +0.158] | 4 / 6 | +0.30 | [+0.092, +0.550] |
| eig_cost_minus_random | 24 | +0.133 | [-0.017, +0.292] | 13 / 6 | -0.28 | [-0.900, +0.267] |
| eig_cost_minus_lookahead | 24 | -0.008 | [-0.033, +0.017] | 1 / 2 | -0.06 | [-0.117, -0.017] |
| eig_cost_minus_eig_cost_llmP | 24 | +0.492 | [+0.317, +0.667] | 16 / 1 | -1.11 | [-1.717, -0.608] |
| lookahead_minus_eig | 24 | -0.200 | [-0.367, -0.042] | 3 / 8 | -0.22 | [-0.783, +0.292] |
| lookahead_minus_sequential | 24 | -0.017 | [-0.242, +0.233] | 6 / 9 | +0.15 | [-0.425, +0.708] |

All failures remain in the denominator; unknown usage stays null.
