"""v0.7 GUIDE replay: model estimation, environment contract, and the controller's prior hook."""

import json
from pathlib import Path
import tempfile
import unittest

from hesp.controller import Budget, run
from hesp.guideapp import GRADES, PROBES, GuideModel, GuideTriageEnvironment
from hesp.planner import PosteriorPlanner
from hesp.secapp import make_sec_env, sec_suite


def incident(org, iid, grade, detector="d1", category="InitialAccess", **facets):
    o = {"category": category, "technique": "none", "entity_types": "Ip+User", "evidence_roles": "mostly_related",
         "scale": "alerts<=1_ev<=5", "detector": detector, "auto_verdict": "none", "roles": "none",
         "threat_family": "none", "geography": "<=1"}
    o.update(facets)
    return {"org": org, "incident": iid, "grade": grade, "first_ts": "2024-06-01T00:00:00Z", "o": o}


def history():
    rows = []
    for i in range(40):      # org A: detector d1 is always TP; category separates grades globally
        rows.append(incident("A", f"a{i}", "TruePositive", "d1", "InitialAccess"))
    for i in range(30):
        rows.append(incident("B", f"b{i}", "BenignPositive", "d2", "Exfiltration"))
    for i in range(30):
        rows.append(incident("C", f"c{i}", "FalsePositive", "d3", "Execution"))
    for i in range(10):      # org D: detector d2 with an inconsistent history
        rows.append(incident("D", f"d{i}", GRADES[i % 3], "d2", "Exfiltration"))
    return rows


class GuideModelTests(unittest.TestCase):
    def setUp(self):
        self.model = GuideModel(history())

    def test_tables_are_distributions_with_other_bucket(self):
        for p in PROBES:
            for h in GRADES:
                row = self.model.tables[p][h]
                self.assertIn("other", row)
                self.assertAlmostEqual(sum(row.values()), 1.0, places=9)
                self.assertTrue(all(v > 0 for v in row.values()))

    def test_detector_facet_is_its_grading_history(self):
        self.assertEqual(self.model.facet(incident("Z", "z", "TruePositive", "d1"), "detector"), "mostly_TruePositive")
        self.assertEqual(self.model.facet(incident("Z", "z", "TruePositive", "nope"), "detector"), "unseen_detector")

    def test_org_prior_is_smoothed_toward_global(self):
        p = self.model.org_prior("A")
        self.assertGreater(p["TruePositive"], self.model.global_prior["TruePositive"])
        self.assertLess(p["TruePositive"], 1.0)
        self.assertEqual(self.model.org_prior("unknown-org"), self.model.global_prior)

    def test_cold_kinds(self):
        self.assertIsNone(self.model.cold_kind(incident("A", "x", "TruePositive", "d1")))       # consistent history
        self.assertEqual(self.model.cold_kind(incident("A", "x", "TruePositive", "d9")), "unseen")
        self.assertEqual(self.model.cold_kind(incident("D", "x", "TruePositive", "d2")), "mixed")

    def test_history_verdict_falls_back_to_org_prior(self):
        self.assertEqual(self.model.history_verdict(incident("A", "x", "BenignPositive", "d1")), "TruePositive")
        self.assertEqual(self.model.history_verdict(incident("B", "x", "TruePositive", "d9")), "BenignPositive")


class GuideEnvironmentTests(unittest.TestCase):
    def setUp(self):
        self.model = GuideModel(history())

    def test_planner_visible_task_does_not_depend_on_the_grade(self):
        seen = set()
        for g in GRADES:
            env = GuideTriageEnvironment(incident("A", "same", g, "d9"), self.model)
            seen.add(json.dumps([env.describe(), env.state(), [(a.id, a.cost, a.description) for a in env.catalog()],
                                 env.priors()], sort_keys=True))
        self.assertEqual(len(seen), 1)
        self.assertEqual(set(env.describe()["answer_options"]), set(GRADES))

    def test_execute_returns_modelled_outcomes_and_verify_checks_the_grade(self):
        env = GuideTriageEnvironment(incident("A", "x", "TruePositive", "d9", "InitialAccess"), self.model)
        acts = {a.id: a for a in env.catalog()}
        obs = env.execute(acts["category"])
        self.assertEqual(obs.outcome, "InitialAccess")
        self.assertIn(obs.outcome, self.model.tables["category"]["TruePositive"])
        self.assertTrue(env.verify("TruePositive", [obs.id]))
        self.assertFalse(env.verify("BenignPositive", [obs.id]))

    def test_controller_starts_from_the_environment_prior(self):
        env = GuideTriageEnvironment(incident("A", "x", "TruePositive", "d9"), self.model)
        with tempfile.TemporaryDirectory() as root:
            result = run(env, PosteriorPlanner(), "hesp", Path(root) / "r", Budget(4, 8, 4, 60))
            with (Path(root) / "r" / "events.jsonl").open(encoding="utf-8") as f:
                first = next(json.loads(l) for l in f if json.loads(l)["kind"] == "planner_request")
        scores = {h["id"]: h["score"] for h in first["request"]["investigation"]["hypotheses"]}
        for h in GRADES:
            self.assertAlmostEqual(scores[h], self.model.org_prior("A")[h], places=9)
        self.assertEqual(result["environment"], "guide_replay")

    def test_existing_families_keep_the_uniform_prior(self):
        with tempfile.TemporaryDirectory() as root:
            with make_sec_env(sec_suite()[0], 5) as env:
                run(env, PosteriorPlanner(), "hesp", Path(root) / "r", Budget(12, 16, 12, 60))
            with (Path(root) / "r" / "events.jsonl").open(encoding="utf-8") as f:
                first = next(json.loads(l) for l in f if json.loads(l)["kind"] == "planner_request")
        scores = [h["score"] for h in first["request"]["investigation"]["hypotheses"]]
        self.assertTrue(all(abs(s - 1 / len(scores)) < 1e-12 for s in scores))


if __name__ == "__main__":
    unittest.main()
