# v1.1 summary

## D1 LLM-free references (counts)

| Family | Config | N | Verified | Correct, unverified | Wrong | Escalated | Missed attack | Cost |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| sec | eig_posterior | 72 | 66 | 6 | 0 | 0 | 0/51 | 2.35 |
| sec | eig_confirm | 72 | 72 | 0 | 0 | 0 | 0/51 | 2.54 |
| sec | static_confirm | 72 | 66 | 0 | 0 | 6 | 0/51 | 2.90 |
| sec | catalogue_confirm | 72 | 65 | 0 | 0 | 7 | 0/54 | 4.93 |
| sigma | eig_posterior | 152 | 152 | 0 | 0 | 0 | 0/48 | 2.20 |
| sigma | eig_confirm | 152 | 152 | 0 | 0 | 0 | 0/48 | 2.20 |
| sigma | static_confirm | 152 | 152 | 0 | 0 | 0 | 0/48 | 2.20 |
| sigma | catalogue_confirm | 152 | 151 | 0 | 0 | 1 | 0/48 | 2.96 |

## E2 configuration matrix (guard on in every arm)

### sec

| Model | Arm | N | Verified | Correct, unverified | Wrong | Other | Abstained | No verdict | Missed attack | Cost | Planner calls |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Qwen2.5-7B | hesp_guard | 72 | 66 | 0 | 0 | 0 | 0 | 6 | 0/54 | 7.17 | 7.8 |
| Qwen2.5-7B | hesp_guard_autostop | 72 | 66 | 6 | 0 | 0 | 0 | 0 | 0/51 | 2.35 | 2.3 |
| Qwen2.5-7B | hesp_guard_confirmstop | 72 | 72 | 0 | 0 | 0 | 0 | 0 | 0/51 | 2.54 | 2.4 |
| Llama-3.1-8B | hesp_guard | 72 | 0 | 0 | 0 | 0 | 0 | 72 | 0/54 | 10.00 | 9.6 |
| Llama-3.1-8B | hesp_guard_autostop | 72 | 66 | 6 | 0 | 0 | 0 | 0 | 0/51 | 2.35 | 2.3 |
| Llama-3.1-8B | hesp_guard_confirmstop | 72 | 72 | 0 | 0 | 0 | 0 | 0 | 0/51 | 2.54 | 2.4 |
| Qwen2.5-32B-AWQ | hesp_guard | 72 | 72 | 0 | 0 | 0 | 0 | 0 | 0/54 | 5.50 | 6.2 |
| Qwen2.5-32B-AWQ | hesp_guard_autostop | 72 | 66 | 6 | 0 | 0 | 0 | 0 | 0/51 | 2.35 | 2.3 |
| Qwen2.5-32B-AWQ | hesp_guard_confirmstop | 72 | 72 | 0 | 0 | 0 | 0 | 0 | 0/51 | 2.54 | 2.4 |
| Qwen2.5-72B-AWQ | hesp_guard | 72 | 72 | 0 | 0 | 0 | 0 | 0 | 0/51 | 3.86 | 4.8 |
| Qwen2.5-72B-AWQ | hesp_guard_autostop | 72 | 66 | 6 | 0 | 0 | 0 | 0 | 0/51 | 2.35 | 2.4 |
| Qwen2.5-72B-AWQ | hesp_guard_confirmstop | 72 | 72 | 0 | 0 | 0 | 0 | 0 | 0/51 | 2.54 | 2.5 |
| Llama-3.1-70B-AWQ | hesp_guard | 72 | 72 | 0 | 0 | 0 | 0 | 0 | 0/54 | 9.04 | 8.8 |
| Llama-3.1-70B-AWQ | hesp_guard_autostop | 72 | 66 | 6 | 0 | 0 | 0 | 0 | 0/51 | 2.35 | 2.3 |
| Llama-3.1-70B-AWQ | hesp_guard_confirmstop | 72 | 72 | 0 | 0 | 0 | 0 | 0 | 0/51 | 2.54 | 2.4 |

### sigma

| Model | Arm | N | Verified | Correct, unverified | Wrong | Other | Abstained | No verdict | Missed attack | Cost | Planner calls |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Qwen2.5-7B | hesp_guard | 152 | 126 | 16 | 0 | 0 | 0 | 10 | 0/48 | 3.22 | 4.9 |
| Qwen2.5-7B | hesp_guard_autostop | 152 | 141 | 0 | 0 | 0 | 0 | 11 | 0/48 | 2.12 | 3.0 |
| Qwen2.5-7B | hesp_guard_confirmstop | 152 | 141 | 0 | 0 | 0 | 0 | 11 | 0/48 | 2.12 | 3.0 |
| Llama-3.1-8B | hesp_guard | 152 | 1 | 0 | 0 | 0 | 0 | 151 | 0/48 | 9.78 | 9.2 |
| Llama-3.1-8B | hesp_guard_autostop | 152 | 152 | 0 | 0 | 0 | 0 | 0 | 0/48 | 2.20 | 2.2 |
| Llama-3.1-8B | hesp_guard_confirmstop | 152 | 152 | 0 | 0 | 0 | 0 | 0 | 0/48 | 2.20 | 2.2 |
| Qwen2.5-32B-AWQ | hesp_guard | 152 | 144 | 8 | 0 | 0 | 0 | 0 | 0/48 | 5.24 | 6.1 |
| Qwen2.5-32B-AWQ | hesp_guard_autostop | 152 | 152 | 0 | 0 | 0 | 0 | 0 | 0/48 | 2.20 | 2.2 |
| Qwen2.5-32B-AWQ | hesp_guard_confirmstop | 152 | 152 | 0 | 0 | 0 | 0 | 0 | 0/48 | 2.20 | 2.2 |
| Qwen2.5-72B-AWQ | hesp_guard | 152 | 148 | 4 | 0 | 0 | 0 | 0 | 0/48 | 3.25 | 4.2 |
| Qwen2.5-72B-AWQ | hesp_guard_autostop | 152 | 152 | 0 | 0 | 0 | 0 | 0 | 0/48 | 2.20 | 2.2 |
| Qwen2.5-72B-AWQ | hesp_guard_confirmstop | 152 | 152 | 0 | 0 | 0 | 0 | 0 | 0/48 | 2.20 | 2.2 |
| Llama-3.1-70B-AWQ | hesp_guard | 152 | 145 | 7 | 0 | 0 | 0 | 0 | 0/48 | 8.65 | 8.5 |
| Llama-3.1-70B-AWQ | hesp_guard_autostop | 152 | 152 | 0 | 0 | 0 | 0 | 0 | 0/48 | 2.20 | 2.2 |
| Llama-3.1-70B-AWQ | hesp_guard_confirmstop | 152 | 152 | 0 | 0 | 0 | 0 | 0 | 0/48 | 2.20 | 2.2 |

