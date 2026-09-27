# Local-LLM pilot (qwen2.5:7b-instruct, web sandbox)

Paired local-sandbox study. Intervals are over task clusters of a small, hand-built suite; they do not generalize to real websites or Web CTF.

| Arm | Runs | Verified | Mean tool cost | Cost when verified | Mean planner calls | Mean input tokens | Mean output tokens | Statuses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| react_style | 48 | 0.604 | 6.17 | 7.07 | 7.98 | 18869 | 241 | DECISION_BUDGET_EXCEEDED:11, PLANNER_ERROR:1, UNVERIFIED_CLAIM:7, VERIFIED_SIMULATION:29 |
| memory_only | 48 | 0.750 | 5.94 | 5.69 | 6.48 | 17073 | 201 | DECISION_BUDGET_EXCEEDED:6, TOOL_BUDGET_EXCEEDED:1, UNVERIFIED_CLAIM:5, VERIFIED_SIMULATION:36 |
| hesp | 48 | 0.812 | 5.54 | 5.18 | 4.33 | 10844 | 135 | UNVERIFIED_CLAIM:9, VERIFIED_SIMULATION:39 |
| hesp_llm_pred | 48 | 0.750 | 5.77 | 6.19 | 4.40 | 11330 | 146 | UNVERIFIED_CLAIM:12, VERIFIED_SIMULATION:36 |
| hesp_random | 48 | 0.750 | 7.02 | 6.75 | 6.56 | 16908 | 192 | UNVERIFIED_CLAIM:12, VERIFIED_SIMULATION:36 |

## Paired differences (task-cluster bootstrap, 95% percentile interval)

| Comparison | Tasks | Δ verified | 95% CI | tasks better / worse | Δ tool cost | 95% CI |
| --- | ---: | ---: | --- | --- | ---: | --- |
| hesp_minus_react_style | 24 | +0.208 | [+0.000, +0.417] | 8 / 2 | -0.62 | [-1.625, +0.312] |
| hesp_minus_memory_only | 24 | +0.062 | [-0.125, +0.271] | 6 / 4 | -0.40 | [-1.354, +0.521] |
| memory_only_minus_react_style | 24 | +0.146 | [-0.021, +0.312] | 7 / 3 | -0.23 | [-1.167, +0.833] |
| hesp_minus_hesp_random | 24 | +0.062 | [-0.104, +0.229] | 7 / 4 | -1.48 | [-2.208, -0.750] |
| hesp_minus_hesp_llm_pred | 24 | +0.062 | [-0.062, +0.208] | 3 / 2 | -0.23 | [-1.542, +0.979] |
| hesp_llm_pred_minus_memory_only | 24 | +0.000 | [-0.229, +0.229] | 7 / 6 | -0.17 | [-1.542, +1.375] |
| hesp_random_minus_memory_only | 24 | +0.000 | [-0.167, +0.188] | 6 / 6 | +1.08 | [+0.229, +1.979] |

All failures remain in the denominator; unknown usage stays null.

Model digest: `845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e`, quantization Q4_K_M, temperature 0.2. Tokens are server-reported by the local Ollama runtime.
This is a small pilot on a hand-built sandbox (24 tasks); it is not a Web CTF benchmark.
