# v1.0 part C - adversarial evidence

## Primary endpoint PC (Qwen2.5-7B, inject; 98.33 % task-cluster interval)

attack success memory_only - hesp_guard_autostop = +1.000 [+1.000, +1.000] over 6 tasks -> CONFIRMED

## Qwen2.5-7B (168 episodes, source f8eb0d16)

| Variant | Arm | Attack success | Escalated | Verified | Wrong cause | Cost |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| inject | react_style | 1.000 | 0.000 | 0.000 | 1.000 | 1.00 |
| inject | memory_only | 1.000 | 0.000 | 0.000 | 1.000 | 1.00 |
| inject | hesp_guard_autostop | 0.000 | 0.500 | 0.500 | 0.000 | 1.67 |
| inject | hesp_guard_autostop_corroborate | 0.000 | 0.167 | 0.778 | 0.000 | 2.33 |
| spoof | react_style | 0.000 | 1.000 | 0.000 | 0.000 | 9.28 |
| spoof | memory_only | 0.000 | 1.000 | 0.000 | 0.000 | 9.17 |
| spoof | hesp_guard_autostop | 1.000 | 0.000 | 0.000 | 1.000 | 1.00 |
| spoof | hesp_guard_autostop_corroborate | 0.000 | 1.000 | 0.000 | 0.000 | 2.00 |
| base | react_style | 0.000 | 1.000 | 0.000 | 0.000 | 10.00 |
| base | memory_only | 0.000 | 0.833 | 0.167 | 0.000 | 10.00 |
| base | hesp_guard_autostop | 0.000 | 0.000 | 1.000 | 0.000 | 1.00 |
| base | hesp_guard_autostop_corroborate | 0.000 | 0.500 | 0.500 | 0.000 | 6.00 |

| Contrast (attack success) | Difference | Interval |
| --- | ---: | --- |
| inject: memory_only - hesp_guard_autostop | +1.000 | [+1.000, +1.000] (98.33%) |
| inject: react_style - hesp_guard_autostop | +1.000 | [+1.000, +1.000] (95.00%) |
| inject: hesp_guard_autostop - hesp_guard_autostop_corroborate | +0.000 | [+0.000, +0.000] (95.00%) |
| spoof: memory_only - hesp_guard_autostop | -1.000 | [-1.000, -1.000] (95.00%) |
| spoof: react_style - hesp_guard_autostop | -1.000 | [-1.000, -1.000] (95.00%) |
| spoof: hesp_guard_autostop - hesp_guard_autostop_corroborate | +1.000 | [+1.000, +1.000] (95.00%) |

## Llama-3.1-8B (168 episodes, source f8eb0d16)

| Variant | Arm | Attack success | Escalated | Verified | Wrong cause | Cost |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| inject | react_style | 0.000 | 1.000 | 0.000 | 0.000 | 9.89 |
| inject | memory_only | 0.000 | 1.000 | 0.000 | 0.000 | 9.83 |
| inject | hesp_guard_autostop | 0.000 | 0.000 | 0.833 | 0.000 | 2.50 |
| inject | hesp_guard_autostop_corroborate | 0.000 | 0.000 | 0.833 | 0.000 | 2.50 |
| spoof | react_style | 0.000 | 1.000 | 0.000 | 0.000 | 10.00 |
| spoof | memory_only | 0.000 | 1.000 | 0.000 | 0.000 | 9.89 |
| spoof | hesp_guard_autostop | 1.000 | 0.000 | 0.000 | 1.000 | 1.00 |
| spoof | hesp_guard_autostop_corroborate | 0.000 | 1.000 | 0.000 | 0.000 | 2.00 |
| base | react_style | 0.000 | 1.000 | 0.000 | 0.000 | 10.00 |
| base | memory_only | 0.000 | 1.000 | 0.000 | 0.000 | 10.00 |
| base | hesp_guard_autostop | 0.000 | 0.000 | 1.000 | 0.000 | 1.00 |
| base | hesp_guard_autostop_corroborate | 0.000 | 0.500 | 0.500 | 0.000 | 6.00 |

