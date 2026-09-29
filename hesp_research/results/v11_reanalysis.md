# v1.1 re-analysis of existing outcomes (review R6)

## 1. Table-source study: security outcomes with numerators and denominators

| Model | Arm | Episodes | Verdicts | Not verified | No verdict | Actionable eps | Benign verdict on actionable | over verdicts | over all actionable |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Qwen2.5-7B | react_style | 72 | 3 | 70 | 69 | 54 | 1 | 1/1 | 1/54 |
| Qwen2.5-7B | memory_only | 72 | 9 | 63 | 63 | 54 | 0 | 0/7 | 0/54 |
| Qwen2.5-7B | hesp_eigc_guard_emp20 | 72 | 72 | 0 | 0 | 54 | 0 | 0/54 | 0/54 |
| Qwen2.5-32B | react_style | 72 | 69 | 28 | 3 | 54 | 13 | 13/51 | 13/54 |
| Qwen2.5-32B | memory_only | 72 | 72 | 18 | 0 | 54 | 2 | 2/54 | 2/54 |
| Qwen2.5-32B | hesp_eigc_guard_emp20 | 72 | 72 | 0 | 0 | 54 | 0 | 0/54 | 0/54 |
| Qwen2.5-72B | react_style | 72 | 72 | 29 | 0 | 54 | 20 | 20/54 | 20/54 |
| Qwen2.5-72B | memory_only | 72 | 71 | 8 | 1 | 54 | 1 | 1/53 | 1/54 |
| Qwen2.5-72B | hesp_eigc_guard_emp20 | 72 | 72 | 0 | 0 | 54 | 0 | 0/54 | 0/54 |

## 2. Sensitivity of confirmed primary endpoints to the clustering unit

| Endpoint | Pre-registered (task clusters) | Cause clusters | Clusters |
| --- | --- | --- | ---: |
| v0.6 7B counted vs Memory-only | +0.875 [+0.750, +0.986] (24) | +0.875 [+0.708, +1.000] | 8 |
| v0.8 ranking Q-7B | +0.306 [+0.125, +0.472] (24) | +0.306 [+0.111, +0.458] | 8 |
| v0.9 P1 controller stop L-8B | +0.917 [+0.792, +1.000] (24) | +0.917 [+0.667, +1.000] | 8 |
| v1.0 PC injection Q-7B | +1.000 [+1.000, +1.000] (6) | +1.000 [+1.000, +1.000] | 6 |

### Leave-one-rule-out, sigma-triage primary endpoints (Qwen2.5-7B)

| Endpoint | Full | Min over left-out rule | Max over left-out rule |
| --- | ---: | ---: | ---: |
| PA1 ranking | +0.171 | +0.157 | +0.191 |
| PA2 full | +0.296 | +0.264 | +0.350 |

## 3. Per-investigation latency (v0.9 controller probes + controller stop; v1.0-A same arm)

| Study | Model | p50 s | p95 s | mean planner calls | mean completion tokens |
| --- | --- | ---: | ---: | ---: | ---: |
| v09 | qwen7b | 2.0 | 5.8 | 2.35 | 72 |
| v09 | llama8b | 2.4 | 6.5 | 2.35 | 87 |
| v09 | qwen32b | 5.5 | 16.8 | 2.35 | 68 |
| v09 | qwen72b | 13.2 | 34.2 | 2.35 | 65 |
| v09 | llama70b | 15.5 | 45.3 | 2.35 | 59 |
| v10a | qwen7b | 1.9 | 3.9 | 2.19 | 67 |
| v10a | llama8b | 3.4 | 5.5 | 2.20 | 83 |
| v10a | qwen32b | 8.3 | 15.6 | 2.20 | 73 |
| v10a | qwen72b | 17.3 | 32.4 | 2.20 | 72 |
| v10a | llama70b | 25.5 | 43.1 | 2.20 | 59 |

Wall time was measured with 32 concurrent episodes sharing one GPU, so it includes queueing.
