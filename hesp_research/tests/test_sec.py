"""v0.5 sec-triage family: defensive alert-triage diagnosis on the loopback sandbox."""

import json
from pathlib import Path
import tempfile
import unittest

from hesp.audit import audit_run
from hesp.controller import Budget, run
from hesp.core import expected_information_gain
from hesp.planner import PosteriorPlanner
from hesp.secapp import (CAUSES, HYPOTHESES, SIGNATURES, SecTriageEnvironment, make_sec_env,
                         sec_suite, true_outcome_distribution)
from hesp.uploadapp import UploadDiagEnvironment
from hesp.webapp import WebDiagEnvironment


class Scripted:
    name = "unit_test_double"

    def __init__(self, decisions):
        self.decisions = list(decisions)

    def decide(self, request):
        return dict(self.decisions.pop(0)) if self.decisions else {"kind": "stop", "reason": "done"}


class SecFamilyTests(unittest.TestCase):
    def test_every_probe_matches_generative_model(self):
        for cause in CAUSES:
            with SecTriageEnvironment(cause, "base", seed=4) as env:
                for action in env.catalog():
                    obs = env.execute(action)
                    self.assertIn(obs.outcome, true_outcome_distribution(action.id, cause, .1), (cause, action.id, obs.raw))

    def test_tables_valid_and_probe_ids_disjoint(self):
        for a in SecTriageEnvironment.build_catalog():
            a.validate(HYPOTHESES)
            self.assertEqual(set(a.outcomes()), set(a.outcome_notes))
        sec = {p["id"] for p in SecTriageEnvironment.PROBES}
        for other in (WebDiagEnvironment, UploadDiagEnvironment):
            self.assertFalse(sec & {p["id"] for p in other.PROBES})

    def test_malicious_verdict_alone_does_not_verify(self):
        # threat_intel="malicious_campaign" is shared by three attacks -> never a signature.
        for cause in ("credential_stuffing", "sqli_probe", "dns_c2"):
            with SecTriageEnvironment(cause, "base", seed=1) as env:
                acts = {a.id: a for a in env.catalog()}
                ti = env.execute(acts["threat_intel"])
                self.assertEqual(ti.outcome, "malicious_campaign")
                self.assertFalse(env.verify(cause, [ti.id]))          # "it's malicious" is not enough
                sig_probe = sorted(p for p, _ in SIGNATURES[cause])[0]
                specific = env.execute(acts[sig_probe])
                self.assertTrue(env.verify(cause, [ti.id, specific.id]))

    def test_shared_benign_outcomes_never_confirm(self):
        # "normal" / "protected" / "none" branches are produced by many causes -> not signatures.
        with SecTriageEnvironment("vuln_component", "base", seed=2) as env:
            acts = {a.id: a for a in env.catalog()}
            src = env.execute(acts["source_ips"])          # -> normal (shared)
            adm = env.execute(acts["admin_exposure"])      # -> protected (shared)
            self.assertEqual((src.outcome, adm.outcome), ("normal", "protected"))
            self.assertFalse(env.verify("vuln_component", [src.id, adm.id]))
            cve = env.execute(acts["component_versions"])  # the actual signature
            self.assertTrue(env.verify("vuln_component", [cve.id]))

    def test_every_unique_outcome_is_a_signature(self):
        # Consistency invariant: any outcome a single cause produces uniquely must confirm it.
        by_outcome = {}
        for probe in SecTriageEnvironment.PROBES:
            for cause in CAUSES:
                for o, p in true_outcome_distribution(probe["id"], cause, 0.0).items():
                    if p > 0:
                        by_outcome.setdefault((probe["id"], o), set()).add(cause)
        for (pid, outcome), causes in by_outcome.items():
            if len(causes) == 1:
                (cause,) = causes
                self.assertIn((pid, outcome), SIGNATURES[cause], f"{pid}={outcome} unique to {cause} but not a signature")

    def test_first_probe_by_eig_per_cost_is_cheap(self):
        prior = {h: 1 / len(HYPOTHESES) for h in HYPOTHESES}
        ranked = sorted(SecTriageEnvironment.build_catalog(),
                        key=lambda a: -expected_information_gain(prior, a) / a.cost)
        self.assertEqual(ranked[0].cost, 1)          # a cost-1 probe leads, not the cost-3 TI enrichment
        self.assertNotEqual(ranked[0].id, "threat_intel")

    def test_suite_balanced_and_drift_distinct(self):
        tasks = sec_suite()
        self.assertEqual(len(tasks), 24)
        self.assertEqual(len({t["task_id"] for t in tasks}), 24)
        for t in tasks:
            if t["variant"] == "drift":
                self.assertNotEqual(t["cause"], t["drift_to"])


class SecControllerTests(unittest.TestCase):
    def test_every_task_solvable_by_direct_confirmation(self):
        with tempfile.TemporaryDirectory() as root:
            for task in sec_suite(("base", "noise")):
                cause = task["cause"]
                probe_id = sorted(p for p, _ in SIGNATURES[cause])[0]
                decisions = []
                for attempt in range(1, 7):          # noise: retry transient 503s
                    decisions += [{"kind": "action", "action_id": probe_id, "reason": "confirm"},
                                  {"kind": "finish", "hypothesis": cause, "evidence_ids": [f"o{attempt:04d}"],
                                   "reason": "direct signature"}]
                with make_sec_env(task, 7) as env:
                    r = run(env, Scripted(decisions), "memory_only", Path(root) / task["task_id"], Budget(12, 16, 12, 60))
                self.assertTrue(r["verified_simulation"], task["task_id"])
                self.assertTrue(audit_run(Path(root) / task["task_id"])["passed"])

    def test_hesp_controller_solves_all_and_audits(self):
        with tempfile.TemporaryDirectory() as root:
            for task in sec_suite():
                with make_sec_env(task, 5) as env:
                    r = run(env, PosteriorPlanner(), "hesp", Path(root) / task["task_id"], Budget(12, 16, 12, 60))
                self.assertTrue(r["verified_simulation"], task["task_id"])
                self.assertTrue(audit_run(Path(root) / task["task_id"])["passed"], task["task_id"])

    def test_planner_request_hides_hidden_cause(self):
        with tempfile.TemporaryDirectory() as root:
            with make_sec_env(sec_suite()[5], 5) as env:
                run(env, Scripted([{"kind": "stop", "reason": "x"}]), "hesp", Path(root) / "r", Budget(12, 16, 12, 60))
            text = (Path(root) / "r/events.jsonl").read_text(encoding="utf-8")
            req = next(json.loads(l)["request"] for l in text.splitlines() if json.loads(l)["kind"] == "planner_request")
            self.assertNotIn("drift_to", json.dumps(req))
            self.assertIn("answer_options", req["task"])


if __name__ == "__main__":
    unittest.main()
