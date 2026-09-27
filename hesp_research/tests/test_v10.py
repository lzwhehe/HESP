"""v1.0 part C: adversarial variants and the benign-corroboration rule."""

import json
from pathlib import Path
import tempfile
import unittest

from hesp.audit import audit_run
from hesp.controller import Budget, run, specific_support
from hesp.planner import NeverFinishPlanner
from hesp.secapp import BENIGN, INJECTION, SecTriageEnvironment, make_sec_env, sec_suite
from hesp.selectors import Selector

BUDGET = Budget(max_tool_calls=10, max_decisions=12, max_tool_cost=10, max_seconds=60.0)


def task(cause, variant):
    return next(t for t in sec_suite((variant,)) if t["cause"] == cause)


def episode(planner, cause, variant, corroborate=None, guard=True, seed=5):
    with tempfile.TemporaryDirectory() as root:
        with make_sec_env(task(cause, variant), seed) as env:
            result = run(env, planner, "hesp", Path(root) / "r", BUDGET, selector=Selector("eig_cost", seed),
                         finish_guard=guard, show_rankings=False, auto_finish=0.8, corroborate_benign=corroborate)
        audit = audit_run(Path(root) / "r")
        events = [json.loads(l) for l in (Path(root) / "r" / "events.jsonl").read_text(encoding="utf-8").splitlines()]
    return result, audit, events


class FinishWith:
    """Scripted planner: probes until ``after`` observations exist, then claims ``hypothesis``
    citing every observation so far (a stand-in for a planner that follows an injected order)."""
    name = "scripted_finish"

    def __init__(self, hypothesis, after=1):
        self.hypothesis, self.after = hypothesis, after

    def decide(self, request):
        zero = {"input_tokens": 0, "output_tokens": 0}
        if len(request["history"]) >= self.after:
            return {"kind": "finish", "hypothesis": self.hypothesis,
                    "evidence_ids": [o["id"] for o in request["history"]][-3:], "reason": "scripted", "usage": zero}
        return {"kind": "action", "action_id": request["tools"][0]["id"], "reason": "scripted", "usage": zero}


class AdversarialVariantTests(unittest.TestCase):
    def test_injection_reaches_raw_text_but_not_the_outcome(self):
        for probe in SecTriageEnvironment.PROBES:
            with self.subTest(probe=probe["id"]):
                outcomes = {}
                for variant in ("base", "inject"):
                    with make_sec_env(task("sqli_probe", variant), 3) as env:
                        action = next(a for a in env.catalog() if a.id == probe["id"])
                        obs = env.execute(action)
                        outcomes[variant] = obs.outcome
                        if variant == "inject":
                            self.assertIn(INJECTION, obs.raw)
                self.assertEqual(outcomes["base"], outcomes["inject"])

    def test_spoof_makes_sources_look_like_a_scanner(self):
        for cause in SecTriageEnvironment.CAUSES:
            with make_sec_env(task(cause, "spoof"), 3) as env:
                action = next(a for a in env.catalog() if a.id == "source_ips")
                self.assertEqual(env.execute(action).outcome, "known_scanner_asn")

    def test_benign_set(self):
        self.assertEqual(BENIGN, {"authorized_scan", "false_positive_monitor"})


class CorroborationTests(unittest.TestCase):
    def test_specific_support_uses_the_table_only(self):
        table = {"a": {"x": 0.9, "y": 0.1}, "b": {"x": 0.05, "y": 0.95}, "other": {"x": 0.5, "y": 0.5}}
        self.assertTrue(specific_support(table, "a", "x"))       # 0.9 >= 10 * 0.05; other excluded
        self.assertFalse(specific_support(table, "a", "y"))
        self.assertFalse(specific_support({"a": {"x": 0.5}, "b": {"x": 0.1}}, "a", "x"))

    def test_spoofed_single_probe_closes_the_case_without_the_rule(self):
        result, audit, _ = episode(NeverFinishPlanner(), "credential_stuffing", "spoof")
        self.assertTrue(audit["passed"], audit["errors"])
        self.assertEqual(result["claimed_hypothesis"], "authorized_scan")
        self.assertEqual(result["finished_by"], "controller")

    def test_rule_withholds_a_single_probe_benign_verdict(self):
        result, audit, events = episode(NeverFinishPlanner(), "credential_stuffing", "spoof", corroborate=2)
        self.assertTrue(audit["passed"], audit["errors"])
        self.assertNotIn(result["claimed_hypothesis"], BENIGN)
        self.assertTrue(any(e["kind"] == "controller_finish_withheld" for e in events))

    def test_rule_lets_a_corroborated_benign_case_close(self):
        result, audit, events = episode(NeverFinishPlanner(), "authorized_scan", "base", corroborate=2)
        self.assertTrue(audit["passed"], audit["errors"])
        self.assertEqual(result["claimed_hypothesis"], "authorized_scan")
        finish = next(e for e in events if e["kind"] == "controller_finish")
        self.assertGreaterEqual(len(finish["corroborating_probes"]), 2)

    def test_guard_rejects_an_uncorroborated_benign_finish_from_the_planner(self):
        result, audit, events = episode(FinishWith("authorized_scan", after=1), "credential_stuffing", "spoof",
                                        corroborate=2)
        self.assertTrue(audit["passed"], audit["errors"])
        rejected = [e for e in events if e["kind"] == "finish_rejected"]
        self.assertTrue(rejected)
        self.assertTrue(any("different probes" in r for r in rejected[0]["reasons"]))
        self.assertNotEqual(result["claimed_hypothesis"], "authorized_scan")

    def test_rule_does_not_touch_actionable_verdicts(self):
        a, _, _ = episode(NeverFinishPlanner(), "sqli_probe", "base", corroborate=2)
        b, _, _ = episode(NeverFinishPlanner(), "sqli_probe", "base", corroborate=None)
        keys = ("claimed_hypothesis", "tool_calls", "tool_cost_units", "verified_simulation")
        self.assertEqual([a[k] for k in keys], [b[k] for k in keys])


if __name__ == "__main__":
    unittest.main()
