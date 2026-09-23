"""LLM components against a fake local Ollama server (no model needed in CI)."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import tempfile
import threading
import unittest

from hesp.audit import audit_run
from hesp.controller import Budget, run
from hesp.llm import LLMPlanner, LLMPredictor, OllamaClient, check_decision, render_request
from hesp.predictors import FrozenPredictor, TablePredictor, calibration
from hesp.webapp import DESCRIPTIONS, HYPOTHESES, WebDiagEnvironment, catalog, true_outcome_distribution


class FakeOllama:
    """Replies with queued message contents; records every request payload."""

    def __init__(self, replies):
        self.replies, self.requests = list(replies), []
        fake = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                fake.requests.append(payload)
                if self.path == "/api/chat":
                    content = fake.replies.pop(0) if fake.replies else '{"kind":"stop","reason":"empty"}'
                    if callable(content):
                        content = content(payload)
                    body = {"message": {"content": content}, "prompt_eval_count": 100,
                            "prompt_eval_cached_count": 20, "eval_count": 10, "total_duration": 1_000_000}
                else:
                    body = {"details": {"family": "fake", "parameter_size": "0B", "quantization_level": "none"}}
                data = json.dumps(body).encode()
                self.send_response(200)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def do_GET(self):
                body = {"models": [{"name": "fake", "digest": "abc"}]} if self.path == "/api/tags" else {"version": "t"}
                data = json.dumps(body).encode()
                self.send_response(200)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def log_message(self, *a):
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.client = OllamaClient("fake", f"http://127.0.0.1:{self.server.server_address[1]}", timeout=10)

    def close(self):
        self.server.shutdown()
        self.server.server_close()


def base_request(mode="react_style", history=()):
    return {"mode": mode, "task": WebDiagEnvironment.describe(WebDiagEnvironment.__new__(WebDiagEnvironment)),
            "tools": [{"id": a.id, "purpose": a.purpose, "cost": a.cost, "description": a.description,
                       "outcome_notes": a.outcome_notes} for a in catalog()],
            "state_version": 0, "remaining_tool_calls": 5, "remaining_tool_cost": 5,
            "history": list(history), "blocked_proposals": []}


class LLMPlannerTests(unittest.TestCase):
    def fake(self, replies):
        fake = FakeOllama(replies)
        self.addCleanup(fake.close)
        return fake

    def test_client_is_loopback_only(self):
        with self.assertRaises(ValueError):
            OllamaClient("m", "http://example.com:11434")

    def test_valid_decision_and_usage_including_cache(self):
        fake = self.fake(['{"kind":"action","action_id":"whoami","reason":"check"}'])
        decision = LLMPlanner(fake.client, seed=3).decide(base_request())
        self.assertEqual(decision["action_id"], "whoami")
        self.assertEqual(decision["usage"], {"input_tokens": 120, "output_tokens": 10, "cached_input_tokens": 20})
        self.assertEqual(decision["llm"]["attempts"], 1)
        self.assertEqual(fake.requests[0]["format"], "json")

    def test_one_repair_attempt_then_fail_closed(self):
        fake = self.fake(["not json", '{"kind":"action","action_id":"quota","reason":"r"}'])
        decision = LLMPlanner(fake.client).decide(base_request())
        self.assertEqual(decision["llm"]["attempts"], 2)
        self.assertEqual(decision["usage"]["input_tokens"], 240)
        self.assertIn("Invalid reply", fake.requests[1]["messages"][-1]["content"])
        fake2 = self.fake(["nope", '{"kind":"action","action_id":"rm -rf","reason":"r"}'])
        with self.assertRaises(ValueError):
            LLMPlanner(fake2.client).decide(base_request())

    def test_seeds_vary_per_call(self):
        fake = self.fake(['{"kind":"stop","reason":"a"}', '{"kind":"stop","reason":"b"}'])
        planner = LLMPlanner(fake.client, seed=1)
        planner.decide(base_request())
        planner.decide(base_request())
        self.assertNotEqual(fake.requests[0]["options"]["seed"], fake.requests[1]["options"]["seed"])

    def test_check_decision(self):
        req = base_request(history=[{"id": "o0001", "action_id": "doc_meta", "state_version": 0,
                                     "outcome": "owner_other", "raw": "x", "valid": True}])
        self.assertIsNone(check_decision({"kind": "finish", "hypothesis": "owner_policy",
                                          "evidence_ids": ["o0001"]}, req))
        for bad in ({"kind": "finish", "hypothesis": "owner_policy", "evidence_ids": ["o9"]},
                    {"kind": "finish", "hypothesis": "sqli", "evidence_ids": ["o0001"]},
                    {"kind": "finish", "hypothesis": "owner_policy", "evidence_ids": []},
                    {"kind": "action", "action_id": "curl"}, {"kind": "explode"}, []):
            self.assertIsNotNone(check_decision(bad, req))

    def test_prompt_sections_follow_arm(self):
        react = render_request(base_request("react_style"))
        self.assertNotIn("Investigation ledger", react)
        self.assertNotIn("Controller rankings", react)
        hesp = base_request("hesp")
        hesp["investigation"] = {"business_state": {"version": 0}, "hypotheses": [{"id": "other", "score": 1}],
                                 "evidence": []}
        hesp["action_rankings"] = [{"action_id": "doc_meta", "expected_information_gain_bits": 1.4,
                                    "cost": 1, "score": 1.4}]
        hesp["blocked_proposals"] = [{"action_id": "help", "reason": "duplicate_same_state", "state_version": 0}]
        text = render_request(hesp)
        for part in ("Investigation ledger", "Controller rankings", "doc_meta: EIG=1.400", "NOT executed"):
            self.assertIn(part, text)

    def test_llm_episode_is_auditable(self):
        def reply(payload):
            text = payload["messages"][-1]["content"]
            if "- o0001 [state v0]" in text:
                return '{"kind":"finish","hypothesis":"owner_policy","evidence_ids":["o0001"],"reason":"owner is bob"}'
            return '{"kind":"action","action_id":"doc_meta","reason":"check owner"}'
        fake = self.fake([reply] * 4)
        with tempfile.TemporaryDirectory() as root, WebDiagEnvironment("owner_policy") as env:
            result = run(env, LLMPlanner(fake.client), "memory_only", Path(root) / "r", Budget(5, 5, 5, 60))
            self.assertEqual(result["status"], "VERIFIED_SIMULATION")
            self.assertEqual(result["reported_input_tokens"], 240)
            self.assertTrue(audit_run(Path(root) / "r")["passed"])


class PredictorTests(unittest.TestCase):
    def test_schema_rows_and_uniform_fallback(self):
        def reply(payload):
            if "Assumed true cause: owner_policy" in payload["messages"][-1]["content"]:
                return "garbage"
            return json.dumps({o: 1.0 for o in payload["format"]["required"]})
        fake = FakeOllama([reply] * 200)
        self.addCleanup(fake.close)
        predictor = LLMPredictor(fake.client)
        tables = predictor.elicit(catalog()[:2], DESCRIPTIONS)
        self.assertEqual(len(predictor.records), 2 * len(HYPOTHESES))
        self.assertEqual(sum(r["uniform_fallback"] for r in predictor.records), 2)
        for a in catalog()[:2]:
            FrozenPredictor(tables, "x")
            for h in HYPOTHESES:
                self.assertAlmostEqual(sum(tables[a.id][h].values()), 1.0)
        self.assertEqual(fake.requests[0]["options"]["temperature"], 0.0)
        with self.assertRaises(ValueError):
            predictor.likelihoods(catalog()[5], HYPOTHESES)

    def test_calibration_perfect_and_wrong(self):
        ids = [a.id for a in catalog()]
        true = lambda a, h: true_outcome_distribution(a, h, 0.1)
        exact = {a: {h: {o: true(a, h).get(o, 0.0) for o in catalog()[i].outcome_notes} for h in HYPOTHESES}
                 for i, a in enumerate(ids)}
        perfect = calibration(exact, true, HYPOTHESES, ids)
        self.assertAlmostEqual(perfect["kl_bits"], 0.0, places=6)
        self.assertEqual(perfect["argmax_agreement"], 1.0)
        designer = calibration({a.id: TablePredictor().likelihoods(a, HYPOTHESES) for a in catalog()}, true,
                               HYPOTHESES, ids)
        self.assertLess(designer["kl_bits"], 0.1)
        uniform = {a.id: {h: {o: 1 / len(a.outcome_notes) for o in a.outcome_notes} for h in HYPOTHESES}
                   for a in catalog()}
        self.assertGreater(calibration(uniform, true, HYPOTHESES, ids)["kl_bits"], designer["kl_bits"])


if __name__ == "__main__":
    unittest.main()