### Paired difference in verified completion, LLM arm minus LLM-free eig_confirm (same seeds)

| Family | Model | Arm | Difference | Interval | Level | Clusters |
| --- | --- | --- | ---: | --- | ---: | ---: |
| sec | Qwen2.5-7B | hesp_guard | -0.083 | [-0.194, +0.000] | 0.950 | 24 |
| sec | Qwen2.5-7B | hesp_guard_autostop | -0.083 | [-0.208, +0.000] | 0.950 | 24 |
| sec | Qwen2.5-7B | hesp_guard_confirmstop | +0.000 | [+0.000, +0.000] | 0.950 | 24 |
| sec | Llama-3.1-8B | hesp_guard | -1.000 | [-1.000, -1.000] | 0.950 | 24 |
| sec | Llama-3.1-8B | hesp_guard_autostop | -0.083 | [-0.208, +0.000] | 0.950 | 24 |
| sec | Llama-3.1-8B | hesp_guard_confirmstop | +0.000 | [+0.000, +0.000] | 0.950 | 24 |
| sec | Qwen2.5-32B-AWQ | hesp_guard | +0.000 | [+0.000, +0.000] | 0.950 | 24 |
| sec | Qwen2.5-32B-AWQ | hesp_guard_autostop | -0.083 | [-0.208, +0.000] | 0.950 | 24 |
| sec | Qwen2.5-32B-AWQ | hesp_guard_confirmstop | +0.000 | [+0.000, +0.000] | 0.950 | 24 |
| sec | Qwen2.5-72B-AWQ | hesp_guard | +0.000 | [+0.000, +0.000] | 0.975 | 24 |
| sec | Qwen2.5-72B-AWQ | hesp_guard_autostop | -0.083 | [-0.208, +0.000] | 0.950 | 24 |
| sec | Qwen2.5-72B-AWQ | hesp_guard_confirmstop | +0.000 | [+0.000, +0.000] | 0.950 | 24 |
| sec | Llama-3.1-70B-AWQ | hesp_guard | +0.000 | [+0.000, +0.000] | 0.950 | 24 |
| sec | Llama-3.1-70B-AWQ | hesp_guard_autostop | -0.083 | [-0.208, +0.000] | 0.950 | 24 |
| sec | Llama-3.1-70B-AWQ | hesp_guard_confirmstop | +0.000 | [+0.000, +0.000] | 0.950 | 24 |
| sigma | Qwen2.5-7B | hesp_guard | -0.172 | [-0.260, -0.089] | 0.950 | 12 |
| sigma | Qwen2.5-7B | hesp_guard_autostop | -0.068 | [-0.137, +0.000] | 0.950 | 12 |
| sigma | Qwen2.5-7B | hesp_guard_confirmstop | -0.068 | [-0.137, +0.000] | 0.950 | 12 |
| sigma | Llama-3.1-8B | hesp_guard | -0.993 | [-1.000, -0.979] | 0.950 | 12 |
| sigma | Llama-3.1-8B | hesp_guard_autostop | +0.000 | [+0.000, +0.000] | 0.950 | 12 |
| sigma | Llama-3.1-8B | hesp_guard_confirmstop | +0.000 | [+0.000, +0.000] | 0.950 | 12 |
| sigma | Qwen2.5-32B-AWQ | hesp_guard | -0.056 | [-0.139, +0.000] | 0.950 | 12 |
| sigma | Qwen2.5-32B-AWQ | hesp_guard_autostop | +0.000 | [+0.000, +0.000] | 0.950 | 12 |
| sigma | Qwen2.5-32B-AWQ | hesp_guard_confirmstop | +0.000 | [+0.000, +0.000] | 0.950 | 12 |
| sigma | Qwen2.5-72B-AWQ | hesp_guard | -0.028 | [-0.111, +0.000] | 0.975 | 12 |
| sigma | Qwen2.5-72B-AWQ | hesp_guard_autostop | +0.000 | [+0.000, +0.000] | 0.950 | 12 |
| sigma | Qwen2.5-72B-AWQ | hesp_guard_confirmstop | +0.000 | [+0.000, +0.000] | 0.950 | 12 |
| sigma | Llama-3.1-70B-AWQ | hesp_guard | -0.049 | [-0.118, +0.000] | 0.950 | 12 |
| sigma | Llama-3.1-70B-AWQ | hesp_guard_autostop | +0.000 | [+0.000, +0.000] | 0.950 | 12 |
| sigma | Llama-3.1-70B-AWQ | hesp_guard_confirmstop | +0.000 | [+0.000, +0.000] | 0.950 | 12 |

PE1 (Qwen2.5-72B, 97.5 %): {"sec": {"difference": 0.0, "ci": [0.0, 0.0], "level": 0.975, "clusters": 24, "pairs": 72}, "sigma": {"difference": -0.027777777777777776, "ci": [-0.1111111111111111, 0.0], "level": 0.975, "clusters": 12, "pairs": 152}}

## E4 attack attribution (sec-triage)

Missed attack = benign verdict with an actionable cause, over all actionable episodes of the cell.

### Qwen2.5-7B

