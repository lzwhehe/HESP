"""v0.9: the controller may conclude on its own (auto_finish); arms without it are unchanged."""

import json
from pathlib import Path
import tempfile
import unittest

from hesp.audit import audit_run
from hesp.controller import Budget, controller_claim, run
from hesp.core import Ledger
from hesp.planner import NeverFinishPlanner, PosteriorPlanner
from hesp.secapp import make_sec_env, sec_suite
from hesp.selectors import Selector

BUDGET = Budget(max_tool_calls=10, max_decisions=12, max_tool_cost=10, max_seconds=60.0)


def episode(planner, mode, task=0, auto_finish=None, seed=5):
    with tempfile.TemporaryDirectory() as root:
        with make_sec_env(sec_suite()[task], seed) as env:
            result = run(env, planner, mode, Path(root) / "r", BUDGET, selector=Selector("eig_cost", seed),
                         show_rankings=False, auto_finish=auto_finish)
        audit = audit_run(Path(root) / "r")
        events = [json.loads(l) for l in (Path(root) / "r" / "events.jsonl").read_text(encoding="utf-8").splitlines()]
    return result, audit, events


class ControllerStopTests(unittest.TestCase):
    def test_never_finishing_planner_gets_no_claim_without_auto_finish(self):
        result, audit, _ = episode(NeverFinishPlanner(), "hesp")
        self.assertTrue(audit["passed"], audit["errors"])
        self.assertIsNone(result["claimed_hypothesis"])
        self.assertIsNone(result["finished_by"])
        self.assertFalse(result["verified_simulation"])

    def test_controller_concludes_for_a_never_finishing_planner(self):
        for mode in ("hesp", "memory_only"):
            with self.subTest(mode=mode):
                result, audit, events = episode(NeverFinishPlanner(), mode, auto_finish=0.8)
                self.assertTrue(audit["passed"], audit["errors"])
                self.assertEqual(result["finished_by"], "controller")
                self.assertIsNotNone(result["claimed_hypothesis"])
                claim = next(e for e in events if e["kind"] == "controller_finish")
                self.assertGreaterEqual(claim["scores"][claim["hypothesis"]], 0.8)

    def test_hesp_auto_finish_is_mostly_right_on_base_tasks(self):
        tasks = [i for i, t in enumerate(sec_suite()) if t["variant"] == "base"]
        verified = [episode(NeverFinishPlanner(), "hesp", task=i, auto_finish=0.8)[0]["verified_simulation"]
                    for i in tasks]
        self.assertGreaterEqual(sum(verified), len(tasks) - 1)

    def test_planner_may_still_finish_first(self):
        result, audit, _ = episode(PosteriorPlanner(0.6), "hesp", auto_finish=0.99)
        self.assertTrue(audit["passed"], audit["errors"])
        self.assertEqual(result["finished_by"], "planner")

    def test_claim_needs_threshold_and_current_support(self):
        ledger = Ledger({"a": 0.5, "b": 0.5})
        self.assertIsNone(controller_claim(ledger, 0.8))
        ledger.scores = {"a": 0.9, "b": 0.1}
        self.assertIsNone(controller_claim(ledger, 0.8))   # no supporting observation yet

    def test_arms_without_auto_finish_are_unchanged(self):
        runs = [episode(PosteriorPlanner(), "hesp", task=3, auto_finish=None)[0] for _ in range(2)]
        keys = ("status", "tool_calls", "tool_cost_units", "planner_calls", "replan_signals", "claimed_hypothesis")
        self.assertEqual([runs[0][k] for k in keys], [runs[1][k] for k in keys])
        self.assertEqual(runs[0]["finished_by"], "planner")

    def test_planner_prompt_does_not_reveal_the_stop_rule(self):
        from hesp.llm import render_request
        firsts = []
        for auto in (None, 0.8):
            _, _, events = episode(NeverFinishPlanner(), "memory_only", auto_finish=auto)
            firsts.append(render_request(next(e["request"] for e in events if e["kind"] == "planner_request")))
        self.assertEqual(firsts[0], firsts[1])


if __name__ == "__main__":
    unittest.main()
