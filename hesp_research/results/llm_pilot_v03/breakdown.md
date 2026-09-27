# Pilot breakdown (descriptive)

## Verified rate by variant

| Arm | base | drift | noise |
| --- | ---: | ---: | ---: |
| react_style | 0.688 | 0.500 | 0.625 |
| memory_only | 0.812 | 0.688 | 0.750 |
| hesp | 1.000 | 0.438 | 1.000 |
| hesp_llm_pred | 1.000 | 0.250 | 1.000 |
| hesp_random | 1.000 | 0.500 | 0.750 |

## Planner behaviour

| Arm | blocked dup. proposals / ep. | eps. with a blocked dup. | repair attempts | LLM s / ep. | tokens / ep. | tokens / verified ep. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| react_style | 2.08 | 17/48 | 13 | 20.4 | 19110 | 30972 |
| memory_only | 0.88 | 14/48 | 20 | 20.1 | 17274 | 23032 |
| hesp | 0.00 | 0/48 | 0 | 12.8 | 10979 | 13513 |
| hesp_llm_pred | 0.00 | 0/48 | 4 | 12.2 | 11476 | 15302 |
| hesp_random | 0.00 | 0/48 | 0 | 22.9 | 17100 | 22800 |

Tokens are server-reported by local Ollama (prompt incl. cached prefix + generated).