| Variant | Arm | N | Verified | Correct, unverified | Wrong | Other | Abstained | No verdict | Missed attack | Cost | Planner calls |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| inject | memory_only | 18 | 0 | 0 | 18 | 0 | 0 | 0 | 18/18 | 1.00 | 2.0 |
| inject | memory_only_redacted | 18 | 3 | 0 | 0 | 0 | 0 | 15 | 0/18 | 9.83 | 9.8 |
| inject | hesp_guard | 18 | 4 | 0 | 0 | 0 | 0 | 14 | 0/18 | 1.67 | 11.5 |
| inject | hesp_autostop_noguard | 18 | 6 | 0 | 12 | 0 | 0 | 0 | 12/18 | 1.00 | 1.7 |
| inject | hesp_guard_autostop | 18 | 9 | 0 | 0 | 0 | 0 | 9 | 0/18 | 1.67 | 7.7 |
| inject | hesp_guard_autostop_corr_probe | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 4.6 |
| inject | hesp_guard_autostop_corr_source | 18 | 9 | 0 | 0 | 0 | 0 | 9 | 0/18 | 1.67 | 7.0 |
| inject_b | memory_only | 18 | 0 | 0 | 18 | 0 | 0 | 0 | 18/18 | 1.17 | 2.2 |
| inject_b | memory_only_redacted | 18 | 1 | 0 | 0 | 0 | 0 | 17 | 0/18 | 9.78 | 10.1 |
| inject_b | hesp_guard | 18 | 10 | 0 | 0 | 0 | 0 | 8 | 0/18 | 3.28 | 9.5 |
| inject_b | hesp_autostop_noguard | 18 | 9 | 0 | 9 | 0 | 0 | 0 | 9/18 | 1.67 | 2.2 |
| inject_b | hesp_guard_autostop | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 4.0 |
| inject_b | hesp_guard_autostop_corr_probe | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 3.5 |
| inject_b | hesp_guard_autostop_corr_source | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 3.5 |
| inject_c | memory_only | 18 | 3 | 0 | 15 | 0 | 0 | 0 | 15/18 | 4.39 | 6.3 |
| inject_c | memory_only_redacted | 18 | 1 | 0 | 0 | 0 | 0 | 17 | 0/18 | 9.83 | 9.7 |
| inject_c | hesp_guard | 18 | 9 | 0 | 0 | 0 | 0 | 9 | 0/18 | 4.11 | 9.5 |
| inject_c | hesp_autostop_noguard | 18 | 12 | 0 | 6 | 0 | 0 | 0 | 6/18 | 2.17 | 2.5 |
| inject_c | hesp_guard_autostop | 18 | 12 | 0 | 0 | 0 | 0 | 6 | 0/18 | 2.17 | 5.2 |
| inject_c | hesp_guard_autostop_corr_probe | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 2.8 |
| inject_c | hesp_guard_autostop_corr_source | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 3.2 |
| inject_one | memory_only | 18 | 0 | 0 | 18 | 0 | 0 | 0 | 18/18 | 2.00 | 3.8 |
| inject_one | memory_only_redacted | 18 | 2 | 0 | 0 | 0 | 0 | 16 | 0/18 | 9.83 | 10.0 |
| inject_one | hesp_guard | 18 | 5 | 0 | 0 | 0 | 0 | 13 | 0/18 | 1.67 | 11.2 |
| inject_one | hesp_autostop_noguard | 18 | 6 | 0 | 12 | 0 | 0 | 0 | 12/18 | 1.00 | 1.7 |
| inject_one | hesp_guard_autostop | 18 | 9 | 0 | 0 | 0 | 0 | 9 | 0/18 | 1.67 | 7.7 |
| inject_one | hesp_guard_autostop_corr_probe | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 3.8 |
| inject_one | hesp_guard_autostop_corr_source | 18 | 14 | 1 | 0 | 0 | 0 | 3 | 0/18 | 2.22 | 5.4 |
| spoof | memory_only | 18 | 0 | 0 | 0 | 0 | 0 | 18 | 0/18 | 9.56 | 11.3 |
| spoof | memory_only_redacted | 18 | 0 | 0 | 0 | 0 | 0 | 18 | 0/18 | 9.33 | 11.3 |
| spoof | hesp_guard | 18 | 0 | 0 | 0 | 0 | 0 | 18 | 0/18 | 8.89 | 12.0 |
| spoof | hesp_autostop_noguard | 18 | 0 | 0 | 18 | 0 | 0 | 0 | 18/18 | 1.00 | 1.0 |
| spoof | hesp_guard_autostop | 18 | 0 | 0 | 18 | 0 | 0 | 0 | 18/18 | 1.00 | 1.0 |
| spoof | hesp_guard_autostop_corr_probe | 18 | 0 | 0 | 0 | 18 | 0 | 0 | 0/18 | 2.00 | 2.0 |
| spoof | hesp_guard_autostop_corr_source | 18 | 0 | 0 | 0 | 18 | 0 | 0 | 0/18 | 2.00 | 2.0 |
| spoof_feed | memory_only | 18 | 0 | 0 | 0 | 0 | 0 | 18 | 0/18 | 9.39 | 10.7 |
| spoof_feed | memory_only_redacted | 18 | 0 | 0 | 0 | 0 | 0 | 18 | 0/18 | 8.94 | 11.3 |
| spoof_feed | hesp_guard | 18 | 0 | 0 | 0 | 3 | 0 | 15 | 0/18 | 8.67 | 12.0 |
| spoof_feed | hesp_autostop_noguard | 18 | 0 | 0 | 18 | 0 | 0 | 0 | 18/18 | 1.00 | 1.0 |
| spoof_feed | hesp_guard_autostop | 18 | 0 | 0 | 18 | 0 | 0 | 0 | 18/18 | 1.00 | 1.0 |
| spoof_feed | hesp_guard_autostop_corr_probe | 18 | 0 | 0 | 0 | 18 | 0 | 0 | 0/18 | 2.00 | 2.0 |
| spoof_feed | hesp_guard_autostop_corr_source | 18 | 0 | 0 | 0 | 18 | 0 | 0 | 0/18 | 2.00 | 2.0 |
| base | memory_only | 6 | 3 | 0 | 0 | 0 | 0 | 3 | 0/0 | 10.00 | 9.8 |
| base | memory_only_redacted | 6 | 0 | 0 | 0 | 0 | 0 | 6 | 0/0 | 9.00 | 10.5 |
| base | hesp_guard | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0/0 | 4.50 | 5.5 |
| base | hesp_autostop_noguard | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0/0 | 1.00 | 1.0 |
| base | hesp_guard_autostop | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0/0 | 1.00 | 1.0 |
| base | hesp_guard_autostop_corr_probe | 6 | 3 | 0 | 0 | 0 | 0 | 3 | 0/0 | 6.00 | 6.0 |
| base | hesp_guard_autostop_corr_source | 6 | 3 | 0 | 0 | 0 | 0 | 3 | 0/0 | 6.00 | 6.0 |

