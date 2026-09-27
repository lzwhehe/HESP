"""v0.4: held-out upload-diag family, state-guarded finish, concurrent suites, vLLM client."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import tempfile
import threading
import unittest

from hesp.audit import audit_run
from hesp.controller import Budget, run
from hesp.core import expected_information_gain
from hesp.llm import OpenAICompatClient
from hesp.planner import PosteriorPlanner
from hesp.selectors import Selector
from hesp.study import run_suite
from hesp.uploadapp import (CAUSES, HYPOTHESES, UploadDiagEnvironment, make_upload_env,
                            true_outcome_distribution, upload_suite)
from hesp.webapp import WebDiagEnvironment, make_web_env, web_suite


class Scripted:
    name = "unit_test_double"

    def __init__(self, decisions):
        self.decisions = list(decisions)

    def decide(self, request):
        return dict(self.decisions.pop(0)) if self.decisions else {"kind": "stop", "reason": "done"}


class UploadFamilyTests(unittest.TestCase):
    def test_every_probe_matches_generative_model(self):
        for cause in CAUSES:
            with UploadDiagEnvironment(cause, "base", seed=2) as env:
                for action in env.catalog():
                    obs = env.execute(action)
                    self.assertIn(obs.outcome, true_outcome_distribution(action.id, cause, .1), (cause, action.id, obs.raw))

    def test_tables_valid_and_structurally_different_from_web(self):
        for a in UploadDiagEnvironment.build_catalog():
            a.validate(HYPOTHESES)
        prior = {h: 1 / len(HYPOTHESES) for h in HYPOTHESES}
        rank = sorted(UploadDiagEnvironment.build_catalog(), key=lambda a: -expected_information_gain(prior, a) / a.cost)
        self.assertEqual(rank[0].id, "dry_run")          # medium-cost broad probe first
        self.assertEqual(rank[0].cost, 2)
        web_rank = sorted(WebDiagEnvironment.build_catalog(),
                          key=lambda a: -expected_information_gain({h: 1 / 9 for h in a.likelihoods}, a) / a.cost)
        self.assertEqual(web_rank[0].cost, 1)

    def test_probe_ids_disjoint_from_web(self):
        web = {p["id"] for p in WebDiagEnvironment.PROBES}
        upload = {p["id"] for p in UploadDiagEnvironment.PROBES}
        self.assertFalse(web & upload)

    def test_generic_forbidden_is_not_a_signature(self):
        with UploadDiagEnvironment("token_revoked") as env:
            acts = {a.id: a for a in env.catalog()}
            dry = env.execute(acts["dry_run"])
            self.assertEqual(dry.outcome, "forbidden")
            self.assertFalse(env.verify("token_revoked", [dry.id]))
            tok = env.execute(acts["token"])
            self.assertTrue(env.verify("token_revoked", [dry.id, tok.id]))

    def test_every_task_solvable_by_direct_confirmation(self):
        from hesp.uploadapp import SIGNATURES
        with tempfile.TemporaryDirectory() as root:
            for task in upload_suite(("base", "noise")):
                cause = task["cause"]
                probe_id = sorted(p for p, _ in SIGNATURES[cause] if p not in ("trace", "dry_run"))[0]
                decisions = [{"kind": "action", "action_id": probe_id, "reason": "confirm"}] * 1
                for attempt in range(1, 6):          # noise: retry transient 503s
                    decisions += [{"kind": "finish", "hypothesis": cause, "evidence_ids": [f"o{attempt:04d}"],
                                   "reason": "direct"}, {"kind": "action", "action_id": probe_id, "reason": "retry"}]
                with make_upload_env(task, 9) as env:
                    r = run(env, Scripted(decisions), "memory_only", Path(root) / task["task_id"], Budget(10, 14, 10, 60))
                self.assertTrue(r["verified_simulation"], task["task_id"])
                self.assertTrue(audit_run(Path(root) / task["task_id"])["passed"])

    def test_elimination_alone_is_not_verified(self):
        # High posterior by elimination without a direct signature must not pass the verifier.
        with tempfile.TemporaryDirectory() as root:
            with UploadDiagEnvironment("token_revoked", "base", 9) as env:
                r = run(env, PosteriorPlanner(), "hesp", Path(root) / "r", Budget(10, 14, 10, 60))
            self.assertEqual(r["status"], "UNVERIFIED_CLAIM")
            self.assertTrue(audit_run(Path(root) / "r")["passed"])


class FinishGuardTests(unittest.TestCase):
    def episode(self, decisions, guard, cause="owner_policy", variant="base", drift_to=None):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        with WebDiagEnvironment(cause, variant, 0, drift_to) as env:
            result = run(env, Scripted(decisions), "memory_only", Path(self.tmp.name) / "r", Budget(10, 8, 10, 60),
                         finish_guard=guard)
        events = [json.loads(l) for l in (Path(self.tmp.name) / "r/events.jsonl").read_text(encoding="utf-8").splitlines()]
        return result, events

    def test_stale_evidence_finish_rejected_then_recovers(self):
        decisions = [{"kind": "action", "action_id": "doc_meta", "reason": "r"},
                     {"kind": "action", "action_id": "whoami", "reason": "r"},       # drift happens here
                     {"kind": "finish", "hypothesis": "owner_policy", "evidence_ids": ["o0001"], "reason": "stale"},
                     {"kind": "action", "action_id": "workflow", "reason": "r"},
                     {"kind": "finish", "hypothesis": "workflow_locked", "evidence_ids": ["o0003"], "reason": "fresh"}]
        unguarded, _ = self.episode(decisions, False, variant="drift", drift_to="workflow_locked")
        self.assertEqual(unguarded["status"], "UNVERIFIED_CLAIM")
        guarded, events = self.episode(decisions, True, variant="drift", drift_to="workflow_locked")
        self.assertEqual(guarded["status"], "VERIFIED_SIMULATION")
        self.assertEqual(guarded["finish_rejections"], 1)
        rejected = next(e for e in events if e["kind"] == "finish_rejected")
        self.assertIn("current state", rejected["reasons"][0])
        feedback = [e["request"]["blocked_proposals"] for e in events if e["kind"] == "planner_request"][-1]
        self.assertTrue(any(b["action_id"] == "finish:owner_policy" for b in feedback))

    def test_guard_accepts_supported_claim_and_never_uses_hidden_cause(self):
        decisions = [{"kind": "action", "action_id": "doc_meta", "reason": "r"},
                     {"kind": "finish", "hypothesis": "owner_policy", "evidence_ids": ["o0001"], "reason": "ok"}]
        result, _ = self.episode(decisions, True)
        self.assertEqual((result["status"], result["finish_rejections"]), ("VERIFIED_SIMULATION", 0))
        # A wrong but ledger-supported claim is *not* blocked by the guard: it only checks the ledger.
        decisions = [{"kind": "action", "action_id": "help", "reason": "r"},
                     {"kind": "finish", "hypothesis": "owner_policy", "evidence_ids": ["o0001"], "reason": "weak"}]
        result, _ = self.episode(decisions, True)
        self.assertEqual(result["finish_rejections"], 1)


class ConcurrencyTests(unittest.TestCase):
    def test_parallel_suite_matches_serial(self):
        arms = {"seq": {"mode": "memory_only", "planner": lambda s: PosteriorPlanner()},
                "guard": {"mode": "hesp", "planner": lambda s: PosteriorPlanner(), "selector": "lookahead",
                          "finish_guard": True}}
        tasks = web_suite()[:4] + upload_suite()[8:12]
        factory = lambda t, s: (make_web_env if t["family"] == "web-diag" else make_upload_env)(t, s)
        with tempfile.TemporaryDirectory() as root:
            _, serial = run_suite(Path(root) / "a", tasks, arms, factory, repeats=2, seed=3)
            _, parallel = run_suite(Path(root) / "b", tasks, arms, factory, repeats=2, seed=3, workers=8)
            key = lambda r: (r["task_id"], r["repeat"], r["arm"])
            pick = lambda r: (r["status"], r["tool_cost_units"], r["planner_calls"])
            self.assertEqual({key(r): pick(r) for r in serial}, {key(r): pick(r) for r in parallel})
            self.assertEqual(len((Path(root) / "b/outcomes.jsonl").read_text().splitlines()), len(parallel))
            manifest = json.loads((Path(root) / "b/manifest.json").read_text())
            self.assertTrue(manifest["arms"]["guard"]["finish_guard"])
            for d in (Path(root) / "b").glob("run*"):
                self.assertTrue(audit_run(d)["passed"], d.name)


class OpenAICompatTests(unittest.TestCase):
    def test_client_payload_usage_and_loopback(self):
        seen = []

        class H(BaseHTTPRequestHandler):
            def do_POST(self):
                payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                seen.append((self.path, payload))
                body = json.dumps({"choices": [{"message": {"content": '{"kind":"stop","reason":"x"}'},
                                                "finish_reason": "stop"}],
                                   "usage": {"prompt_tokens": 50, "completion_tokens": 7,
                                             "prompt_tokens_details": {"cached_tokens": 32}}}).encode()
                self.send_response(200)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *a):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        client = OpenAICompatClient("m", f"http://127.0.0.1:{server.server_address[1]}/v1")
        reply = client.chat([{"role": "user", "content": "hi"}], seed=5, fmt={"type": "object"})
        self.assertEqual(reply["usage"], {"input_tokens": 50, "output_tokens": 7, "cached_input_tokens": 32})
        path, payload = seen[0]
        self.assertEqual(path, "/v1/chat/completions")
        self.assertEqual(payload["seed"], 5)
        self.assertEqual(payload["response_format"]["type"], "json_schema")
        client.chat([{"role": "user", "content": "hi"}])
        self.assertEqual(seen[1][1]["response_format"], {"type": "json_object"})
        with self.assertRaises(ValueError):
            OpenAICompatClient("m", "http://10.0.0.5:8000/v1")


if __name__ == "__main__":
    unittest.main()
