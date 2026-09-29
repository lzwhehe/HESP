# Clustering and drift sensitivity of the sec-triage primary endpoints (exploratory)

| Endpoint | Task clusters (as reported) | Cause clusters | Base | Noise | Drift |
| --- | --- | --- | ---: | ---: | ---: |
| v0.5 Q-7B full HESP - Memory-only | +0.889 [+0.75, +1.00] (24) | +0.889 [+0.72, +1.00] (8) | +0.875 | +0.875 | +0.917 |
| v0.5 Q-32B full HESP - Memory-only | +0.250 [+0.10, +0.42] (24) | +0.250 [+0.11, +0.42] (8) | +0.125 | +0.250 | +0.375 |
| v0.5 Q-72B full HESP - Memory-only | +0.111 [+0.00, +0.24] (24) | +0.111 [+0.03, +0.22] (8) | +0.000 | +0.083 | +0.250 |
| v0.6 Q-7B counted tables - Memory-only | +0.875 [+0.74, +0.97] (24) | +0.875 [+0.71, +0.99] (8) | +0.875 | +0.875 | +0.875 |
| v0.8 Q-7B ranking (blind EIG - blind random) | +0.306 [+0.14, +0.47] (24) | +0.306 [+0.10, +0.46] (8) | +0.250 | +0.333 | +0.333 |
| v0.8 L-8B full HESP - Memory-only | +0.000 [+0.00, +0.00] (24) | +0.000 [+0.00, +0.00] (8) | +0.000 | +0.000 | +0.000 |
| v0.9 L-8B controller stop | +0.917 [+0.79, +1.00] (24) | +0.917 [+0.67, +1.00] (8) | +0.875 | +0.875 | +1.000 |
| v0.9 L-8B selection given stop | +0.056 [-0.07, +0.18] (24) | +0.056 [-0.12, +0.26] (8) | +0.042 | +0.000 | +0.125 |
| v1.0-C Q-7B injection attack success (Mem. - HESP) | +1.000 [+1.00, +1.00] (6) | +1.000 [+1.00, +1.00] (6) | -- | -- | -- |
| v1.1 PE1-sec Q-72B LLM stop - LLM-free confirmation | +0.000 [+0.00, +0.00] (24) | +0.000 [+0.00, +0.00] (8) | +0.000 | +0.000 | +0.000 |

Levels follow each study's protocol (95 %, 97.5 %, or 98.33 %); cause clusters average tasks within a cause first.
