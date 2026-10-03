<div align="center">

![HESP — Hypotheses. Evidence. State. Planning.](assets/hesp-banner.svg)

**Making small local LLMs usable for alert triage: the model reads the logs, a controller decides.**

[![arXiv](https://img.shields.io/badge/arXiv-2609.33446-B31B1B?style=flat-square)](https://arxiv.org/abs/2609.33446)
[![CI](https://github.com/lzwhehe/HESP/actions/workflows/verify.yml/badge.svg?branch=main)](https://github.com/lzwhehe/HESP/actions/workflows/verify.yml)
![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square)
[![License: MIT](https://img.shields.io/badge/license-MIT-64748B?style=flat-square)](../LICENSE)
![Pre-registered](https://img.shields.io/badge/studies-pre--registered-14B8A6?style=flat-square)

[Paper](#paper) · [Key results](#key-results) · [How it works](#how-it-works) · [Quick start](#quick-start) · [Repository layout](#repository-layout) · [Studies](#studies) · [中文](../README.md)

</div>

---

## The problem

Organizations that cannot send telemetry to a hosted model must triage security alerts with small models (7B/8B) on their own hardware. On their own, these models cannot do it: they do not choose what to check next well, and they do not decide when the evidence suffices.

Many alerts, however, belong to recurring types for which analysts already know the plausible causes, the checks that tell them apart, and how past cases were resolved. **HESP targets these known alert types** and splits triage into two jobs:

| Job | Done by | What it involves |
| :--- | :--- | :--- |
| **Reading** | the small model | turning a probe's raw log text into one of the outcomes analysts defined |
| **Deciding** | the controller | choosing the next probe, deciding when to stop, accepting only verdicts the evidence supports |

## Paper

**HESP: Making Small Local LLMs Usable for Alert Triage — The Model Reads the Logs, a Controller Decides**
arXiv: [2609.33446](https://arxiv.org/abs/2609.33446) (v2). LaTeX source in [`paper_read/`](../paper_read/).

## Key results

sec-triage, episodes (of 48) that the independent verifier accepts, Qwen2.5-7B / Llama-3.1-8B:

| Decides | Reads | Structured (labeled) | Raw log, documented format | Raw log, changed format |
| :--- | :--- | ---: | ---: | ---: |
| small model alone (best of four configurations) | model | 13 / 0 | 0 / 0 | **0 / 0** |
| controller | fixed rules | 48 / 48 | 48 / 48 | **0 / 0** |
| controller | model | — | 48 / 48 | **48 / 34** |

- **Neither half works alone.** Deciding alone from raw logs, the small model resolves nothing: it reads the logs but never concludes, re-proposing probes it has already run. Alone, the controller's rule parser reads nothing once the log format changes. Together they resolve the cases.
- **Deciding needs no model.** With structured observations, a controller without any model resolves every case in two settings, and none of five models from 7B to 72B improves on it.
- **Reading is an attack surface.** A consistent benign story written into every log makes Qwen2.5-7B as reader close all 36 attacks as benign. Never letting model-parsed evidence support a benign verdict stops every attack we tested; the cost is that honest benign cases escalate when no trusted parser can read the logs.

**Scope.** All three settings are simulated; candidate causes, probes, and outcomes are written in advance, and each cause leaves a distinctive observation; the prediction tables are counted from a deterministic generator. New alert types and tables counted from real tickets are untested. See the paper's limitations.

## How it works

![One real HESP episode](assets/hesp-pipeline.png)

<sub>One real episode (sec-base-02, Llama-3.1-8B as planner): the model only proposes probes and never concludes; the controller picks probes by expected information gain per cost, updates the causes with Bayes' rule, and concludes once the leader's posterior reaches 0.8 with current supporting evidence. Every prediction is journaled before its observation.</sub>

After each outcome the controller:

1. **Updates the ledger** with Bayes' rule, using prediction tables $P(o \mid h, a)$ counted from development cases with known causes (never elicited from the model).
2. **Checks whether to conclude**: the leader's posterior must reach the threshold and at least one current observation must single it out (confirmation stop).
3. **Selects the next probe** with the highest expected information gain per unit cost.
4. **Protects the verdict**: a finish guard rejects verdicts the ledger does not support; benign verdicts need two independent source groups; model-parsed observations cannot support a benign verdict (reader trust).

## Quick start

**Python 3.10+, standard library only, no API keys, no GPU needed for the commands below.**

```bash
git clone https://github.com/lzwhehe/HESP.git
cd HESP/hesp_research

# unit tests (about a minute)
python -m unittest discover -s tests

# step-by-step trace of the LLM-free controller on one case
python scripts/demo_controller_trace.py --cause dns_c2

# behavioural fingerprint: 288 LLM-free episodes, expect digest 3d9e5bc5...
python scripts/check_equivalence.py

# regenerate a summary from the result files, then the paper's tables
python scripts/v14_summary.py
python ../paper_read/make_tables.py
```

To serve a local model (vLLM or Ollama, OpenAI-compatible), see the [model adapter protocol](../hesp_research/docs/MODEL_ADAPTER.md); the H100 run scripts for each study are in [`hesp_research/scripts/server/`](../hesp_research/scripts/server/).

## Repository layout

```text
HESP/
├── hesp_research/          code, tests, study scripts, and all results
│   ├── hesp/               controller, ledger, selectors, environments (sec / sigma / comp-triage), raw-log reading
│   ├── scripts/            per-study runners and summaries (run_v*_study.py, v*_summary.py)
│   ├── tests/              unit tests
│   ├── results/            outcomes.jsonl, summaries, and hashed episode-journal archives per study
│   └── docs/               PROTOCOL.md (pre-registration), RESULTS.md, external dataset audits
├── paper_read/             the paper (v2, current): LaTeX, table generators, Chinese copy, arXiv packaging
├── paper/                  a separate manuscript: a shortcut audit of LLM security-operations benchmarks
├── arxiv_v2/               a minimal correction of v1 (superseded by paper_read, kept for reference)
└── docs/                   README figures and this file
```

## Studies

Every study was written into [PROTOCOL.md](../hesp_research/docs/PROTOCOL.md) and frozen with a source hash before it ran (the protocol is in Chinese). Failed predictions and errata stay in the record, and every number in the paper is generated by scripts from `hesp_research/results/`.

| Study | Question | Main finding |
| :--- | :--- | :--- |
| v0.3–v0.5 | Does information-gain selection help local models diagnose? | 7B alone 0.03–0.11; with HESP 0.96–1.00 |
| v0.6 | Can the tables do without the designer? | Tables counted from development episodes match designer tables |
| v0.7 | Cold start on real GUIDE incidents | Primary endpoint found invalid before freezing; paused, test split unread |
| v0.8 | Does the ranking help when the planner sees the same information? | Yes (+0.26 to +0.35); Llama-3.1-8B never concludes |
| v0.9 | Letting the controller stop | Llama-3.1-8B from 0 to 0.917 |
| v1.0–v1.1 | Sigma-rule setting, confirmation stop, attacks, fair comparisons | LLM-free controller 72/72 and 152/152; no model improves on it |
| v1.2 | Better prompts; probes return raw logs | Changed format: rule parser 0/364, model reader 48/48 |
| v1.3 | Adaptive attacks on the model reader | Reader trust cuts missed attacks to 0/36 |
| v1.4 | Small model alone on raw logs | 0/48 for both models in every configuration; Qwen wording check also 0/48 |

## Citation

```bibtex
@misc{liu2026hesp,
  title         = {{HESP}: Making Small Local {LLMs} Usable for Alert Triage -- The Model Reads the Logs, a Controller Decides},
  author        = {Liu, Zhuowen and Wang, Zhixuan},
  year          = {2026},
  eprint        = {2609.33446},
  archivePrefix = {arXiv}
}
```