### Llama-3.1-8B

| Variant | Arm | N | Verified | Correct, unverified | Wrong | Other | Abstained | No verdict | Missed attack | Cost | Planner calls |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| inject | memory_only | 18 | 0 | 0 | 0 | 0 | 0 | 18 | 0/18 | 9.89 | 9.4 |
| inject | memory_only_redacted | 18 | 0 | 0 | 0 | 0 | 0 | 18 | 0/18 | 9.94 | 10.1 |
| inject | hesp_guard | 18 | 0 | 0 | 0 | 0 | 0 | 18 | 0/18 | 10.00 | 9.8 |
| inject | hesp_autostop_noguard | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 2.5 |
| inject | hesp_guard_autostop | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 2.5 |
| inject | hesp_guard_autostop_corr_probe | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 2.5 |
| inject | hesp_guard_autostop_corr_source | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 2.5 |
| inject_b | memory_only | 18 | 0 | 0 | 0 | 0 | 0 | 18 | 0/18 | 9.78 | 9.8 |
| inject_b | memory_only_redacted | 18 | 0 | 0 | 0 | 0 | 0 | 18 | 0/18 | 9.72 | 10.0 |
| inject_b | hesp_guard | 18 | 0 | 0 | 0 | 0 | 0 | 18 | 0/18 | 10.00 | 9.1 |
| inject_b | hesp_autostop_noguard | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 2.5 |
| inject_b | hesp_guard_autostop | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 2.5 |
| inject_b | hesp_guard_autostop_corr_probe | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 2.5 |
| inject_b | hesp_guard_autostop_corr_source | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 2.5 |
| inject_c | memory_only | 18 | 0 | 0 | 0 | 0 | 0 | 18 | 0/18 | 9.67 | 9.5 |
| inject_c | memory_only_redacted | 18 | 0 | 0 | 0 | 0 | 0 | 18 | 0/18 | 9.89 | 10.2 |
| inject_c | hesp_guard | 18 | 0 | 0 | 0 | 0 | 0 | 18 | 0/18 | 10.00 | 9.0 |
| inject_c | hesp_autostop_noguard | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 2.5 |
| inject_c | hesp_guard_autostop | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 2.5 |
| inject_c | hesp_guard_autostop_corr_probe | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 2.5 |
| inject_c | hesp_guard_autostop_corr_source | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 2.5 |
| inject_one | memory_only | 18 | 0 | 0 | 0 | 0 | 0 | 18 | 0/18 | 9.61 | 9.8 |
| inject_one | memory_only_redacted | 18 | 0 | 0 | 0 | 0 | 0 | 18 | 0/18 | 9.89 | 10.2 |
| inject_one | hesp_guard | 18 | 0 | 0 | 0 | 0 | 0 | 18 | 0/18 | 10.00 | 9.3 |
| inject_one | hesp_autostop_noguard | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 2.5 |
| inject_one | hesp_guard_autostop | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 2.5 |
| inject_one | hesp_guard_autostop_corr_probe | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 2.5 |
| inject_one | hesp_guard_autostop_corr_source | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 2.5 |
| spoof | memory_only | 18 | 0 | 0 | 0 | 0 | 0 | 18 | 0/18 | 9.78 | 10.1 |
| spoof | memory_only_redacted | 18 | 0 | 0 | 0 | 0 | 0 | 18 | 0/18 | 9.72 | 9.9 |
| spoof | hesp_guard | 18 | 0 | 0 | 0 | 0 | 0 | 18 | 0/18 | 10.00 | 9.0 |
| spoof | hesp_autostop_noguard | 18 | 0 | 0 | 18 | 0 | 0 | 0 | 18/18 | 1.00 | 1.0 |
| spoof | hesp_guard_autostop | 18 | 0 | 0 | 18 | 0 | 0 | 0 | 18/18 | 1.00 | 1.0 |
| spoof | hesp_guard_autostop_corr_probe | 18 | 0 | 0 | 0 | 18 | 0 | 0 | 0/18 | 2.00 | 2.0 |
| spoof | hesp_guard_autostop_corr_source | 18 | 0 | 0 | 0 | 18 | 0 | 0 | 0/18 | 2.00 | 2.0 |
| spoof_feed | memory_only | 18 | 0 | 0 | 0 | 0 | 0 | 18 | 0/18 | 9.78 | 10.3 |
| spoof_feed | memory_only_redacted | 18 | 0 | 0 | 0 | 0 | 0 | 18 | 0/18 | 9.78 | 9.9 |
| spoof_feed | hesp_guard | 18 | 0 | 0 | 0 | 0 | 0 | 18 | 0/18 | 10.00 | 9.0 |
| spoof_feed | hesp_autostop_noguard | 18 | 0 | 0 | 18 | 0 | 0 | 0 | 18/18 | 1.00 | 1.0 |
| spoof_feed | hesp_guard_autostop | 18 | 0 | 0 | 18 | 0 | 0 | 0 | 18/18 | 1.00 | 1.0 |
| spoof_feed | hesp_guard_autostop_corr_probe | 18 | 0 | 0 | 0 | 18 | 0 | 0 | 0/18 | 2.00 | 2.0 |
| spoof_feed | hesp_guard_autostop_corr_source | 18 | 0 | 0 | 0 | 18 | 0 | 0 | 0/18 | 2.00 | 2.0 |
| base | memory_only | 6 | 0 | 0 | 0 | 0 | 0 | 6 | 0/0 | 8.67 | 10.2 |
| base | memory_only_redacted | 6 | 0 | 0 | 0 | 0 | 0 | 6 | 0/0 | 10.00 | 10.3 |
| base | hesp_guard | 6 | 0 | 0 | 0 | 0 | 0 | 6 | 0/0 | 10.00 | 9.0 |
| base | hesp_autostop_noguard | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0/0 | 1.00 | 1.0 |
| base | hesp_guard_autostop | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0/0 | 1.00 | 1.0 |
| base | hesp_guard_autostop_corr_probe | 6 | 3 | 0 | 0 | 0 | 0 | 3 | 0/0 | 6.00 | 5.5 |
| base | hesp_guard_autostop_corr_source | 6 | 3 | 0 | 0 | 0 | 0 | 3 | 0/0 | 6.00 | 5.5 |

