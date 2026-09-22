<div align="center">

![HESP](assets/hesp-banner.svg)

**Evidence-driven planning, with an auditable experimental record.**

[中文](../README.md) · [Protocol](../hesp_research/docs/PROTOCOL.md) · [Results](../hesp_research/results/study_v02/report.md)

</div>

## Research question

Under the same model, tools, and budget, can diagnostic action selection improve progress beyond structured memory alone?

HESP organizes local hypotheses, predicted outcomes, observations, and business state into an auditable planning loop. It computes expected information gain under a supplied predictive model, ranks actions by gain per cost, registers predictions before execution, and requires independent outcome verification.

**Current scope:** a Python standard-library research prototype with handwritten synthetic tasks and a scripted policy. No real LLM or Web CTF experiment has been performed. Software validation is not evidence of method superiority.

## Experimental modes

| Mode | Planner context | Selection |
| --- | --- | --- |
| `react_style` | Goal, tools, execution history | Planner |
| `memory_only` | Above + structured hypotheses, state, evidence | Planner |
| `hesp` | Above + information gain and cost | Controller |

The ReAct-style interface is not a faithful reproduction of the original paper. All modes share budgets, tools, exact duplicate prevention, and the same scripted fixture policy.

## Quick start

Requires Python 3.10+. No dependencies or API keys are needed for the fixture runs.

```bash
git clone https://github.com/lzwhehe/HESP.git
cd HESP/hesp_research
python -m unittest discover -s tests -v
python -m hesp --mode hesp --case owner_policy --output runs/first_run
python scripts/run_study.py --output runs/study --repeats 3 --seed 42
python scripts/audit_run.py runs/first_run
```

Output directories must be new. Each run stores configuration, an event journal, and a result. Paired studies add a frozen manifest, durable outcomes, analysis, and a readable report.

## Recorded verification

The local v0.2 record dated 2026-09-22 includes **50 passing tests** and **36 verified fixture runs**. See the [test transcript](../hesp_research/results/verification_v02/unittest.txt) and [study report](../hesp_research/results/study_v02/report.md).

Repeated deterministic fixtures exercise the pipeline; their intervals and tool counts do not establish real-world efficacy. Missing usage remains unknown, failures stay in the denominator, and paired analysis resamples tasks rather than treating repeated runs as independent tasks.

## Next research stages

1. Select a model and budget, then implement provider-backed decisions and candidate predictions.
2. Introduce authorized, isolated Web tasks with reset support and independent verification.
3. Run a pilot, freeze the protocol and task splits, and conduct controlled experiments.
4. Report costs, negative results, ablations, and limitations alongside any positive findings.

See [contributing](../CONTRIBUTING.md), [changelog](../CHANGELOG.md), and [continuation notes](../hesp_research/docs/CONTINUATION.md). No open-source license has been selected.
