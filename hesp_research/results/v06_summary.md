### Pre-registered primary endpoint (hesp_eigc_guard_emp20_minus_memory_only, 7B; 32B/72B exploratory per R-9)

| Model | delta verified | 95% cluster interval | tasks better / worse |
| --- | ---: | --- | ---: |
| Qwen2.5-7B | +0.875 | [+0.736, +0.972] | 22 / 0 |
| Qwen2.5-32B-AWQ | +0.250 | [+0.097, +0.417] | 8 / 0 |
| Qwen2.5-72B-AWQ | +0.111 | [+0.000, +0.236] | 3 / 0 |

### Verified fraction by arm

| Arm | Qwen2.5-7B | Qwen2.5-32B-AWQ | Qwen2.5-72B-AWQ |
| --- | ---: | ---: | ---: |
| react_style | 0.028 | 0.611 | 0.597 |
| memory_only | 0.125 | 0.750 | 0.889 |
| hesp_eigc_guard_designer | 1.000 | 1.000 | 1.000 |
| hesp_eigc_guard_emp1 | 0.986 | 0.986 | 1.000 |
| hesp_eigc_guard_emp5 | 1.000 | 1.000 | 1.000 |
| hesp_eigc_guard_emp20 | 1.000 | 1.000 | 1.000 |
| hesp_eigc_guard_emp100 | 1.000 | 1.000 | 1.000 |
| hesp_eigc_guard_llmp | 0.069 | 0.375 | 0.375 |

### Mean tool cost by arm

| Arm | Qwen2.5-7B | Qwen2.5-32B-AWQ | Qwen2.5-72B-AWQ |
| --- | ---: | ---: | ---: |
| react_style | 9.14 | 5.50 | 5.79 |
| memory_only | 9.44 | 5.39 | 5.71 |
| hesp_eigc_guard_designer | 7.07 | 3.67 | 4.12 |
| hesp_eigc_guard_emp1 | 9.44 | 6.40 | 5.36 |
| hesp_eigc_guard_emp5 | 9.40 | 6.11 | 5.32 |
| hesp_eigc_guard_emp20 | 9.40 | 6.11 | 5.33 |
| hesp_eigc_guard_emp100 | 9.40 | 6.11 | 5.33 |
| hesp_eigc_guard_llmp | 10.00 | 9.01 | 8.39 |

### Paired comparisons (verified fraction; tool cost)

| Comparison | Qwen2.5-7B | Qwen2.5-32B-AWQ | Qwen2.5-72B-AWQ |
| --- | --- | --- | --- |
| emp20 − memory_only | +0.875 [+0.736, +0.972]; cost -0.04 | +0.250 [+0.097, +0.417]; cost +0.72 | +0.111 [+0.000, +0.236]; cost -0.38 |
| emp1 − memory_only | +0.861 [+0.722, +0.958]; cost -0.00 | +0.236 [+0.069, +0.417]; cost +1.01 | +0.111 [+0.000, +0.236]; cost -0.35 |
| emp5 − memory_only | +0.875 [+0.736, +0.972]; cost -0.04 | +0.250 [+0.097, +0.417]; cost +0.72 | +0.111 [+0.000, +0.236]; cost -0.39 |
| emp100 − memory_only | +0.875 [+0.736, +0.972]; cost -0.04 | +0.250 [+0.097, +0.417]; cost +0.72 | +0.111 [+0.000, +0.236]; cost -0.38 |
| designer − emp20 | +0.000 [+0.000, +0.000]; cost -2.33 | +0.000 [+0.000, +0.000]; cost -2.44 | +0.000 [+0.000, +0.000]; cost -1.21 |
| emp20 − llmp | +0.931 [+0.819, +1.000]; cost -0.60 | +0.625 [+0.417, +0.833]; cost -2.90 | +0.625 [+0.417, +0.833]; cost -3.06 |
| designer − memory_only | +0.875 [+0.736, +0.972]; cost -2.38 | +0.250 [+0.097, +0.417]; cost -1.72 | +0.111 [+0.000, +0.236]; cost -1.58 |
| memory_only − react_style | +0.097 [+0.000, +0.222]; cost +0.31 | +0.139 [+0.028, +0.278]; cost -0.11 | +0.292 [+0.083, +0.500]; cost -0.08 |

### Security-facing metrics, corrected (descriptive only)

Ground truth is the cause in effect at the verdict: `drift_to` only if the drift had already happened. Checked: every verified claim equals this ground truth.

**Qwen2.5-7B**

| Arm | with a claim | unresolved | missed attack | false escalation | wrong cause | citation validity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| react_style | 3/72 | 0.972 | 1.000 | 0.000 | 0.333 | 1.000 |
| memory_only | 9/72 | 0.875 | 0.000 | 0.000 | 0.000 | 1.000 |
| designer | 72/72 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| emp1 | 71/72 | 0.014 | 0.000 | 0.000 | 0.000 | 1.000 |
| emp5 | 72/72 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| emp20 | 72/72 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| emp100 | 72/72 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| llmp | 9/72 | 0.931 | n/a | 0.000 | 0.000 | 1.000 |

**Qwen2.5-32B-AWQ**

| Arm | with a claim | unresolved | missed attack | false escalation | wrong cause | citation validity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| react_style | 69/72 | 0.389 | 0.255 | 0.278 | 0.362 | 0.778 |
| memory_only | 72/72 | 0.250 | 0.037 | 0.167 | 0.125 | 0.940 |
| designer | 72/72 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| emp1 | 71/72 | 0.014 | 0.000 | 0.000 | 0.000 | 1.000 |
| emp5 | 72/72 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| emp20 | 72/72 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| emp100 | 72/72 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| llmp | 27/72 | 0.625 | 0.000 | 0.000 | 0.000 | 1.000 |

**Qwen2.5-72B-AWQ**

| Arm | with a claim | unresolved | missed attack | false escalation | wrong cause | citation validity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| react_style | 72/72 | 0.403 | 0.370 | 0.167 | 0.403 | 0.690 |
| memory_only | 71/72 | 0.111 | 0.019 | 0.000 | 0.056 | 0.967 |
| designer | 72/72 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| emp1 | 72/72 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| emp5 | 72/72 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| emp20 | 72/72 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| emp100 | 72/72 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| llmp | 27/72 | 0.625 | 0.000 | 0.000 | 0.000 | 0.938 |

### Exploratory: self-elicited table under the guard, verified by final cause

| Final cause | Qwen2.5-7B | Qwen2.5-32B-AWQ | Qwen2.5-72B-AWQ |
| --- | ---: | ---: | ---: |
| authorized_scan | 0.00 | 1.00 | 1.00 |
| credential_stuffing | 0.00 | 0.00 | 0.00 |
| dns_c2 | 0.00 | 0.00 | 0.00 |
| false_positive_monitor | 0.56 | 1.00 | 1.00 |
| insider_exfil | 0.00 | 1.00 | 1.00 |
| misconfig_exposed_admin | 0.00 | 0.00 | 0.00 |
| sqli_probe | 0.00 | 0.00 | 0.00 |
| vuln_component | 0.00 | 0.00 | 0.00 |

### Exploratory, LLM-free: does the unobservable 'other' row explain the oracle gap?

| Predictive table | verified | mean tool cost |
| --- | ---: | ---: |
| designer | 1.000 | 2.54 |
| emp20 | 0.875 | 3.53 |
| emp20 + designer 'other' row | 1.000 | 2.54 |
