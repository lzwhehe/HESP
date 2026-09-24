"""Estimate P(o | h, a) from development observations only (PROTOCOL.md v0.6, RQ3).

The point of this script is what it does NOT do: it never calls the environment's
generative function ``true_outcome_distribution``. It runs the probe catalogue against
development episodes, counts what came back, and smooths. That is the information a
deployment could actually obtain.

Per the pre-registration:
  * only the ``base`` and ``noise`` variants are used (``drift`` switches the true cause
    mid-episode, so counts cannot be attributed); this makes the estimate strictly weaker
  * development seeds live at 900000 + i, disjoint from the evaluation seed space
  * k is the number of development episodes per (cause, variant); the k levels are
    nested (the k=20 sample is exactly the first 20 episodes of the k=100 sample)

    python scripts/estimate_empirical_tables.py --k 1 5 20 100 --out results/v06_tables
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hesp.predictors import EmpiricalEstimator
from hesp.secapp import CAUSES, HYPOTHESES, SecTriageEnvironment

DEV_SEED_BASE = 900_000
DEV_VARIANTS = ("base", "noise")


def dev_seed(cause_index, variant_index, i):
    """Deterministic development seed for the i-th episode (1-based) of one (cause, variant).

    Fixed per (cause, variant, i) so that the k-episode sample is exactly the first k
    episodes of any larger sample -- the k levels are nested, not independent draws.
    """
    return DEV_SEED_BASE + (cause_index * len(DEV_VARIANTS) + variant_index) * 1000 + i


def collect_nested(ks, eps):
    """One pass up to max(ks); snapshot an estimator at every requested k.

    Nested samples mean the data-efficiency curve reflects only the amount of development
    data, not which random episodes happened to be drawn at each level.
    """
    ks = sorted(set(ks))
    if ks[-1] >= 1000:
        raise ValueError("k must stay below 1000 to keep per-(cause, variant) seed blocks disjoint")
    estimator = EmpiricalEstimator(eps=eps)
    snapshots = {}
    for i in range(1, ks[-1] + 1):
        for ci, cause in enumerate(CAUSES):
            for vi, variant in enumerate(DEV_VARIANTS):
                # oracle=False: the environment is built without ever computing the designer table.
                with SecTriageEnvironment(cause, variant, seed=dev_seed(ci, vi, i), oracle=False) as env:
                    for action in env.catalog():
                        observation = env.execute(action)
                        # A transient failure is not evidence about the cause -- the controller's
                        # ledger discards it too, so the estimator must not count it either.
                        if observation.valid:
                            estimator.observe(action.id, cause, observation.outcome)
                        else:
                            estimator.skipped_invalid += 1
                estimator.episodes += 1
        if i in ks:
            snapshots[i] = estimator.snapshot()
    return snapshots


def collect(k, eps):
    """Single-k convenience wrapper (used by tests)."""
    return collect_nested([k], eps)[k]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--k", type=int, nargs="+", default=[1, 5, 20, 100])
    parser.add_argument("--eps", type=float, default=0.01)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    catalog = SecTriageEnvironment.build_catalog(oracle=False)
    index = {}
    snapshots = collect_nested(args.k, args.eps)
    for k in sorted(snapshots):
        estimator = snapshots[k]
        record = {"schema": "hesp.empirical_table.v1", "source": f"empirical_{k}",
                  "family": "sec-triage", "k_per_cause_variant": k,
                  "dev_variants": list(DEV_VARIANTS), "dev_seed_base": DEV_SEED_BASE, "nested": True,
                  "dev_episodes": estimator.episodes, "eps": args.eps,
                  "skipped_invalid_observations": estimator.skipped_invalid,
                  "cell_coverage": estimator.coverage(catalog, HYPOTHESES),
                  "tables": estimator.tables(catalog, HYPOTHESES)}
        path = out / f"empirical_{k}.json"
        # Write LF bytes explicitly: the SHA256 below freezes these exact bytes, and git
        # normalises line endings, so a platform-dependent CRLF would break the check on
        # any other checkout (the same failure class as the v0.3 source-hash incident).
        path.write_bytes((json.dumps(record, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        index[f"empirical_{k}"] = {"file": path.name, "sha256": digest,
                                   "dev_episodes": estimator.episodes,
                                   "cell_coverage": record["cell_coverage"]}
        print(f"empirical_{k}: {estimator.episodes} dev episodes, "
              f"cell coverage {record['cell_coverage']:.3f}, sha256 {digest[:12]}")
    (out / "index.json").write_bytes((json.dumps(index, indent=2) + "\n").encode("utf-8"))


if __name__ == "__main__":
    main()
