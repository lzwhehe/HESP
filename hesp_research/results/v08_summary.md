### Primary endpoints (97.5 % task-cluster intervals, Bonferroni over two)

| Endpoint | Model | Comparison | Δ verified | 97.5 % interval | tasks better / worse | confirmed |
| --- | --- | --- | ---: | --- | ---: | --- |
| P1 | Llama-3.1-8B | hesp_eigc_guard − memory_only | +0.000 | [+0.000, +0.000] | 0 / 0 | no |
| P2 | Qwen2.5-7B | hesp_eigc_blind − hesp_random_blind | +0.306 | [+0.139, +0.472] | 14 / 1 | yes |

### Verified completion by arm

| Arm | Qwen2.5-7B | Qwen2.5-32B-AWQ | Qwen2.5-72B-AWQ | Llama-3.1-8B | Llama-3.1-70B-AWQ |
| --- | ---: | ---: | ---: | ---: | ---: |
| memory_only | 0.083 | 0.875 | 0.847 | 0.000 | 0.833 |
| hesp_random_blind | 0.639 | 0.653 | 0.569 | 0.000 | 0.736 |
| hesp_eigc_blind | 0.944 | 1.000 | 0.917 | 0.000 | 1.000 |
| hesp_eigc | 1.000 | 1.000 | 0.958 | 0.000 | 1.000 |
| hesp_eigc_guard | 1.000 | 1.000 | 1.000 | 0.000 | 1.000 |

### Mean probe cost by arm

| Arm | Qwen2.5-7B | Qwen2.5-32B-AWQ | Qwen2.5-72B-AWQ | Llama-3.1-8B | Llama-3.1-70B-AWQ |
| --- | ---: | ---: | ---: | ---: | ---: |
| memory_only | 9.46 | 5.44 | 5.74 | 9.68 | 8.64 |
| hesp_random_blind | 9.26 | 8.10 | 6.36 | 9.97 | 9.86 |
| hesp_eigc_blind | 7.32 | 5.57 | 3.61 | 10.00 | 9.14 |
| hesp_eigc | 9.44 | 6.11 | 5.08 | 10.00 | 9.36 |
| hesp_eigc_guard | 9.44 | 6.11 | 5.33 | 10.00 | 9.36 |

### Decomposition (Δ verified; 95 % intervals except the two primary cells, which are 97.5 %)

| Term | Qwen2.5-7B | Qwen2.5-32B-AWQ | Qwen2.5-72B-AWQ | Llama-3.1-8B | Llama-3.1-70B-AWQ |
| --- | --- | --- | --- | --- | --- |
| HESP vs Memory-only | +0.917 [+0.833, +0.986] | +0.125 [+0.028, +0.250] | +0.153 [+0.042, +0.292] | +0.000 [+0.000, +0.000] | +0.167 [+0.056, +0.292] |
| hand probe choice to controller | +0.556 [+0.403, +0.708] | -0.222 [-0.375, -0.083] | -0.278 [-0.431, -0.125] | +0.000 [+0.000, +0.000] | -0.097 [-0.278, +0.056] |
| EIG/c ranking itself | +0.306 [+0.139, +0.472] | +0.347 [+0.222, +0.486] | +0.347 [+0.181, +0.500] | +0.000 [+0.000, +0.000] | +0.264 [+0.139, +0.403] |
| show ranking to planner | +0.056 [+0.000, +0.153] | +0.000 [+0.000, +0.000] | +0.042 [-0.083, +0.208] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| finish guard | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.042 [+0.000, +0.125] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |

### Security-facing metrics (descriptive): missed attack / false escalation / unresolved

| Arm | Qwen2.5-7B | Qwen2.5-32B-AWQ | Qwen2.5-72B-AWQ | Llama-3.1-8B | Llama-3.1-70B-AWQ |
| --- | --- | --- | --- | --- | --- |
| memory_only | 0.14 / n/a / 0.92 | 0.02 / 0.00 / 0.12 | 0.00 / 0.00 / 0.15 | n/a / n/a / 1.00 | 0.02 / 0.00 / 0.17 |
| hesp_random_blind | 0.19 / 0.17 / 0.36 | 0.26 / 0.06 / 0.35 | 0.24 / 0.12 / 0.43 | n/a / n/a / 1.00 | 0.26 / 0.00 / 0.26 |
| hesp_eigc_blind | 0.07 / 0.00 / 0.06 | 0.00 / 0.00 / 0.00 | 0.06 / 0.14 / 0.08 | n/a / n/a / 1.00 | 0.00 / 0.00 / 0.00 |
| hesp_eigc | 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 | 0.06 / 0.00 / 0.04 | n/a / n/a / 1.00 | 0.00 / 0.00 / 0.00 |
| hesp_eigc_guard | 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 | n/a / n/a / 1.00 | 0.00 / 0.00 / 0.00 |