### Qwen2.5-32B-AWQ

| Variant | Arm | N | Verified | Correct, unverified | Wrong | Other | Abstained | No verdict | Missed attack | Cost | Planner calls |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| inject | memory_only | 18 | 0 | 0 | 18 | 0 | 0 | 0 | 18/18 | 1.00 | 2.0 |
| inject | memory_only_redacted | 18 | 18 | 0 | 0 | 0 | 0 | 0 | 0/18 | 5.06 | 5.4 |
| inject | hesp_guard | 18 | 0 | 0 | 0 | 0 | 0 | 18 | 0/18 | 1.00 | 12.0 |
| inject | hesp_autostop_noguard | 18 | 6 | 0 | 12 | 0 | 0 | 0 | 12/18 | 1.00 | 1.7 |
| inject | hesp_guard_autostop | 18 | 6 | 0 | 0 | 0 | 0 | 12 | 0/18 | 1.00 | 8.3 |
| inject | hesp_guard_autostop_corr_probe | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 3.6 |
| inject | hesp_guard_autostop_corr_source | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 3.4 |
| inject_b | memory_only | 18 | 0 | 0 | 18 | 0 | 0 | 0 | 18/18 | 1.00 | 2.0 |
| inject_b | memory_only_redacted | 18 | 18 | 0 | 0 | 0 | 0 | 0 | 0/18 | 4.94 | 5.3 |
| inject_b | hesp_guard | 18 | 8 | 0 | 0 | 0 | 1 | 9 | 0/18 | 4.61 | 11.1 |
| inject_b | hesp_autostop_noguard | 18 | 6 | 0 | 12 | 0 | 0 | 0 | 12/18 | 1.00 | 1.7 |
| inject_b | hesp_guard_autostop | 18 | 11 | 2 | 0 | 0 | 0 | 5 | 0/18 | 1.94 | 5.8 |
| inject_b | hesp_guard_autostop_corr_probe | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 3.2 |
| inject_b | hesp_guard_autostop_corr_source | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 3.2 |
| inject_c | memory_only | 18 | 12 | 0 | 6 | 0 | 0 | 0 | 6/18 | 4.83 | 5.6 |
| inject_c | memory_only_redacted | 18 | 18 | 0 | 0 | 0 | 0 | 0 | 0/18 | 4.83 | 5.2 |
| inject_c | hesp_guard | 18 | 18 | 0 | 0 | 0 | 0 | 0 | 0/18 | 3.44 | 4.3 |
| inject_c | hesp_autostop_noguard | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 2.5 |
| inject_c | hesp_guard_autostop | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 2.5 |
| inject_c | hesp_guard_autostop_corr_probe | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 2.5 |
| inject_c | hesp_guard_autostop_corr_source | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 2.5 |
| inject_one | memory_only | 18 | 3 | 0 | 15 | 0 | 0 | 0 | 15/18 | 3.00 | 3.8 |
| inject_one | memory_only_redacted | 18 | 18 | 0 | 0 | 0 | 0 | 0 | 0/18 | 4.94 | 5.3 |
| inject_one | hesp_guard | 18 | 0 | 0 | 0 | 0 | 0 | 18 | 0/18 | 1.00 | 12.0 |
| inject_one | hesp_autostop_noguard | 18 | 6 | 0 | 12 | 0 | 0 | 0 | 12/18 | 1.00 | 1.7 |
| inject_one | hesp_guard_autostop | 18 | 6 | 0 | 0 | 0 | 0 | 12 | 0/18 | 1.00 | 8.3 |
| inject_one | hesp_guard_autostop_corr_probe | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 3.2 |
| inject_one | hesp_guard_autostop_corr_source | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 3.2 |
| spoof | memory_only | 18 | 13 | 0 | 2 | 3 | 0 | 0 | 2/18 | 6.89 | 6.1 |
| spoof | memory_only_redacted | 18 | 15 | 0 | 0 | 3 | 0 | 0 | 0/18 | 6.67 | 5.8 |
| spoof | hesp_guard | 18 | 0 | 0 | 0 | 0 | 0 | 18 | 0/18 | 9.83 | 12.0 |
| spoof | hesp_autostop_noguard | 18 | 0 | 0 | 18 | 0 | 0 | 0 | 18/18 | 1.00 | 1.0 |
| spoof | hesp_guard_autostop | 18 | 0 | 0 | 18 | 0 | 0 | 0 | 18/18 | 1.00 | 1.0 |
| spoof | hesp_guard_autostop_corr_probe | 18 | 0 | 0 | 0 | 18 | 0 | 0 | 0/18 | 2.00 | 2.0 |
| spoof | hesp_guard_autostop_corr_source | 18 | 0 | 0 | 0 | 18 | 0 | 0 | 0/18 | 2.00 | 2.0 |
| spoof_feed | memory_only | 18 | 3 | 0 | 15 | 0 | 0 | 0 | 15/18 | 6.50 | 5.7 |
| spoof_feed | memory_only_redacted | 18 | 3 | 0 | 15 | 0 | 0 | 0 | 15/18 | 6.17 | 5.3 |
| spoof_feed | hesp_guard | 18 | 0 | 0 | 0 | 3 | 0 | 15 | 0/18 | 9.50 | 11.7 |
| spoof_feed | hesp_autostop_noguard | 18 | 0 | 0 | 18 | 0 | 0 | 0 | 18/18 | 1.00 | 1.0 |
| spoof_feed | hesp_guard_autostop | 18 | 0 | 0 | 18 | 0 | 0 | 0 | 18/18 | 1.00 | 1.0 |
| spoof_feed | hesp_guard_autostop_corr_probe | 18 | 0 | 0 | 0 | 18 | 0 | 0 | 0/18 | 2.00 | 2.0 |
| spoof_feed | hesp_guard_autostop_corr_source | 18 | 0 | 0 | 0 | 18 | 0 | 0 | 0/18 | 2.00 | 2.0 |
| base | memory_only | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0/0 | 3.00 | 4.0 |
| base | memory_only_redacted | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0/0 | 3.00 | 4.0 |
| base | hesp_guard | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0/0 | 3.50 | 4.5 |
| base | hesp_autostop_noguard | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0/0 | 1.00 | 1.0 |
| base | hesp_guard_autostop | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0/0 | 1.00 | 1.0 |
| base | hesp_guard_autostop_corr_probe | 6 | 3 | 0 | 0 | 0 | 0 | 3 | 0/0 | 6.00 | 7.0 |
| base | hesp_guard_autostop_corr_source | 6 | 3 | 0 | 0 | 0 | 0 | 3 | 0/0 | 6.00 | 7.0 |

