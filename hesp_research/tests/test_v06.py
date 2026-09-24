"""v0.6 (RQ3): the predictive model estimated from observations, not from the generator."""

import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from estimate_empirical_tables import DEV_VARIANTS, collect, collect_nested, dev_seed

from hesp.analysis import BENIGN_CAUSES, security_metrics
from hesp.controller import Budget, citation_validity, run
from hesp.planner import PosteriorPlanner
from hesp.predictors import EmpiricalEstimator, FrozenPredictor
from hesp.selectors import Selector
from hesp.secapp import CAUSES, HYPOTHESES, SecTriageEnvironment, make_sec_env, sec_suite


class EmpiricalEstimationTests(unittest.TestCase):
    def test_estimator_never_consults_the_generative_model(self):
        """The whole point of RQ3: no path from the estimator back to the oracle."""
        original = SecTriageEnvironment.true_outcome_distribution

        def forbidden(*args, **kwargs):
            raise AssertionError("estimator called true_outcome_distribution")

        SecTriageEnvironment.true_outcome_distribution = staticmethod(forbidden)
        try:
            estimator = collect(1, 0.01)
        finally:
            SecTriageEnvironment.true_outcome_distribution = original
        self.assertEqual(estimator.episodes, len(CAUSES) * len(DEV_VARIANTS))

    def test_tables_are_distributions_over_the_declared_vocabulary(self):
        estimator = collect(1, 0.01)
        catalog = SecTriageEnvironment.build_catalog(oracle=False)
        tables = estimator.tables(catalog, HYPOTHESES)
        for action in catalog:
            for h in HYPOTHESES:
                row = tables[action.id][h]
                self.assertEqual(set(row), set(action.outcome_notes))
                self.assertAlmostEqual(sum(row.values()), 1.0, places=9)
                self.assertTrue(all(v > 0 for v in row.values()))   # epsilon floor, no zeros

    def test_unobserved_cells_stay_near_uniform(self):
        estimator = EmpiricalEstimator(eps=0.01)
        catalog = SecTriageEnvironment.build_catalog()
        tables = estimator.tables(catalog, HYPOTHESES)       # nothing observed at all
        self.assertEqual(estimator.coverage(catalog, HYPOTHESES), 0.0)
        for action in catalog:
            row = tables[action.id][HYPOTHESES[0]]
            self.assertAlmostEqual(min(row.values()), max(row.values()), places=9)

    def test_coverage_does_not_fall_as_development_data_grows(self):
        catalog = SecTriageEnvironment.build_catalog()
        small = collect(1, 0.01).coverage(catalog, HYPOTHESES)
        larger = collect(3, 0.01).coverage(catalog, HYPOTHESES)
        self.assertGreaterEqual(larger, small)

    def test_k_levels_are_nested_prefixes(self):
        snaps = collect_nested([1, 2], 0.01)
        small, large = snaps[1], snaps[2]
        for key, row in small.counts.items():
            for outcome, n in row.items():
                self.assertLessEqual(n, large.counts[key][outcome])
        self.assertEqual(large.episodes, 2 * small.episodes)
        # snapshots are independent copies, not views of one mutating estimator
        self.assertIsNot(small.counts, large.counts)

    def test_development_seeds_are_disjoint_from_evaluation(self):
        from hesp.study import cell_seed
        dev = {dev_seed(ci, vi, i) for ci in range(len(CAUSES)) for vi in range(len(DEV_VARIANTS))
               for i in range(1, 101)}
        self.assertEqual(len(dev), len(CAUSES) * len(DEV_VARIANTS) * 100)   # no collisions
        evaluation = {cell_seed(2026, t["task_id"], r) for t in sec_suite() for r in range(1, 4)}
        self.assertFalse(dev & evaluation)


class FrozenTableBytesTests(unittest.TestCase):
    def test_frozen_tables_are_lf_and_platform_independent(self):
        """The SHA256 freezes exact bytes; CRLF would break it on another checkout."""
        import hashlib
        import subprocess
        script = Path(__file__).resolve().parents[1] / "scripts" / "estimate_empirical_tables.py"
        with tempfile.TemporaryDirectory() as out:
            subprocess.run([sys.executable, str(script), "--k", "1", "--out", out],
                           check=True, capture_output=True)
            raw = (Path(out) / "empirical_1.json").read_bytes()
            self.assertNotIn(b"\r\n", raw)
            index = json.loads((Path(out) / "index.json").read_text(encoding="utf-8"))
            self.assertEqual(index["empirical_1"]["sha256"], hashlib.sha256(raw).hexdigest())
            self.assertNotIn(b"\r\n", (Path(out) / "index.json").read_bytes())

    def test_generation_is_deterministic(self):
        a = collect(2, 0.01).tables(SecTriageEnvironment.build_catalog(oracle=False), HYPOTHESES)
        b = collect(2, 0.01).tables(SecTriageEnvironment.build_catalog(oracle=False), HYPOTHESES)
        self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))


