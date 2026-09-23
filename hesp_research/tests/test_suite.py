import json
from pathlib import Path
import tempfile
import unittest

from hesp.analysis import summarize
from hesp.audit import audit_run
from hesp.core import Action
from hesp.planner import PosteriorPlanner
from hesp.selectors import Selector, _map_contrast
from hesp.study import cell_seed, run_suite
from hesp.webapp import make_web_env, web_suite


def act(aid, cost, table):
    return Action(aid, "t", aid, cost, table)


class SelectorTests(unittest.TestCase):
    rankings = [{"action_id": "cheap", "expected_information_gain_bits": .6, "cost": 1, "score": .6},
                {"action_id": "rich", "expected_information_gain_bits": 1.5, "cost": 3, "score": .5}]

    def test_eig_cost_vs_eig(self):
        self.assertEqual(Selector("eig_cost").choose(self.rankings, {}, {}), "cheap")
        self.assertEqual(Selector("eig").choose(self.rankings, {}, {}), "rich")

    def test_random_is_seeded_and_legal(self):
        picks = {Selector("random", s).choose(self.rankings, {}, {}) for s in range(20)}
        self.assertEqual(picks, {"cheap", "rich"})
        self.assertEqual(Selector("random", 4).choose(self.rankings, {}, {}),
                         Selector("random", 4).choose(self.rankings, {}, {}))

    def test_map_greedy_tests_the_leading_hypothesis(self):
        scores = {"a": .7, "b": .2, "c": .1}
        confirm_a = act("confirm_a", 1, {"a": {"y": .99, "n": .01}, "b": {"y": .01, "n": .99}, "c": {"y": .01, "n": .99}})
        split_bc = act("split_bc", 1, {"a": {"y": .5, "n": .5}, "b": {"y": .99, "n": .01}, "c": {"y": .01, "n": .99}})
        self.assertGreater(_map_contrast(scores, confirm_a), _map_contrast(scores, split_bc))
        rankings = [{"action_id": x, "expected_information_gain_bits": 1, "cost": 1, "score": 1}
                    for x in ("confirm_a", "split_bc")]
        self.assertEqual(Selector("map_greedy").choose(rankings, scores, {"confirm_a": confirm_a, "split_bc": split_bc}),
                         "confirm_a")

    def test_unknown_selector_and_empty(self):
        with self.assertRaises(ValueError):
            Selector("oracle")
        self.assertIsNone(Selector().choose([], {}, {}))


class PosteriorPlannerTests(unittest.TestCase):
    def request(self, scores, evidence, history=(), cost=5):
        return {"state_version": 1, "remaining_tool_cost": cost, "remaining_tool_calls": 3,
                "tools": [{"id": "x", "cost": 1}, {"id": "y", "cost": 3}], "history": list(history),
                "investigation": {"hypotheses": [{"id": h, "score": p} for h, p in scores.items()],
                                  "evidence": evidence}}

    def test_finishes_only_with_current_supporting_evidence(self):
        ev = [{"observation_id": "o1", "used": True, "state_version": 0, "relations": {"a": "support"}},
              {"observation_id": "o2", "used": True, "state_version": 1, "relations": {"a": "support"}}]
        d = PosteriorPlanner().decide(self.request({"a": .95, "b": .05}, ev))
        self.assertEqual((d["kind"], d["hypothesis"], d["evidence_ids"]), ("finish", "a", ["o2"]))
        d = PosteriorPlanner().decide(self.request({"a": .95, "b": .05}, ev[:1]))
        self.assertEqual(d["kind"], "action")

    def test_catalogue_order_retry_invalid_and_budget(self):
        hist = [{"action_id": "x", "state_version": 1, "valid": False}]
        self.assertEqual(PosteriorPlanner().decide(self.request({"a": .5, "b": .5}, [], hist))["action_id"], "x")
        hist = [{"action_id": "x", "state_version": 1, "valid": True}]
        self.assertEqual(PosteriorPlanner().decide(self.request({"a": .5, "b": .5}, [], hist, cost=2))["kind"], "stop")


