# v0.4 · qwen2.5-7b-instruct · all families

Paired local-sandbox study. Intervals are over task clusters of a small, hand-built suite; they do not generalize to real websites or Web CTF.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| react_style | 144 | 0.319 | 2.02 | 2.37 | 2.94 | 4023 | 116 | UNVERIFIED_CLAIM:98, VERIFIED_SIMULATION:46 |
| memory_only | 144 | 0.438 | 2.26 | 2.87 | 2.97 | 5135 | 123 | UNVERIFIED_CLAIM:81, VERIFIED_SIMULATION:63 |
| memory_guard | 144 | 0.493 | 2.60 | 3.30 | 8.06 | 13450 | 335 | DECISION_BUDGET_EXCEEDED:72, PLANNER_ERROR:1, VERIFIED_SIMULATION:71 |
| hesp_eigc | 144 | 0.875 | 3.68 | 3.54 | 3.28 | 5071 | 106 | UNVERIFIED_CLAIM:18, VERIFIED_SIMULATION:126 |
| hesp_eigc_guard | 144 | 0.910 | 3.79 | 3.69 | 4.15 | 6639 | 143 | DECISION_BUDGET_EXCEEDED:13, VERIFIED_SIMULATION:131 |
| hesp_la | 144 | 0.917 | 4.22 | 3.95 | 2.85 | 4357 | 95 | UNVERIFIED_CLAIM:12, VERIFIED_SIMULATION:132 |
| hesp_la_guard | 144 | 0.917 | 4.22 | 3.97 | 3.52 | 5582 | 125 | DECISION_BUDGET_EXCEEDED:12, VERIFIED_SIMULATION:132 |
| hesp_random | 144 | 0.868 | 6.02 | 5.76 | 5.45 | 8908 | 173 | UNVERIFIED_CLAIM:19, VERIFIED_SIMULATION:125 |
| hesp_llmp | 144 | 0.896 | 4.74 | 4.46 | 3.06 | 4703 | 102 | UNVERIFIED_CLAIM:15, VERIFIED_SIMULATION:129 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| hesp_la_guard_minus_memory_only | 48 | +0.479 | [+0.347, +0.604] | 28 / 0 | +1.96 | [+1.264, +2.653] |
| hesp_la_guard_minus_react_style | 48 | +0.597 | [+0.465, +0.722] | 32 / 0 | +2.20 | [+1.576, +2.819] |
| memory_only_minus_react_style | 48 | +0.118 | [+0.042, +0.201] | 9 / 1 | +0.24 | [-0.097, +0.590] |
| hesp_eigc_minus_memory_only | 48 | +0.438 | [+0.271, +0.590] | 27 / 2 | +1.42 | [+0.910, +1.944] |
| hesp_eigc_guard_minus_hesp_eigc | 48 | +0.035 | [+0.000, +0.090] | 2 / 0 | +0.11 | [+0.000, +0.278] |
| memory_guard_minus_memory_only | 48 | +0.056 | [+0.014, +0.104] | 6 / 0 | +0.34 | [+0.104, +0.625] |
| hesp_la_guard_minus_memory_guard | 48 | +0.424 | [+0.299, +0.542] | 28 / 1 | +1.62 | [+0.840, +2.389] |
| hesp_la_minus_hesp_eigc | 48 | +0.042 | [-0.062, +0.153] | 7 / 7 | +0.54 | [+0.049, +1.028] |
| hesp_eigc_minus_hesp_random | 48 | +0.007 | [-0.104, +0.104] | 15 / 6 | -2.34 | [-2.840, -1.847] |
| hesp_eigc_minus_hesp_llmp | 48 | -0.021 | [-0.146, +0.097] | 9 / 8 | -1.06 | [-1.694, -0.451] |

All failures remain in the denominator; unknown usage stays null.

Primary family (pre-registered): upload-diag; see report_upload-diag.md.