class ClaimRecordingTests(unittest.TestCase):
    def test_every_episode_records_what_was_claimed(self):
        with tempfile.TemporaryDirectory() as root:
            task = sec_suite()[0]
            with make_sec_env(task, 5) as env:
                result = run(env, PosteriorPlanner(), "hesp", Path(root) / "r", Budget(12, 16, 12, 60))
        self.assertEqual(result["claimed_hypothesis"], task["cause"])
        self.assertTrue(result["claimed_evidence_ids"])
        self.assertEqual(result["claim_citation_validity"], 1.0)

    def test_claim_fields_are_null_when_nothing_was_claimed(self):
        class Stopper:
            name = "stopper"

            def decide(self, request):
                return {"kind": "stop", "reason": "no"}

        with tempfile.TemporaryDirectory() as root:
            with make_sec_env(sec_suite()[1], 5) as env:
                result = run(env, Stopper(), "memory_only", Path(root) / "r", Budget(12, 16, 12, 60))
        self.assertIsNone(result["claimed_hypothesis"])
        self.assertIsNone(result["claim_citation_validity"])

    def test_citation_validity_rejects_unsupported_and_missing_ids(self):
        class Ledger:
            state = {"version": 2}
            scores = {}
            evidence = [{"observation_id": "o0001", "used": True, "state_version": 2,
                         "relations": {"dns_c2": "support"}},
                        {"observation_id": "o0002", "used": True, "state_version": 1,
                         "relations": {"dns_c2": "support"}}]

        self.assertEqual(citation_validity(Ledger(), "dns_c2", ["o0001"]), 1.0)
        self.assertEqual(citation_validity(Ledger(), "dns_c2", ["o0001", "o0002"]), 0.5)   # stale state
        self.assertEqual(citation_validity(Ledger(), "dns_c2", ["o0001", "o9999"]), 0.5)   # missing
        self.assertEqual(citation_validity(Ledger(), "sqli_probe", ["o0001"]), 0.0)        # unsupported
        self.assertIsNone(citation_validity(Ledger(), "dns_c2", []))


class SecurityMetricTests(unittest.TestCase):
    def test_benign_set_is_a_subset_of_the_family(self):
        self.assertTrue(BENIGN_CAUSES < set(CAUSES))

    def test_rates_use_the_right_denominators(self):
        rows = [{"cause": "dns_c2", "claimed_hypothesis": "authorized_scan",
                 "verified_simulation": False, "claim_citation_validity": 0.0},
                {"cause": "authorized_scan", "claimed_hypothesis": "dns_c2",
                 "verified_simulation": False, "claim_citation_validity": 1.0},
                {"cause": "sqli_probe", "claimed_hypothesis": None,
                 "verified_simulation": False, "claim_citation_validity": None}]
        m = security_metrics(rows)
        self.assertEqual(m["episodes_with_a_claim"], 2)
        self.assertEqual(m["missed_attack_rate"], 1.0)      # 1 of 1 actionable episodes with a claim
        self.assertEqual(m["false_escalation_rate"], 1.0)   # 1 of 1 benign episodes with a claim
        self.assertEqual(m["unresolved_rate"], 1.0)         # over all 3 episodes

    def test_empty_denominators_report_none_not_zero(self):
        m = security_metrics([{"cause": "dns_c2", "claimed_hypothesis": None,
                               "verified_simulation": False, "claim_citation_validity": None}])
        self.assertIsNone(m["missed_attack_rate"])
        self.assertIsNone(m["false_escalation_rate"])
        self.assertIsNone(m["evidence_citation_validity"])


class FrozenEmpiricalPredictorTests(unittest.TestCase):
    def test_an_empirical_table_drives_a_full_episode(self):
        estimator = collect(2, 0.01)
        tables = estimator.tables(SecTriageEnvironment.build_catalog(oracle=False), HYPOTHESES)
        predictor = FrozenPredictor(tables, "empirical_2")
        with tempfile.TemporaryDirectory() as root:
            task = sec_suite()[3]
            with make_sec_env(task, 5) as env:
                result = run(env, PosteriorPlanner(), "hesp", Path(root) / "r", Budget(12, 16, 12, 60),
                             predictor=predictor, selector=Selector("eig_cost", 5))
        self.assertEqual(result["prediction_source"], "empirical_2")


if __name__ == "__main__":
    unittest.main()
