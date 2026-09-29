# v1.2 part C

## Fair prompts (selected variant: clear_finish)

| Model | Arm | N | Verified | Right cause | No verdict | Cost | Planner calls |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Qwen2.5-7B | react_style_v1 | 48 | 2 | 2 | 36 | 7.90 | 9.1 |
| Qwen2.5-7B | react_style_clear_finish | 48 | 0 | 0 | 40 | 8.75 | 9.7 |
| Qwen2.5-7B | memory_only_v1 | 48 | 8 | 8 | 40 | 9.58 | 10.5 |
| Qwen2.5-7B | memory_only_clear_finish | 48 | 16 | 17 | 30 | 8.94 | 9.9 |
| Qwen2.5-7B | hesp_guard_v1 | 48 | 44 | 44 | 4 | 7.33 | 8.0 |
| Qwen2.5-7B | hesp_guard_clear_finish | 48 | 48 | 48 | 0 | 6.73 | 7.4 |
| Qwen2.5-7B | hesp_guard_confirmstop_v1 | 48 | 48 | 48 | 0 | 2.54 | 2.5 |
| Qwen2.5-7B | hesp_guard_confirmstop_clear_finish | 48 | 48 | 48 | 0 | 2.54 | 2.5 |
| Llama-3.1-8B | react_style_v1 | 48 | 0 | 0 | 48 | 9.81 | 11.4 |
| Llama-3.1-8B | react_style_clear_finish | 48 | 0 | 0 | 48 | 9.75 | 11.1 |
| Llama-3.1-8B | memory_only_v1 | 48 | 0 | 0 | 48 | 9.62 | 10.3 |
| Llama-3.1-8B | memory_only_clear_finish | 48 | 0 | 0 | 48 | 9.69 | 10.1 |
| Llama-3.1-8B | hesp_guard_v1 | 48 | 0 | 0 | 48 | 10.00 | 9.6 |
| Llama-3.1-8B | hesp_guard_clear_finish | 48 | 32 | 32 | 16 | 10.00 | 9.6 |
| Llama-3.1-8B | hesp_guard_confirmstop_v1 | 48 | 48 | 48 | 0 | 2.54 | 2.5 |
| Llama-3.1-8B | hesp_guard_confirmstop_clear_finish | 48 | 48 | 48 | 0 | 2.54 | 2.5 |

Primary endpoints (confirmstop - Memory-only, selected prompt, 97.5 %):

```
{
 "qwen7b": {
  "difference": 0.6666666666666666,
  "ci": [
   0.4583333333333333,
   0.8541666666666666
  ],
  "level": 0.975,
  "tasks": 24
 },
 "llama8b": {
  "difference": 1.0,
  "ci": [
   1.0,
   1.0
  ],
  "level": 0.975,
  "tasks": 24
 }
}
```

Qwen2.5-7B prompt effects (95 %): react_style: clear_finish - v1 -0.042 [-0.10, +0.00]; memory_only: clear_finish - v1 +0.167 [+0.02, +0.35]; hesp_guard: clear_finish - v1 +0.083 [+0.00, +0.21]; hesp_guard_confirmstop: clear_finish - v1 +0.000 [+0.00, +0.00]

Llama-3.1-8B prompt effects (95 %): react_style: clear_finish - v1 +0.000 [+0.00, +0.00]; memory_only: clear_finish - v1 +0.000 [+0.00, +0.00]; hesp_guard: clear_finish - v1 +0.667 [+0.52, +0.81]; hesp_guard_confirmstop: clear_finish - v1 +0.000 [+0.00, +0.00]

## Raw-log observations

| Model | Parser | Condition | N | Parses | Accurate | Unparsed | Injection adopted | Verified | Wrong | Escalated | Missed attack |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Qwen2.5-7B | llm | documented | 48 | 108 | 108 | 0 | 0/0 | 48 | 0 | 0 | 0/36 |
| Qwen2.5-7B | llm | drifted | 48 | 108 | 108 | 0 | 0/0 | 48 | 0 | 0 | 0/36 |
| Qwen2.5-7B | llm | injected | 48 | 184 | 125 | 6 | 48/105 | 24 | 6 | 18 | 0/36 |
| Qwen2.5-7B | rule | documented | 48 | 108 | 108 | 0 | 0/0 | 48 | 0 | 0 | 0/36 |
| Qwen2.5-7B | rule | drifted | 48 | 364 | 0 | 364 | 0/0 | 0 | 0 | 48 | 0/36 |
| Qwen2.5-7B | rule | injected | 48 | 108 | 108 | 0 | 0/66 | 48 | 0 | 0 | 0/36 |
| Qwen2.5-7B | structured | documented | 48 | 0 | 0 | 0 | 0/0 | 48 | 0 | 0 | 0/36 |
| Llama-3.1-8B | llm | documented | 48 | 108 | 108 | 0 | 0/0 | 48 | 0 | 0 | 0/36 |
| Llama-3.1-8B | llm | drifted | 48 | 196 | 174 | 0 | 0/0 | 34 | 2 | 12 | 0/36 |
| Llama-3.1-8B | llm | injected | 48 | 136 | 129 | 0 | 1/71 | 42 | 0 | 6 | 0/36 |
| Llama-3.1-8B | rule | documented | 48 | 108 | 108 | 0 | 0/0 | 48 | 0 | 0 | 0/36 |
| Llama-3.1-8B | rule | drifted | 48 | 364 | 0 | 364 | 0/0 | 0 | 0 | 48 | 0/36 |
| Llama-3.1-8B | rule | injected | 48 | 108 | 108 | 0 | 0/66 | 48 | 0 | 0 | 0/36 |
| Llama-3.1-8B | structured | documented | 48 | 0 | 0 | 0 | 0/0 | 48 | 0 | 0 | 0/36 |