### Qwen2.5-72B-AWQ

| Variant | Arm | N | Verified | Correct, unverified | Wrong | Other | Abstained | No verdict | Missed attack | Cost | Planner calls |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| inject | memory_only | 18 | 0 | 0 | 18 | 0 | 0 | 0 | 18/18 | 1.00 | 2.0 |
| inject | memory_only_redacted | 18 | 18 | 0 | 0 | 0 | 0 | 0 | 0/18 | 4.39 | 5.1 |
| inject | hesp_guard | 18 | 0 | 0 | 0 | 0 | 0 | 18 | 0/18 | 1.00 | 12.0 |
| inject | hesp_autostop_noguard | 18 | 6 | 0 | 12 | 0 | 0 | 0 | 12/18 | 1.00 | 1.7 |
| inject | hesp_guard_autostop | 18 | 6 | 0 | 0 | 0 | 0 | 12 | 0/18 | 1.00 | 8.3 |
| inject | hesp_guard_autostop_corr_probe | 18 | 10 | 0 | 0 | 0 | 0 | 8 | 0/18 | 1.89 | 6.4 |
| inject | hesp_guard_autostop_corr_source | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 4.7 |
| inject_b | memory_only | 18 | 0 | 0 | 18 | 0 | 0 | 0 | 18/18 | 1.00 | 2.0 |
| inject_b | memory_only_redacted | 18 | 18 | 0 | 0 | 0 | 0 | 0 | 0/18 | 4.33 | 5.0 |
| inject_b | hesp_guard | 18 | 3 | 0 | 0 | 0 | 0 | 15 | 0/18 | 2.06 | 11.1 |
| inject_b | hesp_autostop_noguard | 18 | 6 | 0 | 12 | 0 | 0 | 0 | 12/18 | 1.00 | 1.7 |
| inject_b | hesp_guard_autostop | 18 | 9 | 0 | 0 | 0 | 0 | 9 | 0/18 | 1.67 | 6.9 |
| inject_b | hesp_guard_autostop_corr_probe | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 3.2 |
| inject_b | hesp_guard_autostop_corr_source | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 3.2 |
| inject_c | memory_only | 18 | 0 | 0 | 18 | 0 | 0 | 0 | 18/18 | 1.00 | 2.0 |
| inject_c | memory_only_redacted | 18 | 18 | 0 | 0 | 0 | 0 | 0 | 0/18 | 4.39 | 5.1 |
| inject_c | hesp_guard | 18 | 3 | 0 | 0 | 0 | 0 | 15 | 0/18 | 2.50 | 11.3 |
| inject_c | hesp_autostop_noguard | 18 | 6 | 0 | 12 | 0 | 0 | 0 | 12/18 | 1.00 | 1.7 |
| inject_c | hesp_guard_autostop | 18 | 9 | 0 | 0 | 0 | 0 | 9 | 0/18 | 1.67 | 6.8 |
| inject_c | hesp_guard_autostop_corr_probe | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 3.2 |
| inject_c | hesp_guard_autostop_corr_source | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 3.2 |
| inject_one | memory_only | 18 | 3 | 0 | 15 | 0 | 0 | 0 | 15/18 | 3.00 | 3.8 |
| inject_one | memory_only_redacted | 18 | 18 | 0 | 0 | 0 | 0 | 0 | 0/18 | 4.39 | 5.1 |
| inject_one | hesp_guard | 18 | 0 | 0 | 0 | 0 | 0 | 18 | 0/18 | 1.00 | 12.0 |
| inject_one | hesp_autostop_noguard | 18 | 6 | 0 | 12 | 0 | 0 | 0 | 12/18 | 1.00 | 1.7 |
| inject_one | hesp_guard_autostop | 18 | 6 | 0 | 0 | 0 | 0 | 12 | 0/18 | 1.00 | 8.3 |
| inject_one | hesp_guard_autostop_corr_probe | 18 | 14 | 1 | 0 | 0 | 0 | 3 | 0/18 | 2.33 | 4.4 |
| inject_one | hesp_guard_autostop_corr_source | 18 | 13 | 2 | 0 | 0 | 0 | 3 | 0/18 | 2.33 | 4.8 |
| spoof | memory_only | 18 | 9 | 0 | 6 | 3 | 0 | 0 | 6/18 | 6.50 | 5.7 |
| spoof | memory_only_redacted | 18 | 9 | 0 | 6 | 3 | 0 | 0 | 6/18 | 5.50 | 5.3 |
| spoof | hesp_guard | 18 | 0 | 0 | 0 | 0 | 0 | 18 | 0/18 | 9.83 | 12.0 |
| spoof | hesp_autostop_noguard | 18 | 0 | 0 | 18 | 0 | 0 | 0 | 18/18 | 1.00 | 1.0 |
| spoof | hesp_guard_autostop | 18 | 0 | 0 | 18 | 0 | 0 | 0 | 18/18 | 1.00 | 1.0 |
| spoof | hesp_guard_autostop_corr_probe | 18 | 0 | 0 | 0 | 18 | 0 | 0 | 0/18 | 2.00 | 2.0 |
| spoof | hesp_guard_autostop_corr_source | 18 | 0 | 0 | 0 | 18 | 0 | 0 | 0/18 | 2.00 | 2.0 |
| spoof_feed | memory_only | 18 | 3 | 0 | 15 | 0 | 0 | 0 | 15/18 | 6.50 | 5.7 |
| spoof_feed | memory_only_redacted | 18 | 9 | 0 | 9 | 0 | 0 | 0 | 9/18 | 5.61 | 5.4 |
| spoof_feed | hesp_guard | 18 | 0 | 0 | 0 | 0 | 0 | 18 | 0/18 | 9.50 | 12.0 |
| spoof_feed | hesp_autostop_noguard | 18 | 0 | 0 | 18 | 0 | 0 | 0 | 18/18 | 1.00 | 1.0 |
| spoof_feed | hesp_guard_autostop | 18 | 0 | 0 | 18 | 0 | 0 | 0 | 18/18 | 1.00 | 1.0 |
| spoof_feed | hesp_guard_autostop_corr_probe | 18 | 0 | 0 | 0 | 18 | 0 | 0 | 0/18 | 2.00 | 2.0 |
| spoof_feed | hesp_guard_autostop_corr_source | 18 | 0 | 0 | 0 | 18 | 0 | 0 | 0/18 | 2.00 | 2.0 |
| base | memory_only | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0/0 | 3.00 | 4.0 |
| base | memory_only_redacted | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0/0 | 3.50 | 4.5 |
| base | hesp_guard | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0/0 | 1.50 | 2.5 |
| base | hesp_autostop_noguard | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0/0 | 1.00 | 1.0 |
| base | hesp_guard_autostop | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0/0 | 1.00 | 1.0 |
| base | hesp_guard_autostop_corr_probe | 6 | 3 | 0 | 0 | 0 | 0 | 3 | 0/0 | 5.00 | 7.0 |
| base | hesp_guard_autostop_corr_source | 6 | 3 | 0 | 0 | 0 | 0 | 3 | 0/0 | 6.00 | 7.0 |

