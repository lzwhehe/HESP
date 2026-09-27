"""v1.0 part A: the spec-driven sigma-triage family."""

import copy
from pathlib import Path
import tempfile
import unittest

from hesp.audit import audit_run
from hesp.controller import Budget, run
from hesp.planner import NeverFinishPlanner
from hesp.predictors import EmpiricalEstimator
from hesp.selectors import Selector
from hesp.sigmaapp import (PROBE_IDS, RuleTablePredictor, SigmaEnvironments, make_family, sigma_suite,
                           signatures, validate_spec)

ROWS = {
    "attack": ["admin_user", "unusual_host", "none", "not_approved", "unsigned_or_renamed", "rare_first_seen",
               "interactive_shell", "off_hours", "lateral_movement", "malicious"],
    "benign_1": ["admin_user", "managed_admin_host", "approved_change", "approved", "signed_known_vendor",
                 "fleet_wide_routine", "interactive_shell", "maintenance_window", "none", "clean"],
    "benign_2": ["system_or_service", "no_logon", "none", "approved", "signed_known_vendor", "fleet_wide_routine",
                 "management_agent", "business_hours", "none", "clean"],
}
SPEC = {"rule_id": "00000000-test", "slug": "demo-rule", "title": "Demo rule", "description": "A test rule.",
        "technique": ["T1053"], "logsource": {"product": "windows"},
        "causes": {"attack": "The attack.", "benign_1": "Benign: admin work.", "benign_2": "Benign: software update."},
        "outcomes": {c: dict(zip(PROBE_IDS, row)) for c, row in ROWS.items()}}
BUDGET = Budget(max_tool_calls=10, max_decisions=12, max_tool_cost=10, max_seconds=60.0)


class SpecTests(unittest.TestCase):
    def test_valid_spec(self):
        self.assertEqual(validate_spec(SPEC), [])

    def test_out_of_vocabulary_outcome_is_rejected(self):
        bad = copy.deepcopy(SPEC)
        bad["outcomes"]["attack"]["follow_on"] = "ransomware"
        self.assertTrue(validate_spec(bad))

    def test_cause_without_a_signature_is_rejected(self):
        bad = copy.deepcopy(SPEC)
        bad["outcomes"]["benign_2"] = {**bad["outcomes"]["benign_1"], "prevalence": "rare_first_seen"}
        bad["outcomes"]["attack"]["prevalence"] = "rare_first_seen"
        self.assertTrue(any("signature" in e or "identical" in e for e in validate_spec(bad)))

    def test_signatures_are_unique_outcomes(self):
        sig = signatures(SPEC)
        self.assertIn(("follow_on", "lateral_movement"), sig["attack"])
        self.assertNotIn(("actor_account", "admin_user"), sig["attack"])   # shared with benign_1

    def test_benign_causes_and_tasks(self):
        cls = make_family(SPEC)
        self.assertEqual(cls.BENIGN, {"benign_1", "benign_2"})
        tasks = sigma_suite([SPEC])
        self.assertEqual(len(tasks), 3 * 2)
        self.assertEqual({t["rule"] for t in tasks}, {"demo-rule"})


class EpisodeTests(unittest.TestCase):
    def tables(self):
        cls = make_family(SPEC)
        est = EmpiricalEstimator()
        for i, cause in enumerate(cls.CAUSES):
            for k in range(5):
                with cls(cause, "base", seed=900 + 10 * i + k, oracle=False) as env:
                    for a in env.catalog():
                        o = env.execute(a)
                        if o.valid:
                            est.observe(a.id, cause, o.outcome)
        return {"demo-rule": est.tables(cls.build_catalog(oracle=False), cls.hypotheses_())}

    def test_controller_concludes_correctly_with_counted_tables(self):
        predictor = RuleTablePredictor(self.tables(), "empirical_5")
        envs = SigmaEnvironments([SPEC])
        for task in sigma_suite([SPEC], ("base",)):
            with self.subTest(cause=task["cause"]):
                with tempfile.TemporaryDirectory() as root:
                    with envs(task, 3) as env:
                        result = run(env, NeverFinishPlanner(), "hesp", Path(root) / "r", BUDGET,
                                     predictor=predictor, selector=Selector("eig_cost", 3),
                                     show_rankings=False, auto_finish=0.8)
                    self.assertTrue(audit_run(Path(root) / "r")["passed"])
                self.assertTrue(result["verified_simulation"])
                self.assertEqual(result["claimed_hypothesis"], task["cause"])

    def test_threat_intel_lag_and_noise(self):
        envs = SigmaEnvironments([SPEC])
        task = next(t for t in sigma_suite([SPEC], ("noise",)) if t["cause"] == "attack")
        seen = set()
        for seed in range(40):
            with envs(task, seed) as env:
                ti = next(a for a in env.catalog() if a.id == "threat_intel")
                o = env.execute(ti)
                seen.add(o.outcome if o.valid else "transient")
        self.assertTrue({"malicious", "inconclusive", "transient"} <= seen)


if __name__ == "__main__":
    unittest.main()
