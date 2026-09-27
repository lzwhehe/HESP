"""v1.0 part A, step 3: counted prediction tables for every accepted Sigma rule (PROTOCOL.md v1.0).

Same estimator as v0.6: k LLM-free development episodes per (cause, variant) over base and noise,
every probe run once per episode, transient failures not counted, eps = 0.01 smoothing. Development
seeds start at 800000 and never meet evaluation seeds. The generative outcome model is never called
(``oracle=False``). Output: one file with the tables of every rule, keyed by rule slug, plus its SHA256.

    python scripts/v10a_tables.py --specs results/v10a/specs --k 20 --out results/v10a/tables
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hesp.predictors import EmpiricalEstimator
from hesp.sigmaapp import make_family

DEV_SEED_BASE = 800_000
DEV_VARIANTS = ("base", "noise")


def load_specs(spec_dir):
    index = json.loads((Path(spec_dir) / "index.json").read_text(encoding="utf-8"))
    specs = []
    for entry in index["accepted"]:
        path = Path(spec_dir) / entry["file"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
            raise SystemExit(f"{entry['file']}: SHA256 mismatch against index.json")
        specs.append(json.loads(path.read_text(encoding="utf-8")))
    return specs, index


def count(spec, rule_index, k, eps=0.01):
    cls = make_family(spec)
    est = EmpiricalEstimator(eps=eps)
    for i in range(1, k + 1):
        for ci, cause in enumerate(cls.CAUSES):
            for vi, variant in enumerate(DEV_VARIANTS):
                seed = DEV_SEED_BASE + ((rule_index * 10 + ci) * 10 + vi) * 1000 + i
                with cls(cause, variant, seed=seed, oracle=False) as env:
                    for action in env.catalog():
                        obs = env.execute(action)
                        if obs.valid:
                            est.observe(action.id, cause, obs.outcome)
                        else:
                            est.skipped_invalid += 1
                est.episodes += 1
    catalog = cls.build_catalog(oracle=False)
    return est.tables(catalog, cls.hypotheses_()), est.episodes, est.coverage(catalog, cls.hypotheses_())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--specs", required=True)
    ap.add_argument("--k", type=int, default=20)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    specs, index = load_specs(args.specs)
    tables, meta = {}, {}
    for r, spec in enumerate(specs):
        t, episodes, coverage = count(spec, r, args.k)
        tables[spec["slug"]] = t
        meta[spec["slug"]] = {"dev_episodes": episodes, "cell_coverage": coverage}
        print(f"{spec['slug']}: {episodes} dev episodes, coverage {coverage:.3f}", flush=True)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    record = {"schema": "hesp.v10a.tables.v1", "source": f"empirical_{args.k}", "k_per_cause_variant": args.k,
              "dev_variants": list(DEV_VARIANTS), "dev_seed_base": DEV_SEED_BASE, "eps": 0.01,
              "specs_index_sha256": hashlib.sha256((Path(args.specs) / "index.json").read_bytes()).hexdigest(),
              "rules": meta, "tables": tables}
    path = out / f"empirical_{args.k}.json"
    path.write_bytes((json.dumps(record, indent=2) + "\n").encode("utf-8"))
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    (out / "index.json").write_bytes((json.dumps({f"empirical_{args.k}": {"file": path.name, "sha256": digest}},
                                                 indent=2) + "\n").encode("utf-8"))
    print(f"empirical_{args.k}: sha256 {digest}")


if __name__ == "__main__":
    main()