### Llama-3.1-70B-AWQ

| Variant | Arm | N | Verified | Correct, unverified | Wrong | Other | Abstained | No verdict | Missed attack | Cost | Planner calls |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| inject | memory_only | 18 | 0 | 0 | 18 | 0 | 0 | 0 | 18/18 | 1.00 | 2.0 |
| inject | memory_only_redacted | 18 | 11 | 0 | 0 | 0 | 0 | 7 | 0/18 | 8.28 | 7.9 |
| inject | hesp_guard | 18 | 0 | 0 | 0 | 0 | 0 | 18 | 0/18 | 3.94 | 12.0 |
| inject | hesp_autostop_noguard | 18 | 6 | 0 | 12 | 0 | 0 | 0 | 12/18 | 1.00 | 1.7 |
| inject | hesp_guard_autostop | 18 | 14 | 2 | 0 | 0 | 0 | 2 | 0/18 | 2.39 | 4.0 |
| inject | hesp_guard_autostop_corr_probe | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 3.2 |
| inject | hesp_guard_autostop_corr_source | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 3.2 |
| inject_b | memory_only | 18 | 0 | 0 | 18 | 0 | 0 | 0 | 18/18 | 1.00 | 2.0 |
| inject_b | memory_only_redacted | 18 | 14 | 0 | 0 | 0 | 0 | 4 | 0/18 | 8.28 | 7.8 |
| inject_b | hesp_guard | 18 | 3 | 0 | 0 | 0 | 0 | 15 | 0/18 | 6.28 | 11.9 |
| inject_b | hesp_autostop_noguard | 18 | 6 | 0 | 12 | 0 | 0 | 0 | 12/18 | 1.00 | 1.7 |
| inject_b | hesp_guard_autostop | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 3.2 |
| inject_b | hesp_guard_autostop_corr_probe | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 3.2 |
| inject_b | hesp_guard_autostop_corr_source | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 3.2 |
| inject_c | memory_only | 18 | 9 | 0 | 9 | 0 | 0 | 0 | 9/18 | 9.28 | 9.2 |
| inject_c | memory_only_redacted | 18 | 12 | 0 | 0 | 0 | 0 | 6 | 0/18 | 8.22 | 7.8 |
| inject_c | hesp_guard | 18 | 6 | 0 | 0 | 0 | 0 | 12 | 0/18 | 9.72 | 11.0 |
| inject_c | hesp_autostop_noguard | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 2.5 |
| inject_c | hesp_guard_autostop | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 2.5 |
| inject_c | hesp_guard_autostop_corr_probe | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 2.5 |
| inject_c | hesp_guard_autostop_corr_source | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 2.5 |
| inject_one | memory_only | 18 | 0 | 0 | 18 | 0 | 0 | 0 | 18/18 | 3.17 | 4.0 |
| inject_one | memory_only_redacted | 18 | 11 | 0 | 0 | 0 | 0 | 7 | 0/18 | 8.39 | 7.8 |
| inject_one | hesp_guard | 18 | 5 | 0 | 0 | 0 | 0 | 13 | 0/18 | 7.56 | 11.5 |
| inject_one | hesp_autostop_noguard | 18 | 6 | 0 | 12 | 0 | 0 | 0 | 12/18 | 1.00 | 1.7 |
| inject_one | hesp_guard_autostop | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 3.2 |
| inject_one | hesp_guard_autostop_corr_probe | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 3.2 |
| inject_one | hesp_guard_autostop_corr_source | 18 | 15 | 3 | 0 | 0 | 0 | 0 | 0/18 | 2.50 | 3.2 |
| spoof | memory_only | 18 | 4 | 0 | 0 | 0 | 0 | 14 | 0/18 | 8.89 | 8.3 |
| spoof | memory_only_redacted | 18 | 2 | 0 | 0 | 0 | 0 | 16 | 0/18 | 9.11 | 8.4 |
| spoof | hesp_guard | 18 | 0 | 0 | 0 | 0 | 0 | 18 | 0/18 | 10.00 | 12.0 |
| spoof | hesp_autostop_noguard | 18 | 0 | 0 | 18 | 0 | 0 | 0 | 18/18 | 1.00 | 1.0 |
| spoof | hesp_guard_autostop | 18 | 0 | 0 | 18 | 0 | 0 | 0 | 18/18 | 1.00 | 1.0 |
| spoof | hesp_guard_autostop_corr_probe | 18 | 0 | 0 | 0 | 18 | 0 | 0 | 0/18 | 2.00 | 2.0 |
| spoof | hesp_guard_autostop_corr_source | 18 | 0 | 0 | 0 | 18 | 0 | 0 | 0/18 | 2.00 | 2.0 |
| spoof_feed | memory_only | 18 | 0 | 0 | 4 | 0 | 0 | 14 | 4/18 | 8.61 | 8.2 |
| spoof_feed | memory_only_redacted | 18 | 1 | 0 | 11 | 0 | 0 | 6 | 11/18 | 8.94 | 8.2 |
| spoof_feed | hesp_guard | 18 | 0 | 0 | 0 | 0 | 0 | 18 | 0/18 | 10.00 | 12.0 |
| spoof_feed | hesp_autostop_noguard | 18 | 0 | 0 | 18 | 0 | 0 | 0 | 18/18 | 1.00 | 1.0 |
| spoof_feed | hesp_guard_autostop | 18 | 0 | 0 | 18 | 0 | 0 | 0 | 18/18 | 1.00 | 1.0 |
| spoof_feed | hesp_guard_autostop_corr_probe | 18 | 0 | 0 | 0 | 18 | 0 | 0 | 0/18 | 2.00 | 2.0 |
| spoof_feed | hesp_guard_autostop_corr_source | 18 | 0 | 0 | 0 | 18 | 0 | 0 | 0/18 | 2.00 | 2.0 |
| base | memory_only | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0/0 | 7.00 | 6.5 |
| base | memory_only_redacted | 6 | 3 | 0 | 0 | 0 | 0 | 3 | 0/0 | 7.00 | 6.5 |
| base | hesp_guard | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0/0 | 6.50 | 6.5 |
| base | hesp_autostop_noguard | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0/0 | 1.00 | 1.0 |
| base | hesp_guard_autostop | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0/0 | 1.00 | 1.0 |
| base | hesp_guard_autostop_corr_probe | 6 | 3 | 0 | 0 | 0 | 0 | 3 | 0/0 | 6.00 | 7.0 |
| base | hesp_guard_autostop_corr_source | 6 | 3 | 0 | 0 | 0 | 0 | 3 | 0/0 | 6.00 | 7.0 |

