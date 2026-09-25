import json
from pathlib import Path
import tempfile
import unittest

from hesp.audit import audit_run
from hesp.controller import Budget, run
from hesp.core import Action
from hesp.planner import PosteriorPlanner
from hesp.selectors import Selector
from hesp import webapp
from hesp.webapp import CAUSES, HYPOTHESES, PROBES, WebDiagEnvironment, catalog, true_outcome_distribution


class Always:
    name = "unit_test_double"

    def __init__(self, decision):
        self.decision = decision

    def decide(self, request):
        return dict(self.decision)


class SandboxTests(unittest.TestCase):
    def test_every_probe_outcome_matches_generative_model(self):
        for cause in CAUSES:
            with WebDiagEnvironment(cause, "base", seed=1) as env:
                for action in env.catalog():
                    obs = env.execute(action)
                    expected = true_outcome_distribution(action.id, cause, webapp.VARIANTS["base"]["audit_lag"])
                    self.assertIn(obs.outcome, expected, (cause, action.id, obs.raw))
                    self.assertTrue(obs.valid)
                    self.assertTrue(obs.raw.startswith(action.purpose.split(" ")[0]))

    def test_loopback_only_and_path_allowlist(self):
        with WebDiagEnvironment("owner_policy") as env:
            self.assertTrue(env._base.startswith("http://127.0.0.1:"))
            with self.assertRaises(ValueError):
                env._request("GET", "/admin")
            with self.assertRaises(ValueError):
                env._request("DELETE", "/documents/42")
            rogue = Action("whoami", webapp.TARGET, "GET /admin", 1, catalog()[0].likelihoods)
            with self.assertRaises(ValueError):
                env.execute(rogue)

    def test_server_is_shut_down_on_close(self):
        env = WebDiagEnvironment("owner_policy")
        env.close()
        with self.assertRaises(RuntimeError):
            env.execute(catalog()[0])
        env.close()  # idempotent

    def test_verifier_rules(self):
        with WebDiagEnvironment("owner_policy") as env:
            acts = {a.id: a for a in env.catalog()}
            meta = env.execute(acts["doc_meta"])
            who = env.execute(acts["whoami"])
            self.assertTrue(env.verify("owner_policy", [meta.id]))
            self.assertTrue(env.verify("owner_policy", [who.id, meta.id]))
            self.assertFalse(env.verify("owner_policy", [who.id]))            # no signature cited
            self.assertFalse(env.verify("workflow_locked", [meta.id]))        # wrong cause
            self.assertFalse(env.verify("owner_policy", ["o9999"]))           # unknown id
            self.assertFalse(env.verify("owner_policy", []))
            extra = [env.execute(acts[a]).id for a in ("quota", "features", "workflow")]
            self.assertFalse(env.verify("owner_policy", [meta.id] + extra))   # more than 3 citations

    def test_drift_changes_state_and_cause(self):
        with WebDiagEnvironment("owner_policy", "drift", seed=0, drift_to="workflow_locked") as env:
            acts = {a.id: a for a in env.catalog()}
            first = env.execute(acts["doc_meta"])
            self.assertEqual(env.state()["version"], 0)
            env.execute(acts["whoami"])
            self.assertEqual(env.state()["version"], 1)
            self.assertFalse(env.verify("owner_policy", [first.id]))          # cause changed
            self.assertFalse(env.verify("workflow_locked", [first.id]))
            lock = env.execute(acts["workflow"])
            self.assertEqual(lock.outcome, "locked")
            self.assertTrue(env.verify("workflow_locked", [lock.id]))

    def test_drift_requires_distinct_target(self):
        with self.assertRaises(ValueError):
            WebDiagEnvironment("owner_policy", "drift", drift_to="owner_policy")
        with self.assertRaises(ValueError):
            WebDiagEnvironment("not_a_cause")

    def test_noise_produces_invalid_transient_observations(self):
        seen = set()
        with WebDiagEnvironment("quota_exceeded", "noise", seed=3) as env:
            act = next(a for a in env.catalog() if a.id == "quota")
            for _ in range(40):
                obs = env.execute(act)
                seen.add((obs.valid, obs.outcome))
        self.assertIn((False, "transient_error"), seen)
        self.assertIn((True, "exceeded"), seen)

    def test_tables_are_valid_and_cover_hypotheses(self):
        for action in catalog():
            action.validate(HYPOTHESES)
            self.assertEqual(set(action.outcomes()), set(action.outcome_notes))
        self.assertEqual(len(PROBES), len(catalog()))

    def test_suite_is_balanced(self):
        tasks = webapp.web_suite()
        self.assertEqual(len(tasks), 24)
        self.assertEqual(len({t["task_id"] for t in tasks}), 24)
        for t in tasks:
            if t["variant"] == "drift":
                self.assertNotEqual(t["cause"], t["drift_to"])


class SandboxControllerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def episode(self, cause="owner_policy", variant="base", mode="hesp", planner=None, selector="eig_cost",
                budget=None, name="run", drift_to=None, seed=0):
        with WebDiagEnvironment(cause, variant, seed, drift_to) as env:
            return run(env, planner or PosteriorPlanner(), mode, self.root / name,
                       budget or Budget(10, 14, 10, 60), selector=Selector(selector, seed))

    def requests(self, name="run"):
        return [json.loads(x)["request"] for x in (self.root / name / "events.jsonl").read_text(encoding="utf-8").splitlines()
                if json.loads(x)["kind"] == "planner_request"]

    def test_all_causes_and_variants_verified_and_auditable(self):
        for task in webapp.web_suite():
            name = task["task_id"]
            result = self.episode(task["cause"], task["variant"], drift_to=task["drift_to"], name=name, seed=5)
            self.assertTrue(result["verified_simulation"], name)
            self.assertTrue(audit_run(self.root / name)["passed"], name)

    def test_planner_request_identical_across_hidden_causes(self):
        self.episode("owner_policy", name="a", planner=Always({"kind": "stop", "reason": "x"}))
        self.episode("quota_exceeded", name="b", planner=Always({"kind": "stop", "reason": "x"}))
        self.assertEqual(self.requests("a"), self.requests("b"))
        text = json.dumps(self.requests("a"))
        for hidden in ("drift_to", "task_id", "variant", "_app", "127.0.0.1"):
            self.assertNotIn(hidden, text)

    def test_hesp_first_probe_is_most_informative_per_cost(self):
        self.episode()
        first = next(json.loads(x) for x in (self.root / "run/events.jsonl").read_text(encoding="utf-8").splitlines()
                     if json.loads(x)["kind"] == "prediction_registered")
        self.assertEqual(first["action"]["id"], "doc_meta")
        self.assertEqual(first["selected_by"], "controller:eig_cost")

    def test_transient_error_does_not_consume_dedup_key(self):
        result = self.episode("quota_exceeded", "noise", seed=11, name="noise")
        events = [json.loads(x) for x in (self.root / "noise/events.jsonl").read_text(encoding="utf-8").splitlines()]
        skipped = [e for e in events if e["kind"] == "evidence_update" and e["evidence"]["skip_reason"] == "invalid_observation"]
        self.assertTrue(result["verified_simulation"])
        self.assertTrue(audit_run(self.root / "noise")["passed"])
        if skipped:  # retries of the same probe after a transient error are executed, not blocked
            retried = skipped[0]["evidence"]["action_id"]
            executions = [e for e in events if e["kind"] == "prediction_registered" and e["action"]["id"] == retried]
            self.assertGreaterEqual(len(executions), 2)

    def test_blocked_duplicates_are_fed_back_to_planner(self):
        self.episode(mode="react_style", planner=Always({"kind": "action", "action_id": "help", "reason": "r"}),
                     budget=Budget(10, 4, 10, 60))
        feedback = [r["blocked_proposals"] for r in self.requests()]
        self.assertEqual(feedback[0], [])
        self.assertEqual(feedback[-1][-1]["action_id"], "help")
        self.assertEqual(feedback[-1][-1]["reason"], "duplicate_same_state")

    def test_stale_evidence_is_not_enough_after_drift(self):
        # Finish with the pre-drift signature: must be rejected by the independent verifier.
        class Stale:
            name = "stale"

            def __init__(self):
                self.n = 0

            def decide(self, request):
                self.n += 1
                if self.n <= 2:
                    return {"kind": "action", "action_id": ["doc_meta", "whoami"][self.n - 1], "reason": "r"}
                return {"kind": "finish", "hypothesis": "owner_policy", "evidence_ids": ["o0001"], "reason": "r"}
        result = self.episode("owner_policy", "drift", "memory_only", Stale(), drift_to="workflow_locked")
        self.assertEqual(result["status"], "UNVERIFIED_CLAIM")
        self.assertTrue(audit_run(self.root / "run")["passed"])

    def test_selectors_all_run(self):
        for sel in ("eig_cost", "eig", "map_greedy", "random", "lookahead"):
            result = self.episode(selector=sel, name=sel)
            self.assertTrue(result["verified_simulation"], sel)
            self.assertEqual(result["selector"], sel)

    def test_react_style_rejects_ledger_dependent_script(self):
        result = self.episode(mode="react_style")
        self.assertEqual(result["status"], "PLANNER_ERROR")


if __name__ == "__main__":
    unittest.main()
