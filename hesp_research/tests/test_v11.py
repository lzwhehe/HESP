"""v1.1: confirmation-aware controller stop, source-level corroboration, raw-text redaction,
more attacker variants, and planner prompt variants."""

import json
from pathlib import Path
import tempfile
import unittest

from hesp.audit import audit_run
from hesp.controller import Budget, run
from hesp.llm import PROMPT_VARIANTS, SYSTEM, LLMPlanner, render_request
from hesp.planner import NeverFinishPlanner
from hesp.predictors import FrozenPredictor
from hesp.secapp import BENIGN, INJECTION, INJECTIONS, SOURCE_GROUPS, make_sec_env, sec_suite
from hesp.selectors import Selector

BUDGET = Budget(max_tool_calls=10, max_decisions=12, max_tool_cost=10, max_seconds=60.0)
TABLE = json.loads((Path(__file__).resolve().parents[1] / "results/v06_tables/empirical_20.json")
                   .read_text(encoding="utf-8"))["tables"]


def task(cause, variant):
    return next(t for t in sec_suite((variant,)) if t["cause"] == cause)


def episode(cause, variant, seed=5, **kw):
    with tempfile.TemporaryDirectory() as root:
        with make_sec_env(task(cause, variant), seed) as env:
            result = run(env, NeverFinishPlanner(), kw.pop("mode", "hesp"), Path(root) / "r", BUDGET,
                         selector=Selector("eig_cost", seed), show_rankings=False, auto_finish=0.8,
                         predictor=FrozenPredictor(TABLE, "empirical_20"), **kw)
        audit = audit_run(Path(root) / "r")
        events = [json.loads(l) for l in (Path(root) / "r" / "events.jsonl").read_text(encoding="utf-8").splitlines()]
    return result, audit, events


class ConfirmStopTests(unittest.TestCase):
    def test_posterior_stop_concludes_dns_c2_by_elimination(self):
        result, audit, _ = episode("dns_c2", "base")
        self.assertTrue(audit["passed"], audit["errors"])
        self.assertEqual(result["claimed_hypothesis"], "dns_c2")
        self.assertFalse(result["verified_simulation"])       # no confirming signature cited

    def test_confirm_stop_waits_for_the_signature(self):
        result, audit, events = episode("dns_c2", "base", stop_rule="confirm")
        self.assertTrue(audit["passed"], audit["errors"])
        self.assertEqual(result["claimed_hypothesis"], "dns_c2")
        self.assertTrue(result["verified_simulation"])
        self.assertTrue(any(e["kind"] == "controller_finish_withheld" for e in events))

    def test_confirm_stop_is_verified_on_every_base_cause(self):
        for cause in [t["cause"] for t in sec_suite(("base",))]:
            with self.subTest(cause=cause):
                result, audit, _ = episode(cause, "base", stop_rule="confirm")
                self.assertTrue(audit["passed"], audit["errors"])
                self.assertTrue(result["verified_simulation"])


class SourceCorroborationTests(unittest.TestCase):
    def test_source_groups_cover_every_probe(self):
        from hesp.secapp import PROBES
        self.assertEqual(set(SOURCE_GROUPS), {p["id"] for p in PROBES})
        self.assertEqual(SOURCE_GROUPS["source_ips"], SOURCE_GROUPS["threat_intel"])

    def scripted(self, unit):
        """A planner that queries the two probes behind the forged feed, then claims a benign cause
        citing both (memory_only: its own probe choices are executed)."""
        class Scripted:
            name = "scripted_two_same_source"

            def decide(self, request):
                zero = {"input_tokens": 0, "output_tokens": 0}
                done = [o["action_id"] for o in request["history"]]
                for probe in ("source_ips", "threat_intel"):
                    if probe not in done:
                        return {"kind": "action", "action_id": probe, "reason": "s", "usage": zero}
                return {"kind": "finish", "hypothesis": "authorized_scan",
                        "evidence_ids": [o["id"] for o in request["history"]], "reason": "s", "usage": zero}
        with tempfile.TemporaryDirectory() as root:
            with make_sec_env(task("credential_stuffing", "spoof_feed"), 5) as env:
                result = run(env, Scripted(), "memory_only", Path(root) / "r", BUDGET, finish_guard=True,
                             predictor=FrozenPredictor(TABLE, "empirical_20"), corroborate_benign=2,
                             corroborate_unit=unit)
            self.assertTrue(audit_run(Path(root) / "r")["passed"])
        return result

    def test_forged_feed_beats_probe_level_corroboration(self):
        self.assertEqual(self.scripted("probe")["claimed_hypothesis"], "authorized_scan")

    def test_source_level_corroboration_withholds_it(self):
        result = self.scripted("source")
        self.assertNotEqual(result["claimed_hypothesis"], "authorized_scan")
        self.assertGreater(result["finish_rejections"], 0)

    def test_honest_authorized_scan_still_closes_under_source_rule(self):
        result, audit, _ = episode("authorized_scan", "base", corroborate_benign=2, finish_guard=True,
                                   corroborate_unit="source")
        self.assertTrue(audit["passed"], audit["errors"])
        self.assertEqual(result["claimed_hypothesis"], "authorized_scan")


class RedactionAndVariantTests(unittest.TestCase):
    def test_redaction_keeps_injection_out_of_the_prompt(self):
        for redact in (False, True):
            _, _, events = episode("sqli_probe", "inject", mode="memory_only", redact_raw=redact)
            prompts = [render_request(e["request"]) for e in events if e["kind"] == "planner_request"]
            self.assertEqual(any("NOTE FROM SECURITY OPERATIONS" in p for p in prompts), not redact)

    def test_new_injection_variants_do_not_change_outcomes(self):
        from hesp.secapp import PROBES
        for variant, text in (("inject_b", "ticket-bot"), ("inject_c", "analyst_override"), ("inject_one", "NOTE FROM SECURITY")):
            with self.subTest(variant=variant):
                seen = False
                for probe in PROBES:
                    outs = {}
                    for v in ("base", variant):
                        with make_sec_env(task("dns_c2", v), 3) as env:
                            obs = env.execute(next(a for a in env.catalog() if a.id == probe["id"]))
                            outs[v] = obs.outcome
                            seen |= v == variant and text in obs.raw
                    self.assertEqual(outs["base"], outs[variant])
                self.assertTrue(seen)

    def test_prompt_variants_only_extend_the_system_prompt(self):
        class Dummy:
            model = "m"
        for name in PROMPT_VARIANTS:
            planner = LLMPlanner(Dummy(), prompt_variant=name)
            self.assertTrue(planner.system.startswith(SYSTEM))
            self.assertEqual(planner.name == "ollama:m", name == "v1")


if __name__ == "__main__":
    unittest.main()
