### Primary endpoints (97.5 % task-cluster intervals, Bonferroni over two)

| Endpoint | Model | Comparison | Δ verified | 97.5 % interval | tasks better / worse | confirmed |
| --- | --- | --- | ---: | --- | ---: | --- |
| P1 | Llama-3.1-8B | hesp_eigc_blind_autostop − hesp_eigc_blind | +0.917 | [+0.792, +1.000] | 22 / 0 | yes |
| P2 | Llama-3.1-8B | hesp_eigc_blind_autostop − memory_only_autostop | +0.056 | [-0.069, +0.181] | 4 / 2 | no |

### Verified completion by arm

| Arm | Qwen2.5-7B | Qwen2.5-32B-AWQ | Qwen2.5-72B-AWQ | Llama-3.1-8B | Llama-3.1-70B-AWQ |
| --- | ---: | ---: | ---: | ---: | ---: |
| memory_only | 0.083 | 0.903 | 0.861 | 0.000 | 0.889 |
| memory_only_autostop | 0.694 | 0.819 | 0.833 | 0.861 | 0.889 |
| hesp_eigc_blind | 0.931 | 1.000 | 0.917 | 0.000 | 1.000 |
| hesp_eigc_blind_autostop | 0.917 | 0.917 | 0.875 | 0.917 | 0.917 |
| hesp_random_blind_autostop | 0.736 | 0.708 | 0.694 | 0.750 | 0.750 |

### Mean probe cost by arm

| Arm | Qwen2.5-7B | Qwen2.5-32B-AWQ | Qwen2.5-72B-AWQ | Llama-3.1-8B | Llama-3.1-70B-AWQ |
| --- | ---: | ---: | ---: | ---: | ---: |
| memory_only | 9.50 | 5.22 | 5.61 | 9.72 | 8.56 |
| memory_only_autostop | 5.18 | 4.06 | 4.11 | 4.78 | 4.42 |
| hesp_eigc_blind | 7.19 | 5.49 | 3.57 | 10.00 | 9.04 |
| hesp_eigc_blind_autostop | 2.35 | 2.35 | 2.31 | 2.35 | 2.35 |
| hesp_random_blind_autostop | 6.42 | 6.04 | 5.44 | 6.43 | 6.43 |

### Decomposition (Δ verified; 95 % intervals except the two primary cells, which are 97.5 %)

| Term | Qwen2.5-7B | Qwen2.5-32B-AWQ | Qwen2.5-72B-AWQ | Llama-3.1-8B | Llama-3.1-70B-AWQ |
| --- | --- | --- | --- | --- | --- |
| controller stop (controller probes) | -0.014 [-0.167, +0.125] | -0.083 [-0.208, +0.000] | -0.042 [-0.167, +0.083] | +0.917 [+0.792, +1.000] | -0.083 [-0.208, +0.000] |
| who probes, stop supplied | +0.222 [+0.083, +0.389] | +0.097 [+0.000, +0.222] | +0.042 [-0.083, +0.167] | +0.056 [-0.069, +0.181] | +0.028 [-0.097, +0.153] |
| controller stop (LLM probes) | +0.611 [+0.431, +0.778] | -0.083 [-0.194, +0.000] | -0.028 [-0.125, +0.042] | +0.861 [+0.750, +0.958] | +0.000 [-0.139, +0.139] |
| EIG/c ranking under controller stop | +0.181 [+0.056, +0.306] | +0.208 [+0.069, +0.333] | +0.181 [+0.042, +0.319] | +0.167 [+0.042, +0.292] | +0.167 [+0.042, +0.292] |
| controller probes, LLM stops (v0.8 replication) | +0.847 [+0.708, +0.958] | +0.097 [+0.000, +0.222] | +0.056 [-0.125, +0.236] | +0.000 [+0.000, +0.000] | +0.111 [+0.028, +0.208] |

### Security-facing metrics (descriptive): missed attack / false escalation / unresolved

| Arm | Qwen2.5-7B | Qwen2.5-32B-AWQ | Qwen2.5-72B-AWQ | Llama-3.1-8B | Llama-3.1-70B-AWQ |
| --- | --- | --- | --- | --- | --- |
| memory_only | 0.00 / 0.00 / 0.92 | 0.00 / 0.00 / 0.10 | 0.02 / 0.00 / 0.14 | n/a / n/a / 1.00 | 0.00 / 0.00 / 0.11 |
| memory_only_autostop | 0.00 / 0.00 / 0.31 | 0.00 / 0.00 / 0.18 | 0.00 / 0.00 / 0.17 | 0.00 / 0.00 / 0.14 | 0.00 / 0.00 / 0.11 |
| hesp_eigc_blind | 0.07 / 0.00 / 0.07 | 0.00 / 0.00 / 0.00 | 0.06 / 0.14 / 0.08 | n/a / n/a / 1.00 | 0.00 / 0.00 / 0.00 |
| hesp_eigc_blind_autostop | 0.00 / 0.00 / 0.08 | 0.00 / 0.00 / 0.08 | 0.00 / 0.14 / 0.12 | 0.00 / 0.00 / 0.08 | 0.00 / 0.00 / 0.08 |
| hesp_random_blind_autostop | 0.08 / 0.00 / 0.26 | 0.13 / 0.00 / 0.29 | 0.15 / 0.00 / 0.31 | 0.00 / 0.00 / 0.25 | 0.09 / 0.00 / 0.25 |

### Who concluded: planner / controller / nobody (episodes)

| Arm | Qwen2.5-7B | Qwen2.5-32B-AWQ | Qwen2.5-72B-AWQ | Llama-3.1-8B | Llama-3.1-70B-AWQ |
| --- | --- | --- | --- | --- | --- |
| memory_only | 6 / 0 / 66 | 72 / 0 / 0 | 71 / 0 / 1 | 0 / 0 / 72 | 64 / 0 / 8 |
| memory_only_autostop | 0 / 66 / 6 | 8 / 64 / 0 | 9 / 63 / 0 | 0 / 71 / 1 | 0 / 71 / 1 |
| hesp_eigc_blind | 72 / 0 / 0 | 72 / 0 / 0 | 72 / 0 / 0 | 0 / 0 / 72 | 72 / 0 / 0 |
| hesp_eigc_blind_autostop | 0 / 72 / 0 | 0 / 72 / 0 | 3 / 69 / 0 | 0 / 72 / 0 | 0 / 72 / 0 |
| hesp_random_blind_autostop | 9 / 63 / 0 | 17 / 55 / 0 | 31 / 41 / 0 | 0 / 64 / 8 | 8 / 64 / 0 |
