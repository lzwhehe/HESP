import json
from pathlib import Path
import sys
import tempfile
import unittest

from hesp.controller import Budget, MODES, run, validate_decision
from hesp.environment import CAUSES, SimulatedEnvironment, actions
from hesp.planner import ScriptedPlanner, SubprocessPlanner


class FixedPlanner:
    name = "unit_test_double"

    def __init__(self, decision):
        self.decision = decision

    def decide(self, request):
        return self.decision


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def experiment(self, planner=None, mode="hesp", budget=None, cause="owner_policy"):
        return run(SimulatedEnvironment(cause), planner or ScriptedPlanner(), mode, self.root / "run", budget)

    def events(self):
        return [json.loads(x) for x in (self.root / "run/events.jsonl").read_text().splitlines()]

    def test_all_modes_and_cases_complete_fixture(self):
        for i, cause in enumerate(CAUSES):
            for mode in MODES:
                result = run(SimulatedEnvironment(cause), ScriptedPlanner(), mode, self.root / f"{i}_{mode}")
                self.assertTrue(result["verified_simulation"])
                self.assertFalse(result["research_claim_allowed"])

    def test_predictions_are_logged_before_observations(self):
        self.experiment()
        registered = set()
        for event in self.events():
            if event["kind"] == "prediction_registered":
                registered.add(event["action"]["id"])
            if event["kind"] == "observation":
                self.assertIn(event["observation"]["action_id"], registered)

    def test_planner_does_not_receive_hidden_answer(self):
        self.experiment()
        request = next(e["request"] for e in self.events() if e["kind"] == "planner_request")
        self.assertNotIn("_cause", json.dumps(request))
        self.assertNotIn("fixture_cause", json.dumps(request))
        self.assertEqual(request["task"]["initial_observation"], "Document operation did not complete")

    def test_baseline_does_not_receive_structured_ledger(self):
        self.experiment(mode="react_style")
        requests = [e["request"] for e in self.events() if e["kind"] == "planner_request"]
        self.assertTrue(all("investigation" not in r and "action_rankings" not in r for r in requests))

    def test_memory_control_has_ledger_without_rankings(self):
        self.experiment(mode="memory_only")
        requests = [e["request"] for e in self.events() if e["kind"] == "planner_request"]
        self.assertTrue(all("investigation" in r and "action_rankings" not in r for r in requests))

    def test_hesp_avoids_zero_ig_help_first(self):
        self.experiment()
        first = next(e for e in self.events() if e["kind"] == "prediction_registered")
        self.assertNotEqual(first["action"]["id"], "read_help")

    def test_duplicate_calls_blocked_and_loop_bounded(self):
        planner = FixedPlanner({"kind": "action", "action_id": "read_help", "reason": "repeat"})
        result = self.experiment(planner, "react_style", Budget(max_decisions=4))
        self.assertEqual(result["tool_calls"], 1)
        self.assertEqual(result["blocked_duplicate_proposals"], 3)
        self.assertEqual(result["status"], "DECISION_BUDGET_EXCEEDED")

    def test_unknown_usage_not_zero(self):
        result = self.experiment(FixedPlanner({"kind": "stop", "reason": "test"}))
        self.assertIsNone(result["reported_input_tokens"])
        self.assertEqual(result["usage_unknown_calls"], 1)

    def test_tool_budget_enforced(self):
        result = self.experiment(mode="react_style", budget=Budget(max_tool_calls=1))
        self.assertEqual(result["status"], "TOOL_BUDGET_EXCEEDED")
        self.assertEqual(result["tool_calls"], 1)

    def test_unknown_tool_blocks_execution(self):
        result = self.experiment(FixedPlanner({"kind": "action", "action_id": "live_scan", "reason": "bad"}))
        self.assertEqual(result["status"], "SCOPE_BLOCKED")
        self.assertEqual(result["tool_calls"], 0)

    def test_high_confidence_claim_is_not_success(self):
        planner = FixedPlanner({"kind": "finish", "hypothesis": "owner_policy", "evidence_ids": ["fake"], "reason": "I am sure"})
        result = self.experiment(planner)
        self.assertFalse(result["verified_simulation"])
        self.assertEqual(result["status"], "UNVERIFIED_CLAIM")

    def test_malformed_decision_fails_closed(self):
        result = self.experiment(FixedPlanner({"action": "read_help"}))
        self.assertEqual(result["status"], "PLANNER_ERROR")
        self.assertEqual(result["tool_calls"], 0)

    def test_output_directory_is_not_overwritten(self):
        self.experiment()
        with self.assertRaises(FileExistsError):
            self.experiment()

    def test_independent_verifier_requires_matching_evidence(self):
        env = SimulatedEnvironment("owner_policy")
        obs = env.execute(next(a for a in actions() if a.id == "inspect_owner"))
        self.assertFalse(env.verify("session_expired", [obs.id]))
        self.assertFalse(env.verify("owner_policy", ["fake"]))
        self.assertTrue(env.verify("owner_policy", [obs.id]))

    def test_bad_budget_rejected(self):
        for value in (0, -1, True):
            with self.assertRaises(ValueError):
                Budget(max_tool_calls=value).validate()

    def test_invalid_token_usage_rejected(self):
        with self.assertRaises(ValueError):
            validate_decision({"kind": "stop", "reason": "x", "usage": {"input_tokens": -1, "output_tokens": 0}}, CAUSES)

    def test_external_protocol(self):
        adapter = SubprocessPlanner([sys.executable, "-c",
            "import sys,json; r=json.load(sys.stdin); print(json.dumps({'kind':'stop','reason':r['protocol']}))"])
        self.assertEqual(adapter.decide({"protocol": "test"})["reason"], "test")

    def test_external_invalid_json(self):
        adapter = SubprocessPlanner([sys.executable, "-c", "print('not json')"])
        with self.assertRaises(ValueError):
            adapter.decide({})

    def test_external_command_is_argv_not_shell(self):
        with self.assertRaises(ValueError):
            SubprocessPlanner("python script.py")
