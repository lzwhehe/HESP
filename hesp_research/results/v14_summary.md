# v1.4: the small model deciding alone on raw logs

Verified / episodes; wrong = a named cause other than the true one; missed = attack called benign; no verdict = no finish or `other`. Reference rows are the paired v1.2 C raw episodes (same tasks, seeds, and log text; the model only reads, the controller decides).

## Qwen2.5-7B

| configuration | verified | wrong | missed | no verdict | probes |
|---|---|---|---|---|---|
| react_style_v1_structured | 0/48 | 8 | 8 | 40 | 6.6 |
| react_style_v1_documented | 0/48 | 0 | 0 | 48 | 7.06 |
| react_style_v1_drifted | 0/48 | 0 | 0 | 48 | 5.92 |
| react_style_clear_finish_structured | 0/48 | 6 | 5 | 42 | 7.38 |
| react_style_clear_finish_documented | 0/48 | 0 | 0 | 48 | 7.42 |
| react_style_clear_finish_drifted | 0/48 | 0 | 0 | 48 | 5.48 |
| memory_only_v1_structured | 9/48 | 0 | 0 | 39 | 7.06 |
| memory_only_v1_documented | 0/48 | 0 | 0 | 48 | 6.71 |
| memory_only_v1_drifted | 0/48 | 0 | 0 | 48 | 5.35 |
| memory_only_clear_finish_structured | 13/48 | 0 | 0 | 35 | 7.33 |
| memory_only_clear_finish_documented | 0/48 | 0 | 0 | 48 | 7.46 |
| memory_only_clear_finish_drifted | 0/48 | 0 | 0 | 48 | 5 |
| controller_structured_documented | 48/48 | 0 | 0 | 0 | 2.6 |
| controller_rule_documented | 48/48 | 0 | 0 | 0 | 2.6 |
| controller_rule_drifted | 0/48 | 0 | 0 | 48 | 8.35 |
| controller_llm_documented | 48/48 | 0 | 0 | 0 | 2.6 |
| controller_llm_drifted | 48/48 | 0 | 0 | 0 | 2.6 |

Primary (97.5 %): controller with Qwen2.5-7B reading drifted logs minus Qwen2.5-7B alone (memory_only_clear_finish_drifted): **+1.000 [+1.000, +1.000]** (16 tasks, 48 pairs)

## Llama-3.1-8B

| configuration | verified | wrong | missed | no verdict | probes |
|---|---|---|---|---|---|
| react_style_v1_structured | 0/48 | 0 | 0 | 48 | 7.98 |
| react_style_v1_documented | 0/48 | 0 | 0 | 48 | 8.04 |
| react_style_v1_drifted | 0/48 | 0 | 0 | 48 | 7.4 |
| react_style_clear_finish_structured | 0/48 | 0 | 0 | 48 | 7.85 |
| react_style_clear_finish_documented | 0/48 | 0 | 0 | 48 | 8.04 |
| react_style_clear_finish_drifted | 0/48 | 0 | 0 | 48 | 7.83 |
| memory_only_v1_structured | 0/48 | 0 | 0 | 48 | 7.85 |
| memory_only_v1_documented | 0/48 | 0 | 0 | 48 | 8.04 |
| memory_only_v1_drifted | 0/48 | 0 | 0 | 48 | 7.67 |
| memory_only_clear_finish_structured | 0/48 | 0 | 0 | 48 | 7.52 |
| memory_only_clear_finish_documented | 0/48 | 0 | 0 | 48 | 8.08 |
| memory_only_clear_finish_drifted | 0/48 | 0 | 0 | 48 | 7.48 |
| controller_structured_documented | 48/48 | 0 | 0 | 0 | 2.6 |
| controller_rule_documented | 48/48 | 0 | 0 | 0 | 2.6 |
| controller_rule_drifted | 0/48 | 0 | 0 | 48 | 8.35 |
| controller_llm_documented | 48/48 | 0 | 0 | 0 | 2.6 |
| controller_llm_drifted | 34/48 | 2 | 0 | 12 | 4.52 |

Primary (97.5 %): controller with Llama-3.1-8B reading drifted logs minus Llama-3.1-8B alone (memory_only_clear_finish_drifted): **+0.708 [+0.438, +0.938]** (16 tasks, 48 pairs)

