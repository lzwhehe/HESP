# Selector ablation, tool budget 5

Paired local-sandbox study. Intervals are over task clusters of a small, hand-built suite; they do not generalize to real websites or Web CTF.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| sequential | 120 | 0.767 | 3.11 | 2.53 | 4.11 | 0 | 0 | STOPPED_UNRESOLVED:28, VERIFIED_SIMULATION:92 |
| eig_cost | 120 | 0.775 | 3.25 | 2.74 | 3 | 0 | 0 | STOPPED_UNRESOLVED:27, VERIFIED_SIMULATION:93 |
| eig | 120 | 0.917 | 3.29 | 3.14 | 2.29 | 0 | 0 | STOPPED_UNRESOLVED:10, VERIFIED_SIMULATION:110 |
| map_greedy | 120 | 0.800 | 2.91 | 2.39 | 3.91 | 0 | 0 | STOPPED_UNRESOLVED:24, VERIFIED_SIMULATION:96 |
| random | 120 | 0.608 | 3.78 | 3 | 4.35 | 0 | 0 | STOPPED_UNRESOLVED:47, VERIFIED_SIMULATION:73 |
| lookahead | 120 | 0.775 | 3.25 | 2.74 | 3 | 0 | 0 | STOPPED_UNRESOLVED:27, VERIFIED_SIMULATION:93 |
| eig_cost_llmP | 120 | 0.258 | 4.83 | 4.32 | 3.83 | 0 | 0 | STOPPED_UNRESOLVED:89, VERIFIED_SIMULATION:31 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| eig_cost_minus_sequential | 24 | +0.008 | [-0.192, +0.208] | 4 / 6 | +0.14 | [-0.617, +0.850] |
| eig_cost_minus_eig | 24 | -0.142 | [-0.292, -0.017] | 3 / 6 | -0.04 | [-0.750, +0.583] |
| eig_cost_minus_map_greedy | 24 | -0.025 | [-0.150, +0.100] | 3 / 5 | +0.34 | [+0.008, +0.725] |
| eig_cost_minus_random | 24 | +0.167 | [+0.050, +0.300] | 13 / 4 | -0.53 | [-1.275, +0.117] |
| eig_cost_minus_lookahead | 24 | +0.000 | [+0.000, +0.000] | 0 / 0 | +0.00 | [+0.000, +0.000] |
| eig_cost_minus_eig_cost_llmP | 24 | +0.517 | [+0.325, +0.700] | 17 / 2 | -1.57 | [-2.308, -0.933] |
| lookahead_minus_eig | 24 | -0.142 | [-0.292, -0.017] | 3 / 6 | -0.04 | [-0.750, +0.583] |
| lookahead_minus_sequential | 24 | +0.008 | [-0.192, +0.208] | 4 / 6 | +0.14 | [-0.617, +0.850] |

All failures remain in the denominator; unknown usage stays null.