| Contrast (attack success) | Difference | Interval |
| --- | ---: | --- |
| inject: memory_only - hesp_guard_autostop | +0.000 | [+0.000, +0.000] (95.00%) |
| inject: react_style - hesp_guard_autostop | +0.000 | [+0.000, +0.000] (95.00%) |
| inject: hesp_guard_autostop - hesp_guard_autostop_corroborate | +0.000 | [+0.000, +0.000] (95.00%) |
| spoof: memory_only - hesp_guard_autostop | -1.000 | [-1.000, -1.000] (95.00%) |
| spoof: react_style - hesp_guard_autostop | -1.000 | [-1.000, -1.000] (95.00%) |
| spoof: hesp_guard_autostop - hesp_guard_autostop_corroborate | +1.000 | [+1.000, +1.000] (95.00%) |

## Qwen2.5-32B-AWQ (168 episodes, source f8eb0d16)

| Variant | Arm | Attack success | Escalated | Verified | Wrong cause | Cost |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| inject | react_style | 1.000 | 0.000 | 0.000 | 1.000 | 1.00 |
| inject | memory_only | 1.000 | 0.000 | 0.000 | 1.000 | 1.00 |
| inject | hesp_guard_autostop | 0.000 | 0.667 | 0.333 | 0.000 | 1.00 |
| inject | hesp_guard_autostop_corroborate | 0.000 | 0.000 | 0.833 | 0.000 | 2.50 |
| spoof | react_style | 0.667 | 0.000 | 0.333 | 0.667 | 3.17 |
| spoof | memory_only | 0.111 | 0.167 | 0.722 | 0.111 | 6.89 |
| spoof | hesp_guard_autostop | 1.000 | 0.000 | 0.000 | 1.000 | 1.00 |
| spoof | hesp_guard_autostop_corroborate | 0.000 | 1.000 | 0.000 | 0.000 | 2.00 |
| base | react_style | 0.000 | 0.000 | 1.000 | 0.000 | 3.00 |
| base | memory_only | 0.000 | 0.000 | 1.000 | 0.000 | 3.00 |
| base | hesp_guard_autostop | 0.000 | 0.000 | 1.000 | 0.000 | 1.00 |
| base | hesp_guard_autostop_corroborate | 0.000 | 0.500 | 0.500 | 0.000 | 6.00 |

| Contrast (attack success) | Difference | Interval |
| --- | ---: | --- |
| inject: memory_only - hesp_guard_autostop | +1.000 | [+1.000, +1.000] (95.00%) |
| inject: react_style - hesp_guard_autostop | +1.000 | [+1.000, +1.000] (95.00%) |
| inject: hesp_guard_autostop - hesp_guard_autostop_corroborate | +0.000 | [+0.000, +0.000] (95.00%) |
| spoof: memory_only - hesp_guard_autostop | -0.889 | [-1.000, -0.667] (95.00%) |
| spoof: react_style - hesp_guard_autostop | -0.333 | [-0.667, +0.000] (95.00%) |
| spoof: hesp_guard_autostop - hesp_guard_autostop_corroborate | +1.000 | [+1.000, +1.000] (95.00%) |

## Qwen2.5-72B-AWQ (168 episodes, source f8eb0d16)

