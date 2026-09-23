# Selector ablation, tool budget 6

Paired local-sandbox study. Intervals are over task clusters of a small, hand-built suite; they do not generalize to real websites or Web CTF.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| sequential | 120 | 0.875 | 3.34 | 2.96 | 4.34 | 0 | 0 | STOPPED_UNRESOLVED:15, VERIFIED_SIMULATION:105 |
| eig_cost | 120 | 0.833 | 3.48 | 2.97 | 3.23 | 0 | 0 | STOPPED_UNRESOLVED:20, VERIFIED_SIMULATION:100 |
| eig | 120 | 0.933 | 3.43 | 3.25 | 2.32 | 0 | 0 | STOPPED_UNRESOLVED:8, VERIFIED_SIMULATION:112 |
| map_greedy | 120 | 0.858 | 3.30 | 2.85 | 3.90 | 0 | 0 | STOPPED_UNRESOLVED:17, VERIFIED_SIMULATION:103 |
| random | 120 | 0.700 | 4.22 | 3.46 | 4.69 | 0 | 0 | STOPPED_UNRESOLVED:36, VERIFIED_SIMULATION:84 |
| lookahead | 120 | 0.933 | 3.43 | 3.25 | 2.32 | 0 | 0 | STOPPED_UNRESOLVED:8, VERIFIED_SIMULATION:112 |
| eig_cost_llmP | 120 | 0.350 | 5.57 | 4.76 | 4.45 | 0 | 0 | STOPPED_UNRESOLVED:78, VERIFIED_SIMULATION:42 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| eig_cost_minus_sequential | 24 | -0.042 | [-0.217, +0.133] | 3 / 7 | +0.13 | [-0.800, +1.000] |
| eig_cost_minus_eig | 24 | -0.100 | [-0.233, +0.008] | 3 / 5 | +0.04 | [-0.783, +0.792] |
| eig_cost_minus_map_greedy | 24 | -0.025 | [-0.075, +0.017] | 2 / 4 | +0.17 | [-0.308, +0.658] |
| eig_cost_minus_random | 24 | +0.133 | [+0.000, +0.258] | 13 / 4 | -0.75 | [-1.567, -0.025] |
| eig_cost_minus_lookahead | 24 | -0.100 | [-0.233, +0.008] | 3 / 5 | +0.04 | [-0.783, +0.792] |
| eig_cost_minus_eig_cost_llmP | 24 | +0.483 | [+0.300, +0.650] | 17 / 2 | -2.09 | [-2.917, -1.350] |
| lookahead_minus_eig | 24 | +0.000 | [+0.000, +0.000] | 0 / 0 | +0.00 | [+0.000, +0.000] |
| lookahead_minus_sequential | 24 | +0.058 | [-0.058, +0.192] | 4 / 5 | +0.09 | [-0.650, +0.817] |

All failures remain in the denominator; unknown usage stays null.
