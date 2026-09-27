"""Elicit and freeze LLM predictive tables P(o | h, a) for the web sandbox, before any episode.

The frozen file is later replayed by the study scripts, so every episode of the
"LLM-P" arm uses exactly the same pre-registered predictions. Calibration against the
sandbox's true generative model is reported next to the designer table.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hesp.controller import source_hash
from hesp.llm import DEFAULT_MODEL, LLMPredictor, OllamaClient
from hesp.predictors import calibration
from hesp.webapp import DESCRIPTIONS, HYPOTHESES, VARIANTS, catalog, true_outcome_distribution


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=False)
    client = OllamaClient(args.model)
    info = client.info()
    predictor = LLMPredictor(client, seed=args.seed)
    start = time.time()
    tables = predictor.elicit(catalog(), DESCRIPTIONS)
    seconds = time.time() - start
    ids = [a.id for a in catalog()]
    designer = {a.id: a.likelihoods for a in catalog()}
    cal = {}
    for variant, spec in VARIANTS.items():
        true = (lambda lag: (lambda a, h: true_outcome_distribution(a, h, lag)))(spec["audit_lag"])
        cal[variant] = {"llm": calibration(tables, true, HYPOTHESES, ids),
                        "designer_table": calibration(designer, true, HYPOTHESES, ids)}
    record = {
        "schema": "hesp.elicitation.v1", "created_utc": datetime.now(timezone.utc).isoformat(),
        "source_sha256": source_hash(), "model": info, "seed": args.seed, "temperature": 0.0,
        "eps_floor": predictor.eps, "source": predictor.source, "seconds": round(seconds, 1),
        "usage": predictor.usage, "calls": len(predictor.records),
        "uniform_fallback_rows": sum(r["uniform_fallback"] for r in predictor.records),
        "tables": tables, "records": predictor.records, "calibration_vs_true_model": cal,
        "note": "Calibration is measured against the sandbox generator, which is visible in code; "
                "it quantifies how well the model predicts probe outcomes from the tool contract.",
    }
    path = out / "elicitation.json"
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    print(path, hashlib.sha256(path.read_bytes()).hexdigest())
    print(json.dumps(cal["base"], indent=2))


if __name__ == "__main__":
    main()
