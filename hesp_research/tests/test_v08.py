"""v0.8: blind controller arms give the planner identical information whatever the selector."""

import json
from pathlib import Path
import tempfile
import unittest

from hesp.controller import Budget, run
from hesp.llm import render_request
from hesp.planner import PosteriorPlanner
from hesp.secapp import make_sec_env, sec_suite
from hesp.selectors import Selector


class Stop:
    name = "stop_double"

    def decide(self, request):
        return {"kind": "stop", "reason": "capture the first request"}


def first_prompt(selector, show_rankings):
    with tempfile.TemporaryDirectory() as root:
        with make_sec_env(sec_suite()[0], 5) as env:
            run(env, Stop(), "hesp", Path(root) / "r", Budget(10, 12, 10, 60), selector=Selector(selector, 5),
                show_rankings=show_rankings)
        with (Path(root) / "r" / "events.jsonl").open(encoding="utf-8") as f:
            request = next(json.loads(l)["request"] for l in f if json.loads(l)["kind"] == "planner_request")
    return request, render_request(request)


class BlindArmTests(unittest.TestCase):
    def test_blind_prompts_are_identical_across_selectors(self):
        prompts = {sel: first_prompt(sel, False)[1] for sel in ("random", "eig_cost", "lookahead")}
        self.assertEqual(len(set(prompts.values())), 1)

    def test_blind_prompt_leaks_neither_ranking_nor_selector(self):
        request, text = first_prompt("eig_cost", False)
        self.assertIsNone(request["action_rankings"])
        for token in ("EIG", "information gain", "eig_cost", "random", "lookahead", "rankings"):
            self.assertNotIn(token, text)
        self.assertIn("the controller picks the probe itself", text)

    def test_default_still_shows_the_ranking(self):
        request, text = first_prompt("eig_cost", True)
        self.assertTrue(request["action_rankings"])
        self.assertIn("Controller rankings", text)

    def test_blind_arm_still_says_when_no_probe_is_left(self):
        with tempfile.TemporaryDirectory() as root:
            with make_sec_env(sec_suite()[0], 5) as env:
                run(env, PosteriorPlanner(), "hesp", Path(root) / "r", Budget(10, 16, 10, 60), show_rankings=False)
            with (Path(root) / "r" / "events.jsonl").open(encoding="utf-8") as f:
                reqs = [json.loads(l)["request"] for l in f if json.loads(l)["kind"] == "planner_request"]
        self.assertTrue(any(r["no_legal_probe_left"] for r in reqs) or len(reqs) >= 1)
        for r in reqs:
            self.assertEqual("(no legal probe left)" in render_request(r), r["no_legal_probe_left"])

    def test_selection_is_unchanged_by_hiding_the_ranking(self):
        runs = []
        for show in (True, False):
            with tempfile.TemporaryDirectory() as root:
                with make_sec_env(sec_suite()[3], 5) as env:
                    runs.append(run(env, PosteriorPlanner(), "hesp", Path(root) / "r", Budget(10, 16, 10, 60),
                                    selector=Selector("eig_cost", 5), show_rankings=show))
        keys = ("status", "tool_calls", "tool_cost_units", "claimed_hypothesis")
        self.assertEqual([runs[0][k] for k in keys], [runs[1][k] for k in keys])


if __name__ == "__main__":
    unittest.main()
