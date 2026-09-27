# v1.0 part A - external sigma-triage family

## Primary endpoints (Qwen2.5-7B; 98.33 % rule-cluster intervals)

- PA1 ranking under controller stop: hesp_eigc_blind_autostop - hesp_random_blind_autostop = +0.171 [+0.094, +0.250] (12 rules, 76 tasks; 24 better, 2 worse) -> CONFIRMED
- PA2 full effect: hesp_eigc_blind_autostop - memory_only = +0.296 [+0.088, +0.473] (12 rules, 76 tasks; 32 better, 2 worse) -> CONFIRMED

## Qwen2.5-7B (760 episodes, source f8eb0d16)

| Arm | Verified | Cost | Missed attack | Wrong cause | Finished by |
| --- | ---: | ---: | ---: | ---: | --- |
| memory_only | 0.678 | 5.23 | 0.000 | 0.046 | {'planner': 130, 'None': 22} |
| memory_only_autostop | 0.862 | 2.76 | 0.000 | 0.033 | {'controller': 132, 'planner': 16, 'None': 4} |
| hesp_eigc_blind | 0.882 | 2.98 | 0.083 | 0.026 | {'planner': 151, 'None': 1} |
| hesp_eigc_blind_autostop | 0.974 | 2.07 | 0.083 | 0.026 | {'controller': 134, 'planner': 18} |
| hesp_random_blind_autostop | 0.803 | 3.73 | 0.042 | 0.072 | {'controller': 121, 'planner': 31} |

| Contrast | Difference | Interval |
| --- | ---: | --- |
| hesp_eigc_blind_autostop - hesp_random_blind_autostop | +0.171 | [+0.094, +0.250] (98.33%) |
| hesp_eigc_blind_autostop - memory_only | +0.296 | [+0.088, +0.473] (98.33%) |
| hesp_eigc_blind_autostop - hesp_eigc_blind | +0.092 | [+0.020, +0.176] (95.00%) |
| hesp_eigc_blind_autostop - memory_only_autostop | +0.112 | [-0.014, +0.244] (95.00%) |
| memory_only_autostop - memory_only | +0.184 | [+0.074, +0.303] (95.00%) |

## Llama-3.1-8B (760 episodes, source f8eb0d16)

| Arm | Verified | Cost | Missed attack | Wrong cause | Finished by |
| --- | ---: | ---: | ---: | ---: | --- |
| memory_only | 0.000 | 9.88 | 0.000 | 0.000 | {'None': 152} |
| memory_only_autostop | 0.921 | 2.89 | 0.000 | 0.000 | {'controller': 152} |
| hesp_eigc_blind | 0.007 | 9.78 | 0.000 | 0.000 | {'None': 151, 'planner': 1} |
| hesp_eigc_blind_autostop | 1.000 | 2.20 | 0.000 | 0.000 | {'controller': 152} |
| hesp_random_blind_autostop | 0.895 | 4.27 | 0.000 | 0.000 | {'controller': 151, 'None': 1} |

| Contrast | Difference | Interval |
| --- | ---: | --- |
| hesp_eigc_blind_autostop - hesp_random_blind_autostop | +0.105 | [+0.051, +0.160] (95.00%) |
| hesp_eigc_blind_autostop - memory_only | +1.000 | [+1.000, +1.000] (95.00%) |
| hesp_eigc_blind_autostop - hesp_eigc_blind | +0.993 | [+0.980, +1.000] (95.00%) |
| hesp_eigc_blind_autostop - memory_only_autostop | +0.079 | [+0.014, +0.162] (95.00%) |
| memory_only_autostop - memory_only | +0.921 | [+0.838, +0.986] (95.00%) |

## Qwen2.5-32B-AWQ (760 episodes, source f8eb0d16)