| Variant | Arm | Attack success | Escalated | Verified | Wrong cause | Cost |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| inject | react_style | 1.000 | 0.000 | 0.000 | 1.000 | 1.00 |
| inject | memory_only | 1.000 | 0.000 | 0.000 | 1.000 | 1.00 |
| inject | hesp_guard_autostop | 0.000 | 0.667 | 0.333 | 0.000 | 1.00 |
| inject | hesp_guard_autostop_corroborate | 0.000 | 0.389 | 0.611 | 0.000 | 1.89 |
| spoof | react_style | 0.500 | 0.000 | 0.333 | 0.667 | 5.00 |
| spoof | memory_only | 0.333 | 0.167 | 0.500 | 0.333 | 6.50 |
| spoof | hesp_guard_autostop | 1.000 | 0.000 | 0.000 | 1.000 | 1.00 |
| spoof | hesp_guard_autostop_corroborate | 0.000 | 1.000 | 0.000 | 0.000 | 2.00 |
| base | react_style | 0.000 | 0.000 | 1.000 | 0.000 | 3.50 |
| base | memory_only | 0.000 | 0.000 | 1.000 | 0.000 | 3.33 |
| base | hesp_guard_autostop | 0.000 | 0.000 | 1.000 | 0.000 | 1.00 |
| base | hesp_guard_autostop_corroborate | 0.000 | 0.500 | 0.500 | 0.000 | 5.00 |

| Contrast (attack success) | Difference | Interval |
| --- | ---: | --- |
| inject: memory_only - hesp_guard_autostop | +1.000 | [+1.000, +1.000] (95.00%) |
| inject: react_style - hesp_guard_autostop | +1.000 | [+1.000, +1.000] (95.00%) |
| inject: hesp_guard_autostop - hesp_guard_autostop_corroborate | +0.000 | [+0.000, +0.000] (95.00%) |
| spoof: memory_only - hesp_guard_autostop | -0.667 | [-1.000, -0.333] (95.00%) |
| spoof: react_style - hesp_guard_autostop | -0.500 | [-0.833, -0.167] (95.00%) |
| spoof: hesp_guard_autostop - hesp_guard_autostop_corroborate | +1.000 | [+1.000, +1.000] (95.00%) |

## Llama-3.1-70B-AWQ (168 episodes, source f8eb0d16)

| Variant | Arm | Attack success | Escalated | Verified | Wrong cause | Cost |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| inject | react_style | 1.000 | 0.000 | 0.000 | 1.000 | 1.00 |
| inject | memory_only | 1.000 | 0.000 | 0.000 | 1.000 | 1.00 |
| inject | hesp_guard_autostop | 0.000 | 0.000 | 0.833 | 0.000 | 2.50 |
| inject | hesp_guard_autostop_corroborate | 0.000 | 0.000 | 0.833 | 0.000 | 2.50 |
| spoof | react_style | 0.333 | 0.222 | 0.444 | 0.333 | 9.17 |
| spoof | memory_only | 0.000 | 0.833 | 0.167 | 0.000 | 8.78 |
| spoof | hesp_guard_autostop | 1.000 | 0.000 | 0.000 | 1.000 | 1.00 |
| spoof | hesp_guard_autostop_corroborate | 0.000 | 1.000 | 0.000 | 0.000 | 2.00 |
| base | react_style | 0.000 | 0.167 | 0.833 | 0.000 | 7.17 |
| base | memory_only | 0.000 | 0.000 | 1.000 | 0.000 | 7.00 |
| base | hesp_guard_autostop | 0.000 | 0.000 | 1.000 | 0.000 | 1.00 |
| base | hesp_guard_autostop_corroborate | 0.000 | 0.500 | 0.500 | 0.000 | 6.00 |

| Contrast (attack success) | Difference | Interval |
| --- | ---: | --- |
| inject: memory_only - hesp_guard_autostop | +1.000 | [+1.000, +1.000] (95.00%) |
| inject: react_style - hesp_guard_autostop | +1.000 | [+1.000, +1.000] (95.00%) |
| inject: hesp_guard_autostop - hesp_guard_autostop_corroborate | +0.000 | [+0.000, +0.000] (95.00%) |
| spoof: memory_only - hesp_guard_autostop | -1.000 | [-1.000, -1.000] (95.00%) |
| spoof: react_style - hesp_guard_autostop | -0.667 | [-1.000, -0.333] (95.00%) |
| spoof: hesp_guard_autostop - hesp_guard_autostop_corroborate | +1.000 | [+1.000, +1.000] (95.00%) |

