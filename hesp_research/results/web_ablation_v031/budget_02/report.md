# Selector ablation, tool budget 2

Paired local-sandbox study. Intervals are over task clusters of a small, hand-built suite; they do not generalize to real websites or Web CTF.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| sequential | 120 | 0.400 | 1.77 | 1.42 | 2.77 | 0 | 0 | STOPPED_UNRESOLVED:72, VERIFIED_SIMULATION:48 |
| eig_cost | 120 | 0.450 | 1.65 | 1.22 | 2.65 | 0 | 0 | STOPPED_UNRESOLVED:66, VERIFIED_SIMULATION:54 |
| eig | 120 | 0.450 | 1.65 | 1.22 | 2.65 | 0 | 0 | STOPPED_UNRESOLVED:66, VERIFIED_SIMULATION:54 |
| map_greedy | 120 | 0.450 | 1.65 | 1.22 | 2.65 | 0 | 0 | STOPPED_UNRESOLVED:66, VERIFIED_SIMULATION:54 |
| random | 120 | 0.333 | 1.75 | 1.25 | 2.75 | 0 | 0 | STOPPED_UNRESOLVED:80, VERIFIED_SIMULATION:40 |
| lookahead | 120 | 0.450 | 1.65 | 1.22 | 2.65 | 0 | 0 | STOPPED_UNRESOLVED:66, VERIFIED_SIMULATION:54 |
| eig_cost_llmP | 120 | 0.000 | 2 | n/a | 3 | 0 | 0 | STOPPED_UNRESOLVED:120 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| eig_cost_minus_sequential | 24 | +0.050 | [-0.167, +0.258] | 6 / 3 | -0.12 | [-0.342, +0.117] |
| eig_cost_minus_eig | 24 | +0.000 | [+0.000, +0.000] | 0 / 0 | +0.00 | [+0.000, +0.000] |
| eig_cost_minus_map_greedy | 24 | +0.000 | [-0.150, +0.158] | 2 / 2 | +0.00 | [+0.000, +0.000] |
| eig_cost_minus_random | 24 | +0.117 | [-0.075, +0.325] | 9 / 11 | -0.10 | [-0.300, +0.075] |
| eig_cost_minus_lookahead | 24 | +0.000 | [+0.000, +0.000] | 0 / 0 | +0.00 | [+0.000, +0.000] |
| eig_cost_minus_eig_cost_llmP | 24 | +0.450 | [+0.250, +0.658] | 11 / 0 | -0.35 | [-0.542, -0.183] |
| lookahead_minus_eig | 24 | +0.000 | [+0.000, +0.000] | 0 / 0 | +0.00 | [+0.000, +0.000] |
| lookahead_minus_sequential | 24 | +0.050 | [-0.167, +0.258] | 6 / 3 | -0.12 | [-0.342, +0.117] |

All failures remain in the denominator; unknown usage stays null.
