<div align="center">

![HESP](assets/hesp-banner.svg)

**Evidence-driven planning, with an auditable experimental record.**

[中文](../README.md) · [Results](../hesp_research/docs/RESULTS.md) · [Protocol](../hesp_research/docs/PROTOCOL.md)

</div>

## Research question

Under the same model, tools, and budget, can diagnostic action selection improve progress beyond structured memory alone?

HESP organizes local hypotheses, pre-registered outcome predictions, observations, and versioned business state into an auditable planning loop. It computes expected information gain (EIG) under a supplied predictive model, selects probes (EIG/cost or a budget-aware lookahead), rejects conclusions that rely on stale-state evidence (state guard), and requires an independent verifier.

![Framework](assets/hesp-framework.png)

<sub>The HESP investigation loop on sec-triage alert INC-4271; every number is taken from one real episode replayed by `docs/figures/make_framework_figure.py`. The controller (blue) keeps a posterior <i>p<sub>t</sub>(h)</i> over candidate causes, selects read-only probes by expected information gain per unit cost (EIG/<i>c</i>), and updates with a predictive model <i>P</i>(<i>o</i> | <i>h</i>, <i>a</i>) taken from the designer (oracle bound), counted from <i>k</i> development episodes (shown, <i>k</i> = 20), or elicited from the LLM. The LLM planner π reads the ledger and rankings, but its proposed probe binds only in the baselines: here π proposed <code>auth_log</code> and the controller ran <code>source_ips</code>. A verdict passes the finish guard before the independent verifier, which alone sees the hidden cause <i>h</i>*; a rejection returns its reason to π. Everything inside the red dashed boundary is hidden from π.</sub>

**Scope.** Two self-built, loopback-only web diagnosis sandboxes (web-diag, upload-diag) and locally served open-weight models (Qwen2.5 7B / 32B-AWQ / 72B-AWQ via Ollama or vLLM). These are controlled sandbox experiments, **not** Web CTF or real-website results.

## Results (v0.4, pre-registered)

![v0.4](assets/fig-v04-models.png)

Primary endpoint: paired difference in verified completion, full HESP − Memory-only, on the held-out upload-diag family (24 tasks × 3 repeats, task-cluster bootstrap):

| Planner | Δ [95% CI] | Memory-only rate |
| --- | --- | ---: |
| Qwen2.5-7B | **+0.625** [+0.44, +0.79] | 0.236 |
| Qwen2.5-32B-AWQ | **+0.000** [−0.12, +0.12] | 0.944 |
| Qwen2.5-72B-AWQ | **+0.111** [+0.03, +0.22] | 0.819 |

The benefit shrinks as the planner gets stronger. EIG/cost + state guard reached 1.000 on the held-out family for all three models (exploratory, not pre-registered). The lookahead selector helped on the development family but not on the held-out one, and self-elicited predictive tables were poorly calibrated (KL 0.86–1.76 bits). All 3888 episodes share one frozen source hash and pass the journal audit. Full report: [RESULTS.md](../hesp_research/docs/RESULTS.md).

## Quick start

Python 3.10+, standard library only for everything except serving a model.

```bash
git clone https://github.com/lzwhehe/HESP.git
cd HESP/hesp_research
python -m unittest discover -s tests
python -m hesp --env web --case owner_policy --variant drift --output runs/web_demo
python scripts/run_web_ablation.py --output runs/ablation --repeats 1
# with a local model (Ollama or vLLM): see docs/MODEL_ADAPTER.md
python -m hesp --env web --mode hesp --llm qwen2.5:7b-instruct --output runs/llm_demo
```

Output directories must be new. Every run stores its configuration, an append-only event journal, and a result; studies add a frozen manifest, durable outcomes, paired analysis, and a report.

See [contributing](../CONTRIBUTING.md), [changelog](../CHANGELOG.md), and [continuation notes](../hesp_research/docs/CONTINUATION.md). No open-source license has been selected.
