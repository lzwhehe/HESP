# v0.4 results across models

Verified completion rate per arm (72 episodes per cell: 24 tasks x 3 repeats). Differences are paired per task, 95% task-cluster bootstrap intervals.

## upload-diag (held-out, primary)

| Arm | Qwen2.5-7B | Qwen2.5-32B-AWQ | Qwen2.5-72B-AWQ |
| --- | ---: | ---: | ---: |
| react_style | 0.194 | **0.875** | 0.806 |
| memory_only | 0.236 | **0.944** | 0.819 |
| memory_guard | 0.236 | **0.958** | 0.847 |
| hesp_eigc | **1.000** | 0.875 | 0.917 |
| hesp_eigc_guard | **1.000** | **1.000** | **1.000** |
| hesp_la | 0.875 | 0.819 | **0.889** |
| hesp_la_guard | 0.861 | **0.944** | 0.931 |
| hesp_random | 0.847 | **0.889** | **0.889** |
| hesp_llmp | 0.792 | 0.806 | **0.833** |

| Comparison | Qwen2.5-7B | Qwen2.5-32B-AWQ | Qwen2.5-72B-AWQ |
| --- | --- | --- | --- |
| hesp_la_guard_minus_memory_only (primary) | +0.625 [+0.44, +0.79] | +0.000 [-0.12, +0.12] | +0.111 [+0.03, +0.22] |
| hesp_eigc_minus_memory_only | +0.764 [+0.58, +0.92] | -0.069 [-0.24, +0.10] | +0.097 [+0.00, +0.22] |
| memory_only_minus_react_style | +0.042 [+0.00, +0.12] | +0.069 [+0.00, +0.17] | +0.014 [+0.00, +0.04] |
| memory_guard_minus_memory_only | +0.000 [+0.00, +0.00] | +0.014 [+0.00, +0.04] | +0.028 [+0.00, +0.07] |
| hesp_eigc_guard_minus_hesp_eigc | +0.000 [+0.00, +0.00] | +0.125 [+0.00, +0.25] | +0.083 [+0.00, +0.21] |
| hesp_la_minus_hesp_eigc | -0.125 [-0.25, -0.03] | -0.056 [-0.19, +0.07] | -0.028 [-0.14, +0.07] |
| hesp_eigc_minus_hesp_random | +0.153 [+0.08, +0.24] | -0.014 [-0.15, +0.11] | +0.028 [-0.12, +0.15] |
| hesp_eigc_minus_hesp_llmp | +0.208 [+0.08, +0.35] | +0.069 [-0.07, +0.22] | +0.083 [+0.01, +0.18] |

| Mean tool cost | Qwen2.5-7B | Qwen2.5-32B-AWQ | Qwen2.5-72B-AWQ |
| --- | ---: | ---: | ---: |
| react_style | 1.25 | 5.38 | 4.25 |
| memory_only | 1.00 | 5.19 | 4.21 |
| memory_guard | 1.03 | 5.21 | 4.44 |
| hesp_eigc | 3.35 | 3.60 | 3.06 |
| hesp_eigc_guard | 3.35 | 4.18 | 3.31 |
| hesp_la | 4.40 | 5.68 | 4.43 |
| hesp_la_guard | 4.40 | 6.21 | 4.60 |
| hesp_random | 6.43 | 5.69 | 5.25 |
| hesp_llmp | 5.40 | 5.61 | 4.03 |

## web-diag (development)

| Arm | Qwen2.5-7B | Qwen2.5-32B-AWQ | Qwen2.5-72B-AWQ |
| --- | ---: | ---: | ---: |
| react_style | 0.444 | 0.681 | **0.750** |
| memory_only | 0.639 | **0.889** | 0.806 |
| memory_guard | 0.750 | **0.944** | **0.944** |
| hesp_eigc | 0.750 | 0.764 | **0.806** |
| hesp_eigc_guard | 0.819 | **0.972** | 0.806 |
| hesp_la | 0.958 | **0.972** | **0.972** |
| hesp_la_guard | **0.972** | **0.972** | **0.972** |
| hesp_random | 0.889 | **0.903** | 0.875 |
| hesp_llmp | **1.000** | 0.931 | 0.958 |

| Comparison | Qwen2.5-7B | Qwen2.5-32B-AWQ | Qwen2.5-72B-AWQ |
| --- | --- | --- | --- |
| hesp_la_guard_minus_memory_only | +0.333 [+0.17, +0.50] | +0.083 [-0.01, +0.19] | +0.167 [+0.04, +0.33] |
| hesp_eigc_minus_memory_only | +0.111 [-0.08, +0.29] | -0.125 [-0.28, +0.00] | -0.000 [-0.17, +0.15] |
| memory_only_minus_react_style | +0.194 [+0.07, +0.33] | +0.208 [+0.07, +0.36] | +0.056 [-0.08, +0.18] |
| memory_guard_minus_memory_only | +0.111 [+0.03, +0.19] | +0.056 [+0.01, +0.11] | +0.139 [+0.03, +0.28] |
| hesp_eigc_guard_minus_hesp_eigc | +0.069 [+0.00, +0.18] | +0.208 [+0.07, +0.38] | +0.000 [+0.00, +0.00] |
| hesp_la_minus_hesp_eigc | +0.208 [+0.06, +0.39] | +0.208 [+0.06, +0.39] | +0.167 [+0.01, +0.33] |
| hesp_eigc_minus_hesp_random | -0.139 [-0.32, +0.03] | -0.139 [-0.32, +0.01] | -0.069 [-0.22, +0.07] |
| hesp_eigc_minus_hesp_llmp | -0.250 [-0.42, -0.10] | -0.167 [-0.32, -0.03] | -0.153 [-0.31, -0.01] |

| Mean tool cost | Qwen2.5-7B | Qwen2.5-32B-AWQ | Qwen2.5-72B-AWQ |
| --- | ---: | ---: | ---: |
| react_style | 2.79 | 4.04 | 3.78 |
| memory_only | 3.53 | 3.67 | 4.07 |
| memory_guard | 4.18 | 3.92 | 4.44 |
| hesp_eigc | 4.01 | 3.86 | 3.36 |
| hesp_eigc_guard | 4.24 | 4.86 | 3.36 |
| hesp_la | 4.04 | 3.64 | 3.64 |
| hesp_la_guard | 4.04 | 3.72 | 3.64 |
| hesp_random | 5.61 | 5.24 | 4.90 |
| hesp_llmp | 4.08 | 5.10 | 3.97 |

## Self-elicited predictive tables vs the sandbox generator (base variant)

| Model | family | KL (bits) | Brier | argmax agreement | fallback rows |
| --- | --- | ---: | ---: | ---: | ---: |
| Qwen2.5-7B | upload-diag | 0.86 | 0.377 | 0.73 | 0 |
| Qwen2.5-7B | web-diag | 1.46 | 0.549 | 0.52 | 0 |
| Qwen2.5-32B-AWQ | upload-diag | 1.27 | 0.501 | 0.76 | 7 |
| Qwen2.5-32B-AWQ | web-diag | 1.76 | 0.658 | 0.56 | 0 |
| Qwen2.5-72B-AWQ | upload-diag | 1.08 | 0.339 | 0.88 | 1 |
| Qwen2.5-72B-AWQ | web-diag | 1.23 | 0.460 | 0.65 | 0 |
