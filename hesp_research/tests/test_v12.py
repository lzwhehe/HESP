"""v1.2: joint-evidence stop rules, specificity ratio, joint-identification verifier, stall recovery, and the
comp-triage family. Every option is off by default; the defaults must reproduce v1.1 exactly."""

import json
from pathlib import Path
import tempfile
import unittest

from hesp.audit import audit_run
from hesp.compapp import SCENARIOS, CompEnvironments, comp_suite, signatures, validate
from hesp.controller import Budget, run
from hesp.planner import NeverFinishPlanner
from hesp.predictors import FrozenPredictor
from hesp.secapp import make_sec_env, sec_suite
from hesp.selectors import Selector

BUDGET = Budget(max_tool_calls=10, max_decisions=12, max_tool_cost=10, max_seconds=60.0)
TABLE = json.loads((Path(__file__).resolve().parents[1] / "results/v06_tables/empirical_20.json")
                   .read_text(encoding="utf-8"))["tables"]
VOLATILE = {"wall_seconds", "source_sha256"}


def task(cause, variant):
    return next(t for t in sec_suite((variant,)) if t["cause"] == cause)


def episode(cause, variant="base", seed=5, planner=None, **kw):
    with tempfile.TemporaryDirectory() as root:
        with make_sec_env(task(cause, variant), seed) as env:
            result = run(env, planner or NeverFinishPlanner(), kw.pop("mode", "hesp"), Path(root) / "r", BUDGET,
                         selector=Selector("eig_cost", seed), show_rankings=False, auto_finish=kw.pop("auto_finish", 0.8),
                         predictor=FrozenPredictor(TABLE, "empirical_20"), **kw)
        audit = audit_run(Path(root) / "r")
        events = [json.loads(l) for l in (Path(root) / "r" / "events.jsonl").read_text(encoding="utf-8").splitlines()]
    return result, audit, events


class AlwaysWrongFinisher:
    """Proposes an unsupported finish at every decision (the guard must reject it)."""
    name = "always_wrong_finisher"

    def decide(self, request):
        return {"kind": "finish", "hypothesis": "sqli_probe", "evidence_ids": [], "reason": "insist",
                "usage": {"input_tokens": 0, "output_tokens": 0}}


class DefaultsTests(unittest.TestCase):
    def test_explicit_defaults_reproduce_v11(self):
        a, _, _ = episode("dns_c2")
        b, _, _ = episode("dns_c2", specific_ratio=10.0, finish_rejection_limit=None, record_joint=False)
        self.assertEqual({k: v for k, v in a.items() if k not in VOLATILE},
                         {k: v for k, v in b.items() if k not in VOLATILE})
        self.assertNotIn("verified_joint", a)


class JointEvidenceTests(unittest.TestCase):
    def test_joint_verifier_accepts_elimination_that_the_signature_verifier_rejects(self):
        result, audit, _ = episode("dns_c2", record_joint=True)
        self.assertTrue(audit["passed"], audit["errors"])
        self.assertEqual(result["claimed_hypothesis"], "dns_c2")
        self.assertFalse(result["verified_simulation"])
        self.assertTrue(result["verified_joint"])

    def test_joint_verifier_agrees_on_a_signature_verdict(self):
        result, _, _ = episode("credential_stuffing", record_joint=True)
        self.assertTrue(result["verified_simulation"])
        self.assertTrue(result["verified_joint"])

    def test_joint_stop_rules_are_audited(self):
        for rule in ("joint", "joint_open"):
            with self.subTest(rule=rule):
                result, audit, _ = episode("sqli_probe", stop_rule=rule, record_joint=True)
                self.assertTrue(audit["passed"], audit["errors"])

    def test_higher_ratio_never_concludes_earlier(self):
        low, _, _ = episode("dns_c2", stop_rule="joint_open", specific_ratio=3.0)
        high, _, _ = episode("dns_c2", stop_rule="joint_open", specific_ratio=30.0)
        self.assertGreaterEqual(high["tool_calls"], low["tool_calls"])

    def test_unknown_stop_rule_is_rejected(self):
        with self.assertRaises(ValueError):
            episode("dns_c2", stop_rule="majority")


class StallRecoveryTests(unittest.TestCase):
    def test_v11_behaviour_stalls(self):
        result, audit, _ = episode("dns_c2", planner=AlwaysWrongFinisher(), finish_guard=True, auto_finish=None)
        self.assertTrue(audit["passed"], audit["errors"])
        self.assertEqual(result["status"], "DECISION_BUDGET_EXCEEDED")
        self.assertEqual(result["tool_calls"], 0)

    def test_limit_forces_probes(self):
        result, audit, events = episode("dns_c2", planner=AlwaysWrongFinisher(), finish_guard=True,
                                        auto_finish=0.8, stop_rule="confirm", finish_rejection_limit=2)
        self.assertTrue(audit["passed"], audit["errors"])
        self.assertGreater(result["tool_calls"], 0)
        self.assertTrue(any(e["kind"] == "forced_probe" for e in events))
        self.assertTrue(result["verified_simulation"])


class CompFamilyTests(unittest.TestCase):
    def test_scenarios_are_valid_distributions(self):
        for name, scenario in SCENARIOS.items():
            with self.subTest(name=name):
                self.assertEqual(validate(scenario), [])

    def test_some_causes_have_no_single_observation_signature(self):
        missing = [c for s in SCENARIOS.values() for c, sig in signatures(s["outcomes"]).items() if not sig]
        self.assertGreaterEqual(len(missing), 3)

    def test_every_scenario_pairs_one_attack_with_benign_explanations(self):
        for name, s in SCENARIOS.items():
            attacks = [c for c in s["causes"] if c.startswith("attack")]
            self.assertEqual(len(attacks), 1, name)

    def test_suite_and_sandbox(self):
        tasks = comp_suite()
        self.assertEqual(len(tasks), 24)
        envs = CompEnvironments()
        with envs(tasks[0], 3) as env:
            obs = env.execute(env.catalog()[0])
            self.assertTrue(obs.valid)
            self.assertEqual(env.verify_joint("attack_lateral" if tasks[0]["cause"] != "attack_lateral" else "x"), False)


if __name__ == "__main__":
    unittest.main()