class SuiteTests(unittest.TestCase):
    arms = {"seq": {"mode": "memory_only", "planner": lambda s: PosteriorPlanner()},
            "hesp": {"mode": "hesp", "planner": lambda s: PosteriorPlanner()}}

    def test_paired_seeds_and_resume(self):
        self.assertEqual(cell_seed(1, "t", 0), cell_seed(1, "t", 0))
        self.assertNotEqual(cell_seed(1, "t", 0), cell_seed(1, "t", 1))
        tasks = web_suite()[:3]
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "s"
            report, rows = run_suite(path, tasks, self.arms, make_web_env, repeats=2,
                                     comparisons=[("hesp", "seq")])
            self.assertEqual(len(rows), 12)
            self.assertEqual(report["paired_verification"]["hesp_minus_seq"]["task_clusters"], 3)
            for folder in path.glob("run*"):
                self.assertTrue(audit_run(folder)["passed"], folder.name)
            with self.assertRaises(FileExistsError):
                run_suite(path, tasks, self.arms, make_web_env, repeats=2)
            lines = (path / "outcomes.jsonl").read_text(encoding="utf-8").splitlines()
            (path / "outcomes.jsonl").write_text("\n".join(lines[:-2]) + "\n", encoding="utf-8")
            report2, rows2 = run_suite(path, tasks, self.arms, make_web_env, repeats=2,
                                       comparisons=[("hesp", "seq")], resume=True)
            self.assertEqual(len(rows2), 12)
            self.assertEqual(len(list(path.glob("_aborted_*"))), 2)
            # Deterministic cells rerun to identical outcomes (wall time aside).
            for arm in self.arms:
                self.assertEqual(report2["modes"][arm]["statuses"], report["modes"][arm]["statuses"])
                self.assertEqual(report2["modes"][arm]["tool_cost_units"], report["modes"][arm]["tool_cost_units"])
            with self.assertRaises(ValueError):
                run_suite(path, tasks, self.arms, make_web_env, repeats=3, resume=True)

    def test_manifest_hides_nothing_from_audit_but_planner_never_sees_it(self):
        tasks = web_suite()[:1]
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "s"
            run_suite(path, tasks, self.arms, make_web_env, repeats=1)
            manifest = json.loads((path / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["tasks"][0]["cause"], tasks[0]["cause"])
            for folder in path.glob("run*"):
                for line in (folder / "events.jsonl").read_text(encoding="utf-8").splitlines():
                    event = json.loads(line)
                    if event["kind"] == "planner_request":
                        self.assertNotIn("web-base-00", json.dumps(event))


class GeneralAnalysisTests(unittest.TestCase):
    def row(self, task, arm, ok, cost):
        return {"task_id": task, "repeat": 0, "mode": "hesp", "arm": arm, "verified_simulation": ok,
                "status": "VERIFIED_SIMULATION" if ok else "STOPPED_UNRESOLVED", "tool_calls": cost,
                "tool_cost_units": cost, "planner_calls": 1, "wall_seconds": .1,
                "reported_input_tokens": 0, "reported_output_tokens": 0}

    def test_custom_arms_and_paired_cost(self):
        rows = [self.row("a", "x", True, 2), self.row("a", "y", False, 5),
                self.row("b", "x", True, 3), self.row("b", "y", True, 3)]
        rep = summarize(rows, arms=["x", "y"], comparisons=[("x", "y")])
        self.assertEqual(rep["paired_verification"]["x_minus_y"]["difference"], .5)
        self.assertEqual(rep["paired_verification"]["x_minus_y"]["tasks_better"], 1)
        self.assertEqual(rep["paired_tool_cost"]["x_minus_y"]["difference"], -1.5)
        self.assertEqual(rep["modes"]["y"]["tool_cost_when_verified"], 3)
        with self.assertRaises(ValueError):
            summarize(rows[:-1], arms=["x", "y"])
        with self.assertRaises(ValueError):
            summarize(rows, arms=["x"])


if __name__ == "__main__":
    unittest.main()