| Arm | Verified | Cost | Missed attack | Wrong cause | Finished by |
| --- | ---: | ---: | ---: | ---: | --- |
| memory_only | 0.954 | 5.36 | 0.000 | 0.000 | {'planner': 151, 'None': 1} |
| memory_only_autostop | 0.934 | 2.74 | 0.000 | 0.000 | {'controller': 152} |
| hesp_eigc_blind | 0.947 | 5.24 | 0.000 | 0.000 | {'planner': 152} |
| hesp_eigc_blind_autostop | 1.000 | 2.20 | 0.000 | 0.000 | {'controller': 152} |
| hesp_random_blind_autostop | 0.836 | 4.07 | 0.000 | 0.033 | {'controller': 132, 'planner': 20} |

| Contrast | Difference | Interval |
| --- | ---: | --- |
| hesp_eigc_blind_autostop - hesp_random_blind_autostop | +0.164 | [+0.096, +0.237] (95.00%) |
| hesp_eigc_blind_autostop - memory_only | +0.046 | [+0.007, +0.104] (95.00%) |
| hesp_eigc_blind_autostop - hesp_eigc_blind | +0.053 | [+0.000, +0.135] (95.00%) |
| hesp_eigc_blind_autostop - memory_only_autostop | +0.066 | [+0.007, +0.142] (95.00%) |
| memory_only_autostop - memory_only | -0.020 | [-0.068, +0.013] (95.00%) |

## Qwen2.5-72B-AWQ (760 episodes, source f8eb0d16)

| Arm | Verified | Cost | Missed attack | Wrong cause | Finished by |
| --- | ---: | ---: | ---: | ---: | --- |
| memory_only | 0.895 | 4.51 | 0.000 | 0.033 | {'planner': 150, 'None': 2} |
| memory_only_autostop | 0.914 | 2.49 | 0.000 | 0.026 | {'controller': 141, 'planner': 11} |
| hesp_eigc_blind | 0.974 | 3.02 | 0.000 | 0.013 | {'planner': 152} |
| hesp_eigc_blind_autostop | 1.000 | 2.17 | 0.000 | 0.000 | {'controller': 148, 'planner': 4} |
| hesp_random_blind_autostop | 0.770 | 3.55 | 0.000 | 0.079 | {'planner': 48, 'controller': 104} |

| Contrast | Difference | Interval |
| --- | ---: | --- |
| hesp_eigc_blind_autostop - hesp_random_blind_autostop | +0.230 | [+0.141, +0.324] (95.00%) |
| hesp_eigc_blind_autostop - memory_only | +0.105 | [+0.014, +0.236] (95.00%) |
| hesp_eigc_blind_autostop - hesp_eigc_blind | +0.026 | [+0.000, +0.081] (95.00%) |
| hesp_eigc_blind_autostop - memory_only_autostop | +0.086 | [+0.000, +0.217] (95.00%) |
| memory_only_autostop - memory_only | +0.020 | [+0.000, +0.039] (95.00%) |

## Llama-3.1-70B-AWQ (760 episodes, source f8eb0d16)

| Arm | Verified | Cost | Missed attack | Wrong cause | Finished by |
| --- | ---: | ---: | ---: | ---: | --- |
| memory_only | 0.783 | 7.91 | 0.000 | 0.000 | {'planner': 121, 'None': 31} |
| memory_only_autostop | 0.941 | 2.76 | 0.000 | 0.000 | {'controller': 152} |
| hesp_eigc_blind | 0.954 | 8.65 | 0.000 | 0.000 | {'planner': 152} |
| hesp_eigc_blind_autostop | 1.000 | 2.20 | 0.000 | 0.000 | {'controller': 152} |
| hesp_random_blind_autostop | 0.895 | 4.27 | 0.000 | 0.007 | {'controller': 151, 'planner': 1} |

| Contrast | Difference | Interval |
| --- | ---: | --- |
| hesp_eigc_blind_autostop - hesp_random_blind_autostop | +0.105 | [+0.051, +0.160] (95.00%) |
| hesp_eigc_blind_autostop - memory_only | +0.217 | [+0.135, +0.306] (95.00%) |
| hesp_eigc_blind_autostop - hesp_eigc_blind | +0.046 | [+0.000, +0.118] (95.00%) |
| hesp_eigc_blind_autostop - memory_only_autostop | +0.059 | [+0.000, +0.139] (95.00%) |
| memory_only_autostop - memory_only | +0.158 | [+0.099, +0.224] (95.00%) |