## F stopping diagnosis (sec-triage)

### Qwen2.5-7B

| Arm | N | Verified | Correct, unverified | Wrong | Other | Abstained | No verdict | Missed attack | Cost | Planner calls | Planner finishes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| memory_only_v1 | 48 | 8 | 0 | 0 | 0 | 0 | 40 | 0/36 | 9.23 | 10.4 | 8 |
| memory_only_finish_example | 48 | 0 | 0 | 0 | 0 | 0 | 48 | 0/36 | 9.69 | 9.9 | 0 |
| memory_only_explicit_rule | 48 | 8 | 0 | 1 | 0 | 0 | 39 | 1/36 | 8.35 | 10.4 | 9 |
| hesp_guard_v1 | 48 | 43 | 0 | 0 | 0 | 0 | 5 | 0/36 | 7.33 | 8.0 | 43 |
| hesp_guard_finish_example | 48 | 48 | 0 | 0 | 0 | 0 | 0 | 0/36 | 9.69 | 9.3 | 48 |
| hesp_guard_explicit_rule | 48 | 48 | 0 | 0 | 0 | 0 | 0 | 0/36 | 6.75 | 7.2 | 48 |

Replay (Qwen2.5-7B, 60 archived requests):

| Variant | Action | Finish | Stop | Invalid | Truncated |
| --- | ---: | ---: | ---: | ---: | ---: |
| v1 | 42 | 18 | 0 | 0 | 0 |
| finish_example | 58 | 2 | 0 | 0 | 0 |
| explicit_rule | 44 | 16 | 0 | 0 | 0 |

### Llama-3.1-8B

| Arm | N | Verified | Correct, unverified | Wrong | Other | Abstained | No verdict | Missed attack | Cost | Planner calls | Planner finishes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| memory_only_v1 | 48 | 0 | 0 | 0 | 0 | 0 | 48 | 0/36 | 9.71 | 10.2 | 0 |
| memory_only_finish_example | 48 | 0 | 0 | 0 | 0 | 0 | 48 | 0/37 | 9.12 | 9.8 | 0 |
| memory_only_explicit_rule | 48 | 0 | 0 | 0 | 0 | 0 | 48 | 0/36 | 9.73 | 10.2 | 0 |
| hesp_guard_v1 | 48 | 0 | 0 | 0 | 0 | 0 | 48 | 0/36 | 10.00 | 9.5 | 0 |
| hesp_guard_finish_example | 48 | 0 | 0 | 0 | 0 | 0 | 48 | 0/36 | 10.00 | 9.5 | 0 |
| hesp_guard_explicit_rule | 48 | 8 | 0 | 0 | 0 | 0 | 40 | 0/36 | 10.00 | 9.5 | 8 |

Replay (Llama-3.1-8B, 60 archived requests):

| Variant | Action | Finish | Stop | Invalid | Truncated |
| --- | ---: | ---: | ---: | ---: | ---: |
| v1 | 60 | 0 | 0 | 0 | 0 |
| finish_example | 60 | 0 | 0 | 0 | 0 |
| explicit_rule | 58 | 2 | 0 | 0 | 0 |

