import json
from pathlib import Path
import tempfile
import unittest

from hesp.analysis import summarize
from hesp.audit import audit_run
from hesp.controller import Budget, MODES, run
from hesp.environment import SimulatedEnvironment
from hesp.planner import ScriptedPlanner
from hesp.study import make_schedule, run_study


def outcome(task, repeat, mode, success=True, tokens=0):
    return {"task_id": task, "repeat": repeat, "mode": mode,
            "verified_simulation": success, "status": "VERIFIED_SIMULATION" if success else "PLANNER_ERROR",
            "tool_calls": 1, "tool_cost_units": 1, "planner_calls": 1, "wall_seconds": .1,
            "reported_input_tokens": tokens, "reported_output_tokens": tokens}


class AnalysisTests(unittest.TestCase):
    def test_schedule_is_reproducible_balanced_and_randomized(self):
        plan = make_schedule(3, 42)
        self.assertEqual(plan, make_schedule(3, 42))
        self.assertNotEqual(plan, make_schedule(3, 43))
        self.assertEqual(len(plan), 36)
        self.assertEqual(len({(r['task_id'], r['repeat'], r['mode']) for r in plan}), 36)

    def test_invalid_repeats(self):
        for repeats in (0, -1, True, 1.5):
            with self.assertRaises(ValueError):
                make_schedule(repeats, 0)

    def test_cluster_weighting_not_repeat_weighting(self):
        rows = [outcome("a", 0, m, m == "hesp") for m in MODES]
        rows += [outcome("b", r, m, m != "hesp") for r in range(9) for m in MODES]
        report = summarize(rows)
        comparison = report["paired_verification"]["hesp_minus_memory_only"]
        self.assertEqual(comparison["difference"], 0)
        self.assertEqual(comparison["task_clusters"], 2)
        self.assertEqual(report, summarize(rows))

    def test_missing_and_duplicate_cells_rejected(self):
        rows = [outcome("a", 0, m) for m in MODES]
        for bad in ([], rows[:-1], rows + [rows[0]]):
            with self.assertRaises(ValueError):
                summarize(bad)

    def test_failures_kept_unknown_tokens_not_zero(self):
        rows = [outcome("a", 0, m, False, None) for m in MODES]
        report = summarize(rows)
        for value in report["modes"].values():
            self.assertEqual(value["verified_fraction"], 0)
            self.assertEqual(value["statuses"], {"PLANNER_ERROR": 1})
            self.assertIsNone(value["reported_input_tokens"]["mean_known"])
            self.assertEqual(value["reported_input_tokens"]["unknown_runs"], 1)
        self.assertIsNone(report["paired_verification"]["hesp_minus_memory_only"]["cluster_bootstrap_percentile_95"])

    def test_invalid_verification_rejected(self):
        rows = [outcome("a", 0, m, "false") for m in MODES]
        with self.assertRaises(ValueError):
            summarize(rows)

    def test_full_study_and_all_journals(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "study"
            report = run_study(path, repeats=1)
            self.assertFalse(report["research_claim_allowed"])
            for folder in path.glob("run*"):
                self.assertTrue(audit_run(folder)["passed"], str(folder))
            self.assertEqual(len((path / "outcomes.jsonl").read_text().splitlines()), 12)
            with self.assertRaises(FileExistsError):
                run_study(path)


class RegressionTests(unittest.TestCase):
    def test_scripted_planner_does_not_finish_from_stale_signal(self):
        decision = ScriptedPlanner().decide({
            "history": [{"id": "o1", "outcome": "matched", "state_version": 0, "action_id": "inspect_owner"}],
            "state_version": 1,
            "tools": [{"id": "inspect_owner", "purpose": "diagnose_owner_policy"}],
        })
        self.assertEqual(decision["kind"], "action")

    def test_auditor_detects_removed_prediction(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "run"
            run(SimulatedEnvironment(), ScriptedPlanner(), "hesp", path)
            self.assertTrue(audit_run(path)["passed"])
            file = path / "events.jsonl"
            events = [json.loads(line) for line in file.read_text().splitlines()]
            events = [e for e in events if e["kind"] != "prediction_registered"]
            file.write_text("\n".join(json.dumps(e) for e in events), encoding="utf-8")
            self.assertFalse(audit_run(path)["passed"])

    def test_budget_failure_is_retained_and_auditable(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "run"
            result = run(SimulatedEnvironment(), ScriptedPlanner(), "react_style", path,
                         Budget(max_tool_calls=1))
            self.assertFalse(result["verified_simulation"])
            self.assertTrue(audit_run(path)["passed"])
